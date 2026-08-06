/* ==========================================================
   proto-planet.js — BẢN MẪU: một hành tinh có 11 nhiệm vụ thì bố cục thế nào.

   ⚠️⚠️ NHIỆM VỤ 02–11 LÀ TÊN GIẢ, CHỈ ĐỂ XEM BỐ CỤC. Chúng không có trong
   `Services/Missions.cs`, không có nội dung, không có trang chơi. Trang thật chỉ vẽ
   những nhiệm vụ server trả về — dự án có luật: đừng hứa một nhiệm vụ chưa tồn tại.

   ═══ CÂU TRẢ LỜI VỀ BỐ CỤC ═══

   ① BA MÀN, MỖI MÀN MỘT TẦNG. Với 11 nhiệm vụ thì không thể nhét cả nhiệm vụ lẫn
      chặng vào một màn: 11 × 7 = 77 hàng.
        BẢN ĐỒ    → chọn NƠI            (proto-mission-map.html)
        HÀNH TINH → chọn NHIỆM VỤ       (màn này)
        NHIỆM VỤ  → chọn CHẶNG          (proto-mission-tree.html)
      Đây cũng đúng luồng chủ dự án đã mô tả: bản đồ → click hành tinh → mission tree
      → chọn nhiệm vụ.
      ⚠️ Thêm một tầng là thêm một cú chạm. Bù lại bằng lối tắt **"Chơi tiếp"** ở
         bản đồ — nhảy thẳng vào chặng đang dở, bỏ qua cả hai tầng giữa. Trẻ quay lại
         hôm sau đi ĐÚNG MỘT cú chạm.

   ② MỘT LUẬT ĐẾM ĐƯỢC: MỖI MÀN TỐI ĐA ~6 HÀNG, BẤT KỂ CÓ BAO NHIÊU NHIỆM VỤ.
      Cùng một cơ chế gấp đã dùng cho chặng, nay dùng cho nhiệm vụ:
        · đã xong        → gấp thành MỘT dải (vẫn hiện đủ chấm, vẫn bấm mở được)
        · đang chơi      → hàng đủ + thanh tiến độ + lời mời
        · 2 cái kế tiếp  → hàng nhỏ (để trẻ thấy đường đi tiếp)
        · phần còn lại   → gấp thành "còn N nhiệm vụ nữa"
      Nhờ vậy chiều cao KHÔNG tăng theo số nhiệm vụ: 11 nhiệm vụ và 3 nhiệm vụ cho ra
      cùng một màn. Đo được ở phép kiểm `shot_proto_planet.py`.

   ③ VÌ SAO KHÔNG DÙNG LƯỚI THẺ (như `games.html`). Lưới 11 thẻ trên điện thoại là
      11 thẻ cao xếp dọc — vẫn dài, chỉ khác là mất luôn thứ tự trước–sau. Mà thứ tự
      chính là thứ một hành trình cần nói.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };

  /* ⚠️ CHỈ NHIỆM VỤ 01 LÀ THẬT (khớp `Missions.All`). Mười cái còn lại là TÊN GIẢ. */
  var MISSIONS = [
    { ic:"🌍", nm:"Hành Tinh Xanh",          steps:7, real:true },
    { ic:"🌊", nm:"Đại dương sâu thẳm",      steps:6 },
    { ic:"🌋", nm:"Núi lửa và mảng kiến tạo", steps:5 },
    { ic:"💨", nm:"Bầu khí quyển",           steps:6 },
    { ic:"💧", nm:"Vòng tuần hoàn nước",     steps:5 },
    { ic:"🌲", nm:"Rừng và oxy",             steps:6 },
    { ic:"🧊", nm:"Băng ở hai cực",          steps:5 },
    { ic:"⛈️", nm:"Bão và thời tiết",        steps:6 },
    { ic:"🧭", nm:"Từ trường Trái Đất",      steps:5 },
    { ic:"🌗", nm:"Ngày và đêm",             steps:4 },
    { ic:"🧑‍🚀", nm:"Con người và Trái Đất",   steps:6 }
  ];

  var FOLD_FROM = 2;   // gấp phần đã xong khi có từ 2 nhiệm vụ trở lên
  var PREVIEW   = 2;   // số nhiệm vụ chưa mở được hiện ra; phần còn lại gấp

  var doneCount = 0;
  var openDone = false, openRest = false;

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
    /* Nhiệm vụ thật thì "chưa mở"; nhiệm vụ chưa có nội dung thì "sắp ra mắt" —
       hai câu khác nhau, đừng gộp. */
    return MISSIONS[i].real ? "lock" : "soon";
  }

  /* Số chặng đã xong của nhiệm vụ đang chơi — bản mẫu gieo một con số cho đẹp;
     trang thật đọc `missions.<id>.steps.length` từ server. */
  function curStepsDone() { return Math.min(5, MISSIONS[doneCount] ? MISSIONS[doneCount].steps - 2 : 0); }

  function row(i, mini) {
    var m = MISSIONS[i], st = stateOf(i);
    var lit = (i > 0 && stateOf(i - 1) === "done") ? " lit" : "";
    var bdg = st === "done" ? '<span class="bdg">✓</span>'
            : st === "lock" ? '<span class="bdg">🔒</span>' : "";
    var extra = "";

    if (st === "now") {
      var d = curStepsDone();
      extra = '<span class="mini-bar"><i style="width:' + Math.round(d / m.steps * 100) + '%"></i></span>' +
              '<span class="sub">' + (d ? "Chơi tiếp — chặng " + (d + 1) + "/" + m.steps
                                        : "Bắt đầu — " + m.steps + " chặng") + " →</span>";
    } else if (st === "lock" && i === doneCount + 1) {
      extra = '<span class="sub">Nhiệm vụ kế tiếp</span>';
    } else if (st === "soon") {
      extra = '<span class="sub">Sắp ra mắt</span>';
    }

    return '<li class="node ' + st + lit + (mini ? " mini" : "") + '" data-i="' + i + '">' +
      '<button class="node-btn" type="button" aria-label="Nhiệm vụ ' + (i + 1) + ": " + m.nm + '">' +
        '<span aria-hidden="true">' + m.ic + "</span>" +
        '<span class="num">' + (i + 1) + "</span>" + bdg +
      "</button>" +
      '<div class="node-lb"><b>' + m.nm + "</b>" + extra + "</div>" +
      /* Mũi chỉ ở mép phải — xem ghi chú "HÀNG THẺ TRẢI HẾT BỀ RỘNG" ở
         proto-planet.css. Nó vừa lấp mép phải, vừa nói "hàng này mở ra được". */
      '<span class="chev" aria-hidden="true">›</span>' +
    "</li>";
  }

  function foldRow(id, cls, dots, title, sub, open) {
    var d = "";
    for (var i = 0; i < dots.length; i++) d += '<i class="dot">' + dots[i] + "</i>";
    return '<li class="fold ' + cls + '" id="' + id + '">' +
      '<button class="fold-btn" type="button" aria-expanded="' + (open ? "true" : "false") + '">' +
        (d ? '<span class="dots">' + d + "</span>" : "") +
        '<span class="fold-tx"><b>' + title + "</b>" +
          (sub ? '<span class="sub">' + sub + "</span>" : "") + "</span>" +
        '<span class="chev" aria-hidden="true">' + (open ? "▴" : "▾") + "</span>" +
      "</button></li>";
  }

  function paintHead() {
    var n = MISSIONS.length;
    $("bar-fill").style.width = Math.round(doneCount / n * 100) + "%";
    $("lead").textContent =
      doneCount === 0 ? "Trái Đất có " + n + " nhiệm vụ. Bắt đầu từ nhiệm vụ đang sáng."
    : doneCount === n ? "Bạn đã xong cả " + n + " nhiệm vụ ở Trái Đất."
    : "Xong " + doneCount + " trong " + n + " nhiệm vụ. Nhiệm vụ đang sáng là nhiệm vụ tiếp theo.";
    $("bal").textContent = doneCount * 235;   // bản mẫu: 235 tt mỗi nhiệm vụ
  }

  function paintList() {
    var n = MISSIONS.length, html = "", i;

    /* ── Phần ĐÃ XONG ── */
    if (doneCount >= FOLD_FROM && !openDone) {
      /* ⚠️ CHỈ HIỆN TỐI ĐA 6 CHẤM. `.dots` là `flex:none` nên nó không co lại —
         11 chấm × 32px = 352px, rộng hơn cả khung 330px của điện thoại và làm TRÀN
         NGANG (đo được dư 62px). Sáu chấm đã đủ nói "bạn đi được kha khá rồi";
         con số chính xác thì dòng chữ ngay bên cạnh đang nói. */
      var dots = [];
      for (i = 0; i < Math.min(doneCount, 6); i++) dots.push(MISSIONS[i].ic);
      html += foldRow("fold-done", "", dots, doneCount + " nhiệm vụ đã xong",
                      "Chạm để xem lại", false);
    } else {
      for (i = 0; i < doneCount; i++) html += row(i, false);
      if (doneCount >= FOLD_FROM)
        html += foldRow("fold-done", "up", [], "Thu gọn phần đã xong", "", true);
    }

    if (doneCount < n) {
      html += row(doneCount, false);                       // đang chơi — hàng đủ

      /* ── Vài cái kế tiếp + phần còn lại gấp lại ──
         Đây là chỗ giữ cho màn KHÔNG dài thêm khi số nhiệm vụ tăng. */
      var restStart = Math.min(doneCount + 1 + PREVIEW, n);
      for (i = doneCount + 1; i < restStart; i++) html += row(i, true);

      var rest = n - restStart;
      if (rest > 0) {
        if (openRest) {
          for (i = restStart; i < n; i++) html += row(i, true);
          html += foldRow("fold-rest", "rest up", [], "Thu gọn", "", true);
        } else {
          var rd = [];
          for (i = restStart; i < Math.min(restStart + 6, n); i++) rd.push(MISSIONS[i].ic);
          html += foldRow("fold-rest", "rest", rd, "Còn " + rest + " nhiệm vụ nữa",
                          "Chạm để xem cả hành trình", false);
        }
      }
    }

    $("list").innerHTML = html;
    $("finish").hidden = doneCount < n;
  }

  /* ───────── Sự kiện ───────── */
  $("list").addEventListener("click", function (e) {
    var f = e.target.closest ? e.target.closest(".fold") : null;
    if (f) {
      if (f.id === "fold-rest") openRest = !openRest; else openDone = !openDone;
      paintList();
      return;
    }
    var li = e.target.closest ? e.target.closest(".node") : null;
    if (!li) return;
    var i = parseInt(li.dataset.i, 10), st = stateOf(i), m = MISSIONS[i];

    /* Nhiệm vụ THẬT và đã mở → sang cây chặng. Còn lại thì nói rõ vì sao chưa vào
       được — im lặng khi bấm thì trẻ chỉ tưởng mình bấm trượt. */
    if (m.real && (st === "done" || st === "now")) {
      /* ⚠️ Trỏ sang bản C — từ 04/08/2026 đó là bản cây chặng dùng thật (bản A và B
         giữ lại chỉ để đặt cạnh nhau mà so). Hai đường vào cùng một nhiệm vụ mà
         dẫn tới hai màn khác nhau thì trẻ tưởng là hai nhiệm vụ. */
      location.href = "proto-mission-tree-c.html?done=" + (st === "done" ? 7 : curStepsDone());
      return;
    }
    toast(st === "soon" ? "🚧 “" + m.nm + "” chưa có nội dung — đây là tên giả để xem bố cục."
                        : "🔒 Cần xong “" + MISSIONS[i - 1].nm + "” trước đã.");
  });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    openDone = openRest = false;
    paintHead(); paintList();
  });

  paintHead();
  paintList();
})();
