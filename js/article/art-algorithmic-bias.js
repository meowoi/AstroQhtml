/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3090,
  id: "art-algorithmic-bias",
  src: "AI & Tech",
  cat: "ai",
  em: "⚠️",
  c: ["#ffd9d9", "#c05a5a", "#301010"],
  img: null,
  credit: "MIT Media Lab",
  url: "https://www.media.mit.edu/projects/ai-ethics-for-middle-school/overview/",
  title: { vi: "Máy không cố ý thiên vị — nó học đúng thứ được cho xem",
          en: "A machine is not unfair on purpose — it learns exactly what it was shown" },
  body: {
    vi: ["MIT Media Lab dạy học sinh trung học cơ sở các khái niệm kỹ thuật — chẳng hạn cách huấn luyện một bộ phân loại đơn giản — <b>cùng với</b> những hệ quả về đạo đức mà chính các khái niệm kỹ thuật đó kéo theo, ví dụ như thiên lệch thuật toán.",
           "Hãy đọc lại chỗ nối: hệ quả đạo đức <i>do chính phần kỹ thuật kéo theo</i>, không phải một môn học riêng dạy sau. Bạn dạy máy nhận ra một thứ bằng cách cho nó xem ví dụ; những ví dụ bạn chọn quyết định nó nhận ra gì và bỏ sót gì. Máy không cố ý bất công — nó học đúng thứ nó được cho xem."],
    en: ["MIT Media Lab teaches middle school students technical concepts — such as how to train a simple classifier — <b>together with</b> the ethical implications those technical concepts entail, such as algorithmic bias.",
           "Read the join again: the ethical implications are entailed <i>by the technical part itself</i>, not taught afterwards as a separate subject. You teach a machine to recognise something by showing it examples; the examples you choose decide what it recognises and what it misses. The machine is not unfair on purpose — it learned exactly what it was shown."]
  },
  term: { who: "byte",
           word: { vi: "Bộ phân loại",
                   en: "Classifier" },
           text: { vi: "phần AI xếp một thứ vào một nhóm — thư này là rác hay không, ảnh này có mèo hay không. Nó học từ ví dụ. 🤖",
                   en: "A <b>classifier</b> is the part of an AI that sorts something into a group — spam or not, cat or no cat. It learns from examples. 🤖" } },
  terms: []
};
