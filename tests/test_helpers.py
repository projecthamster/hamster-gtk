# -*- coding: utf-8 -*-

from gi.repository import Gtk

import hamster_gtk.helpers as helpers


def test_get_parent_window_standalone(request):
    """Make sure the parent window of a windowless widget is None."""
    label = Gtk.Label('foo')
    assert helpers.get_parent_window(label) is None


def test_get_parent_window(request):
    """Make sure the parent window of a widget placed in the window is determined correctly."""
    window = Gtk.Window()
    label = Gtk.Label('foo')
    window.add(label)
    assert helpers.get_parent_window(label) == window
