"""Utility functions."""

from flask import current_app


def to_i18n_dict(messages):
    """Convert to I18N dictionary.

    Copies the same value for all the provided languages, and creates empty value for the non provided ones.

    :param messages: A `dict` of messages to convert to i18n object for all available languages.
    :type messages: `dict`

    :return: `dict` containing the message for the all the supported languages.
    """
    return dict((lang, messages.get(lang, u"") if messages else u"") for lang in current_app.config['LANGUAGES'])
