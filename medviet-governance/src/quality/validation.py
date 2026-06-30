# src/quality/validation.py
import pandas as pd
import great_expectations as gx
from great_expectations.core.expectation_suite import ExpectationSuite

def build_patient_expectation_suite() -> ExpectationSuite:
    """
    Tạo expectation suite cho anonymized patient data (chỉ định GX 1.18.2).
    """
    context = gx.get_context()
    suite = gx.ExpectationSuite(name="patient_data_suite")
    suite = context.suites.add(suite)

    # 1. patient_id không được null
    suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="patient_id"))

    # 2. cccd phải có đúng 12 ký tự (hoặc 11 nếu mất số 0 ở đầu)
    suite.add_expectation(gx.expectations.ExpectColumnValueLengthsToBeBetween(
        column="cccd",
        min_value=11,
        max_value=12
    ))

    # 3. ket_qua_xet_nghiem phải trong khoảng [0, 50]
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
        column="ket_qua_xet_nghiem",
        min_value=0,
        max_value=50
    ))

    # 4. benh phải thuộc danh sách hợp lệ
    valid_conditions = ["Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh", "Ung thư giai đoạn 1", "Viêm phổi"]
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(
        column="benh",
        value_set=valid_conditions
    ))

    # 5. email phải match regex pattern
    suite.add_expectation(gx.expectations.ExpectColumnValuesToMatchRegex(
        column="email",
        regex=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    ))

    # 6. Không được có duplicate patient_id
    suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="patient_id"))

    return suite


def validate_anonymized_data(filepath: str) -> dict:
    """
    Validate anonymized data.
    Trả về dict: {"success": bool, "failed_checks": list, "stats": dict}
    """
    df = pd.read_csv(filepath)
    raw_df = pd.read_csv("data/raw/patients_raw.csv")

    results = {
        "success": True,
        "failed_checks": [],
        "stats": {
            "total_rows": len(df),
            "columns": list(df.columns)
        }
    }

    # Check 1: Không còn CCCD gốc trùng với raw
    raw_cccds = set(raw_df["cccd"].astype(str))
    anon_cccds = set(df["cccd"].astype(str))
    common_cccds = raw_cccds.intersection(anon_cccds)
    if len(common_cccds) > 0:
        results["success"] = False
        results["failed_checks"].append(f"Found {len(common_cccds)} un-anonymized CCCDs")

    # Check 2: Không có null values trong các cột quan trọng
    for col in ["patient_id", "benh"]:
        if df[col].isnull().any():
            results["success"] = False
            results["failed_checks"].append(f"Null values in {col}")

    # Check 3: Số rows phải bằng original
    if len(df) != len(raw_df):
        results["success"] = False
        results["failed_checks"].append(f"Row count mismatch: {len(df)} vs {len(raw_df)}")

    return results
