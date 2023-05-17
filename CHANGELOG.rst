=========
Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project adheres to `Semantic Versioning`_.

`Unreleased`_
-------------

Added
^^^^^
* Allow adding the return type in statements
* Allow setting a custom path for a language

Changed
^^^^^^^
* Don't show the title line if the title is missing
* Create the required files if they don't exist
* Have a single source of truth for the language name

`0.7.0`_ - 2023-05-16
---------------------
Added
^^^^^
* Allow showing solution hints

Changed
^^^^^^^
* Use toml files to store statements

`0.6.0`_ - 2023-05-15
---------------------
Changed
^^^^^^^
* Delay failure for all runs

`0.5.0`_ - 2023-05-15
---------------------
Changed
^^^^^^^
* Runner should return "Time <response_id> <timing in nanoseconds>" for timings
* Runner should return "Answer <response_id> <answer>" for runs

`0.4.0`_ - 2023-05-12
---------------------
Removed
^^^^^^^
* Drop benchmark subcommand, as it can be done via timing
* Drop update subcommand, as it can be done via timing
* Drop test subcommand, as it can be done via running


`0.3.0`_ - 2023-05-11
---------------------
Added
^^^^^
* Allow debugging runs
* Delay failing runs

`0.2.0`_ - 2023-05-09
---------------------
Added
^^^^^
* Allow formatting a problem name

`0.1.0`_ - 2023-05-09
---------------------
Added
^^^^^
* Allow running problems
* Allow testing problems
* Allow timing problems
* Allow benchmarking a language
* Allow updating problem timings
* Allow showing problem statements
* Allow generating solutions from a template


.. _`unreleased`: https://github.com/spapanik/eulertools/compare/v0.7.0...main
.. _`0.7.0`: https://github.com/spapanik/yamk/compare/v0.6.0...v0.7.0
.. _`0.6.0`: https://github.com/spapanik/yamk/compare/v0.5.0...v0.6.0
.. _`0.5.0`: https://github.com/spapanik/yamk/compare/v0.4.0...v0.5.0
.. _`0.4.0`: https://github.com/spapanik/yamk/compare/v0.3.0...v0.4.0
.. _`0.3.0`: https://github.com/spapanik/yamk/compare/v0.2.0...v0.3.0
.. _`0.2.0`: https://github.com/spapanik/yamk/compare/v0.1.0...v0.2.0
.. _`0.1.0`: https://github.com/spapanik/yamk/releases/tag/v0.1.0

.. _`Keep a Changelog`: https://keepachangelog.com/en/1.0.0/
.. _`Semantic Versioning`: https://semver.org/spec/v2.0.0.html
