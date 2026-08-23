/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "opportunity-distance",
  topic: { vi: "KỶ LỤC LÁI XE NGOÀI TRÁI ĐẤT",
           en: "THE OFF-EARTH DRIVING RECORD" },
  q: { vi: "Rover nào giữ kỷ lục quãng đường lái xe ngoài Trái Đất, và đi được bao xa?",
       en: "Which rover holds the off-Earth roving distance record, and how far did it drive?" },
  opts: [
    { vi: "Spirit — 45,16 ki-lô-mét trên Sao Hoả",
      en: "Spirit - 45.16 kilometres on Mars" },
    { vi: "Curiosity — 7,7 ki-lô-mét trên Sao Hoả",
      en: "Curiosity - 7.7 kilometres on Mars" },
    { vi: "Opportunity — 45,16 ki-lô-mét trên Sao Hoả",
      en: "Opportunity - 45.16 kilometres on Mars" },
    { vi: "Sojourner — 28,06 ki-lô-mét trên Sao Hoả",
      en: "Sojourner - 28.06 kilometres on Mars" }
  ],
  a: 2,
  ok: { vi: "Đúng! NASA ghi: <b>Opportunity giữ kỷ lục quãng đường di chuyển ngoài Trái Đất, sau khi tích luỹ được 28,06 dặm (45,16 ki-lô-mét) lái xe trên Sao Hoả</b>. Đây là kỷ lục <b>không đến từ tốc độ mà đến từ sự bền bỉ</b> — cộng dồn qua rất nhiều ngày, mỗi ngày một đoạn ngắn.",
       en: "Yes! NASA records that <b>Opportunity holds the off-Earth roving distance record after accruing 28.06 miles (45.16 kilometres) of driving on Mars</b>. This is a record built <b>not from speed but from persistence</b> — added up over many working days, a short stretch at a time." },
  no: { vi: "Chưa đúng! Kỷ lục thuộc về <b>Opportunity</b> với <b>45,16 km</b>. Spirit — chiếc sinh đôi của nó — chỉ đi được 7,7 km; còn Sojourner thì chưa bao giờ rời khỏi vùng quanh chỗ hạ cánh.",
       en: "Not quite! The record belongs to <b>Opportunity</b> with <b>45.16 km</b>. Spirit - its twin - drove only 7.7 km, and Sojourner never left the area around its landing site." },
  hint: { vi: "Hai chiếc rover sinh đôi năm 2004; chiếc đáp xuống đồng bằng Meridiani là chiếc đi xa nhất.",
         en: "Two twin rovers landed in 2004; the one on Meridiani Planum drove farthest." },
  lv: 2,
  src: "merRovers",
  srcQuote: "Opportunity holds the off-Earth roving distance record after accruing 28.06 miles (45.16 kilometers) of driving on Mars.",
  srcChecked: "2026-08-23"
};
