# -*- coding: utf-8 -*-

import gi
gi.require_version('Gdk', '3.0')  # NOQA
from gi.repository import Gtk
import pytest

from hamster_gtk import hamster_gtk
from hamster_gtk.screens.tracking import TrackingScreen

@pytest.fixture
def app(request):
    """Return a app fixture."""
    app = hamster_gtk.HamsterGTK()
    app._startup(app)
    app._activate(app)
    return app


@pytest.fixture
def app_window(request, app):
    return hamster_gtk.MainWindow(application=app)
