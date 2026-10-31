#!/usr/bin/env python3
"""Convert the UCI household power dataset into GridLens hourly CSV format.

Download from https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
Unzip it, then point --input at household_power_consumption.txt.
The public dataset is CC BY 4.0 (Georges Hebrail & Alice Berard).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def convert(source: Path, output: Path, start: str, days: int) -> int:
    begin = pd.Timestamp(start)
    end = begin + pd.Timedelta(days=days)
    if begin.hour != 0 or begin.minute != 0:
        raise ValueError('--start must be a date at midnight, e.g. 2007-01-01')
    sums = {}
    counts = {}
    for chunk in pd.read_csv(source, sep=';', usecols=['Date','Time','Global_active_power'],
                             dtype=str, chunksize=150_000, na_values=['?']):
        timestamps = pd.to_datetime(chunk['Date'] + ' ' + chunk['Time'],
                                    format='%d/%m/%Y %H:%M:%S', errors='coerce')
        power = pd.to_numeric(chunk['Global_active_power'], errors='coerce')
        filtered = pd.DataFrame({'ts':timestamps,'kw':power})
        filtered = filtered[(filtered['ts'] >= begin) & (filtered['ts'] < end)].dropna()
        if filtered.empty:
            continue
        filtered['hour'] = filtered['ts'].dt.floor('h')
        partial = filtered.groupby('hour')['kw'].agg(['sum','count'])
        for hour, row in partial.iterrows():
            sums[hour] = sums.get(hour, 0) + float(row['sum'])
            counts[hour] = counts.get(hour, 0) + int(row['count'])
    expected = pd.date_range(begin, periods=days * 24, freq='h')
    bad = [hour for hour in expected if counts.get(hour,0) < 58]
    if bad:
        raise ValueError(f'{len(bad)} hours have fewer than 58 valid minute readings; '
                         f'first: {bad[0]}. Choose another contiguous period. '
                         'Incomplete hours are never silently imputed.')
    if days < 24:
        raise ValueError('Choose at least 24 days for training and evaluation.')
    frame = pd.DataFrame({
        'timestamp':expected,
        # Each one-minute power reading (kW) represents kWh / 60 minutes.
        'energy_kwh':[round(sums[h] / 60, 4) for h in expected],
    })
    output.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(output,index=False)
    return len(frame)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True,help='Unzipped UCI household_power_consumption.txt')
    p.add_argument('--output',type=Path,default=Path('data/uci_household_hourly.csv'))
    p.add_argument('--start',default='2007-01-01')
    p.add_argument('--days',type=int,default=60)
    args=p.parse_args()
    n=convert(args.input,args.output,args.start,args.days)
    print(f'Wrote {n} hourly readings to {args.output}. Source: UCI dataset 235 (CC BY 4.0).')
