# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from gi.repository import Gtk

from hamster_gtk.preferences import widgets


class TestComboFileChooser(object):
    """Unittests for ComboFileChooser."""

    def test_init(self):
        """Make sure minimal initialisation works."""
        file_chooser = widgets.ComboFileChooser()
        assert file_chooser

    def test_instance(self):
        """Make sure the widget is still a Grid."""
        file_chooser = widgets.ComboFileChooser()
        assert isinstance(file_chooser, Gtk.Grid)

    def test_mnemonic(self, combo_file_chooser):
        """Make sure the widget can be accessed using mnemonic."""
        assert combo_file_chooser._on_mnemonic_activate(combo_file_chooser, False)

    def test_get_config_value(self, combo_file_chooser, paths):
        """Make sure the widget value is retrieved correctly."""
        for path in paths:
            combo_file_chooser._entry.set_text(path)
            assert combo_file_chooser.get_config_value() == path

    def test_set_config_value(self, combo_file_chooser, paths):
        """Make sure the widget value is set correctly."""
        for path in paths:
            combo_file_chooser.set_config_value(path)
            assert combo_file_chooser._entry.get_text() == path
