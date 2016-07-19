# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from gi.repository import Gtk
from six import text_type
import pytest

from hamster_gtk.helpers import _u
from hamster_gtk.tracking import screens


class TestTrackingScreen(object):
    """Unittests for tracking screen."""

    def test_init(self, app):
        """Make sure instance matches expectation."""
        result = screens.TrackingScreen(app)
        assert isinstance(result, screens.TrackingScreen)
        assert len(result.get_children()) == 2

    def test_update_with_ongoing_fact(self, tracking_screen, fact, mocker):
        """Make sure current fact view is shown."""
        fact.end is None
        tracking_screen.app.controler.store.facts.get_tmp_fact = mocker.MagicMock(
            return_value=fact)
        tracking_screen.update()
        result = tracking_screen.get_visible_child()
        assert result == tracking_screen.current_fact_view
        assert isinstance(result, screens.CurrentFactBox)

    def test_update_with_no_ongoing_fact(self, tracking_screen, mocker):
        """Make sure start tracking view is shown."""
        tracking_screen.app.controler.store.facts.get_tmp_fact = mocker.MagicMock(
            side_effect=KeyError)
        tracking_screen.update()
        result = tracking_screen.get_visible_child()
        assert result == tracking_screen.start_tracking_view
        assert isinstance(result, screens.StartTrackingBox)


class TestStartTrackingBox(object):
    """Unittests for TrackingBox."""

    def test_init(self, app):
        """Make sure instances matches expectation."""
        result = screens.StartTrackingBox(app.controler)
        assert isinstance(result, screens.StartTrackingBox)
        assert len(result.get_children()) == 3

    def test__on_start_tracking_button(self, start_tracking_box, fact, mocker):
        """Make sure a new 'ongoing fact' is created."""
        # [FIXME]
        # We need to find a viable way to check if signals are emitted!
        start_tracking_box._controler.store.facts.save = mocker.MagicMock()
        raw_fact = '{fact.activity.name}@{fact.category.name}'.format(fact=fact)
        start_tracking_box.raw_fact_entry.props.text = raw_fact
        start_tracking_box._on_start_tracking_button(None)
        assert start_tracking_box._controler.store.facts.save.called

    def test__reset(self, start_tracking_box):
        """Make sure all relevant widgets are reset."""
        start_tracking_box.raw_fact_entry.props.text = 'foobar'
        start_tracking_box.reset()
        assert start_tracking_box.raw_fact_entry.props.text == ''


class TestCurrentFactBox(object):
    """Unittests for CurrentFactBox."""

    def test_init(self, app):
        result = screens.CurrentFactBox(app.controler)
        assert isinstance(result, screens.CurrentFactBox)

    def test_update_initial_fact(self, current_fact_box, fact):
        """Make sure update re-creates as widgets as expected."""
        assert not current_fact_box.content.get_children()
        current_fact_box.update(fact)
        assert len(current_fact_box.content.get_children()) == 3
        label = current_fact_box.content.get_children()[0]
        expectation = '{activity.name}@{activity.category}'.format(activity=fact.activity)
        assert expectation in _u(label.get_text())

    def test__get_fact_label(self, current_fact_box, fact):
        """Make sure that the label matches expectations."""
        result = current_fact_box._get_fact_label(fact)
        assert isinstance(result, Gtk.Label)
        assert _u(result.get_text()) == text_type(fact)

    def test__get_cancel_button(self, current_fact_box):
        """Make sure widget matches expectation."""
        result = current_fact_box._get_cancel_button()
        assert isinstance(result, Gtk.Button)

    def test__get_save_button(self, current_fact_box):
        """Make sure widget matches expectation."""
        result = current_fact_box._get_save_button()
        assert isinstance(result, Gtk.Button)

    def test__get_invalid_label(self, current_fact_box):
        """Make sure widget matches expectation."""
        result = current_fact_box._get_invalid_label()
        assert isinstance(result, Gtk.Label)

    def test_on_cancel_buton(self, request, current_fact_box, mocker):
        """Make sure that 'tracking-stopped' signal is emitted."""
        current_fact_box._controler.store.facts.cancel_tmp_fact = mocker.MagicMock()
        current_fact_box.emit = mocker.MagicMock()
        result = current_fact_box._on_cancel_button(None)
        assert current_fact_box._controler.store.facts.cancel_tmp_fact.called
        assert result is None
        assert current_fact_box.emit.called_with('tracking-stopped')

    def test_on_cancel_buton_expected_exception(self, request, current_fact_box, mocker):
        """Make sure that we show error dialog if we encounter an expected exception."""
        current_fact_box._controler.store.facts.cancel_tmp_fact = mocker.MagicMock(
            side_effect=KeyError)
        show_error = mocker.patch('hamster_gtk.tracking.screens.helpers.show_error')
        current_fact_box.emit = mocker.MagicMock()
        result = current_fact_box._on_cancel_button(None)
        assert result is None
        assert show_error.called
        assert current_fact_box.emit.called is False

    def test_on_cancel_buton_unexpected_exception(self, request, current_fact_box, mocker):
        """Make sure that we do not intercept unexpected exceptions."""
        current_fact_box._controler.store.facts.cancel_tmp_fact = mocker.MagicMock(
            side_effect=Exception)
        with pytest.raises(Exception):
            current_fact_box._on_cancel_button(None)
