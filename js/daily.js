/* js/daily.js — VIỆC HÔM NAY + CHUỖI NGÀY: chỗ duy nhất khai TÊN, và bảng vẽ dùng chung.
   ------------------------------------------------------------------------------
   PHÂN CÔNG y như js/badges.js và js/ranks.js: **server giữ MỐC và TIỀN, client giữ
   TÊN**. Mốc ("đúng 5 câu"), tiền thưởng, luật ân hạn đều nằm ở
   `AstroqSV/Services/Daily.cs`; ở đây chỉ có chữ song ngữ + chỗ dẫn tới.

   ⚠️ MỌI CON SỐ TRÊN BẢNG ĐỀU LẤY TỪ SERVER. Đừng gõ "5 câu" hay "+6 tt" vào chuỗi
      tiếng Việt — đó là hai nơi cùng giữ một con số, và bản ở client sẽ nói con số cũ
      vào đúng ngày server đổi độ khó. Chuỗi ở đây dùng token `{n}` rồi thay bằng
      `goal` server trả về.

   ⚠️ VIỆC LẠ THÌ HIỆN CHÍNH ID, KHÔNG VỠ TRANG. Server thêm việc thứ tư mà client
      chưa kịp có tên thì `info()` trả về một tên tạm — đúng luật đã dùng cho huy hiệu
      ("thiếu tên thì trang hiện chính id"). Có phép kiểm đối chiếu hai bên.

   ⚠️⚠️ HAI DÒNG GIẢI THÍCH LUẬT ĐÃ BỎ 19/08/2026 (chủ dự án: *"trẻ tự hiểu"*) —
      `.dl-sub` ("hôm nay đã được tính vào chuỗi · tuần này còn n ngày nghỉ") và
      `.dl-rule` (đoạn luật ở chân bảng). Bảng nay chỉ còn 🔥 số ngày + kỷ lục + ba
      hàng việc. Điều ⑤ ở `Daily.cs` vì thế **không còn được thoả ở tầng giao diện**;
      xem ghi chú tại chỗ khai nó để biết cái gì còn giữ và cái gì đã mất.
      ⛔ Đừng "chữa" bằng cách nhét luật vào tooltip hay một nút "?": đó là cùng một
         đoạn chữ, chỉ khó đọc hơn.

   ⚠️⚠️ BA THỨ TUYỆT ĐỐI KHÔNG ĐƯỢC THÊM VÀO ĐÂY (xem năm điều kiện ở Daily.cs):
      · **đồng hồ đếm ngược** dưới mọi hình thức ("còn 4 giờ", "hết hạn lúc 00:00").
        Server cố ý không trả về mốc hết hạn nào, nên thêm được thì phải TỰ TÍNH nửa
        đêm ở client — tức là dựng lại đúng thứ vừa quyết định bỏ.
      · **thông báo / lời giục** ("đừng để mất chuỗi!"). Bảng chỉ nói khi trẻ tự mở.
      · **màu đỏ và dấu than cho việc chưa xong.** Việc chưa làm không phải một lỗi.
*/
(function (global) {
  "use strict";

  /* Tên việc + chỗ dẫn tới. `href` là thứ biến bảng này từ một danh sách chấm công
     thành một cửa đi: chạm vào việc chưa xong là tới đúng nơi làm được nó. */
  var T = {
    quiz: {
      ic: "⚡", href: "quiz.html",
      vi: { nm: "Làm xong {n} lượt Quiz đạt", sub: "Đấu Trường Kiến Thức" },
      en: { nm: "Pass {n} Quiz round",        sub: "Knowledge Arena" }
    },
    play: {
      ic: "🎮", href: "games.html",
      vi: { nm: "Chơi {n} lượt ở Khu Huấn Luyện", sub: "Sáu mini-game" },
      en: { nm: "Play {n} mini-game round",       sub: "Six mini-games" }
    },
    correct: {
      ic: "🎯", href: "quiz.html",
      vi: { nm: "Trả lời đúng {n} câu hỏi", sub: "Cộng dồn cả ngày" },
      en: { nm: "Answer {n} questions right", sub: "Counted across the day" }
    }
  };

  /* ⚠️ CỐ Ý KHÔNG có nhãn bảng / tiêu đề ở đây. Hai chuỗi đó gắn bằng `data-i18n` nên
     phải nằm trong từ điển CỦA TRANG (`check_pages` mục [1] đòi mọi khoá `data-i18n`
     có ở cả `vi` và `en` của trang) — khai cả hai nơi là hai bản sao của một chuỗi.
     Ở đây chỉ giữ phần chữ do JS sinh ra. */
  var TXT = {
    vi: {
      streak: "Chuỗi {n} ngày",
      streak0: "Chưa có chuỗi nào",
      best: "Kỷ lục {n} ngày",
      got: "Đã nhận {n} / {t}",
      done: "xong",
      unknown: "Chưa đọc được việc hôm nay nên bảng đang hiện dấu “—”."
    },
    en: {
      streak: "{n}-day streak",
      streak0: "No streak yet",
      best: "Best {n} days",
      got: "Earned {n} / {t}",
      done: "done",
      unknown: "Today's tasks could not be loaded, so the board shows “—”."
    }
  };

  function L(lang) { return lang === "en" ? "en" : "vi"; }
  function tx(lang, k) { var d = TXT[L(lang)]; return d[k] != null ? d[k] : k; }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /** Tên + icon + chỗ dẫn của một việc. Việc lạ → tên tạm là chính id. */
  function info(id, lang, goal) {
    var e = T[id];
    var g = goal == null ? "" : goal;
    if (!e) return { ic: "•", href: null, nm: String(id), sub: "" };
    var d = e[L(lang)] || e.vi;
    return {
      ic: e.ic, href: e.href,
      nm: String(d.nm).replace("{n}", g),
      sub: d.sub
    };
  }

  /* Ảnh nhỏ của Thiên thạch tím — dùng lại đúng hàm chung để `alt` đổi theo ngôn ngữ. */
  function ttImg() {
    return (global.AstroQ && AstroQ.ttImg)
      ? AstroQ.ttImg()
      : '<img src="img/tt.png" alt="" />';
  }

  /**
   * Vẽ cả bảng vào `box`.
   * @param snap dữ liệu `daily` server trả về, hoặc null = chưa đọc được.
   */
  function paint(box, snap, lang) {
    if (!box) return;
    var lg = L(lang);

    /* ── Chưa đọc được → dấu "—" và nói rõ lý do, KHÔNG hiện 0 ──
       "0/1 việc" là một lời khẳng định SAI về việc hôm nay của trẻ; cùng nguyên tắc
       với dấu "—" ở missions.html và achievements.html. */
    if (!snap) {
      box.innerHTML =
        '<div class="dl-head"><span class="dl-fire" aria-hidden="true">🔥</span>' +
        '<span class="dl-cur">—</span></div>' +
        '<p class="dl-note">' + esc(tx(lg, "unknown")) + "</p>";
      return;
    }

    var s = snap.streak || {};

    var head =
      '<div class="dl-head">' +
        '<span class="dl-fire" aria-hidden="true">🔥</span>' +
        '<span class="dl-cur">' +
          esc(s.cur > 0 ? tx(lg, "streak").replace("{n}", s.cur) : tx(lg, "streak0")) +
        "</span>" +
        (s.best > 0
          ? '<span class="dl-best">' + esc(tx(lg, "best").replace("{n}", s.best)) + "</span>"
          : "") +
      "</div>";

    var rows = (snap.tasks || []).map(function (task) {
      var i = info(task.id, lg, task.goal);
      var cls = "dl-row" + (task.done ? " is-done" : "");
      var meter = task.done
        ? '<span class="dl-ok">' + esc(tx(lg, "done")) + "</span>"
        : '<span class="dl-n">' + task.current + "/" + task.goal + "</span>";
      var body =
        '<span class="dl-ic" aria-hidden="true">' + (task.done ? "✅" : i.ic) + "</span>" +
        '<span class="dl-txt"><b>' + esc(i.nm) + "</b>" +
          (i.sub ? "<span>" + esc(i.sub) + "</span>" : "") + "</span>" +
        meter +
        '<span class="dl-tt">+' + task.tt + " " + ttImg() + "</span>";
      /* Việc CHƯA xong thì cả hàng là một đường đi tới nơi làm được nó; việc đã xong
         thì không còn gì để dẫn tới nên là một hàng thường (không phải một cái link
         bấm vào chẳng để làm gì). */
      return (!task.done && i.href)
        ? '<a class="' + cls + '" href="' + i.href + '">' + body + "</a>"
        : '<div class="' + cls + '">' + body + "</div>";
    }).join("");

    var foot =
      '<p class="dl-got">' +
        esc(tx(lg, "got").replace("{n}", snap.gotTt).replace("{t}", snap.totalTt)) +
        " " + ttImg() +
      "</p>";

    box.innerHTML = head + '<div class="dl-list">' + rows + "</div>" + foot;
  }

  global.AstroQDaily = { ids: Object.keys(T), info: info, text: tx, paint: paint };
})(window);
