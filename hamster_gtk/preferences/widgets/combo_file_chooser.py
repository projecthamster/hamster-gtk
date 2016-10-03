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

"""This module provides file chooser widget."""

# [FIXME]
# Adding 'unicode_literals' raises encoding issues. This is a major sign we
# have a unicode issue!
from __future__ import absolute_import

from gettext import gettext as _

from gi.repository import Gtk
from six import text_type

from hamster_gtk.helpers import get_parent_window

# [FIXME]
# Remove once hamster-lib has been patched
from hamster_gtk.helpers import _u

from .config_widget import ConfigWidget


class ComboFileChooser(Gtk.Grid, ConfigWidget):
    """A file chooser that also has an entry for changing the path."""

    # Required else you would need to specify the full module name in ui file
    __gtype_name__ = 'ComboFileChooser'

    def __init__(self):
        """Initialize widget."""
        super(Gtk.Grid, self).__init__()

        self._entry = Gtk.Entry()
        self._entry.set_hexpand(True)

        self._button = Gtk.Button(_("Choose"))
        self._button.connect('clicked', self._on_choose_clicked)

        self.attach(self._entry, 0, 0, 1, 1)
        self.attach(self._button, 1, 0, 1, 1)
        self.connect('mnemonic-activate', self._on_mnemonic_activate)

    def get_config_value(self):
        """
        Return the selected path.

        Returns:
            six.text_type: Selected file path.
        """
        return _u(self._entry.get_text())

    def set_config_value(self, path):
        """
        Select given file path.

        Args:
            path (six.text_type): Path to be selected
        """
        self._entry.set_text(text_type(path))

    def _on_choose_clicked(self, widget):
        """Open a dialog to select path and update entry widget with it."""
        toplevel = get_parent_window(self)

        dialog = Gtk.FileChooserDialog(_("Please choose a directory"), toplevel,
            Gtk.FileChooserAction.SAVE, (_("_Cancel"), Gtk.ResponseType.CANCEL,
                                         _("_Save"), Gtk.ResponseType.OK))
        dialog.set_filename(self.get_config_value())
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._entry.set_text(_u(dialog.get_filename()))

        dialog.destroy()

    def _on_mnemonic_activate(self, widget, group_cycling):
        """Mnemonic associated with this widget was activated."""
        return self._entry.do_mnemonic_activate(self._entry, group_cycling)
