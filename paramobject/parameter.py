'''
Definition of Parameter.
'''

import paramobject


class Parameter:
    '''
    A parameter for a parametrized object.

    A parameter behave as a read-only property. As properties, parameters
    have a getter function that return its value.

    By default, parameters value are stored in the object params_storage
    mapping. However, if stored is set to False, the owning parametrized
    object won't stores its value.

    If no no getter function is given to the parameter, a default one is used.
    This default getter function simply return the value stored in the
    paramametrized object params storage.

    Parameter name is given by its owning class. You shouldn't need to set this
    attribute yourself.
    '''

    def __init__(self, getter_func=None, *, stored=True, default=None,
                 name=None):

        self.getter_func = getter_func
        self.name = name
        self.stored = stored
        self.default = default

    @property
    def getter_func(self):
        '''
        Returns the getter function to use.

        If a custom getter function is defined, the latter is returned.
        Otherwise, a default getter function is returned.
        '''

        def default_getter_func(instance):
            '''
            Default getter function.

            Returns the value of the parameter as stored in the owning object
            params_storage.
            '''

            if not self.stored:
                raise ValueError('The default getter function cannot be used '
                                 'if the parameter is not stored.')

            return instance.params_storage[self.name]

        if self._getter_func is None:

            if self.name is None:
                raise RuntimeError('A nameless parameter cannot use the '
                                   'default getter function')

            return default_getter_func

        return self._getter_func

    @getter_func.setter
    def getter_func(self, func):

        if func is not None and not callable(func):
            raise TypeError('The getter function must be callable.')

        self._getter_func = func

    def __get__(self, instance, owner=None):

        if instance is None:
            return self

        value = self.getter_func(instance)

        if isinstance(value, paramobject.ParametrizedObject):
            return value.bind(instance, self.name)

        return value

    def wither(self, wither_func=None):
        '''
        Decorator to create a wither.

        Usage:

        >>> class Example(ParametrizedObject):
        ...
        ...     @parameter(default=42, stored=True)
        ...     def foo(self):
        ...         return self.params_storage['foo']
        ...
        ...     @foo.wither
        ...     def with_foo(self, v=None, *, vmax=None):
        ...
        ...         if v is None:
        ...             v = self.foo
        ...
        ...         if vmax is not None:
        ...             v = min(v, vmax)
        ...
        ...         return self.with_params(foo=v)
        '''

        self.wither = paramobject.ParameterWither(self, wither_func)
        return self.wither

    def caster(self, caster_func=None):
        '''
        Decorator to create a caster.

        Can only be used with stored parameters.

        Usage:

        >>> class Example(ParametrizedObject):
        ...
        ...     radius = Parameter(default=10)
        ...
        ...     @parameter
        ...     def diameter(self):
        ...         return 2 * self.radius
        ...
        ...     @radius.caster
        ...     def cast_radius(self, default, **kwargs)
        ...
        ...         radius = kwargs.get('radius', default)
        ...
        ...         if 'diameter' in kwargs:
        ...             radius = kwargs['diameter'] / 2
        ...
        ...         return radius
        '''

        # check that the parameter is stored
        if not self.stored:
            raise ValueError('A non-stored parameter cannot have a caster.')

        self.caster = paramobject.ParameterCaster(self, caster_func)
        return self.caster
