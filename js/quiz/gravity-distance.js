/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "gravity-distance",
  topic: { vi: "LỰC HẤP DẪN",
           en: "GRAVITY" },
  q: { vi: "Theo NASA, lực hấp dẫn thay đổi thế nào khi hai vật ở xa nhau hơn?",
       en: "According to NASA, what happens to gravity as two objects get farther apart?" },
  opts: [
    { vi: "Mạnh lên",
      en: "It gets stronger" },
    { vi: "Không đổi",
      en: "It stays the same" },
    { vi: "Yếu đi",
      en: "It gets weaker" },
    { vi: "Đổi chiều thành lực đẩy",
      en: "It flips into a push" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Hai điều quyết định lực hấp dẫn mạnh hay yếu: vật càng <b>nhiều khối lượng</b> thì lực càng lớn, và lực <b>yếu dần khi khoảng cách xa ra</b>.",
        en: "Right! Two things set how strong gravity is: objects with <b>more mass</b> have more gravity, and gravity <b>gets weaker with distance</b>." },
  no: { vi: "Chưa đúng! Càng xa thì lực hấp dẫn càng <b>yếu</b> — nó không bao giờ đổi thành lực đẩy.",
        en: "Not quite! The farther apart, the <b>weaker</b> gravity gets — and it never turns into a push." },
  hint: { vi: "Mặt Trời rất nặng, nhưng ở đây em không bị nó hút bay đi. Vì sao?",
          en: "The Sun is enormously massive, yet it doesn't yank you off the ground. Why not?" },
  src: "grav"
};
