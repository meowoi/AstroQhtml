/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "grav-two-rules",
  topic: { vi: "LỰC HẤP DẪN",
           en: "GRAVITY" },
  q: { vi: "NASA nêu hai quy tắc: vật có khối lượng lớn hơn thì hấp dẫn mạnh hơn, và hấp dẫn yếu đi khi ở xa. Vậy lực hấp dẫn mà một vật cảm nhận được phụ thuộc vào điều gì?",
       en: "NASA gives two rules: objects with more mass have more gravity, and gravity gets weaker with distance. So what does the gravity an object feels depend on?" },
  opts: [
    { vi: "Chỉ khối lượng",
      en: "Mass only" },
    { vi: "Chỉ khoảng cách",
      en: "Distance only" },
    { vi: "Cả khối lượng lẫn khoảng cách",
      en: "Both mass and distance" },
    { vi: "Không phụ thuộc gì — ở đâu hấp dẫn cũng như nhau",
      en: "Neither — gravity is the same everywhere" }
  ],
  a: 2,
  ok: { vi: "Đúng! <b>Cả hai</b> đều tính. Mặt Trời nặng hơn Trái Đất cực nhiều nhưng ở rất xa; Trái Đất nhẹ hơn nhiều nhưng ở ngay dưới chân ta — nên chính Trái Đất mới là thứ giữ ta đứng trên mặt đất.",
          en: "Yes! <b>Both</b> count. The Sun is vastly heavier than Earth but very far away; Earth is far lighter but right under your feet — which is why Earth is what keeps you on the ground." },
  no: { vi: "Chưa đúng! Phải tính <b>cả hai</b>: khối lượng càng lớn thì hấp dẫn càng mạnh, <b>và</b> càng ra xa thì hấp dẫn càng yếu. Bỏ một trong hai là trả lời sai ngay câu “vì sao ta không bị Mặt Trời hút bay đi”.",
          en: "Not quite! You need <b>both</b>: more mass means more gravity, <b>and</b> gravity weakens with distance. Drop either one and you can't answer “why doesn't the Sun pull us away”." },
  hint: { vi: "Hai quy tắc, không phải một — cả hai được nhắc trong cùng một đoạn.",
            en: "Two rules, not one — both appear in the same passage." },
  lv: 3,
  src: "grav",
  srcQuote: "Objects with more mass have more gravity. Gravity also gets weaker with distance.",
  srcChecked: "2026-08-19"
};
