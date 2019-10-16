from django.test import TestCase

from from_git.aggregator import aggregate_one


class DownloadingTestCase(TestCase):
    def test_aggregate_one(self):
        for url in ["https://github.com/mailchimp", "https://bitbucket.org/mailchimp"]:
            data = aggregate_one(url)
            assert(data['originalRepos'] > 1)
            #assert(missing.empty())
        for url in ["https://github.com/jsdkgjhds", "https://bitbucket.org/hsjdhtjehrje"]:
            data = aggregate_one(url)
            assert(data is None)
            #assert(len(missing) == 1)
