===============================
hamster-gtk
===============================

.. .. image:: https://img.shields.io/pypi/v/hamster-gtk.svg
        :target: https://pypi.python.org/pypi/hamster-gtk

.. image:: https://img.shields.io/travis/projecthamster/hamster-gtk.svg
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

First Steps
------------
* Install dependencies (on debian if using virtualenvwrapper):
  ``apt-get install virtualenvwrapper python-gi gir1.2-gtk-3.0 libglib2.0-dev libgtk-3-dev``.
  If you use python 3, you will need ``python3-gi`` instead.
* Create new virtual env: ``mkvirtualenv hamster-gtk``
* Activate env: ``workon hamster-gtk``
* Activate system site dirs: ``toggleglobalsitepackages``. Otherwise you will have no access
  to Gtk.
* Install ``hamster-gtk``: ``pip install hamster-gtk``.
* Run the little furball: ``hamster-gtk``

Some notes:
* Preference changes will only be applied at the next start right now.
* Exported data is tab seperated.
* This is pre-alpha software!

News: Version 0.10.0
----------------------
This is the first release of ``hamster-gtk``! As such it is just a first glimpse
of things to come and far from useable for end user needs. Whilst you should be able
to track, list and export your activities we do not take any responsibility for data
loss or curruption of any sort. What we *do* take however, are you bug reports and
feature requests.
Happy tracking; Eric.
`
