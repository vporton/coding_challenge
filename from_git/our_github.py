import json
import logging
from copy import deepcopy

from django.conf import settings
from graphqlclient import GraphQLClient

from from_git.common import zero_data, sum_profiles


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
    if not repo['isPrivate']:
        # lower() to be compatible to BitBucket
        result['langs'] = set(t['name'].lower() for t in repo['languages']['nodes'])
    result['topics'] = set(t['topic']['name'] for t in repo['repositoryTopics']['nodes'])

    return result


class OrganizationNotFound(object):
    pass


def get_repositories_for_org(client, org):
    """Return aggregated organization data (see `common.py`) or `None` if no such org."""
    after = None  # track pagination of GitHub API
    while True:
        after_str = ", after: \"%s\"" % after if after is not None else ""
        number_of_repos_in_query = 100
        logging.debug("GraphQL request to GitHub")
        j = client.execute('''
        {
            organization(login: %s) {
                repositories(first: %d%s) {
                    edges {
                        node {
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
                            languages(first: 100) { # limit from https://developer.github.com/v4/guides/resource-limitations/
                                nodes {
                                    name
                                }
                            }
                            repositoryTopics(first: 100) { # limit from https://developer.github.com/v4/guides/resource-limitations/
                                nodes {
                                    topic {
                                        name
                                    }
                                }
                            }
                        }
                    }
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                }
            }
        }
        ''' % (json.dumps(org), number_of_repos_in_query, after_str))
        data = json.loads(j)
        if 'errors' in data:
            if data['data']['organization'] is None:
                yield OrganizationNotFound()
        data = data['data']['organization']['repositories']
        yield from data['edges']
        if not data['pageInfo']['hasNextPage']:  # This was the last page.
            break
        after = data['pageInfo']['endCursor']


def download_organization(url):
    """Return aggregated organization data (see `common.py`) or `None` if no such org."""
    result = deepcopy(zero_data)  # still zero repos processed
    org = url.replace('https://github.com/', '', 1)
    client = GraphQLClient('https://api.github.com/graphql')
    client.inject_token('Bearer ' + settings.GITHUB_API_TOKEN)  # authentication
    repositories = get_repositories_for_org(client, org)

    for repo in repositories:
        if isinstance(repo, OrganizationNotFound):
            return None
        pocessed_repo_data = process_repository(repo)
        result = sum_profiles(result, pocessed_repo_data)
    return result
