/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "oxygen-from-electrolysis",
  topic: { vi: "HỆ GIỮ MẠNG SỐNG",
           en: "LIFE SUPPORT" },
  q: { vi: "Oxy để phi hành đoàn thở trên trạm được làm ra từ đâu?",
       en: "Where does the oxygen the station crew breathes come from?" },
  opts: [
    { vi: "Từ những bình oxy chở lên từ Trái Đất",
      en: "From oxygen tanks shipped up from Earth" },
    { vi: "Từ việc tách nước bằng dòng điện",
      en: "From splitting water with electricity" },
    { vi: "Từ cây cối trồng trong khu vườn Veggie",
      en: "From the plants in the Veggie garden" },
    { vi: "Hút từ khí quyển Trái Đất qua một ống dài",
      en: "Piped up from Earth's atmosphere" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! Bộ sinh oxy có một chồng pin <b>điện phân</b> — nó <b>tách nước ra</b>, cho oxy và hydro. Oxy đưa vào cabin để thở; nước thì đến từ chính hệ thu hồi nước.",
        en: "Right! The oxygen generator has a cell stack that <b>electrolyzes</b> - it <b>breaks water apart</b>, yielding oxygen and hydrogen. The oxygen goes to the cabin; the water comes from the water recovery system." },
  no: { vi: "Chưa đúng! Chở oxy lên thì không đủ cho những chuyến dài. Trạm <b>tách nước</b> bằng dòng điện, và một trong hai mảnh tách ra chính là oxy.",
        en: "Not quite! Shipping oxygen up cannot sustain long missions. The station <b>splits water</b> with electricity, and one of the two pieces is oxygen." },
  hint: { vi: "Nước gồm hai nguyên tố. Nếu tách được nó ra thì em nhận được những gì?",
          en: "Water is made of two elements. If you pull it apart, what do you get?" },
  lv: 3,
  src: "eclss",
  srcQuote: "the cell stack, which electrolyzes, or breaks apart, water provided by the Water Recovery System, yielding oxygen and hydrogen as byproducts",
  srcChecked: "2026-08-22"
};
