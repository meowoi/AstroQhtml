/* ============================================================
   sfx.js — ÂM THANH DỰNG BẰNG WEBAUDIO, dùng chung.

   Vì sao tách ra: `js/mission-intro.js` (**đã xoá 01/08/2026**) đã dựng tiếng động
   cơ + bip radar bằng WebAudio, rồi `mission-earth.html` lại cần bip khi chạm điểm
   quét, tiếng "quét xong", tiếng thu được mẫu vật và nhạc khải hoàn. Chép lại đoạn
   `AudioContext` + `sfxOn()` sang trang thứ hai là chắc chắn có ngày hai bên lệch
   nhau — nhất là chỗ tôn trọng lựa chọn TẮT TIẾNG.
   Lý do đó KHÔNG mất theo file đã xoá: 3 mini-game + `mission-earth.html` vẫn dùng
   chung file này, và MỘT lựa chọn tắt tiếng cho cả app vẫn là điều phải giữ.

   MỘT lựa chọn tắt tiếng cho cả app: `localStorage["astroq-sfx"] === "off"`
   (đúng khoá 3 mini-game đang dùng, nút Âm thanh ở css/game-shell.css).

   KHÔNG tải file âm thanh nào — mọi tiếng đều sinh bằng dao động, đúng cách các
   mini-game đang làm. Toàn bộ bọc try/catch: trình duyệt chặn autoplay hoặc
   không có WebAudio thì trang vẫn chạy bình thường, chỉ là im tiếng.

     <script src="js/sfx.js"></script>
     AstroQSfx.beep();                       // bip ngắn
     AstroQSfx.tone({ f: 660, to: 990, dur: .18 });
     AstroQSfx.arp([523, 659, 784, 1047]);   // chuỗi nốt đi lên
     AstroQSfx.fanfare();                    // nhạc khải hoàn
     AstroQSfx.rumble({ ms: 900 });          // tiếng ù trầm, TỰ TẮT sau 900ms
     AstroQSfx.hush();                       // tắt ngay mọi tiếng ù đang sống
   ============================================================ */
(function (global) {
  "use strict";

  var LS_SFX = "astroq-sfx";
  var AC = null;

  /** Người dùng có đang bật tiếng không. */
  function on() {
    try { return localStorage.getItem(LS_SFX) !== "off"; } catch (e) { return true; }
  }

  /**
   * AudioContext dùng chung cho cả trang. Một context cho tất cả: mỗi
   * `new AudioContext()` là một tài nguyên hệ thống, mở nhiều thì Chrome cảnh
   * báo và cuối cùng từ chối tạo thêm.
   */
  function ctx() {
    if (AC) return AC;
    try {
      var C = global.AudioContext || global.webkitAudioContext;
      if (!C) return null;
      AC = new C();
    } catch (e) { AC = null; }
    return AC;
  }

  /** Đánh thức context — trình duyệt treo nó cho tới khi người dùng có tương tác. */
  function wake() {
    var c = ctx();
    if (c && c.state === "suspended") { try { c.resume(); } catch (e) {} }
    return c;
  }

  /**
   * Một nốt.
   * @param {{f:number, to?:number, dur?:number, type?:string, gain?:number,
   *          delay?:number, lp?:number}} o
   *   f = tần số đầu · to = tần số cuối (trượt) · dur = giây · type = dạng sóng
   *   gain = biên độ (0..1) · delay = giây chờ trước khi phát · lp = lọc thông thấp
   */
  function tone(o) {
    if (!on()) return;
    var c = wake(); if (!c) return;
    o = o || {};
    try {
      var t = c.currentTime + (o.delay || 0);
      var dur = o.dur != null ? o.dur : 0.16;
      var osc = c.createOscillator();
      var g = c.createGain();
      osc.type = o.type || "sine";
      osc.frequency.setValueAtTime(o.f || 660, t);
      if (o.to) osc.frequency.exponentialRampToValueAtTime(Math.max(1, o.to), t + dur);

      var tail = g;
      if (o.lp) {
        var lp = c.createBiquadFilter();
        lp.type = "lowpass"; lp.frequency.value = o.lp;
        g.connect(lp); tail = lp;
      }
      var peak = o.gain != null ? o.gain : 0.05;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(peak, t + Math.min(0.02, dur * 0.2));
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);

      osc.connect(g); tail.connect(c.destination);
      osc.start(t); osc.stop(t + dur + 0.02);
    } catch (e) {}
  }

  /** Bip radar ngắn — dùng cho mỗi lần chạm đúng một điểm tín hiệu. */
  function beep(f) {
    tone({ f: f || 1180, dur: 0.16, gain: 0.05 });
  }

  /** Chuỗi nốt phát lần lượt. `step` = giây giữa hai nốt. */
  function arp(freqs, o) {
    o = o || {};
    var step = o.step != null ? o.step : 0.085;
    for (var i = 0; i < freqs.length; i++) {
      tone({
        f: freqs[i], dur: o.dur != null ? o.dur : 0.2,
        type: o.type || "triangle", gain: o.gain != null ? o.gain : 0.045,
        delay: (o.delay || 0) + i * step
      });
    }
  }

  /**
   * "Quét xong" — hai nốt đi lên rồi một nốt sáng, nghe như hệ thống báo sẵn sàng.
   * Cố ý KHÁC `fanfare` (dùng ở màn tổng kết) để trẻ phân biệt được "xong một
   * việc nhỏ" với "xong cả nhiệm vụ".
   */
  function ready() {
    arp([784, 1047, 1319], { step: 0.09, dur: 0.22, gain: 0.045 });
  }

  /** Thu được mẫu vật — tiếng "ting" tươi, cao dần. */
  function pickup() {
    tone({ f: 880, to: 1760, dur: 0.22, type: "triangle", gain: 0.05 });
    tone({ f: 1320, dur: 0.14, type: "sine", gain: 0.03, delay: 0.06 });
  }

  /** Thả sai ô ngọc — tiếng trầm NGẮN và NHẸ, không phải tiếng "sai" gay gắt. */
  function nope() {
    tone({ f: 300, to: 200, dur: 0.16, type: "sine", gain: 0.035 });
  }

  /** Mặt Trời bùng cháy — tiếng trầm dâng lên rồi bừng sáng. */
  function ignite() {
    tone({ f: 70, to: 240, dur: 1.1, type: "sawtooth", gain: 0.06, lp: 420 });
    arp([523, 659, 784, 1047], { step: 0.1, dur: 0.5, gain: 0.035, delay: 0.55 });
  }

  /** Nhạc khải hoàn ở màn tổng kết sứ mệnh: hợp âm rải + hợp âm đầy. */
  function fanfare() {
    // Đô–Mi–Sol–Đô cao, kiểu kèn báo thắng
    arp([523.25, 659.25, 783.99, 1046.5], { step: 0.13, dur: 0.42,
                                            type: "triangle", gain: 0.05 });
    // Hợp âm đầy đóng lại, ngân dài
    var t = 0.62;
    [523.25, 659.25, 783.99, 1046.5].forEach(function (f) {
      tone({ f: f, dur: 1.5, type: "triangle", gain: 0.032, delay: t });
    });
    tone({ f: 130.81, dur: 1.6, type: "sine", gain: 0.05, delay: t });   // nốt trầm nền
  }

  /**
   * Tiếng rầm rì liên tục (động cơ tàu). Trả về hàm để TẮT.
   * @returns {function():void}
   */
  /* Sổ đăng ký mọi tiếng ù ĐANG SỐNG, để `hush()` tắt được hết.
     ⚠️ CẦN CẢ HAI LỚP, không phải một: `ms` lo trường hợp thường (tiếng tự tắt),
        còn `hush()` lo lúc người chơi bấm "chơi lại" giữa lúc tiếng còn đang ù —
        không có nó thì tiếng của lượt TRƯỚC chồng lên lượt SAU. */
  var LIVE = [];

  /**
   * Tiếng ù trầm (động cơ hỏng / thua).
   *
   * ⚠️⚠️ MẶC ĐỊNH TỰ TẮT SAU `ms` (1200ms). TRƯỚC 22/08/2026 hàm này chạy VÔ HẠN
   *    và chỉ tắt khi người gọi nhớ gọi hàm dừng nó trả về — mà **cả hai người
   *    gọi trong dự án đều vứt hàm đó đi**, nên tiếng thua của Đường Đua Sao Chổi
   *    và Bắt Sao Băng ù mãi: qua bảng kết quả, qua cú bấm "Đua lại", suốt cả lượt
   *    sau, và mỗi lần thua lại cộng thêm một tiếng nữa. Một API mà cách dùng SAI
   *    lại là cách dùng NGẮN NHẤT thì sớm muộn ai cũng dùng sai — nên hướng mặc
   *    định phải là hướng an toàn.
   * ⚠️ Muốn tiếng ù CHẠY LIÊN TỤC (nền động cơ) thì truyền `ms: 0` và **phải** giữ
   *    hàm dừng nó trả về. Hôm nay không nơi nào cần thế.
   *
   * @param {{f1?:number,f2?:number,lp?:number,gain?:number,fade?:number,ms?:number}} [o]
   * @returns {Function} hàm dừng — gọi bao nhiêu lần cũng chỉ dừng một lần.
   */
  function rumble(o) {
    o = o || {};
    if (!on()) return function () {};
    var c = wake(); if (!c) return function () {};
    try {
      var ms = o.ms == null ? 1200 : o.ms;
      /* Ramp lên phải NGẮN HƠN thời gian sống, không thì tiếng bị cắt đúng lúc
         vừa lên tới đỉnh — nghe ra như tiếng bị đứt chứ không như một cú nện. */
      var fade = o.fade != null ? o.fade
               : (ms > 0 ? Math.min(0.3, ms / 1000 * 0.3) : 1.2);
      var g = c.createGain(); g.gain.value = 0.0001;
      var o1 = c.createOscillator(); o1.type = "sawtooth"; o1.frequency.value = o.f1 || 52;
      var o2 = c.createOscillator(); o2.type = "sine";     o2.frequency.value = o.f2 || 47;
      var lp = c.createBiquadFilter(); lp.type = "lowpass"; lp.frequency.value = o.lp || 240;
      o1.connect(lp); o2.connect(lp); lp.connect(g); g.connect(c.destination);
      o1.start(); o2.start();
      var peak = o.gain != null ? o.gain : 0.055;
      g.gain.linearRampToValueAtTime(peak, c.currentTime + fade);
      var stopped = false;
      var stop = function () {
        if (stopped) return;
        stopped = true;
        var k = LIVE.indexOf(stop); if (k >= 0) LIVE.splice(k, 1);
        try {
          g.gain.cancelScheduledValues(c.currentTime);
          g.gain.setValueAtTime(g.gain.value, c.currentTime);
          g.gain.linearRampToValueAtTime(0.0001, c.currentTime + 0.4);
          setTimeout(function () { try { o1.stop(); o2.stop(); } catch (e) {} }, 520);
        } catch (e) {}
      };
      LIVE.push(stop);
      if (ms > 0) setTimeout(stop, ms);
      return stop;
    } catch (e) { return function () {}; }
  }

  /** Tắt NGAY mọi tiếng ù đang sống. Gọi lúc bắt đầu một lượt mới. */
  function hush() {
    LIVE.slice().forEach(function (f) { try { f(); } catch (e) {} });
    LIVE.length = 0;
  }

  global.AstroQSfx = {
    on: on, ctx: ctx, wake: wake,
    tone: tone, beep: beep, arp: arp,
    ready: ready, pickup: pickup, nope: nope, ignite: ignite, fanfare: fanfare,
    rumble: rumble, hush: hush
  };
})(window);
