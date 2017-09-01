###
# Main
#
DAEMON = False

###
# WSGI
#
HOST = 'localhost'
PORT = 8000
REUSE_PORT = True

###
# Database
#
DB_URL = "postgresql://osq:change_this@localhost:5432/osq"

###
# Redis config
#
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

###
# Logging
#
DAEMON = False
LOG_LEVEL = 'DEBUG'
SYSLOG_ADDR = '/dev/log'

###
# Other
#
ZENTRAL_COMPATIBILITY = True
