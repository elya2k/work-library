"""Контрольная работа №1 «Расчёт при растяжении-сжатии», схема 2, вариант 5.
Строит PDF с решением: расчётная схема, эпюра N, подбор сечения «a»."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, FancyArrowPatch

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ---- Исходные данные ----
b, c, d = 150, 140, 230          # мм
P1, P2, P3 = 50, 110, 80         # кН
sig_adm = 160                    # МПа
k = 1.5                          # F1 = a x 1.5a

# ---- Продольные силы (от свободного конца, растяжение +) ----
N3 = -P1                 # участок d (III)
N2 = -P1 + P3            # участок c (II)
N1 = -P1 + P3 - P2       # участок b (I)
R = -N1                  # реакция заделки (вправо)

N_max_F1 = max(abs(N2), abs(N3))
A_req = N_max_F1 * 1e3 / sig_adm
a_req = math.sqrt(A_req / k)
a = math.ceil(a_req)
A = k * a * a
sig2 = N2 * 1e3 / A
sig3 = N3 * 1e3 / A
a_less = a - 1
sig_less = N_max_F1 * 1e3 / (k * a_less ** 2)

x0, x1, x2, x3 = 0, b, b + c, b + c + d
OUT = "projects/sopromat-kr1/KR1_scheme2_var5.pdf"
W, H = 8.27, 11.69


def page():
    fig = plt.figure(figsize=(W, H))
    return fig


def txt(fig, y, s, size=11, x=0.08, **kw):
    fig.text(x, y, s, fontsize=size, va="top", **kw)


def arrow(ax, xs, xe, y=0, color="k", lw=1.8):
    ax.add_patch(FancyArrowPatch((xs, y), (xe, y), arrowstyle="-|>",
                                 mutation_scale=16, lw=lw, color=color,
                                 zorder=5))


def draw_bar(ax, show_sections=True, show_R=True):
    h1, h2 = 0.5, 0.85    # полувысоты F1 и F2 (условно)
    # заделка
    ax.plot([0, 0], [-1.25, 1.25], color="k", lw=2)
    for yy in [i * 0.18 for i in range(-7, 7)]:
        ax.plot([-14, 0], [yy - 0.14, yy], color="k", lw=0.8)
    # участок b (F2 — пунктиром, размеры не заданы)
    ax.plot([x0, x1, x1], [h2, h2, h1], "k--", lw=1.3)
    ax.plot([x0, x1, x1], [-h2, -h2, -h1], "k--", lw=1.3)
    # участки c, d (F1)
    ax.add_patch(Rectangle((x1, -h1), x3 - x1, 2 * h1, fill=False, lw=1.8))
    ax.plot([x2, x2], [-h1, h1], color="k", lw=0.6, ls=":")
    ax.plot([x0 - 10, x3 + 90], [0, 0], color="gray", lw=0.6, ls="-.")
    ax.text((x0 + x1) / 2, h2 + 0.12, "$F_2$", ha="center", fontsize=12)
    ax.text((x1 + x3) / 2, h1 + 0.12, "$F_1$", ha="center", fontsize=12)
    # силы
    arrow(ax, x1 + 70, x1)
    ax.text(x1 + 35, -0.12, "$P_2$=110 кН", ha="center", va="top", fontsize=9)
    arrow(ax, x2 - 70, x2)
    ax.text(x2 - 35, 0.12, "$P_3$=80 кН", ha="center", fontsize=9)
    arrow(ax, x3 + 75, x3)
    ax.text(x3 + 38, 0.14, "$P_1$=50 кН", ha="center", fontsize=9)
    if show_R:
        arrow(ax, -75, -2, y=-1.0, color="tab:red")
        ax.text(-40, -0.9, "R=80 кН", color="tab:red", ha="center",
                fontsize=9)
    if show_sections:
        for xs, lab in [((x0 + x1) / 2, "I"), ((x1 + x2) / 2, "II"),
                        ((x2 + x3) / 2, "III")]:
            ax.plot([xs, xs], [-1.15, 1.15], color="tab:blue", lw=1)
            ax.text(xs + 4, -1.2, lab, color="tab:blue", fontsize=10,
                    va="top")
    # размеры
    yd = -1.55
    for xa, xb_, lab in [(x0, x1, f"b={b}"), (x1, x2, f"c={c}"),
                         (x2, x3, f"d={d}")]:
        ax.annotate("", (xa, yd), (xb_, yd),
                    arrowprops=dict(arrowstyle="<->", lw=0.8))
        ax.text((xa + xb_) / 2, yd + 0.06, lab, ha="center", fontsize=9)
    for xv in (x0, x1, x2, x3):
        ax.plot([xv, xv], [yd - 0.1, -0.55], color="k", lw=0.5)
    ax.text(x3 + 10, yd + 0.06, "мм", fontsize=9)
    ax.set_xlim(-90, x3 + 100)
    ax.set_ylim(-1.9, 1.4)
    ax.set_aspect("auto")
    ax.axis("off")


def draw_N(ax):
    segs = [(x0, x1, N1), (x1, x2, N2), (x2, x3, N3)]
    ax.plot([x0 - 10, x3 + 10], [0, 0], color="k", lw=1)
    for xa, xb_, n in segs:
        col = "tab:blue" if n > 0 else "tab:red"
        ax.add_patch(Rectangle((xa, 0), xb_ - xa, n, color=col, alpha=0.18))
        ax.plot([xa, xa, xb_, xb_], [0, n, n, 0], color=col, lw=1.6)
        step = 12
        xv = xa + step / 2
        while xv < xb_:
            ax.plot([xv, xv], [0, n], color=col, lw=0.5)
            xv += step
        mid = (xa + xb_) / 2
        ax.text(mid, n + (6 if n > 0 else -6),
                f"{n:+d} кН".replace("+", "+"), ha="center",
                va="bottom" if n > 0 else "top", fontsize=10,
                fontweight="bold", color=col)
        ax.text(mid, n / 2, "⊕" if n > 0 else "⊖", ha="center",
                va="center", fontsize=16, color=col)
    for xv in (x1, x2, x3):
        ax.plot([xv, xv], [-95, 45], color="gray", lw=0.4, ls=":")
    ax.text(-20, 0, "0", ha="right", va="center", fontsize=9)
    ax.text(-60, 15, "Эпюра N, кН", fontsize=11, ha="left")
    ax.set_xlim(-90, x3 + 100)
    ax.set_ylim(-110, 55)
    ax.axis("off")


def draw_section(ax):
    w, h = k * a, a
    ax.add_patch(Rectangle((0, 0), w, h, fill=False, lw=2, hatch="////"))
    ax.annotate("", (0, h + 3), (w, h + 3),
                arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(w / 2, h + 3.6, f"1,5a = {w:g} мм", ha="center", fontsize=10)
    ax.annotate("", (-3, 0), (-3, h),
                arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(-4, h / 2, f"a = {a} мм", ha="right", va="center", fontsize=10)
    ax.text(w / 2, -3, "Сечение $F_1$", ha="center", va="top", fontsize=10)
    ax.set_xlim(-22, w + 6)
    ax.set_ylim(-7, h + 7)
    ax.set_aspect("equal")
    ax.axis("off")


with PdfPages(OUT) as pdf:
    # ---------------- Страница 1 ----------------
    fig = page()
    txt(fig, 0.96, "Контрольная работа №1", 16, x=0.5, ha="center",
        fontweight="bold")
    txt(fig, 0.935, "«Расчёт при растяжении-сжатии»  —  схема 2, вариант 5",
        12, x=0.5, ha="center")
    txt(fig, 0.89, "Дано", 13, fontweight="bold")
    lines = [
        f"b = {b} мм,  c = {c} мм,  d = {d} мм",
        f"$P_1$ = {P1} кН,  $P_2$ = {P2} кН,  $P_3$ = {P3} кН",
        "Сечение $F_1$ — прямоугольник  a × 1,5a;   [σ] = 160 МПа",
        "Площадь $F_2$ (участок b) в задании не задана — участок b",
        "в подборе сечения «a» не участвует, для него строится только N.",
    ]
    for i, s in enumerate(lines):
        txt(fig, 0.86 - i * 0.027, s, 11)
    txt(fig, 0.715, "Требуется: а) построить эпюру продольных сил N;", 11)
    txt(fig, 0.69, "б) из условия прочности найти «a» "
        "(округлить до целого мм).", 11, x=0.175)

    txt(fig, 0.65, "Расчётная схема", 13, fontweight="bold")
    ax = fig.add_axes([0.06, 0.40, 0.88, 0.24])
    draw_bar(ax)
    txt(fig, 0.385,
        "Направления сил по схеме 2:  $P_2$ — влево (в сечении x = b),  "
        "$P_3$ — вправо (x = b + c),", 10)
    txt(fig, 0.362, "$P_1$ — влево, приложена к свободному торцу (сжимает "
        "брус).  I, II, III — сечения на участках.", 10)

    txt(fig, 0.315, "Реакция заделки", 13, fontweight="bold")
    txt(fig, 0.285, "Ось x направим вправо. Уравнение равновесия бруса:", 11)
    txt(fig, 0.255, r"$\Sigma X = 0:\;\; R - P_2 + P_3 - P_1 = 0$", 12)
    txt(fig, 0.22, rf"$R = P_2 - P_3 + P_1 = {P2} - {P3} + {P1} = "
        rf"{R}$ кН  (направлена вправо, от стены)", 12)
    txt(fig, 0.16, "Правило знаков: N > 0 — растяжение, N < 0 — сжатие.", 11)
    txt(fig, 0.135, "Продольную силу определяем методом сечений, "
        "рассматривая правую", 11)
    txt(fig, 0.11, "(свободную) часть бруса — тогда реакция R в расчёт "
        "не входит и служит проверкой.", 11)
    pdf.savefig(fig)
    plt.close(fig)

    # ---------------- Страница 2 ----------------
    fig = page()
    txt(fig, 0.96, "а) Эпюра продольных сил", 14, fontweight="bold")
    rows = [
        ("Участок III (d),  b + c ≤ x ≤ b + c + d:",
         rf"$N_{{III}} = -P_1 = {N3}$ кН   (сжатие)"),
        ("Участок II (c),  b ≤ x ≤ b + c:",
         rf"$N_{{II}} = -P_1 + P_3 = -{P1} + {P3} = +{N2}$ кН   (растяжение)"),
        ("Участок I (b),  0 ≤ x ≤ b:",
         rf"$N_{{I}} = -P_1 + P_3 - P_2 = -{P1} + {P3} - {P2} = {N1}$ кН"
         "   (сжатие)"),
    ]
    y = 0.925
    for head, formula in rows:
        txt(fig, y, head, 11, fontweight="bold")
        txt(fig, y - 0.028, formula, 12, x=0.11)
        y -= 0.07
    txt(fig, y + 0.005, rf"Проверка: в заделке $|N_I|$ = {abs(N1)} кН = R. "
        "Скачки на эпюре в точках приложения сил равны", 11)
    txt(fig, y - 0.02, rf"этим силам: {P1}, {P3} (−50→+30), {P2} (+30→−80), "
        f"{R} (в заделке) кН — эпюра построена верно.", 11)

    ax = fig.add_axes([0.06, 0.39, 0.88, 0.25])
    draw_bar(ax, show_sections=True, show_R=True)
    ax = fig.add_axes([0.06, 0.12, 0.88, 0.27])
    draw_N(ax)
    txt(fig, 0.10, "⊕ — растяжение,  ⊖ — сжатие.  Масштаб длин и сил "
        "условный, значения подписаны.", 10)
    pdf.savefig(fig)
    plt.close(fig)

    # ---------------- Страница 3 ----------------
    fig = page()
    txt(fig, 0.96, "б) Подбор размера сечения «a» по условию прочности", 14,
        fontweight="bold")
    s = [
        (r"Условие прочности:   $\sigma_{max} = \dfrac{|N|_{max}}{A} "
         r"\leq [\sigma]$   $\Rightarrow$   "
         r"$A \geq \dfrac{|N|_{max}}{[\sigma]}$", 12),
        ("Сечение $F_1$ работает на участках II и III:", 11),
        (rf"$|N|_{{max}}^{{F_1}} = \max(|N_{{II}}|,\ |N_{{III}}|) = "
         rf"\max({N2};\ {abs(N3)}) = {N_max_F1}$ кН  (участок III, сжатие)",
         12),
        (r"Площадь $F_1 = a \cdot 1{,}5a = 1{,}5a^2$", 12),
        (rf"$A_{{тр}} = \dfrac{{{N_max_F1}\cdot 10^3\ \mathrm{{Н}}}}{{{sig_adm}\ \mathrm{{МПа}}}} "
         rf"= {A_req:.1f}\ \mathrm{{мм}}^2$", 12),
        (rf"$a \geq \sqrt{{\dfrac{{A_{{тр}}}}{{1{{,}}5}}}} = "
         rf"\sqrt{{\dfrac{{{A_req:.1f}}}{{1{{,}}5}}}} = "
         rf"{a_req:.2f}$ мм   $\Rightarrow$   принимаем  a = {a} мм", 12),
    ]
    y = 0.915
    for line, size in s:
        txt(fig, y, line, size)
        y -= 0.06 if "dfrac" in line else 0.04
    txt(fig, y, "Проверка прочности при a = 15 мм:", 11, fontweight="bold")
    y -= 0.035
    chk = [
        rf"$A = 1{{,}}5\cdot{a}^2 = {A:g}\ \mathrm{{мм}}^2$",
        rf"$\sigma_{{III}} = \dfrac{{{N3}\cdot10^3}}{{{A:g}}} = "
        rf"{sig3:.1f}$ МПа,   $|\sigma_{{III}}| = {abs(sig3):.1f} < 160$ МПа  ✓",
        rf"$\sigma_{{II}} = \dfrac{{+{N2}\cdot10^3}}{{{A:g}}} = "
        rf"+{sig2:.1f}$ МПа  < 160 МПа  ✓",
        rf"При a = {a_less} мм:  $\sigma = {sig_less:.1f}$ МПа > 160 МПа "
        rf"(перегрузка {100 * (sig_less / sig_adm - 1):.1f} %) — не подходит.",
    ]
    for line in chk:
        txt(fig, y, line, 12, x=0.11)
        y -= 0.055 if "dfrac" in line else 0.035

    ax = fig.add_axes([0.3, y - 0.19, 0.4, 0.17])
    draw_section(ax)
    y -= 0.22

    txt(fig, y, "Ответ", 14, fontweight="bold")
    ans = [
        rf"Продольные силы:  $N_I$ = {N1} кН (сжатие),  "
        rf"$N_{{II}}$ = +{N2} кН (растяжение),  $N_{{III}}$ = {N3} кН (сжатие).",
        rf"Реакция заделки R = {R} кН.",
        rf"Размер сечения  a = {a} мм  (сечение $F_1$ = {a}×{k * a:g} мм, "
        rf"A = {A:g} мм², $\sigma_{{max}}$ = {abs(sig3):.1f} МПа).",
    ]
    y -= 0.035
    for line in ans:
        txt(fig, y, line, 10.5)
        y -= 0.03
    txt(fig, y - 0.01, "Примечание: площадь $F_2$ не задана, поэтому "
        "участок b в подборе не учитывался. Для справки:", 9.5, color="0.35")
    txt(fig, y - 0.033, rf"при $|N_I|$ = {abs(N1)} кН потребовалось бы "
        rf"$F_2 \geq {abs(N1)}\cdot10^3/160 = {abs(N1) * 1e3 / sig_adm:g}$ мм².",
        9.5, color="0.35")
    pdf.savefig(fig)
    plt.close(fig)

print(f"N: I={N1}, II={N2}, III={N3}, R={R}")
print(f"A_req={A_req:.1f}, a_req={a_req:.3f}, a={a}, A={A}, "
      f"sig2={sig2:.1f}, sig3={sig3:.1f}, sig(a-1)={sig_less:.1f}")
print("PDF:", OUT)
