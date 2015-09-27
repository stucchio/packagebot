import packagebot.interact as interact
import time
import logging

logging.basicConfig(format='%(asctime)-15s -8s %(message)s', level=logging.INFO)

while True:
    interact.pull_updates()
    interact.handle_old_requests()
    time.sleep(1)
