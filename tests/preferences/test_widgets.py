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


class TestConfigComboBoxText(object):
    """Unittests for ConfigComboBoxText."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        combo_box = widgets.ConfigComboBoxText()
        assert combo_box

    def test_instance(self):
        """Make sure the widget is still a ComboBoxText."""
        combo_box = widgets.ConfigComboBoxText()
        assert isinstance(combo_box, Gtk.ComboBoxText)

    def test_values_constructor(self, combo_box_items):
        """Make sure the ComboBoxText can be populated via constructor."""
        combo_box = widgets.ConfigComboBoxText(combo_box_items)
        assert len(combo_box.get_model()) == len(combo_box_items)

    def test_set_get(self, config_combo_box_text, combo_box_items):
        """Make sure the widget returns the same value it received."""
        random_id = random.choice(combo_box_items)[0]
        config_combo_box_text.set_config_value(random_id)
        assert config_combo_box_text.get_config_value() == random_id

        another_random_id = random.choice(combo_box_items)[0]
        config_combo_box_text.set_config_value(another_random_id)
        assert config_combo_box_text.get_config_value() == another_random_id


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
        assert editable_file_chooser.on_mnemonic_activate(editable_file_chooser, False)

    def test_set_get(self, editable_file_chooser, paths):
        """Make sure the widget returns the same value it received."""
        for path in paths:
            editable_file_chooser.set_config_value(path)
            assert editable_file_chooser.get_config_value() == path


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

    def test_params_constructor(self, spinner_params):
        """Make sure the widget can be set up via constructor."""
        spin = widgets.DurationEntry(**spinner_params)
        adjustment = spin.get_adjustment()
        assert adjustment.get_lower() == spinner_params['min']
        assert adjustment.get_upper() == spinner_params['max']
        assert adjustment.get_step_increment() == spinner_params['step']

    def test_params_constructor_partial(self, spinner_params):
        """Providing only some arguments to the constructor should fail."""
        del spinner_params[random.choice(list(spinner_params.keys()))]
        with pytest.raises(ValueError):
            widgets.DurationEntry(**spinner_params)

    def test_params_constructor_overlapping_bounds(self, spinner_params):
        """Passing lower bound greater than upper bound to the constructor should fail."""
        spinner_params['min'], spinner_params['max'] = spinner_params['max'], spinner_params['min']
        with pytest.raises(ValueError):
            widgets.DurationEntry(**spinner_params)

    def test_params_constructor_zero_step(self, spinner_params):
        """Passing zero as a step to the constructor should fail."""
        spinner_params['step'] = 0
        with pytest.raises(ValueError):
            widgets.DurationEntry(**spinner_params)

    def test_params_constructor_decimal_places(self, spinner_params):
        """When given a fractional step, the widget should show values at appropriate precision."""
        spinner_params['step'] = 1e-19
        spin = widgets.DurationEntry(**spinner_params)
        assert spin.get_digits() == 19

    def test_params_constructor_clamped_digits(self, spinner_params):
        """When passing a step with too many decimal places, the precision is clamped."""
        spinner_params['step'] = 1e-25
        spin = widgets.DurationEntry(**spinner_params)
        assert spin.get_digits() == widgets.duration_entry.MAX_DIGITS

    def test_set_get(self, duration_entry, numbers):
        """Make sure the widget returns the same value it received."""
        for number in numbers:
            duration_entry.set_config_value(number)
            assert duration_entry.get_config_value() == number


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

    def test_set_get(self, time_entry, times):
        """Make sure the widget returns the same value it received."""
        for time in times:
            time_entry.set_config_value(time)
            assert time_entry.get_config_value() == time
