# -*- coding: utf-8 -*-
"""
check_earth2d.py — soi TINH ban 2D cua Nhiem Vu 01 o `../react/earth-mission-2d/`.

Repo khong co package.json/tsconfig/node_modules va may khong co Node -> `tsc`
khong chay duoc. Script nay lam thay, va them nhung phep kiem TypeScript khong
lam duoc: doi chieu STEP_IDS voi Missions.cs, kiem URL anh NASA tra 200, va canh
cac quy tac da ghi trong CLAUDE.md.

    cd AstroQhtml
    set PYTHONIOENCODING=utf-8 & python scratchpad/check_earth2d.py

Bo qua phan kiem mang:  python scratchpad/check_earth2d.py --offline

⚠️ Nhan cua check() PHAI KHONG DAU (console Windows cp1252).
"""
import io
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SV = os.path.abspath(os.path.join(ROOT, "..", "AstroqSV"))
M2D = os.path.abspath(os.path.join(ROOT, "..", "react", "earth-mission-2d"))
OFFLINE = "--offline" in sys.argv

ok_n, bad_n = 0, 0


def check(label, cond, detail=""):
    global ok_n, bad_n
    if cond:
        ok_n += 1
        print(f"  [OK]   {label}" + (f"  ({detail})" if detail else ""))
    else:
        bad_n += 1
        print(f"  [HONG] {label}" + (f"  ({detail})" if detail else ""))


def rd(p):
    return io.open(p, encoding="utf-8").read()


def code_only(s):
    """Bo comment truoc khi tim: cac ghi chu o day GIAI THICH vi sao khong dung
    three.js / grayscale / canvas, tim tren van ban tho thi chinh loi canh bao bi
    tinh la vi pham (bai hoc tu check_codex.py)."""
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"^\s*//[^\n]*", " ", s, flags=re.M)
    return s


def brace_errors(s):
    BS, NL = chr(92), chr(10)
    pairs = {"{": "}", "(": ")", "[": "]"}
    closers = set(pairs.values())
    out, stack, i, n, line = [], [], 0, len(s), 1
    while i < n:
        c = s[i]
        if c == NL:
            line += 1; i += 1; continue
        if c == "/" and i + 1 < n and s[i + 1] == "*":
            j = s.find("*/", i + 2)
            line += s.count(NL, i, j if j > 0 else n)
            i = (j + 2) if j > 0 else n; continue
        if c == "/" and i + 1 < n and s[i + 1] == "/":
            j = s.find(NL, i); i = j if j > 0 else n; continue
        if c in ('"', "'", "`"):
            q = c; i += 1
            while i < n and s[i] != q:
                if s[i] == BS: i += 1
                elif s[i] == NL: line += 1
                i += 1
            i += 1; continue
        if c in pairs:
            stack.append((c, line))
        elif c in closers:
            if not stack:
                out.append(f"dong thua '{c}' dong {line}")
            else:
                op, ln = stack.pop()
                if pairs[op] != c:
                    out.append(f"'{op}' dong {ln} dong bang '{c}' dong {line}")
        i += 1
    out += [f"chua dong '{op}' mo o dong {ln}" for op, ln in stack]
    return out


# ══════════════════════════════════════════════════════════════
print("=== [1] File + ngoac ===")
# ⚠️ CometGuidance.tsx + missionChains.ts PHAI nam trong danh sach nay.
#    Chung khong o day thi muc [10] khong thay class `em-` cua overlay Comet ->
#    8 rule CSS cua no bi bao la "bo khong", con class thieu CSS thi khong ai bat.
#    Dung la da tung thieu: `em-spotlight`/`em-target-pulse`/`em-bubble*`/
#    `em-comet-bounce` khong co mot rule nao ma bo kiem van bao 81 dat.
FILES = ["nasaPhotos.ts", "PhotoStage.tsx", "earthMission2dSteps.tsx",
         "EarthMission2D.tsx", "earth-mission-2d.css", "index.ts",
         "CometGuidance.tsx", "missionChains.ts"]
src = {}
for f in FILES:
    p = os.path.join(M2D, f)
    if os.path.exists(p):
        src[f] = rd(p)
    check(f"co file {f}", os.path.exists(p))
if len(src) != len(FILES):
    print("\nDung som: thieu file.")
    sys.exit(1)
for f, s in src.items():
    errs = brace_errors(s)
    check(f"{f}: ngoac can va dung cap", not errs, "; ".join(errs[:3]))

allcode = {f: code_only(s) for f, s in src.items()}

# ══════════════════════════════════════════════════════════════
print("\n=== [2] KHONG CON MOT DAU VET 3D NAO ===")
for pat, label in (
    # ⚠️ ĐỪNG tìm `\bthree\b` trơn: nó khớp chữ "three" trong CÂU TIẾNG ANH của
    #    giao diện ("These three together are why Earth can hold life") và báo
    #    hỏng oan. Phải tìm đúng hình dạng của một lời NHẬP THƯ VIỆN.
    (r"""from ['"]three|require\(['"]three|three@|three\.module|["']three["']\s*:""", "import three"),
    (r"three/addons", "three/addons"),
    (r"THREE\.", "THREE."),
    (r"<canvas", "<canvas"),
    (r"getContext\(", "getContext("),
    (r"WebGL", "WebGL"),
    (r"importmap", "importmap"),
    (r"earth3d", "earth3d.js"),
    (r"PerspectiveCamera|OrbitControls|BufferGeometry|Mesh\(", "API three.js"),
):
    hits = [f for f, s in allcode.items() if re.search(pat, s)]
    check(f"khong file nao dung `{label}`", not hits, f"{hits}")
check("khong nap thu vien animation ngoai",
      not any(re.search(r"from '(framer-motion|gsap|three|@react-three)", s) for s in allcode.values()))

# ══════════════════════════════════════════════════════════════
print("\n=== [3] STEP_IDS khop Missions.cs (DUNG THU TU) ===")
mi = rd(os.path.join(SV, "src/AstroqSV.Api/Services/Missions.cs"))
_earth = mi.split('new("earth", "earth",', 1)[1].split("], DoneMeteors", 1)[0]
sv_ids = [m[0] for m in re.findall(r'new\("([a-z]+)",\s*\d+,\s*\d+,\s*(null|"[a-z0-9,-]+")\)', _earth)]
m = re.search(r"export const STEP_IDS = \[(.*?)\] as const", src["earthMission2dSteps.tsx"], re.S)
check("doc duoc STEP_IDS", bool(m))
cl_ids = re.findall(r"'([a-z]+)'", m.group(1)) if m else []
check("STEP_IDS khop DUNG THU TU voi Missions.cs", sv_ids == cl_ids,
      f"server={sv_ids} client={cl_ids}")
check("du 8 buoc (bo buoc = nhiem vu khong bao gio hoan thanh)",
      len(cl_ids) == 8, f"{len(cl_ids)}")

# Mọi bước phải có nhánh dựng màn trong shell
shell = src["EarthMission2D.tsx"]
missing_case = [s for s in cl_ids if f"case '{s}':" not in shell]
check("moi buoc co nhanh `case` trong shell", not missing_case, f"thieu: {missing_case}")
missing_label = [s for s in cl_ids if not re.search(rf"\b{s}: \{{ vi:", shell)]
check("moi buoc co nhan vi+en o STEP_LABEL", not missing_label, f"thieu: {missing_label}")

# 2 bước server-only phải được khai rõ, không lặng lẽ bỏ
m2 = re.search(r"SERVER_ONLY_STEPS[^=]*=\s*\[(.*?)\]", src["earthMission2dSteps.tsx"], re.S)
so = re.findall(r"'([a-z]+)'", m2.group(1)) if m2 else []
check("2 buoc server doi duoc khai o SERVER_ONLY_STEPS", sorted(so) == ["rotation", "sun"], f"{so}")

# ══════════════════════════════════════════════════════════════
print("\n=== [4] Anh NASA: URL that, bien the that ===")
photos = src["nasaPhotos.ts"]
urls = re.findall(r"(?:src|src2x): '([^']+)'", photos)
check("moi URL anh la https", all(u.startswith("https://") for u in urls), f"{len(urls)} URL")
check("chi dung ten mien NASA",
      all(re.match(r"https://(images-assets|eoimages)\.(nasa\.gov|gsfc\.nasa\.gov)/", u) for u in urls),
      f"la: {[u for u in urls if not re.match(r'https://(images-assets|eoimages)', u)]}")
check("anh Nam Cuc KHONG khai src2x (`~medium` tra 403)",
      not re.search(r"200910220008HQ~medium", photos))
# Nhãn của check() phải không dấu, nhưng ĐIỀU KIỆN thì tra đúng chữ trong file.
check("co ghi chu vi sao `~thumb` khong dung lam LQIP",
      "~thumb" in photos and "CÙNG SỐ BYTE" in photos)
check("moi anh co credit + source de kiem lai",
      photos.count("credit:") == photos.count("source:") == len(re.findall(r"\balt:", photos)),
      f"credit={photos.count('credit:')} source={photos.count('source:')}")

if OFFLINE:
    print("  [..]   bo qua kiem mang (--offline)")
else:
    for u in sorted(set(urls)):
        code = 0
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                code = r.status
        except Exception as e:  # noqa: BLE001
            code = f"loi: {type(e).__name__}"
        check(f"200: ...{u[-46:]}", code == 200, f"{code}")

# ══════════════════════════════════════════════════════════════
print("\n=== [5] DIA LY: lat/lon CHI dung tren ban do phang ===")
steps = src["earthMission2dSteps.tsx"]
check("SampleCollection dung EARTH_EQUIRECT (ban do phang)",
      re.search(r"SampleCollection[\s\S]*?photo=\{EARTH_EQUIRECT\}", steps) is not None)
# latLonToPct chỉ được xuất hiện trong bước life
lat_uses = re.findall(r"latLonToPct", allcode["earthMission2dSteps.tsx"])
check("latLonToPct chi dung 2 lan (import + buoc life)", len(lat_uses) <= 3, f"{len(lat_uses)} lan")
globe_block = allcode["nasaPhotos.ts"]
check("nasaPhotos canh bao KHONG dat lat/lon len anh qua cau",
      "KHONG duoc dat diem mau vat theo lat/lon len anh nay" in
      re.sub(r"[ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠ-ỹ]",
             lambda mm: {"Ô": "O"}.get(mm.group(), mm.group()), src["nasaPhotos.ts"])
      or "lat/lon" in src["nasaPhotos.ts"])
check("4 diem mau vat co lat+lon that", len(re.findall(r"\blat: -?\d", steps)) == 4,
      f"{len(re.findall(r'lat: -?[0-9]', steps))}")

# ══════════════════════════════════════════════════════════════
print("\n=== [6] Hop dong keo-tha: data-want / data-zone ===")
check("vung tha mang `data-zone` (TEN BAT BUOC)", "data-zone" in src["PhotoStage.tsx"])
check("the keo mang `data-want`", steps.count("data-want") >= 2,
      f"{steps.count('data-want')} cho")
check("tim vung tha bang [data-zone], khong phai ten khac",
      "closest<HTMLElement>('[data-zone]')" in steps)
check("dung Pointer Events chu khong phai HTML5 DnD (cam ung)",
      "onPointerDown" in steps and "onDragStart" not in steps)
check("tha ra cho trong thi IM LANG (khong mang oan)",
      steps.count("if (!zoneId) return;") >= 2, f"{steps.count('if (!zoneId) return;')} cho")

# ══════════════════════════════════════════════════════════════
print("\n=== [7] Hieu nang + hinh anh ===")
stage = src["PhotoStage.tsx"]
check("anh khai width + height (chan CLS)", "width={photo.width}" in stage and "height={photo.height}" in stage)
check("anh co loading lazy/eager theo buoc dang mo", "loading={eager ? 'eager' : 'lazy'}" in stage)
check("anh co decoding=async", 'decoding="async"' in stage)
check("dung srcSet + sizes", "srcSet=" in stage and "sizes=" in stage)
check("srcSet CHI them src2x khi co (khong doan bien the)",
      "photo.src2x ?" in stage)
check("hao quang dung dung class de bai yeu cau",
      "drop-shadow-[0_0_35px_rgba(56,189,248,0.6)]" in stage)
check("khoi tha khong bi phong to theo zoom (chong-phong 1/zoom)",
      "scale(${1 / zoom})" in stage)
check("keo xong KHONG tinh la mot cu bam", "DRAG_SLOP" in stage)
check("KHONG dung filter grayscale de lam mo",
      not any("grayscale" in s for s in allcode.values()))
check("khung nhin co touchAction none (keo khong lam cuon trang)",
      "touchAction: 'none'" in stage)

# ══════════════════════════════════════════════════════════════
print("\n=== [8] KHONG tu quyet phan thuong (quy tac muc [3b]) ===")
sh = allcode["EarthMission2D.tsx"]
check("chi cong tu r.awarded / r.xpGained", "r.awarded ?? 0" in sh and "r.xpGained ?? 0" in sh)
bad_num = re.findall(r"(?:meteors|xp|awarded|reward)\s*[:=]\s*(?!0\b)\d+", sh)
check("khong co so thuong viet cung trong shell", not bad_num, f"{bad_num}")
check("huy hieu CHI hien khi server bao newBadges", "r.newBadges" in sh)
check("mat mang / chua dang nhap thi noi that chu khong bia",
      "totals.meteors === 0 && totals.xp === 0" in sh)
check("loi mang KHONG chan giao dien (catch nuot loi co y)",
      re.search(r"catch\s*\{", sh) is not None)
# ⚠️ PHEP KIEM NAY DA DAO CHIEU (30/07/2026). Truoc day no doi mot nut Mat Trang
#    `disabled` o man tong ket. De bai moi doi BO HAN moi thu ve Mat Trang, nen
#    gio phai canh dieu nguoc lai: khong mot nut / nhan / dong "sap ra mat" nao.
#    Server VAN giu `Unlocks: "moon"` - do la du lieu cua server, khong phai giao
#    dien, nen chi soi shell chu khong soi `missionChains.ts` (kieu `MissionTopic`
#    o do co nhanh 'moon' cho cac chuoi sau, dung nhu vay).
moon_hits = re.findall(r"moon|Mat Trang|MAT TRANG|Mặt Trăng|MẶT TRĂNG|🌙", sh)
check("man tong ket KHONG con dau vet Mat Trang nao", not moon_hits, f"{moon_hits}")
check("noi ro Kho Mau Vat do SERVER suy ra, client khong ghi duoc",
      "khong ghi duoc" in src["earthMission2dSteps.tsx"]
      or "cannot add them" in src["earthMission2dSteps.tsx"])

# ══════════════════════════════════════════════════════════════
print("\n=== [9] DUNG LAI, KHONG CHEP ===")
check("dung lai ERAS/ENERGY_SOURCES tu EarthMissionSteps",
      "from '../EarthMissionSteps'" in steps)
check("dung lai component EcoHeroSorting cho buoc eco",
      "EcoHeroSorting" in shell and "from '../EarthMissionSteps'" in shell)
for name in ("ERAS", "ENERGY_SOURCES", "ECO_ACTIONS"):
    check(f"KHONG khai lai `{name}` o ban 2D",
          not re.search(rf"^(export )?const {name}\s*[:=]", steps, re.M))

# ══════════════════════════════════════════════════════════════
print("\n=== [10] CSS: class `em-` hai chieu + giam chuyen dong ===")
css = src["earth-mission-2d.css"]
defined = set(re.findall(r"\.(em-[a-z0-9-]+)", css))

# ⚠️ QUÉT TRÊN CODE ĐÃ BÓC COMMENT, KHÔNG chỉ quét `className=`.
#    Bản đầu chỉ đọc `className=` và báo oan 5 rule "bỏ không"
#    (`em-era`, `em-era-magma|ocean|dino`, `em-night`) — chúng được dùng thật
#    nhưng qua `imageClassName=` và qua một mảng dữ liệu (`filter: 'em-era-magma'`),
#    hai lối mà phép quét hẹp đó không thấy.
#    Nhưng cũng KHÔNG quét bừa cả file: `em-win-title` là ID phần tử
#    (`id=` + `aria-labelledby=`), không phải class — nên phải trừ ra, không thì
#    lại báo oan theo chiều ngược lại.
used, id_names = set(), set()
for f, s in src.items():
    if not f.endswith(".tsx"):
        continue
    used |= set(re.findall(r"\b(em-[a-z0-9-]+)", allcode[f]))
    id_names |= set(re.findall(r'(?:id|aria-labelledby)="(em-[a-z0-9-]+)"', s))
used -= id_names
check("phan biet duoc class voi id (em-win-title la id)", "em-win-title" in id_names)
check("moi class em- dung trong tsx deu co CSS", used <= defined, f"thieu CSS: {sorted(used - defined)}")
check("khong co rule em- bo khong", defined <= used, f"bo khong: {sorted(defined - used)}")
check("co @media prefers-reduced-motion", "prefers-reduced-motion" in css)
rm = css.split("prefers-reduced-motion", 1)[1]
for anim in ("em-pulse", "em-led", "em-scanbeam", "em-shield"):
    check(f"animation vo han `{anim}` bi tat khi giam chuyen dong", anim in rm)
check("GIU phan doi tong thoi ky khi giam chuyen dong (do la noi dung bai hoc)",
      "NOI DUNG" in css or "NỘI DUNG" in css)
check("tia quet MANH, khong phai dai sang day",
      "0.55" in css and "clip-path" in css)

# ══════════════════════════════════════════════════════════════
print("\n=== [11] LUONG HAU-NHIEM-VU: ve Trung Tam Dieu Huong + Comet chi duong ===")
guide = src["CometGuidance.tsx"]
gcode = allcode["CometGuidance.tsx"]
chains = src["missionChains.ts"]
ccode = allcode["missionChains.ts"]

# --- (1) man tong ket: nut nhan thuong + duong ve tu dong ---
check("nut nhan thuong noi ro la ve dau (khong phai chi 'Dong')",
      "NHAN THUONG & VE" in sh.upper().replace("Ậ", "A").replace("Ề", "E")
      or "NHẬN THƯỞNG & VỀ" in sh)
check("duong ve tu dong dat 5 giay dung nhu de bai",
      re.search(r"DEFAULT_AUTO_RETURN = 5\b", sh) is not None)
check("tat duoc duong ve tu dong (autoReturnSeconds = 0)",
      "autoReturnSeconds" in sh)
# ⚠️ Dem gio CHI duoc bat dau sau khi bao xong len server: dem ngay luc mo modal
#    thi mang cham la tre bi keo di truoc khi con so thuong kip ve.
check("CHI dem gio khi da bao xong len server (khong keo tre di truoc khi co so)",
      re.search(r"if \(!win \|\| reporting\) return", sh) is not None)
# ⚠️ Bat ky tuong tac nao cung TAT dem, khong phai tam dung.
for ev in ("onPointerDown", "onMouseEnter", "onKeyDown", "onTouchStart"):
    check(f"`{ev}` tat duong ve tu dong", f"{ev}={{cancelAuto}}" in sh)
check("KHONG bat onFocus (nut co autoFocus -> dem tat ngay khi mo modal)",
      "onFocus={cancelAuto}" not in sh)
check("roi man bang fade-in/fade-out chu khong cat dot ngot",
      "em-fade-out" in sh and "leaving" in sh)

# --- (2) ghi co hoan thanh chuoi ---
check("shell ghi co hoan thanh chuoi qua chainStore",
      "chainStore.markChainComplete(chainId)" in sh)
# ⚠️ Ghi co NGAY luc thang, khong doi tre bam nhan thuong: dong tab o man tong
#    ket thi cong suc van duoc ghi va Comet van chao lan sau.
_next_fn = sh.split("const next =", 1)[1].split("};", 1)[0] if "const next =" in sh else ""
check("ghi co NGAY luc thang, khong doi bam nhan thuong",
      "markChainComplete" in _next_fn)
check("khoa co dung dang de bai (`earth_chain_1_completed`)",
      "earth_chain_1_completed" in chains)
check("co rieng `_greeted` (khong thi Comet chao lai moi lan mo dashboard)",
      "earth_chain_1_greeted" in chains and "greetedKey" in ccode)
check("chuoi RONG khong bao gio tinh la hoan thanh",
      "if (chain.requiredSteps.length === 0) return false" in ccode)
check("cac chuoi Trai Dat tiep theo da khai san (them noi dung, khong sua logic)",
      "earth_chain_2" in chains and "earth_chain_3" in chains)
check("chuoi chua co noi dung phai la status 'soon'",
      ccode.count("status: 'soon'") == 2, f"{ccode.count(chr(39).join(['status: ', 'soon', '']))}")
check("hydrate truoc moi cu ghi (khong thi cu ghi XOA SACH co cu)",
      ccode.count("ensureHydrated()") >= 6, f"{ccode.count('ensureHydrated()')} cho")
check("co getServerSnapshot (thieu la vo hydration khi SSR)",
      "getServerSnapshot" in ccode)
check("server ghi de duoc cache (syncFromServer)", "syncFromServer" in ccode)
check("mo API cho trang vanilla (dashboard.html)", "attachChainBridge" in ccode)

# --- (3) Comet chao + o sang chi duong ---
check("chi chao khi vua xong ma CHUA duoc chao (shouldCelebrate)",
      "snap.hydrated && completed && !greeted" in ccode)
check("loi thoai dung dung cau de bai yeu cau",
      "Xuất sắc lắm!" in guide and "Bảng Nhiệm Vụ" in guide)
check("co ban EN cua loi thoai", "Outstanding!" in guide)
check("dung dung gia tri bong do de bai yeu cau",
      "shadow-[0_0_20px_rgba(56,189,248,0.8)]" in guide
      and "0 0 20px rgba(56, 189, 248, 0.8)" in css)
check("animate-pulse gan san cho luc dashboard duoc port sang React/Tailwind",
      "MISSION_BOARD_PULSE_CLASS" in guide and "animate-pulse" in guide)
check("linh vat co animation nhay mung", "em-comet-bounce" in gcode)
# ⚠️ 4 bai hoc mang tu js/onboard-tour.js
check("(1) o sang TU lam toi ca trang, khong them lop phu toi thu hai",
      "0 0 0 9999px" in css)
check("(2) box thoai co nhanh dat SANG BEN (khong de len the dang gioi thieu)",
      "side: 'right'" in gcode and "side: 'left'" in gcode)
check("(3) co lop trong suot chan bam ra ngoai",
      re.search(r'className="absolute inset-0" aria-hidden="true" onClick=\{dismiss\}', gcode)
      is not None)
check("(4) anh linh vat TO (khung 84px, object-contain)",
      "h-[84px]" in gcode and "object-contain" in gcode)
check("anh loi thi van co linh vat, khong de o trong", "imgOk" in gcode)
check("cuon the dich vao khung nhin TRUOC khi do",
      "scrollIntoView" in gcode)
check("cho cuon xong moi do lan dau (khong do giua luc no con dang bay)",
      re.search(r"setTimeout\(measure, \d{3}\)", gcode) is not None)
check("do lai khi doi co / cuon trang",
      "'resize', measure" in gcode and "'scroll', measure" in gcode)
check("khong tim thay the dich thi VAN chao (chi la khong chieu sang)",
      "em-dim" in gcode)
check("Escape dong duoc overlay", "e.key === 'Escape'" in gcode)
check("moi nhanh dat box co dung mot class that (khong ghep chuoi)",
      all(f"'em-bubble-{s}'" in gcode for s in ("bottom", "top", "right", "left", "center")))
check("KHONG ghep `em-bubble-${...}` (phep kiem [10] chi thay tien to)",
      "em-bubble-${" not in gcode)

# --- (4) TEN KHU VUC: dung ten chinh thuc, khong dat ten thu ba ---
# ⚠️ De bai goi dashboard la "Tram Dieu Khien". Dashboard ten CHINH THUC la
#    "Trung Tam Dieu Huong" (doi 29/07/2026, co phep kiem hai chieu o
#    check_pages.py muc [7]) va moi trang khac deu co nut "Ve Trung Tam Dieu
#    Huong". Dat ten thu ba cho mot cho thi tre khong noi duoc hai thu voi nhau.
check("dung ten chinh thuc `Trung Tam Dieu Huong` cho dashboard",
      "Trung Tâm Điều Hướng" in guide)
# ⚠️ QUET TREN CODE DA BOC COMMENT. `CometGuidance.tsx` co han mot ghi chu GIAI
#    THICH vi sao khong goi dashboard la "Tram Dieu Khien"; tim tren van ban tho
#    thi chinh loi canh bao bi tinh la vi pham. Day la lan thu NAM cung loai loi
#    nay trong du an (xem check_codex.py va muc [2] o tren) - phep kiem phai khop
#    HINH DANG CUA CODE, dung khop chu.
for wrong in ("Trạm Điều Khiển", "Khoang Lái", "Cockpit"):
    hits = [f for f, s in allcode.items() if wrong in s and f.endswith((".tsx", ".ts"))]
    check(f"khong dung ten cu/ten thu ba `{wrong}`", not hits, f"{hits}")
check("ten khu vuc khai MOT cho duy nhat (AREA_NAMES)",
      "AREA_NAMES" in guide and "AREA_NAMES.hub" in sh)
check("index.ts xuat ca phan dashboard (CometGuidance + chainStore)",
      "CometGuidance" in src["index.ts"] and "chainStore" in src["index.ts"])
check("CometGuidance TU nap CSS (mount o dashboard, bundle khac)",
      "import './earth-mission-2d.css'" in guide)

print(f"\n===== {ok_n} dat / {bad_n} hong =====")
sys.exit(1 if bad_n else 0)
