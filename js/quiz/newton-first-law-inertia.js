/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "newton-first-law-inertia",
  topic: { vi: "ĐỊNH LUẬT NEWTON",
           en: "NEWTON'S LAWS" },
  q: { vi: "Xu hướng của một vật chống lại việc bị đổi trạng thái chuyển động gọi là gì?",
       en: "What is the name for an object's tendency to resist changes in its state of motion?" },
  opts: [
    { vi: "Lực đẩy",
      en: "Thrust" },
    { vi: "Quán tính",
      en: "Inertia" },
    { vi: "Ma sát",
      en: "Friction" },
    { vi: "Gia tốc",
      en: "Acceleration" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! Đó là <b>quán tính</b>. Định luật thứ nhất của Newton: vật đang đứng yên thì vẫn đứng yên, vật đang chuyển động thì cứ chuyển động thẳng đều — <b>trừ khi</b> có một lực không cân bằng tác dụng lên nó.",
        en: "Right! That is <b>inertia</b>. Newton's first law: an object at rest stays at rest and an object in motion keeps moving straight at constant speed - <b>unless</b> an unbalanced force acts on it." },
  no: { vi: "Chưa đúng! Tên của xu hướng đó là <b>quán tính</b>. Ma sát là một LỰC làm vật dừng, không phải xu hướng ấy.",
        en: "Not quite! That tendency is called <b>inertia</b>. Friction is a FORCE that stops things, not the tendency itself." },
  hint: { vi: "Đẩy một quyển sách trên bàn thì nó dừng. Vì Newton sai, hay vì có một lực nào đó tác dụng lên nó?",
          en: "Push a book across a table and it stops. Is Newton wrong, or is some force acting on it?" },
  lv: 2,
  src: "newtonsLaws",
  srcQuote: "This tendency to resist changes in a state of motion is inertia.",
  srcChecked: "2026-08-22"
};
