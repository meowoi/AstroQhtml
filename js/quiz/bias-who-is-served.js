/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "bias-who-is-served",
  topic: { vi: "THIÊN LỆCH THUẬT TOÁN",
           en: "ALGORITHMIC BIAS" },
  q: { vi: "MIT cho học sinh làm thử một việc trên nền tảng như YouTube. Việc đó là gì?",
       en: "MIT has students try one thing on a platform such as YouTube. What is it?" },
  opts: [
    { vi: "Đếm xem mỗi ngày có bao nhiêu video mới được đăng lên",
      en: "Counting how many new videos are uploaded each day" },
    { vi: "Nghĩ về những người có liên quan, rồi thiết kế lại thuật toán gợi ý cho họ",
      en: "Considering the stakeholders, then redesigning the recommendation algorithm for them" },
    { vi: "Học cách quay một video cho thật nhiều người xem",
      en: "Learning to film a video that gets as many views as possible" },
    { vi: "Tìm ra mật khẩu của thuật toán để tắt nó đi",
      en: "Finding the algorithm's password so they can switch it off" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! Học sinh được yêu cầu nghĩ về <b>những người có liên quan</b> trong một nền tảng như YouTube, rồi thiết kế lại thuật toán gợi ý để đáp ứng nhu cầu của họ. Câu hỏi thật sự nằm ở đây: thuật toán nên phục vụ AI — người xem, người làm video, hay công ty? Ba câu trả lời cho ra ba thuật toán khác nhau.",
        en: "Right! Students are asked to consider the <b>stakeholders</b> in a platform such as YouTube, then redesign the recommendation algorithm to meet their needs. The real question sits here: who should it serve — the viewer, the creator, or the company? Three answers give three different algorithms." },
  no: { vi: "Chưa đúng. Học sinh được yêu cầu nghĩ về <b>những người có liên quan</b> rồi thiết kế lại thuật toán gợi ý cho họ. Đó là lý do người ta nói thuật toán cũng là một ý kiến: nó luôn phục vụ ai đó, và phục vụ ai là một lựa chọn.",
        en: "Not quite. Students are asked to consider the <b>stakeholders</b> and redesign the recommendation algorithm for them. That is why an algorithm is called an opinion: it always serves someone, and who it serves is a choice." },
  hint: { vi: "Một danh sách video gợi ý làm vui lòng người xem có chắc cũng làm vui lòng người làm video không?",
          en: "Does a recommendation list that pleases viewers necessarily please the creators too?" },
  lv: 3,
  src: "mitAlgorithms",
  srcQuote: "students are asked to consider the stakeholders in a platform such as YouTube, and how they might redesign YouTube's recommendation algorithm",
  srcChecked: "2026-08-20"
};
