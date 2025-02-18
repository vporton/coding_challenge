# We will form below the variable `arr` with each member in the format described in common.py
# and "sum" its members together with the sum_profiles() function.
# The sum will be returned in the JSON response.
import logging
import multiprocessing.pool
import threading

from django.conf import settings

from from_git import our_github, our_bitbucket
from from_git.common import zero_data, sum_profiles


class WrongURLException(Exception):
    """Not GitHub and not BitBucket."""
    pass


def aggregate_one(url):
    """Get data from either GitHub or BitBucket and return aggregated data or `None` if doesn't exist."""
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
        self.threads_counter = 0  # threads_counter of threads working now to produce this result (NOT the number of workers)
        self.ready = threading.Event()  # when the aggregation operation finishes
        self.exception = None


class WorkerPool(multiprocessing.pool.ThreadPool):
    """Running multiple network queries in parallel."""

    def __init__(self):
        self.lock = multiprocessing.Lock()  # against race conditions
        super().__init__(settings.NUM_THREADS_MAIN)

    def run(self, urls):
        """Run our aggregation from multiple GH/BB teams in parallel and
        return the result and the list of missing teams/orgs."""
        logging.debug("Starting the aggregation tread pool")
        aggregation = Aggregation()
        for url in urls:
            aggregation.threads_counter += 1  # do not return until it is zero again
            logging.debug("Launching the thread for %s", url)
            self.apply_async(WorkerPool.process_one, (self, aggregation, url))
        aggregation.ready.wait()  # wait for finishing or error
        if aggregation.exception is not None:
            raise aggregation.exception
        return aggregation.data, aggregation.missing

    @staticmethod
    def process_one(self, result, url):
        """Aggregate one organization/team into our aggregation data."""
        try:
            result_for_one_team = aggregate_one(url)
        except Exception as ex:
            with self.lock:
                result.exception = ex
                # result.threads_counter is nonzero indicating an error
                result.ready.set()
                logging.debug("Exception %s in data aggregation" % str(ex))
                # There is no way to terminate AsyncResult, just wait when it completes :-(
        else:
            with self.lock:  # avoid race conditions
                if result_for_one_team is None:
                    result.missing.append(url)
                else:
                    result.data = sum_profiles(result.data, result_for_one_team)
                result.threads_counter -= 1  # this thread is ready
                logging.debug("Finished the thread for %s" % url)
                if not result.threads_counter:
                    result.ready.set()  # Notify that we have finished with this result object,
                    logging.debug("Finished all threads for a data aggregation")


threads_pool = WorkerPool()


def aggregate_data(profiles):
    """Return aggregated teams/orgs data (see `common.py`) and the list of not found teams/orgs."""
    s, missing_urls = threads_pool.run(profiles)

    s['langs'] = list(sorted(s['langs']))  # Transform the set into a list, see README.
    s['topics'] = list(sorted(s['topics']))  # Transform the set into a list, see README.
    s['langsNum'] = len(s['langs'])
    s['topicsNum'] = len(s['topics'])

    return s, missing_urls
