/* VÒNG ĐỜI MỘT LƯỢT CHƠI — dùng chung (thêm 16/08/2026).
   ────────────────────────────────────────────────────────────────────────────
   Nó lo đúng phần mà SÁU game đang có đều chép lại y hệt nhau: trừ phí vào lượt ·
   chống trừ hai lần · cộng thưởng ĐÚNG MỘT CHỖ · kỷ lục trong máy · báo việc đã
   làm lên server · dòng "đã cộng n tt" và việc vẽ lại nó khi đổi ngôn ngữ.

   ⚠️⚠️ VÌ SAO TÁCH: đếm được ở `game-catch.html`, `game-dodge.html`,
      `game-defender.html`, `game-racer.html`, `game-maze.html`,
      `game-constellation.html` — cả sáu đều có một bản `startRound`/`endRound`/
      `onFinishGame`/`paintPaid`/`readBest`/`saveBest` gần như trùng khớp. Đó là
      ~90 dòng × 6, và là chỗ chứa **ba cái bẫy đã trả giá thật**:
        · Enter/Space vừa xác nhận vừa kích hoạt nút đang có tiêu điểm ⇒ **trừ phí
          HAI LẦN** (ARCADE-01, 25/07/2026);
        · cộng Thiên thạch tím từng viên trong lượt ⇒ ví tăng rồi bị kéo về khi
          server không đồng ý (bài học quiz + đọc bài, 30/07/2026);
        · dòng "đã cộng n tt" do JS sinh nên `applyTexts` không với tới ⇒ **không
          đổi tiếng** khi bấm VI/EN (ARCADE-01).
      Sửa một cái ở một chỗ là năm chỗ kia vẫn sai. Nay một chỗ.

   ⚠️ SÁU GAME CŨ CHƯA CHUYỂN SANG ĐÂY, CỐ Ý. Chúng đang chạy tốt và có bộ đo
      riêng (`shoot_dodge`, `play_maze`, `play_catch`, `play_racer`…); viết lại
      cả sáu trong cùng một lượt là đổi thứ không hỏng. Cùng đường đi đã dùng cho
      `css/game-shell.css` (dựng cho 2 game rồi mới lan ra 6) và `css/page-shell.css`.
      **Game MỚI thì dùng file này, đừng chép lại vòng đời.**

   ⚠️ KHÔNG lo phần VẼ và phần LUẬT CHƠI — đó là việc của từng trang. File này
      không biết game là canvas hay là bảng chọn.

   Cách dùng:
       var RUN = AstroQGameRun.create({
         game: "survival", cost: 3, t: t,
         onStart: function(){ ...dựng lại màn chơi... },
       });
       RUN.start();                                  // bấm "Bắt đầu"
       RUN.finish({ score: 7, seconds: 92, meteors: 4 });
*/
(function (global) {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  function num(v) { var n = Math.floor(v || 0); return n > 0 ? n : 0; }

  function create(opt) {
    opt = opt || {};
    var game    = String(opt.game || "");
    var cost    = num(opt.cost);
    var t       = opt.t || function (k) { return k; };
    var bestKey = opt.bestKey || ("astroq-" + game + "-best");

    /* "idle" chưa chơi · "play" đang chơi · "over" đã xong. Trang tự thêm trạng
       thái riêng nếu cần (ví dụ "paused"), file này chỉ cần biết CÓ đang chơi
       hay không để chặn trừ phí hai lần. */
    var state = "idle";
    var best = readBest();
    var lastPaid = 0;

    function readBest() {
      try { var n = parseInt(localStorage.getItem(bestKey), 10); return isNaN(n) ? 0 : n; }
      catch (e) { return 0; }
    }
    function saveBest(v) {
      if (!(v > best)) return false;
      best = v;
      try { localStorage.setItem(bestKey, String(v)); } catch (e) {}
      return true;
    }

    function paintBalance() {
      var el = $("bal");
      if (el) el.textContent = Economy.getAsteroids();
    }
    function bumpGem() {
      var g = $("gem");
      if (!g) return;
      g.classList.remove("bump"); void g.offsetWidth; g.classList.add("bump");
    }

    function hideAllOv() {
      var ovs = document.querySelectorAll(".ov");
      for (var i = 0; i < ovs.length; i++) ovs[i].classList.remove("show");
    }
    function showOv(id) { var el = $(id); if (el) el.classList.add("show"); }

    /** Chưa đủ tiền thì nói rõ cần bao nhiêu / đang có bao nhiêu, và dẫn sang Quiz. */
    function showNeed() {
      hideAllOv();
      var b = $("need-body");
      if (b) {
        b.textContent = t("need_body")
          .replace("{cost}", cost).replace("{bal}", Economy.getAsteroids());
      }
      showOv("ov-need");
    }

    /* ⚠️ DÒNG "ĐÃ CỘNG N TT" DO JS SINH nên `AstroQ.applyTexts` không với tới nó.
       Phải gọi lại `paintPaid()` trong `applyLang` của trang — nếu không thì đổi
       VI/EN ở bảng kết quả là dòng này đứng nguyên tiếng cũ. Đây là lỗi thật đã
       xảy ra ở ARCADE-01. */
    function paintPaid() {
      var el = $("paid");
      if (!el) return;
      if (lastPaid > 0) {
        el.innerHTML = t("paid_line")
          .replace("{n}", "<b>" + lastPaid + "</b>")
          .replace("{tt}", '<img class="tt-inline" src="img/tt.png" alt="' +
                            (global.AstroQ ? AstroQ.esc(t("tt_name")) : "tt") + '" />');
        el.style.display = "";
      } else {
        el.textContent = "";
        el.style.display = "none";
      }
    }

    return {
      /** Bắt đầu một lượt: kiểm ví → trừ phí → gọi `onStart` của trang. */
      start: function () {
        /* ⚠️ CHẶN TRỪ PHÍ HAI LẦN. Enter/Space vừa là "xác nhận" vừa kích hoạt
           nút đang có tiêu điểm, nên một cú Enter có thể gọi hàm này hai lần. */
        if (state === "play") return false;
        if (Economy.getAsteroids() < cost) { showNeed(); return false; }
        if (document.activeElement && document.activeElement.blur) {
          document.activeElement.blur();
        }
        /* Phí do SERVER quyết (nó tra `Wallet.Fees`), client chỉ gửi TÊN GAME —
           cho client gửi số tiền thì ai cũng chơi miễn phí bằng cách gửi 0. */
        Economy.spend(game);
        paintBalance(); bumpGem();
        lastPaid = 0;
        hideAllOv();
        state = "play";
        if (opt.onStart) opt.onStart();
        return true;
      },

      /**
       * Chốt một lượt. `res` = { score, seconds, meteors }.
       * → { paid, best, newBest } để trang vẽ bảng kết quả.
       */
      finish: function (res) {
        res = res || {};
        state = "over";
        var score   = num(res.score);
        var seconds = num(res.seconds);
        var mined   = num(res.meteors);

        var newBest = saveBest(score);

        /* ⚠️ CHỖ DUY NHẤT CỘNG THƯỞNG VÀO VÍ CHÍNH. Trong lượt, Thiên thạch tím
           chỉ nằm ở ví tạm; cộng từng viên thì trẻ thấy ví tăng rồi bị kéo về
           khi server không đồng ý. */
        if (mined > 0) { Economy.addAsteroids(mined); bumpGem(); }
        paintBalance();
        lastPaid = mined;

        /* Bắn-rồi-quên: bảng kết quả phải hiện NGAY, không đứng chờ mạng. Server
           tự quyết XP và huy hiệu — client không gửi XP lên (xem js/progress.js). */
        if (global.AstroQProgress) {
          AstroQProgress.game({ game: game, score: score,
                                seconds: seconds, meteors: mined });
        }
        paintPaid();
        return { paid: mined, best: best, newBest: newBest };
      },

      state:        function () { return state; },
      setState:     function (s) { state = s; },
      best:         function () { return best; },
      cost:         function () { return cost; },
      paid:         function () { return lastPaid; },
      paintPaid:    paintPaid,
      paintBalance: paintBalance,
      bumpGem:      bumpGem,
      hideAllOv:    hideAllOv,
      showOv:       showOv,
      showNeed:     showNeed
    };
  }

  global.AstroQGameRun = { create: create };
})(window);
