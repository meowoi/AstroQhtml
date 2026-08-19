/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "comet-tail",
  topic: { vi: "SAO CHỔI",
           en: "COMET" },
  q: { vi: "Đuôi sao chổi luôn chỉ về hướng nào?",
       en: "Which way does a comet's tail always point?" },
  opts: [
    { vi: "Luôn chỉ thẳng vào Mặt Trời",
      en: "Straight toward the Sun" },
    { vi: "Luôn ngược hướng bay của sao chổi",
      en: "Always opposite its direction of travel" },
    { vi: "Luôn về phía Trái Đất",
      en: "Always toward Earth" },
    { vi: "Hướng ra xa Mặt Trời",
      en: "Away from the Sun" }
  ],
  a: 3,
  ok: { vi: "Đúng! Áp lực ánh sáng và gió Mặt Trời thổi bụi cùng khí <b>ra xa Mặt Trời</b>. Nghĩa là khi sao chổi đang bay ra khỏi Mặt Trời, cái đuôi lại <b>đi trước</b> nó!",
        en: "Correct! Sunlight pressure and the solar wind blow the dust and gas <b>away from the Sun</b>. So when a comet heads back out, its tail actually leads the way!" },
  no: { vi: "Chưa đúng! Đuôi bị gió Mặt Trời thổi <b>ra xa Mặt Trời</b> — nó không phụ thuộc vào hướng bay của sao chổi.",
        en: "Not quite! The tail is blown <b>away from the Sun</b> — it doesn't depend on which way the comet is moving." },
  hint: { vi: "Cứ hình dung có một cơn gió thổi từ Mặt Trời ra mọi phía.",
          en: "Picture a wind blowing outward from the Sun in every direction." },
  lv: 3,
  src: "comet"
};
