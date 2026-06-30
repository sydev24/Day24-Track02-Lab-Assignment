# tests/test_rbac.py
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

class TestRBAC:
    def test_admin_alice_access(self):
        headers = {"Authorization": "Bearer token-alice"}
        
        # Admin gets 200 on all endpoints
        res_raw = client.get("/api/patients/raw", headers=headers)
        assert res_raw.status_code == 200, f"Expected 200, got {res_raw.status_code}"
        
        res_anon = client.get("/api/patients/anonymized", headers=headers)
        assert res_anon.status_code == 200
        
        res_metrics = client.get("/api/metrics/aggregated", headers=headers)
        assert res_metrics.status_code == 200
        
        res_del = client.delete("/api/patients/test-id-123", headers=headers)
        assert res_del.status_code == 200

    def test_ml_engineer_bob_access(self):
        headers = {"Authorization": "Bearer token-bob"}
        
        # ml_engineer CANNOT access raw or delete production data
        res_raw = client.get("/api/patients/raw", headers=headers)
        assert res_raw.status_code == 403
        
        res_del = client.delete("/api/patients/test-id-123", headers=headers)
        assert res_del.status_code == 403
        
        # ml_engineer CAN access anonymized training data and aggregated metrics
        res_anon = client.get("/api/patients/anonymized", headers=headers)
        assert res_anon.status_code == 200
        
        res_metrics = client.get("/api/metrics/aggregated", headers=headers)
        assert res_metrics.status_code == 200

    def test_data_analyst_carol_access(self):
        headers = {"Authorization": "Bearer token-carol"}
        
        # data_analyst CANNOT access raw or anonymized patient level data
        res_raw = client.get("/api/patients/raw", headers=headers)
        assert res_raw.status_code == 403
        
        res_anon = client.get("/api/patients/anonymized", headers=headers)
        assert res_anon.status_code == 403
        
        # data_analyst CAN access aggregated metrics
        res_metrics = client.get("/api/metrics/aggregated", headers=headers)
        assert res_metrics.status_code == 200

    def test_missing_or_invalid_token(self):
        res_no_token = client.get("/api/patients/raw")
        assert res_no_token.status_code == 401
        
        res_bad = client.get("/api/patients/raw", headers={"Authorization": "Bearer invalid-token"})
        assert res_bad.status_code == 401
