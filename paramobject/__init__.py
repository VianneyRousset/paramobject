'''
Parametrized objects stores a unmutable collections of parameters. Parameters
can be accessed as properties but cannot be set. For example, the parameter foo
is retrieved as follows:

>>> obj.foo

However, the latter parameter cannot be changed. To have an object with a
different value of foo, a new parametrized object has to be created as
follows:

>>> new_obj = obj.__class__(obj, foo=42)

Alternatively, any parametrized object have a so-called `wither` that returns
a new instance of the class with the a new value of the parameter. Therefore,
the following line is equivalent:

>>> new_obj = obj.with_foo(42)

Parameters can be stored in memory or can be computed when its getter is called.
Moreover, stored parameters can have a default value. If no default value is
given (equivalent to having its default value set to None), the value of the
parameters has to be given in the object creation (either directly or
copied from the given parametrized object).

The class ParametrizedObject is intended to be subclassed. Sub-classes can then
directly define parameters with the Parameter class and/or by using the
@parameter decorator.

Here is an example,

>>> class Example(ParametrizedObject):
...
...     # those two parameters are stored in the object
...     height = Parameter(default=42)
...     radius = Parameter(default=10)
...
...     # here a custom getter is defined
...     @parameter(stored=True, default=123)
...     def bar(self):
...         return 11 * self.params_storage['bar']
...
...     # custom wither can be defined
...     @height.wither
...     def with_height(self, height=None, *, max_height=None):
...
...         if height is None:
...             height = self.height
...
...         if max_height is not None:
...             height = min(height, max_height)
...
...         return self.with_params(height=height)
...
...     # this parameter is not stored and is deduced from others
...     @parameter
...     def diameter(self):
...         return 2 * self.radius
...
...     # custom caster should be defined to retrieve the stored parameter
...     # value from deduced parameter.
...     @radius.caster
...     def caster(self, default, **kwargs):
...
...         radius = kwargs.get('radius', kwargs)
...
...         if 'diameter' in kwargs:
...             radius = kwargs['diameter'] / 2
...
...         return radius
'''

# TODO Nested ParametrizedObject
# TODO Check if kwargs has some extra unused arguments

from .parameter import Parameter
from .object import ParametrizedObject
from .wither import ParameterWither
from .caster import ParameterCaster


def parameter(*args, stored=False, default=None):
    '''
    Decorator to defining the getter for a new parameter.

    The following lines are equivalent:

    >>> @parameter
    ... def foo(self):
    ...     ...

    >>> @parameter()
    ... def foo(self):
    ...     ...

    >>> @parameter(default=None, stored=False)
    ... def foo(self):
    ...     ...

    If stored is True, an entry with parameter name will be set in the object
    params storage (`obj.params_storage`).

    If a value other than None is given as default, a default value will be used
    for this param during the object creation.
    '''

    # the function is directly given as parameter
    if args:
        getter_func, = args
        return Parameter(getter_func, default=None, stored=False)

    # prepare decorator
    def decorator(getter_func):
        return Parameter(getter_func, default=default, stored=stored)

    return decorator
