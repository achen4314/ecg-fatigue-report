---
name: ecg-fatigue-report
description: Use when 给学员做 ECG/HRV 疲劳报告。心电图 PDF→HRV→逐搏标注双版本报告。
version: 1.0.0
---

# ECG 疲劳报告（学员心率/HRV 一周分析）

输入=学员近一周的 Apple Watch 单导联 ECG 导出 PDF（每份 30s）；输出=教练版+学员版双份报告（HTML 750px + A4 PDF + 2x 长图 + CSV + 可重建脚本）。2026-10 首次跑通（连晨阳，10 份，全部验证通过）。

## 管线（scripts/ 顺序执行）

1. `digitize.py`：PDF→metrics.json。矢量波形逐样本还原（红色路径，line 项），行拆分，R 峰检出，RR 序列 + HRV 指标。
2. `charts.py`（AUDIENCE=coach|student 切换标题措辞）+ `charts_deep.py`（逐搏级 7 图）+ `annotated.py`（3 段标注 ECG）+ `annotated_deep.py`（全 10 段标注/单搏解剖/RR 直方图）→ PNG 资产。
3. `build_html.py`（教练版）/ `build_html_student.py`（学员版）→ 750px HTML，图全 base64。
4. `print_ecg.js` / `print_ecg_student.js`（puppeteer-core + Edge，$LOCALAPPDATA/Temp/vork_demo/pw）→ A4 PDF + deviceScaleFactor=2 全页长图 PNG。
5. 交付桌面文件夹（新文件名不覆盖），脚本+metrics.json+lit_figs 一并归档。

## PDF 波形数字化要点

- 结构：792×612pt；波形=红色矢量路径（stroke ≈(0.80,0.04,0.13)、width 1pt、每条 127 个 'l' 项=512Hz 采样块、块宽 17.6pt 首尾相接）。定标：1mm=2.8346pt；25mm/s→70.866pt/s；10mm/mV→28.346pt/mV。先用细网格线（灰 0.9、宽 0.5）间距验证（纵向网格 CV≈0.2% 才算合格）。
- 行拆分：3 行×~10s（第 1 行 x 从 65.6 起 9.6s；后两行 40–748.5 各 10s）。y 直方图 2pt 分箱、≥20pt 空带断行；<50 点或 span<400pt 的碎片丢弃（每份另有 1-2 条平坦基线碎片，无 R 峰无害）。RR 只取同行相邻 R 峰（跨行丢 ≤2 个/份，影响 <3%）。
- R 峰：PDF y 向下→R=局部最小；prominence ≥6pt(0.21mV)、最小间距 20pt(0.28s)；RR 过滤 280–2000ms。

## 四重验证（全部通过才可下结论，写进报告方法节）

1. 计算 HR vs 设备标注 ±2bpm（10/10）；
2. 搏数=30s×HR/60（T/P 波误检会使计数翻倍）；
3. 同一记录三行独立心率互比无翻倍/减半行；
4. RR 频谱 0.15–0.4Hz 功率占比与 RMSSD 生理耦合（高 RMSSD↔HF 68–70%，低↔8–18%）。
可疑短 RR（<650ms）终审法：2pt 分箱谷底扫描，确认窗口内深谷数=期望峰数（T 波为小振幅、会破坏计数一致性）。

## 指标口径与噪声阈值（报告可引出处）

- RMSSD 为主（30s 超短时 vs 240–300s 金标准：r=0.932、d=0.104；Munoz 2015, PLoS ONE）；SDNN 仅参考（d=0.516）；辅 pNN50、SD1/SD2、SD2/SD1 比值（≈3 参考线）。
- 噪声阈值（Schneider 2019, Front Physiol, Table 3 卧位）：HR TE=3bpm、SWC=2bpm（5.4%/2.6%）；LnRMSSD TE=6.0%、SWC=2.8%——偏离报告用「% 偏离基线 + TE/SWC 阴影带」图呈现。
- 常模：Nunan 2010（RMSSD 42±15、SDNN 50±16，经 Shaffer & Ginsberg 2017 转载）；青年男性晨/晚对照：Vondrasek 2022 Healthcare（晨 57.8±32.6 vs 晚 47.1±26.0，p=0.008，晨>晚是常态）；设备准确性：O'Grady 2024 Sensors（RHR −0.08bpm；PPG 通道 SDNN 低估 8.31ms）。
- 疲劳判读模式：晨 HR 单调升 + 晨 RMSSD 崩塌后低位横盘 + 睡前 RMSSD 持续低迷 = 交感上行+迷走撤退（Schneider 超负荷微周期同构）。最干净证据=同日同时段对照（如 11 时前后 RMSSD −74%）。基线仅 1 天→不做 z-score，用「基线值+后几日均值」两段式；SD2/SD1 比值、呼吸频率估计（HF 峰）、RSA 幅度（HF 峰幅）均为加分证据。

## 图清单（教练版 17 图 / 学员版 12 图）

教练版：fig2 周全景(双轴) / fig3 晨起趋势 / fig4 晨晚vs文献 / fig5 Poincaré / fig6 三段标注ECG(R峰圈+RR箭头,取摆动最大片段,注窗口取法) / fig7 常模对照(基线/后四日/常模三组) / fig8 全10段tachogram / fig9 ΔRR(pNN50带) / fig10 HR-RMSSD散点(Spearman) / fig11 SD1/SD2+比值 / fig12 呼吸耦合(RSA幅度+呼吸频率) / fig13 基线偏离+TE/SWC带 / fig14 夜间恢复(n=2) / fig15 全10段逐跳标注 / fig16 单搏解剖(Q/S/T近似标注+免责) / fig17 RR直方图2×2。学员版=fig2-7 软化措辞 + fig8/10/12/15/16/17。文献原图：Munoz Fig2、Schneider Fig2（从 OA PDF 提取）+ 引用数值表。

## 双版本口径

- 教练版：完整方法学（四重验证表）、SWC/TE、Kreher 症状表核对、降载方案、复测标准化协议、红黄绿分层。
- 学员版：全篇「你」视角；RMSSD 译为「恢复开关」；删教练工具表；建议=7 天行动清单（降挡训练/4-2-6 呼吸/睡眠/标准化自测/每日三问/就医指征）；保留文献原图+参考文献；红线问题如实写但明确「可逆、非疾病」。
- 共同铁律：非医疗免责声明必带；10 段数据表+验证表必带；局限诚实声明（基线仅 1 天、体位呼吸未标准化、n 小）。

## 坑（实测）

- 文件名带 (1) 后缀：tag() 归一化后统一 lookup，混用会 KeyError。
- PDF 同文档 show_pdf_page 复制页报错→直接画在原页面上导出裁切图。
- 文献图源网络：plos/frontiersin PDF 可 curl；PMC/MDPI/europepmc 图片端点全被墙（europepmc fullTextXML 仅能拿文件名）；OA 图从已下载 PDF 用 page.get_image_info(xrefs=True) bbox 裁切。
- 无 vision 可用时（deepseek 账户无视觉模型）：所有「看图检查」换成程序化定量验证，不依赖 LLM 视觉。
- 标注 ECG 取窗：用「该记录逐搏差最大窗口」，且图注写明窗口取法，防被指摘 cherry-pick。
- 学员数据隐私：报告交付前确认发给谁（教练版含症状核对、学员版不含）。
- pip 装 matplotlib 用清华源 -i https://pypi.tuna.tsinghua.edu.cn/simple（uv 不在 PATH）。

## 项目位置

- 交付样板：C:\Users\admin\Desktop\连晨阳-一周疲劳报告\（双版本三件套+CSV+构建脚本）。
- 工作目录：$LOCALAPPDATA/Temp/ecg_work（输入附件在 %LOCALAPPDATA%/hermes/attachments）。
- 下期学员：换附件 PDF → 改 build 脚本里的学员名/日期 → 重跑管线；指标口径与验证链不变。