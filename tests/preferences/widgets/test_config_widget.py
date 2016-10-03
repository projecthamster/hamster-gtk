# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import pytest

from hamster_gtk.preferences import widgets


class TestConfigWidget(object):
    """Unittests for ConfigWidget."""

    def test_get_config_value(self):
        """Calling get_config_value should raise NotImplementedError."""
        widget = widgets.ConfigWidget()
        with pytest.raises(NotImplementedError):
            widget.get_config_value()

    def test_set_config_value(self):
        """Calling set_config_value should raise NotImplementedError."""
        widget = widgets.ConfigWidget()
        with pytest.raises(NotImplementedError):
            widget.set_config_value(None)
