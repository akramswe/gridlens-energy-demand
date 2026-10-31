import numpy as np
import pandas as pd
import pytest

from gridlens.data import DataError, demo_data
from gridlens.model import FEATURES, feature_table, feature_table_forecast, forecast


def test_24_hour_lag_uses_prior_day_only():
    data = demo_data()
    features = feature_table(data)
    first = features.iloc[0]
    original_row = data.index[data.timestamp == first.timestamp][0]
    assert first['lag_24'] == data.energy_kwh.iloc[original_row - 24]
    assert first['lag_168'] == data.energy_kwh.iloc[original_row - 168]
    assert first['previous_week_mean'] == pytest.approx(data.energy_kwh.iloc[original_row - 191:original_row - 23].mean())


def test_day_ahead_features_require_no_future_actual_values():
    data = demo_data()
    future = pd.DataFrame({'timestamp':pd.date_range(data.timestamp.iloc[-1]+pd.Timedelta(hours=1),periods=24,freq='h'),'energy_kwh':np.nan})
    table = feature_table_forecast(pd.concat([data,future],ignore_index=True))
    assert table.tail(24)[FEATURES].notna().all().all()
    assert table.iloc[-1]['lag_24']==data.energy_kwh.iloc[-1]


@pytest.mark.parametrize('model',['ridge','forest'])
def test_models_return_24_usable_forecasts(model):
    result=forecast(demo_data(),model)
    assert result['train_hours']>=168
    assert result['holdout_hours']>=168
    assert result['mae_kwh']>=0
    assert len(result['forecast'])==24
    assert all(p['kwh']>=0 for p in result['forecast'])
    assert result['forecast'][0]['timestamp'] > result['observed'][-1]['timestamp']


def test_unknown_model():
    with pytest.raises(DataError, match='Unknown model'):
        forecast(demo_data(),'made-up')
