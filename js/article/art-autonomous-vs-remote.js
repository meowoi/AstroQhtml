/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 2010,
  id: "art-autonomous-vs-remote",
  src: "NASA",
  cat: "robot",
  em: "🎛️",
  c: ["#d8e8ff", "#5a80c0", "#16233f"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/astrobee/",
  title: { vi: "Hai kiểu điều khiển robot: tự chủ và từ xa",
          en: "Two ways to run a robot: autonomous and remote" },
  body: {
    vi: ["Một con robot có thể hoạt động theo hai kiểu, và phân biệt được hai kiểu ấy là hiểu được gần hết chuyện robot làm việc thế nào. NASA nói về ba con robot Astrobee trên trạm vũ trụ: chúng làm việc <b>tự chủ</b>, <b>hoặc</b> được <b>điều khiển từ xa</b> bởi phi hành gia, người điều hành chuyến bay hoặc các nhà nghiên cứu ở mặt đất.",
           "Tự chủ nghĩa là robot tự quyết từng bước để xong việc được giao. Điều khiển từ xa nghĩa là có người quyết, robot chỉ thi hành. Cùng một con robot, cùng một việc — chỉ khác ai đang quyết. Và cùng một con robot có thể đổi qua lại giữa hai kiểu, tuỳ việc đó cần gì."],
    en: ["A robot can run in two modes, and telling them apart gets you most of the way to understanding how robots work. NASA describes the three Astrobee robots on the space station: they work <b>autonomously</b>, <b>or</b> by <b>remote control</b> from astronauts, flight controllers or researchers on the ground.",
           "Autonomous means the robot decides each step itself to finish the job it was given. Remote control means a person decides and the robot carries it out. Same robot, same task — the only difference is who is deciding. And one robot can switch between the two, depending on what the job needs."]
  },
  term: { who: "byte",
           word: { vi: "Tự chủ",
                   en: "Autonomous" },
           text: { vi: "không có nghĩa là robot muốn gì làm nấy — nó vẫn nhận việc từ người, chỉ tự quyết <i>cách</i> làm. 🤖",
                   en: "does not mean a robot does as it pleases — it still gets its job from people, and only decides <i>how</i> to do it. 🤖" } },
  terms: []
};
