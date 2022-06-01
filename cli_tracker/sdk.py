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
            py_ver = platform.python_version_tuple()
            if (int(py_ver[0]) >= 3 and int(py_ver[1]) >= 10):
                name = platform.freedesktop_os_release()['ID']
                try:
                    version = platform.freedesktop_os_release()['VERSION_ID']
                except:
                    # Most likely this distribution is a rolling release
                    # distribution and has no version information
                    version = None
                arch = platform.machine()
            else:
                # This is some support for python versions below 3.10
                import distro
                name = distro.id()
                version = distro.version()
                arch = platform.machine()
            sentry_sdk.set_context("os", {
                "name": name,
                "version": version,
                "arch": arch
            })
        elif os_name == "Windows":
            sentry_sdk.set_context("os", {
                "name": "Windows",
                "version": platform.release(),
                "arch": platform.machine()
            })
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
