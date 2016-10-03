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


from __future__ import absolute_import, unicode_literals

import datetime
import os.path
import traceback
from gettext import gettext as _

import gi
gi.require_version('Gdk', '3.0')  # NOQA
gi.require_version('Gtk', '3.0')  # NOQA
import hamster_lib
# Once we drop py2 support, we can use the builtin again but unicode support
# under python 2 is practically non existing and manual encoding is not easily
# possible.
from backports.configparser import SafeConfigParser
from gi.repository import Gdk, GObject, Gtk
from hamster_lib.helpers import config_helpers
from hamster_gtk.helpers import get_parent_window, get_resource_path
from six import text_type

# [FIXME]
# Remove once hamster-lib has been patched
from hamster_gtk.helpers import get_config_instance
from hamster_gtk.misc import HamsterAboutDialog as AboutDialog
from hamster_gtk.overview import OverviewDialog
from hamster_gtk.preferences import PreferencesDialog
from hamster_gtk.tracking import TrackingScreen


APP_NAME = 'Hamster-GTK'
DEFAULT_WINDOW_SIZE = (400, 200)


class HeaderBar(Gtk.HeaderBar):
    """Header bar for the main application window."""

    def __init__(self, app, *args, **kwargs):
        """Initialize header bar."""
        super(HeaderBar, self).__init__(*args, **kwargs)

        self._app = app

        self.set_title(_("Hamster-GTK"))
        self.set_subtitle(_("Your friendly time tracker."))
        self.set_show_close_button(True)

        self.pack_end(self._get_preferences_button())
        self.pack_end(self._get_overview_button())
        self.pack_end(self._get_about_button())

    def _get_overview_button(self):
        """Return a button to open the ``Overview`` dialog."""
        button = Gtk.Button(_("Overview"))
        button.connect('clicked', self._on_overview_button)
        return button

    def _get_preferences_button(self):
        """Return a button to bring up the preferences dialog."""
        button = Gtk.Button(_("Preferences"))
        button.connect('clicked', self._on_preferences_button)
        return button

    def _get_about_button(self):
        """Return a button to bring up the about dialog."""
        button = Gtk.Button(_("About"))
        button.connect('clicked', self._on_about_button)
        return button

    def _on_overview_button(self, button):
        """Callback for overview button."""
        parent = get_parent_window(self)
        OverviewDialog(parent, parent.app)

    def _on_preferences_button(self, button):
        """Bring up, process and shut down preferences dialog."""
        def get_initial():
            """Return current values as a dict."""
            return self._app._config
        parent = get_parent_window(self)
        dialog = PreferencesDialog(parent, parent.app, get_initial())
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            config = dialog.get_config()
            self._app.save_config(config)
        else:
            pass
        dialog.destroy()

    def _on_about_button(self, button):
        """Bring up, process and shut down about dialog."""
        parent = get_parent_window(self)
        dialog = AboutDialog(parent)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            pass
        dialog.destroy()


class MainWindow(Gtk.ApplicationWindow):
    """Main window class that is the center of our GUI."""

    def __init__(self, app, *args, **kwargs):
        """Initialize window."""
        super(MainWindow, self).__init__(*args, application=app, **kwargs)
        # Some basic inventory
        self.app = app
        self._overview_window = None

        # Styling
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_titlebar(HeaderBar(self.app))
        self.set_default_size(*DEFAULT_WINDOW_SIZE)

        # Setup css
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path(get_resource_path('css/hamster-gtk.css'))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Set tracking as default screen at startup.
        self.add(TrackingScreen(self.app))


# [FIXME]
# Its probably more sensible to just extend the app itself.
class SignalHandler(GObject.GObject):
    """
    A simple signaling class. Use this to provide custom signal registration.

    Once signals have been 'registered' here you can ``emit`` or ``connect`` to
    them via its class instances.
    """

    __gsignals__ = {
        str('facts-changed'): (GObject.SIGNAL_RUN_LAST, None, ()),
        str('daterange-changed'): (GObject.SIGNAL_RUN_LAST, None, (GObject.TYPE_PYOBJECT,)),
        str('config-changed'): (GObject.SIGNAL_RUN_LAST, None, ()),
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
        # Which config backend to use.
        self.config_store = 'file'
        # Yes this is redundent, but more transparent. And we can worry about
        # this unwarrented assignment once it actually matters.
        self._config = self._reload_config()

        self.connect('startup', self._startup)
        self.connect('activate', self._activate)
        self.connect('shutdown', self._shutdown)

    def save_config(self, config):
        """
        Save a potentially new/modified config instance to config backend.

        Args:
            config (dict): Dictionary of config keys and values.

        Returns:
            dict: Dictionary of config keys and values.
        """
        cp_instance = self._config_to_configparser(config)
        config_helpers.write_config_file(cp_instance, 'hamster-gtk', 'hamster-gtk.conf')
        self.controler.signal_handler.emit('config-changed')

    def _startup(self, app):
        """Triggered right at startup."""
        print(_('Hamster-GTK started.'))  # NOQA
        self._reload_config()
        self.controler = hamster_lib.HamsterControl(self._config)
        self.controler.signal_handler = SignalHandler()
        self.controler.signal_handler.connect('config-changed', self._config_changed)
        # For convenience only
        # [FIXME]
        # Pick one canonical path and stick to it!
        self.store = self.controler.store

        # Reference to any existing overview dialog.
        self.overview = None

    def _activate(self, app):
        """Triggered in regular use after startup."""
        if not self.window:
            # We want to make sure that we leave the mainloop if anything goes
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

    # We use sender=None for it to be called as a method as well.
    def _reload_config(self):
        """Reload configuration from designated store."""
        config = self._get_config_from_file()
        self._config = config
        return config

    def _config_changed(self, sender):
        """Callback triggered when config has been changed."""
        self.controler.update_config(self._reload_config())

    def _get_default_config(self):
        """
        Return a default config dictionary.

        Note: Those defaults are independend of the particular config store.
        """
        appdirs = config_helpers.HamsterAppDirs('hamster-gtk')
        return {
            # Backend
            'store': 'sqlalchemy',
            'day_start': datetime.time(5, 30, 0),
            'fact_min_delta': 1,
            'tmpfile_path': os.path.join(appdirs.user_data_dir, 'hamster-gtk.tmp'),
            'db_engine': 'sqlite',
            'db_path': os.path.join(appdirs.user_data_dir, 'hamster-gtk.sqlite'),
        }

    def _config_to_configparser(self, config):
        """
        Return a ConfigParser instance representing a given config dictionary.

        Args:
            config (dict): Dictionary of config key/value pairs.

        Returns:
            SafeConfigParser: SafeConfigParser instance representing config.
        """
        def get_store():
            return config['store']

        def get_day_start():
            return config['day_start'].strftime('%H:%M:%S')

        def get_fact_min_delta():
            return text_type(config['fact_min_delta'])

        def get_tmpfile_path():
            return text_type(config['tmpfile_path'])

        def get_db_engine():
            return config['db_engine']

        def get_db_path():
            return text_type(config['db_path'])

        cp_instance = SafeConfigParser()
        cp_instance.add_section('Backend')
        cp_instance.set('Backend', 'store', get_store())
        cp_instance.set('Backend', 'day_start', get_day_start())
        cp_instance.set('Backend', 'fact_min_delta', get_fact_min_delta())
        cp_instance.set('Backend', 'tmpfile_path', get_tmpfile_path())
        cp_instance.set('Backend', 'db_engine', get_db_engine())
        cp_instance.set('Backend', 'db_path', get_db_path())

        return cp_instance

    def _configparser_to_config(self, cp_instance):
        """Return a config dict generate from a configparser nstance."""
        def get_store():
            store = cp_instance.get('Backend', 'store')
            if store not in hamster_lib.REGISTERED_BACKENDS.keys():
                raise ValueError(_("Unrecognized store option."))
            return store

        def get_day_start():
            try:
                day_start = datetime.datetime.strptime(cp_instance.get('Backend',
                    'day_start'), '%H:%M:%S').time()
            except ValueError:
                raise ValueError(_(
                    "We encountered an error when parsing configs 'day_start'"
                    " value! Aborting ..."
                ))
            return day_start

        def get_fact_min_delta():
            return int(cp_instance.get('Backend', 'fact_min_delta'))

        def get_tmpfile_path():
            return cp_instance.get('Backend', 'tmpfile_path')

        def get_db_config():
            """Provide a dict with db-specifiy key/value to be added to the backend config."""
            result = {}
            engine = cp_instance.get('Backend', 'db_engine')
            result = {'db_engine': engine}
            if engine == 'sqlite':
                result.update({'db_path': cp_instance.get('Backend', 'db_path')})
            else:
                try:
                    result.update({'db_port': cp_instance.get('Backend', 'db_port')})
                except KeyError:
                    # Thats alright, the backend will use the default port.
                    pass

                result.update({
                    'db_host': cp_instance.get('Backend', 'db_host'),
                    'db_name': cp_instance.get('Backend', 'db_name'),
                    'db_user': cp_instance.get('Backend', 'db_user'),
                    'db_password': cp_instance.get('Backend', 'db_password'),
                })
            return result

        result = {
            'store': get_store(),
            'day_start': get_day_start(),
            'fact_min_delta': get_fact_min_delta(),
            'tmpfile_path': get_tmpfile_path(),
        }
        result.update(get_db_config())
        return result

    def _write_config_to_file(self, configparser_instance):
        """
        Write a configparser instance to a config file.

        Args:
            cp_instance (SafeConfigParser): Instance to be written to file.
        """
        config_helpers.write_config_file(configparser_instance, 'hamster-gtk', 'hamster-gtk.conf')

    def _get_config_from_file(self):
        """
        Return a config dictionary from acp_instanceg file.

        If there is none create a default config file. This methods main job is
        to convert strings from the loaded ConfigParser File to appropiate
        instances suitable for our config dictionary. The actual data retrival
        is provided by a hamster-lib helper function.

        Returns:
            dict: Dictionary of config key/values.
        """
        def get_fallback():
            config = self._get_default_config()
            return self._config_to_configparser(config)

        cp_instance = get_config_instance(get_fallback(), 'hamster-gtk', 'hamster-gtk.conf')
        return self._configparser_to_config(cp_instance)


def _main():
    """Main function, callable by ``setup.py`` entry point."""
    app = HamsterGTK()
    app.run()
