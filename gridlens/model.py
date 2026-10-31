"""Simple, explainable day-ahead load forecasts.

The key design choice: the newest feature for time t is t-24h. At the end
of today, we can therefore calculate every feature for tomorrow's 24 hours.
The chronological holdout simulates day-ahead prediction (not random splits).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .data import DataError

FEATURES = [
    'lag_24', 'lag_48', 'lag_168', 'previous_day_mean', 'previous_week_mean',
    'hour_sin', 'hour_cos', 'dow_sin', 'dow_cos', 'month_sin', 'month_cos',
    'is_weekend',
]


def feature_table(frame: pd.DataFrame) -> pd.DataFrame:
    ts = frame['timestamp']
    values = frame['energy_kwh']
    result = pd.DataFrame({
        'timestamp': ts,
        'actual': values,
        'lag_24': values.shift(24),
        'lag_48': values.shift(48),
        'lag_168': values.shift(168),
        'previous_day_mean': values.shift(24).rolling(24).mean(),
        'previous_week_mean': values.shift(24).rolling(168).mean(),
        'hour_sin': np.sin(2 * np.pi * ts.dt.hour / 24),
        'hour_cos': np.cos(2 * np.pi * ts.dt.hour / 24),
        'dow_sin': np.sin(2 * np.pi * ts.dt.dayofweek / 7),
        'dow_cos': np.cos(2 * np.pi * ts.dt.dayofweek / 7),
        'month_sin': np.sin(2 * np.pi * ts.dt.month / 12),
        'month_cos': np.cos(2 * np.pi * ts.dt.month / 12),
        'is_weekend': (ts.dt.dayofweek >= 5).astype(int),
    })
    return result.dropna().reset_index(drop=True)


def _estimator(model_name: str):
    if model_name == 'ridge':
        return make_pipeline(StandardScaler(), Ridge(alpha=25.0))
    if model_name == 'forest':
        return RandomForestRegressor(n_estimators=90, max_depth=11,
                                     min_samples_leaf=3, random_state=21, n_jobs=1)
    raise DataError('Unknown model. Choose ridge or forest.')


def forecast(frame: pd.DataFrame, model_name: str = 'ridge') -> dict:
    """Fit on older data, score newer observations, refit, forecast next 24 hours.

    Holdout uses real prior observations available 24h earlier at each point.
    This is a rolling-origin day-ahead evaluation, not a 24-step recursive test.
    """
    prepared = feature_table(frame)
    if len(prepared) < 24 * 7:
        raise DataError('Not enough usable training history after creating lag features.')
    # Reserve complete days at the end (at least 7 days), never shuffle time.
    test_rows = max(24 * 7, (len(prepared) // 5 // 24) * 24)
    if len(prepared) - test_rows < 24 * 7:
        raise DataError('Need at least seven days of training observations.')

    train = prepared.iloc[:-test_rows]
    test = prepared.iloc[-test_rows:]
    model = _estimator(model_name)
    model.fit(train[FEATURES], train['actual'])
    predicted = np.maximum(0.0, model.predict(test[FEATURES]))
    naive = test['lag_24'].to_numpy()
    actual = test['actual'].to_numpy()
    mae = float(mean_absolute_error(actual, predicted))
    baseline_mae = float(mean_absolute_error(actual, naive))
    rmse = float(np.sqrt(mean_squared_error(actual, predicted)))

    # Retrain using all known readings before forecasting unknown tomorrow.
    model = _estimator(model_name)
    model.fit(prepared[FEATURES], prepared['actual'])
    history = pd.concat([
        frame,
        pd.DataFrame({
            'timestamp': pd.date_range(frame['timestamp'].iloc[-1] + pd.Timedelta(hours=1),
                                       periods=24, freq='h'),
            'energy_kwh': [np.nan] * 24,
        }),
    ], ignore_index=True)
    future_features = feature_table_forecast(history).tail(24)
    predicted_future = np.maximum(0.0, model.predict(future_features[FEATURES]))

    # Deliberately no confidence intervals: this basic model is not calibrated to produce them.
    return {
        'model': model_name,
        'mae_kwh': round(mae, 3),
        'rmse_kwh': round(rmse, 3),
        'baseline_mae_kwh': round(baseline_mae, 3),
        'change_vs_baseline_pct': (round(100 * (baseline_mae - mae) / baseline_mae, 1)
                                   if baseline_mae else None),
        'holdout_hours': int(test_rows),
        'train_hours': int(len(train)),
        'holdout_start': test['timestamp'].iloc[0].isoformat(),
        'holdout_end': test['timestamp'].iloc[-1].isoformat(),
        'method': 'Chronological holdout; target-hour features lag by at least 24 hours.',
        'observed': [
            {'timestamp': row.timestamp.isoformat(), 'kwh': float(row.energy_kwh)}
            for row in frame.tail(72).itertuples(index=False)
        ],
        'forecast': [
            {'timestamp': ts.isoformat(), 'kwh': round(float(kwh), 2)}
            for ts, kwh in zip(history['timestamp'].tail(24), predicted_future)
        ],
    }


def feature_table_forecast(frame: pd.DataFrame) -> pd.DataFrame:
    """Generate features for future targets (where actual energy_kwh is unknown)."""
    ts = frame['timestamp']
    values = frame['energy_kwh']
    return pd.DataFrame({
        'timestamp': ts,
        'lag_24': values.shift(24),
        'lag_48': values.shift(48),
        'lag_168': values.shift(168),
        'previous_day_mean': values.shift(24).rolling(24).mean(),
        'previous_week_mean': values.shift(24).rolling(168).mean(),
        'hour_sin': np.sin(2 * np.pi * ts.dt.hour / 24),
        'hour_cos': np.cos(2 * np.pi * ts.dt.hour / 24),
        'dow_sin': np.sin(2 * np.pi * ts.dt.dayofweek / 7),
        'dow_cos': np.cos(2 * np.pi * ts.dt.dayofweek / 7),
        'month_sin': np.sin(2 * np.pi * ts.dt.month / 12),
        'month_cos': np.cos(2 * np.pi * ts.dt.month / 12),
        'is_weekend': (ts.dt.dayofweek >= 5).astype(int),
    })
