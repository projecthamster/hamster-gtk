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

from gi.repository import Gtk


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
        # [FIXME]
        # Add analogous widgets for tags and activities?

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

    # [FIXME]
    # Place in a proper helper module. Maybe even in ``hamster-lib``?
    # In that case make sure to check if we can refactor
    # ``Fact.get_string_delta``!
    def _get_delta_string(self, delta):
        """
        Return a human readable representation of ``datetime.timedelta`` instance.

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
