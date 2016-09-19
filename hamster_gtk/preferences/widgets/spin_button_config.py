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

from gi.repository import Gtk
from .widget_config import WidgetConfig


class SpinButtonConfig(Gtk.SpinButton, WidgetConfig):
    """A spin button that stores configuration."""

    # Required else you would need to specify the full module
    # name in ui file
    __gtype_name__ = 'SpinButtonConfig'

    def get_config_value(self):
        """Return selected value."""
        return self.get_value_as_int()

    def set_config_value(self, value):
        """Set given value."""
        # We need to check for None in order to allow 0 as initial value.
        if value is not None:
            self.set_value(int(value))
