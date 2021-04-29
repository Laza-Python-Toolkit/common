from contextlib import ExitStack
import logging
from collections.abc import Collection
from functools import partial
from itertools import chain
from threading import Lock
from typing import ClassVar, Generic

from djx.common.collections import fallbackdict, fluentdict, PriorityStack

from flex.utils import text
from flex.utils.decorators import export, lookup_property, cached_property
from flex.utils.metadata import metafield, BaseMetadata, get_metadata_class



from .providers import ValueResolver, provide
from .symbols import _ordered_id
from .injectors import Injector
from .abc import ScopeAlias, ScopeConfig, T_ContextStack, T_Injectable, T_Injector, T_Provider, _T_Providers, _T_Cache, _T_Conf, _T_Scope
from . import abc


logger = logging.getLogger(__name__)



_config_lookup = partial(lookup_property, lookup='config', read_only=True)



@export()
class Config(BaseMetadata[_T_Scope], ScopeConfig, Generic[_T_Scope, T_Injector, T_ContextStack]):

    is_abstract = metafield[bool]('abstract', default=False)

    @metafield[int]()
    def _pos(self, value) -> int:
        return _ordered_id()
    
    @metafield[str](inherit=True)
    def name(self, value: str, base: str=None) -> str:
        if not self.is_abstract:
            rv = value or base or self.target.__name__
            assert rv.isidentifier(), f'Scope name must be avalid identifier.'
            return self.target._get_scope_name(rv)
        
    @metafield[int](inherit=True)
    def priority(self, value, base=1) -> int:
        return base or 0 if value is None else value or 0
    
    @metafield[bool](inherit=True, default=None)
    def embedded(self, value, base=False):
        return value if value is not None else base
    
    @metafield[bool](inherit=True, default=None)
    def implicit(self, value, base=False):
        return value if value is not None else base
    
    @metafield[type[_T_Cache]](inherit=True)
    def cache_factory(self, value, base=None) -> type[_T_Cache]:
        return value or base or dict
    
    @metafield[type[T_ContextStack]](inherit=True)
    def context_factory(self, value, base=None) -> type[_T_Cache]:
        return value or base or abc.InjectorContext
    
    @metafield[type[T_Injector]](inherit=True)
    def injector_factory(self, value, base=None) -> type[T_Injector]:
        return value or base or Injector
    
    @metafield[list[str]](inherit=True)
    def depends(self, value: Collection[str], base=()) -> list[str]:
        _seen = set((self.name,))
        tail = (abc.Scope.ANY, abc.Scope.MAIN)
        self.embedded and _seen.update(tail)

        seen = lambda p: p in _seen or _seen.add(p)
        value = value if value is not None else base or ()
        value = value if self.embedded else chain((v for v in value if v not in tail), tail)
        return [p for p in value if not seen(p)]

    def __order__(self):
        return self.priority, self._pos
        



@export
@abc.ScopeConfig.register
class ScopeType(abc.ScopeType):
    
    config: _T_Conf
    __instance__: _T_Scope
    

    def __new__(mcls, name, bases, dct) -> 'ScopeType[_T_Scope]':
        raw_conf = dct.get('Config')
        
        meta_use_cls = raw_conf and getattr(raw_conf, '__use_class__', None)
        meta_use_cls and dct.update(__config_class__=meta_use_cls)

        cls: ScopeType[_T_Scope, _T_Conf] = super().__new__(mcls, name, bases, dct)

        conf_cls = get_metadata_class(cls, '__config_class__', base=Config, name='Config')
        conf_cls(cls, 'config', raw_conf)
        
        cls._is_abstract() or cls._register_scope_type()
        
        return cls
    
    def __repr__(cls) -> str:
        return f'<ScopeType({cls.__name__}, {cls.config!r}>'
    
    def __str__(cls) -> str:
        return f'<ScopeType({cls.__name__}, {cls.config.name!r}>'

    


@export
class Scope(abc.Scope, metaclass=ScopeType[_T_Scope, _T_Conf, T_Provider]):
    """"""

    config: ClassVar[_T_Conf]
    __pos: int
    class Config:
        abstract = True

    name: str = _config_lookup()
    embedded: bool = _config_lookup()
    priority: int = _config_lookup()
    cache_factory: type[_T_Cache] = _config_lookup()
    context_factory: type[T_ContextStack] = _config_lookup()
    injector_factory: type[T_Injector] = _config_lookup()
    
    def __init__(self):
        self.__pos = 0
        super().__init__()

    @property
    def is_ready(self):
        return self.__pos > 0

    @property
    def embeds(self):
        return list(s for s in self.depends if s.embedded)

    @cached_property
    def depends(self):
        return dict((d, d) for d in sorted(self._iter_depends()))
          
    @property
    def parents(self):
        return list(s for s in self.depends if not s.embedded)

    @property
    def resolvers(self):
        try:
            return self._resolvers
        except AttributeError:
            return self._make_resolvers()
        finally:
            self.prepare()

        # rv = fluentdict(p.setup(self) (p.abstract, p) for p in self.providerstack.values())
        # rv = fluentdict(p.setup(self) for p in self.providers.values())
        # self.prepare()
        # return rv

    @cached_property
    def providers(self):
        rv = self._make_providers()
        return rv
           
    @classmethod
    def _implicit_bases(cls):
        return ImplicitScope,
    
    # def get_resolver(self, key):
    #     if key in self._resolvers:
    #         return self._resolvers[key]
    #     return self._resolvers.setdefault(key, self._make_resolver(key))

    def prepare(self: _T_Scope, *, strict=False) -> _T_Scope:
        if self.is_ready:
            if strict:
                raise RuntimeError(f'Scope {self} already prepared')
        else:
            self._prepare()
            self.__pos = _ordered_id()
            self.ready()
        return self
    
    def _prepare(self):
        logger.debug(f'prepare({self})')

    def _make_providers(self) -> _T_Providers:
        stack = PriorityStack()
        for embed in sorted(self.embeds):
            stack.update(embed.providers)
        
        provide(Scope[self.name], alias=Injector, scope=self.name, priority=-1)
        stack.update(self.__class__._providers)
        return stack
    
    def _make_resolvers(self):
        def fallback(key):
            if key in self.providers:
                self._resolvers[key] = self.providers[key].bind( None )
            return self._resolvers.setdefault(key, None)

        self._resolvers = fallbackdict(fallback)
        # self._setup_resolvers()
        return self._resolvers

    def bootstrap(self, inj: T_Injector) -> T_Injector:
        logger.debug(f' + bootstrap({self}):  {inj}')

        self.prepare()

        self.setup_resolvers(inj)

        return inj

    def setup_resolvers(self, inj: T_Injector):
        content: fallbackdict
        parent = inj.parent.content

        def fallback(key):
            res = self.resolvers[key]
            # if res is None:
                # content[key] = parent[key]
                # return parent[key]
            # else:
                # content[key] = res and res.bind(inj)   
            content[key] = res and res.bind(inj)   
            return content[key]  # or inj.parent.providers[key]

        content = fallbackdict(fallback)
        content[type(inj)] = ValueResolver(type(inj), inj, bound=inj)
        inj.content = content
        

    def dispose(self, inj: T_Injector):
        logger.debug(f' x dispose({self}):  {inj}')
        inj.content = None

    def create(self, parent: T_Injector) -> T_Injector:
        if self in parent:
            return parent
            
        for scope in self.parents:
            if scope not in parent:
                parent = scope.create(parent)
    
        logger.debug(f'create({self}): {parent=}')
    
        return self.injector_factory(self, parent)
    
    def create_context(self, inj: T_Injector) -> T_ContextStack:
        return self.config.context_factory(inj)

    def create_exitstack(self, inj: T_Injector) -> ExitStack:
        return ExitStack()

    def _iter_depends(self):
        for n in self.config.depends:
            yield Scope(n)

    def __contains__(self, x) -> None:
        return x == self or any(True for s in self.depends if x in s)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}#{self.config._pos}({self.config.name!r} #{self.is_ready and self.__pos or ""})'

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}#{self.config._pos}({self.config.name!r}, #{self.is_ready and self.__pos or ""}, {self.config!r})'






class ImplicitScope(Scope):
    class Config:
        abstract = True
        implicit = True
        embedded = True
        priority = -1
        





class AnyScope(Scope):
    class Config:
        name = Scope.ANY
        embedded = True






class MainScope(Scope):

    class Config:
        name = Scope.MAIN





class LocalScope(Scope):

    class Config:
        name = Scope.LOCAL
        embedded = True




class ConsoleScope(Scope):

    class Config:
        name = 'console'
        depends = [
            Scope.LOCAL
        ]
        




class RequestScope(Scope):

    class Config:
        name = 'request'
        depends = [
            Scope.LOCAL
        ]
        














