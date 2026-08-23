/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sojourner-first-rover",
  topic: { vi: "CHIẾC ROVER ĐẦU TIÊN",
           en: "THE FIRST ROVER" },
  q: { vi: "Sojourner có gì đặc biệt trong lịch sử khám phá Sao Hoả?",
       en: "What made Sojourner special in the history of Mars exploration?" },
  opts: [
    { vi: "Nó là chiếc rover đi xa nhất trên Sao Hoả",
      en: "It drove farther on Mars than any other rover" },
    { vi: "Nó là chiếc rover đầu tiên mang theo phòng thí nghiệm",
      en: "It was the first rover to carry a laboratory" },
    { vi: "Nó là chiếc rover đầu tiên tự lái bằng AI",
      en: "It was the first rover to drive itself using AI" },
    { vi: "Nó là chiếc rover robot đầu tiên được đặt lên bề mặt Sao Hoả",
      en: "It was the first-ever robotic rover delivered to the Martian surface" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA ghi: tàu Mars Pathfinder đã <b>đưa xuống bề mặt Sao Hoả chiếc rover robot đầu tiên trong lịch sử, tên là Sojourner</b>. Nó rất nhỏ — <b>nặng 23 pound (10,6 kg), cao khoảng 1 foot (30 cm)</b> — nhưng có bánh xe nghĩa là <b>có quyền chọn</b> đi tới chỗ đáng nghiên cứu.",
       en: "Yes! NASA records that Mars Pathfinder <b>delivered the first-ever robotic rover, Sojourner, to the Martian surface</b>. It was tiny - <b>a 23-pound (10.6 kilogram) rover about 1 foot (30 centimetres) tall</b> - but having wheels meant <b>having a choice</b> about where to study." },
  no: { vi: "Chưa đúng! Sojourner <b>không</b> đi xa (nó chưa bao giờ rời khỏi vùng quanh chỗ hạ cánh) và không mang phòng thí nghiệm. Cái đầu tiên của nó là: <b>chiếc rover robot đầu tiên đặt lên bề mặt Sao Hoả</b>, năm 1997. Mọi rover sau này đều đứng trên câu trả lời đó.",
       en: "Not quite! Sojourner did <b>not</b> travel far (it never left the area around its landing site) and carried no laboratory. Its first was being <b>the first-ever robotic rover on the Martian surface</b>, in 1997. Every later rover stands on that answer." },
  hint: { vi: "Trước nó, mọi thứ ta đặt xuống Sao Hoả đều đứng một chỗ.",
         en: "Before it, everything we put on Mars stayed where it landed." },
  lv: 1,
  src: "pathfinder",
  srcQuote: "NASA's Mars Pathfinder successfully demonstrated a new way to safely land on the Red Planet and deliver the first-ever robotic rover, Sojourner, to the Martian surface.",
  srcChecked: "2026-08-23"
};
