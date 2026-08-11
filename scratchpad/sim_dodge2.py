# -*- coding: utf-8 -*-
"""sim_dodge2.py — ĐO ĐỘ KHÓ CỦA VÀNH ĐAI ĐÁ RỜI (game-dodge.html sau 08/08/2026).

Thay `sim_dodge.py` (bản đó mô phỏng CỘT đá + khe hẹp, cơ chế đã bỏ).

Cách chạy:  python scratchpad/sim_dodge2.py

VÌ SAO PHẢI MÔ PHỎNG CHỨ KHÔNG CHỈ CHƠI THỬ TRÊN TRÌNH DUYỆT
────────────────────────────────────────────────────────────
Hai câu hỏi của lượt việc này không trả lời được bằng cách chơi vài lượt:
  ① **Có bao giờ bịt kín cả chiều cao không?** Đá rải ngẫu nhiên thì "bịt kín" là
     một biến cố hiếm — chơi 20 lượt không gặp KHÔNG chứng minh được gì. Ở đây
     kiểm bằng cách đọc thẳng hình học: mọi đá phải nằm gọn trong làn của nó, và
     làn trống phải thật sự trống trên cả bề rộng của tàu.
  ② **Độ khó có tăng DẦN không?** Cần số chết/phút của TỪNG cấp, mà một lượt chơi
     thật chỉ cho một mẫu.

⚠️ MỌI HẰNG SỐ DƯỚI ĐÂY ĐỌC THẲNG TỪ `game-dodge.html`, KHÔNG GÕ LẠI. Gõ lại là
   sớm muộn bộ đo nói về một game khác với game đang chạy — bài học đã lặp lại
   nhiều lần trong dự án (bản giả `codexTotal: 9` tố cáo oan sản phẩm).
"""
import io
import math
import os
import random
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SRC = io.open(os.path.join(ROOT, "game-dodge.html"), encoding="utf-8").read()


def num(name, default=None):
    m = re.search(r"\b%s:\s*(-?[\d.]+)" % name, SRC)
    if not m:
        if default is not None:
            return default
        raise AssertionError("khong doc duoc CONFIG.%s" % name)
    return float(m.group(1))


def pair(name):
    m = re.search(r"\b%s:\s*\[\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\]" % name, SRC)
    assert m, "khong doc duoc CONFIG.%s" % name
    return float(m.group(1)), float(m.group(2))


VW, VH = num("VW"), num("VH")
GRAV, HOLD, FLAPV = num("gravity"), num("holdAccel"), num("flapV")
MAXFALL, MAXRISE = num("maxFall"), num("maxRise")
SCROLL0, SPEEDLERP = num("scroll0"), num("speedLerp")
LANES, LMARGIN, LPAD = int(num("LANES")), num("laneMargin"), num("lanePad")
LJUMP, WJIT, RHIT = int(num("laneJump")), num("waveJitter"), num("rockHit")
RMIN, RMAX = pair("rockR")
BMIN, BMAX = pair("bigR")
BYTEX, BYTEW, BYTEH, INSET = num("byteX"), num("byteW"), num("byteH"), num("hitInset")

TIERS = []
for m in re.finditer(
        r"\{\s*at:(\d+),\s*gap:(\d+),\s*fill:([\d.]+),\s*min:(\d+),"
        r"\s*drift:(\d+),\s*big:([\d.]+),\s*speed:(\d+)\s*\}", SRC):
    a, g, f, mn, d, b, sp = m.groups()
    TIERS.append(dict(at=float(a), gap=float(g), fill=float(f), min=int(mn),
                      drift=float(d), big=float(b), speed=float(sp)))
assert len(TIERS) >= 3, "doc ra %d cap — sai regex?" % len(TIERS)

DT = 1.0 / 60.0
LANEH = (VH - LMARGIN * 2) / LANES
BX0 = VW * BYTEX - BYTEW / 2 + INSET
BX1 = VW * BYTEX + BYTEW / 2 - INSET
BHALF = (BYTEH - INSET * 1.2) / 2


def laneY(i):
    return LMARGIN + LANEH * (i + 0.5)


def tier_at(sec):
    k = 0
    for i, T in enumerate(TIERS):
        if sec >= T["at"]:
            k = i
    return k


class World:
    """Port TỪNG DÒNG của spawnWave/putRock/update trong game-dodge.html."""

    def __init__(self, seed):
        self.rnd = random.Random(seed)
        self.rocks = []
        self.safe = LANES // 2
        self.nextX = VW + 40
        self.t = 0.0
        self.k = 0
        self.wave = 0          # chi co trong sim: bot can biet da thuoc dot nao
        self.speed = SCROLL0
        self.spawnWave(VW + 120)
        self.spawnWave(VW + 120 + TIERS[0]["gap"])
        self.nextX = VW + 120 + TIERS[0]["gap"] * 2

    def T(self):
        return TIERS[self.k]

    def putRock(self, x, i, big):
        r = (BMIN + self.rnd.random() * (BMAX - BMIN)) if big \
            else (RMIN + self.rnd.random() * (RMAX - RMIN))
        cy = (laneY(i) + laneY(i + 1)) / 2 if big else laneY(i)
        half = (LANEH if big else LANEH / 2) - r - LPAD
        if half < 0:
            half = 0.0
        off = (self.rnd.random() * 2 - 1) * half
        amp = min(self.T()["drift"], max(0.0, half - abs(off)))
        self.rocks.append(dict(
            x=x + (self.rnd.random() - 0.5) * self.T()["gap"] * WJIT,
            y0=cy + off, y=cy + off, amp=amp,
            ph=self.rnd.random() * math.tau, phv=0.7 + self.rnd.random() * 0.6,
            r=r, rc=r * RHIT, lane=i, big=big, wave=self.wave))

    def spawnWave(self, x):
        self.wave += 1
        T = self.T()
        lo = max(0, self.safe - LJUMP)
        hi = min(LANES - 1, self.safe + LJUMP)
        self.safe = lo + self.rnd.randrange(hi - lo + 1)
        filled = [False] * LANES
        if self.rnd.random() < T["big"]:
            pairs = [i for i in range(LANES - 1)
                     if i != self.safe and i + 1 != self.safe]
            if pairs:
                p = pairs[self.rnd.randrange(len(pairs))]
                self.putRock(x, p, True)
                filled[p] = filled[p + 1] = True
        for i in range(LANES):
            if i == self.safe or filled[i]:
                continue
            if self.rnd.random() < T["fill"]:
                self.putRock(x, i, False)
                filled[i] = True
        have = sum(1 for f in filled if f)
        guard = 0
        while have < T["min"] and guard < 8:
            guard += 1
            free = [i for i in range(LANES) if i != self.safe and not filled[i]]
            if not free:
                break
            j = free[self.rnd.randrange(len(free))]
            self.putRock(x, j, False)
            filled[j] = True
            have += 1
        self.nextX = x + T["gap"]

    def step(self):
        self.t += DT
        self.k = tier_at(self.t)
        self.speed += (self.T()["speed"] - self.speed) * min(1.0, DT * SPEEDLERP)
        dx = self.speed * DT
        for a in self.rocks:
            a["x"] -= dx
            if a["amp"] > 0:
                a["ph"] += a["phv"] * DT
                a["y"] = a["y0"] + math.sin(a["ph"]) * a["amp"]
        self.rocks = [a for a in self.rocks if a["x"] + a["r"] >= -24]
        self.nextX -= dx
        if self.nextX <= VW + 40:
            self.spawnWave(VW + 40)
        return dx


def hits(y, rocks):
    """Đúng `hitRock` của game: điểm gần nhất trên hitbox tàu ↔ tâm đá."""
    y0, y1 = y - BHALF, y + BHALF
    for a in rocks:
        cx = max(BX0, min(a["x"], BX1))
        cy = max(y0, min(a["y"], y1))
        dx, dy = a["x"] - cx, a["y"] - cy
        if dx * dx + dy * dy <= a["rc"] * a["rc"]:
            return True
    return False


# ═════════════════════════════════════════════════════════════════════════════
# [1] HÌNH HỌC: làn trống có THẬT SỰ trống không (không cần người chơi)
# ═════════════════════════════════════════════════════════════════════════════
def check_geometry(seeds=60, secs=200.0):
    """Với MỌI đá sinh ra: đá phải nằm gọn trong dải làn của nó, chừa ≥ lanePad.
    Đây là thứ chứng minh 'không bao giờ bịt kín' — mạnh hơn mọi lượt chơi thử."""
    worst = 1e9
    n = 0
    for s in range(seeds):
        w = World(1000 + s)
        seen = set()
        while w.t < secs:
            w.step()
            for a in w.rocks:
                key = id(a)
                if key in seen:
                    continue
                seen.add(key)
                n += 1
                span = LANEH * (2 if a["big"] else 1)
                cy = laneY(a["lane"]) + (LANEH / 2 if a["big"] else 0)
                top, bot = cy - span / 2, cy + span / 2
                # khoảng hở còn lại giữa mép đá và ranh giới dải làn
                worst = min(worst, (a["y"] - a["r"]) - top, bot - (a["y"] + a["r"]))
    return worst, n


def check_corridor(seeds=40, secs=200.0):
    """Ở MỌI khung hình: dải y của LÀN TRỐNG mà đá KHÔNG chạm tới phải cao hơn
    tàu. Đo trên đúng cột x của tàu."""
    worst = 1e9
    for s in range(seeds):
        w = World(7000 + s)
        while w.t < secs:
            w.step()
            # đá đang phủ cột x của tàu
            near = [a for a in w.rocks if a["x"] + a["r"] > BX0 and a["x"] - a["r"] < BX1]
            free = 0.0
            y = LMARGIN
            run = 0.0
            while y <= VH - LMARGIN:
                if hits(y, near):
                    run = 0.0
                else:
                    run += 1.0
                    free = max(free, run)
                y += 1.0
            worst = min(worst, free)
    return worst


# ═════════════════════════════════════════════════════════════════════════════
# [2] ĐỘ KHÓ: bot bay thật, đếm số chết mỗi phút TỪNG CẤP
# ═════════════════════════════════════════════════════════════════════════════
def free_span(rocks, y_lo=None, y_hi=None):
    """Khoảng trống DỌC rộng nhất ở cột x của tàu → (tâm, chiều cao)."""
    if y_lo is None:
        y_lo = LMARGIN + BHALF
    if y_hi is None:
        y_hi = VH - LMARGIN - BHALF
    best_c, best_h, run0 = (y_lo + y_hi) / 2, 0.0, None
    yy = y_lo
    while yy <= y_hi:
        if hits(yy, rocks):
            run0 = None
        else:
            if run0 is None:
                run0 = yy
            h = yy - run0
            if h > best_h:
                best_h, best_c = h, run0 + h / 2
        yy += 2.0
    return best_c, best_h


def survive(seed, t0, limit=60.0, flap_cd=0.15, react=0.0):
    """Bay từ một điểm SẠCH ở giây `t0` cho tới khi chết → trả về số giây sống được.

    ⚠️ ĐỪNG ĐO BẰNG CÁCH "chết rồi hồi sinh rồi đo tiếp". Bản đầu của bộ đo này làm
       thế và cho ra 23–174 chết/phút ở mọi cấp, con số đó ĐỘC LẬP với việc tôi sửa
       bộ điều khiển của bot — dấu hiệu rõ ràng là nó đang đo một thứ khác. Thủ phạm:
       hồi sinh đặt tàu vào `laneY(safe)` của đợt VỪA SINH (còn ở ngoài màn), tức
       thường là giữa một hòn đá đang ở trước mặt → chết lại ngay, chết dây chuyền.
       Một phép đo hỏng theo kiểu đó thì mọi thay đổi đều "không có tác dụng", và
       nó sẽ tố cáo oan sản phẩm.
    ⚠️ Cũng đừng đo từ giây 0 rồi cắt lát theo cấp: cấp 5 chỉ gặp được sau khi đã
       sống qua 120 giây, nên mẫu của cấp 5 chỉ gồm những lượt may mắn.
    """
    w = World(seed)
    while w.t < t0:                 # hâm nóng: thế giới chạy tới đúng cấp cần đo
        w.step()
    near = [a for a in w.rocks if a["x"] + a["r"] > BX0 and a["x"] - a["r"] < BX1 + 60]
    y, _ = free_span(near)          # vào ở chỗ trống, không phải vào giữa hòn đá
    lane = min(range(LANES), key=lambda i: abs(laneY(i) - y))
    vy, cd = 0.0, 0.0
    while w.t < t0 + limit:
        w.step()
        cd -= DT
        # ---- đá đang phủ đúng cột x của tàu (thứ chặn đường đổi làn) ----
        at = [a for a in w.rocks if a["x"] + a["r"] > BX0 - 8 and a["x"] - a["r"] < BX1 + 8]
        # ---- nhìn: làn trống của ĐỢT SẮP TỚI (đợt gần nhất còn ở trước mũi) ----
        ahead = [a for a in w.rocks if a["x"] - a["r"] > BX1]
        want = lane
        if ahead:
            wid = min(a["wave"] for a in ahead)
            grp = [a for a in ahead if a["wave"] == wid]
            occupied = set()
            for a in grp:
                occupied.add(a["lane"])
                if a["big"]:
                    occupied.add(a["lane"] + 1)
            free = [i for i in range(LANES) if i not in occupied]
            if free:
                want = min(free, key=lambda i: abs(i - lane))
        # ---- ĐỔI LÀN THÌ PHẢI CHỜ ĐỢT TRƯỚC ĐI QUA ─────────────────────────────
        #  ⚠️ ĐÂY LÀ THỨ BA BẢN BOT TRƯỚC ĐỀU THIẾU, VÀ NÓ GIẢI THÍCH HẾT SỐ CHẾT
        #     VÔ LÝ: bot nhắm sang làn kế rồi bay thẳng qua ranh giới làn, trong khi
        #     một hòn đá của đợt TRƯỚC vẫn còn nằm ở làn đó ngay trước mũi. Người
        #     chơi thật giữ làn cho tới lúc trống rồi mới sang. Đo được ở bản cũ:
        #     chết ở y=178 vì đá ở y=160 trong khi đích là y=249 — tức là nó tự lao
        #     xuyên qua một hòn đá để đi tới chỗ trống.
        if want != lane:
            step = 1 if want > lane else -1
            y0, y1 = laneY(lane), laneY(lane + step)
            clear = True
            k = 0.0
            while k <= 1.0001:
                if hits(y0 + (y1 - y0) * k, at):
                    clear = False
                    break
                k += 0.2
            if clear:
                lane += step
        target = laneY(lane)
        # ---- bay: bật CHỈ KHI đang ở DƯỚI đích và chưa bay lên ────────────────
        #  ⚠️ BẢN TRƯỚC BẬT THEO VỊ TRÍ DỰ ĐOÁN sau 0,1s, và nó bật cả khi tàu đang
        #     ở TRÊN đích mà rơi xuống nhanh → cú bật cộng dồn thành một cú vọt
        #     ~77px, đủ để lên đụng mép trên. Đo được: y đi từ 57 → 13 (mép) trong
        #     khi đích là 82. Người chơi thật bật khi thấy mình TỤT, không bật theo
        #     một phép dự đoán.
        #  ⚠️ VÀ PHẢI THẢ TAY (không `holding`): giữ tay thì trọng lực chỉ còn 560
        #     nên MỘT cú bật nhấc tàu 400²/(2·560) = 143px — vượt cả một làn.
        if y > target + 6.0 and vy > -80.0 and cd <= 0.0:
            vy = FLAPV
            cd = flap_cd + react
        vy += GRAV * DT
        vy = max(MAXRISE, min(MAXFALL, vy))
        y += vy * DT
        # ---- chết ----
        if y - BYTEH / 2 <= 0 or y + BYTEH / 2 >= VH:
            return w.t - t0
        now = [a for a in w.rocks if a["x"] + a["r"] > BX0 and a["x"] - a["r"] < BX1]
        if hits(y, now):
            return w.t - t0
    return limit


def main():
    print("Doc tu game-dodge.html: LANES=%d laneH=%.1f pad=%.0f jump=%d"
          % (LANES, LANEH, LPAD, LJUMP))
    print("Tau: hitbox %.0fx%.0f (nua cao %.1f), x = %.0f..%.0f"
          % (BYTEW - INSET * 2, BHALF * 2, BHALF, BX0, BX1))
    print("So cap doc duoc: %d  ->  %s\n"
          % (len(TIERS), " | ".join("C%d@%ds v=%d" % (i + 1, T["at"], T["speed"])
                                    for i, T in enumerate(TIERS))))

    print("=== [1] Hinh hoc: da co nam gon trong lan cua no khong ===")
    worst, n = check_geometry()
    print("  %d hon da  ·  ho nho nhat giua mep da va ranh gioi lan: %.2f px" % (n, worst))
    print("  %s da khong bao gio tran khoi lan (can >= 0)\n"
          % ("[ok]  " if worst >= -0.01 else "[FAIL]"))

    print("=== [2] Hanh lang: khoang trong o cot cua tau ===")
    free = check_corridor()
    print("  khoang trong HEP NHAT qua 40 luot x 200s: %.0f px  (tau cao %.0f px)"
          % (free, BHALF * 2))
    print("  %s luon co cho lot (can > %.0f)\n"
          % ("[ok]  " if free > BHALF * 2 else "[FAIL]", BHALF * 2))

    print("=== [3] Do kho tung cap — SO LIEU GIAI TICH (khong phu thuoc bot) ===")
    # ⚠️ PHAI CO MUC NAY. Con so cua bot lan lon voi cai dở của chính con bot: no
    #    dao dong +-26px quanh tam lan, nen thay doi mat do bi nhieu do lam mo. Bon
    #    so duoi day suy thang tu luat sinh dot nen chung tang/giam DON DIEU theo
    #    thiet ke — day moi la bang chung cho "phan cap tang dan".
    prev = None
    for i, T in enumerate(TIERS):
        w = World(4242 + i)
        while w.t < T["at"] + 1.0:
            w.step()
        n_wave, n_rock, corr, samples = 0, 0, 0.0, 0
        t_end = w.t + 40.0
        seen = set()
        while w.t < t_end:
            w.step()
            for a in w.rocks:
                if a["wave"] not in seen:
                    pass
            near = [a for a in w.rocks if a["x"] + a["r"] > BX0 and a["x"] - a["r"] < BX1]
            _, h = free_span(near)
            corr += h
            samples += 1
        # dem lai bang cach sinh rieng: so da moi dot cua cap nay
        w2 = World(777 + i)
        while w2.t < T["at"] + 1.0:
            w2.step()
        before = w2.wave
        cnt = {}
        for _ in range(int(40.0 / DT)):
            w2.step()
            for a in w2.rocks:
                cnt[id(a)] = a["wave"]
        waves = set(cnt.values())
        n_wave = len(waves)
        n_rock = len(cnt)
        wps = T["speed"] / T["gap"]                 # so dot moi giay
        need = LANEH * wps                          # px/s doc phai bay de doi 1 lan/dot
        line = ("     Cap %d: %.2f da/dot  ·  %.2f dot/giay  ·  hanh lang TB %3.0fpx"
                "  ·  can %3.0f px/s doc"
                % (i + 1, n_rock / max(1, n_wave), wps, corr / max(1, samples), need))
        if prev is not None:
            line += "  (kho hon)" if (n_rock / max(1, n_wave)) >= prev else "  <-- KHONG kho hon!"
        prev = n_rock / max(1, n_wave)
        print(line)
    print("     (cu bat nhac tau %.0f px — moc de doi chieu voi hanh lang)"
          % (FLAPV * FLAPV / (2 * GRAV)))
    print()

    print("=== [4] Do kho tung cap: song duoc bao lau tu mot diem sach ===")
    LIMIT, N = 60.0, 60
    for cd_, lbl in ((0.15, "bam nhanh"), (0.40, "bam cham (tre nho)")):
        print("  -- %s --" % lbl)
        prev = None
        for i, T in enumerate(TIERS):
            xs = [survive(9000 + i * 100 + k, T["at"] + 1.0, LIMIT, flap_cd=cd_)
                  for k in range(N)]
            mean = sum(xs) / len(xs)
            full = sum(1 for x in xs if x >= LIMIT)
            rate = 60.0 / mean if mean > 0 else 999.0
            arrow = ""
            if prev is not None:
                arrow = "  (kho hon cap truoc)" if mean < prev else "  <-- KHONG kho hon!"
            print("     Cap %d: song TB %5.1fs  ·  %2d/%d luot tron %ds  ·  %.2f chet/phut%s"
                  % (i + 1, mean, full, N, int(LIMIT), rate, arrow))
            prev = mean
    print()
    print("(Cap sau phai song NGAN hon cap truoc — do la 'phan cap tang dan')")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
