# -*- coding: utf-8 -*-
"""Digitize Apple Watch ECG PDFs (vector trace) -> RR intervals -> HRV metrics."""
import fitz, glob, os, json, re, sys, time
import numpy as np

FILES = sorted(glob.glob(r"C:\Users\admin\AppData\Local\hermes\attachments\健康 - 连晨阳 - 心电图*.pdf"))
PT_PER_SEC = 72/25.4*25   # 25 mm/s -> pt/s = 70.866
PT_PER_MV  = 72/25.4*10   # 10 mm/mV -> pt/mV = 28.346
OUT = r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json"

def extract_trace(page):
    red = [d for d in page.get_drawings() if d.get("color") and d["color"][1] < 0.3 and d["color"][2] < 0.3]
    pts = []
    for d in red:
        for it in d["items"]:
            if it[0] == 'l':
                pts.append((it[1].x, it[1].y)); pts.append((it[2].x, it[2].y))
            elif it[0] == 'c':
                p1,p2,p3,p4 = it[1],it[2],it[3],it[4]
                ts = np.linspace(0,1,17)[:-1]
                a=(1-ts)**3; b=3*(1-ts)**2*ts; c=3*(1-ts)*ts**2; d=ts**3
                for t in range(16):
                    pts.append((a[t]*p1.x+b[t]*p2.x+c[t]*p3.x+d[t]*p4.x,
                                a[t]*p1.y+b[t]*p2.y+c[t]*p3.y+d[t]*p4.y))
    if not pts:
        return None
    arr = np.array(pts)
    ys = arr[:,1]
    lo, hi = ys.min(), ys.max()
    # split into rows: find y-gaps (>20pt empty band)
    counts, edges = np.histogram(ys, bins=np.arange(lo-1, hi+2, 2.0))
    occupied = counts > 0
    # boundaries between rows where >15pt gap (>=8 empty 2pt-bins)
    breaks = [0]
    gap_run = 0
    for i in range(1, len(occupied)):
        if not occupied[i]:
            gap_run += 1
            if gap_run == 10:  # 20pt gap
                breaks.append(i-10)
                gap_run = 0
        else:
            gap_run = 0
    breaks.append(len(occupied)-1)
    rows = []
    for b in range(len(breaks)-1):
        ylo = edges[breaks[b]] - 2; yhi = edges[breaks[b+1]+1] + 2
        m = (ys >= ylo) & (ys <= yhi)
        row = arr[m]
        if len(row) < 50:
            continue
        row = row[np.argsort(row[:,0])]
        keep = np.ones(len(row), bool)
        keep[1:] = np.any(np.abs(np.diff(row, axis=0)) > 1e-9, axis=1)
        row = row[keep]
        rows.append(row)
    return rows

def find_rpeaks(row, dist_pt=20, prom_pt=6, win=12):
    x, y = row[:,0], row[:,1]
    n = len(x)
    if n < 30:
        return []
    local_min = (y[1:-1] <= y[:-2]) & (y[1:-1] < y[2:])
    cand = np.where(local_min)[0] + 1
    # prominence: base = max y within +-win samples (excluding 3-sample dip)
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

def validate_grid(page):
    fine = [d for d in page.get_drawings()
            if d.get("color") and d["color"][0] > 0.85 and d["color"][1] > 0.85 and d["color"][2] > 0.85
            and d.get("width") and d["width"] < 0.6]
    hs, vs = [], []
    for d in fine:
        r = d["rect"]
        if r.width < 0.3: vs.append(r.x0)
        elif r.height < 0.3: hs.append(r.y0)
    def spacing(lst):
        s = np.sort(np.unique(np.round(lst, 2)))
        if len(s) < 3: return None
        d = np.diff(s); d = d[d > 0.5]
        med = float(np.median(d))
        return (round(med, 3), round(float(np.std(d)/med), 4) if med else None)
    return spacing(hs), spacing(vs)

results = {}
t0 = time.time()
for k, f in enumerate(FILES):
    name = os.path.basename(f)
    doc = fitz.open(f); page = doc[0]
    txt = page.get_text().replace(' ', '')
    m = re.search(r'平均(\d+)次', txt)
    hr_stated = int(m.group(1)) if m else None
    rows = extract_trace(page)
    g1, g2 = validate_grid(page)
    rr_ms, amps = [], []
    all_peaks = []
    for row in rows:
        pk = find_rpeaks(row)
        for p in pk:
            all_peaks.append((float(row[p,0]), float(row[p,1])))
            l = max(0, p-12); r = min(len(row), p+13)
            base = max(row[l:p].max(), row[p+1:r].max())
            amps.append((base - row[p,1]) / PT_PER_MV)
        xs = [row[p,0] for p in pk]
        for a,b in zip(xs[:-1], xs[1:]):
            rr = (b-a)/PT_PER_SEC*1000
            if 280 < rr < 2000:
                rr_ms.append(rr)
    rr = np.array(rr_ms)
    hr_calc = float(60000/rr.mean()) if len(rr) else None
    diffs = np.abs(np.diff(rr))
    sdnn = float(rr.std(ddof=1)) if len(rr) > 1 else None
    rmssd = float(np.sqrt((diffs**2).mean())) if len(diffs) else None
    pnn50 = float(100*np.sum(diffs > 50)/len(diffs)) if len(diffs) else None
    sd1 = float(np.sqrt(0.5)*diffs.std(ddof=1)) if len(diffs) > 1 else None
    sd2 = float(np.sqrt(2*sdnn**2 - 0.5*diffs.std(ddof=1)**2)) if (len(diffs) > 1 and sdnn) else None
    hr_inst = 60000/rr
    results[name] = dict(
        hr_stated=hr_stated, hr_calc=round(hr_calc,1) if hr_calc else None,
        n_peaks=len(all_peaks), n_rr=int(len(rr_ms)),
        meanRR=round(float(rr.mean()),1) if len(rr) else None,
        sdnn=round(sdnn,1) if sdnn else None,
        rmssd=round(rmssd,1) if rmssd else None,
        pnn50=round(pnn50,1) if pnn50 is not None else None,
        sd1=round(sd1,1) if sd1 else None, sd2=round(sd2,1) if sd2 else None,
        hr_min=round(float(hr_inst.min()),1) if len(rr) else None,
        hr_max=round(float(hr_inst.max()),1) if len(rr) else None,
        r_amp_mv=round(float(np.median(amps)),2) if amps else None,
        grid_h=g1, grid_v=g2, n_rows=len(rows) if rows else 0,
        rr_list=[round(float(x),1) for x in rr_ms],
        peaks=[(round(p[0],2), round(p[1],2)) for p in all_peaks])
    doc.close()
    print(f"[{k+1}/{len(FILES)}] {name.split('心电图')[-1].replace('.pdf','')} stated={hr_stated} calc={hr_calc} "
          f"RMSSD={rmssd} SDNN={sdnn} peaks={len(all_peaks)} rows={len(rows) if rows else 0} "
          f"gridH={g1} gridV={g2} ({time.time()-t0:.0f}s)", flush=True)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(results, fh, ensure_ascii=False, indent=1)
print("saved", OUT)
