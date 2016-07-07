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


"""Main module for 'hamster-gtk'. Provides central ``Gtk.Application`` instance."""


from __future__ import unicode_literals

import traceback

from gettext import gettext as _

import gi
gi.require_version('Gdk', '3.0')  # NOQA
gi.require_version('Gtk', '3.0')  # NOQA
import hamster_lib
from gi.repository import Gdk, GObject, Gtk

from . import helpers
from .screens.overview import OverviewScreen
from .screens.tracking import TrackingScreen


APP_NAME = 'Hamster-GTK'
DEFAULT_WINDOW_SIZE = (400, 200)


class HeaderBar(Gtk.HeaderBar):
    """Header bar for the main application window."""

    def __init__(self, parent, app, **kwargs):
        """Initialize header bar."""
        super(HeaderBar, self).__init__(**kwargs)
        self._parent = parent
        self._app = app

        self.set_title(_("Hamster-GTK"))
        self.set_subtitle(_("Your friendly time tracker."))
        self.set_show_close_button(True)

        overview_button = Gtk.Button('Overview')
        overview_button.connect('clicked', self._on_overview_button)
        self.pack_end(overview_button)

    def _on_overview_button(self, button):
        """Callback for overview button."""
        if not self._parent._overview_window:
            self._parent._overview_window = OverviewScreen(self._parent, self._app)
        self._parent._overview_window.present()


class MainWindow(Gtk.ApplicationWindow):
    """Main window class that is the center of our GUI."""

    def __init__(self, app, *args, **kwargs):
        """Initialize window."""
        super(MainWindow, self).__init__(*args, application=app, **kwargs)
        # Some basic inventory
        self._app = app
        self._overview_window = None

        # Styling
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_titlebar(HeaderBar(self, self._app))
        self.set_default_size(*DEFAULT_WINDOW_SIZE)

        # Setup css
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(self._get_css().encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Set tracking as default screen at startup.
        self.add(TrackingScreen(self, self._app))

    def _get_css(self):
        """
        Return a string representing our CSS definitions.

        This will be obsolete in the future, once we move it to a dedicated file.
        See Issue #4.
        """
        return """
            #DayRowDateBox {
                background: #dfdfdf;
            }

            #OverviewDateLabel {
                padding-left: 10px;
                padding-right: 10px;
            }

            #OverviewTagLabel {
                padding: 2px;
            }

            #OverviewDescriptionLabel {
                padding-bottom: 20px;
            }

            #OverviewTagBox {
                background: gray;
                border-radius: 5px;
                border-color: gray;
                border-width: 1px 1px 1px 1px;
                border-style: solid;
                color: white;
            }

            #OverviewFactList {
                background: @bg_color;
            }

            #OverviewFactBox {
                padding-left: 10px;
                padding-right: 10px;
            }

            /* EditDialog */
            #EditDialogMainBox {
                padding: 15px;
            }
            """


class SignalHandler(GObject.GObject):
    """
    A simple signaling class. Use this to provide custom signal registration.

    Once signals have been 'registered' here you can ``emit`` or ``connect`` to
    them via its class instances.
    """

    __gsignals__ = {
        str('facts-changed'): (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        str('daterange-changed'): (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    def __init__(self):
        """Initialize instance."""
        super(SignalHandler, self).__init__()


class HamsterGTK(Gtk.Application):
    """Main application class."""

    def __init__(self):
        """Setup instance and make sure default signals are connected to methods."""
        super(HamsterGTK, self).__init__()
        self.window = None

        self.connect('startup', self._startup)
        self.connect('activate', self._activate)
        self.connect('shutdown', self._shutdown)

    def _startup(self, app):
        """Triggered right at startup."""
        print(_('Hamster-GTK started.'))  # NOQA
        self.controler = hamster_lib.HamsterControl(helpers._get_config())
        self.controler.signal_handler = SignalHandler()
        # For convenience only
        self.store = self.controler.store

        # Reference to any existing overview dialog.
        self.overview = None

    def _activate(self, app):
        """Triggered in regular use after startup."""
        if not self.window:
            # We wamt to make sure that we leave the mainloop if anything goes
            # wrong setting up the actual window.
            try:
                self.window = MainWindow(app)
            except:
                traceback.print_exc()
                self.quit()

        app.add_window(self.window)
        self.window.show_all()
        self.window.present()

    def _shutdown(self, app):
        """Triggered upon termination."""
        print('Hamster-GTK shut down.')  # NOQA


def _main():
    """Main function, callable by ``setup.py`` entry point."""
    app = HamsterGTK()
    app.run()
