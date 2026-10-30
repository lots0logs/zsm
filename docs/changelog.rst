Changelog
=========

1.0 (lots0logs fork)
-------------------

- Include the empty command output fix from upstream PR #1.
- Isolate snapshot discovery from child datasets.
- Add opt-in clock-aligned scheduling and fix exact elapsed-time boundaries.
- Document scheduling, retention, downtime, and local clock behavior.
- Support and test Python 3.10 through 3.14 with updated dependencies.
- Publish tested wheel and source artifacts through GitHub Releases only,
  using plain version tags without a leading v.

0.4.0
-----

Fix logic for destroying snapshots, so it handles multiple older ones.
This is especially relevant when zsm has not been run for a while,
and there is a backlog of very old snapshots lying around.

Drop support for Python 3.6.
Add support for Python 3.10.

0.3.0
-----

Move library code from zsm-lib into zsm.

Remove dependency on sarge.

Update dependencies to newer versions.

Update project config files to more modern patterns.

0.2.1
-----

Update requirements to newer versions.

Fix crash in _deserialize after upgrading to marshmallow 3.

0.2.0
-----

Start including tests in source packages.

Snapshot config field ``name`` renamed to ``label``,
to avoid confusion with the actual ZFS snapshot name.
Also improved validation.

Snapshot config field ``delta`` renamed to ``frequency``,
because it makes more sense grammatically.
Also changed implementation from simple dict to complex string.
See :doc:`quickstart` and :doc:`config` for more information.

Fix bug where it would incorrectly find and manage snapshots
where the label was only a partial match.
Add regression test to detect this bug.

Start including tests in source packages.

Improve test coverage.

0.1.0
-----

Initial release.

Add commands:

- ``cron``
- ``validate-config``
- ``version``
