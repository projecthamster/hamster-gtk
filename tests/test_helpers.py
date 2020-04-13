# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime

import pytest
from gi.repository import Gtk

import hamster_gtk.helpers as helpers


def test_get_parent_window_standalone(request):
    """Make sure the parent window of a windowless widget is None."""
    label = Gtk.Label('foo')
    assert helpers.get_parent_window(label) is None


def test_get_parent_window(request):
    """Make sure the parent window of a widget placed in the window is determined correctly."""
    window = Gtk.Window()
    label = Gtk.Label('foo')
    window.add(label)
    assert helpers.get_parent_window(label) == window


@pytest.mark.parametrize(('text', 'expectation'), [
    # Date, time and datetime
    ('2016-02-01 12:00 ',
     {'timeinfo': '2016-02-01 12:00 ',
      }),
    ('2016-02-01 ',
     {'timeinfo': '2016-02-01 ',
      }),
    ('12:00 ',
     {'timeinfo': '12:00 ',
      }),
    # Timeranges
    ('2016-02-01 12:00 - 2016-02-03 15:00 ',
     {'timeinfo': '2016-02-01 12:00 - 2016-02-03 15:00 ',
      }),
    ('12:00 - 2016-02-03 15:00 ',
     {'timeinfo': '12:00 - 2016-02-03 15:00 ',
      }),
    ('12:00 - 15:00 ',
     {'timeinfo': '12:00 - 15:00 ',
      }),
    ('2016-01-01 12:00 ,lorum_ipsum',
     {'timeinfo': '2016-01-01 12:00 ',
      'description': ',lorum_ipsum',
      }),
    ('2016-01-01 12:00 foo@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '2016-01-01 12:00 ',
      'activity': 'foo',
      'category': '@bar',
      'tags': ' #t1 #t2',
      'description': ',lorum_ipsum',
      }),
    ('12:00 - 15:00 foo@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '12:00 - 15:00 ',
      'activity': 'foo',
      'category': '@bar',
      'tags': ' #t1 #t2',
      'description': ',lorum_ipsum',
      }),
    ('2016-02-20 12:00 - 2016-02-20 15:00 foo@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '2016-02-20 12:00 - 2016-02-20 15:00 ',
      'activity': 'foo',
      'category': '@bar',
      'tags': ' #t1 #t2',
      'description': ',lorum_ipsum',
      }),
    ('2016-02-20 12:00 - 2016-02-20 15:00 foo,bar, lorum_ipsum',
     {'timeinfo': '2016-02-20 12:00 - 2016-02-20 15:00 ',
      'activity': 'foo',
      'description': ',bar, lorum_ipsum',
      }),
    # Others
    # Using a ``#`` in the activity name will cause the entire regex to fail.
    ('2016-02-20 12:00 - 2016-02-20 15:00 foo#bar@bar #t1 #t2,lorum_ipsum', {}),
    # Using a `` #`` will cause the regex to understand it as a tag.
    ('2016-02-20 12:00 - 2016-02-20 15:00 foo #bar@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '2016-02-20 12:00 - 2016-02-20 15:00 ',
      'activity': 'foo',
      'tags': ' #bar@bar #t1 #t2',
      'description': ',lorum_ipsum',
      }),
    ('a #b',
     {'tags': ' #b'}
     ),
    ('a #b@c',
     {'activity': 'a',
      'tags': ' #b@c',
      }),
    ('foo', {'activity': 'foo'}),
    ('foo@bar',
     {'activity': 'foo',
      'category': '@bar'
      }),
    ('@bar',
     {'category': '@bar'
      }),
    (' #t1',
     {'tags': ' #t1',
      }),
    (' #t1 #t2',
     {'tags': ' #t1 #t2',
      }),
    (' ##t1 #t#2',
     {'tags': ' ##t1 #t#2',
      }),
    (',lorum_ipsum',
     {'description': ',lorum_ipsum',
      }),
    # 'Malformed' raw fact strings
    ('2016-02-20 12:00 -  foo@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '2016-02-20 12:00 ',
      'activity': '-  foo',
      'category': '@bar',
      'tags': ' #t1 #t2',
      'description': ',lorum_ipsum',
      }),
    # Invalid
    ('2016-02-20 12:00-2016-02-20 15:00 foo@bar #t1 #t2,lorum_ipsum', {}),
    ('2016-02-20 12:00-2016-02-20 15:00 foo#t1@bar #t1 #t2,lorum_ipsum', {}),
    ('2016-02-20 12:00-2016-02-20 15:00 foo,blub@bar #t1 #t2,lorum_ipsum', {}),
    ('2016-02-20 12:00-2016-02-20 15:00 foo:blub@bar #t1 #t2,lorum_ipsum', {}),
])
def test_decompose_raw_fact_string(request, text, expectation):
    result = helpers.decompose_raw_fact_string(text)
    if expectation:
        for key, value in expectation.items():
            assert result[key] == value
    else:
        assert result is None


@pytest.mark.parametrize(('minutes', 'expectation'), (
    (1, '1 min'),
    (30, '30 min'),
    (59, '59 min'),
    (60, '01:00'),
    (300, '05:00'),
))
def test__get_delta_string(minutes, expectation):
    delta = datetime.timedelta(minutes=minutes)
    result = helpers.get_delta_string(delta)
    assert result == expectation


class TestSerializeActivity(object):
    """Unit tests for `serialize_activity` helper function."""

    #@pytest.mark.parametrize('seperator', (
    def test_with_category(self, activity):
        """Make sure that the serialized activity matches expectations."""
        result = helpers.serialize_activity(activity)
        assert result == '{s.name}@{s.category.name}'.format(s=activity)

    @pytest.mark.parametrize('activity__category', (None,))
    def test_without_category(self, activity):
        """Make sure that the serialized activity matches expectations."""
        result = helpers.serialize_activity(activity)
        assert result == '{s.name}'.format(s=activity)

    @pytest.mark.parametrize('separator', (';', '/', '%'))
    def test_seperators(self, activity, separator):
        """Make sure that the serialized activity matches expectations."""
        result = helpers.serialize_activity(activity, separator)
        assert result == '{s.name}{seperator}{s.category.name}'.format(s=activity,
            seperator=separator)
