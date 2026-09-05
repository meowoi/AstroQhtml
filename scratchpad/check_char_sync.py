# -*- coding: utf-8 -*-
"""check_char_sync.py — CAU NOI NHAN VAT giua cache trong may va ho so tren server.

VI SAO CO BO DO NAY (22/08/2026)
--------------------------------
Chu du an bao: "da dang nhap nhieu lan roi ma dang nhap lai van phai chon nhan vat".
Doc ca luong ra HAI lo hong doc lap, moi cai mot minh da du gay loi:

  [A] `select.html` CO Y khong nap SDK Firebase nen khong co token => nhan vat
      chi duoc ghi vao `localStorage`, KHONG BAO GIO len server. Duong ghi duy
      nhat vao truong `character` la `PUT /me/profile`, ma no chi duoc goi tu
      `profile.html` (doi trang phuc). Nen `PROFILE.character` tren DynamoDB
      RONG vinh vien voi moi tre chua vao trang Ho so.

  [B] `logout()` xoa SACH moi khoa `astroq-*` (co y — may dung chung), ma
      `syncProfile()` luc dang nhap chi ghi lai uid/email/name/admin. Nen
      `astroq-user.character` LUON rong sau khi dang nhap, va `go()` o
      js/firebase-auth-ui.js doc dung truong do de chon dashboard hay select.

Bo do nay do CA HAI, tren CHINH `js/characters.js` + `js/progress.js` that
(khong ban sao), bang cach gia lap `auth` de soi duoc server nhan gi.

  python scratchpad/check_char_sync.py
"""
import pathlib
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
HARNESS = HERE / "_char_sync_harness.html"

OK = "  [OK]  "
NG = "  [HONG]"
_n = {"ok": 0, "ng": 0}


def chk(name, cond, extra=""):
    tag = OK if cond else NG
    _n["ok" if cond else "ng"] += 1
    print(tag + " " + name + (("  [" + str(extra) + "]") if extra else ""))


def _no_comments(src):
    """Bo comment ma GIU chuoi — moi phep kiem dang 'khong duoc chua X' phai
    chay tren ban nay, khong thi chinh loi ghi chu giai thich vi sao khong dung
    X lai bi tinh la vi pham (loi da lap rat nhieu lan trong du an)."""
    out, i, n = [], 0, len(src)
    while i < n:
        c = src[i]
        if c in "\"'":
            q = c
            out.append(c)
            i += 1
            while i < n:
                if src[i] == "\\":
                    out.append(src[i:i + 2])
                    i += 2
                    continue
                out.append(src[i])
                if src[i] == q:
                    i += 1
                    break
                i += 1
            continue
        if src.startswith("//", i):
            while i < n and src[i] != "\n":
                i += 1
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        out.append(c)
        i += 1
    return "".join(out)


def browser_tests():
    print("\n=== [1] CHAY THAT tren js/characters.js + js/progress.js ===")
    errs = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page()
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(HARNESS.as_uri())
        pg.wait_for_function("window.__done === true", timeout=20000)
        log = pg.inner_text("#out")
        b.close()

    lines = [l for l in log.splitlines() if l.strip()]
    if not lines:
        chk("gian kiem co chay", False, "0 dong ket qua")
        return
    for l in lines:
        chk(l[6:].strip(), l.startswith("PASS"))
    chk("0 loi trang", not errs, "; ".join(errs[:3]))


def static_tests():
    ch = (ROOT / "js" / "characters.js").read_text(encoding="utf-8")
    pr = (ROOT / "js" / "progress.js").read_text(encoding="utf-8")
    fa = (ROOT / "js" / "firebase-auth.js").read_text(encoding="utf-8")
    af = (ROOT / "js" / "auth-flow.js").read_text(encoding="utf-8")
    ui = (ROOT / "js" / "firebase-auth-ui.js").read_text(encoding="utf-8")
    me = (ROOT.parent / "AstroqSV" / "src" / "AstroqSV.Api" / "Endpoints"
          / "MeEndpoints.cs").read_text(encoding="utf-8-sig")

    ch_c, pr_c, fa_c, af_c = (_no_comments(x) for x in (ch, pr, fa, af))

    print("\n=== [2] PHIA DOC: dang nhap phai KEO ho so ve cache ===")
    chk("firebase-auth.js co hydrateProfile", "function hydrateProfile" in fa_c)
    # Lo hong [B]: khong await thi nguoi goi chuyen trang truoc khi loi goi ve.
    m = re.search(r"async login\(.*?\n  \},", fa_c, re.S)
    body = m.group(0) if m else ""

    # ⚠️⚠️ ĐI THEO MỘT CẤP `await`, KHÔNG GHIM HÌNH DẠNG CODE. Bản cũ đòi
    #    `await hydrateProfile(` nằm THẲNG trong thân `login()`; ngày 05/09/2026 nó
    #    báo hỏng 2 phép kiểm trong khi sản phẩm hoàn toàn đúng — `syncProfile` và
    #    `await hydrateProfile` đã tách ra hàm `afterSignIn(api, user)` mà `login()`
    #    await, tức HÀNH VI KHÔNG ĐỔI, chỉ ĐỔI CHỖ. (Chứng minh nó là lỗi CÓ SẴN chứ
    #    không phải hồi quy: thân `login()` cắt ra từ HEAD và từ bản hiện tại dài y
    #    hệt 993 ký tự và cùng thiếu chuỗi đó.)
    # ⚠️ KHÔNG nới lỏng: điều phải bảo đảm — *đường đăng nhập CHỜ hydrateProfile xong
    #    rồi mới trả lời* — giữ nguyên; chỉ thôi đòi nó nằm ở đúng một chỗ. Người gọi
    #    chuyển trang NGAY sau khi `login()` trả về, nên bỏ chạy nền là `unload` cắt
    #    giữa đường và lỗi "đăng nhập lại phải chọn lại nhân vật" quay lại.
    def _than(ten):
        """Thân một hàm khai ở cấp 0 (`async function x(...)` / `function x(...)`)."""
        mm = re.search(r"(?:async\s+)?function\s+" + re.escape(ten) + r"\s*\(.*?\n\}",
                       fa_c, re.S)
        return mm.group(0) if mm else ""

    _ung = [body] + [_than(t) for t in
                     set(re.findall(r"await\s+([A-Za-z_$][\w$]*)\s*\(", body))]
    _cho = next((b for b in _ung if re.search(r"await\s+hydrateProfile\(", b)), "")
    chk("duong dang nhap CHO hydrateProfile xong (khong bo chay nen)", bool(_cho))
    chk("hydrateProfile goi SAU syncProfile",
        bool(_cho) and 0 <= _cho.find("syncProfile(") < _cho.find("hydrateProfile("))
    chk("hydrateProfile co HAN CHO (fail-open, khong chan cua vao app)",
        "HYDRATE_MS" in fa_c and "Promise.race" in fa_c)
    chk("hydrateProfile ghi character vao cache", "next.character" in fa_c)
    chk("hydrateProfile ghi ca alias selectedCharacter", "next.selectedCharacter" in fa_c)
    chk("hydrateProfile keo ca bac (depth) ve", "next.depth" in fa_c)
    # Ghi 'avatarZoom' o day la de HAI cho cung giu mot luat (zoom la cua characters.js).
    chk("hydrateProfile KHONG doan avatarZoom", "avatarZoom" not in fa_c)
    chk("chi ghi truong server CO (khong ghi '' de len cache)",
        bool(re.search(r"if\(p\.character\)", fa_c)))

    print("\n=== [3] PHIA GHI: cau noi hai chieu ===")
    for fn in ("function get(", "function chosen(", "function absorb(",
               "function syncUp(", "function sync(", "function touch("):
        chk("characters.js co " + fn + ")", fn in ch_c)
    chk("dong dau theo uid (hai dua tre dung chung may)",
        'LS_SYNC = "astroq-char-synced"' in ch_c)
    # Thu tu nhanh la LUAT: nhanh 'day len' phai dung TRUOC nhanh 'keo ve',
    # khong thi lua chon moi o select.html bi gia tri cu tren server ghi nguoc.
    m = re.search(r"function sync\(auth, uid, serverChar, serverAvatar\)\s*\{(.*?)\n  \}", ch_c, re.S)
    sb = m.group(1) if m else ""
    chk("sync(): doc duoc than ham", bool(sb))
    chk("sync(): nhanh DAY LEN dung TRUOC nhanh KEO VE",
        bool(sb) and sb.find("pendingUp(") < sb.find("absorb("))
    chk("sync(): co nhanh 'hai ben da khop' (khoi PUT vo nghia moi lan dang nhap)",
        "stampNow(" in sb)
    chk("syncUp(): gui ten trong gioi han 24 ky tu cua server",
        bool(re.search(r"nm\.length\s*<=\s*24", ch_c)))
    chk("syncUp(): chi dong dau khi server nhan (r.ok)",
        bool(re.search(r"if\s*\(r && r\.ok\)\s*\{[^}]*setItem\(LS_SYNC", ch_c)))
    chk("absorb(): id la thi GIU NGUYEN cache", bool(re.search(r"if \(!c\) return \"\";", ch_c)))

    print("\n=== [4] NOI DAY: progress.js va select.html ===")
    chk("progress.js co syncIdentity", "function syncIdentity" in pr_c)
    chk("syncIdentity nam trong load()  (GET /me/profile)",
        pr_c.count("syncIdentity(a, r.data)") >= 1)
    # Hai route tra hai hinh dang: /me/achievements phang o goc, /me/profile boc trong profile{}.
    chk("syncIdentity nhan CA HAI hinh dang response",
        "data.profile || data" in pr_c)
    # Dem LOI GOI, khong dem ca dong khai bao `function syncIdentity(auth, data)`
    # — no cung bat dau bang "syncIdentity(a".
    n_call = len(re.findall(r"(?<!function )syncIdentity\(a,", pr_c))
    chk("syncIdentity noi vao dung 2 cho (load + achievements)", n_call == 2, n_call)
    chk("syncIdentity KHONG await (viec nen, khong chan giao dien)",
        "await syncIdentity" not in pr_c and "return syncIdentity" not in pr_c)
    chk("select.html danh dau 'lua chon chua gui' (AstroQChars.touch)",
        "AstroQChars.touch()" in af_c)
    m = re.search(r"function startJourney\(\)\s*\{(.*?)\n  \}", af_c, re.S)
    sj = m.group(1) if m else ""
    chk("touch() goi SAU khi ghi ho so vao localStorage",
        bool(sj) and sj.find("setItem(LS_USER") < sj.find("AstroQChars.touch()"))

    print("\n=== [5] TRANG NAO DUNG THI PHAI NAP characters.js ===")
    for page in ("dashboard.html", "achievements.html", "codex.html",
                 "certificate.html", "profile.html"):
        html = (ROOT / page).read_text(encoding="utf-8")
        # Phai bat dung THE <script>, khong bat chuoi trong khoi ghi chu —
        # ghi chu cua chinh lan sua nay co nhac ten hai file do.
        def tag_at(f):
            m = re.search(r'<script[^>]+src="[^"]*' + re.escape(f) + r'"', html)
            return m.start() if m else -1
        i_ch, i_pr = tag_at("js/characters.js"), tag_at("js/progress.js")
        chk(page + ": nap characters.js", i_ch >= 0)
        if i_ch >= 0 and i_pr >= 0:
            chk(page + ": characters.js nap TRUOC progress.js", i_ch < i_pr,
                "ch=%d pr=%d" % (i_ch, i_pr))

    print("\n=== [6] SERVER: /me/achievements phai tra nhan vat ===")
    m = re.search(r'MapGet\("/achievements".*?\n        \}\);', me, re.S)
    ach = m.group(0) if m else ""
    chk("doc duoc route /me/achievements", bool(ach))
    for f in ("character", "avatar", "name"):
        chk("/me/achievements tra ve " + f,
            bool(re.search(r"\b" + f + r"\s*=\s*prof is null", ach)))
    # 0 luot doc DynamoDB them: `prof` da nam trong tay tu truoc (dung cho `depth`).
    chk("dung lai `prof` da doc san (0 luot doc them)", ach.count("GetUserAsync") == 1,
        ach.count("GetUserAsync"))
    chk("PUT /me/profile van nhan `character`", "req.Character" in me)

    print("\n=== [8] TRE CU bi buoc qua select.html: KHONG nem lai vao onboarding ===")
    # `/me/profile` phai tra co, va tra o CHINH item da doc (0 luot doc them).
    m = re.search(r'MapGet\("/profile".*?\n        \}\);', me, re.S)
    prof = m.group(0) if m else ""
    chk("doc duoc route GET /me/profile", bool(prof))
    chk("/me/profile tra ve `map01Seen`", "map01Seen =" in prof)
    chk("khong doc them DynamoDB (dung lai `profile` da co)",
        prof.count("GetUserAsync") == 1, prof.count("GetUserAsync"))
    # hydrate phai ghi cache, va CHI khi server noi true.
    chk("hydrateProfile ghi cache astroq-map01-seen",
        'setItem("astroq-map01-seen"' in fa_c)
    chk("chi ghi khi server noi TRUE (khong xoa dau cua tre da xem)",
        bool(re.search(r"p\.map01Seen === true", fa_c)))
    # select.html phai re nhanh theo co, khong theo "vua bam chon xong".
    chk("auth-flow.js co ham returning()", "function returning()" in af_c)
    chk("returning() doc dung khoa cache",
        bool(re.search(r'returning\(\)\s*\{[^}]*astroq-map01-seen', af_c, re.S)))
    m = re.search(r"function startJourney\(\)\s*\{(.*?)\n  \}", af_c, re.S)
    sj = m.group(1) if m else ""
    chk("startJourney(): dich den re theo returning()", "returning()" in sj)
    chk("startJourney(): tre CU ve dashboard, tre MOI van sang ban do",
        bool(re.search(r'skipIntro \? "dashboard\.html" : "explorer\.html\?onboard=1"', sj)))
    chk("startJourney(): admin van bo qua onboarding (khong lam mat nhanh cu)",
        "admin ||" in sj)
    # Cau chu: khong duoc goi la "cap the ID moi" voi mot tre da choi ca thang.
    for k in ("title_back", "subtitle_back", "start_back"):
        # ⚠️ Phai co ranh gioi tu: `subtitle_back:` CHUA chuoi `title_back:`,
        #    dem thang chuoi con thi ra 4 thay vi 2 (cung bay `map01Seen` la
        #    tien to cua `map01SeenAt` da ghi 01/08/2026).
        n = len(re.findall(r"(?<![A-Za-z_])" + k + r":", af_c))
        chk("khoa `" + k + "` khai o CA vi va en", n == 2, n)
    chk("doi cau chu SAU applyTexts (khong thi bi ghi de)",
        af_c.find("AstroQ.applyTexts(t)") < af_c.find('t("title_back")'))

    print("\n=== [7] CHOT CHAN: khong duoc quay lai trang thai cu ===")
    # Neu ai do bo hydrateProfile thi go() lai luon doc ra rong => loi quay lai y nguyen.
    chk("go() van quyet duong di bang u.character (nen hydrate la BAT BUOC)",
        "u.character ?" in ui)
    chk("logout() van don sach cache (giu quyet dinh may dung chung)",
        "clearAccountData" in (ROOT / "js" / "firebase-auth.js").read_text(encoding="utf-8"))


def main():
    if not HARNESS.exists():
        print("[X] Khong thay " + HARNESS.name)
        return 1
    browser_tests()
    static_tests()
    print("\n=== KET QUA: %d dat / %d hong ===" % (_n["ok"], _n["ng"]))
    return 1 if _n["ng"] else 0


if __name__ == "__main__":
    sys.exit(main())
