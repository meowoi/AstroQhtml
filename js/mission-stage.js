/* ============================================================
   js/mission-stage.js — VỎ MÀN CHƠI, dùng chung cho MỌI nhiệm vụ.

   Nạp như script thường (KHÔNG phải module), sau `js/mission-engine.js`:
     <script src="js/mission-stage.js"></script>

   ────────────────── VÌ SAO CÓ FILE NÀY (15/08/2026) ──────────────────
   `js/mission-engine.js` đã tách phần ĐIỀU PHỐI bước ra dùng chung từ
   31/07/2026, nhưng phần VỎ thì vẫn nằm nguyên trong `mission-earth.html`:
   header · bảng mục tiêu · box thoại · thẻ "vừa nhận được" · kéo-thả ·
   bảng câu đố · màn tổng kết · đường về tự động · hộp "tiếp hay dừng" ·
   vào chơi tiếp · `?step=`. Đo được **~600 dòng JS + ~200 dòng markup +
   ~430 dòng CSS**.

   Nhiệm vụ thứ hai ở Trái Đất (`mission-orbit.html`) vì thế chỉ còn hai
   đường: chép cả khối đó, hoặc tách ra. Chép là hai bản sớm muộn lệch —
   và lịch sử file `CLAUDE.md` đã ghi đúng cái giá đó nhiều lần (ba bản
   `.modal-card`, hai mảng `ARTICLES`, ba bản box thoại linh vật trước khi
   có `css/mascot.css`). Quy tắc 2 mục 6: **thứ dùng chung thì tách ra
   dùng lại, không copy-paste giữa các trang.**

   ⚠️ VỎ TỰ DỰNG MARKUP, KHÔNG BẮT TRANG CHÉP LẠI ~200 DÒNG HTML.
      Đúng khuôn `js/game-shell.js` (dựng console + thanh cấp cho 6 game)
      và `js/user-menu.js`. Trang chỉ khai **phần riêng của nó**: các lớp
      cảnh và các `.me-board` mang nội dung bước.

   ⚠️ VỎ TỰ MANG CHUỖI SONG NGỮ của phần nó sở hữu (nút Về, OK, màn tổng
      kết, hộp hỏi, nhãn bàn phím của kéo-thả…). Đúng khuôn `js/daily.js`
      và `js/weeklog.js`. Nhờ vậy nhiệm vụ mới KHÔNG phải khai lại ~40
      khoá i18n — mà khai lại là hai bảng chữ sẽ trôi khỏi nhau.

   ⚠️ NĂM KHOÁ VẪN LẤY TỪ TỪ ĐIỂN CỦA TRANG, vì chúng là NỘI DUNG của
      nhiệm vụ chứ không phải của vỏ: `tag` · `win_h` · `win_badge` ·
      `win_badge_sub` · `win_next`. Trang nào cũng phải khai đủ 5 khoá này
      ở CẢ `vi` và `en`; `check_pages` [20] đối chiếu.

   ⚠️⚠️ KHÔNG CÓ MỘT CON SỐ THƯỞNG NÀO TRONG FILE NÀY. Mọi số hiện ở màn
      tổng kết đều đọc từ `RUN.reward` — tức bản sao của thứ SERVER trả về
      (`Services/Missions.cs` tra bảng rồi cộng). Thêm một phép cộng vào
      đây là mở đường cho client tự bịa thưởng.

   ────────────────────────── CÁCH DÙNG ──────────────────────────
     var ST = AstroQStage.create({
       mission : "earth",           // khoá nhiệm vụ ở Services/Missions.cs
       stepIds : STEP_IDS,          // ĐÚNG THỨ TỰ CHƠI
       lang    : function () { return LANG; },
       t       : t                  // hàm dịch của trang (5 khoá kể trên)
     });
     ST.mount();                    // dựng markup, PHẢI gọi trước mọi $('id')
     …dựng `steps`, rồi RUN = AstroQMission.create({ … onWin: ST.showWin })…
     ST.attach(RUN);
     ST.applyLang(LANG);            // gọi lại mỗi lần đổi ngôn ngữ
     ST.resumeSteps();              // vào chơi tiếp / `?step=` / `?restart=1`
   ============================================================ */
(function (global) {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  };

  /* ═══════════════════ CHUỖI SONG NGỮ CỦA VỎ ═══════════════════
     ⚠️ Chỉ những chuỗi VỎ sở hữu. Nội dung bước, tên nhiệm vụ, tên huy
        hiệu của nhiệm vụ thì thuộc về trang (và tên huy hiệu thì thuộc về
        `js/badges.js` — chỗ DUY NHẤT khai tên huy hiệu). */
  var TXT = {
    vi: {
      back: "Về đường đi", next: "OK", card_ok: "Đã hiểu!",
      obj_k: "MỤC TIÊU", tt_name: "Thiên thạch tím",
      a_sfx: "Bật/tắt âm thanh", a_lang: "Language / Ngôn ngữ",
      a_steps: "Tiến độ nhiệm vụ",
      comet: "Comet", byte: "Byte",
      load_txt: "ĐANG NẠP HỆ THỐNG QUÉT…",
      load_fail: "Không dựng được cảnh. Kiểm tra kết nối mạng rồi tải lại trang nhé.",
      saved_off: "Chưa gửi được lên máy chủ — sẽ tự gửi lại khi bạn đăng nhập.",
      resumed: "Chơi tiếp từ chặng {n}/{t} nhé!",
      /* Kéo-thả: lời cho trình đọc màn hình. Khai bằng khoá riêng vì
         `js/pick-place.js` đọc chúng qua getter (đổi VI/EN giữa chừng thì
         lời đọc phải đổi theo, mà bảng chỉ dựng MỘT LẦN lúc mở bước). */
      kb_hold: "Đã cầm {n}. Dùng Tab hoặc phím mũi tên để chọn chỗ đặt, rồi bấm Enter.",
      kb_place: "Đã đặt {n} vào {z}.",
      kb_wrong: "{n} không thuộc {z}. Thử chỗ khác nhé.",
      kb_drop: "Đã bỏ {n} xuống.",
      win_rw_k: "PHẦN THƯỞNG SỨ MỆNH",
      win_tt: "+{n} Thiên thạch tím",
      win_codex: "{n}/{t} mẫu dữ liệu",
      win_xp: "+{n} XP",
      win_badges: "Huy hiệu mới: {n}",
      win_next_k: "VIỆC TIẾP THEO",
      win_home: "Về Trung Tâm Điều Hướng",
      win_missions: "Trung Tâm Nhiệm Vụ",
      win_awards: "Kho Thành Tích",
      win_brag: "Cho bố mẹ xem",
      win_auto: "Tự về Trung Tâm Điều Hướng sau {n} giây… (chạm vào để ở lại)",
      af_h: "Xong chặng “{n}”!",
      af_p: "Chặng tiếp theo: {n}",
      af_next: "Chơi tiếp chặng {n}",
      af_stop: "Để lần sau",
      af_back: "Về đường đi",
      replayed: "Chặng này bạn đã xong từ trước rồi, nên lần này không có thêm phần thưởng nhé.",
      brag_tag: "BÁO CÁO SỨ MỆNH",
      brag_tt: "Thiên thạch tím", brag_xp: "Kinh nghiệm",
      brag_codex: "Mẫu dữ liệu", brag_badge: "Huy hiệu",
      brag_note: "Con vừa hoàn thành một sứ mệnh ở astroQ."
    },
    en: {
      back: "Back to the path", next: "OK", card_ok: "Got it!",
      obj_k: "OBJECTIVE", tt_name: "Purple Meteor",
      a_sfx: "Sound on/off", a_lang: "Language / Ngôn ngữ",
      a_steps: "Mission progress",
      comet: "Comet", byte: "Byte",
      load_txt: "BOOTING SCAN SYSTEM…",
      load_fail: "Could not build the scene. Check your connection and reload.",
      saved_off: "Not sent to the server yet — it will retry when you sign in.",
      resumed: "Continuing from step {n}/{t}!",
      kb_hold: "Holding {n}. Use Tab or the arrow keys to pick a slot, then press Enter.",
      kb_place: "Placed {n} into {z}.",
      kb_wrong: "{n} does not belong in {z}. Try another slot.",
      kb_drop: "Put {n} back down.",
      win_rw_k: "MISSION REWARDS",
      win_tt: "+{n} Purple Meteors",
      win_codex: "{n}/{t} data samples",
      win_xp: "+{n} XP",
      win_badges: "New badges: {n}",
      win_next_k: "WHAT'S NEXT",
      win_home: "Back to Navigation Hub",
      win_missions: "Mission Control",
      win_awards: "Trophy Room",
      win_brag: "Show your parents",
      win_auto: "Returning to the Navigation Hub in {n}s… (tap to stay)",
      af_h: "Step “{n}” complete!",
      af_p: "Next step: {n}",
      af_next: "Play step {n}",
      af_stop: "Later",
      af_back: "Back to the path",
      replayed: "You had already finished this step, so there are no extra rewards this time.",
      brag_tag: "MISSION REPORT",
      brag_tt: "Purple Meteors", brag_xp: "Experience",
      brag_codex: "Data samples", brag_badge: "Badges",
      brag_note: "I just completed a mission on astroQ."
    }
  };

  /* Markup của vỏ. Trang chỉ khai `.me-ui` + các `.me-board` của riêng nó;
     hàm `mount()` chèn phần dưới đây vào đúng chỗ. */
  function hudHtml(d) {
    return '' +
      '<header class="me-top">' +
        '<button class="back hit" id="back" type="button">&lt; <span id="back-t"></span></button>' +
        '<span class="me-tag" id="tag"></span>' +
        '<span class="me-steps" id="steps" role="img" aria-label="' + esc(d.a_steps) + '"></span>' +
        '<span class="me-cur" id="cur" title="' + esc(d.tt_name) + '">' +
          '<img src="img/tt.png" alt="' + esc(d.tt_name) + '" />' +
          '<span class="v" id="bal">0</span>' +
        '</span>' +
        '<button type="button" class="me-mute hit" id="mute" title="' + esc(d.a_sfx) + '"' +
                ' aria-label="' + esc(d.a_sfx) + '" aria-pressed="false"></button>' +
        '<span class="lang-switch" role="group" aria-label="' + esc(d.a_lang) + '">' +
          '<button type="button" class="hit" data-lang="vi">VI</button>' +
          '<button type="button" class="hit" data-lang="en">EN</button>' +
        '</span>' +
      '</header>' +

      '<section class="me-obj" id="obj">' +
        '<span class="k"><span class="led"></span><span id="obj-k"></span></span>' +
        '<h2><span class="ic" id="obj-ic">🎯</span><span id="obj-h">—</span></h2>' +
        '<p id="obj-p"></p>' +
        '<span class="prog" id="obj-prog">' +
          '<span class="bar"><i id="obj-bar"></i></span>' +
          '<span class="n" id="obj-n">0/0</span>' +
        '</span>' +
      '</section>' +

      '<span class="me-hand" id="hand" aria-hidden="true">👆</span>' +

      '<section class="aq-say me-say" id="say" role="status" aria-live="polite">' +
        '<span class="aq-ava"><img id="say-ava" src="img/m1.png" alt="" /></span>' +
        '<span class="body">' +
          '<span class="aq-nm" id="say-who">Comet</span>' +
          '<p class="line" id="say-line"></p>' +
        '</span>' +
        '<button type="button" class="next hide hit" id="say-next">OK</button>' +
      '</section>' +

      /* Thẻ "vừa nhận được" — MỘT thẻ cho mọi thứ trẻ nhận: mẫu vật, huy
         hiệu, mảnh dữ liệu. Trẻ đọc chúng y như nhau (emoji lớn · tên ·
         một câu · nhãn trạng thái) nên dựng ba thẻ khác nhau là bắt nó
         học ba thứ cho một việc.
         ⚠️ NÚT "Đã hiểu!" LÀ BẮT BUỘC, KHÔNG PHẢI TRANG TRÍ. Thẻ từng TỰ
            ĐÓNG sau 3,4 giây; chủ dự án chơi thật và báo là không đủ thời
            gian đọc. Thẻ MANG BÀI HỌC nên phải để trẻ tự quyết lúc nào
            đọc xong. Cả thẻ vẫn bấm được — nút chỉ là chỗ NÓI RA rằng
            phải bấm, và là thứ bàn phím Tab tới được. */
      '<article class="me-card hit" id="card" role="dialog" aria-modal="true" aria-hidden="true">' +
        '<div class="top" id="card-ic">🌊</div>' +
        '<div class="nm" id="card-nm">—</div>' +
        '<p class="fact" id="card-fact"></p>' +
        '<p class="sub" id="card-sub" hidden></p>' +
        '<span class="got" id="card-got"></span>' +
        '<button type="button" class="ok hit" id="card-ok"></button>' +
      '</article>' +

      /* Bảng CÂU ĐỐ — markup của khuôn `buildAsk`, nên nó thuộc về vỏ chứ không
         thuộc về một nhiệm vụ. Dùng lại `.me-board` như mọi bảng khác: trẻ nhận ra
         ngay đây là "một bảng của tàu", không phải một hộp thoại lạ. */
      '<section class="me-board me-ask" id="ask">' +
        '<span class="k" id="ask-k"></span>' +
        '<p class="q" id="ask-q"></p>' +
        '<div class="opts" id="ask-opts"></div>' +
      '</section>';
  }

  function tailHtml() {
    return '' +
      '<div class="me-win" id="win" role="dialog" aria-modal="true" aria-hidden="true">' +
        '<div class="me-win-card">' +
          '<h2><span aria-hidden="true">🚀</span> <span id="win-h">—</span></h2>' +
          '<div class="me-cheer" aria-hidden="true">' +
            '<img src="img/m1.png" alt="" /><img src="img/b1.png" alt="" />' +
          '</div>' +
          '<div class="medal">' +
            '<div class="big" aria-hidden="true">🎖️</div>' +
            '<div class="nm" id="win-badge">—</div>' +
            '<div class="sub" id="win-badge-sub">—</div>' +
          '</div>' +
          '<div class="sec">' +
            '<span class="k"><span aria-hidden="true">🎁</span><span id="win-rw-k"></span></span>' +
            '<div class="rw"><img src="img/tt.png" alt="" /><span id="win-rw-tt">—</span></div>' +
            '<div class="rw"><span class="ic" aria-hidden="true">📘</span><span id="win-rw-codex">—</span></div>' +
            '<div class="rw"><span class="ic" aria-hidden="true">⭐</span><span id="win-rw-xp">—</span></div>' +
            /* Huy hiệu mở THÊM trong lượt. Chỉ hiện cái SERVER báo trong
               `newBadges` — chưa đăng nhập / mất mạng thì khối này rỗng
               chứ không tự nhận là đã mở được cái nào. */
            '<div class="rw hide" id="win-rw-badges"><span class="ic" aria-hidden="true">🏅</span>' +
              '<span id="win-badges">—</span></div>' +
          '</div>' +
          '<div class="sec">' +
            '<span class="k"><span aria-hidden="true">🧭</span><span id="win-next-k"></span></span>' +
            '<div class="nextup"><span class="ic" aria-hidden="true">🎯</span><span id="win-next">—</span></div>' +
          '</div>' +
          /* ⚠️ NÚT CHÍNH (vàng) LÀ "VỀ TRUNG TÂM ĐIỀU HƯỚNG", không phải nút
             sang Trung Tâm Nhiệm Vụ: đường về dashboard là đường ĐƯỢC THIẾT
             KẾ (về tới đó Comet chúc mừng và chỉ việc tiếp theo), và nó khớp
             với đường về TỰ ĐỘNG sau 5 giây. */
          '<div class="acts">' +
            '<button type="button" class="go" id="win-home">—</button>' +
            '<button type="button" class="ghost" id="win-missions">—</button>' +
            '<button type="button" class="ghost" id="win-awards">—</button>' +
            /* ⚠️ KHOE VỚI BỐ MẸ, KHÔNG KHOE VỚI NGƯỜI LẠ. Thẻ dựng ngay trong
               máy, không gửi đi đâu cả (xem js/brag.js). */
            '<button type="button" class="ghost" id="win-brag">—</button>' +
          '</div>' +
          '<p class="autoline" id="win-auto" aria-live="polite"></p>' +
        '</div>' +
      '</div>' +

      /* Hộp "tiếp hay dừng" — `docs/decisions/008` quyết định 4: *chơi xong
         một chặng thì HỎI, đừng tự quyết*. Dùng lại nguyên vỏ `.me-win` —
         cùng một kiểu hộp thì trẻ chỉ phải học một lần. */
      '<div class="me-win me-next" id="after" role="dialog" aria-modal="true" aria-hidden="true">' +
        '<div class="me-win-card">' +
          '<h2><span aria-hidden="true">🎉</span> <span id="af-h">—</span></h2>' +
          '<p class="af-p" id="af-p">—</p>' +
          '<div class="acts">' +
            '<button type="button" class="go" id="af-next">—</button>' +
            '<button type="button" class="ghost" id="af-stop">—</button>' +
          '</div>' +
        '</div>' +
      '</div>' +

      '<div class="me-toast" id="toast" role="status" aria-live="polite"></div>';
  }

  function loadHtml(d) {
    return '<div class="me-load" id="load">' +
             '<span class="ring" aria-hidden="true"></span>' +
             '<span class="txt" id="load-txt">' + esc(d.load_txt) + '</span>' +
             '<span class="sub" id="load-sub"></span>' +
           '</div>';
  }

  function create(cfg) {
    var mission  = cfg.mission;
    var stepIds  = (cfg.stepIds || []).slice();
    var pageT    = cfg.t || function (k) { return k; };
    var langOf   = cfg.lang || function () { return "vi"; };

    var RUN = null;
    var serverDone = new Set();
    var sayResolve = null;
    var toastTimer = 0;
    var autoLeft = null, autoTimer = null;
    var nudgeTimers = {};

    /** Chuỗi của VỎ. */
    function T(k) {
      var d = TXT[langOf() === "en" ? "en" : "vi"] || TXT.vi;
      return d[k] != null ? d[k] : k;
    }

    /* ───────────────────── Dựng markup ───────────────────── */
    function mount() {
      var ui = document.querySelector(".me-ui");
      if (!ui) throw new Error("mission-stage: thiếu .me-ui trong trang");
      var d = TXT[langOf() === "en" ? "en" : "vi"] || TXT.vi;
      ui.insertAdjacentHTML("afterbegin", hudHtml(d));
      ui.insertAdjacentHTML("beforebegin", loadHtml(d));
      document.body.insertAdjacentHTML("beforeend", tailHtml());
      wire();
    }

    /* ───────────────────── Toast ───────────────────── */
    function toast(msg) {
      var el = $("toast");
      el.innerHTML = String(msg).replace(/\{tt\}/g,
        '<img src="img/tt.png" alt="' + esc(T("tt_name")) + '" />');
      el.classList.add("show");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () { el.classList.remove("show"); }, 2600);
    }
    function paintBalance() {
      if (global.Economy) $("bal").textContent = Economy.getAsteroids();
    }

    /* ───────────────────── Box thoại ───────────────────── */
    function say(who, html, opt) {
      var wait = !opt || opt.wait !== false;
      var el = $("say");
      el.classList.toggle("byte", who === "byte");
      $("say-ava").src = who === "byte" ? "img/b1.png" : "img/m1.png";
      $("say-who").textContent = who === "byte" ? T("byte") : T("comet");
      $("say-line").innerHTML = html;
      /* ⚠️ NHẤC LÊN KHỎI BẢNG ĐÁY NGAY Ở ĐÂY — LỖI THẬT 19/08/2026. Chặng ① của
         `mission-orbit.html` gọi `say()` thẳng lúc bảng "HỆ THỐNG QUAN SÁT" còn mở;
         hai hộp cùng neo đáy nên bảng đè kín box thoại, che luôn nút "OK" — mà đó là
         đường DUY NHẤT đi tiếp (chủ dự án chơi thật rồi gửi ảnh). Trước đó việc nhấc
         nằm ở `boardSay()`, tức mỗi chỗ gọi phải TỰ NHỚ dùng hàm nào; luật "chỗ nào
         cũng phải nhớ" thì sớm muộn có một chỗ quên. Nay `say()` tự đo: không bảng
         nào mở thì `liftAboveBoards` bỏ `.lift`, nên bước không có bảng không đổi gì. */
      liftAboveBoards(el);
      el.classList.add("show");
      var next = $("say-next");
      next.textContent = T("next");
      if (!wait) { next.classList.add("hide"); return Promise.resolve(); }
      next.classList.remove("hide");
      return new Promise(function (res) { sayResolve = res; });
    }
    function hideSay() { $("say").classList.remove("show", "lift"); }

    /* ───────────────────── Bảng mục tiêu ───────────────────── */
    function objective(o) {
      $("obj-ic").textContent = o.ic;
      $("obj-h").textContent = o.h;
      $("obj-p").textContent = o.p;
      $("obj-k").textContent = T("obj_k");
      progress(o.n, o.total);
      $("obj").classList.add("show");
    }
    function progress(n, total) {
      var show = total > 0;
      $("obj-prog").style.display = show ? "" : "none";
      if (!show) return;
      $("obj-bar").style.width = Math.round((n / total) * 100) + "%";
      $("obj-n").textContent = n + "/" + total;
    }
    function hideObjective() { $("obj").classList.remove("show"); }

    /* ───────────────────── Thẻ "vừa nhận được" ─────────────────────
       ⚠️⚠️ THẺ PHẢI NHẤC LÊN KHỎI BẢNG ĐÁY — LỖI THẬT ĐÃ SỬA 03/08/2026.
       Chủ dự án chơi thật rồi gửi ảnh: *"2 bảng thông tin che nhau"*. Thẻ
       canh giữa KHUNG NHÌN, còn `.me-board` neo ĐÁY. Nặng nhất: **nút "Đã
       hiểu!" bị bảng đè**, mà đó là đường DUY NHẤT đóng thẻ → trẻ nhìn thấy
       nút mà bấm không được.
       ⚠️ CŨNG PHẢI NÂNG `z-index`: thẻ là `aria-modal="true"` mà `.me-board`
          nằm SAU nó trong DOM, không có z-index thì bảng vẽ ĐÈ LÊN thẻ. Một
          hộp thoại modal bị chính trang đè lên là hộp thoại nói dối. */
    /* Đo bảng đáy CAO NHẤT đang mở rồi nhấc `el` lên khỏi nó qua `--board-h`. MỘT phép
       đo cho HAI thứ neo khác nhau: thẻ (`.me-card.lift` canh giữa khoảng CÒN LẠI phía
       trên bảng) và box thoại (`.me-say.lift` neo ngay trên mép bảng). Hai công thức CSS
       khác nhau, cùng một con số — nên chỉ một chỗ đo.
       ⚠️ ĐO NGAY LÚC GỌI, đừng gán cứng: bảng cao dần theo số thẻ đã xếp, và dòng nhắc
          dài ra thì bảng cũng cao thêm một dòng.
       ⚠️ Không bảng nào đang mở → BỎ `.lift` và bỏ luôn biến, không để lại số cũ: bước
          sau không có bảng mà vẫn nhấc thì hộp lơ lửng giữa khung nhìn. */
    function liftAboveBoards(el) {
      var b = Array.prototype.slice.call(document.querySelectorAll(".me-board.show"))
        .reduce(function (h, n) { return Math.max(h, n.offsetHeight); }, 0);
      if (!b) { el.style.removeProperty("--board-h"); el.classList.remove("lift"); return; }
      el.style.setProperty("--board-h", (b + 12) + "px");
      el.classList.add("lift");
    }

    function liftCard() { liftAboveBoards($("card")); }

    function showCard(c) {
      sfx("pickup");
      var el = $("card");
      el.style.setProperty("--cc", c.cc);
      el.style.setProperty("--cbg", c.cbg);
      $("card-ic").textContent = c.ic;
      $("card-nm").textContent = c.nm;
      $("card-fact").textContent = c.fact;
      $("card-sub").textContent = c.sub || "";
      $("card-sub").hidden = !c.sub;   // bước không truyền `sub` thì không để ô trống
      $("card-got").textContent = c.tag;
      $("card-ok").textContent = T("card_ok");
      liftCard();
      el.classList.add("show");
      el.setAttribute("aria-hidden", "false");
      return new Promise(function (res) {
        var close = function () {
          el.classList.remove("show");
          el.setAttribute("aria-hidden", "true");
          el.removeEventListener("click", close);
          setTimeout(res, 260);
        };
        el.addEventListener("click", close);
        /* ⚠️ KHÔNG TỰ ĐÓNG SAU VÀI GIÂY (bỏ 02/08/2026). Thẻ này MANG BÀI HỌC
           nên nó là thứ để ĐỌC, không phải hiệu ứng để ngắm; trẻ đọc chậm hơn
           người lớn nhiều. `prefers-reduced-motion` CŨNG không tự đóng: giảm
           chuyển động là bớt hoạt cảnh, KHÔNG phải bớt thời gian đọc. */
        $("card-ok").focus();
      });
    }

    /* ═══════════════════ KÉO-THẢ ═══════════════════
       `js/pick-place.js` lo cả đường chuột lẫn đường bàn phím. Ở đây chỉ nối
       thêm âm thanh và bộ nhãn đọc song ngữ.
       ⚠️ Nhãn khai bằng GETTER, không phải chuỗi tính sẵn: trẻ đổi VI/EN giữa
          chừng thì lời đọc phải đổi theo, mà bảng chỉ dựng MỘT LẦN lúc mở bước. */
    function dragDrop(opt) {
      global.AstroQPickPlace.wire({
        items: opt.items, zones: opt.zones, wide: opt.wide,
        canDrop: opt.canDrop, onHit: opt.onHit, onMiss: opt.onMiss,
        sfx: sfx,
        labels: {
          get hold()  { return T("kb_hold"); },
          get place() { return T("kb_place"); },
          get wrong() { return T("kb_wrong"); },
          get drop()  { return T("kb_drop"); }
        }
      });
    }

    /** Nhấp nháy dòng nhắc + lời khích lệ rồi tự trả lại câu hướng dẫn cũ.
        Không cần tên bảng: `say()` tự đo bảng đang mở để nhấc box thoại lên. */
    function nudge(hintId, wrongText, hintText) {
      $(hintId).textContent = wrongText;
      say("byte", wrongText, { wait: false });
      clearTimeout(nudgeTimers[hintId]);
      nudgeTimers[hintId] = setTimeout(function () {
        $(hintId).textContent = hintText;
        hideSay();
      }, 2200);
    }

    /* ───────────────────── Bảng câu đố ─────────────────────
       ⚠️ NÚT `<button>`, KHÔNG PHẢI KÉO-THẢ: ở đây chỉ có MỘT câu hỏi và vài
          lựa chọn; dựng bằng khuôn kéo-thả là bắt trẻ làm thao tác khó hơn cho
          một việc dễ hơn. Bàn phím đi qua bằng Tab + Enter mà không cần dòng nào.
       ⚠️ Cả dãy bị VÔ HIỆU ngay khi bấm: `onPick` có `await`, không khoá thì cú
          bấm thứ hai chạy chồng và thẻ nội dung mở hai lần.
       @param cfg {k, q, opts:[{id, ic, tx}], onPick} */
    function buildAsk(cfg) {
      $("ask-k").textContent = cfg.k;
      $("ask-q").textContent = cfg.q;
      $("ask-opts").innerHTML = cfg.opts.map(function (o) {
        return '<button type="button" class="me-ask-opt hit" data-pick="' + esc(o.id) + '">' +
               '<span class="ic" aria-hidden="true">' + o.ic + "</span>" +
               '<span class="tx">' + esc(o.tx) + "</span></button>";
      }).join("");
      Array.prototype.forEach.call($("ask-opts").querySelectorAll(".me-ask-opt"), function (b) {
        b.addEventListener("click", function () {
          Array.prototype.forEach.call($("ask-opts").querySelectorAll(".me-ask-opt"),
            function (o) { o.disabled = true; });
          cfg.onPick(b.getAttribute("data-pick"));
        });
      });
    }

    /* ───────────────────── Âm thanh ─────────────────────
       Lớp mỏng quanh `AstroQSfx` để chỗ gọi không phải kiểm `if` mỗi lần. */
    function sfx(name, arg) {
      if (!global.AstroQSfx) return;
      try { global.AstroQSfx[name](arg); } catch (e) {}
    }
    function paintMute() {
      var off = !global.AstroQSfx || !global.AstroQSfx.on();
      $("mute").textContent = off ? "🔇" : "🔊";
      $("mute").setAttribute("aria-pressed", off ? "true" : "false");
    }

    /* ───────────────────── Màn tổng kết ───────────────────── */
    function badgeIcon(id) {
      return (global.AstroQBadges && global.AstroQBadges.icon) ? global.AstroQBadges.icon(id) : "🏅";
    }
    function badgeName(id) {
      return (global.AstroQBadges && global.AstroQBadges.name)
        ? global.AstroQBadges.name(id, langOf()) : id;
    }

    /**
     * Chữ TĨNH của màn tổng kết — vẽ ngay lúc đổi ngôn ngữ, KHÔNG đợi tới lúc mở.
     *
     * ⚠️ ĐỪNG ĐỂ CHỖ GIỮ `—` SỐNG TỚI LÚC MỞ. Ba lý do, và lý do thứ ba là lỗi thật
     *    đã bắt được: ① trình đọc màn hình có thể chạm tới nội dung modal trước khi
     *    nó hiện; ② tiêu đề là thứ quyết định modal cao bao nhiêu, mà bố cục ấy phải
     *    đúng ngay từ đầu; ③ `smoke_mission_earth` ĐO BỐ CỤC màn tổng kết khi nó CHƯA
     *    mở — với chỗ giữ `—` thì tiêu đề chỉ còn "🚀—", và phép kiểm "không để emoji
     *    rơi xuống một dòng riêng" báo hỏng. Bản đầu của lượt tách vỏ 15/08/2026 mắc
     *    đúng lỗi này: markup cũ nướng sẵn tiêu đề tiếng Việt vào HTML nên không ai
     *    thấy, markup do JS dựng thì lộ ra ngay.
     */
    function paintWinStatic() {
      $("win-h").textContent = pageT("win_h");
      $("win-badge").textContent = pageT("win_badge");
      $("win-badge-sub").textContent = pageT("win_badge_sub");
      $("win-next").textContent = pageT("win_next");
      $("win-rw-k").textContent = T("win_rw_k");
      $("win-next-k").textContent = T("win_next_k");
      $("win-missions").textContent = T("win_missions");
      $("win-awards").textContent = T("win_awards");
      $("win-brag").textContent = T("win_brag");
      if (autoLeft === null) $("win-home").textContent = T("win_home");
    }

    function showWin() {
      sfx("fanfare");
      hideObjective();
      hideSay();
      paintWinStatic();
      var RW = RUN ? RUN.reward : { meteors: 0, xp: 0, codex: 0, codexTotal: 0, badges: [] };
      $("win-rw-tt").textContent = T("win_tt").replace("{n}", RW.meteors);
      $("win-rw-codex").textContent = T("win_codex")
        .replace("{n}", RW.codex).replace("{t}", RW.codexTotal);
      $("win-rw-xp").textContent = T("win_xp").replace("{n}", RW.xp);
      /* Bỏ `rookie-astronaut` ra vì nó đã có khối huân chương riêng ở trên —
         liệt kê hai lần thì trẻ tưởng được hai cái. Rỗng thì ẩn cả dòng. */
      var extra = RW.badges.filter(function (b) { return b !== "rookie-astronaut"; });
      $("win-rw-badges").classList.toggle("hide", extra.length === 0);
      if (extra.length) {
        $("win-badges").textContent = T("win_badges").replace("{n}",
          extra.map(function (b) { return badgeIcon(b) + " " + badgeName(b); }).join(" · "));
      }
      $("win").classList.add("show");
      $("win").setAttribute("aria-hidden", "false");
      startAuto();
      setTimeout(function () { $("win-home").focus(); }, 300);
    }

    /* ─────────────── Đường về tự động 5 giây ───────────────
       ⚠️ CHỈ ĐẾM KHI ĐÃ BÁO XONG LÊN SERVER — bất biến này có sẵn nhờ THỨ TỰ
          GỌI: `RUN.finish()` báo server xong rồi mới gọi `onWin`. Đếm ngay lúc
          mở modal thì mạng chậm là trẻ bị kéo đi trước khi con số thưởng kịp
          về, và thứ duy nhất nó kịp đọc là "+0".
       ⚠️ BẤT KỲ TƯƠNG TÁC NÀO CŨNG TẮT ĐẾM, KHÔNG PHẢI TẠM DỪNG. Một màn thưởng
          tự biến mất sau 5 giây là màn thưởng bị lấy đi giữa lúc đang đọc.
       ⚠️ CỐ Ý KHÔNG bắt `focus`: nút chính được `focus()` cho người dùng bàn
          phím, bắt focus là đếm tắt ngay lúc mở modal và tính năng thành vô nghĩa.
       ⚠️ ĐỪNG GỌI `startAuto()` Ở ĐÂU KHÁC ngoài `showWin()`. Nhờ nó chỉ sống ở
          màn tổng kết — mà màn tổng kết chỉ mở khi ĐÃ HẾT chặng — nên điều kiện
          "tắt đồng hồ khi còn chặng sau" của `008` được thoả BẰNG CẤU TRÚC, chứ
          không bằng một cái cờ phải nhớ tắt. */
    var AUTO_RETURN_SECS = 5;

    function paintAuto() {
      $("win-home").textContent = T("win_home") + (autoLeft === null ? "" : " (" + autoLeft + ")");
      $("win-auto").textContent = autoLeft === null ? "" : T("win_auto").replace("{n}", autoLeft);
    }
    function cancelAuto() {
      if (autoLeft === null) return;
      autoLeft = null;
      clearTimeout(autoTimer);
      autoTimer = null;
      paintAuto();
    }
    function startAuto() {
      autoLeft = AUTO_RETURN_SECS;
      paintAuto();
      var tick = function () {
        autoLeft--;
        if (autoLeft <= 0) { autoLeft = null; location.href = "dashboard.html"; return; }
        paintAuto();
        autoTimer = setTimeout(tick, 1000);
      };
      autoTimer = setTimeout(tick, 1000);
    }

    /* ─────────────── XONG MỘT CHẶNG: HỎI TIẾP HAY DỪNG ───────────────
       ⚠️ CÁC CHẶNG SERVER ĐÃ GHI NHẬN lúc mở trang — dùng để phân biệt "vừa
          xong một chặng mới" với "vừa ôn lại một chặng cũ". Hai việc đó đáng
          được nói hai câu khác nhau, và chỉ việc thứ nhất mới có chặng kế. */
    function treeUrl() { return "mission-tree.html?m=" + encodeURIComponent(mission); }
    function pad2(n) { return n < 10 ? "0" + n : String(n); }

    function stepName(id) {
      var s = global.AstroQCatalog ? global.AstroQCatalog.step(mission, id) : null;
      return s ? s[langOf() === "en" ? "en" : "vi"].nm : id;
    }

    function openAsk(id, replay) {
      var i = stepIds.indexOf(id);
      $("af-h").textContent = T("af_h").replace("{n}", stepName(id));
      if (replay) {
        $("af-p").textContent = T("replayed");
        $("af-next").hidden = true;
        $("af-stop").textContent = T("af_back");
      } else {
        $("af-p").textContent = T("af_p").replace("{n}", stepName(stepIds[i + 1]));
        $("af-next").hidden = false;
        $("af-next").textContent = T("af_next").replace("{n}", pad2(i + 2));
        $("af-stop").textContent = T("af_stop");
      }
      $("after").classList.add("show");
      $("after").setAttribute("aria-hidden", "false");
      setTimeout(function () {
        ($("af-next").hidden ? $("af-stop") : $("af-next")).focus();
      }, 60);
    }
    function closeAsk() {
      $("after").classList.remove("show");
      $("after").setAttribute("aria-hidden", "true");
    }

    /** Móc `onStepDone` của js/mission-engine.js. Trả `true` = engine ĐỪNG tự đi tiếp. */
    function afterStep(id, last) {
      /* Ôn lại một chặng cũ: không có chặng nào vừa mở ra để đi tiếp và tiến độ
         không nhúc nhích — hỏi "tiếp hay dừng" ở đó là hỏi một câu vô nghĩa. Vẫn
         MỞ HỘP (chứ không lặng lẽ nhảy trang) để nói rõ vì sao lần này không có
         thưởng: để trẻ tự phát hiện bằng dòng "+0" là cách tệ nhất. */
      if (serverDone.has(id)) { openAsk(id, true); return true; }
      /* Chặng cuối → trả `false` để engine mở màn tổng kết. Ở đó không còn gì để hỏi. */
      if (last) return false;
      openAsk(id, false);
      return true;
    }

    /* ───────────────── VÀO CHƠI TIẾP TỪ CHẶNG CÒN DỞ ─────────────────
       ⚠️ ĐỌC CACHE, KHÔNG GỌI API — bắt buộc, không phải tối ưu: trang nhiệm vụ
          **cố ý không nạp** `js/firebase-auth.js` nên nó KHÔNG có token để hỏi
          `GET /me/missions`. Trang CÓ token (`missions.html`, `dashboard.html`)
          ghi cache; ở đây chỉ đọc. Luật vẫn ở server: cache chỉ chứa **id chặng**,
          không một con số thưởng nào.
       ⚠️ CHƯA ĐỌC ĐƯỢC SERVER LẦN NÀO → MỞ TỪ CHẶNG ①. Thà chơi lại một chặng
          còn hơn bỏ qua một chặng trẻ chưa từng học.
       ⚠️ Xong cả nhiệm vụ → cũng từ chặng ①: đó là lượt "Chơi lại".
       ⚠️ `?step=<id>` — cây chặng mở đúng một chặng. `RUN.openAt()` KẸP theo số
          chặng đã mở, nên gõ tay một chặng chưa mở vào thanh URL cũng không vượt
          được: địa chỉ là thứ ai cũng sửa được. */
    function resumeSteps() {
      try {
        var q = new URLSearchParams(location.search);
        if (q.get("restart") === "1") return;
        if (!global.AstroQProgress || !global.AstroQProgress.missionSteps) return;
        var p = global.AstroQProgress.missionSteps(mission);
        if (!p.known) return;
        serverDone = new Set(p.done.map(String));

        /* Số chặng ĐÃ MỞ = đoạn đầu liền mạch. Cùng phép đếm với `RUN.resume()`
           và với cây chặng — ba chỗ nói ba con số khác nhau là lỗi trẻ thấy ngay. */
        var unlocked = 0;
        while (unlocked < stepIds.length && serverDone.has(stepIds[unlocked])) unlocked++;

        var want = q.get("step");
        var k = want ? stepIds.indexOf(want) : -1;

        if (p.complete && k < 0) return;

        var open = p.complete ? 0 : RUN.resume(p.done);
        if (k >= 0) open = RUN.openAt(k, unlocked);
        if (open > 0 && !serverDone.has(stepIds[open])) {
          toast(T("resumed").replace("{n}", open + 1).replace("{t}", RUN.total));
        }
      } catch (e) {
        /* Cache hỏng / localStorage bị chặn → mở từ chặng ①. Không được để việc
           đọc một bản sao TUỲ CHỌN làm vỡ cả nhiệm vụ. */
        console.warn("[AstroQ] Không đọc được tiến độ nhiệm vụ:", e && e.message);
      }
    }

    /* ───────────────────── Sự kiện ───────────────────── */
    function wire() {
      $("say-next").addEventListener("click", function () {
        $("say-next").classList.add("hide");
        var r = sayResolve; sayResolve = null;
        if (r) r();
      });

      $("mute").addEventListener("click", function () {
        var off = !global.AstroQSfx.on();
        try { localStorage.setItem("astroq-sfx", off ? "on" : "off"); } catch (e) {}
        paintMute();
        if (off) sfx("beep", 880);   // bật lại thì kêu một tiếng cho biết đã bật
      });

      /* ⚠️ ĐƯỜNG VỀ LÀ CÂY CHẶNG, KHÔNG PHẢI DASHBOARD. Cây chặng là nhà của
         nhiệm vụ: từ đó về bản đồ → Trung Tâm Nhiệm Vụ → dashboard là một chuỗi
         liền mạch, mỗi bước lùi một tầng. */
      $("back").addEventListener("click", function () { location.href = treeUrl(); });

      /* ⚠️ Bấm ra ngoài hộp và Escape đều là CHỌN DỪNG, cùng nghĩa với nút "Để
         lần sau" — hai cách đóng cho ra hai kết quả khác nhau là chỗ trẻ học sai
         một lần rồi ngại bấm mãi. Tiến độ đã ghi lên server TRƯỚC khi hộp mở. */
      $("af-next").addEventListener("click", function () { closeAsk(); RUN.next(); });
      $("af-stop").addEventListener("click", function () { closeAsk(); location.href = treeUrl(); });
      $("after").addEventListener("click", function (e) {
        if (e.target === $("after")) $("af-stop").click();
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && $("after").classList.contains("show")) $("af-stop").click();
      });

      /* Tắt đường về tự động khi trẻ tương tác. Gắn trên CẢ thẻ modal, không chỉ
         trên nút — trẻ di chuột vào để đọc cũng là một tín hiệu "tôi đang xem". */
      ["pointerdown", "keydown", "mouseenter", "touchstart"].forEach(function (ev) {
        $("win").addEventListener(ev, cancelAuto, { passive: true });
      });

      $("win-missions").addEventListener("click", function () { location.href = "missions.html"; });
      $("win-awards").addEventListener("click", function () { location.href = "achievements.html"; });
      $("win-home").addEventListener("click", function () { location.href = "dashboard.html"; });

      /* ⚠️ SỐ LIỆU LẤY ĐÚNG TỪ CÁC Ô ĐÃ HIỆN TRÊN MÀN TỔNG KẾT, không tính lại:
         tính lại là hai nơi giữ một con số, và thẻ khoe sẽ nói khác bảng tổng kết
         vào ngày ai đó đổi cách tính. Chỗ nào chưa đọc được thì ô đó đã là dấu
         "—" sẵn — thẻ cũng hiện "—", không bao giờ bịa một con số 0. */
      $("win-brag").addEventListener("click", function () {
        if (!global.AstroQBrag) return;
        var txt = function (id) { var el = $(id); return el ? el.textContent.trim() : "—"; };
        var badgeRow = $("win-rw-badges");
        var lines = [
          { ic: "☄️", k: T("brag_tt"),    v: txt("win-rw-tt") },
          { ic: "⭐", k: T("brag_xp"),    v: txt("win-rw-xp") },
          { ic: "📘", k: T("brag_codex"), v: txt("win-rw-codex") }
        ];
        if (badgeRow && !badgeRow.classList.contains("hide")) {
          lines.push({ ic: "🏅", k: T("brag_badge"), v: txt("win-badges") });
        }
        global.AstroQBrag.open({
          lang: langOf(), tag: T("brag_tag"), badge: "🎖️",
          title: txt("win-h"), sub: txt("win-badge-sub"),
          lines: lines, note: T("brag_note")
        });
      });
    }

    /** Vẽ lại mọi chữ VỎ sở hữu. Gọi mỗi lần đổi ngôn ngữ. */
    function applyLang() {
      $("back-t").textContent = T("back");
      $("tag").textContent = pageT("tag");
      $("obj-k").textContent = T("obj_k");
      $("card-ok").textContent = T("card_ok");
      $("say-next").textContent = T("next");
      $("load-txt").textContent = T("load_txt");
      $("steps").setAttribute("aria-label", T("a_steps"));
      $("cur").setAttribute("title", T("tt_name"));
      $("cur").querySelector("img").setAttribute("alt", T("tt_name"));
      $("mute").setAttribute("title", T("a_sfx"));
      $("mute").setAttribute("aria-label", T("a_sfx"));
      document.querySelector(".lang-switch").setAttribute("aria-label", T("a_lang"));
      /* Chữ tĩnh của màn tổng kết vẽ LUÔN, kể cả khi nó chưa mở — xem khối cảnh báo
         ở `paintWinStatic`. Phần SỐ (thưởng) thì chỉ có nghĩa khi đã báo xong server,
         nên nó nằm trong `showWin`. */
      paintWinStatic();
      /* Màn tổng kết và hộp hỏi có thể ĐANG MỞ lúc trẻ đổi ngôn ngữ ở tab khác —
         vẽ lại cả phần số chứ không chỉ phần chữ. */
      if ($("win").classList.contains("show")) showWin();
      if ($("after").classList.contains("show")) {
        var cur = RUN ? RUN.step : null;
        if (cur) openAsk(cur, serverDone.has(cur));
      }
    }

    /** Báo cho vỏ biết trình điều phối. Gọi ngay sau `AstroQMission.create`. */
    function attach(run) { RUN = run; }

    return {
      mount: mount,
      attach: attach,
      applyLang: applyLang,
      resumeSteps: resumeSteps,

      toast: toast,
      paintBalance: paintBalance,
      paintMute: paintMute,
      sfx: sfx,

      say: say,
      hideSay: hideSay,

      objective: objective,
      progress: progress,
      hideObjective: hideObjective,

      showCard: showCard,
      liftCard: liftCard,

      dragDrop: dragDrop,
      nudge: nudge,
      buildAsk: buildAsk,

      showWin: showWin,
      afterStep: afterStep,
      treeUrl: treeUrl,

      /* Bề mặt cho bộ kiểm thử tự động. CHỈ điều khiển và đọc trạng thái —
         không cấp thưởng, không bỏ qua chặng nào. */
      get autoLeft() { return autoLeft; },
      get askOpen() { return $("after").classList.contains("show"); },
      askNext: function () { $("af-next").click(); return true; },
      askStop: function () { $("af-stop").click(); return true; },
      sayNext: function () { $("say-next").click(); return true; },
      /** ⚠️ KHÔNG trả Promise: `page.evaluate` của Playwright tự chờ promise
          được trả về, mà `showWin` là async → script test treo thay vì báo hỏng. */
      win: function () { showWin(); return true; }
    };
  }

  global.AstroQStage = { create: create };
})(window);
