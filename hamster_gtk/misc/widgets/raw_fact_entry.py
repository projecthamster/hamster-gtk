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

"""Widget meant to handle 'raw-fact' strings and provides autocompletion."""
from __future__ import absolute_import, unicode_literals
import datetime

from gi.repository import GObject, Gtk
from orderedset import OrderedSet
from six import text_type
from hamster_lib import Category, Fact
from hamster_gtk.helpers import _u
from hamster_gtk import helpers


class RawFactEntry(Gtk.Entry):
    """A custom entry widgets that provides ``faw fact`` specific autocompletion behaviour."""

    def __init__(self, controller, *args, **kwargs):
        """Instantiate the class."""
        super(RawFactEntry, self).__init__(*args, **kwargs)
        self._controller = controller
        self._controller.signal_handler.connect('facts-changed', self._on_facts_changed)
        self.set_completion(RawFactCompletion(self._controller))

    # Callbacks
    def _on_facts_changed(self, evtl):
        """Callback triggered when facts have changed."""
        self.set_completion(RawFactCompletion(self._controller))


class RawFactCompletion(Gtk.EntryCompletion):
    """
    Return a completion instance to match 'activity@category' strings.

    Returns:
        Gtk.EntryCompletion: Completion instance.
    """

    def __init__(self, controller, *args, **kwargs):
        """instantiate class."""
        super(RawFactCompletion, self).__init__(*args, **kwargs)
        self._controller = controller
        self.set_model(self._get_store())
        self.set_text_column(0)
        self.set_match_func(self._match_anywhere, None)
        self.connect('match-selected', self._on_match_selected)

    def _get_store(self):
        store = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING)
        for activity in self._get_activities():
            category = ''
            if activity.category:
                category = text_type(activity.category.name)
            store.append([
                helpers.serialise_activity(activity), text_type(activity.name), category
            ])
        return store

    def _get_activities(self):
        today = datetime.date.today()
        recent_activities = [fact.activity for fact in self._controller.facts.get_all(
            start=today, end=today)]
        return OrderedSet(recent_activities)

    def _match_anywhere(self, entrystr, iter, data, *args):
        """
        Check if the entrysring is a substring of our text_column.

        Args:
            entrystr (str): The text extracted from the entry so far. Note that key is
                normalized and case-folded (see GLib.utf8_normalize() and
                GLib.utf8_casefold()).
            iter: Iterator position indicating the model row we check against.
            data: Arbitrary user data.

        Returns:
            boot: ``True`` if ``entrystring`` is a substring, ``False`` if not.

        Note this is a custom match function, for details on the general generic
        solution [please see|https://lazka.github.io/pgi-docs/#Gtk-3.0/
        callbacks.html#Gtk.EntryCompletionMatchFunc].
        """
        # 'activity@category' string that we try to match against.
        modelstr = _u(self.get_model()[iter][0])
        # Parse the entire entry string to extract all semantic information.
        fact = Fact.create_from_raw_fact(_u(entrystr))
        # Make the extracted ``Fact`` available to other callbacks.
        self._tmp_fact = fact
        # If the parsed string seems to contain any activity related
        # information, encode it in its canonical form.
        if fact.activity:
            activity_string = helpers.serialise_activity(fact.activity)
        return activity_string in modelstr

    def _on_match_selected(self, model, iter):
        """Callback to be executed once a match is selected by the user."""
        activity_name = _u(model[iter][1])
        category_name = _u(model[iter][2])
        fact = self._tmp_fact
        # We complete ``self._tmp_fact`` with activity/category information
        # taken from the matching model row.
        fact.activity.name = activity_name
        if category_name:
            fact.activity.category = Category(category_name)
        else:
            fact.activity.category = None
        # Put a string that contains all available and completed information
        # in the text entry.
        self.get_entry().set_text(helpers.serialise_fact(fact))
        self.get_entry().set_position(-1)
        return True
