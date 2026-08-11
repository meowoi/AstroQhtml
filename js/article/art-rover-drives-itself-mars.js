/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 2030,
  id: "art-rover-drives-itself-mars",
  src: "NASA",
  cat: "robot",
  em: "🤖",
  c: ["#ffe0c2", "#c8562a", "#3a1508"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/solar-system/nasas-self-driving-perseverance-mars-rover-takes-the-wheel/",
  title: { vi: "Chiếc xe tự lái xa nhà nhất: rover trên Sao Hỏa",
          en: "The most distant self-driving car: a rover on Mars" },
  body: {
    vi: ["Hãy thử tưởng tượng bạn phải lái một chiếc xe ở cách xa tới mức mỗi mệnh lệnh mất nhiều phút mới tới nơi. Đó chính là chuyện xảy ra với rover trên Sao Hỏa. Vì tín hiệu radio giữa Trái Đất và Sao Hỏa bị trễ, đội điều khiển không thể chỉ cầm một cái cần gạt rồi đẩy rover đi tới. Đến lúc bạn nhìn thấy tảng đá phía trước thì bánh xe đã lăn qua nó từ lâu rồi.",
           "Nên cách làm trước đây là con người lên kế hoạch trước từng chút một. Các kỹ sư soi kỹ ảnh chụp từ vệ tinh, có lúc đeo cả kính 3D để nhìn địa hình quanh rover cho ra chiều sâu. Khi cả đội đã đồng ý, họ mới truyền bộ lệnh lên Sao Hỏa, và hôm sau rover mới thi hành đúng bộ lệnh đó. Một ngày làm việc của chiếc xe được vạch sẵn từ một hành tinh khác.",
           "Rồi rover Perseverance được trang bị một hệ thống tên là AutoNav. Nó tự dựng bản đồ ba chiều của địa hình phía trước, tự nhận ra những chỗ nguy hiểm, và tự vạch một đường vòng qua vật cản mà không cần thêm chỉ dẫn nào từ những người điều khiển ở Trái Đất. Một kỹ sư của NASA gọi khả năng đó bằng một cụm từ rất dễ nhớ: vừa đi vừa nghĩ — rover suy nghĩ về đường đi trong lúc bánh xe vẫn đang lăn.",
           "Việc đó đổi được bao nhiêu? Cộng thêm vài cải tiến khác, Perseverance có thể đạt tốc độ tối đa khoảng 120 mét mỗi giờ, trong khi chiếc rover đàn anh Curiosity — dùng một bản AutoNav cũ hơn — đi được chừng 20 mét mỗi giờ. Nhóm kỹ sư nói họ đã làm AutoNav nhanh lên bốn tới năm lần. Nghe thì chậm, nhưng hãy nhớ: không ai ngồi trong xe cả, và người gần nhất đang ở cách đó hàng chục triệu ki-lô-mét."],
    en: ["Imagine driving a car so far away that every command takes minutes to arrive. That is exactly the situation for a rover on Mars. Because of the radio signal delay between Earth and Mars, the team cannot simply push the rover forward with a joystick. By the time you spot the rock ahead, the wheels have long since rolled over it.",
           "So the old approach was for humans to plan every stretch in advance. Engineers studied satellite images closely, sometimes even putting on 3D glasses to see the ground around the rover with real depth. Once the team signed off, they beamed the instructions to Mars, and the rover carried them out the following day. A whole working day for the vehicle was mapped out from another planet.",
           "Then the Perseverance rover was given a system called AutoNav. It makes 3D maps of the terrain ahead, identifies hazards, and plans a route around any obstacles without additional direction from controllers back on Earth. One NASA engineer described the ability with a phrase that is easy to remember: thinking while driving — the rover is working out its route while its wheels are still turning.",
           "How much difference does that make? Combined with a few other improvements, Perseverance might reach a top speed of about 120 meters per hour, while its older sibling Curiosity — running an earlier version of AutoNav — covers roughly 20 meters per hour. The engineers say they sped AutoNav up by four or five times. It sounds slow, but remember: nobody is sitting in the driver's seat, and the nearest person is tens of millions of kilometres away."]
  },
  term: { who: "byte",
           word: { vi: "Vật cản",
                   en: "Hazard" },
           text: { vi: "thứ chắn đường robot — tảng đá, cái hố, dốc quá đứng. Nhận ra nó là việc đầu tiên, đi vòng qua nó là việc thứ hai. 🤖",
                   en: "A <b>hazard</b> is anything blocking a robot's path — a rock, a hole, a slope too steep. Spotting it comes first; steering around it comes second. 🤖" } },
  terms: ["sensor", "condition", "sequence", "algorithm"]
};
