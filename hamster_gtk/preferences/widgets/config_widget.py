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

"""This module provides “interface” for config widgets."""


class ConfigWidget(object):
    """
    Abstract class defining unified setter/getter methods for accessing widget values.

    Depending on a particular widget, the way a value is set/retrieved varies while the semantics
    are rather constant. This class provides a consistent interface to be implemented by our custom
    widgets, which should help in making the access to their values cleaner and more concise.
    """

    def get_config_value(self):
        """Get widget value."""
        raise NotImplementedError

    def set_config_value(self, value):
        """Set widget value."""
        raise NotImplementedError
