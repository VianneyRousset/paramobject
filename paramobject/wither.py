'''
Definition of ParameterWither.

Each parameter has a wither defined in its owning class. If no wither is
specified in the class using the `Parameter.wither` decorator, the
ParametrizedObjectMeta metaclass will make sure that a default will with be
present in the owning class.

A wither behaves as a method (but is actually an object) that returns a copy
of the owning object with a new parameter value. A wither name should start
with `with_`. For example, here is a parametrized class Foo with the parameter
bar:

>>> class Foo(ParametrizedObject):
...     bar = Parameter(default=42)
...

In this case a default wither `with_bar` will be created:

>>> foo = Foo()
... print(foo.bar) # prints 42
...
... newfoo = foo.with_bar(77)
... print(foo.bar) # prints 77

A custom wither can be defined using the `Parameter.wither` decorator:

>>> class Foo(ParametrizedObject):
...
...     bar = Parameter(default=42)
...
...     @bar.wither
...     def with_bar(self, val=None, maxval=None):
...
...         if val is None:
...             val = self.val
...
...         if maxval is not None:
...             val = min(val, maxval)
...
...         return self.with_params(bar=val)
'''

from types import MethodType
import paramobject


class ParameterWither: # pylint: disable=too-few-public-methods
    '''
    A helper to create new parametrized object with a new parameter value.
    '''

    def __init__(self, parameter, wither_func=None):

        if not isinstance(parameter, paramobject.Parameter):
            raise TypeError(f'A Parameter is expected, got: {type(parameter)}.')

        self.parameter = parameter
        self.wither_func = wither_func

    @property
    def wither_func(self):
        '''
        Returns the wither function to use.

        If a custom wither function is defined, the latter is returned.
        Otherwise, a default wither function is returned.
        '''

        def default_wither_func(instance, value):
            '''
            Default wither function.

            Returns a copy of the owning object with the new parameters value
            given in the __init__ **kwargs.
            '''

            # check if the parameter name is set for the default wither function
            if self.parameter.name is None:
                raise RuntimeError('A nameless parameter cannot use the '
                                   'default wither function')

            return instance.with_params({self.parameter.name: value})

        if self._wither_func is None:
            return default_wither_func

        return self._wither_func

    @wither_func.setter
    def wither_func(self, func):

        if func is not None and not callable(func):
            raise TypeError('The wither function must be callable.')

        self._wither_func = func

    def __get__(self, instance, owner=None):

        if instance is None:
            return self

        # return the wither function bound to the instance
        return MethodType(self.wither_func, instance)
