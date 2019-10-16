# We will form below the variable `arr` with each member in the format described in common.py
# and "sum" its members together with the __add__() operator.
# The sum will be returned in the JSON response.
from functools import reduce

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


def aggregate_data(profiles):
    # It would be a little more efficient to summarize an element and throw it away, but so code is more natural.
    # We could alternatively use a generator function, but it this a performance improvement?
    arr = []
    for url in profiles:
        arr.append(aggregate_one(url))

    s = reduce(sum_profiles, arr, zero_data)  # "Sum" several profiles together
    s['langs'] = list(sorted(s['langs']))  # Transform the set into a list, see README.
    s['topics'] = list(sorted(s['topics']))  # Transform the set into a list, see README.
    s['langsNum'] = len(s['langs'])
    s['topicsNum'] = len(s['topics'])
    return s
