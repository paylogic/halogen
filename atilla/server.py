"""Create app stuff."""

try:
    from http import client as httplib
except ImportError:  # pragma: no cover
    import httplib
import logging
import logging.handlers
import os
import sys

from flask import Flask, current_app
from raven.contrib.flask import Sentry
from flask.ext.cache import Cache

from atilla import validators, cache, clients, exception_handlers
from atilla.wrappers import Request, Response

from werkzeug.exceptions import default_exceptions
from werkzeug.utils import import_string


class Application(Flask):

    """Flask application."""

    test_client_class = clients.TestClient
    request_class = Request
    response_class = Response


def load_blueprints(app):
    """Load the blueprints from the configuration."""
    for app_location in app.config['BLUEPRINTS']:
        app_blueprint = import_string(app_location)
        app.register_blueprint(app_blueprint)


def close_sessions_at_start():
    """Close all database sessions at the start of every request."""
    try:
        current_app.db.close()
    except Exception:
        pass


def close_sessions_at_end(*args, **kwargs):
    """Close all database sessions at the end of every request."""
    current_app.db.close()


def create_app(name, mode, app_class=None, config=None, settings_module=None):
    """Create and initialize the application.

    :param name: name of the application
    :type name: str
    :param mode: mode (environment) for the application
    :type mode: str
    :param app_class: optional class for the application object
    :type app_class: type
    :config: application config file name
    :type config: str
    :param settings_module: python settings module for the application
    :type settings_module: str

    :return: application object
    :rtype: flask.Flask
    """
    app = app_class(name) if app_class else Application(name)

    app.config.setdefault('BLUEPRINTS', [])
    app.config.setdefault('SENTRY_DSN', None)
    app.config.setdefault('MEMCACHED_SERVERS', [])
    app.config.setdefault('TRANSACTION_COMMIT_STATUS_CODES', [httplib.OK, httplib.CREATED])
    app.config.setdefault('LOG_FACILITY', 'test')
    app.config.setdefault('LOG_USER_ERRORS', False)
    app.config.setdefault('LOG_USER_ERROR_EXC_INFO', False)
    app.config.setdefault('LOG_USER_ERROR_LEVEL', logging.DEBUG)
    app.config.setdefault('SENTRY_CAPTURE_USER_ERRORS', False)
    app.config.setdefault('SERVICE_NAME', 'atilla')
    app.config.setdefault('MEMCACHED_COUNTER_TIME', 3600)
    app.config.setdefault('HOST', 'localhost')
    app.config.setdefault('PORT', '8080')
    app.config.setdefault('DEBUG', False)
    app.config.setdefault('LANGUAGES', ['en'])
    app.config.setdefault('LOG_ADDRESS', '/var/run/syslog' if sys.platform == 'darwin' else '/dev/log')

    # URL converters
    app.url_map.converters['uid'] = validators.UidValidator

    # Load the configuration
    config_name = u'{0}Config'.format(mode.lower().title())
    try:
        app.config.from_object(
            u'{0}.{1}'.format(settings_module, config_name)
        )
        if config and os.path.exists(config):
            app.config.from_pyfile(config)
    except ImportError:
            raise RuntimeError(u"Can't find {0} in {1}".format(config_name, settings_module))

    # Setup the error handlers
    for code in default_exceptions:
        app.error_handler_spec[None][code] = exception_handlers.exception_handler

    app.register_error_handler(Exception, exception_handlers.exception_handler)

    # Setup Logging
    if app.config['SENTRY_DSN']:
        app.sentry = Sentry(app)
    # Setup cache
    if app.config['MEMCACHED_SERVERS']:
        app.cache = Cache(app, config={
            'CACHE_TYPE': 'memcached',
            'CACHE_MEMCACHED_SERVERS': app.config['MEMCACHED_SERVERS']
        })

    syslog = logging.handlers.SysLogHandler(
        facility=app.config['LOG_FACILITY'],
        address=app.config['LOG_ADDRESS'],
    )
    syslog.setLevel(logging.DEBUG)

    app.logger.addHandler(syslog)

    # Setup endpoints (blueprints)
    with app.app_context():
        load_blueprints(app)

    app.before_request(close_sessions_at_start)
    app.teardown_request(close_sessions_at_end)
    app.after_request(after_request)

    return app


def after_request(response, *args, **kwargs):
    """Log requests and response.

    :param response: flask.Response object.
    :param *args: Required by Flask, but unused.
    :param **kwargs: Required by Flask, but unused.

    :return: flask.Response object.
    """
    if current_app.config['MEMCACHED_SERVERS']:
        cache.increase_memcached_counter(status_code=response.status_code)

    if response.status_code in current_app.config['TRANSACTION_COMMIT_STATUS_CODES']:
        current_app.db.commit()
    else:
        current_app.db.rollback()

    return response
