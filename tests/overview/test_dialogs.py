# -*- coding: utf-8 -*-


import pytest


class TestOverviewDialog(object):
    """Unittests for the overview dialog."""

    def test__get_facts(self, request, overview_dialog, mocker):
        """Make sure that daterange is considered when fetching facts."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock()
        overview_dialog._get_facts()
        assert overview_dialog._app.store.facts.get_all.called_with(*overview_dialog._daterange)

    @pytest.mark.parametrize('exception', (TypeError, ValueError))
    def test__get_facts_handled_exception(self, request, overview_dialog, exception, mocker):
        """Make sure that we show error dialog if we encounter an expected exception."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock(side_effect=exception)
        show_error = mocker.patch('hamster_gtk.overview.dialogs.helpers.show_error')
        result = overview_dialog._get_facts()
        assert result is None
        assert show_error.called

    def test__get_facts_unhandled_exception(self, request, overview_dialog, mocker):
        """Make sure that we do not intercept unexpected exceptions."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock(side_effect=Exception)
        with pytest.raises(Exception):
            overview_dialog._get_facts()
