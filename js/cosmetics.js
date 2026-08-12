/* ============================================================
   js/cosmetics.js — BUỒNG LÁI CỦA CON. Chỗ DUY NHẤT khai TÊN đồ trang trí.

   Nạp như script thường (sau js/ui-common.js):
     <script src="js/cosmetics.js"></script>
     AstroQCos.name(id, lang) · .apply() · .absorb(equipped, ship) · .ship()

   ⚠️⚠️ PHÂN CÔNG: **SERVER GIỮ GIÁ, CLIENT GIỮ TÊN.** File này KHÔNG có một con số
   giá nào, và đó là luật chứ không phải thiếu sót — bảng giá ở
   `AstroqSV/Services/Cosmetics.cs`, `GET /me/shop` trả kèm. Chép giá sang đây là hai
   nơi giữ một luật, và ngày đổi giá thì bản ở client vẫn nói con số cũ, tức **nói sai
   với trẻ ngay ở chỗ nó quyết định tiêu tiền**. Cùng phân công đã dùng cho huy hiệu
   (`js/badges.js`), mẫu vật (`js/specimens.js`), bậc (`js/ranks.js`) và mốc XP.

   ⚠️ BA ĐIỀU CẤM (nói lại từ Services/Cosmetics.cs, vì đây là chỗ người ta sẽ sửa
   khi muốn "cho hấp dẫn hơn"): không bán lợi thế · không hộp ngẫu nhiên · không
   khan hiếm giả.

   ⚠️ MÀU KHAI Ở `css/cockpit.css`, KHÔNG Ở ĐÂY. File này chỉ giữ CHỮ. Màu là việc
   của CSS (quy tắc 1 mục 2 CLAUDE.md: CSS luôn nằm trong `css/*.css`) — trừ ô xem
   trước ở cửa hàng, và ô đó cũng dùng class `cos-sw cos-sw--<id>` chứ không gán
   màu bằng JS.

   ⚠️ ĐỘ SÂU ≠ TRANG TRÍ. `js/depth.js` quyết NỘI DUNG, file này quyết HÌNH THỨC.
   Đừng gộp: một cái là luật dạy học, một cái là sở thích.
   ============================================================ */
(function (global) {
  "use strict";

  /* Món mặc định mỗi loại — luôn có, giá 0. Phải khớp `Cosmetics.Defaults` ở
     server; `scratchpad/check_pages.py` mục [23] đối chiếu hai bên. */
  var DEFAULTS = { theme: "cockpit-cyan", frame: "frame-steel" };

  var T = {
    vi: {
      "cockpit-cyan":   "Đèn Cyan",
      "cockpit-amber":  "Đèn Hổ Phách",
      "cockpit-violet": "Đèn Tím Thiên Hà",
      "cockpit-mint":   "Đèn Bạc Hà",
      "cockpit-rose":   "Đèn Hồng Tinh Vân",
      "frame-steel":    "Khung Thép",
      "frame-gold":     "Khung Vàng",
      "frame-nebula":   "Khung Tinh Vân",
      "frame-ice":      "Khung Băng",
      kind_theme: "Đèn buồng lái",
      kind_frame: "Khung thẻ ID",
      free: "Có sẵn"
    },
    en: {
      "cockpit-cyan":   "Cyan Lights",
      "cockpit-amber":  "Amber Lights",
      "cockpit-violet": "Galaxy Violet",
      "cockpit-mint":   "Mint Lights",
      "cockpit-rose":   "Nebula Rose",
      "frame-steel":    "Steel Frame",
      "frame-gold":     "Gold Frame",
      "frame-nebula":   "Nebula Frame",
      "frame-ice":      "Ice Frame",
      kind_theme: "Cockpit lights",
      kind_frame: "ID card frame",
      free: "Included"
    }
  };

  function lang(l) {
    if (l === "en" || l === "vi") return l;
    return (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
  }
  function t(k, l) { return (T[lang(l)] || T.vi)[k] || k; }

  function user() {
    try { return (global.AstroQ && AstroQ.getUser && AstroQ.getUser()) || {}; }
    catch (e) { return {}; }
  }

  /** Món đang đeo, đọc từ cache trong máy. Thiếu → món mặc định. */
  function equipped() {
    var u = user();
    var e = (u && u.equipped) || {};
    return {
      theme: e.theme || DEFAULTS.theme,
      frame: e.frame || DEFAULTS.frame
    };
  }

  /** Tên phi thuyền do trẻ đặt (chuỗi rỗng = chưa đặt). */
  function ship() { var u = user(); return (u && u.ship) || ""; }

  /* ── ÁP LÊN TRANG ──
     Gán vào `<html>` chứ không vào `<body>`: các biến màu của dự án khai ở `:root`,
     nên chỗ ghi đè phải ở cùng cấp mới thắng được mà không cần `!important`.
     ⚠️ Gọi NGAY khi nạp (không chờ DOMContentLoaded) để buồng lái không nhấp một
        cái từ tông mặc định sang tông của trẻ — cùng lý do `.ver-badge` phải chịu
        được cả hai trạng thái `readyState`. */
  function apply() {
    try {
      var e = equipped();
      var r = document.documentElement;
      r.setAttribute("data-cockpit", e.theme);
      r.setAttribute("data-frame", e.frame);
    } catch (err) {}
  }

  /** Nhận `equipped`/`ship` do SERVER trả rồi ghi xuống cache + vẽ lại ngay. */
  function absorb(eq, shipName) {
    var u = user();
    if (eq && typeof eq === "object") {
      u.equipped = {
        theme: eq.theme || DEFAULTS.theme,
        frame: eq.frame || DEFAULTS.frame
      };
    }
    if (typeof shipName === "string") u.ship = shipName;
    try { if (global.AstroQ && AstroQ.setUser) AstroQ.setUser(u); } catch (e) {}
    apply();
    return equipped();
  }

  /** Ghi món đang đeo vào cache (dùng khi vừa mua/vừa đeo, trước khi server trả). */
  function setEquipped(kind, id) {
    if (!id || (kind !== "theme" && kind !== "frame")) return equipped();
    var u = user();
    var e = u.equipped || {};
    e[kind] = id;
    u.equipped = e;
    try { if (global.AstroQ && AstroQ.setUser) AstroQ.setUser(u); } catch (err) {}
    apply();
    return equipped();
  }

  global.AstroQCos = {
    DEFAULTS: DEFAULTS,
    name: function (id, l) { return t(id, l); },
    kindName: function (kind, l) { return t("kind_" + kind, l); },
    freeLabel: function (l) { return t("free", l); },
    equipped: equipped,
    setEquipped: setEquipped,
    ship: ship,
    apply: apply,
    absorb: absorb,
    isDefault: function (id) {
      return id === DEFAULTS.theme || id === DEFAULTS.frame;
    }
  };

  apply();   // áp ngay, đừng chờ
})(window);
