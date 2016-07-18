# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime

import pytest
from gi.repository import Gtk

from hamster_gtk.overview import widgets


class TestFactGrid(object):
    """Unittests for FactGrid."""

    def test_init(self, app):
        """Make sure minimal initialisation works."""
        fact_grid = widgets.FactGrid(app.controler, {})
        assert fact_grid

    def test__get_date_widget(self, fact_grid):
        """Make sure expected label is returned."""
        result = fact_grid._get_date_widget(datetime.date.today())
        assert isinstance(result, Gtk.EventBox)

    def test__get_fact_list(self, app, fact_grid):
        """Make sure a FactListBox is retuned."""
        result = fact_grid._get_fact_list(app.controler, [])
        assert isinstance(result, widgets.fact_grid.FactListBox)


class TestFactListBox(object):
    """Unittest for FactListBox."""

    def test_init(self, app, set_of_facts):
        """Test that instantiation works as expected."""
        result = widgets.fact_grid.FactListBox(app.controler, set_of_facts)
        assert isinstance(result, widgets.fact_grid.FactListBox)
        assert len(result.get_children()) == len(set_of_facts)

    def test__on_activate_reject(self, fact_list_box, fact, mocker):
        """Make sure an edit dialog is created, processed and then destroyed."""
        fact_list_box.get_toplevel = Gtk.Window
        mocker.patch('hamster_gtk.overview.widgets.fact_grid.EditFactDialog.run',
                     return_value=Gtk.ResponseType.REJECT)
        fact_list_box._delete_fact = mocker.MagicMock()
        row = mocker.MagicMock()
        row.fact = fact
        fact_list_box._on_activate(None, row)
        assert fact_list_box._delete_fact.called

    def test__on_activate_apply(self, fact_list_box, fact, mocker):
        """Make sure an edit dialog is created, processed and then destroyed."""
        fact_list_box.get_toplevel = Gtk.Window
        mocker.patch('hamster_gtk.overview.widgets.fact_grid.EditFactDialog.run',
                     return_value=Gtk.ResponseType.APPLY)
        fact_list_box._update_fact = mocker.MagicMock()
        row = mocker.MagicMock()
        row.fact = fact
        fact_list_box._on_activate(None, row)
        assert fact_list_box._update_fact.called

    def test__delete_fact(self, request, fact_list_box, fact, mocker):
        """Make sure that ``facts_changed`` signal is emitted."""
        fact_list_box._controler.store.facts.remove = mocker.MagicMock()
        fact_list_box.emit = mocker.MagicMock()
        result = fact_list_box._delete_fact(fact)
        assert fact_list_box._controler.store.facts.remove.called
        assert result is result
        assert fact_list_box.emit.called_with('facts_changed')

    @pytest.mark.parametrize('exception', (KeyError, ValueError))
    def test__delete_fact_expected_exception(self, request, fact_list_box, exception, fact,
            mocker):
        """Make sure that we show error dialog if we encounter an expected exception."""
        fact_list_box._controler.store.facts.remove = mocker.MagicMock(side_effect=exception)
        show_error = mocker.patch('hamster_gtk.overview.widgets.fact_grid.helpers.show_error')
        fact_list_box.emit = mocker.MagicMock()
        result = fact_list_box._delete_fact(fact)
        assert result is None
        assert show_error.called
        assert fact_list_box.emit.called is False

    def test__delete_fact_unexpected_exception(self, request, fact_list_box, fact, mocker):
        """Make sure that we do not intercept unexpected exceptions."""
        fact_list_box._controler.store.facts.remove = mocker.MagicMock(side_effect=Exception)
        with pytest.raises(Exception):
            fact_list_box._on_cancel_button(fact)


class TestFactListRow(object):
    """Unittests for FactListRow."""

    def test_init(self, fact):
        """Make sure instantiated object matches expectations."""
        result = widgets.fact_grid.FactListRow(fact)
        assert isinstance(result, widgets.fact_grid.FactListRow)
        hbox = result.get_children()[0]
        children = hbox.get_children()
        assert isinstance(children[0], Gtk.Label)
        assert isinstance(children[1], widgets.fact_grid.FactBox)
        assert isinstance(children[2], Gtk.EventBox)

    def test_get_time_widget(self, factlist_row, fact):
        """Make sure widget matches expectations."""
        result = factlist_row._get_time_widget(fact)
        assert isinstance(result, Gtk.Label)

    def test_get_delta_widget(self, factlist_row, fact):
        """Make sure widget matches expectations."""
        result = factlist_row._get_delta_widget(fact)
        assert isinstance(result, Gtk.EventBox)


class TestFactBox(object):
    """Unittests for FactBox."""

    def test_init(self, fact):
        """Make sure instantiated object matches expectations."""
        result = widgets.fact_grid.FactBox(fact)
        assert isinstance(result, widgets.fact_grid.FactBox)
        assert len(result.get_children()) == 3

    def test_init_without_description(self, fact):
        """Make sure instantiated object matches expectations."""
        fact.description = ''
        result = widgets.fact_grid.FactBox(fact)
        assert isinstance(result, widgets.fact_grid.FactBox)
        assert len(result.get_children()) == 2

    def test__get_activity_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        result = factbox._get_activity_widget(fact)
        assert isinstance(result, Gtk.Label)

    def test__get_tags_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        # [FIXME]
        # Once the method is not just using a dummy tag, this needs to be
        # refactored.
        result = factbox._get_tags_widget(fact)
        assert isinstance(result, Gtk.Box)
        assert len(result.get_children()) == 1

    def test__get_desciption_widget(self, factbox, fact):
        """Make sure instantiated object matches expectations."""
        result = factbox._get_description_widget(fact)
        assert isinstance(result, Gtk.Label)
        result = factbox._get_description_widget(fact)
        assert isinstance(result, Gtk.Label)


class TestCharts(object):
    """Unittests for Charts."""

    def test_init(self, totals):
        """Make sure instance matches expectation."""
        result = widgets.Charts(totals)
        assert isinstance(result, widgets.Charts)
        assert len(result.get_children()) == 1

    def test__get_category_widget(self, charts, totals):
        """Make sure widget matches expectations."""
        result = charts._get_category_widget(totals.category)
        assert isinstance(result, Gtk.Grid)
        # Each category will trigger adding 3 children.
        assert len(result.get_children()) == 3 * len(totals.category)

    @pytest.mark.parametrize(('minutes', 'expectation'), (
        (1, '1 min'),
        (30, '30 min'),
        (59, '59 min'),
        (60, '01:00'),
        (300, '05:00'),
    ))
    def test__get_delta_string(self, charts, minutes, expectation):
        delta = datetime.timedelta(minutes=minutes)
        result = charts._get_delta_string(delta)
        assert result == expectation


class TestHorizontalBarChart(object):
    """Unittests for HorizontalBarChart."""

    # [FIXME]
    # Figure out a way to test the draw function properly.

    def test_init(self, bar_chart_data):
        """Make sure instance matches expectations."""
        value, max_value = bar_chart_data
        result = widgets.charts.HorizontalBarChart(value, max_value)
        assert isinstance(result, widgets.charts.HorizontalBarChart)


class TestSummary(object):
    """Unittests for Summery."""

    def test_init(self, category_highest_totals):
        """Test that instance meets expectation."""
        result = widgets.Summary(category_highest_totals)
        assert isinstance(result, widgets.Summary)
        assert len(result.get_children()) == len(category_highest_totals)
