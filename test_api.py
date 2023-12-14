import unittest
import requests


class AppTest(unittest.TestCase):
    base_url = "http://aef8a6d87f0434164b0811d76b2ed63b-371865466.ap-southeast-1.elb.amazonaws.com"

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
        data = response.json()
        self.assertEqual(data, {"status": "analytics service is healthy"})

    def test_invalid_endpoint(self):
        url = f"{self.base_url}/invalid-endpoint"
        response = requests.get(url)
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
