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
from six import text_type

from hamster_gtk import helpers
from hamster_gtk.helpers import _u
from orderedset import OrderedSet


def _get_segment_boundaries(segment, match):
    """
    Return start and end positions for a given segment.

    Args:
        segmemt (text_type): The segment we want to know the boundries for. Valid choices are:
            ``activity``, ``category``, ``activity+category``, ``tags`` and ``description``.
        match: A match object instance.

    Returns:
        tuple: Tuple (int, int) representing the given segment's start and end position.
    """
    # We can not simply use ``match.span`` as ``activity+category`` is not
    # represented as such in the match instance.
    if segment == 'activity+category':
        activity, category = match.group('activity', 'category')
        start = match.start('activity')
        end = match.end('category')
        if not activity:
            start = match.start('category')
        if not category:
            end = match.end('activity')
        result = (start, end)
    else:
        result = (match.start(segment), match.end(segment))
    return result


class RawFactEntry(Gtk.Entry):
    """A custom entry widgets that provides ``raw fact`` specific autocompletion behaviour."""

    def __init__(self, app, split_activity_autocomplete=False, *args, **kwargs):
        """
        Instantiate class.

        Args:
            controller: Controller instance.
            config: Config instance.
            split_activity_autocomplete (bool, optional): If ``True`` autocompletion
                will handle ``Activity.name`` and ``Activity.category`` independently.
                If ``False`` it will try to match against the concatenated ``name@category``
                string. Defaults to ``False``.
        """
        super(RawFactEntry, self).__init__(*args, **kwargs)
        self._app = app
        self._app.controller.signal_handler.connect('facts-changed', self._on_facts_changed)
        self._split_activity_autocomplete = split_activity_autocomplete
        self.set_completion(RawFactCompletion(app))
        # The re.match instance of the current string or None
        self.match = None
        # Identifier for the segment the cursor is currently in. None if no
        # match is available.
        self.current_segment = None
        self.connect('changed', self._on_changed)

    def replace_segment_text(self, segment_string,):
        """
        Replace the substring of the entry text that matches ``self.current_segment``.

        Args:
            segment_string (text_type): New text that is to replace the old.

        Returns:
            None
        """
        def add_prefix(segment, string):
            # [TODO]
            # Once autocompletion supports more segments with prefixes, this will
            # need to be extended.
            result = string
            if segment == 'category':
                result = '@{}'.format(string)
            return result

        if not self.match:
            return

        match = self.match
        segment = self.current_segment
        segment_string = add_prefix(segment, segment_string)
        segment_start, segment_end = _get_segment_boundaries(segment, match)
        old_string = _u(self.get_text())
        new_string = '{}{}{}'.format(
            old_string[:segment_start],
            segment_string,
            old_string[segment_end:],
        )
        self.set_text(new_string)
        self.set_position(segment_start + len(segment_string))

    def get_segment_text(self):
        """
        Return the string for the segment given by ``self.current_segment``.

        Returns:
            text_type or None: Returns ``None`` if ``self.current_segment=None``.
        """
        def remove_prefix(segment, string):
            # [TODO]
            # Once autocompletion supports more segments with prefixes, this will
            # need to be extended.
            result = string
            if segment == 'category':
                result = string[1:]
            return result

        if self.current_segment is None:
            return

        if self.current_segment == 'activity+category':
            activity, category = self.match.group('activity', 'category')
            if activity or category:
                result = ''
                if activity:
                    result += activity
                if category:
                    result += category
            else:
                result = None
        else:
            result = self.match.group(self.current_segment)
            if result:
                result = remove_prefix(self.current_segment, result)
        return result

    # Callbacks
    def _on_facts_changed(self, evt):
        """Callback triggered when facts have changed."""
        self.set_completion(RawFactCompletion(self._app))

    def _on_changed(self, widget):
        """
        Callback triggered whenever entry text is changed.

        Its main task is to keep track of which segment of the raw fact string the
        user is currently editing. For this the whole string is inspected and matched
        against our regex. By comparing the current cursor position with individual
        matched segment spans a guess about which one is currently edited is made.
        """
        def get_segment(match):
            """
            Return the segment the cursor is currently in.

            Returns:
                text_type or None: Segment identifier or None if cursor not within any segment.
            """
            result = None
            cursor_position = self.get_position()

            segments = ['timeinfo', 'tags', 'description']
            if self._split_activity_autocomplete:
                segments.extend(('activity', 'category'))
            else:
                segments.append('activity+category')

            for segment in segments:
                start, end = _get_segment_boundaries(segment, match)
                if start <= cursor_position <= end:
                    result = segment

            return result

        def run_autocomplete(segment):
            completion = self.get_completion()
            completion.set_model(completion.segment_models[segment])

        self.match = helpers.decompose_raw_fact_string(_u(self.get_text()), raw=True)
        # Do nothing if we could not 'match' the raw string.
        # Please note that the completions 'match function' will be run
        # regardless of what we do here.
        if self.match:
            self.current_segment = get_segment(self.match)
            if self.current_segment in ('activity', 'category', 'activity+category'):
                run_autocomplete(self.current_segment)


class RawFactCompletion(Gtk.EntryCompletion):
    """
    Return a completion instance to match 'activity@category' strings.

    Returns:
        Gtk.EntryCompletion: Completion instance.
    """

    def __init__(self, app, *args, **kwargs):
        """Instantiate class."""
        super(RawFactCompletion, self).__init__(*args, **kwargs)
        self._app = app
        self._activities_model, self._categories_model, self._activities_with_categories_model = (
            self._get_stores()
        )
        self.set_model(self._activities_model)
        self.set_text_column(0)
        self.set_match_func(self._match_anywhere, None)
        self.connect('match-selected', self._on_match_selected)
        self.segment_models = {
            'activity': self._activities_model,
            'category': self._categories_model,
            'activity+category': self._activities_with_categories_model,
        }

    def _get_stores(self):
        activities, categories = OrderedSet(), OrderedSet()

        activities_with_categories_store = Gtk.ListStore(GObject.TYPE_STRING)
        for activity in self._get_activities():
            activities.add(text_type(activity.name))
            if activity.category:
                categories.add(text_type(activity.category.name))

            # While we iterate over all activities anyway, we use this to
            # populate the 'activity+category' store right away.
            if activity.category:
                text = '{activity}@{category}'.format(
                    activity=activity.name, category=activity.category.name
                )
            else:
                text = activity.name
            activities_with_categories_store.append([text])

        activities_store = Gtk.ListStore(GObject.TYPE_STRING)
        for activity in activities:
            activities_store.append([activity])

        categories_store = Gtk.ListStore(GObject.TYPE_STRING)
        for category in categories:
            categories_store.append([category])
        return (activities_store, categories_store, activities_with_categories_store)

    def _get_activities(self):
        """
        Return all activities that should be considered for autocompletion.

        This is the place where we define which reference frame should be used
        for autocomplete suggestions.
        """
        today = datetime.date.today()
        start = today - datetime.timedelta(days=self._app.config['autocomplete_activities_offset'])
        recent_activities = [fact.activity for fact in self._app.controller.facts.get_all(
            start=start, end=today)]
        return OrderedSet(recent_activities)

    def _match_anywhere(self, completion, entrystr, iter, data):
        """
        Check if the entrystring is a substring of our text_column.

        Args:
            entrystr (str): The text extracted from the entry so far. Note that
                we do not use this at all. Instead we fetch
                ``self.get_entry().get_segment_text`` in order to get only the text
                of the currently edited segment.
            iter: Iterator position indicating the model row we check against.
                This works because
                ``self.get_entry()._on_changed`` makes sure that the completion
                model is set properly according to ``self.get_entry().current_segment``.
            data: Arbitrary user data.

        Returns:
            bool: ``True`` if ``self.get_entry.get_segment_text`` is a substring,
                ``False`` if not.

        Note this is a custom match function, for details on the general generic
        solution [please see|https://lazka.github.io/pgi-docs/#Gtk-3.0/
        callbacks.html#Gtk.EntryCompletionMatchFunc].
        """
        result = False
        entry = self.get_entry()
        modelstring = ''
        hit = self.get_model()[iter][0]
        # We only need to check if the string was matched at all. Otherwise
        # there are no 'segments' anyway.
        if hit and entry.match:
            modelstring = _u(hit)
            segment_text = entry.get_segment_text()
            result = segment_text in modelstring
        return result

    def _on_match_selected(self, completion, model, iter):
        """Callback to be executed once a match is selected by the user."""
        entry = self.get_entry()
        name = _u(model[iter][0])
        entry.replace_segment_text(name)
        return True
