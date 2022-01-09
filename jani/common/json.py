from __future__ import annotations
from enum import Enum
from abc import ABCMeta, abstractmethod
from collections.abc import Set, Mapping, Sequence, Callable
from dataclasses import is_dataclass
import uuid
import decimal
import typing as t
from datetime import datetime, time, date, timedelta
import warnings
import orjson
import json as stdjson

from enum import IntFlag, unique

from functools import partial, reduce
from jani.common.collections import fallbackdict
from jani.common.functools import export


T_Jsonable = t.TypeVar('T_Jsonable', bound='Jsonable', covariant=True)

def _json(o):
    return 

def _get_default_encoder(typ):
    if hasattr(typ, '__json__'):
        __type_defaults[typ] = typ.__json__
    elif issubclass(typ, Mapping):
        __type_defaults[typ] = dict
    elif issubclass(typ, Enum):
        __type_defaults[typ] = Jsonable.attr_getter('value')
    elif issubclass(typ, decimal.Decimal):
        __type_defaults[typ] = str
    elif issubclass(typ, (Sequence, Set)):
        __type_defaults[typ] = tuple
    # elif issubclass(typ, (time, date, datetime)):
    #     __type_defaults[typ] = typ.isoformat
    elif issubclass(typ, Jsonable):
        __type_defaults[typ] = Jsonable.method_caller()
    else:
        __type_defaults[typ] = None
    return __type_defaults[typ]
    
    
__type_defaults = fallbackdict[type, Callable[..., 'Jsonable']](_get_default_encoder)



JSONDecodeError = orjson.JSONDecodeError
JSONEncodeError = orjson.JSONEncodeError




@export()
class Jsonable(metaclass=ABCMeta):
    
    __slots__ = ()

    @classmethod
    def __subclasshook__(cls, klass) -> bool:
        if cls is Jsonable:
            return hasattr(klass, '__json__') or is_dataclass(klass)
        return NotImplemented

    @abstractmethod
    def __json__(self) -> Jsonable:
        ...

    @classmethod
    def method_caller(cls, obj, name='__json__', *, default=...):
        default_fn = callable(default) and default
        def __json__(obj):
            fn = getattr(obj, name, None)
            if fn is None:
                if default is ...:
                    raise AttributeError(name)
                elif default_fn is False:
                    return default
                fn = default_fn
            return fn()

    @classmethod
    def attr_getter(cls, name, *, default=...):
        def __json__(obj):
            rv = getattr(obj, name, default)
            if rv is ... is default:
                raise AttributeError(name)
            return rv
    
    


Jsonable.register(time)
Jsonable.register(date)
Jsonable.register(datetime)
Jsonable.register(decimal.Decimal)
Jsonable.register(uuid.UUID)
Jsonable.register(Set)
Jsonable.register(Sequence)
Jsonable.register(Mapping)
Jsonable.register(str)
Jsonable.register(bytes)
Jsonable.register(int)
Jsonable.register(float)
Jsonable.register(list)
Jsonable.register(tuple)
Jsonable.register(dict)
Jsonable.register(type(None))



@export()
@unique
class JsonOpt(IntFlag):

    INDENT_2 =  orjson.OPT_INDENT_2
        
    NAIVE_UTC = orjson.OPT_NAIVE_UTC
    NON_STR_KEYS = orjson.OPT_NON_STR_KEYS
    OMIT_MICROSECONDS = orjson.OPT_OMIT_MICROSECONDS
    SERIALIZE_NUMPY = orjson.OPT_SERIALIZE_NUMPY
    SORT_KEYS = orjson.OPT_SORT_KEYS
    STRICT_INT = orjson.OPT_STRICT_INTEGER
    UTC_Z = orjson.OPT_UTC_Z

    PASSTHROUGH_SUBCLASS = orjson.OPT_PASSTHROUGH_SUBCLASS
    PASSTHROUGH_DATETIME = orjson.OPT_PASSTHROUGH_DATETIME

    APPEND_NEWLINE = orjson.OPT_APPEND_NEWLINE
    PASSTHROUGH_DATACLASS = orjson.OPT_PASSTHROUGH_DATACLASS

    ORJSON_OPT = reduce(lambda r, k: r | getattr(orjson, f'OPT_{k}', 0), vars(), 0)

    DECODE = PASSTHROUGH_DATETIME << 8
    




def to_jsonable(o):
    enc = __type_defaults[o.__class__]
    if enc is None:
        raise TypeError(o)
    return enc(o) 
        


def _get_default_fn(default=None):
    if default is not None:
        def _to_jsonable(o): 
            return (__type_defaults[o.__class__] or default)(o)
        return _to_jsonable
    return to_jsonable




@export()
def dumps(obj: Jsonable, default: t.Callable[[t.Any], Jsonable]=None, opts: JsonOpt=0) -> t.AnyStr:
    """Serialize ``obj`` to a JSON formatted ``bytes``
    Uses ``orjson`` if available or falls back to the standard ``json`` library.
    """
    if opts & JsonOpt.DECODE:
        opts = opts & JsonOpt.ORJSON_OPT
        return orjson.dumps(obj, _get_default_fn(default), int(opts)).decode()
    else:
        return orjson.dumps(obj, _get_default_fn(default), int(opts))
    


@export()
def dumpstr(obj: Jsonable, default: t.Callable[[t.Any], Jsonable]=None, opts: JsonOpt=0) -> str:
    """Serialize ``obj`` to a JSON formatted ``bytes``
    Uses ``orjson`` if available or falls back to the standard ``json`` library.
    """
    return dumps(obj, default, opts | JsonOpt.DECODE)
    


# @export()
# def dumps(obj: Jsonable, *, default: t.Callable[[t.Any], Jsonable]=None, flags: JsonOpt=0):
#     """Serialize ``obj`` to a JSON formatted ``bytes`` or ``str``.
#     Uses ``orjson`` if available or falls back to the standard ``json`` library.
#     """
#     return dumpb(obj, default=default, flags=flags) #.decode()



if t.TYPE_CHECKING:
    @export()
    def loads(s: t.AnyStr):
        """Unserialize a JSON object from a string ``s``.
        Uses ``orjson`` if available or falls back to the standard ``json`` library.
        """
        
    @export()
    def loadstr(s: t.AnyStr):
        """Unserialize a JSON object from a string ``s``.
        Uses ``orjson`` if available or falls back to the standard ``json`` library.
        """
else:
    loads = export(orjson.loads)
    loadstr = export(loads, name='loadstr')

