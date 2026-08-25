/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 1170,
  id: "lib-andromeda",
  src: "NASA",
  cat: "astronomy",
  em: "🌀",
  c: ["#c6d8ff", "#5a78c8", "#20305e"],
  img: "https://images-assets.nasa.gov/image/PIA04921/PIA04921~large.jpg",
  /* Anh cho THE LUOI (219x130 => can 438px o DPR2). Ban `~small` la 640px.
     ⚠️ `img` o tren GIU nguyen ban lon: the HERO ve o 598x210 (can 1196px).
     ⚠️ URL da mo va kiem 200 ngay 25/08/2026 — dung doan `~small`/`~medium`
        theo mau, `~medium` tra 403 o 3/6 anh nay. */
  thumb: "https://images-assets.nasa.gov/image/PIA04921/PIA04921~small.jpg",
  credit: "NASA / JPL-Caltech",
  /* ⚠️ Truoc 22/08/2026 truong nay tro TRANG CHU `science.nasa.gov/` — mot trang
     chu khong do duoc mot cau trich nao (noi dung doi hang ngay). Nay tro dung
     trang noi ve Tien Nu, cung la trang `andromeda` trong bang nguon. */
  url: "https://science.nasa.gov/universe/galaxies/andromeda-galaxy/",
  title: { vi: "Thiên hà Tiên Nữ — người hàng xóm khổng lồ",
          en: "The Andromeda Galaxy — our giant neighbour" },
  body: {
    vi: ["<b>Thiên hà</b> là một tập hợp khổng lồ gồm hàng trăm tỉ ngôi sao. Trái Đất của chúng ta nằm trong thiên hà Dải Ngân Hà.",
           "Tiên Nữ (Andromeda) là thiên hà lớn gần chúng ta nhất, cách khoảng 2,5 triệu năm ánh sáng — và đang tiến lại gần Dải Ngân Hà!"],
    en: ["A <b>galaxy</b> is a huge collection of hundreds of billions of stars. Our Earth lives in the Milky Way galaxy.",
           "Andromeda is the nearest big galaxy to us, about 2.5 million light-years away — and it's slowly heading toward the Milky Way!"]
  },
  term: { who: "byte",
           word: { vi: "Năm ánh sáng",
                   en: "Light-year" },
           text: { vi: "quãng đường ánh sáng đi trong 1 năm — cực kỳ xa nhé! 🤖",
                   en: "A <b>light-year</b> is how far light travels in one year — incredibly far! 🤖" } },
  /* Noi voi kho cau hoi: bai day dung ca hai — Trai Dat nam trong DAI NGAN HA,
     va Tien Nu la thien ha LON gan ta nhat. (Khong dat cau ve 2,5 trieu nam anh
     sang hay ve viec Tien Nu dang tien lai gan: bai co ghi, nhung ca hai trang
     nguon deu KHONG noi — khong dan nguon cho dieu trang khong chung minh.) */
  terms: ["earth-in-milky-way", "andromeda-nearest-large-galaxy"]
};
