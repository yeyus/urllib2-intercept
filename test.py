import sys
import ssl
import logging
from time import sleep

import urllib2


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# interceptor setup
from interceptor.har import HarFile
from interceptor.interceptor import install_opener
harfile = HarFile()
opener = install_opener(harfile, harpath="test.har")
# end of interceptor setup

xml_vlanlist_vlanid_str = """<?xml version='1.0' encoding='utf-8'?>
<DeviceConfiguration>
    <version>1.0</version>
    <VLANList action="$action">
        <VLAN>
            <VLANID>$vlanid</VLANID>
        </VLAN>
    </VLANList>
</DeviceConfiguration>"""


def send_urllib_request(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return opener.open(url)
    # return urllib2.urlopen(url, context=ctx)


def marvell_send_get_request(url, sessionId):
    global gsessionId
    request = urllib2.Request(url, headers={"sessionid": sessionId})
    contents = send_urllib_request(request).read()
    if str(contents).find("Request Is not authenticated") != -1:
        logger.info("Request Is not authenticated")
    return contents


def switch_urllib_request_response(url, xmlstr):
    global gsessionId
    request = urllib2.Request(url, headers={"sessionid": gsessionId}, data=xmlstr)
    send_urllib_request(request).read()


def main():
    logger.info("Request 1 - GET https://catfact.ninja/fact")
    result = marvell_send_get_request("https://catfact.ninja/fact", "fake123")
    logger.info("Response 1 - " + result)
    logger.info("Request 2 - GET https://api.coindesk.com/v1/bpi/currentprice.json")
    marvell_send_get_request(
        "https://api.coindesk.com/v1/bpi/currentprice.json", "fakefake"
    )
    logger.info("Request 3 - POST https://api.coindesk.com/v1/bpi/currentprice.json")
    switch_urllib_request_response("http://httpbin.org/post", xml_vlanlist_vlanid_str)

    logger.info("Request 4 - (Self Signed Cert) GET https://self-signed.badssl.com/")
    result = marvell_send_get_request("https://self-signed.badssl.com/", "fake123")


if __name__ == "__main__":
    global gsessionId
    gsessionId = "fakefakegsessionId"

    logger.info("calling main")

    main()
    sleep(30)
    logger.info("stopping after 30s")
