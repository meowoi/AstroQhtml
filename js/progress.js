/* ============================================================
   progress.js — BÁO VIỆC ĐÃ LÀM lên server, và giữ một bản sao trong máy.

   Trang nào cũng nạp được (nhẹ, không phụ thuộc gì ngoài js/ui-common.js):
     <script src="js/progress.js"></script>

   Báo một việc đã làm — gọi ở đúng chỗ đã có sẵn "chốt lượt" của từng trang:
     AstroQProgress.quiz({ correct:4, total:5, meteors:40 });
     AstroQProgress.game({ game:"dodge", score:120, seconds:38, meteors:3 });
     AstroQProgress.lesson("ten-bai");
     AstroQProgress.planet("mars");

   Đọc lại để vẽ trang:
     AstroQProgress.load()   → Promise<{ ok, source:"server"|"local", data }>
     AstroQProgress.local()  → bản sao trong máy, đọc ngay không chờ mạng

   BỐN ĐIỀU QUAN TRỌNG
   ─────────────────────────────────────────────────────────────
   1. **Client KHÔNG tính XP, KHÔNG tự mở huy hiệu, KHÔNG quyết số tiền.** Chỉ gửi
      "đã làm gì"; server (Services/Achievements.cs, Services/Wallet.cs) quyết cộng
      bao nhiêu XP, mở huy hiệu nào, trừ phí bao nhiêu. Bản sao trong máy vì thế
      chỉ có BỘ ĐẾM THÔ, không có xp/badges tự tính.
   2. **Không bao giờ ném lỗi và không bao giờ chặn giao diện.** Game đang chạy
      thì việc nộp kết quả không được phép làm treo màn hình kết thúc lượt —
      gọi rồi đi tiếp, mạng hỏng thì thôi.
   3. **Mất mạng / chưa đăng nhập → xếp hàng chờ** trong localStorage; lần sau
      mở trang có phiên đăng nhập thì tự gửi lại (`flush()` chạy khi nạp file này).
   4. **Mỗi việc có `opId` riêng.** Gửi lại từ hàng chờ mà server đã xử lý xong
      (phản hồi mất giữa đường) thì không được cộng tiền / trừ phí lần hai — server
      dedupe theo `opId`. **Sinh opId MỘT LẦN lúc tạo việc**, không phải lúc gửi:
      sinh lúc gửi thì mỗi lần thử lại là một op mới và mất hết ý nghĩa.

   Số dư ví trả về từ mọi lời gọi được đẩy thẳng vào `Economy.setFromServer()` —
   đó là chỗ duy nhất chữa lại sai lệch giữa cache và ví thật.
   ============================================================ */
(function (global) {
  "use strict";

  var LS_LOCAL = "astroq-progress";        // bản sao bộ đếm để vẽ khi offline
  var LS_QUEUE = "astroq-progress-queue";  // việc chưa gửi được
  var MAX_QUEUE = 40;                      // đủ cho vài ngày offline, không phình vô hạn

  /** Mã lượt duy nhất, sinh MỘT LẦN lúc tạo việc (xem điều 4 ở đầu file). */
  function newOpId() {
    try {
      if (global.crypto && global.crypto.randomUUID) return global.crypto.randomUUID();
    } catch (e) {}
    return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 10);
  }

  /** Số dư ví thật từ server → ghi đè cache của economy.js. */
  function syncWallet(data) {
    if (!data || !data.wallet || !global.Economy || !global.Economy.setFromServer) return;
    global.Economy.setFromServer(data.wallet.meteors);
  }

  function read(key, fallback) {
    try {
      var v = localStorage.getItem(key);
      return v === null ? fallback : JSON.parse(v);
    } catch (e) { return fallback; }
  }
  function write(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {}
  }

  /* ---------------- Bản sao bộ đếm trong máy ---------------- */
  function emptyLocal() {
    return {
      quizTaken: 0, quizAnswered: 0, quizCorrect: 0, quizPerfect: 0,
      gamesPlayed: 0, lessonsRead: 0, flightSeconds: 0, meteorsEarned: 0,
      planets: [], bests: {}, lessons: []
    };
  }
  function localData() {
    var d = read(LS_LOCAL, null);
    if (!d || typeof d !== "object") return emptyLocal();
    var base = emptyLocal();
    for (var k in base) if (base.hasOwnProperty(k) && d[k] != null) base[k] = d[k];
    return base;
  }

  /** Cộng bản sao trong máy theo cùng sự kiện vừa gửi lên server. */
  function bumpLocal(ev) {
    var d = localData();
    if (ev.meteors > 0) d.meteorsEarned += ev.meteors;

    if (ev.type === "quiz") {
      d.quizTaken++;
      d.quizAnswered += ev.total || 0;
      d.quizCorrect  += ev.correct || 0;
      if ((ev.total || 0) > 0 && ev.correct === ev.total) d.quizPerfect++;
    } else if (ev.type === "game") {
      d.gamesPlayed++;
      d.flightSeconds += ev.seconds || 0;
      var g = ev.game || "?";
      if (!(d.bests[g] >= (ev.score || 0))) d.bests[g] = ev.score || 0;
    } else if (ev.type === "lesson") {
      // Chống đếm trùng giống server: một bài chỉ tính một lần
      if (d.lessons.indexOf(ev.id) === -1) { d.lessons.push(ev.id); d.lessonsRead++; }
    } else if (ev.type === "planet") {
      if (d.planets.indexOf(ev.id) === -1) d.planets.push(ev.id);
    }
    // type "mission": KHÔNG có bản sao trong máy. Bước nào đã xong, thưởng bao nhiêu
    // đều do server giữ — đoán ở client thì lúc mất mạng sẽ hiện thưởng chưa có thật.
    
    write(LS_LOCAL, d);
    return d;
  }

  /* ---------------- Hàng chờ ---------------- */
  function queue() { var q = read(LS_QUEUE, []); return Array.isArray(q) ? q : []; }
  function enqueue(ev) {
    var q = queue();
    q.push(ev);
    // Bỏ những việc CŨ NHẤT khi tràn: việc mới phản ánh trạng thái gần đây hơn
    if (q.length > MAX_QUEUE) q = q.slice(q.length - MAX_QUEUE);
    write(LS_QUEUE, q);
  }

  /** Có phiên đăng nhập + có API hay không. */
  function auth() {
    return global.AstroQAuth && global.AstroQAuth.postProgress ? global.AstroQAuth : null;
  }

  /** Gửi một việc trong hàng chờ tới đúng route của nó. */
  function send(a, item) {
    if (item && item.kind === "spend") {
      return a.spendWallet({ reason: "game", game: item.game, opId: item.opId });
    }
    if (item && item.type === "mission") {
      return a.missionStep({ mission: item.mission, step: item.step, opId: item.opId });
    }
    return a.postProgress(item);
  }

  /* Module ES js/firebase-auth.js chạy SAU các script cổ điển, nên lúc file này
     nạp xong thì AstroQAuth có thể chưa tồn tại. Chờ có hạn rồi mới kết luận. */
  function waitAuth(ms) {
    if (auth()) return Promise.resolve(auth());
    return new Promise(function (resolve) {
      var t0 = Date.now();
      var timer = setInterval(function () {
        if (auth() || Date.now() - t0 > ms) { clearInterval(timer); resolve(auth()); }
      }, 60);
    });
  }

  var flushing = false;

  /** Gửi lại những việc đang xếp hàng. Gọi được nhiều lần, tự bỏ qua nếu đang chạy. */
  function flush() {
    if (flushing) return Promise.resolve(false);
    var q = queue();
    if (q.length === 0) return Promise.resolve(true);

    flushing = true;
    return waitAuth(2500).then(function (a) {
      if (!a) { flushing = false; return false; }

      // Gửi lần lượt: server chống trùng theo từng việc, nhưng thứ tự vẫn nên
      // giữ đúng để kỷ lục và bộ đếm ra cùng kết quả như lúc chơi.
      var i = 0;
      function step() {
        if (i >= q.length) {
          write(LS_QUEUE, []);       // chỉ xoá hàng chờ khi đã gửi HẾT
          flushing = false;
          return true;
        }
        return send(a, q[i]).then(function (r) {
          if (!r || !r.ok) {
            // Vẫn hỏng → giữ lại phần chưa gửi, lần sau thử tiếp
            write(LS_QUEUE, q.slice(i));
            flushing = false;
            return false;
          }
          syncWallet(r.data);
          i++;
          return step();
        });
      }
      return step();
    }).catch(function () { flushing = false; return false; });
  }

  /** Gửi một việc. Luôn trả Promise, không bao giờ reject. */
  function report(ev) {
    ev.opId = ev.opId || newOpId();
    bumpLocal(ev);
    return waitAuth(2500).then(function (a) {
      if (!a) { enqueue(ev); return { ok: false, reason: "auth", queued: true }; }
      return send(a, ev).then(function (r) {
        if (!r || !r.ok) { enqueue(ev); return { ok: false, reason: (r && r.reason) || "http", queued: true }; }
        syncWallet(r.data);
        return r;
      });
    }).catch(function () {
      enqueue(ev);
      return { ok: false, reason: "error", queued: true };
    });
  }

  /**
   * Trừ phí một lượt chơi. Gọi từ `Economy.spend(game)` — đừng gọi trực tiếp,
   * không thì cache và ví lệch nhau.
   *
   * Chỉ gửi TÊN GAME; server tra bảng phí của nó. Mất mạng → xếp hàng chờ kèm
   * `opId` nên gửi lại không bị trừ hai lần.
   */
  function spendReport(game) {
    var item = { kind: "spend", game: String(game || ""), opId: newOpId() };
    return waitAuth(2500).then(function (a) {
      if (!a) { enqueue(item); return { ok: false, reason: "auth", queued: true }; }
      return a.spendWallet({ reason: "game", game: item.game, opId: item.opId })
        .then(function (r) {
          if (!r || !r.ok) {
            // 409 "insufficient" KHÔNG xếp hàng chờ: server đã trả lời rõ là không
            // đủ tiền, gửi lại chỉ nhận đúng câu đó. Chỉ xếp lại khi lỗi mạng.
            if (r && r.reason === "http" && r.code === "insufficient") {
              if (r.meteors != null && global.Economy) Economy.setFromServer(r.meteors);
              return r;
            }
            enqueue(item);
            return { ok: false, reason: (r && r.reason) || "http", queued: true };
          }
          syncWallet(r.data);
          return r;
        });
    }).catch(function () {
      enqueue(item);
      return { ok: false, reason: "error", queued: true };
    });
  }

  var AstroQProgress = {
    /**
     * Xong một lượt Quiz.
     * @param {{correct:number,total:number,meteors:number,terms?:string[]}} o
     *   `terms` = khoá thuật ngữ ĐÃ TRẢ LỜI ĐÚNG (khoá `term` của
     *   js/quiz-questions.js). Đây là DÂY NỐI để Sổ Tay Thuật Ngữ biết thẻ nào đã
     *   giải mã — thiếu nó thì mọi thẻ khoá vĩnh viễn, đúng tình trạng trước
     *   30/07/2026.
     */
    quiz: function (o) {
      o = o || {};
      var ev = { type: "quiz", correct: o.correct | 0, total: o.total | 0,
                 meteors: o.meteors | 0 };
      /* ⚠️ CHỈ GỬI KHI CÓ. `terms: []` là tập rỗng, mà string set của DynamoDB
         KHÔNG nhận tập rỗng — server đã chặn nhưng gửi thừa một trường rỗng trong
         mỗi lượt là mời lỗi. */
      if (o.terms && o.terms.length) ev.terms = o.terms.slice();
      return report(ev);
    },
    /** Xong một lượt game. `game` là khoá kỷ lục: "dodge" | "defender" | "constellation". */
    game: function (o) {
      o = o || {};
      return report({ type: "game", game: String(o.game || ""), score: o.score | 0,
                      seconds: o.seconds | 0, meteors: o.meteors | 0 });
    },
    /** Đọc xong một bài. Gọi bao nhiêu lần cũng chỉ tính một. */
    lesson: function (id) { return report({ type: "lesson", id: String(id || "") }); },
    /** Ghé một hành tinh. Ghé lại không tính thêm. */
    planet: function (id) { return report({ type: "planet", id: String(id || "") }); },

    /** Trừ phí một lượt. Gọi qua `Economy.spend(game)`, không gọi trực tiếp. */
    spend: spendReport,

    /**
     * Báo XONG MỘT BƯỚC nhiệm vụ. Chỉ gửi `{mission, step}` — **không gửi con số
     * thưởng nào**; server tra Services/Missions.cs rồi cộng (đây là chỗ thưởng
     * không thể bịa, khác điểm game). Mất mạng → xếp hàng chờ kèm `opId`.
     */
    missionStep: function (mission, step) {
      return report({ type: "mission", mission: String(mission || ""),
                      step: String(step || "") });
    },

    /** Bản sao bộ đếm trong máy — đọc ngay, không chờ mạng. */
    local: localData,

    /** Số việc đang xếp hàng chờ gửi. */
    pending: function () { return queue().length; },

    /**
     * Lấy hồ sơ + tiến độ để vẽ trang.
     * → { ok, source:"server"|"local", data, reason? }
     * Server không trả lời được thì trả bộ đếm trong máy, kèm `source:"local"`
     * để trang tự hiện lời nhắc — hiện số cũ mà không nói gì là đánh lừa người dùng.
     */
    load: function () {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.getProfile) return { ok: false, source: "local", reason: "auth", data: localData() };
        return a.getProfile().then(function (r) {
          if (!r || !r.ok) {
            return { ok: false, source: "local", reason: (r && r.reason) || "http", data: localData() };
          }
          syncWallet(r.data);        // số dư thật → ghi đè cache của economy.js
          return { ok: true, source: "server", data: r.data };
        });
      }).catch(function () {
        return { ok: false, source: "local", reason: "error", data: localData() };
      });
    },

    /** Lấy kho thành tích (server là nơi quyết huy hiệu nào đã mở). */
    achievements: function () {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.getAchievements) return { ok: false, reason: "auth" };
        return a.getAchievements().then(function (r) {
          if (r && r.ok) syncWallet(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Lấy trạng thái NHIỆM VỤ (bước nào đã xong, mẫu Codex nào đã có, xong cả
     * nhiệm vụ chưa). Dùng cho Sảnh Nhiệm Vụ `missions.html`.
     *
     * Nhẹ hơn `achievements()` vì `GET /me/missions` chỉ trả đúng khối nhiệm vụ,
     * không kéo theo cả bộ huy hiệu — trang Sảnh không cần huy hiệu.
     *
     * Trả `{ ok:false, reason }` khi chưa đăng nhập / mất mạng; trang gọi phải
     * hiện dấu `—` chứ **không đoán số bước đã xong**, y như achievements.html.
     */
    missions: function () {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.getMissions) return { ok: false, reason: "auth" };
        return a.getMissions();
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Lấy Kho Mẫu Vật (server là nơi quyết mẫu nào đã thu thập — suy ra từ bộ đếm
     * tiến độ, không có đường ghi riêng).
     */
    specimens: function () {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.getSpecimens) return { ok: false, reason: "auth" };
        return a.getSpecimens().then(function (r) {
          if (r && r.ok) syncWallet(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Đặt mẫu vật lên bàn điều khiển khoang lái (tối đa 3). Đây là thứ DUY NHẤT
     * của kho mẫu vật mà client được quyết — nhưng server vẫn kiểm từng id phải
     * có thật và đã mở khoá.
     *
     * KHÔNG xếp hàng chờ như các việc khác: đây là lựa chọn trang trí, gửi lại
     * sau nhiều giờ thì có thể ghi đè lựa chọn mới hơn ở máy khác.
     */
    setDesk: function (ids) {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.setSpecimenDesk) return { ok: false, reason: "auth" };
        return a.setSpecimenDesk(ids);
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    /**
     * Lấy số dư ví thật rồi ghi đè cache. Dùng cho trang chỉ HIỆN số dư mà không
     * cần hồ sơ (games.html, các trang game) — nhẹ hơn gọi cả `/me/profile`.
     */
    syncWallet: function () {
      return waitAuth(2500).then(function (a) {
        if (!a || !a.getWallet) return { ok: false, reason: "auth" };
        return a.getWallet().then(function (r) {
          if (r && r.ok) syncWallet(r.data);
          return r;
        });
      }).catch(function () { return { ok: false, reason: "error" }; });
    },

    flush: flush,

    /** Xoá bản sao + hàng chờ trong máy (dùng khi đăng xuất / khi thử nghiệm). */
    clearLocal: function () {
      try { localStorage.removeItem(LS_LOCAL); localStorage.removeItem(LS_QUEUE); } catch (e) {}
    }
  };

  global.AstroQProgress = AstroQProgress;

  // Có việc đang chờ thì thử gửi lại ngay khi mở trang, và mỗi khi có mạng lại.
  if (queue().length > 0) flush();
  global.addEventListener("online", function () { flush(); });
})(window);
