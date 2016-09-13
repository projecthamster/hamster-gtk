# -*- coding: utf-8 -*-

"""Fixtures for unittesting the preferences submodule."""

from __future__ import absolute_import, unicode_literals

import datetime
from gi.repository import Gtk
import os.path
import pytest

from hamster_gtk.preferences import widgets


# Instances

@pytest.fixture
def combo_box_text_config(request, combo_box_items):
    """Return a ComboBoxTextConfig instance."""
    widget = widgets.ComboBoxTextConfig()
    for id, item in combo_box_items:
        widget.append(id, item)
    return widget


@pytest.fixture
def editable_file_chooser(request):
    """Return a EditableFileChooser instance."""
    return widgets.EditableFileChooser()


@pytest.fixture
def spin_button_config(request, adjustment):
    """Return a SpinButtonConfig instance."""
    return widgets.SpinButtonConfig(adjustment)


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
def adjustment(request, faker, numbers):
    """Return a list of random numbers."""
    value = sorted(numbers)[len(numbers) // 2]
    lower = min(numbers)
    upper = max(numbers)
    step_increment = 1
    page_increment = 5
    page_size = 5
    return Gtk.Adjustment(value, lower, upper, step_increment, page_increment, page_size)


@pytest.fixture
def numbers(request, faker):
    """Return a list of random numbers."""
    amount = 8
    return [faker.random_number(digits=5) for i in range(amount)]


@pytest.fixture
def times(request, faker):
    """Return a list of random numbers."""
    amount = 3
    return [datetime.datetime.strptime(faker.time(), '%H:%M:%S').time() for i in range(amount)]
