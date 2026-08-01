/* ============================================================
   js/pick-place.js — KHUÔN "THẺ → Ô": kéo-thả bằng chuột **và** chơi
   được bằng bàn phím. Nền của khuôn `profile_builder`.

   Nạp như script thường, trước script chính của trang:
     <script src="js/pick-place.js"></script>
   Kèm `css/pick-place.css`.

   ⚠️ VÌ SAO CÓ FILE NÀY (31/07/2026 — bước 3 của `docs/decisions/002`)
   ─────────────────────────────────────────────────────────────
   `mission-earth.html` đã có một hàm `dragDrop()` dùng chung cho ba
   bước (năng lượng sạch · Eco-Hero · lõi hành tinh) — hình dạng đúng,
   nhưng **chỉ nghe sự kiện con trỏ**. Trẻ dùng bàn phím focus được vào
   thẻ (thẻ là `<button>`) rồi bấm Enter thì **không có gì xảy ra**:
   bước đó không thể hoàn thành, tức là không chơi được nhiệm vụ.

   Rà 31/07/2026: cả `mission-earth.html` chỉ có ĐÚNG MỘT handler
   `keydown`, và nó dùng để mở khoá âm thanh. Không có hạ tầng bàn phím
   nào để dựa vào — nên hạ tầng đó nằm ở đây, làm một lần, cho cả 5 khuôn.

   ───────────────────── HAI ĐƯỜNG, MỘT LUẬT ─────────────────────
   Chuột  : nhấc thẻ → rê → thả lên ô.
   Bàn phím: Enter/Space trên thẻ = **cầm lên** → Tab hoặc ← → ↑ ↓ đi
             giữa các ô → Enter/Space = **đặt xuống** → Esc = bỏ xuống.

   Cả hai đi qua CÙNG một hàm `resolve(thẻ, ô)`, nên không thể có
   chuyện chuột tính điểm một kiểu còn bàn phím một kiểu.

   ⚠️ KHÔNG dùng sự kiện `click` cho đường bàn phím, dù thẻ là `<button>`
      và Enter/Space vốn tự sinh `click`. Lý do: đường chuột gọi
      `preventDefault()` trong `pointerdown` (bắt buộc, không thì rê thẻ
      thành bôi đen chữ), mà việc đó **chặn luôn `click` ở phần lớn
      trình duyệt**. Nghe `keydown` thẳng thì hai đường không giẫm chân nhau.

   ⚠️ Thả ra CHỖ TRỐNG thì IM LẶNG — giữ nguyên luật cũ. Nhấc thẻ lên rồi
      đổi ý bỏ xuống là chuyện bình thường; báo "chưa đúng rồi" lúc đó là
      mắng oan. Chỉ thả TRÚNG một ô mới tính đúng/sai.

   ───────────────────── CÁCH DÙNG ─────────────────────
     AstroQPickPlace.wire({
       items : [...],          // <button data-want="khoá-ô">
       zones : [...],          // <div data-zone="khoá-ô">
       wide  : true,           // thẻ rộng (chép cả innerHTML lúc bay)
       canDrop(z) {...},       // mặc định: ô chưa có class `ok`
       onHit(el, z) {...},
       onMiss(el, z) {...},
       sfx   : sfx,            // (tên, tần số) — không truyền thì im
       labels: { hold, place, wrong, drop }            // song ngữ, xem dưới
     });

   Nhãn đọc cho trẻ dùng bàn phím / trình đọc màn hình:
     hold   `{item}` thẻ vừa cầm · `{n}` số ô đang nhận được
     place  `{item}` `{zone}` — đặt ĐÚNG
     wrong  `{item}` `{zone}` — đặt SAI
     drop   bỏ thẻ xuống (Esc, hoặc bấm Enter lại trên chính thẻ đó)
   Nhãn của thẻ/ô lấy từ `data-label`, không có thì lấy chữ bên trong
   (`.tx`/`.lb` nếu có). Trang PHẢI khai đủ cả `vi` và `en`.
   ============================================================ */
(function (global) {
  "use strict";

  /* Một vùng đọc duy nhất cho cả trang. `aria-live="polite"` chứ không phải
     `assertive`: lời báo đặt thẻ không được cắt ngang lời Comet đang nói. */
  var live = null;
  function announce(msg) {
    if (!msg) return;
    if (!live) {
      live = document.createElement("div");
      live.className = "aq-live";
      live.setAttribute("aria-live", "polite");
      live.setAttribute("aria-atomic", "true");
      document.body.appendChild(live);
    }
    /* Đặt rỗng trước rồi mới gán: hai lời báo GIỐNG NHAU liên tiếp (thả sai
       hai lần vào cùng một ô) thì trình đọc coi là không đổi và im luôn. */
    live.textContent = "";
    global.setTimeout(function () { live.textContent = msg; }, 30);
  }

  function labelOf(el) {
    if (!el) return "";
    var d = el.getAttribute("data-label");
    if (d) return d;
    var tx = el.querySelector(".tx") || el.querySelector(".lb");
    return ((tx || el).textContent || "").replace(/\s+/g, " ").trim();
  }

  /** Thay `{khoá}` trong mẫu câu. Dùng map chứ không dùng thứ tự tham số —
      tiếng Việt và tiếng Anh không luôn xếp "thẻ" trước "ô" trong câu. */
  function fill(tpl, map) {
    return String(tpl || "").replace(/\{(\w+)\}/g, function (m, k) {
      return map[k] != null ? String(map[k]) : m;
    });
  }

  function wire(opt) {
    var items   = opt.items || [];
    var zones   = opt.zones || [];
    var wide    = !!opt.wide;
    var L       = opt.labels || {};
    var sfx     = opt.sfx || function () {};
    var canDrop = opt.canDrop || function (z) { return !z.classList.contains("ok"); };

    var fly = null, dragEl = null;   // đường CHUỘT
    var held = null;                 // đường BÀN PHÍM

    function keyOf(z)  { return z.getAttribute("data-zone"); }
    function wantOf(e) { return e.getAttribute("data-want"); }
    function usable(el) { return !el.classList.contains("used"); }
    function openZones() { return zones.filter(canDrop); }

    /** Luật chung của CẢ HAI đường. `z` rỗng = thả ra chỗ trống → im lặng. */
    function resolve(el, z) {
      if (!z) return;
      if (keyOf(z) === wantOf(el) && canDrop(z)) {
        sfx("beep", 920);
        opt.onHit(el, z);
        announce(fill(L.place, { item: labelOf(el), zone: labelOf(z) }));
      } else {
        sfx("nope");
        opt.onMiss(el, z);
        announce(fill(L.wrong, { item: labelOf(el), zone: labelOf(z) }));
      }
    }

    /* ═══════════════ Đường CHUỘT ═══════════════ */
    function zoneUnder(x, y) {
      return zones.find(function (z) {
        var r = z.getBoundingClientRect();
        return x >= r.left && x <= r.right && y >= r.top && y <= r.bottom;
      }) || null;
    }
    function paintOver(z) {
      zones.forEach(function (x) { x.classList.toggle("over", x === z && canDrop(x)); });
    }
    function move(e) {
      if (!fly) return;
      fly.style.left = e.clientX + "px";
      fly.style.top  = e.clientY + "px";
      paintOver(zoneUnder(e.clientX, e.clientY));
    }
    function drop(e) {
      if (!fly || !dragEl) return;
      var z = zoneUnder(e.clientX, e.clientY);
      fly.remove(); fly = null;
      paintOver(null);
      dragEl.classList.remove("dragging");
      var el = dragEl; dragEl = null;
      resolve(el, z);
    }

    /* ═══════════════ Đường BÀN PHÍM ═══════════════ */
    function markTargets(on) {
      zones.forEach(function (z) {
        var ok = on && canDrop(z);
        z.classList.toggle("aq-target", !!ok);
        if (ok) z.setAttribute("tabindex", "0");
        else z.removeAttribute("tabindex");
      });
    }
    function release(refocus) {
      if (!held) return;
      var el = held; held = null;
      el.classList.remove("aq-holding");
      el.setAttribute("aria-pressed", "false");
      markTargets(false);
      if (refocus) el.focus();
    }
    function hold(el) {
      if (held === el) { release(true); announce(L.drop); return; }
      release(false);
      var open = openZones();
      if (!open.length) return;
      held = el;
      el.classList.add("aq-holding");
      el.setAttribute("aria-pressed", "true");
      markTargets(true);
      sfx("beep", 640);
      announce(fill(L.hold, { item: labelOf(el), n: open.length }));
      open[0].focus();
    }
    /** ← → ↑ ↓ đi giữa các ô còn nhận được (vòng lại đầu/cuối). */
    function stepFocus(from, dir) {
      var open = openZones();
      if (!open.length) return;
      var i = open.indexOf(from);
      open[(i < 0 ? 0 : i + dir + open.length) % open.length].focus();
    }

    items.forEach(function (el) {
      el.setAttribute("aria-pressed", "false");
      el.addEventListener("pointerdown", function (e) {
        if (!usable(el)) return;
        e.preventDefault();
        release(false);                 // đang cầm bằng bàn phím thì bỏ xuống đã
        dragEl = el;
        el.classList.add("dragging");
        fly = document.createElement("span");
        fly.className = "me-fly" + (wide ? " wide" : "");
        if (wide) fly.innerHTML = el.innerHTML; else fly.textContent = el.textContent;
        document.body.appendChild(fly);
        move(e);
        /* Bắt con trỏ vào chính thẻ: không có dòng này thì ngón tay/chuột đi ra
           khỏi thẻ là mất luôn `pointermove` và thẻ đứng chết giữa đường. */
        el.setPointerCapture(e.pointerId);
      });
      el.addEventListener("pointermove", move);
      el.addEventListener("pointerup", drop);
      el.addEventListener("pointercancel", drop);

      el.addEventListener("keydown", function (e) {
        if (!usable(el)) return;
        if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
          e.preventDefault();
          hold(el);
        }
      });
    });

    zones.forEach(function (z) {
      z.addEventListener("keydown", function (e) {
        if (!held) return;
        if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
          e.preventDefault();
          var el = held;
          release(false);
          resolve(el, z);
          /* Sau khi đặt xong, focus về khay thẻ để trẻ đi tiếp — KHÔNG để focus
             chết trên một ô vừa mất `tabindex` (trình duyệt sẽ ném focus về
             <body> và người dùng bàn phím mất chỗ đứng). */
          var next = items.filter(usable)[0];
          if (next) next.focus(); else z.blur();
          return;
        }
        if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); stepFocus(z, +1); }
        if (e.key === "ArrowLeft"  || e.key === "ArrowUp")   { e.preventDefault(); stepFocus(z, -1); }
        if (e.key === "Escape") { e.preventDefault(); release(true); announce(L.drop); }
      });
    });
  }

  global.AstroQPickPlace = { wire: wire, announce: announce, labelOf: labelOf };
})(window);
