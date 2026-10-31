# Building a small Power BI report from GridLens

This is a practical companion to the web dashboard, not a prebuilt `.pbix` file.
You can turn the exported CSV into a Power BI report in a few minutes, then
save your own `.pbix` file here if you want to show a native Power BI example.

## 1. Import

1. In GridLens, choose a dataset and click **Export to Power BI**.
2. In Power BI Desktop, choose **Home → Get data → Text/CSV**.
3. Select `gridlens_powerbi_export.csv` and open **Transform Data**.
4. Set `timestamp` to Date/Time, `energy_kwh` to Decimal Number,
   `hour` and `month` to Whole Number, and `is_weekend` to True/False.
5. Close & Apply. Rename the imported table to `Energy`.

## 2. Useful measures

```dax
Total Energy (kWh) = SUM(Energy[energy_kwh])

Total Energy (MWh) = DIVIDE([Total Energy (kWh)], 1000)

Average Hourly Load (kW) = AVERAGE(Energy[energy_kwh])

Peak Hourly Load (kW) = MAX(Energy[energy_kwh])
```

The CSV has one row per complete hour. Hourly energy in kWh is numerically
identical to average load in kW over that hour; the units are still different.

## 3. Suggested visuals

- **Cards:** total MWh, average hourly load, peak hourly load.
- **Line chart:** `timestamp` on the X axis, `energy_kwh` on the Y axis.
  Choose *day* and sum for a daily consumption trend.
- **Column chart:** hour on the X axis; average of `energy_kwh` on Y.
- **Column chart:** weekday on the X axis; average of `energy_kwh` on Y.
  Set weekday sort order manually so Monday appears before Sunday.
- **Slicers:** month and weekend flag.

You can import `gridlens_24h_forecast.csv` as a separate table if you also
want to compare observed data and predicted future demand.

## Important context

When exporting the built-in demo, every observation is **synthetic**. Label
your Power BI report as an example, not actual facility or grid readings.
If you use UCI data, include the [dataset citation](https://doi.org/10.24432/C58K54).

## Why there isn't a .pbix in the repo

Power BI Desktop saves a native `.pbix` report, which requires the desktop
application to create. Rather than include a misleading or fake report file,
this folder provides reproducible steps and real DAX expressions for a report
you can create and validate yourself.
