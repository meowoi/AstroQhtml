/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "orbit-needs-balance",
  topic: { vi: "QUỸ ĐẠO",
           en: "ORBITS" },
  q: { vi: "Theo NASA, hai thứ nào phải cân nhau để một quỹ đạo xảy ra?",
       en: "According to NASA, which two things must be balanced for an orbit to happen?" },
  opts: [
    { vi: "Nhiệt độ và áp suất",
      en: "Temperature and pressure" },
    { vi: "Khối lượng và thể tích",
      en: "Mass and volume" },
    { vi: "Đà của vật và lực hấp dẫn",
      en: "The object's momentum and the force of gravity" },
    { vi: "Ánh sáng và bóng tối",
      en: "Light and darkness" }
  ],
  a: 2,
  ok: { vi: "Đúng rồi! <b>Đà</b> của vật phải cân với <b>lực hấp dẫn</b>. Khi chúng cân nhau thì vật <b>luôn luôn đang rơi</b> về phía hành tinh — nhưng vì đi ngang đủ nhanh nên nó không bao giờ chạm tới.",
        en: "Right! The object's <b>momentum</b> must balance the <b>force of gravity</b>. When they balance, the object is <b>always falling</b> toward the planet - but moving sideways fast enough that it never hits." },
  no: { vi: "Chưa đúng! NASA nêu <b>đà</b> và <b>lực hấp dẫn</b>. Đà quá lớn thì vật vượt qua và bay mất; đà quá nhỏ thì nó bị kéo xuống và rơi.",
        en: "Not quite! NASA names <b>momentum</b> and <b>gravity</b>. Too much momentum and it speeds past; too little and it is pulled down and crashes." },
  hint: { vi: "Ở đây không có gì đứng yên cả — lực hấp dẫn vẫn kéo suốt. Vậy \"cân bằng\" là cân giữa hai việc nào?",
          en: "Nothing is at rest here - gravity never stops pulling. So what two motions are being balanced?" },
  lv: 3,
  src: "whatIsAnOrbit",
  srcQuote: "An object's momentum and the force of gravity have to be balanced for an orbit to happen.",
  srcChecked: "2026-08-22"
};
