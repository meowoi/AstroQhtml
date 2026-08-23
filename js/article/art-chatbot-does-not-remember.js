/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3120,
  id: "art-chatbot-does-not-remember",
  src: "AI & Tech",
  cat: "ai",
  em: "🧠",
  c: ["#d8e4ff", "#5f7bd6", "#131c3c"],
  img: null,
  credit: null,
  url: "https://news.mit.edu/2025/teaching-large-language-models-to-absorb-new-knowledge-1112",
  title: { vi: "Chatbot không nhớ điều bạn vừa kể cho nó",
          en: "A chatbot does not remember what you just told it" },
  body: {
    vi: ["Bạn kể cho chatbot một chuyện quan trọng. Hôm sau mở cuộc trò chuyện mới, nó không biết gì cả. Nhiều bạn tưởng mình gõ sai chỗ, hoặc tưởng nó cố tình quên.",
           "MIT giải thích: một mô hình ngôn ngữ lớn sau khi được huấn luyện xong và đưa vào dùng thì <b>“bộ não” của nó đứng yên</b> — nó không tự thay đổi mình để nhận thêm kiến thức mới. Nên nếu hôm nay bạn nói với nó một điều gì đó, thì <i>lần sau mở một cuộc trò chuyện mới, nó sẽ không nhớ điều ấy</i>. Nó không quên — nó chưa bao giờ ghi lại."],
    en: ["You tell a chatbot something important. The next day you open a new conversation and it knows nothing about it. Many people assume they typed in the wrong place, or that it forgot on purpose.",
           "MIT explains it: once a large language model has finished training and been put to work, its <b>“brain” is static</b> — it cannot permanently change itself to take in new knowledge. So if you tell it something today, <i>the next time you start a new conversation it will not remember</i>. It did not forget — it never wrote it down."]
  },
  term: { who: "byte",
           word: { vi: "Bộ não đứng yên",
                   en: "A static brain" },
           text: { vi: "Huấn luyện xong là <b>đóng băng</b>. Trò chuyện không phải học — mỗi cuộc trò chuyện mới bắt đầu lại từ chỗ trắng. 🤖",
                   en: "Once training ends, it is <b>frozen</b>. Chatting is not learning — every new conversation starts from blank. 🤖" } },
  terms: ["chatbot-does-not-remember"]
};
