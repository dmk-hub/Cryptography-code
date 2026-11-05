"""
tv5_tamper_test.py - Chạy 6 test case kiểm tra tính chống giả mạo (Tamper Resistance) cho TV5.
Yêu cầu: File license_core.py phải nằm cùng thư mục.
"""
import base64
from datetime import date
import json

# Import các hàm từ code TV3
from license_core import generate_keys, create_license, verify_license

# 1. Tạo dữ liệu license mẫu
LICENSE_DATA = {
    "license_id": "LIC-001",
    "user": "Alice",
    "machine_id": "PC-1234",
    "issue_date": "2026-01-01",
    "expiry_date": "2099-12-31",
}

# Tạo khóa Vendor (khóa chuẩn) và khóa Hacker (khóa khác)
print("Đang tạo khóa Vendor (RSA-2048)...")
priv_vendor, pub_vendor = generate_keys(2048)

print("Đang tạo khóa Hacker (RSA-2048)...")
priv_hacker, pub_hacker = generate_keys(2048)

# Tạo license gốc hợp lệ
valid_license = create_license(priv_vendor, LICENSE_DATA)

# Hàm phụ để in kết quả cho đẹp
def print_result(test_id, action, expected, actual_reason):
    status = "PASS" if actual_reason != "VALID" or expected == "Hợp lệ" else "FAIL"
    # Riêng test 1, actual_reason phải là VALID mới là PASS
    if test_id == 1:
        status = "PASS" if actual_reason == "VALID" else "FAIL"
    
    print(f"| {test_id} | {action:<35} | {expected:<20} | {status:<4} | {actual_reason} |")

print("\n" + "="*95)
print(f"| {'Test':<4} | {'Hành động':<35} | {'Mong đợi':<20} | {'Kết quả':<4} | {'Chi tiết lý do từ chối'} |")
print("="*95)

# ---------------------------------------------------------
# TEST 1: License gốc, không sửa gì
# ---------------------------------------------------------
ok, reason = verify_license(pub_vendor, valid_license, "PC-1234")
print_result(1, "License gốc, không sửa gì", "Hợp lệ", reason)

# ---------------------------------------------------------
# TEST 2: Sửa tên người dùng (Alice -> Alicf)
# ---------------------------------------------------------
tampered_data = dict(valid_license["data"])
tampered_data["user"] = "Alicf"
license_2 = {"data": tampered_data, "signature": valid_license["signature"]}
ok, reason = verify_license(pub_vendor, license_2, "PC-1234")
print_result(2, "Sửa tên người dùng", "Từ chối (chữ ký sai)", reason)

# ---------------------------------------------------------
# TEST 3: Sửa ngày hết hạn (2099 -> 2020)
# ---------------------------------------------------------
tampered_data = dict(valid_license["data"])
tampered_data["expiry_date"] = "2020-01-01"
license_3 = {"data": tampered_data, "signature": valid_license["signature"]}
ok, reason = verify_license(pub_vendor, license_3, "PC-1234")
print_result(3, "Sửa ngày hết hạn", "Từ chối (chữ ký sai)", reason)

# ---------------------------------------------------------
# TEST 4: Sửa một ký tự trong chữ ký
# ---------------------------------------------------------
sig = valid_license["signature"]
# Đổi ký tự thứ 10 (nếu là A thì đổi thành B, ngược lại đổi thành A)
bad_sig = sig[:10] + ("A" if sig[10] != "A" else "B") + sig[11:]
license_4 = {"data": valid_license["data"], "signature": bad_sig}
ok, reason = verify_license(pub_vendor, license_4, "PC-1234")
print_result(4, "Sửa một ký tự trong chữ ký", "Từ chối", reason)

# ---------------------------------------------------------
# TEST 5: License ký đúng nhưng đã hết hạn
# ---------------------------------------------------------
# Tạo dữ liệu với ngày hết hạn trong quá khứ, nhưng vẫn ký đúng bằng priv_vendor
expired_data = dict(LICENSE_DATA)
expired_data["expiry_date"] = "2020-01-01"
license_5 = create_license(priv_vendor, expired_data)
ok, reason = verify_license(pub_vendor, license_5, "PC-1234", today=date(2026, 1, 1))
print_result(5, "License ký đúng nhưng đã hết hạn", "Từ chối (hết hạn)", reason)

# ---------------------------------------------------------
# TEST 6: License ký bằng khóa khác (Hacker giả mạo)
# ---------------------------------------------------------
# Hacker tự tạo license bằng khóa của mình
license_6 = create_license(priv_hacker, LICENSE_DATA)
ok, reason = verify_license(pub_vendor, license_6, "PC-1234") # Hệ thống verify bằng pub_vendor
print_result(6, "License ký bằng khóa khác", "Từ chối", reason)

print("="*95 + "\n")