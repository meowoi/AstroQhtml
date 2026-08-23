/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "voyager-weak-signal",
  topic: { vi: "TÍN HIỆU CỦA VOYAGER",
           en: "THE VOYAGER SIGNAL" },
  q: { vi: "Công suất mà ăng-ten trên Trái Đất nhận được từ tín hiệu Voyager yếu tới mức nào?",
       en: "How weak is the power that Earth's antennas receive from the Voyager signals?" },
  opts: [
    { vi: "Yếu hơn 20 lần mức cần để chạy một cái đồng hồ điện tử",
      en: "20 times weaker than what is needed to run a digital watch" },
    { vi: "Yếu hơn 20 nghìn lần mức đó",
      en: "20 thousand times weaker than that" },
    { vi: "Yếu hơn 20 triệu lần mức đó",
      en: "20 million times weaker than that" },
    { vi: "Yếu hơn 20 tỷ lần mức đó",
      en: "20 billion times weaker than that" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA viết: <b>công suất mà các ăng-ten của Mạng Không Gian Sâu nhận được từ tín hiệu Voyager yếu hơn 20 tỷ lần so với mức cần để chạy một cái đồng hồ điện tử</b>. Không đủ để làm nhích một kim đồng hồ, mà vẫn <b>đọc ra được thông tin</b> — nếu ăng-ten đủ lớn và bạn biết chính xác phải nghe cái gì.",
       en: "Yes! NASA writes that <b>the power that the DSN antennas receive from the Voyager signals is 20 billion times weaker than what is needed to run a digital watch</b>. Not enough to move a watch hand, yet still enough to <b>read information out of</b> - if your antenna is big enough and you know exactly what to listen for." },
  no: { vi: "Chưa đúng! Con số khó tin tới mức đáng nhớ: <b>yếu hơn 20 TỶ lần</b>. Hai tàu Voyager phóng năm 1977 và nay đã ra tới không gian giữa các ngôi sao — tín hiệu đi càng xa thì càng yếu.",
       en: "Not quite! The figure is startling enough to remember: <b>20 BILLION times weaker</b>. The two Voyagers launched in 1977 and are now in interstellar space - the farther a signal travels, the weaker it gets." },
  hint: { vi: "Con số này lớn hơn một triệu rất nhiều.",
         en: "The figure is very much larger than a million." },
  lv: 2,
  src: "dsnAntennas",
  srcQuote: "the power that the DSN antennas receive from the Voyager signals is 20 billion times weaker than what is needed to run a digital watch",
  srcChecked: "2026-08-23"
};
