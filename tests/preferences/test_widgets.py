# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import random

import pytest
from gi.repository import Gtk

from hamster_gtk.preferences import widgets


class TestConfigWidget(object):
    """Unittests for ConfigWidget."""

    def test_get_config_value(self):
        """Calling get_config_value should raise NotImplementedError."""
        widget = widgets.ConfigWidget()
        with pytest.raises(NotImplementedError):
            widget.get_config_value()

    def test_set_config_value(self):
        """Calling set_config_value should raise NotImplementedError."""
        widget = widgets.ConfigWidget()
        with pytest.raises(NotImplementedError):
            widget.set_config_value(None)


class TestHamsterComboBoxText(object):
    """Unittests for HamsterComboBoxText."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        combo_box = widgets.HamsterComboBoxText()
        assert combo_box

    def test_instance(self):
        """Make sure the widget is still a ComboBoxText."""
        combo_box = widgets.HamsterComboBoxText()
        assert isinstance(combo_box, Gtk.ComboBoxText)

    def test_values_constructor(self, combo_box_items):
        """Make sure the ComboBoxText can be populated via constructor."""
        combo_box = widgets.HamsterComboBoxText(combo_box_items)
        assert len(combo_box.get_model()) == len(combo_box_items)

    def test_get_config_value(self, hamster_combo_box_text, combo_box_items):
        """Make sure the widget value is retrieved correctly."""
        random_id = random.choice(combo_box_items)[0]
        hamster_combo_box_text.set_active_id(random_id)
        assert hamster_combo_box_text.get_config_value() == random_id

        another_random_id = random.choice(combo_box_items)[0]
        hamster_combo_box_text.set_active_id(another_random_id)
        assert hamster_combo_box_text.get_config_value() == another_random_id

    def test_set_config_value(self, hamster_combo_box_text, combo_box_items):
        """Make sure the widget value is set correctly."""
        random_id = random.choice(combo_box_items)[0]
        hamster_combo_box_text.set_config_value(random_id)
        assert hamster_combo_box_text.get_active_id() == random_id

        another_random_id = random.choice(combo_box_items)[0]
        hamster_combo_box_text.set_config_value(another_random_id)
        assert hamster_combo_box_text.get_active_id() == another_random_id


class TestEditableFileChooser(object):
    """Unittests for EditableFileChooser."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        file_chooser = widgets.EditableFileChooser()
        assert file_chooser

    def test_instance(self):
        """Make sure the widget is still a Grid."""
        file_chooser = widgets.EditableFileChooser()
        assert isinstance(file_chooser, Gtk.Grid)

    def test_mnemonic(self, editable_file_chooser):
        """Make sure the widget can be accessed using mnemonic."""
        assert editable_file_chooser._on_mnemonic_activate(editable_file_chooser, False)

    def test_get_config_value(self, editable_file_chooser, paths):
        """Make sure the widget value is retrieved correctly."""
        for path in paths:
            editable_file_chooser._entry.set_text(path)
            assert editable_file_chooser.get_config_value() == path

    def test_set_config_value(self, editable_file_chooser, paths):
        """Make sure the widget value is set correctly."""
        for path in paths:
            editable_file_chooser.set_config_value(path)
            assert editable_file_chooser._entry.get_text() == path


class TestDurationEntry(object):
    """Unittests for DurationEntry."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        spin = widgets.DurationEntry()
        assert spin

    def test_instance(self):
        """Make sure the widget is still a SpinButton."""
        spin = widgets.DurationEntry()
        assert isinstance(spin, Gtk.SpinButton)

    def test_params_constructor(self, simple_adjustment):
        """Make sure the widget can be set up via constructor."""
        spin = widgets.DurationEntry(simple_adjustment)
        adjustment = spin.get_adjustment()
        assert adjustment.get_lower() == simple_adjustment.min
        assert adjustment.get_upper() == simple_adjustment.max
        assert adjustment.get_step_increment() == simple_adjustment.step

    def test_params_constructor_adjustment(self, adjustment):
        """Make sure the widget can be set up by passing :class:`Gtk.Adjustment` to constructor."""
        spin = widgets.DurationEntry(adjustment)
        assert spin.get_adjustment() == adjustment

    def test_params_constructor_overlapping_bounds(self, simple_adjustment):
        """Passing lower bound greater than upper bound to the constructor should fail."""
        new_adj = simple_adjustment._replace(min=simple_adjustment.max, max=simple_adjustment.min)
        with pytest.raises(ValueError):
            widgets.DurationEntry(new_adj)

    def test_params_constructor_zero_step(self, simple_adjustment):
        """Passing zero as a step to the constructor should fail."""
        new_adj = simple_adjustment._replace(step=0)
        with pytest.raises(ValueError):
            widgets.DurationEntry(new_adj)

    def test_params_constructor_invalid(self):
        """
        Passing a value that is neither a :class:`Gtk.Adjustment`, nor a :class:`SimpleAdjustment`
        to the constructor should fail.
        """
        with pytest.raises(ValueError):
            widgets.DurationEntry(42)

    def test_params_constructor_decimal_places(self, simple_adjustment):
        """When given a fractional step, the widget should show values at appropriate precision."""
        new_adj = simple_adjustment._replace(step=1e-19)
        spin = widgets.DurationEntry(new_adj)
        assert spin.get_digits() == 19

    def test_params_constructor_clamped_digits(self, simple_adjustment):
        """When passing a step with too many decimal places, the precision is clamped."""
        new_adj = simple_adjustment._replace(step=1e-25)
        spin = widgets.DurationEntry(new_adj)
        assert spin.get_digits() == widgets.DurationEntry.MAX_DIGITS

    def test_get_config_value(self, duration_entry, numbers):
        """Make sure the widget value is retrieved correctly."""
        for number in numbers:
            duration_entry.set_value(number)
            assert duration_entry.get_config_value() == number

    def test_set_config_value(self, duration_entry, numbers):
        """Make sure the widget value is set correctly."""
        for number in numbers:
            duration_entry.set_config_value(number)
            assert duration_entry.get_value_as_int() == number


class TestTimeEntry(object):
    """Unittests for TimeEntry."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        entry = widgets.TimeEntry()
        assert entry

    def test_instance(self):
        """Make sure the widget is still a Entry."""
        entry = widgets.TimeEntry()
        assert isinstance(entry, Gtk.Entry)

    def test_get_invalid(self, time_entry):
        """Make sure an error is raised when the entered value is invalid."""
        time_entry.set_text('moo')
        with pytest.raises(ValueError):
            time_entry.get_config_value()

    def test_get_config_value(self, time_entry, times):
        """Make sure the widget value is retrieved correctly."""
        for time in times:
            time_entry.set_text(time.strftime('%H:%M:%S'))
            assert time_entry.get_config_value() == time

    def test_set_config_value(self, time_entry, times):
        """Make sure the widget value is set correctly."""
        for time in times:
            time_entry.set_config_value(time)
            assert time_entry.get_text() == time.strftime('%H:%M:%S')