# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pytest
from gi.repository import Gtk

from hamster_gtk.preferences import widgets


class TestHamsterSpinButton(object):
    """Unittests for HamsterSpinButton."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        spin = widgets.HamsterSpinButton()
        assert spin

    def test_instance(self):
        """Make sure the widget is still a SpinButton."""
        spin = widgets.HamsterSpinButton()
        assert isinstance(spin, Gtk.SpinButton)

    def test_params_constructor(self, simple_adjustment):
        """Make sure the widget can be set up via constructor."""
        spin = widgets.HamsterSpinButton(simple_adjustment)
        adjustment = spin.get_adjustment()
        assert adjustment.get_lower() == simple_adjustment.min
        assert adjustment.get_upper() == simple_adjustment.max
        assert adjustment.get_step_increment() == simple_adjustment.step

    def test_params_constructor_adjustment(self, adjustment):
        """Make sure the widget can be set up by passing :class:`Gtk.Adjustment` to constructor."""
        spin = widgets.HamsterSpinButton(adjustment)
        assert spin.get_adjustment() == adjustment

    def test_params_constructor_overlapping_bounds(self, simple_adjustment):
        """Passing lower bound greater than upper bound to the constructor should fail."""
        new_adj = simple_adjustment._replace(min=simple_adjustment.max, max=simple_adjustment.min)
        with pytest.raises(ValueError):
            widgets.HamsterSpinButton(new_adj)

    def test_params_constructor_zero_step(self, simple_adjustment):
        """Passing zero as a step to the constructor should fail."""
        new_adj = simple_adjustment._replace(step=0)
        with pytest.raises(ValueError):
            widgets.HamsterSpinButton(new_adj)

    def test_params_constructor_invalid(self):
        """
        Passing a value that is neither a :class:`Gtk.Adjustment`, nor a :class:`SimpleAdjustment`
        to the constructor should fail.
        """
        with pytest.raises(ValueError):
            widgets.HamsterSpinButton(42)

    def test_params_constructor_decimal_places(self, simple_adjustment):
        """When given a fractional step, the widget should show values at appropriate precision."""
        new_adj = simple_adjustment._replace(step=1e-19)
        spin = widgets.HamsterSpinButton(new_adj)
        assert spin.get_digits() == 19

    def test_params_constructor_clamped_digits(self, simple_adjustment):
        """When passing a step with too many decimal places, the precision is clamped."""
        new_adj = simple_adjustment._replace(step=1e-25)
        spin = widgets.HamsterSpinButton(new_adj)
        assert spin.get_digits() == widgets.HamsterSpinButton.MAX_DIGITS

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
