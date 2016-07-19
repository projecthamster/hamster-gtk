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


"""
This module contains auxillary dialog classes.

Dialogs simple enough not to warrent dedicated modules are gathered in this one.
"""

from __future__ import absolute_import, unicode_literals

import calendar
import datetime
from gettext import gettext as _

from gi.repository import Gtk
from hamster_lib import Fact
from six import text_type

from hamster_gtk import helpers
from hamster_gtk.helpers import _u


class ErrorDialog(Gtk.MessageDialog):
    """
    Error Dialog used to provide feedback to the user.

    Right now we basicly just pass exception messages to the user. Whilst this is usefull to
    provide meaningfull information at this early stage, we probably want to provide more user
    friendly messages later on.
    """

    def __init__(self, parent, message, *args, **kwargs):
        """Initialize dialog."""
        super(ErrorDialog, self).__init__(*args, buttons=Gtk.ButtonsType.CLOSE,
            message_type=Gtk.MessageType.ERROR, text=message, **kwargs)
        self.set_transient_for(parent)


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
        button = Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)
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


class EditFactDialog(Gtk.Dialog):
    """
    Dialog that allows editing of a fact instance.

    The user can edit the fact in question by entering a new ``raw fact``
    string and/or specifying particular attribute values in dedicated widgets.
    In cases where a ``raw fact`` provided contains information in conflict
    with values of those dedicated widgets the latter are authorative.
    """

    def __init__(self, parent, fact):
        """
        Initialize dialog.

        Args:
            parent (Gtk.Window): Parent window.
            fact (hamster_lib.Fact): Fact instance to be edited.
        """
        super(EditFactDialog, self).__init__()
        self._fact = fact

        self.set_transient_for(parent)
        self.set_default_size(600, 200)
        # ``self.content_area`` is a ``Gtk.Box``. We strive for an
        # ``Gtk.Grid`` only based layout. So we have to add this extra step.
        self._mainbox = self._get_main_box()
        self.get_content_area().add(self._mainbox)

        # We do not use ``self.add_buttons`` because this only allows to pass
        #  on strings not actual button instances. We want to pass button
        # instances however so we can customize them if we want to.
        self.add_action_widget(self._get_delete_button(), Gtk.ResponseType.REJECT)
        self.add_action_widget(self._get_apply_button(), Gtk.ResponseType.APPLY)
        self.add_action_widget(self._get_cancel_button(), Gtk.ResponseType.CANCEL)
        self.show_all()

    @property
    def updated_fact(self):
        """Fact instance using values at the time of accessing it."""
        def get_raw_fact_value():
            """Get text from raw fact entry field."""
            return _u(self._raw_fact_widget.get_text())

        def get_description_value():
            """Get unicode value from widget."""
            text_view = self._description_widget.get_child()
            text_buffer = text_view.get_buffer()
            start, end = text_buffer.get_bounds()
            return _u(text_buffer.get_text(start, end, True))

        # Create a new fact instance from the provided raw string.
        fact = Fact.create_from_raw_fact(get_raw_fact_value())
        # Instead of transferring all attributes of the parsed fact to the
        # existing ``self._fact`` we just go the other way round and attach the
        # old facts PK to the newly created instance.
        fact.pk = self._fact.pk
        # Explicit description trumps anything that may have been included in
        # the `raw_fact``.
        fact.description = get_description_value()
        return fact

    # Widgets
    def _get_main_box(self):
        """Return the main layout container storing the content area."""
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        grid.set_name('EditDialogMainBox')
        grid.set_row_spacing(20)

        self._raw_fact_widget = self._get_raw_fact_widget()
        self._description_widget = self._get_description_widget()
        grid.attach(self._get_old_fact_widget(), 0, 0, 1, 1)
        grid.attach(self._raw_fact_widget, 0, 1, 1, 1)
        grid.attach(self._description_widget, 0, 2, 1, 1)
        return grid

    def _get_old_fact_widget(self):
        """Return a widget representing the fact to be edited."""
        label = Gtk.Label(text_type(self._fact))
        label.set_hexpand(True)
        label.set_name('EditDialogOldFactLabel')
        return label

    def _get_raw_fact_widget(self):
        """Return a widget that accepts user input to provide new ``raw fact`` string."""
        entry = Gtk.Entry()
        # [FIXME]
        # Maybe it would be sensible to have a serialization helper method as
        # part of ``hamster-lib``?!
        label = '{start}-{end} {activity}@{category}'.format(
            start=self._fact.start.strftime('%H:%M'),
            end=self._fact.end.strftime("%H:%M"),
            activity=text_type(self._fact.activity.name),
            category=text_type(self._fact.category.name)
        )
        entry.set_text(label)
        entry.set_name('EditDialogRawFactEntry')
        return entry

    def _get_description_widget(self):
        """Return a widget that displays and allows editing of ``fact.description``."""
        if self._fact.description:
            description = self._fact.description
        else:
            description = ''
        window = Gtk.ScrolledWindow()
        text_buffer = Gtk.TextBuffer()
        text_buffer.set_text(description)
        view = Gtk.TextView.new_with_buffer(text_buffer)
        view.set_hexpand(True)
        window.add(view)
        view.set_name('EditDialogDescriptionWindow')
        return window

    def _get_delete_button(self):
        """Return a *delete* button."""
        return Gtk.Button.new_from_stock(Gtk.STOCK_DELETE)

    def _get_apply_button(self):
        """Return a *apply* button."""
        return Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)

    def _get_cancel_button(self):
        """Return a *cancel* button."""
        return Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
