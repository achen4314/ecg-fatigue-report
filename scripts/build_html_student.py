# -*- coding: utf-8 -*-
"""Build the STUDENT-facing fatigue report HTML (no coach jargon)."""
import base64, json, os

B = r"C:\Users\admin\AppData\Local\Temp\ecg_work\build"
L = r"C:\Users\admin\AppData\Local\Temp\ecg_work\lit\figs"
OUT_HTML = os.path.join(B, "report_student.html")

def b64(p):
    with open(p, "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

IMG = {n: b64(os.path.join(B, n)) for n in ["fig2_week-s.png", "fig3_morning-s.png",
      "fig4_morneve-s.png", "fig5_poincare-s.png", "fig6_annotated_ecg.png", "fig7_norms-s.png",
      "fig8_tacho.png", "fig10_hrrmssd.png", "fig12_rsa.png", "fig15_all_strips.png",
      "fig16_beat.png", "fig17_hist.png"]}
LIT = {n: b64(os.path.join(L, n)) for n in ["munoz_fig2_0.png", "schneider_fig2_0.png"]}

D = json.load(open(r"C:\Users\admin\AppData\Local\Temp\ecg_work\metrics.json", encoding="utf-8"))
S = json.load(open(os.path.join(B, "summary.json"), encoding="utf-8"))

order = ["2026-09-26 08.28", "2026-09-26 10.51", "2026-09-27 19.04", "2026-09-28 09.55",
         "2026-09-28 18.53", "2026-09-29 11.53", "2026-09-30 08.57", "2026-09-30 22.39",
         "2026-10-01 09.03", "2026-10-02 09.50(1)"]
def tag(k): return k.split("心电图")[-1].replace(".pdf", "").replace("(1)", "")
by_tag = {tag(k): v for k, v in D.items()}
rows_html = ""
for t in order:
    v = by_tag[t.replace("(1)", "")]
    t2 = t.replace("(1)", "")
    hh = int(t2.split(" ")[1].split(".")[0])
    kind = "晨起" if hh <= 9 else ("睡前" if hh >= 18 else "白天")
    kc = "#2F6FED" if kind == "晨起" else ("#7C5CFC" if kind == "睡前" else "#5B6478")
    rows_html += f"""<tr>
      <td style="white-space:nowrap">{t2}</td>
      <td><span class="tag" style="background:{kc}1A;color:{kc};border:1px solid {kc}55">{kind}</span></td>
      <td>{v['hr_calc']:.0f}</td><td><b>{v['rmssd']}</b></td><td>{v['sdnn']}</td>
      <td>{v['hr_min']}–{v['hr_max']}</td></tr>"""

html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=750, initial-scale=1">
<title>连晨阳 · 一周心率与恢复状态报告</title>
<style>
:root {{ --ink:#1A1D29; --mut:#5A6172; --blue:#171B40; --green:#A0FF00; --green-d:#5C8F00;
  --red:#E5484D; --amber:#F5A524; --card:#FFFFFF; --line:#DDE1E8; --soft:#F4F6FA; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:"Microsoft YaHei","PingFang SC",sans-serif; background:#EDF0F5; color:var(--ink);
  font-size:14px; line-height:1.8; }}
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
ul, ol {{ margin:6px 0 6px 22px; }}
li {{ margin:5px 0; }}
.check li {{ list-style:none; position:relative; padding-left:26px; }}
.check li::before {{ content:"☐"; position:absolute; left:2px; color:var(--blue); font-size:15px; }}
.refs {{ font-size:11.5px; color:#4A5060; }}
.refs li {{ margin:6px 0; }}
.note {{ font-size:12px; color:var(--mut); background:#FFF9E8; border:1px dashed #E4CD8F;
  border-radius:10px; padding:10px 14px; margin:12px 0; }}
.kv {{ display:flex; font-size:13px; margin:4px 0; }}
.kv .k {{ width:110px; color:var(--mut); flex:none; }}
.kv .v {{ font-weight:600; }}
</style></head><body><div class="page">

<div class="hero">
  <h1>连晨阳 · 一周心率与恢复状态报告</h1>
  <div class="sub">基于你的 Apple Watch 单导联心电图 10 份 · 2026-09-26 ~ 10-02 · 男，28 岁</div>
  <div class="verdict">
    <div class="box"><div class="k">晨起心率（一周变化）</div><div class="v red">65 → 81 bpm&nbsp; +25.7%</div></div>
    <div class="box"><div class="k">恢复调节水平（RMSSD）</div><div class="v red">117.7 → 31.4 ms&nbsp; −73%</div></div>
    <div class="box"><div class="k">身体在说什么</div><div class="v amber">累了，需要主动恢复</div></div>
  </div>
</div>

<div class="wrap">
<div class="lead"><b>给你的三句话：</b>① 这一周，你的心脏在「提速」运转——晨起心率从 65 升到 81 次/分，说明身体承受的压力在累积；② 你的「恢复开关」（医学上叫迷走神经调节）从很高的水平回落到低位，恢复能力暂时变弱了；③ <b>这不是疾病，是可逆的疲劳累积——你的心脏节律每次都是正常的</b>。报告后面有明确的 7 天行动清单，照着做，两周后我们再看一次数据。</div>

<h2>一、这份报告怎么读</h2>
<p>你的 Apple Watch 每次测量会生成一段 30 秒的心电图。这段波形里藏着两个关键信息：</p>
<ul>
<li><b>心率</b>——每分钟跳多少次，反映身体的「运行档位」；</li>
<li><b>RMSSD</b>——相邻两次心跳间隔的差异有多大，医学上叫「心率变异性」。心跳间隔越自由地摆动，说明你的「恢复开关」（迷走神经）越活跃；间隔越死板均匀，说明身体越紧绷、恢复开关关得越小。RMSSD 数值越大 = 恢复状态越好。</li>
</ul>
<p>健康心脏的心跳<b>本来就不该像节拍器一样均匀</b>。下面所有结论，都来自对你 10 段心电图的逐跳分析，并且经过了与设备本身读数的交叉核对。</p>

<h2>二、这些数据可靠吗</h2>
<p>三件事让你放心：① 10 段心电图全部由波形<b>逐点数字化</b>后重新计算，从你心电图算出的心率与手表标注的心率<b>全部只差 ±2 次/分以内</b>；② 30 秒短测量算出的 RMSSD 已被大样本研究证明与 5 分钟「金标准」高度一致（下图，相关系数 r=0.93）；③ 心率读数本身，Apple Watch 与专业胸带标准相差仅 0.08 次/分（O'Grady 2024）。</p>
<img class="fig" src="{LIT['munoz_fig2_0.png']}">
<div class="figcap"><b>文献原图（Munoz et al., PLoS ONE 2015，3,387 人）：</b>证明 30 秒短记录的 RMSSD 足够可靠，可作为 5 分钟标准的替代——本报告用它作为恢复状态的主指标。<span class="src">出处：Munoz ML, et al. PLoS ONE. 2015;10(9):e0138921. CC BY 4.0。</span></div>

<h2>三、一周全景：你的身体发生了什么</h2>
<img class="fig" src="{IMG['fig2_week-s.png']}">
<div class="figcap"><b>图：</b>蓝线=你的平均心率，绿线=你的 RMSSD（恢复调节水平）。绿色浅带=健康成人正常区间。三个变化：心率整体抬升；RMSSD 从很高跌入区间中下部后保持平稳；睡前（紫色）两项都比晨起（蓝色）差。</div>
<h3>10 次测量的全部数据</h3>
<table>
<tr><th>记录时间</th><th>时段</th><th>平均心率</th><th>RMSSD</th><th>SDNN</th><th>心率波动范围</th></tr>
{rows_html}
</table>
<div class="tbl-note">心率单位=次/分，RMSSD/SDNN 单位=毫秒（ms）。「心率波动范围」是这次 30 秒内最慢与最快瞬间心率的跨度——跨度大说明心跳自由摆动，跨度小说明心跳紧绷均匀。时段划分：晨起 ≤09:59；睡前 ≥18:00；其余为白天。</div>

<h2>四、发现一：你的心脏这一周在「提速」</h2>
<img class="fig" src="{IMG['fig3_morning-s.png']}">
<div class="figcap"><b>图：</b>五次晨起测量：心率 65 → 68 → 68 → 72 → 81，一路走高；RMSSD 从 117.7 回落到 28–35 后保持平稳。运动科学里，晨起心率持续上升是「负荷在累积、身体还没完全恢复」的经典信号——文献中的超负荷训练周呈现完全相同的模式（见下图）。</div>
<img class="fig" src="{LIT['schneider_fig2_0.png']}">
<div class="figcap"><b>文献原图（Schneider et al., Front Physiol 2019）：</b>37 名运动员在「超负荷训练周」的心率（左）与恢复指标（右）变化——训练负荷加大时心率上升、恢复指标下降，休息周后恢复。你的这一周与之同构，只是程度较轻、且完全可逆。<span class="src">出处：Schneider C, et al. Front Physiol. 2019;10:582. CC BY 4.0。</span></div>

<h2>五、发现二：你的「恢复开关」关小了</h2>
<p><b>同样时间点的前后对比：</b>9-26 上午 10:51 与 9-29 上午 11:53，都是上午 11 点前后，条件可比——RMSSD 从 <b>207.4 掉到 53.9 ms（三天 −74%）</b>。第一天的你，心跳随呼吸大幅摆动（开关全开）；三天后，心跳变得规整（开关关小）。这不是随机波动，变化幅度是正常日间噪声的几十倍。</p>
<img class="fig" src="{IMG['fig4_morneve-s.png']}">
<div class="figcap"><b>图：</b>你与同龄人的对比。23 名健康青年男性的研究显示：<b>晨起 RMSSD 57.8、睡前 47.1，晚上只略低于早上</b>——而你的睡前三次只有 21.5 / 39.0 / 21.0，明显偏低，说明「白天的消耗 + 训练后的恢复不足」让你晚上的身体一直没能松下来。</div>
<p class="note"><b>一个积极的细节：</b>9-28 晚上你的 RMSSD 是 39.0，比前后两个晚上（21.5 / 21.0）高出一大截——说明当天有恢复性的事件（可能是午休、放松或轻松的一天）起了作用。<b>你的身体对「休息」的反应非常敏感、非常快</b>。这是好消息：只要给对恢复手段，你的状态回升也会很快。</p>

<h2>六、你的「心跳指纹」：同一颗心脏，一周前后</h2>
<img class="fig" src="{IMG['fig6_annotated_ecg.png']}">
<div class="figcap"><b>图：你的真实心电图，圈出来的是每一次心跳（R 峰），红箭头之间是相邻两次心跳的间隔（毫秒）。</b>上：9-26 晨起，间隔在 607–1100 ms 之间大幅摆动——心跳「踩着呼吸的节奏自由呼吸」；中：9-27 睡前，间隔 824–879 ms 高度均匀——心跳像节拍器一样规整；下：10-2 晨起，依旧规整、且整体更快（恢复开关仍关着，心率还在高挡位）。每个面板取的是该次记录中摆动最大的片段。</div>
<img class="fig" src="{IMG['fig5_poincare-s.png']}">
<div class="figcap"><b>图：逐搏散点图。</b>点云越散开=心跳越自由（恢复好）；越压成一条线=心跳越紧绷。9-26 晨（最散）→ 9-27 晚 / 9-30 晨（几乎成线）→ 10-2 晨（略松开但整体更快）。与上面的心电图互相印证。</div>


<h2>七、更细一层：你的每一次心跳</h2>
<p>前面看到的是「平均值」，这一节把每次测量里的<b>每一次心跳</b>都摊开来看——结论一致，而且更直观。</p>
<img class="fig" src="{IMG['fig8_tacho.png']}">
<div class="figcap"><b>图：逐搏全览。</b>每一张小图是你一次测量里全部心跳的间隔（毫秒）。线越「平」=心跳越紧绷。9-26 的两条（晨起+白天）上下摆幅很大——心跳在自由呼吸；9-27 晚和 9-30 晚几乎压成一条直线——心跳被「锁死」了；10-2 晨整条线更靠下——心跳又平又快。这就是「恢复开关关小」的样子。</div>
<img class="fig" src="{IMG['fig10_hrrmssd.png']}">
<div class="figcap"><b>图：心率与恢复指标的关系。</b>你的 10 次测量落成一条负相关带：心率越高，恢复指标越低。左上角是 9-26 的你（慢而舒展），右下角是一周后的你（快而紧绷）。</div>
<img class="fig" src="{IMG['fig12_rsa.png']}">
<div class="figcap"><b>图：你的呼吸和心跳曾经「合拍」。</b>健康状态下，吸气时心跳加快、呼气时心跳变慢（呼吸性窦性心律不齐），这是恢复开关工作的表现。9-26 你的呼吸摆动幅度有 58–168 毫秒（呼吸 9–11 次/分，深而慢）；后期只剩 4–30 毫秒。注意 9-28 晚上你的呼吸估计达到 20 次/分——呼吸变浅变快，也是身体紧张的一个信号。</div>
<img class="fig" src="{IMG['fig17_hist.png']}">
<div class="figcap"><b>图：心跳间隔的分布。</b>9-26 的分布又宽又有多个峰（呼吸在心跳上留痕）；后期又窄又单峰——心跳被锁死在均值附近。分布越窄，调节空间越小。</div>

<h2>八、你的全部 10 段心电图：逐跳标注</h2>
<img class="fig" src="{IMG['fig15_all_strips.png']}">
<div class="figcap"><b>图：你的 10 次测量逐一标注</b>——蓝圈是每一次心跳，红箭头之间是相邻两次心跳的间隔（毫秒）。扫一眼就能看到：前两份间隔长短交替（呼吸节奏鲜明），后面越来越齐、10-2 晨最短最密。</div>
<img class="fig" src="{IMG['fig16_beat.png']}">
<div class="figcap"><b>图：你的一次心跳长什么样（9-26 基线记录）。</b>R 峰是心室的收缩主波，T 波是心室的「复位」过程——你的 QRS-T 波群形态完整正常，这份报告所有的间隔测量，都是数这些蓝圈之间距离算出来的。</div>

<h2>九、你现在的状态：三点定位</h2>
<div class="flag">
  <div class="f f-amber"><div class="fk">🟡 身体在提醒你</div>一周内晨起心率 +16.6 次/分、恢复指标 −73%，这是「负荷累积、恢复没跟上」的典型组合——就像手机连续几天没充满电。</div>
  <div class="f f-green"><div class="fk">🟢 完全不用担心的部分</div>10 段心电图全部为正常窦性节律，无房颤迹象，心率波动范围始终在健康区间（54.6–98.8）——心脏本身一切正常。</div>
  <div class="f f-amber"><div class="fk">🟡 需要修正的环节</div>睡前的恢复水平连续偏低（三次全部 <40 ms），说明「练完之后的放松」和「睡眠恢复」是目前最大的短板，而不是训练本身。</div>
</div>
<p><b>一句话总结：</b>你处在「功能性疲劳累积」阶段——离身体透支还很远，但已经值得认真对待。现在做对恢复，3–7 天即可看到数据回升；继续硬顶，疲劳会继续加深。</p>

<h2>十、未来 7 天行动清单（照做即可）</h2>
<div class="card gray">
<h3>训练</h3>
<ul>
<li>接下来 3–5 天主动降挡：把高强度/大重量日换成轻松有氧或技术练习（心率别超过自己最大心率的 80%），或与教练商量调整计划；</li>
<li>练后的放松时间加倍：每次训练后做 10 分钟慢呼吸放松再离场。</li>
</ul>
<h3>每晚睡前 10 分钟「4-2-6 呼吸法」</h3>
<ul>
<li>仰卧，吸气 4 秒 → 屏住 2 秒 → 呼气 6 秒，循环 10 分钟（约每分钟 5 次）。这个节奏是迷走神经的「激活频率」，坚持 1 周对 RMSSD 的回升帮助最直接。</li>
</ul>
<h3>睡眠</h3>
<ul>
<li>保证 7 小时以上；睡前 2 小时不喝酒、不喝咖啡、少看屏幕。</li>
</ul>
<h3>每天两次 30 秒自测（建立你自己的健康基线）</h3>
<ul class="check">
<li>晨起：醒来后 5–10 分钟内、先排尿、不吃不喝、<b>同一姿势</b>（躺或坐，选一种固定不变）、安静 1 分钟后测 30 秒 ECG；</li>
<li>睡前：躺下安静 2 分钟后测 30 秒 ECG；</li>
<li>连续记录两周，把 PDF 交给教练或发给我，之后的报告就能对照「你自己的正常值」判断，比任何标准都准。</li>
</ul>
<h3>每天三个小记录（30 秒）</h3>
<ul class="check">
<li>① 昨晚睡了几小时？质量 1–5 分？② 今天主观疲劳感 1–10 分？③ 昨天训练强度自我感觉（轻松/适中/很累）？</li>
</ul>
</div>
<div class="card">
<div class="ct">⚠ 出现以下情况请及时就医（目前你一条都不沾）</div>
<ul>
<li>静息心率持续超过 100 次/分，或晨起心率连续 3 天不回落到 70 附近；</li>
<li>出现心慌、胸闷、胸痛、头晕眼前发黑、明显活动后气喘；</li>
<li>手表心电图提示「不确定」或「房颤」字样。</li>
</ul>
</div>

<h2>十一、诚实的说明（这份报告的边界）</h2>
<ul>
<li>你的「基线」只有 9-26 一天的数据，若那天状态特别好（比如刻意深呼吸），「回落幅度」可能被高估——但心率上升、睡前低迷、同时间点对比三条证据互相独立，总结论不受影响；</li>
<li>测量时的姿势、呼吸深浅、测量前是否活动过都会影响读数，未来按第八节的标准流程测，数据会更准；</li>
<li>10 次测量、7 天跨度，样本有限：本报告的结论是「多条证据互相印证的描述性判断」，不是医疗诊断。</li>
</ul>

<h2>附录 · 数据来源文献</h2>
<ol class="refs">
<li>Munoz ML, et al. Validity of (Ultra-)Short Recordings for Heart Rate Variability Measurements. <i>PLoS ONE</i>. 2015;10(9):e0138921.</li>
<li>Schneider C, et al. Heart Rate Variability Monitoring During Strength and High-Intensity Interval Training Overload Microcycles. <i>Front Physiol</i>. 2019;10:582.</li>
<li>Vondrasek JD, et al. Heart Rate Variability and Chronotype in Young Adult Men. <i>Healthcare</i>. 2022;10(12):2465.</li>
<li>Shaffer F, Ginsberg JP. An Overview of Heart Rate Variability Metrics and Norms. <i>Front Public Health</i>. 2017;5:258.</li>
<li>Nunan D, et al. A Quantitative Systematic Review of Normal Values for Short-Term Heart Rate Variability in Healthy Adults. <i>Pacing Clin Electrophysiol</i>. 2010;33(11):1407–1417.</li>
<li>O'Grady L, et al. The Validity of Apple Watch Series 9 and Ultra 2 for Serial Measurements of Heart Rate Variability and Resting Heart Rate. <i>Sensors</i>. 2024;24(19):6220.</li>
<li>Plews DJ, et al. Training Adaptation and Heart Rate Variability in Elite Endurance Athletes. <i>Sports Med</i>. 2013;43(9):773–781.</li>
<li>Buchheit M. Monitoring Training Status with HR Measures. <i>Front Physiol</i>. 2014;5:73.</li>
<li>Stanley J, Peake JM, Buchheit M. Cardiac Parasympathetic Reactivation Following Exercise. <i>Sports Med</i>. 2013;43(12):1259–1277.</li>
<li>Saw AE, et al. Monitoring the Athlete Training Response. <i>Br J Sports Med</i>. 2016;50(5):281–291.</li>
<li>Boudreau P, et al. A Circadian Rhythm in Heart Rate Variability Contributes to the Increased Cardiac Sympathovagal Response to Awakening in the Morning. <i>Chronobiol Int</i>. 2012;29(6):757–768.</li>
</ol>
<div class="note"><b>免责声明：</b>本报告由心电图波形数据自动分析生成，用于运动训练与恢复管理，不构成医疗诊断或治疗建议。有任何心脏不适请及时就医。</div>
<p style="font-size:11px;color:#8A8FA3;text-align:center;margin-top:22px">生成于 2026-10-03 · 数据 2026-09-26 ~ 10-02 · Apple Watch 单导联 ECG 10 份</p>
</div></div></body></html>"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)
print("student html written:", OUT_HTML, len(html), "chars")
