import csv
import statistics

times = []
with open("benchmark_raw.csv") as f:
    for row in csv.DictReader(f):
        if row["key_size_or_n"] == "2048" and row["step"] == "sign":
            times.append(float(row["time_ms"]))

print(f"Số lần đo: {len(times)}")
print(f"Mean thực tế tính lại: {statistics.mean(times):.3f} ms")
print(f"Median thực tế tính lại: {statistics.median(times):.3f} ms")