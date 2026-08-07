/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "meteoroid-chain",
  topic: { vi: "THIÊN THẠCH NHỎ",
           en: "METEOROID" },
  q: { vi: "Ba từ meteoroid – meteor – meteorite khác nhau ở điểm nào?",
       en: "What actually distinguishes meteoroid, meteor and meteorite?" },
  opts: [
    { vi: "Khác nhau ở màu sắc của hòn đá",
      en: "The colour of the rock" },
    { vi: "Khác nhau ở thành phần hoá học",
      en: "Their chemical make-up" },
    { vi: "Khác nhau ở nơi vật thể đang ở: trong không gian, trong khí quyển, hay đã nằm trên mặt đất",
      en: "Where the object is: in space, in the atmosphere, or already on the ground" },
    { vi: "Khác nhau ở tên người tìm ra nó",
      en: "Who discovered it" }
  ],
  a: 2,
  ok: { vi: "Tuyệt! Vẫn là một hòn đá, chỉ đổi tên theo <b>vị trí</b>: trong không gian là <b>meteoroid</b>, đang cháy sáng trong khí quyển là <b>meteor</b> (sao băng), còn sót lại và nằm trên đất là <b>meteorite</b> (thiên thạch).",
        en: "Nice! It's the same rock, renamed by <b>location</b>: in space it's a <b>meteoroid</b>, blazing through the atmosphere it's a <b>meteor</b> (shooting star), and once it survives to the ground it's a <b>meteorite</b>." },
  no: { vi: "Chưa đúng! Ba từ đó nói về <b>vị trí</b> chứ không nói về chất liệu: không gian → khí quyển → mặt đất.",
        en: "Not quite! The three words describe <b>location</b>, not material: space → atmosphere → ground." },
  hint: { vi: "Cùng một hòn đá đi qua ba chặng đường. Ba cái tên ứng với <b>ba chặng</b> đó.",
          en: "One rock, three stages of a journey. Three names for <b>three stages</b>." },
  src: "meteor"
};
