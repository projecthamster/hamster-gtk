# -*- encoding: utf-8 -*-


# This file is part of 'hamster-gtk'.
#
# 'hamster-gtk' is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# 'hamster-gtk' is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with 'hamster-gtk'.  If not, see <http://www.gnu.org/licenses/>.


"""General purpose helper methods."""

from __future__ import absolute_import, unicode_literals

import datetime
import operator
import re
from gettext import gettext as _

import six
from orderedset import OrderedSet
from six import text_type


def _u(string):
    """
    Return passed string as a text instance.

    This helper is particularly useful to wrap Gtk 'string return values' as
    they depend on the used python version. On python 2 Gtk will return utf-8
    encoded bytestrings while on python 3 it will return 'unicode strings'.

    The reason we have to use this and not ``six.u`` is that six does not make
    assumptions about the encoding and hence can not be used to safely decode
    non ascii bytestrings into unicode.

    Args:
        string (str): A string instance. On ``py2`` this will be a bytestring,
            on ``py3`` a 'unicode string'.

    Returns:
        text_type: Returns a 'unicode text type'. Under ``py2`` that means a
        ``unicode`` instance, under ``py3`` this will be a ``str`` instance.
    """
    if six.PY2:
        return string.decode('utf-8')
    else:
        return string


def show_error(parent, error, message=None):
    """
    Display an error dialog.

    Besides the clients own error reporting this is suitable to present backend
    errors to the user instead of failing silently.

    This functions runs the dialog a modal and takes care of its destruction afterwards.

    Args:
        parent (Gtk.Window): Parrent window.
        error (str): Exception message.
        message (str, optional): User friendly error message providing some broad context.

    Returns:
        None
    """
    # We can not import this on a global level due to circular imports.
    from .misc import ErrorDialog

    if not message:
        message = error
    dialog = ErrorDialog(parent, message)
    dialog.run()
    dialog.destroy()


def clear_children(widget):
    """
    Remove and destroy all children from a widget.

    It seems GTK really does not have this build in. Iterating over all
    seems a bit blunt, but seems to be the way to do this.
    """
    # [TODO]
    # Replace with Gtk.Container.foreach()?
    for child in widget.get_children():
        child.destroy()
    return widget


def get_parent_window(widget):
    """
    Reliably determine parent window of a widget.

    Just using :meth:`Gtk.Widget.get_toplevel` would return the widget itself
    if it had no parent window.

    On the other hand using :meth:`Gtk.Widget.get_ancestor` would return only
    the closest :class:`Gtk.Window` in the hierarchy.

    https://developer.gnome.org/gtk3/unstable/GtkWidget.html#gtk-widget-get-toplevel
    """
    toplevel = widget.get_toplevel()
    if not toplevel.is_toplevel():
        toplevel = None

    return toplevel


def calendar_date_to_datetime(date):
    """Convert :meth:`Gtk.Calendar.get_date` value to :class:`datetime.date`."""
    year, month, day = date
    return datetime.date(int(year), int(month) + 1, int(day))


def decompose_raw_fact_string(text, raw=False):
    """
    Try to match a given string with modular regex groups.

    Args:
        text (text_type): String to be analysed.
        raw (bool): If ``True``, return the raw match instance, if ``False`` return
            its corresponding ``groupdict``.

    Returns:
        re.MatchObject or dict: ``re.MatchObject`` if ``raw=True``, else ``dict``.
            Returning the ``re.MatchObject`` is particularly useful if one is
            interested in the groups ``span``s.

    Note:
        This is not at all about providing valid facts or even raw facts. This function
        is only trying to extract whatever information can be matched to its various
        groups (aka 'segments').
        Nevertheless, this can be the basis for future implementations
        that replace ``Fact.create_from_raw_string`` with a regex based approach.
    """
    time_regex = r'([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]'
    # Whilst we do not really want to do sanity checks here being as specific as
    # possible will enhance matching accuracy.
    relative_time_regex = r'-\d{1,3}'
    date_regex = r'20[0-9][0-9]-[0-1][0-9]-[0-3][0-9]'
    datetime_regex = r'({date}|{time}|{date} {time})'.format(date=date_regex, time=time_regex)
    # Please note the trailing whitespace!
    timeinfo_regex = r'({relative} |{datetime} |{datetime} - {datetime} )'.format(
        datetime=datetime_regex,
        relative=relative_time_regex
    )
    # This is the central place where we define which characters are viable for
    # our various segments.
    # Please note that this is also where we define each segments 'separator'.
    activity_regex = r'[^@:#,]+'
    category_regex = r'@[^@,#]+'
    tag_regex = r' (#[^,]+)'
    description_regex = r',.+'

    regex = (
        r'^(?P<timeinfo>{timeinfo})?(?P<activity>{activity})?(?P<category>{category})?'
        '(?P<tags>({tag})*)(?P<description>{description})?$'.format(
            timeinfo=timeinfo_regex,
            activity=activity_regex,
            category=category_regex,
            tag=tag_regex,
            description=description_regex,
        )
    )

    pattern = re.compile(regex, re.UNICODE)
    match = pattern.match(text)
    result = match
    if match and not raw:
        result = match.groupdict()
    return result


# [TODO]
# Once LIB-251 has been fixed this should no longer be needed.
def get_recent_activities(controller, start, end):
    """Return a list of all activities logged in facts within the given timeframe."""
    # [FIXME]
    # This manual sorting within python is of course less than optimal. We stick
    # with it for now as this is just a preliminary workaround helper anyway and
    # effective sorting will need to be implemented by the storage backend in
    # ``hamster-lib``.
    facts = sorted(controller.facts.get_all(start=start, end=end),
        key=operator.attrgetter('start'), reverse=True)
    recent_activities = [fact.activity for fact in facts]
    return OrderedSet(recent_activities)


def serialize_activity(activity, separator='@'):
    """
    Provide a serialized string version of an activity.

    Args:
        activity (Activity): ``Activity`` instance to serialize.
        separator (str, optional): ``string`` used to separate ``activity.name`` and
            ``category.name``. The separator will be omitted if
            ``activity.category=None``. Defaults to ``@``.

    Returns:
        str: A string representation of the passed activity.
    """
    if not separator:
        raise ValueError(_("No valid separator has been provided."))

    category_text = None

    if activity.category:
        category_text = activity.category.name

    if category_text:
        result = '{activity_text}{separator}{category_text}'.format(activity_text=activity.name,
            category_text=category_text, separator=separator)
    else:
        result = activity.name
    return text_type(result)


def get_delta_string(delta):
    """
    Return a human readable representation of ``datetime.timedelta`` instance.

    In most contexts it is not that useful to present the delta in seconds.
    Instead we return the delta either in minutes or ``hours:minutes`` depending on the
    value.

    Args:
        delta (datetime.timedelta): The timedelta instance to render.

    Returns:
        text_type: The datetime instance rendered as text.

    Note:
        So far, this does not account for large deltas that span days and more.
    """
    seconds = delta.total_seconds()
    minutes = int(seconds / 60)
    if minutes < 60:
        result = '{} min'.format(minutes)
    else:
        result = '{hours:02d}:{minutes:02d}'.format(
            hours=int(seconds / 3600), minutes=int((seconds % 3600) / 60))
    return text_type(result)


def rgb_to_gtk_rgb(r, g, b):
    """Map '255' based RGB values to 0-1 based floats expected by cairo."""
    return float(r) / 255, float(g) / 255, float(b) / 255
