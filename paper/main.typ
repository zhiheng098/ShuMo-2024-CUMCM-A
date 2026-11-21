#let body-font = ("Times New Roman", "SimSun")
#let song-font = ("SimSun", "Times New Roman")
#let hei-font = ("SimHei", "SimSun")
#let kai-font = ("KaiTi", "SimSun")

#let cn-numbering(..nums) = {
  let ns = nums.pos()
  if ns.len() == 1 {
    numbering("一、", ns.at(0))
  } else if ns.len() == 2 {
    numbering("1.1", ns.at(0), ns.at(1))
  } else {
    numbering("1.1.1", ns.at(0), ns.at(1), ns.at(2))
  }
}

#set document(title: "“板凳龙”盘入调头全过程的运动学建模与安全边界求解", author: ())
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 2.5cm, right: 2.5cm),
  numbering: "1",
)
#set text(font: body-font, size: 12.05pt, lang: "zh")
#set par(
  first-line-indent: (amount: 2em, all: true),
  justify: true,
  leading: 0.72em,
  spacing: 0.35em,
)
#set heading(numbering: cn-numbering)
#set enum(numbering: "1.")
#set table(inset: 0.45em)
#show heading.where(level: 1): set align(center)
#show heading.where(level: 1): set text(size: 17.3pt, weight: "bold")
#show heading.where(level: 1): set block(above: 1.25em, below: 0.82em)
#show heading.where(level: 2): set text(size: 14.45pt, weight: "bold")
#show heading.where(level: 2): set block(above: 1.15em, below: 0.55em)
#show heading.where(level: 3): set text(size: 12.05pt, weight: "bold")
#show heading.where(level: 3): set block(above: 1.15em, below: 0.55em)
#show figure.caption: it => text(size: 12pt, weight: "bold")[#it]
#show raw: set text(size: 10pt, font: ("Courier New", "SimSun"))
#show raw.where(block: true): set block(
  fill: luma(97%),
  stroke: 0.8pt + luma(70%),
  inset: 0.7em,
  above: 0.7em,
  below: 0.7em,
  breakable: false,
)

#let song = (body) => text(font: song-font, body)
#let hei = (body) => text(font: hei-font, weight: "bold", body)
#let kai = (body) => text(font: kai-font, body)
#let paper-title(body) = {
  align(center)[#text(size: 17.3pt, weight: "bold")[#body]]
  v(1em)
}
#let abstract-title() = align(center)[#text(size: 14pt, weight: "bold")[摘要]]
#let keywords-cn(body) = block(above: 1em)[
  #text(font: hei-font, size: 12pt, weight: "bold")[关键字：] #body
]
#let abstract-cn(body, keywords) = {
  abstract-title()
  block(above: 0.15em)[#body]
  keywords-cn(keywords)
  pagebreak()
}
#let toc-page() = {
  show outline.entry.where(level: 1): it => link(
    it.element.location(),
    block(above: 7pt)[
      #text(font: hei-font, size: 12pt, weight: "bold")[
        #grid(
          columns: (auto, 1fr, auto),
          column-gutter: 0.5em,
          [#it.prefix()#it.body()],
          [#repeat[.]],
          [#it.page()],
        )
      ]
    ],
  )
  outline(
    title: align(center)[#text(font: hei-font, size: 17.3pt, weight: "bold")[目录]],
    depth: 3,
  )
  pagebreak()
}
#let references-cn() = [
#heading(numbering: none, outlined: true)[参考文献]
#{ set par(first-line-indent: 0pt, spacing: 0.35em); include("references.typ") }
]
#let appendix-cn(file: "sections/A_code.typ") = [
#include(file)
]

#let three-line-table(caption, columns, header, body, inset: (x: 0.35em, y: 0.52em), cell-align: center) = {
  let col-count = header.len()
  let body-rows = calc.floor(body.len() / col-count)
  let bottom-y = body-rows + 1
  let styled-header = header.map(cell => strong(cell))

  block(width: 100%, breakable: false)[
    #align(center)[
      #box[
        #align(center)[#text(font: hei-font, size: 10.5pt, weight: "bold")[#caption]]
        #v(0.6em)
        #table(
          columns: columns,
          align: cell-align,
          stroke: none,
          inset: inset,
          table.hline(y: 0, stroke: 0.8pt),
          table.hline(y: 1, stroke: 0.5pt),
          table.hline(y: bottom-y, stroke: 0.8pt),
          ..styled-header,
          ..body,
        )
      ]
    ]
  ]
}

#counter(page).update(1)

#paper-title[“板凳龙”盘入调头全过程的运动学建模与安全边界求解]

#abstract-cn[
  板凳龙由 223 块刚性板凳经 224 个把手首尾相连而成，链总长 369.16 m。本文以弧长参数化的等距螺线为统一几何底座，建立“刚性弦长递推 + 最小平移重叠量（SAT）碰撞判定 + 圆弧相切方程”的全过程运动学模型，逐问给出可复现的数值结果。

  *针对问题一*，用解析弧长函数 $G(r)$ 与牛顿反解给出螺线上任意弧长对应的位姿，将 224 个把手的位置问题化为一元弦长方程的串联求根，并引入“上一时刻解热启动 + 牛顿迭代 + 二分兜底”的三重保障，速度由隐函数求导解析得到。求得 0–300 s 共 301 个时刻、224 个节点的位置与速率，最大弦长残差 $4.88 times 10^(-13)$ m，龙头速率恒为 1 m/s，全队速率 0.996478–1.000000 m/s，速率沿链单调略降。

  *针对问题二*，将每块板凳表示为带 0.275 m 外延、0.15 m 半宽的矩形，用 8 条边法向的投影得到最小平移重叠量作为碰撞判据，先以 1 s 步长粗扫、再在首个变号区间内二分。求得*首次碰撞时刻 $t^* = 412.473800$ s*，首个接触对为龙头板凳与第 8 节龙身板凳，该时刻龙头半径 2.2887 m，接触前 $10^(-3)$ s 间隙 $+2.733 times 10^(-5)$ m、接触后 $-2.531 times 10^(-5)$ m，符号翻转正确。

  *针对问题三*，以“龙头自 $r = 16p$ 盘入至 $r = 4.5$ m 全程无碰撞”为可行域，先用 12 个螺距样本验证可行性关于 $p$ 的单调性，再二分求临界值。求得*最小螺距 $p_(min) = 0.450274$ m/圈（45.027 cm）*，区间宽度 $7.63 times 10^(-7)$ m；临界构形出现在 $t = 216.5$ s，最近板凳对为龙头板凳与第 19 节龙身板凳。

  *针对问题四*，将“与两螺线相切 + 两弧外切 + $R_1 = 2R_2$”化为一元二次方程，得到*标准调头曲线长度 $L_0 = 13.621245$ m*（$R_1 = 3.0054$、$R_2 = 1.5027$ m），并证明切点固定时 $L = alpha dot (R_1 + R_2)$ 与半径比例无关。进一步以切点内移量 $delta_1$ 为决策变量、以最小曲率半径 $R_2 >= l_1 / 2$ 为约束，求得*最短调头曲线 $L^* = 11.772919$ m*，较基准缩短 1.848326 m（13.57%），并指出该极限解在运动学上退化。

  *针对问题五*，指出速度放大系数 $A_i$ 沿链累乘、在调头段随时间剧变，1 s 采样会低估峰值，故在细网格上取峰并给出步长收敛表。标准调头曲线在 $Delta t <= 0.5$ s 后完全收敛，得 *$A_(max) = 1.603836$（第 6 节龙身、$t = 14.50$ s）*，从而*龙头最大速率 $v_(max) = 2 / A_(max) = 1.247010$ m/s*；中心差分校验相对偏差 $5.2 times 10^(-5)$，以 $v_(max)$ 驱动时峰值时刻最大把手速率恰为 2.000000 m/s。

  最后对接触容差、时间步长、板宽、曲率下限逐项做灵敏度分析，结果表明 $t^*$ 对容差不敏感（$<= 0.35$ ms）、递推无路径依赖（$10^(-12)$ m 量级）、而螺距与调头曲线长度对几何参数敏感。
][
  板凳龙；等距螺线；弦长递推；SAT 碰撞检测；S 形调头曲线；时间分辨率
]

#toc-page()

#include("sections/1_restatement.typ")
#include("sections/2_analysis.typ")
#include("sections/3_assumptions.typ")
#include("sections/4_symbols.typ")
#include("sections/5_problem1.typ")
#include("sections/6_problem2.typ")
#include("sections/7_problem3.typ")
#include("sections/8_problem4.typ")
#include("sections/9_problem5.typ")
#include("sections/10_sensitivity.typ")
#include("sections/11_evaluation.typ")

#pagebreak()
#references-cn()
#pagebreak()
#appendix-cn()
