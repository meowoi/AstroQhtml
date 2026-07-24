/* ============================================================
   AstroQ — Hệ thống số dư "Thiên thạch tím" (Purple Asteroids)
   Tiền tệ trong ứng dụng: kiếm được khi trả lời đúng quiz,
   tiêu khi vào chơi game. Lưu bền bằng localStorage.

   Cách dùng:
     <script src="economy.js"></script>
     Economy.getAsteroids();        // đọc số dư (mặc định 50 nếu mới)
     Economy.addAsteroids(10);      // cộng khi trả lời đúng
     Economy.useAsteroids(20);      // trừ khi vào game → true/false
   Hình ảnh đại diện: img/tt.png
   ============================================================ */
(function (global) {
  'use strict';

  var STORAGE_KEY = 'astroq-asteroids'; // khoá localStorage
  var DEFAULT_BALANCE = 50;             // số dư khi người dùng mới vào
  var ASTEROID_IMG = 'img/tt.png';      // ảnh thiên thạch tím

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
   * Lần đầu (chưa có dữ liệu) sẽ khởi tạo = DEFAULT_BALANCE (50).
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
     TIỆN ÍCH BỔ SUNG (tuỳ chọn)
     ========================================================== */

  /** Đặt lại số dư về mặc định (50). */
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
