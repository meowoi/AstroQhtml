/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "exoplanet-transit",
  topic: { vi: "NGOẠI HÀNH TINH",
           en: "EXOPLANET" },
  q: { vi: "Một cách phổ biến để tìm ngoại hành tinh là quan sát điều gì?",
       en: "One common way to find exoplanets is to watch for what?" },
  opts: [
    { vi: "Âm thanh phát ra từ ngôi sao",
      en: "Sounds coming from the star" },
    { vi: "Ngôi sao mờ đi một chút khi hành tinh đi ngang trước mặt nó",
      en: "The star dimming slightly as a planet crosses in front of it" },
    { vi: "Nhiệt độ trên Trái Đất tăng lên",
      en: "Earth's temperature going up" },
    { vi: "Ngắm bằng mắt thường vào đêm rằm",
      en: "Looking with the naked eye on a full-moon night" }
  ],
  a: 1,
  ok: { vi: "Đúng! Đó là <b>phương pháp quá cảnh (transit)</b>: hành tinh đi ngang trước ngôi sao thì che bớt ánh sáng, khiến ngôi sao <b>mờ đi một chút</b> — kính thiên văn đo được độ mờ ấy. Một cách khác là đo <b>độ lắc</b> của ngôi sao do hành tinh kéo (radial velocity).",
        en: "Correct! That's the <b>transit method</b>: a planet crossing in front of its star blocks a little starlight, so the star <b>dims slightly</b> — and telescopes can measure it. Another way is to measure the star's <b>wobble</b> (radial velocity)." },
  no: { vi: "Chưa đúng! Cách phổ biến là <b>phương pháp quá cảnh</b> — đo lúc ngôi sao mờ đi vì hành tinh che ngang. Âm thanh không truyền được trong chân không vũ trụ.",
        en: "Not quite! The common way is the <b>transit method</b> — measuring the dip in starlight as a planet crosses. Sound can't travel through the vacuum of space." },
  hint: { vi: "Nếu có ai đi ngang qua trước bóng đèn, ánh sáng sẽ <b>tối đi một chút</b>.",
          en: "When someone walks in front of a lamp, the light <b>dips a little</b>." },
  src: "exo"
};
