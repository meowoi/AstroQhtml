/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-surya-two-hours",
  topic: { vi: "DỰ BÁO BÃO MẶT TRỜI",
           en: "FORECASTING SOLAR STORMS" },
  q: { vi: "Mô hình AI Surya của NASA dự đoán trước các đợt bùng sáng Mặt Trời được bao lâu?",
       en: "How far ahead can NASA's Surya AI model predict solar flares?" },
  opts: [
    { vi: "Trước hai tuần",
      en: "Two weeks ahead" },
    { vi: "Trước hai giờ",
      en: "Two hours ahead" },
    { vi: "Trước hai phút",
      en: "Two minutes ahead" },
    { vi: "Trước chín năm",
      en: "Nine years ahead" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA cho biết Surya <b>tạo ra những dự đoán dạng hình ảnh về các đợt bùng sáng Mặt Trời trước hai giờ</b>. Hai giờ nghe ngắn, nhưng đó là khoảng thời gian đủ để người vận hành vệ tinh và lưới điện <b>làm một việc gì đó</b>, thay vì chỉ biết chuyện sau khi nó đã xảy ra.",
       en: "Yes! NASA says Surya <b>generates visual predictions of solar flares two hours into the future</b>. Two hours sounds short, but it is long enough for satellite and power-grid operators to <b>actually do something</b>, instead of only learning about it afterwards." },
  no: { vi: "Chưa đúng! Con số là <b>hai giờ</b>. (Chín năm là lượng dữ liệu quan sát Mặt Trời dùng để <b>huấn luyện</b> Surya, không phải khoảng dự báo.)",
       en: "Not quite! The figure is <b>two hours</b>. (Nine years is the amount of solar observation data used to <b>train</b> Surya, not the forecast window.)" },
  hint: { vi: "Đủ để người vận hành lưới điện kịp làm một việc gì đó — không phải hàng tuần.",
         en: "Long enough for a grid operator to act — not weeks." },
  lv: 2,
  src: "aiHelio",
  srcQuote: "Surya, with its ability to generate visual predictions of solar flares two hours into the future, marks a major step towards the use of AI for operational space weather prediction.",
  srcChecked: "2026-08-23"
};
