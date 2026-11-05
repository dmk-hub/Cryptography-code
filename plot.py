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
# Style (applies to all figures)
# ---------------------------------------------------------------------------
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linestyle": "--",
    "axes.axisbelow": True,
    "legend.frameon": False,
})
BLUE, ORANGE, GREEN, RED = "#2b6cb0", "#dd6b20", "#2f855a", "#c53030"
FIGSIZE = (6.5, 4.4)

# ---------------------------------------------------------------------------
# Read benchmark_results.csv
# ---------------------------------------------------------------------------
rows = []
with open("benchmark_results.csv", newline="") as f:
    for r in csv.DictReader(f):
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


def sec(ms):
    return ms / 1000.0


def asym_err(means, stds):
    """Error bars that never go below 0 (time cannot be negative)."""
    lower = [min(s, m) for m, s in zip(means, stds)]
    return [lower, list(stds)]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(name, dpi=300)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 1: Verification scalability
# ---------------------------------------------------------------------------
ns = [100, 500, 1000]
means = [sec(find(n, "verify_batch")["mean_ms"]) for n in ns]
stds = [sec(find(n, "verify_batch")["std_ms"]) for n in ns]

fig, ax = plt.subplots(figsize=FIGSIZE)
ax.errorbar(ns, means, yerr=asym_err(means, stds), marker="o", markersize=7,
            linewidth=2, color=BLUE, ecolor="gray", capsize=4,
            label="Mean ± 1 std")
for x, y, s in zip(ns, means, stds):
    ax.annotate(f"{y:.4f} s", (x, y + s), textcoords="offset points",
                xytext=(0, 7), ha="center", fontsize=10)
ax.set_title("Figure 1: Verification Scalability (RSA-2048)")
ax.set_xlabel("Number of licenses verified")
ax.set_ylabel("Total time (seconds)")
ax.set_xticks(ns)
ax.set_xlim(0, 1100)
ax.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.2)
ax.legend(loc="upper left")
save(fig, "figure1_scalability.png")

# ---------------------------------------------------------------------------
# Figure 2: Key generation
# ---------------------------------------------------------------------------
sizes = [2048, 4096]
means = [sec(find(s, "keygen")["mean_ms"]) for s in sizes]
stds = [sec(find(s, "keygen")["std_ms"]) for s in sizes]

fig, ax = plt.subplots(figsize=FIGSIZE)
bars = ax.bar([f"RSA-{s}" for s in sizes], means, width=0.5,
              yerr=asym_err(means, stds), capsize=6,
              color=[GREEN, RED], ecolor="gray")
for bar, m, s in zip(bars, means, stds):
    ax.annotate(f"{m:.3f} s", (bar.get_x() + bar.get_width() / 2, m + s),
                textcoords="offset points", xytext=(0, 6),
                ha="center", fontsize=10)
ax.set_title("Figure 2: Key Generation Time")
ax.set_xlabel("RSA key size")
ax.set_ylabel("Time per key pair (seconds)")
ax.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.2)
ax.grid(axis="x", visible=False)
save(fig, "figure2_keygen.png")

# ---------------------------------------------------------------------------
# Figure 3: Sign vs Verify
# ---------------------------------------------------------------------------
labels = ["Sign", "Verify"]
means = [sec(find(2048, "sign")["mean_ms"]), sec(find(2048, "verify")["mean_ms"])]
stds = [sec(find(2048, "sign")["std_ms"]), sec(find(2048, "verify")["std_ms"])]

fig, ax = plt.subplots(figsize=FIGSIZE)
bars = ax.bar(labels, means, width=0.5, yerr=asym_err(means, stds),
              capsize=6, color=[ORANGE, BLUE], ecolor="gray")
for bar, m, s in zip(bars, means, stds):
    ax.annotate(f"{m:.6f} s", (bar.get_x() + bar.get_width() / 2, m + s),
                textcoords="offset points", xytext=(0, 6),
                ha="center", fontsize=10)
ax.set_title("Figure 3: Sign vs Verify (RSA-2048)")
ax.set_xlabel("Operation")
ax.set_ylabel("Time per operation (seconds)")
ax.set_ylim(0, max(m + s for m, s in zip(means, stds)) * 1.2)
ax.grid(axis="x", visible=False)
save(fig, "figure3_sign_vs_verify.png")

print("Saved: figure1_scalability.png, figure2_keygen.png, figure3_sign_vs_verify.png")