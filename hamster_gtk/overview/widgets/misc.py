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

"""This module provide widgets that did not fit in the other modules."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from gi.repository import Gtk
from six import text_type

from hamster_gtk.misc.dialogs import DateRangeSelectDialog


class HeaderBar(Gtk.HeaderBar):
    """Headerbar used by the overview screen."""

    def __init__(self, controler, *args, **kwargs):
        """Initialize headerbar."""
        super(HeaderBar, self).__init__(*args, **kwargs)
        self.set_show_close_button(True)
        self.set_title(_("Overview"))
        self._daterange_button = self._get_daterange_button()
        self.pack_start(self._get_prev_daterange_button())
        self.pack_start(self._get_next_daterange_button())
        self.pack_start(self._daterange_button)
        self.pack_end(self._get_export_button())

        controler.signal_handler.connect('daterange-changed', self._on_daterange_changed)

    # Widgets
    def _get_export_button(self):
        """Return a button to export facts."""
        button = Gtk.Button(_("Export"))
        button.connect('clicked', self._on_export_button_clicked)
        return button

    def _get_daterange_button(self):
        """Return a button that opens the *select daterange* dialog."""
        # We add a dummy label which will be set properly once a daterange is
        # set.
        button = Gtk.Button('')
        button.connect('clicked', self._on_daterange_button_clicked)
        return button

    def _get_prev_daterange_button(self):
        """Return a 'previous dateframe' widget."""
        button = Gtk.Button(_("Earlier"))
        button.connect('clicked', self._on_previous_daterange_button_clicked)
        return button

    def _get_next_daterange_button(self):
        """Return a 'next dateframe' widget."""
        button = Gtk.Button(_("Later"))
        button.connect('clicked', self._on_next_daterange_button_clicked)
        return button

    # Callbacks
    def _on_daterange_button_clicked(self, button):
        """Callback for when the 'daterange' button is clicked."""
        parent = self.get_parent()
        dialog = DateRangeSelectDialog(parent)
        response = dialog.run()
        if response == Gtk.ResponseType.APPLY:
            parent._daterange = dialog.daterange
        dialog.destroy()

    def _on_daterange_changed(self, sender, daterange):
        """Callback to be triggered if the 'daterange' changed."""
        def get_label_text(daterange):
            start, end = daterange
            if start == end:
                text = text_type(start)
            else:
                text = '{} - {}'.format(start, end)
            return text
        self._daterange_button.set_label(get_label_text(daterange))

    def _on_previous_daterange_button_clicked(self, button):
        """Callback for when the 'previous' button is clicked."""
        self.get_parent().apply_previous_daterange()

    def _on_next_daterange_button_clicked(self, button):
        """Callback for when the 'next' button is clicked."""
        self.get_parent().apply_next_daterange()

    def _on_export_button_clicked(self, button):
        """
        Trigger fact export if button clicked.

        This is the place to run extra logic about where to save/which format.
        ``parent._export_facts`` only deals with the actual export.
        """
        parent = self.get_parent()
        dialog = Gtk.FileChooserDialog(_("Please Choose where to export to"), parent,
            Gtk.FileChooserAction.SAVE, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_current_name('{}.csv'.format(_("hamster_export")))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            target_path = dialog.get_filename()
            parent._export_facts(target_path)
        else:
            pass
        dialog.destroy()


class Summary(Gtk.Box):
    """A widget that shows categories with highest commutative ``Fact.delta``."""

    def __init__(self, category_totals):
        """Initialize widget."""
        super(Summary, self).__init__()

        for category, total in category_totals:
            label = Gtk.Label()
            label.set_markup("<b>{}:</b> {} minutes".format(category,
                                                            int(total.total_seconds() / 60)))
            self.pack_start(label, False, False, 10)
