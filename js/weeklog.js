/* js/weeklog.js — NHẬT KÝ TUẦN: SO VỚI CHÍNH MÌNH, KHÔNG SO VỚI AI KHÁC.
   ------------------------------------------------------------------------------
   Mục A2 của `docs/proposals/2026-08-12-de-xuat-hap-dan-cho-tre-8-15.md`: từ ~11 tuổi
   ganh đua mới thành thứ vui, nhưng **so với chính mình theo thời gian** là dạng an
   toàn nhất — và dữ liệu đã có sẵn ở nhật ký sự kiện.

   ⚠️⚠️ TUYỆT ĐỐI KHÔNG BAO GIỜ SO VỚI TRẺ KHÁC. Không thứ hạng, không phần trăm
      "giỏi hơn bao nhiêu bạn", không trung bình cộng của người khác. Đề xuất đã bác
      bảng xếp hạng ở mục 5 và đây là chỗ dễ nhất để nó len vào: server **không có**
      route nào trả dữ liệu của trẻ khác, nên thêm được là phải dựng cả một đường mới —
      đừng dựng. Có phép kiểm quét file này tìm chữ mang nghĩa xếp hạng.

   ⚠️ GIẢM KHÔNG TÔ ĐỎ, và không có dấu than nào. Đây là nhật ký học tập của một đứa
      trẻ đọc về chính nó; đỏ đọc ra thành "em kém đi rồi". Cùng luật đã chốt cho
      `parent.html` (*"xu hướng giảm KHÔNG tô đỏ"*) và cho bảng việc hằng ngày.

   ⚠️ TUẦN TRƯỚC RỖNG THÌ KHÔNG SO. "Tăng 76 điểm" so với một tuần không có dữ liệu là
      một con số BỊA, và nó nằm đúng chỗ dễ tin nhất. Bài học này đã trả giá ở
      `parent.html` ngày 09/08/2026.

   ⚠️ MẪU SỐ SỐ NGÀY LÀ `days`, KHÔNG PHẢI 7. Tuần đăng ký bị cắt còn 2 ngày mà in
      "1/7" là cách đọc sai mà cả việc cắt tuần sinh ra để tránh (xem Services/Report.cs).

   ⚠️ `accuracy === null` KHÁC 0%. null = chưa làm câu nào; 0% = làm mà sai hết. In 0%
      cho một đứa trẻ không làm bài nào là một lời khẳng định sai về nó.

   TÊN GAME KHÔNG NẰM Ở ĐÂY — trang truyền vào qua `opts.gameName(key)`. Bảng tên game
   hiện đang ở TỪNG TRANG (`GAMES` của games.html, `rec_*` của profile.html), nên khai
   thêm một bản thứ ba ở đây là chắc chắn có ngày ba bản nói ba tên. Việc gom chúng về
   một `js/games-catalog.js` là một đợt dọn riêng — ghi ở CLAUDE.md.
*/
(function (global) {
  "use strict";

  var TXT = {
    vi: {
      d_days: "Số ngày có học", d_correct: "Câu trả lời đúng",
      d_games: "Lượt chơi", d_xp: "XP nhận được",
      up: "nhiều hơn {n}", down: "ít hơn {n}", same: "như tuần trước",
      first: "Tuần trước chưa có gì để so — tuần này là mốc đầu tiên của bạn.",
      empty: "Tuần này chưa ghi được hoạt động nào. Làm một việc là nó xuất hiện ở đây.",
      pre: "Tuần này nằm trước ngày bạn bắt đầu, nên chưa có gì để ghi.",
      partial: "Tuần đầu của bạn, tính từ ngày bắt đầu nên chỉ có {n} ngày.",
      acc: "Độ chính xác", acc_prev: "tuần trước {n}%", acc_none: "chưa làm câu nào",
      fly: "Thời gian bay", min: "{n} phút",
      best_h: "Điểm cao nhất tuần này",
      best_tie: "bằng kỷ lục của bạn",
      best_none: "Tuần này chưa chơi lượt nào có điểm.",
      more: "Xem chi tiết", less: "Thu lại",
      since: "Nhật ký bắt đầu ghi từ {d}."
    },
    en: {
      d_days: "Days with activity", d_correct: "Correct answers",
      d_games: "Game rounds", d_xp: "XP earned",
      up: "{n} more", down: "{n} fewer", same: "same as last week",
      first: "There is no earlier week to compare with — this one is your first marker.",
      empty: "Nothing recorded this week yet. Do one thing and it shows up here.",
      pre: "This week is before you started, so there is nothing to record.",
      partial: "Your first week, counted from the day you started — {n} days.",
      acc: "Accuracy", acc_prev: "last week {n}%", acc_none: "no questions yet",
      fly: "Flight time", min: "{n} min",
      best_h: "Best score this week",
      best_tie: "matches your record",
      best_none: "No scored rounds this week yet.",
      more: "See details", less: "Hide details",
      since: "The log starts on {d}."
    }
  };

  /** Mốc bắt đầu ghi nhật ký. Trước ngày này mọi tuần đều rỗng, và trang phải NÓI
      THẬT điều đó thay vì vẽ một loạt số 0 — xem Services/Report.cs. */
  var SINCE = "2026-08-09";

  function L(l) { return l === "en" ? "en" : "vi"; }
  function tx(l, k) { var d = TXT[L(l)]; return d[k] != null ? d[k] : k; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function num(n, lang) {
    return Number(n || 0).toLocaleString(L(lang) === "en" ? "en-US" : "vi-VN");
  }
  /* ⚠️ HAI NHÁNH PHẢI THẬT SỰ KHÁC NHAU. Bản đầu của tôi viết `p[2]/p[1]/p[0]` cho CẢ
     HAI ngôn ngữ — vừa là mã chết trông như đang làm việc gì, vừa in ra `09/08/2026`
     cho người đọc tiếng Anh, mà chuỗi đó đọc ra **hai ngày khác nhau** tuỳ người
     (9 tháng 8 hay 8 tháng 9). Dự án đã chốt bốn dạng viết cho ngày ra mắt vì đúng lý
     do này (xem khối `index.html` ở CLAUDE.md mục 2): EN dùng tên tháng. */
  var MON_EN = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  function dmy(iso, lang) {
    var p = String(iso || "").split("-");
    if (p.length !== 3) return String(iso || "");
    if (L(lang) === "en") {
      var mi = parseInt(p[1], 10) - 1;
      var mon = MON_EN[mi] || p[1];
      return parseInt(p[2], 10) + " " + mon + " " + p[0];      // 9 Aug 2026
    }
    return p[2] + "/" + p[1] + "/" + p[0];                      // 09/08/2026
  }

  /**
   * Một dòng so sánh. `prev` là null khi KHÔNG có gì để so (tuần trước rỗng) —
   * lúc đó KHÔNG vẽ phần chênh lệch, chứ không vẽ "▲ 0".
   */
  function deltaHtml(cur, prev, lang) {
    if (prev == null) return "";
    var d = (cur || 0) - (prev || 0);
    if (d === 0) return '<span class="wl-d wl-same">= ' + esc(tx(lang, "same")) + "</span>";
    /* ⚠️ Nhánh GIẢM dùng class `wl-down` — và `wl-down` KHÔNG được tô đỏ ở CSS.
       Mũi nhọn chỉ để đọc được hướng, không để phán xét. */
    var up = d > 0;
    var key = up ? "up" : "down";
    return '<span class="wl-d ' + (up ? "wl-up" : "wl-down") + '">' +
           (up ? "▲ " : "▼ ") +
           esc(tx(lang, key).replace("{n}", num(Math.abs(d), lang))) + "</span>";
  }

  function row(label, value, cur, prev, lang) {
    return '<div class="wl-row"><span class="wl-k">' + esc(label) + "</span>" +
           '<span class="wl-v">' + esc(value) + "</span>" +
           deltaHtml(cur, prev, lang) + "</div>";
  }

  /**
   * Vẽ nhật ký tuần.
   * @param data  phản hồi `GET /me/report`, hoặc null = chưa đọc được.
   * @param opts  { lang, gameName(key)->string, senior:bool, onToggle() }
   */
  function paint(box, data, opts) {
    if (!box) return;
    opts = opts || {};
    var lang = L(opts.lang);
    var gname = opts.gameName || function (k) { return k; };

    if (!data || !data.current) {
      box.innerHTML = '<p class="wl-note">—</p>';
      return;
    }

    var c = data.current, p = data.previous || {};
    var life = data.lifetime || {};

    /* Cả tuần nằm TRƯỚC ngày bắt đầu → một câu KHÁC HẲN "chưa ghi được gì". Nói nhầm
       câu là đổ cho đứa trẻ một tuần nó chưa tồn tại. */
    if (c.days === 0) {
      box.innerHTML = '<p class="wl-note">' + esc(tx(lang, "pre")) + "</p>" +
                      '<p class="wl-since">' + esc(tx(lang, "since").replace("{d}", dmy(SINCE, lang))) + "</p>";
      return;
    }
    if (c.empty) {
      box.innerHTML = '<p class="wl-note">' + esc(tx(lang, "empty")) + "</p>" +
                      '<p class="wl-since">' + esc(tx(lang, "since").replace("{d}", dmy(SINCE, lang))) + "</p>";
      return;
    }

    /* Tuần trước rỗng ⇒ mọi phần chênh lệch để null. KHÔNG so với 0: "tăng 24 câu"
       so với một tuần không có dữ liệu là một con số bịa. */
    var cmp = !p.empty && p.days > 0;
    var pv = function (k) { return cmp ? (p[k] || 0) : null; };

    var head = "";
    if (!cmp) head += '<p class="wl-note">' + esc(tx(lang, "first")) + "</p>";
    if (c.partial) {
      head += '<p class="wl-note">' +
              esc(tx(lang, "partial").replace("{n}", c.days)) + "</p>";
    }

    // Mẫu số là `c.days`, KHÔNG phải 7 — xem ghi chú đầu file.
    var basic =
      row(tx(lang, "d_days"), c.activeDays + "/" + c.days, c.activeDays, pv("activeDays"), lang) +
      row(tx(lang, "d_correct"), num(c.quizCorrect, lang), c.quizCorrect, pv("quizCorrect"), lang) +
      row(tx(lang, "d_games"), num(c.games, lang), c.games, pv("games"), lang) +
      row(tx(lang, "d_xp"), num(c.xp, lang), c.xp, pv("xp"), lang);

    /* ─── Chi tiết ───
       `senior` chỉ quyết định MỞ SẴN hay không; nút luôn có ở cả hai bậc. Bậc tuổi
       không được KHOÁ gì — luật đã chốt ở js/depth.js. */
    var accTxt = c.accuracy == null ? tx(lang, "acc_none") : c.accuracy + "%";
    var accSub = (cmp && p.accuracy != null)
      ? ' <span class="wl-sub">(' + esc(tx(lang, "acc_prev").replace("{n}", p.accuracy)) + ")</span>"
      : "";
    var mins = Math.round((c.gameSeconds || 0) / 60);

    var bests = c.bests || {};
    var lifeB = life.bests || {};
    var bkeys = Object.keys(bests).sort(function (a, b) { return bests[b] - bests[a]; });
    var bestHtml = bkeys.length
      ? bkeys.map(function (k) {
          /* ⚠️ "BẰNG kỷ lục", KHÔNG PHẢI "kỷ lục MỚI". Điểm tuần này bằng kỷ lục cả đời
             thì chỉ chắc chắn được rằng nó BẰNG — kỷ lục đó có thể đã lập từ tuần
             trước và tuần này chỉ chạm lại. Nói "mới" là một suy luận không có căn cứ
             trong dữ liệu. */
          var tie = lifeB[k] != null && bests[k] >= lifeB[k];
          return '<div class="wl-brow"><span class="wl-bk">' + esc(gname(k)) + "</span>" +
                 '<span class="wl-bv">' + num(bests[k], lang) + "</span>" +
                 (tie ? '<span class="wl-tie">' + esc(tx(lang, "best_tie")) + "</span>" : "") +
                 "</div>";
        }).join("")
      : '<p class="wl-note">' + esc(tx(lang, "best_none")) + "</p>";

    var detail =
      '<div class="wl-row"><span class="wl-k">' + esc(tx(lang, "acc")) + "</span>" +
        '<span class="wl-v">' + esc(accTxt) + "</span>" + accSub + "</div>" +
      row(tx(lang, "fly"), tx(lang, "min").replace("{n}", num(mins, lang)),
          null, null, lang) +
      '<div class="wl-bh">' + esc(tx(lang, "best_h")) + "</div>" + bestHtml;

    box.innerHTML =
      head +
      '<div class="wl-list">' + basic + "</div>" +
      '<button class="wl-more" type="button" id="wl-toggle" aria-expanded="' +
        (opts.senior ? "true" : "false") + '" aria-controls="wl-detail">' +
        esc(tx(lang, opts.senior ? "less" : "more")) + "</button>" +
      '<div class="wl-detail" id="wl-detail"' + (opts.senior ? "" : " hidden") + ">" +
        detail + "</div>" +
      '<p class="wl-since">' +
        esc(tx(lang, "since").replace("{d}", dmy(SINCE, lang))) + "</p>";

    var btn = box.querySelector("#wl-toggle");
    var det = box.querySelector("#wl-detail");
    if (btn && det) {
      btn.addEventListener("click", function () {
        var open = det.hidden;
        det.hidden = !open;
        btn.setAttribute("aria-expanded", open ? "true" : "false");
        btn.textContent = tx(lang, open ? "less" : "more");
      });
    }
  }

  global.AstroQWeekLog = { paint: paint, text: tx, since: SINCE };
})(window);
