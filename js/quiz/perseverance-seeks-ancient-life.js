/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "perseverance-seeks-ancient-life",
  topic: { vi: "ROBOT TRÊN SAO HOẢ",
           en: "ROVERS ON MARS" },
  q: { vi: "Robot Perseverance đang tìm gì trên Sao Hoả?",
       en: "What is the Perseverance rover searching for on Mars?" },
  opts: [
    { vi: "Người ngoài hành tinh đang sống ở đó",
        en: "Aliens living there right now" },
    { vi: "Vàng và kim cương",
        en: "Gold and diamonds" },
    { vi: "Một hành tinh mới",
        en: "A brand new planet" },
    { vi: "Dấu vết của sự sống vi sinh cổ đại",
        en: "Signs of ancient microbial life" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! NASA ghi Perseverance đang tìm <b>dấu vết của sự sống vi sinh cổ đại</b> — những sinh vật rất nhỏ, sống từ rất lâu về trước.",
        en: "Right! NASA says Perseverance is searching for <b>signs of ancient microbial life</b> - tiny living things from very long ago." },
  no: { vi: "Chưa đúng! Nó không đi tìm người ngoài hành tinh đang sống, mà tìm <b>dấu vết của sự sống vi sinh cổ đại</b> còn lưu trong đá.",
        en: "Not quite! It is not looking for aliens alive today, but for <b>signs of ancient microbial life</b> preserved in the rocks." },
  hint: { vi: "Hai chữ quan trọng là \"cổ đại\" và \"vi sinh\": thứ nó tìm vừa rất nhỏ, vừa đã qua từ lâu.",
          en: "Two words matter: \"ancient\" and \"microbial\" - what it seeks was both tiny and long ago." },
  lv: 2,
  src: "perseverance",
  srcQuote: "The Mars 2020 Perseverance Rover is searching for signs of ancient microbial life, to advance NASA's quest to explore the past habitability of Mars.",
  srcChecked: "2026-08-22"
};
