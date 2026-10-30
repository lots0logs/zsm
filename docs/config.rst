Configuration file
==================

The config file is a YAML file where the top level object is a mapping.

Fields
------

- ``snapshots`` (List of mappings) - Define what snapshots to take.

  - ``dataset`` (String) - Name of an existing dataset, including pool name. |br|
    Example: ``tank/data``.
  - ``label`` (String) - Descriptive short name, typically describing the frequency. |br|
    Examples: ``daily``, ``weekly``, ``every-2-minutes``.
  - ``frequency`` (String) - Define how often the snapshot should be taken. |br|
    Can contain multiple values consisting of a number and a unit. |br|
    Supported units are ``weeks``, ``days``, ``hours``, ``minutes``, ``seconds``,
    including various abbreviations like ``w``, ``d``, ``h``, ``min``, ``sec``. |br|
    Examples: ``2w``, ``3d 12h``, ``2Weeks3DAYS 5h,3mins,2secs``.
  - ``schedule`` (String, optional) - ``elapsed`` (default) or ``clock``. |br|
    Elapsed scheduling creates a snapshot when its age reaches ``frequency``.
    Clock scheduling creates one snapshot per fixed local wall-clock interval,
    independent of the seconds at which cron or ZFS finishes running.
  - ``retention`` (Integer) - Number of old snapshots to keep. |br|
    Example: ``12``.

.. |br| raw:: html

   <br />

Clock-aligned scheduling
------------------------

For example, use ``frequency: "15min"`` and ``schedule: "clock"`` with a
quarter-hour cron job to take snapshots in the :00, :15, :30 and :45 slots.
Use ``frequency: "1h"`` for hourly slots, ``1d`` for midnight boundaries,
and ``1w`` for Sunday midnight boundaries. Intervals are anchored to local
midnight on Sunday, January 4, 1970; other durations use that same anchor.
The frequency must be positive.

A run creates a snapshot only if the latest snapshot belongs to an earlier
slot. Repeated runs within a slot do not create duplicates. After downtime,
only the current slot is captured; missed snapshots cannot be recreated.
The actual run time is recorded in the snapshot name, using the same timestamp
as the scheduling decision. Existing snapshots participate without renaming.

This is local wall-clock scheduling: the repeated hour when clocks move back
is treated as the same slot, and clock jumps forward do not backfill slots.
Cron must still run at least as often as the desired snapshot interval.

Labels remain independent: a frequent and an hourly rule may both create
snapshots at :00. Clock alignment does not select or promote retention tiers.
Pruning still uses actual snapshot age and ``frequency * retention``; it is
unchanged by the scheduling mode. Existing configurations default to elapsed
scheduling, including exact-interval equality (previously skipped).
