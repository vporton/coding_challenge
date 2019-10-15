# We have a choice of python-bitbucket and atlassian-python-api.
# I chose the least general library as probably faster and better
# suited for our rather specialized task.
import json
from copy import deepcopy

import github3
from django.conf import settings
from graphqlclient import GraphQLClient

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
    if not repo['isPrivate']:
        if repo['parent']:  # check if forked
            result['forkedRepos'] = 1
        else:
            result['originalRepos'] = 1
    result['watchers'] = repo['watchers']['totalCount']
    result['followers'] = repo['stargazers']['totalCount']
    if not repo['isPrivate'] and repo['primaryLanguage']:
        result['langs'] = {repo['primaryLanguage']}  # somehow ineffient
    result['topics'] = set(t['nodes']['topic']['name'] in repo['repositoryTopics'])

    return result


def download_organization(url):
    result = deepcopy(zero_data)  # still zero repos processed
    org = url.replace('https://github.com/', '', 1)
    client = GraphQLClient('https://api.github.com/graphql')
    client.inject_token('Bearer ' + settings.GITHUB_API_TOKEN)  # TODO: Don't hardcode
    # FIXME: quoting the org name
    j = client.execute('''
{
    search(query: "%s", type: REPOSITORY) {
        nodes {
            isPrivate
            parent
            watchers {
                totalCount
            }
            stargazers {
                totalCount
            }
            primaryLanguage
            repositoryTopics {
                nodes {
                    topic {
                        name
                    }
                }
            }
        }
    }
}
''' % org)
    data = json.loads(j)
    for repo in data['repository']:
        result = sum_profiles(result, process_repository(repo))
    return result
