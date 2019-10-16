import multiprocessing
import threading
from copy import deepcopy

import requests
from django.conf import settings

from from_git.common import zero_data, sum_profiles


class RepoWatchersHandler(object):
    """Counter of repository watchers for a repository (used in a thread)."""
    def __init__(self):
        self.counter = 0  # counter of threads working now to produce this result (NOT the number of workers)
        self.ready = threading.Event()  # when the downloading finishes


class WorkerPool(multiprocessing.pool.ThreadPool):
    """Running multiple network queries in parallel."""

    def __init__(self):
        super().__init__(settings.NUM_THREADS_ADDITIONAL)
        self.lock = multiprocessing.Lock()  # against race conditions
        self.exception = None

    def start_getting(self, handler, data, url):
        """Run our aggregation from multiple GH/BB teams in parallel and return the result."""
        handler.counter += 1  # do not return until it is zero again
        print("START %s" % url)
        self.apply_async(WorkerPool.process_one, (self, handler, data, url))

    @staticmethod
    def process_one(self, handler, data, url):
        """Aggregate one organization/team into our aggregation data."""
        print("processing %s" % url)
        try:
            watchers_response = requests.get(url)
            with self.lock:  # avoid race conditions
                data['watchers'] += watchers_response.json()['size']
                handler.counter -= 1  # this thread is ready
                if not handler.counter:
                    handler.ready.set()  # Notify that we have finished with this result object.
        except Exception as ex:
            with self.lock:
                handler.exception = ex
                # handler.counter is nonzero indicating an error
                handler.ready.set()
                self.terminate()


watchers_threads_pool = WorkerPool()


class RepoNotFound(object):
    pass


# Based on https://community.atlassian.com/t5/Bitbucket-discussions/How-to-list-all-repositories-of-a-team-through-Bitbucket-REST/td-p/1142643
def list_team_repos(team, fields):
    """Yields repository data for each team's repository. Or return `None` if no such team."""

    # Request 100 repositories per page (and only their slugs), and the next page URL
    next_page_url = 'https://api.bitbucket.org/2.0/repositories/%s?pagelen=100&fields=next,%s' % (team, fields)

    # Keep fetching pages while there's a page to fetch
    while next_page_url is not None:
        response = requests.get(next_page_url)
        if not response.ok:
            yield RepoNotFound()
        page_json = response.json()

        # Parse repositories from the JSON
        for repo in page_json['values']:
            yield repo

        # Get the next page URL, if present
        # It will include same query parameters, so no need to append them again
        next_page_url = page_json.get('next', None)


def process_repository(total, repo, watchers_handler):
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

    # Query to update result['watchers'] in a separate thread,
    # Don't retrieve the items, only size.
    watchers_threads_pool.start_getting(watchers_handler, total, repo['links']['watchers']['href'] + '?pagelen=0')

    # result['followers'] = 0  # No followers concept in BitBucket.
    if not repo['is_private'] and repo['language']:
        result['langs'] = {repo['language']}  # somehow ineffient
    # result['topics'] = set()  # No topics concept in BitBucket

    return result


def download_team(url):
    """Return aggregated team data (see `common.py`) or `None` if no such team."""
    team = url.replace('https://bitbucket.org/', '', 1)
    result = deepcopy(zero_data)  # still zero repos processed

    lst = list_team_repos(team, 'values.is_private,values.parent,values.links.watchers.href,values.language')
    total = {'watchers': 0}
    watchers_handler = RepoWatchersHandler()
    for repo in lst:
        if isinstance(repo, RepoNotFound):
            return None
        processed_team_data = process_repository(total, repo, watchers_handler)
        result = sum_profiles(result, processed_team_data)

    watchers_handler.ready.wait()  # Wait when all watchers requests finish
    if watchers_handler.exception is not None:
        raise watchers_handler.exception

    result['watchers'] = total['watchers']
    return result
