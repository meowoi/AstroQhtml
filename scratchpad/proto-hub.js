/* ==========================================================
   proto-hub.js — BẢN MẪU Trung Tâm Nhiệm Vụ. Dữ liệu GIẢ.

   ⚠️⚠️ ĐỒNG HỒ ĐẾM LÙI TỪ SỐ GIÂY SERVER GỬI VỀ — TUYỆT ĐỐI KHÔNG ĐỌC ĐỒNG HỒ MÁY.
   Trong cả file này không có một lời gọi `Date` nào, và đó là điều kiện của tính năng
   chứ không phải sở thích: nếu "còn 7 giờ" tính bằng giờ của máy thì **đổi giờ hệ
   thống là làm mới việc hàng ngày** — mà đây là app cho trẻ 8–15, chúng sẽ thử.
   Trang thật: `GET /me/daily` trả `secondsLeft`, client chỉ trừ dần mỗi giây; mở lại
   trang là hỏi lại server. Có phép kiểm quét file này đòi 0 lời gọi `Date`.

   ⚠️ HAI NHÓM DƯỚI CHƯA CÓ BACKEND. `POST /me/progress` chỉ nhận
      `quiz`/`game`/`lesson`/`planet`; `Wallet` không có mục thưởng `daily` và phép
      kiểm `test_wallet` đã chứng minh `reason` lạ trả **400**. Nên đây là bản mẫu để
      chốt CHỖ ĐẶT, không phải để chơi. Dải `.warn` trên trang nói đúng câu đó.

   ⚠️ VIỆC HÀNG NGÀY KHÔNG ĐƯỢC KHOÁ THEO TIẾN ĐỘ. Không có `lock`, không hỏi cổng lộ
      trình, không hỏi cấp độ — với trẻ mới thì một việc hàng ngày bị khoá là khoá
      vĩnh viễn ở đúng ngày đầu tiên (cùng loại lỗi 7 mẫu vật `planet:*` suýt mắc).
      Vì thế `DAILY` cố ý chỉ có hai trạng thái: chưa làm và đã xong.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var TT_IMG = '<img src="../img/tt.png" alt="Thiên thạch tím" />';

  /* Bảy chặng của Nhiệm vụ 01 — chỉ dùng để viết dòng "Chơi tiếp" cho đúng tên. */
  var STEP_NM = ["Bề mặt hành tinh xanh", "Lần theo dòng thời gian",
                 "Mặt Trời và ba vùng khí hậu", "Sự sống ở khắp nơi",
                 "Kích hoạt năng lượng sạch", "Eco-Hero: nên hay không nên?",
                 "Đóng dấu Hồ Sơ Trái Đất"];
  var STEP_IC = ["🛰️", "⏳", "☀️", "🌳", "⚡", "♻️", "🗂️"];

  /* ── Việc hàng ngày: đều là việc app THẬT SỰ CÓ ──
     ⚠️ Đừng khai một việc chưa tồn tại (bài học `js/specimens.js`: "đừng viết Mở khoá
        tại Mission 02"). Ba việc dưới đều nối được vào thứ đang chạy: Quiz, một chặng
        nhiệm vụ, và mini-game. */
  var DAILY = [
    { ic:"⚡", nm:"Làm một lượt Quiz đạt",      sub:"Đúng ít nhất 3/5 câu", tt:15, xp:20, ok:true  },
    { ic:"🌍", nm:"Chơi một chặng nhiệm vụ",    sub:"Chặng nào cũng được",  tt:10, xp:15, ok:false },
    { ic:"🎮", nm:"Chơi một lượt ở Khu Huấn Luyện", sub:"Game nào cũng được", tt:10, xp:15, ok:false }
  ];

  var EVENTS = [
    { ic:"☄️", nm:"Mưa sao băng Perseid",  sub:"Ghé 3 hành tinh trong tuần này", tt:60, xp:80 }
  ];

  /* Server gửi số giây còn lại; client chỉ trừ dần. */
  var daySec = 7 * 3600 + 12 * 60 + 5;      // còn 7 giờ 12 phút 05 tới lượt đổi mới
  var evSec  = 2 * 86400 + 4 * 3600 + 30 * 60;

  var STEPS_N = STEP_NM.length;
  var q = parseInt((location.search.match(/done=(\d+)/) || [])[1], 10);
  var doneCount = (q >= 0 && q <= STEPS_N) ? q : 0;
  var hasEvent = true;

  var toastT = null;
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.classList.remove("show"); }, 2600);
  }

  function pad(n) { return n < 10 ? "0" + n : String(n); }

  /* "còn 7:12:05" · "còn 2 ngày 4 giờ" — dưới một ngày thì đếm tới từng giây (sắp hết
     thì trẻ cần biết chính xác), trên một ngày thì nói ngày–giờ (đếm giây cho một mốc
     hai ngày nữa là một dãy số nhảy liên tục mà không ai dùng để làm gì). */
  function fmt(sec) {
    if (sec <= 0) return "đã hết";
    if (sec >= 86400) {
      var d = Math.floor(sec / 86400), h = Math.floor((sec % 86400) / 3600);
      return "còn " + d + " ngày " + h + " giờ";
    }
    var hh = Math.floor(sec / 3600), mm = Math.floor((sec % 3600) / 60), ss = sec % 60;
    return "còn " + hh + ":" + pad(mm) + ":" + pad(ss);
  }

  /* ───────── Lối tắt "Chơi tiếp" ─────────
     ⚠️ Chỉ hiện khi THẬT SỰ đang dở. Chưa bắt đầu thì chưa có gì để "tiếp"; xong hết
        rồi thì nó trỏ vào một chặng không tồn tại. */
  function paintResume() {
    var on = doneCount > 0 && doneCount < STEPS_N;
    $("resume").hidden = !on;
    if (!on) return;
    $("r-nm").textContent = STEP_NM[doneCount];
    $("resume").querySelector(".r-ic").textContent = STEP_IC[doneCount];
    $("r-sub").textContent = "Trái Đất · chặng " + pad(doneCount + 1) + " / " + STEPS_N;
  }

  function paintMain() {
    $("main-m").textContent = doneCount >= STEPS_N ? "Trái Đất: 7/7 chặng"
                            : "Trái Đất: " + doneCount + "/" + STEPS_N + " chặng";
    $("map-sub").textContent = doneCount >= STEPS_N
      ? "Xong Trái Đất. Điểm đến sau sẽ mở khi có nhiệm vụ."
      : "Chọn nơi để tới. Trái Đất đang mở.";
    var tt = 0, i;
    for (i = 0; i < doneCount; i++) tt += [0, 20, 20, 20, 25, 30, 20][i];
    if (doneCount >= STEPS_N) tt += 100;
    for (i = 0; i < DAILY.length; i++) if (DAILY[i].ok) tt += DAILY[i].tt;
    $("bal").textContent = tt;
  }

  function taskRow(t, cls, done) {
    var rw = "";
    if (t.tt) rw += "<span>" + TT_IMG + (done ? "đã nhận " : "+") + t.tt + "</span>";
    rw += "<span>✨ " + (done ? "đã nhận " : "+") + t.xp + " XP</span>";
    return '<li class="task ' + cls + (done ? " ok" : "") + '">' +
      '<button class="task-btn" type="button"' + (done ? " disabled" : "") +
        ' aria-label="' + t.nm + (done ? " — đã xong" : "") + '">' +
        '<span class="t-ic" aria-hidden="true">' + t.ic + "</span>" +
        '<span class="t-b"><b>' + t.nm + "</b>" +
          '<span class="sub">' + (done ? "Đã xong hôm nay" : t.sub) + "</span>" +
          '<span class="t-rw">' + rw + "</span>" +
        "</span>" +
        '<span class="chev" aria-hidden="true">' + (done ? "✓" : "›") + "</span>" +
      "</button></li>";
  }

  function paintDaily() {
    var html = "", left = 0;
    for (var i = 0; i < DAILY.length; i++) {
      html += taskRow(DAILY[i], "", DAILY[i].ok);
      if (!DAILY[i].ok) left++;
    }
    $("daily").innerHTML = html;
    /* Câu chân nói ra LUẬT, không nói ra lời khen. Trẻ cần biết bao giờ đổi mới. */
    $("day-foot").textContent = left === 0
      ? "Xong cả " + DAILY.length + " việc hôm nay. Lượt mới sẽ có sau khi đồng hồ về 0."
      : "Còn " + left + " việc. Ba việc mới sẽ thay chỗ khi đồng hồ về 0.";
  }

  function paintEvents() {
    $("ev-sec").hidden = !hasEvent;
    if (!hasEvent) return;
    var html = "";
    for (var i = 0; i < EVENTS.length; i++) html += taskRow(EVENTS[i], "ev", false);
    $("events").innerHTML = html;
  }

  function tick() {
    if (daySec > 0) daySec--;
    if (evSec > 0) evSec--;
    $("day-m").textContent = fmt(daySec);
    if (hasEvent) $("ev-m").textContent = fmt(evSec);
  }

  /* ───────── Sự kiện ───────── */
  $("r-go").addEventListener("click", function () {
    location.href = "proto-mission-tree-c.html?done=" + doneCount;
  });

  $("daily").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".task-btn") : null;
    if (!b || b.disabled) return;
    toast("→ việc hàng ngày chưa có backend (bản mẫu: không điều hướng)");
  });
  $("events").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".task-btn") : null;
    if (!b || b.disabled) return;
    toast("→ sự kiện chưa có backend (bản mẫu: không điều hướng)");
  });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    paintResume(); paintMain();
  });

  $("seg-ev").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    hasEvent = b.dataset.ev === "1";
    paintEvents();
  });

  /* Bề mặt cho phép kiểm */
  window.__hub = {
    get done() { return doneCount; },
    get daySec() { return daySec; },
    get resumeOn() { return !$("resume").hidden; },
    get eventOn() { return !$("ev-sec").hidden; }
  };

  paintResume(); paintMain(); paintDaily(); paintEvents();
  tick();
  setInterval(tick, 1000);
})();
