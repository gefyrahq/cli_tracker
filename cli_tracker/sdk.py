import atexit
import platform
import os
import sys
import time

import sentry_sdk

class CliTracker:
    def __init__(self, application, dsn, release, timer=True):
        # The server name may contain some confidential information
        # since we do not need those scrape it from the Sentry object.
        self.sentry = sentry_sdk.init(
            dsn=dsn,
            release=release,
            traces_sample_rate=0,
            server_name="",
            shutdown_timeout=0
        )
        self.opted_out = False
        if timer:
            self.execution_time = 0
            self.start_timer()

        self._set_os_context()
        self._parse_arguments()

        sentry_sdk.set_context("cli", {
            "name": application,
            "version": release,
        })
        atexit.register(self.onExit)

    def onExit(self) -> None:
        if self.opted_out:
            return
        if hasattr(self, "_start_time"):
            self.stop_timer()
            sentry_sdk.set_context("cli", {
                "execution_time": self.execution_time,
            })
        sentry_sdk.capture_message("command executed")

    def _parse_arguments(self):
        args = sys.argv
        if len(args) > 1:
            sentry_sdk.set_tag("command", args[1])

    def _set_os_context(self):
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
            sentry_sdk.set_context("os", {
                "name": uname.sysname,
                "version": uname.release,
            })

    def add_information(self, key: str, value: str, group: str = '') -> None:
        if not group:
            group = "additional_information"
        sentry_sdk.set_context(group, {
            key: value,
        })

    def report_opt_out(self):
        sentry_sdk.set_context("opt_out", {
            "opt_out": True
        })
        sentry_sdk.capture_message("opt_out")
        self.opted_out = True


    def report_opt_in(self):
        sentry_sdk.set_context("opt_out", {
            "opt_in": True
        })
        sentry_sdk.capture_message("opt_in")
        self.opted_out = False

    def start_timer(self) -> None:
        self._start_time = time.perf_counter()

    def stop_timer(self) -> None:
        self.execution_time = self.execution_time + time.perf_counter() - self._start_time

