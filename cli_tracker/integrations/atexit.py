from __future__ import absolute_import

import os
import sys
import atexit

from sentry_sdk.hub import Hub
from sentry_sdk.utils import logger
from sentry_sdk.integrations import Integration


def default_callback(pending, timeout):
    # type: (int, int) -> None
    """This is the default shutdown callback that is set on the options.
    It prints out a message to stderr that informs the user that some events
    are still pending and the process is waiting for them to flush out.
    """
    sys.stderr.flush()


class SilentAtexitIntegration(Integration):
    identifier = "atexit"

    def __init__(self, callback=None):
        if callback is None:
            callback = default_callback
        self.callback = callback

    @staticmethod
    def setup_once():
        @atexit.register
        def _shutdown():
            logger.debug("atexit: got shutdown signal")
            hub = Hub.main
            integration = hub.get_integration(AtexitIntegration)
            if integration is not None:
                logger.debug("atexit: shutting down client")

                # If there is a session on the hub, close it now.
                hub.end_session()

                # If an integration is there, a client has to be there.
                client = hub.client
                client.close(callback=integration.callback)
