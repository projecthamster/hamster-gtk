# -*- coding: utf-8 -*-

"""Fixtures for unittesting the overview submodule."""

from __future__ import absolute_import, unicode_literals

import datetime
import random

import pytest

from hamster_gtk.overview import dialogs, widgets


# Instances

@pytest.fixture
def charts(request, totals):
    """Return a Charts instance."""
    return widgets.Charts(totals)


@pytest.fixture
def fact_grid(request, app):
    """
    Retrurn a generic FactGrid instance.

    Note:
        This instance does not have a parent associated.
    """
    return widgets.fact_grid.FactGrid(app.controler, {})


@pytest.fixture
def fact_list_box(request, app, set_of_facts):
    """Return a FactListBox with random facts."""
    return widgets.fact_grid.FactListBox(app.controler, set_of_facts)


@pytest.fixture
def factlist_row(request, fact):
    """Return a plain FactListRow instance."""
    return widgets.fact_grid.FactListRow(fact)


@pytest.fixture
def factbox(request, fact):
    """Return a plain FactBox instance."""
    return widgets.fact_grid.FactBox(fact)


@pytest.fixture
def overview_dialog(main_window, app):
    """Return a generic :class:`OverViewDialog` instance."""
    return dialogs.OverviewDialog(main_window, app)

# Data


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
    return dialogs.Totals(activity=[], category=category_totals, date=[])


@pytest.fixture(params=(0, 7, 15, 30, 55))
def daterange_offset_parametrized(request):
    """Return various daterange offset variants as easy to use timedeltas."""
    return datetime.timedelta(days=request.param)
