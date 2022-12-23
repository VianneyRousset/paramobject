'''
Parametrizedobject definition.

Parameter must be contained in a ParametrizedObject in order to work as
expected.
'''

from abc import ABCMeta, ABC
from inspect import getmembers
from .storage import StaticDict, ParametersView
from .parameter import Parameter


from dataclasses import dataclass

class ParametrizedObjectMeta(ABCMeta):
    '''
    Metaclass for parametrized object.

    This metaclass set the name stored in each parameter. It also makes sure,
    that every parameter has its corresponding wither and all stored parameter
    has its corresponding caster.
    '''

    def __new__(cls, cls_name, bases, namespace, **kwargs):

        # iterate over each class parameter
        for name, attr in list(namespace.items()):

            if isinstance(attr, Parameter):

                # give name to parameter
                attr.name = name

                # add parameter wither if missing
                if f'with_{name}' not in namespace:
                    namespace[f'with_{name}'] = attr.wither()

                # add parameter caster for stored params if missing
                if attr.stored and f'cast_{name}' not in namespace:
                    namespace[f'cast_{name}'] = attr.caster()

        return super().__new__(cls, cls_name, bases, namespace, **kwargs)


class ParametrizedObject(ABC, metaclass=ParametrizedObjectMeta):
    '''
    Stores a unmutable collections of parameters.

    Parameters can be accessed as properties but cannot be set. For example,
    the parameter foo is retrieved as follows:

    >>> obj.foo

    Every parameter has a wither given that prefixes its name with 'with_'. A
    wither create a copy of the parametrized object with the corresponding
    paramater having a new value. For example, the following line creates a copy
    of an parametrized object with foo = 42:

    >>> newobj = obj.with_foot(42)

    In general, the method `with_params()` creates a copy of the parametrized
    object with the given parameters being changed:

    >>> newobj = obj.with_params(foo=42, bar=77)

    A view on all the object parameters can be gather using `obj.params`.
    '''

    def __init__(self, *args, **kwargs):

        super().__init__()

        self.params_storage = StaticDict(self.stored_params.keys())

        # deduce and save stored parameters values
        for name in self.stored_params:
            caster = getattr(self, f'cast_{name}')
            self.params_storage[name] = caster(*args, **kwargs)

        self.binding = None

    def with_params(self, *args, **kwargs):
        '''
        Returns a copy of the object with the given modified parameters values.

        The following lines are equivalent:

        >>> newobj = obj.with_params(foo=42, bar=77)
        >>> newobj = obj.with_params({'foo': 42, 'bar': 77})
        '''

        params = dict(*args, **kwargs)

        newobj = self.__class__(self, **params)

        if self.binding is not None:
            return self.binding.transfer(newobj)

        return newobj

    @property
    def params(self):
        '''Paramters view (mapping) of all the available parameters.'''
        cls = self.__class__
        return ParametersView(self, (name for name, attr in getmembers(cls)
                                     if isinstance(attr, Parameter)))

    @property
    def stored_params(self):
        '''Paramters view (mapping) of all the available stored parameters.'''
        return ParametersView(self, (name for name in self.params.keys()
                                     if getattr(self.__class__, name).stored))

    def bind(self, obj, name):
        '''Returns a copy of the parametrized object bound to obj.'''

        if not isinstance(obj, ParametrizedObject):
            raise TypeError(f'A ParametrizedObject is expected, got '
                            f'{type(obj)}.')

        copy = self.__class__(self)
        copy.binding = ParametrizedObjectBinding(obj, name)
        return copy

    def unbind(self):
        '''Returns a unbound copy of the parametrized object.'''
        copy = self.__class__(self)
        copy.binding = None
        return copy


@dataclass
class ParametrizedObjectBinding:

    obj: ParametrizedObject
    name: str

    def transfer(self, instance):
        return self.obj.with_params(**{self.name: instance})
