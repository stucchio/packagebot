from datetime import timedelta

TOKEN = "fake"

#This data is obviously fake
SQL_HOST = 'localhost'
SQL_PORT = 5432
SQL_DB = 'telegram'
SQL_USER = 'telegram'
SQL_PASSWORD = 'FOSTdsPjuAiq'

USPS_USERNAME = "fake"
USPS_PASSWORD = "fake"

DATE_FORMAT = "%B %d, %Y %I:%M %p"

TELEGRAM_POLL_TIMEOUT = 60
TELEGRAM_POLL_LIMIT = 1000

UPDATE_INTERVAL = timedelta(minutes=30)
REQUEST_EXPIRATION_TIME_DELTA = timedelta(days=30)
