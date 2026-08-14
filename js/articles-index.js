/* js/articles-index.js — MUC LUC KHO BAI DOC + BO NAP.

   ⚠️⚠️ FILE NAY SINH RA BANG SCRIPT — DUNG SUA BANG TAY.
        Nguon su that la `js/article/<id>.js` (MOT BAI MOI FILE, chua DU moi truong).
        Them bai = them file roi chay:  python scratchpad/split_articles.py

   VI SAO KHONG CON MOT FILE `js/articles.js` — do 09/08/2026, khong doan:
     mot-file la **52,3 KB gzip cho 39 bai = 52% duong tai cua library.html**, ma tre
     chi doc **1 bai** moi luot. Dung nguong da buoc chia ngan hang cau hoi ngay
     07/08/2026 (43,6 KB = 51% duong tai quiz.html, dung 5/100 cau). Tach ra: phan
     nhe **3,7 KB**, phan nang (than bai) **43,4 KB = 92%**. Con so nay KHONG TANG
     khi kho lon len — do la ca ly do chon don vi chia la TUNG BAI.

   MUC LUC GIU GI: id · src · cat · em · c[3] · img · title — dung du cho luoi the,
   3 o cua khoi noi bat, va bo loc nguon/chu de. `body`/`term`/`url`/`credit`/`terms`
   nam trong file bai, tai khi CAN:
     · mo trinh doc            -> load(id)
     · doan mo dau cua THE LON o khoi noi bat -> load(id) cua dung mot bai
     · tim kiem toan van       -> loadAll(), goi khi tre bat dau tim

   LUAT NOI DUNG (cho bai moi — bo kiem `smoke_library_featured.py` muc [8] canh):
     · `url` phai tra 200 va thuoc nguon tin cay (NASA · ESA · NOAA · USGS · NPS ·
       MIT · Exploratorium · LCO · UCAR). MIT vao danh sach 09/08/2026 vi NASA gan
       nhu khong co noi dung ve AI trong DOI SONG; bo `wiki/` da dan MIT tu truoc.
     · moi con so trong than bai phai TRICH DUOC nguyen van tu trang nguon.
     · `body.vi` va `body.en` phai CUNG SO DOAN.
     · `terms` phai la khoa cau CO THAT (co file `js/quiz/<khoa>.js`) — sai mot chu
       la day noi sang Dau Truong dut IM LANG.
     · `img` la `null` hoac URL https; ⛔ dung doan duong dan anh NASA theo mau —
       da do: `~large` KHONG ton tai voi moi anh.
     · ⛔ dung viet "doc xong nhan Thien thach tim" — doc bai KHONG con thuong tu
       30/07/2026 (`Wallet.MaxPerLesson = 0`).
*/
window.AstroQArticles = (function () {
  "use strict";

  var IDX = [
    { ord: 1010, id: "art-moons-891-and-counting", src: "NASA", cat: "astronomy", em: "🌙", c: ["#e8eefc", "#9aa8c8", "#2a3350"], img: null, title: {"vi": "Hệ Mặt Trời có bao nhiêu mặt trăng? Nhiều hơn bạn đoán", "en": "How many moons does the Solar System have? More than you'd guess"} },
    { ord: 1020, id: "art-ganymede-biggest-moon", src: "NASA", cat: "astronomy", em: "🌑", c: ["#e4ecf6", "#7d90ae", "#1e2738"], img: null, title: {"vi": "Vệ tinh lớn nhất Hệ Mặt Trời còn to hơn một hành tinh", "en": "The Solar System's biggest moon is larger than a planet"} },
    { ord: 1030, id: "art-asteroid-belt-leftovers", src: "NASA", cat: "astronomy", em: "🪨", c: ["#e0d6c8", "#8a7a66", "#2e2620"], img: null, title: {"vi": "Vành đai tiểu hành tinh: đống vật liệu chưa bao giờ thành hành tinh", "en": "The asteroid belt: building material that never became a planet"} },
    { ord: 1040, id: "art-meteoroid-meteor-meteorite", src: "NASA", cat: "astronomy", em: "🌠", c: ["#ffe6a8", "#ff9a3c", "#5e2a10"], img: null, title: {"vi": "Ba cái tên cho cùng một hòn đá", "en": "Three names for the very same rock"} },
    { ord: 1050, id: "art-comet-tail-points-away", src: "NASA", cat: "astronomy", em: "☄️", c: ["#d8f4ff", "#4fb8e8", "#123a5e"], img: null, title: {"vi": "Vì sao đuôi sao chổi không bao giờ kéo lê phía sau", "en": "Why a comet's tail never trails behind it"} },
    { ord: 1060, id: "art-dwarf-planet-third-rule", src: "NASA", cat: "astronomy", em: "🧊", c: ["#d6f0ff", "#6fa8d0", "#1c3a52"], img: null, title: {"vi": "Sao Diêm Vương trượt ở điều luật thứ ba", "en": "Pluto failed the third rule"} },
    { ord: 1070, id: "art-gravity-pulls-to-center", src: "NASA", cat: "astronomy", em: "🍎", c: ["#b9e4ff", "#3d7fd0", "#0e2044"], img: null, title: {"vi": "Trọng lực không kéo bạn xuống — nó kéo bạn vào tâm", "en": "Gravity does not pull you down — it pulls you inward"} },
    { ord: 1080, id: "art-atmosphere-shield", src: "NASA", cat: "astronomy", em: "🌍", c: ["#8ee0ff", "#2f6fd0", "#0e2a5e"], img: null, title: {"vi": "Lá chắn khí quyển của Trái Đất", "en": "Earth's atmospheric shield"} },
    { ord: 1090, id: "art-light-and-shadow-space", src: "NASA", cat: "astronomy", em: "🌌", c: ["#4a0e17", "#003049", "#fdf0d5"], img: null, title: {"vi": "Ánh sáng và bóng tối — hai thứ vũ trụ dạy ta", "en": "Light and shadow — two lessons from space"} },
    { ord: 1100, id: "art-solar-eclipse-dance", src: "NASA", cat: "astronomy", em: "☀️", c: ["#ff9f1c", "#ffbf69", "#2ec4b6"], img: null, title: {"vi": "Điệu nhảy bóng tối của nhật thực", "en": "The shadow dance of a solar eclipse"} },
    { ord: 1110, id: "art-blood-moon-lunar-eclipse", src: "NASA", cat: "astronomy", em: "🌕", c: ["#e63946", "#f1faee", "#1d3557"], img: null, title: {"vi": "Vì sao Mặt Trăng hoá đỏ trong nguyệt thực", "en": "Why the Moon turns red in an eclipse"} },
    { ord: 1120, id: "art-star-colors-temperature", src: "NASA", cat: "astronomy", em: "⭐", c: ["#ffd166", "#f77f00", "#d62828"], img: null, title: {"vi": "Cầu vồng nhiệt độ của các vì sao", "en": "The temperature rainbow of the stars"} },
    { ord: 1130, id: "lib-nebula", src: "NASA", cat: "astronomy", em: "🌌", c: ["#8ee0ff", "#2f6fd0", "#0e2a5e"], img: "https://images-assets.nasa.gov/image/PIA25433/PIA25433~large.jpg", title: {"vi": "Tinh vân Đại Bàng — vườn ươm của các ngôi sao", "en": "The Eagle Nebula — a nursery of stars"} },
    { ord: 1140, id: "art-supernova-recycles-stars", src: "NASA", cat: "astronomy", em: "💥", c: ["#fff0c0", "#ff7a4d", "#5e1a2e"], img: null, title: {"vi": "Khi một ngôi sao nổ, vật chất của nó được dùng lại", "en": "When a star explodes, its material gets used again"} },
    { ord: 1150, id: "lib-saturn", src: "NASA", cat: "astronomy", em: "🪐", c: ["#ffe6b0", "#d9a441", "#5e3f14"], img: "https://images-assets.nasa.gov/image/PIA22766/PIA22766~orig.jpg", title: {"vi": "Tàu Cassini và vành đai Sao Thổ", "en": "Cassini and Saturn's rings"} },
    { ord: 1160, id: "lib-mars", src: "NASA", cat: "robot", em: "🔴", c: ["#ffcaa8", "#d1642f", "#5e2410"], img: "https://images-assets.nasa.gov/image/PIA21496/PIA21496~medium.jpg", title: {"vi": "Robot Perseverance khám phá Sao Hỏa", "en": "Perseverance rover exploring Mars"} },
    { ord: 1170, id: "lib-andromeda", src: "NASA", cat: "astronomy", em: "🌀", c: ["#c6d8ff", "#5a78c8", "#20305e"], img: "https://images-assets.nasa.gov/image/PIA04921/PIA04921~large.jpg", title: {"vi": "Thiên hà Tiên Nữ — người hàng xóm khổng lồ", "en": "The Andromeda Galaxy — our giant neighbour"} },
    { ord: 1180, id: "jwst", src: "NASA", cat: "astronomy", em: "🔭", c: ["#8ee0ff", "#2f8fd6", "#0e2a5e"], img: null, title: {"vi": "Kính thiên văn James Webb hé lộ những thiên hà cổ đại", "en": "James Webb Telescope reveals ancient galaxies"} },
    { ord: 1190, id: "lib-gaia", src: "ESA", cat: "astronomy", em: "🛰️", c: ["#b6f5cf", "#3fd6a0", "#12503a"], img: null, title: {"vi": "Tàu Gaia của ESA vẽ bản đồ 3D Ngân Hà", "en": "ESA's Gaia maps the Milky Way in 3D"} },
    { ord: 1200, id: "art-oldest-light-we-can-see", src: "NASA", cat: "astronomy", em: "📻", c: ["#ffd9e8", "#c25a94", "#2e1030"], img: null, title: {"vi": "Thứ ánh sáng cổ nhất mà chúng ta còn nhìn thấy được", "en": "The oldest light we can still see"} },
    { ord: 2010, id: "art-autonomous-vs-remote", src: "NASA", cat: "robot", em: "🎛️", c: ["#d8e8ff", "#5a80c0", "#16233f"], img: null, title: {"vi": "Hai kiểu điều khiển robot: tự chủ và từ xa", "en": "Two ways to run a robot: autonomous and remote"} },
    { ord: 2020, id: "art-sojourner-first-rover", src: "NASA", cat: "robot", em: "🛞", c: ["#ffe4c4", "#c98a4a", "#3a2410"], img: null, title: {"vi": "Sojourner: bộ bánh xe đầu tiên lăn trên một hành tinh khác", "en": "Sojourner: the first wheels to roll on another planet"} },
    { ord: 2030, id: "art-rover-drives-itself-mars", src: "NASA", cat: "robot", em: "🤖", c: ["#ffe0c2", "#c8562a", "#3a1508"], img: null, title: {"vi": "Chiếc xe tự lái xa nhà nhất: rover trên Sao Hỏa", "en": "The most distant self-driving car: a rover on Mars"} },
    { ord: 2040, id: "art-canadarm2-robot-arm", src: "NASA", cat: "robot", em: "🦾", c: ["#dfe8ff", "#6b86c8", "#1c2748"], img: null, title: {"vi": "Cánh tay robot biết tự bò quanh trạm vũ trụ", "en": "The robot arm that crawls around the space station"} },
    { ord: 2050, id: "art-astrobee-flying-robots", src: "NASA", cat: "robot", em: "🐝", c: ["#fff0c0", "#e0b040", "#3a2a08"], img: null, title: {"vi": "Ba con robot bay lượn bên trong trạm vũ trụ", "en": "Three robots that fly around inside the space station"} },
    { ord: 2060, id: "art-robots-buy-crew-time", src: "NASA", cat: "robot", em: "⏳", c: ["#d8e8ff", "#5a80c0", "#16233f"], img: null, title: {"vi": "Robot trên trạm vũ trụ không để làm hộ — mà để mua lại thời gian", "en": "Robots on the station are not there to replace anyone — they buy back time"} },
    { ord: 2070, id: "art-robonaut-first-humanoid", src: "NASA", cat: "robot", em: "🧤", c: ["#e6e0ff", "#8878c8", "#241c48"], img: null, title: {"vi": "Robot hình người đầu tiên bay vào không gian", "en": "The first humanoid robot in space"} },
    { ord: 2080, id: "art-ingenuity-first-flight-mars", src: "NASA", cat: "robot", em: "🚁", c: ["#ffe8c8", "#d98a3c", "#402008"], img: null, title: {"vi": "Chiếc máy bay đầu tiên cất cánh ở một hành tinh khác", "en": "The first aircraft ever to fly on another planet"} },
    { ord: 2090, id: "art-opportunity-distance-record", src: "NASA", cat: "robot", em: "🏁", c: ["#ffd9b0", "#c96a2e", "#3a1a08"], img: null, title: {"vi": "Kỷ lục lái xe ngoài Trái Đất: 45 ki-lô-mét trên Sao Hoả", "en": "The off-Earth driving record: 45 kilometres across Mars"} },
    { ord: 2100, id: "art-curiosity-lab-on-wheels", src: "NASA", cat: "robot", em: "🔬", c: ["#ffe8b8", "#d08a3a", "#3a2208"], img: null, title: {"vi": "Curiosity: cả một phòng thí nghiệm đặt trên sáu bánh xe", "en": "Curiosity: an entire laboratory on six wheels"} },
    { ord: 3010, id: "art-what-is-ai-nasa", src: "NASA", cat: "ai", em: "🧩", c: ["#e8d4ff", "#8a5ad0", "#241246"], img: null, title: {"vi": "AI là gì? Câu trả lời của chính NASA", "en": "What is AI? NASA's own answer"} },
    { ord: 3020, id: "art-ai-already-around-you", src: "AI & Tech", cat: "ai", em: "📱", c: ["#e0f0ff", "#4a90d0", "#12294a"], img: null, title: {"vi": "AI đã ở quanh bạn từ trước khi bạn nghe tới từ đó", "en": "AI was around you before you ever heard the word"} },
    { ord: 3030, id: "art-ai-maps-dark-craters", src: "NASA", cat: "ai", em: "🗺️", c: ["#dfe8ff", "#6b86c8", "#1c2748"], img: null, title: {"vi": "AI dựng bản đồ những cái hố không có ánh sáng", "en": "AI maps craters that never see light"} },
    { ord: 3040, id: "art-ai-counts-storm-damage", src: "NASA", cat: "ai", em: "🏘️", c: ["#ffe8c8", "#d98a3c", "#402008"], img: null, title: {"vi": "Sau một cơn bão, AI đếm những tấm bạt trên mái nhà", "en": "After a storm, AI counts tarps on roofs"} },
    { ord: 3050, id: "art-ai-found-binary-stars", src: "NASA", cat: "ai", em: "👥", c: ["#ffe0f0", "#c05a98", "#2e1030"], img: null, title: {"vi": "AI cộng với người thường: hơn 10.000 cặp sao đôi", "en": "AI plus ordinary people: over 10,000 binary star pairs"} },
    { ord: 3060, id: "art-ai-finds-asteroids-hubble", src: "NASA", cat: "ai", em: "🧠", c: ["#f0d4ff", "#7a4fd0", "#241246"], img: null, title: {"vi": "AI đi tìm tiểu hành tinh trong kho ảnh cũ của Hubble", "en": "AI hunting asteroids in Hubble's old picture archive"} },
    { ord: 3070, id: "art-ai-tags-nasa-data", src: "NASA", cat: "ai", em: "🔎", c: ["#d4f0e8", "#4aa890", "#123a30"], img: null, title: {"vi": "Tìm một tập dữ liệu trong kho của NASA: việc AI đang giúp", "en": "Finding one dataset in NASA's archive: a job AI now helps with"} },
    { ord: 3080, id: "art-ai-predicts-solar-flares", src: "NASA", cat: "ai", em: "🌞", c: ["#fff0c8", "#e8a030", "#4a2a08"], img: null, title: {"vi": "AI học chín năm nhìn Mặt Trời để đoán trước cơn bão", "en": "AI that watched the Sun for nine years to see storms coming"} },
    { ord: 3090, id: "art-algorithmic-bias", src: "AI & Tech", cat: "ai", em: "⚠️", c: ["#ffd9d9", "#c05a5a", "#301010"], img: null, title: {"vi": "Máy không cố ý thiên vị — nó học đúng thứ được cho xem", "en": "A machine is not unfair on purpose — it learns exactly what it was shown"} },
    { ord: 3100, id: "art-algorithms-are-opinions", src: "AI & Tech", cat: "ai", em: "⚖️", c: ["#ffe0f0", "#c05a98", "#2e1030"], img: null, title: {"vi": "Một thuật toán cũng là một ý kiến", "en": "An algorithm is an opinion too"} },
    { ord: 3110, id: "lib-exoplanet", src: "AI & Tech", cat: "ai", em: "🪐", c: ["#e6c6ff", "#a06be0", "#3a1f6e"], img: "https://images-assets.nasa.gov/image/PIA22082/PIA22082~orig.jpg", title: {"vi": "AI giúp tìm hành tinh ngoài Hệ Mặt Trời", "en": "AI helps find planets beyond the Solar System"} },
    { ord: 4002, id: "art-code-written-before-launch", src: "NASA", cat: "it", em: "📜", c: ["#8ee0ff", "#3f7fd6", "#0d1f4a"], img: null, title: {"vi": "Không ai cầm tay lái khi tàu hạ cánh xuống Sao Hoả", "en": "Nobody is at the wheel when a spacecraft lands on Mars"} },
    { ord: 4006, id: "art-loop-you-can-see-on-mars", src: "NASA", cat: "it", em: "🔁", c: ["#ffd08a", "#d1762f", "#3a1c0c"], img: null, title: {"vi": "Vết bánh xe trên Sao Hoả có hoa văn, và đó là dấu của một vòng lặp", "en": "The rover's tracks on Mars have a pattern — and it is the mark of a loop"} },
    { ord: 4010, id: "art-how-data-gets-home", src: "NASA", cat: "it", em: "📡", c: ["#d4f0e8", "#4aa890", "#123a30"], img: null, title: {"vi": "Ảnh từ Sao Hoả về tới màn hình bạn bằng cách nào?", "en": "How does a picture from Mars reach your screen?"} },
    { ord: 4020, id: "art-three-stations-120-degrees", src: "NASA", cat: "it", em: "🌐", c: ["#dfe8ff", "#6b86c8", "#1c2748"], img: null, title: {"vi": "Vì sao phải có đúng ba trạm, cách nhau 120 độ", "en": "Why there must be three stations, 120 degrees apart"} },
    { ord: 4030, id: "art-voyager-signal-20-billion", src: "NASA", cat: "it", em: "⌚", c: ["#e8e0ff", "#8878c8", "#241c48"], img: null, title: {"vi": "Tín hiệu của Voyager yếu hơn 20 tỷ lần một cái đồng hồ điện tử", "en": "Voyager's signal is 20 billion times weaker than a digital watch"} },
    { ord: 4040, id: "art-supercomputer-climate", src: "NASA", cat: "it", em: "🖥️", c: ["#ffe6b0", "#d9a441", "#5e3f14"], img: null, title: {"vi": "Một phép mô phỏng chạy gần một năm liền", "en": "One simulation that ran for nearly a year"} },
    { ord: 4050, id: "art-supercomputer-galaxy-vr", src: "NASA", cat: "it", em: "🕹️", c: ["#e6c6ff", "#8a5ad8", "#2a1550"], img: null, title: {"vi": "Bay qua trung tâm thiên hà bằng thực tế ảo", "en": "Flying through the galaxy's centre in virtual reality"} },
    { ord: 5010, id: "lib-qubit", src: "NASA", cat: "quantum", em: "⚛️", c: ["#c6ffe6", "#4ade80", "#155e40"], img: null, title: {"vi": "Qubit là gì, và vì sao đừng nói nó 'vừa 0 vừa 1'", "en": "What a qubit is — and why not to say it's 'both 0 and 1'"} },
    { ord: 5020, id: "art-quantum-many-states-at-once", src: "NASA", cat: "quantum", em: "🎲", c: ["#d8ffe8", "#3fc888", "#0e4030"], img: null, title: {"vi": "Chồng chập: khi một hạt ở nhiều trạng thái cùng lúc", "en": "Superposition: when one particle is in many states at once"} },
    { ord: 5030, id: "lib-blackhole", src: "NASA", cat: "quantum", em: "🕳️", c: ["#ffe1a8", "#f2a53c", "#3a2410"], img: "https://images-assets.nasa.gov/image/PIA23122/PIA23122~medium.jpg", title: {"vi": "Hố đen khổng lồ ở thiên hà M87", "en": "The giant black hole in galaxy M87"} },
    { ord: 6010, id: "art-body-in-space-changes", src: "NASA", cat: "life", em: "🧑‍🚀", c: ["#7ee07a", "#3f9e5c", "#0d2c22"], img: null, title: {"vi": "Cơ thể bạn sẽ đổi khác nếu sống trên trạm vũ trụ", "en": "Your body changes if you live on a space station"} },
    { ord: 6020, id: "art-microgravity-is-falling", src: "NASA", cat: "life", em: "🪶", c: ["#9ff0c8", "#33a07a", "#0c2a26"], img: null, title: {"vi": "Phi hành gia không hề hết trọng lực — họ đang rơi", "en": "Astronauts are not out of gravity — they are falling"} },
    { ord: 6030, id: "art-what-life-needs", src: "NASA", cat: "life", em: "💧", c: ["#8ee0ff", "#3aa07c", "#0b2a2c"], img: null, title: {"vi": "Sự sống cần gì? Danh sách ngắn hơn bạn nghĩ", "en": "What does life need? A shorter list than you would think"} },
    { ord: 6040, id: "art-growing-plants-in-space", src: "NASA", cat: "life", em: "🌱", c: ["#a8f07a", "#4aa03c", "#132a10"], img: null, title: {"vi": "Trồng rau trên trạm vũ trụ khó ở chỗ tưới nước", "en": "The hard part of gardening in space is watering"} },
    { ord: 6050, id: "art-space-biology-questions", src: "NASA", cat: "life", em: "🔬", c: ["#c9f07a", "#5aa03c", "#1a2a0e"], img: null, title: {"vi": "Những câu hỏi mà ngành sinh học không gian chưa trả lời xong", "en": "The questions space biology has not finished answering"} },
    { ord: 7010, id: "art-units-lost-a-spacecraft", src: "NASA", cat: "math", em: "📏", c: ["#ffcf6b", "#d1892f", "#3a2a0c"], img: null, title: {"vi": "Một con tàu mất vì hai bên dùng hai đơn vị khác nhau", "en": "A spacecraft was lost because two sides used different units"} },
    { ord: 7020, id: "art-light-year-is-a-distance", src: "NASA", cat: "math", em: "📐", c: ["#ffe08a", "#d1a02f", "#3a2f0c"], img: null, title: {"vi": "Năm ánh sáng là một khoảng cách, không phải một khoảng thời gian", "en": "A light-year is a distance, not a length of time"} },
    { ord: 7030, id: "art-measuring-stars-with-angles", src: "NASA", cat: "math", em: "📡", c: ["#ffd9a0", "#c98a3a", "#33240c"], img: null, title: {"vi": "Đo khoảng cách tới một ngôi sao mà không cần tới gần nó", "en": "Measuring the distance to a star without going near it"} },
    { ord: 7040, id: "art-orbit-is-a-balance", src: "NASA", cat: "math", em: "🛰️", c: ["#ffe3a8", "#c9922f", "#332608"], img: null, title: {"vi": "Quỹ đạo không phải hình tròn, và nó là một thế cân bằng", "en": "An orbit is not a circle, and it is a balance"} }
  ];

  /* Bai cu ↔ bai da gop. Chi dung de DOC LAI lich su; bai moi khong them vao day. */
  var OLD_ID = { "gaia": "lib-gaia", "eht": "lib-blackhole", "exo-ai": "lib-exoplanet" };

  /* ───────── Trang thai da doc — DUNG CHUNG cho ca hai trang ─────────
     ⚠️ Ba ham nay tung duoc chep y het o `learn.html` va `library.html`. Chung phai
        giong nhau tung chu, khong thi loi "doc o trang nay, trang kia bao chua doc"
        quay lai — nen chung thuoc ve day, khong thuoc ve tung trang. */
  var READ_KEY = "astroq-read";

  function readSet() {
    try { return JSON.parse(localStorage.getItem(READ_KEY) || "[]"); } catch (e) { return []; }
  }
  function isRead(id) {
    var s = readSet();
    if (s.indexOf(id) >= 0) return true;
    for (var k in OLD_ID) if (OLD_ID[k] === id && s.indexOf(k) >= 0) return true;
    return false;
  }
  function markRead(id) {
    var s = readSet();
    if (s.indexOf(id) < 0) {
      s.push(id);
      try { localStorage.setItem(READ_KEY, JSON.stringify(s)); } catch (e) {}
    }
  }

  /* ───────── Chon bai noi bat — DUNG CHUNG ─────────
     Uu tien bai CHUA DOC (giu thu tu khai bao), thieu thi lay them bai da doc cho du n
     — nen con so n khong bao gio hut ke ca khi tre da doc het.
     ⚠️ Cho goi phai tinh MOT LAN luc mo trang. Tinh lai sau moi lan danh dau da doc thi
        bai vua doc bien khoi khoi noi bat ngay duoi tay tre va ca khoi nhay cho. */
  function featured(n) {
    var unread = [], seen = [];
    for (var i = 0; i < IDX.length; i++) {
      (isRead(IDX[i].id) ? seen : unread).push(IDX[i]);
    }
    return unread.concat(seen).slice(0, Math.min(n, IDX.length));
  }

  function byId(id) {
    for (var i = 0; i < IDX.length; i++) if (IDX[i].id === id) return IDX[i];
    return null;
  }

  /* ───────── Bo nap than bai ─────────
     ⚠️ MOT FILE HONG KHONG DUOC GIET CA TRANG: `import()` co `.catch` rieng tung
        file, bai hong tra `null`. Cho goi phai chiu duoc `null` — tha khong mo duoc
        MOT bai con hon mot trang trang. Cung luat da dung cho `js/quiz/`. */
  var CACHE = {}, ALL_P = null;

  /* ⚠️⚠️ `file://` CHAN `import()` MODULE — va do la mot LY DO KHAC HAN "mat mang".
     Do duoc 09/08/2026 tren Chromium: mo library.html tu dia thi muc luc nap binh
     thuong (no la script CO DIEN) nhung moi lan `import()` file bai deu bi tu choi:
       Access to script at 'file:///.../js/article/jwst.js' from origin 'null'
       has been blocked by CORS policy
     Neu de trang noi "kiem tra ket noi" thi no NOI SAI NGUYEN NHAN: mang khong lien
     quan gi, va nguoi doc se di sua dung thu khong hong. Nen bo nap phai noi ra
     duoc su khac biet, va trang chon cau theo do.
     ⚠️ Day la HE QUA cua viec chia kho (09/08/2026): truoc do ca kho nam trong mot
        script co dien nen xem bang file:// van doc duoc bai. Tu nay library.html va
        learn.html vao cung nhom voi quiz/codex/explorer/dashboard — deu can may chu.
        Nguoi dung THAT khong bi anh huong: GitHub Pages phuc vu qua https. */
  function needsServer() {
    try { return location.protocol === "file:"; } catch (e) { return false; }
  }

  /* ⚠️ CHOT DUONG DAN BANG `currentScript`, KHONG viet "./article/". Do duoc: trong
     Chromium thi `import()` o mot script CO DIEN giai theo URL CUA SCRIPT, nen
     "./article/x.js" ra dung /js/article/x.js. NHUNG du an da tra gia mot lan vi dung
     lop loi nay — `import("./api.js")` o `js/index.js` (07/08/2026): tu /en/ no thanh
     /en/api.js va form waitlist chet cam. Suy tu URL cua chinh file nay thi dung o moi
     noi dat trang, khong phu thuoc trang nam o thu muc nao. */
  var SELF = (document.currentScript && document.currentScript.src) || "";
  var ART_DIR = SELF ? SELF.replace(/[^/]*$/, "") + "article/" : "js/article/";

  function load(id) {
    if (CACHE[id]) return Promise.resolve(CACHE[id]);
    if (!byId(id)) return Promise.resolve(null);
    return import(ART_DIR + id + ".js")
      .then(function (m) { CACHE[id] = m["default"]; return CACHE[id]; })
      .catch(function (e) {
        if (window.console) console.warn("[articles] khong tai duoc bai " + id, e);
        return null;
      });
  }

  /* Tai HET than bai — chi dung cho TIM KIEM TOAN VAN, va chi goi khi tre bat dau
     tim. Nho vay duong tai luc MO TRANG khong he chua thu nay. Ket qua nho lai. */
  function loadAll() {
    if (!ALL_P) {
      ALL_P = Promise.all(IDX.map(function (e) { return load(e.id); }))
        .then(function (a) { return a.filter(Boolean); });
    }
    return ALL_P;
  }

  /* Than bai da nam trong bo nho chua? Cho tim kiem doc ma KHONG phai cho mang. */
  function loaded(id) { return CACHE[id] || null; }

  window.AstroQArticles = {
    all: function () { return IDX.slice(); },
    featured: featured,
    byId: byId,
    load: load,
    loadAll: loadAll,
    loaded: loaded,
    needsServer: needsServer,
    readSet: readSet,
    isRead: isRead,
    markRead: markRead,
    READ_KEY: READ_KEY
  };
  return window.AstroQArticles;
})();
