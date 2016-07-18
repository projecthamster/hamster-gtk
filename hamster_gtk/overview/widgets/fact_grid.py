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

"""This module provides widgets related to the 'listing' of facts."""

# [FIXME]
# Adding 'unicode_literals' raises encoding issues. This is a major sign we
# have a unicode issue!
from __future__ import absolute_import

from gi.repository import Gtk

from hamster_gtk import helpers
from hamster_gtk.misc.dialogs import EditFactDialog


class FactGrid(Gtk.Grid):
    """Listing of facts per day."""

    def __init__(self, controler, initial, *args, **kwargs):
        """
        Initialize widget.

        Args:
            initial (dict): Dictionary where keys represent individual dates
                and values an iterable of facts of that date.
        """
        super(FactGrid, self).__init__(*args, **kwargs)
        self.set_column_spacing(0)

        row = 0
        for date, facts in initial.items():
            # [FIXME] Order by fact start
            self.attach(self._get_date_widget(date), 0, row, 1, 1)
            self.attach(self._get_fact_list(controler, facts), 1, row, 1, 1)
            row += 1

    def _get_date_widget(self, date):
        """
        Return a widget to be used in the 'date column'.

        Args:
            date (datetime.date): Date to be displayed.
        """
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

    def _get_fact_list(self, controler, facts):
        """
        Return a widget representing all of the dates facts.

        We use a ``Gtk.ListBox`` as opposed to just adding widgets representing
        the facts right to the ``FactGrid`` in order to make use of
        ``Gtk.ListBox`` keyboard and mouse navigation / event handling.
        """
        # [FIXME]
        # It would be preferable to not have to pass the controler instance
        # through all the way, but for now it will do.
        return FactListBox(controler, facts)


class FactListBox(Gtk.ListBox):
    """A List widget that represents each fact in a seperate actionable row."""

    def __init__(self, controler, facts):
        """Initialize widget."""
        super(FactListBox, self).__init__()

        self._controler = controler

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
        edit_dialog = EditFactDialog(self.get_toplevel(), row.fact)
        response = edit_dialog.run()
        if response == Gtk.ResponseType.CANCEL:
            pass
        elif response == Gtk.ResponseType.REJECT:
            self._delete_fact(edit_dialog._fact)
        elif response == Gtk.ResponseType.APPLY:
            self._update_fact(edit_dialog.updated_fact)
        edit_dialog.destroy()

    def _update_fact(self, fact):
        """Update the a fact with values from edit dialog."""
        try:
            self._controler.store.facts.save(fact)
        except (ValueError, KeyError) as message:
            helpers.show_error(self, message)
        else:
            self._controler.signal_handler.emit('facts_changed')

    def _delete_fact(self, fact):
        """Delete fact from the backend. No further confirmation is required."""
        try:
            result = self._controler.store.facts.remove(fact)
        except (ValueError, KeyError) as error:
            helpers.show_error(self.get_toplevel(), error)
        else:
            self._controler.signal_handler.emit('facts_changed')
            return result


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
        # [FIXME]
        # Switch to grid design.
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
        # [FIXME]
        # Switch to Grid based design
        self.pack_start(self._get_activity_widget(fact), True, True, 0)
        self.pack_start(self._get_tags_widget(fact), True, True, 0)
        if fact.description:
            self.pack_start(self._get_description_widget(fact), False, False, 0)

    def _get_activity_widget(self, fact):
        """Return widget to render the activity, including its related category."""
        # [FIXME]
        # Once 'preferences/config' is live, we can change this.
        # Most likly we do not actually need to jump through extra hoops as
        # legacy hamster did but just use a i18n'ed string and be done.
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
        # [FIXME]
        # Switch to Grid based layout.
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
