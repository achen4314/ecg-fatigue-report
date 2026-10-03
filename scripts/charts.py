# -*- coding: utf-8 -*-
"""Charts for the fatigue report. Output PNG assets to build/."""
import json, os
import numpy as np

AUD = os.environ.get("AUDIENCE", "coach")  # coach | student
def SFX(p):  # student version: soft titles + -s suffix
    return p.replace(".png", "-s.png") if AUD == "student" else p
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

D = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))
OUT = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
os.makedirs(OUT, exist_ok=True)

# VORK palette
BLUE = "#171B40"; GREEN = "#A0FF00"; RED = "#E5484D"; AMBER = "#F5A524"; GRAY = "#8A8FA3"
MORN = "#2F6FED"; EVE = "#7C5CFC"; DAY = "#5B6478"

# parse records
def tag(k):
    return k.split("心电图")[-1].replace(".pdf", "").replace("(1)", "")

recs = []
for k, v in D.items():
    t = tag(k).strip()
    dstr, hm = t.split(" ")
    hr = v["hr_calc"]
    mo, dd = dstr.split("-")[1], dstr.split("-")[2]
    hh = int(hm.split(".")[0])
    x = float(dd) + (0.05 if hh <= 9 else 0.45 if hh < 18 else 0.85)  # 早/白/晚 position
    kind = "早" if hh <= 9 else ("晚" if hh >= 18 else "白")
    recs.append(dict(x=x, date=dstr, time=hm, kind=kind, hr=hr, rmssd=v["rmssd"],
                     sdnn=v["sdnn"], pnn50=v["pnn50"], sd1=v["sd1"], sd2=v["sd2"], tag=t))
recs.sort(key=lambda r: (r["date"], r["time"]))

# ---------------- Fig 2: week overview, HR + RMSSD ----------------
fig, ax1 = plt.subplots(figsize=(11.5, 4.6), dpi=200)
xs = [r["x"] for r in recs]
for r in recs:
    c = MORN if r["kind"] == "早" else (EVE if r["kind"] == "晚" else DAY)
    mk = "o" if r["kind"] == "早" else ("D" if r["kind"] == "晚" else "^")
    ax1.plot(r["x"], r["hr"], mk, color=c, ms=9, zorder=3)
    ax1.annotate(f"{r['hr']:.0f}", (r["x"], r["hr"]), textcoords="offset points",
                 xytext=(0, 11), ha="center", fontsize=8, color=c, fontweight="bold")
ax1.plot(xs, [r["hr"] for r in recs], "-", color=BLUE, alpha=0.35, lw=1.2, zorder=2)
ax1.set_ylabel("平均心率 (bpm)", color=BLUE, fontsize=10)
ax1.tick_params(axis="y", labelcolor=BLUE)
ax1.set_ylim(55, 95)
ax1.grid(axis="y", ls=":", alpha=0.4)

ax2 = ax1.twinx()
for r in recs:
    c = MORN if r["kind"] == "早" else (EVE if r["kind"] == "晚" else DAY)
    mk = "s" if r["kind"] == "早" else ("D" if r["kind"] == "晚" else "^")
    ax2.plot(r["x"], r["rmssd"], mk, color=c, ms=8, zorder=3, alpha=0.95)
    ax2.annotate(f"{r['rmssd']:.0f}", (r["x"], r["rmssd"]), textcoords="offset points",
                 xytext=(0, -15), ha="center", fontsize=8, color=c)
ax2.plot(xs, [r["rmssd"] for r in recs], "--", color=GREEN, alpha=0.9, lw=1.4, zorder=2)
ax2.set_ylabel("RMSSD (ms)", color="#5C8F00", fontsize=10)
ax2.tick_params(axis="y", labelcolor="#5C8F00")
ax2.set_ylim(0, 230)
ax2.axhspan(19, 75, color=GREEN, alpha=0.07)
ax2.text(26.05, 47, "健康成人短程常模\nRMSSD 19–75 ms\n(Nunan 2010, 引自 Shaffer 2017)", fontsize=7.5, color="#5C8F00", va="center")

tick_dates = ["26", "27", "28", "29", "30", "01", "02"]
ticks = []
for dd, pos in zip(["26","27","28","29","30","01","02"], [26,27,28,29,30,31,32]):
    ticks.append(pos)
ax1.set_xticks(ticks)
ax1.set_xticklabels([f"9-{d}" if int(d)>26 else d for d in ["26","27","28","29","30","01","02"]], fontsize=9)
ax1.set_xlim(25.6, 32.6)
ax1.set_title(("连晨阳 一周心率与恢复状态全景（2026-09-26 ~ 10-02）  ●晨起 ■睡前 ▲白天" if AUD=="student"
                 else "连晨阳 一周心率与 RMSSD 全景（2026-09-26 ~ 10-02）  ●晨起 ■睡前 ▲白天"),
             fontsize=12, color=BLUE, fontweight="bold", pad=10)
fig.tight_layout()
fig.savefig(os.path.join(OUT, SFX("fig2_week.png")), bbox_inches="tight")
plt.close(fig)
print("fig2 ok")

# ---------------- Fig 3: morning trend with baseline band ----------------
morn = [r for r in recs if r["kind"] == "早"]
fig, ax = plt.subplots(figsize=(11.5, 4.4), dpi=200)
x = [r["x"] for r in morn]
hr = [r["hr"] for r in morn]
rm = [r["rmssd"] for r in morn]
ax2 = ax.twinx()
ax.plot(x, hr, "o-", color=RED, lw=2, ms=8, label="晨起心率")
for xi, h in zip(x, hr):
    ax.annotate(f"{h:.0f}", (xi, h), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=9, color=RED, fontweight="bold")
ax2.plot(x, rm, "s--", color=BLUE, lw=2, ms=8, label="晨起 RMSSD")
for xi, v in zip(x, rm):
    ax2.annotate(f"{v:.0f}", (xi, v), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=BLUE)
ax.set_ylabel("晨起平均心率 (bpm)", color=RED); ax.set_ylim(50, 95)
ax2.set_ylabel("晨起 RMSSD (ms)", color=BLUE); ax2.set_ylim(0, 140)
ax2.axhspan(19, 75, color=GREEN, alpha=0.06)
ax.set_xticks([26, 28, 30, 31, 32]); ax.set_xticklabels(["9-26", "9-28", "9-30", "10-1", "10-2"])
ax.set_xlim(25.5, 32.6)
ax.grid(ls=":", alpha=0.4)
ax.set_title(("晨起趋势：心率一周 +16 bpm（65→81，+25%），恢复调节指标 RMSSD 从高位回落至低位并保持平稳" if AUD=="student"
                 else "晨起趋势：心率 6 天 +16 bpm（65→81，+25%），RMSSD 自 117.7 崩塌至 ~30 后低位徘徊"),
             fontsize=12, color=BLUE, fontweight="bold", pad=10)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1+h2, l1+l2, loc="center left", fontsize=9, framealpha=0.9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, SFX("fig3_morning.png")), bbox_inches="tight"); plt.close(fig)
print("fig3 ok")

# ---------------- Fig 4: morning vs evening vs literature ----------------
fig, ax = plt.subplots(figsize=(11.5, 4.2), dpi=200)
me = [r["rmssd"] for r in recs if r["kind"] == "早"]
ev = [r["rmssd"] for r in recs if r["kind"] == "晚"]
ev_days = [r["tag"][:10] for r in recs if r["kind"] == "晚"]
me_days = [r["tag"][:10] for r in recs if r["kind"] == "早"]
pos = list(range(len(me)))
ax.bar([p-0.18 for p in pos], me, width=0.34, color=MORN, label=("你·晨起 (n=%d)" % len(me) if AUD=="student" else f"学员晨起 (n={len(me)})"))
xb = [r["x"] for r in recs if r["kind"] == "晚"]
ax.bar([p+0.18 for p in pos[:len(ev)]], ev, width=0.34, color=EVE, label=("你·睡前 (n=%d)" % len(ev) if AUD=="student" else f"学员睡前 (n={len(ev)})"))
# literature reference
ax.axhline(57.8, color="#2F9E44", lw=2, ls="--", label="文献：青年男性晨 RMSSD 57.8±32.6 (Vondrasek 2022)")
ax.axhline(47.1, color="#E8590C", lw=2, ls="--", label="文献：青年男性晚 RMSSD 47.1±26.0 (Vondrasek 2022)")
ax.set_xticks(pos); ax.set_xticklabels([d[5:] for d in me_days])
ax.set_ylabel("RMSSD (ms)")
ax.set_title(("你的晨/晚 RMSSD 与同龄健康青年对照（23 名健康男性，24.6±3.4 岁，Vondrasek 2022）" if AUD=="student"
                 else "学员晨/晚 RMSSD 与文献对照（23 名健康青年男性，24.6±3.4 岁，Vondrasek et al. 2022, Healthcare）"),
             fontsize=11.5, color=BLUE, fontweight="bold")
ax.grid(axis="y", ls=":", alpha=0.4); ax.legend(fontsize=8.5, loc="upper right", framealpha=0.95)
fig.tight_layout(); fig.savefig(os.path.join(OUT, SFX("fig4_morneve.png")), bbox_inches="tight"); plt.close(fig)
print("fig4 ok")

# ---------------- Fig 5: Poincare 2x2 ----------------
def poincare(ax, rec, title, c):
    rr = np.array(D[[k for k in D if tag(k).strip() == rec][0]]["rr_list"])
    x = rr[:-1]; y = rr[1:]
    ax.plot(x, y, "o", ms=5, color=c, alpha=0.75, mec="white", mew=0.4)
    ax.plot([min(x.min(),y.min()), max(x.max(),y.max())]*1, [min(x.min(),y.min()), max(x.max(),y.max())], ls="--", color=GRAY, lw=0.8)
    lo = min(x.min(), y.min())-40; hi = max(x.max(), y.max())+40
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    r = D[[k for k in D if tag(k).strip() == rec][0]]
    ax.set_title(f"{title}\nRMSSD {r['rmssd']:.0f} ms  SD1 {r['sd1']:.0f} ms", fontsize=9.5, color=BLUE)
    ax.grid(ls=":", alpha=0.35)
    ax.set_xlabel("RR$_n$ (ms)", fontsize=8); ax.set_ylabel("RR$_{n+1}$ (ms)", fontsize=8)

fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), dpi=200)
poincare(axs[0], "2026-09-26 08.28", "9-26 晨起（基线）", MORN)
poincare(axs[1], "2026-09-27 19.04", "9-27 睡前", EVE)
poincare(axs[2], "2026-09-30 08.57", "9-30 晨起", MORN)
poincare(axs[3], "2026-10-02 09.50", "10-2 晨起", MORN)
fig.suptitle(("你的逐搏心跳散点：点云越宽 = 心跳的「自由摆动」越大（恢复调节越强）" if AUD=="student" else "Poincaré 散点：点云越宽=逐搏变异性越大（迷走调节越强）"), fontsize=11.5, color=BLUE, fontweight="bold", y=1.02)
fig.tight_layout(); fig.savefig(os.path.join(OUT, SFX("fig5_poincare.png")), bbox_inches="tight"); plt.close(fig)
print("fig5 ok")

# ---------------- Fig 7: norms comparison ----------------
fig, ax = plt.subplots(figsize=(11.5, 3.8), dpi=200)
cats = ["RMSSD\n(迷走/短程)", "SDNN\n(总变异性)"]
morn_rm = [r["rmssd"] for r in recs if r["kind"] == "早"]
morn_sd = [r["sdnn"] for r in recs if r["kind"] == "早"]
base_rm, rest_rm = morn_rm[0], float(np.mean(morn_rm[1:]))
base_sd, rest_sd = morn_sd[0], float(np.mean(morn_sd[1:]))
subj_eve = float(np.mean([r["rmssd"] for r in recs if r["kind"] == "晚"]))
eve_sd = float(np.mean([r["sdnn"] for r in recs if r["kind"] == "晚"]))
norm_m, norm_s = 42, 15   # Nunan 2010 via Shaffer 2017
norm_sdnn_m, norm_sdnn_s = 50, 16
x = np.arange(2)
ax.bar(x-0.27, [base_rm, base_sd], 0.17, color=GREEN, label=("你·基线晨起 (9-26)" if AUD=="student" else "学员 基线晨起 (9-26)"))
ax.bar(x-0.09, [rest_rm, rest_sd], 0.17, color=MORN, label=("你·后四日晨起均值" if AUD=="student" else "学员 后四日晨起均值"))
ax.bar(x+0.09, [subj_eve, eve_sd], 0.17, color=EVE, label=("你·睡前均值" if AUD=="student" else "学员 睡前均值"))
ax.bar(x+0.27, [norm_m, norm_sdnn_m], 0.17, color=GRAY, label="健康成人常模均值 (Nunan 2010)")
ax.errorbar(x+0.27, [norm_m, norm_sdnn_m], yerr=[norm_s, norm_sdnn_s], fmt="none", ecolor=BLUE, capsize=4, lw=1.2)
for xi, v in zip(x-0.27, [base_rm, base_sd]):
    ax.text(xi, v+3, f"{v:.0f}", ha="center", fontsize=8, color="#3A5F00", fontweight="bold")
for xi, v in zip(x-0.09, [rest_rm, rest_sd]):
    ax.text(xi, v+3, f"{v:.0f}", ha="center", fontsize=8, color=MORN, fontweight="bold")
for xi, v in zip(x+0.09, [subj_eve, eve_sd]):
    ax.text(xi, v+3, f"{v:.0f}", ha="center", fontsize=8, color=EVE, fontweight="bold")
for xi, v in zip(x+0.27, [norm_m, norm_sdnn_m]):
    ax.text(xi, v+norm_s+7, f"{v:.0f}±{norm_s if xi==0 else norm_sdnn_s}", ha="center", fontsize=8, color=BLUE)
ax.set_xticks(x); ax.set_xticklabels(cats)
ax.set_ylim(0, 90)
ax.set_ylabel("ms")
ax.set_title(("你的一周 HRV 与健康成人常模对照（常模引自 Nunan 2010，经 Shaffer & Ginsberg 2017 转载）" if AUD=="student"
                 else "学员一周 HRV 与健康成人短程常模对照（常模引自 Nunan 2010，经 Shaffer & Ginsberg 2017 Table 6 转载）"),
             fontsize=11.5, color=BLUE, fontweight="bold")
ax.legend(fontsize=8.5, loc="upper right"); ax.grid(axis="y", ls=":", alpha=0.4)
fig.tight_layout(); fig.savefig(os.path.join(OUT, SFX("fig7_norms.png")), bbox_inches="tight"); plt.close(fig)
print("fig7 ok")

# ---------------- summary json for html ----------------
summ = dict(
    morn_hr=[(r["tag"][:10], r["hr"]) for r in morn],
    morn_rmssd=[(r["tag"][:10], r["rmssd"]) for r in morn],
    eve_rmssd=[(r["tag"][:10], r["rmssd"]) for r in recs if r["kind"]=="晚"],
    eve_hr=[(r["tag"][:10], r["hr"]) for r in recs if r["kind"]=="晚"],
    base_rmssd=morn[0]["rmssd"], rest_morn_rmssd=round(float(np.mean([r["rmssd"] for r in morn[1:]])),1),
    rmssd_drop_pct=round(100*(1-morn[1]["rmssd"]/morn[0]["rmssd"]),1),
    subj_eve_rmssd=round(float(np.mean([r["rmssd"] for r in recs if r["kind"]=="晚"])),1),
    hr_rise=round(morn[-1]["hr"]-morn[0]["hr"],1),
    hr_rise_pct=round(100*(morn[-1]["hr"]/morn[0]["hr"]-1),1),
    daytime_drop_pct=round(100*(1-53.9/207.4),1),
)
json.dump(summ, open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("summary ok", summ)
