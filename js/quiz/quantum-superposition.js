/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "quantum-superposition",
  topic: { vi: "CHỒNG CHẬP LƯỢNG TỬ",
           en: "QUANTUM SUPERPOSITION" },
  q: { vi: "Theo NASA, hiệu ứng chồng chập (superposition) nghĩa là gì?",
       en: "According to NASA, what does the effect called superposition mean?" },
  opts: [
    { vi: "Hai hạt ở xa nhau vẫn liên hệ được với nhau",
      en: "Two distant particles stay correlated with each other" },
    { vi: "Một hạt chuyển động nhanh hơn ánh sáng",
      en: "A particle moves faster than light" },
    { vi: "Ta chưa biết hạt đó đang ở trạng thái nào",
      en: "We do not yet know which state the particle is in" },
    { vi: "Một hạt có thể ở nhiều trạng thái khác nhau cùng một lúc",
      en: "A particle can be in many different states at once" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA viết: cơ học lượng tử mô tả những hiệu ứng như chồng chập, <b>trong đó một hạt có thể ở nhiều trạng thái khác nhau cùng một lúc</b>. Đây là chỗ rất dễ kể sai: nó <b>không</b> nói rằng ta chưa biết — nó nói rằng <b>mô tả đúng về hạt đó, trước khi ta đo, gồm nhiều trạng thái cùng lúc</b>.",
       en: "Yes! NASA writes that quantum mechanics describes effects such as superposition, <b>where a particle can be in many different states at once</b>. This is the easiest thing to get wrong: it does <b>not</b> say we simply do not know — it says <b>the correct description of that particle, before we measure, includes many states at once</b>." },
  no: { vi: "Chưa đúng! Chồng chập là <b>một hạt ở nhiều trạng thái khác nhau CÙNG LÚC</b>. \"Ta chưa biết nó ở trạng thái nào\" là cách kể sai phổ biến nhất — và chỗ khác nhau giữa hai câu ấy chính là chỗ khác nhau giữa vật lý cổ điển và vật lý lượng tử. (Còn hai hạt ở xa vẫn liên hệ được thì gọi là <b>rối lượng tử</b>.)",
       en: "Not quite! Superposition is <b>one particle in many different states AT ONCE</b>. \"We just do not know which state it is in\" is the most common wrong telling — and the gap between those two sentences is the gap between classical and quantum physics. (Two distant particles staying linked is <b>entanglement</b>.)" },
  hint: { vi: "Chú ý: câu này nói về MỘT hạt, và về chuyện xảy ra TRƯỚC khi ta đo.",
         en: "Note: this is about ONE particle, and about what holds BEFORE we measure." },
  lv: 2,
  src: "quantumComputing",
  srcQuote: "Quantum mechanics describes effects such as superposition, where a particle can be in many different states at once.",
  srcChecked: "2026-08-23"
};
