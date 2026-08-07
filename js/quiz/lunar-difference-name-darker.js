/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "lunar-difference-name-darker",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Mẹo đơn giản nhất để phân biệt Nhật thực và Nguyệt thực qua tên gọi là gì?",
       en: "What is an easy way to remember the difference between a solar and lunar eclipse by name?" },
  opts: [
    { vi: "Tên gọi cho biết thiên thể nào bị tối đi: nhật thực thì Mặt Trời tối, nguyệt thực thì Mặt Trăng tối",
      en: "The name tells you what gets darker: in a solar eclipse the Sun gets darker, in a lunar eclipse the Moon gets darker" },
    { vi: "Tên gọi cho biết thiên thể nào biến thành màu xanh",
      en: "The name tells you which body turns blue" },
    { vi: "Tên gọi cho biết hiện tượng diễn ra ở mùa nào",
      en: "The name tells you which season it occurs in" },
    { vi: "Tên gọi không mang ý nghĩa nào",
      en: "The name holds zero meaning" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tên gọi chỉ rõ đối tượng bị tối đi: Nhật thực thì Mặt Trời (Nhật) tối, Nguyệt thực thì Mặt Trăng (Nguyệt) tối.",
        en: "Correct! The name indicates what darkens: solar = Sun darkens, lunar = Moon darkens." },
  no: { vi: "Chưa đúng. Hãy nhớ quy tắc: tên gọi chỉ ra chính thiên thể bị che tối trong hiện tượng.",
        en: "Incorrect. Remember the simple rule: the name reveals which body gets darker." },
  hint: { vi: "Nhật có nghĩa là Mặt Trời, Nguyệt có nghĩa là Mặt Trăng.",
          en: "Solar refers to the Sun, and lunar refers to the Moon." },
  lv: 3,
  src: "nasaSpaceplaceEclipses",
  srcQuote: "The name tells you what gets darker when the eclipse happens. In a solar eclipse, the Sun gets darker. In a lunar eclipse, the Moon gets darker.",
  srcChecked: "2026-08-06"
};
