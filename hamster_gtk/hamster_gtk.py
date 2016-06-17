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

from gettext import gettext as _

import gi
gi.require_version('Gdk', '3.0')  # NOQA
gi.require_version('Gtk', '3.0')  # NOQA
from gi.repository import Gdk, Gtk
import hamsterlib

from . import helpers
from .screens.overview import OverviewScreen
from .screens.tracking import TrackingScreen


APP_NAME = 'Hamster-GTK'
DEFAULT_WINDOW_SIZE = (400, 200)


class HeaderBar(Gtk.HeaderBar):
    """Header bar for the main application window."""

    def __init__(self, parent, **kwargs):
        """Initialize header bar."""
        super(HeaderBar, self).__init__(**kwargs)
        self._parent = parent
        self.set_title(_("Hamster-GTK"))
        self.set_subtitle(_("Your friendly time tracker."))
        self.set_show_close_button(True)

        overview_button = Gtk.Button('Overview')
        overview_button.connect('clicked', self._on_overview_button)
        self.pack_end(overview_button)

    def _on_overview_button(self, button):
        """Callback for overview button."""
        if not self._parent._overview_window:
            self._parent._overview_window = OverviewScreen(self._parent, self._parent._app)
        self._parent._overview_window.present()


class MainWindow(Gtk.ApplicationWindow):
    """Main window class that is the center of our GUI."""

    def __init__(self, app, *args, **kwargs):
        """Initialize window."""
        super(MainWindow, self).__init__(*args, application=app, **kwargs)
        self.set_titlebar(HeaderBar(self))

        # Setup css
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(self._get_css().encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Some basic inventory
        self._app = app
        self._overview_window = None

        # Some Geometry
        self.set_default_size(*DEFAULT_WINDOW_SIZE)

        # Set tracking as default screen at startup.
        self.add(TrackingScreen(self))

    # [FIXME] Obsolete?
    def _facts_changed(self):
        """
        Callback to indicate that facts have been changed in the backend.

        Workaround until we have evaluated the need for proper signals.
        """
        # self.app.overview.update()
        pass

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

            #OverviewFactsBox {
                padding-bottom: 20px;
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
            """


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
        self.controler = hamsterlib.HamsterControl(helpers._get_config())
        # For convenience only
        self.store = self.controler.store

        # Reference to any existing overview dialog.
        self.overview = None

    def _activate(self, app):
        """Triggered in regular use after startup."""
        if not self.window:
            self.window = MainWindow(app)
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
