# We will form below the variable `arr` with each member in the format described in common.py
# and "sum" its members together with the __add__() operator.
# The sum will be returned in the JSON response.
import multiprocessing.pool

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


class WorkerPool(multiprocessing.pool.Pool):
    def __init__(self):
        self.lock = multiprocessing.Lock()
        super().__init__(settings.NUM_THREADS)

    def run(self, urls):
        result = Result()
        async_results = []
        for url in urls:
            async_results.append(self.apply_async(WorkerPool.process_one, result, url))

        return result.data

    @staticmethod
    def process_one(self, result, url):
        result_for_one_team = aggregate_one(url)
        with self.lock:
            result.data = sum_profiles(result.data, result_for_one_team)


threads_pool = WorkerPool()


def aggregate_data(profiles):
    s = threads_pool.run(profiles)

    s['langs'] = list(sorted(s['langs']))  # Transform the set into a list, see README.
    s['topics'] = list(sorted(s['topics']))  # Transform the set into a list, see README.
    s['langsNum'] = len(s['langs'])
    s['topicsNum'] = len(s['topics'])

    return s
