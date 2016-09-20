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

MAX_DIGITS = 20


class DurationEntry(Gtk.SpinButton, ConfigWidget):
    """A widget for entering a duration."""

    # Required else you would need to specify the full module
    # name in ui file
    __gtype_name__ = 'DurationEntry'

    def __init__(self, min=None, max=None, step=None):
        """Initialize widget."""
        super(Gtk.Entry, self).__init__()

        # When any parameter is provided,
        if min is not None or max is not None or step is not None:
            # all arguments have to be specified.
            if min is None or max is None or step is None:
                raise ValueError('Lower and upper bounds and a step must be provided.')
            if min > max:
                raise ValueError('Minimal value has to be lower than maximal value.')
            if step == 0:
                raise ValueError('Step value has to be non-zero.')

            adjustment = Gtk.Adjustment(min, min, max,
                step, 10 * step, 0)

            if abs(step) >= 1:
                digits = 0
            else:
                digits = abs(math.floor(math.log10(abs(step))))

            if digits > MAX_DIGITS:
                digits = MAX_DIGITS

            self.configure(adjustment, step, digits)
            self.set_numeric(True)

    def get_config_value(self):
        """Return selected value."""
        return self.get_value_as_int()

    def set_config_value(self, value):
        """Set given value."""
        self.set_value(int(value))
