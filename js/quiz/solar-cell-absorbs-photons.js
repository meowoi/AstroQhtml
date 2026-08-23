/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "solar-cell-absorbs-photons",
  topic: { vi: "ĐIỆN MẶT TRỜI",
           en: "SOLAR ELECTRICITY" },
  q: { vi: "Trong một tấm pin mặt trời, thứ gì hấp thụ các photon để tạo ra điện?",
       en: "Inside a solar panel, what absorbs the photons so electricity can be made?" },
  opts: [
    { vi: "Một cái tuabin quay",
      en: "A spinning turbine" },
    { vi: "Lớp silic sẫm màu",
      en: "The dark silicon" },
    { vi: "Lớp kính bên ngoài",
      en: "The outer glass" },
    { vi: "Một cục ắc quy",
      en: "A battery" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! <b>Lớp silic sẫm màu</b> hấp thụ các <b>photon</b> — tức các hạt của ánh sáng — rồi các ô quang điện biến chúng thành điện. Tấm pin <b>không có bộ phận nào chuyển động</b>.",
        en: "Right! The <b>dark silicon</b> absorbs the <b>photons</b> - particles from light - and the PV cells convert them into electricity. A panel has <b>no moving parts</b> at all." },
  no: { vi: "Chưa đúng! Không có tuabin nào cả. Chính <b>lớp silic sẫm màu</b> hấp thụ photon, và các ô quang điện biến chúng thành điện.",
        en: "Not quite! There is no turbine. It is the <b>dark silicon</b> that absorbs photons, and the PV cells turn them into electricity." },
  hint: { vi: "Vì sao tấm pin lại có màu đen chứ không phải màu trắng bóng?",
          en: "Why is a solar panel black rather than shiny white?" },
  lv: 2,
  src: "solarToElectric",
  srcQuote: "The dark silicon absorbs the photons, or particles from light, which the PV cells convert into electricity.",
  srcChecked: "2026-08-22"
};
