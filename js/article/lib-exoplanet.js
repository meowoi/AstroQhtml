/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3110,
  id: "lib-exoplanet",
  src: "AI & Tech",
  cat: "ai",
  em: "🪐",
  c: ["#e6c6ff", "#a06be0", "#3a1f6e"],
  img: "https://images-assets.nasa.gov/image/PIA22082/PIA22082~orig.jpg",
  /* Anh cho THE LUOI (219x130 => can 438px o DPR2). Ban `~small` la 640px.
     ⚠️ `img` o tren GIU nguyen ban lon: the HERO ve o 598x210 (can 1196px).
     ⚠️ URL da mo va kiem 200 ngay 25/08/2026 — dung doan `~small`/`~medium`
        theo mau, `~medium` tra 403 o 3/6 anh nay. */
  thumb: "https://images-assets.nasa.gov/image/PIA22082/PIA22082~small.jpg",
  credit: "NASA / JPL-Caltech",
  url: "https://science.nasa.gov/exoplanets/",
  title: { vi: "AI giúp tìm hành tinh ngoài Hệ Mặt Trời",
          en: "AI helps find planets beyond the Solar System" },
  body: {
    vi: ["<b>Ngoại hành tinh</b> là những hành tinh quay quanh một ngôi sao khác, không phải Mặt Trời của chúng ta.",
           "Máy tính dùng <b>trí tuệ nhân tạo</b> để soi hàng triệu ngôi sao, nhận ra lúc ánh sáng chớp mờ đi — dấu hiệu có hành tinh đi ngang qua."],
    en: ["<b>Exoplanets</b> are planets orbiting other stars, not our Sun.",
           "Computers use <b>artificial intelligence</b> to scan millions of stars and spot tiny dips in brightness — a sign a planet passed in front."]
  },
  term: { who: "byte",
           word: { vi: "Trí tuệ nhân tạo",
                   en: "Artificial Intelligence" },
           text: { vi: "<b>AI</b> giúp máy tính học từ ví dụ để tự nhận ra quy luật — như cách tớ học vậy! 🤖",
                   en: "<b>AI</b> lets computers learn from examples to spot patterns by themselves — just like me! 🤖" } },
  /* Noi voi kho cau hoi: bai day CA hai: ngoai hanh tinh la hanh tinh quay quanh mot ngoi sao KHAC, va cach tim la thay anh sang ngoi sao mo di khi hanh tinh di ngang truoc mat. */
  terms: ["exoplanet", "exoplanet-transit"]
};
