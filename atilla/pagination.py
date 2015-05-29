"""Helperfunctions for pagination."""
import collections
import math

from six.moves import http_client
from six.moves.urllib import parse as urlparse
from flask import url_for, current_app

from atilla import exceptions

PageResponse = collections.namedtuple('PageResponse', 'content,count')


def parse_current_page(page):
    """Get page number from page number string.

    :param page: page number
    :type page: str

    :return: `int` parsed page number
    :raises: atilla.exceptions.ApiException - when given page is not an integer or less than 1
    """
    try:
        page = int(page)
    except TypeError:
        message = description = 'Page is not an integer.'
        raise exceptions.ApiException(
            message=message,
            description=description,
            status_code=http_client.BAD_REQUEST,
        )

    if page <= 0:
        message = description = 'The supplied page number is less than 1.'
        raise exceptions.ApiException(
            message=message,
            status_code=http_client.BAD_REQUEST,
            description=description,
        )

    return page


class Page(object):

    """Current page."""

    def __init__(self, func, page):
        """Intialize current page.

        :param func: Function for getting items.
        :param page: Requested page.
        """
        limit_per_page = current_app.config['OBJECTS_PER_PAGE']

        def get_response():
            return func(
                limit=limit_per_page,
                offset=0 if page == 1 else limit_per_page * (page - 1),
            )

        response = get_response()
        self.number_pages = int(math.ceil(float(response.count) / limit_per_page))

        if page > self.number_pages >= 1:
            page = self.number_pages
            response = get_response()

        self.number = page
        self.content = response.content
        self.item_count = response.count

    def has_next_page(self):
        """Helper function for checking that we have next page depends on number of page and number of pages.

        :return: Boolean.
        """
        return self.number < self.number_pages

    def has_prev_page(self):
        """Helper function for checking that we have next page depends on number of page.

        :return: Boolean.
        """
        return self.number > 1


def calculate_first_next_prev_last_links(page, collection_uri):
    """Helper function which updates response with next and prev links.

    :param page: Instance of Page class.
    :param collection_uri: name of the flask route to use as a collection url for pagination links.
    :return: Dictionary with links.
    """
    links = {}
    if page.has_next_page():
        links['next'] = urlparse.urljoin(url_for(collection_uri, _external=True), '?page={0}'.format(page.number + 1))

    if page.has_prev_page():
        links['prev'] = urlparse.urljoin(url_for(collection_uri, _external=True), '?page={0}'.format(page.number - 1))

    if page.number_pages > 1:
        links['last'] = urlparse.urljoin(url_for(collection_uri, _external=True), '?page={0}'.format(page.number_pages))

    if page.number > 1:
        links['first'] = url_for(collection_uri, _external=True)

    return links
