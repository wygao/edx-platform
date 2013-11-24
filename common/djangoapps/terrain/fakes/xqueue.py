"""
Fake implementation of XQueue for acceptance tests.
"""

from .http import FakeHttpRequestHandler, FakeHttpService
import json
import requests
import threading


class FakeXQueueHandler(FakeHttpRequestHandler):
    """
    A handler for XQueue POST requests.
    """

    def do_POST(self):
        """
        Handle a POST request from the client

        Sends back an immediate success/failure response.
        It then POSTS back to the client with grading results.
        """
        msg = "XQueue received POST request {0} to path {1}".format(self.post_dict, self.path)
        self.log_message(msg)

        # Respond only to grading requests
        if self._is_grade_request():
            try:
                xqueue_header = json.loads(self.post_dict['xqueue_header'])
                callback_url = xqueue_header['lms_callback_url']

            except KeyError:
                # If the message doesn't have a header or body,
                # then it's malformed.
                # Respond with failure
                error_msg = "XQueue received invalid grade request"
                self._send_immediate_response(False, message=error_msg)

            except ValueError:
                # If we could not decode the body or header,
                # respond with failure

                error_msg = "XQueue could not decode grade request"
                self._send_immediate_response(False, message=error_msg)

            else:
                # Send an immediate response of success
                # The grade request is formed correctly
                self._send_immediate_response(True)

                # Wait a bit before POSTing back to the callback url with the
                # grade result configured by the server
                # Otherwise, the problem will not realize it's
                # queued and it will keep waiting for a response indefinitely
                delayed_grade_func = lambda: self._send_grade_response(
                    callback_url, xqueue_header
                )

                timer = threading.Timer(self.server.response_delay, delayed_grade_func)
                timer.start()

        # If we get a request that's not to the grading submission
        # URL, return an error
        else:
            error_message = "Invalid request URL"
            self._send_immediate_response(False, message=error_message)

    def _send_immediate_response(self, success, message=""):
        """
        Send an immediate success/failure message
        back to the client
        """

        # Send the response indicating success/failure
        response_str = json.dumps(
            {'return_code': 0 if success else 1, 'content': message}
        )

        self.log_message("XQueue: sent response {0}".format(response_str))

        if self._is_grade_request():
            self.send_response(
                200, content=response_str, headers={'Content-type': 'text/plain'}
            )
        else:
            self.send_response(500)

    def _send_grade_response(self, postback_url, xqueue_header):
        """
        POST the grade response back to the client
        using the response provided by the server configuration
        """
        data = {
            'xqueue_header': json.dumps(xqueue_header),
            'xqueue_body': json.dumps(self.server.grade_response)
        }

        self.log_message("XQueue: sent grading response {0}".format(data))
        requests.post(postback_url, data=data)

    def _is_grade_request(self):
        return 'xqueue/submit' in self.path


class FakeXQueueService(FakeHttpService):
    """
    A fake XQueue grading server that responds
    to POST requests to localhost.
    """

    HANDLER_CLASS = FakeXQueueHandler

    # Number of seconds to delay sending a grading response
    DEFAULT_DELAY_SEC = 2

    def __init__(self, *args, **kwargs):
        """
        Set a default grade response.
        """
        super(FakeXQueueService, self).__init__(*args, **kwargs)
        self._grade_response = dict()
        self.set_grade_response({'correct': True, 'score': 1, 'msg': ''})
        self._response_delay = self.DEFAULT_DELAY_SEC

    @property
    def response_delay(self):
        return self._response_delay

    @property
    def grade_response(self):
        return self._grade_response

    def set_grade_response(self, grade_response_dict):
        """
        Configure the response sent by the grader.
        """

        # Check that the grade response has the right keys
        assert(
            'correct' in grade_response_dict and
            'score' in grade_response_dict and
            'msg' in grade_response_dict
        )

        # Wrap the message in <div> tags to ensure that it is valid XML
        grade_response_dict['msg'] = "<div>%s</div>" % grade_response_dict['msg']

        # Save the response dictionary
        self._grade_response = grade_response_dict

    def set_response_delay(self, delay_sec):
        """
        Configure the delay for the grader response.
        """
        self._response_delay = delay_sec
