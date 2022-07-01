from sentry_sdk.integrations.atexit import AtexitIntegration, default_callback

class SilentAtexitIntegration(AtexitIntegration):

    def __init__(self, callback=None):
        if callback is None:
            callback = default_callback
        self.callback = callback
