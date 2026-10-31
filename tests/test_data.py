import io
import pandas as pd
import pytest

from gridlens.data import DataError, demo_data, overview, parse_upload, validate_frame


def test_demo_is_repeatable_and_hourly():
    first = demo_data()
    second = demo_data()
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 120 * 24
    pd.testing.assert_frame_equal(first, validate_frame(first))


def test_stats_have_correct_units_and_ranges():
    report = overview(demo_data(), 'Demo')
    assert report['hours'] == 120 * 24
    assert report['total_mwh'] > 0
    assert report['peak_kw'] >= report['mean_kw']
    assert len(report['hourly_profile']) == 24
    assert len(report['weekday_profile']) == 7


def test_duplicate_and_missing_hours_rejected():
    data = demo_data()
    with pytest.raises(DataError, match='Duplicate'):
        validate_frame(pd.concat([data, data.iloc[[0]]], ignore_index=True))
    with pytest.raises(DataError, match='without gaps'):
        validate_frame(data.drop(index=10))


def test_bad_energy_rejected():
    data = demo_data()
    data.loc[3,'energy_kwh'] = -1
    with pytest.raises(DataError, match='negative'):
        validate_frame(data)


def test_csv_round_trip():
    csv = demo_data().to_csv(index=False).encode()
    actual = parse_upload(csv)
    assert len(actual)==2880
    assert actual.energy_kwh.iloc[100] > 0


def test_missing_columns_reported():
    with pytest.raises(DataError, match='timestamp, energy_kwh'):
        parse_upload(b'when,power\n2025-01-01,4.0\n')
