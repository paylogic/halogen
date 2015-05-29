"""Server tests."""
import copy
import logging

from atilla.server import (
    Application,
    create_app,
    httplib,
)


def test_create_app():
    """Test create app shortcut."""
    app = create_app(name='test', mode='test', settings_module='tests.settings')
    assert isinstance(app, Application)


class TestConfig(object):

    """Test application config."""

    LOG_ADDRESS = ('localhost', logging.handlers.SYSLOG_UDP_PORT)


def test_create_app_config():
    """Test create app config."""
    app = create_app(name='test', mode='test', settings_module='tests.test_server')
    config = copy.copy(app.config)
    config.update({
        'BLUEPRINTS': [],
        'SENTRY_DSN': None,
        'MEMCACHED_SERVERS': [],
        'TRANSACTION_COMMIT_STATUS_CODES': [httplib.OK, httplib.CREATED],
        'LOG_FACILITY': 'test',
        'LOG_USER_ERRORS': False,
        'LOG_USER_ERROR_EXC_INFO': False,
        'LOG_USER_ERROR_LEVEL': logging.DEBUG,
        'SENTRY_CAPTURE_USER_ERRORS': False,
        'SERVICE_NAME': 'atilla',
        'MEMCACHED_COUNTER_TIME': 3600,
        'HOST': 'localhost',
        'PORT': '8080',
        'DEBUG': False,
        'LANGUAGES': ['en'],
    })
    assert app.config == config
