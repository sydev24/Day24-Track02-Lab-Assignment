# tests/test_quality.py
import pytest
import os
from src.quality.validation import build_patient_expectation_suite, validate_anonymized_data

class TestDataQuality:
    def test_build_expectation_suite(self):
        suite = build_patient_expectation_suite()
        assert suite is not None
        assert suite.name == "patient_data_suite"
        assert len(suite.expectations) >= 5


    def test_validate_anonymized_dataset(self):
        # We verify on the generated anonymized dataset
        anon_path = "data/processed/patients_anonymized.csv"
        if not os.path.exists(anon_path):
            import pandas as pd
            from src.pii.anonymizer import MedVietAnonymizer
            df = pd.read_csv("data/raw/patients_raw.csv")
            anon = MedVietAnonymizer()
            df_anon = anon.anonymize_dataframe(df)
            df_anon.to_csv(anon_path, index=False)
            
        res = validate_anonymized_data(anon_path)
        assert res["success"] is True, f"Validation failed: {res['failed_checks']}"
        assert res["stats"]["total_rows"] > 0
