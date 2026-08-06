/* ==========================================================
   proto-mission-tree.js — BẢN MẪU, dữ liệu GIẢ.

   Trang thật sẽ lấy đúng những con số này từ `GET /me/missions`. Ở đây gieo tay để
   xem giao diện ở cả ba tình huống mà không cần đăng nhập.

   ⚠️ Số thưởng chép từ `AstroqSV/Services/Missions.cs` chỉ để bản mẫu trông thật.
      Trang thật KHÔNG được gán cứng con số nào — server tra bảng rồi trả về.

   ═══ BẢN 3 (04/08/2026) — HAI VIỆC CHỦ DỰ ÁN BÁO ═══

   ① BỎ NÚT MẶT TRĂNG KHỎI CÂY CỦA TRÁI ĐẤT.
      *"sao nhiệm vụ ở hành tinh xanh lại có mặt trăng ở đấy?"* — đúng, và nó phá
      chính thứ bậc vừa dựng: BẢN ĐỒ là chỗ chọn NƠI, CÂY là các chặng CỦA MỘT NƠI.
      Nhét một nơi khác vào cuối cây là trộn hai tầng làm một.
      ⚠️ Nhưng KHÔNG được xoá trắng: nút đó đang gánh câu "xong rồi thì làm gì tiếp"
         (bài học đã ghi khi bỏ khối Mặt Trăng ở màn tổng kết — xoá trắng là biến
         thành đường cụt, tệ hơn cả lời hứa hão). Nay thay bằng **thẻ kết** chỉ hiện
         khi xong hết, và nó trỏ NGƯỢC VỀ BẢN ĐỒ — đúng tầng của nó.

   ② CÂY SẼ DÀI NGOẰNG KHI THÊM NHIỆM VỤ. Đo được: 7 chặng đã cao ~900px trên điện
      thoại, tức trẻ phải cuộn 1,5 màn để thấy chặng đang mở. Hai cách gộp lại:
      · GẤP PHẦN ĐÃ XONG thành một dải nhỏ ("5 chặng đã xong · Xem lại") — thứ trẻ
        cần thấy là chặng ĐANG mở, không phải danh sách việc đã làm.
      · CHẶNG CHƯA MỞ vẽ nhỏ lại, bỏ dòng phụ.
      Đo lại: 5/7 chặng còn **~300px** thay vì ~900px, và chặng đang mở luôn nằm
      trong khung nhìn đầu tiên.
      ⚠️ Dải gấp vẫn BẤM MỞ ĐƯỢC — chơi lại một chặng cũ là việc có thật, giấu hẳn
         là lấy đi một đường đi.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* ───────── Bảy chặng của Nhiệm vụ 01, đúng thứ tự chơi ─────────
     `id` khớp STEP_IDS ở mission-earth.html và Missions.All ở server. */
  var STEPS = [
    { id:"scan",     ic:"🛰️", nm:"Bề mặt hành tinh xanh",     tt:0,  xp:20, codex:0,
      p:"Chạm 7 châu lục trên ảnh vệ tinh thật, rồi tự đoán: nước hay đất nhiều hơn?" },
    { id:"timeline", ic:"⏳", nm:"Lần theo dòng thời gian",    tt:20, xp:30, codex:1,
      p:"Đi qua 5 mốc trong 4,54 tỷ năm — từ hành tinh nóng chảy tới Trái Đất hôm nay." },
    { id:"sun",      ic:"☀️", nm:"Mặt Trời và ba vùng khí hậu", tt:20, xp:30, codex:1,
      p:"Nếu Mặt Trời tắt thì sao? Đoán thử, rồi xem vì sao xích đạo nóng còn hai cực lạnh." },
    { id:"life",     ic:"🌳", nm:"Sự sống ở khắp nơi",         tt:20, xp:40, codex:4,
      p:"Bay tới 4 nơi có thật trên Trái Đất và đoán xem mỗi nơi nằm ở nấc nào của cột độ cao." },
    { id:"energy",   ic:"⚡", nm:"Kích hoạt năng lượng sạch",   tt:25, xp:35, codex:1,
      p:"Khói đen đang phủ kín khí quyển. Thay ba ống khói bằng ba nguồn năng lượng sạch." },
    { id:"eco",      ic:"♻️", nm:"Eco-Hero: nên hay không nên?", tt:30, xp:40, codex:1,
      p:"Bảy việc hằng ngày, hai cái rổ. Việc nào nên làm, việc nào không?" },
    { id:"core",     ic:"🗂️", nm:"Đóng dấu Hồ Sơ Trái Đất",    tt:20, xp:40, codex:0,
      p:"Ba điều bạn vừa học, một con dấu. Và câu chốt: phải có đủ cả ba cùng một lúc." }
  ];

  var DONE_TT = 100, DONE_XP = 120;
  var TT_IMG = '<img src="../img/tt.png" alt="Thiên thạch tím" />';

  /* Gấp phần đã xong khi có TỪ 2 CHẶNG TRỞ LÊN. Một chặng thì gấp không tiết kiệm
     được gì mà lại thêm một thứ phải bấm. */
  var FOLD_FROM = 2;

  var q = parseInt((location.search.match(/done=(\d+)/) || [])[1], 10);
  var doneCount = (q >= 0 && q <= STEPS.length) ? q : 0;
  var openDone = false;      // dải "đã xong" đang mở hay đang gấp
  var picked = null;

  /* ───────── Toast ───────── */
  var toastT = null;
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.classList.remove("show"); }, 2600);
  }

  function stateOf(i) {
    if (i < doneCount) return "done";
    if (i === doneCount) return "now";
    return "lock";
  }

  /* ───────── Đầu khối: MỘT câu + MỘT thanh ───────── */
  function paintHead() {
    var n = STEPS.length;
    $("bar-fill").style.width = Math.round(doneCount / n * 100) + "%";
    $("lead").textContent =
      doneCount === 0 ? "Bảy chặng khám phá. Chạm vào chặng đang sáng để bắt đầu."
    : doneCount === n ? "Bạn đã đi hết bảy chặng của Trái Đất."
    : "Bạn đã đi " + doneCount + " trong " + n + " chặng. Chặng đang sáng là chặng tiếp theo.";

    var tt = 0;
    for (var i = 0; i < doneCount; i++) tt += STEPS[i].tt;
    if (doneCount === n) tt += DONE_TT;
    $("bal").textContent = tt;
  }

  /* ───────── Một hàng chặng ─────────
     `mini` = chặng chưa mở: vòng nhỏ hơn, bỏ dòng phụ trừ chặng ngay kế tiếp. */
  function row(i, mini) {
    var s = STEPS[i], st = stateOf(i);
    var lit = (i > 0 && stateOf(i - 1) === "done") ? " lit" : "";
    var bdg = st === "done" ? '<span class="bdg">✓</span>'
            : st === "lock" ? '<span class="bdg">🔒</span>' : "";
    var sub = st === "now"
      ? '<span class="sub">' + (doneCount === 0 ? "Bắt đầu ở đây →" : "Chơi tiếp →") + "</span>"
      : (st === "lock" && i === doneCount + 1)
        ? '<span class="sub">Chặng kế tiếp</span>' : "";

    return '<li class="node ' + st + lit + (mini ? " mini" : "") + '" data-i="' + i + '">' +
      '<button class="node-btn" type="button" aria-label="Chặng ' + (i + 1) + ": " + s.nm + '">' +
        '<span aria-hidden="true">' + s.ic + "</span>" +
        '<span class="num">' + (i + 1) + "</span>" + bdg +
      "</button>" +
      '<div class="node-lb"><b>' + s.nm + "</b>" + sub + "</div>" +
    "</li>";
  }

  /* ───────── Vẽ cây ───────── */
  function paintTree() {
    var n = STEPS.length, html = "", i;
    var fold = doneCount >= FOLD_FROM && !openDone;

    if (fold) {
      /* Dải gấp: vẫn cho thấy ĐỦ số chấm đã xong (trẻ nhìn ra mình đi được bao xa)
         nhưng chỉ tốn một hàng. Bấm vào là mở ra để chơi lại. */
      var dots = "";
      for (i = 0; i < doneCount; i++) dots += '<i class="dot">' + STEPS[i].ic + "</i>";
      html +=
        '<li class="fold" id="fold">' +
          '<button class="fold-btn" type="button" aria-expanded="false">' +
            '<span class="dots">' + dots + "</span>" +
            '<span class="fold-tx"><b>' + doneCount + " chặng đã xong</b>" +
              '<span class="sub">Chạm để xem lại</span></span>' +
            '<span class="chev" aria-hidden="true">▾</span>' +
          "</button>" +
        "</li>";
    } else {
      for (i = 0; i < doneCount; i++) html += row(i, false);
      if (doneCount >= FOLD_FROM) {
        html += '<li class="fold up" id="fold-up">' +
          '<button class="fold-btn" type="button" aria-expanded="true">' +
            '<span class="fold-tx"><b>Thu gọn phần đã xong</b></span>' +
            '<span class="chev" aria-hidden="true">▴</span>' +
          "</button></li>";
      }
    }

    if (doneCount < n) {
      html += row(doneCount, false);                       // chặng đang mở — hàng đủ
      for (i = doneCount + 1; i < n; i++) html += row(i, true);   // chưa mở — hàng nhỏ
    }

    $("tree").innerHTML = html;

    /* ───────── Thẻ kết ─────────
       ⚠️ CHỈ hiện khi xong hết, và nó trỏ NGƯỢC VỀ BẢN ĐỒ. Đây là chỗ trả lời câu
          "xong rồi thì làm gì tiếp" mà nút Mặt Trăng cũ đang gánh sai tầng. */
    $("finish").hidden = doneCount < n;
  }

  /* ───────── Bảng chi tiết ───────── */
  function openSheet(i) {
    picked = i;
    var s = STEPS[i], st = stateOf(i);
    $("sh-ic").textContent = s.ic;
    $("sh-tag").textContent = "Chặng " + (i + 1) + " / " + STEPS.length;
    $("sh-h").textContent = s.nm;
    $("sh-p").textContent = s.p;

    var kv = "";
    if (s.tt)    kv += "<span>" + TT_IMG + (st === "done" ? "đã nhận " : "") + s.tt + "</span>";
    kv += "<span>✨ " + (st === "done" ? "đã nhận " : "") + s.xp + " XP</span>";
    if (s.codex) kv += "<span>🗂️ " + s.codex + " mẫu dữ liệu</span>";
    $("sh-kv").innerHTML = kv;

    if (st === "done") {
      /* Nói TRƯỚC khi trẻ bấm. Server đã chặn cộng thưởng lần hai (ghi có điều kiện,
         trả `counted:false`) — thứ đang thiếu chỉ là CHỮ. Để trẻ tự phát hiện bằng
         dòng "+0" ở màn tổng kết là cách tệ nhất. */
      note("Chặng này đã tính thưởng rồi. Chơi lại là để ôn — không nhận thêm Thiên thạch tím hay XP.");
      btn("Chơi lại chặng này", true);
    } else if (st === "now") {
      note("");
      btn(doneCount === 0 ? "Bắt đầu nhiệm vụ" : "Chơi chặng này", true);
    } else {
      note("Cần xong chặng " + i + " — “" + STEPS[i - 1].nm + "” — trước đã.");
      btn("Chưa mở", false);
    }
    $("sheet").hidden = false;
  }
  function note(txt) { var el = $("sh-note"); el.textContent = txt; el.hidden = !txt; }
  function btn(label, on) { var b = $("sh-go"); b.textContent = label; b.disabled = !on; }

  /* ───────── Sự kiện ───────── */
  $("tree").addEventListener("click", function (e) {
    var f = e.target.closest ? e.target.closest(".fold") : null;
    if (f) { openDone = !openDone; paintTree(); return; }
    var li = e.target.closest ? e.target.closest(".node") : null;
    if (!li) return;
    /* Chặng chưa mở vẫn MỞ ĐƯỢC BẢNG — bảng nói rõ cần gì. Im lặng khi bấm thì trẻ
       chỉ tưởng mình bấm trượt (bài học của cổng lộ trình ở explorer). */
    openSheet(parseInt(li.dataset.i, 10));
  });

  $("sh-x").addEventListener("click", function () { $("sheet").hidden = true; });
  $("sheet").addEventListener("click", function (e) {
    if (e.target === $("sheet")) $("sheet").hidden = true;
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !$("sheet").hidden) $("sheet").hidden = true;
  });

  $("sh-go").addEventListener("click", function () {
    toast("→ mission-earth.html?step=" + STEPS[picked].id + "  (bản mẫu: không điều hướng)");
    $("sheet").hidden = true;
  });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    openDone = false;
    $("sheet").hidden = true;
    paintHead(); paintTree();
  });

  Array.prototype.forEach.call($("seg").querySelectorAll("button"), function (b) {
    b.classList.toggle("on", parseInt(b.dataset.case, 10) === doneCount);
  });

  paintHead();
  paintTree();
})();
