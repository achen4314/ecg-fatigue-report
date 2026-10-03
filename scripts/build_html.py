# -*- coding: utf-8 -*-
"""Build the fatigue report HTML with embedded figures."""
import base64, json, os

B = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
L = r"C:\Users\admin\AppData\Local\Temp\ecg_work\lit\figs"
OUT_HTML = os.path.join(B, "report.html")

def b64(p):
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

IMG = {n: b64(os.path.join(B, n)) for n in ["fig2_week.png", "fig3_morning.png", "fig4_morneve.png",
      "fig5_poincare.png", "fig6_annotated_ecg.png", "fig7_norms.png", "fig8_tacho.png",
      "fig9_drr.png", "fig10_hrrmssd.png", "fig11_sd.png", "fig12_rsa.png", "fig13_dev.png",
      "fig14_overnight.png", "fig15_all_strips.png", "fig16_beat.png", "fig17_hist.png"]}
LIT = {n: b64(os.path.join(L, n)) for n in ["munoz_fig2_0.png", "munoz_fig3_0.png",
      "schneider_fig2_0.png", "schneider_fig3_0.png"]}

D = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))
S = json.load(open(os.path.join(B, "summary.json"), encoding="utf-8"))

# ordered records
order = ["2026-09-26 08.28", "2026-09-26 10.51", "2026-09-27 19.04", "2026-09-28 09.55",
         "2026-09-28 18.53", "2026-09-29 11.53", "2026-09-30 08.57", "2026-09-30 22.39",
         "2026-10-01 09.03", "2026-10-02 09.50(1)"]
def tag(k): return k.split("心电图")[-1].replace(".pdf", "").replace("(1)", "")
by_tag = {tag(k): v for k, v in D.items()}
rows_html = ""
for i, t in enumerate(order):
    v = by_tag[t.replace("(1)", "")]
    t2 = t.replace("(1)", "")
    hh = int(t2.split(" ")[1].split(".")[0])
    kind = "晨起" if hh <= 9 else ("睡前" if hh >= 18 else "白天")
    kc = "#2F6FED" if kind == "晨起" else ("#7C5CFC" if kind == "睡前" else "#5B6478")
    dev = round(v["hr_calc"] - v["hr_stated"], 1)
    rows_html += f"""<tr>
      <td style="white-space:nowrap">{t2}</td>
      <td><span class="tag" style="background:{kc}1A;color:{kc};border:1px solid {kc}55">{kind}</span></td>
      <td>{v['hr_stated']}</td><td>{v['hr_calc']:.1f}</td><td>{dev:+.1f}</td>
      <td>{v['meanRR']}</td><td>{v['sdnn']}</td><td><b>{v['rmssd']}</b></td>
      <td>{v['pnn50']}</td><td>{v['sd1']}</td><td>{v['sd2']}</td>
      <td>{v['hr_min']}–{v['hr_max']}</td><td>{v['n_peaks']}</td></tr>"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=750, initial-scale=1">
<title>连晨阳 · 一周心率与疲劳状态分析报告</title>
<style>
:root {{ --ink:#1A1D29; --mut:#5A6172; --blue:#171B40; --green:#A0FF00; --green-d:#5C8F00;
  --red:#E5484D; --amber:#F5A524; --card:#FFFFFF; --line:#DDE1E8; --soft:#F4F6FA; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:"Microsoft YaHei","PingFang SC",sans-serif; background:#EDF0F5; color:var(--ink);
  font-size:14px; line-height:1.75; }}
.page {{ width:750px; margin:0 auto; background:#fff; padding:0 0 40px; }}
.wrap {{ padding:0 28px; }}
h1 {{ font-size:25px; color:var(--blue); font-weight:800; letter-spacing:.5px; }}
h2 {{ font-size:17.5px; color:var(--blue); font-weight:800; margin:34px 0 14px;
  padding-left:11px; border-left:5px solid var(--green); line-height:1.35; }}
h3 {{ font-size:15px; color:var(--blue); font-weight:700; margin:18px 0 8px; }}
p {{ margin:8px 0; }}
.hero {{ background:linear-gradient(160deg,#171B40 0%,#232A5C 60%,#2C356E 100%); color:#fff;
  padding:34px 28px 28px; }}
.hero .sub {{ color:#B9C2E8; font-size:12.5px; margin-top:6px; }}
.badge {{ display:inline-block; background:var(--green); color:#171B40; font-weight:800;
  font-size:12px; padding:2px 12px; border-radius:12px; margin-left:8px; vertical-align:3px; }}
.verdict {{ display:flex; gap:10px; margin-top:18px; }}
.verdict .box {{ flex:1; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.18);
  border-radius:12px; padding:12px 14px; }}
.verdict .box .k {{ font-size:12px; color:#B9C2E8; }}
.verdict .box .v {{ font-size:19px; font-weight:800; margin-top:2px; }}
.verdict .box .v.red {{ color:#FF8A8E; }} .verdict .box .v.amber {{ color:#FFC46B; }}
.verdict .box .v.green {{ color:#A0FF00; }}
.lead {{ background:#F7F9EC; border:1.5px solid #C6DC7F; border-radius:12px; padding:16px 18px; margin:20px 0; }}
.lead b {{ color:var(--blue); }}
.card {{ border:1px solid var(--line); border-radius:12px; padding:16px 18px; margin:14px 0; background:var(--card); }}
.card.gray {{ background:var(--soft); }}
.card .ct {{ font-weight:800; color:var(--blue); font-size:14.5px; margin-bottom:8px; }}
.chain {{ display:flex; align-items:stretch; gap:0; margin:16px 0; flex-wrap:wrap; }}
.chain .node {{ background:var(--soft); border:1px solid var(--line); border-radius:10px;
  padding:10px 12px; font-size:12.5px; flex:1; min-width:120px; }}
.chain .arrow {{ align-self:center; color:var(--green-d); font-weight:900; font-size:18px; padding:0 6px; }}
table {{ width:100%; border-collapse:collapse; font-size:12.3px; margin:10px 0; }}
th {{ background:var(--blue); color:#fff; padding:7px 6px; font-weight:700; white-space:nowrap; }}
td {{ border:1px solid var(--line); padding:6px; text-align:center; }}
tr:nth-child(even) td {{ background:#FAFBFD; }}
.tbl-note {{ font-size:11.5px; color:var(--mut); margin-top:4px; }}
img.fig {{ width:100%; border-radius:8px; margin:6px 0; }}
.figcap {{ font-size:12.3px; color:var(--mut); margin:2px 0 10px; padding:8px 12px;
  background:var(--soft); border-left:3px solid var(--green-d); border-radius:0 8px 8px 0; }}
.figcap b {{ color:var(--ink); }}
.src {{ font-size:11px; color:#7A8090; margin-top:4px; display:block; }}
.flag {{ display:flex; gap:8px; margin:10px 0; }}
.flag .f {{ flex:1; border-radius:10px; padding:12px 14px; font-size:13px; }}
.f-red {{ background:#FDECEC; border:1.5px solid #F5B5B8; }}
.f-amber {{ background:#FDF6E8; border:1.5px solid #F0D9A8; }}
.f-green {{ background:#EFF9E2; border:1.5px solid #C6DC7F; }}
.f .fk {{ font-weight:800; font-size:13.5px; margin-bottom:4px; }}
.f-red .fk {{ color:#C22D32; }} .f-amber .fk {{ color:#B7791F; }} .f-green .fk {{ color:#3A5F00; }}
ul {{ margin:6px 0 6px 20px; }}
li {{ margin:4px 0; }}
.refs {{ font-size:11.5px; color:#4A5060; }}
.refs li {{ margin:6px 0; }}
.note {{ font-size:12px; color:var(--mut); background:#FFF9E8; border:1px dashed #E4CD8F;
  border-radius:10px; padding:10px 14px; margin:12px 0; }}
.kv {{ display:flex; font-size:13px; margin:4px 0; }}
.kv .k {{ width:110px; color:var(--mut); flex:none; }}
.kv .v {{ font-weight:600; }}
hr.sep {{ border:none; border-top:1px dashed var(--line); margin:20px 0; }}
</style></head><body><div class="page">

<div class="hero">
  <h1>连晨阳 · 一周心率与疲劳状态分析报告 <span class="badge">教练版</span></h1>
  <div class="sub">数据来源：Apple Watch（Watch8,3）单导联 ECG 共 10 份 · 覆盖 2026-09-26 ~ 10-02 · 男，28 岁（1998-09-05）· 由教练转交分析</div>
  <div class="verdict">
    <div class="box"><div class="k">晨起心率变化（6 天）</div><div class="v red">65 → 81 bpm&nbsp; +25.7%</div></div>
    <div class="box"><div class="k">晨起 RMSSD（基线→后四日）</div><div class="v red">117.7 → 31.4 ms&nbsp; −73%</div></div>
    <div class="box"><div class="k">综合疲劳信号判定</div><div class="v amber">黄转红预警 · 未解除</div></div>
  </div>
</div>

<div class="wrap">
<div class="lead"><b>一句话结论：</b>一周之内，学员自主神经状态出现<b>「交感驱动上行 + 迷走调节崩塌」的双向漂移</b>——晨起心率 6 天上升 16.6 bpm（远超日常噪声），迷走指标 RMSSD 从基线 117.7 ms 跌至 28–35 ms 低位徘徊（−73%~−76%），睡前 RMSSD 持续低迷（21–39 ms）。该组合是<b>训练负荷/压力累积的典型自主神经签名</b>，与文献中「超负荷微周期」的 HRV 反应模式一致。<b>判定：疲劳累积进行中，尚未解除；建议降载 + 标准化复测，暂不需要医疗转诊。</b></div>

<h2>一、证据链总览</h2>
<div class="chain">
  <div class="node"><b>① 原始信号</b><br>10 份 30s 单导联 ECG 矢量波形，512 Hz</div>
  <div class="arrow">→</div>
  <div class="node"><b>② 数字化</b><br>矢量坐标逐样本还原 → R 峰检出 → RR 间期（ms）</div>
  <div class="arrow">→</div>
  <div class="node"><b>③ 三重验证</b><br>计算心率 vs 设备标注 ±2 bpm；搏数与 30s 理论搏数一致；逐行心率一致；呼吸频段功率与 RMSSD 生理耦合</div>
  <div class="arrow">→</div>
  <div class="node"><b>④ 指标</b><br>HR · RMSSD · SDNN · pNN50 · SD1/SD2</div>
  <div class="arrow">→</div>
  <div class="node"><b>⑤ 文献锚定</b><br>超短时有效性 / 常模 / SWC 噪声阈值 / 疲劳机制</div>
  <div class="arrow">→</div>
  <div class="node"><b>⑥ 判定与建议</b><br>红黄绿分层 + 降载方案 + 复测协议</div>
</div>
<p>本报告不构成医疗诊断。所有「心律」结论（窦性心律、未见房颤迹象）均为设备算法报告（算法版本 2），未经临床医生复核；本报告仅作运动训练负荷与恢复管理用途。</p>

<h2>二、方法与数据说明（严谨性基础）</h2>
<h3>2.1 信号与数字化</h3>
<p>10 份 PDF 均为 Apple Watch 单导联（导联 I）30 秒 ECG 导出件：25 mm/s、10 mm/mV、512 Hz。波形为矢量路径，本报告将矢量坐标<b>逐样本还原（每样本 ≈1.97 ms）</b>，以 R 峰间横轴距离除以走纸速度得到 RR 间期，精度不受截图/印刷分辨率影响。网格定标经逐线测量验证：细格间距 2.83 pt（1 mm），横轴变异系数 0.18%（即时间轴几乎零误差）。</p>
<h3>2.2 三重验证（全部通过）</h3>
<table>
<tr><th>验证项</th><th>方法</th><th>结果</th></tr>
<tr><td>心率对账</td><td>RR 间期换算的平均心率 vs 设备标注心率</td><td><b>10/10 全部偏差 ≤ ±2 bpm</b>（见附录数据表）</td></tr>
<tr><td>搏数完整性</td><td>检出搏数 vs 30 s × 心率/60 的理论搏数</td><td>10/10 一致（如 86 bpm → 43 搏 ✓；62 bpm → 31 搏 ✓）；P/T 波若被误检则计数会翻倍，未发生</td></tr>
<tr><td>分段一致性</td><td>同一记录三行（各 ~10 s）独立计算的心率互比</td><td>行间差 ≤ 4 bpm 为主（10-2 晨三行 77.1/77.7/77.3），无翻倍/减半异常行</td></tr>
<tr><td>频域佐证</td><td>RR 序列 0.15–0.4 Hz（呼吸频段）功率占比</td><td>高 RMSSD 记录 → 高频占比 68–70%；低 RMSSD 记录 → 8–18%，生理耦合正确</td></tr>
</table>
<h3>2.3 30 秒短程记录是否可信？</h3>
<img class="fig" src="{LIT['munoz_fig2_0.png']}">
<div class="figcap"><b>文献原图（Munoz et al., PLoS ONE 2015, n=3,387）</b>：不同时长的 HRV 与 240–300 s 金标准的偏差与 95% 一致限（对数变换后）。<b>30 s 记录的 RMSSD 与金标准高度一致（r=0.932，Cohen's d=0.104，属"小差异"）</b>，30 s 的 SDNN 一致性中等（r=0.859，d=0.516）。结论：30 s 短程 RMSSD 是金标准的良好替代——本报告将 <b>RMSSD 作为迷走调节的主指标</b>，SDNN 作参考。<span class="src">出处：Munoz ML, van Roon A, Riese H, et al. Validity of (Ultra-)Short Recordings for Heart Rate Variability Measurements. PLoS ONE. 2015;10(9):e0138921. CC BY 4.0。</span></div>
<p>设备层面：O'Grady et al.（Sensors 2024, n=39, 316 次配对测量）验证 Apple Watch 静息心率与 Polar H10+Kubios 参考标准<b>平均差仅 −0.08 bpm</b>；同时提示手表 PPG 通道的 HRV(SDNN) 较胸带<b>平均低估 8.31 ms</b>——本报告直接基于 ECG App 的单导联波形计算 HRV，规避了 PPG 通道的系统偏差，但个体间绝对值的比较仍应谨慎，趋势比较更可靠。</p>

<h2>三、一周数据全景</h2>
<img class="fig" src="{IMG['fig2_week.png']}">
<div class="figcap"><b>图 2：</b>10 次记录的平均心率（蓝）与 RMSSD（绿）时间线。绿色浅带 = 健康成人短程 RMSSD 常模区间 19–75 ms（Nunan 2010，经 Shaffer & Ginsberg 2017 转载）。直观三件事：①心率整体抬升；②RMSSD 从高位坠入常模中下带后横盘；③睡前（紫）两条线全面劣于晨起（蓝）。</div>

<h3>3.1 全部 10 次记录指标明细</h3>
<table>
<tr><th>记录时间</th><th>时段</th><th>设备HR</th><th>计算HR</th><th>差</th><th>平均RR</th><th>SDNN</th><th>RMSSD</th><th>pNN50%</th><th>SD1</th><th>SD2</th><th>瞬时HR范围</th><th>搏数</th></tr>
{rows_html}
</table>
<div class="tbl-note">单位：HR=次/分，其余 ms。瞬时 HR 范围由最短/最长 RR 换算，反映单次记录内的节律波动幅度。时段划分：晨起 ≤09:59；睡前 ≥18:00；其余为白天。</div>

<h2>四、核心发现一：晨起心率 6 天上升 16.6 bpm（+25.7%）</h2>
<img class="fig" src="{IMG['fig3_morning.png']}">
<div class="figcap"><b>图 3：</b>晨起序列（5 次，08:28–09:50）。心率 65 → 68 → 68 → 72 → 81，单调抬升；RMSSD 117.7 → 28.2 → 32.9 → 29.3 → 35.3，崩塌后低位横盘。</div>
<div class="card"><div class="ct">变化是否超出「噪声」？——用文献 SWC 校准</div>
<p>Schneider et al.（Front Physiol 2019）在 37 名受训运动员 4 天基线期测得的<b>卧位晨测 HR 日间典型误差 TE=3 bpm（5.4%），最小有价值变化 SWC=2 bpm（2.6%）</b>。学员 +16.6 bpm 相当于 <b>5.5×TE、8×SWC</b>；RMSSD −73% 相当于 <b>12×TE（6.0%）、26×SWC（2.8%）</b>。变化量级远在测量噪声之外，<b>是真信号而非随机波动</b>。参考：该文献中力量训练超负荷组正是「卧位晨 HR 从负荷第 2 天起突破 SWC 持续升高、LnRMSSD 同步下降」——与学员本周模式同构。</p></div>
<img class="fig" src="{LIT['schneider_fig2_0.png']}">
<div class="figcap"><b>文献原图（Schneider et al., Front Physiol 2019）</b>：超负荷微周期中卧位/立位静息 HR 与 HRV 的时间进程——<b>负荷期 HR 升高、LnRMSSD 下降，恢复期回归</b>。本报告学员的「HR 升 + RMSSD 降」组合即该模式的个体镜像。<span class="src">出处：Schneider C, Wiewelhove T, Raeder C, et al. Heart Rate Variability Monitoring During Strength and High-Intensity Interval Training Overload Microcycles. Front Physiol. 2019;10:582. CC BY 4.0。</span></div>

<h2>五、核心发现二：迷走调节崩塌（基线 → 一周内 −73% 以上）</h2>
<p><b>同日同时段对照（最干净的证据）：</b>9-26 10:51 与 9-29 11:53 均为上午 11 时前后，体位与昼夜时相可比——RMSSD <b>207.4 → 53.9 ms（−74.0%）</b>，SDNN 161.3 → 66.8 ms（−59%），平均心率 62 → 68。三天内迷走张力下降四分之三，远超 SWC。</p>
<img class="fig" src="{IMG['fig4_morneve.png']}">
<div class="figcap"><b>图 4：</b>学员晨/晚 RMSSD 与同龄文献对照。Vondrasek et al.（Healthcare 2022）在 23 名健康青年男性（24.6±3.4 岁）测得<b>晨 RMSSD 57.8±32.6 vs 晚 47.1±26.0 ms（p=0.008）</b>：健康人晨高于晚是常态。学员恰相反——<b>睡前三次全部低于 40 ms（21.5 / 39.0 / 21.0，均值 27.2），比文献晚间均值低 42%，且低于自身晨起</b>，说明睡前未完成迷走再激活（恢复不足），符合「恢复不足→副交感重建延迟」的疲劳生理学（Stanley et al., Sports Med 2013 综述口径）。</div>
<p class="note"><b>一个值得注意的反弹：</b>9-28 晚 RMSSD 39.0 ms 明显高于 9-27 晚（21.5）与 9-30 晚（21.0）——同日 9-28 晨仅 28.2 ms 处于低谷。该「晚高于晨」的反常节律提示 9-28 白天可能存在恢复性事件（补觉/休息/放松），提示<b>恢复手段对迷走重建有效且敏感</b>，可写入后续干预策略。</p>

<h2>六、波形证据：同一颗心脏，一周前后的「节律面貌」</h2>
<img class="fig" src="{IMG['fig6_annotated_ecg.png']}">
<div class="figcap"><b>图 5：原始波形标注（圈 R 峰 + 逐搏 RR 毫秒值）。</b>上：9-26 晨起，RR 在 607–1100 ms 之间大幅摆动（呼吸性窦性心律不齐，逐搏差最大达 493 ms）——迷走对窦房结的"刹车/松刹"调节鲜明；中：9-27 睡前，RR 824–879 ms 高度均匀——迷走调节几乎消失，心脏近似"定速运转"；下：10-2 晨起，节律依旧均匀且整体加快（RR ≈ 640–880 ms）——交感驱动占优。每个面板选取该记录中逐搏差异最大的连续片段，RMSSD 为全记录统计（故与片段观感略有出入属正常）。</div>
<img class="fig" src="{IMG['fig5_poincare.png']}">
<div class="figcap"><b>图 6：Poincaré 散点（RRn vs RRn+1）。</b>点云沿"下一搏=本搏"对角线的离散度 = 短程变异性（SD1，即逐搏调节）。9-26 晨点云最散（SD1=70.0），9-27 晚与 9-30 晨几乎压成一条线（SD1=9.3/14.1），10-2 晨小幅恢复（SD1=20.3）但整体心率更快。四个面板对比即"迷走调节塌缩"的可视化。</div>

<h2>七、与常模对照</h2>
<img class="fig" src="{IMG['fig7_norms.png']}">
<div class="figcap"><b>图 7：</b>健康成人短程常模（Nunan 2010 系统综述，经 Shaffer & Ginsberg 2017 Table 6 转载：RMSSD 42±15 ms、SDNN 50±16 ms）。学员基线晨（9-26）远高于常模（高迷走储备），后四日晨均 RMSSD 31.4 ms 落入常模<b>低带</b>、睡前 27.2 ms 贴近常模区间下限 19 ms。注意：常模为群体均值，个体纵向对比的权重应高于横向对比——本报告的核心结论建立在学员自身基线上，常模仅作定位参考。</div>


<h2>八、逐搏级证据（更细一层）</h2>
<img class="fig" src="{IMG['fig8_tacho.png']}">
<div class="figcap"><b>图 8：逐搏全览（tachogram）——</b>10 次记录的每一个 RR 间隔按搏序连线。间隔线越「平」=心跳越紧绷。9-26 两条（晨起+白天）摆幅最大；9-27 晚、9-30 晚几乎压成直线；10-2 晨整体下移（更快）且依旧平直——疲劳期的「定速心跳」形态。</div>
<img class="fig" src="{IMG['fig9_drr.png']}">
<div class="figcap"><b>图 9：逐搏差分（ΔRR）——</b>相邻间隔之差，绿色带=±50 ms（pNN50 判定带）。基线日大量 |Δ|>100 ms 的摆动柱；9-28 起摆动柱几近消失（pNN50 0–18%）。差分塌缩=迷走逐搏调节退场的最直接证据。</div>
<img class="fig" src="{IMG['fig10_hrrmssd.png']}">
<div class="figcap"><b>图 10：心率 × RMSSD 关系——</b>10 次记录落在一条清晰的负相关带上（Spearman r=−0.53，中等强度）：心率越高的记录 RMSSD 越低。图左上方「低心率+高 RMSSD」是 9-26 的基线位置，右下角是本周后期的位置——一周内整体沿该带向右下滑移，即自主神经平衡系统性向交感侧偏移。</div>
<img class="fig" src="{IMG['fig11_sd.png']}">
<div class="figcap"><b>图 11：SD1/SD2 与比值——</b>SD1（短程逐搏调节）从基线 70.0 降至 9–20；SD2/SD1 比值从 1.4 升至 3.8–6.3，越过 ≈3 参考线——按文献口径（SD2/SD1 升高=交感激越/迷走撤退），一周内平衡显著向交感侧漂移，且 10-2 未见回落。</div>
<img class="fig" src="{IMG['fig12_rsa.png']}">
<div class="figcap"><b>图 12：呼吸与心跳的耦合——</b>由 RR 频谱 0.15–0.4 Hz 峰估计呼吸频率并测量呼吸摆动幅度（RSA）。基线日 RSA 幅度 58–168 ms（呼吸 9–11 次/分，深而慢）；后期降至 4–30 ms。注意 9-28 晚呼吸频率估计 20 次/分且 RSA 仅 9.6 ms——呼吸变浅变快本身就是应激/疲劳的伴随表现。</div>
<img class="fig" src="{IMG['fig13_dev.png']}">
<div class="figcap"><b>图 13：相对基线的偏离与噪声带——</b>晨起 HR 与 RMSSD 相对 9-26 基线的 % 偏离，阴影带=日间典型误差（TE）与最小有价值变化（SWC，Schneider 2019 卧位值）。HR +25.7% ≈ 5.5×TE；RMSSD −76% ≈ 27×SWC——两项均远超噪声，且 10-2 仍无回归迹象。</div>
<img class="fig" src="{IMG['fig14_overnight.png']}">
<div class="figcap"><b>图 14：夜间恢复检查——</b>睡前→次日晨起的 RMSSD 回升幅度：+6.7 / +8.3 ms。健康状态下夜间迷走重建应使晨起明显高于睡前（文献晨晚差 ≈10.7 ms）；本学员回升量偏小，且距离自身基线 117.7 ms 相距甚远——睡眠恢复效率不足。（仅 2 对完整数据，n=2，供方向参考。）</div>

<h2>九、全部 10 段原始心电图逐跳标注（附录）</h2>
<img class="fig" src="{IMG['fig15_all_strips.png']}">
<div class="figcap"><b>图 15：</b>10 次记录逐一标注——蓝圈=检出的每一次 R 峰，红箭头间=相邻 RR 间隔（ms），每段取该记录摆动最大片段。扫描即可看出：前两份（9-26）间隔长短交替、摆幅大；9-27 起间隔趋同；10-2 晨间隔最短且最齐。</div>
<img class="fig" src="{IMG['fig16_beat.png']}">
<div class="figcap"><b>图 16：单个心搏的解剖标注（9-26 基线记录）——</b>QRS-T 波群完整、形态正常，为本报告所有 RR 测量的「读数单元」。Q/S/T 为按波形形态的算法近似标注，供读图示意（非临床诊断测量）。</div>
<img class="fig" src="{IMG['fig17_hist.png']}">
<div class="figcap"><b>图 17：RR 间隔分布对比——</b>基线日分布宽、多峰（呼吸节律在间隔上留下双峰痕迹）；后期分布窄、单峰（心跳被锁死在均值附近）。分布宽度本身就是自主神经调节空间的可视化。</div>

<h2>十、综合判定与疲劳信号分层</h2>
<div class="flag">
  <div class="f f-red"><div class="fk">🔴 红灯信号（需立即干预）</div>晨起 HR 一周 +16.6 bpm（+25.7%）；晨起 RMSSD 较自身基线 −73%；10-2 晨 HR 81 bpm 仍未回落——<b>疲劳未解除</b>。</div>
  <div class="f f-amber"><div class="fk">🟡 黄灯信号（持续观察）</div>睡前 RMSSD 三次全 <40 ms（恢复不足）；pNN50 多日 <10%（逐搏调节弱）；9-28 晚的反弹提示恢复敏感、但未延续。</div>
  <div class="f f-green"><div class="fk">🟢 绿灯信号（排除项）</div>10 份全部窦性心律、无房颤迹象（设备算法）；无持续静息 HR>100；逐搏序列无心律失常形态；瞬时 HR 范围 54.6–98.8 属生理范围。</div>
</div>
<div class="card"><div class="ct">与「交感型训练适应不良」特征核对（Kreher & Schwartz, Sports Health 2012, 症状表复刻）</div>
<table>
<tr><th>文献列出的交感型特征</th><th>本学员数据</th><th>是否命中</th></tr>
<tr><td>静息心动过速（相对自身基线）</td><td>晨起 HR +25.7%（65→81）</td><td>✅ 命中</td></tr>
<tr><td>坐立不安 / 睡眠浅（问卷项）</td><td>暂无主观问卷数据</td><td>⚠ 待补</td></tr>
<tr><td>易激惹 / 焦虑（问卷项）</td><td>暂无主观问卷数据</td><td>⚠ 待补</td></tr>
<tr><td>恢复缓慢（客观）</td><td>睡前 RMSSD 持续低位，晚间迷走重建不足</td><td>✅ 命中</td></tr>
<tr><td>食欲下降 / 体重变化</td><td>暂无数据</td><td>⚠ 待补</td></tr>
</table>
<div class="tbl-note">依据：Kreher JB, Schwartz JB. Overtraining Syndrome: A Practical Guide. Sports Health. 2012;4(2):128–138.（症状表内容为按原文复刻，非原文图片）。命中项与文献框架一致，但"训练适应不良/过度训练"为临床综合征，需病史+主观问卷+运动表现三联确认，<b>本报告不作此诊断，仅提示处于该谱系的早期信号区</b>。</div></div>

<h2>十一、给教练的可执行建议</h2>
<div class="card gray">
<h3>9.1 立即（本周内）</h3>
<ul>
<li><b>降载：</b>未来 3–5 天按"黄转红"规则执行——强度日降为容量日、容量日降为恢复技术日（心率上限压至 ≤80% HRmax，停止高乳酸无氧段落）。</li>
<li><b>补恢复手段：</b>9-28 晚的 RMSSD 反弹证明恢复干预有效且敏感——安排午睡/睡前 10 分钟 4-2-6 慢呼吸（吸气4s-屏息2s-呼气6s，每分钟≈5 次，文献支持的迷走激活节律）。</li>
<li><b>睡眠审计：</b>确认入睡时间与时长，睡前 2h 断酒精/咖啡因/大屏。</li>
</ul>
<h3>9.2 复测标准化协议（关键——建立个体真基线）</h3>
<ul>
<li><b>每日晨起固定复测：</b>醒来后 5–10 分钟内、排尿后、未进食饮咖啡、<b>同一体位</b>（推荐仰卧或坐位二选一，全程一致）、安静 1 分钟后再录 30 s ECG，连续 ≥14 天。</li>
<li><b>睡前复测：</b>同样固定流程（仰卧 2 分钟后再录）。</li>
<li><b>配套每日三问：</b>①昨晚睡了几小时/质量 1-5 分？②今天主观疲劳 1-10？③昨天训练 RPE？——主观指标与 HRV 联判，命中率显著高于单指标（Saw et al., BJSM 2016 综述）。</li>
<li><b>判定阈值（个体化后启用）：</b>晨 HR 较 7 天均值 >3 bpm 或 RMSSD 较 7 天基线跌出 1.5 SD 记黄、2 SD 记红（Plews 2013 / Buchheit 2014 的滚动 z-score 框架）；本报告 10 次数据尚不足以定个体基线，故以 9-26 基线 + 文献 SWC 作替代。</li>
</ul>
<h3>9.3 何时建议就医（本学员暂未触发）</h3>
<ul>
<li>静息 HR 持续 >100 bpm 或晨起 HR 连续 3 天不回落到自身基线 ±5 bpm 内；</li>
<li>出现心悸、胸闷、胸痛、晕厥/黑矇、活动耐量明显下降；</li>
<li>ECG App 报"不确定/房颤"或主观不适时——设备算法分类仅供筛查，不能替代临床心电图。</li>
</ul>
</div>

<h2>十二、局限性与不确定度（如实声明）</h2>
<ul>
<li><b>基线仅 1 天：</b>9-26 的高 RMSSD（117.7 / 207.4）可能含"首次测量新鲜感/深呼吸"成分，若其并非日常典型状态，则"崩塌"幅度被高估；但 HR 上升、睡前低迷、同小时对照（−74%）三条独立证据不受此影响，结论稳健。</li>
<li><b>测量条件未标准化：</b>体位、呼吸深度、是否刚起床、测量前 30 分钟行为（饮水/咖啡因/走动）均未知；时间点有 08:28–11:53 的漂移——HRV 有昼夜节律（晨高晚低，Boudreau 2012），本报告已按时段分层并在同小时对照中规避。</li>
<li><b>样本小：</b>10 次记录、7 天跨度，无训练负荷与睡眠数据——趋势为描述性证据链，不做统计推断；结论的"强度"来自多指标互证而非单一 p 值。</li>
<li><b>设备口径：</b>单导联（导联 I）波形质量可受运动伪影/佩戴松紧影响；ECG App 的"窦性心律"分类为算法输出（版本 2），非医生诊断。</li>
<li><b>行间断层：</b>每份 30 s 波形分 3 行显示，行间衔接处的 1 个 RR 间期被舍弃（每份丢失 ≤2 个），对 RMSSD 影响 <3%，已计入。</li>
</ul>

<h2>附录 A · 参考文献</h2>
<ol class="refs">
<li>Munoz ML, van Roon A, Riese H, et al. Validity of (Ultra-)Short Recordings for Heart Rate Variability Measurements. <i>PLoS ONE</i>. 2015;10(9):e0138921. doi:10.1371/journal.pone.0138921（开放获取，CC BY；图 2 为原文原图）</li>
<li>Schneider C, Wiewelhove T, Raeder C, et al. Heart Rate Variability Monitoring During Strength and High-Intensity Interval Training Overload Microcycles. <i>Front Physiol</i>. 2019;10:582. doi:10.3389/fphys.2019.00582（开放获取，CC BY；图 2、表 3 为原文原图/原表）</li>
<li>Vondrasek JD, Alkahtani SA, Al-Hudaib AA, et al. Heart Rate Variability and Chronotype in Young Adult Men. <i>Healthcare</i>. 2022;10(12):2465. doi:10.3390/healthcare10122465（开放获取，CC BY 4.0；晨/晚 RMSSD 对照数据）</li>
<li>Shaffer F, Ginsberg JP. An Overview of Heart Rate Variability Metrics and Norms. <i>Front Public Health</i>. 2017;5:258. doi:10.3389/fpubh.2017.00258（开放获取；Nunan 常模经其 Table 6 转载）</li>
<li>Nunan D, Sandercock GRH, Brodie DA. A Quantitative Systematic Review of Normal Values for Short-Term Heart Rate Variability in Healthy Adults. <i>Pacing Clin Electrophysiol</i>. 2010;33(11):1407–1417.</li>
<li>Kreher JB, Schwartz JB. Overtraining Syndrome: A Practical Guide. <i>Sports Health</i>. 2012;4(2):128–138. doi:10.1177/1941738111434406</li>
<li>O'Grady L, et al. The Validity of Apple Watch Series 9 and Ultra 2 for Serial Measurements of Heart Rate Variability and Resting Heart Rate. <i>Sensors</i>. 2024;24(19):6220.（开放获取）</li>
<li>Plews DJ, Laursen PB, Stanley J, Kilding AE, Buchheit M. Training Adaptation and Heart Rate Variability in Elite Endurance Athletes. <i>Sports Med</i>. 2013;43(9):773–781.</li>
<li>Buchheit M. Monitoring Training Status with HR Measures: Do All Roads Lead to Rome? <i>Front Physiol</i>. 2014;5:73.</li>
<li>Stanley J, Peake JM, Buchheit M. Cardiac Parasympathetic Reactivation Following Exercise. <i>Sports Med</i>. 2013;43(12):1259–1277.</li>
<li>Saw AE, Main LC, Gastin PB. Monitoring the Athlete Training Response: Subjective Self-Reported Measures Trump Commonly Used Objective Measures. <i>Br J Sports Med</i>. 2016;50(5):281–291.</li>
<li>Boudreau P, Yeh WH, Dumont GA, Boivin DB. A Circadian Rhythm in Heart Rate Variability Contributes to the Increased Cardiac Sympathovagal Response to Awakening in the Morning. <i>Chronobiol Int</i>. 2012;29(6):757–768.</li>
</ol>
<div class="note"><b>免责声明：</b>本报告由心电图波形数据自动分析生成，用于运动训练负荷与恢复管理，不构成医疗诊断或治疗建议。任何心脏不适症状请及时就医。</div>
<p style="font-size:11px;color:#8A8FA3;text-align:center;margin-top:22px">生成于 2026-10-03 · 数据 2026-09-26 ~ 10-02 · Apple Watch 单导联 ECG 10 份</p>
</div></div></body></html>"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("html written:", OUT_HTML, len(html), "chars")

# CSV export
import csv
with open(os.path.join(B, "连晨阳-ECG指标明细.csv"), "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["记录时间", "时段", "设备HR", "计算HR", "偏差", "平均RR_ms", "SDNN_ms", "RMSSD_ms",
                "pNN50_pct", "SD1_ms", "SD2_ms", "瞬时HR最小", "瞬时HR最大", "检出搏数"])
    for t in order:
        v = by_tag[t.replace("(1)", "")]; t2 = t.replace("(1)", "")
        hh = int(t2.split(" ")[1].split(".")[0])
        kind = "晨起" if hh <= 9 else ("睡前" if hh >= 18 else "白天")
        w.writerow([t2, kind, v["hr_stated"], f"{v['hr_calc']:.1f}", f"{v['hr_calc']-v['hr_stated']:+.1f}",
                    v["meanRR"], v["sdnn"], v["rmssd"], v["pnn50"], v["sd1"], v["sd2"],
                    v["hr_min"], v["hr_max"], v["n_peaks"]])
print("csv ok")
