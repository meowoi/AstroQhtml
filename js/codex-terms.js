/* ============================================================
   codex-terms.js — SỔ TAY THUẬT NGỮ: nội dung song ngữ. CHỖ DUY NHẤT khai báo.

   Port từ `../react/astronaut-codex/termsData.ts` sang vanilla ngày 30/07/2026.
   Lý do port thay vì dựng toolchain: repo này là web tĩnh, không build step
   (CLAUDE.md mục 1), và React + ReactDOM ~140 KB gzip đi ngược đúng cái đánh đổi
   mà dự án đã trả giá để có (font 621→101 KB, ảnh 72 MB→2,79 MB, cố ý không nạp
   SDK Firebase 233 KB ở trang cần mượt).

   PHÂN CÔNG (giống js/badges.js và js/specimens.js):
     · SERVER giữ **trạng thái**: `PROGRESS.terms` là tập khoá thuật ngữ mà trẻ đã
       TRẢ LỜI ĐÚNG trong Quiz. Client không tự quyết thuật ngữ nào đã giải mã.
     · FILE NÀY chỉ giữ phần **hiển thị**: tên, ví von, định nghĩa, ví dụ đời
       thường, nhãn sơ đồ, icon, nguồn.

   ⚠️ `q` LÀ DÂY NỐI THẬT với `js/quiz-questions.js`. Mỗi phần tử phải là một khoá
      `term` CÓ THẬT trong ngân hàng câu hỏi; sai một chữ thì thuật ngữ đó **khoá
      vĩnh viễn** mà không ai thấy lỗi. Phép kiểm `check_pages.py` mục [12] đối
      chiếu hai bên.

   ⚠️ `q: []` NGHĨA LÀ "CHƯA CÓ CÂU HỎI NÀO", KHÔNG PHẢI "khoá mãi mãi". Giao diện
      có trạng thái thứ ba `soon` cho trường hợp đó: nói thật là "sắp có" và KHÔNG
      dẫn sang Quiz — đúng bài học ở js/specimens.js ("đừng viết 'Mở khoá tại
      Mission 02', nhiệm vụ ĐÓ chưa tồn tại").
      ✅ Từ 30/07/2026 **CẢ 15 THUẬT NGỮ ĐỀU CÓ CÂU HỎI** (thêm 10 câu cho lỗ đen ·
      hấp dẫn · tinh vân · siêu tân tinh · bức xạ nền), nên hiện không thuật ngữ nào
      ở trạng thái `soon`. Nhánh đó vẫn phải giữ: thuật ngữ thêm sau sẽ lại rơi vào
      đó cho tới khi có câu hỏi.

   ⚠️ SỐ LIỆU DẪN NGUYÊN VĂN TỪ NASA, 12 URL đã kiểm trả 200 ngày 30/07/2026.
      Sửa con số mà không mở lại nguồn là bịa. Cách diễn đạt cho trẻ thì **chưa
      qua rà soát chuyên môn** — cần giáo viên đọc lại trước khi phát hành, cùng
      ghi chú như learningdata/ và js/specimens.js.

   ⚠️ 4 thuật ngữ AI/Lượng tử của bản React CỐ Ý CHƯA PORT: chúng là bản nháp
      `reviewed:false`, không có nguồn. Thêm vào đây là phát hành nội dung chưa
      đối chiếu. Bổ sung nguồn xong thì thêm với `cat:"ai"`/`"quantum"`.

     <script src="js/codex-terms.js"></script>
     AstroQCodex.all()                  → mảng thuật ngữ theo thứ tự hiển thị
     AstroQCodex.text("term_comet","vi") → { t, an, sum, def, gr, dg }
     AstroQCodex.isDecoded(term, done)  → đã giải mã chưa (done = Set khoá bank)
   ============================================================ */
(function (global) {
  "use strict";

  /* Nguồn — khai một chỗ để nhiều thuật ngữ dùng chung, và để đổi URL chỉ sửa
     một dòng. `sci` = science.nasa.gov · `sp` = spaceplace.nasa.gov (trang NASA
     viết CHO TRẺ EM, đúng độ tuổi 8–15; science.nasa.gov không có trang định
     nghĩa lực hấp dẫn tương đương). */
  var SRC = {
    stars:    { label: "NASA Science — Stars",            url: "https://science.nasa.gov/universe/stars/" },
    planets:  { label: "NASA Science — About the Planets", url: "https://science.nasa.gov/solar-system/planets/" },
    dwarf:    { label: "NASA Science — Dwarf Planets",    url: "https://science.nasa.gov/dwarf-planets/" },
    moons:    { label: "NASA Science — Moons",            url: "https://science.nasa.gov/solar-system/moons/" },
    ganymede: { label: "NASA Science — Ganymede",         url: "https://science.nasa.gov/jupiter/moons/ganymede/" },
    asteroid: { label: "NASA Science — Asteroid Facts",   url: "https://science.nasa.gov/solar-system/asteroids/facts/" },
    comet:    { label: "NASA Science — Comet Facts",      url: "https://science.nasa.gov/solar-system/comets/facts/" },
    meteor:   { label: "NASA Science — Meteors & Meteorites", url: "https://science.nasa.gov/solar-system/meteors-meteorites/facts/" },
    exo:      { label: "NASA Science — Exoplanets",       url: "https://science.nasa.gov/exoplanets/" },
    bh:       { label: "NASA Science — Black Holes",      url: "https://science.nasa.gov/universe/black-holes/" },
    gravity:  { label: "NASA Space Place — What Is Gravity?", url: "https://spaceplace.nasa.gov/what-is-gravity/en/" },
    cosmos:   { label: "NASA Science — Cosmic History",   url: "https://science.nasa.gov/universe/overview/" }
  };

  /* t = tên · an = tên ví von · sum = một dòng cho thẻ · def = định nghĩa
     gr = ví dụ đời thường · dg = 3 nhãn quanh sơ đồ
     ic = khoá icon trong js/icons.js · q = khoá `term` trong js/quiz-questions.js
     src = mảng nguồn (mảng vì một định nghĩa có thể dẫn từ hai trang) */
  var T = [
    {
      id: "term_star", cat: "space", ic: "cx-star", q: ["star", "star-fusion"],
      src: [SRC.stars],
      vi: { t: "Ngôi sao", an: "Lò phản ứng khổng lồ trên trời",
            sum: "Quả cầu khí nóng tự phát sáng — Mặt Trời là một ngôi sao.",
            def: "Ngôi sao là quả cầu khí nóng khổng lồ, phần lớn là hydro kèm một ít heli. Áp suất và nhiệt độ trong lõi ép các hạt nhân hydro lại thành heli — gọi là phản ứng nhiệt hạch. Chính năng lượng đó làm ngôi sao phát sáng và giữ nó không sụp xuống dưới sức nặng của chính mình.",
            gr: "Hãy tưởng tượng một quả bóng bay khổng lồ chứa đầy khí, to đến mức lực hút của chính nó bóp phần giữa lại thật chặt. Bóp càng chặt thì giữa càng nóng — nóng tới mức phát sáng. Mặt Trời chính là quả bóng đó.",
            dg: ["Lõi: hydro → heli", "Lớp khí: chủ yếu hydro", "Tự phát ra ánh sáng"] },
      en: { t: "Star", an: "A giant reactor in the sky",
            sum: "A ball of hot gas that shines by itself — the Sun is a star.",
            def: "A star is a giant ball of hot gas, mostly hydrogen with some helium. Crushing pressure and heat in the core fuse hydrogen nuclei into helium — nuclear fusion. That energy is what makes a star shine, and what stops it collapsing under its own weight.",
            gr: "Picture a huge balloon full of gas, so big that its own pull squeezes the middle very hard. The harder it squeezes, the hotter the middle gets — hot enough to glow. Our Sun is that balloon.",
            dg: ["Core: hydrogen → helium", "Gas layers: mostly hydrogen", "Makes its own light"] }
    },
    {
      id: "term_planet", cat: "space", ic: "cx-planet", q: ["planet", "planet-count"],
      /* 8 hành tinh: trang Planets · ba tiêu chí IAU: trang Dwarf Planets.
         ⚠️ Trang Planets KHÔNG liệt kê ba tiêu chí đó — ghi một nguồn là dẫn nguồn
            cho một câu mình không đọc ở đó. Vì thế `src` là MẢNG. */
      src: [SRC.planets, SRC.dwarf],
      vi: { t: "Hành tinh", an: "Người dọn sân chuyên nghiệp",
            sum: "Quay quanh Mặt Trời, gần tròn, và đã dọn sạch vùng quỹ đạo.",
            def: "Theo Liên đoàn Thiên văn Quốc tế (IAU, 2006), một hành tinh phải làm được ba việc: quay quanh ngôi sao của nó, đủ nặng để lực hấp dẫn của chính nó bóp nó thành hình gần tròn, và dọn sạch các vật thể cùng cỡ quanh quỹ đạo. Hệ Mặt Trời có 8 hành tinh: Sao Thuỷ, Sao Kim, Trái Đất, Sao Hoả, Sao Mộc, Sao Thổ, Sao Thiên Vương, Sao Hải Vương.",
            gr: "Giống một bạn được giao dọn hẳn một khu sân: bạn ấy đủ lớn để tự dọn sạch, và sau khi dọn thì trong sân không còn hòn đá nào cùng cỡ lăn lóc. Đó là điều kiện thứ ba — cũng là điều kiện Sao Diêm Vương không đạt.",
            dg: ["① Quay quanh Mặt Trời", "② Gần tròn", "③ Dọn sạch quỹ đạo"] },
      en: { t: "Planet", an: "The professional yard-cleaner",
            sum: "Orbits the Sun, nearly round, and has cleared its orbital zone.",
            def: "The International Astronomical Union (IAU, 2006) says a planet must do three things: orbit its star, be heavy enough that its own gravity squeezes it nearly round, and clear away objects of similar size around its orbit. The Solar System has 8 planets: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus and Neptune.",
            gr: "Like a kid put in charge of a whole yard: big enough to clear it alone, and once cleared there are no similar-sized rocks left rolling about. That third rule is the one Pluto does not pass.",
            dg: ["① Orbits the Sun", "② Nearly round", "③ Orbit cleared"] }
    },
    {
      id: "term_dwarf_planet", cat: "space", ic: "cx-dwarf", q: ["dwarf", "dwarf-ceres"],
      src: [SRC.dwarf],
      vi: { t: "Hành tinh lùn", an: "Gần thành hành tinh, chỉ thiếu bước dọn sân",
            sum: "Đủ tròn, đủ quay quanh Mặt Trời — nhưng chưa dọn sạch quỹ đạo.",
            def: "Hành tinh lùn quay quanh Mặt Trời và cũng gần tròn, nhưng chưa dọn sạch vùng quỹ đạo của mình. Hệ Mặt Trời có 5 hành tinh lùn, tính từ Mặt Trời ra là Ceres, Pluto, Haumea, Makemake và Eris. Ceres là vật thể lớn nhất trong vành đai tiểu hành tinh và là hành tinh lùn duy nhất ở vùng trong hệ Mặt Trời.",
            gr: "Vẫn là bạn được giao dọn sân, nhưng sân đó đông đúc quá — dọn mãi vẫn còn đá lăn khắp nơi. Bạn ấy không làm gì sai, chỉ là khu sân quá nhiều đồ.",
            dg: ["Gần tròn ✔", "Quay quanh Mặt Trời ✔", "Dọn sạch quỹ đạo ✘"] },
      en: { t: "Dwarf Planet", an: "Almost a planet, just missing the clean-up",
            sum: "Round enough, orbits the Sun — but has not cleared its orbit.",
            def: "A dwarf planet orbits the Sun and is nearly round, but has not cleared its orbital neighbourhood. The Solar System has 5 dwarf planets, outward from the Sun: Ceres, Pluto, Haumea, Makemake and Eris. Ceres is the largest object in the asteroid belt and the only dwarf planet in the inner Solar System.",
            gr: "Still the kid cleaning the yard, but this yard is far too crowded — no matter how much they tidy, rocks keep rolling in. Nothing was done wrong; the yard just has too much stuff.",
            dg: ["Nearly round ✔", "Orbits the Sun ✔", "Orbit cleared ✘"] }
    },
    {
      id: "term_moon", cat: "space", ic: "cx-moon", q: ["moon", "moon-largest"],
      /* định nghĩa vệ tinh: trang Moons · "Ganymede lớn hơn Sao Thuỷ": trang Ganymede */
      src: [SRC.moons, SRC.ganymede],
      vi: { t: "Vệ tinh tự nhiên", an: "Bạn đồng hành quay quanh hành tinh",
            sum: "Vật thể hình thành tự nhiên, quay quanh một hành tinh.",
            def: "NASA gọi những vật thể hình thành tự nhiên và quay quanh hành tinh là mặt trăng, hay vệ tinh tự nhiên. Thứ do con người chế tạo rồi phóng lên quỹ đạo thì là vệ tinh nhân tạo — chữ “tự nhiên” chính là chỗ khác nhau. Vệ tinh lớn nhất hệ Mặt Trời là Ganymede của Sao Mộc: nó còn lớn hơn cả hành tinh Sao Thuỷ.",
            gr: "Giống em chạy vòng quanh mẹ trong công viên: mẹ đi tới đâu em cũng theo, nhưng em vẫn chạy vòng quanh mẹ. Mặt Trăng làm đúng vậy với Trái Đất.",
            dg: ["Hình thành tự nhiên", "Quay quanh một hành tinh", "Lớn nhất: Ganymede"] },
      en: { t: "Moon / Natural Satellite", an: "A companion circling a planet",
            sum: "A naturally formed object that orbits a planet.",
            def: "NASA calls naturally formed objects that orbit a planet moons, or natural satellites. Something built by people and launched into orbit is an artificial satellite — the word “natural” is the difference. The largest moon in the Solar System is Jupiter's Ganymede: it is even bigger than the planet Mercury.",
            gr: "Like running circles around your mum in the park: wherever she walks you follow, but you keep circling her. That is exactly what the Moon does with Earth.",
            dg: ["Formed naturally", "Orbits a planet", "Largest: Ganymede"] }
    },
    {
      id: "term_asteroid", cat: "space", ic: "cx-asteroid", q: ["asteroid-belt", "asteroid-what"],
      src: [SRC.asteroid],
      vi: { t: "Tiểu hành tinh", an: "Mảnh vụn còn lại từ buổi xây nhà",
            sum: "Mảnh đá còn sót từ thời hệ Mặt Trời mới hình thành.",
            def: "Tiểu hành tinh là những mảnh đá còn sót lại từ lúc hệ Mặt Trời hình thành, khoảng 4,6 tỉ năm trước. Vành đai chính nằm giữa Sao Hoả và Sao Mộc, và NASA ước tính ở đó có khoảng 1,1–1,9 triệu tiểu hành tinh lớn hơn 1 km. Điểm phân biệt quan trọng: tiểu hành tinh là ĐÁ, còn sao chổi là BĂNG.",
            gr: "Sau khi xây xong một căn nhà, quanh sân luôn còn mấy đống gạch vụn không dùng hết. Tiểu hành tinh chính là gạch vụn của công trình mang tên hệ Mặt Trời — và chúng vẫn nằm đó suốt 4,6 tỉ năm.",
            dg: ["Bằng đá, không phải băng", "Vành đai: giữa Hoả – Mộc", "1,1–1,9 triệu viên >1 km"] },
      en: { t: "Asteroid", an: "Leftover rubble from building day",
            sum: "Rocky leftovers from when the Solar System formed.",
            def: "Asteroids are rocky remnants left over from the formation of the Solar System about 4.6 billion years ago. The main belt lies between Mars and Jupiter, where NASA estimates there are roughly 1.1–1.9 million asteroids larger than 1 km. Key difference: asteroids are ROCK, comets are ICE.",
            gr: "After a house is built there are always piles of leftover bricks around the yard. Asteroids are the leftover bricks of the project called the Solar System — still sitting there after 4.6 billion years.",
            dg: ["Rock, not ice", "Belt: Mars – Jupiter", "1.1–1.9 million over 1 km"] }
    },
    {
      id: "term_comet", cat: "space", ic: "cx-comet", q: ["comet-what", "comet-tail"],
      src: [SRC.comet],
      vi: { t: "Sao chổi", an: "Quả cầu tuyết bẩn",
            sum: "Băng lẫn bụi; lại gần Mặt Trời thì mọc đuôi dài.",
            def: "NASA gọi sao chổi là “quả cầu tuyết bẩn”: phần lớn là băng bọc một lớp bụi và chất hữu cơ tối màu. Khi lại gần Mặt Trời, băng bốc hơi tạo ra lớp khí bao quanh (coma) và cái đuôi dài. Đuôi luôn bị áp lực ánh sáng cùng gió Mặt Trời thổi RA XA Mặt Trời — nên khi sao chổi bay ngược trở ra, cái đuôi lại đi trước nó.",
            gr: "Giống một cục tuyết lẫn đất em nặn rồi mang lại gần bếp lửa: nó tan, bốc hơi, và làn hơi bị gió từ bếp thổi bạt về một phía. Gió ở đây là gió Mặt Trời.",
            dg: ["Nhân: băng + bụi", "Coma: lớp khí bao quanh", "Đuôi: luôn xa Mặt Trời"] },
      en: { t: "Comet", an: "A dirty snowball",
            sum: "Ice and dust; grows a long tail near the Sun.",
            def: "NASA calls comets “dirty snowballs”: mostly ice wrapped in dark dust and organic material. Near the Sun the ice vaporises, creating a surrounding cloud of gas (the coma) and a long tail. Light pressure and the solar wind always blow the tail AWAY from the Sun — so on the way back out, the tail leads the comet.",
            gr: "Like a snowball with dirt in it brought near a fire: it melts, steams, and the steam is blown to one side. Here the wind is the solar wind.",
            dg: ["Nucleus: ice + dust", "Coma: surrounding gas", "Tail: always away from Sun"] }
    },
    {
      id: "term_meteoroid", cat: "space", ic: "cx-meteoroid", q: ["meteoroid", "meteoroid-chain"],
      src: [SRC.meteor],
      vi: { t: "Thiên thạch nhỏ", an: "Hòn đá đang đi du lịch trong không gian",
            sum: "Đá không gian, từ hạt bụi tới tiểu hành tinh nhỏ — vẫn ở ngoài kia.",
            def: "Meteoroid là “đá không gian” có kích thước từ hạt bụi cho tới một tiểu hành tinh nhỏ. Điều quan trọng nhất của định nghĩa là VỊ TRÍ: nó vẫn đang bay trong không gian, chưa chạm vào khí quyển hành tinh nào. Cả ba từ meteoroid – meteor – meteorite nói về cùng một hòn đá, chỉ khác ở chặng đường nó đang đi.",
            gr: "Giống một quả bóng đang bay giữa trời: lúc còn trên không thì gọi là “bóng đang bay”. Chưa rơi, chưa nằm đất — chỉ đang bay.",
            dg: ["Đang ở TRONG KHÔNG GIAN", "Cỡ: hạt bụi → tiểu hành tinh nhỏ", "Chặng 1 / 3"] },
      en: { t: "Meteoroid", an: "A rock on holiday in space",
            sum: "Space rock, from dust grain to small asteroid — still out there.",
            def: "A meteoroid is a “space rock” ranging from a dust grain to a small asteroid. The key part of the definition is WHERE it is: still travelling through space, not yet touching any planet's atmosphere. Meteoroid, meteor and meteorite all describe the same rock at different stages of its journey.",
            gr: "Like a ball in mid-flight: while it is up in the air we call it “a ball flying”. Not fallen, not on the ground — just flying.",
            dg: ["Still IN SPACE", "Size: dust → small asteroid", "Stage 1 of 3"] }
    },
    {
      id: "term_meteor", cat: "space", ic: "cx-meteor", q: ["meteor", "meteor-fireball"],
      src: [SRC.meteor],
      vi: { t: "Sao băng", an: "Vệt sáng vụt qua trời đêm",
            sum: "Không phải ngôi sao — là đá không gian đang cháy trong khí quyển.",
            def: "Sao băng chẳng phải ngôi sao nào cả: đó là vệt sáng sinh ra khi một meteoroid lao vào khí quyển ở tốc độ rất cao rồi cháy lên. Một sao băng sáng hơn cả Sao Kim thì được NASA gọi là quả cầu lửa (fireball) — sáng đến mức có thể thấy khi trời còn chưa tối hẳn.",
            gr: "Xoa hai bàn tay thật nhanh vào nhau, em sẽ thấy nóng lên. Đó là ma sát. Hòn đá lao vào lớp không khí dày của Trái Đất cũng bị “xoa” như vậy, nhưng nhanh gấp hàng nghìn lần — nóng tới mức phát sáng.",
            dg: ["Đang CHÁY trong khí quyển", "Sáng hơn Sao Kim = fireball", "Chặng 2 / 3"] },
      en: { t: "Meteor", an: "A streak of light across the night",
            sum: "Not a star — space rock burning up in the atmosphere.",
            def: "A meteor is not a star at all: it is the streak of light made when a meteoroid enters the atmosphere at high speed and burns up. A meteor brighter than Venus is called a fireball by NASA — bright enough to be seen before the sky is fully dark.",
            gr: "Rub your palms together fast and they warm up. That is friction. A rock hitting Earth's thick air is “rubbed” the same way, but thousands of times faster — hot enough to glow.",
            dg: ["BURNING in the atmosphere", "Brighter than Venus = fireball", "Stage 2 of 3"] }
    },
    {
      id: "term_meteorite", cat: "space", ic: "cx-meteorite", q: ["meteorite", "meteorite-survive"],
      src: [SRC.meteor],
      vi: { t: "Thiên thạch", an: "Hòn đá vũ trụ em có thể cầm lên tay",
            sum: "Sống sót qua khí quyển và chạm tới mặt đất.",
            def: "Một meteoroid sống sót qua chuyến đi xuyên khí quyển và chạm tới mặt đất thì được gọi là meteorite. Phần lớn thiên thạch tìm được chỉ to bằng viên sỏi đến nắm tay, vì thường dưới 5% khối lượng ban đầu tới được mặt đất. Mỗi ngày có khoảng 48,5 tấn vật chất thiên thạch rơi xuống Trái Đất.",
            gr: "Đây là chặng cuối của cùng một hòn đá: đã đi hết không gian, cháy sáng qua khí quyển, giờ nằm im trên mặt đất để một nhà khoa học nhặt lên. Khí quyển Trái Đất là tấm khiên rất tốt.",
            dg: ["Đã NẰM TRÊN MẶT ĐẤT", "Sống sót: thường dưới 5%", "Chặng 3 / 3"] },
      en: { t: "Meteorite", an: "A space rock you can hold in your hand",
            sum: "Survived the atmosphere and reached the ground.",
            def: "A meteoroid that survives the trip through the atmosphere and reaches the ground is called a meteorite. Most meteorites found are pebble- to fist-sized, because usually less than 5% of the original mass makes it down. About 48.5 tonnes of meteoritic material falls on Earth every day.",
            gr: "This is the last stage of the same rock: it crossed space, blazed through the atmosphere, and now lies still on the ground for a scientist to pick up. Earth's atmosphere is a very good shield.",
            dg: ["ON THE GROUND", "Survives: usually under 5%", "Stage 3 of 3"] }
    },
    {
      id: "term_exoplanet", cat: "space", ic: "cx-exoplanet", q: ["exoplanet", "exoplanet-transit"],
      src: [SRC.exo],
      vi: { t: "Ngoại hành tinh", an: "Hành tinh ở nhà người khác",
            sum: "Hành tinh nằm ngoài hệ Mặt Trời — đã xác nhận hơn 6.000.",
            def: "Ngoại hành tinh là bất kỳ hành tinh nào nằm ngoài hệ Mặt Trời của chúng ta; tiền tố “exo-” trong tiếng Hy Lạp nghĩa là “bên ngoài”. NASA đã xác nhận hơn 6.000 ngoại hành tinh. Cách tìm phổ biến là phương pháp quá cảnh: hành tinh đi ngang trước ngôi sao thì che bớt ánh sáng, làm ngôi sao mờ đi một chút, và kính thiên văn đo được độ mờ đó.",
            gr: "Ban đêm em nhìn một bóng đèn ở xa. Nếu có con muỗi bay ngang trước bóng đèn, ánh sáng sẽ tối đi một chút xíu. Em không thấy con muỗi, nhưng em BIẾT nó vừa đi qua.",
            dg: ["Ngoài hệ Mặt Trời", "Đã xác nhận: hơn 6.000", "Tìm bằng độ mờ của sao"] },
      en: { t: "Exoplanet", an: "A planet at somebody else's house",
            sum: "A planet outside our Solar System — over 6,000 confirmed.",
            def: "An exoplanet is any planet beyond our Solar System; the Greek prefix “exo-” means “outside”. NASA has confirmed more than 6,000 exoplanets. The common way to find them is the transit method: as a planet passes in front of its star it blocks a little light, dimming the star slightly, and telescopes measure that dip.",
            gr: "At night you look at a distant lamp. If a mosquito flies in front of it, the light dims a tiny bit. You never see the mosquito, but you KNOW it went past.",
            dg: ["Outside the Solar System", "Confirmed: over 6,000", "Found by star dimming"] }
    },
    {
      id: "term_black_hole", cat: "space", ic: "cx-blackhole", q: ["black-hole", "black-hole-light"],
      src: [SRC.bh],
      vi: { t: "Lỗ đen", an: "Cái giếng sâu đến mức ánh sáng cũng không leo ra được",
            sum: "Đặc đến mức ngay cả ánh sáng cũng không thoát ra nổi.",
            def: "NASA định nghĩa lỗ đen là vật thể đặc tới mức lực hấp dẫn ngay dưới bề mặt của nó — gọi là chân trời sự kiện — mạnh đến mức KHÔNG GÌ thoát ra được, kể cả ánh sáng. Chân trời sự kiện không phải một mặt đất; nó là đường biên chứa toàn bộ vật chất làm nên lỗ đen. Một loại lỗ đen sinh ra khi ngôi sao rất lớn cạn nhiên liệu rồi nổ thành siêu tân tinh. Lỗ đen nhỏ nhất từng biết nặng gấp 3,8 lần Mặt Trời; lớn nhất quan sát được là TON 618, gấp 66 tỉ lần.",
            gr: "Tưởng tượng một cái phễu rất sâu và rất trơn. Hòn bi gần miệng phễu còn leo ra được; nhưng qua một vạch nào đó thì dốc quá, leo kiểu gì cũng tuột lại. Vạch đó là chân trời sự kiện — chỉ khác là thứ không leo ra được gồm cả tia sáng.",
            dg: ["Chân trời sự kiện: đường biên", "Ánh sáng KHÔNG thoát ra", "Nhỏ nhất đã biết: 3,8 lần Mặt Trời"] },
      en: { t: "Black Hole", an: "A well so deep even light cannot climb out",
            sum: "So dense that not even light can escape.",
            def: "NASA defines a black hole as an object so dense that gravity just beneath its surface — the event horizon — is strong enough that NOTHING can escape, not even light. The event horizon is not a solid surface; it is a boundary containing all the matter that makes up the black hole. One kind is born when a very massive star runs out of fuel and explodes as a supernova. The smallest known black hole is 3.8 times the Sun's mass; the largest observed, TON 618, is 66 billion times.",
            gr: "Picture a very deep, very slippery funnel. A marble near the rim can still climb out; past a certain line it is too steep and always slides back. That line is the event horizon — except here even light cannot climb out.",
            dg: ["Event horizon: a boundary", "Light does NOT escape", "Smallest known: 3.8 solar masses"] }
    },
    {
      id: "term_gravity", cat: "space", ic: "cx-gravity", q: ["gravity", "gravity-distance"],
      src: [SRC.gravity],
      vi: { t: "Lực hấp dẫn", an: "Sợi dây vô hình mọi vật đều cầm",
            sum: "Lực kéo mọi vật về phía tâm — càng nặng, càng gần thì càng mạnh.",
            def: "NASA định nghĩa lực hấp dẫn là lực mà một hành tinh hay vật thể dùng để kéo các vật khác về phía tâm của nó. Mọi thứ CÓ KHỐI LƯỢNG đều có lực hấp dẫn, và hai điều quyết định nó mạnh hay yếu: vật càng nhiều khối lượng thì lực càng lớn, và lực yếu dần khi khoảng cách xa ra. Chính lực này giữ các hành tinh quay quanh Mặt Trời và giữ Mặt Trăng quay quanh Trái Đất; lực hấp dẫn của Mặt Trăng cũng gây ra thuỷ triều.",
            gr: "Vì sao em nhảy lên rồi lại rơi xuống sân chứ không bay mất vào không gian? Vì Trái Đất đang kéo em về phía tâm của nó. Cân nặng của em chính là số đo lực kéo đó.",
            dg: ["Càng nhiều khối lượng → càng mạnh", "Càng xa → càng yếu", "Giữ hành tinh trên quỹ đạo"] },
      en: { t: "Gravity", an: "The invisible string everything holds",
            sum: "The pull toward a body's centre — stronger with more mass, weaker with distance.",
            def: "NASA defines gravity as the force by which a planet or other body draws objects toward its centre. Everything WITH MASS has gravity, and two things set how strong it is: objects with more mass have more gravity, and gravity gets weaker with distance. This force keeps all the planets in orbit around the Sun and keeps the Moon in orbit around Earth; the Moon's gravity also causes ocean tides.",
            gr: "Why do you land back on the ground when you jump instead of floating off into space? Because Earth is pulling you toward its centre. Your weight is the measure of that pull.",
            dg: ["More mass → stronger", "Farther → weaker", "Keeps planets in orbit"] }
    },
    {
      id: "term_nebula", cat: "space", ic: "cx-nebula", q: ["nebula", "nebula-gas"],
      src: [SRC.stars],
      vi: { t: "Tinh vân", an: "Vườn trẻ của các ngôi sao",
            sum: "Đám mây khí và bụi khổng lồ — nơi các ngôi sao được sinh ra.",
            def: "Các ngôi sao hình thành trong những đám mây khí và bụi khổng lồ mà NASA gọi là mây phân tử. Khí ở đó chủ yếu là hydro, kèm một ít heli và lượng nhỏ các nguyên tố khác. Ở những chỗ mây đặc lại, lực hấp dẫn hút thêm vật chất về, phần giữa bị ép ngày càng chặt và nóng lên — đủ nóng để phản ứng nhiệt hạch khởi động, và một ngôi sao ra đời. Mây phân tử đầy các cụm sao mới sinh được gọi là “vườn trẻ của các ngôi sao”.",
            gr: "Giống sương mù dày đặc trên sân vào sáng sớm, nhưng rộng bằng cả một vùng trời và đặc hơn ở vài chỗ. Chính mấy chỗ đặc đó tự co lại rồi bật sáng thành ngôi sao — một đám mây có thể sinh rất nhiều ngôi sao cùng lúc.",
            dg: ["Mây khí + bụi (chủ yếu hydro)", "Chỗ đặc co lại vì hấp dẫn", "Nóng đủ → sao ra đời"] },
      en: { t: "Nebula", an: "A nursery for stars",
            sum: "A huge cloud of gas and dust — where stars are born.",
            def: "Stars form in large clouds of gas and dust that NASA calls molecular clouds. The gas is mostly hydrogen, with some helium and small amounts of other elements. Where the cloud grows denser, gravity attracts more matter, the middle is squeezed ever tighter and heats up — hot enough for nuclear fusion to start, and a star is born. Molecular clouds full of newly formed star clusters are called stellar nurseries.",
            gr: "Like thick fog over the yard at dawn, but as wide as a patch of sky and denser in places. Those dense patches pull themselves together and light up as stars — one cloud can make many stars at once.",
            dg: ["Gas + dust (mostly hydrogen)", "Dense parts collapse by gravity", "Hot enough → a star is born"] }
    },
    {
      id: "term_supernova", cat: "space", ic: "cx-supernova", q: ["supernova", "supernova-elements"],
      src: [SRC.stars],
      vi: { t: "Siêu tân tinh", an: "Tiếng nổ chia lại vật liệu cho cả vũ trụ",
            sum: "Vụ nổ khổng lồ khi một ngôi sao rất lớn kết thúc cuộc đời.",
            def: "Ngôi sao khối lượng lớn cuối cùng cũng cạn nhiên liệu. Khi đó lõi sắt của nó sụp xuống cho tới lúc lực giữa các hạt nhân “đạp phanh”, rồi nảy trở lại. Cú nảy đó tạo ra một sóng xung kích lan ra ngoài xuyên qua cả ngôi sao, và kết quả là vụ nổ khổng lồ gọi là siêu tân tinh. Vật chất bị bắn vào không gian sẽ làm giàu cho các mây phân tử sau này, rồi đi vào thành phần của thế hệ ngôi sao kế tiếp.",
            gr: "Giống một toà nhà bằng gạch bị sập: gạch không biến mất, nó bay ra khắp nơi và được dùng lại để xây những căn nhà mới. Nên các ngôi sao sinh sau luôn có nhiều “gạch” quý hơn các ngôi sao sinh trước.",
            dg: ["Sao lớn cạn nhiên liệu", "Lõi sụp rồi NẢY lại", "Sóng xung kích → vụ nổ"] },
      en: { t: "Supernova", an: "The blast that shares materials with the universe",
            sum: "A huge explosion when a very massive star ends its life.",
            def: "A high-mass star eventually runs out of fuel. Its iron core then collapses until forces between the nuclei push the brakes, and it rebounds. That rebound creates a shock wave travelling outward through the star, and the result is a huge explosion called a supernova. Material cast into space enriches future molecular clouds and becomes part of the next generation of stars.",
            gr: "Like a brick building collapsing: the bricks do not vanish, they scatter and get reused to build new houses. So stars born later always have more precious “bricks” than stars born earlier.",
            dg: ["Massive star runs out of fuel", "Core collapses then REBOUNDS", "Shock wave → explosion"] }
    },
    {
      id: "term_cmb", cat: "space", ic: "cx-cmb", q: ["cmb", "cmb-when"],
      src: [SRC.cosmos],
      vi: { t: "Bức xạ nền vũ trụ", an: "Bức ảnh sơ sinh của vũ trụ",
            sum: "Ánh sáng cổ nhất ta quan sát được — còn lại từ thuở vũ trụ sơ sinh.",
            def: "Khoảng 380.000 năm sau Big Bang, vũ trụ nguội đủ để các hạt nhân nguyên tử bắt được electron — giai đoạn các nhà thiên văn gọi là kỷ nguyên tái kết hợp. Ánh sáng phát ra khi đó vẫn còn đo được tới hôm nay và được gọi là bức xạ nền vũ trụ: đó là ÁNH SÁNG CỔ NHẤT mà ta quan sát được. Bản đồ của nó cho thấy những chênh lệch nhiệt độ 13,8 tỉ năm tuổi — chính là mầm mống lớn dần lên thành các thiên hà ngày nay.",
            gr: "Giống tấm ảnh chụp em lúc mới sinh: em bây giờ đã khác hẳn, nhưng tấm ảnh vẫn giữ nguyên hình dáng thuở đó. Những vệt sáng-tối lấm chấm trên ảnh chính là chỗ về sau mọc lên các thiên hà.",
            dg: ["380.000 năm sau Big Bang", "Ánh sáng CỔ NHẤT quan sát được", "Chênh lệch nhiệt độ → mầm thiên hà"] },
      en: { t: "Cosmic Microwave Background", an: "The universe's newborn photo",
            sum: "The oldest light we can observe — left from the infant universe.",
            def: "About 380,000 years after the big bang, the universe cooled enough for atomic nuclei to capture electrons — the period astronomers call the epoch of recombination. The light released then is still detectable today and is called the cosmic microwave background: it is the OLDEST LIGHT we can observe. Its map shows 13.8-billion-year-old temperature fluctuations — the very seeds that grew into the galaxies we see now.",
            gr: "Like a photo of you as a newborn: you look completely different today, but the photo still holds that moment. The light and dark speckles on this photo are exactly where galaxies later grew.",
            dg: ["380,000 years after big bang", "OLDEST light we can observe", "Temperature ripples → galaxy seeds"] }
    }
  ];

  var BY_ID = {};
  var BY_QUIZ_TERM = {};
  for (var i = 0; i < T.length; i++) {
    BY_ID[T[i].id] = T[i];
    for (var j = 0; j < T[i].q.length; j++) BY_QUIZ_TERM[T[i].q[j]] = T[i].id;
  }

  function lang2(lang) { return lang === "en" ? "en" : "vi"; }

  global.AstroQCodex = {
    /** Mảng thuật ngữ theo thứ tự hiển thị. Trả BẢN SAO nông để ngoài không sắp lại được. */
    all: function () { return T.slice(); },

    get: function (id) { return BY_ID[id] || null; },

    /** Phần chữ theo ngôn ngữ: { t, an, sum, def, gr, dg }. */
    text: function (id, lang) {
      var t = BY_ID[id];
      return t ? t[lang2(lang)] : null;
    },

    /**
     * Thuật ngữ đã giải mã chưa. `done` là Set/mảng khoá `term` mà trẻ đã trả lời
     * ĐÚNG (server trả trong `progress.terms`).
     * ⚠️ CHỖ DUY NHẤT quyết định trạng thái — mọi nơi phải gọi hàm này, đừng tự so
     *    `q[0]`, không thì thuật ngữ có 2 khoá sẽ hiện khác nhau ở hai màn.
     */
    isDecoded: function (term, done) {
      if (!term || !term.q.length || !done) return false;
      var has = done.has ? function (k) { return done.has(k); }
                         : function (k) { return done.indexOf(k) !== -1; };
      for (var k = 0; k < term.q.length; k++) if (has(term.q[k])) return true;
      return false;
    },

    /**
     * Thuật ngữ này CÓ ĐƯỜNG mở khoá chưa. `q: []` = chưa có câu hỏi nào trong
     * ngân hàng → giao diện phải nói "sắp có", KHÔNG hứa một nhiệm vụ không tồn tại.
     */
    hasPath: function (term) { return !!(term && term.q.length); },

    /** Khoá bank → id thuật ngữ. Dùng để map kết quả Quiz sang sổ tay. */
    idOfQuizTerm: function (key) { return BY_QUIZ_TERM[key] || null; },

    /** Mọi khoá bank mà sổ tay đang chờ — script kiểm thử đối chiếu với bank. */
    quizTerms: function () { return Object.keys(BY_QUIZ_TERM); },

    has: function (id) { return Object.prototype.hasOwnProperty.call(BY_ID, id); },
    ids: function () { return T.map(function (x) { return x.id; }); }
  };
})(window);
