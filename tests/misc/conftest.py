# -*- coding: utf-8 -*-

"""Fixtures for unittesting the misc submodule."""

import datetime

import fauxfactory
import pytest

from hamster_gtk import overview
from hamster_gtk.misc import dialogs


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
