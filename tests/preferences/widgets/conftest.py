# -*- coding: utf-8 -*-

"""Fixtures for unittesting the preferences submodule."""

from __future__ import absolute_import, unicode_literals

import datetime
import os.path

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
def combo_file_chooser(request):
    """Return a ComboFileChooser instance."""
    return widgets.ComboFileChooser()


@pytest.fixture
def hamster_spin_button(request, adjustment):
    """Return a HamsterSpinButton instance."""
    return widgets.HamsterSpinButton(adjustment)


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


@pytest.fixture
def times_without_seconds(request, times):
    """Return a list of random times rounded down to whole minutes."""
    return [time.replace(second=0) for time in times]
