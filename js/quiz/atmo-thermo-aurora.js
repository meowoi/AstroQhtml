/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-thermo-aurora",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Hiện tượng Cực quang (bắc cực quang và nam cực quang) được tạo ra do yếu tố nào?",
       en: "What process creates auroras (the northern and southern lights) in the atmosphere?" },
  opts: [
    { vi: "Các hạt tích điện bị kích thích va chạm với nhau tỏa sáng",
      en: "Excited particles collide to create auroras" },
    { vi: "Do ánh sáng Mặt Trời phản chiếu trực tiếp từ các tảng băng ở vùng cực",
      en: "Due to sunlight directly reflecting off polar ice sheets" },
    { vi: "Ánh đèn từ các thành phố lớn phản chiếu lên mây",
      en: "City lights reflecting onto clouds" },
    { vi: "Mặt Trăng chiếu ánh sáng đỏ vào ban đêm",
      en: "Red moonlight shining at night" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Khi các hạt tích điện bị kích thích va chạm trong tầng khí quyển sẽ tạo nên cực quang.",
        en: "Correct! Excited charged particles colliding in the upper atmosphere create auroras." },
  no: { vi: "Chưa đúng. Cực quang không phải ánh sáng phản chiếu từ băng hay đèn thành phố — nó là ánh sáng do chính các hạt năng lượng cao va chạm mà PHÁT RA, nên vẫn thấy được vào những đêm không trăng.",
        en: "Incorrect. Auroras are not reflected light from ice or city lights — high-energy particles collide and EMIT the light themselves, which is why they shine on moonless nights." },
  hint: { vi: "Đây là sự tương tác giữa hạt năng lượng Mặt Trời và khí quyển Trái Đất.",
          en: "This is an interaction between solar energy particles and Earth's atmosphere." },
  lv: 3,
  src: "nasaGeneralAtmosphere",
  srcQuote: "When these particles are excited, they collide to create auroras – also known as the northern and southern lights.",
  srcChecked: "2026-08-06"
};
