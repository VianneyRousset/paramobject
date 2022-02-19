#!/usr/bin/env python

# pylint: disable=disallowed-name
# pylint: disable=missing-class-docstring,
# pylint: disable=missing-function-docstring,
# pylint: disable=no-self-use

import unittest
from paramobject import ParametrizedObject, parameter, Parameter


class TestParametrizedObject(unittest.TestCase):

    def test_basic_values(self):

        class ClassUnderTest(ParametrizedObject):

            foo = Parameter(default=42)
            bar = Parameter()

            @parameter(stored=True, default=123)
            def baz(self):
                return self.params_storage['baz']

            @parameter(stored=True)
            def qux(self):
                return self.params_storage['qux']

            @parameter
            def quux(self):
                return 11 * self.bar

        # missing mandatory parameter value must raise ValueError
        self.assertRaises(ValueError, ClassUnderTest)
        self.assertRaises(ValueError, ClassUnderTest, bar=1)
        self.assertRaises(ValueError, ClassUnderTest, qux=2)

        # check correct default values
        obj = ClassUnderTest(bar=1, qux=2)
        self.assertEqual(obj.foo, 42)
        self.assertEqual(obj.baz, 123)

        # check correct values
        obj = ClassUnderTest(foo=1, bar=2, baz=3, qux=4)
        self.assertEqual(obj.foo, 1)
        self.assertEqual(obj.bar, 2)
        self.assertEqual(obj.baz, 3)
        self.assertEqual(obj.qux, 4)
        self.assertEqual(obj.quux, 22)

    def test_wither(self):

        class ClassUnderTest(ParametrizedObject):

            foo = Parameter(default=42)
            bar = Parameter(default=77)

            @bar.wither
            def with_bar(self, bar, as_string=False):

                if as_string:
                    bar = str(bar)

                return self.with_params(bar=bar)

        # check values
        obj = ClassUnderTest()
        self.assertEqual(obj.foo, 42)
        self.assertEqual(obj.bar, 77)

        # check default wither
        obj = ClassUnderTest()
        self.assertEqual(obj.with_foo(10).foo, 10)

        # check custom wither
        obj = ClassUnderTest()
        self.assertEqual(obj.with_bar(10).bar, 10)
        self.assertEqual(obj.with_bar(10, as_string=True).bar, '10')

    def test_caster(self):

        class ClassUnderTest(ParametrizedObject):

            radius = Parameter(default=10)

            @parameter
            def diameter(self):
                return 2 * self.radius

            @radius.caster
            def cast_radius(self, default, **kwargs):

                radius = kwargs.get('radius', default)

                if 'diameter' in kwargs:
                    radius = kwargs['diameter'] / 2

                return radius

        # check default
        obj = ClassUnderTest()
        self.assertEqual(obj.radius, 10)
        self.assertEqual(obj.diameter, 20)

        # check init with radius
        obj = ClassUnderTest(radius=100)
        self.assertEqual(obj.radius, 100)
        self.assertEqual(obj.diameter, 200)

        # check init with diameter
        obj = ClassUnderTest(diameter=100)
        self.assertEqual(obj.radius, 50)
        self.assertEqual(obj.diameter, 100)

        # check wither
        obj = ClassUnderTest()
        self.assertEqual(obj.with_radius(100).diameter, 200)

    def test_subclassing(self):

        class ClassUnderTest(ParametrizedObject):
            foo = Parameter(default=42)

        class SubClassUnderTest(ClassUnderTest):
            bar = Parameter(default=77)

        # check values
        obj = SubClassUnderTest()
        self.assertEqual(obj.foo, 42)
        self.assertEqual(obj.bar, 77)

    def test_nested_parametrized_object(self):

        class ContainedClassUnderTest(ParametrizedObject):
            bar = Parameter(default=42)

        class ClassUnderTest(ParametrizedObject):
            foo = Parameter(default=ContainedClassUnderTest())

        # check value
        obj = ClassUnderTest()
        self.assertEqual(obj.foo.bar, 42)

        # check wither, contained class must return an instance of the
        # containing class
        obj = ClassUnderTest()
        self.assertIsInstance(obj.foo.with_bar(10), ClassUnderTest)
        self.assertEqual(obj.foo.with_bar(10).foo.bar, 10)


if __name__ == '__main__':
    unittest.main()
