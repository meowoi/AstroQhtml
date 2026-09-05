/* ============================================================================
   js/guest-claim.js — THẺ "LƯU TIẾN ĐỘ CỦA CON" của ĐƯỜNG CHƠI THỬ.

   Nạp như script thường (KHÔNG phải module), sau `js/progress.js`:
     <script src="js/guest-claim.js"></script>
     AstroQGuestClaim.due(n) · .open({ lang, steps }) · .TRIAL_STEPS

   ────────────────── VIỆC 3 CỦA BẢN DUYỆT 04/09/2026 ──────────────────
   Số đo khiến việc này ra đời: **mất ~99,6% người ghé TRƯỚC form đăng ký**, và
   trong 14 ngày chỉ **3 người ngoài** đăng ký thật. Nên đường mới đảo thứ tự:
   trẻ **chơi trước** — không đăng nhập, không tài khoản — rồi mới hỏi, và
   **CHỈ hỏi một ô email**.

   Nửa server là `POST /auth/claim` (`AstroqSV/.../AuthEndpoints.cs`, deploy
   05/09/2026): tạo tài khoản với **mật khẩu ngẫu nhiên không ai biết**, trả về
   một **custom token**, gửi kèm thư kích hoạt. File này là nửa client của bước đó.

   ⚠️⚠️ VÌ SAO PHẢI LÀ CUSTOM TOKEN, KHÔNG PHẢI MẬT KHẨU. Trẻ không gõ mật khẩu
      nào cả, và server cũng không giữ một cái đọc được — nên KHÔNG có gì để
      `signInWithEmailAndPassword`. Mà không có phiên thì `AstroQProgress.flush()`
      không gửi được hàng chờ, tức **đúng thứ vừa hứa cứu ("lưu tiến độ của con")
      là thứ mất**. Đường vào phiên ở đây là custom token, và nó sống đúng một
      lần, trong đúng một lời gọi (xem `claimGuest` ở js/firebase-auth.js).

   ⚠️⚠️ SDK FIREBASE CHỈ TẢI KHI TRẺ THẬT SỰ BẤM LƯU. Trang nhiệm vụ và trang game
      **cố ý không nạp** `js/firebase-auth.js` (233 KB thô / 64 KB gzip;
      `check_pages.py` mục [4] canh danh sách trang được phép nạp). Nên ở đây là
      `import()` **động**, chạy trong handler của nút — không phải lúc mở trang.
      Đổi nó thành `<script src=…>` là làm chậm đúng những màn phải mượt, và mục
      [4] sẽ báo hỏng ngay.

   ⚠️ `import()` TRONG SCRIPT CỔ ĐIỂN GIẢI ĐƯỜNG DẪN THEO **URL CỦA TRANG**, không
      theo URL của file này — khác hẳn `import()` trong module. Gõ cứng
      `"./js/firebase-auth.js"` là đúng ở `/mission-earth.html` và **404** ở
      `/en/…`. Nên đường dẫn suy từ chính thẻ `<script>` đang chạy, cùng idiom với
      `js/index-gate.js` và `JS_DIR` của `js/index.js`.

   ⚠️ KHÔNG BAO GIỜ NÓI "ĐÃ LƯU XONG" KHI HÀNG CHỜ CHƯA RỖNG. `flush()` trả về
      `true` chỉ khi gửi hết; gửi dở mà báo xong là nói dối đúng vào lúc đứa trẻ
      vừa đưa email để đổi lấy lời hứa đó.
   ============================================================================ */
(function (global) {
  "use strict";

  /* Bao nhiêu chặng thì hỏi. Ba — đủ để trẻ đã có thứ đáng để mất, chưa đủ lâu
     để lượt chơi bị cắt ngang khi còn đang hào hứng. Đây là con số của SẢN PHẨM,
     không phải hằng số kỹ thuật; đổi thì đổi ở đúng đây. */
  var TRIAL_STEPS = 3;

  /* Bấm "Để sau" thì ghi lại SỐ CHẶNG lúc đó, và chỉ hỏi lại khi trẻ chơi thêm
     đủ `TRIAL_STEPS` chặng nữa. Không có mốc này thì hộp bật lên sau MỌI chặng —
     một lời mời hỏi đi hỏi lại là một lời mời bị tắt theo phản xạ. */
  var LS_SNOOZE = "astroq-claim-snooze";

  /* Thư mục js/ suy từ src của chính thẻ script này — xem cảnh báo ở đầu file.
     Suy không ra thì để rỗng và `submit()` nói ra bằng một câu lỗi, chứ không
     đoán một đường dẫn rồi ăn 404 giữa lúc trẻ đang chờ. */
  var JS_DIR = (function () {
    try {
      var s = document.currentScript && document.currentScript.src;
      return s ? s.replace(/[^/]*$/, "") : "";
    } catch (e) { return ""; }
  })();

  /* Cùng hình dạng với `EmailRe()` ở server (`AuthEndpoints.cs`). Đây chỉ là phép
     chặn sớm cho đỡ một vòng mạng — server vẫn kiểm lại, và server mới là nơi nói
     câu cuối. */
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  var TXT = {
    vi: {
      h:       "Lưu tiến độ của con",
      sub:     "Con vừa chơi xong {n} chặng đầu. Cho mình một địa chỉ email để giữ lại phần vừa chơi nhé.",
      /* ⚠️ Câu RIÊNG cho khu game — nói "chặng" ở đó là một câu SAI: game không
         có chặng nào, nó có LƯỢT CHƠI. Một lời mời gọi sai tên thứ trẻ vừa làm
         là một lời mời đọc ra như của trang khác. */
      sub_game: "Con vừa chơi {n} lượt. Cho mình một địa chỉ email để giữ lại điểm và kỷ lục nhé.",
      only:    "Chỉ cần MỘT ô email. Không tên, không mật khẩu.",
      lb:      "Email của bố mẹ",
      ph:      "email@vidu.com",
      go:      "Lưu tiến độ của con",
      going:   "Đang lưu…",
      skip:    "Để sau",
      fine:    "Mình gửi một lá thư tới hòm thư này để con quay lại chơi được ở máy khác.",
      e_mail:  "Email chưa đúng định dạng.",
      e_load:  "Chưa tải được phần đăng nhập. Kiểm tra mạng rồi thử lại nhé.",
      e_demo:  "Bản này chưa nối máy chủ nên chưa lưu được. Tiến độ vẫn nằm trong máy.",
      ok_n:    "Đã lưu {n} việc của con!",
      ok_0:    "Đã lưu tiến độ của con!",
      ok_part: "Đã tạo tài khoản, nhưng còn {n} việc chưa gửi xong. Mình sẽ gửi nốt lần sau.",
      ok_acc:  "Đã ghi nhận email. Mở thư giúp mình rồi quay lại nhé."
    },
    en: {
      h:       "Save your progress",
      sub:     "You just finished the first {n} stages. Leave an email address and we'll keep them.",
      sub_game: "You just played {n} rounds. Leave an email address and we'll keep your scores.",
      only:    "ONE email box. No name, no password.",
      lb:      "A parent's email",
      ph:      "email@example.com",
      go:      "Save my progress",
      going:   "Saving…",
      skip:    "Later",
      fine:    "We'll send one email so you can come back on another device.",
      e_mail:  "That email address looks invalid.",
      e_load:  "Couldn't load the sign-in code. Check your connection and try again.",
      e_demo:  "This build isn't connected to the server yet, so nothing was saved. Your progress stays on this device.",
      ok_n:    "Saved {n} of your runs!",
      ok_0:    "Progress saved!",
      ok_part: "Account created, but {n} runs haven't been sent yet. We'll finish next time.",
      ok_acc:  "Email noted. Open it and come back."
    }
  };

  var el = null;          // gốc `.gc`, dựng một lần rồi dùng lại
  var refs = {};
  var closeWith = null;   // resolve của lời hứa `open()` đang mở
  var lastFocus = null;
  var lang = "vi";

  function T(k) {
    var d = TXT[lang === "en" ? "en" : "vi"] || TXT.vi;
    return d[k] || k;
  }

  /** Có phiên đăng nhập THẬT hay không — cùng phép thử `js/index-gate.js` dùng.
      Hồ sơ thời demo ghi `astroq-user` KHÔNG có `uid`, nên phải hỏi `uid`. */
  function signedIn() {
    try {
      if (!global.AstroQ || !AstroQ.getUser) return false;
      var u = AstroQ.getUser();
      return !!(u && u.uid);
    } catch (e) { return false; }
  }

  function snoozeRead() {
    try { return parseInt(global.localStorage.getItem(LS_SNOOZE), 10) || 0; }
    catch (e) { return 0; }
  }

  function snoozeWrite(n) {
    try { global.localStorage.setItem(LS_SNOOZE, String(n | 0)); } catch (e) {}
  }

  /**
   * Đã tới lúc hỏi chưa? `steps` = số chặng đang nằm trong hàng chờ (chưa cứu được).
   * ⚠️ Đã có phiên thì KHÔNG BAO GIỜ hỏi: hàng chờ của người đã đăng nhập tự gửi
   *    được, và hỏi email của người đang đăng nhập là hỏi một câu vô nghĩa.
   */
  function due(steps) {
    var n = steps | 0;
    if (signedIn()) return false;
    if (n < TRIAL_STEPS) return false;
    return n >= snoozeRead() + TRIAL_STEPS;
  }

  function build() {
    if (el) return;
    el = document.createElement("div");
    el.className = "gc";
    el.setAttribute("role", "dialog");
    el.setAttribute("aria-modal", "true");
    el.setAttribute("aria-hidden", "true");
    el.setAttribute("aria-labelledby", "gc-h");
    el.innerHTML =
      '<div class="gc-card">' +
        '<h2 id="gc-h">—</h2>' +
        '<p class="gc-sub" id="gc-sub">—</p>' +
        '<p class="gc-only" id="gc-only">—</p>' +
        /* `<form>` THẬT, không phải một `<div>` có nút: Enter trong ô email phải
           gửi được, và bàn phím di động mới hiện đúng phím "Đi" thay vì Xuống dòng. */
        '<form novalidate>' +
          '<label class="gc-lb" for="gc-email" id="gc-lb">—</label>' +
          '<input type="email" id="gc-email" name="email" autocomplete="email" ' +
                 'inputmode="email" spellcheck="false" required />' +
          '<div class="gc-acts">' +
            '<button type="submit" class="gc-go" id="gc-go">—</button>' +
            '<button type="button" class="gc-skip" id="gc-skip">—</button>' +
          '</div>' +
        '</form>' +
        '<p class="gc-msg" id="gc-msg" role="status" aria-live="polite"></p>' +
        '<p class="gc-fine" id="gc-fine">—</p>' +
      '</div>';
    document.body.appendChild(el);

    refs.h     = el.querySelector("#gc-h");
    refs.sub   = el.querySelector("#gc-sub");
    refs.only  = el.querySelector("#gc-only");
    refs.lb    = el.querySelector("#gc-lb");
    refs.email = el.querySelector("#gc-email");
    refs.go    = el.querySelector("#gc-go");
    refs.skip  = el.querySelector("#gc-skip");
    refs.msg   = el.querySelector("#gc-msg");
    refs.fine  = el.querySelector("#gc-fine");
    refs.form  = el.querySelector("form");

    refs.form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      submit();
    });

    /* Escape = "Để sau", đi qua ĐÚNG nút đó chứ không gọi thẳng `finish()`: hai
       đường ra khác nhau về hành vi (một cái ghi mốc hoãn, một cái không) là thứ
       không ai rà lại được ở lần sửa sau.

       ⚠️⚠️ NGHE Ở `document`, KHÔNG NGHE Ở `.gc` — lỗi thật, chỉ đo mới thấy.
          Bản đầu gắn trên chính thẻ, nên nó chỉ chạy khi tiêu điểm còn nằm TRONG
          thẻ. Mà thẻ **cố ý không đóng khi bấm ra nền**, nên một cú chạm hụt
          (chuyện thường trên điện thoại) đẩy tiêu điểm về `<body>` và từ đó
          **Escape mất tác dụng** — trẻ bấm hụt rồi bấm Escape thì không thoát
          được. Đo được: bấm ra nền xong nhấn Escape → thẻ đứng nguyên.
       ⚠️ Chỉ xử lý khi thẻ ĐANG mở (`closeWith` khác null), không thì nó ăn phím
          Escape của mọi lớp phủ khác trên trang. */
    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape" || !closeWith) return;
      ev.stopPropagation();
      refs.skip.click();
    });

    /* ⚠️ KHÔNG đóng khi bấm ra nền. Đây là một câu hỏi có hai câu trả lời rõ ràng;
       một cú chạm hụt trên điện thoại không được tính là "để sau". */
  }

  function paint(steps, kind) {
    refs.h.textContent    = T("h");
    refs.sub.textContent  =
      T(kind === "game" ? "sub_game" : "sub").replace("{n}", String(steps | 0));
    refs.only.textContent = T("only");
    refs.lb.textContent   = T("lb");
    refs.email.placeholder = T("ph");
    refs.go.textContent   = T("go");
    refs.skip.textContent = T("skip");
    refs.fine.textContent = T("fine");
    say("", "");
  }

  function say(text, kind) {
    refs.msg.textContent = text || "";
    refs.msg.className = "gc-msg" + (kind ? " " + kind : "");
  }

  function busy(on) {
    refs.go.disabled = !!on;
    refs.go.textContent = on ? T("going") : T("go");
    refs.email.readOnly = !!on;
  }

  function finish(result) {
    if (!el) return;
    var r0 = result || { saved: false, skipped: true };
    if (r0.skipped) snoozeWrite(r0.steps | 0);
    el.classList.remove("show");
    el.setAttribute("aria-hidden", "true");
    try { if (lastFocus && lastFocus.focus) lastFocus.focus(); } catch (e) {}
    var r = closeWith; closeWith = null;
    if (r) r(r0);
  }

  /** Lấy module xác thực. Tải một lần; lần sau trình duyệt trả bản đã nạp. */
  function loadAuth() {
    if (global.AstroQAuth && global.AstroQAuth.claimGuest)
      return Promise.resolve(global.AstroQAuth);
    if (!JS_DIR) return Promise.resolve(null);
    return import(JS_DIR + "firebase-auth.js")
      .then(function (m) { return (m && m.default) || global.AstroQAuth || null; })
      .catch(function (e) {
        console.warn("[AstroQ] Không tải được js/firebase-auth.js:", e && e.message);
        return null;
      });
  }

  function submit() {
    var email = (refs.email.value || "").trim().toLowerCase();
    if (!EMAIL_RE.test(email)) {
      refs.email.setAttribute("aria-invalid", "true");
      say(T("e_mail"), "bad");
      try { refs.email.focus(); } catch (e) {}
      return;
    }
    refs.email.removeAttribute("aria-invalid");
    busy(true);
    say(T("going"), "");

    loadAuth().then(function (A) {
      if (!A || !A.claimGuest) { busy(false); say(T("e_load"), "bad"); return; }

      return A.claimGuest(email).then(function (r) {
        if (!r || !r.ok) {
          busy(false);
          say((r && (r.notConfigured ? T("e_demo") : r.message)) || T("e_load"), "bad");
          return;
        }

        /* Có tài khoản nhưng KHÔNG có phiên (nhánh `throttled` của server, hoặc
           đúc token hỏng). Hàng chờ vẫn nằm nguyên trong máy — nói đúng như vậy,
           đừng mượn câu "đã lưu xong". */
        if (!r.signedIn) {
          say(r.message || T("ok_acc"), "ok");
          setTimeout(function () {
            finish({ saved: false, account: true, email: email });
          }, 2200);
          return;
        }

        /* Có phiên rồi → GỬI NỐT HÀNG CHỜ. `flush()` không tự chạy lại giữa lượt
           tải trang (nó chỉ chạy lúc nạp `js/progress.js` và mỗi khi có mạng lại),
           nên không gọi ở đây là tài khoản có mà tiến độ vẫn nằm nguyên trong máy —
           đúng cái vừa hứa là cái mất. */
        var P = global.AstroQProgress;
        var n0 = (P && P.pending) ? P.pending() : 0;
        var done = (P && P.flush) ? P.flush() : Promise.resolve(false);
        return Promise.resolve(done).then(function (empty) {
          var left = (P && P.pending) ? P.pending() : 0;
          if (empty || left === 0) {
            say(n0 > 0 ? T("ok_n").replace("{n}", String(n0)) : T("ok_0"), "ok");
          } else {
            say(T("ok_part").replace("{n}", String(left)), "ok");
          }
          setTimeout(function () {
            finish({ saved: true, signedIn: true, email: email, sent: n0 - left });
          }, 2200);
        });
      });
    }).catch(function (e) {
      busy(false);
      say(T("e_load"), "bad");
      console.warn("[AstroQ] Lưu tiến độ hỏng:", e && e.message);
    });
  }

  /**
   * Mở thẻ. → Promise<{ saved, skipped?, account?, signedIn?, email?, sent? }>
   * `opts.steps` = số việc vừa làm (chỉ để nói ra trong câu mời, và để ghi mốc
   *                hoãn khi trẻ bấm "Để sau").
   * `opts.kind`  = "mission" (mặc định) | "game" — quyết ĐÚNG MỘT câu: gọi thứ
   *                trẻ vừa làm là "chặng" hay "lượt". Xem `sub_game` ở bảng chữ.
   * `opts.lang`  = "vi" | "en"; không truyền thì hỏi `AstroQ.getLang()`.
   */
  function open(opts) {
    var o = opts || {};
    var steps = o.steps | 0;
    lang = o.lang || (global.AstroQ && AstroQ.getLang && AstroQ.getLang()) || "vi";
    build();
    paint(steps, o.kind);
    busy(false);
    refs.email.value = "";
    refs.email.removeAttribute("aria-invalid");
    lastFocus = document.activeElement;

    /* ⚠️ Mốc hoãn phải mang theo SỐ CHẶNG lúc MỞ. `finish()` được gọi từ bốn đường
       và không đường nào tự biết con số đó, nên nó được gắn vào đúng handler ở đây. */
    refs.skip.onclick = function () {
      finish({ saved: false, skipped: true, steps: steps });
    };

    return new Promise(function (resolve) {
      closeWith = resolve;
      el.setAttribute("aria-hidden", "false");
      // Một khung hình để trình duyệt kịp áp `visibility` trước khi chạy chuyển cảnh.
      requestAnimationFrame(function () {
        el.classList.add("show");
        setTimeout(function () { try { refs.email.focus(); } catch (e) {} }, 80);
      });
    });
  }

  global.AstroQGuestClaim = {
    TRIAL_STEPS: TRIAL_STEPS,
    due: due,
    open: open,
    /** Cho bộ đo: quên mốc hoãn. Không có đường nào trong app gọi hàm này. */
    _resetSnooze: function () { try { global.localStorage.removeItem(LS_SNOOZE); } catch (e) {} }
  };
})(window);
