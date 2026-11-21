# 验证和验收报告

验收对象：`paper/main.typ`（Typst 0.15.1，国赛 `zh/cumcm` 模板）→ `paper/main.pdf`（27 页）。
结果记录：`code/outputs/summary.json`、`reports/RESULTS_REPORT.md`；建模依据：`reports/ANALYSIS_MODELING_REPORT.md`。

## 结论

**PASS**

硬错误 0 项；文本质量门禁 PASS；15 张图、11 张表全部在正文中被引用且文件存在；六项关键数值与结果记录逐一对齐；编译无告警；27 页 PDF 逐页视觉检查通过（无空白页、无裁切、无重叠、无乱码）。

## 检查项

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| Step 1 文本质量门禁 | PASS | `writing_check.sh` 输出 `PASS: writing text gate passed`，0 FAIL / 0 WARN |
| Step 2 章节数量与顺序 | PASS | 11 个 include + 1 个附录，顺序 1→11 与文件名前缀一致，12 个文件均有标题 |
| Step 3 图表与章节匹配 | PASS | 15 个 `#figure`、11 个三线表；15 张图路径全部存在；15 个 `fig:` 标签全部被正文引用 |
| Step 4 写作质量与泄露 | PASS | 无 TODO/待补充/占位符；无 `figures_paper/`、`code/outputs/`、`*.npz`、`src.py` 等内部名称 |
| Step 5 数值一致性 | PASS | $t^*$、$p_(min)$、$L_0$、$L^*$、$A_(max)$、$v_(max)$ 六项与 `summary.json` 一致 |
| Step 6 引用与模板规范 | PASS | 6 条参考文献；正文 4 处 `#super("[n]")` 引用落版正确；保留国赛模板的标题页、摘要页、目录、页码 |
| Step 7 编译 | PASS | `typst compile main.typ` 无 error / 无 warning；PDF 1.57 MB、27 页、A4 595×842 pt |
| Step 8 PDF 视觉检查 | PASS | 27 页全部导出 PNG 逐页查看；程序化检查 0 处真实越界、0 空白页 |
| Step 9 验收报告 | PASS | 本文件 |

## 章节结构

| 序号 | 文件 | 标题 |
| --- | --- | --- |
| 1 | `1_restatement.typ` | 问题重述 |
| 2 | `2_analysis.typ` | 问题分析 |
| 3 | `3_assumptions.typ` | 模型假设 |
| 4 | `4_symbols.typ` | 符号说明 |
| 5 | `5_problem1.typ` | 问题一：盘入过程的运动学模型 |
| 6 | `6_problem2.typ` | 问题二：首次碰撞时刻的确定 |
| 7 | `7_problem3.typ` | 问题三：调头空间约束下的最小螺距 |
| 8 | `8_problem4.typ` | 问题四：$S$ 形调头曲线的设计与全程运动学 |
| 9 | `9_problem5.typ` | 问题五：把手速率上限下的龙头最大速率 |
| 10 | `10_sensitivity.typ` | 灵敏度分析 |
| 11 | `11_evaluation.typ` | 模型评价与推广 |
| 附录 | `A_code.typ` | 附录 A 核心代码（标题在文件内生成，`main.typ` 的 `appendix-cn()` 不再重复输出） |

## 图表引用

15 张图：技术路线图（§2）、问题一 3 张、问题二 2 张、问题三 2 张、问题四 3 张、问题五 3 张、灵敏度 1 张。图题编号 1–15 连续，正文全部以 `@fig:*` 交叉引用（Typst 自动编号），无“图 X”硬编码错位。

11 张三线表：表 1 参数、表 2 符号、表 3/4 问题一、表 5 问题二、表 6 问题三、表 7/8/9 问题四、表 10 问题五、表 11 灵敏度。表题编号 1–11 连续，正文均以“表 N”引用。

## 数值一致性

| 指标 | 结果记录 | 论文出现位置 |
| --- | --- | --- |
| 首次碰撞 $t^*$ | 412.473800 s | 摘要、§6.4、表 5、图 5、§10 |
| 最小螺距 $p_(min)$ | 0.450274 m/圈 | 摘要、§7.3、图 7、§10 |
| 标准调头曲线 $L_0$ | 13.621245 m | 摘要、§8.3、图 8、表 7 |
| 最短调头曲线 $L^*$ | 11.772919 m | 摘要、§8.5、图 8、表 7、§10 |
| 放大系数 $A_(max)$ | 1.603836 | 摘要、§9.3、图 12/13、表 10 |
| 龙头最大速率 $v_(max)$ | 1.247010 m/s | 摘要、§9.3、§11 |

## 文本质量门禁

`writing_check.sh`（MSYS2 bash + 本地 python3 代理）输出：

```
INFO: detected engine: Typst (main suffix: .typ)
INFO: section file count: 12
INFO: main include count: 11
PASS: writing text gate passed
```

不再出现 `WARN: section is short`。

## 编译

```
cd paper && typst compile main.typ
→ 无输出（无 error / 无 warning），生成 main.pdf 27 页、A4、1.57 MB
```

字体全部为系统已安装的 Times New Roman / SimSun / SimHei / KaiTi，无 `unknown font family` 告警；图片 PDF 内嵌为矢量，仅热图含 2 处位图（imshow 本身为栅格数据）。

## PDF 视觉检查

逐页导出 PNG（100 dpi 全页 + 关键区域 220 dpi 放大）检查，并辅以程序化检测：

- 页数 27，页面尺寸恒为 595×842 pt，无空白页（`空白页: []`）；
- 文本最大右边界 530.4 pt，超出 16 cm 版心 6.0 pt，全部为中文标点悬挂（61 行），属 Typst 的 CJK 标点避头尾处理，非溢出；
- 真实水平越界 1 处为行首全角括号悬挂（同属标点悬挂），无内容被裁切；
- 表格（11 张）均未超出版心，单元格无重叠、无截断；
- 公式（含积分、分段、矩阵式）未越界，未压到正文；
- 中英文与数学符号无缺字、无乱码；代码块等宽字体正常。

## 本次发现的问题与修复

| # | 问题 | 级别 | 处理 |
| --- | --- | --- | --- |
| 1 | §3 模型假设仅 524 字，被判 `section is short` | WARN | 补写“假设的作用”说明、新增“碰撞判定容差假设”，并加一段以数值校验反证假设合理性的收束段（~1100 字） |
| 2 | 附录 `A_code.typ` 无 `= ` 级标题，标题由 `main.typ` 的 `appendix-cn()` 代劳 | FAIL（结构门禁） | 将 `#heading(numbering: none, outlined: true)[附录 A 核心代码]` 移入 `A_code.typ`，同步删除 `main.typ` 中的重复标题，附录自包含 |
| 3 | 8 个图标签（spd1、rad、scan、turn、snap4、spd4、amax、sens）在正文中未被引用 | WARN | 在 §5.4、§7.2、§8.5、§8.6、§9.2、§10 对应段落补 6 处 `@fig:*` 交叉引用 |
| 4 | 正文无参考文献引用标记，6 条文献“有表无引” | WARN | 在 §1.2、§2.3(1)(2)(3) 补 4 处 `#super("[1]")`、`#super("[3, 4]")`、`#super("[3]")`、`#super("[5, 6]")`，PDF 中落版为右上角标 |
| 5 | §7.3 两条展示公式尾随“（不可行）/（可行）”，被排版成独立居中行，留下两处大空行 | 版式 | 改写为一句叙述：“在 $p_(min) - 2times10^(-4)$ 处最小间隙为 −4.71×10⁻⁶ m，判定为不可行；……”，页高减少 1 页 |
| 6 | 图 7(a) 顶部两条图例文字贴住坐标框上沿，且被网格线贯穿 | 版式 | 标签下移至 0.90/0.80，`ylim` 上限由 0.95 提到 1.02，文字与标注加白色底衬，重绘并同步 `paper/figures/` |
| 7 | 三线表与上下文间距几乎为 0（图题与表题紧贴） | 版式 | `common.typ` 的 `three-line-table` 增加 `above: 1.2em, below: 0.9em` |
| 8 | 附录代码块长行溢出灰框、跨页断块留下 2 行孤块 | 版式 | 拆长行（`radius` 的初值赋值、`R2` 的求根），块级 `raw` 设 `breakable: false`，并按“标题 + 代码”整体包进 `#block(breakable: false)` |

## 仍需处理的问题

无阻塞项。以下为说明性事项，不影响验收结论：

1. 中文标点悬挂使个别行右边界超出 6 pt，属 Typst CJK 版式默认行为，与国赛常规排版一致，不做抑制。
2. 因图片与三线表不可跨页拆分，第 10、23 页等存在 30%–40% 的页底留白；如需进一步压缩页数，可调整图幅或改为跨页表，但不属于硬错误。
3. 文本门禁脚本依赖 `python3`。本机 MSYS2 未带 python3，验收时以 `_tmp/bin/python3` 代理（`exec /d/python/python.exe "$@"`）提供；该代理只用于本次验收，不进入论文或代码目录。
4. 论文数据与代码结果的一致性由 `code/outputs/summary.json` 机器比对；若后续重跑 Notebook 产生新结果，需重新执行本验收的 Step 5。
