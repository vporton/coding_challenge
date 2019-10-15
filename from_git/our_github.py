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
    repo = repo['node']
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
    result['topics'] = set(t['nodes']['topic']['name'] for t in repo['repositoryTopics']['nodes'])

    return result


def get_repositories_for_org(client, org):
    after = None
    while True:
        # FIXME: quoting
        after_str = ", after: \"%s\"" % after if after is not None else ""
        number_of_repos_in_query = 100
        j = client.execute('''
        {
            search(query: "%s", type: REPOSITORY, first: %d%s) {
                edges { node {
                    ... on Repository {
                        isPrivate
                        parent {
                            id
                        }
                        watchers {
                            totalCount
                        }
                        stargazers {
                            totalCount
                        }
                        primaryLanguage { # FIXME: several
                            name
                        }
                        repositoryTopics(first: 100) { # exprimentally found max valu that works
                            nodes {
                                topic {
                                    name
                                }
                            }
                        }
                    }
                } }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        ''' % (org, number_of_repos_in_query, after_str))  # hardcoded limit  # FIXME: calculation
        # TODO: Debug pagination
        data = json.loads(j)['data']['search']
        if not data['pageInfo']['hasNextPage']:
            break
        after = data['pageInfo']['endCursor']
        yield from data['edges']


def download_organization(url):
    result = deepcopy(zero_data)  # still zero repos processed
    org = url.replace('https://github.com/', '', 1)
    client = GraphQLClient('https://api.github.com/graphql')
    client.inject_token('Bearer ' + settings.GITHUB_API_TOKEN)  # TODO: Don't hardcode
    for repo in get_repositories_for_org(client, org):
        pocessed_repo_data = process_repository(repo)
        result = sum_profiles(result, pocessed_repo_data)
    return result
