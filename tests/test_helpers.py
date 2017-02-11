# -*- coding: utf-8 -*-

import os.path

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


def test_get_resource_path(request, file_path):
    """Make sure the path to the resource is correct."""
    path = helpers.get_resource_path(file_path)
    expected = os.path.join(os.path.dirname(helpers.__file__), 'resources', file_path)
    assert path == expected


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
      'activity': ',lorum_ipsum',
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
    ('2016-02-20 12:00 - 2016-02-20 15:00 foo,bar@bar #t1 #t2,lorum_ipsum',
     {'timeinfo': '2016-02-20 12:00 - 2016-02-20 15:00 ',
      'activity': 'foo,bar',
      'category': '@bar',
      'tags': ' #t1 #t2',
      'description': ',lorum_ipsum',
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
     {'activity': ',lorum_ipsum',
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
