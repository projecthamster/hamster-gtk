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


import datetime
from gettext import gettext as _

from gi.repository import Gtk
from hamster_lib import Fact

import hamster_gtk.helpers as helpers


class TrackingScreen(Gtk.Stack):
    """Main container for the tracking screen."""

    def __init__(self, parent, app):
        """Setup widget."""
        super(TrackingScreen, self).__init__()
        self._parent = parent
        self._app = app

        self.main_window = parent
        self.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        self.set_transition_duration(1000)
        self.current_fact_view = CurrentFactBox(self, self._app)
        self.start_tracking_view = StartTrackingBox(self, self._app)
        self.add_titled(self.start_tracking_view, 'start tracking', _("Start Tracking"))
        self.add_titled(self.current_fact_view, 'ongoing fact', _("Show Ongoing Fact"))
        self.update()
        self.show_all()

    def update(self):
        """
        Determine which widget should be displayed.

        This depends on wether there exists an *ongoing fact* or not.
        """
        try:
            current_fact = self._app.controler.store.facts.get_tmp_fact()
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

    def __init__(self, parent, app):
        """Setup widget."""
        # We need to wrap this in a vbox to limit its vertical expansion.
        super(CurrentFactBox, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent = parent
        self._app = app
        self.main_window = parent.main_window
        self.content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(self.content, False, False, 0)
        self.update()

    def update(self, fact=None):
        """Update widget content."""
        for child in self.content.get_children():
            child.destroy()

        if not fact:
            try:
                fact = self.fact = self._app.controler.store.facts.get_tmp_fact()
            except KeyError:
                # This should never be seen by the user. It would mean that a
                # switch to this screen has been triggered without an ongoing
                # fact existing.
                self.content.pack_start(self._get_invalid_label(), True, True, 0)
        else:
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

    # Button methods
    def _on_cancel_button(self, button):
        """
        Triggerd when 'cancel' button clicked.

        Discard current *ongoing fact* without saving.
        """
        self.main_window._app.store.facts.cancel_tmp_fact()
        self.parent.switch()

    def _on_save_button(self, button):
        """
        Triggerd when 'save' button clicked.

        Save *ongoing fact* to storage.
        """
        try:
            self.main_window._app.store.facts.stop_tmp_fact()
        except Exception as error:
            helpers.show_error(self.main_window, error)
        else:
            self.parent.update()
            # Inform the main window about the chance.
            self._app.controler.signal_handler.emit('facts-changed')


class StartTrackingBox(Gtk.Box):
    """Box to be used if no *ongoing fact* is present."""

    def __init__(self, parent, app, *args, **kwargs):
        """Setup widget."""
        super(StartTrackingBox, self).__init__(orientation=Gtk.Orientation.VERTICAL,
                                               spacing=10, *args, **kwargs)
        self.parent = parent
        self._app = app

        self.main_window = parent.main_window
        self.set_homogeneous(False)

        # Introduction text
        text = _('Currently no tracked activity. Want to start one?')
        self.current_fact_label = Gtk.Label(text)
        self.pack_start(self.current_fact_label, False, False, 0)

        # Fact entry field
        self.raw_fact_entry = Gtk.Entry()
        self.pack_start(self.raw_fact_entry, False, False, 0)

        # Buttons
        start_button = Gtk.Button(label=_('Start Tracking'))
        start_button.connect('clicked', self._on_start_tracking_button)
        self.pack_start(start_button, False, False, 0)

    def _on_start_tracking_button(self, button):
        """
        Start a new *ongoing fact*.

        Note:
            Whilst we accept the full ``raw_fact`` syntax, we ignore any ``Fact.end``
            information encoded in the string. Unlike legacy hamster we *only*
            deal with *ongoing facts* in this widget.
        """
        def complete_tmp_fact(fact):
            """Apply fallback logic in case no start time has been encoded."""
            if not fact.start:
                fact.start = datetime.datetime.now()
            # Make sure we dismuss any extracted end information.
            fact.end = None
            return fact

        raw_fact = self.raw_fact_entry.props.text

        try:
            fact = Fact.create_from_raw_fact(raw_fact)
        except Exception as error:
            helpers.show_error(self.main_window, error)
        else:
            fact = complete_tmp_fact(fact)

            try:
                fact = self.main_window._app.store.facts.save(fact)
            except Exception as error:
                helpers.show_error(self.main_window, error)
            else:
                self.parent.update()
