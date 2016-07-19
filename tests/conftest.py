# -*- coding: utf-8 -*-

"""Unittest fixtures."""

from __future__ import absolute_import, unicode_literals

import datetime

import fauxfactory
import pytest
from gi.repository import Gtk
from hamster_lib.helpers.config_helpers import HamsterAppDirs
from pytest_factoryboy import register

from hamster_gtk import hamster_gtk

from . import factories

register(factories.CategoryFactory)
register(factories.ActivityFactory)
register(factories.FactFactory)


@pytest.fixture
def appdirs(request):
    """Return HamsterAppDirs instance."""
    return HamsterAppDirs('hamster-gtk')


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
def header_bar(request, app):
    """
    Return a HeaderBar instance.

    Note:
        This instance has not been added to any parent window yet!
    """
    return hamster_gtk.HeaderBar(app)


@pytest.fixture
def dummy_window(request):
    """
    Return a generic :class:`Gtk.Window` instance.

    This is useful for tests that do not actually rely on external
    functionality.
    """
    return Gtk.Window()


@pytest.fixture
def preferences_dialog(request, dummy_window, app, config):
    """Return plain PreferencesDialog instance."""
    return hamster_gtk.PreferencesDialog(dummy_window, app, config)


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


@pytest.fixture
def config(request, tmpdir):
    """Return a dict of config keys and values."""
    config = {
        'store': 'sqlalchemy',
        'day_start': datetime.time(5, 30, 0),
        'fact_min_delta': 1,
        'tmpfile_path': tmpdir.join('tmpfile.hamster'),
        'db_engine': 'sqlite',
        'db_path': ':memory:',
    }
    return config


@pytest.fixture(params=('sqlalchemy',))
def store_parametrized(request):
    """Return a parametrized store value."""
    return request.param


@pytest.fixture(params=(
    datetime.time(0, 0, 0),
    datetime.time(5, 30, 0),
    datetime.time(17, 22, 0),
))
def day_start_parametrized(request):
    """Return a parametrized day_start value."""
    return request.param


@pytest.fixture(params=(0, 1, 30, 60))
def fact_min_delta_parametrized(request):
    """Return a parametrized fact_min_delta value."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
))
def tmpfile_path_parametrized(request, tmpdir):
    """Return a parametrized tmpfile_path value."""
    return tmpdir.mkdir(request.param).join('tmpfile.hamster')


@pytest.fixture(params=(
    'sqlite',
))
def db_engine_parametrized(request):
    """Return a parametrized db_engine value."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    ':memory:',
))
def db_path_parametrized(request, tmpdir):
    """Return a parametrized db_path value."""
    if not request.param == ':memory:':
        path = tmpdir.mkdir(request.param).join('hamster.file')
    else:
        path = request.param
    return path


@pytest.fixture
def initial_config_parametrized(request, store_parametrized, day_start_parametrized,
        fact_min_delta_parametrized, tmpfile_path_parametrized, db_engine_parametrized,
        db_path_parametrized):
            """Return a config fixture with heavily parametrized config values."""
            return {
                'store': store_parametrized,
                'day_start': day_start_parametrized,
                'fact_min_delta': fact_min_delta_parametrized,
                'tmpfile_path': tmpfile_path_parametrized,
                'db_engine': db_engine_parametrized,
                'db_path': db_path_parametrized,
            }
