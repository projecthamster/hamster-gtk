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

"""This module provides a HamsterSwitch widget that implements the ConfigWidget mixin."""

from __future__ import absolute_import

from gi.repository import Gtk

from .config_widget import ConfigWidget


class HamsterSwitch(Gtk.Switch, ConfigWidget):
    """A ToggleButton that implements our unified custom ConfigWidget interface."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'HamsterSwitch'

    def __init__(self, active=False):
        """
        Initialize widget.

        Args:
            active (bool, optional): State of the button. Defaults to ``False``.
        """
        super(Gtk.Switch, self).__init__()
        self.set_active(active)

    def get_config_value(self):
        """
        Return the id of the selected item.

        Returns:
            bool: ``True`` if state is ``active``, ``False`` else.
        """
        return self.get_active()

    def set_config_value(self, active):
        """
        Set button state according to passed value.

        Args:
            active (bool): If ``True`` button will be set to ``active``. ``inactive`` else.
        """
        self.set_active(active)
