# -*- coding: utf-8 -*-
import gi
from gi.repository import Gtk

gi.require_version('Gdk', '3.0')  # NOQA


def test_minimal(request):
    """Minimal test to showcase strange segfault behaviour when run with tox."""
    box = Gtk.Box()
    assert box
