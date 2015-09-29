import packagebot.interact as interact
import packagebot.config as config
import time
import logging
import urllib2

logging.basicConfig(format='%(asctime)-15s -8s %(message)s', level=logging.DEBUG)
_log = logging.getLogger("bot")

while True:
    try:
        interact.pull_updates(config.TELEGRAM_POLL_TIMEOUT, config.TELEGRAM_POLL_LIMIT)
    except urllib2.URLError:
        _log.exception("Could not connect to telegram. Will try again later.")
        time.sleep(10)
    interact.handle_old_requests()
