/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 1130,
  id: "lib-nebula",
  src: "NASA",
  cat: "astronomy",
  em: "🌌",
  c: ["#8ee0ff", "#2f6fd0", "#0e2a5e"],
  img: "https://images-assets.nasa.gov/image/PIA25433/PIA25433~large.jpg",
  /* Anh cho THE LUOI (219x130 => can 438px o DPR2). Ban `~small` la 640px.
     ⚠️ `img` o tren GIU nguyen ban lon: the HERO ve o 598x210 (can 1196px).
     ⚠️ URL da mo va kiem 200 ngay 25/08/2026 — dung doan `~small`/`~medium`
        theo mau, `~medium` tra 403 o 3/6 anh nay. */
  thumb: "https://images-assets.nasa.gov/image/PIA25433/PIA25433~small.jpg",
  credit: "NASA / JPL-Caltech",
  url: "https://science.nasa.gov/mission/webb/",
  title: { vi: "Tinh vân Đại Bàng — vườn ươm của các ngôi sao",
          en: "The Eagle Nebula — a nursery of stars" },
  body: {
    vi: ["Trong vũ trụ có những đám mây khí và bụi khổng lồ gọi là <b>tinh vân</b>. Bên trong chúng, khí co lại và nóng dần lên cho tới khi bùng cháy thành những ngôi sao mới.",
           "Tinh vân Đại Bàng nổi tiếng với 'Những Cột Trụ Sáng Tạo' — các cột khí cao hàng nghìn tỉ km, nơi hàng loạt ngôi sao đang chào đời."],
    en: ["Space has giant clouds of gas and dust called <b>nebulae</b>. Inside them, gas squeezes together and heats up until it lights up as new stars.",
           "The Eagle Nebula is famous for the 'Pillars of Creation' — towers of gas trillions of km tall where many stars are being born."]
  },
  term: { who: "comet",
           word: { vi: "Tinh vân",
                   en: "Nebula" },
           text: { vi: "'đám mây' khổng lồ bằng khí và bụi trong vũ trụ — chính là nơi các ngôi sao ra đời đó! 🐱",
                   en: "A <b>nebula</b> is a giant 'cloud' of gas and dust in space — it's where stars are born! 🐱" } },
  /* Noi voi kho cau hoi: bai day dung cau tra loi: sao sinh ra trong nhung dam may khi va bui khong lo. (Khong noi `nebula-gas`: cau do hoi NGUYEN NHAN co lai — luc hap dan — ma bai khong he noi.) */
  terms: ["nebula"]
};
