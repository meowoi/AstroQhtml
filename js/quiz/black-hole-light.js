/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "black-hole-light",
  topic: { vi: "LỖ ĐEN",
           en: "BLACK HOLE" },
  q: { vi: "Thứ gì có thể thoát ra từ bên trong chân trời sự kiện của lỗ đen?",
       en: "What can escape from inside a black hole's event horizon?" },
  opts: [
    { vi: "Ánh sáng thì thoát được, vật chất thì không",
      en: "Light can escape, but matter cannot" },
    { vi: "Sóng vô tuyến thì thoát được",
      en: "Radio waves can escape" },
    { vi: "Vật gì đi đủ nhanh cũng thoát được",
      en: "Anything moving fast enough can escape" },
    { vi: "Không gì cả — kể cả ánh sáng",
      en: "Nothing at all — not even light" }
  ],
  a: 3,
  ok: { vi: "Đúng rồi! Lỗ đen đặc tới mức lực hấp dẫn ngay dưới chân trời sự kiện mạnh đến mức <b>không gì thoát ra được, kể cả ánh sáng</b>. Vì thế ta không thể nhìn thấy phần bên trong.",
        en: "Right! A black hole is so dense that gravity just beneath the event horizon is strong enough that <b>nothing can escape — not even light</b>. That's why we cannot see inside." },
  no: { vi: "Chưa đúng! <b>Không gì</b> thoát ra được, và ánh sáng cũng vậy — đó chính là lý do nó “đen”.",
        en: "Not quite! <b>Nothing</b> escapes, light included — that is exactly why it looks black." },
  hint: { vi: "Nghĩ về cái tên: vì sao ta gọi nó là lỗ <b>đen</b>?",
          en: "Think about the name: why do we call it a <b>black</b> hole?" },
  lv: 2,
  src: "bh"
};
