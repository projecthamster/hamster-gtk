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

"""Unittests for RawFactEntry."""

from __future__ import absolute_import, unicode_literals

from hamster_gtk.misc import widgets


def test_init(app):
        assert widgets.RawFactEntry(app.controller)


def test__on_facts_changed(raw_fact_entry):
        old_completion = raw_fact_entry.get_completion()
        raw_fact_entry._on_facts_changed(None)
        assert raw_fact_entry.get_completion() is not old_completion
