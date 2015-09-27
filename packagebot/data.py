import psycopg2
import config
from datetime import datetime, timedelta
from usps import StringTrackingReply

conn = psycopg2.connect(database=config.SQL_DB, user=config.SQL_USER, password=config.SQL_PASSWORD, host=config.SQL_HOST, port=config.SQL_PORT)

UPDATE_INTERVAL = timedelta(minutes=30)

def get_serviceable_requests():
    with conn.cursor() as cur:
        too_old = datetime.now() - UPDATE_INTERVAL
        cur.execute("SELECT tracking_code, chat_id, value FROM tracking_requests WHERE (last_update IS NULL) OR (last_update < %(tooold)s);", {'tooold' : too_old })
        for record in cur:
            yield record

def insert_request(tracking_code, chat_id, value=None):
    with conn.cursor() as cur:
        try:
            if value is None:
                cur.execute("INSERT INTO tracking_requests (tracking_code, chat_id) VALUES (%s, %s);", (tracking_code, chat_id))
            else:
                cur.execute("INSERT INTO tracking_requests (tracking_code, chat_id, value, last_update) VALUES (%s, %s, %s, %s);", (tracking_code, chat_id, value, datetime.now()))
            conn.commit()
        except psycopg2.IntegrityError, e:
            conn.rollback()
            cur.execute("SELECT value FROM tracking_requests WHERE tracking_code=%s AND chat_id=%s;", (tracking_code, chat_id))
            result = cur.fetchone()
            conn.rollback()
            if (result[0] is None):
                return None
            else:
                return StringTrackingReply(result[0])

def update_request(tracking_code, chat_id, value):
    with conn.cursor() as cur:
        if value is None:
            cur.execute("UPDATE tracking_requests SET value=%s, last_update=%s WHERE tracking_code=%s AND chat_id=%s;", (None, datetime.now(), tracking_code, chat_id))
        else:
            cur.execute("UPDATE tracking_requests SET value=%s, last_update=%s WHERE tracking_code=%s AND chat_id=%s;", (value.user_string(), datetime.now(), tracking_code, chat_id))
        conn.commit()

def last_update_id():
    with conn.cursor() as cur:
        cur.execute("SELECT max(update_id) FROM messages_viewed;")
        result = cur.fetchone()
        conn.rollback()
        if result[0] is None:
            return 0
        return result[0]

def set_last_update_id(update_id):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO messages_viewed (update_id, last_update) VALUES (%s, %s);", (update_id, datetime.now()))
        conn.commit()
