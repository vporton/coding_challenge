# We have a choice of agithub (maybe, too general purpose), octohub (low level), github3.py
# (claims to be convenient and ergonomic).
# We should have use instead github-api-v4 to support more efficient GraphQL queries,
# but that project is still in planning stage.
# So our choice is github3.py.

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
    result['langs'] = {repo.language}  # somehow ineffient
    result['topics'] = set(repo.topics())

    return result


def download_organization(url):
    result = deepcopy(zero_data)  # still zero repos processed
    global etag
    i = github.repositories_by(url.replace('https://bitbucket.org/', '', 1), etag=etag)
    for short_repository in i:
        etag = i.etag  # store
        # full_repository = short_repository.refresh()
        result = sum_profiles(result, short_repository)
    return result
