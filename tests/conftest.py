# -*- coding: utf-8 -*-

"""Unittest fixtures."""

import datetime
import random

import fauxfactory
import pytest
from gi.repository import Gtk
from pytest_factoryboy import register

import factories
import hamster_gtk.hamster_gtk as hamster_gtk
import hamster_gtk.screens.overview as overview
from hamster_gtk.screens import edit, tracking

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


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
def main_window(request, app):
    """Return a ``ApplicationWindow`` fixture."""
    return hamster_gtk.MainWindow(app)


@pytest.fixture
def header_bar(request):
    """
    Return a HeaderBar instance.

    Note:
        This instance has not been added to any parent window yet!
    """
    return hamster_gtk.HeaderBar()


@pytest.fixture
def dummy_window(request):
    """
    Return a generic :class:`Gtk.Window` instance.

    This is useful for tests that do not actually rely on external
    functionality.
    """
    return Gtk.Window()


@pytest.fixture
def overview_screen(main_window, app):
    """Return a generic :class:`OverViewDialog` instance."""
    return overview.OverviewScreen(main_window, app)


@pytest.fixture
def daterange_select_dialog(overview_screen):
    """Return a functional DateRangeSelectDialog instance."""
    return overview.DateRangeSelectDialog(overview_screen)


@pytest.fixture
def fact_grid(request, app):
    """
    Retrurn a generic FactGrid instance.

    Note:
        This instance does not have a parent associated.
    """
    return overview.FactGrid(app.controler, {})


@pytest.fixture
def fact_list_box(request, app, set_of_facts):
    """Return a FactListBox with random facts."""
    return overview.FactListBox(app.controler, set_of_facts)


@pytest.fixture
def factlist_row(request, fact):
    """Return a plain FactListRow instance."""
    return overview.FactListRow(fact)


@pytest.fixture
def factbox(request, fact):
    """Return a plain FactBox instance."""
    return overview.FactBox(fact)


@pytest.fixture
def edit_fact_dialog(request, fact, dummy_window):
    """Return a edit fact dialog for a generic fact."""
    return edit.EditFactDialog(dummy_window, fact)


@pytest.fixture
def charts(request, totals):
    """Return a Charts instance."""
    return overview.Charts(totals)


@pytest.fixture
def tracking_screen(request, app):
    """Return a plain TrackingScreen instance."""
    return tracking.TrackingScreen(app)


@pytest.fixture
def start_tracking_box(request, app):
    """Provide a plain StartTrackingBox instance."""
    return tracking.StartTrackingBox(app.controler)


@pytest.fixture
def current_fact_box(request, app):
    """Provide a plain CurrentFactBox instance."""
    return tracking.CurrentFactBox(app.controler)

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


@pytest.fixture
def facts_grouped_by_date(request, fact_factory):
    """Return a dict with facts ordered by date."""
    return {}


@pytest.fixture
def set_of_facts(request, fact_factory):
    """Provide a set of randomized fact instances."""
    return fact_factory.build_batch(5)


@pytest.fixture
def bar_chart_data(request):
    """
    Return a (value, max_value) tuple suitable to instantiate a BarChart.

    The value is randomized. BarChart widgets also expect a max_value that
    establishes the baseline (100%) for the chart. This fixtures provides such
    a value that makes sure that in effect the value is is in between 5% - 100%
    of that max value.
    """
    value = random.randrange(1, 100)
    # In case value is max value for the total set
    minimal_max_value = value
    # Value is at least 5% of the max value for total set
    maximal_max_value = 20 * value
    max_value = random.randrange(minimal_max_value, maximal_max_value)
    return (value, max_value)


@pytest.fixture
def category_highest_totals(request, faker):
    """Provide a list of timedeltas representing highest category totals."""
    amount = 3
    return [(faker.name(), faker.time_delta()) for i in range(amount)]


@pytest.fixture
def totals(request, faker):
    """Return a randomized 'Totals'-tuple."""
    amount = 5
    category_totals = {faker.name(): faker.time_delta() for i in range(amount)}
    return overview.Totals(activity=[], category=category_totals, date=[])
