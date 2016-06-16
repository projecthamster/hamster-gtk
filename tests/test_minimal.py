# -*- coding: utf-8 -*-
import gi
gi.require_version('Gdk', '3.0')  # NOQA
from gi.repository import Gtk


def test_minimal(request):
    """Minimal test to showcase strange segfault behaviour when run with tox."""
    box = Gtk.Box()
    assert box
