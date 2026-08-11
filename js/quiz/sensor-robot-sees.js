/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sensor-robot-sees",
  topic: { vi: "CẢM BIẾN",
           en: "SENSORS" },
  q: { vi: "Ba con robot Astrobee bay trong trạm vũ trụ “nhìn” và định hướng bằng gì?",
       en: "How do the three Astrobee robots “see” and navigate inside the space station?" },
  opts: [
    { vi: "Bằng camera và các cảm biến",
      en: "With cameras and sensors" },
    { vi: "Bằng một sợi dây nối tới máy tính của trạm",
      en: "Through a cable plugged into the station computer" },
    { vi: "Bằng cách hỏi phi hành gia sau mỗi mét",
      en: "By asking an astronaut every metre" },
    { vi: "Chúng không định hướng — chúng bay ngẫu nhiên",
      en: "They don't navigate — they drift at random" }
  ],
  a: 0,
  ok: { vi: "Chính xác! NASA nói <b>camera và các cảm biến</b> giúp chúng nhìn và định hướng. Cảm biến chính là “giác quan” của robot: không có chúng thì mọi phần thông minh phía sau cũng không có gì để suy nghĩ về.",
        en: "Correct! NASA says <b>cameras and sensors</b> help them see and navigate. Sensors are a robot's “senses”: without them, all the clever parts behind have nothing to think about." },
  no: { vi: "Chưa đúng. NASA nói <b>camera và các cảm biến</b> giúp chúng nhìn và định hướng. Chúng bay tự do trong trạm nên không thể có dây, và chúng làm việc <i>tự chủ</i> hoặc được điều khiển từ xa.",
        en: "Not quite. NASA says <b>cameras and sensors</b> help them see and navigate. They fly freely, so no cable — and they work <i>autonomously</i> or by remote control." },
  hint: { vi: "Mắt và tai của bạn tương ứng với bộ phận nào của robot?",
          en: "What is a robot's version of your eyes and ears?" },
  lv: 1,
  src: "astrobee",
  srcQuote: "Cameras and sensors help them to “see” and navigate their surroundings.",
  srcChecked: "2026-08-09"
};
