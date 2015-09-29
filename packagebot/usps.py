import config

import requests
from bs4 import BeautifulSoup
import re
import logging
from xml.dom import minidom
from datetime import datetime

_log = logging.getLogger("usps")

headers = {
    'Accept' : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'host' : 'tools.usps.com',
    'User-Agent' : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36"
    }

class TrackingReply(object):
    def user_string(self):
        raise NotImplemented()

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return self.user_string() == other.user_string()

    def __ne__(self, other):
        return (not self.__eq__(other))

class StringTrackingReply(TrackingReply):
    def __init__(self, info):
        if not ((type(info) is str) or (type(info) is unicode)):
            raise TypeError("Info must be a string or unicode.")
        self._info = info

    def user_string(self):
        return self._info

    def __str__(self):
        return "StringTrackingReply(" + self._info + ")"

class USPSScrapingTracker(object):
    name = "USPS-scrape"

    _maybe_valid_regex = '\d{22}'

    def maybe_valid(self, code):
        return not (re.match(self._maybe_valid_regex, code) is None)

    def track(self, tracking_code):
        if not self.maybe_valid(tracking_code):
            return None
        url = "https://tools.usps.com/go/TrackConfirmAction_input?qtc_tLabels1=" + str(tracking_code)
        data = requests.get(url, verify=False,headers=headers)
        soup = BeautifulSoup(data.text, 'html.parser')
        try:
            text_update = soup.find_all('p', 'tracking-summary-details')[0]
            return StringTrackingReply(text_update.text.strip())
        except IndexError, e:
            _log.exception("USPS unable to parse result for %s", tracking_code)
            return None


class USPSApiTrackingReply(TrackingReply):
    def __init__(self, timestamp, event, city, state):
        self._timestamp = timestamp
        self._event = event
        self._city = city
        self._state = state

    def _location(self):
        if (not (self._state is None)) and (not (self._city is None)):
            return self._city + ", " + self._state
        if (self._state is None) and (not (self._city is None)):
            return self._city
        if (not (self._state is None)) and (self._city is None):
            return self._state
        return "Unknown Location"

    def user_string(self):
        return "Your item " + self._event + " at " + self._location() + " at " + self._timestamp.strftime(config.DATE_FORMAT)

    def __str__(self):
        return "USPSApiTrackingReply(" + self._timestamp.strftime(config.DATE_FORMAT) + ", " + str(self._event) + ", " + self._location() + ")"

class USPSParsingError(Exception):
    pass

class USPSApiTracker(object):
    name = "USPS-api"

    _maybe_valid_regex = '(\d{22}|L.*)'

    def maybe_valid(self, code):
        return not (re.match(self._maybe_valid_regex, code) is None)

    def _get_first(self, dom, name):
        elems = dom.getElementsByTagName(name)
        if hasattr(elems[0], "firstChild") and (not (elems[0].firstChild is None)):
            return elems[0].firstChild.nodeValue
        else:
            return None

    DATE_FORMAT = "%B %d, %Y %I:%M %p"

    def _parse_summary(self, dom):
        summary = dom.getElementsByTagName('TrackSummary')[0]
        try:
            timestamp = datetime.strptime(self._get_first(summary, 'EventDate') + " " + self._get_first(summary, 'EventTime'), self.DATE_FORMAT)
        except AttributeError:
            raise USPSParsingError("error in timestamp")
        except TypeError:
            raise USPSParsingError("error in timestamp")
        event = self._get_first(summary, 'Event')
        city = self._get_first(summary, 'EventCity')
        state = self._get_first(summary, 'EventState')
        return USPSApiTrackingReply(timestamp, event, city, state)

    def _parse_details(self, dom):
        result = []
        for d in dom.getElementsByTagName('TrackDetail'):
            timestamp = datetime.strptime(self._get_first(d, 'EventDate') + " " + self._get_first(d, 'EventTime'), self.DATE_FORMAT)
            event = self._get_first(d, 'Event')
            city = self._get_first(d, 'EventCity')
            state = self._get_first(d, 'EventState')
            result.append(USPSApiTrackingReply(timestamp, event, city, state))
        return result

    def track(self, tracking_code):
        url = 'http://production.shippingapis.com/ShippingApi.dll?API=TrackV2&XML=<TrackFieldRequest USERID="' + config.USPS_USERNAME + '"><TrackID ID="' + tracking_code + '"></TrackID></TrackFieldRequest>'
        _log.info("Requesting tracking info from %s", url)
        data = requests.get(url)
        _log.info("Received tracking info. Size was %s bytes.", len(data.text))
        dom = minidom.parseString(data.text)
        try:
            return self._parse_summary(dom)
        except USPSParsingError:
            _log.debug("Could not parse summary, attempting to parse details.")
            details = self._parse_details(dom)
            if len(details) > 0:
                return details[0]
            else:
                return None
        except IndexError, e:
            _log.info("Unable to retrieve tracking info via API for %s", tracking_code)
            return None
        except Exception, e:
            _log.error("Unexpected exception: " + dom.toprettyxml())
            raise
