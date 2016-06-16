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

from . import dialogs


def _get_config():
    """
    Get config to be passed to controler.

    For now this is just a dummy/mock.
    """
    return {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 1,
        'tmpfile_path': '/tmp/tmpfile.pickle',
        'db_engine': 'sqlite',
        'db_path': '/tmp/hamster.sqlite',
    }


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
    if not message:
        message = error
    dialog = dialogs.ErrorDialog(parent, message)
    dialog.run()
    dialog.destroy()
