# -*- coding: utf-8 -*-

import pytest


class TestSimpleAdjustment(object):
    """Unittests for ConfigWidget."""

    def test_immutable(self, simple_adjustment, numbers):
        """Make sure the object is immutable."""
        with pytest.raises(AttributeError):
            simple_adjustment.min = numbers[0]
        with pytest.raises(AttributeError):
            simple_adjustment.max = numbers[1]
        with pytest.raises(AttributeError):
            simple_adjustment.step = numbers[2]

        with pytest.raises(TypeError):
            simple_adjustment[0] = numbers[0]
        with pytest.raises(TypeError):
            simple_adjustment[1] = numbers[1]
        with pytest.raises(TypeError):
            simple_adjustment[2] = numbers[2]

    def test_min(self, simple_adjustment):
        """Make sure min is alias of the field number 0."""
        assert simple_adjustment.min == simple_adjustment[0]

    def test_max(self, simple_adjustment):
        """Make sure max is alias of the field number 1."""
        assert simple_adjustment.max == simple_adjustment[1]

    def test_step(self, simple_adjustment):
        """Make sure step is alias of the field number 2."""
        assert simple_adjustment.step == simple_adjustment[2]

    def test_replace(self, simple_adjustment, numbers):
        """Make sure fields are correcly replaced."""
        new_adjustment = simple_adjustment.replace(min=numbers[0], max=numbers[1], step=numbers[2])
        assert new_adjustment[0] == numbers[0]
        assert new_adjustment[1] == numbers[1]
        assert new_adjustment[2] == numbers[2]

    def test_replace_incorrect(self, simple_adjustment):
        """Calling replace with unknown key should fail."""
        with pytest.raises(ValueError):
            simple_adjustment.replace(foo=42)

    def test_repr(self, simple_adjustment):
        """Make sure the representation is correct."""
        expected_string = 'SimpleAdjustment(min=%d, max=%d, step=%d)' % simple_adjustment
        assert repr(simple_adjustment) == expected_string
