# We have a choice of python-bitbucket and atlassian-python-api. (Later found also fifbucket.)
# I choose python-bitbucket as more specialized and so probably more efficient and easy to use.

from copy import deepcopy

from github3.repos import Repository

from from_git.common import zero_data


def download_organization(url):
    repo_name = url.replace('https://bitbucket.org/', '', 1)
    repositories = Repository.all(repo_name)
    result = deepcopy(zero_data)
    return result
