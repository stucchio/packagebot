import packagebot.interact as interact
import packagebot.config as config
import time
import logging

logging.basicConfig(format='%(asctime)-15s -8s %(message)s', level=logging.DEBUG)

while True:
    interact.pull_updates(config.TELEGRAM_POLL_TIMEOUT, config.TELEGRAM_POLL_LIMIT)
    interact.handle_old_requests()
