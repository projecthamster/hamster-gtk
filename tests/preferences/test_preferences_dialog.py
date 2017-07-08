# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import pytest

from hamster_gtk.preferences import PreferencesDialog


class TestPreferencesDialog(object):
    """Unittests for PreferencesDialog."""

    @pytest.mark.parametrize('empty_initial', (True, False))
    def test_init(self, dummy_window, app, config, empty_initial):
        """Make instantiation works as expected."""
        if empty_initial:
            config = {}
        result = PreferencesDialog(dummy_window, app, config)
        grids = result.get_content_area().get_children()[0].get_children()
        # This assumes 2 children per config entry (label and widget).
        grid_entry_counts = [len(g.get_children()) / 2 for g in grids]
        assert sum(grid_entry_counts) == 10

    @pytest.mark.slowtest
    def test_get_config(self, preferences_dialog, config_parametrized):
        """
        Make sure retrieval of field values works as expected.

        In particular we need to make sure that unicode/utf-8 handling works as
        expected.
        """
        preferences_dialog._set_config(config_parametrized)
        result = preferences_dialog.get_config()
        assert result == config_parametrized

    @pytest.mark.slowtest
    def test_set_config(self, preferences_dialog, config_parametrized):
        """Make sure setting the field values works as expected."""
        preferences_dialog._set_config(config_parametrized)
        for title, page in preferences_dialog._pages:
            for key, (label, widget) in page._fields.items():
                assert widget.get_config_value() == config_parametrized[key]

    def test_set_config_empty_value(self, preferences_dialog):
        with pytest.raises(ValueError):
            preferences_dialog._set_config({})
