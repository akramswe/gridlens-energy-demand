# Design notes

A few technical decisions behind GridLens.

## Why an API instead of calculations entirely in the browser?

It separates data checking, feature engineering, and prediction from presentation. The browser only displays data returned by documented endpoints. This makes it easier to test the logic directly or replace the dashboard later.

## Why a synthetic demo?

The repository should run straight after cloning. Real utility datasets often require access, licenses, careful treatment of time zones, and a lot of storage. The repeatable generator gives someone a stable way to explore the UI without inventing a real data source. The README also explains how to use one properly attributed UCI dataset.

## Why a simple model?

Ridge is quick to run and easy to explain. Random Forest provides a nonlinear comparison. Both are stronger portfolio demonstrations when paired with a clear baseline and strict validation than an untested complicated network. No neural-network framework is used or claimed in this implementation.

## Where time can cause trouble

- Only complete, continuous hourly data is accepted. DST changes can create repeated or missing local clock times; normalize those records before import.
- For a target at time *t*, the newest input is at *t - 24 hours*. This prevents tomorrow's features from needing predicted intermediate demand values.
- The evaluation holds out the most recent observations and scores errors using actual lagged history available at each historical target time. This is not proof of future production accuracy.
- The model doesn't know about public holidays, weather, or temporary shutdowns.

## Before using this in a real organization

Add authenticated user sessions, persistent storage, upload scanning, request-level resource limits, deployment monitoring, a data dictionary, daylight-saving/time-zone rules, better evaluation, privacy controls, and a model-update procedure. This is a portfolio prototype, not operational power-grid software.
