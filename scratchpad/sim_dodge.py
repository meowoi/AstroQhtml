# -*- coding: utf-8 -*-
"""Mo phong dung y nguyen vat ly + logic sinh cot cua game-dodge.html
   de kiem: (1) khe hep co voi tay toi duoc khong, (2) do kho co that la "De" khong."""
import random, math

VW, VH = 800, 500
GRAV, HOLD, FLAPV = 1500.0, 560.0, -400.0
MAXFALL, MAXRISE = 540.0, -430.0
S0, SACC, SMAX = 190.0, 2.2, 300.0
COLGAP, COLW = 300.0, 64.0
GAPH0, GAPHMIN, GAPSHRINK = 200.0, 158.0, 1.4
GAPMARGIN, GAPSTEP = 52.0, 150.0
BYTEX, BYTEW, BYTEH, INSET = VW * 0.25, 46.0, 34.0, 6.0
DT = 1.0 / 60.0

BX0 = BYTEX - BYTEW / 2 + INSET          # 183
BX1 = BYTEX + BYTEW / 2 - INSET          # 217
BH = BYTEH - INSET * 1.2                 # 26.8
BDY = BYTEH / 2 - INSET * 0.6            # nua chieu cao hitbox


def run(seed, maxT=180.0, flapCd=0.15, react=0.0):
    """flapCd = khoang nghi toi thieu giua 2 cu bat (mo phong toc do bam that cua nguoi)
       react  = do tre phan ung (s)"""
    rnd = random.Random(seed)
    y, vy, t, dist = VH * 0.42, 0.0, 0.0, 0.0
    cols, lastGapY = [], VH / 2.0
    deaths = []
    cd = 0.0

    def spawn(x):
        nonlocal lastGapY
        gapH = max(GAPHMIN, GAPH0 - t * GAPSHRINK)
        lo, hi = GAPMARGIN + gapH / 2, VH - GAPMARGIN - gapH / 2
        lo2, hi2 = max(lo, lastGapY - GAPSTEP), min(hi, lastGapY + GAPSTEP)
        gapY = lo2 + rnd.random() * max(0.0, hi2 - lo2)
        lastGapY = gapY
        cols.append({"x": x, "gapY": gapY, "gapH": gapH})

    spawn(VW + 140); spawn(VW + 140 + COLGAP)

    while t < maxT:
        speed = min(SMAX, S0 + t * SACC)
        dx = speed * DT
        t += DT; dist += dx / 20.0

        # --- bot: nham vao tam khe cua cot ke tiep chua vuot qua ---
        target, nxt = VH / 2.0, None
        for c in cols:
            if c["x"] + COLW > BX0 - 4:
                nxt = c; break
        if nxt: target = nxt["gapY"] + rnd.uniform(-8, 8)   # nham khong hoan hao
        # giu phim khi dang o duoi tam khe (bot don gian, khong toi uu)
        holding = y > target - 6
        cd -= DT
        if y > target - 4 and vy > -60 and cd <= 0:
            vy = FLAPV; cd = flapCd          # bat len (co gioi han toc do bam)
        vy += (HOLD if holding else GRAV) * DT
        vy = max(MAXRISE, min(MAXFALL, vy))
        y += vy * DT

        if y - BYTEH / 2 <= 0 or y + BYTEH / 2 >= VH:
            deaths.append(("edge", round(t, 2), round(dist)))
            y = max(BYTEH / 2, min(VH - BYTEH / 2, y)); vy = 0

        for c in cols: c["x"] -= dx
        for c in cols:
            if c["x"] < BX1 and c["x"] + COLW > BX0:
                top, bot = c["gapY"] - c["gapH"] / 2, c["gapY"] + c["gapH"] / 2
                if y - BDY < top or y + BDY > bot:
                    deaths.append(("column", round(t, 2), round(dist)))
                    y = c["gapY"]; vy = 0          # hoi sinh de do het duong
        cols[:] = [c for c in cols if c["x"] + COLW >= -20]
        if not cols or cols[-1]["x"] < VW:
            spawn(cols[-1]["x"] + COLGAP if cols else VW + 140)
    return deaths, dist, max(GAPHMIN, GAPH0 - t * GAPSHRINK)


print("=== 1. Kiem kha nang voi toi: bat 1 lan len duoc bao nhieu px? ===")
# tu vy=0, bat -400 roi giu phim (accel 560 xuong)
y, vy, rise = 0.0, FLAPV, 0.0
while vy < 0:
    vy = min(MAXFALL, vy + HOLD * DT); y += vy * DT
print("   1 cu bat + giu phim -> len %.0f px trong %.2fs" % (-y, 0.714))
print("   Khe lech nhau toi da (gapStep) = %.0f px -> can %.1f cu bat" % (GAPSTEP, GAPSTEP / -y))
gap_time = COLGAP / S0
print("   Thoi gian giua 2 cot o toc do dau = %.2fs (du cho 2-3 cu bat)" % gap_time)
fall_t = math.sqrt(2 * GAPSTEP / GRAV)
print("   Roi %.0f px (tha phim) mat %.2fs -> %s" % (GAPSTEP, fall_t, "DU" if fall_t < gap_time else "THIEU"))
print()

print("=== 2. Do kho theo toc do bam phim cua nguoi choi (8 seed x 180s) ===")
for cd, ten in [(0.10, "bam nhanh"), (0.15, "trung binh"), (0.25, "bam cham"), (0.40, "rat cham")]:
    tot_col = tot_edge = 0
    for s in range(8):
        d, dist, gh = run(s, flapCd=cd)
        tot_col += len([x for x in d if x[0] == "column"])
        tot_edge += len([x for x in d if x[0] == "edge"])
    per_min = (tot_col + tot_edge) / (8 * 3.0)
    print("   nghi %.2fs giua 2 cu bat (%-10s): %2d dung cot, %2d cham mep -> %.2f lan chet/phut"
          % (cd, ten, tot_col, tot_edge, per_min))
print()
d, dist, gh = run(0, maxT=180.0)
print("   Khe hep sau 180s: %.0f px (cham day %.0f px o giay thu %.0f)" % (gh, GAPHMIN, (GAPH0-GAPHMIN)/GAPSHRINK))
print("   Toc do cuon cham tran %.0f px/s o giay thu %.0f" % (SMAX, (SMAX-S0)/SACC))
print("   -> do kho tang cham roi DUNG lai (dung y do 'Diff: De', choi endless duoc lau)")
