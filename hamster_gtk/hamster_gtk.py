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

import collections
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
from six import text_type

# [FIXME]
# Remove once hamster-lib has been patched
from hamster_gtk.helpers import _u, get_config_instance
from hamster_gtk.overview import OverviewDialog
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

    def _on_overview_button(self, button):
        """Callback for overview button."""
        parent = self.get_parent()
        OverviewDialog(parent, parent.app)

    def _on_preferences_button(self, button):
        """Bring up, process and shut down preferences dialog."""
        def get_initial():
            """Return current values as a dict."""
            return self._app._config
        parent = self.get_parent()
        dialog = PreferencesDialog(parent, parent.app, get_initial())
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            config = dialog.get_config()
            self._app.save_config(config)
        else:
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
        style_provider.load_from_data(self._get_css().encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Set tracking as default screen at startup.
        self.add(TrackingScreen(self.app))

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
        self.config = self._reload_config()

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
        self._reload_config()
        # [FIXME]
        # hamster-lib currentl provides no proper way to update its config
        # See: https://github.com/projecthamster/hamster-lib/issues/190
        # We want something like ``self.controler.update_config(self._config)``

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


class PreferencesDialog(Gtk.Dialog):
    """A dialog that shows and allows editing of config settings."""

    def __init__(self, parent, app, initial, *args, **kwargs):
        """
        Instantiate dialog.

        Args:
            parent (Gtk.Window): Diaog parent.
            app (HamsterGTK): Main app instance. Needed in order to retrieve
                and manipulate config values.
        """
        super(PreferencesDialog, self).__init__(*args, **kwargs)

        self._parent = parent
        self._app = app

        self.set_transient_for(self._parent)

        # We use an ordered dict as the order reflects display order as well.
        self._fields = collections.OrderedDict([
            ('store', self._get_store_widget(initial=initial['store'])),
            ('day_start', self._get_day_start_widget(initial=initial['day_start'])),
            ('fact_min_delta', self._get_fact_min_delta_widget(initial=initial['fact_min_delta'])),
            ('tmpfile_path', self._get_tmpfile_path_widget(initial=initial['tmpfile_path'])),
            ('db_engine', self._get_db_engine_widget(initial=initial['db_engine'])),
            ('db_path', self._get_db_path_widget(initial=initial['db_path'])),
        ])

        grid = Gtk.Grid()
        grid.set_hexpand(True)
        row = 0
        for key, widgets in self._fields.items():
            label, widget = widgets
            grid.attach(label, 0, row, 1, 1)
            grid.attach(widget, 1, row, 1, 1)
            row += 1

        self.get_content_area().add(grid)
        self.add_action_widget(self._get_cancel_button(), Gtk.ResponseType.CANCEL)
        self.add_action_widget(self._get_apply_button(), Gtk.ResponseType.APPLY)

        self.show_all()

    def get_config(self):
        """Parse config widgets and construct a {field: value} dict."""
        def get_string(widget):
            if isinstance(widget, Gtk.Entry):
                result = _u(widget.get_text())
            elif isinstance(widget, Gtk.ComboBoxText):
                index = widget.get_active()
                result = widget.options[index]
            elif isinstance(widget, Gtk.Grid):
                result = _u(widget.entry.get_text())
            else:
                raise TypeError(_("Unhandled widget class!"))
            return result

        def get_time(widget):
            if isinstance(widget, Gtk.Entry):
                result = _u(widget.get_text())
                # We are tollerant against malformed time information.
                try:
                    result = datetime.datetime.strptime(result, '%H:%M:%S').time()
                except ValueError:
                    result = datetime.datetime.strptime(result, '%H:%M').time()
            else:
                raise TypeError(_("Unhandled widget class!"))
            return result

        def get_int(widget):
            string = get_string(widget)
            result = None
            if string:
                result = int(string)
            return result

        string_fields = ('store', 'tmpfile_path', 'db_engine', 'db_path')
        time_fields = ('day_start',)
        int_fields = ('fact_min_delta',)

        result = {}
        for key in string_fields:
            label, widget = self._fields[key]
            result[key] = get_string(widget)

        for key in time_fields:
            label, widget = self._fields[key]
            result[key] = get_time(widget)

        for key in int_fields:
            label, widget = self._fields[key]
            result[key] = get_int(widget)
        return result

    # Widgets
    def _get_apply_button(self):
        """Return a *apply* button."""
        return Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)

    def _get_cancel_button(self):
        """Return a *cancel* button."""
        return Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)

    def _get_store_widget(self, initial=None):
        """Return widget to set the backend store."""
        label = Gtk.Label(_("Store"))
        widget = Gtk.ComboBoxText()
        # It seems Gtk.ComboBox provides no easy access to its stored options
        # that would allow getting their index. The index however is needed in
        # order to programmatically set an option. Until we find a better
        # solution we need to keep our own 'string-to-index' mapping.
        # We create a immutable duplicate of the original store list in order
        # to prevent accidental side effects and changes to the list effecting
        # the combobox index.
        widget.options = tuple(hamster_lib.REGISTERED_BACKENDS.keys())
        for store in hamster_lib.REGISTERED_BACKENDS.values():
            widget.append_text(store.verbose_name)
        if initial:
            widget.set_active(widget.options.index(initial))
        return (label, widget)

    def _get_day_start_widget(self, initial=None):
        """Return widget to set the *day start* value."""
        label_text = "{} (HH:MM:SS)".format(_("Day Start"))
        label = Gtk.Label(label_text)
        widget = Gtk.Entry()
        # We need to be explicit about 'None'. A bool(datetime.time(0, 0, 0))
        # evaluates to False and as a consequence would not trigger the setting
        # of the initial value.
        if initial is not None:
            widget.set_text(text_type(initial.strftime('%H:%M:%S')))
        return (label, widget)

    def _get_fact_min_delta_widget(self, initial=None):
        """Return widget to set the minimum duration for a fact."""
        label = Gtk.Label(_("Minimal Fact Duration"))
        widget = Gtk.Entry()
        # We need to check for None in order to allow 0 as initial value.
        if initial is not None:
            widget.set_text(text_type(int(initial)))
        return (label, widget)

    def _get_tmpfile_path_widget(self, initial=None):
        """Return widget to set the location to save the tmp fact."""
        label = Gtk.Label(_("Full 'tmpfile'-path"))
        grid = self._get_path_entry_with_button(initial,
            self._on_tmpfile_path_choose_button_clicked)
        return (label, grid)

    def _get_db_engine_widget(self, initial=None):
        """Return widget to specify the *db-engine* value."""
        label = Gtk.Label(_("DB Engine"))
        widget = Gtk.ComboBoxText()
        widget.options = ('sqlite', 'postgresql', 'mysql', 'oracle', 'mssql')
        for engine in widget.options:
            widget.append_text(engine)
        if initial:
            widget.set_active(widget.options.index(initial))
        return (label, widget)

    def _get_db_path_widget(self, initial=None):
        """Return a widget to specify the *db-path*."""
        label = Gtk.Label(_("DB Path"))
        grid = self._get_path_entry_with_button(initial,
            self._on_db_path_choose_button_clicked)
        return (label, grid)

    # Callbacks
    def _on_tmpfile_path_choose_button_clicked(self, button):
        """Open a dialog to select path."""
        self._update_entry_via_filechooser('tmpfile_path')

    def _on_db_path_choose_button_clicked(self, button):
        """Open a dialog to select path."""
        self._update_entry_via_filechooser('db_path')

    # Helpers
    def _update_entry_via_filechooser(self, fieldname):
        """Open a dialog to select path and update entry widget with it."""
        def update_entry(new_path):
            entry = self._fields[fieldname][1].entry
            entry.set_text(text_type(new_path))
        dialog = Gtk.FileChooserDialog(_("Please choose a directory"), self,
            Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            update_entry(dialog.get_filename())
        else:
            pass
        dialog.destroy()

    def _get_path_entry_with_button(self, initial, callback):
        """Return a path entry field with accompanying button."""
        entry = Gtk.Entry()
        entry.set_hexpand(True)
        button = Gtk.Button(_("Choose"))
        button.connect('clicked', callback)
        grid = Gtk.Grid()
        grid.entry = entry
        grid.attach(entry, 0, 0, 1, 1)
        grid.attach(button, 1, 0, 1, 1)
        if initial:
            entry.set_text(text_type(initial))
        return grid


def _main():
    """Main function, callable by ``setup.py`` entry point."""
    app = HamsterGTK()
    app.run()
