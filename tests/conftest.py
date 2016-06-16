# -*- coding: utf-8 -*-

"""Unittest fixtures."""

import pytest

import hamster_gtk.hamster_gtk as hamster_gtk


@pytest.fixture
def app(request):
    """Return an ``Application`` fixture."""
    app = hamster_gtk.HamsterGTK()
    app._startup(app)
    app._activate(app)
    return app


@pytest.fixture
def app_window(request, app):
    """Return a ``ApplicationWindow`` fixture."""
    return hamster_gtk.MainWindow(app)
