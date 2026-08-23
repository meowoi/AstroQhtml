/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-metadata-eases-load",
  topic: { vi: "AI DÁN NHÃN DỮ LIỆU",
           en: "AI TAGGING DATA" },
  q: { vi: "Mô hình đề xuất từ khoá của NASA làm gì đối với những người biên mục dữ liệu?",
       en: "What does NASA's keyword recommender model do for the people who catalogue data?" },
  opts: [
    { vi: "Giảm gánh nặng cho họ, vẫn giữ chất lượng mô tả ở mức cao",
      en: "Reduces their burden while keeping metadata quality high" },
    { vi: "Thay thế họ hoàn toàn, không cần người nữa",
      en: "Replaces them entirely, so no people are needed" },
    { vi: "Xoá những tập dữ liệu không ai dùng tới",
      en: "Deletes datasets that nobody uses" },
    { vi: "Dịch tên các tập dữ liệu sang nhiều thứ tiếng",
      en: "Translates dataset names into many languages" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA viết: bằng cách tự động đề xuất những từ khoá chính xác và đã chuẩn hoá, mô hình <b>giảm bớt gánh nặng cho những người biên mục trong khi vẫn giữ chất lượng dữ liệu mô tả ở mức cao</b>. Hãy chú ý cách nói — <b>giảm gánh nặng, không phải thay thế</b>.",
       en: "Yes! NASA writes that by automatically recommending precise, standardised keywords, the model <b>reduces the burden on human curators while ensuring metadata quality remains high</b>. Note the wording — <b>reduces the burden, does not replace them</b>." },
  no: { vi: "Chưa đúng! Chỗ đáng đọc kỹ chính là cách NASA nói: mô hình <b>giảm gánh nặng</b> cho người biên mục, <b>không</b> thay thế họ — và chất lượng phần mô tả vẫn phải giữ ở mức cao.",
       en: "Not quite! The wording is the point: the model <b>reduces the burden</b> on curators — it does <b>not</b> replace them, and metadata quality still has to stay high." },
  hint: { vi: "Đọc kỹ động từ NASA dùng: giảm bớt, hay thay thế?",
         en: "Read NASA's verb carefully: reduce, or replace?" },
  lv: 2,
  src: "aiMetadata",
  srcQuote: "By automatically recommending precise, standardized keywords, the model reduces the burden on human curators while ensuring metadata quality remains high.",
  srcChecked: "2026-08-23"
};
