# We have a choice of python-bitbucket and atlassian-python-api. (Later found also fifbucket.)
# I choose python-bitbucket as more specialized and so probably more efficient and easy to use.

from copy import deepcopy

import requests
from pybitbucket.team import Team

from from_git.common import zero_data, sum_profiles


def process_repository(repo):
    """Process repo data.

    I don't needlessly abstract as the project specification does not require this,
    and instead of returning repository data in a special format,
    return the "processed" data in the same format as a summary for an entire organization.
    Code for returning it in a special format can be easily extracted in the future if
    the project grows and we'd need this abstraction."""
    result = deepcopy(zero_data)
    if not repo.is_private:
        if hasattr(repo, 'parent'):  # check if forked
            result['forkedRepos']  = 1
        else:
            result['originalRepos'] = 1
    # No pybitbucket wrapper, do ourselves:
    watchers_response = requests.get(repo.links.watchers.href + '?pagelen=0')  # don't retrieve the items, only size
    result['watchers'] = watchers_response.json()['size']
    # result['followers'] = 0  # No followers concept in BitBucket.
    if not repo.is_private and repo.language:
        result['langs'] = {repo.language}  # somehow ineffient
    # result['topics'] = set()  # No topics concept in BitBucket
    return result


def download_organization(url):
    repo_name = url.replace('https://bitbucket.org/', '', 1)
    repositories = Team(repo_name)
    for repo in repositories:
        result = sum_profiles(result, process_repository(repo))
    return result
