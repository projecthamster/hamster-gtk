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

"""This module provides simplified Adjustment object for :class:`.DurationEntry`."""


class SimpleAdjustment(tuple):
    """
    Simplified version of :class:`Gtk.Adjustment`.

    Note:
        Instances of this class are immutable.
    """

    def __new__(_cls, min, max, step):
        """Create new instance of SimpleAdjustment(min, max, step)."""
        return tuple.__new__(_cls, (min, max, step))

    @property
    def min(self):
        """
        The lower bound for the :class:`.DurationEntry` – its value cannot be any lower than this.

        Alias for field number 0.

        Returns:
            int: The minimum value.
        """
        return self[0]

    @property
    def max(self):
        """
        The upper bound for the :class:`.DurationEntry` – its value cannot be any lower than this.

        Alias for field number 1.

        Returns:
            int: The maximum value.
        """
        return self[1]

    @property
    def step(self):
        """
        The amount the value will be increased/decreased when the corresponding button is clicked.

        Alias for field number 2.

        Returns:
            int: The step size.
        """
        return self[2]

    def replace(self, **kwds):
        """
        Return a new :class:`SimpleAdjustment` object replacing specified fields with new values.

        Args:
            min (int): Optional, new value for min.
            max (int): Optional, new value for max.
            step (int): Optional, new value for step.
        """
        result = tuple.__new__(self.__class__, list(map(kwds.pop, ('min', 'max', 'step'), self)))
        if kwds:
            raise ValueError('Got unexpected field names: %r' % list(kwds))
        return result

    def __repr__(self):
        """Return a nicely formatted representation string."""
        return self.__class__.__name__ + '(min=%r, max=%r, step=%r)' % self
