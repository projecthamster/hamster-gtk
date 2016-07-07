# -*- coding: utf-8 -*-

"""Unittest fixtures."""

import datetime

import fauxfactory
import pytest
from gi.repository import Gtk

import hamster_gtk.hamster_gtk as hamster_gtk
import hamster_gtk.screens.overview as overview


# Instances
@pytest.fixture
def app(request):
    """
    Return an ``Application`` fixture.

    Please note: the app has just been started but not activated.
    """
    app = hamster_gtk.HamsterGTK()
    app._startup(app)
    return app


@pytest.fixture
def app_window(request, app):
    """Return a ``ApplicationWindow`` fixture."""
    return hamster_gtk.MainWindow(app)


@pytest.fixture
def dummy_window(self):
    """
    Return a generic :class:`Gtk.Window` instance.

    This is useful for tests that do not actually rely on external
    functionality.
    """
    return Gtk.Window()


@pytest.fixture
def overview_screen(app_window, app):
    """Return a generic :class:`OverViewDialog` instance."""
    return overview.OverviewScreen(app_window, app)


@pytest.fixture
def daterange_select_dialog(overview_screen):
    """Return a functional DateRangeSelectDialog instance."""
    return overview.DateRangeSelectDialog(overview_screen)


# Data
@pytest.fixture(params=(
    fauxfactory.gen_string('utf8'),
    fauxfactory.gen_string('cjk'),
    fauxfactory.gen_string('latin1'),
    fauxfactory.gen_string('cyrillic'),
))
def word_parametrized(request):
    """Return a string paramized with various different charakter constelations."""
    return request.param


@pytest.fixture(params=(0, 7, 15, 30, 55))
def daterange_offset_parametrized(request):
    """Return various daterange offset variants as easy to use timedeltas."""
    return datetime.timedelta(days=request.param)


@pytest.fixture
def daterange(request):
    """Return a randomized daterange tuple."""
    offset = datetime.timedelta(days=7)
    start = fauxfactory.gen_date()
    return (start, start + offset)


@pytest.fixture
def daterange_parametrized(request, daterange_offset_parametrized):
    """Return daterange parametrized with various lengths."""
    start = fauxfactory.gen_date()
    return (start, start + daterange_offset_parametrized)


@pytest.fixture(params=(
    (datetime.date(2016, 7, 10), (datetime.date(2016, 7, 4), datetime.date(2016, 7, 10))),
    (datetime.date(2016, 7, 1), (datetime.date(2016, 6, 27), datetime.date(2016, 7, 3))),
    (datetime.date(2016, 7, 18), (datetime.date(2016, 7, 18), datetime.date(2016, 7, 24))),
))
def weekrange_parametrized(request):
    """Return parametrized ``date``/``weekrange`` pairs."""
    return request.param


@pytest.fixture(params=(
    (datetime.date(2016, 7, 10), (datetime.date(2016, 7, 1), datetime.date(2016, 7, 31))),
    (datetime.date(2016, 2, 2), (datetime.date(2016, 2, 1), datetime.date(2016, 2, 29))),
))
def monthrange_parametrized(request):
    """Return parametrized ``date``/``monthrange`` pairs."""
    return request.param
