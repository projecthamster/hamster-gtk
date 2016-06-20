# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from six import text_type

from hamster_gtk import hamster_gtk
from hamster_gtk.screens.tracking import TrackingScreen


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
        assert isinstance(window._app, hamster_gtk.HamsterGTK)
        assert window.get_size() == hamster_gtk.DEFAULT_WINDOW_SIZE
        assert isinstance(window.get_children()[0], TrackingScreen)

    def test_get_css(self, app_window):
        """Make sure a string is returned."""
        assert isinstance(app_window._get_css(), text_type)


class TestHeaderBar(object):
    """Test that headerbar works as intended."""

    def test_initial_anatomy(self, app_window):
        """Test that the bars initial setup is as expected."""
        bar = hamster_gtk.HeaderBar(app_window, app_window._app)
        assert bar.props.title == 'Hamster-GTK'
        assert bar.props.subtitle == 'Your friendly time tracker.'
        assert bar.props.show_close_button
        assert len(bar.get_children()) == 1

    def test_on_overview_button_overview_exists(self, app_window):
        """Test that we don't create a new overview if we already have one."""
        app_window.overview = True
        bar = hamster_gtk.HeaderBar(app_window, app_window._app)
        assert bar._on_overview_button(None) is None
