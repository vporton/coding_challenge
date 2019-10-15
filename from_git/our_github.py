# We have a choice of python-bitbucket and atlassian-python-api.
# I chose the least general library as probably faster and better
# suited for our rather specialized task.

from copy import deepcopy

from github3 import github

from from_git.common import zero_data, sum_profiles

# TODO: Should be thread-local?
# Allow github3.py to store data in a cache
etag = None  # GitHub last returned ETag


def process_repository(repo):
    """Process repo data.

    I don't needlessly abstract as the project specification does not require this,
    and instead of returning repository data in a special format,
    return the "processed" data in the same format as a summary for an entire organization.
    Code for returning it in a special format can be easily extracted in the future if
    the project grows and we'd need this abstraction."""
    result = deepcopy(zero_data)
    if not repo.private:
        if repo.parent:  # check if forked
            result['forkedRepos']  = 1
        else:
            result['originalRepos'] = 1
    result['watchers'] = repo.subscribers_count
    result['followers'] = repo.stargazers_count
    if not repo.private and repo.language:
        result['langs'] = {repo.language}  # somehow ineffient
    result['topics'] = set(repo.topics())

    return result


def download_organization(url):
    result = deepcopy(zero_data)  # still zero repos processed
    org = url.replace('https://github.com/', '', 1)
    global etag
    i = github.repositories_by(org, etag=etag)
    for short_repository in i:
        etag = i.etag  # store
        # full_repository = short_repository.refresh()
        result = sum_profiles(result, process_repository(short_repository))
    return result
