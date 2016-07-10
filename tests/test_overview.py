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

import pytest
from freezegun import freeze_time
from gi.repository import Gtk

from hamster_gtk import helpers
from hamster_gtk.screens import overview


class TestFactGrid(object):
    """Unittests for FactGrid."""

    def test_init(self, app):
        """Make sure minimal initialisation works."""
        fact_grid = overview.FactGrid(app.controler, {})
        assert fact_grid

    def test__get_date_widget(self, fact_grid):
        """Make sure expected label is returned."""
        result = fact_grid._get_date_widget(datetime.date.today())
        assert isinstance(result, Gtk.EventBox)

    def test__get_fact_list(self, app, fact_grid):
        """Make sure a FactListBox is retuned."""
        result = fact_grid._get_fact_list(app.controler, [])
        assert isinstance(result, overview.FactListBox)


class TestFactListBox(object):
    """Unittest for FactListBox."""

    def test_init(self, app, set_of_facts):
        """Test that instantiation works as expected."""
        result = overview.FactListBox(app.controler, set_of_facts)
        assert isinstance(result, overview.FactListBox)
        assert len(result.get_children()) == len(set_of_facts)

    def test__on_activate_reject(self, fact_list_box, fact, mocker):
        """Make sure an edit dialog is created, processed and then destroyed."""
        fact_list_box.get_toplevel = Gtk.Window
        mocker.patch('hamster_gtk.screens.overview.EditFactDialog.run',
                     return_value=Gtk.ResponseType.REJECT)
        fact_list_box._delete_fact = mocker.MagicMock()
        row = mocker.MagicMock()
        row.fact = fact
        fact_list_box._on_activate(None, row)
        assert fact_list_box._delete_fact.called

    def test__on_activate_apply(self, fact_list_box, fact, mocker):
        """Make sure an edit dialog is created, processed and then destroyed."""
        fact_list_box.get_toplevel = Gtk.Window
        mocker.patch('hamster_gtk.screens.overview.EditFactDialog.run',
                     return_value=Gtk.ResponseType.APPLY)
        fact_list_box._update_fact = mocker.MagicMock()
        row = mocker.MagicMock()
        row.fact = fact
        fact_list_box._on_activate(None, row)
        assert fact_list_box._update_fact.called


class TestFactListRow(object):
    """Unittests for FactListRow."""

    def test_init(self, fact):
        """Make sure instantiated object matches expectations."""
        result = overview.FactListRow(fact)
        assert isinstance(result, overview.FactListRow)
        hbox = result.get_children()[0]
        children = hbox.get_children()
        assert isinstance(children[0], Gtk.Label)
        assert isinstance(children[1], overview.FactBox)
        assert isinstance(children[2], Gtk.EventBox)

    def test_get_time_widget(self, factlist_row, fact):
        """Make sure widget matches expectations."""
        result = factlist_row._get_time_widget(fact)
        assert isinstance(result, Gtk.Label)

    def test_get_delta_widget(self, factlist_row, fact):
        """Make sure widget matches expectations."""
        result = factlist_row._get_delta_widget(fact)
        assert isinstance(result, Gtk.EventBox)


class TestFactBox(object):
    """Unittests for FactBox."""

    def test_init(self, fact):
        """Make sure instantiated object matches expectations."""
        result = overview.FactBox(fact)
        assert isinstance(result, overview.FactBox)
        assert len(result.get_children()) == 3

    def test_init_without_description(self, fact):
        """Make sure instantiated object matches expectations."""
        fact.description = ''
        result = overview.FactBox(fact)
        assert isinstance(result, overview.FactBox)
        assert len(result.get_children()) == 2

    def test__get_activity_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        result = factbox._get_activity_widget(fact)
        assert isinstance(result, Gtk.Label)

    def test__get_tags_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        # [FIXME]
        # Once the method is not just using a dummy tag, this needs to be
        # refactored.
        result = factbox._get_tags_widget(fact)
        assert isinstance(result, Gtk.Box)
        assert len(result.get_children()) == 1

    def test__get_desciption_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        result = factbox._get_description_widget(fact)
        assert isinstance(result, Gtk.Label)
        result = factbox._get_description_widget(fact)
        assert isinstance(result, Gtk.Label)


class TestCharts(object):
    """Unittests for Charts."""

    def test_init(self, totals):
        """Make sure instance matches expectation."""
        result = overview.Charts(totals)
        assert isinstance(result, overview.Charts)
        assert len(result.get_children()) == 1

    def test__get_category_widget(self, charts, totals):
        """Make sure widget matches expectations."""
        result = charts._get_category_widget(totals.category)
        assert isinstance(result, Gtk.Grid)
        # Each category will trigger adding 3 children.
        assert len(result.get_children()) == 3 * len(totals.category)

    @pytest.mark.parametrize(('minutes', 'expectation'), (
        (1, '1 min'),
        (30, '30 min'),
        (59, '59 min'),
        (60, '01:00'),
        (300, '05:00'),
    ))
    def test__get_delta_string(self, charts, minutes, expectation):
        delta = datetime.timedelta(minutes=minutes)
        result = charts._get_delta_string(delta)
        assert result == expectation


class TestSummary(object):
    """Unittests for Summery."""

    def test_init(self, category_highest_totals):
        """Test that instance meets expectation."""
        result = overview.Summary(category_highest_totals)
        assert isinstance(result, overview.Summary)
        assert len(result.get_children()) == len(category_highest_totals)


class TestHorizontalBarChart(object):
    """Unittests for HorizontalBarChart."""

    # [FIXME]
    # Figure out a way to test the draw function properly.

    def test_init(self, bar_chart_data):
        """Make sure instance matches expectations."""
        value, max_value = bar_chart_data
        result = overview.HorizontalBarChart(value, max_value)
        assert isinstance(result, overview.HorizontalBarChart)


class TestDateRangeSelectDialog(object):
    """Unittests for the daterange select dialog."""

    def test_init(self, overview_screen):
        assert overview.DateRangeSelectDialog(overview_screen)

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
