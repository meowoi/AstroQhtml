/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-moon-shadows-umbra-penumbra",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Trong diễn biến của một kỳ nhật thực ban ngày, bóng của Mặt Trăng đổ xuống Trái Đất theo trình tự nào?",
       en: "During the progression of a daytime solar eclipse, in what order do the Moon's shadows reach Earth?" },
  opts: [
    { vi: "Bóng nửa tối (penumbra) đến trước, tiếp theo bóng tối toàn phần (umbra) xuất hiện ở đỉnh điểm nhật thực",
      en: "The partial shadow (penumbra) arrives first, followed by the full shadow (umbra) at the height of the eclipse" },
    { vi: "Bóng tối toàn phần (umbra) xuất hiện trước, sau đó mới tới bóng nửa tối",
      en: "The full shadow (umbra) appears first, followed by the partial shadow" },
    { vi: "Cả hai bóng xuất hiện đồng thời cùng một giây",
      en: "Both shadows arrive at the exact same second" },
    { vi: "Chỉ có duy nhất bóng mờ xuất hiện, không có bóng tối",
      en: "Only a faint shadow appears with no dark shadow" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Khi Mặt Trăng lướt qua Mặt Trời, bóng nửa tối penumbra chạm vào Trái Đất trước, rồi bóng tối umbra mới xuất hiện ở pha đỉnh điểm.",
        en: "Correct! As the Moon passes, the partial penumbra touches Earth first, followed by the dark umbra at eclipse peak." },
  no: { vi: "Chưa đúng. Bóng phủ dần dần: bóng nửa tối mờ nhạt trùm trước, đến đỉnh nhật thực bóng tối umbra mới phủ kín.",
        en: "Incorrect. Shadow coverage builds progressively: the lighter penumbra hits first, then the deep umbra covers at peak." },
  hint: { vi: "Hãy nghĩ đến quá trình bóng mờ xuất hiện trước khi bầu trời tối sẫm hoàn toàn.",
          en: "Think about how partial darkness precedes total darkness during the event." },
  lv: 3,
  src: "exploratoriumEclipse",
  srcQuote: "During the day, as the moon passes in front of the Sun, it begins to cast a partial shadow (called the penumbra) onto Earth. At the height of the eclipse, the Sun's light is entirely blocked, and the moon casts a full shadow called the umbra.",
  srcChecked: "2026-08-06"
};
