/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "robots-free-crew-time",
  topic: { vi: "ROBOT MUA LẠI THỜI GIAN",
           en: "ROBOTS BUYING BACK TIME" },
  q: { vi: "NASA nêu lý do gì cho việc dùng robot trên Trạm Vũ trụ Quốc tế?",
       en: "What reason does NASA give for using robots on the International Space Station?" },
  opts: [
    { vi: "Thời gian của phi hành đoàn là một tài nguyên có giá trị",
      en: "Crew time is a valuable resource" },
    { vi: "Robot làm việc chính xác hơn con người ở mọi việc",
      en: "Robots are more accurate than humans at everything" },
    { vi: "Trạm vũ trụ không còn đủ chỗ cho thêm phi hành gia",
      en: "The station has no room for more astronauts" },
    { vi: "Robot không cần không khí nên tiết kiệm oxy",
      en: "Robots need no air, so they save oxygen" }
  ],
  a: 0,
  ok: { vi: "Đúng! NASA nói thẳng: <b>thời gian của phi hành đoàn là một tài nguyên có giá trị trên Trạm Vũ trụ Quốc tế, và giá trị đó chỉ tăng thêm với những nhiệm vụ tương lai</b>. Nên robot ở đó <b>không phải để làm hộ</b> — mà để nhận phần việc lặp lại, <b>giải phóng thời gian</b> và <b>giảm rủi ro</b>.",
       en: "Yes! NASA says it plainly: <b>crew time is a valuable resource on the International Space Station and its value only increases for future space missions</b>. So the robots are <b>not there as replacements</b> - they take the repetitive jobs, <b>freeing up time</b> and <b>reducing risk</b>." },
  no: { vi: "Chưa đúng! Lý do NASA nêu là <b>thời gian của phi hành đoàn</b>: mỗi giờ của một phi hành gia đều rất đắt, nên việc lặp lại hoặc nguy hiểm thì để robot làm, còn con người dành thời gian cho phần chỉ con người làm được.",
       en: "Not quite! NASA's stated reason is <b>crew time</b>: every astronaut hour is expensive, so repetitive or risky jobs go to robots while people spend their time on what only people can do." },
  hint: { vi: "Thứ khan hiếm nhất trên trạm không phải chỗ ở, mà là một loại tài nguyên khác.",
         en: "The scarcest thing on the station is not space, but another resource." },
  lv: 2,
  src: "roboticHelpers",
  srcQuote: "Crew time is a valuable resource on the International Space Station and its value only increases for future space missions.",
  srcChecked: "2026-08-23"
};
