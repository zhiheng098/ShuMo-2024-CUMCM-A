#heading(numbering: none, outlined: true)[附录 A #h(1em) 核心代码]

以下给出核心代码（Python 3.14 + NumPy），完整实现、数据与运行脚本见提交的 Notebook 文件。

#set par(first-line-indent: 0pt)

#block(breakable: false)[
*1. 螺线弧长原函数与半径反解*

```python
def G(r):
    return 0.5 * r * math.hypot(r, k) + 0.5 * k * k * math.asinh(r / k)

def radius(s, guess=None):
    # 由弧长反解半径：解 G(r) = G0 - k*s
    target = G0 - k * s
    if guess and guess > 0:
        r = guess
    else:
        r = max(math.sqrt(2 * target), 1e-3)
    for _ in range(80):
        f = G(r) - target
        rn = r - f / math.hypot(r, k)
        if rn <= 1e-12:
            rn = 0.5 * r
        if abs(rn - r) <= 2e-15 * max(1.0, r):
            return rn
        r = rn
    return r
```
]

#block(breakable: false)[
*2. 刚性弦长递推（牛顿迭代 + 区间约束）*

```python
for i in range(1, n):
    li = ell[i - 1]
    px, py = X[i - 1]
    # 以上一时刻同一连杆的弧长间隔热启动
    gs = s[i - 1] - (warm[i - 1] - warm[i])
    si = gs
    for _ in range(16):
        r, p, t = path_state(si)
        dx, dy = p[0] - px, p[1] - py
        h = dx * dx + dy * dy - li * li
        if abs(h) < 1e-12 * li:
            break
        d = 2.0 * (dx * t[0] + dy * t[1])
        sn = si - h / d
        # 限制在区间内，防止跳到另一支根
        if not (s[i - 1] - 2.6 * li < sn < s[i - 1]):
            break
        si = sn
    r_, X[i], Tg[i] = path_state(si)
    s[i] = si
```
]

#block(breakable: false)[
*3. 速度放大系数（隐函数求导）*

```python
for i in range(1, len(X)):
    ux = (X[i, 0] - X[i - 1, 0]) / ell[i - 1]
    uy = (X[i, 1] - X[i - 1, 1]) / ell[i - 1]
    num = ux * Tg[i - 1, 0] + uy * Tg[i - 1, 1]
    den = ux * Tg[i, 0] + uy * Tg[i, 1]
    a = num / den if abs(den) > 1e-14 else float("nan")
    v[i] = v[i - 1] * a
    A[i] = A[i - 1] * a
```
]

#block(breakable: false)[
*4. SAT 最小平移重叠量（负值即间隙）*

```python
def sat_pen(qa, qb):
    best = 1e18
    for q in (qa, qb):
        for e in range(4):
            x1, y1 = q[e]
            x2, y2 = q[(e + 1) % 4]
            ax, ay = -(y2 - y1), (x2 - x1)
            L = math.hypot(ax, ay)
            ax, ay = ax / L, ay / L
            amin = bmin = 1e18
            amax = bmax = -1e18
            for px, py in qa:
                d = px * ax + py * ay
                amin = min(amin, d)
                amax = max(amax, d)
            for px, py in qb:
                d = px * ax + py * ay
                bmin = min(bmin, d)
                bmax = max(bmax, d)
            pen = min(amax, bmax) - max(amin, bmin)
            best = min(best, pen)
    return best
```
]

#block(breakable: false)[
*5. 调头曲线半径（一元二次方程 + 退化回退）*

```python
A = mx * mx + my * my - 9.0      # m = 2*n1 + n2
B = 2 * (bx * mx + by * my)      # b0 = Q1 - Q2
C = bx * bx + by * by
if abs(A) < 1e-12:
    # 切点落在边界时退化为一次方程
    R2 = -C / B
else:
    sq = math.sqrt(B * B - 4 * A * C)
    roots = ((-B + sq) / (2 * A), (-B - sq) / (2 * A))
    R2 = max(r for r in roots if r > 0)
R1 = 2 * R2
```
]
