/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ml-learns-from-data",
  topic: { vi: "HỌC MÁY",
           en: "MACHINE LEARNING" },
  q: { vi: "Học máy khác một chương trình máy tính thông thường ở chỗ nào?",
       en: "How is machine learning different from an ordinary computer program?" },
  opts: [
    { vi: "Nó chạy nhanh hơn vì dùng nhiều bộ xử lý hơn",
      en: "It runs faster because it uses more processors" },
    { vi: "Nó xem một lượng lớn dữ liệu rồi học cách đưa ra dự đoán dựa trên dữ liệu đó",
      en: "It looks at large amounts of data and learns how to make predictions based on that data" },
    { vi: "Nó không cần điện để hoạt động",
      en: "It does not need electricity to run" },
    { vi: "Nó chỉ chạy được trên vệ tinh",
      en: "It only works aboard satellites" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Chương trình thường thì <b>người viết từng luật</b>; học máy thì <b>người cho xem rất nhiều ví dụ</b> và luật là thứ máy tự tìm ra. Vì thế dữ liệu không phải thứ phụ — dữ liệu chính là bài học.",
        en: "Exactly! With an ordinary program <b>people write every rule</b>; with machine learning <b>people show many examples</b> and the rules are what the machine works out. So the data is not a side detail — the data is the lesson." },
  no: { vi: "Chưa đúng. NASA nói loại AI này <b>xem một lượng lớn dữ liệu rồi học cách đưa ra dự đoán nhanh và chính xác dựa trên dữ liệu đó</b>. Điểm khác biệt không phải tốc độ, mà là <i>luật đến từ đâu</i>.",
        en: "Not quite. NASA says this kind of AI <b>looks at large amounts of data and learns how to make fast and accurate predictions based on that data</b>. The difference is not speed — it is <i>where the rules come from</i>." },
  hint: { vi: "Ai viết ra luật: người, hay chính cái máy?",
          en: "Who writes the rules: a person, or the machine?" },
  lv: 2,
  src: "nasaWhatIsAi",
  srcQuote: "This type of AI looks at large amounts of data and learns how to make fast and accurate predictions based on that data.",
  srcChecked: "2026-08-09"
};
