/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "canadarm2-two-hands",
  topic: { vi: "CÁNH TAY ROBOT TRẠM VŨ TRỤ",
           en: "THE STATION'S ROBOTIC ARM" },
  q: { vi: "Vì sao cánh tay Canadarm2 có thể tự di chuyển tới bất cứ đâu trên trạm vũ trụ?",
       en: "Why can the Canadarm2 move itself anywhere it needs to go on the space station?" },
  opts: [
    { vi: "Vì nó chạy trên một đường ray vòng quanh cả trạm",
      en: "Because it rides a rail that circles the whole station" },
    { vi: "Vì phi hành gia tháo nó ra rồi gắn lại ở chỗ mới",
      en: "Because astronauts detach it and refit it elsewhere" },
    { vi: "Vì nó nhẹ nên có thể trôi tự do trong vi trọng lực",
      en: "Because it is light enough to float freely in microgravity" },
    { vi: "Vì mỗi đầu của nó đều dùng được làm điểm neo, trong khi đầu kia làm việc",
      en: "Because each end can be an anchor point while the other works" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA giải thích: <b>mỗi đầu của nó có thể dùng làm điểm neo trong khi đầu kia làm việc</b>. Hai đầu giống hệt nhau (đều là một \"bàn tay\" gọi là đầu kẹp khoá), nên cánh tay <b>tự bò quanh trạm giống một con sâu đo</b>: bám đầu này, thả đầu kia, với tới chốt tiếp theo rồi đổi vai.",
       en: "Yes! NASA explains: <b>each of its ends can be used as an anchor point while the other carries out various tasks</b>. Both ends are identical (each a \"hand\" called a latching end effector), so the arm <b>inches around the station like a caterpillar</b>: grip with one end, release the other, reach the next fixture, then swap roles." },
  no: { vi: "Chưa đúng! Bí mật nằm ở chỗ Canadarm2 <b>không có vai</b>: hai đầu giống hệt nhau, nên <b>đầu nào cũng làm điểm neo được</b> trong khi đầu kia làm việc. Đầu neo phải bám vào một chốt gắn có đường điện và dữ liệu.",
       en: "Not quite! The trick is that the Canadarm2 <b>has no shoulder</b>: both ends are identical, so <b>either end can anchor</b> while the other works. The anchoring end must be secured to a power data grapple fixture." },
  hint: { vi: "Cánh tay của bạn có một đầu gắn vào người. Cánh tay này thì hai đầu giống nhau.",
         en: "Your arm has one end fixed to your body. This arm has two identical ends." },
  lv: 3,
  src: "canadarm2",
  srcQuote: "Each of its ends can be used as an anchor point while the other carries out various tasks.",
  srcChecked: "2026-08-23"
};
