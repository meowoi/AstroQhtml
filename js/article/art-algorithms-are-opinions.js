/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 370,
  id: "art-algorithms-are-opinions",
  src: "AI & Tech",
  cat: "ai",
  em: "⚖️",
  c: ["#ffe0f0", "#c05a98", "#2e1030"],
  img: null,
  credit: "MIT Media Lab",
  url: "https://www.media.mit.edu/projects/ai-ethics-for-middle-school/overview/",
  title: { vi: "Một thuật toán cũng là một ý kiến",
          en: "An algorithm is an opinion too" },
  body: {
    vi: ["Chúng ta hay nghĩ máy tính thì khách quan: nó chỉ tính toán, không thiên vị ai. MIT Media Lab dạy học sinh trung học cơ sở một ý khác hẳn, và nó gọn tới mức đáng nhớ: học sinh học cách nghĩ về thuật toán như những ý kiến. Một câu ngắn nhưng đảo hẳn cách nhìn — vì một ý kiến thì luôn là ý kiến CỦA AI ĐÓ, và luôn có thể khác đi.",
           "Vì sao lại thế? Vì mỗi thuật toán đều do người viết ra, và người viết phải chọn. Chọn xem cái gì là quan trọng, chọn xem xếp cái nào lên trước. Chương trình học của MIT đi song song hai thứ: học sinh học các khái niệm kỹ thuật — chẳng hạn cách huấn luyện một bộ phân loại đơn giản — cùng với những hệ quả về đạo đức mà chính các khái niệm kỹ thuật đó kéo theo, ví dụ như thiên lệch thuật toán.",
           "Hãy để ý cách đặt vấn đề đó. Nó không nói kỹ thuật là một chuyện còn đạo đức là chuyện khác, học xong cái này rồi mới học cái kia. Nó nói hệ quả đạo đức **do chính các khái niệm kỹ thuật kéo theo**. Bạn dạy máy nhận ra một thứ bằng cách cho nó xem ví dụ; những ví dụ bạn chọn quyết định nó nhận ra gì và bỏ sót gì. Chuyện đó vừa là kỹ thuật vừa là một lựa chọn.",
           "Và MIT cho học sinh làm thử trên một thứ chúng dùng hằng ngày: học sinh được yêu cầu suy nghĩ về những người có liên quan trong một nền tảng như YouTube, và cách chúng sẽ thiết kế lại thuật toán gợi ý của YouTube để đáp ứng nhu cầu của những người đó. Câu hỏi ấy rất đáng thử: thuật toán gợi ý video nên phục vụ ai — người xem, người làm video, hay công ty? Ba câu trả lời cho ra ba thuật toán khác nhau. Đó chính là chỗ nó thành một ý kiến."],
    en: ["We tend to assume computers are objective: they just calculate, without favouring anyone. MIT Media Lab teaches middle school students something quite different, and it is short enough to remember: students learn to think of algorithms as opinions. A brief sentence, but it flips the whole view — because an opinion always belongs to SOMEONE, and could always have been otherwise.",
           "Why would that be? Because every algorithm is written by people, and those people have to choose. Choose what counts as important, choose what gets ranked first. MIT's curriculum runs two things side by side: students learn technical concepts — such as how to train a simple classifier — and the ethical implications those technical concepts entail, such as algorithmic bias.",
           "Notice how that is framed. It does not say the technical part is one subject and ethics another, to be studied afterwards. It says the ethical implications are entailed by the technical concepts themselves. You teach a machine to recognise something by showing it examples; the examples you pick decide what it recognises and what it misses. That is simultaneously a technical act and a choice.",
           "And MIT has students try this on something they use every day: students are asked to consider the stakeholders in a platform such as YouTube, and how they might redesign YouTube's recommendation algorithm to meet the needs of those stakeholders. It is a question worth attempting: who should a video recommendation serve — the viewer, the person who made the video, or the company? Three answers give three different algorithms. That is precisely where it becomes an opinion."]
  },
  term: { who: "byte",
           word: { vi: "Thiên lệch thuật toán",
                   en: "Algorithmic bias" },
           text: { vi: "<b>Thiên lệch thuật toán</b> là khi một hệ thống đối xử không đều với các nhóm khác nhau — thường vì dữ liệu dạy nó vốn đã lệch. Máy không cố ý; nó học đúng thứ nó được cho xem. 🤖",
                   en: "<b>Algorithmic bias</b> is a system treating groups unevenly — usually because the data that taught it was already skewed. The machine is not being unfair on purpose; it learned exactly what it was shown. 🤖" } },
  terms: []
};
