/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "llm-not-fully-understood",
  topic: { vi: "CHATBOT",
           en: "CHATBOTS" },
  q: { vi: "Mô hình ngôn ngữ lớn do con người làm ra. Vậy có phải người ta đã hiểu rõ bên trong nó xảy ra chuyện gì?",
       en: "Large language models are built by people. So do we fully understand what happens inside them?" },
  opts: [
    { vi: "Đúng, vì người viết ra từng dòng lệnh của nó",
      en: "Yes — people wrote every line of its code" },
    { vi: "Đúng, vì nếu không hiểu thì đã không ai dám dùng",
      en: "Yes — nobody would use it if they did not understand it" },
    { vi: "Không, nhưng chỉ vì các công ty giữ bí mật",
      en: "No, but only because companies keep it secret" },
    { vi: "Không — dù đã được dùng làm công cụ trong nhiều lĩnh vực, các nhà khoa học vẫn chưa hiểu hết cách chúng hoạt động",
      en: "No — although they are used as tools in many areas, scientists still do not fully grasp how they work" }
  ],
  a: 3,
  ok: { vi: "Đúng, và đây là chỗ rất đáng nhớ. Người ta viết <b>cách huấn luyện</b>, chứ không viết ra từng luật mà mô hình rút được — nên biết một thứ <b>dùng được</b> khác với biết nó <b>hoạt động thế nào</b>. Chính vì thế mới có nhóm nghiên cứu đi mổ xẻ bên trong.",
        en: "Yes, and this is worth remembering. People write the <b>training method</b>, not each rule the model derives — so knowing something <b>works</b> is not knowing <b>how</b> it works. That is exactly why research groups dig into their insides." },
  no: { vi: "Chưa đúng. Đây không phải chuyện giữ bí mật: MIT viết rằng <b>các nhà khoa học vẫn chưa hiểu hết</b> cách những mô hình này hoạt động, dù chúng đã được dùng làm công cụ ở nhiều nơi.",
        en: "Not quite. This is not about secrecy: MIT writes that <b>scientists still do not fully grasp</b> how these models work, even though they are already used as tools in many areas." },
  hint: { vi: "Người viết ra CÁCH HUẤN LUYỆN, hay viết ra từng luật mà máy rút được?",
          en: "Do people write the TRAINING METHOD, or each rule the machine derives?" },
  lv: 3,
  src: "mitLlmMechanism",
  srcQuote: "Even though these models are being used as tools in many areas, such as customer support, code generation, and language translation, scientists still don’t fully grasp how they work.",
  srcChecked: "2026-08-23"
};
