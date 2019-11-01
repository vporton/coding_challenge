from django.test import TestCase

import from_git
from from_git.aggregator import aggregate_one, WrongURLException, aggregate_data
from from_git.common import sum_profiles

class UtilsTestCase(TestCase):
    def test_sum_profiles(self):
        a = {
            'originalRepos': 10,
            'forkedRepos': 3,
            'watchers': 15,
            'followers': 10,
            'langs': {"python", "php"},
            'topics': {"a", "b"},
        }
        b = {
            'originalRepos': 20,
            'forkedRepos': 4,
            'watchers': 7,
            'followers': 8,
            'langs': {"python", "c"},
            'topics': {"b", "c"},
        }
        sum = {
            'originalRepos': 30,
            'forkedRepos': 7,
            'watchers': 22,
            'followers': 18,
            'langs': {"python", "php", "c"},
            'topics': {"a", "b", "c"},
        }
        self.assertDictEqual(sum_profiles(a, b), sum)

class DownloadingTestCase(TestCase):
    def test_gh_bb(self):
        data = from_git.our_github.download_organization("https://github.com/mailchimp")
        assert(data['originalRepos'] > 1)
        assert("python" in data['langs'])

        data = from_git.our_bitbucket.download_team("https://bitbucket.org/mailchimp")
        assert(data['originalRepos'] > 1)
        assert("python" in data['langs'])

        data = from_git.our_github.download_organization("https://github.com/jfdskfhdskhgjk")
        assert(data is None)

        data = from_git.our_bitbucket.download_team("https://bitbucket.org/fjsldkhgkjd")
        assert(data is None)

    def test_aggregate_one(self):
        for url in ["https://github.com/mailchimp", "https://bitbucket.org/mailchimp"]:
            data = aggregate_one(url)
            assert(data['originalRepos'] > 1)
            assert("python" in data['langs'])
        for url in ["https://github.com/jsdkgjhds", "https://bitbucket.org/hsjdhtjehrje"]:
            data = aggregate_one(url)
            assert(data is None)
        self.assertRaises(WrongURLException, aggregate_one, "hjhjk")

    def test_aggregate_data(self):
        data, missing = aggregate_data(["https://github.com/mailchimp",
                                        "https://bitbucket.org/mailchimp",
                                        "https://github.com/hejwhrejkhw",
                                        "https://bitbucket.org/hsjdhtjehrje"])
        assert(data['originalRepos'] > 1)
        assert(data['forkedRepos'] > 1)
        assert("python" in data['langs'])
        assert("ecommerce" in data['topics'])
        assert(missing == ["https://github.com/hejwhrejkhw", "https://bitbucket.org/hsjdhtjehrje"])
