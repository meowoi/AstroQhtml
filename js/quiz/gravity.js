/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "gravity",
  topic: { vi: "LỰC HẤP DẪN",
           en: "GRAVITY" },
  q: { vi: "Lực hấp dẫn của một hành tinh kéo các vật về đâu?",
       en: "Where does a planet's gravity pull objects toward?" },
  opts: [
    { vi: "Về phía tâm của hành tinh",
      en: "Toward the centre of the planet" },
    { vi: "Về phía cực Bắc",
      en: "Toward the North Pole" },
    { vi: "Ra xa khỏi hành tinh",
      en: "Away from the planet" },
    { vi: "Về phía ngôi sao gần nhất",
      en: "Toward the nearest star" }
  ],
  a: 0,
  ok: { vi: "Chính xác! NASA định nghĩa lực hấp dẫn là lực mà một hành tinh dùng để kéo các vật <b>về phía tâm của nó</b>. Vì thế em nhảy lên rồi lại rơi xuống sân.",
        en: "Correct! NASA defines gravity as the force by which a planet draws objects <b>toward its centre</b>. That's why you land back on the ground when you jump." },
  no: { vi: "Chưa đúng! Lực hấp dẫn kéo mọi vật <b>về phía tâm</b> của hành tinh — không phải về một cực, cũng không đẩy ra ngoài.",
        en: "Not quite! Gravity pulls everything <b>toward the centre</b> of the planet — not toward a pole, and it never pushes away." },
  hint: { vi: "Ở Việt Nam hay ở Nam Mỹ, thả tay ra là đồ vật đều rơi <b>xuống</b> — “xuống” là về hướng nào?",
          en: "In Vietnam or in South America, a dropped object always falls <b>down</b> — which direction is “down”?" },
  lv: 1,
  src: "grav"
};
