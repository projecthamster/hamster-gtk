# -*- coding: utf-8 -*-

"""
Most of the widget related methods are tested very naivly. Hardly any
properties are checked right now. It is mostly about checking if they can be
instantiated at all.
Once the actuall design/layout becomes more solidified it may be worth while to
elaborate on those. It should be fairly simple now that we provide the
infrastructure.
"""

import datetime

from freezegun import freeze_time
from gi.repository import Gtk

from hamster_gtk import helpers
from hamster_gtk.misc import dialogs


class TestDateRangeSelectDialog(object):
    """Unittests for the daterange select dialog."""

    def test_init(self, dummy_window):
        assert dialogs.DateRangeSelectDialog(dummy_window)

    def test_daterange_getter(self, daterange_select_dialog, daterange_parametrized):
        """Make sure a tuple of start- end enddate is returned."""
        start, end = daterange_parametrized
        daterange_select_dialog._start_calendar.select_month(start.month - 1, start.year)
        daterange_select_dialog._start_calendar.select_day(start.day)
        daterange_select_dialog._end_calendar.select_month(end.month - 1, end.year)
        daterange_select_dialog._end_calendar.select_day(end.day)
        assert daterange_select_dialog.daterange == daterange_parametrized

    def test_daterange_setter(self, daterange_select_dialog, daterange_parametrized):
        """Make sure the correct start- and endtime is set on the calendars."""
        start, end = daterange_parametrized
        dialog = daterange_select_dialog
        daterange_select_dialog.daterange = daterange_parametrized
        assert helpers.calendar_date_to_datetime(dialog._start_calendar.get_date()) == start
        assert helpers.calendar_date_to_datetime(dialog._end_calendar.get_date()) == end

    def test__get_apply_button(self, daterange_select_dialog):
        """Make sure widget matches expectation."""
        result = daterange_select_dialog._get_apply_button()
        assert isinstance(result, Gtk.Button)

    def test__get_today_widget(self, daterange_select_dialog, mocker):
        """Make sure widget matches expectation."""
        daterange_select_dialog._on_today_button_clicked = mocker.MagicMock()
        result = daterange_select_dialog._get_today_widget()
        result.emit('clicked')
        assert daterange_select_dialog._on_today_button_clicked.called

    def test__get_week_widget(self, daterange_select_dialog, mocker):
        """Make sure widget matches expectation."""
        daterange_select_dialog._on_week_button_clicked = mocker.MagicMock()
        result = daterange_select_dialog._get_week_widget()
        result.emit('clicked')
        assert daterange_select_dialog._on_week_button_clicked.called

    def test__get_month_widget(self, daterange_select_dialog, mocker):
        """Make sure widget matches expectation."""
        daterange_select_dialog._on_month_button_clicked = mocker.MagicMock()
        result = daterange_select_dialog._get_month_widget()
        result.emit('clicked')
        assert daterange_select_dialog._on_month_button_clicked.called

    def test__get_start_calendar(self, daterange_select_dialog):
        """Make sure widget matches expectation."""
        result = daterange_select_dialog._get_start_calendar()
        assert isinstance(result, Gtk.Calendar)

    def test__get_end_calendar(self, daterange_select_dialog):
        """Make sure widget matches expectation."""
        result = daterange_select_dialog._get_end_calendar()
        assert isinstance(result, Gtk.Calendar)

    def test__get_custom_range_label(self, daterange_select_dialog):
        """Make sure widget matches expectation."""
        result = daterange_select_dialog._get_custom_range_label()
        assert isinstance(result, Gtk.Label)

    def test__get_custom_range_connection_label(self, daterange_select_dialog):
        """Make sure widget matches expectation."""
        result = daterange_select_dialog._get_custom_range_connection_label()
        assert isinstance(result, Gtk.Label)

    def test__get_double_label_button(self, daterange_select_dialog, word_parametrized):
        """Make sure widget matches expectation."""
        l_label = word_parametrized
        r_label = word_parametrized
        result = daterange_select_dialog._get_double_label_button(l_label, r_label)
        assert isinstance(result, Gtk.Button)

    def test__get_week_range(self, daterange_select_dialog, weekrange_parametrized):
        """Make the right daterange is returned."""
        date, expectation = weekrange_parametrized
        result = daterange_select_dialog._get_week_range(date)
        assert result == expectation

    def test__get_month_range(self, daterange_select_dialog, monthrange_parametrized):
        """Make the right daterange is returned."""
        date, expectation = monthrange_parametrized
        result = daterange_select_dialog._get_month_range(date)
        assert result == expectation

    @freeze_time('2016-04-01')
    def test__on_today_button_clicked(self, daterange_select_dialog, mocker):
        """Test that 'datetime' is set to today and right response is triggered."""
        daterange_select_dialog.response = mocker.MagicMock()
        daterange_select_dialog._on_today_button_clicked(None)
        assert daterange_select_dialog.daterange == (datetime.date(2016, 4, 1),
                                                     datetime.date(2016, 4, 1))
        assert daterange_select_dialog.response.called_with(Gtk.ResponseType.APPLY)

    @freeze_time('2016-04-01')
    def test__on_week_button_clicked(self, daterange_select_dialog, mocker):
        """Test that 'datetime' is set to 'this week' and right response is triggered."""
        daterange_select_dialog.response = mocker.MagicMock()
        daterange_select_dialog._on_week_button_clicked(None)
        assert daterange_select_dialog.daterange == (datetime.date(2016, 3, 28),
                                                     datetime.date(2016, 4, 3))
        assert daterange_select_dialog.response.called_with(Gtk.ResponseType.APPLY)

    @freeze_time('2016-04-01')
    def test__on_month_button_clicked(self, daterange_select_dialog, mocker):
        """Test that 'datetime' is set to 'this month' and right response is triggered."""
        daterange_select_dialog.response = mocker.MagicMock()
        daterange_select_dialog._on_month_button_clicked(None)
        assert daterange_select_dialog.daterange == (datetime.date(2016, 4, 1),
                                                     datetime.date(2016, 4, 30))
        assert daterange_select_dialog.response.called_with(Gtk.ResponseType.APPLY)


class TestEditFactDialog(object):
    """Unittests for the edit dialog."""

    def test_init(self, fact, dummy_window):
        result = dialogs.EditFactDialog(dummy_window, fact)
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
        dialog = dialogs.EditFactDialog(dummy_window, fact)
        today = datetime.date.today()
        fact.start = datetime.datetime.combine(today, fact.start.time()).replace(second=0)
        fact.end = datetime.datetime.combine(today, fact.end.time()).replace(second=0)
        result = dialog.updated_fact
        assert result.as_tuple() == fact.as_tuple()


class TestErrorDialog(object):
    """Unittests for ErrorDialog."""

    def test_init_with_parent_window(self, dummy_window):
        """Test instances where toplevel is a window instance."""
        result = dialogs.ErrorDialog(dummy_window, '')
        assert result
