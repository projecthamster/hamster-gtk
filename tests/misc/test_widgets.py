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

from __future__ import absolute_import, unicode_literals

import pytest
from gi.repository import Gtk
from orderedset import OrderedSet

from hamster_gtk.misc import widgets
from hamster_gtk.misc.widgets.raw_fact_entry import RawFactCompletion
from hamster_gtk.helpers import _u
import hamster_gtk.helpers as helpers


class TestRawFactEntry(object):
    """Unittests for RawFactEntry."""

    def test_init(self, app):
        assert widgets.RawFactEntry(app.controller)

    def test__on_facts_changed(self, raw_fact_entry):
        old_completion = raw_fact_entry.get_completion()
        raw_fact_entry._on_facts_changed(None)
        assert raw_fact_entry.get_completion() is not old_completion


class TestRawFactCompletion(object):
    """Unittests for RawFactCompletion."""

    def test_init__(self, app, mocker):
        """Test instantiation."""
        result = RawFactCompletion(app.controller)
        assert result.get_model()
        assert result.get_text_column() == 0

    def test__get_store(self, raw_fact_completion, activity_factory, mocker):
        """Make sure the ``ListStore`` is constructed to our expectations."""
        raw_fact_completion._get_activities = mocker.MagicMock(
            return_value=activity_factory.build_batch(10))
        result = raw_fact_completion._get_store()
        assert isinstance(result, Gtk.ListStore)
        assert raw_fact_completion._get_activities.called
        assert len(result) == 10

    def test__get_activities(self, app, raw_fact_completion, fact_factory, mocker):
        """Make sure that we fetch the right activities and remove duplicates."""
        # In reality we can not get duplicate facts but separate facts with the
        # same ``Activity`` but this will do just fine.
        fact_1, fact_2 = fact_factory.build_batch(2)
        app.controller.facts.get_all = mocker.MagicMock(
            return_value=[fact_1, fact_2, fact_1])
        result = raw_fact_completion._get_activities()
        assert result == OrderedSet([fact_1.activity, fact_2.activity])

    @pytest.mark.parametrize(('entrystring', 'expectation'), (
        ('foo', True),
        ('bar', True),
        ('fo', True),
        ('oo', True),
        ('ar', True),
        ('ba', True),
        ('foobar', False),
    ))
    def test__match_anywhere(self, raw_fact_completion, activity_model_static, mocker,
            entrystring, expectation):
        """Make sure that only valid sub strings return ``True``."""
        raw_fact_completion.get_model = mocker.MagicMock(return_value=activity_model_static)
        iter = activity_model_static.get_iter(0)
        result = raw_fact_completion._match_anywhere(entrystring, iter, None)
        assert raw_fact_completion._tmp_fact
        assert result is expectation

    def test__match_selected(self, raw_fact_entry, raw_fact_completion, activity,
            activity_model, fact):
        """
        Make sure that selecting a match completes the entry as expected.

        Besides checking that the entry string we also make sure the cursor is placed
        just after the text.
        """
        iter = activity_model.get_iter(0)
        raw_fact_entry.set_completion(raw_fact_completion)
        raw_fact_completion._tmp_fact = fact
        raw_fact_completion._on_match_selected(activity_model, iter)
        entry = raw_fact_completion.get_entry()
        fact.activity = activity
        serialised_fact = helpers.serialise_fact(fact)
        assert _u(entry.get_text()) == serialised_fact
        assert entry.get_position() == len(serialised_fact)
