import abc
import collections
import datetime
import enum


_PRIMITIVE_TYPES = {int, float, bool, str, type(None)}


class UpdateHistory:
    def __init__(self, attribute: str, value, time_of_update: datetime.datetime):
        self.attribute = attribute
        self.value = value
        self.time_of_update = time_of_update

    def __repr__(self) -> str:
        return "{0}(attribute='{1}', value={2}, time_of_update={3})".format(
            type(self).__name__,
            self.attribute,
            self.value,
            self.time_of_update
        )

    def __str__(self) -> str:
        return repr(self)



class Recordable:
    """
    A base class used to monitor, track, and audit an object's history.
    Deriving a class from Recordable will allow all updates to its properties to be recorded and stored.
    Update times are captured in UTC.

    Recordable.__init__(self) MUST be the very first step that happens in the derived class' __init__ method.
    """
    _whitelisted_fields = {
        '_whitelisted_fields',
        '_history',
        '_recordable_types',
        '_size'
    }


    def __init__(self, recordable_types=_PRIMITIVE_TYPES):
        """
        recorded_types is a container of types that are to be recorded.
        If None, record all values.
        If empty, record no values.

        Recordable.__init__(self) MUST be the very first step that happens in the derived class' __init__ method.
        """
        self._history = collections.defaultdict(list)
        self._recordable_types = recordable_types
        self._size = 0


    @property
    def recordable_types(self) -> {type}:
        return self._recordable_types


    @recordable_types.setter
    def recordable_types(self, new_recordable_types: {type}) -> None:
        self._recordable_types = new_recordable_types


    def __setattr__(self, name: str, value):
        super().__setattr__(name, value)
        if name not in self._whitelisted_fields:
            value_to_record = value if self.should_record_value(value) else None
            self._update(name, value_to_record)
            self._size += 1


    def last_modification(self) -> UpdateHistory:
        """
        Returns the last update that occurred, or None if there haven't been any.
        """
        return self._history[-1] if self._history else None


    def diff_count(self) -> int:
        """
        Returns the total number of updates that have been captured so far.
        """
        return self._size


    def timeline(self, descending=True) -> [UpdateHistory]:
        """
        Returns a one-dimensional list of all updates that have been captured, ordered by time-of-update.
        If descending=True, order the list from most-recent to least-recent update.
        Otherwise, order from least-recent to most-recent.
        """
        updates = []
        for records in self._history.values():
            updates.extend(records)

        return sorted(updates, key=lambda update: update.time_of_update, reverse=descending)


    def report(self) -> {str: [UpdateHistory]}:
        """
        Returns a dictionary whose keys are string attribute fields,
        and values are a list of updates that those fields have gone through.
        """
        return dict(self._history)


    def should_record_value(self, value) -> bool:
        """
        Override this method to determine what values should be recorded.
        By default, it will ensure that the value's type is in the recorded_types container with which the object was initialized.
        Return True if the value should be recorded, or False if not.
        If a value should not be recorded, its attribute and time will still be captured. Only the actual value will be skipped.
        """
        return self.recordable_types is None or type(value) in self.recordable_types


    def _update(self, attribute: str, value) -> None:
        """
        Given the attribute and value passed into __setattr__,
        process and record this update.
        """
        time_of_update = datetime.datetime.utcnow()
        update = UpdateHistory(attribute, value, time_of_update)
        self._history[attribute].append(update)



class IntegerIdentifiable:
    __id = 0

    @classmethod
    def new_id(cls) -> int:
        result = cls.__id
        cls.__id += 1
        return result



class Serializable(metaclass=abc.ABCMeta):
    """
    Base class to represent an object that can be serialized and consumed by JsonResponse.
    Derived classes must implement the `.context()` method that returns a dictionary representing the object.
    The dictionary should consist only of JSON-compliant builtin Python types.
    Derived instances of this class should be serialized through the `serialize()` function in `pazaak.helpers.utilities`.
    """

    @abc.abstractmethod
    def context(self) -> dict:
        """
        Returns a raw dictionary representing the object.
        This will be passed into serialize().
        """
        pass

    def json(self) -> dict:
        context = self.context()
        return serialize(context)



class _SerializableEnumMeta(enum.EnumMeta, abc.ABCMeta):
    """
    Intermediate metaclass necessary for multiple inheritance with enums.
    """
    pass



class SerializableEnum(Serializable, enum.Enum, metaclass=_SerializableEnumMeta):

    @classmethod
    def should_export_to_js(cls) -> bool:
        """
        Override this to return True if the enum should be auto-exported as a JS class.
        See pazaak.enums.export_enums_to_js() for details.
        """
        return False

    def key(self) -> str:
        """
        Override this to return the value that this enum should use when it's the key in a dictionary.
        For example, if MyEnum.A = 1, then this default implementation when calling serialize() on {MyEnum.A: 'test'} results in {1: 'test'}.
        """
        return self.value

    def context(self) -> dict:
        return {
            'name': self.name,
            'value': self.value
        }


def serialize(payload):
    """
    Recursively serializes the keyword arguments into a payload that JsonResponse should be able to consume.
    Any object in the kwargs derived from Serializable will use their `.json()` method.
    Returns the serialized kwargs as a dictionary.
    """
    result = payload
    payload_type = type(payload)

    if isinstance(payload, Serializable) or issubclass(payload_type, Serializable):
        result = payload.json()

    elif isinstance(payload, dict):
        result = {}
        for field, value in payload.items():
            if isinstance(field, SerializableEnum):
                field = field.key()
            result[field] = serialize(value)

    elif isinstance(payload, list):
        result = [serialize(item) for item in payload]

    return result


if __name__ == '__main__':
    pass