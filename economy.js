/* ============================================================
   AstroQ — Số dư "Thiên thạch tím" (Purple Meteors)

   ⚠️ TỪ 29/07/2026: localStorage chỉ còn là **CACHE**. Nguồn sự thật là ví trong
   DynamoDB (`PK=USER#<uid>, SK=WALLET`), đọc/ghi qua các route `/me/*`.

   PHÂN CÔNG (đọc trước khi sửa):
     · **PHÍ do SERVER quyết.** `Economy.spend("dodge")` chỉ gửi TÊN GAME lên;
       server tra bảng `Wallet.Fees` rồi trừ. Client không bao giờ gửi số tiền —
       gửi được thì ai cũng chơi miễn phí bằng cách gửi 0.
     · **THƯỞNG thì server đặt TRẦN.** `addAsteroids(n)` chỉ cộng vào cache cho
       giao diện phản hồi ngay; con số thật do `POST /me/progress` trả về và
       `setFromServer()` GHI ĐÈ lên cache. Nhờ vậy không bị cộng hai lần.
     · **Hàm đọc/ghi cache vẫn ĐỒNG BỘ** (`getAsteroids`, `useAsteroids`) để 3 game
       không phải đổi logic chặn phí — đợi mạng xong mới cho vào lượt thì lúc mạng
       yếu trẻ bấm mà không thấy gì xảy ra.

   Cách dùng:
     <script src="economy.js"></script>
     Economy.getAsteroids();        // đọc cache (đồng bộ, luôn có số để vẽ)
     Economy.spend("dodge");        // trừ phí một lượt — server quyết bao nhiêu
     Economy.addAsteroids(10);      // cộng LẠC QUAN, server sẽ ghi đè lại
     Economy.setFromServer(120);    // số dư thật từ server (js/progress.js gọi)
   Hình ảnh đại diện: img/tt.png
   ============================================================ */
(function (global) {
  'use strict';

  var STORAGE_KEY = 'astroq-asteroids'; // khoá localStorage (CACHE)

  /* ⚠️ PHẢI LÀ 0, KHỚP VỚI VÍ SERVER (`DynamoContext` tạo ví `meteors = 0`).
     Trước đây là 50 và đó là một SỐ DƯ ẢO: phi hành gia mới mở app trên máy sạch
     thấy 50 tt, bấm chơi được một lượt, rồi lời gọi `/me/*` đầu tiên gọi
     `setFromServer(0)` và số dư tụt về 0 ngay trước mắt — còn server thì từ chối
     trừ phí (409, ví đang 0). Pilot mới kiếm tt bằng cách LÀM QUIZ ĐẠT. */
  var DEFAULT_BALANCE = 0;
  var ASTEROID_IMG = 'img/tt.png';      // ảnh thiên thạch tím

  /* Phí mỗi lượt — BẢN SAO để hiện badge "5 / lượt" và chặn tại chỗ cho nhanh.
     Con số trừ THẬT do server quyết (Services/Wallet.cs `Fees`). Hai bên lệch thì
     server đúng: `setFromServer()` sẽ chỉnh lại cache ngay sau đó. */
  /* ⚠️ PHÍ SUY TỪ ĐỘ KHÓ — luật đầy đủ ở `Wallet.FeeByDiff` + `Wallet.Diff`:
     độ khó đo bằng "mất bao nhiêu thì hết lượt" (Dễ = không có cách nào thua ·
     Vừa = có nhiều lớp đệm · Khó = một lần chạm là hết), và phí = Dễ 3 / Vừa 4 /
     Khó 5. Bảng này chỉ là BẢN SAO để giao diện hiện phí trước khi gọi server —
     server vẫn là nơi quyết định trừ bao nhiêu. `check_pages` mục [3d] đối chiếu
     cả ba nơi (Wallet.cs · economy.js · mảng GAMES ở games.html). */
  var FEES = { constellation: 3, maze: 3, survival: 3,
             catch: 4, racer: 4, defender: 4, comms: 4, recycle: 4, units: 4,
             dodge: 5 };

  // Bộ nhớ dự phòng khi localStorage không dùng được (chế độ riêng tư…).
  var memoryBalance = null;

  /* ---- Chuẩn hoá amount về số nguyên không âm ---- */
  function normalize(amount) {
    var n = Math.floor(Number(amount));
    return (isNaN(n) || n < 0) ? 0 : n;
  }

  /* ---- Đọc/ghi thô với localStorage (an toàn khi bị chặn) ---- */
  function readRaw() {
    try {
      var v = global.localStorage.getItem(STORAGE_KEY);
      return v === null ? null : v;
    } catch (e) {
      return memoryBalance === null ? null : String(memoryBalance);
    }
  }

  function writeRaw(value) {
    memoryBalance = value;
    try {
      global.localStorage.setItem(STORAGE_KEY, String(value));
    } catch (e) { /* bỏ qua — đã có memoryBalance */ }
  }

  /* ---- Gán số dư + phát sự kiện để UI tự cập nhật ---- */
  function setAsteroids(value) {
    var v = normalize(value);
    writeRaw(v);
    try {
      global.dispatchEvent(new CustomEvent('asteroids:change', { detail: { balance: v } }));
    } catch (e) { /* môi trường không có CustomEvent — bỏ qua */ }
    return v;
  }

  /* ==========================================================
     API CHÍNH
     ========================================================== */

  /**
   * Lấy số lượng thiên thạch tím hiện tại.
   * Lần đầu (chưa có dữ liệu) sẽ khởi tạo = DEFAULT_BALANCE (0).
   * @returns {number}
   */
  function getAsteroids() {
    var raw = readRaw();
    if (raw === null) {
      return setAsteroids(DEFAULT_BALANCE); // khởi tạo lần đầu
    }
    var n = parseInt(raw, 10);
    return isNaN(n) || n < 0 ? setAsteroids(DEFAULT_BALANCE) : n;
  }

  /**
   * Cộng thêm thiên thạch (vd: khi trả lời đúng quiz).
   * @param {number} amount - số lượng cộng thêm (số nguyên dương)
   * @returns {number} số dư mới
   */
  function addAsteroids(amount) {
    var add = normalize(amount);
    return setAsteroids(getAsteroids() + add);
  }

  /**
   * Trừ thiên thạch (vd: khi vào chơi game).
   * @param {number} amount - chi phí cần trả
   * @returns {boolean} true nếu đủ và đã trừ; false nếu KHÔNG đủ (số dư giữ nguyên)
   */
  function useAsteroids(amount) {
    var cost = normalize(amount);
    var balance = getAsteroids();
    if (balance < cost) return false; // không đủ → không trừ
    setAsteroids(balance - cost);
    return true;
  }

  /* ==========================================================
     ĐỒNG BỘ VỚI SERVER
     ========================================================== */

  /**
   * Ghi số dư THẬT từ server vào cache. Gọi từ js/progress.js mỗi khi một route
   * `/me/*` trả về `wallet.meteors`.
   *
   * Đây là chỗ chữa lại mọi sai lệch: cộng lạc quan lúc trả lời đúng quiz, trừ
   * lạc quan lúc vào game, hay cache bị sửa bằng DevTools — tất cả đều bị con số
   * của server ghi đè.
   * @returns {number} số dư sau khi ghi
   */
  function setFromServer(meteors) {
    var n = Math.floor(Number(meteors));
    if (!isFinite(n) || n < 0) return getAsteroids();   // server trả rác → giữ cache
    if (n === getAsteroids()) return n;                 // không đổi → khỏi phát event
    return setAsteroids(n);
  }

  /** Phí một lượt theo bảng ở client (chỉ để hiện số + chặn tại chỗ). */
  function feeFor(game) {
    var f = FEES[String(game)];
    return typeof f === 'number' ? f : 0;
  }

  /**
   * Trừ phí một lượt chơi.
   *
   * Hai bước, cố ý tách rời:
   *   1. ĐỒNG BỘ — trừ cache và trả `true/false` ngay, để game chặn được lượt
   *      chơi mà không phải chờ mạng.
   *   2. BẤT ĐỒNG BỘ — nhờ js/progress.js gửi `POST /me/wallet/spend {game}`;
   *      server tra bảng phí của NÓ rồi trừ, và số dư trả về ghi đè lên cache.
   *
   * ⚠️ Nếu cache nói đủ mà server nói không đủ thì lượt chơi ĐÃ bắt đầu — không
   * chặn lại giữa lượt (làm vậy còn tệ hơn). Số dư được chỉnh về đúng ngay sau đó
   * nên lượt KẾ TIẾP bị chặn. Mất mạng thì việc trừ phí được xếp hàng chờ kèm
   * `opId`, gửi lại sau và server chống trừ hai lần.
   *
   * @param {string} game "dodge" | "defender" | "constellation"
   * @returns {boolean} true nếu cache đủ tiền và đã trừ
   */
  function spend(game) {
    var fee = feeFor(game);
    if (fee <= 0) return false;
    if (!useAsteroids(fee)) return false;               // cache không đủ → chặn ngay

    if (global.AstroQProgress && global.AstroQProgress.spend) {
      global.AstroQProgress.spend(game);                // fire-and-forget
    }
    return true;
  }

  /* ==========================================================
     TIỆN ÍCH BỔ SUNG (tuỳ chọn)
     ========================================================== */

  /** Đặt lại số dư về mặc định (0 — khớp ví server). */
  function resetAsteroids() { return setAsteroids(DEFAULT_BALANCE); }

  /** Lắng nghe thay đổi số dư. Trả về hàm huỷ đăng ký. */
  function onAsteroidsChange(callback) {
    if (typeof callback !== 'function') return function () {};
    var handler = function (e) { callback(e.detail ? e.detail.balance : getAsteroids()); };
    global.addEventListener('asteroids:change', handler);
    return function () { global.removeEventListener('asteroids:change', handler); };
  }

  /**
   * Gắn huy hiệu số dư (ảnh tt.png + số) vào một phần tử và tự cập nhật.
   * @param {HTMLElement|string} target - phần tử hoặc id
   */
  function renderAsteroids(target) {
    var el = typeof target === 'string' ? document.getElementById(target) : target;
    if (!el) return;
    el.innerHTML =
      '<img src="' + ASTEROID_IMG + '" alt="Thiên thạch tím" ' +
      'style="width:1.4em;height:1.4em;object-fit:contain;vertical-align:middle;margin-right:.4em;" />' +
      '<span class="asteroid-count" style="font-weight:700;vertical-align:middle;"></span>';
    var countEl = el.querySelector('.asteroid-count');
    var paint = function (v) { countEl.textContent = v; };
    paint(getAsteroids());
    onAsteroidsChange(paint);
  }

  /* ==========================================================
     Xuất API
     ========================================================== */
  var Economy = {
    getAsteroids: getAsteroids,
    addAsteroids: addAsteroids,
    useAsteroids: useAsteroids,
    resetAsteroids: resetAsteroids,
    onAsteroidsChange: onAsteroidsChange,
    renderAsteroids: renderAsteroids,
    /* Đồng bộ server (xem khối "ĐỒNG BỘ VỚI SERVER" ở trên) */
    setFromServer: setFromServer,
    spend: spend,
    feeFor: feeFor,
    FEES: FEES,
    STORAGE_KEY: STORAGE_KEY,
    DEFAULT_BALANCE: DEFAULT_BALANCE,
    ASTEROID_IMG: ASTEROID_IMG
  };

  // Dùng như <script> thường: gắn vào window (kèm các hàm rời cho tiện).
  global.Economy = Economy;
  global.getAsteroids = getAsteroids;
  global.addAsteroids = addAsteroids;
  global.useAsteroids = useAsteroids;

  // Hỗ trợ import kiểu module (CommonJS / bundler) nếu cần.
  if (typeof module !== 'undefined' && module.exports) module.exports = Economy;

})(typeof window !== 'undefined' ? window : this);
