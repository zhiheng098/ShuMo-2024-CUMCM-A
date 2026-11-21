"""论文级结果图重绘（scibox-figure 版式规范）。

读取 code/outputs/*.npz 的真实结果，按期刊版式（Times 衬线 + 中文宋体回退、去顶/右边框、
刻度朝内、Okabe-Ito 配色、双栏 7.0 in / 单栏 3.35 in）重绘，输出矢量 PDF 与 300 dpi PNG。

用法: py -3.14 paper_figures.py
"""
import math
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

OUT = ROOT / "outputs"
FIG = ROOT.parent / "figures_paper"
FIG.mkdir(parents=True, exist_ok=True)

BLUE, RED, GREEN, ORANGE, SKY, PURPLE, GREY = (
    "#0072B2", "#D55E00", "#009E73", "#E69F00", "#56B4E9", "#CC79A7", "#8C8C8C")

mpl.rcParams.update({
    "font.family": ["Times New Roman", "SimSun"],
    "mathtext.fontset": "stix",
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.7,
    "xtick.major.width": 0.7,
    "ytick.major.width": 0.7,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "xtick.top": True,
    "ytick.right": True,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "legend.frameon": False,
    "lines.linewidth": 1.0,
    "figure.dpi": 120,
})

CW, DW = 3.35, 7.0
SPIRAL_B = 1.7
SPIRAL_R0 = 16 * SPIRAL_B
SPIRAL_K = SPIRAL_B / (2 * math.pi)
R_CIRCLE = 4.5
HALF_W, OVER = 0.15, 0.275
N_NODE = 224


def save(fig, name):
    try:
        fig.tight_layout()
    except Exception:
        pass
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("  ->", name)


def panel(ax, letter, dx=-0.14, dy=1.03):
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, family="Times New Roman",
            fontsize=8, fontweight="bold", va="bottom", ha="left")


def style_ax(ax, grid=True):
    if grid:
        ax.grid(True, ls=":", lw=0.4, color="0.75", alpha=0.9)
        ax.set_axisbelow(True)


def spiral_xy(n_turn=3, n=4000, sign=1.0):
    th = np.linspace(0, 2 * np.pi * n_turn, n)
    rr = SPIRAL_R0 - SPIRAL_K * th
    return sign * rr * np.cos(th), -sign * rr * np.sin(th)


def board_quads(X):
    quads, centers = [], np.empty((len(X) - 1, 2))
    for j in range(len(X) - 1):
        x0, y0 = X[j]
        x1, y1 = X[j + 1]
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        nx, ny = -uy, ux
        ax_, ay_ = x0 - OVER * ux, y0 - OVER * uy
        bx_, by_ = x1 + OVER * ux, y1 + OVER * uy
        quads.append(((ax_ + HALF_W * nx, ay_ + HALF_W * ny),
                      (bx_ + HALF_W * nx, by_ + HALF_W * ny),
                      (bx_ - HALF_W * nx, by_ - HALF_W * ny),
                      (ax_ - HALF_W * nx, ay_ - HALF_W * ny)))
        centers[j] = (0.5 * (ax_ + bx_), 0.5 * (ay_ + by_))
    return quads, centers


def nearest_pair(qa, qb, n=40):
    """两块矩形边界上最近点对的中点（用于标注真实接触位置）。"""
    def sample(q):
        pts = []
        for k in range(4):
            x0, y0 = q[k]
            x1, y1 = q[(k + 1) % 4]
            for t in np.linspace(0, 1, n):
                pts.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
        return np.array(pts)

    pa, pb = sample(qa), sample(qb)
    d2 = ((pa[:, None, :] - pb[None, :, :]) ** 2).sum(-1)
    i, j = np.unravel_index(np.argmin(d2), d2.shape)
    return (0.5 * (pa[i, 0] + pb[j, 0]), 0.5 * (pa[i, 1] + pb[j, 1]))


def draw_boards(ax, X, color=BLUE, lw=0.45, hot=None, hot_color=RED, fade=None):
    quads, centers = board_quads(X)
    for j, q in enumerate(quads):
        xs = [p[0] for p in q] + [q[0][0]]
        ys = [p[1] for p in q] + [q[0][1]]
        on = (hot is not None) and (j in hot)
        col = hot_color if on else color
        if fade is not None and not on:
            if math.hypot(centers[j][0], centers[j][1]) > fade:
                col = "0.80"
        ax.plot(xs, ys, color=col, lw=(0.9 if on else lw),
                zorder=6 if on else 3, solid_joinstyle="miter")


def _G(r):
    return 0.5 * r * math.hypot(r, SPIRAL_K) + 0.5 * SPIRAL_K ** 2 * math.asinh(r / SPIRAL_K)


_G0 = _G(SPIRAL_R0)


def _radius(s):
    target = _G0 - SPIRAL_K * s
    r = max(math.sqrt(2 * target), 1e-3)
    for _ in range(60):
        f = _G(r) - target
        rn = r - f / math.hypot(r, SPIRAL_K)
        if abs(rn - r) <= 1e-14 * max(1.0, r):
            return rn
        r = rn
    return r


def _state(s):
    r = _radius(s)
    th = (SPIRAL_R0 - r) / SPIRAL_K
    c, sn = math.cos(th), math.sin(th)
    L = math.hypot(r, SPIRAL_K)
    return ((r * c, -r * sn), ((-SPIRAL_K * c - r * sn) / L, (SPIRAL_K * sn - r * c) / L))


def turn_geom(off1):
    """S 形调头曲线：切点 1 内移 off1，R1=2R2，三处相切。返回几何参数或 None。"""
    u0 = (_G0 - _G(R_CIRCLE)) / SPIRAL_K
    Q1, T1 = _state(u0 + off1)
    Q2m, T2 = _state(u0)
    Q2 = (-Q2m[0], -Q2m[1])
    n1, n2 = (T1[1], -T1[0]), (T2[1], -T2[0])
    bx, by = Q1[0] - Q2[0], Q1[1] - Q2[1]
    mx, my = 2 * n1[0] + n2[0], 2 * n1[1] + n2[1]
    A = mx * mx + my * my - 9.0
    B = 2 * (bx * mx + by * my)
    C = bx * bx + by * by
    if abs(A) < 1e-12:          # δ1=0 附近方程退化为一次方程
        roots = [-C / B] if abs(B) > 1e-15 else []
    else:
        disc = B * B - 4 * A * C
        if disc < 0:
            return None
        sq = math.sqrt(disc)
        roots = [(-B + sq) / (2 * A), (-B - sq) / (2 * A)]
    roots = [r for r in roots if r > 1e-6]
    if not roots:
        return None
    R2 = max(roots)
    R1 = 2 * R2
    C1 = (Q1[0] + R1 * n1[0], Q1[1] + R1 * n1[1])
    C2 = (Q2[0] - R2 * n2[0], Q2[1] - R2 * n2[1])
    J = (C1[0] + R1 / (R1 + R2) * (C2[0] - C1[0]), C1[1] + R1 / (R1 + R2) * (C2[1] - C1[1]))

    def sweep(v0, v1, om):
        d = math.atan2(v0[0] * v1[1] - v0[1] * v1[0], v0[0] * v1[0] + v0[1] * v1[1])
        return (d if om > 0 else -d) % (2 * math.pi)

    e1e = ((J[0] - C1[0]) / R1, (J[1] - C1[1]) / R1)
    e2e = ((Q2[0] - C2[0]) / R2, (Q2[1] - C2[1]) / R2)
    a1 = sweep(((Q1[0] - C1[0]) / R1, (Q1[1] - C1[1]) / R1), e1e, -1)
    a2 = sweep(((J[0] - C2[0]) / R2, (J[1] - C2[1]) / R2), e2e, +1)
    return dict(R1=R1, R2=R2, a1=a1, a2=a2, L=R1 * a1 + R2 * a2,
                Q1=Q1, Q2=Q2, J=J, C1=C1, C2=C2, e1e=e1e, e2e=e2e)


def arc_xy(g, which, n=500):
    C = g["C1"] if which == 1 else g["C2"]
    R = g["R1"] if which == 1 else g["R2"]
    e_end = g["e1e"] if which == 1 else g["e2e"]
    a = g["a1"] if which == 1 else g["a2"]
    om = -1 if which == 1 else +1
    ang = -om * np.linspace(0, a * R, n) / R
    ca, sa = np.cos(ang), np.sin(ang)
    return C[0] + R * (e_end[0] * ca - e_end[1] * sa), C[1] + R * (e_end[0] * sa + e_end[1] * ca)


D1 = np.load(OUT / "q1_data.npz")
D2 = np.load(OUT / "q2_data.npz")
D3 = np.load(OUT / "q3_data.npz")
D4 = np.load(OUT / "q4_data.npz")
DG = np.load(OUT / "q4_geometry.npz")
D5 = np.load(OUT / "q5_data.npz")

T1, X1, V1, R1_ = D1["t"], D1["X"], D1["V"], D1["R"]
T2, DM2, TSTAR = D2["t_scan"], D2["dmin"], float(D2["t_star"])
X2_, PAIR2 = D2["X"], D2["pair"]
PG, DGMIN, FG, PMIN = D3["p_grid"], D3["d_grid"], D3["feas_grid"].astype(bool), float(D3["p_min"])
BIS = D3["bis"]
X3_, S3C, PAIR3 = D3["X"], float(D3["s_crit"]), D3["pair"]
T4, X4, V4, A4 = D4["t"], D4["X"], D4["V"], D4["A"]
AMAX, TPEAK, IPEAK, VMAX = float(D5["Amax"]), float(D5["t_peak"]), int(D5["i_peak"]), float(D5["v_max"])
T5, A5 = D5["t"], D5["A"]
TF5, AF5 = D5["tf"], D5["af"]
CONV = D5["conv"]

print("绘制论文级图形 →", FIG)


def fig01():
    fig, axes = plt.subplots(2, 3, figsize=(DW, 4.9), sharex=True, sharey=True)
    xs, ys = spiral_xy(n_turn=3)
    for ax, tt in zip(axes.flat, [0, 60, 120, 180, 240, 300]):
        ax.plot(xs, ys, color="0.85", lw=0.45, zorder=0)
        X = X1[int(tt)]
        ax.plot(X[:, 0], X[:, 1], color=BLUE, lw=1.0, zorder=3)
        ax.plot(X[0, 0], X[0, 1], "o", ms=3.0, color=RED, zorder=7)
        ax.plot(X[-1, 0], X[-1, 1], "s", ms=2.6, mfc="none", mec=GREEN, mew=0.9, zorder=7)
        ax.set_aspect("equal")
        ax.set_xlim(-13.2, 13.2)
        ax.set_ylim(-13.2, 13.2)
        ax.set_title(f"t = {tt} s", pad=3)
        ax.set_xticks([-10, 0, 10])
        ax.set_yticks([-10, 0, 10])
    for ax in axes[-1]:
        ax.set_xlabel("x / m")
    for ax in axes[:, 0]:
        ax.set_ylabel("y / m")
    panel(axes[0, 0], "a", dx=-0.20)
    save(fig, "fig01_dragon_snapshots")


def fig02():
    fig, ax = plt.subplots(figsize=(CW, 2.5))
    for i, tt in enumerate([0, 60, 120, 180, 300]):
        ax.plot(np.arange(N_NODE), V1[int(tt)], lw=0.9,
                color=plt.cm.viridis(0.12 + 0.19 * i), label=f"t = {tt} s")
    ax.set_xlabel("把手节点编号 i")
    ax.set_ylabel("速率 v / (m/s)")
    ax.set_xlim(0, N_NODE - 1)
    ax.set_ylim(0.9962, 1.0003)
    ax.legend(loc="lower left", ncol=2, handlelength=1.5, columnspacing=0.9)
    style_ax(ax)
    save(fig, "fig02_speed_profile_q1")


def fig03():
    fig, ax = plt.subplots(figsize=(CW, 2.4))
    ax.plot(T1, R1_[:, 0], color=BLUE, label="龙头前把手")
    ax.plot(T1, R1_[:, -1], color=RED, ls="--", label="龙尾（后）把手")
    ax.fill_between(T1, R1_[:, 0], R1_[:, -1], color=SKY, alpha=0.12, lw=0)
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("极径 r / m")
    ax.set_xlim(0, 300)
    ax.legend(loc="center right")
    style_ax(ax)
    save(fig, "fig03_head_radius")


def fig04():
    fig, axes = plt.subplots(1, 2, figsize=(DW, 2.6), gridspec_kw={"width_ratios": [1.55, 1]})
    ax = axes[0]
    ax.plot(T2, DM2, color=BLUE, lw=0.9)
    ax.axhline(0, color="k", lw=0.6, ls="--")
    ax.axvline(TSTAR, color=RED, lw=0.7, ls=":")
    ax.plot([TSTAR], [0], marker="*", ms=7, color=RED, zorder=5, clip_on=False)
    ax.annotate(f"t* = {TSTAR:.2f} s", xy=(TSTAR, 0), xytext=(24, -0.145),
                fontsize=7, color=RED, ha="left",
                arrowprops=dict(arrowstyle="->", lw=0.6, color=RED,
                                connectionstyle="arc3,rad=-0.12"))
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("最小间隙 d / m")
    ax.set_xlim(0, 440)
    style_ax(ax)
    panel(ax, "a")
    ax = axes[1]
    m = (T2 > TSTAR - 4) & (T2 < TSTAR + 4)
    ax.plot(T2[m] - TSTAR, DM2[m], "o-", ms=2.2, lw=0.8, color=BLUE)
    ax.axhline(0, color="k", lw=0.6, ls="--")
    ax.axvline(0, color=RED, lw=0.7, ls=":")
    ax.set_xlabel("t - t* / s")
    ax.set_ylabel("d / m")
    ax.set_xlim(-4, 4)
    style_ax(ax)
    panel(ax, "b")
    save(fig, "fig04_gap_vs_time")


def fig05():
    p = PAIR2.astype(int)
    quads, _ = board_quads(X2_)
    qa, qb = quads[p[0]], quads[p[1]]
    cx, cy = nearest_pair(qa, qb)
    fig, axes = plt.subplots(1, 2, figsize=(DW, 3.5))
    xs, ys = spiral_xy(n_turn=2)
    ax = axes[0]
    ax.plot(xs, ys, color="0.86", lw=0.45, zorder=0)
    draw_boards(ax, X2_, color=BLUE, lw=0.25, hot={p[0], p[1]})
    ax.set_aspect("equal")
    ax.set_xlim(-8.8, 8.8)
    ax.set_ylim(-8.8, 8.8)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(f"t* = {TSTAR:.2f} s", pad=3)
    panel(ax, "a")
    ax = axes[1]
    draw_boards(ax, X2_, color="0.84", lw=0.3, hot={p[0], p[1]})
    for q in (qa, qb):
        ax.fill([v[0] for v in q], [v[1] for v in q], color=RED, alpha=0.12, lw=0)
    ax.set_aspect("equal")
    ax.set_xlim(cx - 0.78, cx + 0.78)
    ax.set_ylim(cy - 0.78, cy + 0.78)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.annotate("角点接触", xy=(cx, cy), xytext=(cx - 0.72, cy + 0.30), fontsize=7,
                arrowprops=dict(arrowstyle="->", lw=0.6))
    panel(ax, "b")
    save(fig, "fig05_contact_configuration")


def fig06():
    fig, axes = plt.subplots(1, 2, figsize=(DW, 2.7), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]
    ax.plot(PG[~FG], DGMIN[~FG], "s", ms=3.6, mfc="none", mec=RED, mew=0.9)
    ax.plot(PG[FG], DGMIN[FG], "o", ms=3.6, mfc="none", mec=BLUE, mew=0.9)
    ax.axhline(0, color="k", lw=0.6, ls="--")
    ax.axvline(PMIN, color=GREEN, lw=0.8, ls=":")
    ax.annotate(f"p_min = {PMIN:.4f} m", xy=(PMIN, 0.50), xytext=(PMIN + 0.10, 0.68),
                fontsize=7, color=GREEN,
                arrowprops=dict(arrowstyle="->", lw=0.6, color=GREEN),
                bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.text(0.27, 0.90, "○ 可行（全程最小间隙）", color=BLUE, fontsize=6.8, va="top",
            bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.text(0.27, 0.80, "□ 不可行（首次接触间隙）", color=RED, fontsize=6.8, va="top",
            bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.set_xlabel("螺距 p / (m/圈)")
    ax.set_ylabel("最小间隙 / m")
    ax.set_xlim(0.25, 1.36)
    ax.set_ylim(-0.13, 1.02)
    style_ax(ax)
    panel(ax, "a")
    ax = axes[1]
    ax.semilogy(np.arange(1, len(BIS) + 1), BIS[:, 1] - BIS[:, 0], "o-", ms=2.2, lw=0.8, color=PURPLE)
    ax.set_xlabel("二分迭代次数")
    ax.set_ylabel("区间宽度 / (m/圈)")
    ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, q: f"{v:g}"))
    style_ax(ax)
    panel(ax, "b")
    save(fig, "fig06_pitch_scan")


def fig07():
    p = PAIR3.astype(int)
    quads, _ = board_quads(X3_)
    qa, qb = quads[p[0]], quads[p[1]]
    cx, cy = nearest_pair(qa, qb)
    fig, axes = plt.subplots(1, 2, figsize=(DW, 3.5))
    xs, ys = spiral_xy(n_turn=4)
    ax = axes[0]
    ax.plot(xs, ys, color="0.86", lw=0.45, zorder=0)
    draw_boards(ax, X3_, color=BLUE, lw=0.2, hot={p[0], p[1]})
    ax.add_patch(Circle((0, 0), R_CIRCLE, fill=False, ls="--", lw=0.7, color=RED, zorder=2))
    ax.set_aspect("equal")
    ax.set_xlim(-9.0, 9.0)
    ax.set_ylim(-9.0, 9.0)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.set_title(f"p_min = {PMIN:.4f} m, t = {S3C:.1f} s", pad=3)
    panel(ax, "a")
    ax = axes[1]
    draw_boards(ax, X3_, color="0.84", lw=0.3, hot={p[0], p[1]})
    for q in (qa, qb):
        ax.fill([v[0] for v in q], [v[1] for v in q], color=RED, alpha=0.12, lw=0)
    ax.set_aspect("equal")
    ax.set_xlim(cx - 0.72, cx + 0.72)
    ax.set_ylim(cy - 0.72, cy + 0.72)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    panel(ax, "b")
    save(fig, "fig07_critical_configuration")


def fig08():
    fig, axes = plt.subplots(1, 2, figsize=(DW, 3.4), gridspec_kw={"width_ratios": [1.0, 1]})
    xs, ys = spiral_xy(n_turn=2.2)
    ax = axes[0]
    ax.plot(xs, ys, color="0.88", lw=0.4, zorder=0)
    ax.plot(-xs, -ys, color="0.88", lw=0.4, zorder=0)
    ax.add_patch(Circle((0, 0), R_CIRCLE, fill=False, ls="--", lw=0.7, color=RED, zorder=1))
    g0 = turn_geom(0.0)
    gs = turn_geom(float(DG["off1"]))
    for g, ls, lw, col in ((g0, "--", 0.9, GREY), (gs, "-", 1.3, BLUE)):
        ax.plot(*arc_xy(g, 1), ls=ls, lw=lw, color=col)
        ax.plot(*arc_xy(g, 2), ls=ls, lw=lw, color=col)
    ax.plot([], [], "--", color=GREY, lw=0.9, label=f"基准 L0 = {float(DG['L0']):.4f} m")
    ax.plot([], [], "-", color=BLUE, lw=1.3, label=f"最短 L* = {float(DG['Lstar']):.4f} m")
    ax.plot(*DG["Q10"], "s", ms=3.2, color="k", zorder=8)
    ax.plot(*DG["Q20"], "s", ms=3.2, color="k", zorder=8)
    ax.plot(*DG["Q1"], "s", ms=3.2, color=BLUE, zorder=8)
    ax.annotate("Q1", DG["Q10"], textcoords="offset points", xytext=(5, -9), fontsize=7)
    ax.annotate("Q2", DG["Q20"], textcoords="offset points", xytext=(-11, 5), fontsize=7)
    ax.annotate("Q1*", DG["Q1"], textcoords="offset points", xytext=(-20, -2), fontsize=7, color=BLUE)
    ax.annotate("J*", DG["J"], textcoords="offset points", xytext=(5, 4), fontsize=7, color=BLUE)
    ax.set_aspect("equal")
    ax.set_xlim(-5.3, 5.3)
    ax.set_ylim(-5.3, 5.3)
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.legend(loc="lower right", handlelength=1.8)
    panel(ax, "a")

    ax = axes[1]
    off1 = float(DG["off1"])
    off = np.linspace(0, off1 * 1.25, 36)
    Ls, R2s = [], []
    for o in off:
        g = turn_geom(float(o))
        Ls.append(g["L"] if g else np.nan)
        R2s.append(g["R2"] if g else np.nan)
    ax.plot(off, Ls, color=BLUE, lw=1.2)
    ax.set_xlabel("切点内移量 δ1 / m")
    ax.set_ylabel("曲线长度 L / m", color=BLUE)
    ax.tick_params(axis="y", colors=BLUE)
    ax.axvline(off1, color=GREEN, lw=0.8, ls=":")
    ax.annotate(f"δ1* = {off1:.3f} m\nL* = {float(DG['Lstar']):.4f} m",
                xy=(off1, float(DG["Lstar"])), xytext=(off1 * 0.36, float(DG["Lstar"]) - 0.75),
                fontsize=7, color=GREEN,
                arrowprops=dict(arrowstyle="->", lw=0.6, color=GREEN))
    ax2 = ax.twinx()
    ax2.plot(off, R2s, color=RED, lw=1.0, ls="--")
    ax2.axhline(1.43, color=RED, lw=0.7, ls="-.")
    ax2.set_ylabel("弧 2 半径 R2 / m", color=RED)
    ax2.tick_params(axis="y", colors=RED)
    ax2.set_ylim(0.62, 1.62)
    ax2.spines["right"].set_visible(True)
    ax2.spines["right"].set_linewidth(0.7)
    ax2.text(off1 * 0.05, 1.445, "R2_min = 1.43 m", fontsize=6.5, color=RED, va="bottom")
    ax.set_xlim(0, off1 * 1.25)
    style_ax(ax)
    panel(ax, "b", dx=-0.18)
    save(fig, "fig08_turn_curves")


def fig09():
    fig, axes = plt.subplots(2, 2, figsize=(DW, 5.4))
    xs, ys = spiral_xy(n_turn=15)
    cases = [(-100, 17.0, "a"), (0, 5.4, "b"), (8, 5.4, "c"), (100, 17.0, "d")]
    for ax, (tt, lim, letter) in zip(axes.flat, cases):
        it = int(tt) + 100
        if lim > 6:
            ax.plot(xs, ys, color="0.86", lw=0.35, zorder=0)
            ax.plot(-xs, -ys, color="0.86", lw=0.35, zorder=0)
        ax.add_patch(Circle((0, 0), R_CIRCLE, fill=False, ls="--", lw=0.6, color=RED, zorder=1))
        if lim < 6:
            draw_boards(ax, X4[it], color=BLUE, lw=0.35, hot={0}, fade=R_CIRCLE)
        else:
            ax.plot(X4[it][:, 0], X4[it][:, 1], color=BLUE, lw=1.1, zorder=3)
        ax.plot(X4[it][0, 0], X4[it][0, 1], "o", ms=3.0, color=RED, zorder=7)
        ax.set_aspect("equal")
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_title("t = %d s%s" % (tt, "（调头空间局部）" if lim < 6 else ""), pad=3)
        ax.set_xlabel("x / m")
        ax.set_ylabel("y / m")
        panel(ax, letter)
    fig.tight_layout()
    save(fig, "fig09_turn_snapshots")


def fig10():
    fig, ax = plt.subplots(figsize=(CW, 2.5))
    for i, tt in enumerate([-100, -50, 0, 50, 100]):
        ax.plot(np.arange(N_NODE), V4[int(tt) + 100], lw=0.9,
                color=plt.cm.viridis(0.12 + 0.19 * i), label=f"t = {tt} s")
    ax.axhline(2.0, color=RED, lw=0.7, ls="--")
    ax.text(3, 2.07, "v = 2 m/s 上限", fontsize=6.5, color=RED)
    ax.set_xlabel("把手节点编号 i")
    ax.set_ylabel("速率 v / (m/s)")
    ax.set_xlim(0, N_NODE - 1)
    ax.set_ylim(0.30, 2.25)
    ax.legend(loc="center right", handlelength=1.5)
    style_ax(ax)
    save(fig, "fig10_speed_profile_q4")


def fig11():
    fig, ax = plt.subplots(figsize=(DW, 2.9))
    m = ax.imshow(A5.T, aspect="auto", origin="lower", cmap="magma",
                  extent=[T5[0] - 0.1, T5[-1] + 0.1, -0.5, N_NODE - 0.5],
                  vmin=float(np.nanmin(A5)), vmax=float(np.nanmax(A5)))
    ax.plot([TPEAK], [IPEAK], "o", mfc="none", mec="cyan", ms=9, mew=1.1)
    ax.annotate(f"A_max = {AMAX:.3f}（第 {IPEAK} 节，t = {TPEAK:.2f} s）",
                xy=(TPEAK, IPEAK), xytext=(TPEAK + 18, IPEAK + 72), fontsize=7, color="cyan",
                arrowprops=dict(arrowstyle="->", lw=0.6, color="cyan"))
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("把手节点编号 i")
    cb = fig.colorbar(m, ax=ax, pad=0.015, fraction=0.035)
    cb.set_label("速度放大系数 A(t)")
    cb.ax.tick_params(width=0.6, size=2, labelsize=7)
    cb.outline.set_linewidth(0.6)
    save(fig, "fig11_amplification_heatmap")


def fig12():
    fig, ax = plt.subplots(figsize=(CW, 2.3))
    ax.plot(T5, np.nanmax(A5, axis=1), color=RED, lw=0.9)
    ax.axhline(AMAX, color="k", lw=0.6, ls=":")
    ax.plot([TPEAK], [AMAX], "o", ms=3.4, color=RED)
    ax.annotate(f"A_max = {AMAX:.4f}", xy=(TPEAK, AMAX),
                xytext=(TPEAK + 12, AMAX - 0.16), fontsize=7,
                arrowprops=dict(arrowstyle="->", lw=0.6))
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel("max A")
    ax.set_xlim(T5[0], T5[-1])
    ax.set_ylim(0.85, 1.75)
    style_ax(ax)
    save(fig, "fig12_max_amplification")


def fig13():
    fig, ax = plt.subplots(figsize=(CW, 2.3))
    ax.plot(TF5, AF5, "-", lw=1.0, color=BLUE, label=f"第 {IPEAK} 节龙身前把手")
    ax.axhline(AMAX, color=RED, lw=0.6, ls=":")
    ax.axvline(TPEAK, color=RED, lw=0.6, ls=":")
    ax.set_xlabel("时间 t / s")
    ax.set_ylabel(f"A{IPEAK}(t)")
    ax.legend(loc="upper left", handlelength=1.5)
    style_ax(ax)
    save(fig, "fig13_peak_zoom")


def fig14():
    import json
    S = json.load(open(OUT / "summary.json", encoding="utf-8"))
    tol = np.array(S["sensitivity"]["tolerance"], dtype=float)
    steps = np.array(S["sensitivity"]["time_step"], dtype=float)

    fig, axes = plt.subplots(1, 2, figsize=(DW, 2.5))
    ax = axes[0]
    ax.semilogx(tol[:, 0], (tol[:, 1] - tol[1, 1]) * 1e3, "o-", ms=3.4, lw=0.9, color=BLUE)
    ax.set_xlabel("接触容差 ε / m")
    ax.set_ylabel("t* 偏移 / ms")
    ax.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, q: f"{v:g}"))
    ax.set_title("终时刻对容差不敏感（≤0.35 ms）", pad=3)
    style_ax(ax)
    panel(ax, "a")

    ax = axes[1]
    dt_ = np.array([1.0, 0.5, 0.25])
    tt_ = np.array([D2["step_t"][list(D2["step_dt"]).index(k)] for k in dt_])
    ax.plot(dt_, tt_ - TSTAR, "s-", ms=3.4, lw=0.9, color=RED)
    ax.axhline(0, color="k", lw=0.6, ls=":")
    ax.set_xlabel("粗扫步长 Δt / s")
    ax.set_ylabel("首次接触时刻偏差 / s")
    ax.set_title("粗网格不早于二分结果", pad=3)
    style_ax(ax)
    panel(ax, "b")
    save(fig, "fig14_sensitivity")


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07,
              fig08, fig09, fig10, fig11, fig12, fig13, fig14):
        f()
    print("完成：%d 张 PDF + PNG" % len(list(FIG.glob('fig*.pdf'))))
    print("关键数值：t*=%.4f s，p_min=%.4f m/圈，L0=%.4f m，L*=%.4f m，A_max=%.4f，v_max=%.4f m/s"
          % (TSTAR, PMIN, float(DG["L0"]), float(DG["Lstar"]), AMAX, VMAX))
