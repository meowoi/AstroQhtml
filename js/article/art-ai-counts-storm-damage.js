/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3040,
  id: "art-ai-counts-storm-damage",
  src: "NASA",
  cat: "ai",
  em: "🏘️",
  c: ["#ffe8c8", "#d98a3c", "#402008"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/learning-resources/what-is-ai-grades-5-8/",
  title: { vi: "Sau một cơn bão, AI đếm những tấm bạt trên mái nhà",
          en: "After a storm, AI counts tarps on roofs" },
  body: {
    vi: ["Sau bão, người ta cần biết vùng nào bị nặng nhất để cứu trợ tới đúng chỗ. Đi hỏi từng nhà thì quá lâu, mà đúng lúc đó thời gian là thứ thiếu nhất.",
           "NASA nêu một cách rất bất ngờ: AI có thể đếm số tấm bạt phủ trên mái nhà trong ảnh vệ tinh để đo mức thiệt hại. Nhà bị vỡ mái thì người ta căng bạt lên — nên đếm bạt là đếm nhà bị hỏng. Điều hay ở đây không phải công nghệ, mà là ý tưởng: chọn một thứ máy <i>nhìn được</i> để thay cho thứ mình <i>muốn biết</i>."],
    en: ["After a storm, people need to know which areas were hit hardest so help goes to the right places. Asking house by house takes far too long, and time is exactly what is short.",
           "NASA describes a surprising method: AI can count tarps on roofs in satellite images to measure damage. A house with a broken roof gets a tarp over it — so counting tarps counts damaged homes. The clever part is not the technology but the idea: pick something a machine <i>can see</i> to stand in for what you <i>want to know</i>."]
  },
  term: { who: "byte",
           word: { vi: "Chỉ dấu thay thế",
                   en: "Proxy" },
           text: { vi: "Khi thứ bạn cần đo quá khó, hãy đo một <b>chỉ dấu thay thế</b> — thứ dễ thấy hơn nhưng đi cùng với nó. Bạt trên mái thay cho mái bị vỡ. 🤖",
                   en: "When the thing you need is too hard to measure, measure a <b>proxy</b> — something easier to see that travels with it. Tarps stand in for broken roofs. 🤖" } },
  terms: ["ai-counts-tarps"]
};
