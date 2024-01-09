import unittest
import requests


class AppTest(unittest.TestCase):
    base_url = "http://a303ede1d4e774c069e082aa09a1468c-1467826700.ap-southeast-1.elb.amazonaws.com"

    def test_pr_created_per_month(self):
        url = f"{self.base_url}/pr-created"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_commits_count_per_push(self):
        url = f"{self.base_url}/push-data"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_file_changes_per_commit(self):
        url = f"{self.base_url}/commits-data"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_health_check(self):
        url = f"{self.base_url}"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)

    def test_invalid_endpoint(self):
        url = f"{self.base_url}/invalid-endpoint"
        response = requests.get(url)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
