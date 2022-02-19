'''
Definition of ParameterCaster.

Each stored parameter has a caster defined in its owning class. If no cast is
specified in the class using the `Parameter.caster` decorator, the
ParametrizedObjectMeta metaclass will make sure that a default caster will be
present in the owning class.

Casters are used during the parametrized object initialization. The latter
computes the value of the parameters from the **kwargs received in the
parametrized object __init__. A caster name should start with `cast_`. For
example, here is a parametrized object with the parameeter bar:

>>> class Foo(ParametrizedObject):
...     bar = Parameter(default=42)

In this cast a default caster `cast_bar` will be created.

>>> foo = Foo()
... print(foo.cast_bar()) # prints 42
... print(foo.cast_bar(a=77)) # prints 77

A custom caster function can be defined using the `Parameter.caster` decorator:

>>> class Foo(ParametrizedObject):
...
...     radius = Parameter(default=10)
...
...     @radius.caster
...     def cast_radius(self, default, **kwargs):
...
...         radius = kwargs.get('radius', default)
...
...         if 'diameter' in kwargs:
...             radius = kwargs['diameter'] / 2
...
...         return radius
...
...     @parameter
...     def diameter(self):
...         return 2 * self.radius
'''

from types import MethodType
import paramobject


class ParameterCaster: # pylint: disable=too-few-public-methods
    '''
    Used to compute a parameter value from the __init__ **kwargs.
    '''

    def __init__(self, parameter, caster_func=None):

        if not isinstance(parameter, paramobject.Parameter):
            raise TypeError(f'A Parameter is expected, got: {type(parameter)}')

        self.parameter = parameter
        self.caster_func = caster_func

    @property
    def caster_func(self):
        '''
        Returns the caster function to use.

        If a custom caster function is defined, the latter is returned.
        Otherwise, a default caster function is returned.
        '''

        #pylint: disable-next=unused-argument
        def default_caster_func(instance, default, **kwargs):
            '''
            Default caster function.

            Returns the value of the parameter directly given in **kwargs.
            '''

            return kwargs.get(self.parameter.name, default)

        if self._caster_func is None:

            return default_caster_func

        return self._caster_func

    @caster_func.setter
    def caster_func(self, func):

        if func is not None and not callable(func):
            raise TypeError('The caster function must be callable.')

        self._caster_func = func

    def __get__(self, instance, owner=None):

        if instance is None:
            return self

        # check that the parameter has a name
        if self.parameter.name is None:
            raise RuntimeError('A name must be attributed to the parameter in '
                               'order to be used.')

        def wrapper(instance, *args, **kwargs):
            '''
            Caster function wrapper.

            This wrapper handles the case were a parametrized object is given
            in the __init__ arguments. In this case, the given object stored
            parameters are extracted into the **kwargs.

            This wrapper also provide the parameter default value to the
            caster function.
            '''

            # if an object might have been given as argument
            if args:

                obj, = args

                if not isinstance(obj, instance.__class__):
                    raise TypeError(f'A instance of the class '
                                    f'{instance.__class__} or one of its '
                                    f'subclasses is expected, not: '
                                    f'{type(obj)}.')

                params = dict(obj.stored_params)

            else:
                params = {}

            # overwrite params given by kwargs
            params.update(kwargs)

            # gather default value
            default = getattr(instance.__class__, self.parameter.name).default

            return self.caster_func(instance, default, **params)

        # return the caster function wrapper bound to the instance
        return MethodType(wrapper, instance)
