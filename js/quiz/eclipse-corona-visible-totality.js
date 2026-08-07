/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-corona-visible-totality",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Tại sao con người có thể quan sát thấy vành nhật hoa phát sáng bằng mắt thường trong kỳ nhật thực toàn phần?",
       en: "Why can people observe the glowing corona during a total solar eclipse?" },
  opts: [
    { vi: "Vì Mặt Trăng đã che khuất ánh chói lọi của bề mặt Mặt Trời",
      en: "Because the Moon blocks out the bright light of the Sun's surface" },
    { vi: "Vì vành nhật hoa tự nhiên bùng phát nóng hơn 100 lần",
      en: "Because the corona naturally bursts 100 times hotter" },
    { vi: "Vì Trái Đất tiến lại gần Mặt Trời hơn",
      en: "Because Earth moves closer to the Sun" },
    { vi: "Vì bầu khí quyển Trái Đất biến thành kính hiển vi",
      en: "Because Earth's atmosphere acts as a microscope" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Bình thường bề mặt quá rực rỡ che lấp vành nhật hoa; khi Mặt Trăng chắn ánh sáng bề mặt, vành nhật hoa trắng mờ hiện ra.",
        en: "Correct! When the Moon blocks the intense surface glare, the faint white corona emerges." },
  no: { vi: "Chưa đúng. Ánh sáng bề mặt quá mạnh bình thường làm lóa mắt; khi bị che đi vành nhật hoa mới lộ rõ.",
        en: "Incorrect. Normal surface glare hides the faint corona until blocked by the Moon." },
  hint: { vi: "Mặt Trăng đóng vai trò như một đĩa chắn sáng che đi phần đĩa rực rỡ.",
          en: "The Moon acts like an occulting disk blocking the bright solar face." },
  lv: 2,
  src: "nasaSunCorona",
  srcQuote: "During a total solar eclipse, the moon passes between Earth and the Sun. When this happens, the moon blocks out the bright light of the Sun.",
  srcChecked: "2026-08-06"
};
