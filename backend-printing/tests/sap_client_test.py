from unittest.mock import patch, PropertyMock, MagicMock
import unittest
import requests
import json
from helper.sap_client import SAPPrintClient
from helper.models import SAPSystem, PrintQueue
from tests.constants import (
    QUEUE_RESPONSE,
    QUEUE_RESPONSE_SKIP_SSL,
    NUMBER_OF_PRINT_ITEMS,
    PRINT_ITEMS_SAP,
)


class TestSAPPrintClient(unittest.TestCase):
    def setUp(self):
        queue = PrintQueue(queue_name="queue1", print_share_id="share_id")
        self.client = SAPPrintClient(
            SAPSystem(
                sap_sid="sid",
                sap_user="user",
                sap_password="password",
                sap_hostname="https://hostname",
                sap_print_queues=[queue, queue],
            )
        )

        self.client_skip_ssl = SAPPrintClient(
            SAPSystem(
                sap_sid="sid",
                sap_user="user",
                sap_password="password",
                sap_hostname="https://hostname",
                sap_print_queues=[queue, queue],
                skip_ssl_verification=True,
            )
        )

    def test_find_print_queue(self):
        response = self.client.find_print_queue("queue1")
        self.assertEqual(response, True)

    @patch("requests.get")
    def test_get_print_queues(self, mock_requests_get):
        def response():
            res = requests.Response()
            res.status_code = 200
            res._content = json.dumps(QUEUE_RESPONSE).encode("utf-8")
            return res

        mock_requests_get.return_value = response()
        resp = self.client.get_print_queues()
        self.assertEqual(resp, ["queue1", "queue2"])

    @patch("requests.get")
    def test_get_print_queues_skip_ssl_verification(self, mock_requests_get):
        def response():
            res = requests.Response()
            res.status_code = 200
            res._content = json.dumps(QUEUE_RESPONSE_SKIP_SSL).encode("utf-8")
            return res

        mock_requests_get.return_value = response()
        resp = self.client_skip_ssl.get_print_queues()
        self.assertEqual(resp, ["queue3", "queue4"])

    @patch("requests.get")
    def test_get_print_items_from_queue(self, mock_requests_get):
        responses = [
            {
                "status_code": 200,
                "content": json.dumps(NUMBER_OF_PRINT_ITEMS).encode("utf-8"),
            },
            {
                "status_code": 200,
                "content": json.dumps(PRINT_ITEMS_SAP).encode("utf-8"),
            },
        ]

        def side_effect(*args, **kwargs):
            response = responses.pop(0)
            res = requests.Response()
            res.status_code = response["status_code"]
            res._content = response["content"]
            return res

        mock_requests_get.side_effect = side_effect
        response1 = self.client.get_print_items_from_queue("queue1")
        self.assertEqual(response1, PRINT_ITEMS_SAP["d"]["results"])
