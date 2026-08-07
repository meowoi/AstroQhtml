/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "atmo-thermo-location",
  topic: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
  q: { vi: "Tầng nhiệt (Thermosphere) nằm ở vị trí nào so với tầng trung lưu?",
       en: "Where does the thermosphere reside relative to the mesosphere?" },
  opts: [
    { vi: "Nằm phía trên tầng trung lưu",
      en: "Resides above the mesosphere" },
    { vi: "Nằm phía dưới tầng đối lưu",
      en: "Resides below the troposphere" },
    { vi: "Nằm sát mực nước biển",
      en: "Resides at sea level" },
    { vi: "Nằm bên trong tầng bình lưu",
      en: "Resides inside the stratosphere" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Tầng nhiệt (Thermosphere) nằm phía trên tầng trung lưu.",
        en: "Correct! The thermosphere resides directly above the mesosphere." },
  no: { vi: "Chưa đúng. Tầng nhiệt nằm ở vị trí phía trên tầng trung lưu và dưới tầng ngoại lưu.",
        en: "Incorrect. The thermosphere sits above the mesosphere and below the exosphere." },
  hint: { vi: "Đây là tầng khí quyển cao thứ tư tính từ mặt đất lên.",
          en: "This is the fourth atmospheric layer going upward from ground." },
  lv: 2,
  src: "nasaGeneralAtmosphere",
  srcQuote: "The thermosphere resides above the mesosphere.",
  srcChecked: "2026-08-06"
};
