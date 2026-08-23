/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "earth-in-milky-way",
  topic: { vi: "THIÊN HÀ",
           en: "GALAXIES" },
  q: { vi: "Trái Đất nằm trong thiên hà nào?",
       en: "Which galaxy is Earth in?" },
  opts: [
    { vi: "Thiên hà Tiên Nữ",
        en: "The Andromeda galaxy" },
    { vi: "Dải Ngân Hà",
        en: "The Milky Way" },
    { vi: "Thiên hà Tam Giác",
        en: "The Triangulum galaxy" },
    { vi: "Trái Đất không nằm trong thiên hà nào",
        en: "Earth is not in any galaxy" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA gọi Dải Ngân Hà là <b>thiên hà nhà</b> của chúng ta.",
        en: "Right! NASA calls the Milky Way our <b>home galaxy</b>." },
  no: { vi: "Chưa đúng! Thiên hà nhà của chúng ta là <b>Dải Ngân Hà</b>; Tiên Nữ là một thiên hà khác.",
        en: "Not quite! Our home galaxy is the <b>Milky Way</b>; Andromeda is a different galaxy." },
  hint: { vi: "Vệt sáng mờ vắt ngang trời đêm chính là thiên hà của chúng ta, nhìn từ bên trong nó.",
          en: "That faint band of light across the night sky is our own galaxy, seen from inside it." },
  lv: 1,
  src: "galaxies",
  srcQuote: "Our home galaxy is called the Milky Way.",
  srcChecked: "2026-08-22"
};
