# src/pii/anonymizer.py
# pyrefly: ignore [missing-import]
import pandas as pd
# pyrefly: ignore [missing-import]
from presidio_anonymizer import AnonymizerEngine
# pyrefly: ignore [missing-import]
from presidio_anonymizer.entities import OperatorConfig
from faker import Faker
import hashlib
from .detector import build_vietnamese_analyzer, detect_pii

fake = Faker("vi_VN")

class MedVietAnonymizer:

    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()
        self.anonymizer = AnonymizerEngine()

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        if not text or pd.isna(text):
            return str(text)
            
        results = detect_pii(text, self.analyzer)
        if not results:
            return text

        operators = {}

        if strategy == "replace":
            operators = {
                "PERSON": OperatorConfig("replace", {"new_value": fake.name()}),
                "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": fake.email()}),
                "VN_CCCD": OperatorConfig("replace", {"new_value": fake.numerify("############")}),
                "VN_PHONE": OperatorConfig("replace", {"new_value": fake.numerify("09########")}),
            }
        elif strategy == "mask":
            operators = {
                "PERSON": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 6, "from_end": True}),
                "EMAIL_ADDRESS": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 5, "from_end": False}),
                "VN_CCCD": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 8, "from_end": True}),
                "VN_PHONE": OperatorConfig("mask", {"type": "mask", "masking_char": "*", "chars_to_mask": 7, "from_end": True}),
            }
        elif strategy == "hash":
            operators = {
                ent: OperatorConfig("custom", {"lambda": lambda x: hashlib.sha256(x.encode()).hexdigest()[:12]})
                for ent in ["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"]
            }

        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators
        )
        return anonymized.text

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()

        # Xử lý các cột text chứa PII phức tạp
        for col in ["ho_ten", "dia_chi", "email"]:
            if col in df_anon.columns:
                df_anon[col] = df_anon[col].astype(str).apply(lambda x: self.anonymize_text(x, strategy="replace"))

        # Thay thế trực tiếp cột số cccd và so_dien_thoai bằng fake data mới
        if "cccd" in df_anon.columns:
            df_anon["cccd"] = [fake.numerify("############") for _ in range(len(df_anon))]
        if "so_dien_thoai" in df_anon.columns:
            df_anon["so_dien_thoai"] = [fake.numerify("09########") for _ in range(len(df_anon))]

        return df_anon

    def calculate_detection_rate(self, original_df: pd.DataFrame, pii_columns: list) -> float:
        total = 0
        detected = 0

        for col in pii_columns:
            for value in original_df[col].dropna().astype(str):
                total += 1
                results = detect_pii(value, self.analyzer)
                if len(results) > 0:
                    detected += 1

        return detected / total if total > 0 else 0.0
