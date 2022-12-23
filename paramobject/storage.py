'''
Definition of StaticDict and ParametersView.

StaticDict behave as a dict with restrict predefined set of available keys.

ParametersView helps to access a restricted set of parameters of a parametrized
object as a read-only mapping.
'''

from collections.abc import Mapping, MutableMapping


class StaticDict(MutableMapping):
    '''
    Dict with predefined set of available str keys.

    Any writing of a key outside the available keys set will raise a KeyError.
    Any reading of a key outside the available keys set or of a unset item will
    raise a KeyError.

    __iter__ returns an interator over all available keys.
    '''

    def __init__(self, available_keys):

        # check types
        for key in available_keys:

            if not isinstance(key, str):
                raise TypeError(f'Keys are expected to be strings, got '
                                f'{type(key)}')

        self.content = {key: None for key in available_keys}

    def __getitem__(self, key):

        value = self.content[key]

        if value is None:
            raise KeyError(key)

        return value

    def __setitem__(self, key, value):

        # check if key is in the set of keys
        if key not in self.content:
            raise KeyError(key)

        # forbid writting None
        if value is None:
            raise ValueError(f'Entry "{key}" cannot be set to None.')

        self.content[key] = value

    def __delitem__(self, key):
        self.content[key] = None

    def __iter__(self):
        return iter(self.content)

    def __len__(self):
        return len(self.content)


class ParametersView(Mapping):
    '''
    Read-only view on a restricted set of parameters of a parametrized object.
    '''

    def __init__(self, obj, param_names):
        self._obj = obj
        self._param_names = list(sorted(param_names))

    def __getitem__(self, param_name):

        if param_name not in self._param_names:
            raise KeyError(param_name)

        try:
            return getattr(self._obj, param_name)

        except AttributeError as err:
            raise KeyError(param_name) from err

    def __len__(self):
        return len(self._param_names)

    def __iter__(self):
        return iter(self._param_names)

    def __str__(self):

        maxlen = max(len(name) for name in self)
        fmt = '{:' + str(maxlen) + '>s} : {}'

        lines = [fmt.format(name, repr(value)) for name, value in self.items()]
        return '\n'.join(lines)
