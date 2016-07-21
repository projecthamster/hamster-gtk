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

In order to do that, this module contains multiple auxiliary widgets to render specific aspects.

Due to using default ``Gtk`` classes as bases for our custom widgets (such as
``HorizontalBarChart``) we are able to greatly reduce the codebase compared to ``legacy hamster``.
The one major downside is, that we can not easily reimplement its eye candy
'slide in from the bottom' transition when opening the 'details' widget. Whilst this is unfortunate
reimplementing this properly is out of the scope right now and a price we are willing to pay.
"""

from __future__ import absolute_import

import datetime
import operator
from collections import defaultdict, namedtuple

from gi.repository import Gtk
from hamster_lib import reports

from . import widgets
from .. import helpers

Totals = namedtuple('Totals', ('activity', 'category', 'date'))


class OverviewDialog(Gtk.Dialog):
    """Overview-screen that provides information about a users facts.."""

    def __init__(self, parent, app, *args, **kwargs):
        """Initialize dialog."""
        super(OverviewDialog, self).__init__(*args, **kwargs)
        self.set_transient_for(parent)
        self.titlebar = widgets.HeaderBar(app.controler)
        self._parent = parent
        self._app = app
        self._connect_signals()

        self.set_default_size(640, 800)
        self.set_titlebar(self.titlebar)
        self.main_box = self.get_content_area()
        self._daterange = self._get_default_daterange()

        self._charts = False

        # [FIXME] Should be a property to make sure the signal is emitted
        self._facts = None
        self._grouped_facts = None

        self.refresh()
        self.show_all()

    @property
    def _daterange(self):
        """Return the 'daterange' for which this overview displays facts."""
        return self.__daterange

    @_daterange.setter
    def _daterange(self, daterange):
        """Set daterange and make sure we emit the corresponding signal."""
        self.__daterange = daterange
        self._app.controler.signal_handler.emit('daterange-changed', self.__daterange)

    def _connect_signals(self):
        """Connect signals this instance listens for."""
        self._app.controler.signal_handler.connect('config-changed', self._on_config_changed)
        self._app.controler.signal_handler.connect('facts-changed', self._on_facts_changed)
        self._app.controler.signal_handler.connect('daterange-changed', self._on_daterange_changed)

    def _get_default_daterange(self):
        """Return the default daterange used when none has been selected by user."""
        today = datetime.date.today()
        return (today, today)

    def _on_config_changed(self, sender):
        """Callback to be triggered if the applications config has changed."""
        self.refresh()

    def _on_facts_changed(self, sender):
        """Callback to be triggered if stored facts have been changed."""
        self.refresh()

    def _on_daterange_changed(self, sender, daterange):
        """Callback to be triggered if the 'daterange' changed."""
        self.refresh()

    def refresh(self):
        """Recompute data and trigger redrawing."""
        self._facts = self._get_facts()
        self._grouped_facts, self._totals = self._group_facts()

        helpers.clear_children(self.main_box)

        facts_window = Gtk.ScrolledWindow()
        self.factlist = widgets.FactGrid(self._app.controler, self._grouped_facts.by_date)
        facts_window.add(self.factlist)
        self.main_box.pack_start(facts_window, True, True, 0)

        # [FIXME]
        # Evaluate transfer to helper or even hamster-lib.
        self.totals_panel = widgets.Summary(self._get_highest_totals(self._totals.category, 3))
        self.main_box.pack_start(self.totals_panel, False, False, 0)

        # [FIXME]
        # Only show button if there are facts.
        charts_button = Gtk.Button('click to show more details ...')
        charts_button.connect('clicked', self._on_charts_button)
        self.main_box.pack_start(charts_button, False, True, 0)

        self.main_box.show_all()

    def _on_charts_button(self, button):
        """On button click either show or hide extended details."""
        if self._charts:
            self._charts.destroy()
            self._charts = False
        else:
            self._charts = widgets.Charts(self._totals)
            self.main_box.pack_start(self._charts, False, False, 0)
            self.show_all()

    # [FIXME]
    # To avoid multiple falls to the backend, maybe some rudimentaty chaching
    # would be sensible.
    def _get_facts(self):
        """
        Collect and return all facts too be shown, not necessarily be visible.

        A TypeError may indicated that the passed daterange istances may be of
        invalid type. A ValueError that end is before start.
        """
        start, end = self._daterange
        try:
            result = self._app.store.facts.get_all(start, end)
        except (TypeError, ValueError) as error:
            helpers.show_error(self.get_toplevel(), error)
        else:
            return result

    def _group_facts(self):
        """
        Return ``self._facts`` grouped by various keys.

        Note:
            We handle totals as part of this method in order to limit the
            amount of iterations over ``self._facts``.
        """
        # [FIXME]
        # This is probably useful to other clients as well and worth
        # considering for hamster-lib.
        def get_total(totals):
            """Return a dictionary of max deltas per key."""
            max_total = defaultdict(datetime.timedelta)
            # [FIXME]
            # is this really the *max* total, and not rather the total per key?
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
        # In case of a 'month' we should return another (variable) month
        # length not necessarily the same length
        orig_start, orig_end = self._daterange
        offset = (orig_end - orig_start) + datetime.timedelta(days=1)
        self._daterange = (orig_start - offset, orig_end - offset)

    def apply_next_daterange(self):
        """Apply a daterange of equal 'length' right before the given range."""
        # [FIXME]
        # In case of a 'month' we should return another (variable) month
        # length not necessarily the same length
        orig_start, orig_end = self._daterange
        offset = (orig_end - orig_start) + datetime.timedelta(days=1)
        self._daterange = (orig_start + offset, orig_end + offset)

    def _export_facts(self, target_path):
        """
        Export current set of facts to file.

        Args:
            target_path (text_type): Location to export to.
        """
        writer = reports.TSVWriter(target_path)
        writer.write_report(self._get_facts())

    # Widgets
    def _get_summery_widget(self, category_totals):
        # [FIXME]
        # Change to Grid based layout
        box = Gtk.Box
        for category, total in category_totals:
            label = Gtk.Label()
            label.set_markup("<b>{}:</b> {} minutes".format(category,
                                                            int(total.total_seconds() / 60)))
            box.pack_start(label, False, False, 10)
        return box

    # Callbacks
