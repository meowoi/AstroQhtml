/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "eclipse-umbra-total-blocked",
  topic: { vi: "Thiên Văn",
           en: "Astronomy" },
  q: { vi: "Người quan sát đứng trong vùng bóng tối trung tâm (umbra) của Mặt Trăng sẽ nhìn thấy hiện tượng gì?",
       en: "What do observers standing within the Moon's central umbra see?" },
  opts: [
    { vi: "Nhìn thấy Mặt Trời bị che khuất hoàn toàn",
      en: "They see the Sun completely blocked" },
    { vi: "Nhìn thấy Mặt Trời chỉ bị che một phần nhỏ",
      en: "They see the Sun only partially covered" },
    { vi: "Nhìn thấy Mặt Trăng phát ra ánh sáng xanh",
      en: "They see the Moon emitting blue light" },
    { vi: "Không nhìn thấy bất kỳ bóng tối nào",
      en: "They see no shadow at all" }
  ],
  a: 0,
  ok: { vi: "Chính xác! Đứng trong vùng umbra hẹp, bạn sẽ trải nghiệm nhật thực toàn phần với Mặt Trời bị che khuất hoàn toàn.",
        en: "Correct! Within the central umbra, observers witness the Sun completely covered." },
  no: { vi: "Chưa đúng. Vùng bóng tối đậm nhất umbra mang lại góc nhìn nhật thực toàn phần.",
        en: "Incorrect. The dark umbral cone provides a view of total solar obscuration." },
  hint: { vi: "Vùng umbra là vùng tâm bóng tối nhất trên Trái Đất.",
          en: "The umbra is the darkest central shadow zone on Earth." },
  lv: 2,
  src: "nasaEclipseGeometry",
  srcQuote: "Observers on Earth who are within the smaller, central umbra see the Sun completely blocked.",
  srcChecked: "2026-08-06"
};
