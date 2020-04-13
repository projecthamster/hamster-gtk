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


"""Screen to handle tracking of an *ongoing fact*."""


from __future__ import absolute_import, unicode_literals

import datetime
from gettext import gettext as _

from gi.repository import GObject, Gtk
from hamster_lib import Fact

import hamster_gtk.helpers as helpers
from hamster_gtk.helpers import _u
from hamster_gtk.misc.widgets import RawFactEntry


class TrackingScreen(Gtk.Stack):
    """Main container for the tracking screen."""

    def __init__(self, app, *args, **kwargs):
        """Setup widget."""
        super(TrackingScreen, self).__init__(*args, **kwargs)
        self._app = app

        self.main_window = helpers.get_parent_window(self)
        self.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        self.set_transition_duration(1000)
        self.current_fact_view = CurrentFactBox(self._app.controller)
        self.current_fact_view.connect('tracking-stopped', self.update)
        self.start_tracking_view = StartTrackingBox(self._app)
        self.start_tracking_view.connect('tracking-started', self.update)
        self.add_titled(self.start_tracking_view, 'start tracking', _("Start Tracking"))
        self.add_titled(self.current_fact_view, 'ongoing fact', _("Show Ongoing Fact"))
        self.update()
        self.show_all()

    def update(self, evt=None):
        """
        Determine which widget should be displayed.

        This depends on whether there exists an *ongoing fact* or not.
        """
        try:
            current_fact = self._app.controller.store.facts.get_tmp_fact()
        except KeyError:
            self.start_tracking_view.show()
            self.set_visible_child(self.start_tracking_view)
        else:
            self.current_fact_view.update(current_fact)
            self.current_fact_view.show()
            self.set_visible_child(self.current_fact_view)
        self.show_all()


class CurrentFactBox(Gtk.Box):
    """Box to be used if current fact is present."""

    __gsignals__ = {
        str('tracking-stopped'): (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, controller):
        """Setup widget."""
        # We need to wrap this in a vbox to limit its vertical expansion.
        # [FIXME]
        # Switch to Grid based layout.
        super(CurrentFactBox, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._controller = controller
        self.content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(self.content, False, False, 0)

    def update(self, fact=None):
        """Update widget content."""
        for child in self.content.get_children():
            child.destroy()

        if not fact:
            try:
                fact = self._controller.store.facts.get_tmp_fact()
            except KeyError:
                # This should never be seen by the user. It would mean that a
                # switch to this screen has been triggered without an ongoing
                # fact existing.
                self.content.pack_start(self._get_invalid_label(), True, True, 0)
        self.content.pack_start(self._get_fact_label(fact), True, True, 0)
        self.content.pack_start(self._get_cancel_button(), False, False, 0)
        self.content.pack_start(self._get_save_button(), False, False, 0)

    def _get_fact_label(self, fact):
        text = '{fact}'.format(fact=fact)
        return Gtk.Label(text)

    def _get_cancel_button(self):
        cancel_button = Gtk.Button(_('Cancel'))
        cancel_button.connect('clicked', self._on_cancel_button)
        return cancel_button

    def _get_save_button(self):
        save_button = Gtk.Button(_('Stop & Save'))
        save_button.connect('clicked', self._on_save_button)
        return save_button

    def _get_invalid_label(self):
        """Return placeholder in case there is no current ongoing fact present."""
        return Gtk.Label(_("There currently is no ongoing fact that could be displayed."))

    # Callbacks
    def _on_cancel_button(self, button):
        """
        Triggerd when 'cancel' button clicked.

        Discard current *ongoing fact* without saving.
        """
        try:
            self._controller.store.facts.cancel_tmp_fact()
        except KeyError as err:
            helpers.show_error(helpers.get_parent_window(self), err)
        else:
            self.emit('tracking-stopped')

    def _on_save_button(self, button):
        """
        Triggerd when 'save' button clicked.

        Save *ongoing fact* to storage.
        """
        try:
            self._controller.store.facts.stop_tmp_fact()
        except Exception as error:
            helpers.show_error(helpers.get_parent_window(self), error)
        else:
            self.emit('tracking-stopped')
            # Inform the controller about the chance.
            self._controller.signal_handler.emit('facts-changed')


class StartTrackingBox(Gtk.Box):
    """Box to be used if no *ongoing fact* is present."""

    __gsignals__ = {
        str('tracking-started'): (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    # [FIXME]
    # Switch to Grid based layout.

    def __init__(self, app, *args, **kwargs):
        """Setup widget."""
        super(StartTrackingBox, self).__init__(orientation=Gtk.Orientation.VERTICAL,
                                               spacing=10, *args, **kwargs)
        self._app = app
        self.set_homogeneous(False)
        self._app.controller.signal_handler.connect('config-changed', self._on_config_changed)

        # [FIXME]
        # Refactor to call separate 'get_widget' methods instead.
        # Introduction text
        text = _('Currently no tracked activity. Want to start one?')
        self.current_fact_label = Gtk.Label(text)
        self.pack_start(self.current_fact_label, False, False, 0)

        # Fact entry field
        autocomplete_split_activity = self._app._config['autocomplete_split_activity']
        self.raw_fact_entry = RawFactEntry(self._app, autocomplete_split_activity)
        self.raw_fact_entry.connect('activate', self._on_raw_fact_entry_activate)
        self.pack_start(self.raw_fact_entry, False, False, 0)

        # Buttons
        start_button = Gtk.Button(label=_("Start Tracking"))
        start_button.connect('clicked', self._on_start_tracking_button)
        self.start_button = start_button
        self.pack_start(start_button, False, False, 0)

        # Recent activities
        if self._app.config['tracking_show_recent_activities']:
            self.recent_activities_widget = self._get_recent_activities_widget()
            self.pack_start(self.recent_activities_widget, True, True, 0)
        else:
            self.recent_activities_widget = None

    def _start_ongoing_fact(self):
        """
        Start a new *ongoing fact*.

        Note:
            Whilst we accept the full ``raw_fact`` syntax, we ignore any ``Fact.end``
            information encoded in the string. Unlike legacy hamster we *only*
            deal with *ongoing facts* in this widget.
        """
        # [FIXME]
        # This should be done in one place only. And the hamster-lib. If at all
        # via hamster-lib.helpers.
        def complete_tmp_fact(fact):
            """Apply fallback logic in case no start time has been encoded."""
            if not fact.start:
                fact.start = datetime.datetime.now()
            # Make sure we dismiss any extracted end information.
            fact.end = None
            return fact

        raw_fact = _u(self.raw_fact_entry.props.text)

        try:
            fact = Fact.create_from_raw_fact(raw_fact)
        except Exception as error:
            helpers.show_error(helpers.get_parent_window(self), error)
        else:
            fact = complete_tmp_fact(fact)

            try:
                fact = self._app.controller.store.facts.save(fact)
            except Exception as error:
                helpers.show_error(self.get_top_level(), error)
            else:
                self.emit('tracking-started')
                self._app.controller.signal_handler.emit('facts-changed')
                self.reset()

    def reset(self):
        """Clear all data entry fields."""
        self.raw_fact_entry.props.text = ''

    def set_raw_fact(self, raw_fact):
        """Set the text in the raw fact entry."""
        self.raw_fact_entry.props.text = raw_fact

    def _get_recent_activities_widget(self):
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        grid = RecentActivitiesGrid(self, self._app.controller)
        # We need to 'show' the grid early in order to make sure space is
        # allocated to its children so they actually have a height that we can
        # use.
        grid.show_all()
        # We fetch an arbitrary Button as height-reference [#224]
        min_height = 0
        children = grid.get_children()
        if children:
            height = children[1].get_preferred_height()[1]
            min_height = self._app.config['tracking_recent_activities_count'] * height

        scrolled_window.set_min_content_height(min_height)
        scrolled_window.add(grid)
        return scrolled_window

    # Callbacks
    def _on_start_tracking_button(self, button):
        """Callback for the 'start tracking' button."""
        self._start_ongoing_fact()

    def _on_raw_fact_entry_activate(self, evt):
        """Callback for when ``enter`` is pressed within the entry."""
        self._start_ongoing_fact()

    def _on_config_changed(self, sender):
        """Callback triggered when 'config-changed' event fired."""
        if self._app.config['tracking_show_recent_activities']:
            # We re-create it even if one existed before because its parameters
            # (e.g. size) may have changed.
            if self.recent_activities_widget:
                self.recent_activities_widget.destroy()
            self.recent_activities_widget = self._get_recent_activities_widget()
            self.pack_start(self.recent_activities_widget, True, True, 0)
        else:
            if self.recent_activities_widget:
                self.recent_activities_widget.destroy()
                self.recent_activities_widget = None
        self.show_all()


class RecentActivitiesGrid(Gtk.Grid):
    """A widget that lists recent activities and allows for quick continued tracking."""

    def __init__(self, start_tracking_widget, controller, *args, **kwargs):
        """
        Initiate widget.

        Args:
            start_tracking_widget (StartTrackingBox): Is needed in order to set the raw fact.
            controller: Is needed in order to query for recent activities.
        """
        super(Gtk.Grid, self).__init__(*args, **kwargs)
        self._start_tracking_widget = start_tracking_widget
        self._controller = controller

        self._controller.signal_handler.connect('facts-changed', self.refresh)
        self._populate()

    def refresh(self, sender=None):
        """Clear the current content and re-populate and re-draw the widget."""
        helpers.clear_children(self)
        self._populate()
        self.show_all()

    def _populate(self):
        """Fill the widget with rows per activity."""
        def add_row_widgets(row_index, activity):
            """
            Add a set of widgets to a specific row based on the activity passed.

            Args:
                row_counter (int): Which row to add to.
                activity (hamster_lib.Activity): The activity that is represented by this row.
            """
            def get_label(activity):
                """Label representing the activity/category combination."""
                label = Gtk.Label(helpers.serialize_activity(activity))
                label.set_halign(Gtk.Align.START)
                return label

            def get_copy_button(activity):
                """
                A button that will copy the activity/category string to the raw fact entry.

                The main use case for this is a user that want to add a description or tag before
                actually starting the tracking.
                """
                button = Gtk.Button('Copy')
                activity = helpers.serialize_activity(activity)
                button.connect('clicked', self._on_copy_button, activity)
                return button

            def get_start_button(activity):
                """A button that will start a new ongoing fact based on that activity."""
                button = Gtk.Button('Start')
                activity = helpers.serialize_activity(activity)
                button.connect('clicked', self._on_start_button, activity)
                return button

            self.attach(get_label(activity), 0, row_index, 1, 1)
            self.attach(get_copy_button(activity), 1, row_index, 1, 1)
            self.attach(get_start_button(activity), 2, row_index, 1, 1)

        today = datetime.date.today()
        start = today - datetime.timedelta(1)
        activities = helpers.get_recent_activities(self._controller, start, today)

        row_index = 0
        for activity in activities:
            add_row_widgets(row_index, activity)
            row_index += 1

    def _on_copy_button(self, button, activity):
        """
        Set the activity/category text in the 'start tracking entry'.

        Args:
            button (Gtk.Button): The button that was clicked.
            activity (text_type): Activity text to be copied as raw fact.

        Note:
            Besides copying the text we also assign focus and place the cursor
            at the end of the pasted text as to facilitate fast entry of
            additional text.
        """
        self._start_tracking_widget.set_raw_fact(activity)
        self._start_tracking_widget.raw_fact_entry.grab_focus_without_selecting()
        self._start_tracking_widget.raw_fact_entry.set_position(len(activity))

    def _on_start_button(self, button, activity):
        """
        Start a new ongoing fact based on this activity/category.

        Args:
            button (Gtk.Button): The button that was clicked.
            activity (text_type): Activity text to be copied as raw fact.
        """
        self._start_tracking_widget.set_raw_fact(activity)
        self._start_tracking_widget._start_ongoing_fact()
