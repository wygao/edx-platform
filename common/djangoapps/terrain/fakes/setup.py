"""
Initialize and teardown fake HTTP services for use in acceptance tests.
"""

#pylint: disable=C0111
#pylint: disable=W0621

from lettuce import before, after, world
from django.conf import settings

from .lti import FakeLTIService
from .youtube import FakeYouTubeService
from .xqueue import FakeXQueueService


@before.all
def setup_fake_services():
    """
    Start all fake services running on localhost.
    """

    # Set up LTI
    world.lti_server = FakeLTIService()
    world.lti_server.start()
    world.lti_server.oauth_settings = {
        'client_key': 'test_client_key',
        'client_secret': 'test_client_secret',
        'lti_base':  'http://{}:{}/'.format('127.0.0.1', world.lti_server.port),
        'lti_endpoint': 'correct_lti_endpoint'
    }

    # Set up YouTube
    world.youtube_server = FakeYouTubeService(port_num=settings.VIDEO_PORT)
    world.youtube_server.start()

    # Set up XQueue
    world.xqueue_server = FakeXQueueService(port_num=settings.XQUEUE_PORT)
    world.xqueue_server.start()


@after.all
def stop_fake_services(total):
    """
    Stop all fake services.
    """
    world.lti_server.shutdown()
    world.youtube_server.shutdown()
    world.xqueue_server.shutdown()
