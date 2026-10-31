from fastapi.testclient import TestClient
from main import app
from gridlens.data import demo_data

client=TestClient(app)


def test_home_and_health():
    response=client.get('/')
    assert response.status_code==200
    assert 'Understand the load' in response.text
    assert client.get('/api/health').json()=={'status':'ok'}


def test_overview_and_export():
    result=client.get('/api/overview').json()
    assert result['label']=='Generated demo facility'
    assert result['hours']==2880
    exported=client.get('/api/export')
    assert exported.status_code==200
    assert 'energy_kwh' in exported.text
    assert 'is_weekend' in exported.text


def test_api_forecast():
    response=client.post('/api/forecast',json={'dataset_id':'demo','model':'ridge'})
    assert response.status_code==200
    assert len(response.json()['forecast'])==24


def test_csv_upload():
    csv=demo_data().to_csv(index=False).encode()
    response=client.post('/api/upload',files={'file':('energy.csv',csv,'text/csv')})
    assert response.status_code==200
    dataset_id=response.json()['dataset_id']
    assert client.get('/api/overview',params={'dataset_id':dataset_id}).json()['hours']==2880


def test_reject_invalid_upload():
    response=client.post('/api/upload',files={'file':('energy.csv',b'a,b\n1,2\n','text/csv')})
    assert response.status_code==422
    assert 'timestamp' in response.json()['detail']
