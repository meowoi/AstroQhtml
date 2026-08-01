/* ============================================================================
   js/route-gate.js — CỔNG LỘ TRÌNH ở phía client (docs/decisions/003).

   Trẻ khám phá LẦN LƯỢT: chưa xong 70% nhiệm vụ ở điểm đến này thì chưa mở điểm
   đến sau. `explorer.html` hỏi file này để biết hành tinh nào bấm được.

   ⚠️ FILE NÀY KHÔNG TÍNH LUẬT, CHỈ ĐỌC. Cổng do server quyết
      (`Services/Missions.cs`: `UnlockRatio` · `UnlockGate` · `Route` ·
      `UnlockedPlaces`) và trả sẵn thành mảng `unlockedPlaces` trong
      `GET /me/missions`. Ở đây chỉ còn một phép "có trong mảng không" — không có
      chỗ cho hai bên hiểu luật khác nhau. Cùng phân công như `js/badges.js`
      (server giữ mốc, client giữ tên) và `js/ranks.js`.

   ⚠️ TẠI SAO PHẢI ĐI QUA CACHE, KHÔNG GỌI API THẲNG TỪ EXPLORER:
      `AstroQProgress.missions()` cần token, tức cần `js/firebase-auth.js` — mà
      `explorer.html` **cố ý không nạp** SDK đó (233 KB, trang này đã kéo three.js;
      `check_pages.py` mục [4] canh chuyện đó). Nên:
        · trang CÓ token (dashboard, missions) gọi `refresh()` → ghi cache;
        · `explorer.html` gọi `load()` → đọc cache.
      Đây là đúng khuôn đã dùng cho `astroq-progress`: nguồn sự thật ở server,
      trong máy chỉ là bản sao để vẽ được giao diện.

   ⚠️ CỔNG LÀ LỜI DẪN ĐƯỜNG, KHÔNG PHẢI HÀNG RÀO AN NINH. Cache trong máy sửa
      được bằng DevTools. Chấp nhận được vì bấm vào một hành tinh **không cấp
      phần thưởng nào do client quyết** — `AstroQProgress.planet()` chỉ báo việc đã
      làm, server mới cộng. Muốn hàng rào thật thì phải chặn ở server, và server
      **đã** là nơi duy nhất quyết `unlockedPlaces`.
   ============================================================================ */
(function (global) {
  "use strict";

  var CACHE = "astroq-route-gate";

  /* ⚠️ CHỈ DÙNG KHI CHƯA TỪNG ĐỌC ĐƯỢC SERVER LẦN NÀO (máy sạch + chưa đăng nhập).
     Đây là một con số client giữ trong khi server mới là nguồn sự thật — đúng thứ
     dự án đã trả giá 6 lần. Nên `check_pages.py` có phép kiểm đối chiếu nó với
     `Missions.Route[0]`; lệch là báo hỏng, không phải im lặng.
     Fail-closed: thà khoá hết trừ điểm đến đầu tiên, còn hơn mở hết (phá cổng) hay
     khoá cả điểm đến đầu (trẻ kẹt cứng, không vào được đâu). */
  var FIRST_PLACE = "earth";

  var st = {
    active: false,   // cổng có hiệu lực trên trang này hay không
    ready: false,    // đã hỏi xong chưa (thành công HOẶC thất bại)
    live: false,     // số đang dùng là của server lần này, không phải cache cũ
    route: [FIRST_PLACE],
    open: [FIRST_PLACE],
    gate: 0, done: 0, total: 0
  };

  var blockedCb = null;

  function readCache() {
    try {
      var raw = global.localStorage.getItem(CACHE);
      if (!raw) return null;
      var o = JSON.parse(raw);
      if (!o || !Array.isArray(o.open) || !o.open.length) return null;
      return o;
    } catch (e) { return null; }
  }

  function writeCache() {
    try {
      global.localStorage.setItem(CACHE, JSON.stringify({
        route: st.route, open: st.open,
        gate: st.gate, done: st.done, total: st.total
      }));
    } catch (e) { /* chế độ riêng tư chặn localStorage — không phải lỗi cần báo */ }
  }

  /* Rót dữ liệu từ `GET /me/missions` vào trạng thái. Trả true nếu nhận được thật.
     ⚠️ ĐÒI `unlockedPlaces` LÀ MẢNG KHÔNG RỖNG. Server cũ (chưa deploy bản có cổng)
     trả về thiếu trường này; nhận bừa `[]` là khoá luôn cả Trái Đất. */
  function absorb(d) {
    if (!d || !Array.isArray(d.unlockedPlaces) || !d.unlockedPlaces.length) return false;
    st.open = d.unlockedPlaces.slice();
    st.route = Array.isArray(d.route) && d.route.length ? d.route.slice() : st.open.slice();
    var m = d.missions && d.missions[st.route[0]];
    if (m) {
      st.gate = m.gate | 0;
      st.done = (m.doneSteps || []).length;
      st.total = (m.steps || []).length;
    }
    st.live = true;
    writeCache();
    return true;
  }

  /** Hỏi server rồi ghi cache. Gọi từ trang CÓ token (dashboard, missions). */
  function refresh() {
    if (!global.AstroQProgress || !global.AstroQProgress.missions) {
      st.ready = true;
      return Promise.resolve(false);
    }
    return global.AstroQProgress.missions().then(function (r) {
      var got = !!(r && r.ok && absorb(r.data));
      st.ready = true;
      return got;
    }).catch(function () { st.ready = true; return false; });
  }

  /**
   * Nạp trạng thái cổng cho trang hiện tại: cache trước (vẽ được ngay), rồi thử
   * hỏi server nếu trang này có token. Luôn resolve — không bao giờ ném ra ngoài,
   * vì cổng hỏng không được làm vỡ bản đồ.
   */
  function load() {
    var c = readCache();
    if (c) {
      st.open = c.open.slice();
      st.route = (Array.isArray(c.route) && c.route.length ? c.route : c.open).slice();
      st.gate = c.gate | 0; st.done = c.done | 0; st.total = c.total | 0;
    }
    return refresh().then(function () { return info(); });
  }

  /** Bấm vào điểm đến này được không. Cổng tắt thì mọi thứ mở, y như trước. */
  function canVisit(id) {
    if (!st.active) return true;
    return st.open.indexOf(String(id)) >= 0;
  }

  function info() {
    return {
      active: st.active, ready: st.ready,

      /* `live` = số này vừa lấy từ server trong lượt tải trang NÀY. Chỉ để chẩn
         đoán — ĐỪNG dùng nó để chọn lời nhắc.
         ⚠️ `explorer.html` không có token (cố ý không nạp SDK Firebase) nên ở đó
            `live` LUÔN false. Bản đầu của file này dùng `live` để chọn câu nhắc, và
            hậu quả là MỌI trẻ đều bị nói "không đọc được tiến độ của bạn" dù cache
            có số thật — bộ `smoke_route_gate.py` bắt được đúng chỗ này. */
      live: st.live,

      /** CÓ số tiến độ dùng được hay không (từ server HOẶC cache). Đây mới là thứ
       *  quyết định nói "còn n bước nữa" hay nói "chưa đọc được tiến độ". */
      known: st.total > 0 && st.gate > 0,

      route: st.route.slice(), open: st.open.slice(),
      first: st.route[0] || FIRST_PLACE,
      gate: st.gate, done: st.done, total: st.total,
      /** Còn bao nhiêu bước nữa mới mở điểm đến sau. 0 = đã đạt cổng. */
      remaining: Math.max(0, st.gate - st.done)
    };
  }

  global.AstroQGate = {
    FIRST_PLACE: FIRST_PLACE,
    load: load,
    refresh: refresh,
    canVisit: canVisit,
    info: info,

    /**
     * Rót thẳng dữ liệu `GET /me/missions` mà trang GỌI RỒI vào cache — để
     * `missions.html` không phải gọi API lần thứ hai cho cùng một câu trả lời.
     * Trả true nếu dữ liệu dùng được.
     */
    feed: function (data) { var got = absorb(data); if (got) st.ready = true; return got; },

    /** Bật/tắt cổng. Mặc định TẮT — xem ghi chú ở `explorer.html`. */
    setActive: function (on) { st.active = on !== false; },
    active: function () { return st.active; },

    /** Trang đăng ký cách NÓI với trẻ khi bấm vào chỗ còn khoá. */
    onBlocked: function (cb) { blockedCb = typeof cb === "function" ? cb : null; },

    /** `selectBody` gọi cái này thay vì im lặng bỏ qua cú bấm. */
    explain: function (id) { if (blockedCb) blockedCb(String(id), info()); },

    /** Xoá cache — dùng khi thử lại luồng. Console: AstroQGate.reset() */
    reset: function () {
      try { global.localStorage.removeItem(CACHE); } catch (e) {}
      st.open = [FIRST_PLACE]; st.route = [FIRST_PLACE];
      st.gate = st.done = st.total = 0; st.live = false; st.ready = false;
    }
  };
})(window);
