# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from hamster_gtk.preferences import PreferencesDialog


class TestPreferencesDialog(object):
    """Unittests for PreferencesDialog."""

    def test_init(self, dummy_window, app, config):
        """Make instantiation works as expected."""
        result = PreferencesDialog(dummy_window, app, config)
        grid = result.get_content_area().get_children()[0]
        # This assumes 2 children per config entry (label and widget).
        assert len(grid.get_children()) / 2 == len(config.keys())

    def test_get_config(self, dummy_window, app, initial_config_parametrized):
        """
        Make sure retrieval of field values works as expected.

        In particular we need to make sure that unicode/utf-8 handling works as
        expected.
        """
        dialog = PreferencesDialog(dummy_window, app, initial_config_parametrized)
        result = dialog.get_config()
        assert result == initial_config_parametrized

    def test_set_config(self, dummy_window, app, initial_config_parametrized):
        """Make sure setting the field values works as expected."""
        dialog = PreferencesDialog(dummy_window, app, initial_config_parametrized)
        another_config_parametrized = initial_config_parametrized
        dialog._set_config(another_config_parametrized)
        for key, (_label, widget) in dialog._fields.items():
            assert widget.get_config_value() == initial_config_parametrized[key]
