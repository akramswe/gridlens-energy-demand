# How to add GridLens to your CV

Only add this project after running it, reviewing its code, and making enough
changes or doing enough testing that you can explain your decisions honestly.

**GridLens — Electricity Consumption & Day-Ahead Forecasting Dashboard**  
*Python · FastAPI · pandas · scikit-learn · JavaScript · Plotly · Power BI-ready CSV*

- Built a full-stack dashboard for exploring hourly electricity consumption, including daily trends, peak usage, and hourly / weekly demand patterns.
- Implemented Ridge and Random Forest forecasting with 24-hour-ahead features, chronological holdout evaluation, and a seasonal-naive baseline for comparison.
- Added CSV upload validation, REST endpoints, downloadable forecasts, Power BI-ready exports, and automated API / model tests.

If you have room for only one bullet:

> Built GridLens, a FastAPI and JavaScript energy analytics dashboard with hourly CSV ingestion, scikit-learn day-ahead forecasts, baseline evaluation, and Power BI-ready exports.

**What not to claim:** You did not train a PyTorch model in this version,
there is no Azure deployment, there is no native Power BI report (`.pbix`),
and the bundled data is synthetic. If you add any of those later, update the
entry to reflect the actual work.

## Interview talking points

- Why are the most recent predictive features at least 24 hours old? So every feature for tomorrow is known at the end of today.
- How do you avoid temporal leakage? A time-ordered split and lagged inputs, never shuffled records or future target values.
- What is the baseline? Predict the same hourly consumption as yesterday, then compare its holdout MAE to the trained model's MAE.
- Why Ridge before a neural network? It is fast, reproducible, and easier to benchmark. Sophistication is not a substitute for a useful baseline.
- What is the main limitation? No holidays, weather, uncertainty intervals, or changes in operating schedules. Demo measurements are generated and should not be interpreted as grid data.
- What would you do next? Try UCI measurements, use rolling historical validations, and build a Power BI report from the export.
