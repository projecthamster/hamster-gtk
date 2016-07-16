# -*- coding: utf-8 -*-

"""Unittest fixtures."""

import fauxfactory
import pytest
from gi.repository import Gtk
from pytest_factoryboy import register

import factories
import hamster_gtk.hamster_gtk as hamster_gtk

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


@pytest.fixture(params=(
    fauxfactory.gen_string('utf8'),
    fauxfactory.gen_string('cjk'),
    fauxfactory.gen_string('latin1'),
    fauxfactory.gen_string('cyrillic'),
))
def word_parametrized(request):
    """Return a string paramized with various different charakter constelations."""
    return request.param


@pytest.fixture
def facts_grouped_by_date(request, fact_factory):
    """Return a dict with facts ordered by date."""
    return {}


@pytest.fixture
def set_of_facts(request, fact_factory):
    """Provide a set of randomized fact instances."""
    return fact_factory.build_batch(5)
