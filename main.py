"""GridLens API and built-in frontend.

This is a local portfolio demo. Uploaded datasets are held in process memory,
not written to disk, and disappear when the server restarts.
"""

from __future__ import annotations

import io
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gridlens.data import DataError, demo_data, overview, parse_upload
from gridlens.model import forecast

ROOT = Path(__file__).resolve().parent
app = FastAPI(title='GridLens API', version='1.0.0', description='Day-ahead electricity demand demo')
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')

# In-memory datasets, intentionally small; not a multi-user production datastore.
DATASETS = {'demo': (demo_data(), 'Generated demo facility')}
MAX_DATASETS = 5


class ForecastRequest(BaseModel):
    dataset_id: str = 'demo'
    model: str = 'ridge'


def require_dataset(dataset_id: str):
    if dataset_id not in DATASETS:
        raise HTTPException(status_code=404, detail='Dataset not found. Refresh and upload again.')
    return DATASETS[dataset_id]


@app.get('/', include_in_schema=False)
def index():
    return FileResponse(ROOT / 'static' / 'index.html')


@app.get('/api/health')
def health():
    return {'status': 'ok'}


@app.get('/api/datasets')
def datasets():
    return {'datasets': [{'id': key, 'label': value[1], 'rows': len(value[0])}
                         for key, value in DATASETS.items()]}


@app.get('/api/overview')
def get_overview(dataset_id: str = Query(default='demo', max_length=128)):
    frame, label = require_dataset(dataset_id)
    return overview(frame, label)


@app.post('/api/forecast')
def get_forecast(request: ForecastRequest):
    frame, _ = require_dataset(request.dataset_id)
    try:
        return forecast(frame, request.model)
    except DataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post('/api/upload')
async def upload(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=422, detail='Choose a .csv file.')
    raw = await file.read(4 * 1024 * 1024 + 1)
    try:
        frame = parse_upload(raw)
    except DataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if len(DATASETS) >= MAX_DATASETS:
        # Only evict other uploaded data; never remove the sample dataset.
        oldest = next(key for key in DATASETS if key != 'demo')
        DATASETS.pop(oldest)
    dataset_id = uuid.uuid4().hex[:12]
    # Display names are text-only client-side; no HTML injection.
    label = file.filename[:80]
    DATASETS[dataset_id] = (frame, label)
    return {'dataset_id': dataset_id, 'label': label, 'rows': len(frame)}


@app.get('/api/export')
def export_data(dataset_id: str = Query(default='demo', max_length=128)):
    frame, _ = require_dataset(dataset_id)
    export = frame.copy()
    export['hour'] = export['timestamp'].dt.hour
    export['weekday'] = export['timestamp'].dt.day_name()
    export['month'] = export['timestamp'].dt.month
    export['is_weekend'] = export['timestamp'].dt.dayofweek >= 5
    csv = export.to_csv(index=False)
    return Response(content=csv, media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename="gridlens_powerbi_export.csv"',
    })


@app.get('/api/example-csv')
def example_csv():
    return Response(content=demo_data().to_csv(index=False), media_type='text/csv', headers={
        'Content-Disposition': 'attachment; filename="gridlens_demo_hourly.csv"',
    })
