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

    def __init__(self, adj=None):
        """
        Initialize widget.

        Args:
            adj (Gtk.Adjustment, SimpleAdjustment, optional): Adjustment for the widget, either
                :class:`Gtk.Adjustment` or a :class:`SimpleAdjustment`.
                See their respective documentation for more information. Defaults to ``None`` in
                which case it can be set later.
        """
        super(Gtk.HamsterSpinButton, self).__init__()

        if adj is not None:
            if isinstance(adj, SimpleAdjustment):
                if adj.min > adj.max:
                    raise ValueError('Minimal value has to be lower than maximal value.')
                if adj.step == 0:
                    raise ValueError('Step value has to be non-zero.')

                # Because we can not easily enforce our named tuple
                # ``SimpleAdjustment`` to only take ``int``s we instead make
                # sure that its values are cast to ``int`` here before usage.
                adjustment = Gtk.Adjustment(adj.min, adj.min, adj.max, adj.step, 10 * adj.step, 0)
                # [TODO]
                # It is not entirely clear why we do not use
                # ``self.set_adjustment`` like we do for the
                # ``elif Gtk.Adjustment`` branch.
                # According to the original author of this code 'jtojnar' there
                # were some problems with ``climb_rate`` but at this point
                # details are no longer present.
                # As a consequence this should be investigated and cleaned up.
                self.configure(adjustment, adj.step, 0)
                self.set_numeric(True)
            elif isinstance(adj, Gtk.Adjustment):
                self.set_adjustment(adj)
            else:
                raise ValueError('Instance of SimpleAdjustment or Gtk.Adjustment is expected.')

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
