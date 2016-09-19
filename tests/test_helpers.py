# -*- coding: utf-8 -*-

import os.path
import hamster_gtk.helpers as helpers


def test_get_resource_path(request, file_path):
    """Make sure the path to the resource is correct."""
    path = helpers.get_resource_path(file_path)
    expected = os.path.join(os.path.dirname(helpers.__file__), 'resources', file_path)
    assert path == expected
