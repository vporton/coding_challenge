# We have a choice of python-bitbucket and atlassian-python-api. (Later found also fifbucket.)
# python-bitbucket is incompatible with uitemplate 0.6 used by github.py.

from copy import deepcopy

import requests

from from_git.common import zero_data, sum_profiles


# Based on https://community.atlassian.com/t5/Bitbucket-discussions/How-to-list-all-repositories-of-a-team-through-Bitbucket-REST/td-p/1142643
def list_team_repos(team, fields):
    # Request 100 repositories per page (and only their slugs), and the next page URL
    next_page_url = 'https://api.bitbucket.org/2.0/repositories/%s?pagelen=100&fields=next,%s' % (team, fields)

    # Keep fetching pages while there's a page to fetch
    while next_page_url is not None:
        response = requests.get(next_page_url)
        page_json = response.json()

        # Parse repositories from the JSON
        for repo in page_json['values']:
            yield repo

        # Get the next page URL, if present
        # It will include same query parameters, so no need to append them again
        next_page_url = page_json.get('next', None)


def process_repository(repo):
    """Process repo data.

    I don't needlessly abstract as the project specification does not require this,
    and instead of returning repository data in a special format,
    return the "processed" data in the same format as a summary for an entire organization.
    Code for returning it in a special format can be easily extracted in the future if
    the project grows and we'd need this abstraction."""
    result = deepcopy(zero_data)
    if not repo['is_private']:
        if 'parent' in repo:  # check if forked
            result['forkedRepos'] = 1
        else:
            result['originalRepos'] = 1
    # No pybitbucket wrapper, do ourselves:
    watchers_response = requests.get(repo['links']['watchers']['href'] + '?pagelen=0')  # don't retrieve the items, only size
    result['watchers'] = watchers_response.json()['size']
    # result['followers'] = 0  # No followers concept in BitBucket.
    if not repo['is_private'] and repo['language']:
        result['langs'] = {repo['language']}  # somehow ineffient
    # result['topics'] = set()  # No topics concept in BitBucket
    return result


def download_team(url):
    team = url.replace('https://bitbucket.org/', '', 1)
    result = deepcopy(zero_data)  # still zero repos processed
    for repo in list_team_repos(team, 'values.is_private,values.parent,values.links.watchers.href,values.language'):
        processed_team_data = process_repository(repo)
        result = sum_profiles(result, processed_team_data)
    return result
