# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from gi.repository import Gtk
import random

from hamster_gtk.preferences import widgets


class TestComboBoxTextConfig(object):
    """Unittests for ComboBoxTextConfig."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        combo_box = widgets.ComboBoxTextConfig()
        assert combo_box

    def test_instance(self):
        """Make sure the widget is still a ComboBoxText."""
        combo_box = widgets.ComboBoxTextConfig()
        assert isinstance(combo_box, Gtk.ComboBoxText)

    def test_set_get(self, combo_box_text_config, combo_box_items):
        """Make sure the widget returns the same value it received."""
        random_id = random.choice(combo_box_items)[0]
        combo_box_text_config.set_config_value(random_id)
        assert combo_box_text_config.get_config_value() == random_id

        another_random_id = random.choice(combo_box_items)[0]
        combo_box_text_config.set_config_value(another_random_id)
        assert combo_box_text_config.get_config_value() == another_random_id


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

    def test_set_get(self, editable_file_chooser, paths):
        """Make sure the widget returns the same value it received."""
        for path in paths:
            editable_file_chooser.set_config_value(path)
            assert editable_file_chooser.get_config_value() == path


class TestSpinButtonConfig(object):
    """Unittests for SpinButtonConfig."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        spinner = widgets.SpinButtonConfig()
        assert spinner

    def test_instance(self):
        """Make sure the widget is still a SpinButton."""
        spinner = widgets.SpinButtonConfig()
        assert isinstance(spinner, Gtk.SpinButton)

    def test_set_get(self, spin_button_config, numbers):
        """Make sure the widget returns the same value it received."""
        for number in numbers:
            spin_button_config.set_config_value(number)
            assert spin_button_config.get_config_value() == number


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

    def test_set_get(self, time_entry, times):
        """Make sure the widget returns the same value it received."""
        for time in times:
            time_entry.set_config_value(time)
            assert time_entry.get_config_value() == time
