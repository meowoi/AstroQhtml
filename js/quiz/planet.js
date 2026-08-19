/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "planet",
  topic: { vi: "HÀNH TINH",
           en: "PLANET" },
  q: { vi: "Ngoài việc quay quanh Mặt Trời và có dạng gần tròn, IAU còn đòi một hành tinh phải làm được điều gì?",
       en: "Besides orbiting the Sun and being nearly round, what third thing does the IAU require of a planet?" },
  opts: [
    { vi: "Dọn sạch các vật thể cùng cỡ quanh quỹ đạo của nó",
      en: "Clear away other objects of similar size near its orbit" },
    { vi: "Có ít nhất một vệ tinh",
      en: "Have at least one moon" },
    { vi: "Có khí quyển để thở",
      en: "Have a breathable atmosphere" },
    { vi: "Tự phát ra ánh sáng",
      en: "Make its own light" }
  ],
  a: 0,
  ok: { vi: "Chuẩn! Tiêu chí thứ ba của IAU (2006) là <b>“dọn sạch vùng quỹ đạo”</b>: hành tinh phải đủ nặng để lực hấp dẫn của nó hút hoặc đẩy hết các vật thể cùng cỡ ra khỏi đường bay.",
        en: "Exactly! The IAU's third criterion (2006) is <b>“clearing the neighbourhood”</b>: a planet must be massive enough that its gravity has swept away other objects of similar size along its orbit." },
  no: { vi: "Chưa đúng! Tiêu chí thứ ba là <b>dọn sạch vùng quỹ đạo</b> — không liên quan tới vệ tinh hay khí quyển. Hành tinh cũng không tự phát sáng, nó chỉ phản chiếu ánh sáng ngôi sao.",
        en: "Not quite! The third criterion is <b>clearing its orbital neighbourhood</b> — nothing about moons or air. Planets don't make light either; they reflect their star's." },
  hint: { vi: "Nghĩ tới cái sân: hành tinh phải <b>dọn sạch sân</b> của mình.",
          en: "Think of a playground: a planet has to <b>sweep its own yard</b> clean." },
  lv: 3,
  src: "dwarf"
};
