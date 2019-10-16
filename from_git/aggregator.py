# We will form below the variable `arr` with each member in the format described in common.py
# and "sum" its members together with the __add__() operator.
# The sum will be returned in the JSON response.
import multiprocessing.pool
import threading

from django.conf import settings

from from_git import our_github, our_bitbucket
from from_git.common import zero_data, sum_profiles


class WrongURLException(Exception):
    pass


def aggregate_one(url):
    """Get data from either GitHub or BitBucket."""
    if url.startswith("https://github.com/"):
        return our_github.download_organization(url)
    elif url.startswith("https://bitbucket.org/"):
        return our_bitbucket.download_team(url)
    else:
        raise WrongURLException("Only GitHub organization and BitBucket team URLs are supported.")


class Aggregation(object):
    """Data in the middle of our aggregation process."""
    def __init__(self):
        self.data = zero_data  # nothing downloaded yet
        self.missing = []  # not found teams/orgs
        self.counter = 0  # counter of threads working now to produce this result (NOT the number of workers)
        self.ready = threading.Event()  # when the aggregation operation finishes


class WorkerPool(multiprocessing.pool.ThreadPool):
    """Running multiple network queries in parallel."""

    def __init__(self):
        self.lock = multiprocessing.Lock()  # against race conditions
        super().__init__(settings.NUM_THREADS_MAIN)

    def run(self, urls):
        """Run our aggregation from multiple GH/BB teams in parallel and
        return the result and the list of missing teams/orgs."""
        aggregation = Aggregation()
        for url in urls:
            aggregation.counter += 1  # do not return until it is zero again
            self.apply_async(WorkerPool.process_one, (self, aggregation, url))
        aggregation.ready.wait()
        return aggregation.data, aggregation.missing

    @staticmethod
    def process_one(self, result, url):
        """Aggregate one organization/team into our aggregation data."""
        result_for_one_team = aggregate_one(url)
        if result_for_one_team is None:
            result.missing.push(url)
        with self.lock:  # avoid race conditions
            if result_for_one_team is not None:
                result.data = sum_profiles(result.data, result_for_one_team)
            result.counter -= 1  # this thread is ready
            if not result.counter:
                result.ready.set()  # Notify that we have finished with this result object,


threads_pool = WorkerPool()


def aggregate_data(profiles):
    """Return aggregated teams/orgs data (see `common.py`) and the list of not found teams/orgs."""
    s, missing = threads_pool.run(profiles)

    s['langs'] = list(sorted(s['langs']))  # Transform the set into a list, see README.
    s['topics'] = list(sorted(s['topics']))  # Transform the set into a list, see README.
    s['langsNum'] = len(s['langs'])
    s['topicsNum'] = len(s['topics'])

    return s, missing
