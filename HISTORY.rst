.. :changelog:

History
========

0.11.0 (2016-10-03)
--------------------
- Config changes are now applied at runtime (Fixes: #57).
- ``PreferencesDialog`` and its widgets moved to seperate sub-package (PR: #83).
- ``facts_changed`` Signal has been renamed to ``facts-changed`` (Fixes: #51).
- ``Overview._charts`` gets destroyed on ``refresh`` (Closes: #106).
- *Show more* button in overview is inactive if there are no facts at all (Closes: #105).
- Improved contrast for ``date colour`` in overview with dark themes (Closes: #93).
- ``hamster_gtk.misc.dialogs`` has been split into multiple sub-modules (Closes: #96).
- Test setup makes use of ``xvfb`` (Closes: #95).
- ``tox`` tests against ``python3`` instead more specific python 3 versions (PR: #92).
- Add new helper function ``hamster_gtk.helpers.get_parent_window`` (Closes: #60).
- Fix ``EditDialog`` for uncategoriezed facts (Closes: #59).
- Replace GTK stock buttons with generic label buttons (Closes: #46).
- Escape values inserted as markup (Closes: #78).
- Move CSS into seperate file (Closes: #4).
- Add new function ``hamster_gtk.helpers.get_resource_path`` (PR: #81).
- Add basic ``AboutDialog`` (Closes: #17).
- Minor fixes and refinements.


0.10.0 (2016-07-21)
---------------------
* First release on PyPI.
