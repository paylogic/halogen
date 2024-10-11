"""Halogen basic types."""
import datetime
import decimal
import enum
import typing
from typing import Union, Optional, Any

import dateutil.parser
import isodate
import pytz

from .exceptions import ValidationError

if typing.TYPE_CHECKING:
    from .schema import _Schema


class Type(object):
    """Base class for creating types."""

    def __init__(self, validators=None, *args, **kwargs):
        """Type constructor.

        :param validators: A list of :class:`halogen.validators.Validator` objects that check the validity of the
            deserialized value. Validators raise :class:`halogen.exception.ValidationError` exceptions when
            value is not valid.
        """
        self.validators = validators or []

    def serialize(self, value, **kwargs):
        """Serialization of value."""
        return value

    def deserialize(self, value, **kwargs):
        """Deserialization of value.

        :return: Deserialized value.
        :raises: :class:`halogen.exception.ValidationError` exception if value is not valid.
        """
        validation_exceptions = []
        for validator in self.validators:
            try:
                validator.validate(value, **kwargs)
            except ValidationError as e:
                validation_exceptions.append(e)

        if len(validation_exceptions) > 0:
            raise ValidationError(validation_exceptions)

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
        super().__init__(*args, **kwargs)
        self.item_type = item_type or Type()
        self.allow_scalar = allow_scalar

    def serialize(self, value, **kwargs):
        """Serialize every item of the list."""
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        return super().serialize([self.item_type.serialize(val, **kwargs) for val in value], **kwargs)

    def deserialize(self, value, **kwargs):
        """Deserialize every item of the list."""
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        if not isinstance(value, (list, tuple)):
            if self.allow_scalar:
                value = [value]
            else:
                raise ValidationError('"{}" is not a list'.format(value))
        value = super().deserialize(value)
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
        return super().deserialize(result, **kwargs)


class ISODateTime(Type):
    """ISO-8601 datetime schema type."""

    type = "datetime"
    message = u"'{val}' is not a valid ISO-8601 datetime"

    def serialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        return super().serialize(value.isoformat(), **kwargs)

    def deserialize(self, value, **kwargs):
        value = value() if callable(value) else value
        try:
            dateutil.parser.parse(value)
            value = getattr(isodate, "parse_{0}".format(self.type))(value)
        except (isodate.ISO8601Error, ValueError):
            raise ValueError(self.message.format(val=value))

        return super().deserialize(value)


class ISOUTCDateTime(Type):
    """ISO-8601 datetime schema type in UTC timezone."""

    type = "datetime"
    message = u"'{val}' is not a valid ISO-8601 datetime"

    def format_as_utc(self, value):
        """Format UTC times."""
        if isinstance(value, datetime.datetime):
            if value.tzinfo is not None:
                value = value.astimezone(pytz.UTC)
            value = value.replace(microsecond=0)
        return value.isoformat().replace("+00:00", "Z")

    def serialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        return super().serialize(self.format_as_utc(value), **kwargs)

    def deserialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        value = value() if callable(value) else value
        try:
            dateutil.parser.parse(value)
            value = getattr(isodate, "parse_{0}".format(self.type))(value)
        except (isodate.ISO8601Error, ValueError):
            raise ValueError(self.message.format(val=value))

        return super().deserialize(value)


class ISOUTCDate(ISOUTCDateTime):
    """ISO-8601 date schema type in UTC timezone."""

    type = "date"
    message = u"'{val}' is not a valid ISO-8601 date"


class String(Type):
    """String schema type."""

    def serialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        return super().serialize(str(value), **kwargs)

    def deserialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        return super().deserialize(str(value), **kwargs)


class Int(Type):
    """Int schema type."""

    def serialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        return super().serialize(int(value), **kwargs)

    def deserialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        try:
            value = int(value)
        except ValueError:
            raise ValueError(u"'{val}' is not an integer".format(val=value))
        return super().deserialize(value, **kwargs)


class Boolean(Type):
    """Boolean schema type."""

    def serialize(self, value, **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")
        return super().serialize(bool(value), **kwargs)

    def deserialize(self, value: Union[str, int, bool, None], **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        if isinstance(value, int):
            if value not in (0, 1):
                raise ValueError("'{val}' is not 1 or 0".format(val=value))
            value = bool(value)

        if isinstance(value, str):
            str_value = str(value).lower()
            if str_value not in ("0", "1", "true", "false"):
                raise ValueError("'{val}' is not 1, 0, true or false".format(val=value))

            if str_value == "true":
                value = True
            elif str_value == "false":
                value = False
            else:
                value = int(str_value)
                value = bool(value)

        return super().deserialize(value, **kwargs)


class Amount(Type):
    """Amount (money) schema type."""

    err_unknown_currency = u"'{currency}' is not a valid currency."

    def __init__(self, currencies, amount_class, **kwargs):
        """Initialize new instance of Amount.

        :param currencies: list of all possible currency codes.
        :param amount_class: class for the Amount deserialized value.
        """
        self.currencies = currencies
        self.amount_class = amount_class
        super().__init__(**kwargs)

    def amount_object_to_dict(self, amount) -> dict[str, str]:
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

    def serialize(self, value, **kwargs):
        """Serialize amount.

        :param value: Amount value.

        :return: Converted amount.
        """
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        return super().serialize(self.amount_object_to_dict(value), **kwargs)

    def deserialize(self, value, **kwargs):
        """Deserialize the amount.

        :param value: Amount in CURRENCYAMOUNT or {"currency": CURRENCY, "amount": AMOUNT} format. For example EUR35.50
            or {"currency": "EUR", "amount": "35.50"}

        :return: A paylogic Amount object.
        :raises ValidationError: when amount can"t be deserialzied
        :raises ValidationError: when amount has more than 2 decimal places
        """
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        if isinstance(value, str):
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
            raise ValueError(u"'{amount}' cannot be parsed to decimal.".format(amount=amount))

        if amount.as_tuple().exponent < -2:
            raise ValueError(u"'{amount}' has more than 2 decimal places.".format(amount=amount))

        value = self.amount_class(currency=currency, amount=amount)
        return super().deserialize(value)


class Nullable(Type):
    """Nullable type."""

    def __init__(self, nested_type: Union[type[Type], Type, "_Schema"], *args, **kwargs):
        self.nested_type = nested_type
        super().__init__(*args, **kwargs)

    def serialize(self, value: Optional[Any], **kwargs):
        if value is None:
            return None
        return self.nested_type.serialize(value, **kwargs)

    def deserialize(self, value: Optional[Any], **kwargs):
        if value is None:
            return None
        return self.nested_type.deserialize(value, **kwargs)


class Enum(Type):
    """Enum schema type for enum.Enum."""

    def __init__(
        self,
        enum_type: type[enum.Enum],
        use_values: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        if not issubclass(enum_type, enum.Enum):
            raise TypeError("Must be subclass of enum.Enum.")
        self.enum_type = enum_type
        self.use_values = use_values

    def serialize(self, value: Optional[enum.Enum], **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        value = value.value if self.use_values else value.name

        return super().serialize(value, **kwargs)

    def deserialize(self, value: Optional[str], **kwargs):
        if value is None:
            raise ValueError("None passed, use Nullable type for nullable values")

        if self.use_values:
            value = self.enum_type(value)
        else:
            try:
                value = self.enum_type[value]
            except KeyError:
                raise ValueError(f"Unknown enum key: {value}")

        return super().deserialize(value, **kwargs)
