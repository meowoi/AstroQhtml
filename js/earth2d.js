/* ============================================================
   earth2d.js — CẢNH TRÁI ĐẤT BẢN 2D cho NHIỆM VỤ 01 "HÀNH TINH XANH".

   THAY `js/earth3d.js` + three.js. Đo được: three.module.js 1.243 KB raw /
   **250 KB gzip** + OrbitControls 29/6 KB, nạp từ **unpkg.com** — nhiều hơn cả SDK
   Firebase (233 KB) mà dự án cố ý từ chối ở trang cần mượt, cộng thêm một chặng
   DNS+TCP+TLS tới tên miền lạ (dự án đã tự host font để cắt đúng hai chặng như vậy).
   Bản 2D: 0 KB thư viện, ảnh đường tải đầu **50 KB** (`img/earth/globe-640.avif`).

   ⚠️ GIỮ NGUYÊN HỢP ĐỒNG `world.*` CỦA BẢN 3D. `mission-earth.html` gọi 22 hàm ở
      ~50 chỗ; đổi tên hay đổi ngữ nghĩa một hàm là phải sửa cả 8 bước nhiệm vụ và
      viết lại bộ smoke 141 phép kiểm. Cài lại đúng hợp đồng thì trang gần như không
      phải sửa. `panTo()` CHƯA BAO GIỜ được gọi với lat/lon (chỉ `dist` + `ms`) —
      đó là lý do bản 2D làm được việc này gọn.

   ⚠️ HAI HỆ TOẠ ĐỘ, ĐỪNG TRỘN:
      · `setMap('flat')` — bản đồ PHẲNG (equirectangular). lat/lon quy ra phần trăm
        bằng một phép chia, **chính xác tuyệt đối**. BẮT BUỘC cho bước `life`, nơi 4
        thẻ mẫu vật khẳng định vị trí thật (Amazon, Himalaya, Nam Cực, Đại Tây Dương).
      · `setMap('globe')` — ảnh CHỤP quả cầu, tâm Bắc Mỹ. Ở đây lat/lon được chiếu
        **TƯƠNG ĐỐI so với điểm đang nhìn**, KHÔNG phải toạ độ địa lý tuyệt đối.
        Ảnh đó không thấy Amazon/Himalaya/Nam Cực (chúng ở nửa bên kia), nên đặt
        điểm theo lat/lon tuyệt đối lên nó là **DẠY SAI ĐỊA LÝ** — đúng lỗi bản 3D
        đã mắc khi sinh lục địa bằng nhiễu fBm rồi neo thẻ "Rừng Amazon" vào giữa
        đại dương. Bước `scan` cố ý đặt điểm quanh chỗ đang nhìn (`facingLatLon()`
        + dlat/dlon) nên nó đúng ở chế độ này.

   ⚠️ DẤU HIỆU PHẢI CHỐNG-PHÓNG `scale(1/zoom)`. Marker nằm TRONG lớp bị biến hình
      (phải vậy, không thì kéo xong trẻ chạm "Amazon" nhưng dưới ngón tay đã là đại
      dương), nhưng nếu để nó phóng theo thì ở zoom 3× vòng ngắm trùm kín nửa hành
      tinh.

   ⚠️ KÉO XONG KHÔNG ĐƯỢC TÍNH LÀ MỘT CÚ BẤM. Ngưỡng `DRAG_SLOP` 6px — thiếu nó thì
      bước tự hoàn thành khi trẻ chỉ đang kéo ảnh.

     <script src="js/earth2d.js"></script>
     const world = AstroQEarth2D.create(document.getElementById('stage'));
   ============================================================ */
(function (global) {
  "use strict";

  /* Ảnh: AVIF trước, WebP sau. Không có nhánh JPG — mọi trình duyệt hỗ trợ AVIF
     hoặc WebP đều nằm trong tầm hỗ trợ của app; thêm nhánh thứ ba là thêm asset
     không ai tải. */
  var MAPS = {
    globe: { avif: "img/earth/globe-640.avif", webp: "img/earth/globe-640.webp",
             w: 640, h: 640, flat: false },
    flat:  { avif: "img/earth/flat-2048.avif", webp: "img/earth/flat-2048.webp",
             w: 2048, h: 1024, flat: true }
  };

  var DRAG_SLOP = 6;          // px — dưới ngưỡng này thì coi là một cú BẤM
  var DEG_PER_PX = 0.42;      // kéo 1px đổi bao nhiêu độ kinh tuyến
  var SPIN_DEG_S = 3.2;       // hành tinh tự quay (độ/giây) khi setSpin(1)
  var LAT_LIMIT = 62;         // chặn kéo lên/xuống quá mức (ảnh hết đất để nhìn)

  function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
  function reduced() {
    try {
      return global.matchMedia &&
             global.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) { return false; }
  }

  /** Chuẩn hoá kinh tuyến về [-180, 180) — kéo nhiều vòng vẫn phải ra số dùng được. */
  function wrapLon(d) {
    d = ((d + 180) % 360 + 360) % 360 - 180;
    return d;
  }

  /**
   * Khoảng cách GÓC giữa hai điểm trên cầu, theo độ.
   * ⚠️ KHÔNG lấy `|lon1-lon2|`: ở vĩ độ cao hai kinh tuyến cách nhau 30° thì khoảng
   *    cách thật nhỏ hơn nhiều, và bước `rotation` sẽ xong quá sớm hoặc không bao
   *    giờ xong. Dùng công thức haversine trên đơn vị cầu.
   */
  function angleBetween(lat1, lon1, lat2, lon2) {
    var r = Math.PI / 180;
    var dLat = (lat2 - lat1) * r, dLon = wrapLon(lon2 - lon1) * r;
    var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.cos(lat1 * r) * Math.cos(lat2 * r) *
            Math.sin(dLon / 2) * Math.sin(dLon / 2);
    return 2 * Math.asin(Math.min(1, Math.sqrt(a))) / r;
  }

  function el(tag, cls, parent) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (parent) parent.appendChild(e);
    return e;
  }

  /** Chạy một tween theo `ms`. `prefers-reduced-motion` → nhảy thẳng tới đích. */
  function tween(ms, step, done) {
    return new Promise(function (resolve) {
      if (reduced()) ms = 0;
      if (!ms) { step(1); if (done) done(); resolve(); return; }
      var t0 = 0;
      function frame(ts) {
        if (!t0) t0 = ts;
        var k = clamp((ts - t0) / ms, 0, 1);
        // ease-out-cubic — cùng cảm giác với tween của bản 3D
        step(1 - Math.pow(1 - k, 3));
        if (k < 1) requestAnimationFrame(frame);
        else { if (done) done(); resolve(); }
      }
      requestAnimationFrame(frame);
    });
  }

  function create(stage, opts) {
    opts = opts || {};
    if (!stage) throw new Error("earth2d: thiếu phần tử sân khấu");

    /* ---------------- Dựng lớp ----------------
       Thứ tự trong DOM = thứ tự vẽ: ảnh → lưới → marker → drone → khiên.
       Mặt Trời và vệ tinh nằm NGOÀI lớp biến hình: chúng không thuộc bề mặt hành
       tinh nên không được pan/zoom theo nó. */
    stage.classList.add("e2");
    stage.innerHTML = "";

    var view = el("div", "e2-view", stage);          // khung cắt
    var layer = el("div", "e2-layer", view);         // lớp BỊ biến hình
    var pic = el("picture", "", layer);
    var srcA = el("source", "", pic);
    srcA.type = "image/avif";
    var srcW = el("source", "", pic);
    srcW.type = "image/webp";
    var img = el("img", "e2-img", pic);
    img.alt = "";
    img.decoding = "async";
    img.setAttribute("aria-hidden", "true");

    var grid = el("div", "e2-grid", layer);
    var markerBox = el("div", "e2-markers", layer);
    var drone = el("div", "e2-drone", layer);
    var beam = el("div", "e2-beam", drone);
    /* VÒNG NGẮM = chỗ mà `facing` rơi vào trên màn hình.
       ⚠️ ĐẶT TRONG `layer` VÀ CHIẾU BẰNG ĐÚNG `project()` CỦA MARKER — không gán
          `left:50%` cho xong. Đo được trên bản đồ phẳng: điểm ở `facing` rơi vào
          **(62,5%, 50%)** của khung, KHÔNG phải tâm; và con số đó đổi theo `zoom`.
          Gán cứng một vị trí là vẽ vòng ngắm lệch khỏi chính cái đích nó chỉ, tức
          trẻ kéo trạm vào vòng mà thanh tín hiệu không lên — lỗi im lặng, và là
          loại lỗi đã làm bước `rotation` bản 3D KHÔNG THỂ hoàn thành.
       Bước `rotation` thắng khi `stationAngleTo(...) < 20°`, tức khi trạm về gần
       `facing` — nên vòng này là đích nhìn thấy được của đúng điều kiện đó. */
    var aim = el("div", "e2-aim", layer);
    aim.hidden = true;

    var sun = el("button", "e2-sun", view);
    sun.type = "button";
    sun.setAttribute("aria-label", "Mặt Trời");
    var sat = el("div", "e2-sat", view);
    var shieldEl = el("div", "e2-shield", view);

    /* ---------------- Trạng thái ---------------- */
    var map = "globe";
    var facing = { lat: 0, lon: -95 };   // ảnh quả cầu tâm ~Bắc Mỹ
    var zoom = 1;
    var spinScale = 0;
    var sunLit = 1;
    var dragRotate = true, dragZoom = true, earthDrag = false;
    var markers = [];                    // {id, lat, lon, done, node}
    var pickCbs = [];
    var running = false, raf = 0, last = 0;
    var shieldK = 0;                     // 0 → 1 khi màng khí quyển bọc dần

    setMap("globe");

    /* ---------------- Ảnh + vẽ lại ---------------- */
    function setMap(kind) {
      var m = MAPS[kind] || MAPS.globe;
      map = MAPS[kind] ? kind : "globe";
      srcA.srcset = m.avif;
      srcW.srcset = m.webp;
      img.src = m.webp;                  // nhánh cuối, trình duyệt tự chọn source
      img.width = m.w; img.height = m.h; // khai cỡ để chặn CLS
      stage.classList.toggle("e2-flat", !!m.flat);
      paint();
    }

    /**
     * lat/lon → phần trăm trên ảnh.
     * · bản đồ phẳng: một phép chia, đúng tuyệt đối.
     * · ảnh quả cầu: chiếu chính hình (orthographic) quanh ĐIỂM ĐANG NHÌN. Điểm ở
     *   nửa bên kia trả `visible:false` — gọi chỗ dùng phải ẩn nó, không được vẽ
     *   một dấu hiệu lên chỗ hành tinh đang che.
     */
    function project(lat, lon) {
      var m = MAPS[map];
      if (m.flat) {
        return { x: (wrapLon(lon) + 180) / 360 * 100,
                 y: (90 - lat) / 180 * 100, visible: true };
      }
      var r = Math.PI / 180;
      var dLon = wrapLon(lon - facing.lon) * r;
      var la = lat * r, la0 = facing.lat * r;
      var cosc = Math.sin(la0) * Math.sin(la) +
                 Math.cos(la0) * Math.cos(la) * Math.cos(dLon);
      // Bán kính đĩa hành tinh trên ảnh ~46% chiều rộng (đo trên ảnh NASA thật)
      var k = 46;
      return {
        x: 50 + k * Math.cos(la) * Math.sin(dLon),
        y: 50 - k * (Math.cos(la0) * Math.sin(la) -
                     Math.sin(la0) * Math.cos(la) * Math.cos(dLon)),
        visible: cosc > 0.12
      };
    }

    function paint() {
      var m = MAPS[map];
      // Ảnh quả cầu: "xoay" = dịch ảnh theo kinh/vĩ tuyến. Bản đồ phẳng: dịch thật.
      var px = m.flat ? -wrapLon(facing.lon) / 360 * 100 : 0;
      var py = m.flat ? (facing.lat) / 180 * 100 : 0;
      layer.style.transform =
        "translate(" + px.toFixed(3) + "%," + py.toFixed(3) + "%) scale(" + zoom.toFixed(3) + ")";
      stage.classList.toggle("e2-night", !sunLit);

      for (var i = 0; i < markers.length; i++) {
        var mk = markers[i], p = project(mk.lat, mk.lon);
        mk.node.style.left = p.x + "%";
        mk.node.style.top = p.y + "%";
        mk.node.hidden = !p.visible;
        /* CHỐNG-PHÓNG: dấu hiệu giữ nguyên cỡ trên màn hình dù ảnh phóng bao nhiêu. */
        mk.node.style.transform =
          "translate(-50%,-50%) scale(" + (1 / zoom).toFixed(3) + ")";
      }

      /* Vòng ngắm: chiếu CHÍNH `facing` bằng cùng một hàm `project()` — nên nó luôn
         nằm đúng chỗ mà điều kiện `stationAngleTo(...) = 0` quy về, ở mọi zoom. */
      if (!aim.hidden) {
        var ap = project(facing.lat, facing.lon);
        aim.style.left = ap.x + "%";
        aim.style.top = ap.y + "%";
        aim.style.transform =
          "translate(-50%,-50%) scale(" + (1 / zoom).toFixed(3) + ")";
      }
    }

    /* ---------------- Vòng vẽ ---------------- */
    function frame(ts) {
      if (!running) return;
      if (!last) last = ts;
      var dt = Math.min(0.05, (ts - last) / 1000);
      last = ts;
      if (spinScale && !reduced()) {
        facing.lon = wrapLon(facing.lon + SPIN_DEG_S * spinScale * dt);
        paint();
      }
      raf = requestAnimationFrame(frame);
    }

    /* ---------------- Kéo / phóng ---------------- */
    var down = null;
    /* ⚠️ KHÔNG `setPointerCapture` NGAY Ở `pointerdown` — đó là lỗi làm cả cảnh 2D
       KHÔNG CHƠI ĐƯỢC, và nó im lặng tuyệt đối.
       Bắt con trỏ lên `.e2-view` khiến MỌI sự kiện con trỏ sau đó bị chuyển hướng
       về chính `view`, nên `click` KHÔNG BAO GIỜ tới được `.e2-mk` hay `.e2-sun`
       nằm bên trong. Hậu quả: chạm điểm tín hiệu không ăn, chạm Mặt Trời không ăn
       → nhiệm vụ tắc ở bước 1.
       Nham hiểm ở chỗ `document.elementFromPoint()` vẫn trả về đúng cái nút (việc
       dò trúng đích vẫn đúng, chỉ có việc GIAO sự kiện là hỏng), nên soi bằng
       elementFromPoint sẽ kết luận "nút bấm được" — đo được đúng như vậy.
       Cách đúng: chỉ bắt con trỏ KHI ĐÃ THẬT SỰ KÉO (vượt DRAG_SLOP). Lúc đó
       trình duyệt cũng đã tự huỷ `click`, nên không mất gì; còn cú chạm không kéo
       thì đi thẳng tới nút như thường. */
    view.addEventListener("pointerdown", function (e) {
      if (!dragRotate && !earthDrag) return;
      down = { x: e.clientX, y: e.clientY, lon: facing.lon, lat: facing.lat,
               moved: 0, id: e.pointerId, captured: false };
    });
    view.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - down.x, dy = e.clientY - down.y;
      down.moved = Math.max(down.moved, Math.abs(dx) + Math.abs(dy));
      // Vượt ngưỡng kéo mới bắt con trỏ, để còn kéo tiếp được ra ngoài khung.
      if (!down.captured && down.moved > DRAG_SLOP) {
        down.captured = true;
        if (view.setPointerCapture) { try { view.setPointerCapture(down.id); } catch (err) {} }
      }
      facing.lon = wrapLon(down.lon - dx * DEG_PER_PX / zoom);
      facing.lat = clamp(down.lat + dy * DEG_PER_PX / zoom, -LAT_LIMIT, LAT_LIMIT);
      paint();
    });
    view.addEventListener("pointerup", function () { down = null; });
    view.addEventListener("pointercancel", function () { down = null; });

    view.addEventListener("wheel", function (e) {
      if (!dragZoom) return;
      e.preventDefault();
      zoom = clamp(zoom * (e.deltaY > 0 ? 0.92 : 1.08), 0.8, 3);
      paint();
    }, { passive: false });

    function fire(ev) { for (var i = 0; i < pickCbs.length; i++) pickCbs[i](ev); }

    sun.addEventListener("click", function () { fire({ type: "sun" }); });

    /* ---------------- Marker ---------------- */
    function clearMarkers() {
      markers = [];
      markerBox.innerHTML = "";
    }

    function addMarkers(list) {
      clearMarkers();
      (list || []).forEach(function (m) {
        var b = el("button", "e2-mk", markerBox);
        b.type = "button";
        b.dataset.id = m.id;
        b.style.setProperty("--mk", "rgb(" + (m.rgb || "95,240,255") + ")");
        b.setAttribute("aria-label", m.label || m.id);
        b.addEventListener("click", function () {
          /* KÉO XONG KHÔNG PHẢI MỘT CÚ BẤM — không có ngưỡng này thì bước tự xong
             lúc trẻ chỉ đang kéo ảnh (bài học đã ghi ở PhotoStage bản React). */
          if (down && down.moved > DRAG_SLOP) return;
          fire({ type: "marker", id: m.id });
        });
        markers.push({ id: m.id, lat: m.lat, lon: m.lon, done: false, node: b });
      });
      paint();
    }

    function markDone(id) {
      for (var i = 0; i < markers.length; i++) {
        if (markers[i].id === id) {
          if (markers[i].done) return false;       // đã xong → không tính lần hai
          markers[i].done = true;
          markers[i].node.classList.add("done");
          return true;
        }
      }
      return false;
    }

    /* ---------------- API — ĐÚNG hợp đồng bản 3D ---------------- */
    var world = {
      start: function () {
        if (running) return;
        running = true; last = 0;
        raf = requestAnimationFrame(frame);
      },
      stop: function () {
        running = false;
        if (raf) { cancelAnimationFrame(raf); raf = 0; }
      },
      resize: paint,

      onPick: function (cb) { if (typeof cb === "function") pickCbs.push(cb); },
      addMarkers: addMarkers,
      clearMarkers: clearMarkers,
      markDone: markDone,
      get markers() {
        return markers.map(function (m) { return { id: m.id, done: m.done }; });
      },

      /**
       * MỚI so với bản 3D — và BẮT BUỘC phải gọi trước khi đặt marker theo lat/lon
       * THẬT. Xem cảnh báo "hai hệ toạ độ" ở đầu file.
       * @param {'globe'|'flat'} kind
       */
      setMap: setMap,
      get map() { return map; },

      /**
       * Toạ độ CSS của một vật trong cảnh, để script kiểm thử **bấm thật vào chỗ
       * nó đang hiện** thay vì gọi `pick()` tắt qua — gọi tắt thì vùng chạm và
       * việc bị che đều không được kiểm, mà đó là chỗ dễ sai nhất.
       */
      screenOf: function (kind, id) {
        var node = null;
        if (kind === "marker") {
          for (var i = 0; i < markers.length; i++) {
            if (markers[i].id === id) { node = markers[i].node; break; }
          }
        } else if (kind === "sun") node = sun;
        else if (kind === "sat") node = sat;
        if (!node) return null;
        var r = node.getBoundingClientRect();
        var vr = view.getBoundingClientRect();
        var vis = !node.hidden && r.width > 0 &&
                  r.right > vr.left && r.left < vr.right &&
                  r.bottom > vr.top && r.top < vr.bottom &&
                  getComputedStyle(node).visibility !== "hidden";
        return { x: r.left + r.width / 2, y: r.top + r.height / 2,
                 facing: !node.hidden, visible: vis };
      },

      setControls: function (o) {
        o = o || {};
        if (o.rotate != null) dragRotate = !!o.rotate;
        if (o.zoom != null) dragZoom = !!o.zoom;
      },

      /**
       * `dist` là khoảng cách camera của bản 3D: NHỎ = gần = phóng to.
       * Quy sang zoom 2D bằng `4.4 / dist` rồi kẹp — giữ đúng cảm giác của 8 bước
       * (2,5 gần nhất → 1,76×; 5,2 xa nhất → 0,85×).
       * lat/lon KHÔNG được dùng ở bất kỳ chỗ gọi nào; nếu sau này cần thì thêm
       * nhánh chuyển `facing`, đừng lặng lẽ bỏ qua tham số.
       */
      panTo: function (o) {
        o = o || {};
        var ms = o.ms != null ? o.ms : 1500;
        var z0 = zoom;
        var z1 = o.dist != null ? clamp(4.4 / o.dist, 0.8, 3) : zoom;
        var l0 = facing.lon, l1 = o.lon != null ? o.lon : facing.lon;
        var a0 = facing.lat, a1 = o.lat != null ? o.lat : facing.lat;
        var dl = wrapLon(l1 - l0);
        return tween(ms, function (k) {
          zoom = z0 + (z1 - z0) * k;
          facing.lon = wrapLon(l0 + dl * k);
          facing.lat = a0 + (a1 - a0) * k;
          paint();
        });
      },

      showGrid: function (on) {
        grid.style.display = on === false ? "none" : "";
        grid.style.opacity = "1";
      },
      fadeGrid: function (ms) {
        return tween(ms == null ? 900 : ms,
          function (k) { grid.style.opacity = String(1 - k); },
          function () { grid.style.display = "none"; });
      },

      /* Mặt Trời: `sunOn` là GETTER (bản 3D cũng vậy) — `mission-earth.html` đọc
         `world.sunOn` để chặn cú chạm thứ hai vào Mặt Trời đã cháy. */
      get sunOn() { return !!sunLit; },
      igniteSun: function (ms) {
        return tween(ms == null ? 1700 : ms, function (k) {
          sunLit = k;
          sun.style.setProperty("--lit", k.toFixed(3));
          stage.classList.toggle("e2-night", k < 0.5);
        }, function () { sunLit = 1; stage.classList.remove("e2-night"); });
      },
      dimSun: function (ms) {
        return tween(ms == null ? 1200 : ms, function (k) {
          sunLit = 1 - k;
          sun.style.setProperty("--lit", (1 - k).toFixed(3));
          stage.classList.toggle("e2-night", k > 0.5);
        }, function () { sunLit = 0; stage.classList.add("e2-night"); });
      },

      setSatelliteVisible: function (on) {
        sat.classList.toggle("show", on !== false);
      },
      setSatelliteSignal: function (on) {
        sat.classList.toggle("ok", on !== false);
      },

      /**
       * Góc giữa TRẠM PHÁT SÓNG và hướng đang nhìn, theo độ. Bước `rotation` xong
       * khi dưới 20°.
       * ⚠️ ĐÂY LÀ CHỖ BẢN 3D CÓ MỘT LỖI THIẾT KẾ THẬT: ở đó kéo là quay CAMERA nên
       *    `earth.quaternion` không đổi và góc trạm–vệ tinh **y nguyên** — bước đó
       *    chỉ tự xong vì hành tinh tự quay (tức là trẻ ngồi chờ, không phải giải),
       *    và ở `prefers-reduced-motion` (không tự quay) thì **treo vĩnh viễn**.
       *    Bản 2D không còn cửa cho lỗi đó: thứ trẻ kéo và thứ được chấm điểm là
       *    CÙNG MỘT con số (`facing.lon`).
       */
      stationAngleTo: function (lat, lon) {
        return angleBetween(facing.lat, facing.lon, lat, lon);
      },

      setSpin: function (scale) { spinScale = Number(scale) || 0; },

      /** Kéo xoay CHÍNH hành tinh (bước 5) thay vì xoay camera. */
      setEarthDrag: function (on) { earthDrag = on !== false; },

      /** Bật/tắt vòng ngắm — đích NHÌN THẤY ĐƯỢC của `stationAngleTo(...) → 0`. */
      showAim: function (on) { aim.hidden = on === false; paint(); },

      facingLatLon: function () {
        return { lat: facing.lat, lon: facing.lon };
      },

      /** Drone bay tới một vùng rồi quét bằng tia laser. */
      sendDrone: function (lat, lon) {
        var p = project(lat, lon);
        drone.style.left = p.x + "%";
        drone.style.top = p.y + "%";
        drone.classList.add("show");
        return tween(reduced() ? 0 : 1500, function (k) {
          drone.style.setProperty("--scan", k.toFixed(3));
        }, function () { drone.classList.remove("show"); });
      },

      /** Màng khí quyển bọc hành tinh (bước cuối). */
      shield: function (ms) {
        shieldEl.classList.add("show");
        return tween(ms == null ? 1600 : ms, function (k) {
          shieldK = k;
          shieldEl.style.setProperty("--k", k.toFixed(3));
        });
      },

      /* ⚠️ `shieldOn` LÀ MỘT PHẦN CỦA HỢP ĐỒNG, đừng bỏ sót như bản đầu của tôi.
         Bản 3D có `get shieldOn() { return shieldU.strength.value > 0.1; }` và
         `mission-earth.html` cùng bộ kiểm thử đều đọc nó để biết màng đã bọc chưa.
         Thiếu nó thì `world.shieldOn` là `undefined` — KHÔNG ném lỗi, chỉ lặng lẽ
         khác `true`, nên bước cuối trông như chạy đúng mà phép kiểm thì đỏ.
         Ngưỡng 0,1 lấy đúng theo bản 3D để hai engine trả lời giống nhau. */
      get shieldOn() { return shieldK > 0.1; }
    };

    return world;
  }

  global.AstroQEarth2D = { create: create };
})(window);
