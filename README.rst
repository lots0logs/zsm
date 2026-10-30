zsm — ZFS Snapshot Manager
==========================

Stable ZFS snapshot management for Linux and FreeBSD. This is the
``lots0logs/zsm`` fork of `thnee/zsm <https://github.com/thnee/zsm>`_,
maintained after years of use of the upstream package.

What changed from upstream
--------------------------

Version **1.0** includes:

- **Empty output handling:** an empty ZFS command result returns an empty list
  rather than a list containing an empty string, avoiding snapshot-list crashes.
  This includes the fix originally submitted in
  `upstream PR #1 <https://github.com/thnee/zsm/pull/1>`_.
- **Dataset isolation:** a dataset's snapshot list excludes child datasets.
  Parent and child datasets can safely use different retention policies.
- **Clock-aligned scheduling:** opt in with ``schedule: clock`` to capture one
  snapshot per fixed wall-clock slot. Quarter-hour snapshots no longer miss a
  slot because cron ran a second earlier than on its previous run.
- **Elapsed-time boundary fix:** the default elapsed schedule takes a snapshot
  when its age equals the interval, rather than waiting until it exceeds it.
- **Current Python support:** Python 3.10–3.14 is tested in CI. Packaging and test
  dependencies are updated, and the CLI no longer depends on ``pkg_resources``.
- **GitHub releases:** tested wheels and source archives are published here,
  with checksums. This fork is not published to PyPI. Release tags are plain
  versions such as ``1.0``, without a leading ``v``.

Existing configurations retain elapsed-time scheduling. Clock alignment is
opt-in, and retention remains based on snapshot age. Labels are still
independent: a frequent rule and an hourly rule can both create a snapshot at
:00. Selecting a single retention tier per boundary is not implemented.

Installing this fork
--------------------

Python 3.10 or newer and the ZFS command-line tools are required. Use an isolated
Python environment and point your system cron entry at that environment's
``zsm`` executable. For version 1.0::

    python3 -m venv /opt/zsm
    /opt/zsm/bin/python -m pip install https://github.com/lots0logs/zsm/releases/download/1.0/zsm-1.0-py3-none-any.whl
    /opt/zsm/bin/zsm version

Creating ``/opt/zsm`` may require administrator privileges. Installing ``zsm``
from PyPI or the FreeBSD package repository installs upstream, not this fork.
The Python import and executable names remain ``zsm``.

Clock-aligned example
---------------------

.. code-block:: yaml

    snapshots:
      - dataset: tank/home
        label: frequent
        frequency: 15min
        retention: 3
        schedule: clock
      - dataset: tank/home
        label: hourly
        frequency: 1h
        retention: 12
        schedule: clock

Run ``zsm cron`` every 15 minutes. A clock rule creates at most one snapshot
per interval and captures only the current slot after downtime. Day boundaries
are local midnight; week boundaries are Sunday midnight. Retention is unchanged:
``frequency * retention`` defines the maximum snapshot age, checked at each run.

See `configuration documentation <docs/config.rst>`_ and
`quickstart <docs/quickstart.rst>`_ for details. Daily and weekly rules are
configured separately; leave them out for short-lived workspace datasets.

Development and releases
------------------------

Run checks locally::

    python -m pip install '.[test,build]'
    python -m pytest --cov=zsm
    flake8 .
    black --check .
    isort --check .
    python -m build
    python -m twine check --strict dist/*

To release, update ``setup.py`` and the changelog on ``main``, then push a tag
whose name exactly matches the package version, for example ``1.0``.
``.github/workflows/release.yml`` runs the test matrix, verifies the tagged
commit is on ``main``, builds and validates both distributions, smoke-tests
the wheel, and creates a GitHub release with the wheel, source archive, and
``SHA256SUMS``. It does not publish to PyPI.

Upstream's BSD-2-Clause license and original author attribution are preserved.
