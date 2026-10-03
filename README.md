# ecg-fatigue-report（技能包）

学员 ECG/HRV 疲劳报告技能：输入学员近一周的 Apple Watch 单导联心电图导出 PDF（每份 30 秒），
输出**教练版 + 学员版**双份报告（HTML / A4 PDF / 2x 高清长图 / 指标 CSV），全程可重建。

## 管线

1. `scripts/digitize.py` —— PDF 矢量波形逐样本数字化 → R 峰检出 → RR 间期 → HRV 指标（metrics.json）
2. `scripts/charts.py`（AUDIENCE=coach|student）+ `charts_deep.py` + `annotated.py` + `annotated_deep.py` —— 17 张图表与逐跳标注
3. `scripts/build_html.py` / `build_html_student.py` —— 教练版 / 学员版 750px HTML
4. `scripts/print_ecg.js` / `print_ecg_student.js` —— puppeteer-core + Edge 出 A4 PDF 与 2x 长图

## 要点

- 四重验证（计算心率 vs 设备标注、搏数、三行一致性、呼吸频段耦合）全部通过才可下结论
- 方法学与阈值锚定开放文献：Munoz 2015（30s HRV 有效性）、Schneider 2019（TE/SWC 噪声阈值）、
  Nunan 2010 / Shaffer 2017（常模）、Vondrasek 2022（晨晚对照）、O'Grady 2024（设备准确性）
- 详见 `SKILL.md`（Hermes 技能本体）与 `使用说明.txt`（路径常量与运行环境）
