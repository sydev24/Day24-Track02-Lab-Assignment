# scripts/demo_pipeline.py
import os
import sys
sys.path.insert(0, os.path.abspath("."))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from src.pii.anonymizer import MedVietAnonymizer
from src.encryption.vault import SimpleVault
from src.quality.validation import validate_anonymized_data

def main():
    print("=" * 70)
    print(" 🏥 MEDVIET AI GOVERNANCE PLATFORM — END-TO-END DEMO 🏥")
    print("=" * 70)

    # 1. Load Raw Data
    raw_path = "data/raw/patients_raw.csv"
    if not os.path.exists(raw_path):
        print("⏳ Generating raw data...")
        os.system("python scripts/generate_data.py")
    
    df_raw = pd.read_csv(raw_path)
    print("\n[Bước 1] DỮ LIỆU THÔ BAN ĐẦU (RAW DATA - CHỨA PII NHẠY CẢM):")
    print("-" * 70)
    cols_to_show = ["patient_id", "ho_ten", "cccd", "so_dien_thoai", "benh"]
    print(df_raw[cols_to_show].head(3).to_string(index=False))

    # 2. Anonymize Data
    print("\n[Bước 2] THỰC THI ẨN DANH HÓA PII (PRESIDIO + SPACY NLP):")
    print("-" * 70)
    anonymizer = MedVietAnonymizer()
    df_anon = anonymizer.anonymize_dataframe(df_raw.head(5))
    os.makedirs("data/processed", exist_ok=True)
    anon_path = "data/processed/demo_anonymized.csv"
    df_anon.to_csv(anon_path, index=False)
    print(df_anon[cols_to_show].head(3).to_string(index=False))

    # 3. Envelope Encryption
    print("\n[Bước 3] MÃ HÓA ENVELOPE ENCRYPTION (AES-256-GCM CẤP CỘT):")
    print("-" * 70)
    vault = SimpleVault()
    sample_text = df_raw.loc[0, "benh"]
    encrypted_payload = vault.encrypt_data(sample_text)
    print(f"🔒 Bản gốc   : {sample_text}")
    print(f"🔑 Ciphertext: {encrypted_payload['ciphertext'][:40]}...")
    print(f"🔐 Decrypted : {vault.decrypt_data(encrypted_payload)}")

    # 4. Data Quality Validation
    print("\n[Bước 4] KIỂM CHỨNG CHẤT LƯỢNG DỮ LIỆU (GREAT EXPECTATIONS):")
    print("-" * 70)
    # Validate against anonymized dataframe saved earlier
    # Generate full anonymized dataset for accurate check
    full_anon = anonymizer.anonymize_dataframe(df_raw)
    full_anon_path = "data/processed/patients_anonymized.csv"
    full_anon.to_csv(full_anon_path, index=False)
    
    val_res = validate_anonymized_data(full_anon_path)
    if val_res["success"]:
        print("✅ Kiểm tra chất lượng dữ liệu PASSED 100%!")
        print(f"📊 Tổng số hồ sơ hợp lệ: {val_res['stats']['total_rows']} dòng")
    else:
        print(f"❌ Lỗi chất lượng: {val_res['failed_checks']}")

    # 5. RBAC API simulation
    print("\n[Bước 5] PHÂN QUYỀN TRUY CẬP RBAC (CASBIN):")
    print("-" * 70)
    from fastapi.testclient import TestClient
    from src.api.main import app
    client = TestClient(app)
    
    users = [
        ("Alice (Admin)", "token-alice", "/api/patients/raw"),
        ("Bob (ML Engineer)", "token-bob", "/api/patients/raw"),
        ("Bob (ML Engineer)", "token-bob", "/api/patients/anonymized"),
        ("Carol (Data Analyst)", "token-carol", "/api/patients/anonymized"),
        ("Carol (Data Analyst)", "token-carol", "/api/metrics/aggregated")
    ]
    
    for name, token, endpoint in users:
        res = client.get(endpoint, headers={"Authorization": f"Bearer {token}"})
        status_icon = "🟢 ALLOWED (200)" if res.status_code == 200 else f"🔴 DENIED ({res.status_code})"
        print(f"👤 {name.ljust(22)} ➔ {endpoint.ljust(26)} : {status_icon}")

    print("\n" + "=" * 70)
    print(" ✨ HOÀN TẤT CHẠY THỬ! TOÀN BỘ HỆ THỐNG HOẠT ĐỘNG HOÀN HẢO! ✨")
    print("=" * 70)

if __name__ == "__main__":
    main()
