/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-training-data-from-people",
  topic: { vi: "HỌC MÁY",
           en: "MACHINE LEARNING" },
  q: { vi: "Muốn dạy một hệ AI thì cần rất nhiều “dữ liệu huấn luyện”. Theo AI4K12, số dữ liệu đó thường từ đâu ra?",
       en: "Teaching an AI system takes a lot of “training data”. According to AI4K12, where does it usually come from?" },
  opts: [
    { vi: "Máy tự sinh ra hết, không cần ai cả",
      en: "The machine generates all of it by itself" },
    { vi: "Thường phải do CON NGƯỜI cung cấp — đôi khi máy tự thu được một phần",
      en: "It must usually be supplied by people — sometimes the machine gathers some itself" },
    { vi: "Luôn được tải tự động từ Internet",
      en: "It is always downloaded automatically from the Internet" },
    { vi: "Do một hệ AI khác viết ra",
      en: "Another AI system writes it" }
  ],
  a: 1,
  ok: { vi: "Đúng! Đây là chỗ nhiều người bất ngờ: phía sau một hệ AI “tự học” thường là <b>rất nhiều công của con người</b> — thu, chọn, dán nhãn dữ liệu. Máy học được từ những gì người ta cho nó xem, nên <b>ai chọn dữ liệu là chuyện quan trọng</b>.",
        en: "Yes! This surprises people: behind a “self-learning” AI there is usually <b>a great deal of human work</b> — collecting, choosing and labelling data. A machine learns from what it is shown, so <b>who picks the data matters</b>." },
  no: { vi: "Chưa đúng. AI4K12 nói dữ liệu huấn luyện <b>thường phải do con người cung cấp</b>, đôi khi máy tự thu được một phần. Không có ai đưa dữ liệu vào thì chẳng có gì để học cả.",
        en: "Not quite. AI4K12 says training data <b>must usually be supplied by people</b>, and is sometimes gathered by the machine itself. With nobody feeding it data, there is nothing to learn from." },
  hint: { vi: "Hỏi xem AI học từ đâu — và ai đặt thứ đó trước mặt nó.",
          en: "Ask where the AI learns from — and who puts that in front of it." },
  lv: 2,
  src: "ai4k12Learning",
  srcQuote: "This “training data” must usually be supplied by people, but is sometimes acquired by the machine itself.",
  srcChecked: "2026-08-23"
};
