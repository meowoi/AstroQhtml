#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AstroQ · fetch_nasa_news.py
============================
Tự động tải dữ liệu vũ trụ từ NHIỀU endpoint của NASA (mặc định: 1 năm gần
nhất = hôm nay lùi 365 ngày) và lưu thành các file JSON vào từng thư mục con:

    learningdata/astronomy/nasa_articles/
        ├── apod/            (Astronomy Picture of the Day)
        ├── images/          (NASA Image & Video Library — ảnh 4K theo từ khoá)
        ├── mars/            (Mars Rover Photos — ảnh xe tự hành gửi về)
        └── techtransfer/    (Patents / Software / Spinoff mới của NASA)

Mỗi thư mục có thêm `_index.json` tổng hợp. Chỉ dùng thư viện chuẩn của Python.

Ví dụ:
    # Tất cả nguồn:
    python scripts/fetch_nasa_news.py --source all

    # Ảnh 4K theo từ khoá:
    python scripts/fetch_nasa_news.py --source images --query "James Webb" --limit 20
    python scripts/fetch_nasa_news.py --source images --query "Black Hole"

    # Ảnh Sao Hỏa mới nhất trong 1 năm (dừng khi đủ --limit):
    python scripts/fetch_nasa_news.py --source mars --rover perseverance --limit 100

    # Phát minh / công nghệ NASA:
    python scripts/fetch_nasa_news.py --source techtransfer --tt-kind patent --tt-query "robot"

Khuyến nghị đặt API key riêng (free tại https://api.nasa.gov):
    NASA_API_KEY=xxxx python scripts/fetch_nasa_news.py --source all
"""

import argparse
import datetime as _dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

APOD_ENDPOINT = "https://api.nasa.gov/planetary/apod"
IMAGES_SEARCH = "https://images-api.nasa.gov/search"
IMAGES_ASSET = "https://images-api.nasa.gov/asset/"
MARS_ENDPOINT = "https://api.nasa.gov/mars-photos/api/v1"
TECH_ENDPOINT = "https://technology.nasa.gov/api/query"
USER_AGENT = "AstroQ-fetch-nasa-news/2.0 (educational)"
ALL_SOURCES = ["apod", "images", "mars", "techtransfer"]

# In được tiếng Việt trên console Windows (cp1252) mà không lỗi.
for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# --------------------------------------------------------------------------
# Tiện ích chung
# --------------------------------------------------------------------------
def repo_root():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(here)


def default_out_dir():
    return os.path.join(repo_root(), "learningdata", "astronomy", "nasa_articles")


def slugify(text, maxlen=60):
    text = (str(text) if text is not None else "").strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:maxlen] or "item"


def html_strip(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#39;", "'")
    return re.sub(r"\s+", " ", s).strip()


def http_get(url, retries=4, timeout=60, soft_404=False):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404 and soft_404:
                return None
            if e.code == 429:
                wait = (attempt + 1) * 6
                print("  ! Bị giới hạn tần suất (429). Chờ %ds rồi thử lại…" % wait)
                time.sleep(wait)
                continue
            if 500 <= e.code < 600:
                time.sleep((attempt + 1) * 3)
                continue
            try:
                msg = e.read().decode("utf-8", "replace")
            except Exception:
                msg = ""
            raise RuntimeError("HTTP %s khi gọi %s\n%s" % (e.code, url, msg[:300]))
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last = e
            time.sleep((attempt + 1) * 3)
            continue
    raise RuntimeError("Không gọi được API sau %d lần: %s" % (retries, last))


def http_get_json(url, soft_404=False):
    txt = http_get(url, soft_404=soft_404)
    if txt is None:
        return None
    return json.loads(txt)


def date_range(days):
    today = _dt.date.today()
    return (today - _dt.timedelta(days=days)).isoformat(), today.isoformat()


# --------------------------------------------------------------------------
# 1) APOD — Astronomy Picture of the Day
# --------------------------------------------------------------------------
def apod_page_url(date_iso):
    try:
        d = _dt.date.fromisoformat(date_iso)
        return "https://apod.nasa.gov/apod/ap%s.html" % d.strftime("%y%m%d")
    except Exception:
        return "https://apod.nasa.gov/apod/astropix.html"


def collect_apod(api_key, days, reward, limit, images_only):
    start, end = date_range(days)
    q = urllib.parse.urlencode({"api_key": api_key, "start_date": start,
                                "end_date": end, "thumbs": "true"})
    print("→ APOD: %s … %s" % (start, end))
    raw = http_get_json("%s?%s" % (APOD_ENDPOINT, q))
    if isinstance(raw, dict):
        raw = [raw]
    out = []
    for it in raw:
        if not it.get("date"):
            continue
        media = it.get("media_type", "image")
        if images_only and media != "image":
            continue
        out.append({
            "id": "apod-%s" % it["date"],
            "source": "NASA APOD",
            "source_reference": "NASA APOD API (api.nasa.gov)",
            "date": it.get("date", ""),
            "title": (it.get("title") or "").strip(),
            "media_type": media,
            "image_url": it.get("url", ""),
            "hd_image_url": it.get("hdurl", ""),
            "thumbnail_url": it.get("thumbnail_url", "") or (it.get("url", "") if media == "image" else ""),
            "explanation": (it.get("explanation") or "").strip(),
            "copyright": (it.get("copyright") or "").strip(),
            "nasa_url": apod_page_url(it.get("date", "")),
            "api_source_url": APOD_ENDPOINT,
            "reward_purple_meteors": reward,
        })
    return out[:limit] if limit else out


# --------------------------------------------------------------------------
# 2) NASA Image & Video Library — ảnh 4K theo từ khoá
# --------------------------------------------------------------------------
def image_best_url(nasa_id):
    """Trả URL ảnh gốc/lớn nhất (~orig ≈ 4K) cho một nasa_id."""
    try:
        data = http_get_json(IMAGES_ASSET + urllib.parse.quote(nasa_id))
        items = (data.get("collection") or {}).get("items") or []
        hrefs = [it.get("href", "") for it in items
                 if it.get("href", "").lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))]
        for key in ("~orig", "~large", "~medium", "~small", "~thumb"):
            for h in hrefs:
                if key in h.lower():
                    return h
        return hrefs[0] if hrefs else ""
    except Exception:
        return ""


def collect_images(query, days, reward, limit, hi_res):
    start, end = date_range(days)
    y0, y1 = start[:4], end[:4]
    print("→ Image Library: '%s' (%s–%s), 4K=%s" % (query, y0, y1, hi_res))
    out, page = [], 1
    cap = limit if limit else 40
    while len(out) < cap and page <= 20:
        q = urllib.parse.urlencode({"q": query, "media_type": "image",
                                    "year_start": y0, "year_end": y1, "page": page})
        data = http_get_json("%s?%s" % (IMAGES_SEARCH, q))
        items = (data.get("collection") or {}).get("items") or []
        if not items:
            break
        for it in items:
            d0 = (it.get("data") or [{}])[0]
            if not d0.get("title"):
                continue
            nasa_id = d0.get("nasa_id") or slugify(d0.get("title"))
            links = it.get("links") or []
            preview = next((lk.get("href", "") for lk in links
                            if lk.get("render") == "image" or lk.get("rel") == "preview"), "")
            best = image_best_url(nasa_id) if hi_res else ""
            if hi_res:
                time.sleep(0.25)
            out.append({
                "id": "nasa-img-%s" % slugify(nasa_id, 50),
                "source": "NASA Image and Video Library",
                "source_reference": "NASA Images API (images-api.nasa.gov)",
                "date": (d0.get("date_created") or "")[:10],
                "title": (d0.get("title") or "").strip(),
                "media_type": "image",
                "image_url": best or preview,
                "hd_image_url": best,
                "thumbnail_url": preview,
                "explanation": (d0.get("description") or "").strip(),
                "copyright": (d0.get("secondary_creator") or d0.get("photographer") or "").strip(),
                "nasa_url": "https://images.nasa.gov/details/%s" % nasa_id,
                "api_source_url": IMAGES_SEARCH,
                "reward_purple_meteors": reward,
                "extra": {"nasa_id": nasa_id, "keywords": d0.get("keywords", [])},
            })
            if limit and len(out) >= limit:
                break
        page += 1
        time.sleep(0.4)
    return out[:limit] if limit else out


# --------------------------------------------------------------------------
# 3) Mars Rover Photos — ảnh xe tự hành gửi về (1 năm gần nhất)
# --------------------------------------------------------------------------
def _mars_norm(p, rover, reward):
    cam = p.get("camera") or {}
    rv = (p.get("rover") or {}).get("name", rover)
    cam_name = cam.get("full_name") or cam.get("name", "")
    return {
        "id": "mars-%s-%s" % (rover.lower(), p.get("id")),
        "source": "NASA Mars Rover Photos",
        "source_reference": "NASA Mars Rover Photos API (api.nasa.gov/mars-photos)",
        "date": p.get("earth_date", ""),
        "title": "%s · Sol %s · %s" % (rv, p.get("sol"), cam_name),
        "media_type": "image",
        "image_url": p.get("img_src", ""),
        "hd_image_url": p.get("img_src", ""),
        "thumbnail_url": p.get("img_src", ""),
        "explanation": "Ảnh do xe tự hành %s chụp bằng camera %s (Sol %s · %s)." % (
            rv, cam_name, p.get("sol"), p.get("earth_date", "")),
        "copyright": "NASA/JPL-Caltech",
        "nasa_url": p.get("img_src", ""),
        "api_source_url": MARS_ENDPOINT,
        "reward_purple_meteors": reward,
        "extra": {"rover": rv, "sol": p.get("sol"),
                  "camera": cam.get("name"), "camera_full": cam.get("full_name")},
    }


def collect_mars(api_key, rover, days, reward, limit):
    cap = limit if limit else 250          # chặn an toàn khi không đặt --limit
    print("→ Mars Rover Photos: %s (tối đa %d ảnh mới nhất, trong ~%d ngày)" % (rover, cap, days))
    out = []

    # (1) Ảnh mới nhất — endpoint latest_photos
    latest = http_get_json("%s/rovers/%s/latest_photos?api_key=%s" % (MARS_ENDPOINT, rover, api_key), soft_404=True)
    if latest and latest.get("latest_photos"):
        for p in latest["latest_photos"]:
            out.append(_mars_norm(p, rover, reward))
            if len(out) >= cap:
                return out

    # (2) Đi lùi theo earth_date để lấy thêm trong 1 năm
    today = _dt.date.today()
    for i in range(days + 1):
        if len(out) >= cap:
            break
        d = (today - _dt.timedelta(days=i)).isoformat()
        page = 1
        while len(out) < cap:
            q = urllib.parse.urlencode({"api_key": api_key, "earth_date": d, "page": page})
            data = http_get_json("%s/rovers/%s/photos?%s" % (MARS_ENDPOINT, rover, q), soft_404=True)
            if data is None:                 # 404 = endpoint tạm không khả dụng
                if not out and i == 0:
                    print("  ! Mars Photos API đang trả 404 (endpoint tạm không khả dụng) — bỏ qua Mars.")
                    return out
                break
            photos = data.get("photos") or []
            if not photos:
                break
            for p in photos:
                out.append(_mars_norm(p, rover, reward))
                if len(out) >= cap:
                    break
            page += 1
            time.sleep(0.3)
    return out


# --------------------------------------------------------------------------
# 4) NASA TechTransfer — patents / software / spinoff
# --------------------------------------------------------------------------
def collect_techtransfer(api_key, kind, query, reward, limit):
    term = query or "space"                  # API cần một từ khoá; mặc định 'space'
    url = "%s/%s/%s" % (TECH_ENDPOINT, kind, urllib.parse.quote(term))
    print("→ TechTransfer: %s '%s'" % (kind, term))
    data = http_get_json(url) or {}
    rows = data.get("results") or []
    out = []
    for row in rows:
        if not isinstance(row, list):
            continue
        g = lambda i: (row[i] if i < len(row) else "") or ""
        case = g(1)
        title = html_strip(g(2))
        if not title:
            continue
        out.append({
            "id": "nasa-tt-%s-%s" % (kind, slugify(case or g(0) or title, 40)),
            "source": "NASA TechTransfer (%s)" % kind,
            "source_reference": "NASA TechTransfer API (technology.nasa.gov/api/query)",
            "date": "",
            "title": title,
            "media_type": kind,
            "image_url": "",
            "hd_image_url": "",
            "thumbnail_url": "",
            "explanation": html_strip(g(3)),
            "copyright": "NASA",
            "nasa_url": ("https://technology.nasa.gov/patent/%s" % case) if case else "https://technology.nasa.gov/",
            "api_source_url": TECH_ENDPOINT,
            "reward_purple_meteors": reward,
            "extra": {"case": case, "category": g(4), "center": g(9) or g(6)},
        })
    return out[:limit] if limit else out


# --------------------------------------------------------------------------
# Lưu file + chỉ mục
# --------------------------------------------------------------------------
def save_article(article, out_dir, overwrite):
    base = slugify(article["id"], 60)
    if article.get("title"):
        base = base + "-" + slugify(article["title"], 30)
    path = os.path.join(out_dir, base[:90] + ".json")
    if os.path.exists(path) and not overwrite:
        return False
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return True


def dedupe_sort_limit(articles, limit):
    seen, uniq = set(), []
    for a in sorted(articles, key=lambda x: x.get("date", ""), reverse=True):
        if a["id"] in seen:
            continue
        seen.add(a["id"])
        uniq.append(a)
    return uniq[:limit] if limit else uniq


def write_index(articles, out_dir, meta):
    index = {
        "meta": meta,
        "count": len(articles),
        "articles": [{
            "id": a["id"], "date": a["date"], "title": a["title"],
            "source": a["source"], "media_type": a["media_type"],
            "image_url": a.get("image_url", ""), "nasa_url": a["nasa_url"],
            "reward_purple_meteors": a["reward_purple_meteors"],
        } for a in articles],
    }
    path = os.path.join(out_dir, "_index.json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Tải dữ liệu NASA (nhiều endpoint) -> JSON.")
    ap.add_argument("--source", choices=ALL_SOURCES + ["all"], default="apod")
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--query", default="James Webb", help="Từ khoá cho --source images")
    ap.add_argument("--rover", default="perseverance",
                    choices=["perseverance", "curiosity", "opportunity", "spirit"])
    ap.add_argument("--tt-kind", default="patent",
                    choices=["patent", "patent_issued", "software", "spinoff"])
    ap.add_argument("--tt-query", default="", help="Từ khoá TechTransfer (rỗng = tất cả)")
    ap.add_argument("--api-key", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--limit", type=int, default=0, help="0 = không giới hạn (Mars mặc định 250)")
    ap.add_argument("--reward", type=int, default=6)
    ap.add_argument("--images-only", action="store_true", help="Chỉ ảnh (apod)")
    ap.add_argument("--overwrite", action="store_true")
    try:
        ap.add_argument("--hi-res", action=argparse.BooleanOptionalAction, default=True,
                        help="Tải ảnh gốc ~4K từ Image Library (mặc định bật)")
    except AttributeError:                      # Python < 3.9
        ap.add_argument("--no-hi-res", dest="hi_res", action="store_false", default=True)
    args = ap.parse_args(argv)

    api_key = args.api_key or os.environ.get("NASA_API_KEY") or "DEMO_KEY"
    out_base = args.out or default_out_dir()
    sources = ALL_SOURCES if args.source == "all" else [args.source]
    start, end = date_range(args.days)

    print("== AstroQ · Tải dữ liệu NASA ==")
    print("Khoảng thời gian: %s → %s (%d ngày) | Nguồn: %s" % (start, end, args.days, ", ".join(sources)))
    print("Lưu vào: %s" % out_base)
    if api_key == "DEMO_KEY":
        print("(DEMO_KEY — giới hạn ~30 lần/giờ, 50 lần/ngày. Đặt NASA_API_KEY để mở rộng.)")

    total = 0
    for src in sources:
        out_dir = os.path.join(out_base, src)
        os.makedirs(out_dir, exist_ok=True)
        try:
            if src == "apod":
                arts = collect_apod(api_key, args.days, args.reward, args.limit, args.images_only)
            elif src == "images":
                arts = collect_images(args.query, args.days, args.reward, args.limit, args.hi_res)
            elif src == "mars":
                arts = collect_mars(api_key, args.rover, args.days, args.reward, args.limit)
            elif src == "techtransfer":
                arts = collect_techtransfer(api_key, args.tt_kind, args.tt_query, args.reward, args.limit)
            else:
                arts = []
        except RuntimeError as e:
            print("  LỖI [%s]: %s" % (src, e), file=sys.stderr)
            continue

        arts = dedupe_sort_limit(arts, args.limit)
        saved = sum(1 for a in arts if save_article(a, out_dir, args.overwrite))
        write_index(arts, out_dir, {
            "source": src, "date_start": start, "date_end": end, "days": args.days,
            "reward": args.reward, "used_demo_key": api_key == "DEMO_KEY",
            "query": args.query if src == "images" else None,
            "rover": args.rover if src == "mars" else None,
            "tt_kind": args.tt_kind if src == "techtransfer" else None,
        })
        total += len(arts)
        print("  ✓ %-12s %3d bài (lưu mới %d) → %s/" % (src, len(arts), saved, src))

    print("Tổng cộng: %d bài." % total)
    return 0 if total else 2


if __name__ == "__main__":
    raise SystemExit(main())
