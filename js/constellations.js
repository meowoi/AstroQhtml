/* ============================================================
   constellations.js — 4 chòm sao, tên song ngữ. CHỖ DUY NHẤT khai báo tên.

   `key` PHẢI khớp `cons.key` trong mảng `SKY` của game-constellation.html, vì đó
   là khoá dùng ở CẢ ba nơi: `PROGRESS.consts` trên server, `astroq-constellation-best`
   trong máy, và điều kiện `const:<key>` của Services/Specimens.cs.

   ⚠️ Bản đầu của achievements.html dùng TÊN TIẾNG VIỆT làm khoá ("Đại Hùng") nên
   bộ sưu tập luôn hiện 0/4 với người chơi thật. Đừng lặp lại: khoá là id.

   Tách ra file riêng (29/07/2026) khi trang Kho Mẫu Vật cần tên chòm sao thứ ba —
   copy 4 dòng dữ liệu sang trang thứ ba là chắc chắn có ngày ba bên lệch nhau.

     <script src="js/constellations.js"></script>
     AstroQConsts.all()  ·  AstroQConsts.name("orion", "vi")   → "Lạp Hộ"
     AstroQConsts.localBests()          → { <key>: giây } của CHÍNH trẻ đang chơi
     AstroQConsts.saveLocalBest(k, s)   → true nếu là kỷ lục mới

   ⚠️⚠️ KỶ LỤC TRONG MÁY ĐÓNG DẤU `uid`, VÀ ĐÓ LÀ BẮT BUỘC KỂ TỪ 22/08/2026.
      `achievements.html` nay GỘP kỷ lục trong máy với `PROGRESS.consts` của server
      (để chòm vừa ghép không biến mất cho tới khi tải lại trang — chủ dự án báo
      đúng lỗi đó). Gộp mà không đóng dấu uid thì trên máy dùng chung, bộ sưu tập
      của đứa trước sẽ hiện ra cho đứa sau. Đóng dấu thì có CẢ HAI.
   ⚠️ Bản ghi CŨ là một object phẳng `{ <key>: giây }` (không có `uid`). Vẫn đọc
      được — trước lượt này mỗi máy chỉ có một trẻ, nên coi nó là của trẻ đang
      dùng; ghi lần sau sẽ tự đóng dấu. Không có đường lùi này thì mọi người chơi
      cũ mất bộ sưu tập trong máy trong im lặng.
   ============================================================ */
(function (global) {
  "use strict";

  var CONSTS = [
    { key: "ursa-major", vi: "Đại Hùng",  en: "Ursa Major" },
    { key: "cassiopeia", vi: "Thiên Hậu", en: "Cassiopeia" },
    { key: "orion",      vi: "Lạp Hộ",    en: "Orion" },
    { key: "scorpius",   vi: "Bọ Cạp",    en: "Scorpius" }
  ];

  var LS_BEST = "astroq-constellation-best";

  function uidNow() {
    try {
      var u = global.AstroQ && AstroQ.getUser ? AstroQ.getUser() : null;
      return u && u.uid ? String(u.uid) : "";
    } catch (e) { return ""; }
  }

  /** Kỷ lục trong máy CỦA TRẺ ĐANG CHƠI. Của uid khác → trả về rỗng. */
  function localBests() {
    var raw;
    try { raw = JSON.parse(localStorage.getItem(LS_BEST) || "null"); }
    catch (e) { return {}; }
    if (!raw || typeof raw !== "object") return {};
    /* Bản ghi cũ: object phẳng, không có `uid`. Coi là của trẻ đang dùng. */
    if (!raw.best) {
      if (raw.uid != null) return {};          // có `uid` mà không có `best` = rác
      return raw;
    }
    if (raw.uid !== uidNow()) return {};
    return (raw.best && typeof raw.best === "object") ? raw.best : {};
  }

  /**
   * Ghi kỷ lục mới nếu nhanh hơn.
   * ⚠️ CẮT bớt chứ không làm tròn: làm tròn lên thì lượt 4,95s lưu thành 5,0 và
   *    bảng kết quả hiện "Thời gian 0:04 · Kỷ lục 0:05" — kỷ lục tệ hơn cả lượt
   *    vừa chơi, trông như lỗi tính điểm.
   */
  function saveLocalBest(key, secs) {
    var b = localBests(), cur = b[key];
    if (cur != null && Number(cur) <= secs) return false;
    b[key] = Math.floor(secs * 10) / 10;
    try { localStorage.setItem(LS_BEST, JSON.stringify({ uid: uidNow(), best: b })); }
    catch (e) {}
    return true;
  }

  global.AstroQConsts = {
    all: function () { return CONSTS.slice(); },
    LS_BEST: LS_BEST,
    localBests: localBests,
    saveLocalBest: saveLocalBest,
    count: CONSTS.length,
    /** Chòm sao lạ (dữ liệu cũ) → trả chính key, không vỡ trang. */
    name: function (key, lang) {
      for (var i = 0; i < CONSTS.length; i++) {
        if (CONSTS[i].key === key) return lang === "en" ? CONSTS[i].en : CONSTS[i].vi;
      }
      return key;
    }
  };
})(window);
