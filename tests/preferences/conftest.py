# -*- coding: utf-8 -*-

"""Fixtures for unittesting the preferences submodule."""

from __future__ import absolute_import, unicode_literals

import datetime
import os.path

import fauxfactory
import pytest
from gi.repository import Gtk

from hamster_gtk.preferences import widgets


# Instances

@pytest.fixture
def hamster_combo_box_text(request, combo_box_items):
    """Return a HamsterComboBoxText instance."""
    widget = widgets.HamsterComboBoxText()
    for id, item in combo_box_items:
        widget.append(id, item)
    return widget


@pytest.fixture
def editable_file_chooser(request):
    """Return a EditableFileChooser instance."""
    return widgets.EditableFileChooser()


@pytest.fixture
def duration_entry(request, adjustment):
    """Return a DurationEntry instance."""
    return widgets.DurationEntry(adjustment)


@pytest.fixture
def time_entry(request):
    """Return a TimeEntry instance."""
    return widgets.TimeEntry()


# Data

@pytest.fixture
def combo_box_items(request, faker):
    """Return a collection of items to be placed into ComboBox."""
    amount = 5
    return [(faker.user_name(), faker.name()) for i in range(amount)]


@pytest.fixture
def paths(request, faker):
    """Return a list of file paths."""
    amount = 3
    return [os.path.join(faker.uri(), faker.uri_path()) for i in range(amount)]


@pytest.fixture
def adjustment(request, numbers):
    """Return a list of random numbers."""
    value = sorted(numbers)[len(numbers) // 2]
    lower = min(numbers)
    upper = max(numbers)
    step_increment = 1
    page_increment = 5
    page_size = 0
    return Gtk.Adjustment(value, lower, upper, step_increment, page_increment, page_size)


@pytest.fixture
def simple_adjustment(request, faker):
    """Return three random numbers in an ascending order."""
    a = faker.random_number()
    b = faker.random_number()
    step = faker.random_number(digits=2)
    return widgets.SimpleAdjustment(min=min(a, b), max=max(a, b), step=step)


@pytest.fixture
def numbers(request, faker):
    """Return a list of random numbers."""
    amount = 8
    return [faker.random_number(digits=5) for i in range(amount)]


@pytest.fixture
def times(request, faker):
    """Return a list of random times."""
    amount = 3
    return [datetime.datetime.strptime(faker.time(), '%H:%M:%S').time() for i in range(amount)]


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
