=============
Build Process
=============

``hamster-gtk`` provides an easy to use ``dist`` make target that allows easy
creation of binary (wheel) and source distribution packages.

One thing to be aware of with regards to this process is that
``hamster_gtk/resources`` houses non-python data required by the package. This
is mainly auxiliary data (css, menu definitions, etc) required by GTK best
practices. In order to avoid having to manage the distribution of those
individual files we follow GTKs recommendation and create a dedicated
``GResource`` file that contains all those extra files. This can be done
manually with the ``make resources`` target and will also be triggered  just
before the ``dist`` target. It is worth noting that the original “data
source code” itself is not part of the package itself. Only
``hamster-gtk.gresource`` is actually shipped! On the other hand, it is also
for this reason that ``hamster-gtk.gresource`` is not part of the code
repository as it only ever is needed as part of the package creation process.

Caveat when testing
-------------------

Depending on your particular test setup, that is if you do not run the test
suite against the actual package, but against the local source itself you will
need to create ``hamster-gtk.gresource`` with ``make resources`` in order for
the codebase to work.
