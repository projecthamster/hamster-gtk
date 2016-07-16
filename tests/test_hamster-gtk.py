# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from gi.repository import Gtk
from six import text_type

from hamster_gtk import hamster_gtk
from hamster_gtk.tracking import TrackingScreen


class TestHamsterGTK(object):
    """Unittests for the main app class."""

    def test_instantiation(self):
        """Make sure class instatiation works as intended."""
        app = hamster_gtk.HamsterGTK()
        assert app


class TestMainWindow(object):
    """Unittests for the main application window."""

    def test_init(self, app):
        """Make sure class setup works up as intended."""
        window = hamster_gtk.MainWindow(app)
        assert isinstance(window.get_titlebar(), hamster_gtk.HeaderBar)
        assert isinstance(window.app, hamster_gtk.HamsterGTK)
        assert isinstance(window.get_children()[0], TrackingScreen)

    def test_get_css(self, main_window):
        """Make sure a string is returned."""
        assert isinstance(main_window._get_css(), text_type)


class TestHeaderBar(object):
    """Unittests for main window titlebar."""

    def test_initial_anatomy(self, header_bar):
        """Test that the bars initial setup is as expected."""
        assert header_bar.props.title == 'Hamster-GTK'
        assert header_bar.props.subtitle == 'Your friendly time tracker.'
        assert header_bar.props.show_close_button
        assert len(header_bar.get_children()) == 1

    def test__get_oheader_barview_button(self, header_bar, mocker):
        """Test that that button returned matches expectation."""
        header_bar._on_overview_button = mocker.MagicMock()
        result = header_bar._get_overview_button()
        assert isinstance(result, Gtk.Button)
        result.emit('clicked')
        assert header_bar._on_overview_button.called

    def test__on_overview_button(self, main_window, mocker):
        """Make sure a new overview is created if none exist."""
        bar = main_window.get_titlebar()
        overview_class = mocker.patch('hamster_gtk.hamster_gtk.OverviewDialog')
        bar._on_overview_button(None)
        assert overview_class.called
