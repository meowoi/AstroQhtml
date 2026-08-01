/* ============================================================
   js/mission-engine.js — TRÌNH ĐIỀU PHỐI BƯỚC, dùng chung cho MỌI nhiệm vụ.

   Nạp như script thường (KHÔNG phải module), trước script chính của trang:
     <script src="js/mission-engine.js"></script>

   ⚠️ VÌ SAO CÓ FILE NÀY (31/07/2026 — bước 2 của `docs/decisions/002`)
   ─────────────────────────────────────────────────────────────
   Nhiệm vụ Trái Đất đã có sẵn một sổ đăng ký bước rất đúng hình dạng
   (`const steps = { scan:{}, timeline:{}, … }` chạy bằng `STEP_IDS[]` +
   `stepIdx`) — nhưng nó nằm LỌT THỎM trong 1.700 dòng của
   `mission-earth.html`, nên nhiệm vụ thứ hai muốn dùng lại thì chỉ còn
   cách chép. File này bê nguyên phần điều phối ra ngoài, KHÔNG đổi
   hành vi: cùng thứ tự, cùng điều kiện, cùng chỗ chờ mạng.

   Nhiệm vụ chỉ còn phải khai NỘI DUNG (`steps`) và cảnh của riêng nó.

   ────────────────────── CÁCH DÙNG ──────────────────────
     var RUN = AstroQMission.create({
       mission : "earth",              // khoá nhiệm vụ ở Services/Missions.cs
       stepIds : ["scan", "timeline"], // ĐÚNG THỨ TỰ CHƠI
       steps   : steps,                // sổ đăng ký bước của trang
       stepsEl : document.getElementById("steps"),  // dãy chấm tiến độ
       codexTotal: 9,                  // số tạm cho tới khi server trả số thật
       t       : t,                    // hàm dịch của trang
       toast   : toast,
       onBalance: paintBalance,        // gọi sau mỗi lần báo bước
       onWin   : showWin               // hết bước cuối
     });
     RUN.paint();  await RUN.enter();  // vào bước đầu

   MỘT BƯỚC là một object, mọi móc đều TUỲ CHỌN:
     enter()        dựng cảnh + mục tiêu khi vào bước
     pick(ev)       nhận cú chạm vào cảnh
     tick()         chạy đều đặn nếu bước cần theo dõi liên tục
     outro()        diễn hiệu ứng ăn mừng khi xong
     afterReport()  chạy SAU khi server đã trả lời (xem thứ tự dưới đây)

   ⚠️ THỨ TỰ TRONG `finish()` LÀ CÓ LÝ DO, ĐỪNG ĐẢO:
        outro()  →  báo server  →  afterReport()  →  bước kế
     · `outro()` chạy TRƯỚC khi báo server: hiệu ứng phải nổ ra ngay,
       không được đứng chờ mạng. Thưởng hiện lên trong lúc trẻ đang xem.
     · `afterReport()` là chỗ duy nhất đọc được thứ server vừa trả (ví dụ
       bước `eco` khoe huy hiệu vừa mở). Gộp nó vào `outro()` là đọc
       `reward.badges` lúc còn rỗng.

   ⚠️ KHÔNG CÓ CON SỐ THƯỞNG NÀO TRONG FILE NÀY. Client chỉ gửi
   `{mission, step}`; `Services/Missions.cs` tra bảng rồi cộng. Toàn bộ
   `reward` dưới đây là BẢN SAO của thứ server trả về để vẽ màn tổng kết —
   không phải chỗ tính toán. Thêm một phép cộng vào đây là mở đường cho
   client tự bịa thưởng.
   ============================================================ */
(function (global) {
  "use strict";

  function create(cfg) {
    var mission   = cfg.mission;
    var stepIds   = (cfg.stepIds || []).slice();
    var steps     = cfg.steps || {};
    var stepsEl   = cfg.stepsEl || null;
    var t         = cfg.t         || function (k) { return k; };
    var toast     = cfg.toast     || function () {};
    var onBalance = cfg.onBalance || function () {};
    var onWin     = cfg.onWin     || function () {};

    var idx    = 0;
    var done   = new Set();
    var reward = { meteors: 0, xp: 0, codex: 0,
                   codexTotal: cfg.codexTotal || 0, badges: [] };

    /** Bước đang chạy, hoặc `undefined` nếu id không có trong sổ đăng ký. */
    function current() { return steps[stepIds[idx]]; }

    /* ───────── Dãy chấm tiến độ ─────────
       Chấm ĐÃ XONG · chấm ĐANG LÀM · gạch nối sáng khi bước trước đã xong. */
    function paint() {
      if (!stepsEl) return;
      var html = "";
      for (var i = 0; i < stepIds.length; i++) {
        if (i) html += '<span class="l' + (done.has(stepIds[i - 1]) ? " ok" : "") + '"></span>';
        var cls = done.has(stepIds[i]) ? "ok" : (i === idx ? "now" : "");
        html += '<span class="s ' + cls + '"></span>';
      }
      stepsEl.innerHTML = html;
    }

    /* ───────── Báo một bước đã xong lên server ─────────
       Không bao giờ ném lỗi ra ngoài: `AstroQProgress` đã nuốt lỗi mạng và
       xếp hàng chờ, còn ở đây thiếu module thì trả về một kết quả "không ok"
       chứ không làm vỡ luồng chơi. Mất mạng KHÔNG được chặn trẻ đi tiếp. */
    function report(step) {
      if (!global.AstroQProgress || !global.AstroQProgress.missionStep) {
        return Promise.resolve({ ok: false, reason: "no-module" });
      }
      return global.AstroQProgress.missionStep(mission, step).then(function (r) {
        if (r && r.ok && r.data) {
          if (typeof r.data.awarded  === "number") reward.meteors += r.data.awarded;
          if (typeof r.data.xpGained === "number") reward.xp      += r.data.xpGained;
          /* Huy hiệu do SERVER mở (`Achievements.NewlyEarned`) — client chỉ GHI LẠI
             để hiện thẻ chúc mừng, không bao giờ tự thêm id vào đây. Chưa đăng nhập
             hoặc mất mạng thì danh sách rỗng và trang không nhận là đã mở được cái nào. */
          if (Array.isArray(r.data.newBadges)) {
            r.data.newBadges.forEach(function (b) {
              if (typeof b === "string" && reward.badges.indexOf(b) < 0) reward.badges.push(b);
            });
          }
          var m = r.data.missions && r.data.missions[mission];
          if (m) {
            reward.codex      = (m.codex || []).length;
            reward.codexTotal = m.codexTotal || reward.codexTotal;
          }
          if (r.data.awarded > 0) toast("+" + r.data.awarded + " {tt}");
        } else if (r && r.queued) {
          toast(t("saved_off"));
        }
        onBalance();
        return r;
      });
    }

    /** Vào bước đang trỏ tới (gọi một lần lúc mở màn). */
    function enter() {
      var st = current();
      return st && st.enter ? st.enter() : Promise.resolve();
    }

    /** Chốt một bước. Gọi lại lần hai cho cùng id thì không làm gì. */
    function finish(id) {
      if (done.has(id)) return Promise.resolve();
      done.add(id);
      paint();
      var st = steps[id];
      return Promise.resolve(st && st.outro ? st.outro() : null)
        .then(function () { return report(id); })
        .then(function () { return st && st.afterReport ? st.afterReport() : null; })
        .then(function () { return next(); });
    }

    /** Sang bước kế; hết bước thì gọi `onWin`. */
    function next() {
      if (idx >= stepIds.length - 1) return Promise.resolve(onWin());
      idx++;
      paint();
      var st = current();
      return Promise.resolve(st && st.enter ? st.enter() : null);
    }

    /* Chuyển cú chạm / nhịp theo dõi cho ĐÚNG bước đang chạy. Bước không khai
       móc thì bỏ qua — trang không phải tự kiểm tra `if (st && st.pick)`. */
    function pick(ev) { var st = current(); if (st && st.pick) st.pick(ev); }
    function tick()   { var st = current(); if (st && st.tick) st.tick(); }

    return {
      /** Id bước đang chạy. */
      get step()   { return stepIds[idx]; },
      /** Vị trí bước đang chạy (0-based). */
      get index()  { return idx; },
      /** Các bước đã xong TRONG lượt này. */
      get done()   { return Array.from(done); },
      /** Bản sao thưởng server đã trả — đọc để vẽ màn tổng kết. */
      get reward() { return { meteors: reward.meteors, xp: reward.xp,
                              codex: reward.codex, codexTotal: reward.codexTotal,
                              badges: reward.badges.slice() }; },
      get total()  { return stepIds.length; },
      current: current,
      paint: paint,
      enter: enter,
      finish: finish,
      next: next,
      pick: pick,
      tick: tick
    };
  }

  global.AstroQMission = { create: create };
})(window);
