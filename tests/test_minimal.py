# -*- coding: utf-8 -*-
import gi
gi.require_version('Gdk', '3.0')  # NOQA
from gi.repository import Gtk

def test_smoke(request):
    Gtk.Box()
    pass
