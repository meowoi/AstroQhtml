/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "comet-what",
  topic: { vi: "SAO CHỔI",
           en: "COMET" },
  q: { vi: "Sao chổi được tạo nên chủ yếu từ gì?",
       en: "What is a comet mostly made of?" },
  opts: [
    { vi: "Đá và kim loại đặc",
      en: "Solid rock and metal" },
    { vi: "Khí hydro đang cháy",
      en: "Burning hydrogen gas" },
    { vi: "Băng bọc lớp bụi và chất hữu cơ tối màu",
      en: "Ice coated with dust and dark organic material" },
    { vi: "Kim cương và thuỷ tinh",
      en: "Diamond and glass" }
  ],
  a: 2,
  ok: { vi: "Chuẩn! NASA gọi sao chổi là <b>“quả cầu tuyết bẩn”</b>: phần lớn là băng bọc lớp vật chất hữu cơ tối màu. Khi lại gần Mặt Trời, băng bốc hơi tạo ra lớp khí bao quanh (coma) và cái đuôi dài.",
        en: "Exactly! NASA calls comets <b>“dirty snowballs”</b>: mostly ice coated with dark organic material. Near the Sun that ice vaporises into a glowing coma and a long tail." },
  no: { vi: "Chưa đúng! Sao chổi chủ yếu là <b>băng</b> lẫn bụi — đó là lý do nó mọc đuôi khi lại gần Mặt Trời. Vật thể bằng đá thì là <b>tiểu hành tinh</b>.",
        en: "Not quite! A comet is mostly <b>ice</b> and dust — that's why it grows a tail near the Sun. The rocky ones are <b>asteroids</b>." },
  hint: { vi: "Vì sao nó mọc đuôi khi lại gần Mặt Trời? Vì có thứ gì đó <b>bốc hơi</b> được.",
          en: "Why does it grow a tail near the Sun? Because something in it can <b>evaporate</b>." },
  src: "comet"
};
