/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 4010,
  id: "art-how-data-gets-home",
  src: "NASA",
  cat: "it",
  em: "📡",
  c: ["#d4f0e8", "#4aa890", "#123a30"],
  img: null,
  credit: null,
  url: "https://spaceplace.nasa.gov/dsn-antennas/en/",
  title: { vi: "Ảnh từ Sao Hoả về tới màn hình bạn bằng cách nào?",
          en: "How does a picture from Mars reach your screen?" },
  body: {
    vi: ["Một tấm ảnh chụp trên Sao Hoả không tự bay về Trái Đất. Nó phải được gửi đi thành tín hiệu vô tuyến, và ở đầu này phải có ai đó đang lắng nghe. NASA gọi hệ thống lắng nghe đó là Mạng Không Gian Sâu, và mô tả rất gọn: đó là một tập hợp những ăng-ten vô tuyến lớn ở các nơi khác nhau trên thế giới.",
           "Phía tàu vũ trụ chỉ có ăng-ten nhỏ, nên NASA nói chúng chỉ có thể phát những tín hiệu vô tuyến <b>yếu</b> về Trái Đất. Vì thế phần khó không nằm ở việc gửi, mà ở việc <i>nghe được</i>: ăng-ten ở Trái Đất phải thật lớn — ăng-ten lớn nhất ở mỗi trạm rộng 70 mét (230 foot)."],
    en: ["A photograph taken on Mars does not fly home by itself. It has to be sent as a radio signal, and someone at this end has to be listening. NASA calls that listening system the Deep Space Network, and describes it simply: a collection of big radio antennas in different parts of the world.",
           "The spacecraft only carries small antennas, so NASA says they can beam only <b>weak</b> radio signals back to Earth. The hard part is therefore not the sending but the <i>hearing</i>: the antennas on Earth have to be enormous — the largest at each site is 70 meters (230 feet) across."]
  },
  term: { who: "byte",
           word: { vi: "Tín hiệu vô tuyến",
                   en: "Radio signal" },
           text: { vi: "cách gửi thông tin đi mà không cần dây. Cùng một họ với sóng đài phát thanh và wifi ở nhà bạn. 🤖",
                   en: "A <b>radio signal</b> carries information with no wire. Same family as radio broadcasts and the wifi in your home. 🤖" } },
  terms: ["dsn-why-big-antennas"]
};
