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

"""This module provides ComboBoxText widget extended to store preferences."""

from __future__ import absolute_import

from gi.repository import Gtk

# [FIXME]
# Remove once hamster-lib has been patched
from hamster_gtk.helpers import _u

from .config_widget import ConfigWidget


class HamsterComboBoxText(Gtk.ComboBoxText, ConfigWidget):
    """A ComboBoxText that implements our unified custom ConfigWidget interface."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'HamsterComboBoxText'

    def __init__(self, items=None):
        """
        Initialize widget.

        Args:
            items (dict): Dict of ids/texts to be selectable.
        """
        super(Gtk.ComboBoxText, self).__init__()

        if items is not None:
            for id, text in items:
                self.append(id, text)

    def get_config_value(self):
        """
        Return the id of the selected item.

        Returns:
            six.text_type: Identifier of the selected item
        """
        return _u(self.get_active_id())

    def set_config_value(self, id):
        """
        Select item with a given id.

        Args:
            id (six.text_type): Identifier of an item to be selected
        """
        self.set_active_id(id)
