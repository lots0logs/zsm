import datetime
from unittest import mock

import freezegun
import pytest

import zsm.manage
import zsm.zfs


def test_get_snapshots_finds_correct_items():
    label = "abc"
    valid_names = ["zsm_abc_11", "zsm_abc_22"]
    invalid_names = [
        "zsm_xyz_11",  # Wrong label.
        "zsm_abcc_11",  # Label is only partial match.
        "xyz_abc_11",  # Right pattern, but wrong prefix.
        "abc",  # Wrong prefix, and not enough parts.
        "zsm",  # Right prefix, but not enough parts.
        "zsm_abc_11_lol",  # Right prefix, and right label, but too many parts.
        "",  # Empty string should not even be possible to get.
    ]
    names = valid_names + invalid_names

    dataset = mock.MagicMock()

    with mock.patch(
        "zsm.zfs.get_snapshots",
        return_value=[zsm.zfs.Snapshot(dataset=dataset, name=name) for name in names],
    ):
        snapshots = zsm.manage.get_snapshots(dataset=dataset, label=label)

    # Assert that result only contains snapshots with valid names.
    assert snapshots == [
        zsm.zfs.Snapshot(dataset=dataset, name=name) for name in valid_names
    ]


def test_create_snaphot_calls_zfs_create_snapshot():
    dataset = mock.MagicMock()

    with mock.patch("zsm.zfs.create_snapshot") as mock_create_snapshot:
        zsm.manage.create_snapshot(dataset=dataset, label="asdf")

    assert mock_create_snapshot.called


def test_parse_snapshot_returns_correct_parts():
    expected_label = "daily"
    expected_timestamp = datetime.datetime.now()
    formatted_expected_timestamp = expected_timestamp.strftime(
        zsm.manage.SNAPSHOT_TIMESTAMP_FORMAT
    )

    label, timestamp = zsm.manage.parse_snapshot(
        snapshot=zsm.zfs.Snapshot(
            dataset=mock.MagicMock(),
            name=zsm.manage.SNAPSHOT_DELIMITER.join(
                [
                    zsm.manage.SNAPSHOT_PREFIX,
                    expected_label,
                    formatted_expected_timestamp,
                ]
            ),
        )
    )

    # Round down microseconds, because that is not stored in the snapshot name.
    expected_timestamp = expected_timestamp.replace(microsecond=0)

    assert label == expected_label
    assert timestamp == expected_timestamp


dataset = zsm.zfs.Dataset(name="tank/data")


@mock.patch("zsm.zfs.create_snapshot")
@mock.patch("zsm.zfs.destroy_snapshot")
@mock.patch(
    "zsm.zfs.get_snapshots",
    return_value=[
        zsm.zfs.Snapshot(dataset=dataset, name="zsm_often_2022-03-05T11:59:00"),
        zsm.zfs.Snapshot(dataset=dataset, name="zsm_often_2022-03-05T11:09:00"),
        zsm.zfs.Snapshot(dataset=dataset, name="zsm_often_2022-03-05T11:19:00"),
        zsm.zfs.Snapshot(dataset=dataset, name="zsm_often_2022-03-05T11:29:00"),
        zsm.zfs.Snapshot(dataset=dataset, name="zsm_often_2022-03-05T11:39:00"),
    ],
)
@freezegun.freeze_time("2022-03-05 11:45:00")
def test_manage_snapshots_calls_zfs_create_and_destroy(
    mocked_zfs_get_snapshots,
    mocked_zfs_destroy_snapshot,
    mocked_zfs_create_snapshot,
):
    config = dict(
        snapshots=[
            dict(
                dataset=dataset,
                label="often",
                frequency=datetime.timedelta(minutes=10),
                retention=5,
            )
        ]
    )

    zsm.manage.manage_snapshots(
        config=config,
        now=datetime.datetime(2022, 3, 5, 12, 11, 00),
        dry_run=False,
    )

    assert mocked_zfs_create_snapshot.call_args_list == [
        mock.call(
            dataset=dataset,
            name="zsm_often_2022-03-05T11:45:00",
        )
    ]
    assert mocked_zfs_destroy_snapshot.call_args_list == [
        mock.call(
            snapshot=zsm.zfs.Snapshot(
                dataset=dataset,
                name="zsm_often_2022-03-05T11:09:00",
            )
        ),
        mock.call(
            snapshot=zsm.zfs.Snapshot(
                dataset=dataset,
                name="zsm_often_2022-03-05T11:19:00",
            )
        ),
    ]
    assert mocked_zfs_get_snapshots.called


@mock.patch("zsm.manage.create_snapshot")
@mock.patch("zsm.manage.get_snapshots")
def test_elapsed_creates_at_exact_frequency(get_snapshots, create):
    get_snapshots.return_value = [
        zsm.zfs.Snapshot(dataset, "zsm_hourly_2026-10-30T12:00:02")
    ]
    zsm.manage.create_snapshots(
        datetime.datetime(2026, 10, 30, 13, 0, 2),
        dataset,
        "hourly",
        datetime.timedelta(hours=1),
        False,
    )
    create.assert_called_once_with(dataset=dataset, label="hourly")


@mock.patch("zsm.zfs.create_snapshot")
@mock.patch("zsm.manage.get_snapshots")
def test_clock_creates_despite_negative_second_jitter(get_snapshots, create):
    get_snapshots.return_value = [
        zsm.zfs.Snapshot(dataset, "zsm_frequent_2026-10-30T12:00:02")
    ]
    now = datetime.datetime(2026, 10, 30, 12, 15, 1)
    zsm.manage.create_snapshots(
        now,
        dataset,
        "frequent",
        datetime.timedelta(minutes=15),
        False,
        schedule="clock",
    )
    create.assert_called_once_with(
        dataset=dataset, name="zsm_frequent_2026-10-30T12:15:01"
    )


@mock.patch("zsm.manage.create_snapshot")
@mock.patch("zsm.manage.get_snapshots")
def test_clock_skips_repeated_run_in_same_slot(get_snapshots, create):
    get_snapshots.return_value = [
        zsm.zfs.Snapshot(dataset, "zsm_hourly_2026-10-30T12:00:02")
    ]
    zsm.manage.create_snapshots(
        datetime.datetime(2026, 10, 30, 12, 59, 59),
        dataset,
        "hourly",
        datetime.timedelta(hours=1),
        False,
        schedule="clock",
    )
    create.assert_not_called()


@pytest.mark.parametrize(
    "latest, now, frequency, expected",
    [
        ("2026-10-30T12:00:02", "2026-10-30T13:00:01", 3600, True),
        ("2026-10-30T23:59:59", "2026-10-31T00:00:01", 86400, True),
        ("2026-10-31T23:59:59", "2026-11-01T00:00:01", 604800, True),
        ("2026-10-27T12:00:00", "2026-10-30T13:00:00", 900, True),
        ("2026-10-30T13:00:00", "2026-10-30T12:00:00", 900, False),
        ("2026-10-30T12:15:01", "2026-10-30T12:16:00", 900, False),
    ],
)
def test_clock_boundaries_and_downtime(latest, now, frequency, expected):
    snapshots = [zsm.zfs.Snapshot(dataset, "zsm_test_" + latest)]
    with (
        mock.patch("zsm.manage.get_snapshots", return_value=snapshots),
        mock.patch("zsm.manage.create_snapshot") as create,
    ):
        zsm.manage.create_snapshots(
            datetime.datetime.strptime(now, zsm.manage.SNAPSHOT_TIMESTAMP_FORMAT),
            dataset,
            "test",
            datetime.timedelta(seconds=frequency),
            False,
            schedule="clock",
        )
    assert create.call_count == int(expected)


@pytest.mark.parametrize("dry_run", [True, False])
def test_clock_first_snapshot_and_dry_run(dry_run):
    now = datetime.datetime(2026, 10, 30, 12, 15, 1)
    with (
        mock.patch("zsm.manage.get_snapshots", return_value=[]),
        mock.patch("zsm.manage.create_snapshot") as create,
    ):
        zsm.manage.create_snapshots(
            now,
            dataset,
            "test",
            datetime.timedelta(minutes=15),
            dry_run,
            schedule="clock",
        )
    if dry_run:
        create.assert_not_called()
    else:
        create.assert_called_once_with(dataset=dataset, label="test", now=now)


def test_manage_passes_clock_schedule():
    config = {
        "snapshots": [
            {
                "dataset": dataset,
                "label": "test",
                "frequency": datetime.timedelta(hours=1),
                "retention": 12,
                "schedule": "clock",
            }
        ]
    }
    now = datetime.datetime(2026, 10, 30, 13)
    with (
        mock.patch("zsm.manage.create_snapshots") as create,
        mock.patch("zsm.manage.destroy_snapshots"),
    ):
        zsm.manage.manage_snapshots(config, now, True)
    assert create.call_args[1]["schedule"] == "clock"
