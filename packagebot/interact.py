import config
import telegram
import usps
import data
import logging

_log = logging.getLogger("interact")

bot = telegram.Bot(token=config.TOKEN)

def _invalid_message(packageid):
    return "The tracking code " + str(packageid) + " is invalid."

def _update_message(packageid, info):
    return str(packageid) + ": " + info.user_string()

def _unable_to_find_tracking_code(tracking_code):
    return "We were unable to find a package for '" + str(tracking_code) + "'. We'll try again later and notify you if we find anything."

trackers = [usps.USPSApiTracker()]

START_MSG = """Welcome to the tracking bot.

To track a package (currently only USPS), just tell me it's tracking code and I'll keep you updated.

To stop receiving updates, just type `stop`.
"""

def pull_updates(long_poll_timeout, limit):
    _log.debug("Polling for updates, timeout=%s, limit=%s", long_poll_timeout, limit)
    updates = bot.getUpdates(offset=data.last_update_id()+1, limit=limit, timeout=long_poll_timeout)
    _log.info("Received %s updates from telegram", len(updates))
    max_update_id = None

    for u in updates:
        if max_update_id is None:
            max_update_id = u.update_id
        else:
            max_update_id = max(max_update_id, u.update_id)
        tracking_code = u.message.text
        chat_id = u.message.chat_id

        if (tracking_code.lower() == "/start") or (tracking_code.lower() == "/help"):
            bot.sendMessage(chat_id=chat_id, text = START_MSG)
            continue

        if (tracking_code.lower() == 'stop'):
            data.delete_requests(chat_id)
            bot.sendMessage(chat_id=chat_id, text = "I'll stop sending you updates.")
            continue

        maybe_valid = [ t.maybe_valid(tracking_code) for t in trackers]
        if sum(maybe_valid) == 0:
            bot.sendMessage(chat_id=chat_id, text = _invalid_message(tracking_code))
            _log.info("Received invalid tracking code %s from chat %s", tracking_code, chat_id)
            continue

        for t in trackers:
            if t.maybe_valid(tracking_code):
                d = data.insert_request(tracking_code, chat_id)
                _log.info("Received %s from inserting %s, %s", d, tracking_code, chat_id)
                if (not (d is None)):
                    bot.sendMessage(chat_id=chat_id, text=_update_message(tracking_code, d))
                    _log.info("Received request for tracking code %s from %s which already existed. Replied with cached data: %s", tracking_code, chat_id, d)
                else:
                    _log.info("Received request for tracking code %s from %s. Will begin tracking.", tracking_code, chat_id)

    if (not (max_update_id is None)):
        data.set_last_update_id(max_update_id)
        _log.info("Set last update ID to %s", max_update_id)

def handle_old_requests():
    for r in data.get_serviceable_requests():
        tracking_code, chat_id, value, sent_could_not_find = r
        _log.info("Requesting tracking info for %s", r)
        info = None
        for t in trackers:
            if t.maybe_valid(tracking_code):
                info = t.track(tracking_code)
                _log.info("Requested tracking info for %s from %s, received: %s", tracking_code, t.name, info)
                if not (info is None):
                    break

        if (info is None) and (not sent_could_not_find):
            bot.sendMessage(chat_id=chat_id, text = _unable_to_find_tracking_code(tracking_code))
            data.mark_cant_find_request(tracking_code, chat_id)
            _log.info("Notified user %s that we cannot find info on %s", chat_id, tracking_code)
        else:
            if (info != value):
                bot.sendMessage(chat_id=chat_id, text = _update_message(tracking_code, info))
                _log.info("New information found for %s, notified user %s: %s", tracking_code, chat_id, info)

        if (not (info is None)):
            data.update_request(tracking_code, chat_id, info)
        else:
            data.update_request(tracking_code, chat_id, None)
