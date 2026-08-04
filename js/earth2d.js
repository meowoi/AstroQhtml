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

  /* SÀN PHÓNG = 1, KHÔNG PHẢI 0,8 (sửa 02/08/2026, `docs/decisions/005`).
     ⚠️ Dưới 1 là lớp ảnh NHỎ HƠN KHUNG, tức chắc chắn có dải đen trên và dưới —
        `.e2-layer` cao `max(50vw,100vh)` nên ở zoom 1 nó vừa đủ phủ, còn zoom 0,846
        (bước ③ gọi `dist:5.2`) đo được hở **76px trên + 76px dưới** trên khung
        1900×985. Đây là dải đen ĐỐI XỨNG, khác dải đen do `facing.lat` gây ra.
     Mất gì: `dist > 4.4` không lùi ra xa thêm được nữa. Không mất bài học nào —
     ở zoom 1 bản đồ đã phủ trọn bề rộng khung, tức "thấy cả hai nửa cùng lúc"
     (mục đích của `dist:5.2` ở bước ③) vẫn đạt. */
  var ZOOM_MIN = 1;

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
    /* ẢNH BỀ MẶT — BA BẢN, LÁT THEO KINH TUYẾN (sửa 02/08/2026, `docs/decisions/005`).
       ⚠️ LỖI ĐÃ CHỮA: `paint()` dịch lớp này theo `facing` tới ±50% bề rộng, nhưng
          lớp chỉ được cỡ để phủ khung KHI phép dịch = 0 (`css:550`). Không có chỗ nào
          kẹp phép dịch lại → mọi `facing.lon != 0` đều đẩy ảnh ra khỏi khung và để lại
          một dải ĐEN. Đo được (`scratchpad/probe_map_cover.py`): **5/9 cấu hình bước
          thật hở, trên MỌI cỡ màn**; tệ nhất bước ③ `sun` hở **602px bên phải** trên
          khung 1900×985. Chủ dự án gặp đúng lỗi này khi chơi thật.
       ⚠️ KHÔNG chữa bằng cách kẹp `px`: ở zoom 1 thì kẹp chỉ cho phép |lon| ≤ 6,4°,
          tức ném bỏ khung nhìn `FACE_OPEN` (30, 95) mà `004` đã chọn VÌ NỘI DUNG.
       Chữa đúng: bản đồ equirectangular **lặp liền mạch theo kinh độ** — kinh tuyến
       180°Đ và 180°T là cùng một đường. Nên đặt thêm một bản phía tây và một bản phía
       đông; ba bản phủ 3× bề rộng lớp, mà phép dịch tối đa chỉ 0,5× → không bao giờ hở.
       (Kiểm được: cần `zoom ≥ 2/3`, mà sàn phóng là `ZOOM_MIN` = 1.)
       ⚠️⚠️ HAI BẢN SAO PHẢI Ở NGOÀI HỘP CỦA LỚP (`left:±100%`) VÀ KHÔNG ĐƯỢC ĐỔI CỠ
          LỚP. Marker định vị bằng PHẦN TRĂM của `.e2-layer` (`project()` trả `x =
          (lon+180)/360*100`), nên đổi cỡ hay tỉ lệ lớp là dời toàn bộ toạ độ địa lý —
          đúng lỗi "thẻ Amazon rơi giữa đại dương" của bản 3D. Bản sao chỉ để LẤP MẮT.
       Bản sao chỉ hiện ở chế độ bản đồ phẳng: ảnh quả cầu là ảnh CHỤP một hình cầu,
       lát nó ra cạnh nhau là vô nghĩa (xem `.e2-wrap` trong CSS). */
    function mkPic(cls) {
      var pc = el("picture", cls, layer);
      var a = el("source", "", pc); a.type = "image/avif";
      var w = el("source", "", pc); w.type = "image/webp";
      var im = el("img", "e2-img", pc);
      im.alt = "";
      im.decoding = "async";
      im.setAttribute("aria-hidden", "true");
      return { a: a, w: w, img: im };
    }
    var pics = [
      mkPic(""),                  // bản THẬT — cái mà marker neo vào
      mkPic("e2-wrap e2-wrap-w"), // bản sao phía TÂY  (left:-100%)
      mkPic("e2-wrap e2-wrap-e")  // bản sao phía ĐÔNG (left:+100%)
    ];

    var grid = el("div", "e2-grid", layer);
    var markerBox = el("div", "e2-markers", layer);
    var drone = el("div", "e2-drone", layer);
    var beam = el("div", "e2-beam", drone);
    /* ⛔⛔ KHÔNG DỰNG LẠI NÚT `.e2-sun` — ĐÃ BỎ HẲN 03/08/2026.
       Đây là **rác còn sót của một quyết định đã chốt từ 02/08/2026**: bản 1 của bước ③
       bắt trẻ đi tìm và chạm nút Mặt Trời, chủ dự án bác vì nút neo `top:9%; right:8%`
       của khung mà bản đồ đã phủ kín → nó lẫn vào chính bức ảnh Trái Đất; rồi bản 2 bị
       bác tiếp với đúng câu *"trẻ hiểu rằng mặt trời nằm trên trái đất. Vẫn vô lý"*.
       Lời thoại đã viết lại cho đúng (có phép kiểm ở `check_pages` đòi nói rõ Mặt Trời
       **không nằm trên tấm bản đồ này**), và chính chú thích của phép kiểm đó đã ghi
       "sau khi bỏ nút `.e2-sun`" — nhưng THẺ DOM thì chưa ai xoá. Nên nó vẫn vẽ ra một
       đĩa sáng mờ ở góc trên-phải trong MỌI bước, và chủ dự án chơi thật rồi hỏi lại:
       *"vẫn còn hình mặt trời ở đây? bỏ đi"*.
       Cùng một họ với `.e2-terminator` và vành tròn của `.e2-shield`: một hình đúng cho
       QUẢ CẦU (nơi Mặt Trời ở ngoài rìa hành tinh) bị để nguyên trên BẢN ĐỒ PHẲNG phủ
       kín khung, nơi mọi pixel đều là bề mặt Trái Đất — tức nó nói rằng Mặt Trời nằm
       TRÊN mặt đất.
       ⚠️ `igniteSun`/`dimSun` VẪN CÒN và vẫn là bài học của bước ③ — chúng chỉ còn tác
          động lên `.e2-night` (cả bản đồ tối đi rồi sáng lại) và `sunLit`. Thứ trẻ thấy
          là HỆ QUẢ, không phải cái đèn. */
    var shieldEl = el("div", "e2-shield", view);

    /* ---------------- Trạng thái ---------------- */
    var map = "globe";
    var facing = { lat: 0, lon: -95 };   // ảnh quả cầu tâm ~Bắc Mỹ
    var zoom = 1;
    var spinScale = 0;
    var sunLit = 1;
    var dragRotate = true, dragZoom = true;
    var markers = [];                    // {id, lat, lon, done, node}
    var pickCbs = [];
    var running = false, raf = 0, last = 0;
    var shieldK = 0;                     // 0 → 1 khi màng khí quyển bọc dần

    setMap("globe");

    /* ---------------- Ảnh + vẽ lại ---------------- */
    function setMap(kind) {
      var m = MAPS[kind] || MAPS.globe;
      map = MAPS[kind] ? kind : "globe";
      for (var pi = 0; pi < pics.length; pi++) {
        var P = pics[pi];
        P.a.srcset = m.avif;
        P.w.srcset = m.webp;
        P.img.src = m.webp;                    // nhánh cuối, trình duyệt tự chọn source
        P.img.width = m.w; P.img.height = m.h; // khai cỡ để chặn CLS
      }
      // Ba bản dùng CÙNG một URL nên trình duyệt giải mã một lần rồi dùng lại.
      stage.classList.toggle("e2-flat", !!m.flat);
      /* ⚠️⚠️ PHẢI ĐO LẠI BỐ CỤC Ở ĐÂY — LỖI CÓ SẴN, sửa 02/08/2026.
         `.e2-layer` đổi CỠ theo chế độ bản đồ: quả cầu `min(100vw,100vh)` (vuông),
         bản đồ phẳng `max(50vw,100vh)`. Nhưng `measure()` chỉ chạy MỘT LẦN lúc dựng
         (khi map còn là `globe`) và khi `resize` — nên `lyH` giữ mãi chiều cao của
         ảnh QUẢ CẦU. Trên khung 1440×900 hai con số trùng nhau (900) nên không ai
         thấy; trên **điện thoại dọc 390×844 thì lệch 390 vs 844**, và hậu quả là
         `maxPyPct()` ra **0** → `paint()` kẹp phép dịch DỌC về 0 → **không tài nào
         đưa được vĩ độ cao vào khung**. Đo được: Nam Cực (lat −75) ở `dist:3,1` rơi
         xuống y = 921 trên khung cao 844, tức nằm ngoài — bước ④ `life` không chơi
         được trên máy tính bảng dọc.
         ⚠️ `probe_map_cover.py` KHÔNG bắt được (203/203 vẫn xanh): kẹp py về 0 làm
            MẤT khả năng dịch dọc chứ không làm HỞ khung, mà nó chỉ hỏi chuyện hở.
         Đọc `offsetHeight` ép trình duyệt tính lại bố cục, nên chỉ gọi ở đây —
         KHÔNG gọi trong `paint()` (nó chạy mỗi khung hình khi hành tinh tự quay). */
      measure();
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

    /* ---------------- Trần dịch DỌC ----------------
       ⚠️ VĨ TUYẾN KHÔNG LÁT ĐƯỢC — hai cực là MÉP THẬT của thế giới, không có gì
          phía trên Bắc Cực để ghép vào. Nên trục dọc phải KẸP, khác trục ngang.
       Đo được trước khi sửa: `.e2-layer` cao `max(50vw,100vh)`, mà trên khung
       1900×985 thì `max(950,985) = 985` — ĐÚNG BẰNG chiều cao khung, tức phần dư
       dọc bằng **0**. Vì thế mọi `facing.lat != 0` đều hở một dải đen trên hoặc
       dưới: bước ③ `sun` (lat 30, zoom 0,846) hở **240px phía trên**.
       Kẹp chỉ đổi KHUNG NHÌN, không đổi địa lý: marker là con của `.e2-layer` nên
       chúng dịch CÙNG lớp — toạ độ thật giữ nguyên tuyệt đối. */
    var vpW = 0, vpH = 0, lyH = 0;
    function measure() {
      vpW = view.clientWidth; vpH = view.clientHeight; lyH = layer.offsetHeight;
    }
    // Đọc bố cục MỘT LẦN rồi nhớ lại; `paint()` chạy mỗi khung hình khi hành tinh
    // tự quay, đọc `clientHeight` ở đó là ép trình duyệt tính lại bố cục 60 lần/giây.
    window.addEventListener("resize", measure);
    measure();

    function maxPyPct() {
      if (!lyH) measure();
      if (!lyH) return 0;
      return Math.max(0, (lyH * zoom - vpH) / 2) / lyH * 100;
    }

    function paint() {
      var m = MAPS[map];
      // Ảnh quả cầu: "xoay" = dịch ảnh theo kinh/vĩ tuyến. Bản đồ phẳng: dịch thật.
      // px KHÔNG cần kẹp — ba bản ảnh lát theo kinh tuyến đã lo (xem `mkPic`).
      var px = m.flat ? -wrapLon(facing.lon) / 360 * 100 : 0;
      var py = m.flat ? clamp((facing.lat) / 180 * 100, -maxPyPct(), maxPyPct()) : 0;
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
       về chính `view`, nên `click` KHÔNG BAO GIỜ tới được `.e2-mk`
       nằm bên trong. Hậu quả: chạm điểm tín hiệu không ăn, chạm Mặt Trời không ăn
       → nhiệm vụ tắc ở bước 1.
       Nham hiểm ở chỗ `document.elementFromPoint()` vẫn trả về đúng cái nút (việc
       dò trúng đích vẫn đúng, chỉ có việc GIAO sự kiện là hỏng), nên soi bằng
       elementFromPoint sẽ kết luận "nút bấm được" — đo được đúng như vậy.
       Cách đúng: chỉ bắt con trỏ KHI ĐÃ THẬT SỰ KÉO (vượt DRAG_SLOP). Lúc đó
       trình duyệt cũng đã tự huỷ `click`, nên không mất gì; còn cú chạm không kéo
       thì đi thẳng tới nút như thường. */
    view.addEventListener("pointerdown", function (e) {
      if (!dragRotate) return;
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
      zoom = clamp(zoom * (e.deltaY > 0 ? 0.92 : 1.08), ZOOM_MIN, 3);
      paint();
    }, { passive: false });

    function fire(ev) { for (var i = 0; i < pickCbs.length; i++) pickCbs[i](ev); }

    /* ⛔ KHÔNG CÒN `sun.addEventListener(… fire({type:"sun"}))` — bỏ 03/08/2026 cùng thẻ
       `.e2-sun`. Bước ③ không nhận cú chạm Mặt Trời nào nữa (`pick({type:'sun'})` đã bị
       gỡ khỏi cả `mission-earth.html` lẫn bộ smoke từ 02/08/2026); giữ lời gọi này lại
       sau khi biến `sun` biến mất là một `ReferenceError` chạy NGAY lúc dựng cảnh — và
       đó đúng là lỗi tôi vừa tự tạo ra trong lượt này rồi bắt được bằng `pageerror`.
       Cùng vết với nhánh `"sat"` ở `screenOf` bên dưới. */

    /* ---------------- Marker ---------------- */
    function clearMarkers() {
      markers = [];
      markerBox.innerHTML = "";
    }

    /**
     * @param list [{id, lat, lon, rgb, label, cls?, html?}]
     *   `cls`  — class PHỤ thêm vào `.e2-mk`, để một bước dựng dấu hiệu kiểu khác
     *            (bước ⑤ dùng nó cho ba nhà máy trên bản đồ).
     *   `html` — nội dung bên trong. Mặc định rỗng (chấm tròn thuần CSS).
     * ⚠️ MỌI DẤU HIỆU NEO THEO lat/lon PHẢI ĐI QUA ĐÂY, đừng tự chèn phần tử vào
     *    `.e2-layer`: `paint()` chỉ cập nhật vị trí + chống-phóng cho những gì nằm
     *    trong `markers`. Chèn tay là dấu hiệu đứng yên trong khi bản đồ trượt đi —
     *    đúng lỗi "mục tiêu chạy khỏi con trỏ" mà `004` đã đi sửa.
     */
    function addMarkers(list) {
      clearMarkers();
      (list || []).forEach(function (m) {
        var b = el("button", "e2-mk" + (m.cls ? " " + m.cls : ""), markerBox);
        b.type = "button";
        if (m.html) b.innerHTML = m.html;
        b.dataset.id = m.id;
        if (m.zone) b.dataset.zone = m.zone;   // để `pick-place.js` nhận làm ô thả
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
        }
        /* ⚠️ HAI NHÁNH ĐÃ BỎ, CÙNG MỘT LÝ DO — ĐỪNG THÊM LẠI NHÁNH NÀO TRỎ VÀO BIẾN
           KHÔNG CÒN TỒN TẠI:
             · `"sat"` — bỏ 02/08/2026 cùng bước `rotation` (`docs/decisions/005`);
             · `"sun"` — bỏ 03/08/2026 cùng thẻ `.e2-sun`.
           Cả hai từng sống sót sau khi biến của chúng bị xoá, tức là một `ReferenceError`
           **nằm chờ đúng người gọi đầu tiên** — im lặng tuyệt đối cho tới lúc đó. Nhánh
           `"sun"` thì tệ hơn: lời gọi `sun.addEventListener` ở trên chạy NGAY lúc dựng
           cảnh nên nó giết cả trang, và chỉ có `pageerror` mới nói ra được. */
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
        var z1 = o.dist != null ? clamp(4.4 / o.dist, ZOOM_MIN, 3) : zoom;
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

      /**
       * ĐƯA MỘT ĐIỂM ĐỊA LÝ VÀO ĐÚNG TÂM KHUNG NHÌN — rồi mới gọi `panTo`.
       *
       * ⚠️ VÌ SAO KHÔNG PHẢI LÀ `panTo({lon})`: `panTo` nhận thẳng `facing.lon`, mà
       *    `facing.lon` chỉ TRÙNG tâm khung khi `zoom = 1`. Phóng to thì lệch đi.
       *    Công thức (z = zoom đích): **facing.lon = z · lon**.
       *
       * ⚠️ TRƯỚC 02/08/2026 CÔNG THỨC NÀY CÒN CÓ MỘT SỐ HẠNG BÙ `180 − 180·V/W`, vì
       *    `.e2-layer` ở chế độ phẳng bị **neo mép trái** (CSS quá ràng buộc — xem
       *    `css/mission-earth.css`). Số hạng đó nay đã BỎ vì CSS đã căn giữa lớp.
       *    Đừng thêm lại: khi lớp còn neo trái, dải kinh độ với tới được bị cắt mất
       *    một đầu và **mọi kinh độ đông hơn ~83° không thể đưa vào khung trên điện
       *    thoại dọc** — marker chỉ vẽ trên bản ảnh THẬT, hai bản sao lát chỉ lấp mắt.
       *
       * ⚠️ ẢNH QUẢ CẦU thì `project()` đã lấy `facing` làm TÂM phép chiếu, nên ở đó
       *    hàm này chuyển thẳng xuống `panTo` — đừng "sửa" nó thành áp công thức cho
       *    cả hai chế độ.
       */
      centerOn: function (o) {
        o = o || {};
        var m = MAPS[map];
        if (!m.flat) return world.panTo(o);
        var z = o.dist != null ? clamp(4.4 / o.dist, ZOOM_MIN, 3) : zoom;
        var out = {};
        for (var k in o) if (o.hasOwnProperty(k)) out[k] = o[k];
        if (o.lon != null) out.lon = wrapLon(z * o.lon);
        /* Trục DỌC cùng công thức, nhưng `paint()` còn KẸP `py` theo phần dư dọc
           (`maxPyPct`) vì hai cực là mép thật của thế giới — nên vĩ độ cao có thể
           không vào được đúng tâm. Không sao: điều cần là marker NẰM TRONG khung,
           và phép kẹp chỉ kéo khung về phía cực gần nhất, tức vẫn đi đúng hướng. */
        if (o.lat != null) out.lat = z * o.lat;
        return world.panTo(out);
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

      /* Mặt Trời: `sunOn` là GETTER (bản 3D cũng vậy) — nay chỉ còn là "bản đồ đang
         sáng hay đang tối", vì không còn vật thể Mặt Trời nào để chạm.
         ⚠️ KHÔNG CÒN `sun.style.setProperty("--lit", …)`: thẻ `.e2-sun` đã bỏ hẳn
            03/08/2026 (lý do đầy đủ ở chỗ khai `shieldEl`). Bài học của bước ③ nằm ở
            `.e2-night` — CẢ BẢN ĐỒ tối đi rồi sáng lại — chứ không ở một cái đèn góc
            màn hình. Giữ `sunLit` vì `mission-earth.html` và bộ smoke đọc `world.sunOn`. */
      get sunOn() { return !!sunLit; },
      igniteSun: function (ms) {
        return tween(ms == null ? 1700 : ms, function (k) {
          sunLit = k;
          stage.classList.toggle("e2-night", k < 0.5);
        }, function () { sunLit = 1; stage.classList.remove("e2-night"); });
      },
      dimSun: function (ms) {
        return tween(ms == null ? 1200 : ms, function (k) {
          sunLit = 1 - k;
          stage.classList.toggle("e2-night", k > 0.5);
        }, function () { sunLit = 0; stage.classList.add("e2-night"); });
      },

      setSpin: function (scale) { spinScale = Number(scale) || 0; },

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
