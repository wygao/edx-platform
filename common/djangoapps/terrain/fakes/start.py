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
def start_fake_services():
    """
    Start all fake services running on localhost.
    """

    # Set up LTI
    world.lti_server = FakeLTIService(
        'test_client_key', 'test_client_secret', 'correct_lti_endpoint'
    )

    # Set up YouTube
    world.youtube_server = FakeYouTubeService(
        port_num=getattr(settings, 'VIDEO_PORT', 0)
    )

    # Set up XQueue
    world.xqueue_server = FakeXQueueService(
        port_num=getattr(settings, 'XQUEUE_PORT', 0)
    )


@after.all
def stop_fake_services(total):
    """
    Stop all fake services.
    """
    world.lti_server.shutdown()
    world.youtube_server.shutdown()
    world.xqueue_server.shutdown()
