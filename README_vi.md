# License Core (TV3)

Code lõi để sinh và xác minh license (RSA + SHA-256).

## Yêu cầu
- Python 3.8+
- `pip install cryptography`

## Các file
- `license_core.py` - module gồm 3 hàm tách biệt

## Các hàm
| Hàm | Công dụng |
|---|---|
| `generate_keys(key_size)` | Sinh cặp khóa RSA. `key_size` = 2048 hoặc 4096. Trả về `(private_key, public_key)` |
| `create_license(private_key, license_data)` | Chuẩn hóa dữ liệu, băm SHA-256, ký bằng khóa riêng. Trả về `{"data": ..., "signature": ...}` |
| `verify_license(public_key, license, machine_id, today=None)` | Kiểm tra chữ ký, rồi ngày hết hạn, rồi ID máy. Trả về `(True, "VALID")` hoặc `(False, "<lý do>")` |

## Chạy nhanh
```python
from license_core import generate_keys, create_license, verify_license

priv, pub = generate_keys(2048)
lic = create_license(priv, {
    "license_id": "LIC-001", "user": "Alice", "machine_id": "PC-1234",
    "issue_date": "2026-01-01", "expiry_date": "2099-12-31"})
print(verify_license(pub, lic, "PC-1234"))   # (True, 'VALID')
```
Ngày dùng định dạng `YYYY-MM-DD`.

## Chạy tự kiểm thử
```
python license_core.py
```
Dòng cuối cùng mong đợi: `ALL TESTS PASSED`.

## Gợi ý đo thời gian (cho TV4)
Đo thời gian từng hàm riêng, ví dụ dùng `time.perf_counter()` bao quanh
`generate_keys`, `create_license` và `verify_license`. Lặp lại nhiều lần (ví dụ 50-100)
rồi lấy trung bình. Sinh khóa có yếu tố ngẫu nhiên nên thời gian dao động rất mạnh.

## Các lý do từ chối
- `invalid signature (license was modified)` - chữ ký không hợp lệ (license bị sửa)
- `license expired` - license hết hạn
- `machine ID mismatch` - ID máy không khớp
- `malformed license` / `missing or invalid expiry date` - license sai cấu trúc / thiếu hoặc sai ngày hết hạn

## Lưu ý cho kiểm thử giả mạo (TV5)
Sửa bất kỳ giá trị nào trong `lic["data"]`, hoặc bất kỳ ký tự nào của `lic["signature"]`,
rồi gọi `verify_license` -> kết quả bắt buộc phải là `False`.
