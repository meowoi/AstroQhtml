/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "star-fusion",
  topic: { vi: "NGÔI SAO",
           en: "STAR" },
  q: { vi: "Trong lõi Mặt Trời, các hạt nhân hydro bị ép lại để tạo thành nguyên tố nào?",
       en: "In the Sun's core, hydrogen nuclei are squeezed together to form which element?" },
  opts: [
    { vi: "Sắt (Fe)",
      en: "Iron (Fe)" },
    { vi: "Ô-xy (O)",
      en: "Oxygen (O)" },
    { vi: "Heli (He)",
      en: "Helium (He)" },
    { vi: "Vàng (Au)",
      en: "Gold (Au)" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Áp suất và nhiệt độ khủng khiếp trong lõi ép hạt nhân hydro lại thành <b>heli</b>. Quá trình đó gọi là <b>phản ứng nhiệt hạch</b>, và nó sinh ra toàn bộ năng lượng giữ cho ngôi sao không sụp xuống.",
        en: "Right! The immense pressure and heat in the core fuse hydrogen nuclei into <b>helium</b>. That process — <b>nuclear fusion</b> — releases the energy that keeps a star from collapsing." },
  no: { vi: "Chưa đúng! Hydro hợp lại thành <b>heli</b> — đó là nguồn năng lượng của mọi ngôi sao.",
        en: "Not quite! Hydrogen fuses into <b>helium</b> — that's what powers every star." },
  hint: { vi: "Nguyên tố nhẹ thứ hai trong bảng tuần hoàn — cùng loại khí người ta bơm vào bóng bay!",
          en: "The second-lightest element on the periodic table — the same gas that fills party balloons!" },
  src: "star"
};
