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

"""This module provides SpinButton widget extended to store preferences."""

from __future__ import absolute_import

import math

from gi.repository import Gtk

from .config_widget import ConfigWidget
from collections import namedtuple

SimpleAdjustment = namedtuple('SimpleAdjustment', ('min', 'max', 'step'))
"""Simpilified version of :class:`Gtk.Adjustment`."""
SimpleAdjustment.min.__doc__ = """The minimum value."""
SimpleAdjustment.max.__doc__ = """The maximum value."""
SimpleAdjustment.step.__doc__ = """The amount the value will be increased/decreased
when the corresponding buttons are clicked."""


class DurationEntry(Gtk.SpinButton, ConfigWidget):
    """A widget for entering a duration."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'DurationEntry'

    MAX_DIGITS = 20
    """Maximum number of digits displayed after decimal point."""

    def __init__(self, adj=None):
        """
        Initialize widget.

        Args:
            adj: Adjustment for the widget, either :class:`Gtk.Adjustment` or
                a :class:`SimpleAdjustment`. See their respective documentation
                for more information.
        """
        super(Gtk.Entry, self).__init__()

        if adj is not None:
            if isinstance(adj, SimpleAdjustment):
                if adj.min > adj.max:
                    raise ValueError('Minimal value has to be lower than maximal value.')
                if adj.step == 0:
                    raise ValueError('Step value has to be non-zero.')

                adjustment = Gtk.Adjustment(adj.min, adj.min, adj.max, adj.step, 10 * adj.step, 0)

                if abs(adj.step) >= 1:
                    digits = 0
                else:
                    digits = abs(math.floor(math.log10(abs(adj.step))))

                if digits > self.MAX_DIGITS:
                    digits = self.MAX_DIGITS

                self.configure(adjustment, adj.step, digits)
                self.set_numeric(True)
            elif isinstance(adj, Gtk.Adjustment):
                self.set_adjustment(adj)
            else:
                raise ValueError('Instance of SimpleAdjustment or Gtk.Adjustment is expected.')

    def get_config_value(self):
        """Return selected value.

        Returns:
            :class:`int`: Number entered into the widget
        """
        return self.get_value_as_int()

    def set_config_value(self, value):
        """
        Set given value.

        Args:
            value: Value to be set
        """
        self.set_value(int(value))
