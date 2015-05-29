"""Tests for atilla/cache.py."""
import mock

from atilla import cache


@mock.patch('werkzeug.contrib.cache.time')
def test_increase_memcached_counter(mocked_time, mocked_memcached, current_app):
    """Increase the memcached counter for every Response STATUS CODE."""
    mocked_time.return_value = 0
    current_app.config['MEMCACHED_COUNTER_TIME'] = 0
    current_app.config['SERVICE_NAME'] = 'namespace'
    cache.increase_memcached_counter('status_code')

    key = 'flask_cache_{namespace}-{status_code}'.format(
        namespace='namespace',
        status_code='status_code'
    )
    mocked_memcached.return_value.add.assert_called_with(key, '0', 0)
    mocked_memcached.return_value.incr.assert_called_with(key, 1)
