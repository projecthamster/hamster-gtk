# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pytest
from gi.repository import Gtk

from hamster_gtk.preferences import widgets


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

    def test_get_config_value_short(self, time_entry, times_without_seconds):
        """Make sure the widget value is retrieved correctly when using the short time form."""
        for time in times_without_seconds:
            time_entry.set_text(time.strftime('%H:%M'))
            assert time_entry.get_config_value() == time

    def test_set_config_value(self, time_entry, times):
        """Make sure the widget value is set correctly."""
        for time in times:
            time_entry.set_config_value(time)
            assert time_entry.get_text() == time.strftime('%H:%M:%S')

    def test_set_config_value_short(self, time_entry, times_without_seconds):
        """Make sure the widget value is set correctly evem if our value ommits seconds."""
        for time in times_without_seconds:
            time_entry.set_config_value(time)
            assert time_entry.get_text() == time.strftime('%H:%M:%S')
