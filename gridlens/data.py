"""Data validation and the explicitly synthetic demo data.

One row = one completed hour; energy_kwh is energy consumed during that hour.
Timezone-naive timestamps are treated as local clock readings, not UTC.
"""

from __future__ import annotations

import io
import numpy as np
import pandas as pd

MAX_UPLOAD_BYTES = 4 * 1024 * 1024
MAX_ROWS = 30_000
MIN_ROWS = 24 * 24  # enough history for 168-hour lags plus train/test windows


class DataError(ValueError):
    """An issue that a user can resolve by fixing the input CSV."""


def demo_data() -> pd.DataFrame:
    """Create a repeatable *fictional* facility load curve, not utility measurements."""
    index = pd.date_range('2025-09-01 00:00', periods=24 * 120, freq='h')
    rng = np.random.default_rng(19)
    hour = index.hour.to_numpy()
    weekday = index.dayofweek.to_numpy()
    day_num = np.arange(len(index)) / 24

    # A plausible illustrative office/industrial mix, deliberately not a grid model.
    office_hours = 14 * ((hour >= 7) & (hour <= 18)).astype(float)
    evening = 4 * np.exp(-0.5 * ((hour - 19) / 3.0) ** 2)
    weekend = np.where(weekday >= 5, -10, 0)
    weekly_wave = 2.6 * np.sin(2 * np.pi * day_num / 7)
    seasonal = 2.8 * np.cos(2 * np.pi * day_num / 60)
    trend = 0.035 * day_num
    noise = rng.normal(0, 1.8, len(index))
    load = np.maximum(5, 33 + office_hours + evening + weekend + weekly_wave + seasonal + trend + noise)
    return pd.DataFrame({'timestamp': index, 'energy_kwh': np.round(load, 3)})


def validate_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate a continuous hourly series; never silently interpolate missing data."""
    required = {'timestamp', 'energy_kwh'}
    if not required.issubset(frame.columns):
        raise DataError('CSV needs exactly these columns at minimum: timestamp, energy_kwh.')
    if len(frame) > MAX_ROWS:
        raise DataError(f'Too many records; limit the file to {MAX_ROWS:,} hourly rows.')
    if len(frame) < MIN_ROWS:
        raise DataError('At least 24 days (576 hourly rows) are needed for forecasting.')

    result = frame[['timestamp', 'energy_kwh']].copy()
    try:
        result['timestamp'] = pd.to_datetime(result['timestamp'], errors='raise')
    except (ValueError, TypeError) as exc:
        raise DataError('Invalid timestamp. Use YYYY-MM-DD HH:MM:SS.') from exc
    if result['timestamp'].dt.tz is not None:
        # Normalize a supplied offset while retaining a consistent naive UTC index.
        result['timestamp'] = result['timestamp'].dt.tz_convert('UTC').dt.tz_localize(None)
    if result['timestamp'].isna().any():
        raise DataError('The timestamp column contains missing values.')
    try:
        result['energy_kwh'] = pd.to_numeric(result['energy_kwh'], errors='raise')
    except (ValueError, TypeError) as exc:
        raise DataError('energy_kwh must contain numeric values.') from exc
    if (~np.isfinite(result['energy_kwh'].to_numpy())).any():
        raise DataError('energy_kwh cannot contain missing or infinite values.')
    if (result['energy_kwh'] < 0).any():
        raise DataError('energy_kwh cannot be negative.')
    result = result.sort_values('timestamp', kind='stable').reset_index(drop=True)
    if result['timestamp'].duplicated().any():
        raise DataError('Duplicate timestamps found. Keep one reading per hour.')
    diffs = result['timestamp'].diff().dropna()
    if not (diffs == pd.Timedelta(hours=1)).all():
        raise DataError('The series must contain one reading every hour, without gaps. '
                        'Choose a contiguous period and check daylight-saving transitions.')
    return result


def parse_upload(raw: bytes) -> pd.DataFrame:
    if len(raw) > MAX_UPLOAD_BYTES:
        raise DataError('File is too large (maximum 4 MB).')
    if not raw:
        raise DataError('The uploaded file is empty.')
    try:
        frame = pd.read_csv(io.BytesIO(raw), encoding='utf-8-sig')
    except (UnicodeError, pd.errors.ParserError, ValueError) as exc:
        raise DataError('Could not read the CSV. Save a UTF-8, comma-separated file.') from exc
    return validate_frame(frame)


def overview(frame: pd.DataFrame, label: str) -> dict:
    dates = frame['timestamp']
    energy = frame['energy_kwh']
    daily = frame.assign(day=dates.dt.date).groupby('day', sort=True)['energy_kwh'].sum()
    by_hour = frame.assign(hour=dates.dt.hour).groupby('hour')['energy_kwh'].mean()
    by_weekday = frame.assign(weekday=dates.dt.dayofweek).groupby('weekday')['energy_kwh'].mean()
    recent = daily.iloc[-90:]

    return {
        'label': label,
        'start': dates.iloc[0].isoformat(),
        'end': dates.iloc[-1].isoformat(),
        'hours': int(len(frame)),
        'days': round(len(frame) / 24, 1),
        'total_mwh': round(float(energy.sum()) / 1000, 2),
        'mean_kw': round(float(energy.mean()), 2),
        'peak_kw': round(float(energy.max()), 2),
        'peak_at': dates.iloc[int(energy.to_numpy().argmax())].isoformat(),
        'daily': [{'date': str(d), 'kwh': round(float(v), 2)} for d, v in recent.items()],
        'hourly_profile': [{'hour': int(h), 'kw': round(float(v), 2)} for h, v in by_hour.items()],
        'weekday_profile': [{'weekday': int(d), 'kw': round(float(v), 2)} for d, v in by_weekday.items()],
        'recent_hourly': [
            {'timestamp': row.timestamp.isoformat(), 'kwh': float(row.energy_kwh)}
            for row in frame.tail(96).itertuples(index=False)
        ],
    }
