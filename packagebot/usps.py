import requests
from bs4 import BeautifulSoup
import re
import logging

_log = logging.getLogger("interact")

headers = {
    'Accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'host' : 'tools.usps.com',
    'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36"
    }

class USPSTracker(object):
    name = "USPS"

    _maybe_valid_regex = '\d{22}'

    def maybe_valid(self, code):
        return not (re.match(self._maybe_valid_regex, code) is None)

    def track(self, tracking_code):
        if not self.maybe_valid(tracking_code):
            return None
        url = "https://tools.usps.com/go/TrackConfirmAction_input?qtc_tLabels1=" + str(tracking_code)
        data = requests.get(url, verify=False,headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        # latest = soup.find_all("tr", 'detail-wrapper latest-detail')
        try:
            text_update = soup.find_all('p', 'tracking-summary-details')[0]
            return text_update.text.strip()
        except IndexError, e:
            _log.exception("USPS unable to parse result for %s", tracking_code)
            return None
