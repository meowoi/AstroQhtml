/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ingenuity-first-flight",
  topic: { vi: "BAY TRÊN SAO HOẢ",
           en: "FLYING ON MARS" },
  q: { vi: "Trực thăng Ingenuity của NASA đi vào lịch sử với việc gì?",
       en: "What did NASA's Ingenuity helicopter make history for?" },
  opts: [
    { vi: "Chiếc máy bay đầu tiên bay có động cơ, có điều khiển ở một hành tinh khác",
      en: "The first aircraft to achieve powered, controlled flight on another planet" },
    { vi: "Chiếc máy bay đầu tiên chở người bay trên Sao Hoả",
      en: "The first aircraft to carry a person over Mars" },
    { vi: "Chiếc tàu đầu tiên hạ cánh xuống Sao Hoả",
      en: "The first craft to land on Mars" },
    { vi: "Chiếc rover đầu tiên tự lái trên Sao Hoả",
      en: "The first rover to drive itself on Mars" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA gọi nó bằng đúng một dòng: <b>chiếc máy bay đầu tiên đạt được chuyến bay có động cơ và có điều khiển ở một hành tinh khác</b>. <b>Có động cơ</b> nghĩa là nó tự tạo lực đẩy chứ không rơi hay lượn theo gió; <b>có điều khiển</b> nghĩa là nó đi tới nơi người ta muốn.",
       en: "Yes! NASA puts it in one line: <b>the first aircraft to achieve powered, controlled flight on another planet</b>. <b>Powered</b> means it made its own thrust rather than falling or gliding; <b>controlled</b> means it went where people wanted it to go." },
  no: { vi: "Chưa đúng! Ingenuity là <b>máy bay</b>, không phải rover và không chở người. Cái đầu tiên của nó là <b>chuyến bay có động cơ và có điều khiển ở một hành tinh khác</b> — trước nó, mọi thứ ta đưa tới Sao Hoả đều lăn trên đất hoặc đứng một chỗ.",
       en: "Not quite! Ingenuity is an <b>aircraft</b>, not a rover, and it carried nobody. Its first was <b>powered, controlled flight on another planet</b> — before it, everything we sent to Mars rolled or stayed put." },
  hint: { vi: "Hai chữ đáng dừng lại: có động cơ, và có điều khiển.",
         en: "Two words worth pausing on: powered, and controlled." },
  lv: 1,
  src: "ingenuity",
  srcQuote: "The first aircraft to achieve powered, controlled flight on another planet",
  srcChecked: "2026-08-23"
};
