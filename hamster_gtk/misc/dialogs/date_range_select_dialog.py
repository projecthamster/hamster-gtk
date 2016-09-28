# -*- encoding: utf-8 -*-

# This file is part of 'hamster-gtk'.
#
# 'hamster-gtk' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-gtk' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-gtk'.  If not, see <http://www.gnu.org/licenses/>.


"""This module contains Dialog for selecting a date range."""

from __future__ import absolute_import, unicode_literals

import calendar
import datetime
from gettext import gettext as _

from gi.repository import Gtk

from hamster_gtk import helpers


class DateRangeSelectDialog(Gtk.Dialog):
    """
    A Dialog that allows to select two dates that form a 'daterange'.

    The core of the dialog is two :class:`Gtk.Calendar` widgets which allow for
    manual setting of start- and enddate. Additionally, three presets are
    provided for the users convenience.
    """

    # Gtk.Calendar returns month in a ``0`` based ordering which is why we
    # need to add/subtract ``1`` when translating with real live months.

    def __init__(self, parent, *args, **kwargs):
        """
        Initialize widget.

        Args:
            parent (OverviewScreen): Parent window for this dialog.
        """
        super(DateRangeSelectDialog, self).__init__(*args, **kwargs)
        self.set_transient_for(parent)
        self._mainbox = Gtk.Grid()
        self._mainbox.set_hexpand(True)
        self._mainbox.set_vexpand(True)

        self._start_calendar = Gtk.Calendar()
        self._end_calendar = Gtk.Calendar()

        self._mainbox.attach(self._get_today_widget(), 0, 0, 4, 1)
        self._mainbox.attach(self._get_week_widget(), 0, 1, 4, 1)
        self._mainbox.attach(self._get_month_widget(), 0, 2, 4, 1)
        self._mainbox.attach(self._get_custom_range_label(), 0, 3, 1, 1)
        self._mainbox.attach(self._get_custom_range_connection_label(), 2, 3, 1, 1)
        self._mainbox.attach(self._start_calendar, 1, 3, 1, 1)
        self._mainbox.attach(self._end_calendar, 3, 3, 1, 1)

        self.get_content_area().add(self._mainbox)
        self.add_action_widget(self._get_apply_button(), Gtk.ResponseType.APPLY)
        self.show_all()

    @property
    def daterange(self):
        """Return start and end date as per calendar widgets."""
        start = helpers.calendar_date_to_datetime(self._start_calendar.get_date())
        end = helpers.calendar_date_to_datetime(self._end_calendar.get_date())
        return (start, end)

    @daterange.setter
    def daterange(self, daterange):
        """Set calendar dates according to daterange."""
        start, end = daterange
        self._start_calendar.select_month(start.month - 1, start.year)
        self._start_calendar.select_day(start.day)
        self._end_calendar.select_month(end.month - 1, end.year)
        self._end_calendar.select_day(end.day)

    # Widgets
    def _get_apply_button(self):
        button = Gtk.Button(_('_Apply'), use_underline=True)
        return button

    def _get_today_widget(self):
        """Return a widget that sets the daterange to today."""
        button = self._get_double_label_button(_("Today"), datetime.date.today())
        button.set_hexpand(True)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self._on_today_button_clicked)
        return button

    def _get_week_widget(self):
        """Return a widget that sets the daterange to the current week."""
        start, end = self._get_week_range(datetime.date.today())
        date_text = _("{} to {}".format(start, end))
        button = self._get_double_label_button(_("Current Week"), date_text)
        button.set_hexpand(True)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self._on_week_button_clicked)
        return button

    def _get_month_widget(self):
        """Return a widget that sets the daterange to the current month."""
        start, end = self._get_month_range(datetime.date.today())
        date_text = _("{} to {}".format(start, end))
        button = self._get_double_label_button(_("Current Month"), date_text)
        button.set_hexpand(True)
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.connect('clicked', self._on_month_button_clicked)
        return button

    def _get_start_calendar(self):
        """Return ``Gtk.Calendar`` instance for the start date."""
        return Gtk.Calendar()

    def _get_end_calendar(self):
        """Return ``Gtk.Calendar`` instance for the end date."""
        return Gtk.Calendar()

    def _get_custom_range_label(self):
        """Return a 'heading' label for the widget."""
        return Gtk.Label(_("Custom Range"))

    def _get_custom_range_connection_label(self):
        """Return the label to be displayed between the two calendars."""
        return Gtk.Label(_("to"))

    # Helper
    def _get_double_label_button(self, left_label, right_label):
        """
        Return a special button with two label components.

        The left label will be left aligned the right one right aligned.
        """
        button = Gtk.Button()
        grid = Gtk.Grid()
        button.add(grid)

        left_label = Gtk.Label(left_label)
        left_label.set_hexpand(True)
        left_label.set_halign(Gtk.Align.START)

        right_label = Gtk.Label(right_label)
        right_label.set_hexpand(True)
        right_label.set_halign(Gtk.Align.END)

        grid.attach(left_label, 0, 0, 1, 1)
        grid.attach(right_label, 1, 0, 1, 1)
        return button

    def _get_week_range(self, date):
        """Return the start- and enddate of the week a given date is in."""
        def get_offset_to_weekstart(weekday):
            """
            Return the distance to the desired start of the week given weekday.

            No extra work is required if we want weeks to start on mondays as
            in this case ``weekday=0``. If a different start of the week is
            desired, we need to add some adjustments.
            """
            offset = weekday
            return datetime.timedelta(days=offset)

        start = date - get_offset_to_weekstart(date.weekday())
        end = start + datetime.timedelta(days=6)
        return (start, end)

    def _get_month_range(self, date):
        """Return the start- and enddate of the month a given date is in."""
        start = date - datetime.timedelta(days=date.day - 1)
        days_in_month = calendar.monthrange(date.year, date.month)[1]
        end = start + datetime.timedelta(days=days_in_month - 1)
        return (start, end)

    # Callbacks
    def _on_today_button_clicked(self, button):
        today = datetime.date.today()
        self.daterange = (today, today)
        self.response(Gtk.ResponseType.APPLY)

    def _on_week_button_clicked(self, button):
        start, end = self._get_week_range(datetime.date.today())
        self.daterange = (start, end)
        self.response(Gtk.ResponseType.APPLY)

    def _on_month_button_clicked(self, button):
        start, end = self._get_month_range(datetime.date.today())
        self.daterange = (start, end)
        self.response(Gtk.ResponseType.APPLY)
