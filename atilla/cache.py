"""Caching utils."""

from flask import current_app


def increase_memcached_counter(status_code):
    """Increase the memcached counter for every Response STATUS CODE.

    If the counter does not exist yet, it creates a new one and stores it
    for a number of seconds specified in :ref: `settings.Config.MEMCACHED_COUNTER_TIME`.

    :param status_code: property of flask.Response object.
    :param memcached_client: client to memcached.
    :param namespace: namespace for keys.
    """
    namespace = current_app.config['SERVICE_NAME']

    key = '{namespace}-{status_code}'.format(
        namespace=namespace,
        status_code=status_code
    )
    # .add() only creates the key if it does not exist
    current_app.cache.add(key=key, value='0', timeout=current_app.config['MEMCACHED_COUNTER_TIME'])
    current_app.cache.cache.inc(key=key)
