# -*- coding: utf-8 -*-
"""Deeper ECG annotations: all-10-strips appendix, single-beat anatomy, RR histograms."""
import fitz, glob, os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyArrowPatch, Circle

for fp in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"]:
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

PT_PER_SEC = 72/25.4*25
PT_PER_MV = 72/25.4*10
GRID_S = 72/25.4
A = r"C:\Users\admin\AppData\Local\hermes\attachments"
OUT = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
MORN = "#2F6FED"; EVE = "#7C5CFC"; DAY = "#5B6478"; BLUE = "#171B40"

def extract_rows(path):
    doc = fitz.open(path); page = doc[0]
    red = [d for d in page.get_drawings() if d.get("color") and d["color"][1] < 0.3 and d["color"][2] < 0.3]
    pts = []
    for d in red:
        for it in d["items"]:
            if it[0] == 'l':
                pts.append((it[1].x, it[1].y)); pts.append((it[2].x, it[2].y))
    doc.close()
    arr = np.array(pts)
    ys = arr[:,1]
    counts, edges = np.histogram(ys, bins=np.arange(ys.min()-1, ys.max()+2, 2.0))
    occupied = counts > 0
    breaks = [0]; gap_run = 0
    for i in range(1, len(occupied)):
        if not occupied[i]:
            gap_run += 1
            if gap_run == 10:
                breaks.append(i-10); gap_run = 0
        else:
            gap_run = 0
    breaks.append(len(occupied)-1)
    rows = []
    for b in range(len(breaks)-1):
        ylo = edges[breaks[b]]-2; yhi = edges[breaks[b+1]+1]+2
        m = (ys >= ylo) & (ys <= yhi)
        row = arr[m]
        row = row[np.argsort(row[:,0])]
        keep = np.ones(len(row), bool)
        keep[1:] = np.any(np.abs(np.diff(row, axis=0)) > 1e-9, axis=1)
        row = row[keep]
        if len(row) > 50 and (row[:,0].max()-row[:,0].min()) > 400:
            rows.append(row)
    return rows

def find_rpeaks(row, dist_pt=20, prom_pt=6, win=12):
    x, y = row[:,0], row[:,1]
    n = len(x)
    local_min = (y[1:-1] <= y[:-2]) & (y[1:-1] < y[2:])
    cand = np.where(local_min)[0] + 1
    peaks = []
    for i in cand:
        l = max(0, i-win); r = min(n, i+win+1)
        base = max(y[l:max(l,i-2)].max() if l < i-2 else y[i],
                   y[min(r,i+3):r].max() if r > i+3 else y[i])
        if base - y[i] >= prom_pt:
            if not peaks or x[i]-x[peaks[-1]] >= dist_pt:
                peaks.append(i)
            elif y[i] < y[peaks[-1]]:
                peaks[-1] = i
    return peaks

def kind_of(t):
    hh = int(t.split(" ")[1].split(".")[0])
    return "晨起" if hh <= 9 else ("睡前" if hh >= 18 else "白天")
def col_of(k): return MORN if k == "晨起" else (EVE if k == "睡前" else DAY)

FILES = {t: glob.glob(os.path.join(A, f"*心电图{t}.pdf"))[0] for t in
         ["2026-09-26 08.28", "2026-09-26 10.51", "2026-09-27 19.04", "2026-09-28 09.55",
          "2026-09-28 18.53", "2026-09-29 11.53", "2026-09-30 08.57", "2026-09-30 22.39",
          "2026-10-01 09.03", "2026-10-02 09.50(1)"]}
D = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))
def tag(k): return k.split("心电图")[-1].replace(".pdf", "").replace("(1)", "")
def lookup(t):
    t = t.replace("(1)", "")
    for k, v in D.items():
        if tag(k) == t:
            return v
    raise KeyError(t)

# ---------------- fig15: all 10 strips annotated ----------------
fig, axs = plt.subplots(5, 2, figsize=(13, 15.5), dpi=200)
for ax, t in zip(axs.ravel(), FILES.keys()):
    t2 = t.replace("(1)", "")
    rows = extract_rows(FILES[t])
    pks = [find_rpeaks(r) for r in rows]
    best = None
    for ri, row in enumerate(rows):
        p = pks[ri]
        if len(p) < 7:
            continue
        rr = np.diff([row[k,0] for k in p]) / PT_PER_SEC * 1000
        rr = rr[(rr > 280) & (rr < 2000)]
        if len(rr) < 6:
            continue
        diffs = np.abs(np.diff(rr))
        for w in range(len(rr)-5):
            s = diffs[w:w+5].max()
            if best is None or s > best[0]:
                best = (s, ri, w)
    _, ri, w = best
    row = rows[ri]; p = pks[ri][w:w+7]
    x0 = row[p[0],0]-14; x1 = row[p[6],0]+14
    seg = row[(row[:,0] >= x0) & (row[:,0] <= x1)]
    ymin = seg[:,1].min()-12; ymax = seg[:,1].max()+20
    for gx in np.arange(np.floor(x0/GRID_S)*GRID_S, x1, GRID_S):
        ax.axvline(gx, color="#E9EBF0", lw=0.5, zorder=0)
    ax.plot(seg[:,0], seg[:,1], color="#CC0A24", lw=1.2, zorder=3)
    for j in range(7):
        px, py = row[p[j],0], row[p[j],1]
        ax.add_patch(Circle((px, py), 4.2, fill=False, ec="#1D4ED8", lw=1.3, zorder=6))
        if j < 6:
            px2 = row[p[j+1],0]
            rr = (px2-px)/PT_PER_SEC*1000
            yarr = ymin + 13
            ax.add_patch(FancyArrowPatch((px, yarr), (px2, yarr), arrowstyle="<->",
                        mutation_scale=9, color="#B91C1C", lw=1.1, zorder=7))
            ax.text((px+px2)/2, yarr+3.5, f"{rr:.0f}", ha="center", va="bottom", fontsize=7.3,
                    color="#B91C1C", fontweight="bold", zorder=7)
    ax.set_xlim(x0-2, x1+2); ax.set_ylim(ymin, ymax)
    k = kind_of(t2); c = col_of(k)
    v = lookup(t)
    ax.set_title(f"{t2}（{k}）  HR {v['hr_calc']:.0f} · RMSSD {v['rmssd']:.0f} ms · pNN50 {v['pnn50']:.0f}%",
                 fontsize=9.3, color=c, fontweight="bold", pad=3)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#C7CAD4"); s.set_linewidth(0.6)
fig.suptitle("附录：全部 10 段原始心电图的逐跳标注（蓝圈=R 峰；红箭头间=相邻心跳间隔 ms；每段取摆动最大片段）",
             fontsize=13, color=BLUE, fontweight="bold", y=0.998)
fig.tight_layout(rect=[0, 0, 1, 0.988])
fig.savefig(os.path.join(OUT, "fig15_all_strips.png"), bbox_inches="tight"); plt.close(fig)
print("fig15 ok")

# ---------------- fig16: single beat anatomy ----------------
rows = extract_rows(FILES["2026-09-26 08.28"])
row = rows[1]; pks = find_rpeaks(row)
# pick a clean R: prefer one with symmetric neighbors
sel = pks[len(pks)//2]
x0 = row[sel,0]-80; x1 = row[sel,0]+90
seg = row[(row[:,0] >= x0) & (row[:,0] <= x1)]
# locate S: local max (y) within [R, R+50ms]
R_pt = row[sel,0]; R_y = row[sel,1]
s_cand = seg[(seg[:,0] >= R_pt) & (seg[:,0] <= R_pt+3.5*GRID_S)]
S_i = np.argmax(s_cand[:,1]) if len(s_cand) else None
# T: deepest local min in [R+120ms, R+420ms] with prominence
t_cand = seg[(seg[:,0] >= R_pt+8.5*GRID_S) & (seg[:,0] <= R_pt+30*GRID_S)]
T_i_glob = np.argmin(t_cand[:,1]) if len(t_cand) else None
# Q: local min within [R-40ms, R-8ms]
q_cand = seg[(seg[:,0] >= R_pt-2.8*GRID_S) & (seg[:,0] <= R_pt-0.6*GRID_S)]
Q_i = np.argmin(q_cand[:,1]) if len(q_cand) else None

fig, ax = plt.subplots(figsize=(11.5, 4.2), dpi=200)
for gx in np.arange(np.floor(x0/GRID_S)*GRID_S, x1, GRID_S):
    ax.axvline(gx, color="#E9EBF0", lw=0.5, zorder=0)
ymin = seg[:,1].min()-10; ymax = seg[:,1].max()+24
ax.plot(seg[:,0], seg[:,1], color="#CC0A24", lw=1.5, zorder=3)
ax.add_patch(Circle((R_pt, R_y), 5, fill=False, ec="#1D4ED8", lw=1.8, zorder=6))
ax.annotate("R 峰（心室主波）", (R_pt, R_y), xytext=(R_pt+22, R_y-34), fontsize=9.5, color="#1D4ED8",
            fontweight="bold", arrowprops=dict(arrowstyle="->", color="#1D4ED8", lw=1.2), zorder=8)
if S_i is not None:
    ax.add_patch(Circle((s_cand[S_i,0], s_cand[S_i,1]), 4, fill=False, ec="#2F9E44", lw=1.5, zorder=6))
    ax.annotate("S 波", (s_cand[S_i,0], s_cand[S_i,1]), xytext=(s_cand[S_i,0]+26, s_cand[S_i,1]+30),
                fontsize=9.5, color="#2F9E44", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#2F9E44", lw=1.2), zorder=8)
if Q_i is not None:
    ax.add_patch(Circle((q_cand[Q_i,0], q_cand[Q_i,1]), 4, fill=False, ec="#2F9E44", lw=1.3, zorder=6))
    ax.annotate("Q 波", (q_cand[Q_i,0], q_cand[Q_i,1]), xytext=(q_cand[Q_i,0]-64, q_cand[Q_i,1]+26),
                fontsize=9.5, color="#2F9E44", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#2F9E44", lw=1.2), zorder=8)
if T_i_glob is not None and len(t_cand):
    Ty = t_cand[T_i_glob,1]
    ax.add_patch(Circle((t_cand[T_i_glob,0], Ty), 4, fill=False, ec="#F59E0B", lw=1.5, zorder=6))
    ax.annotate("T 波（复极）", (t_cand[T_i_glob,0], Ty), xytext=(t_cand[T_i_glob,0]+40, Ty-36),
                fontsize=9.5, color="#B45309", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#F59E0B", lw=1.2), zorder=8)
# PR / QT intervals
pr_ms = (R_pt - (q_cand[Q_i,0] if Q_i is not None else R_pt)) / PT_PER_SEC * 1000
qt_ms = ((t_cand[T_i_glob,0] if T_i_glob is not None else R_pt) - R_pt) / PT_PER_SEC * 1000
ax.text(0.02, 0.88, "P 波（心房激动）位于 R 峰前 ~120–200 ms（本段 P 波低平，未标）", transform=ax.transAxes, fontsize=9.5, color="#5A6172")
ax.set_xlim(x0-2, x1+2); ax.set_ylim(ymin, ymax)
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_color("#C7CAD4"); s.set_linewidth(0.8)
sb = 5*GRID_S
ax.plot([x1-sb, x1], [ymin+2.5, ymin+2.5], color="#374151", lw=1.8, zorder=8)
ax.text(x1-sb/2, ymin+6.5, "0.2 s", ha="center", fontsize=8, color="#374151", zorder=8)
ax.set_title("单个心搏的解剖标注（取自 9-26 晨起基线记录；Q/S/T 为按波形形态的算法近似标注，供读图示意）",
             fontsize=12, color=BLUE, fontweight="bold")
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig16_beat.png"), bbox_inches="tight"); plt.close(fig)
print("fig16 ok")

# ---------------- fig17: RR histograms 2x2 ----------------
fig, axs = plt.subplots(2, 2, figsize=(11.5, 6.0), dpi=200)
picks = ["2026-09-26 08.28", "2026-09-27 19.04", "2026-09-30 22.39", "2026-10-02 09.50(1)"]
for ax, t in zip(axs.ravel(), picks):
    v = lookup(t)
    rr = np.array(v["rr_list"])
    k = kind_of(t.replace("(1)", "")); c = col_of(k)
    ax.hist(rr, bins=np.arange(500, 1250, 40), color=c, alpha=0.75, edgecolor="white")
    ax.axvline(rr.mean(), color=BLUE, lw=1.8, ls="--")
    ax.set_title(f"{t.replace('(1)','')}（{k}）  均值 {rr.mean():.0f} ± {rr.std():.0f} ms", fontsize=9.8, color=BLUE, fontweight="bold")
    ax.set_xlim(450, 1250); ax.set_xlabel("RR 间隔 (ms)", fontsize=8.5); ax.set_ylabel("搏数", fontsize=8.5)
    ax.grid(ls=":", alpha=0.4)
fig.suptitle("RR 间隔分布：基线日的「宽分布+多峰」=呼吸摆动大；后期「窄分布+单峰」=心跳被锁死在均值附近",
             fontsize=12.5, color=BLUE, fontweight="bold", y=1.0)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "fig17_hist.png"), bbox_inches="tight"); plt.close(fig)
print("fig17 ok")
