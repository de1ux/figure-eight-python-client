from unittest import TestCase

import mock as mock

from figure_eight_client import FigureEightClient

# valid_zip is a zip with a csv containing the text '{"fake": "data"}\n'
valid_zip = 'PK\x03\x04\x14\x00\x08\x00\x08\x00\x1bS\xf1N\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x00\x10\x00asdf.csvUX\x0c\x00\xd7K/]\xd6K/]\xf5\x01\x14\x00\xabVJK\xccNU\xb2RPJI,IT\xaa\xe5\x02\x00PK\x07\x08E)\x04J\x13\x00\x00\x00\x11\x00\x00\x00PK\x01\x02\x15\x03\x14\x00\x08\x00\x08\x00\x1bS\xf1NE)\x04J\x13\x00\x00\x00\x11\x00\x00\x00\x08\x00\x0c\x00\x00\x00\x00\x00\x00\x00\x00@\xa4\x81\x00\x00\x00\x00asdf.csvUX\x08\x00\xd7K/]\xd6K/]PK\x05\x06\x00\x00\x00\x00\x01\x00\x01\x00B\x00\x00\x00Y\x00\x00\x00\x00\x00'


class MockRequestsResponse:
    status_code = 200
    content = valid_zip

    def __init__(self, status_code):
        self.status_code = status_code


class MockRequests:
    attempt = 0
    fail_before = 0
    response = None

    def __init__(self, status_code, fail_before=0):
        self.fail_before = fail_before
        self.response = MockRequestsResponse(status_code)

    def get(self, url):
        self.attempt += 1
        if self.attempt < self.fail_before:
            raise Exception("Triggered exception")

        return self.response


class FigureEightClientTest(TestCase):

    @mock.patch("figure_eight_client.figure_eight_client.requests.get")
    def test_get_json_results_by_job_id_retries_exceeded(self, requests_mock):
        requests_mock.side_effect = MockRequestsResponse(400)

        c = FigureEightClient("mock_api_key", "mock_endpoint_url")
        with self.assertRaises(Exception):
            c.get_json_results_by_job_id("mock_job_id", retry_limit=5, retry_timeout=0)

        # 1 initial call + 5 retries
        self.assertEqual(requests_mock.call_count, 6)

    @mock.patch("figure_eight_client.figure_eight_client.requests")
    def test_get_json_results_by_job_id_retries_resolves(self, requests_mock):
        r = MockRequests(200, fail_before=3)
        requests_mock.get = r.get

        c = FigureEightClient("mock_api_key", "mock_endpoint_url")
        c.get_json_results_by_job_id("mock_job_id", retry_limit=5, retry_timeout=0)

        # 1 initial + 3 fail_before
        self.assertEqual(r.attempt, 4)

    @mock.patch("figure_eight_client.figure_eight_client.requests")
    def test_get_json_results_by_job_id_zip_handler(self, requests_mock):
        r = MockRequests(200)
        requests_mock.get = r.get

        c = FigureEightClient("mock_api_key", "mock_endpoint_url")
        results = c.get_json_results_by_job_id("mock_job_id", retry_limit=5, retry_timeout=0)

        self.assertTrue(len(results) > 0)
        self.assertTrue('fake' in results[0])
        self.assertTrue(results[0]['fake'] == 'data')
