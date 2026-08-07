/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "condition",
  topic: { vi: "ĐIỀU KIỆN",
           en: "CONDITIONS" },
  q: { vi: "“NẾU phía trước có thiên thạch THÌ dừng lại.” Đây là loại lệnh gì?",
       en: "“IF an asteroid is ahead THEN stop.” What kind of command is this?" },
  opts: [
    { vi: "Lệnh điều kiện (If)",
      en: "Condition (If)" },
    { vi: "Vòng lặp",
      en: "Loop" },
    { vi: "Biến số",
      en: "Variable" },
    { vi: "Hàm vẽ",
      en: "Draw function" }
  ],
  a: 0,
  ok: { vi: "Đúng rồi! <b>Lệnh điều kiện If</b> giúp Byte quyết định dựa trên tình huống.",
        en: "Right! An <b>If condition</b> lets Byte decide based on the situation." },
  no: { vi: "Chưa đúng! “Nếu… thì…” chính là <b>lệnh điều kiện (If)</b>.",
        en: "Not quite! “If… then…” is exactly an <b>If condition</b>." },
  hint: { vi: "“Nếu… thì…” — nghe giống loại lệnh nào?",
          en: "“If… then…” — which command does that sound like?" }
};
