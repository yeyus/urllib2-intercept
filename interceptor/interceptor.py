"""Intercept HTTP connections that use urllib.request (Python 3)
aka urllib2 (Python 2).
"""

from urllib2 import BaseHandler
import ssl
import signal
import urllib2
import datetime
import time
from logger import logger


class MockReader:
    def __init__(self, value):
        self.value = value

    def read(self):
        return self.value


class InterceptHandler(BaseHandler):
    handler_order = 510

    def __init__(self, har_file):
        self.har_file = har_file
        self.request_startdate = None
        self.request_startms = None
        logger.info("InterceptHandler init")

    def http_request(self, request):
        logger.info("Request: " + request._Request__original)
        self.request_startdate = datetime.datetime.now().isoformat()
        self.request_startms = time.time()
        return request

    def http_response(self, request, response):
        # logger.info("Response: " + response.url)
        # logger.info("Response: " + str(response.code) + " - " + response.msg)
        reader = MockReader(response.read())
        response.read = reader.read
        self.har_file.add_entry(
            request=request,
            response=response,
            startDate=self.request_startdate,
            time=(time.time() - self.request_startms)*1000,
        )
        return response

    https_request = http_request
    https_response = http_response


def install_opener(harfile, harpath):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ctx), InterceptHandler(harfile))
    urllib2.install_opener(opener)

    def signal_handler(*args):
        logger.info("Signal handler USR2 captured, writing to " + harpath)
        harfile.write_to_file(harpath)
        logger.info("Wrote to " + harpath)

    try:
        signal.signal(signal.SIGUSR2, signal_handler)
    except (ValueError):
        logger.error("Can't register signal handler for har file in thread")

    logger.info("interceptor installed")
    return opener


def uninstall_opener():
    urllib2.install_opener(None)
