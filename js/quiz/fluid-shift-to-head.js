/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "fluid-shift-to-head",
  topic: { vi: "CƠ THỂ TRONG KHÔNG GIAN",
           en: "THE BODY IN SPACE" },
  q: { vi: "Trong vi trọng lực, chất lỏng trong cơ thể dồn đi đâu — và NASA lo nó ảnh hưởng tới bộ phận nào?",
       en: "In microgravity, where do the body's fluids shift - and which organ does NASA worry about?" },
  opts: [
    { vi: "Dồn xuống chân, ảnh hưởng đầu gối",
      en: "Down to the legs, affecting the knees" },
    { vi: "Dồn ra tay, ảnh hưởng ngón tay",
      en: "Out to the arms, affecting the fingers" },
    { vi: "Dồn lên đầu, ảnh hưởng mắt",
      en: "Upward to the head, affecting the eyes" },
    { vi: "Không dồn đi đâu cả",
      en: "They do not shift at all" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! Chất lỏng <b>dồn lên đầu</b>, và chính áp lực đó có thể đè lên <b>mắt</b> gây vấn đề thị lực — nên thị lực là thứ NASA theo dõi rất kỹ.",
        en: "Right! Fluids <b>shift upward to the head</b>, and that pressure can push on the <b>eyes</b> and cause vision problems - which is why NASA watches vision closely." },
  no: { vi: "Chưa đúng! Không có trọng lực kéo xuống nữa nên chất lỏng <b>dồn LÊN đầu</b>, chứ không xuống chân.",
        en: "Not quite! With no gravity pulling down, fluids shift <b>UP to the head</b>, not down to the legs." },
  hint: { vi: "Ở Trái Đất, cái gì giữ cho máu không dồn hết lên đầu khi em đứng?",
          en: "On Earth, what keeps your blood from pooling in your head while you stand?" },
  lv: 2,
  src: "bodyInSpace",
  srcQuote: "the fluids in the body shift upward to the head in microgravity, which may put pressure on the eyes and cause vision problems",
  srcChecked: "2026-08-22"
};
