# -*- encoding: utf-8 -*-


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

"""Unittests for LabelledWidgetsGrid."""

from __future__ import unicode_literals

import pytest

from hamster_gtk.misc.widgets import LabelledWidgetsGrid


@pytest.mark.parametrize('no_fields', (True, False))
def test_init(preference_page_fields, no_fields):
    """Make sure instantiation works with and without fields provided."""
    if no_fields:
        grid = LabelledWidgetsGrid()
        assert grid._fields == {}
    else:
        grid = LabelledWidgetsGrid(preference_page_fields)
        assert grid._fields == preference_page_fields
    rows = len(grid.get_children()) / 2
    assert rows == len(grid._fields)


def test_get_values(labelled_widgets_grid, preference_page_fields, mocker):
    """Make sure widget fetches values for all its sub-widgets."""
    for key, (label, widget) in preference_page_fields.items():
        widget.get_config_value = mocker.MagicMock()
    labelled_widgets_grid.get_values()
    for key, (label, widget) in preference_page_fields.items():
        assert widget.get_config_value.called


def test_set_values(labelled_widgets_grid, preference_page_fields, mocker):
    """Make sure widget sets values for all its sub-widgets."""
    for key, (label, widget) in preference_page_fields.items():
        widget.set_config_value = mocker.MagicMock()
    labelled_widgets_grid.set_values(preference_page_fields)
    for key, (label, widget) in preference_page_fields.items():
        assert widget.set_config_value.called
