# Both the repository data and the summary data (as presented in JSON) has this format
# (before returning the response we will replace the sets with an ordered lists,
# see README.md for why we do this ordering):

# # See the project mission for the meaning of these values
# {
#     'originalRepos': NUM,
#     'forkedRepos': NUM,
#     'watchers': NUM,
#     'followers': NUM,
#     'langsNum': NUM,  # may be missing
#     'langs': set(...),
#     'topicsNum': NUM,  # may be missing
#     'topics': set(...),
# }

# Nothing downloaded yet
zero_data = {
    'originalRepos': 0,
    'forkedRepos': 0,
    'watchers': 0,
    'followers': 0,
    'langsNum': 0,
    'langs': set(),
    'topicsNum': 0,
    'topics': set(),
}

def sum_profiles(a, b):
    """Make a "sum" of two aggregated data values.

    Could be `__add__()` operator instead but that would need a special class what is more complication than a benefit."""
    return {
        'originalRepos': a['originalRepos'] + b['originalRepos'],
        'forkedRepos': a['forkedRepos'] + b['forkedRepos'],
        'watchers': a['watchers'] + b['watchers'],
        'followers': a['followers'] + b['followers'],
        # 'langsNum': a['langsNum'] + b['langsNum'],
        'langs': a['langs'] | b['langs'],
        # 'topicsNum': a['topicsNum'] + b['topicsNum'],
        'topics': a['topics'] | b['topics'],
    }
