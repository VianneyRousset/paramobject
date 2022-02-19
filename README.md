# paramobject
An easy way to create parametrized object in Python.

Parametrized objects stores a unmutable collections of parameters. Parameters
can be accessed as properties but cannot be set. Here is an example,

```python
from paramobject import ParametrizedObject, Parameter, parameter

class Cylinder(ParametrizedObject):

  # those two parameters are stored in the object
  length = Parameter(default=42)
  radius = Parameter(default=10)

  # this parameter is not stored but deduces from another parameter
  @parameter
  def diameter(self):
    return 2 * self.radius

  # custom wither can be defined
  @length.wither
  def with_length(self, length=None, *, max_length=None):

    if length is None:
        length = self.length

    if max_length is not None:
        length = min(length, max_length)

    return self.with_params(length=length)

  # custom caster should be defined to retrieve the stored parameter
  # value from deduced parameter.
  @radius.caster
  def caster(self, default, **kwargs):

      radius = kwargs.get('radius', kwargs)

      if 'diameter' in kwargs:
          radius = kwargs['diameter'] / 2

      return radius


# any omitted parameter will use its default value if specified
cylinder = Cylinder(length=50)

# parameter value are retrieved as properties
print(cylinder.length) # prints 50
print(cylinder.radius) # prints 10
print(cylinder.diameter) # prints 20

# parameter value cannot be directly modified. A copy of the object with
# a new parameter value must be created using withers:
long_cylinder = cylinder.with_length(1000)
print(cylinder.length) # prints 1000

# custom wither can be defined to allow more complex operations
print(cylinder.with_length(max_length=20).length) # prints 20


class Cuboid(ParametrizedObject):
  size = Parameter(default=(1, 1, 1))


class Hammer(ParametrizedObject):
  handle = Cylinder(radius=1, lenght=20)
  head = Cuboid(size=(2, 2, 5))


# parametrized object can be nested
hammer = Hammer()
print(hammer.handle.length) # prints 20

# in this case, contained parametrized object withers directly returns a 
# copy of the owning object.
long_hammer = hammer.handle.with_length(100)
print(long_hammer.handle.length) # prints 100
```
