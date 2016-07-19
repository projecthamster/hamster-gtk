# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os.path

from gi.repository import Gtk
from six import text_type

import hamster_gtk.hamster_gtk as hamster_gtk
from hamster_gtk.tracking import TrackingScreen


class TestHamsterGTK(object):
    """Unittests for the main app class."""

    def test_instantiation(self):
        """Make sure class instatiation works as intended."""
        app = hamster_gtk.HamsterGTK()
        assert app

    def test__reload_config(self, app, config, mocker):
        """Make sure a config is retrieved and stored as instance attribute."""
        app._get_config_from_file = mocker.MagicMock(return_value=config)
        result = app._reload_config()
        assert result == config
        assert app._config == config

    def test__get_default_config(self, app, appdirs):
        """Make sure the defaults use appdirs for relevant paths."""
        result = app._get_default_config()
        assert len(result) == 6
        assert os.path.dirname(result['tmpfile_path']) == appdirs.user_data_dir
        assert os.path.dirname(result['db_path']) == appdirs.user_data_dir

    def test__config_to_configparser(self, app, config):
        """Make sure conversion of a config dictionary matches expectations."""
        result = app._config_to_configparser(config)
        assert result.get('Backend', 'store') == config['store']
        assert datetime.datetime.strptime(
            result.get('Backend', 'day_start'), '%H:%M:%S'
        ).time() == config['day_start']
        assert int(result.get('Backend', 'fact_min_delta')) == config['fact_min_delta']
        assert result.get('Backend', 'tmpfile_path') == config['tmpfile_path']
        assert result.get('Backend', 'db_engine') == config['db_engine']
        assert result.get('Backend', 'db_path') == config['db_path']

    def test__get_configparser_to_config(self, app, config):
        """Make sure conversion works as expected."""
        # [FIXME]
        # Maybe we find a better way to do this?
        cp_instance = app._config_to_configparser(config)
        result = app._configparser_to_config(cp_instance)
        assert result['store'] == cp_instance.get('Backend', 'store')
        assert result['day_start'] == datetime.datetime.strptime(
            cp_instance.get('Backend', 'day_start'), '%H:%M:%S').time()
        assert result['fact_min_delta'] == int(cp_instance.get('Backend', 'fact_min_delta'))
        assert result['tmpfile_path'] == cp_instance.get('Backend', 'tmpfile_path')
        assert result['db_engine'] == cp_instance.get('Backend', 'db_engine')
        assert result['db_path'] == cp_instance.get('Backend', 'db_path')


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
        assert len(header_bar.get_children()) == 2

    def test__get_overview_button(self, header_bar, mocker):
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

    def test__get_preferences_button(self, header_bar, mocker):
        """Test that that button returned matches expectation."""
        header_bar._on_preferences_button = mocker.MagicMock()
        result = header_bar._get_preferences_button()
        assert isinstance(result, Gtk.Button)
        result.emit('clicked')
        assert header_bar._on_preferences_button.called

    def test__on_preferences_button_apply(self, main_window, mocker):
        """Make sure a preference dialog is created."""
        bar = main_window.get_titlebar()
        preferences_class = mocker.patch('hamster_gtk.hamster_gtk.PreferencesDialog')
        mocker.patch('hamster_gtk.hamster_gtk.PreferencesDialog.run',
            return_value=Gtk.ResponseType.APPLY)
        bar._app.save_config = mocker.MagicMock()
        bar._on_preferences_button(None)
        assert preferences_class.called
        bar._app.save_config.called


class TestPreferencesDialog(object):
    """Unittests for PreferencesDialog."""

    def test_init(self, dummy_window, app, config):
        """Make instantiation works as expected."""
        result = hamster_gtk.PreferencesDialog(dummy_window, app, config)
        grid = result.get_content_area().get_children()[0]
        # This assumes 2 children per config entry (label and widget).
        assert len(grid.get_children()) / 2 == len(config.keys())

    def test_get_config(self, dummy_window, app, initial_config_parametrized):
        """
        Make sure retrieval of field values works as expected.

        In particular we need to make sure that unicode/utf-8 handling works as
        expected.
        """
        dialog = hamster_gtk.PreferencesDialog(dummy_window, app, initial_config_parametrized)
        result = dialog.get_config()
        assert result == initial_config_parametrized

    def test_get_store_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_store_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.ComboBoxText)

    def test_get_day_start_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_day_start_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.Entry)

    def test_get_fact_min_delta_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_fact_min_delta_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.Entry)

    def test_get_tmpfile_path_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_tmpfile_path_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.Grid)

    def test_get_db_engine_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_db_engine_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.ComboBoxText)

    def test_get_db_path_widget(self, preferences_dialog):
        """Make sure widgets match expectation."""
        label, widget = preferences_dialog._get_db_path_widget()
        assert isinstance(label, Gtk.Label)
        assert isinstance(widget, Gtk.Grid)
