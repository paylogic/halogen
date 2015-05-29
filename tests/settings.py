"""Test settings."""
import logging


class TestConfig(object):

    """Test application config."""

    LOG_FACILITY = 'syslog'
    BLUEPRINTS = []
    MEMCACHED_SERVERS = ["127.0.0.1:11211"]
    SERVICE_NAME = 'atilla'
    DEBUG = True
    PORT = 1443
    HOST = '127.0.0.1'
    SERVER_NAME = '{0}:{1}'.format(HOST, PORT)
    SENTRY_DSN = ''
    SENTRY_CAPTURE_USER_ERRORS = True
    LOG_USER_ERRORS = True
    LOG_USER_ERROR_EXC_INFO = True
    LOG_USER_ERROR_LEVEL = logging.INFO
    MEMCACHED_COUNTER_TIME = 0
    TRANSACTION_COMMIT_STATUS_CODES = [200, 201]
    OBJECTS_PER_PAGE = 2
    LOG_ADDRESS = ('localhost', logging.handlers.SYSLOG_UDP_PORT)
