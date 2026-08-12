"""check_lab_sources.py — moi URL nguon cua Phong Nghien Cuu phai tra 200.

Chay:  python scratchpad/check_lab_sources.py

⚠️⚠️ VI SAO CAN MOT BO RIENG: mot URL da tung dung KHONG co nghia la no con dung.
   Du an da bi hai lan:
     · bang NSSDC Planetary Fact Sheet -> 307 ve www.nasa.gov/nssdc/ (12/08/2026)
     · nasa.gov/audience/foreducators/microgravity/index.html -> **404** (12/08/2026)
   Ca hai deu la nan nhan cua lan doi cau truc site cua NASA. Lan thu hai LOT TOI
   BAN THAT: LAB-02 dan mot URL chet o dong "Nguon", tuc dua tre bam vao mot trang
   khong ton tai — thu te nhat co the xay ra voi mot khu day nguon.
   Nen: KIEM LAI, dinh ky, va truoc moi lan them nguon moi.

⚠️ Doc URL THANG TU `js/lab-catalog.js` — khong go lai danh sach o day, khong thi
   them mot nguon moi la bo kiem khong biet gi (loi "hai noi giu mot su that").
"""
import io
import os
import re
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAT = os.path.join(ROOT, "js", "lab-catalog.js")

# ⚠️ Chi nhan ten mien CUA NASA. Khong noi long thanh "URL bat ky": mot khu day
#    nguon ma dan mot blog la mat ca ly do no ton tai. `spaceplace` la trang NASA
#    viet CHO TRE EM — dung do tuoi cua du an.
OK_HOSTS = ("science.nasa.gov", "spaceplace.nasa.gov", "www.nasa.gov",
            "nasa.gov", "imagine.gsfc.nasa.gov")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126 Safari/537.36")

dat = hong = 0


def check(label, cond, detail=""):
    global dat, hong
    if cond:
        dat += 1
        print("  [OK]   %s%s" % (label, ("  (%s)" % detail) if detail else ""))
    else:
        hong += 1
        print("  [HONG] %s%s" % (label, ("  (%s)" % detail) if detail else ""))


def head(url):
    """Tra ve (ma HTTP, dich chuyen huong). Dung GET chu khong HEAD: mot so may
       chu cua NASA tra 403 cho HEAD nhung 200 cho GET, nen HEAD bao hong oan."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, (r.url if r.url != url else "")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, str(e)[:60]


def main():
    if not os.path.isfile(CAT):
        print("[HONG] khong thay %s" % CAT)
        return 1
    src = io.open(CAT, encoding="utf-8").read()

    # Bo comment truoc khi tim: ghi chu trong file CO NHAC URL da chet
    # (`nasa.gov/audience/foreducators/...`) de giai thich vi sao doi nguon — dem ca
    # chu trong ghi chu cua chinh minh la loi da lap nhieu lan trong du an.
    code = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
    code = re.sub(r"(?m)^\s*//.*$", " ", code)

    keys = re.findall(r"^\s{4}(\w+):\s*\{\s*$", code, re.M)
    urls = re.findall(r'url:\s*"([^"]+)"', code)
    print("Doc tu js/lab-catalog.js: %d nguon\n" % len(urls))
    check("doc duoc it nhat 1 nguon (khong 'dat' mot cach RONG)", len(urls) >= 1,
          "%d nguon" % len(urls))
    if not urls:
        return 1

    for u in urls:
        host = re.sub(r"^https?://([^/]+).*$", r"\1", u)
        check("ten mien cua NASA: %s" % host, host in OK_HOSTS, u[:64])

    print()
    for u in urls:
        st, extra = head(u)
        check("200: %s" % u[:66], st == 200,
              ("HTTP %s%s" % (st, (" -> " + extra) if extra else ""))
              if st != 200 else "")

    # ⚠️ URL da chet KHONG duoc quay lai. Ghim dung nhung cai da bi bat, de ai do
    #    "khoi phuc" mot nguon cu la biet ngay.
    print()
    DEAD = ("nasa.gov/audience/foreducators/microgravity",
            "nssdc.gsfc.nasa.gov/planetary/factsheet",
            "planet_table_ratio.html")
    for d in DEAD:
        # detail chi in khi HONG — "[OK] ... (con dung)" la mot dong doc nguoc nghia.
        check("KHONG dung lai URL da chet: %s" % d, d not in code,
              "" if d not in code else "CON DUNG")

    print("\n" + "-" * 62)
    print("  KET QUA: %d dat / %d hong" % (dat, hong))
    print("-" * 62)
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
