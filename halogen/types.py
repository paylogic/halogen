"""Halogen basic types."""
import datetime
import decimal

import isodate
import pytz
import six

from .exceptions import ValidationError


class Type(object):

    """Base class for creating types."""

    def __init__(self, validators=None, *args, **kwargs):
        """Type constructor.

        :param validators: A list of :class:`halogen.validators.Validator` objects that check the validity of the
            deserialized value. Validators raise :class:`halogen.exception.ValidationError` exceptions when
            value is not valid.
        """
        self.validators = validators or []

    def serialize(self, value):
        """Serialization of value."""
        return value

    def deserialize(self, value):
        """Deserialization of value.

        :return: Deserialized value.
        :raises: :class:`halogen.exception.ValidationError` exception is value is not valid.
        """
        for validator in self.validators:
            validator.validate(value)

        return value

    @staticmethod
    def is_type(value):
        """Determine if value is an instance or subclass of the class Type."""
        if isinstance(value, type):
            return issubclass(value, Type)
        return isinstance(value, Type)


class List(Type):

    """List type for Halogen schema attribute."""

    def __init__(self, item_type=None, allow_scalar=False, *args, **kwargs):
        """Create a new List.

        :param item_type: Item type or schema.
        :param allow_scalar: Automatically convert scalar value to the list.
        """
        super(List, self).__init__(*args, **kwargs)
        self.item_type = item_type or Type()
        self.allow_scalar = allow_scalar

    def serialize(self, value, **kwargs):
        """Serialize every item of the list."""
        return [self.item_type.serialize(val, **kwargs) for val in value]

    def deserialize(self, value, **kwargs):
        """Deserialize every item of the list."""
        if self.allow_scalar and not isinstance(value, (list, tuple)):
            value = [value]
        value = super(List, self).deserialize(value)
        result = []
        errors = []

        for index, val in enumerate(value):
            try:
                result.append(self.item_type.deserialize(val, **kwargs))
            except ValidationError as exc:
                exc.index = index
                errors.append(exc)
        if errors:
            raise ValidationError(errors)
        return result


class ISOUTCDateTime(Type):

    """ISO-8601 datetime schema type in UTC timezone."""

    type = "datetime"
    message = u"'{val}' is not a valid ISO-8601 datetime"
    format = "%Y-%m-%dT%H:%MZ"

    def format_as_utc(self, value):
        """Format UTC times."""
        if isinstance(value, datetime.datetime):
            if value.tzinfo is not None:
                value = value.astimezone(pytz.UTC)
        return value.strftime(self.format)

    def serialize(self, value, **kwargs):

        return self.format_as_utc(value) if value else None

    def deserialize(self, value, **kwargs):
        value = value() if callable(value) else value
        try:
            value = getattr(isodate, "parse_{0}".format(self.type))(value)
        except (isodate.ISO8601Error, ValueError):
            raise ValueError(self.message.format(val=value))

        return super(ISOUTCDateTime, self).deserialize(value)


class ISOUTCDate(ISOUTCDateTime):

    """ISO-8601 date schema type in UTC timezone."""

    type = "date"
    message = u"'{val}' is not a valid ISO-8601 date"
    format = "%Y-%m-%d"


class String(Type):

    """String schema type."""

    def serialize(self, value, **kwargs):
        if value:
            return six.text_type(super(String, self).serialize(value))
        return ""

    def deserialize(self, value, **kwargs):
        if value is not None:
            return super(String, self).deserialize(value)
        return ""


class Int(Type):

    """Int schema type."""

    def serialize(self, value, **kwargs):
        return int(value) if value is not None else None

    def deserialize(self, value, **kwargs):
        try:
            value = int(value) if value is not None else None
        except ValueError:
            raise ValueError("'{val}' is not an integer".format(val=value))
        return super(Int, self).deserialize(value, **kwargs)


class Boolean(Type):

    """Boolean schema type."""

    def serialize(self, value, **kwargs):
        return bool(value) if value is not None else None

    def deserialize(self, value, **kwargs):
        try:
            value = int(value)
            value = bool(value) if value == 1 or value == 0 else None
        except ValueError:
            str_value = str(value).lower()
            if str_value == "true":
                value = True
            elif str_value == "false":
                value = False

        if not isinstance(value, bool):
            raise ValueError("'{val}' is not an 1 or 0 and true or false".format(val=value))

        return value


class Amount(Type):

    """Amount (money) schema type."""

    err_unknown_currency = "'{currency}' is not a valid currency."

    def __init__(self, currencies, amount_class, **kwargs):
        """Initialize new instance of Amount.

        :param currencies: list of all possible currency codes.
        :param amount_class: class for the Amount deserialized value.
        """
        self.currencies = currencies
        self.amount_class = amount_class
        super(Amount, self).__init__(**kwargs)

    def amount_object_to_dict(self, amount):
        """Return the dictionary representation of an Amount object.

        Amount object must have amount and currency properties and as_tuple method which will return (currency, amount)
        and as_quantized method to quantize amount property.

        :param amount: instance of Amount object

        :return: dict with amount and currency keys.
        """
        currency, amount = (
            amount.as_quantized(digits=2).as_tuple()
            if not isinstance(amount, dict)
            else (amount["currency"], amount["amount"])
        )
        if currency not in self.currencies:
            raise ValueError(self.err_unknown_currency.format(currency=currency))
        return {
            "amount": str(amount),
            "currency": str(currency),
        }

    def serialize(self, value):
        """Serialize amount.

        :param value: Amount value.

        :return: Converted amount.
        """
        if value is None:
            return None
        return self.amount_object_to_dict(value)

    def deserialize(self, value, **kwargs):
        """Deserialize the amount.

        :param value: Amount in CURRENCYAMOUNT or {"currency": CURRENCY, "amount": AMOUNT} format. For example EUR35.50
            or {"currency": "EUR", "amount": "35.50"}

        :return: A paylogic Amount object.
        :raises ValidationError: when amount can"t be deserialzied
        :raises ValidationError: when amount has more than 2 decimal places
        """
        if value is None:
            return None

        if isinstance(value, six.string_types):
            currency = value[:3]
            amount = value[3:]
        elif isinstance(value, dict):
            if set(value.keys()) != set(("currency", "amount")):
                raise ValueError("Amount object has to have currency and amount fields.")
            amount = value["amount"]
            currency = value["currency"]
        else:
            raise ValueError("Value cannot be parsed to Amount.")

        if currency not in self.currencies:
            raise ValueError(self.err_unknown_currency.format(currency=currency))

        try:
            amount = decimal.Decimal(amount).normalize()
        except decimal.InvalidOperation:
            raise ValueError("'{amount}' cannot be parsed to decimal.".format(amount=amount))

        if amount.as_tuple().exponent < - 2:
            raise ValueError("'{amount}' has more than 2 decimal places.".format(amount=amount))

        value = self.amount_class(currency=currency, amount=amount)
        return super(Amount, self).deserialize(value)
