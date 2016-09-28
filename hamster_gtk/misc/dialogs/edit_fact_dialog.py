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


"""This module contains Dialog for editing facts."""

from __future__ import absolute_import, unicode_literals

from gettext import gettext as _

from gi.repository import Gtk
from hamster_lib import Fact
from six import text_type

from hamster_gtk.helpers import _u


class EditFactDialog(Gtk.Dialog):
    """
    Dialog that allows editing of a fact instance.

    The user can edit the fact in question by entering a new ``raw fact``
    string and/or specifying particular attribute values in dedicated widgets.
    In cases where a ``raw fact`` provided contains information in conflict
    with values of those dedicated widgets the latter are authorative.
    """

    def __init__(self, parent, fact):
        """
        Initialize dialog.

        Args:
            parent (Gtk.Window): Parent window.
            fact (hamster_lib.Fact): Fact instance to be edited.
        """
        super(EditFactDialog, self).__init__()
        self._fact = fact

        self.set_transient_for(parent)
        self.set_default_size(600, 200)
        # ``self.content_area`` is a ``Gtk.Box``. We strive for an
        # ``Gtk.Grid`` only based layout. So we have to add this extra step.
        self._mainbox = self._get_main_box()
        self.get_content_area().add(self._mainbox)

        # We do not use ``self.add_buttons`` because this only allows to pass
        #  on strings not actual button instances. We want to pass button
        # instances however so we can customize them if we want to.
        self.add_action_widget(self._get_delete_button(), Gtk.ResponseType.REJECT)
        self.add_action_widget(self._get_apply_button(), Gtk.ResponseType.APPLY)
        self.add_action_widget(self._get_cancel_button(), Gtk.ResponseType.CANCEL)
        self.show_all()

    @property
    def updated_fact(self):
        """Fact instance using values at the time of accessing it."""
        def get_raw_fact_value():
            """Get text from raw fact entry field."""
            return _u(self._raw_fact_widget.get_text())

        def get_description_value():
            """Get unicode value from widget."""
            text_view = self._description_widget.get_child()
            text_buffer = text_view.get_buffer()
            start, end = text_buffer.get_bounds()
            return _u(text_buffer.get_text(start, end, True))

        # Create a new fact instance from the provided raw string.
        fact = Fact.create_from_raw_fact(get_raw_fact_value())
        # Instead of transferring all attributes of the parsed fact to the
        # existing ``self._fact`` we just go the other way round and attach the
        # old facts PK to the newly created instance.
        fact.pk = self._fact.pk
        # Explicit description trumps anything that may have been included in
        # the `raw_fact``.
        fact.description = get_description_value()
        return fact

    # Widgets
    def _get_main_box(self):
        """Return the main layout container storing the content area."""
        grid = Gtk.Grid()
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        grid.set_name('EditDialogMainBox')
        grid.set_row_spacing(20)

        self._raw_fact_widget = self._get_raw_fact_widget()
        self._description_widget = self._get_description_widget()
        grid.attach(self._get_old_fact_widget(), 0, 0, 1, 1)
        grid.attach(self._raw_fact_widget, 0, 1, 1, 1)
        grid.attach(self._description_widget, 0, 2, 1, 1)
        return grid

    def _get_old_fact_widget(self):
        """Return a widget representing the fact to be edited."""
        label = Gtk.Label(text_type(self._fact))
        label.set_hexpand(True)
        label.set_name('EditDialogOldFactLabel')
        return label

    def _get_raw_fact_widget(self):
        """Return a widget that accepts user input to provide new ``raw fact`` string."""
        entry = Gtk.Entry()
        # [FIXME]
        # Maybe it would be sensible to have a serialization helper method as
        # part of ``hamster-lib``?!
        start_string = self._fact.start.strftime('%Y-%m-%d %H:%M')
        end_string = self._fact.end.strftime("%Y-%m-%d %H:%M")
        if self._fact.category is None:
            label = '{start} - {end} {activity}'.format(
                start=start_string,
                end=end_string,
                activity=text_type(self._fact.activity.name)
            )
        else:
            label = '{start} - {end} {activity}@{category}'.format(
                start=start_string,
                end=end_string,
                activity=text_type(self._fact.activity.name),
                category=text_type(self._fact.category.name)
            )

        entry.set_text(label)
        entry.set_name('EditDialogRawFactEntry')
        return entry

    def _get_description_widget(self):
        """Return a widget that displays and allows editing of ``fact.description``."""
        if self._fact.description:
            description = self._fact.description
        else:
            description = ''
        window = Gtk.ScrolledWindow()
        text_buffer = Gtk.TextBuffer()
        text_buffer.set_text(description)
        view = Gtk.TextView.new_with_buffer(text_buffer)
        view.set_hexpand(True)
        window.add(view)
        view.set_name('EditDialogDescriptionWindow')
        return window

    def _get_delete_button(self):
        """Return a *delete* button."""
        return Gtk.Button(_('_Delete'), use_underline=True)

    def _get_apply_button(self):
        """Return a *apply* button."""
        return Gtk.Button(_('_Apply'), use_underline=True)

    def _get_cancel_button(self):
        """Return a *cancel* button."""
        return Gtk.Button(_('_Cancel'), use_underline=True)
