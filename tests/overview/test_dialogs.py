# -*- coding: utf-8 -*-


import pytest


class TestOverviewDialog(object):
    """Unittests for the overview dialog."""

    def test__get_facts(self, overview_dialog, mocker):
        """Make sure that daterange is considered when fetching facts."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock()
        overview_dialog._get_facts()
        assert overview_dialog._app.store.facts.get_all.called_with(*overview_dialog._daterange)

    @pytest.mark.parametrize('exception', (TypeError, ValueError))
    def test__get_facts_handled_exception(self, overview_dialog, exception, mocker):
        """Make sure that we show error dialog if we encounter an expected exception."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock(side_effect=exception)
        show_error = mocker.patch('hamster_gtk.overview.dialogs.helpers.show_error')
        result = overview_dialog._get_facts()
        assert result is None
        assert show_error.called

    def test__get_facts_unhandled_exception(self, overview_dialog, mocker):
        """Make sure that we do not intercept unexpected exceptions."""
        overview_dialog._app.store.facts.get_all = mocker.MagicMock(side_effect=Exception)
        with pytest.raises(Exception):
            overview_dialog._get_facts()

    # [FIXME]
    # It is probably good to also have a more comprehensive test that actually
    # checks if a file with particular content is written.
    def test__export_facts(self, overview_dialog, tmpdir, mocker):
        """
        Make sure the proper report class is instantiated and writter.

        With all its mocks this test is not the best one imageinable, but as
        the method will change rapidly soon this does for now.
        """
        writer = mocker.patch('hamster_gtk.overview.dialogs.reports.TSVWriter')
        overview_dialog._get_facts = mocker.MagicMock(return_value={})
        result = overview_dialog._export_facts(tmpdir.strpath)
        assert result is None
        assert writer.called
        assert overview_dialog._get_facts.called
