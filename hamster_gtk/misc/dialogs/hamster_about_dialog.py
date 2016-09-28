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


"""This module contains Dialog displaying information about the application."""


from __future__ import absolute_import, unicode_literals

import sys
from gettext import gettext as _

import hamster_lib
from gi.repository import Gtk

import hamster_gtk


class HamsterAboutDialog(Gtk.AboutDialog):
    """Basic 'About'-dialog class using Gtk default dialog."""

    # Whilst we are not perfectly happy with the layout and general
    # structure of the dialog it is little effort and works for now.
    # Alternatively we could either try to customize is to match our
    # expectations or construct our own from scratch.

    def __init__(self, parent, *args, **kwargs):
        """Initialize the dialog."""
        super(HamsterAboutDialog, self).__init__(*args, **kwargs)
        authors = ['Eric Goller <eric.goller@ninjaduck.solutions>']
        python_version_string = '{}.{}.{}'.format(
            sys.version_info.major, sys.version_info.minor, sys.version_info.micro
        )
        comments = _(
            "Thank you for using 'Hamster-GTK.'"
            " Your current runtime uses 'hamster-lib' {lib_version} and is interpretet by"
            " Python {python_version}.").format(lib_version=hamster_lib.__version__,
                                                python_version=python_version_string)

        meta = {
            'program-name': "Hamster-GTK",
            'version': hamster_gtk.__version__,
            'copyright': "Copyright © 2015–2016 Eric Goller / ninjaduck.solutions",
            'website': "http://projecthamster.org",
            'website-label': _("Visit Project Hamster Website"),
            'title': _("About Hamster-GTK"),
            'license-type': Gtk.License.GPL_3_0,
            'authors': authors,
            'comments': comments,
        }

        for key, value in meta.items():
            self.set_property(key, value)

        self.set_transient_for(parent)
