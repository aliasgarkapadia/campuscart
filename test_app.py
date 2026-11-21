from app import app

def test_health_ok():
    r = app.test_client().get("/health")
    assert r.status_code == 200 and r.json["status"] == "ok"

def test_health_reports_version():
    assert "version" in app.test_client().get("/health").json

def test_order_validation():
    r = app.test_client().post("/orders", json={"item": "pen"})
    assert r.status_code == 400