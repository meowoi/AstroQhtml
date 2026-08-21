# -*- coding: utf-8 -*-
r"""Đo CÂN BẰNG của Đường Đua Sao Chổi sau khi có đối thủ + skill tăng tốc.

⚠️⚠️ VÌ SAO PHẢI ĐO, KHÔNG PHẢI CHƠI THỬ VÀI LƯỢT: quãng đường của trẻ trước lượng
này **không phụ thuộc trẻ chơi hay hay dở** (đâm đá chỉ mất nhiên liệu, không mất
tốc độ). Thả đối thủ có tốc độ cố định vào một đường đua như thế thì kết quả là
TẤT ĐỊNH — hoặc luôn thắng, hoặc luôn thua. Skill tăng tốc là thứ duy nhất trẻ
dùng để đổi kết quả, nên câu hỏi cân bằng là một câu hỏi SỐ HỌC:

  ① Không tăng tốc lần nào thì có CHẮC CHẮN không thắng? (nếu không thì skill vô
     nghĩa — trẻ thắng mà chẳng cần làm gì)
  ② Tăng tốc đủ số lần mà một lượt chơi tốt LẤY ĐƯỢC thì có thắng? (nếu không thì
     đường đua là bất khả thi và trẻ bỏ)
  ③ Nhiên liệu có ĐỦ cho số lần tăng tốc đó? (skill mà không trả nổi giá thì nó
     chỉ là một cái nút để nhìn)

Cùng lối `sim_dodge2.py` (ARCADE-01) và mục [2] của `play_recycle`/`play_units`:
đọc hằng số THẲNG từ file game rồi tích phân, không gõ lại con số nào ở đây.

⚠️ ĐỔI `raceLen` / `speed*` / `boost*` / `rivals` thì CHẠY LẠI BỘ NÀY TRƯỚC.
"""
import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
DT = 1.0 / 60.0
ok_n = bad_n = 0


def check(cond, name, extra=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print("  [OK]   " + name + (("  (%s)" % extra) if extra else ""))
    else:
        bad_n += 1
        print("  [HONG] " + name + (("  (%s)" % extra) if extra else ""))


def cfg():
    """Doc CONFIG cua game-racer.html — nguon su that duy nhat."""
    src = io.open("game-racer.html", encoding="utf-8", newline=None).read()
    i = src.index("var CONFIG = {")
    blk = src[i:src.index("\n  };", i)]
    # BOC CHU THICH TRUOC KHI DOC SO. Ban dau cua bo nay doc ra `raceLen = 1200`
    # — con so do nam trong mot GHI CHU ("Ban dau de raceLen: 1200...") chu khong
    # phai gia tri dang chay (14000). Lop loi "dem ca chu trong ghi chu cua chinh
    # minh" da lap rat nhieu lan trong du an; moi phep doc CONFIG phai boc truoc.
    blk = re.sub(r"/\*.*?\*/", " ", blk, flags=re.S)
    blk = re.sub(r"//[^\n]*", " ", blk)
    out = {}
    for k in ("raceLen speed0 speedMax speedRamp fuel0 fuelDrain fuelCan hitCost "
              "pickEvery gemChance clusterEvery boostNeed boostPerGem boostMs "
              "boostMul boostFuel").split():
        m = re.search(k + r":\s*([0-9.]+)", blk)
        assert m, "khong doc duoc " + k
        out[k] = float(m.group(1))
    riv = []
    for rid, f, be, bms, bmul in re.findall(
            r'id:"([a-z]+)",\s*f:([0-9.]+),\s*bEvery:([0-9.]+),'
            r'\s*bMs:([0-9.]+),\s*bMul:([0-9.]+)', blk):
        riv.append({"id": rid, "f": float(f), "bEvery": float(be),
                    "bMs": float(bms), "bMul": float(bmul)})
    out["rivals"] = riv
    return out


C = cfg()
LEN = C["raceLen"]


def base_speed_series(tmax=200.0):
    """Duong cong tang toc dung cong thuc cua game, tra ve list (t, speed)."""
    v = C["speed0"]
    t = 0.0
    out = []
    while t < tmax:
        v += (C["speedMax"] - v) * min(1.0, C["speedRamp"] * DT)
        out.append(v)
        t += DT
    return out


SPD = base_speed_series()


def run_player(nboost):
    """Tra ve (giay ve dich, so lan tang toc that su dung, nhien lieu can).

    Lan tang toc thu i chi bam duoc khi da hung du tinh the cho no. Tinh the roi
    trung binh moi `pickEvery/gemChance` met, va mot lan tang toc can
    `boostNeed/boostPerGem` viên → mốc mét của lần thứ i tính được. Đây là mô hình
    "trẻ hứng được gần hết vật phẩm" — tức GIỚI HẠN TRÊN của một lượt chơi tốt.
    """
    per_gem = C["pickEvery"] / C["gemChance"]
    gems_per_boost = C["boostNeed"] / C["boostPerGem"]
    gate = [i * gems_per_boost * per_gem for i in range(1, nboost + 1)]
    d = 0.0
    t = 0.0
    bt = 0.0
    used = 0
    fuel_used = 0.0
    k = 0
    while d < LEN and k < len(SPD):
        v = SPD[k]
        if bt <= 0 and used < nboost and d >= gate[used]:
            used += 1
            bt = C["boostMs"] / 1000.0
            fuel_used += C["boostFuel"]
        mul = C["boostMul"] if bt > 0 else 1.0
        d += v * mul * DT
        fuel_used += C["fuelDrain"] * DT
        if bt > 0:
            bt -= DT
        t += DT
        k += 1
    return t, used, fuel_used


def run_rival(r):
    d = 0.0
    t = 0.0
    bt = 0.0
    nxt = r["bEvery"]
    nb = 0
    k = 0
    while d < LEN and k < len(SPD):
        if bt > 0:
            bt -= DT
        elif d >= nxt:
            nxt += r["bEvery"]
            bt = r["bMs"] / 1000.0
            nb += 1
        mul = r["bMul"] if bt > 0 else 1.0
        d += SPD[k] * r["f"] * mul * DT
        t += DT
        k += 1
    return t, nb


print("=== Doc tu game-racer.html ===")
print("   duong dua %.0f m · toc do %.0f→%.0f · tang toc x%.2f trong %.1fs, "
      "%.0f%% nhien lieu/lan"
      % (LEN, C["speed0"], C["speedMax"], C["boostMul"],
         C["boostMs"] / 1000.0, C["boostFuel"]))

rt = []
for r in C["rivals"]:
    t, nb = run_rival(r)
    rt.append((t, r["id"], nb))
    print("   doi thu %-6s f=%.3f -> ve dich %5.1fs (tang toc %d lan)"
          % (r["id"], r["f"], t, nb))
best_rival = min(rt)
print("   => doi thu nhanh nhat: %s %.1fs" % (best_rival[1], best_rival[0]))

print("\n=== Tre voi k lan tang toc ===")
rows = []
for k in range(0, 11):
    t, used, fu = run_player(k)
    if used < k:
        continue                      # khong hung du tinh the cho k lan
    rows.append((k, t, fu))
    print("   k=%-2d -> %5.1fs  (nhien lieu can %5.1f%%)  %s"
          % (k, t, fu, "THANG" if t < best_rival[0] else "thua"))

print()
# ① Khong tang toc thi phai KHONG thang
t0 = rows[0][1]
check(t0 > best_rival[0],
      "khong tang toc lan nao thi KHONG thang (skill co nghia)",
      "tre %.1fs vs %s %.1fs" % (t0, best_rival[1], best_rival[0]))

# ② Phai co mot so lan tang toc DAT DUOC ma thang
per_gem = C["pickEvery"] / C["gemChance"]
gems = LEN / per_gem
max_boost = int(gems * C["boostPerGem"] / C["boostNeed"])
wins = [r for r in rows if r[1] < best_rival[0]]
kmin = wins[0][0] if wins else None
check(kmin is not None and kmin <= max_boost,
      "thang duoc bang so lan tang toc mot luot LAY DUOC",
      "can %s lan, ca duong dua co ~%d vien tinh the -> toi da %d lan"
      % (kmin, round(gems), max_boost))

# ③ Khong duoc thang qua de: phai dung it nhat mot phan ba so lan lay duoc
check(kmin is not None and kmin >= 2,
      "khong thang bang mot lan bam duy nhat (con la thu thach)",
      "can %s lan" % kmin)

# ④ Nhien lieu phai du cho so lan do
cans = LEN / C["pickEvery"] * (1 - C["gemChance"])
avail = C["fuel0"] + cans * C["fuelCan"]
need = wins[0][2] if wins else 0
check(wins and need < avail,
      "nhien lieu DU cho luot thang do (skill tra noi gia cua no)",
      "can %.0f%%, co toi da %.0f%% (%d thung)" % (need, avail, round(cans)))

# ⑤ Ba doi thu phai khac nhau — bang khong thi ba cai dau tren dai dua dinh lien
ts = sorted(x[0] for x in rt)
gaps = [round(ts[i + 1] - ts[i], 2) for i in range(len(ts) - 1)]
check(all(g >= 0.8 for g in gaps),
      "ba doi thu ve dich cach nhau du xa de doc ra la ba tay dua",
      "cach nhau %s giay" % gaps)

# ⑥ Doi thu cham nhat khong duoc cham hon ca luot khong tang toc + nhieu
check(max(ts) < t0 + 12,
      "doi thu cham nhat khong bi bo lai qua xa (van la mot cuoc dua)",
      "cham nhat %.1fs vs tre khong tang toc %.1fs" % (max(ts), t0))

print("\n" + "=" * 56)
print("KET QUA: %d dat / %d hong" % (ok_n, bad_n))
sys.exit(1 if bad_n else 0)
