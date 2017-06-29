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

from collections import namedtuple

from gi.repository import Gtk

from .config_widget import ConfigWidget

SimpleAdjustment = namedtuple('SimpleAdjustment', ('min', 'max', 'step'))
"""
Simpilified version of :class:`Gtk.Adjustment`.

Args:
    min: The minimum value.
    max: The maximum value.
    step: The amount the value will be increased/decreased
        when the corresponding button is clicked.
"""


class HamsterSpinButton(Gtk.SpinButton, ConfigWidget):
    """A widget for entering a duration."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'HamsterSpinButton'

    def __init__(self, adjustment=None, climb_rate=0, digits=0):
        """
        Initialize widget.

        Args:
            adj (Gtk.Adjustment, SimpleAdjustment, optional): Adjustment for the widget, either
                :class:`Gtk.Adjustment` or a :class:`SimpleAdjustment`.
                See their respective documentation for more information. Defaults to ``None`` in
                which case it can be set later.
            climb_rate (float): See Gtk.SpinButton documentation.
            digits (int): See Gtk.SpinButton documentation.
        """
        super(Gtk.SpinButton, self).__init__()

        self.set_numeric(True)

        if adjustment is not None:
            if isinstance(adjustment, SimpleAdjustment):
                self._validate_simple_adjustment(adjustment)
                adjustment = Gtk.Adjustment(adjustment.min, adjustment.min, adjustment.max,
                    adjustment.step, 10 * adjustment.step, 0)
            elif not isinstance(adjustment, Gtk.Adjustment):
                raise ValueError('Instance of SimpleAdjustment or Gtk.Adjustment is expected.')

        self.configure(adjustment, climb_rate, digits)

    def _validate_simple_adjustment(self, adjustment):
        if adjustment.min > adjustment.max:
            raise ValueError('Minimal value has to be lower than maximal value.')
        if adjustment.step == 0:
            raise ValueError('Step value has to be non-zero.')

        return True

    def get_config_value(self):
        """Return selected value.

        Returns:
            int: Number entered into the widget
        """
        return self.get_value_as_int()

    def set_config_value(self, value):
        """
        Set given value.

        Args:
            value (int): Value to be set
        """
        self.set_value(int(value))
