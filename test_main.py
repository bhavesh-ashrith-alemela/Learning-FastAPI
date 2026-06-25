from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

#Test /test api
def test_tst():
    response = client.get("/test")
    #status code checking
    assert response.status_code == 200
    #response data checking
    assert response.json() == {"message": "Hello Bhavesh"}

#Test /add api
def test_add():
    response = client.get("/add?a=5&b=4")
    assert response.status_code == 200
    assert response.json() == {"return": 9}