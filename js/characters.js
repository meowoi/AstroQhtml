/* ============================================================
   characters.js — DANH SÁCH NHÂN VẬT, CHỖ DUY NHẤT khai báo.

   Trước 29/07/2026 mảng này nằm riêng trong js/auth-flow.js. Tách ra vì
   `profile.html` (Hồ sơ Phi Hành Gia) cũng cho đổi trang phục, mà copy 10
   dòng dữ liệu sang trang thứ hai là chắc chắn có ngày hai bên lệch nhau.

   Nạp TRƯỚC js/auth-flow.js và trước script riêng của profile.html:
     <script src="js/characters.js"></script>

   API:
     AstroQChars.all()          → mảng nhân vật (bản sao, sửa không ảnh hưởng gốc)
     AstroQChars.byId("m")      → một nhân vật, null nếu không có
     AstroQChars.MYSTERY        → số ô "???" chưa mở khoá
     AstroQChars.avatarOf(u)    → ảnh avatar theo hồ sơ người dùng (có đường lùi)
     AstroQChars.zoomOf(u)      → mức zoom avatar tương ứng
     AstroQChars.get()          → id nhân vật đang chọn ("" = chưa chọn bao giờ)
     AstroQChars.chosen()       → đã chọn nhân vật chưa (quyết select.html vs dashboard)
     AstroQChars.absorb(id,ava) → nhận nhân vật từ SERVER, ghi xuống cache
     AstroQChars.syncUp(a,uid)  → đẩy nhân vật trong máy lên server, MỘT LẦN/uid
     AstroQChars.sync(...)      → cầu nối hai chiều, gọi từ trang CÓ token

   ⚠️⚠️ CACHE Ở `astroq-user.character`, NGUỒN SỰ THẬT Ở HỒ SƠ TRÊN SERVER — cùng
   khuôn `js/depth.js`. `select.html` CỐ Ý không nạp SDK Firebase nên nó ghi được
   cache mà KHÔNG gửi được lên server; trang có token lo việc đẩy lên / kéo về.
   LỖI THẬT ĐÃ TRẢ GIÁ (22/08/2026): thiếu cầu nối này thì nhân vật chỉ sống trong
   một máy, mà `logout()` xoá sạch mọi khoá `astroq-*` (xem `clearAccountData` ở
   `js/ui-common.js`) ⇒ **đăng nhập lại là phải chọn lại nhân vật, mọi lần.**

   role/trait/stats vẫn là dữ liệu tạm (giữ nguyên như bản cũ, chờ cập nhật).
   ============================================================ */
(function (global) {
  "use strict";

  var CHARACTERS = [
    { id:"m",     name:"Comet",    model:"3d/m3d.png",     ava:"ava/avam.png",     role:{vi:"Phi công trưởng",en:"Chief Pilot"},   trait:{vi:"Lanh lợi & tò mò",en:"Quick & curious"},  stats:{pow:78,spd:90,iq:74} },
    { id:"b",     name:"Byte",     model:"3d/b3d.png",     ava:"ava/avab.png",     role:{vi:"Kỹ sư hệ thống",en:"Systems Engineer"},trait:{vi:"Điềm tĩnh & logic",en:"Calm & logical"}, stats:{pow:70,spd:66,iq:95} },
    { id:"q",     name:"Quark",    model:"3d/q3d.png",     ava:"ava/q2.png",       role:{vi:"Trinh sát",en:"Scout"},               trait:{vi:"Nhanh nhẹn & tinh nghịch",en:"Nimble & playful"}, stats:{pow:60,spd:96,iq:70} },
    { id:"raica", name:"Castor",   model:"3d/raica3d.png", ava:"ava/avaraica.png", zoom:1.6, role:{vi:"Chỉ huy",en:"Commander"},   trait:{vi:"Quyết đoán & ấm áp",en:"Decisive & warm"}, stats:{pow:88,spd:72,iq:82} },
    { id:"bao",   name:"Umbra",    model:"3d/bao3D.png",   ava:"ava/avabao.png",   role:{vi:"Đội trưởng tấn công",en:"Strike Leader"},trait:{vi:"Dũng mãnh & nhanh",en:"Fierce & fast"}, stats:{pow:94,spd:92,iq:66} },
    { id:"chim",  name:"Ignis",    model:"3d/chim3D.png",  ava:"ava/avachim.png",  role:{vi:"Hoa tiêu",en:"Navigator"},            trait:{vi:"Tự do & tinh mắt",en:"Free & sharp-eyed"}, stats:{pow:64,spd:88,iq:80} },
    { id:"cho",   name:"Sirius",   model:"3d/cho2.png",    ava:"ava/avacho.png",   role:{vi:"Vệ binh",en:"Guardian"},              trait:{vi:"Trung thành & gan dạ",en:"Loyal & brave"}, stats:{pow:82,spd:78,iq:72} },
    { id:"chuot", name:"Lyrae",    model:"3d/chuot3d.png", ava:"ava/avachuot.png", role:{vi:"Thợ máy",en:"Mechanic"},              trait:{vi:"Khéo léo & lanh",en:"Handy & sharp"}, stats:{pow:58,spd:84,iq:86} },
    { id:"cu",    name:"Moros",    model:"3d/cu3d.png",    ava:"ava/avacu.png",    role:{vi:"Nhà thiên văn",en:"Astronomer"},      trait:{vi:"Uyên bác & trầm",en:"Wise & quiet"}, stats:{pow:62,spd:60,iq:98} },
    { id:"cua",   name:"Karkinos", model:"3d/cua3d.png",   ava:"ava/avacua.png",   role:{vi:"Kỹ thuật viên giáp",en:"Armor Tech"}, trait:{vi:"Cứng cỏi & lì",en:"Tough & sturdy"}, stats:{pow:90,spd:54,iq:70} }
  ];

  /** Số ô "???" hiện kèm roster (nhân vật chưa mở khoá). */
  var MYSTERY = 2;

  function byId(id) {
    for (var i = 0; i < CHARACTERS.length; i++) {
      if (CHARACTERS[i].id === id) return CHARACTERS[i];
    }
    return null;
  }

  /* Ảnh avatar theo hồ sơ, có đường lùi: hồ sơ ghi sẵn `avatar` (bản cũ) →
     tra theo `character` → cuối cùng lấy nhân vật đầu danh sách. Nhờ vậy hồ sơ
     lưu từ trước khi có file này vẫn hiện đúng ảnh. */
  function avatarOf(u) {
    if (u && u.avatar) return u.avatar;
    var c = u && byId(u.character || u.selectedCharacter);
    return (c || CHARACTERS[0]).ava;
  }
  function zoomOf(u) {
    if (u && u.avatarZoom) return u.avatarZoom;
    var c = u && byId(u.character || u.selectedCharacter);
    return (c && c.zoom) || 1;
  }

  /* ══════════════════════════════════════════════════════════════════════
     CẦU NỐI CACHE ↔ SERVER
     Cùng khuôn `js/depth.js`: hồ sơ trong máy là CACHE, hồ sơ trên server là
     NGUỒN SỰ THẬT. Ở đây vì `characters.js` là chỗ duy nhất biết luật nhân vật
     (id nào có thật, zoom bao nhiêu) — để phía gọi tự suy là có ngày hai trang
     suy khác nhau.
     ══════════════════════════════════════════════════════════════════════ */

  /* Đóng dấu uid: hai đứa trẻ dùng chung một máy thì nhân vật của đứa trước
     không được đẩy lên hồ sơ của đứa sau. Cùng lý do `astroq-depth-synced`. */
  var LS_SYNC = "astroq-char-synced";

  function user() {
    try { return (global.AstroQ && AstroQ.getUser && AstroQ.getUser()) || null; }
    catch (e) { return null; }
  }

  /** id nhân vật đang chọn. `""` = chưa chọn bao giờ (KHÁC "chọn con đầu danh sách"). */
  function get() {
    var u = user();
    return (u && (u.character || u.selectedCharacter)) || "";
  }

  /** Đã chọn nhân vật chưa. Đây là câu quyết định `select.html` hay `dashboard.html`. */
  function chosen() { return !!byId(get()); }

  /**
   * Nhận nhân vật do SERVER trả về rồi ghi xuống cache.
   * `serverAvatar` có thể rỗng (hồ sơ cũ chỉ có `character`) — khi đó lấy ảnh
   * từ chính danh sách trên, nên không bao giờ ghi một đường dẫn rỗng vào hồ sơ.
   * → id đã ghi, hoặc "" nếu server không trả nhân vật nào.
   */
  function absorb(serverChar, serverAvatar) {
    var c = byId(serverChar);
    if (!c) return "";                       // rỗng / id lạ → GIỮ NGUYÊN cache
    var u = user() || {};
    u.character = c.id;
    u.selectedCharacter = c.id;
    u.avatar = serverAvatar || c.ava;
    u.avatarZoom = c.zoom || 1;              // zoom là luật của file này, server không lưu
    try { if (global.AstroQ && AstroQ.setUser) AstroQ.setUser(u); } catch (e) {}
    return c.id;
  }

  /* ── ĐẨY LÊN SERVER MỘT LẦN, gọi từ trang CÓ token ──
     ⚠️ Gửi kèm `name`: `select.html` ghi cả hai cùng lúc, và một hồ sơ có nhân vật
        mà không có tên thì `dashboard.html` lại chào "Phi hành gia" cho một đứa
        trẻ đã tự đặt tên. Server nhận cả hai trong MỘT lời gọi (PUT /me/profile).
     ⚠️ Không bao giờ ném lỗi, không bao giờ chặn giao diện — cùng hợp đồng với
        `js/progress.js`. Hỏng thì lần mở trang sau thử lại. */
  function syncUp(auth, uid) {
    try {
      if (!auth || !auth.updateProfile || !chosen()) return Promise.resolve(false);
      var stamp = uid ? String(uid) : "";
      var done = "";
      try { done = localStorage.getItem(LS_SYNC) || ""; } catch (e) {}
      if (done && done === stamp) return Promise.resolve(false);

      var u = user() || {};
      var c = byId(get());
      var patch = { character: c.id, avatar: c.ava };
      /* Tên: chỉ gửi khi có thật và trong giới hạn server (24 ký tự — xem
         MeEndpoints.cs). Gửi tên quá dài thì server trả 400 và MẤT LUÔN cả
         nhân vật, vì PUT này là một giao dịch. */
      var nm = String(u.pilotName || u.name || "").trim();
      if (nm && nm.length <= 24) patch.name = nm;

      return auth.updateProfile(patch).then(function (r) {
        if (r && r.ok) { try { localStorage.setItem(LS_SYNC, stamp); } catch (e) {} return true; }
        return false;
      })["catch"](function () { return false; });
    } catch (e) { return Promise.resolve(false); }
  }

  function stampNow(uid) {
    try { localStorage.setItem(LS_SYNC, uid ? String(uid) : ""); } catch (e) {}
  }

  /** Máy này đang giữ một lựa chọn CHƯA từng gửi lên hồ sơ của uid này. */
  function pendingUp(uid) {
    if (!chosen()) return false;
    try { return (localStorage.getItem(LS_SYNC) || "") !== (uid ? String(uid) : ""); }
    catch (e) { return true; }   // localStorage bị chặn → coi như chưa gửi, gửi lại vô hại
  }

  /**
   * Cầu nối HAI CHIỀU. Ba nhánh, và chúng KHÔNG bao giờ giẫm chân nhau:
   *   ① hai bên đã khớp        → không làm gì, chỉ đóng dấu;
   *   ② máy này có lựa chọn CHƯA GỬI → ĐẨY lên (lựa chọn đó mới hơn);
   *   ③ còn lại                → KÉO về (server là nguồn sự thật).
   *
   * ⚠️⚠️ VÌ SAO NHÁNH ② PHẢI ĐỨNG TRƯỚC NHÁNH ③ — chứ không phải "server luôn
   *    thắng". Trẻ vào lại `select.html` đổi nhân vật là chuyện THƯỜNG (thẻ ID là
   *    cửa vào, và `profile.html` cũng dẫn về đó). Trang đó KHÔNG có token nên nó
   *    chỉ ghi được cache; nếu server thắng vô điều kiện thì lượt mở dashboard kế
   *    tiếp sẽ lặng lẽ kéo con vật CŨ về, và trẻ thấy lựa chọn của mình tự hoàn
   *    nguyên mà không có gì báo. Cùng thứ tự ưu tiên `syncDepth()` ở dashboard.html
   *    dùng (`declared()` trước `absorb`).
   * ⚠️ Nhánh ① tồn tại để `hydrateProfile()` (js/firebase-auth.js) vừa kéo hồ sơ về
   *    lúc đăng nhập thì dashboard KHÔNG gửi lại y nguyên cái vừa nhận: dấu
   *    `astroq-char-synced` đã bị `logout()` xoá nên nếu chỉ xét dấu thì nhánh ②
   *    sẽ nổ, tốn một PUT vô nghĩa mỗi lần đăng nhập.
   */
  function sync(auth, uid, serverChar, serverAvatar) {
    var mine = get();
    var theirs = byId(serverChar) ? serverChar : "";
    if (mine && mine === theirs) { stampNow(uid); return Promise.resolve(false); }   // ①
    if (pendingUp(uid)) return syncUp(auth, uid);                                    // ②
    absorb(serverChar, serverAvatar);                                                // ③
    return Promise.resolve(false);
  }

  /** Xoá dấu đã-đồng-bộ = "máy này có lựa chọn mới, chưa gửi". Gọi khi trẻ ĐỔI nhân vật. */
  function touch() { try { localStorage.removeItem(LS_SYNC); } catch (e) {} }

  global.AstroQChars = {
    // Trả bản sao nông: trang nào lỡ sort/đổi mảng thì không làm hỏng trang khác
    all: function () { return CHARACTERS.slice(); },
    byId: byId,
    MYSTERY: MYSTERY,
    avatarOf: avatarOf,
    zoomOf: zoomOf,
    get: get,
    chosen: chosen,
    absorb: absorb,
    syncUp: syncUp,
    sync: sync,
    touch: touch
  };
})(window);
