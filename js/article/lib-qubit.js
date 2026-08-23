/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 5010,
  id: "lib-qubit",
  src: "NASA",
  cat: "quantum",
  em: "⚛️",
  c: ["#c6ffe6", "#4ade80", "#155e40"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/intelligent-systems-division/discovery-and-systems-health/nasa-quail/",
  title: { vi: "Qubit là gì, và vì sao đừng nói nó 'vừa 0 vừa 1'",
          en: "What a qubit is — and why not to say it's 'both 0 and 1'" },
  body: {
    vi: ["Máy tính bạn đang dùng lưu mọi thứ bằng bit, và mỗi bit chỉ nhận một trong hai giá trị. Máy tính lượng tử thì dùng một thứ khác, gọi là qubit. NASA viết định nghĩa của nó thế này: không như máy tính truyền thống, nơi các bit buộc phải mang giá trị 0 hoặc 1, một qubit có thể biểu diễn một số 0, một số 1, hoặc một chồng chập của cả hai giá trị.",
           "Hãy đọc kỹ ba chữ cuối. Cách nói bạn hay gặp là 'qubit vừa là 0 vừa là 1 cùng lúc', nhưng NASA không viết vậy — NASA viết đó là <b>một chồng chập</b> của hai giá trị. Đây không phải chuyện bắt bẻ chữ nghĩa: 'vừa cái này vừa cái kia' nghe như hai thứ nằm cạnh nhau, còn chồng chập là <i>một</i> trạng thái, và nó là trạng thái không có thứ gì trong đời sống hằng ngày giống hẳn.",
           "Cũng nên tránh cách ví với một đồng xu đang xoay tít, 'vừa ngửa vừa sấp cho tới khi bạn nhìn'. Nó dễ hiểu nhưng dẫn tới một ý sai hơn cả: rằng đồng xu ĐÃ ngửa hoặc ĐÃ sấp rồi, chỉ là ta chưa biết. Trong thế giới lượng tử thì không phải thế — bạn có thể đọc bài <i>Chồng chập</i> trong Góc Khám Phá để xem chỗ khác nhau ấy.",
           "Vậy vì sao người ta đi làm những cái máy khó hiểu như vậy? NASA nói: biểu diễn thông tin bằng qubit cho phép xử lý thông tin theo những cách không có gì tương đương trong tính toán cổ điển, bằng cách tận dụng những hiện tượng như rối lượng tử, giao thoa và hiệu ứng đường hầm. NASA có hẳn một phòng thí nghiệm riêng cho việc này — QuAIL, hình thành năm 2012 — và nhiệm vụ của nó, theo NASA, là xác định và phát triển tiềm năng của tính toán lượng tử để giúp các nhiệm vụ NASA trong tương lai tham vọng hơn, hiệu quả hơn và an toàn hơn."],
    en: ["The computer you are using stores everything in bits, and each bit takes one of just two values. A quantum computer uses something else, called a qubit. NASA writes its definition like this: unlike traditional computers, in which bits must have a value of either zero or one, a qubit can represent a zero, a one, or a superposition of both values.",
           "Read those last words carefully. The phrasing you usually meet is 'a qubit is both 0 and 1 at the same time', but that is not what NASA writes — NASA writes it is <b>a superposition</b> of both values. This is not nitpicking: 'both this and that' sounds like two things sitting side by side, whereas a superposition is <i>one</i> state, and it is a state nothing in everyday life quite matches.",
           "It is also worth avoiding the spinning-coin picture, 'both heads and tails until you look'. It is easy to grasp but leads to a worse idea: that the coin IS already heads or tails and we merely do not know yet. In the quantum world that is not the case — you can read the <i>Superposition</i> article in the Discovery Corner for exactly where the difference lies.",
           "So why build machines this puzzling at all? NASA says: representing information in qubits allows the information to be processed in ways that have no equivalent in classical computing, taking advantage of phenomena such as quantum entanglement, interference, and tunneling. NASA has a laboratory devoted to it — QuAIL, formed in 2012 — and its mandate, in NASA's words, is to determine and advance the potential for quantum computation to enable more ambitious, efficient, and safer NASA missions in the future."]
  },
  term: { who: "byte",
           word: { vi: "Qubit",
                   en: "Qubit" },
           text: { vi: "bit của máy tính lượng tử. Theo NASA nó biểu diễn được một số 0, một số 1, <i>hoặc một chồng chập</i> của cả hai — chứ không phải \"vừa 0 vừa 1\". 🤖",
                   en: "A <b>qubit</b> is a quantum computer's bit. Per NASA it can represent a zero, a one, <i>or a superposition</i> of both — not \"both 0 and 1\". 🤖" } },
  terms: ["qubit-superposition"]
};
