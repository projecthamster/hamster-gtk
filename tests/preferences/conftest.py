# -*- coding: utf-8 -*-

"""Fixtures for unittesting the preferences submodule."""

from __future__ import absolute_import, unicode_literals

import datetime

import fauxfactory
import pytest


# Data

@pytest.fixture(params=('sqlalchemy',))
def store_parametrized(request):
    """Return a parametrized store value."""
    return request.param


@pytest.fixture(params=(
    datetime.time(0, 0, 0),
    datetime.time(5, 30, 0),
    datetime.time(17, 22, 0),
))
def day_start_parametrized(request):
    """Return a parametrized day_start value."""
    return request.param


@pytest.fixture(params=(0, 1, 30, 60))
def fact_min_delta_parametrized(request):
    """Return a parametrized fact_min_delta value."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
))
def tmpfile_path_parametrized(request, tmpdir):
    """Return a parametrized tmpfile_path value."""
    return tmpdir.mkdir(request.param).join('tmpfile.hamster')


@pytest.fixture(params=(
    'sqlite',
))
def db_engine_parametrized(request):
    """Return a parametrized db_engine value."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_utf8(),
    fauxfactory.gen_latin1(),
    ':memory:',
))
def db_path_parametrized(request, tmpdir):
    """Return a parametrized db_path value."""
    if not request.param == ':memory:':
        path = tmpdir.mkdir(request.param).join('hamster.file')
    else:
        path = request.param
    return path


@pytest.fixture
def initial_config_parametrized(request, store_parametrized, day_start_parametrized,
        fact_min_delta_parametrized, tmpfile_path_parametrized, db_engine_parametrized,
        db_path_parametrized):
            """Return a config fixture with heavily parametrized config values."""
            return {
                'store': store_parametrized,
                'day_start': day_start_parametrized,
                'fact_min_delta': fact_min_delta_parametrized,
                'tmpfile_path': tmpfile_path_parametrized,
                'db_engine': db_engine_parametrized,
                'db_path': db_path_parametrized,
            }
