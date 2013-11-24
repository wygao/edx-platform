"""
Unit tests for the fake LTI server implementation.
"""

import unittest
import requests
from terrain.fakes.lti import FakeLTIService


class FakeLTIServiceTest(unittest.TestCase):

    def setUp(self):

        self.server = FakeLTIService(
            'test_client_key', 'test_client_secret', 'correct_lti_endpoint'
        )

        self.addCleanup(self.server.shutdown)

    def test_request(self):
        """
        Tests that LTI server processes request with right program
        path, and responds with incorrect signature.
        """
        data = {
            'user_id': 'default_user_id',
            'role': 'student',
            'oauth_nonce': '',
            'oauth_timestamp': '',
            'oauth_consumer_key': 'client_key',
            'lti_version': 'LTI-1p0',
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_version': '1.0',
            'oauth_signature': '',
            'lti_message_type': 'basic-lti-launch-request',
            'oauth_callback': 'about:blank',
            'launch_presentation_return_url': '',
            'lis_outcome_service_url': '',
            'lis_result_sourcedid': ''
        }

        response = requests.post(
            self.server.lti_base + self.server.lti_endpoint, data=data
        )
        self.assertIn("Wrong LTI signature", response.text)
