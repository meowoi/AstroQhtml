/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sensor-why-autonomous",
  topic: { vi: "CẢM BIẾN",
           en: "SENSORS" },
  q: { vi: "Astrobee có thể làm việc TỰ ĐỘNG, không cần ai điều khiển từng động tác. Vì sao khi đó cảm biến lại càng quan trọng?",
       en: "Astrobee can work AUTONOMOUSLY, with nobody steering each move. Why do sensors matter even more then?" },
  opts: [
    { vi: "Vì cảm biến làm robot bay nhanh hơn",
      en: "Because sensors make the robot fly faster" },
    { vi: "Vì không có người chỉ đường, robot phải tự nhận biết xung quanh mới đi được",
      en: "Because with nobody guiding it, the robot must sense its surroundings to move at all" },
    { vi: "Vì cảm biến thay cho pin",
      en: "Because sensors take the place of the battery" },
    { vi: "Vì phi hành gia thích tiếng cảm biến kêu",
      en: "Because the astronauts like the sound sensors make" }
  ],
  a: 1,
  ok: { vi: "Chính xác! Astrobee <b>làm việc tự động HOẶC do người điều khiển từ xa</b>. Khi tự động thì không ai nói cho nó biết phía trước có gì, nên nó phải <b>tự “nhìn” bằng camera và cảm biến</b> để định hướng — cảm biến chính là cặp mắt của nó.",
          en: "Exactly! Astrobee works <b>autonomously or via remote control</b>. When it's on its own, nobody tells it what lies ahead, so it must <b>“see” for itself with cameras and sensors</b> — the sensors are its eyes." },
  no: { vi: "Chưa đúng! Cảm biến không phải để bay nhanh hay để thay pin. Khi <b>không có người điều khiển</b>, robot chỉ còn cách <b>tự nhận biết xung quanh</b> — và đó đúng là việc của cảm biến.",
          en: "Not quite! Sensors aren't for speed or for replacing the battery. With <b>nobody at the controls</b>, the robot's only option is to <b>sense its surroundings itself</b> — which is exactly a sensor's job." },
  hint: { vi: "Nếu bịt mắt bạn rồi bảo bạn tự đi trong một căn phòng lạ thì sao?",
            en: "What if someone blindfolded you and asked you to cross an unfamiliar room?" },
  lv: 3,
  src: "astrobee",
  srcQuote: "Working autonomously or via remote control by astronauts, flight controllers or researchers on the ground, the robots are designed to complete tasks",
  srcChecked: "2026-08-19"
};
