from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_process_document():
    response = client.post('/process', json={'text': 'O CPF do cliente é 12345678900'})
    assert response.status_code == 200
    data = response.json()
    assert '[CPF]' in data['anonymized_text']
    assert data['metadata']['status'] == 'processed'
