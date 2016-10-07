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

"""This module provides a Grid for easy construction of preference screens."""

from __future__ import absolute_import

from gi.repository import Gtk


class PreferencesGrid(Gtk.Grid):
    """A widget which arranges labelled fields automatically."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'PreferencesGrid'

    def __init__(self, fields=None):
        """
        Initialize widget.

        Args:
            fields (collections.OrderedDict): Ordered dictionary of {key, (label, widget)}.
        """
        super(Gtk.Grid, self).__init__()

        if fields:
            self._fields = fields
        else:
            self._fields = {}

        row = 0
        for key, (label, widget) in self._fields.items():
            label_widget = Gtk.Label(label)
            label_widget.set_use_underline(True)
            label_widget.set_mnemonic_widget(widget)
            self.attach(label_widget, 0, row, 1, 1)
            self.attach(widget, 1, row, 1, 1)
            row += 1

    def get_values(self):
        """
        Parse config widgets and construct a {field: value} dict.

        Returns:
            dict: Dictionary of config keys/values.
        """
        result = {}
        for key, (label, widget) in self._fields.items():
            result[key] = widget.get_config_value()

        return result

    def set_values(self, values):
        """
        Go through widgets and set their values.

        Args:
            values (dict): Dictionary of config keys/values
        """
        for key, (label, widget) in self._fields.items():
            widget.set_config_value(values.get(key, ''))
