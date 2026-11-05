"""
tv4_plots.py - Draw Figure 1, 2, 3 for TV4 from benchmark_results.csv.
Put this file in the SAME folder as benchmark_results.csv, then run:
    python tv4_plots.py

Output:
    - figure1_scalability.png
    - figure2_keygen.png
    - figure3_sign_vs_verify.png
All times are converted from ms to SECONDS (as required by TV4).
"""
import csv

import matplotlib
matplotlib.use("Agg")   # no GUI needed; just save PNG
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Read benchmark_results.csv
# ---------------------------------------------------------------------------
rows = []
with open("benchmark_results.csv", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append({
            "key_size_or_n": int(r["key_size_or_n"]),
            "step": r["step"],
            "mean_ms": float(r["mean_ms"]),
            "median_ms": float(r["median_ms"]),
            "std_ms": float(r["std_ms"]),
        })

def find(key_or_n, step):
    for r in rows:
        if r["key_size_or_n"] == key_or_n and r["step"] == step:
            return r
    raise KeyError(f"No row for key_size_or_n={key_or_n}, step={step}")

def to_seconds(ms):
    return ms / 1000.0

# ---------------------------------------------------------------------------
# Figure 1: Verification scalability (N = 100, 500, 1000)
# ---------------------------------------------------------------------------
ns = [100, 500, 1000]
totals_s = [to_seconds(find(n, "verify_batch")["mean_ms"]) for n in ns]
std_s = [to_seconds(find(n, "verify_batch")["std_ms"]) for n in ns]

fig, ax = plt.subplots(figsize=(6.5, 4.2))
ax.plot(ns, totals_s, marker="o", linewidth=2, color="#1f77b4",
        label="Total verification time")
ax.errorbar(ns, totals_s, yerr=std_s, fmt="none", ecolor="gray",
            capsize=4, label="±1 std")
ax.set_title("Figure 1: Verification Scalability (RSA-2048)")
ax.set_xlabel("Number of licenses verified (N)")
ax.set_ylabel("Total time (seconds)")
ax.set_xticks(ns)
ax.grid(True, alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig("figure1_scalability.png", dpi=300)
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 2: Key Generation (RSA-2048 vs RSA-4096)
# ---------------------------------------------------------------------------
sizes = [2048, 4096]
gen_mean_s = [to_seconds(find(s, "keygen")["mean_ms"]) for s in sizes]
gen_std_s = [to_seconds(find(s, "keygen")["std_ms"]) for s in sizes]

fig, ax = plt.subplots(figsize=(6.5, 4.2))
bars = ax.bar([str(s) for s in sizes], gen_mean_s, yerr=gen_std_s,
              capsize=6, color=["#2ca02c", "#d62728"])
ax.set_title("Figure 2: Key Generation Time (RSA-2048 vs RSA-4096)")
ax.set_xlabel("RSA key size (bits)")
ax.set_ylabel("Time per key pair (seconds)")
ax.grid(True, axis="y", alpha=0.3)
for bar, v in zip(bars, gen_mean_s):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
            f"{v:.3f}s", ha="center", va="bottom", fontsize=10)
fig.tight_layout()
fig.savefig("figure2_keygen.png", dpi=300)
plt.close(fig)

# ---------------------------------------------------------------------------
# Figure 3: Sign vs Verify (RSA-2048)
# ---------------------------------------------------------------------------
sign_s = to_seconds(find(2048, "sign")["mean_ms"])
verify_s = to_seconds(find(2048, "verify")["mean_ms"])
sign_std = to_seconds(find(2048, "sign")["std_ms"])
verify_std = to_seconds(find(2048, "verify")["std_ms"])

fig, ax = plt.subplots(figsize=(6.5, 4.2))
bars = ax.bar(["Sign", "Verify"], [sign_s, verify_s],
              yerr=[sign_std, verify_std], capsize=6,
              color=["#ff7f0e", "#1f77b4"])
ax.set_title("Figure 3: Sign vs Verify (RSA-2048)")
ax.set_xlabel("Operation")
ax.set_ylabel("Time per operation (seconds)")
ax.grid(True, axis="y", alpha=0.3)
for bar, v in zip(bars, [sign_s, verify_s]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
            f"{v:.4f}s", ha="center", va="bottom", fontsize=10)
fig.tight_layout()
fig.savefig("figure3_sign_vs_verify.png", dpi=300)
plt.close(fig)

print("Saved:")
print("  figure1_scalability.png")
print("  figure2_keygen.png")
print("  figure3_sign_vs_verify.png")