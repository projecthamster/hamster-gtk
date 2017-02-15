# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os.path

from gi.repository import Gtk

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

    def test__config_changed(self, app, config, mocker):
        """Make sure the controller *and* client config is updated."""
        app._reload_config = mocker.MagicMock(return_value=config)
        app.controller.update_config = mocker.MagicMock()
        app._config_changed(None)
        assert app._reload_config.called
        assert app.controller.update_config.called_with(config)

    def test__create_actions(self, app, mocker):
        """Test that that actions are created."""
        app.add_action = mocker.MagicMock()
        app._create_actions()
        assert app.add_action.call_count == 4

    def test__on_about_action(self, app, mocker):
        """Make sure an about dialog is created."""
        about_class = mocker.patch('hamster_gtk.hamster_gtk.AboutDialog')
        app._on_about_action(None, None)
        assert about_class.called
        assert about_class.return_value.run.called

    def test__on_overview_action(self, app, mocker):
        """Make sure an overview dialog is created."""
        overview_class = mocker.patch('hamster_gtk.hamster_gtk.OverviewDialog')
        app._on_overview_action(None, None)
        assert overview_class.called
        assert overview_class.return_value.run.called

    def test__on_preferences_action(self, app, mocker):
        """Make sure a preference dialog is created."""
        preferences_class = mocker.patch('hamster_gtk.hamster_gtk.PreferencesDialog')
        app._on_preferences_action(None, None)
        assert preferences_class.called
        assert preferences_class.return_value.run.called

    def test__on_preferences_action_apply(self, app, mocker):
        """Make sure config is saved when apply is pressed in preference dialog."""
        mocker.patch('hamster_gtk.hamster_gtk.PreferencesDialog.run',
            return_value=Gtk.ResponseType.APPLY)
        app.save_config = mocker.MagicMock()
        app._on_preferences_action(None, None)
        assert app.save_config.called

    def test__on_preferences_action_cancel(self, app, mocker):
        """Make sure config is not saved when cancel is pressed in preference dialog."""
        mocker.patch('hamster_gtk.hamster_gtk.PreferencesDialog.run',
            return_value=Gtk.ResponseType.CANCEL)
        app.save_config = mocker.MagicMock()
        app._on_preferences_action(None, None)
        assert not app.save_config.called


class TestMainWindow(object):
    """Unittests for the main application window."""

    def test_init(self, app):
        """Make sure class setup works up as intended."""
        window = hamster_gtk.MainWindow(app)
        assert isinstance(window.get_titlebar(), hamster_gtk.HeaderBar)
        assert isinstance(window.app, hamster_gtk.HamsterGTK)
        assert isinstance(window.get_children()[0], TrackingScreen)


class TestHeaderBar(object):
    """Unittests for main window titlebar."""

    def test_initial_anatomy(self, header_bar):
        """Test that the bars initial setup is as expected."""
        assert header_bar.props.title == 'Hamster-GTK'
        assert header_bar.props.subtitle == 'Your friendly time tracker.'
        assert header_bar.props.show_close_button
        assert len(header_bar.get_children()) == 1

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
