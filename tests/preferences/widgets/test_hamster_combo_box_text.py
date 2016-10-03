# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import random

from gi.repository import Gtk

from hamster_gtk.preferences import widgets


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
        random.shuffle(combo_box_items)
        for id, text in combo_box_items:
            hamster_combo_box_text.set_active_id(id)
            assert hamster_combo_box_text.get_config_value() == id

    def test_set_config_value(self, hamster_combo_box_text, combo_box_items):
        """Make sure the widget value is set correctly."""
        random.shuffle(combo_box_items)
        for id, text in combo_box_items:
            hamster_combo_box_text.set_config_value(id)
            assert hamster_combo_box_text.get_active_id() == id
