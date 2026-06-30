# tests/test_encryption.py
import pytest
import os
import pandas as pd
from src.encryption.vault import SimpleVault

@pytest.fixture
def vault(tmp_path):
    key_path = os.path.join(tmp_path, "test_key.bin")
    return SimpleVault(master_key_path=key_path)

class TestEnvelopeEncryption:
    def test_kek_generation(self, vault):
        assert len(vault.kek) == 32

    def test_dek_generation_and_decryption(self, vault):
        plaintext_dek, encrypted_dek = vault.generate_dek()
        assert len(plaintext_dek) == 32
        assert len(encrypted_dek) > 32
        
        decrypted_dek = vault.decrypt_dek(encrypted_dek)
        assert decrypted_dek == plaintext_dek

    def test_encrypt_decrypt_data(self, vault):
        secret_message = "Bệnh nhân Nguyễn Văn A - CCCD 012345678901 - Ung thư giai đoạn 1"
        payload = vault.encrypt_data(secret_message)
        
        assert "encrypted_dek" in payload
        assert "ciphertext" in payload
        assert payload["algorithm"] == "AES-256-GCM"
        
        decrypted_message = vault.decrypt_data(payload)
        assert decrypted_message == secret_message

    def test_encrypt_column(self, vault):
        df = pd.DataFrame({
            "patient_id": [1, 2],
            "sensitive_info": ["Di ứng Penicillin", "Tiểu đường tuýp 2"]
        })
        
        encrypted_df = vault.encrypt_column(df, "sensitive_info")
        
        # Original text should not be visible in encrypted column
        assert "Penicillin" not in encrypted_df["sensitive_info"].iloc[0]
        assert "algorithm" in encrypted_df["sensitive_info"].iloc[0]
