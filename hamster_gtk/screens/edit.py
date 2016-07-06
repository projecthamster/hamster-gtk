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


"""Module that provides the edit screen class."""

from gi.repository import Gtk
from six import text_type

from hamster_lib import Fact
from hamster_gtk.helpers import show_error


class EditFactDialog(Gtk.Dialog):
    """
    Dialog that allows editing of a fact instance.

    The user can edit the fact in question by entering a new ``raw fact``
    string and/or specifying particular attribute values in dedicated widgets.
    In cases where a ``raw fact`` provided contains information in conflict
    with values of those dedicated widgets the latter are authorative.
    """

    def __init__(self, parent, fact, app):
        """
        Initialize dialog.

        Args:
            parent (Gtk.Window): Parent window.
            app (Gtk.Application): Our main application  instance.
            fact (hamster_lib.Fact): Fact instance to be edited.
        """
        super(EditFactDialog, self).__init__()
        self._fact = fact
        self._parent = parent
        self._app = app

        self.set_transient_for(self._parent)
        self.set_default_size(600, 200)
        self._mainbox = Gtk.Grid()
        self._mainbox.set_hexpand(True)
        self._mainbox.set_vexpand(True)
        self._mainbox.set_name('EditDialogMainBox')
        self._mainbox.set_row_spacing(20)
        # ``self.content_area`` is a ``Gtk.Box``. We strive for an
        # ``Gtk.Grid`` only based layout. So we have to add this extra step.
        self.get_content_area().add(self._mainbox)
        self._mainbox.attach(self._get_old_fact_widget(), 0, 0, 1, 1)
        self._raw_fact_widget = self._get_raw_fact_widget()
        self._description_widget = self._get_description_widget()
        self._mainbox.attach(self._raw_fact_widget, 0, 1, 1, 1)
        self._mainbox.attach(self._description_widget, 0, 2, 1, 1)

        self._add_buttons()
        self.show_all()

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
        label = '{start}-{end} {activity}@{category}'.format(
            start=self._fact.start.strftime('%H:%M'),
            end=self._fact.end.strftime("%H:%M"),
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

    def _get_raw_fact_value(self):
        return self._raw_fact_widget.get_text().decode('utf-8')

    def _get_description_value(self):
        """Get unicode value from widget."""
        text_view = self._description_widget.get_child()
        text_buffer = text_view.get_buffer()
        start, end = text_buffer.get_bounds()
        return text_buffer.get_text(start, end, True).decode('utf-8')

    def _add_buttons(self):
        """
        Add button widgets to the action area.

        We do not use ``self.add_buttons`` because this only allows to pass on
        strings not actual button instances. We want to pass button instances
        however so we can customize them if we want to.
        """
        # [FIXME] According to http://lazka.github.io/pgi-docs/Gtk-3.0/constants.html#Gtk.STOCK_OK
        # Stock buttons are deprecated since 3.10. The new solution however
        # is unclear.
        delete = Gtk.Button.new_from_stock(Gtk.STOCK_DELETE)
        apply = Gtk.Button.new_from_stock(Gtk.STOCK_APPLY)
        cancel = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        self.add_action_widget(delete, Gtk.ResponseType.REJECT)
        self.add_action_widget(apply, Gtk.ResponseType.APPLY)
        self.add_action_widget(cancel, Gtk.ResponseType.CANCEL)

    def apply(self):
        """Close dialog, updating the fact with values specified."""
        # Create a new fact instance from the provided raw string.
        fact = Fact.create_from_raw_fact(self._get_raw_fact_value())
        # Instead of transfering all attributes of the parsed fact to the
        # existing ``self._fact`` we just go the other way round and attach the
        # old facts PK to the newly created instance.
        fact.pk = self._fact.pk
        # Explicit description trumps anything that may have been included in
        # the `raw_fact``.
        fact.description = self._get_description_value()
        try:
            self._app.controler.store.facts.save(fact)
        except (ValueError, KeyError) as message:
            show_error(self, message)
        self._app.controler.signal_handler.emit('facts_changed')

    def delete(self):
        """Delete this fact from the backend. No further confirmation is required."""
        result = self._app.store.facts.remove(self._fact)
        self._app.controler.signal_handler.emit('facts_changed')
        return result
