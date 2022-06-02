from cli_tracker.sdk import CliTracker

dsn = "https://d818eb1e70554f1ab6b002436bf42a90@sentry.unikube.io/2"
tracker = CliTracker("TestApp", dsn, "0.0.1")
