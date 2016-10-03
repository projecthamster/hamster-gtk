# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pytest
from gi.repository import Gtk

from hamster_gtk.preferences.widgets import HamsterSpinButton, SimpleAdjustment


class TestHamsterSpinButton(object):
    """Unittests for HamsterSpinButton."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        spin = HamsterSpinButton()
        assert spin

    def test_instance(self):
        """Make sure the widget is still a SpinButton."""
        spin = HamsterSpinButton()
        assert isinstance(spin, Gtk.SpinButton)

    def test_params_constructor(self, simple_adjustment):
        """Make sure the widget can be set up via constructor."""
        spin = HamsterSpinButton(simple_adjustment)
        adjustment = spin.get_adjustment()
        assert adjustment.get_lower() == simple_adjustment.min
        assert adjustment.get_upper() == simple_adjustment.max
        assert adjustment.get_step_increment() == simple_adjustment.step

    def test_params_constructor_adjustment(self, adjustment):
        """Make sure the widget can be set up by passing :class:`Gtk.Adjustment` to constructor."""
        spin = HamsterSpinButton(adjustment)
        assert spin.get_adjustment() == adjustment

    def test_params_constructor_overlapping_bounds(self, simple_adjustment):
        """Passing lower bound greater than upper bound to the constructor should fail."""
        new_adj = SimpleAdjustment(min=simple_adjustment.max, max=simple_adjustment.min,
            step=simple_adjustment.step)
        with pytest.raises(ValueError):
            HamsterSpinButton(new_adj)

    def test_params_constructor_zero_step(self, simple_adjustment):
        """Passing zero as a step to the constructor should fail."""
        new_adj = SimpleAdjustment(min=simple_adjustment.min, max=simple_adjustment.max, step=0)
        with pytest.raises(ValueError):
            HamsterSpinButton(new_adj)

    def test_params_constructor_invalid(self):
        """
        Passing a value that is neither a :class:`Gtk.Adjustment`, nor a :class:`SimpleAdjustment`
        to the constructor should fail.
        """
        with pytest.raises(ValueError):
            HamsterSpinButton(42)

    def test_get_config_value(self, hamster_spin_button, numbers):
        """Make sure the widget value is retrieved correctly."""
        for number in numbers:
            hamster_spin_button.set_value(number)
            assert hamster_spin_button.get_config_value() == number

    def test_set_config_value(self, hamster_spin_button, numbers):
        """Make sure the widget value is set correctly."""
        for number in numbers:
            hamster_spin_button.set_config_value(number)
            assert hamster_spin_button.get_value_as_int() == number
