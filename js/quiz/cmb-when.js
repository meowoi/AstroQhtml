/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "cmb-when",
  topic: { vi: "BỨC XẠ NỀN VŨ TRỤ",
           en: "COSMIC MICROWAVE BACKGROUND" },
  q: { vi: "Ánh sáng của bức xạ nền được phát ra vào khoảng bao lâu sau Big Bang?",
       en: "Roughly how long after the big bang was the background light released?" },
  opts: [
    { vi: "Khoảng 1 giây sau",
      en: "About 1 second after" },
    { vi: "Khoảng 1 triệu tỉ năm sau",
      en: "About a quadrillion years after" },
    { vi: "Đúng vào lúc Big Bang xảy ra",
      en: "At the very instant of the big bang" },
    { vi: "Khoảng 380.000 năm sau",
      en: "About 380,000 years after" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! Khoảng <b>380.000 năm</b> sau Big Bang, vũ trụ nguội đủ để các hạt nhân bắt được electron — giai đoạn gọi là <b>kỷ nguyên tái kết hợp</b>. Ánh sáng phát ra khi đó chính là bức xạ nền.",
        en: "Right! About <b>380,000 years</b> after the big bang the universe cooled enough for nuclei to capture electrons — the <b>epoch of recombination</b>. The light released then is the background radiation." },
  no: { vi: "Chưa đúng! Con số NASA ghi là khoảng <b>380.000 năm</b> sau Big Bang.",
        en: "Not quite! The figure NASA gives is about <b>380,000 years</b> after the big bang." },
  hint: { vi: "Không phải ngay lập tức, cũng không phải hàng tỉ năm — mà là <b>vài trăm nghìn</b> năm.",
          en: "Not instantly, and not billions of years — a few <b>hundred thousand</b> years." },
  lv: 3,
  src: "cosmos"
};
