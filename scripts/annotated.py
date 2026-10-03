# -*- coding: utf-8 -*-
"""Annotated ECG strips: R peaks circled, RR intervals arrowed, grid drawn from vector data."""
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
GRID_S = 72/25.4      # 1mm
GRID_M = 5*GRID_S     # 5mm
OUT = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
A = r"C:\Users\admin\AppData\Local\hermes\attachments"

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

def draw_strip(ax, row, pk_idx, n_beats, title, color, annotate_rr=True):
    # crop around chosen peaks
    i0, i1 = pk_idx[0], pk_idx[min(n_beats, len(pk_idx))-1]
    x0 = row[i0,0] - 18; x1 = row[i1,0] + 18
    seg = row[(row[:,0] >= x0) & (row[:,0] <= x1)]
    ymin = seg[:,1].min() - 14; ymax = seg[:,1].max() + 22
    # grid
    for gx in np.arange(np.floor(x0/GRID_S)*GRID_S, x1, GRID_S):
        ax.axvline(gx, color="#E5E7EB", lw=0.5 if abs(round(gx/GRID_S) - gx/GRID_S) > 1e-6 or round(gx/GRID_M)*GRID_M != gx else 0.9, zorder=0)
    ax.plot(seg[:,0], seg[:,1], color=color, lw=1.4, zorder=3)
    # R peaks
    rrs = []
    for j in range(n_beats):
        pi = pk_idx[j]
        px, py = row[pi,0], row[pi,1]
        ax.add_patch(Circle((px, py), 5.2, fill=False, ec="#1D4ED8", lw=1.6, zorder=6))
        if j+1 < n_beats:
            px2 = row[pk_idx[j+1],0]
            rr = (px2-px)/PT_PER_SEC*1000
            rrs.append(rr)
            # double arrow above
            yarr = ymin + 16
            ax.add_patch(FancyArrowPatch((px, yarr), (px2, yarr), arrowstyle="<->",
                        mutation_scale=11, color="#B91C1C", lw=1.4, zorder=7))
            ax.text((px+px2)/2, yarr+4.5, f"{rr:.0f} ms", ha="center", va="bottom",
                    fontsize=8.6, color="#B91C1C", fontweight="bold", zorder=7)
    ax.set_xlim(x0-2, x1+2); ax.set_ylim(ymin, ymax)
    ax.set_title(title, fontsize=10.5, color="#171B40", fontweight="bold", pad=6)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_color("#C7CAD4"); s.set_linewidth(0.8)
    # scale bar
    sb = 5*GRID_S
    ax.plot([x1-sb, x1], [ymin+2.5, ymin+2.5], color="#374151", lw=1.6, zorder=8)
    ax.text(x1-sb/2, ymin+5.5, "0.2 s", ha="center", fontsize=7.5, color="#374151", zorder=8)
    return rrs

files = {tag: glob.glob(os.path.join(A, f"*心电图{tag}.pdf"))[0] for tag in
         ["2026-09-26 08.28", "2026-09-27 19.04", "2026-10-02 09.50(1)"]}
meta = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))

rows_all, peaks_all = {}, {}
for tag, f in files.items():
    rows = extract_rows(f)
    rows_all[tag] = rows
    peaks_all[tag] = [find_rpeaks(r) for r in rows]

fig, axs = plt.subplots(3, 1, figsize=(11.5, 7.6), dpi=200)
panels = [
    ("2026-09-26 08.28", "9-26 晨起（基线）——逐搏差异大，呼吸性窦性心律不齐明显", 7),
    ("2026-09-27 19.04", "9-27 睡前——RR 高度均匀，迷走调节近乎消失", 7),
    ("2026-10-02 09.50(1)", "10-2 晨起——节律仍匀、且整体加快（HR 81）", 7),
]
rrs_out = {}
for ax, (tag, title, nb) in zip(axs, panels):
    rows = rows_all[tag]; pks = peaks_all[tag]
    # choose the 7-peak window containing the largest successive RR difference
    best = None
    for ri, row in enumerate(rows):
        p = pks[ri]
        if len(p) < nb:
            continue
        rr = np.diff([row[k,0] for k in p]) / PT_PER_SEC * 1000
        rr = rr[(rr > 280) & (rr < 2000)]
        if len(rr) < nb-1:
            continue
        diffs = np.abs(np.diff(rr))
        for w in range(len(rr) - (nb-2)):
            score = diffs[w:w+(nb-2)].max()
            if best is None or score > best[0]:
                best = (score, ri, w)
    _, ri, w = best
    rrs_out[tag] = draw_strip(ax, rows[ri], pks[ri][w:w+nb], nb, title, "#CC0A24")
    key = [k for k in meta if tag.replace("(1)","") in k][0]
    v = meta[key]
    rm = rrs_out[tag]
    ax.text(0.995, 0.03, f"HR {v['hr_calc']:.0f} bpm · RMSSD {v['rmssd']:.0f} ms · SDNN {v['sdnn']:.0f} ms · pNN50 {v['pnn50']:.0f}%",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=9,
            bbox=dict(boxstyle="round,pad=0.35", fc="#F3F4F6", ec="#C7CAD4"), zorder=9)

fig.suptitle("原始心电图标注：R 峰（蓝圈）与 RR 间期（红箭头·毫秒）——同一个人，一周前后的「节律面貌」对比\n（原图 = Apple Watch 单导联 ECG，25 mm/s，10 mm/mV；红箭头间距=相邻两次心跳间隔）",
             fontsize=12, color="#171B40", fontweight="bold", y=0.995)
fig.tight_layout(rect=[0, 0, 1, 0.955])
fig.savefig(os.path.join(OUT, "fig6_annotated_ecg.png"), bbox_inches="tight")
plt.close(fig)
print("fig6 ok, RRs:", {k: [round(r) for r in v] for k, v in rrs_out.items()})
