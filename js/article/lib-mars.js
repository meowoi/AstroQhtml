/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 1160,
  id: "lib-mars",
  src: "NASA",
  cat: "robot",
  em: "🔴",
  c: ["#ffcaa8", "#d1642f", "#5e2410"],
  img: "https://images-assets.nasa.gov/image/PIA21496/PIA21496~medium.jpg",
  /* Anh cho THE LUOI (219x130 => can 438px o DPR2). Ban `~small` la 640px.
     ⚠️ `img` o tren GIU nguyen ban lon: the HERO ve o 598x210 (can 1196px).
     ⚠️ URL da mo va kiem 200 ngay 25/08/2026 — dung doan `~small`/`~medium`
        theo mau, `~medium` tra 403 o 3/6 anh nay. */
  thumb: "https://images-assets.nasa.gov/image/PIA21496/PIA21496~small.jpg",
  credit: "NASA / JPL-Caltech",
  /* ⚠️ Truoc 22/08/2026 truong nay tro TRANG CHU `mars.nasa.gov/` — xem ly do
     o `lib-andromeda`. Nay tro dung trang nhiem vu Perseverance. */
  url: "https://science.nasa.gov/mission/mars-2020-perseverance/",
  title: { vi: "Robot Perseverance khám phá Sao Hỏa",
          en: "Perseverance rover exploring Mars" },
  body: {
    vi: ["<b>Xe tự hành</b> (rover) là robot 6 bánh do NASA gửi lên Sao Hỏa. Nó tự lái, chụp ảnh và thu thập mẫu đá.",
           "Perseverance đang tìm dấu vết của sự sống cổ đại và thử tạo khí oxy từ bầu khí quyển Sao Hỏa để giúp con người sau này."],
    en: ["A <b>rover</b> is a six-wheeled robot NASA sends to Mars. It drives itself, takes photos and collects rock samples.",
           "Perseverance is looking for signs of ancient life and even makes oxygen from Mars' air to help future explorers."]
  },
  term: { who: "byte",
           word: { vi: "Xe tự hành",
                   en: "Rover" },
           text: { vi: "<b>Rover</b> là robot biết tự lái trên hành tinh khác — giống anh em họ của tớ! 🤖",
                   en: "A <b>rover</b> is a robot that drives itself on another planet — like my cousin! 🤖" } },
  /* Noi voi kho cau hoi: bai day dung ca hai — Perseverance tim DAU VET SU SONG
     CO DAI, va no tao OXY tu bau khi quyen Sao Hoa. (Khong dat cau ve "6 banh"
     hay "tu lai": trang Perseverance khong noi hai dieu do.) */
  terms: ["perseverance-seeks-ancient-life", "moxie-oxygen-from-mars-air"]
};
