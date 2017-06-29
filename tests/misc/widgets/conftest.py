# -*- coding: utf-8 -*-

"""Fixtures for unittesting the misc widgets submodule."""

from __future__ import absolute_import, unicode_literals

import collections

import pytest

from hamster_gtk.misc import widgets
from hamster_gtk.preferences.widgets import (ComboFileChooser,
                                             HamsterComboBoxText)


@pytest.fixture
def preference_page_fields(request):
    """Return a static dict of valid fields suitable to be consumed by ``LabelledWidgetsGrid``."""
    return collections.OrderedDict((
        ('store', ('_Store', HamsterComboBoxText([]))),
        ('db_engine', ('DB _Engine', HamsterComboBoxText([]))),
        ('db_path', ('DB _Path', ComboFileChooser())),
        ('tmpfile_path', ('_Temporary file', ComboFileChooser())),
    ))


@pytest.fixture
def labelled_widgets_grid(request, preference_page_fields):
    """Return a ``LabelledWidgetsGrid`` instance."""
    return widgets.LabelledWidgetsGrid(preference_page_fields)
