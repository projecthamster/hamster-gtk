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


"""General purpose helper methods."""

import datetime

import six
import os.path


def _u(string):
    """
    Return passed string as a text instance.

    This helper is particularly useful to wrap Gtk 'string return values' as
    they depend on the used python version. On python 2 Gtk will return utf-8
    encoded bytestrings while on python 3 it will return 'unicode strings'.

    The reason we have to use this and not ``six.u`` is that six does not make
    assumptions about the encoding and hence can not be used to safely decode
    non ascii bytestrings into unicode.

    Args:
        string (str): A string instance. On ``py2`` this will be a bytestring,
            on ``py3`` a 'unicode string'.

    Returns:
        text_type: Returns a 'unicode text type'. Under ``py2`` that means a
        ``unicode`` instance, under ``py3`` this will be a ``str`` instance.
    """
    if six.PY2:
        return string.decode('utf-8')
    else:
        return string


def show_error(parent, error, message=None):
    """
    Display an error dialog.

    Besides the clients own error reporting this is suitable to present backend
    errors to the user instead of failing silently.

    This functions runs the dialog a modal and takes care of its destruction afterwards.

    Args:
        parent (Gtk.Window): Parrent window.
        error (str): Exception message.
        message (str, optional): User friendly error message providing some broad context.

    Returns:
        None
    """
    # We can not import this on a global level due to circular imports.
    from .misc import ErrorDialog

    if not message:
        message = error
    dialog = ErrorDialog(parent, message)
    dialog.run()
    dialog.destroy()


def clear_children(widget):
    """
    Remove and destroy all children from a widget.

    It seems GTK really does not have this build in. Iterating over all
    seems a bit blunt, but seems to be the way to do this.
    """
    for child in widget.get_children():
        child.destroy()
    return widget


def get_parent_window(widget):
    """
    Reliably determine parent window of a widget.

    Just using :meth:`Gtk.Widget.get_toplevel` would return the widget itself
    if it had no parent window.

    On the other hand using :meth:`Gtk.Widget.get_ancestor` would return only
    the closest :class:`Gtk.Window` in the hierarchy.

    https://developer.gnome.org/gtk3/unstable/GtkWidget.html#gtk-widget-get-toplevel
    """
    toplevel = widget.get_toplevel()
    if not toplevel.is_toplevel():
        toplevel = None

    return toplevel


def calendar_date_to_datetime(date):
    """Convert :meth:`Gtk.Calendar.get_date` value to :class:`datetime.date`."""
    year, month, day = date
    return datetime.date(int(year), int(month) + 1, int(day))


# [FIXME]
# Remove once hamster-lib is patched
# This should probablyy be named/limited to: 'read_config_file'.
# The 'fallback' behaviour should live with ``_get_config_from_file``.
def get_config_instance(fallback_config_instance, app_name, file_name):
    """Patched version of ``hamster-lib`` helper function until it get fixed upstream."""
    from hamster_lib.helpers import config_helpers
    from backports.configparser import SafeConfigParser
    config = SafeConfigParser()
    path = config_helpers.get_config_path(app_name, file_name)
    existing_config = config.read(path)
    if not existing_config:
        config = config_helpers.write_config_file(fallback_config_instance, app_name,
                                                  file_name=file_name)
    return config


def get_resource_path(file_name):
    """Return path to a resource file."""
    return os.path.join(os.path.dirname(__file__), 'resources', file_name)
