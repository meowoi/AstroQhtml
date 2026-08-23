/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "chatbot-does-not-remember",
  topic: { vi: "CHATBOT",
           en: "CHATBOTS" },
  q: { vi: "Hôm nay bạn kể cho một chatbot một chuyện quan trọng. Mai mở cuộc trò chuyện MỚI, nó có nhớ không?",
       en: "Today you tell a chatbot something important. Tomorrow, in a NEW conversation, will it remember?" },
  opts: [
    { vi: "Có, vì mọi thứ bạn gõ đều được nó học thuộc",
      en: "Yes — everything you type gets memorised" },
    { vi: "Có, nếu bạn nhắc nó nhớ cho kỹ",
      en: "Yes, if you ask it to remember carefully" },
    { vi: "Không — huấn luyện xong là “bộ não” của nó đứng yên, không tự nhận thêm kiến thức mới",
      en: "No — once trained, its “brain” is static and cannot take in new knowledge by itself" },
    { vi: "Không, vì nó xoá dữ liệu mỗi đêm cho đỡ nặng",
      en: "No, because it deletes data every night to save space" }
  ],
  a: 2,
  ok: { vi: "Đúng! Trò chuyện <b>không phải</b> là học. Mô hình được huấn luyện xong rồi mới đưa vào dùng, và từ lúc đó nó đứng yên — nên mỗi cuộc trò chuyện mới bắt đầu lại từ chỗ trắng.",
        en: "Right! Chatting is <b>not</b> learning. The model is trained first and deployed afterwards, and from then on it is static — so each new conversation starts from blank." },
  no: { vi: "Chưa đúng. MIT nói rõ: huấn luyện xong và đưa vào dùng thì <b>“bộ não” của nó đứng yên</b>. Nó không nhớ vì nó chưa bao giờ ghi lại, chứ không phải vì nó xoá đi.",
        en: "Not quite. MIT is explicit: once trained and deployed, its <b>“brain” is static</b>. It does not remember because it never recorded anything — not because it deleted it." },
  hint: { vi: "Hỏi xem nó ĐANG học, hay đã học xong từ trước rồi.",
          en: "Ask whether it is still learning, or finished learning long ago." },
  lv: 2,
  src: "mitLlmMemory",
  srcQuote: "Once a fully trained LLM has been deployed, its “brain” is static and can’t permanently adapt itself to new knowledge.",
  srcChecked: "2026-08-23"
};
