"""
Fake implementation of an HTTP service.
"""

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json
import urllib
import urlparse
import threading

from logging import getLogger
logger = getLogger(__name__)


class FakeHttpRequestHandler(BaseHTTPRequestHandler, object):
    """
    Handler for the fake HTTP service.
    """

    protocol = "HTTP/1.0"

    def log_message(self, format_str, *args):
        """
        Redirect messages to keep the test console clean.
        """

        msg = "{0} - - [{1}] {2}\n".format(
            self.client_address[0],
            self.log_date_time_String(),
            format_str % args
        )

        sys.stdout.write(msg)


class FakeHttpService(HTTPServer, object):
    """
    Fake HTTP service implementation.
    """

    # Subclasses override this to provide the handler class to use.
    # Should be a subclass of `FakeHttpRequestHandler`
    HANDLER_CLASS = None

    def __init__(self, port_num=0):
        """
        Configure the server to listen on localhost.
        Default is to choose an arbitrary open port.
        """
        address = ('127.0.0.1', port_num)
        HTTPServer.__init__(self, address, self.HANDLER_CLASS)

    def start(self):
        """
        Start the server listening on a local port.
        """
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.daemon = True
        server_thread.start()

    def shutdown(self):
        """
        Stop the server and free up the port
        """
        # First call superclass shutdown()
        HTTPServer.shutdown(self)

        # We also need to manually close the socket
        self.socket.close()

    @property
    def port(self):
        """
        Return the port that the service is listening on.
        """
        _, port = self.server_address
        return port
