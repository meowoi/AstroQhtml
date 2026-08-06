/* ==========================================================
   proto-mission-tree-b.js — BẢN B: ĐƯỜNG LIỀN MẠCH (theo Duolingo / Candy Crush).

   Cùng dữ liệu, cùng hàng, cùng bảng chi tiết với bản A. Khác ĐÚNG MỘT cơ chế:

     A — gấp phần đã xong lại        → màn luôn ngắn, nhưng mất cảm giác "đi được xa"
     B — không gấp gì, đường liền mạch → giữ cảm giác đó, bù lại phải có hai thứ
                                        chống lạc: thanh dính + nút nhảy về

   ═══ BA CHI TIẾT LẤY TỪ KHẢO SÁT ═══

   ① TỰ CUỘN TỚI CHẶNG ĐANG MỞ NGAY KHI VÀO TRANG. Đây là thứ làm cho "đường dài"
      không thành gánh nặng: trẻ mở trang ra là đã đứng sẵn ở chỗ cần làm, cái đuôi
      đã xong nằm phía trên để nó tự cuộn lên xem nếu muốn.
      ⚠️ Cuộn KHÔNG mượt ở lần đầu (`behavior:"auto"`): một trang tự trôi ngay khi
         vừa mở đọc ra như trang bị lỗi. Chỉ khi trẻ BẤM nút nhảy thì mới cuộn mượt,
         vì lúc đó nó là hệ quả của một hành động — và `prefers-reduced-motion` thì
         cả hai đều tức thì.

   ② NÚT NỔI "VỀ CHỖ ĐANG CHƠI" chỉ hiện khi chặng đang mở đã ra khỏi khung nhìn.
      Duolingo có đúng nút này. Nó tồn tại VÌ đường dài — tức là bản B tự thừa nhận
      cái giá của mình.

   ③ THANH DÍNH mang TIẾN ĐỘ, không chỉ mang cái tên. Thanh cùng loại của Duolingo bị
      người dùng chê là "không giúp được mấy"; một dải chỉ ghi lại cái tên đã có ở
      tiêu đề trang thì đúng là chỉ chiếm chỗ.

   ⚠️ Cái giá đã được ghi nhận ở Duolingo: cuộn về bài cũ mất ~20 giây. Với 7 chặng
      thì chưa tới mức đó — đó là lý do B đáng thử cho CÂY CHẶNG, còn danh sách 11
      nhiệm vụ thì vẫn nên gấp như bản A.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

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

  var DONE_TT = 100;
  var TT_IMG = '<img src="../img/tt.png" alt="Thiên thạch tím" />';

  var q = parseInt((location.search.match(/done=(\d+)/) || [])[1], 10);
  var doneCount = (q >= 0 && q <= STEPS.length) ? q : 5;   // mặc định 5/7 cho dễ so
  var picked = null;

  var reduced = window.matchMedia &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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

  /* ───────── Thanh dính phải nằm ngay dưới header ─────────
     ⚠️ Đo chiều cao THẬT của `.hub-top` rồi gán vào `--top`. Gán cứng một con số thì
        sai ở màn hẹp — ở đó header tự xuống hai hàng. */
  function syncTop() {
    var h = $("top").getBoundingClientRect().height;
    document.documentElement.style.setProperty("--top", Math.round(h) + "px");
  }

  function paintHead() {
    var n = STEPS.length;
    var pct = Math.round(doneCount / n * 100);
    $("bar-fill").style.width = pct + "%";
    $("m-fill").style.width = pct + "%";
    $("m-ct").textContent = doneCount + " / " + n;
    $("lead").textContent =
      doneCount === 0 ? "Bảy chặng khám phá. Chạm vào chặng đang sáng để bắt đầu."
    : doneCount === n ? "Bạn đã đi hết bảy chặng của Trái Đất."
    : "Bạn đã đi " + doneCount + " trong " + n + " chặng.";

    var tt = 0;
    for (var i = 0; i < doneCount; i++) tt += STEPS[i].tt;
    if (doneCount === n) tt += DONE_TT;
    $("bal").textContent = tt;
  }

  /* ───────── Vẽ cây — KHÔNG GẤP GÌ CẢ ─────────
     Cái đuôi các chặng đã xong được giữ nguyên kích cỡ: ở bản B nó chính là phần
     thưởng, không phải thứ để dọn đi. */
  function paintTree() {
    var html = "";
    for (var i = 0; i < STEPS.length; i++) {
      var s = STEPS[i], st = stateOf(i);
      var lit = (i > 0 && stateOf(i - 1) === "done") ? " lit" : "";
      var bdg = st === "done" ? '<span class="bdg">✓</span>'
              : st === "lock" ? '<span class="bdg">🔒</span>' : "";
      var sub = st === "now"
        ? '<span class="sub">' + (doneCount === 0 ? "Bắt đầu ở đây →" : "Chơi tiếp →") + "</span>"
        : (st === "lock" && i === doneCount + 1)
          ? '<span class="sub">Chặng kế tiếp</span>' : "";

      html += '<li class="node ' + st + lit + '" data-i="' + i + '">' +
        '<button class="node-btn" type="button" aria-label="Chặng ' + (i + 1) + ": " + s.nm + '">' +
          '<span aria-hidden="true">' + s.ic + "</span>" +
          '<span class="num">' + (i + 1) + "</span>" + bdg +
        "</button>" +
        '<div class="node-lb"><b>' + s.nm + "</b>" + sub + "</div>" +
      "</li>";
    }
    $("tree").innerHTML = html;
    $("finish").hidden = doneCount < STEPS.length;
    watchCurrent();
  }

  /* ───────── ① Tự cuộn tới chặng đang mở ───────── */
  function curNode() {
    return $("tree").querySelector(".node.now") ||
           $("tree").querySelector(".node:last-child");
  }
  function goCurrent(smooth) {
    var el = curNode();
    if (!el) return;
    el.scrollIntoView({ block: "center",
                        behavior: (smooth && !reduced) ? "smooth" : "auto" });
  }

  /* ───────── ② Nút nổi: chỉ hiện khi chặng đang mở ra khỏi khung ───────── */
  var obs = null;
  function watchCurrent() {
    if (obs) obs.disconnect();
    var el = curNode();
    $("jump").hidden = true;
    if (!el || !window.IntersectionObserver) return;
    obs = new IntersectionObserver(function (ents) {
      var e = ents[0];
      $("jump").hidden = e.isIntersecting;
      /* Mũi tên phải chỉ ĐÚNG hướng phải cuộn — chỉ xuống trong khi chỗ cần tới nằm
         phía trên là chỉ sai đường, và đó là loại lỗi trẻ không tự sửa được. */
      $("jump").querySelector(".j-ar").textContent =
        e.boundingClientRect.top > 0 ? "↓" : "↑";
    }, { threshold: 0.6 });
    obs.observe(el);
  }

  /* ───────── Bảng chi tiết (giống hệt bản A) ───────── */
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
  function note(t) { var e = $("sh-note"); e.textContent = t; e.hidden = !t; }
  function btn(l, on) { var b = $("sh-go"); b.textContent = l; b.disabled = !on; }

  /* ───────── Sự kiện ───────── */
  $("tree").addEventListener("click", function (e) {
    var li = e.target.closest ? e.target.closest(".node") : null;
    if (li) openSheet(parseInt(li.dataset.i, 10));
  });
  $("jump").addEventListener("click", function () { goCurrent(true); });

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
    $("sheet").hidden = true;
    paintHead(); paintTree(); goCurrent(false);
  });

  Array.prototype.forEach.call($("seg").querySelectorAll("button"), function (b) {
    b.classList.toggle("on", parseInt(b.dataset.case, 10) === doneCount);
  });

  window.addEventListener("resize", syncTop);

  syncTop();
  paintHead();
  paintTree();
  /* Cuộn sau khi bố cục đã ổn định — gọi ngay trong lượt dựng thì chiều cao ảnh/chữ
     chưa xong và nó cuộn tới một vị trí sẽ đổi ngay sau đó. */
  requestAnimationFrame(function () { goCurrent(false); });

  /* Bề mặt cho phép kiểm — cùng khuôn `window.__mission` của trang nhiệm vụ. */
  window.__treeB = {
    get done() { return doneCount; },
    get jumpVisible() { return !$("jump").hidden; },
    /* ⚠️ "Đang nhìn thấy" phải có ĐÚNG MỘT định nghĩa, dùng chung cho cả nút nổi lẫn
       phép kiểm. Bản đầu ở đây đòi hàng nằm TRỌN trong khung, còn `IntersectionObserver`
       chỉ đòi 60% — nên trên màn 1440×960 hàng lộ ra 67% thì nút ẩn (đúng) mà phép
       kiểm lại bảo "không nhìn thấy" và báo hỏng oan. Nay cả hai cùng đọc một con số. */
    SEEN: 0.6,
    curInView: function () {
      var el = curNode(); if (!el) return false;
      var r = el.getBoundingClientRect(), vh = window.innerHeight || 0;
      var vis = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
      return r.height > 0 && vis / r.height >= 0.6;
    }
  };
})();
