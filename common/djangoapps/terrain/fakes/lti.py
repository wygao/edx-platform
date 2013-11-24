"""
Fake implementation of an LTI service for acceptance tests.
"""

from .http import FakeHttpRequestHandler, FakeHttpService
from textwrap import dedent
from oauthlib.oauth1.rfc5849 import signature
import mock


class FakeLTIHandler(FakeHttpRequestHandler):
    """
    A handler for LTI POST requests.
    """

    CORRECT_KEYS = [
        'user_id', 'role', 'oauth_nonce', 'oauth_timestamp',
        'oauth_consumer_key', 'lti_version', 'oauth_signature_method',
        'oauth_version', 'oauth_signature', 'lti_message_type',
        'oauth_callback', 'lis_outcome_service_url', 'lis_result_sourcedid',
        'launch_presentation_return_url'
    ]

    def do_POST(self):
        """
        Handle a POST request from the client and sends response back.
        """
        msg = "LTI provider received POST request {} to path {}".format(
            str(self.post_dict), self.path
        )
        self.log_message(msg)

        # Respond only to requests with correct lti endpoint:
        if self._is_correct_lti_request():
            if sorted(self.CORRECT_KEYS) != sorted(self.post_dict.keys()):
                status_message = "Incorrect LTI header"
            else:
                params = {k: v for k, v in self.post_dict.items() if k != 'oauth_signature'}
                if self.server.check_oauth_signature(params, self.post_dict['oauth_signature']):
                    status_message = "This is LTI tool. Success."
                else:
                    status_message = "Wrong LTI signature"
        else:
            status_message = "Invalid request URL"

        self._send_lti_response(status_message)

    def _send_lti_response(self, message):
        """
        Send message back to the client
        """

        response_str = dedent("""
            <html><head><title>TEST TITLE</title></head>
            <body>
            <div><h2>IFrame loaded</h2>
            <h3>Server response is:</h3>
            <h3 class="result">{}</h3></div>
            </body></html>
        """.format(message)).strip()

        self.log_message("LTI: sent response {}".format(response_str))

        headers = {'Content-type': 'text/html'}
        if self._is_correct_lti_request():
            self.send_response(200, headers=headers, content=response_str)
        else:
            self.send_response(500)

    def _is_correct_lti_request(self):
        """If url to LTI tool is correct."""
        return self.server.lti_endpoint in self.path


class FakeLTIService(FakeHttpService):
    """
    A fake LTI provider server that responds to POST requests to localhost.
    """

    HANDLER_CLASS = FakeLTIHandler

    def __init__(self, client_key, client_secret, lti_endpoint, port_num=0):
        """
        Configure the service to recognize `client_key` and `client_secret`
        at the URL path `lti_endpoint`.
        """
        super(FakeLTIService, self).__init__(port_num=port_num)
        self._lti_base = "http://127.0.0.1:{0}/".format(self.port)
        self._lti_endpoint = lti_endpoint
        self._client_key = client_key
        self._client_secret = unicode(client_secret)

    @property
    def lti_base(self):
        """
        Return the base URL at which to contact the LTI service.
        """
        return self._lti_base

    @property
    def lti_endpoint(self):
        """
        Return the URL path at which to contact the LTI service.
        """
        return self._lti_endpoint

    @property
    def client_key(self):
        return self._client_key

    @property
    def client_secret(self):
        return self._client_secret

    def check_oauth_signature(self, params, client_signature):
        """
        Checks oauth signature from client.

        `params` are params from post request except signature,
        `client_signature` is signature from request.

        Builds mocked request and verifies hmac-sha1 signing::
            1. builds string to sign from `params`, `url` and `http_method`.
            2. signs it with `client_secret` which comes from server settings.
            3. obtains signature after sign and then compares it with request.signature
            (request signature comes form client in request)

        Returns `True` if signatures are correct, otherwise `False`.
        """
        request = mock.Mock(
            params=[(unicode(k), unicode(v)) for k, v in params.items()],
            uri=unicode(self.lti_base + self.lti_endpoint),
            http_method=u'POST',
            signature=unicode(client_signature)
        )

        return signature.verify_hmac_sha1(request, self.client_secret)
