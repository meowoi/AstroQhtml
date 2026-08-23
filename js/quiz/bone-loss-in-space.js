/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "bone-loss-in-space",
  topic: { vi: "CƠ THỂ TRONG KHÔNG GIAN",
           en: "THE BODY IN SPACE" },
  q: { vi: "Theo NASA, xương chịu lực (xương chân, xương hông) mất bao nhiêu mật độ khoáng mỗi tháng bay?",
       en: "According to NASA, how much mineral density do weight-bearing bones lose each month in spaceflight?" },
  opts: [
    { vi: "Khoảng 0,1% mỗi tháng",
      en: "About 0.1% a month" },
    { vi: "Trung bình 1% đến 1,5% mỗi tháng",
      en: "On average 1% to 1.5% a month" },
    { vi: "Khoảng 10% mỗi tháng",
      en: "About 10% a month" },
    { vi: "Không mất gì cả",
      en: "They lose nothing at all" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA đo được <b>1% đến 1,5% mỗi tháng</b> — và chỉ ở những xương <b>chịu lực</b>, tức những xương ngày nào cũng phải đỡ sức nặng của em.",
        en: "Right! NASA measured <b>1% to 1.5% per month</b> — and only in <b>weight-bearing</b> bones, the ones that carry your weight every day." },
  no: { vi: "Chưa đúng! Con số NASA đưa ra là <b>1% đến 1,5% mỗi tháng</b>. Nghe nhỏ, nhưng một chuyến bay dài thì cộng lại thành nhiều.",
        en: "Not quite! NASA's figure is <b>1% to 1.5% per month</b>. That sounds small, but it adds up over a long flight." },
  hint: { vi: "Xương là mô sống. Tín hiệu nói cho nó biết cần dày tới đâu chính là sức nặng đè lên nó mỗi ngày.",
          en: "Bone is living tissue. The signal telling it how thick to be is the weight pressing on it every day." },
  lv: 2,
  src: "bodyInSpace",
  srcQuote: "weight-bearing bones lose on average 1% to 1.5% of mineral density per month during spaceflight",
  srcChecked: "2026-08-22"
};
