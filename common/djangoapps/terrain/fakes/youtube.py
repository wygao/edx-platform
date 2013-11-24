"""
Fake implementation of YouTube for acceptance tests.
"""

from .http import FakeHttpRequestHandler, FakeHttpService
import json
import time
import requests


class FakeYouTubeHandler(FakeHttpRequestHandler):
    """
    A handler for Youtube GET requests.
    """

    def do_GET(self):
        """
        Handle a GET request from the client and sends response back.
        """

        self.log_message(
            "Youtube provider received GET request to path {}".format(self.path)
        )

        if 'test_transcripts_youtube' in self.path:

            if 't__eq_exist' in self.path:
                status_message = "".join([
                    '<?xml version="1.0" encoding="utf-8" ?>',
                    '<transcript><text start="1.0" dur="1.0">',
                    'Equal transcripts</text></transcript>'
                ])

                self.send_response(
                    200, content=status_message, headers={'Content-type': 'application/xml'}
                )

            elif 't_neq_exist' in self.path:
                status_message = "".join([
                    '<?xml version="1.0" encoding="utf-8" ?>',
                    '<transcript><text start="1.1" dur="5.5">',
                    'Transcripts sample, different that on server',
                    '</text></transcript>'
                ])

                self.send_response(
                    200, content=status_message, headers={'Content-type': 'application/xml'}
                )

            else:
                self.send_response(404)

        elif 'test_youtube' in self.path:
            self._send_video_response("I'm youtube.")

        else:
            self.send_response(
                404, content="Unused url", headers={'Content-type': 'text/plain'}
            )

    def _send_video_response(self, message):
        """
        Send message back to the client for video player requests.
        Requires sending back callback id.
        """
        # Delay the response to simulate network latency
        time.sleep(self.server.time_to_response)

        # Construct the response content
        callback = self.get_params['callback'][0]
        response = callback + '({})'.format(json.dumps({'message': message}))
        self.log_message("Youtube: sent response {}".format(message))

        self.send_response(200, content=response, headers={'Content-type': 'text/html'})


class FakeYouTubeService(FakeHttpService):
    """
    A fake Youtube provider server that responds
    to GET requests to localhost.
    """
    HANDLER_CLASS = FakeYouTubeHandler

    DEFAULT_DELAY_SEC = 0.5

    def __init__(self, *args, **kwargs):
        super(FakeYouTubeService, self).__init__(*args, **kwargs)
        self._time_to_response = self.DEFAULT_DELAY_SEC

    @property
    def time_to_response(self):
        return self._time_to_response

    @time_to_response.setter
    def time_to_response(self, value):
        self._time_to_response = float(value)
