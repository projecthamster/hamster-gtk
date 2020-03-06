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

"""This module provides widgets related to the rendering of charts."""

from __future__ import absolute_import, unicode_literals

import operator

from gi.repository import GObject, Gtk, GLib

from hamster_gtk import helpers


class Charts(Gtk.Grid):
    """
    A widget that lists all categories with their commutative ``Fact.delta``.

    Features a bar chart that will use the highest category total-delta as scale.
    """

    # [TODO] Evaluate ordering.

    def __init__(self, totals):
        """Initialize widget."""
        super(Charts, self).__init__()
        self.set_column_spacing(20)
        self.attach(Gtk.Label(label='Categories'), 0, 0, 1, 1)
        self.attach(self._get_barcharts(totals.category), 0, 1, 1, 1)
        self.attach(Gtk.Label(label='Activities'), 1, 0, 1, 1)
        self.attach(self._get_barcharts(totals.activity), 1, 1, 1, 1)
        self.attach(Gtk.Label(label='Dates'), 2, 0, 1, 1)
        self.attach(self._get_barcharts(totals.date), 2, 1, 1, 1)

    def _get_barcharts(self, totals):
        """
        Return a widget to represent all categories in a column.

        Args:
            totals (dict): A dict that provides delta values for given keys. {key: delta}.

        Returns:
            Gtk.Grid: A Grid which contains one column and as many rows as there
                are ``keys`` in ``totals``. Each row contains a barchart with labels
                showing the delta relative to the highest delta value in ``totals``.
        """
        # The highest amount of time spend. This is the scale for all other totals.
        # Python 2.7 does not yet have support for the ``default`` kwarg.
        if not totals:
            max_total = 0
        else:
            max_total = max(totals.values())
            # Sorting a dict like this returns a list of tuples.
            totals = sorted(totals.items(), key=operator.itemgetter(1),
                            reverse=True)

        grid = Gtk.Grid()
        grid.set_column_spacing(5)
        grid.set_row_spacing(5)

        # Build individual 'rows'.
        row = 0
        for category, delta in totals:
            # For reducing font size we opt for explicit markup in accordance
            # with (3.2) https://developer.gnome.org/gtk3/3.0/gtk-question-index.html#id530878
            # As this solution is relative to the users default font size.
            category_label = Gtk.Label()
            category_label.set_selectable(True)
            category_label.set_halign(Gtk.Align.START)
            category_label.set_markup("<small>{}</small>".format(category))
            bar_chart = HorizontalBarChart(delta.total_seconds(), max_total.total_seconds(), 100,
                15)
            delta_label = Gtk.Label()
            delta_label.set_selectable(True)
            delta_label.set_halign(Gtk.Align.START)
            delta_label.set_markup("<small>{}</small>".format(GLib.markup_escape_text(
                helpers.get_delta_string(delta))))
            grid.attach(category_label, 0, row, 1, 1)
            grid.attach(bar_chart, 1, row, 1, 1)
            grid.attach(delta_label, 2, row, 1, 1)
            row += 1
        return grid


class HorizontalBarChart(Gtk.DrawingArea):
    """
    A simple horizontal bar chart.

    Note:
        This solution is not too general. It comes without any coordinate system and labeling.
        If you need more, either work towards a dedicated library or incorporate any of the big
        charting backends.
    """

    def __init__(self, value, max_value, width=150, height=40):
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
