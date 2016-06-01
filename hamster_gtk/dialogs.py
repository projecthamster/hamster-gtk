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


"""
This module contains auxillary dialog classes.

Dialogs simple enough not to warrent dedicated modules are gathered in this one.
"""

from gi.repository import Gtk


class ErrorDialog(Gtk.MessageDialog):
    """
    Error Dialog used to provide feedback to the user.

    Right now we basicly just pass exception messages to the user. Whilst this is usefull to
    provide meaningfull information at this early stage, we probably want to provide more user
    friendly messages later on.
    """

    def __init__(self, parent, message, *args, **kwargs):
        """Initialize dialog."""
        super(ErrorDialog, self).__init__(*args, buttons=Gtk.ButtonsType.CLOSE,
            message_type=Gtk.MessageType.ERROR, text=message, **kwargs)
        self.set_transient_for(parent)
