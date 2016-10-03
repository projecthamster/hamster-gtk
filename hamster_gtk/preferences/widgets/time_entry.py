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

"""This module provides a widget for entering time."""

from __future__ import absolute_import

import datetime

from gi.repository import Gtk
from six import text_type

# [FIXME]
# Remove once hamster-lib has been patched
from hamster_gtk.helpers import _u

from .config_widget import ConfigWidget


class TimeEntry(Gtk.Entry, ConfigWidget):
    """A widget for entering time."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'TimeEntry'

    def get_config_value(self):
        """
        Return time entered into the widget.

        The entered time has to match either ``HH:MM:SS`` or ``HH:MM`` form,
        otherwise an error is thrown.

        Returns:
            datetime.time: Selected time.

        Raises:
            ValueError: When the text entered in the field does not constitute a valid time.
        """
        result = _u(self.get_text())
        # We are tollerant against malformed time information.
        try:
            result = datetime.datetime.strptime(result, '%H:%M:%S').time()
        except ValueError:
            result = datetime.datetime.strptime(result, '%H:%M').time()

        return result

    def set_config_value(self, value):
        """
        Set the widgets time string to passed value.

        Args:
            value (datetime.time): Time to be selected
        """
        self.set_text(text_type(value.strftime('%H:%M:%S')))
