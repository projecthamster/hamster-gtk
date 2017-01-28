===============================
hamster-gtk
===============================

.. image:: https://img.shields.io/pypi/v/hamster-gtk.svg
        :target: https://pypi.python.org/pypi/hamster-gtk

.. image:: https://img.shields.io/travis/projecthamster/hamster-gtk/master.svg
        :target: https://travis-ci.org/projecthamster/hamster-gtk

.. .. image:: https://readthedocs.org/projects/hamster-gtk/badge/?version=latest
        :target: https://readthedocs.org/projects/hamster-gtk/?badge=latest
        :alt: Documentation Status


A GTK interface to the hamster time tracker.

**IMPORTANT**
At this early stage ``hamster-gtk`` is pre-alpha software. As such you are very
welcome to take it our for a spin and submit feedback, however you should not
rely on it to work properly and most certainly you should not use it in an
production environment!
You have been warned.

Dependencies
-------------

To Run the Testsuite
~~~~~~~~~~~~~~~~~~~~~
- make
- xvfb

First Steps
------------
* Install dependencies (on debian if using virtualenvwrapper):
  install virtualenvwrapper python-gi gir1.2-gtk-3.0 libglib2.0-dev
  libgtk-3-dev``.
  If you use python 3, you will need ``python3-gi`` instead.
* Create new virtual env: ``mkvirtualenv hamster-gtk``
* Activate env: ``workon hamster-gtk``
* Activate system site dirs: ``toggleglobalsitepackages``. Otherwise you will
  have no access to Gtk.
* Install ``hamster-gtk``: ``pip install hamster-gtk``.
* Run the little furball: ``hamster-gtk``

Some notes:

* Preference changes will only be applied at the next start right now.
* Exported data is tab separated.
* This is pre-alpha software!

How to run the testsuite
-------------------------
- Create a virtual environment ``mkvirtualenv hamster-gtk`` (python 2) or
  ``mkvirtualenv -p python3 hamster-gtk`` (python 3). Whilst those instructions
  do not reflect best practices (which would make use of python 3's built in
  venv) it does provide a better handling of ``system-site-packages``.
  `This issue <http://bugs.python.org/issue24875>`_ provides some context for
  the problems one may run into using ``system-site-packages`` with python3
  venvs. It is our hope that python 3.7 will fix this.
- enable access to system-site-packages for our virtual environment:
  ``$ toggleglobalsitepackages``. This is needed to access our global GTK
  related packages.
- Install development environment: ``make develop``.
- To run the actual testsuite: ``make test``.
- To run tests and some auxiliary style checks (flake8, pep257, etc):
  ``make test-all``.

Right now, our actual code testing does not utilize ``tox`` as we keep running
into segfaults (which does not happen without ``tox``).
For  this same reason we are currently unable to run our code tests on Travis
as well (we still run the 'style checks' at least).
We hope to get to the bottom of this at some point and would be most grateful
if you have any hint or pointer that may help tracking down this issue.

News: Version 0.11.0
----------------------
This release introduces refines various aspects of your *Hamster-GTK*
experience. Whilst we introduce no new major dialogs (just a simple
about-dialog). We catch up with the lastest version of ``hamster-lib``,
``0.12.0``. The most noteworthy change for user is probably the ability to use
whitespaces with your ``Activity.name``. Besides that we fixed some rather
anoying bugs as well as continued to refine the codebase. All in all, while
still not big on features, this release should feel much more stable and
reliable. This is not the least due to multiple contributions by ``jtojnar``,
thanks for that! As ususal, for more changes and details, please refer to the
changelog. Happy tracking; Eric.
