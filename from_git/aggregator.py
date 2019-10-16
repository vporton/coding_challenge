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
    """Get data from either GitHub o BitBucket."""
    if url.startswith("https://github.com/"):
        return our_github.download_organization(url)
    elif url.startswith("https://bitbucket.org/"):
        return our_bitbucket.download_team(url)
    else:
        raise WrongURLException("Only GitHub organization and BitBucket team URLs are supported.")


class Result(object):
    def __init__(self):
        self.data = zero_data
        self.counter = 0  # counter of threads working to produce this result
        self.event = threading.Event()


class WorkerPool(multiprocessing.pool.ThreadPool):
    def __init__(self):
        self.lock = multiprocessing.Lock()
        super().__init__(settings.NUM_THREADS)

    def run(self, urls):
        result = Result()
        for url in urls:
            result.counter += 1  # do not return until it is zero again
            self.apply_async(WorkerPool.process_one, (self, result, url))
        # Can acquire only when all calls are finished:
        result.event.wait()
        return result.data

    @staticmethod
    def process_one(self, result, url):
        result_for_one_team = aggregate_one(url)
        with self.lock:
            result.data = sum_profiles(result.data, result_for_one_team)
            result.counter -= 1
            if not result.counter:
                result.event.set()  # Notify that we have finished with this result object,


threads_pool = WorkerPool()


def aggregate_data(profiles):
    s = threads_pool.run(profiles)

    s['langs'] = list(sorted(s['langs']))  # Transform the set into a list, see README.
    s['topics'] = list(sorted(s['topics']))  # Transform the set into a list, see README.
    s['langsNum'] = len(s['langs'])
    s['topicsNum'] = len(s['topics'])

    return s
