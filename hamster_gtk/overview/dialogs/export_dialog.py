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


"""This Module provides the ``ExportDialog`` class to choose file to be exported."""

from __future__ import absolute_import

import os.path
from gettext import gettext as _

from gi.repository import Gtk

from hamster_gtk.preferences.widgets import PreferencesGrid


class ExportDialog(Gtk.FileChooserDialog):
    """Dialog used for exporting."""

    def __init__(self, parent):
        """
        Initialize export dialog.

        Args:
            parent (Gtk.Window): Parent window for the dialog.
        """
        super(ExportDialog, self).__init__(_("Please choose where to export to"), parent,
            Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        self._export_format_chooser = self._get_export_format_chooser()
        self._export_format_chooser.connect('changed', self._on_export_format_changed)

        export_options = PreferencesGrid(
            {'format': (_("Export _format:"), self._export_format_chooser)})
        export_options.show_all()
        self.set_extra_widget(export_options)

        self.set_current_name(_("hamster_export"))
        self._export_format_chooser.set_active_id('tsv')

    def _get_export_format_chooser(self):
        chooser = Gtk.ComboBoxText()
        chooser.append('tsv', _("TSV"))
        chooser.append('ical', _("iCal"))
        chooser.append('xml', _("XML"))
        return chooser

    def _on_export_format_changed(self, combobox):
        """
        Change file extension of the selected file to the one that was chosen.

        Args:
            combobox (Gtk.ComboBoxText): Combo box that was changed.
        """
        new_ext = self.get_export_format()
        (name, ext) = os.path.splitext(self.get_current_name())
        self.set_current_name('{}.{}'.format(name, new_ext))

    def get_export_format(self):
        """
        Return currently selected export format.

        Returns:
            text_type: Currently selected export format.
        """
        return self._export_format_chooser.get_active_id()
