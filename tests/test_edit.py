# -*- coding: utf-8 -*-

import datetime

from gi.repository import Gtk

from hamster_gtk.screens import edit


class TestEditFactDialog(object):
    """Unittests for the edit dialog."""

    def test_init(self, fact, dummy_window):
        result = edit.EditFactDialog(dummy_window, fact)
        assert result

    def test__get_main_box(self, edit_fact_dialog):
        """Make sure the returned container matches expectation."""
        result = edit_fact_dialog._get_main_box()
        assert len(result.get_children()) == 3
        assert isinstance(result, Gtk.Grid)

    def test__get_old_fact_widget(self, edit_fact_dialog):
        """Test the widget representing the original fact."""
        result = edit_fact_dialog._get_old_fact_widget()
        assert isinstance(result, Gtk.Label)

    def test__get_raw_fact_widget(self, edit_fact_dialog):
        """Test the widget representing the new fact."""
        result = edit_fact_dialog._get_raw_fact_widget()
        assert isinstance(result, Gtk.Entry)

    def test__get_desciption_widget(self, edit_fact_dialog):
        """Test the description widget matches expectation."""
        result = edit_fact_dialog._get_description_widget()
        assert isinstance(result, Gtk.ScrolledWindow)

    def test__get_delete_button(self, edit_fact_dialog):
        """Make sure the delete button matches expectations."""
        result = edit_fact_dialog._get_delete_button()
        assert isinstance(result, Gtk.Button)

    def test__get_apply_button(self, edit_fact_dialog):
        """Make sure the apply button matches expectations."""
        result = edit_fact_dialog._get_apply_button()
        assert isinstance(result, Gtk.Button)

    def test__get_cancel_button(self, edit_fact_dialog):
        """Make sure the cancel button matches expectations."""
        result = edit_fact_dialog._get_cancel_button()
        assert isinstance(result, Gtk.Button)

    # [FIXME]
    # Add tests for changed values.
    def test_updated_fact_same(self, dummy_window, fact):
        """
        Make sure the property returns Fact matching field values.

        We need to jump through some extra hoops because we the current
        implementation will always set the edited fact to today as well as ignore
        all 'second' time info.
        """
        dialog = edit.EditFactDialog(dummy_window, fact)
        today = datetime.date.today()
        fact.start = datetime.datetime.combine(today, fact.start.time()).replace(second=0)
        fact.end = datetime.datetime.combine(today, fact.end.time()).replace(second=0)
        result = dialog.updated_fact
        assert result.as_tuple() == fact.as_tuple()
