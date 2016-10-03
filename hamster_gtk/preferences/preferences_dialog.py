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


"""This module provides the preferences dialog."""


from __future__ import absolute_import, unicode_literals

import collections
from gettext import gettext as _

import hamster_lib
from gi.repository import GObject, Gtk

from hamster_gtk.preferences.widgets import (ComboFileChooser,
                                             HamsterComboBoxText,
                                             HamsterSpinButton,
                                             SimpleAdjustment, TimeEntry)


class PreferencesDialog(Gtk.Dialog):
    """A dialog that shows and allows editing of config settings."""

    def __init__(self, parent, app, initial, *args, **kwargs):
        """
        Instantiate dialog.

        Args:
            parent (Gtk.Window): Dialog parent.
            app (HamsterGTK): Main app instance. Needed in order to retrieve
                and manipulate config values.
        """
        super(PreferencesDialog, self).__init__(*args, **kwargs)

        self._parent = parent
        self._app = app

        self.set_transient_for(self._parent)

        db_engines = [('sqlite', _('SQLite')), ('postgresql', _('PostgreSQL')),
            ('mysql', _('MySQL')), ('oracle', _('Oracle')), ('mssql', _('MSSQL'))]
        stores = [(store, hamster_lib.REGISTERED_BACKENDS[store].verbose_name)
            for store in hamster_lib.REGISTERED_BACKENDS]

        # We use an ordered dict as the order reflects display order as well.
        self._fields = collections.OrderedDict([
            ('day_start', (_('_Day Start (HH:MM:SS)'), TimeEntry())),
            ('fact_min_delta', (_('_Minimal Fact Duration'),
                HamsterSpinButton(SimpleAdjustment(0, GObject.G_MAXDOUBLE, 1)))),
            ('store', (_('_Store'), HamsterComboBoxText(stores))),
            ('db_engine', (_('DB _Engine'), HamsterComboBoxText(db_engines))),
            ('db_path', (_('DB _Path'), ComboFileChooser())),
            ('tmpfile_path', (_('_Temporary file'), ComboFileChooser())),
        ])

        grid = Gtk.Grid()
        grid.set_hexpand(True)
        row = 0
        for key, (label, widget) in self._fields.items():
            label_widget = Gtk.Label(label)
            label_widget.set_use_underline(True)
            label_widget.set_mnemonic_widget(widget)
            grid.attach(label_widget, 0, row, 1, 1)
            grid.attach(widget, 1, row, 1, 1)
            row += 1

        self._set_config(initial)

        self.get_content_area().add(grid)
        self.add_button(_('_Cancel'), Gtk.ResponseType.CANCEL)
        self.add_button(_('_Apply'), Gtk.ResponseType.APPLY)

        self.show_all()

    def get_config(self):
        """
        Parse config widgets and construct a {field: value} dict.

        Returns:
            dict: Dictionary of config keys/values.
        """
        result = {}
        for key, (_label, widget) in self._fields.items():
            result[key] = widget.get_config_value()

        return result

    def _set_config(self, values):
        """
        Go through widgets and set their values.

        Args:
            values (dict): Dictionary of config keys/values
        """
        for key, (_label, widget) in self._fields.items():
            widget.set_config_value(values[key])
