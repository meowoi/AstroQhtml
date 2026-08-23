/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "robonaut-first-humanoid",
  topic: { vi: "ROBOT HÌNH NGƯỜI",
           en: "A HUMANOID ROBOT" },
  q: { vi: "Robonaut 2 (R2) trở thành cái đầu tiên gì vào năm 2011?",
       en: "What did Robonaut 2 (R2) become the first of in 2011?" },
  opts: [
    { vi: "Robot đầu tiên đi bộ ngoài không gian một mình",
      en: "The first robot to spacewalk alone" },
    { vi: "Robot hình người đầu tiên bay vào không gian",
      en: "The first humanoid robot in space" },
    { vi: "Robot đầu tiên lái được một con tàu vũ trụ",
      en: "The first robot to pilot a spacecraft" },
    { vi: "Robot đầu tiên đặt chân lên Mặt Trăng",
      en: "The first robot to set foot on the Moon" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA ghi: <b>Robonaut 2, hay R2, năm 2011 trở thành robot hình người đầu tiên bay vào không gian</b>. Vì sao lại làm một con robot có hình người? Vì trạm vũ trụ được thiết kế cho <b>tay người</b> — công tắc, tay nắm, dụng cụ đều làm theo cỡ bàn tay người.",
       en: "Yes! NASA records: <b>Robonaut 2, or R2, in 2011 became the first humanoid robot in space</b>. Why build a human-shaped robot? Because the station is designed for <b>human hands</b> - switches, handrails and tools are all sized for them." },
  no: { vi: "Chưa đúng! Cái đầu tiên của R2 là <b>robot hình người đầu tiên bay vào không gian</b>, năm 2011. Nó được đưa lên dạng chỉ có phần thân, gắn vào một cái trụ; hai chân chỉ được thêm vào năm 2014.",
       en: "Not quite! R2's first was being the <b>first humanoid robot in space</b>, in 2011. It arrived as a torso only, fixed to a stanchion; its two legs were not added until 2014." },
  hint: { vi: "Phần lớn robot không giống người. Con này thì có bàn tay linh hoạt.",
         en: "Most robots look nothing like us. This one has dexterous hands." },
  lv: 1,
  src: "robonaut2",
  srcQuote: "Robonaut 2, or R2, in 2011 became the first humanoid robot in space.",
  srcChecked: "2026-08-23"
};
