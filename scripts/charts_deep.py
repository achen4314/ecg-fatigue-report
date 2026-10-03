# -*- coding: utf-8 -*-
"""Deeper charts: beat-level tachograms, dRR, HR-RMSSD, SD ratios, respiration, deviation bands."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

BLUE = "#171B40"; GREEN = "#A0FF00"; RED = "#E5484D"; AMBER = "#F5A524"; GRAY = "#8A8FA3"
MORN = "#2F6FED"; EVE = "#7C5CFC"; DAY = "#5B6478"
D = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))
OUT = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
AUD = os.environ.get("AUDIENCE", "coach")

def tag(k): return k.split("心电图")[-1].replace(".pdf", "").replace("(1)", "")
order = ["2026-09-26 08.28", "2026-09-26 10.51", "2026-09-27 19.04", "2026-09-28 09.55",
         "2026-09-28 18.53", "2026-09-29 11.53", "2026-09-30 08.57", "2026-09-30 22.39",
         "2026-10-01 09.03", "2026-10-02 09.50(1)"]
def kind_of(t):
    hh = int(t.split(" ")[1].split(".")[0])
    return "晨起" if hh <= 9 else ("睡前" if hh >= 18 else "白天")
def col_of(k): return MORN if k == "晨起" else (EVE if k == "睡前" else DAY)
def lookup(t):
    t = t.replace("(1)", "")
    for k, v in D.items():
        if tag(k) == t:
            return v
    raise KeyError(t)

def rsa_analysis(rr):
    """Return (breath_freq_hz, hf_amp_ms, hf_frac) from RR FFT."""
    rr = np.array(rr)
    if len(rr) < 8:
        return None, None, None
    t = np.cumsum(rr)/1000.0
    ti = np.arange(t[0], t[-1], 0.25)
    rri = np.interp(ti, t, rr) - np.mean(rr)
    w = np.hanning(len(rri))
    f = np.fft.rfftfreq(len(rri), 0.25)
    spec = np.abs(np.fft.rfft(rri*w))**2
    hf = (f >= 0.15) & (f <= 0.40)
    tot = (f >= 0.04) & (f <= 0.50)
    hf_frac = 100*spec[hf].sum()/spec[tot].sum() if spec[tot].sum() > 0 else 0
    pk = f[hf][np.argmax(spec[hf])] if spec[hf].max() > 0 else None
    hf_amp = 2*np.sqrt(max(spec[hf].max(), 0.0))/len(rri)*2  # peak amplitude in ms
    return pk, hf_amp, hf_frac

def spearman(a, b):
    ra = np.argsort(np.argsort(a)); rb = np.argsort(np.argsort(b))
    return np.corrcoef(ra, rb)[0, 1]

# ---------------- fig8: tachogram grid (all 10) ----------------
fig, axs = plt.subplots(2, 5, figsize=(13, 5.4), dpi=200)
for ax, t in zip(axs.ravel(), order):
    v = lookup(t)
    rr = np.array(v["rr_list"])
    k = kind_of(t); c = col_of(k)
    ax.plot(rr, "o-", color=c, ms=3.5, lw=0.9)
    ax.axhline(np.mean(rr), color=GRAY, lw=0.7, ls="--")
    ax.set_ylim(450, 1250)
    ax.set_title(f"{t.replace('(1)','')}  {k}", fontsize=8.8, color=BLUE, pad=3)
    ax.text(0.03, 0.88, f"HR {v['hr_calc']:.0f} · RMSSD {v['rmssd']:.0f}", transform=ax.transAxes,
            fontsize=7.6, color=c, fontweight="bold")
    ax.set_xticks([]); ax.grid(ls=":", alpha=0.35)
    for s in ax.spines.values(): s.set_color("#C7CAD4"); s.set_linewidth(0.6)
fig.suptitle("逐搏全览（tachogram）：每一次心跳的间隔，按记录顺序排列——间隔线越「平」=心跳越紧绷",
             fontsize=12.5, color=BLUE, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig8_tacho.png"), bbox_inches="tight"); plt.close(fig)
print("fig8 ok")

# ---------------- fig9: dRR grid ----------------
fig, axs = plt.subplots(2, 5, figsize=(13, 5.4), dpi=200)
for ax, t in zip(axs.ravel(), order):
    v = lookup(t)
    rr = np.array(v["rr_list"])
    drr = np.diff(rr)
    k = kind_of(t); c = col_of(k)
    ax.stem(range(len(drr)), drr, linefmt=c, markerfmt="o", basefmt=" ")
    ax.axhspan(-50, 50, color=GREEN, alpha=0.08)
    ax.axhline(0, color=GRAY, lw=0.7)
    ax.set_ylim(-260, 260)
    ax.set_title(f"{t.replace('(1)','')}  {k}", fontsize=8.8, color=BLUE, pad=3)
    ax.text(0.03, 0.88, f"pNN50 {v['pnn50']:.0f}%", transform=ax.transAxes, fontsize=7.6, color=c, fontweight="bold")
    ax.set_xticks([]); ax.grid(ls=":", alpha=0.35)
    for s in ax.spines.values(): s.set_color("#C7CAD4"); s.set_linewidth(0.6)
fig.suptitle("逐搏差分（ΔRR）：相邻间隔之差，绿色带=±50 ms（pNN50 判定带）——基线日大量大摆动，后期几乎归零",
             fontsize=12.5, color=BLUE, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fig9_drr.png"), bbox_inches="tight"); plt.close(fig)
print("fig9 ok")

# ---------------- fig10: HR vs RMSSD scatter ----------------
fig, ax = plt.subplots(figsize=(6.6, 4.6), dpi=200)
hrs, rms = [], []
for t in order:
    v = lookup(t)
    k = kind_of(t); c = col_of(k)
    hrs.append(v["hr_calc"]); rms.append(v["rmssd"])
    mk = "o" if k == "晨起" else ("D" if k == "睡前" else "^")
    ax.plot(v["hr_calc"], v["rmssd"], mk, color=c, ms=11, mec="white", mew=0.8)
    ax.annotate(t.replace("(1)", "")[5:].replace(" ", "\n"), (v["hr_calc"], v["rmssd"]),
                textcoords="offset points", xytext=(7, 5), fontsize=7.3, color=c)
r = spearman(np.array(hrs), np.array(rms))
ax.set_xlabel("平均心率 (bpm)"); ax.set_ylabel("RMSSD (ms)")
ax.set_yscale("log"); ax.set_yticks([20, 30, 50, 80, 120, 200]); ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
ax.set_title(f"心率 × 恢复指标：中等强度负相关（Spearman r = {r:.2f}）——心率越高的记录，恢复调节越低", fontsize=12, color=BLUE, fontweight="bold")
ax.grid(ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig10_hrrmssd.png"), bbox_inches="tight"); plt.close(fig)
print("fig10 ok")

# ---------------- fig11: SD1/SD2 + ratio ----------------
fig, ax = plt.subplots(figsize=(13, 4.4), dpi=200)
x = np.arange(len(order))
sd1 = [lookup(t)["sd1"] for t in order]
sd2 = [lookup(t)["sd2"] for t in order]
ratio = [sd2[i]/sd1[i] if sd1[i] > 0 else 0 for i in range(len(order))]
ax.bar(x-0.19, sd1, 0.36, color=MORN, label="SD1（短程·逐搏调节）")
ax.bar(x+0.19, sd2, 0.36, color=EVE, label="SD2（长程·整体波动）")
ax2 = ax.twinx()
ax2.plot(x, ratio, "s-", color=RED, lw=1.6, ms=5, label="SD2/SD1 比值")
for xi, rv in zip(x, ratio):
    ax2.annotate(f"{rv:.1f}", (xi, rv), textcoords="offset points", xytext=(0, 7), ha="center",
                 fontsize=7.5, color=RED, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([t.replace("(1)", "")[5:] for t in order], fontsize=8, rotation=35, ha="right")
ax.set_ylabel("ms"); ax.set_ylim(0, 200)
ax2.set_ylabel("SD2/SD1", color=RED); ax2.set_ylim(0, 14)
ax2.axhline(3.0, color=AMBER, ls="--", lw=1.2); ax2.text(len(order)-0.4, 3.15, "≈3 参考线", fontsize=8, color=AMBER)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="upper right", fontsize=8.5)
ax.set_title("SD1 / SD2 与二者比值：基线日 SD1=70→后期 9–20；SD2/SD1 从 1.4 升至 3.8–6.3（自主神经平衡向交感侧偏移）",
             fontsize=11.5, color=BLUE, fontweight="bold")
ax.grid(ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig11_sd.png"), bbox_inches="tight"); plt.close(fig)
print("fig11 ok")

# ---------------- fig12: respiration estimate ----------------
fig, ax = plt.subplots(figsize=(13, 4.2), dpi=200)
bf, amp, frac = [], [], []
for t in order:
    v = lookup(t)
    f0, a0, h0 = rsa_analysis(v["rr_list"])
    bf.append(f0*60 if f0 else None); amp.append(a0); frac.append(h0)
x = np.arange(len(order))
cols = [col_of(kind_of(t)) for t in order]
ax.bar(x-0.19, amp, 0.38, color=cols, label="呼吸摆动幅度（RSA, ms）")
ax2 = ax.twinx()
ax2.plot(x, bf, "o-", color=BLUE, lw=1.6, ms=6, label="估计呼吸频率（次/分）")
for xi, b in zip(x, bf):
    if b: ax2.annotate(f"{b:.0f}", (xi, b), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=7.5, color=BLUE)
ax.set_xticks(x); ax.set_xticklabels([t.replace("(1)", "")[5:] for t in order], fontsize=8, rotation=35, ha="right")
ax.set_ylabel("RSA 幅度 (ms)")
ax2.set_ylabel("估计呼吸频率 (次/分)", color=BLUE); ax2.set_ylim(0, 30)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="upper left", fontsize=8.5)
ax.set_title("呼吸与心跳的耦合（呼吸性窦性心律不齐）：基线日呼吸摆动幅度 58–168 ms，后期降至 4–30 ms——迷走对窦房结的调节变弱",
             fontsize=11.5, color=BLUE, fontweight="bold")
ax.grid(ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig12_rsa.png"), bbox_inches="tight"); plt.close(fig)
print("fig12 ok")

# ---------------- fig13: baseline deviation with noise bands (coach) ----------------
fig, axs = plt.subplots(1, 2, figsize=(13, 4.0), dpi=200)
morn_t = [t for t in order if kind_of(t) == "晨起"]
mhr = [lookup(t)["hr_calc"] for t in morn_t]
mrm = [lookup(t)["rmssd"] for t in morn_t]
hr_dev = [100*(h/mhr[0]-1) for h in mhr]
rm_dev = [100*(r/mrm[0]-1) for r in mrm]
xs = np.arange(len(morn_t))
axs[0].bar(xs, hr_dev, 0.5, color=RED, alpha=0.85)
axs[0].axhspan(-4.6, 4.6, color=GRAY, alpha=0.15); axs[0].axhspan(-3.1, 3.1, color=GREEN, alpha=0.18)
axs[0].axhline(0, color=GRAY, lw=1)
axs[0].annotate("±TE(3bpm→±4.6%)", (len(xs)-1, 4.6), fontsize=7.5, color=GRAY, va="bottom", ha="right")
axs[0].annotate("±SWC(2bpm→±3.1%)", (len(xs)-1, 3.1), fontsize=7.5, color="#5C8F00", va="bottom", ha="right")
for xi, dv in zip(xs, hr_dev):
    axs[0].text(xi, dv + (1.4 if dv >= 0 else -1.4), f"{dv:+.0f}%", ha="center", fontsize=8.5, color=RED, fontweight="bold")
axs[0].set_xticks(xs); axs[0].set_xticklabels([t[5:] for t in morn_t], fontsize=9)
axs[0].set_ylim(-12, 40); axs[0].set_title("晨起心率相对基线的偏离（%）", fontsize=11, color=BLUE, fontweight="bold")
axs[0].grid(ls=":", alpha=0.4)
axs[1].bar(xs, rm_dev, 0.5, color=MORN, alpha=0.85)
axs[1].axhspan(-6.0, 6.0, color=GRAY, alpha=0.15); axs[1].axhspan(-2.8, 2.8, color=GREEN, alpha=0.18)
axs[1].axhline(0, color=GRAY, lw=1)
axs[1].annotate("±TE(6.0%)", (len(xs)-1, 6.0), fontsize=7.5, color=GRAY, va="bottom", ha="right")
axs[1].annotate("±SWC(2.8%)", (len(xs)-1, 2.8), fontsize=7.5, color="#5C8F00", va="bottom", ha="right")
for xi, dv in zip(xs, rm_dev):
    axs[1].text(xi, dv + (1.2 if dv >= 0 else -1.2), f"{dv:+.0f}%", ha="center", fontsize=8.5, color=MORN, fontweight="bold")
axs[1].set_xticks(xs); axs[1].set_xticklabels([t[5:] for t in morn_t], fontsize=9)
axs[1].set_ylim(-95, 15); axs[1].set_title("晨起 RMSSD 相对基线的偏离（%）", fontsize=11, color=BLUE, fontweight="bold")
axs[1].grid(ls=":", alpha=0.4)
fig.suptitle("相对基线的偏离与噪声带（TE=日间典型误差，SWC=最小有价值变化，Schneider 2019 表 3 卧位值）——RMSSD 的 −76% 是 SWC 的 27 倍",
             fontsize=11.5, color=BLUE, fontweight="bold", y=1.04)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig13_dev.png"), bbox_inches="tight"); plt.close(fig)
print("fig13 ok")

# ---------------- fig14: overnight recovery pairs ----------------
pairs = [("2026-09-27 19.04", "2026-09-28 09.55"), ("2026-09-30 22.39", "2026-10-01 09.03")]
fig, ax = plt.subplots(figsize=(6.6, 4.2), dpi=200)
for i, (e, m) in enumerate(pairs):
    ve = D[[k for k in D if tag(k) == e][0]]; vm = D[[k for k in D if tag(k) == m][0]]
    ax.bar([i-0.18, i+0.18], [ve["rmssd"], vm["rmssd"]], 0.3, color=[EVE, MORN])
    d = vm["rmssd"]-ve["rmssd"]
    ax.annotate(f"+{d:.1f}", (i, max(ve["rmssd"], vm["rmssd"])+2), ha="center", fontsize=9, color="#5C8F00", fontweight="bold")
    ax.text(i-0.18, ve["rmssd"]+1, f"{ve['rmssd']:.0f}", ha="center", fontsize=8.5, color=EVE)
    ax.text(i+0.18, vm["rmssd"]+1, f"{vm['rmssd']:.0f}", ha="center", fontsize=8.5, color=MORN)
ax.set_xticks([0, 1]); ax.set_xticklabels(["9-27晚 → 9-28晨", "9-30晚 → 10-1晨"])
ax.set_ylabel("RMSSD (ms)"); ax.set_ylim(0, 45)
ax.set_title("夜间恢复检查（睡前 → 次日晨起）：两晚仅回升 +6.7 / +8.3 ms，离基线 117.7 相距甚远——夜间睡眠未完成恢复任务（n=2，仅供方向参考）",
             fontsize=10.5, color=BLUE, fontweight="bold")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=EVE, label="睡前"), Patch(color=MORN, label="次日晨起")], fontsize=8.5)
ax.grid(ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig14_overnight.png"), bbox_inches="tight"); plt.close(fig)
print("fig14 ok")
