/* ============================================================
   js/brag.js — "CHO BỐ MẸ XEM": một thẻ thành tích dựng NGAY TRONG MÁY.

   Nạp như script thường (sau js/ui-common.js):
     <script src="js/brag.js"></script>
     AstroQBrag.open({ tag, title, sub, badge, lines:[{ic,k,v}], note })

   ⚠️⚠️ KHÔNG GỬI GÌ RA NGOÀI, VÀ ĐÓ LÀ TOÀN BỘ LÝ DO NÓ TỒN TẠI.
   Nhu cầu **kết nối** là nhu cầu astroQ thoả kém nhất (đo được: 0 tính năng xã hội),
   nhưng với trẻ 8–15 thì chat / kết bạn / nội dung do người dùng đăng là cả một hạng
   mục an toàn và pháp lý riêng. Thẻ này lấy phần lớn giá trị của "khoe" mà **không
   mở cửa đó**: nó vẽ bằng canvas trong chính trang, và đối tượng người xem là **bố mẹ
   đang ngồi cạnh**.
     · KHÔNG tải lên đâu cả · KHÔNG có URL chia sẻ · KHÔNG gọi mạng.
     · KHÔNG dùng `navigator.share`: cửa đó đưa tệp sang ứng dụng khác của hệ điều
       hành, tức dữ liệu của một đứa trẻ ra khỏi máy bằng một cú bấm. Nếu sau này
       muốn, đó là một QUYẾT ĐỊNH riêng phải chốt, không phải một tiện ích thêm vào.
   `scratchpad/smoke_brag.py` canh đúng điều này bằng cách đếm **request ra ngoài = 0**
   trong suốt lúc mở thẻ và lưu ảnh.

   ⚠️ CANVAS CHÍNH LÀ THẺ, không phải một bản vẽ thứ hai để xuất ảnh. Dựng một bản DOM
   để xem và một bản canvas để lưu là **hai nguồn sự thật cho một bố cục** — sớm muộn
   ảnh lưu ra khác thứ trẻ vừa nhìn. Ở đây trẻ nhìn đúng cái canvas sẽ được lưu.

   ⚠️ CHỜ FONT XONG MỚI VẼ (`document.fonts.ready`). Canvas không đợi `@font-face`:
   vẽ sớm thì chữ ra font hệ thống, và ảnh lưu lại trông không phải của astroQ.

   ⚠️ KHÔNG BAO GIỜ BỊA SỐ. Người gọi truyền `v` là chuỗi đã sẵn sàng; chỗ nào chưa
   đọc được thì truyền dấu `—`. Cùng luật đã chốt cho dashboard/hồ sơ: "0" là một lời
   khẳng định SAI về tiến độ của trẻ, khác hẳn "chưa biết".
   ============================================================ */
(function (global) {
  "use strict";

  /* Khổ dọc 1080×1350 — vừa màn điện thoại của bố mẹ khi xem ảnh đã lưu. */
  var W = 1080, H = 1350;

  var T = {
    vi: {
      head: "Cho bố mẹ xem",
      save: "Lưu ảnh",
      close: "Đóng",
      saved: "Đã lưu ảnh vào máy của bạn",
      local: "Thẻ này dựng ngay trong máy bạn — không gửi đi đâu cả.",
      brand: "astroQ.org"
    },
    en: {
      head: "Show a grown-up",
      save: "Save image",
      close: "Close",
      saved: "Image saved to your device",
      local: "This card is made on your own device — nothing is sent anywhere.",
      brand: "astroQ.org"
    }
  };
  function lang(l) {
    if (l === "en" || l === "vi") return l;
    return (global.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
  }
  function t(k, l) { return (T[lang(l)] || T.vi)[k] || k; }

  var box = null, cv = null, lastFocus = null, onKey = null;

  function mount() {
    if (box) return;
    box = document.createElement("div");
    box.className = "brag";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.hidden = true;
    box.innerHTML =
      '<div class="brag-card">' +
        '<div class="brag-head"><span class="brag-h"></span>' +
          '<button type="button" class="brag-x" aria-label="Close">✕</button></div>' +
        '<canvas class="brag-cv" width="' + W + '" height="' + H + '"></canvas>' +
        '<p class="brag-note"></p>' +
        '<div class="brag-acts">' +
          '<button type="button" class="brag-save"></button>' +
          '<button type="button" class="brag-close"></button>' +
        '</div>' +
      '</div>';
    document.body.appendChild(box);
    cv = box.querySelector(".brag-cv");

    /* Bấm ra ngoài thẻ = đóng, cùng nghĩa với nút Đóng. Hai cách đóng cho ra hai kết
       quả khác nhau là chỗ trẻ học sai một lần rồi ngại bấm mãi. */
    box.addEventListener("click", function (e) { if (e.target === box) close(); });
    box.querySelector(".brag-x").addEventListener("click", close);
    box.querySelector(".brag-close").addEventListener("click", close);
    box.querySelector(".brag-save").addEventListener("click", save);
  }

  function paintChrome(l) {
    box.querySelector(".brag-h").textContent = t("head", l);
    box.querySelector(".brag-save").textContent = t("save", l);
    box.querySelector(".brag-close").textContent = t("close", l);
    box.querySelector(".brag-note").textContent = t("local", l);
  }

  /* ── Vẽ thẻ ──
     Chỉ dùng gradient + hình cơ bản + emoji: KHÔNG tải ảnh nào (một `drawImage` từ
     `img/` cũng là một request, và bộ đo đếm request ra ngoài = 0 sẽ khó đọc). */
  function draw(d, l) {
    var ctx = cv.getContext("2d");
    ctx.clearRect(0, 0, W, H);

    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "#0a1024"); g.addColorStop(0.55, "#131b3f"); g.addColorStop(1, "#1c1145");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    // Sao nền: tất định theo chỉ số, KHÔNG ngẫu nhiên — hai lần mở cùng một thành
    // tích phải ra cùng một tấm thẻ, không thì "lưu lại" là một tấm khác.
    for (var i = 0; i < 90; i++) {
      var x = (i * 137.13) % W, y = (i * 311.7) % H, r = 1 + (i % 5) * 0.5;
      ctx.globalAlpha = 0.14 + (i % 7) * 0.045;
      ctx.fillStyle = "#eaf1ff";
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;

    ctx.strokeStyle = "rgba(120,170,255,.35)"; ctx.lineWidth = 4;
    ctx.strokeRect(28, 28, W - 56, H - 56);

    ctx.textAlign = "center";
    ctx.fillStyle = "#9fd0ff";
    ctx.font = "600 30px 'JetBrains Mono', ui-monospace, monospace";
    ctx.fillText(String(d.tag || "ASTROQ"), W / 2, 108);

    if (d.badge) {
      ctx.font = "150px 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif";
      ctx.fillText(String(d.badge), W / 2, 290);
    }

    ctx.fillStyle = "#f2f7ff";
    ctx.font = "800 62px 'Space Grotesk', system-ui, sans-serif";
    wrap(ctx, String(d.title || ""), W / 2, d.badge ? 390 : 300, W - 160, 72);

    if (d.sub) {
      ctx.fillStyle = "#a9bbdd";
      ctx.font = "400 34px 'Inter', system-ui, sans-serif";
      wrap(ctx, String(d.sub), W / 2, d.badge ? 470 : 380, W - 180, 46);
    }

    // Các dòng số liệu — mỗi dòng một khối bo góc, đọc được từ xa
    var lines = (d.lines || []).slice(0, 4);
    var top = 560, rowH = 132;
    ctx.textAlign = "left";
    for (var k = 0; k < lines.length; k++) {
      var row = lines[k], y = top + k * rowH;
      ctx.fillStyle = "rgba(255,255,255,.055)";
      rrect(ctx, 90, y, W - 180, rowH - 22, 22); ctx.fill();
      ctx.font = "58px 'Segoe UI Emoji', 'Apple Color Emoji', sans-serif";
      ctx.fillText(String(row.ic || "•"), 122, y + 74);
      ctx.fillStyle = "#93a7cc";
      ctx.font = "500 27px 'JetBrains Mono', ui-monospace, monospace";
      ctx.fillText(String(row.k || "").toUpperCase(), 210, y + 48);
      ctx.fillStyle = "#f2f7ff";
      ctx.font = "700 44px 'Space Grotesk', system-ui, sans-serif";
      ctx.fillText(String(row.v == null ? "—" : row.v), 210, y + 96);
    }

    ctx.textAlign = "center";
    if (d.note) {
      ctx.fillStyle = "#8fa4c8";
      ctx.font = "400 28px 'Inter', system-ui, sans-serif";
      wrap(ctx, String(d.note), W / 2, H - 168, W - 200, 38);
    }
    ctx.fillStyle = "#6f86ad";
    ctx.font = "600 28px 'JetBrains Mono', ui-monospace, monospace";
    ctx.fillText(t("brand", l), W / 2, H - 66);
  }

  function rrect(ctx, x, y, w, h, r) {
    if (ctx.roundRect) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); return; }
    ctx.beginPath();
    ctx.moveTo(x + r, y); ctx.lineTo(x + w - r, y); ctx.quadraticCurveTo(x + w, y, x + w, y + r);
    ctx.lineTo(x + w, y + h - r); ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
    ctx.lineTo(x + r, y + h); ctx.quadraticCurveTo(x, y + h, x, y + h - r);
    ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.closePath();
  }

  /** Xuống dòng theo BỀ RỘNG THẬT của chữ — tên nhiệm vụ dài ngắn khác nhau, và
      bản EN dài hơn bản VI ở phần lớn câu. */
  function wrap(ctx, text, cx, y, maxW, lh) {
    var words = text.split(/\s+/), line = "", out = [];
    for (var i = 0; i < words.length; i++) {
      var trial = line ? line + " " + words[i] : words[i];
      if (ctx.measureText(trial).width > maxW && line) { out.push(line); line = words[i]; }
      else line = trial;
    }
    if (line) out.push(line);
    for (var j = 0; j < out.length; j++) ctx.fillText(out[j], cx, y + j * lh);
    return out.length;
  }

  function save() {
    try {
      var a = document.createElement("a");
      /* Tên tệp không mang tên trẻ — nó là thứ hiện ra ở thư mục Tải về và trong mọi
         hộp thoại chia sẻ của hệ điều hành. */
      a.download = "astroq-thanh-tich.png";
      a.href = cv.toDataURL("image/png");
      a.click();
      if (global.AstroQ && AstroQ.makeToast) {
        // Toast dùng chung nếu trang có; không có thì im lặng, KHÔNG dựng toast thứ hai.
        var el = document.getElementById("toast");
        if (el) AstroQ.makeToast("toast", 2200)(t("saved"));
      }
    } catch (e) { /* Lưu hỏng thì thẻ vẫn còn trên màn hình — không làm gì thêm. */ }
  }

  function close() {
    if (!box || box.hidden) return;
    box.hidden = true;
    document.documentElement.classList.remove("brag-open");
    if (onKey) { document.removeEventListener("keydown", onKey); onKey = null; }
    /* Trả tiêu điểm về đúng nút vừa bấm — không thì trình đọc màn hình và người dùng
       bàn phím bị ném về đầu trang (bài học modal của Kho Mẫu Vật). */
    if (lastFocus && lastFocus.focus) { try { lastFocus.focus(); } catch (e) {} }
    lastFocus = null;
  }

  function open(d) {
    mount();
    var l = lang(d && d.lang);
    lastFocus = document.activeElement;
    paintChrome(l);
    box.hidden = false;
    document.documentElement.classList.add("brag-open");
    box.querySelector(".brag-save").focus();

    onKey = function (e) { if (e.key === "Escape") { e.preventDefault(); close(); } };
    document.addEventListener("keydown", onKey);

    // Vẽ ngay một lần (để thẻ không trống), rồi vẽ lại khi font đã sẵn sàng.
    draw(d || {}, l);
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () { if (!box.hidden) draw(d || {}, l); })["catch"](function () {});
    }
  }

  global.AstroQBrag = { open: open, close: close, t: t, W: W, H: H };
})(window);
