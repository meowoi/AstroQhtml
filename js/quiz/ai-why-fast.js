/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-why-fast",
  topic: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
  q: { vi: "Vì sao các nhà thiên văn để AI soi hàng chục nghìn ảnh Hubble thay vì tự xem từng ảnh?",
       en: "Why do astronomers let AI comb through tens of thousands of Hubble images instead of looking at each one themselves?" },
  opts: [
    { vi: "Vì AI thấy được những thứ mắt người không bao giờ thấy",
      en: "Because AI can see things human eyes never could" },
    { vi: "Vì người sẽ mất vô số giờ, còn AI nhận ra mẫu rất nhanh",
      en: "Because people would need countless hours, while AI recognises patterns fast" },
    { vi: "Vì AI không bao giờ sai",
      en: "Because AI never makes mistakes" },
    { vi: "Vì ảnh Hubble quá mờ, người không xem được",
      en: "Because Hubble images are too blurry for people" }
  ],
  a: 1,
  ok: { vi: "Đúng! NASA nói thẳng: <b>người sẽ phải mất vô số giờ</b> để soi hết dữ liệu của nhiều năm quan sát, còn <b>AI dùng nhận dạng mẫu để chỉ ra nhanh những phần đáng chú ý</b>. Lợi thế ở đây là <b>khối lượng và tốc độ</b>, chứ không phải AI thấy được điều con người không thấy.",
          en: "Yes! NASA puts it plainly: <b>it would take countless hours for individuals</b> to sort through years of observations, while <b>AI uses pattern recognition to swiftly identify key components</b>. The advantage is <b>volume and speed</b>, not seeing what humans cannot." },
  no: { vi: "Chưa đúng! Lý do là <b>khối lượng công việc</b>: hàng chục nghìn ảnh thì người soi hết sẽ mất vô số giờ. AI nhanh, nhưng nó <b>không</b> phải thứ không bao giờ sai — chính dự án đó vẫn cần hàng nghìn người tình nguyện cùng kiểm.",
          en: "Not quite! The reason is <b>sheer volume</b>: tens of thousands of images would take a person countless hours. AI is fast, but it is <b>not</b> infallible — that very project still needed thousands of volunteers checking alongside it." },
  hint: { vi: "Thử nhân xem: 30.000 ảnh, mỗi ảnh vài phút thì mất bao lâu?",
            en: "Do the multiplication: 30,000 images at a few minutes each is how long?" },
  lv: 3,
  src: "aiHubble",
  srcQuote: "But while it would take countless hours for individuals to sort through information from years of observations, artificial intelligence (AI) programs can use pattern recognition to swiftly identify key components",
  srcChecked: "2026-08-19"
};
