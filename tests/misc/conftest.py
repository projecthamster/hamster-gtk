# -*- coding: utf-8 -*-

"""Fixtures for unittesting the misc submodule."""

from __future__ import absolute_import, unicode_literals
import datetime

import fauxfactory
import pytest
from gi.repository import GObject, Gtk
from six import text_type

from hamster_gtk import overview
from hamster_gtk.misc import dialogs, widgets
from hamster_gtk import helpers


@pytest.fixture
def daterange_select_dialog(request, main_window, app):
    """Return a functional DateRangeSelectDialog instance."""
    overview_dialog = overview.OverviewDialog(main_window, app)
    return dialogs.DateRangeSelectDialog(overview_dialog)


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


@pytest.fixture
def edit_fact_dialog(request, fact, dummy_window):
    """Return a edit fact dialog for a generic fact."""
    return dialogs.EditFactDialog(dummy_window, fact)


@pytest.fixture
def raw_fact_entry(request, app):
    """Return a ``RawFactEntry`` instance."""
    return widgets.RawFactEntry(app.controller)


@pytest.fixture
def raw_fact_completion(request, app):
    """Return a RawFactCompletion`` instance."""
    return widgets.raw_fact_entry.RawFactCompletion(app.controller)


@pytest.fixture
def activity_model_static(request):
    """
    Return a ``ListStore`` instance with the 'foo@bar' activity as it's only row.

    While this fixture is not too generic and has its activity hard coded it allows
    for more specific testing as we can know for sure which (sub) string apear and
    which do not.
    """
    model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING)
    model.append(['foo@bar', 'foo', 'bar'])
    return model


@pytest.fixture
def activity_model(request, activity):
    """Return a ``ListStore`` instance with a generic ``Activity`` as its only row."""
    model = Gtk.ListStore(GObject.TYPE_STRING, GObject.TYPE_STRING, GObject.TYPE_STRING)
    model.append([
        helpers.serialise_activity(activity),
        text_type(activity.name),
        text_type(activity.category.name)
    ])
    return model
