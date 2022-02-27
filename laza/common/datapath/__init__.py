from abc import abstractmethod
import typing as t 

from collections.abc import Hashable, Callable

# from enum import Enum, auto

from laza.common.collections import Arguments

_T_Obj = t.TypeVar('_T_Obj')
_T_Symbol = t.TypeVar('_T_Symbol')
_T_Args = t.TypeVar('_T_Args')
_T_Kwargs = t.TypeVar('_T_Kwargs')
_T_Item = t.TypeVar('_T_Item', int, str, Hashable)



# class TokenType(Enum):
#     attribute       = auto()
#     index           = auto()
#     key             = auto()




class Symbol(t.Generic[_T_Symbol, _T_Obj]):
    __slots__ =  'val', 

    val: _T_Symbol

    def __new__(cls, token: _T_Symbol):
        self = object.__new__(cls)
        self.val = token
        return self

    def __eq__(self, x):
        if isinstance(x, self.__class__):
            return x.val == self.val
        return False
    
    def __ne__(self, x):
        return not self.__eq__(x)

    def __repr__(self):
        return f'{self.__class__.__name__}({self!s})'

    def __str__(self):
        return str(self.val)

    def __hash__(self):
        return hash(self.val)

    @abstractmethod
    def __call__(self, o: _T_Obj):
        raise NotImplementedError(f'{self.__class__.__name__}.__eval__datapath__()')



class Attribute(Symbol[str, _T_Obj]):
    __slots__ = ()

    def __call__(self, o: _T_Obj):
        return getattr(o, self.val)

    def __str__(self):
        return f'.{self.val}'


class Item(Symbol[_T_Item, _T_Obj]):
    __slots__ = ()

    def __call__(self, o: _T_Obj):
        return o[self.val]

    def __str__(self):
        return f'[{self.val}]'



class Slice(Symbol[tuple[t.Union[_T_Item, None], t.Union[_T_Item, None], t.Union[_T_Item, None]], _T_Obj]):

    __slots__ = ()

    def __call__(self, o: _T_Obj):
        start, stop, step = self.val
        return o[start:stop:step]

    def __str__(self):
        start, stop, step = ('' if v is None else v for v in self.val)
        return f'[{start!s}:{stop!s}:{step!s}]'



class Call(Symbol[Arguments[_T_Args, _T_Kwargs], _T_Obj]):
    __slots__ = ()
  
    def __call__(self, o: _T_Obj):
        v = self.val
        return o(*v.args, **v.kwargs)

    def __str__(self):
        v = self.val
        a = ', '.join(map(repr, v.args))
        kw = ', '.join(f'{k!s}={v!r}' for k,v in v.kwargs.items())
        return f'({", ".join(filter(None, (a, kw)))})'





class DataPath(t.Generic[_T_Obj]):

    __slots__ =  '__expr__',

    __expr__: tuple[Symbol[_T_Symbol, _T_Obj]]

    def __new__(cls, __path: tuple[Symbol[_T_Symbol, _T_Obj]]=()):
        self = object.__new__(cls)
        self.__expr__ = tuple(__path)
        return self

    def __push__(self, *exprs: Symbol[_T_Symbol, _T_Obj]):
        return self.__class__(self.__expr__ + exprs)

    def __getattr__(self, name: str):
        if  name[:2] == '__' == name[-2:]:
            raise AttributeError(name)

        return self.__push__(Attribute(name))    
    
    def __getitem__(self, k: t.Union[_T_Item, slice]):
        if k.__class__ is slice:
            return self.__push__(Slice((k.start, k.stop, k.step)))
        else:
            return self.__push__(Item(k))
           
    def __reduce__(self):
        return self.__class__, (self.__expr__,)
        
    def __eq__(self, x):
        if isinstance(x, self.__class__):
            return x.__expr__ == self.__expr__
        return False
    
    def __ne__(self, x):
        return not self.__eq__(x)
    
    def __hash__(self):
        return hash(self.__expr__)
    
    def __call__(self, *a: _T_Args, **kw: _T_Kwargs):
        return self.__push__(Call(Arguments(a, kw)))

    def __eval__(self, o: _T_Obj):
        r = o
        for t in self.__expr__:
            r = t(r)
        return r

    def __str__(self):
        return '$' + ''.join(map(str, self.__expr__))
    
    def __repr__(self):
        return f'<{self.__class__.__name__}: {self!s}>'
    