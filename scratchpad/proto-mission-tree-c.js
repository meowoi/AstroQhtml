/* ==========================================================
   proto-mission-tree-c.js — BẢN MẪU C, dữ liệu GIẢ (chép từ bản A/B).

   C = CƠ CHẾ CỦA B + CÁCH VẼ MỚI.
     · giữ của B: không gấp gì cả · mở trang là tự cuộn tới chặng đang mở ·
       nút nổi "Về chỗ đang chơi" · thanh dính mang tiến độ
     · đổi so với B: **bỏ nhãn chữ cạnh mỗi nút**, cột vòng tròn uốn lượn giữa màn,
       tên chặng chỉ hiện ở bong bóng trên chặng đang mở và trong bảng chi tiết

   ⚠️ Vì sao đổi: chủ dự án báo *"nhiệm vụ sẽ bị căn hết về phía trái, trống hết bên
      phải"* — đúng, và nhãn chữ chính là thứ gây ra. Lý do đầy đủ ghi ở đầu
      `proto-mission-tree-c.css`.

   ⚠️ TÊN CHẶNG KHÔNG BIẾN MẤT, nó chuyển chỗ: `aria-label` của từng nút (trình đọc
      màn hình vẫn đọc đủ), bong bóng trên chặng đang mở, và bảng chi tiết khi chạm.
      Bỏ nhãn mà không có ba chỗ đó thì đúng là lấy đi thông tin.
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
  var SEEN = 0.6;   // ngưỡng "đang nhìn thấy" — DÙNG CHUNG, xem ghi chú ở curInView()

  var q = parseInt((location.search.match(/done=(\d+)/) || [])[1], 10);
  var doneCount = (q >= 0 && q <= STEPS.length) ? q : 0;
  var picked = null, obs = null;

  var reduced = window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

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
  function curNode() { return $("tree").querySelector(".node.now"); }

  /* ───────── Thanh dính + câu dẫn ───────── */
  function paintHead() {
    var n = STEPS.length;
    $("m-ct").textContent = doneCount + " / " + n;
    $("m-fill").style.width = Math.round(doneCount / n * 100) + "%";
    $("lead").textContent =
      doneCount === 0 ? "Bảy chặng khám phá. Chạm vào chặng đang sáng để bắt đầu."
    : doneCount === n ? "Bạn đã đi hết bảy chặng của Trái Đất."
    : "Bạn đã đi " + doneCount + " trong " + n + " chặng.";

    var tt = 0;
    for (var i = 0; i < doneCount; i++) tt += STEPS[i].tt;
    if (doneCount === n) tt += DONE_TT;
    $("bal").textContent = tt;
  }

  /* ───────── Một nút trên đường ─────────
     Không có `.node-lb`. Tên chặng nằm ở `aria-label` (trình đọc màn hình) và ở bong
     bóng của chặng đang mở. */
  function row(i) {
    var s = STEPS[i], st = stateOf(i);
    var bdg = st === "done" ? '<span class="bdg">✓</span>'
            : st === "lock" ? '<span class="bdg">🔒</span>' : "";
    var bub = st === "now"
      ? '<div class="bub" aria-hidden="true"><b>' + s.nm + "</b>" +
        '<span class="go">' + (doneCount === 0 ? "Bắt đầu ở đây →" : "Chơi tiếp →") +
        "</span></div>"
      : "";

    /* ⚠️ CHẶNG CHƯA MỞ THÌ CHẶN HẲN Ở CHÍNH CÁI NÚT (`disabled`), không chặn bằng
       một câu `if` trong hàm xử lý bấm. Chặn bằng `if` thì nút vẫn nhận tiêu điểm
       bàn phím và vẫn báo với trình đọc màn hình rằng nó bấm được — tức là chặn cho
       chuột mà không chặn cho người dùng bàn phím. */
    var off = st === "lock" ? " disabled" : "";

    return '<li class="node ' + st + '" data-i="' + i + '">' +
      '<button class="node-btn" type="button"' + off + ' aria-label="Chặng ' + (i + 1) + ": " + s.nm +
        " — " + (st === "done" ? "đã xong" : st === "now" ? "đang mở" : "chưa mở") + '">' +
        '<span aria-hidden="true">' + s.ic + "</span>" +
        '<span class="num">' + (i + 1) + "</span>" + bdg +
      "</button>" + bub +
    "</li>";
  }

  function paintTree() {
    var html = "";
    for (var i = 0; i < STEPS.length; i++) html += row(i);
    $("tree").innerHTML = html;
    $("finish").hidden = doneCount < STEPS.length;
    /* Câu điều kiện mở chỉ hiện khi THẬT SỰ còn chặng khoá — xong hết mà vẫn treo
       một dòng nói về chặng chưa mở là nói về thứ không còn tồn tại. */
    $("rule").hidden = doneCount >= STEPS.length - 1;
    watchCurrent();
  }

  /* ───────── Tự cuộn tới chặng đang mở ─────────
     ⚠️ Lúc MỞ TRANG thì cuộn tức thì (`behavior:"auto"`), cố ý: một trang tự trôi
        ngay khi vừa mở đọc ra như trang bị lỗi. Chỉ khi trẻ BẤM nút nhảy mới cuộn
        mượt — lúc đó nó là hệ quả của một hành động. */
  function goCurrent(smooth) {
    var el = curNode();
    if (!el) return;
    el.scrollIntoView({ block: "center",
                        behavior: (smooth && !reduced) ? "smooth" : "auto" });
  }

  /* ⚠️ MỘT ĐỊNH NGHĨA "ĐANG NHÌN THẤY" CHO CẢ SẢN PHẨM LẪN PHÉP KIỂM.
        Bản B lúc đầu để phép kiểm đòi nút nằm TRỌN trong khung, còn observer chỉ đòi
        60% — trên desktop một nút lộ 67% thì nút nhảy ẩn (đúng) mà phép kiểm báo
        hỏng. Hai định nghĩa cho một câu hỏi thì sớm muộn có một cái sai. */
  function curInView() {
    var el = curNode();
    if (!el) return false;
    var r = el.getBoundingClientRect(), vh = window.innerHeight || 0;
    var vis = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
    return r.height > 0 && vis / r.height >= SEEN;
  }

  function watchCurrent() {
    if (obs) { obs.disconnect(); obs = null; }
    var el = curNode();
    if (!el) { $("jump").hidden = true; return; }
    obs = new IntersectionObserver(function (ents) {
      var e = ents[0];
      $("jump").hidden = e.isIntersecting;
      $("jump").querySelector(".j-ar").textContent =
        e.boundingClientRect.top > 0 ? "↓" : "↑";
    }, { threshold: SEEN });
    obs.observe(el);
  }

  /* ⚠️ Đo chiều cao THẬT của header rồi gán vào `--top`. Gán cứng là sai ở một khổ
        máy nào đó — header tự xuống 2 hàng trên màn hẹp (bài học `#time-ghost`). */
  function syncTop() {
    var h = $("top").getBoundingClientRect().height;
    document.documentElement.style.setProperty("--top", Math.round(h) + "px");
  }

  /* ───────── Bảng chi tiết — giống hệt A và B ───────── */
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

    /* ⚠️ Không còn nhánh `lock` ở đây: chặng chưa mở KHÔNG mở được bảng nữa
       (chủ dự án chốt 04/08/2026). Điều kiện mở nay nằm ở dòng `#rule` luôn hiển thị
       — đọc được mà không phải chạm vào đâu. */
    if (st === "done") {
      note("Chặng này đã tính thưởng rồi. Chơi lại là để ôn — không nhận thêm Thiên thạch tím hay XP.");
      btn("Chơi lại chặng này", true);
    } else {
      note("");
      btn(doneCount === 0 ? "Bắt đầu nhiệm vụ" : "Chơi chặng này", true);
    }
    $("sheet").hidden = false;
  }
  function note(txt) { var el = $("sh-note"); el.textContent = txt; el.hidden = !txt; }
  function btn(label, on) { var b = $("sh-go"); b.textContent = label; b.disabled = !on; }

  /* ───────── Sự kiện ───────── */
  $("tree").addEventListener("click", function (e) {
    var li = e.target.closest ? e.target.closest(".node") : null;
    if (!li || li.classList.contains("lock")) return;   // chặn hẳn — xem ghi chú ở row()
    openSheet(parseInt(li.dataset.i, 10));
  });

  /* ───────── XONG MỘT CHẶNG: HỎI TIẾP HAY DỪNG ─────────
     Bản mẫu diễn lại cả vòng để bấm thử được: bấm "Chơi chặng này" coi như đã chơi
     xong chặng đó. Trang thật thì hộp này bật ở màn tổng kết của `mission-earth.html`.
     ⚠️ Chơi LẠI một chặng cũ thì KHÔNG hỏi — không có chặng nào vừa mở ra để mà đi
        tiếp, và tiến độ không nhúc nhích. Hỏi ở đó là hỏi một câu vô nghĩa. */
  function finishStep() {
    var i = doneCount;                 // chặng vừa chơi
    var s = STEPS[i];
    doneCount = i + 1;
    paintHead(); paintTree();

    $("af-tag").textContent = "Chặng " + (i + 1) + " / " + STEPS.length;
    $("af-h").textContent = "Xong chặng “" + s.nm + "”!";
    var kv = "";
    if (s.tt) kv += "<span>" + TT_IMG + "+" + s.tt + "</span>";
    kv += "<span>✨ +" + s.xp + " XP</span>";
    if (s.codex) kv += "<span>🗂️ +" + s.codex + " mẫu dữ liệu</span>";
    $("af-kv").innerHTML = kv;

    if (doneCount < STEPS.length) {
      var nx = STEPS[doneCount];
      $("af-ic").textContent = "🎉";
      $("af-p").textContent = "Chặng tiếp theo: “" + nx.nm + "”.";
      $("af-next").textContent = "Chơi tiếp chặng " + pad(doneCount + 1) + " →";
      $("af-next").hidden = false;
      $("af-stop").textContent = "Để lần sau";
    } else {
      /* Xong cả nhiệm vụ thì KHÔNG hỏi nữa — không còn chặng nào để đi tiếp, và đây
         là lúc duy nhất đáng để đưa trẻ đi chỗ khác. */
      $("af-ic").textContent = "🏆";
      $("af-p").textContent = "Bạn đã đi hết bảy chặng của Trái Đất.";
      $("af-next").hidden = true;
      $("af-stop").textContent = "Về bản đồ";
    }
    $("after").hidden = false;
    $("af-next").hidden ? $("af-stop").focus() : $("af-next").focus();
  }
  function pad(n) { return n < 10 ? "0" + n : String(n); }

  $("af-next").addEventListener("click", function () {
    $("after").hidden = true;
    goCurrent(true);
    toast("→ mission-earth.html?step=" + STEPS[doneCount].id + "  (bản mẫu: không điều hướng)");
  });
  $("af-stop").addEventListener("click", function () {
    $("after").hidden = true;
    if (doneCount >= STEPS.length) { location.href = "proto-mission-map.html"; return; }
    goCurrent(true);
    toast("Đã lưu chỗ đang chơi. Lần sau mở lại là vào đúng đây.");
  });

  $("jump").addEventListener("click", function () { goCurrent(true); });

  $("sh-x").addEventListener("click", function () { $("sheet").hidden = true; });
  $("sheet").addEventListener("click", function (e) {
    if (e.target === $("sheet")) $("sheet").hidden = true;
  });
  /* Bấm ra ngoài hộp "tiếp hay dừng" cũng là CHỌN DỪNG — cùng nghĩa với Escape, để
     hai cách đóng không cho ra hai kết quả khác nhau. */
  $("after").addEventListener("click", function (e) {
    if (e.target === $("after")) $("af-stop").click();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (!$("sheet").hidden) { $("sheet").hidden = true; return; }
    /* ⚠️ Escape ở hộp "tiếp hay dừng" = CHỌN DỪNG, không phải "bỏ qua câu hỏi".
       Đóng mà không chọn gì thì trẻ mất luôn màn chúc mừng lẫn đường đi tiếp. */
    if (!$("after").hidden) $("af-stop").click();
  });

  $("sh-go").addEventListener("click", function () {
    var replay = picked < doneCount;
    $("sheet").hidden = true;
    if (replay) {
      toast("Chơi lại chặng “" + STEPS[picked].nm + "” — không nhận thêm thưởng.");
      return;
    }
    finishStep();      // bản mẫu: coi như trẻ vừa chơi xong chặng đang mở
  });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    $("sheet").hidden = true;
    $("after").hidden = true;
    paintHead(); paintTree(); goCurrent(false);
  });

  Array.prototype.forEach.call($("seg").querySelectorAll("button"), function (b) {
    b.classList.toggle("on", parseInt(b.dataset.case, 10) === doneCount);
  });

  window.addEventListener("resize", syncTop);

  /* Bề mặt cho phép kiểm — cùng hình dạng với `window.__treeB`. */
  window.__treeC = {
    get done() { return doneCount; },
    get jumpVisible() { return !$("jump").hidden; },
    get afterOpen() { return !$("after").hidden; },
    curInView: curInView,
    go: goCurrent
  };

  syncTop();
  paintHead();
  paintTree();
  goCurrent(false);
})();
