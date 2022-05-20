import atexit
import platform
import os
from pprint import pprint

import sentry_sdk

dsn = "https://078bcf96639e44168d60d2918771d345@o1254779.ingest.sentry.io/6422893"

class CliTracker:
    def __init__(self, application, dsn, release):
        self.sentry = sentry_sdk.init(
            dsn=dsn,
            release=release,
            traces_sample_rate=0,
            server_name=""
        )
    
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("my-tag", application)
            scope.set_extra("ExecutionTime", 20)
            self.scope = scope

        uname = os.uname()
        os_name = platform.uname().system
        if os_name == "Darwin":
            mac = platform.mac_ver()
            sentry_sdk.set_context("os", {
                "name": "macOS",
                "version": mac[0],
                "arch": mac[2]
            })
        elif os_name == "Linux":
            desktop = platform.freedesktop_os_release()
            sentry_sdk.set_context("os", {
                "name": "macOS",
                "version": mac[0], # TODO Georg
                "arch": mac[2]
            })
        elif os_name == "Windows":
            pass
        else:
            pass
        sentry_sdk.set_context("os", {
            "name": uname.sysname,
            "version": uname.release,
        })

        sentry_sdk.set_context("cli", {
            "name": application,
            "version": release,
        })
        atexit.register(self.onExit)

    def onExit(self):
        sentry_sdk.set_context("cli", {
            "execution_time": 20,
        })
        


tracker = CliTracker("TestApp", dsn, "0.0.1")