# -*- coding: utf-8 -*-
"""Insert deep-evidence sections into both HTML builders."""
import re

NEW_COACH_IMG = """"fig2_week.png", "fig3_morning.png", "fig4_morneve.png",
      "fig5_poincare.png", "fig6_annotated_ecg.png", "fig7_norms.png", "fig8_tacho.png",
      "fig9_drr.png", "fig10_hrrmssd.png", "fig11_sd.png", "fig12_rsa.png", "fig13_dev.png",
      "fig14_overnight.png", "fig15_all_strips.png", "fig16_beat.png", "fig17_hist.png"]"""

COACH_SECTIONS = """
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

<h2>十、综合判定与疲劳信号分层</h2>"""

STUDENT_SECTIONS = """
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

<h2>九、你现在的状态：三点定位</h2>"""

# ---- coach builder ----
src = open('ecg_work/build_html.py', encoding='utf-8').read()
src = src.replace("""IMG = {n: b64(os.path.join(B, n)) for n in ["fig2_week.png", "fig3_morning.png", "fig4_morneve.png",
      "fig5_poincare.png", "fig6_annotated_ecg.png", "fig7_norms.png"]}""", 
"IMG = {n: b64(os.path.join(B, n)) for n in [" + NEW_COACH_IMG)
src = src.replace('<h2>八、综合判定与疲劳信号分层</h2>', COACH_SECTIONS, 1)
src = src.replace('<h2>九、给教练的可执行建议</h2>', '<h2>十一、给教练的可执行建议</h2>')
src = src.replace('<h2>十、局限性与不确定度（如实声明）</h2>', '<h2>十二、局限性与不确定度（如实声明）</h2>')
open('ecg_work/build_html.py', 'w', encoding='utf-8').write(src)
print('coach builder patched')

# ---- student builder ----
src = open('ecg_work/build_html_student.py', encoding='utf-8').read()
src = src.replace("""IMG = {n: b64(os.path.join(B, n)) for n in ["fig2_week-s.png", "fig3_morning-s.png",
      "fig4_morneve-s.png", "fig5_poincare-s.png", "fig6_annotated_ecg.png", "fig7_norms-s.png"]}""",
"""IMG = {n: b64(os.path.join(B, n)) for n in ["fig2_week-s.png", "fig3_morning-s.png",
      "fig4_morneve-s.png", "fig5_poincare-s.png", "fig6_annotated_ecg.png", "fig7_norms-s.png",
      "fig8_tacho.png", "fig10_hrrmssd.png", "fig12_rsa.png", "fig15_all_strips.png",
      "fig16_beat.png", "fig17_hist.png"]}""")
src = src.replace('<h2>七、你现在的状态：三点定位</h2>', STUDENT_SECTIONS, 1)
src = src.replace('<h2>八、未来 7 天行动清单（照做即可）</h2>', '<h2>十、未来 7 天行动清单（照做即可）</h2>')
src = src.replace('<h2>九、诚实的说明（这份报告的边界）</h2>', '<h2>十一、诚实的说明（这份报告的边界）</h2>')
open('ecg_work/build_html_student.py', 'w', encoding='utf-8').write(src)
print('student builder patched')
