# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from hamster_gtk import dialogs


class TestErrorDialog(object):
    """Unittests for ErrorDialog."""

    def test_init_with_parent_window(self, dummy_window):
        """Test instances where toplevel is a window instance."""
        result = dialogs.ErrorDialog(dummy_window, '')
        assert result
