"""
license_core.py - Phần lõi của Hệ thống Xác minh License Phần mềm An toàn (TV3)

Ba hàm riêng biệt (để TV4 đo thời gian từng hàm độc lập):
    1. generate_keys(key_size)                      -> (private_key, public_key)
    2. create_license(private_key, license_data)    -> license (dict)
    3. verify_license(public_key, license, machine_id, today=None) -> (bool, reason)

Chạy `python license_core.py` để thực hiện self-test nhanh.
Yêu cầu: pip install cryptography
"""

import base64
import json
from datetime import date

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa


# Hàm phụ: dạng chuẩn hóa (nhất quán) của dữ liệu license
def canonicalize(license_data: dict) -> bytes:
    """Chuyển dữ liệu license thành MỘT chuỗi byte cố định.

    Các khóa được sắp xếp và không dùng khoảng trắng thừa, nên cùng một dữ liệu
    luôn cho ra cùng một chuỗi byte -> cùng một mã băm SHA-256. Được dùng ở CẢ
    hai bước tạo và xác minh.
    """
    text = json.dumps(license_data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)
    return text.encode("utf-8")


# Hàm 1: Sinh cặp khóa RSA
def generate_keys(key_size: int = 2048):
    """Sinh một cặp khóa RSA. key_size phải là 2048 hoặc 4096."""
    if key_size not in (2048, 4096):
        raise ValueError("key_size phải là 2048 hoặc 4096")
    private_key = rsa.generate_private_key(public_exponent=65537,
                                           key_size=key_size)
    return private_key, private_key.public_key()


# Hàm 2: Tạo license (dữ liệu -> chuỗi chuẩn hóa -> SHA-256 -> ký)
def create_license(private_key, license_data: dict) -> dict:
    """Ký dữ liệu license bằng khóa riêng tư.

    Ví dụ license_data:
        {"license_id": "LIC-001", "user": "Alice",
         "machine_id": "PC-1234", "issue_date": "2026-01-01",
         "expiry_date": "2027-01-01"}   (ngày theo định dạng YYYY-MM-DD)

    Trả về: {"data": license_data, "signature": <chuỗi base64>}
    Lưu ý: thư viện sẽ băm chuỗi byte chuẩn hóa bằng SHA-256 rồi ký mã băm
    bằng RSA (PKCS#1 v1.5) trong một lần gọi sign() duy nhất.
    """
    message = canonicalize(license_data)
    signature = private_key.sign(message, padding.PKCS1v15(), hashes.SHA256())
    return {
        "data": license_data,
        "signature": base64.b64encode(signature).decode("ascii"),
    }


# Hàm 3: Xác minh license
def verify_license(public_key, license_obj: dict, machine_id: str,
                   today=None):
    """Xác minh một license. Trả về (True, "VALID") hoặc (False, "<lý do>").

    Thứ tự kiểm tra: 1) chữ ký  2) ngày hết hạn  3) mã máy.
    `today` (datetime.date) có thể truyền vào để test; mặc định là hôm nay.
    """
    # Kiểm tra cấu trúc
    try:
        data = license_obj["data"]
        signature = base64.b64decode(license_obj["signature"], validate=True)
    except Exception:
        return False, "REJECTED: license sai cấu trúc"

    # 1) Kiểm tra chữ ký (thư viện ném ngoại lệ khi chữ ký sai)
    try:
        public_key.verify(signature, canonicalize(data),
                          padding.PKCS1v15(), hashes.SHA256())
    except InvalidSignature:
        return False, "REJECTED: chữ ký không hợp lệ (license đã bị sửa)"
    except Exception:
        return False, "REJECTED: không thể xác minh chữ ký"

    # 2) Kiểm tra ngày hết hạn
    try:
        expiry = date.fromisoformat(data["expiry_date"])
    except Exception:
        return False, "REJECTED: thiếu hoặc sai ngày hết hạn"
    if (today or date.today()) > expiry:
        return False, "REJECTED: license đã hết hạn"

    # 3) Kiểm tra mã máy
    if data.get("machine_id") != machine_id:
        return False, "REJECTED: mã máy không khớp"

    return True, "VALID"


# Self-test nhanh
def _self_test():
    sample = {
        "license_id": "LIC-001",
        "user": "Alice",
        "machine_id": "PC-1234",
        "issue_date": "2026-01-01",
        "expiry_date": "2099-12-31",
    }
    results = []

    def check(name, got, expected):
        ok = (got == expected)
        results.append(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {got}")

    for size in (2048, 4096):
        print(f"\n--- Kích thước khóa {size} ---")
        priv, pub = generate_keys(size)
        lic = create_license(priv, sample)

        check("License đúng thì hợp lệ",
              verify_license(pub, lic, "PC-1234")[0], True)

        # Đổi một chữ trong dữ liệu (Alice -> Alicf)
        tampered = {"data": dict(lic["data"], user="Alicf"),
                    "signature": lic["signature"]}
        check("Đổi 1 chữ trong dữ liệu thì bị từ chối",
              verify_license(pub, tampered, "PC-1234")[0], False)

        # Đổi một chữ trong chữ ký
        sig = lic["signature"]
        bad_sig = sig[:10] + ("A" if sig[10] != "A" else "B") + sig[11:]
        check("Đổi 1 chữ trong chữ ký thì bị từ chối",
              verify_license(pub, {"data": lic["data"], "signature": bad_sig},
                             "PC-1234")[0], False)

        check("Sai mã máy thì bị từ chối",
              verify_license(pub, lic, "PC-9999")[0], False)

        check("License hết hạn thì bị từ chối",
              verify_license(pub, lic, "PC-1234", today=date(2100, 1, 1))[0],
              False)

        # Thứ tự khóa khác nhau vẫn phải xác minh được (chuẩn hóa hoạt động)
        reordered = {"data": dict(reversed(list(lic["data"].items()))),
                     "signature": lic["signature"]}
        check("Thứ tự khóa khác nhau vẫn hợp lệ",
              verify_license(pub, reordered, "PC-1234")[0], True)

    print("\nTẤT CẢ TEST ĐỀU PASS" if all(results) else "\nCÓ TEST FAIL")
    return all(results)


if __name__ == "__main__":
    raise SystemExit(0 if _self_test() else 1)