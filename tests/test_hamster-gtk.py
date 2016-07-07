# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

from freezegun import freeze_time
from gi.repository import Gtk
from six import text_type

from hamster_gtk import hamster_gtk, helpers
from hamster_gtk.screens import overview
from hamster_gtk.screens.tracking import TrackingScreen


class TestHamsterGTK(object):
    """Unittests for the main app class."""

    def test_instantiation(self):
        """Make sure class instatiation works as intended."""
        app = hamster_gtk.HamsterGTK()
        assert app


class TestMainWindow(object):
    """Unittests for the main application window."""

    def test_init(self, app):
        """Make sure class setup works up as intended."""
        window = hamster_gtk.MainWindow(app)
        assert isinstance(window.get_titlebar(), hamster_gtk.HeaderBar)
        assert isinstance(window._app, hamster_gtk.HamsterGTK)
        assert window.get_size() == hamster_gtk.DEFAULT_WINDOW_SIZE
        assert isinstance(window.get_children()[0], TrackingScreen)

    def test_get_css(self, app_window):
        """Make sure a string is returned."""
        assert isinstance(app_window._get_css(), text_type)


class TestHeaderBar(object):
    """Test that headerbar works as intended."""

    def test_initial_anatomy(self, app_window):
        """Test that the bars initial setup is as expected."""
        bar = hamster_gtk.HeaderBar(app_window, app_window._app)
        assert bar.props.title == 'Hamster-GTK'
        assert bar.props.subtitle == 'Your friendly time tracker.'
        assert bar.props.show_close_button
        assert len(bar.get_children()) == 1

    def test_on_overview_button_overview_exists(self, app_window):
        """Test that we don't create a new overview if we already have one."""
        app_window.overview = True
        bar = hamster_gtk.HeaderBar(app_window, app_window._app)
        assert bar._on_overview_button(None) is None


class TestOverviewScreen(object):
    """Unittests for the overview dialog."""

    def test_daterange(self, request):
        """Test that we return the right attribute."""
        pass

    def test_daterange_emit_signal(self, request):
        """Test that setting a daterange emit the right signal."""
        pass


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
