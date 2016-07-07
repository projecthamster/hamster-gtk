# -*- coding: utf-8 -*-

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
This Module provides the ``Overview`` class to generate a general listing of our data.

In order to do that, this module contains multiple auxiliary widgets to render specific aspects of
this screen.

Due to using default ``Gtk`` classes as bases for our custom widgets (such as
``HorizontalBarChart``) we are able to greatly reduce the codebase compared to ``legacy hamster``.
The one major downside is, that we can not easily reimplement its eye candy
'slide in from the bottom' transition when opening the 'details' widget. Whilst this is unfortunate
reimplementing this properly is out of the scope right now and a price we are willing to pay.
"""

import calendar
import datetime
import operator
from collections import defaultdict, namedtuple
from gettext import gettext as _

from gi.repository import Gtk
from six import text_type

import hamster_gtk.dialogs as dialogs
import hamster_gtk.helpers as helpers
from hamster_gtk.screens.edit import EditFactDialog


class OverviewScreen(Gtk.Dialog):
    """Overview-screen that provides information about a users facts.."""

    def __init__(self, parent, app):
        """Initialize dialog."""
        super(OverviewScreen, self).__init__(parent=parent)
        self._parent = parent
        self._app = app
        self._connect_signals()

        self.set_default_size(640, 800)
        self.titlebar = HeaderBar()
        self.set_titlebar(self.titlebar)
        self.set_transient_for(parent)
        self._daterange = self._get_default_daterange()

        self._charts = False

        # [FIXME] Should be a property to make sure the signal is emitted
        self._facts = None
        self._grouped_facts = None

        self.main_box = self.get_content_area()
        self.refresh()

        self.connect('delete-event', self._on_delete)

    @property
    def _daterange(self):
        """Return the 'daterange' for which this overview displays facts."""
        return self.__daterange

    @_daterange.setter
    def _daterange(self, daterange):
        """Set daterange and make sure we emit the corresponding signal."""
        self.__daterange = daterange
        self._app.controler.signal_handler.emit('daterange-changed')

    def _connect_signals(self):
        """Connect signals this instance listens for."""
        self._app.controler.signal_handler.connect('facts-changed', self._on_facts_changed)
        self._app.controler.signal_handler.connect('daterange-changed', self._on_daterange_changed)

    def _get_default_daterange(self):
        """Return the default daterange used when none has been selected by user."""
        today = datetime.date.today()
        return (today, today)

    def _on_facts_changed(self, sender):
        """Callback to be triggered if stored facts have been changed."""
        self.refresh()

    def _on_daterange_changed(self, sender):
        """Callback to be triggered if the 'daterange' changed."""
        def get_label_text(daterange):
            start, end = daterange
            if start == end:
                text = text_type(start)
            else:
                text = '{} - {}'.format(start, end)
            return text
        self.titlebar.set_daterange_button_label(get_label_text(self._daterange))
        self.refresh()

    def refresh(self):
        """Recompute data and trigger redrawing."""
        self._facts = self._get_facts()
        self._grouped_facts, self._totals = self._group_facts()

        helpers.clear_children(self.main_box)

        facts_window = Gtk.ScrolledWindow()
        self.factlist = FactGrid(facts_window, self._app, self._grouped_facts.by_date)
        facts_window.add(self.factlist)
        self.main_box.pack_start(facts_window, True, True, 0)

        self.totals_panel = Summary(self._get_highest_totals(self._totals.category, 3))
        self.main_box.pack_start(self.totals_panel, False, False, 0)

        # [FIXME]
        # Only show button if there are facts.
        charts_button = Gtk.Button('click to show more details ...')
        charts_button.connect('clicked', self._on_charts_button)
        self.main_box.pack_start(charts_button, False, True, 0)

        self.show_all()

    def _on_charts_button(self, button):
        """On button click either show or hide extended details."""
        if self._charts:
            self._charts.destroy()
            self._charts = False
        else:
            self._charts = Charts(self._totals)
            self.main_box.pack_start(self._charts, False, False, 0)
            self.show_all()

    def _on_delete(self, event, data):
        """
        Close this dialog.

        It would be preferable to just hide the dialog and re-present it if
        it required again, but we did run into serious issues "re-showing" it.
        So for now we get rid of it entirely so a new instance is triggered
        instead.
        """
        self.destroy()
        self._parent._overview_window = None

    def _get_facts(self):
        """Collect and return all facts too be shown, not necessarily be visible."""
        start, end = self._daterange
        return self._app.store.facts.get_all(start, end)

    def _group_facts(self):
        """
        Return ``self._facts`` grouped by various keys.

        Note:
            We handle totals as part of this method in order to limit the
            amount of iterations over ``self._facts``.
        """
        def get_total(totals):
            """Return a dictionary of max deltas per key."""
            max_total = defaultdict(datetime.timedelta)
            for key, deltas in totals.items():
                for delta in deltas:
                    max_total[key] += delta
            return max_total

        facts_by_date = defaultdict(list)
        date_deltas = defaultdict(list)
        facts_by_category = defaultdict(list)
        category_deltas = defaultdict(list)
        facts_by_activity = defaultdict(list)
        activity_deltas = defaultdict(list)

        GroupedFacts = namedtuple('GroupedFacts', ('by_activity', 'by_category', 'by_date'))
        # Provide a dummy in case there are no facts to be grouped.
        grouped_facts = GroupedFacts({}, {}, {})

        for fact in self._facts:
            facts_by_date[fact.date].append(fact)
            date_deltas[fact.date].append(fact.delta)

            # Take note: ``Fact.activity`` is only unique for the composite key
            # activity.name/activity.category!
            facts_by_activity[fact.activity].append(fact)
            activity_deltas[fact.activity].append(fact.delta)

            facts_by_category[fact.category].append(fact)
            category_deltas[fact.category].append(fact.delta)

            grouped_facts = GroupedFacts(
                by_activity=facts_by_activity,
                by_category=facts_by_category,
                by_date=facts_by_date
            )

        Totals = namedtuple('Totals', ('activity', 'category', 'date'))
        totals = Totals(
            activity=get_total(activity_deltas),
            category=get_total(category_deltas),
            date=get_total(date_deltas)
        )
        return grouped_facts, totals

    def _get_highest_totals(self, dictionary, amount):
        """Return specified amount of items with the highest value."""
        totals = sorted(dictionary.items(), key=operator.itemgetter(1),
                        reverse=True)
        if len(totals) < amount:
            result = totals
        else:
            result = totals[:amount]
        return result

    def apply_previous_daterange(self):
        """Apply a daterange of equal 'length' right before the given range."""
        # [FIXME]
        # In case of a 'month' we should return another (varialble) month
        # length not neccessarily the same length
        orig_start, orig_end = self._daterange
        offset = (orig_end - orig_start) + datetime.timedelta(days=1)
        self._daterange = (orig_start - offset, orig_end - offset)

    def apply_next_daterange(self):
        """Apply a daterange of equal 'length' right before the given range."""
        # [FIXME]
        # In case of a 'month' we should return another (varialble) month
        # length not neccessarily the same length
        orig_start, orig_end = self._daterange
        offset = (orig_end - orig_start) + datetime.timedelta(days=1)
        self._daterange = (orig_start + offset, orig_end + offset)


class HeaderBar(Gtk.HeaderBar):
    """Headerbar used by the overview screen."""

    def __init__(self, *args, **kwargs):
        """Initialize headerbar."""
        super(HeaderBar, self).__init__(*args, **kwargs)
        self.set_show_close_button(True)
        self.set_title(_("Overview"))
        self._daterange_button = self._get_daterange_button()
        self.pack_start(self._get_prev_daterange_button())
        self.pack_start(self._get_next_daterange_button())
        self.pack_start(self._daterange_button)

    def set_daterange_button_label(self, text):
        """Set text on the 'daterange button'."""
        # We provide this method as a clean public interface rather than exposing
        # the button directly.
        label = self._daterange_button.get_children()[0]
        label.set_text(text)

    # Widgets
    def _get_daterange_button(self):
        """Return a button that opens the *select daterange* dialog."""
        # We add a dummy label which will be set properly once a daterange is
        # set.
        button = Gtk.Button('')
        button.connect('clicked', self._on_daterange_button_clicked)
        return button

    def _get_prev_daterange_button(self):
        """Return a 'previous dateframe' widget."""
        button = Gtk.Button(_("Earlier"))
        button.connect('clicked', self._on_previous_daterange_button_clicked)
        return button

    def _get_next_daterange_button(self):
        """Return a 'next dateframe' widget."""
        button = Gtk.Button(_("Later"))
        button.connect('clicked', self._on_next_daterange_button_clicked)
        return button

    # Callbacks
    def _on_daterange_button_clicked(self, button):
        """Callback for when the 'daterange' button is clicked."""
        parent = self.get_parent()
        dialog = DateRangeSelectDialog(parent)
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            parent._daterange = dialog.daterange
        dialog.destroy()

    def _on_previous_daterange_button_clicked(self, button):
        """Callback for when the 'previous' button is clicked."""
        self.get_parent().apply_previous_daterange()

    def _on_next_daterange_button_clicked(self, button):
        """Callback for when the 'next' button is clicked."""
        self.get_parent().apply_next_daterange()


class FactGrid(Gtk.Grid):
    """Listing of facts per day."""

    def __init__(self, parent, app, initial):
        """Initialize widget."""
        super(FactGrid, self).__init__()
        self.set_column_spacing(0)
        self._parent = parent
        self._app = app

        row = 0
        for date, facts in initial.items():
            # [FIXME] Order by fact start
            self.attach(self._get_date_widget(date), 0, row, 1, 1)
            self.attach(FactListBox(self._parent, self._app, facts), 1, row, 1, 1)
            row += 1

    def _get_date_widget(self, date):
        """Return a widget to be used in the 'date column'."""
        date_string = date.strftime("%A\n%b %d")
        date_box = Gtk.EventBox()
        date_box.set_name('DayRowDateBox')
        date_label = Gtk.Label()
        date_label.set_name('OverviewDateLabel')
        date_label.set_markup("<b>{}</b>".format(date_string))
        date_label.set_valign(Gtk.Align.START)
        date_label.set_justify(Gtk.Justification.RIGHT)
        date_box.add(date_label)
        return date_box

    def _get_fact_list(self, facts):
        """
        Return a widget representing all of the dates facts.

        We use a ``Gtk.ListBox`` as opposed to just adding widgets representing
        the facts right to the ``FactGrid`` in order to make use of
        ``Gtk.ListBox`` keyboard and mouse navigation / event handling.
        """
        return FactListBox(facts)


class FactListBox(Gtk.ListBox):
    """A List widget that represents each fact in a seperate actionable row."""

    def __init__(self, parent, app, facts):
        """Initialize widget."""
        super(FactListBox, self).__init__()
        self._parent = parent
        self._app = app

        self.set_name('OverviewFactList')
        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.props.activate_on_single_click = False
        self.connect('row-activated', self._on_activate)

        for fact in facts:
            row = FactListRow(fact)
            self.add(row)

    # Signal callbacks
    def _on_activate(self, widget, row):
        """Callback trigger if a row is 'activated'."""
        edit_dialog = EditFactDialog(self.get_toplevel(), row.fact, self._app)
        response = edit_dialog.run()
        if response == Gtk.ResponseType.CANCEL:
            pass
        elif response == Gtk.ResponseType.REJECT:
            edit_dialog.delete()
        elif response == Gtk.ResponseType.APPLY:
            edit_dialog.apply()
        else:
            message = _(
                "Something went wrong. Dialog returned unexpected value."
                " No changes were perpormed!"
            )
            dialog = dialogs.ErrorDialog(widget.get_toplevel(), message)
            dialog.run
            dialog.destroy()
        edit_dialog.destroy()


class FactListRow(Gtk.ListBoxRow):
    """A row representing a single fact."""

    def __init__(self, fact):
        """
        Initialize widget.

        Attributes:
            fact (hamster_lib.Fact): Fact instance represented by this row.
        """
        super(FactListRow, self).__init__()
        self.fact = fact
        self.set_hexpand(True)
        self.set_name('FactListRow')
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_widget = self._get_time_widget(fact)
        fact_box = FactBox(fact)
        delta_widget = self._get_delta_widget(fact)
        hbox.pack_start(time_widget, False, True, 0)
        hbox.pack_start(fact_box, True, True, 0)
        hbox.pack_start(delta_widget, False, True, 0)
        self.add(hbox)

    def _get_time_widget(self, fact):
        """"Return widget to represent ``Fact.start`` and ``Fact.end``."""
        start_time = fact.start.strftime('%H:%M')
        end_time = fact.end.strftime('%H:%M')
        time_label = Gtk.Label('{start} - {end}'.format(start=start_time, end=end_time))
        time_label.props.valign = Gtk.Align.START
        time_label.props.halign = Gtk.Align.START
        return time_label

    def _get_delta_widget(self, fact):
        """"Return widget to represent ``Fact.delta``."""
        label = Gtk.Label('{} Minutes'.format(fact.get_string_delta()))
        label.props.valign = Gtk.Align.START
        label.props.halign = Gtk.Align.END
        box = Gtk.EventBox()
        box.add(label)
        return box


class FactBox(Gtk.Box):
    """
    Widget to render details about a fact.

    Note:
        ``Fact.start`` and ``Fact.end`` are not shown by *this* widget.
    """

    def __init__(self, fact):
        """Initialize widget."""
        super(FactBox, self).__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_name('OverviewFactBox')
        self.pack_start(self._get_activity_widget(fact), True, True, 0)
        self.pack_start(self._get_tags_widget(fact), True, True, 0)
        if fact.description:
            self.pack_start(self._get_description_widget(fact), False, False, 0)

    def _get_activity_widget(self, fact):
        """Return widget to render the activity, including its related category."""
        if not fact.category:
            category = 'not categorised'
        else:
            category = str(fact.category)
        activity_label = Gtk.Label()
        activity_label.set_markup("{activity} - {category}".format(
            activity=fact.activity.name, category=category))
        activity_label.props.halign = Gtk.Align.START
        return activity_label

    def _get_tags_widget(self, fact):
        """
        Return widget to represent ``Fact.tags``.

        Note:
            Right now, this just returns a pseudo-tag to showcase the functionality and
            styling options because ``hamster_lib`` (0.11.0) does not support tags yet.
        """
        def get_tag_widget(name):
            tag_label = Gtk.Label()
            tag_label.set_markup("<small>{}</small>".format(name))
            tag_label.set_name('OverviewTagLabel')
            tag_box = Gtk.EventBox()
            tag_box.set_name('OverviewTagBox')
            tag_box.add(tag_label)
            return tag_box

        tags_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        # Just a pseudo tag for now to illustrate styling.
        tags_box.pack_start(get_tag_widget('pseudo tag'), False, False, 0)
        return tags_box

    def _get_description_widget(self, fact):
        """Return a widget to render ``Fact.description``."""
        description_label = Gtk.Label()
        description_label.set_name('OverviewDescriptionLabel')
        description_label.set_line_wrap(True)
        description_label.set_markup("<small><i>{}</i></small>".format(fact.description))
        description_label.props.halign = Gtk.Align.START
        return description_label


class Summary(Gtk.Box):
    """A widget that shows categories with highest commutative ``Fact.delta``."""

    def __init__(self, category_totals):
        """Initialize widget."""
        super(Summary, self).__init__()

        for category, total in category_totals:
            label = Gtk.Label()
            label.set_markup("<b>{}:</b> {} minutes".format(category,
                                                            int(total.total_seconds() / 60)))
            self.pack_start(label, False, False, 10)


class Charts(Gtk.Grid):
    """
    A widget that lists all categories with their commutative ``Fact.delta``.

    Features a bar chart that will use the highest category total-delta as scale.
    """

    # [TODO] Evaluate ordering.

    def __init__(self, totals):
        """Initialize widget."""
        super(Charts, self).__init__()
        self.attach(self._get_category_widget(totals.category), 0, 0, 1, 1)

    def _get_category_widget(self, category_totals):
        """Return a widget to represent all categories in a column."""
        grid = Gtk.Grid()
        row = 0
        # the highest amount of time spend in a category. This is the scale for
        # all other totals.
        max_total = max(category_totals.values())

        # Build individual category 'rows'.
        for category, total in category_totals.items():
            category_label = Gtk.Label(category)
            bar_chart = HorizontalBarChart(total.total_seconds(), max_total.total_seconds())
            total_label = Gtk.Label(self._get_delta_string(total))
            grid.attach(category_label, 0, row, 1, 1)
            grid.attach(bar_chart, 1, row, 1, 1)
            grid.attach(total_label, 2, row, 1, 1)
            row += 1
        return grid

    # [FIXME] Place in a proper helper module. Maybe even in ``hamster-lib``?
    # In that case make sure to check if we can refactor
    # ``Fact.get_string_delta``!
    def _get_delta_string(self, delta):
        """
        Return a human readable string representation of ``datetime.timedelta`` instance.

        In most contexts its not that useful to present the delta in seconds.
        Instead we return the delta either in minutes or ``hours:minutes`` depending on the
        value.

        Note:
            So far, this does not account for large deltas that span days and more.
        """
        seconds = delta.total_seconds()
        minutes = int(seconds / 60)
        if minutes < 60:
            result = '{} min'.format(minutes)
        else:
            result = '{hours:02d}:{minutes:02d}'.format(
                hours=int(seconds / 3600), minutes=int((seconds % 3600) / 60))
        return result


class HorizontalBarChart(Gtk.DrawingArea):
    """
    A simple horizontal bar chart.

    Note:
        This solution is not to general. It comes without any coordinate system and labeling.
        If you need more, either work towards a dedicated library or incorporate any of the big
        charting backends.
    """

    def __init__(self, value, max_value, width=15, height=40):
        """Initialize widget."""
        super(HorizontalBarChart, self).__init__()
        # [FIXME] Make things more flexible/customizable.

        self._value = float(value)
        self._max_value = float(max_value)
        # -1 for no hints
        self._width_hint = width
        self._height_hint = height

        self.set_size_request(self._width_hint, self._height_hint)

        self.connect('draw', self._on_draw)

    def _on_draw(self, widget, context):
        """Method called on ``draw`` event. Renders the actual widget."""
        context.set_source_rgb(0.8, 0.8, 0.8)
        context.set_line_width(0.5)

        allocation = self.get_allocation()
        width_allocated = allocation.width
        height_allocated = allocation.height

        bar_length = width_allocated * (self._value / self._max_value)
        # [FIXME] Revisit.
        # bar_width = self._height_hint
        bar_width = height_allocated

        x_start, y_start = 0, 0

        bar_x = int(x_start + bar_length)
        bar_y = int(y_start + bar_width)

        context.rectangle(x_start, y_start, bar_x, bar_y)
        context.fill()


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
