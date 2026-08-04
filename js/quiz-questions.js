/* js/quiz-questions.js — NGÂN HÀNG CÂU HỎI của Đấu Trường Kiến Thức
   (tên khu tới 04/08/2026: "Thử Thách Quiz").
   CHỖ DUY NHẤT khai báo câu hỏi cho quiz.html (trước 30/07/2026 mảng này nằm
   inline trong quiz.html). Tách ra vì bộ câu hỏi giờ lớn hơn cả phần logic của
   trang, và để trang khác (library.html "Làm Quiz bài này", màn ôn tập sau
   nhiệm vụ) dùng lại được mà không phải chép dữ liệu.

   MỘT CÂU HỎI gồm:
     term   khoá thuật ngữ — pickRound() dùng nó để MỖI LƯỢT không hỏi trùng
            thuật ngữ. Đừng đặt trùng khoá cho hai thuật ngữ khác nhau.
     topic  nhãn hiện ở badge [ CHỦ ĐỀ · CÂU n/m ]
     q      câu hỏi · opts 4 lựa chọn · a chỉ số đáp án đúng (0..3)
     ok/no  lời giải thích khi đúng / khi sai · hint lời mascot Byte
     src    (tuỳ chọn) nguồn tham chiếu, hiện ở cuối popup giải thích.

   ⚠️ NỘI DUNG THIÊN VĂN LẤY TỪ NASA — mỗi câu có `src` trỏ về đúng trang đã
   đối chiếu (kiểm trả 200 ngày 30/07/2026). Sửa số liệu thì phải sửa cả `src`;
   viết một con số không có nguồn là bịa. Năm câu về lập trình (không có `src`)
   là câu khái niệm của bài học, không phải số liệu khoa học.

   ⚠️ KHÔNG CẦN ĐẾM PHÂN BỐ A/B/C/D NỮA (sửa 31/07/2026). Luật cũ ở đây bắt rải
   đều đáp án đúng để trẻ không học mẹo "cứ chọn B". Từ 31/07/2026 `quiz.html`
   gọi `shuffleOptions()` trong `renderQuestion()` — **4 lựa chọn được trộn lại
   mỗi lần hiện câu**, nên THỨ TỰ KHAI BÁO Ở FILE NÀY KHÔNG BAO GIỜ TỚI NGƯỜI
   CHƠI. Đếm phân bố ở đây là đo một thứ không ai nhìn thấy.
   Chú thích cũ còn ghi "A=8·B=6·C=6·D=5 (25 câu)" trong khi bank đã 35 câu —
   đúng cái bẫy của việc chép một con số vào chú thích rồi phải nhớ cập nhật.

   ⚠️ NHƯNG luật chỉ chết CHỪNG NÀO MỌI trang dùng bank đều trộn. Hiện **chỉ
   `quiz.html` dùng bank này** (library.html chưa nối vào dù nói ở trên là để
   dùng chung). Trang mới nào vẽ thẳng `opts` theo thứ tự khai báo thì luật rải
   đều SỐNG LẠI với riêng trang đó — hoặc tốt hơn, dùng lại `shuffled()` của bank.

   ⚠️ `a` LUÔN là chỉ số trong `opts` GỐC, không phải ô trên màn hình. Đừng trộn
   tại chỗ `opts` và đừng sửa `a` — xem chú thích ở `quiz.html` chỗ ORDER/SLOT. */
window.AstroQQuestions = (function () {
  "use strict";

  /* Nguồn dùng lại nhiều lần — khai một chỗ để không gõ lệch URL. */
  var S = {
    star:   { name: "NASA Science — Stars",                url: "https://science.nasa.gov/universe/stars/" },
    planet: { name: "NASA Science — About the Planets",    url: "https://science.nasa.gov/solar-system/planets/" },
    dwarf:  { name: "NASA Science — Pluto & Dwarf Planets", url: "https://science.nasa.gov/dwarf-planets/" },
    moon:   { name: "NASA Science — Moons",                url: "https://science.nasa.gov/solar-system/moons/" },
    ganym:  { name: "NASA Science — Ganymede",             url: "https://science.nasa.gov/jupiter/moons/ganymede/" },
    aster:  { name: "NASA Science — Asteroid Facts",       url: "https://science.nasa.gov/solar-system/asteroids/facts/" },
    comet:  { name: "NASA Science — Comet Facts",          url: "https://science.nasa.gov/solar-system/comets/facts/" },
    meteor: { name: "NASA Science — Meteors & Meteorites", url: "https://science.nasa.gov/solar-system/meteors-meteorites/facts/" },
    exo:    { name: "NASA Science — Exoplanets",           url: "https://science.nasa.gov/exoplanets/" },
    /* Ba nguồn thêm 30/07/2026 cho 5 thuật ngữ mới. Cả ba đã kiểm trả 200.
       ⚠️ `grav` là **NASA Space Place**, không phải science.nasa.gov — cố ý: đó là
          trang NASA viết CHO TRẺ EM, đúng độ tuổi 8–15, và science.nasa.gov không
          có trang định nghĩa lực hấp dẫn tương đương. Vẫn là nguồn NASA chính thức;
          phép kiểm nguồn đã nới đúng hai tên miền này, không mở cho URL bất kỳ. */
    bh:     { name: "NASA Science — Black Holes",          url: "https://science.nasa.gov/universe/black-holes/" },
    grav:   { name: "NASA Space Place — What Is Gravity?", url: "https://spaceplace.nasa.gov/what-is-gravity/en/" },
    cosmos: { name: "NASA Science — Cosmic History",       url: "https://science.nasa.gov/universe/overview/" }
  };

  var ALL = [

    /* ══════════════════ 1. STAR — Ngôi sao ══════════════════ */
    {
      term: "star",
      topic: { vi: "NGÔI SAO", en: "STAR" },
      q: { vi: "Ngôi sao là gì?", en: "What is a star?" },
      opts: [
        { vi: "Quả cầu khí nóng khổng lồ, tự phát ra ánh sáng", en: "A giant ball of hot gas that makes its own light" },
        { vi: "Khối đá lạnh quay quanh một hành tinh", en: "A cold rock orbiting a planet" },
        { vi: "Cục băng lẫn bụi, có đuôi dài", en: "A lump of ice and dust with a long tail" },
        { vi: "Hòn đá đang cháy trong khí quyển", en: "A rock burning up in the atmosphere" }
      ],
      a: 0,
      ok: { vi: "Chính xác! NASA cho biết ngôi sao là <b>quả cầu khí nóng khổng lồ</b> — phần lớn là hydro, kèm một ít heli. Mặt Trời chính là một ngôi sao.",
            en: "Correct! NASA describes a star as a <b>giant ball of hot gas</b> — mostly hydrogen with some helium. Our Sun is a star." },
      no: { vi: "Chưa đúng! Ngôi sao là <b>quả cầu khí nóng tự phát sáng</b>, không phải đá cũng không phải băng.",
            en: "Not quite! A star is a <b>ball of hot gas that shines on its own</b> — not rock, not ice." },
      hint: { vi: "Mặt Trời là một ngôi sao. Nó nóng, nó sáng, và nó <b>không hề rắn</b>.",
              en: "The Sun is a star. It's hot, it's bright, and it is <b>not solid</b>." },
      src: S.star
    },
    {
      term: "star-fusion",
      topic: { vi: "NGÔI SAO", en: "STAR" },
      q: { vi: "Trong lõi Mặt Trời, các hạt nhân hydro bị ép lại để tạo thành nguyên tố nào?",
           en: "In the Sun's core, hydrogen nuclei are squeezed together to form which element?" },
      opts: [
        { vi: "Sắt (Fe)", en: "Iron (Fe)" },
        { vi: "Ô-xy (O)", en: "Oxygen (O)" },
        { vi: "Heli (He)", en: "Helium (He)" },
        { vi: "Vàng (Au)", en: "Gold (Au)" }
      ],
      a: 2,
      ok: { vi: "Đúng rồi! Áp suất và nhiệt độ khủng khiếp trong lõi ép hạt nhân hydro lại thành <b>heli</b>. Quá trình đó gọi là <b>phản ứng nhiệt hạch</b>, và nó sinh ra toàn bộ năng lượng giữ cho ngôi sao không sụp xuống.",
            en: "Right! The immense pressure and heat in the core fuse hydrogen nuclei into <b>helium</b>. That process — <b>nuclear fusion</b> — releases the energy that keeps a star from collapsing." },
      no: { vi: "Chưa đúng! Hydro hợp lại thành <b>heli</b> — đó là nguồn năng lượng của mọi ngôi sao.",
            en: "Not quite! Hydrogen fuses into <b>helium</b> — that's what powers every star." },
      hint: { vi: "Nguyên tố nhẹ thứ hai trong bảng tuần hoàn — cùng loại khí người ta bơm vào bóng bay!",
              en: "The second-lightest element on the periodic table — the same gas that fills party balloons!" },
      src: S.star
    },

    /* ══════════════════ 2. PLANET — Hành tinh ══════════════════ */
    {
      term: "planet",
      topic: { vi: "HÀNH TINH", en: "PLANET" },
      q: { vi: "Ngoài việc quay quanh Mặt Trời và có dạng gần tròn, IAU còn đòi một hành tinh phải làm được điều gì?",
           en: "Besides orbiting the Sun and being nearly round, what third thing does the IAU require of a planet?" },
      opts: [
        { vi: "Dọn sạch các vật thể cùng cỡ quanh quỹ đạo của nó", en: "Clear away other objects of similar size near its orbit" },
        { vi: "Có ít nhất một vệ tinh", en: "Have at least one moon" },
        { vi: "Có khí quyển để thở", en: "Have a breathable atmosphere" },
        { vi: "Tự phát ra ánh sáng", en: "Make its own light" }
      ],
      a: 0,
      ok: { vi: "Chuẩn! Tiêu chí thứ ba của IAU (2006) là <b>“dọn sạch vùng quỹ đạo”</b>: hành tinh phải đủ nặng để lực hấp dẫn của nó hút hoặc đẩy hết các vật thể cùng cỡ ra khỏi đường bay.",
            en: "Exactly! The IAU's third criterion (2006) is <b>“clearing the neighbourhood”</b>: a planet must be massive enough that its gravity has swept away other objects of similar size along its orbit." },
      no: { vi: "Chưa đúng! Tiêu chí thứ ba là <b>dọn sạch vùng quỹ đạo</b> — không liên quan tới vệ tinh hay khí quyển. Hành tinh cũng không tự phát sáng, nó chỉ phản chiếu ánh sáng ngôi sao.",
            en: "Not quite! The third criterion is <b>clearing its orbital neighbourhood</b> — nothing about moons or air. Planets don't make light either; they reflect their star's." },
      hint: { vi: "Nghĩ tới cái sân: hành tinh phải <b>dọn sạch sân</b> của mình.",
              en: "Think of a playground: a planet has to <b>sweep its own yard</b> clean." },
      src: S.dwarf
    },
    {
      term: "planet-count",
      topic: { vi: "HÀNH TINH", en: "PLANET" },
      q: { vi: "Hệ Mặt Trời của chúng ta có bao nhiêu hành tinh?", en: "How many planets are in our solar system?" },
      opts: [
        { vi: "7 hành tinh", en: "7 planets" },
        { vi: "8 hành tinh", en: "8 planets" },
        { vi: "9 hành tinh", en: "9 planets" },
        { vi: "12 hành tinh", en: "12 planets" }
      ],
      a: 1,
      ok: { vi: "Đúng! NASA ghi rõ hệ Mặt Trời có <b>8 hành tinh</b>: Sao Thuỷ, Sao Kim, Trái Đất, Sao Hoả, Sao Mộc, Sao Thổ, Sao Thiên Vương và Sao Hải Vương.",
            en: "Correct! NASA states our solar system has <b>8 planets</b>: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus and Neptune." },
      no: { vi: "Chưa đúng! Có <b>8 hành tinh</b>. Sao Diêm Vương từng được xem là hành tinh thứ chín, nhưng năm 2006 IAU xếp lại nó thành <b>hành tinh lùn</b>.",
            en: "Not quite! There are <b>8 planets</b>. Pluto was once counted as the ninth, but in 2006 the IAU reclassified it as a <b>dwarf planet</b>." },
      hint: { vi: "Đếm từ Sao Thuỷ ra tới Sao Hải Vương — và nhớ rằng Sao Diêm Vương đã “đổi nghề”.",
              en: "Count from Mercury out to Neptune — and remember Pluto changed job title." },
      src: S.planet
    },

    /* ══════════════════ 3. DWARF PLANET — Hành tinh lùn ══════════════════ */
    {
      term: "dwarf",
      topic: { vi: "HÀNH TINH LÙN", en: "DWARF PLANET" },
      q: { vi: "Hành tinh lùn cũng quay quanh Mặt Trời và cũng gần tròn. Vậy nó THIẾU điều gì so với hành tinh?",
           en: "A dwarf planet orbits the Sun and is nearly round too. So what is it MISSING compared with a planet?" },
      opts: [
        { vi: "Nó không có vệ tinh nào", en: "It has no moons at all" },
        { vi: "Nó không tự quay quanh trục", en: "It doesn't spin on its axis" },
        { vi: "Nó chưa dọn sạch vùng quỹ đạo của mình", en: "It hasn't cleared its orbital neighbourhood" },
        { vi: "Nó không phải vật thể rắn", en: "It isn't a solid body" }
      ],
      a: 2,
      ok: { vi: "Chính xác! Hành tinh lùn <b>chưa dọn sạch vùng quỹ đạo</b> — quanh nó vẫn còn rất nhiều vật thể khác. Sao Diêm Vương chia sẻ vùng của mình với vô số vật thể ở vành đai Kuiper, dù bản thân nó vẫn có vệ tinh riêng.",
            en: "Exactly! A dwarf planet <b>hasn't cleared its orbit of debris</b> — plenty of other bodies still share its lane. Pluto shares its neighbourhood with countless Kuiper Belt objects, even though it does have moons of its own." },
      no: { vi: "Chưa đúng! Điều còn thiếu là <b>dọn sạch vùng quỹ đạo</b>. Hành tinh lùn vẫn có thể có vệ tinh và vẫn tự quay bình thường.",
            en: "Not quite! What's missing is <b>clearing the orbital neighbourhood</b>. A dwarf planet can still have moons and still spin normally." },
      hint: { vi: "Cùng một câu chuyện “dọn sân” — nhưng lần này là <b>chưa dọn xong</b>.",
              en: "Same “sweep the yard” story — except this time the yard <b>isn't swept</b>." },
      src: S.dwarf
    },
    {
      term: "dwarf-ceres",
      topic: { vi: "HÀNH TINH LÙN", en: "DWARF PLANET" },
      q: { vi: "Hành tinh lùn nào nằm trong vành đai tiểu hành tinh, giữa Sao Hoả và Sao Mộc?",
           en: "Which dwarf planet sits in the asteroid belt between Mars and Jupiter?" },
      opts: [
        { vi: "Ceres", en: "Ceres" },
        { vi: "Sao Diêm Vương (Pluto)", en: "Pluto" },
        { vi: "Eris", en: "Eris" },
        { vi: "Makemake", en: "Makemake" }
      ],
      a: 0,
      ok: { vi: "Đúng! <b>Ceres</b> là vật thể lớn nhất trong vành đai tiểu hành tinh và là hành tinh lùn duy nhất ở vùng trong hệ Mặt Trời. Bốn hành tinh lùn còn lại — Pluto, Haumea, Makemake, Eris — đều nằm xa hơn Sao Hải Vương.",
            en: "Correct! <b>Ceres</b> is the largest object in the asteroid belt and the only dwarf planet in the inner solar system. The other four — Pluto, Haumea, Makemake and Eris — all lie beyond Neptune." },
      no: { vi: "Chưa đúng! Đó là <b>Ceres</b>. Pluto, Haumea, Makemake và Eris đều ở xa hơn Sao Hải Vương, ngoài vành đai Kuiper.",
            en: "Not quite! It's <b>Ceres</b>. Pluto, Haumea, Makemake and Eris are all far beyond Neptune, out in the Kuiper Belt." },
      hint: { vi: "Nó là <b>vật thể lớn nhất</b> trong vành đai tiểu hành tinh — tàu Dawn của NASA đã bay tới đó.",
              en: "It's the <b>largest object</b> in the asteroid belt — NASA's Dawn spacecraft visited it." },
      src: S.dwarf
    },

    /* ══════════════════ 4. MOON — Vệ tinh tự nhiên ══════════════════ */
    {
      term: "moon",
      topic: { vi: "VỆ TINH TỰ NHIÊN", en: "NATURAL SATELLITE" },
      q: { vi: "Vệ tinh tự nhiên (moon) là gì?", en: "What is a moon, or natural satellite?" },
      opts: [
        { vi: "Thiết bị do con người phóng lên quỹ đạo", en: "A device humans launched into orbit" },
        { vi: "Vật thể hình thành tự nhiên, quay quanh một hành tinh", en: "A naturally-formed body that orbits a planet" },
        { vi: "Một ngôi sao nhỏ quay quanh ngôi sao lớn", en: "A small star orbiting a bigger star" },
        { vi: "Hòn đá đã rơi xuống mặt đất", en: "A rock that has landed on the ground" }
      ],
      a: 1,
      ok: { vi: "Chuẩn! NASA gọi <b>vật thể hình thành tự nhiên quay quanh hành tinh</b> là mặt trăng (moon) hay vệ tinh tự nhiên. Thứ do con người chế tạo rồi phóng lên thì gọi là <b>vệ tinh nhân tạo</b>.",
            en: "Exactly! NASA calls <b>naturally-formed bodies that orbit planets</b> moons, or planetary satellites. Something humans built and launched is an <b>artificial satellite</b>." },
      no: { vi: "Chưa đúng! Vệ tinh tự nhiên là <b>vật thể tự nhiên quay quanh một hành tinh</b> — chữ “tự nhiên” chính là chỗ khác với vệ tinh nhân tạo.",
            en: "Not quite! A natural satellite is a <b>natural body orbiting a planet</b> — the word “natural” is exactly what sets it apart from an artificial one." },
      hint: { vi: "Chữ quan trọng nhất trong câu hỏi là <b>“tự nhiên”</b>.",
              en: "The key word in the question is <b>“natural”</b>." },
      src: S.moon
    },
    {
      term: "moon-largest",
      topic: { vi: "VỆ TINH TỰ NHIÊN", en: "NATURAL SATELLITE" },
      q: { vi: "Vệ tinh lớn nhất trong hệ Mặt Trời là vệ tinh nào?", en: "Which is the largest moon in the solar system?" },
      opts: [
        { vi: "Mặt Trăng của Trái Đất", en: "Earth's Moon" },
        { vi: "Europa (Sao Mộc)", en: "Europa (Jupiter)" },
        { vi: "Titan (Sao Thổ)", en: "Titan (Saturn)" },
        { vi: "Ganymede (Sao Mộc)", en: "Ganymede (Jupiter)" }
      ],
      a: 3,
      ok: { vi: "Đúng! <b>Ganymede</b> của Sao Mộc là vệ tinh lớn nhất hệ Mặt Trời — theo NASA nó còn <b>lớn hơn cả hành tinh Sao Thuỷ</b>, và là vệ tinh duy nhất có từ trường riêng.",
            en: "Correct! Jupiter's <b>Ganymede</b> is the largest moon in the solar system — NASA notes it is <b>even bigger than the planet Mercury</b>, and it's the only moon with its own magnetic field." },
      no: { vi: "Chưa đúng! Đó là <b>Ganymede</b>, một vệ tinh của Sao Mộc, thậm chí lớn hơn cả Sao Thuỷ.",
            en: "Not quite! It's <b>Ganymede</b>, a moon of Jupiter — larger even than the planet Mercury." },
      hint: { vi: "Nó thuộc Sao Mộc, và to hơn cả <b>một hành tinh</b> thật sự.",
              en: "It belongs to Jupiter — and it's bigger than an actual <b>planet</b>." },
      src: S.ganym
    },

    /* ══════════════════ 5. ASTEROID — Tiểu hành tinh ══════════════════ */
    {
      term: "asteroid-belt",
      topic: { vi: "TIỂU HÀNH TINH", en: "ASTEROID" },
      q: { vi: "Vành đai tiểu hành tinh chính nằm ở đâu?", en: "Where is the main asteroid belt?" },
      opts: [
        { vi: "Giữa Trái Đất và Sao Hoả", en: "Between Earth and Mars" },
        { vi: "Giữa Sao Hoả và Sao Mộc", en: "Between Mars and Jupiter" },
        { vi: "Bên ngoài Sao Hải Vương", en: "Beyond Neptune" },
        { vi: "Ngay quanh Mặt Trăng", en: "Right around the Moon" }
      ],
      a: 1,
      ok: { vi: "Chính xác! Vành đai chính nằm <b>giữa Sao Hoả và Sao Mộc</b>. NASA ước tính ở đó có khoảng <b>1,1–1,9 triệu</b> tiểu hành tinh lớn hơn 1 km.",
            en: "Exactly! The main belt orbits <b>between Mars and Jupiter</b>. NASA estimates it holds roughly <b>1.1 to 1.9 million</b> asteroids larger than 1 km." },
      no: { vi: "Chưa đúng! Vành đai chính ở <b>giữa Sao Hoả và Sao Mộc</b>. Vùng bên ngoài Sao Hải Vương là vành đai Kuiper — nơi của các vật thể băng.",
            en: "Not quite! The main belt lies <b>between Mars and Jupiter</b>. The region beyond Neptune is the Kuiper Belt, home to icy bodies." },
      hint: { vi: "Nó ngăn giữa hành tinh đỏ và hành tinh khổng lồ nhất.",
              en: "It sits between the red planet and the biggest giant." },
      src: S.aster
    },
    {
      term: "asteroid-what",
      topic: { vi: "TIỂU HÀNH TINH", en: "ASTEROID" },
      q: { vi: "Tiểu hành tinh thực chất là gì?", en: "What is an asteroid, really?" },
      opts: [
        { vi: "Mảnh đá còn sót lại từ thời hệ Mặt Trời mới hình thành", en: "A rocky leftover from when the solar system formed" },
        { vi: "Cục băng bốc hơi thành đuôi dài khi gần Mặt Trời", en: "An icy lump that grows a long tail near the Sun" },
        { vi: "Một quả cầu khí nóng cỡ nhỏ", en: "A small ball of hot gas" },
        { vi: "Vệ tinh nhân tạo đã hỏng", en: "A broken-down artificial satellite" }
      ],
      a: 0,
      ok: { vi: "Đúng! NASA gọi tiểu hành tinh là <b>mảnh đá còn sót lại</b> từ lúc hệ Mặt Trời hình thành khoảng <b>4,6 tỉ năm</b> trước. Chúng đôi khi còn được gọi là “tiểu hành tinh” (minor planets).",
            en: "Correct! NASA describes asteroids as <b>rocky remnants</b> left over from the formation of the solar system about <b>4.6 billion years</b> ago. They're sometimes called minor planets." },
      no: { vi: "Chưa đúng! Đó là <b>mảnh đá</b> còn sót lại từ thời hệ Mặt Trời hình thành. Cục băng có đuôi dài là <b>sao chổi</b>, không phải tiểu hành tinh.",
            en: "Not quite! It's a <b>rocky leftover</b> from the solar system's formation. The icy one with a tail is a <b>comet</b>, not an asteroid." },
      hint: { vi: "Từ khoá là <b>đá</b> — băng thì thuộc về một loại vật thể khác.",
              en: "The key word is <b>rock</b> — ice belongs to a different kind of object." },
      src: S.aster
    },

    /* ══════════════════ 6. COMET — Sao chổi ══════════════════ */
    {
      term: "comet-what",
      topic: { vi: "SAO CHỔI", en: "COMET" },
      q: { vi: "Sao chổi được tạo nên chủ yếu từ gì?", en: "What is a comet mostly made of?" },
      opts: [
        { vi: "Đá và kim loại đặc", en: "Solid rock and metal" },
        { vi: "Khí hydro đang cháy", en: "Burning hydrogen gas" },
        { vi: "Băng bọc lớp bụi và chất hữu cơ tối màu", en: "Ice coated with dust and dark organic material" },
        { vi: "Kim cương và thuỷ tinh", en: "Diamond and glass" }
      ],
      a: 2,
      ok: { vi: "Chuẩn! NASA gọi sao chổi là <b>“quả cầu tuyết bẩn”</b>: phần lớn là băng bọc lớp vật chất hữu cơ tối màu. Khi lại gần Mặt Trời, băng bốc hơi tạo ra lớp khí bao quanh (coma) và cái đuôi dài.",
            en: "Exactly! NASA calls comets <b>“dirty snowballs”</b>: mostly ice coated with dark organic material. Near the Sun that ice vaporises into a glowing coma and a long tail." },
      no: { vi: "Chưa đúng! Sao chổi chủ yếu là <b>băng</b> lẫn bụi — đó là lý do nó mọc đuôi khi lại gần Mặt Trời. Vật thể bằng đá thì là <b>tiểu hành tinh</b>.",
            en: "Not quite! A comet is mostly <b>ice</b> and dust — that's why it grows a tail near the Sun. The rocky ones are <b>asteroids</b>." },
      hint: { vi: "Vì sao nó mọc đuôi khi lại gần Mặt Trời? Vì có thứ gì đó <b>bốc hơi</b> được.",
              en: "Why does it grow a tail near the Sun? Because something in it can <b>evaporate</b>." },
      src: S.comet
    },
    {
      term: "comet-tail",
      topic: { vi: "SAO CHỔI", en: "COMET" },
      q: { vi: "Đuôi sao chổi luôn chỉ về hướng nào?", en: "Which way does a comet's tail always point?" },
      opts: [
        { vi: "Luôn chỉ thẳng vào Mặt Trời", en: "Straight toward the Sun" },
        { vi: "Luôn ngược hướng bay của sao chổi", en: "Always opposite its direction of travel" },
        { vi: "Luôn về phía Trái Đất", en: "Always toward Earth" },
        { vi: "Hướng ra xa Mặt Trời", en: "Away from the Sun" }
      ],
      a: 3,
      ok: { vi: "Đúng! Áp lực ánh sáng và gió Mặt Trời thổi bụi cùng khí <b>ra xa Mặt Trời</b>. Nghĩa là khi sao chổi đang bay ra khỏi Mặt Trời, cái đuôi lại <b>đi trước</b> nó!",
            en: "Correct! Sunlight pressure and the solar wind blow the dust and gas <b>away from the Sun</b>. So when a comet heads back out, its tail actually leads the way!" },
      no: { vi: "Chưa đúng! Đuôi bị gió Mặt Trời thổi <b>ra xa Mặt Trời</b> — nó không phụ thuộc vào hướng bay của sao chổi.",
            en: "Not quite! The tail is blown <b>away from the Sun</b> — it doesn't depend on which way the comet is moving." },
      hint: { vi: "Cứ hình dung có một cơn gió thổi từ Mặt Trời ra mọi phía.",
              en: "Picture a wind blowing outward from the Sun in every direction." },
      src: S.comet
    },

    /* ══════════════════ 7. METEOROID — Thiên thạch nhỏ ══════════════════ */
    {
      term: "meteoroid",
      topic: { vi: "THIÊN THẠCH NHỎ", en: "METEOROID" },
      q: { vi: "Meteoroid (thiên thạch nhỏ) là gì?", en: "What is a meteoroid?" },
      opts: [
        { vi: "Vệt sáng vụt qua trời đêm", en: "A streak of light flashing across the night sky" },
        { vi: "Hòn đá đang bay trong không gian, từ hạt bụi tới tiểu hành tinh nhỏ", en: "A rock travelling in space, from a dust grain up to a small asteroid" },
        { vi: "Hòn đá đã rơi xuống và nằm trên mặt đất", en: "A rock that has landed and lies on the ground" },
        { vi: "Một hành tinh lùn ở vành đai Kuiper", en: "A dwarf planet in the Kuiper Belt" }
      ],
      a: 1,
      ok: { vi: "Chuẩn! NASA định nghĩa meteoroid là <b>“đá không gian” có cỡ từ hạt bụi tới tiểu hành tinh nhỏ</b> — điểm quan trọng nhất là nó vẫn <b>đang ở trong không gian</b>.",
            en: "Exactly! NASA defines meteoroids as <b>space rocks ranging from dust grains to small asteroids</b> — the key point is that they are still <b>out in space</b>." },
      no: { vi: "Chưa đúng! Meteoroid vẫn đang <b>trong không gian</b>. Vệt sáng trên trời là <b>meteor</b>, còn hòn đá nằm trên đất là <b>meteorite</b>.",
            en: "Not quite! A meteoroid is still <b>in space</b>. The streak in the sky is a <b>meteor</b>; the rock on the ground is a <b>meteorite</b>." },
      hint: { vi: "Cả ba từ meteoroid / meteor / meteorite chỉ khác nhau ở <b>nơi</b> hòn đá đang ở.",
              en: "Meteoroid / meteor / meteorite differ only by <b>where</b> the rock is." },
      src: S.meteor
    },
    {
      term: "meteoroid-chain",
      topic: { vi: "THIÊN THẠCH NHỎ", en: "METEOROID" },
      q: { vi: "Ba từ meteoroid – meteor – meteorite khác nhau ở điểm nào?",
           en: "What actually distinguishes meteoroid, meteor and meteorite?" },
      opts: [
        { vi: "Khác nhau ở màu sắc của hòn đá", en: "The colour of the rock" },
        { vi: "Khác nhau ở thành phần hoá học", en: "Their chemical make-up" },
        { vi: "Khác nhau ở nơi vật thể đang ở: trong không gian, trong khí quyển, hay đã nằm trên mặt đất", en: "Where the object is: in space, in the atmosphere, or already on the ground" },
        { vi: "Khác nhau ở tên người tìm ra nó", en: "Who discovered it" }
      ],
      a: 2,
      ok: { vi: "Tuyệt! Vẫn là một hòn đá, chỉ đổi tên theo <b>vị trí</b>: trong không gian là <b>meteoroid</b>, đang cháy sáng trong khí quyển là <b>meteor</b> (sao băng), còn sót lại và nằm trên đất là <b>meteorite</b> (thiên thạch).",
            en: "Nice! It's the same rock, renamed by <b>location</b>: in space it's a <b>meteoroid</b>, blazing through the atmosphere it's a <b>meteor</b> (shooting star), and once it survives to the ground it's a <b>meteorite</b>." },
      no: { vi: "Chưa đúng! Ba từ đó nói về <b>vị trí</b> chứ không nói về chất liệu: không gian → khí quyển → mặt đất.",
            en: "Not quite! The three words describe <b>location</b>, not material: space → atmosphere → ground." },
      hint: { vi: "Cùng một hòn đá đi qua ba chặng đường. Ba cái tên ứng với <b>ba chặng</b> đó.",
              en: "One rock, three stages of a journey. Three names for <b>three stages</b>." },
      src: S.meteor
    },

    /* ══════════════════ 8. METEOR — Sao băng ══════════════════ */
    {
      term: "meteor",
      topic: { vi: "SAO BĂNG", en: "METEOR" },
      q: { vi: "“Sao băng” mà ta thấy trên trời đêm thực chất là gì?", en: "What is a “shooting star” really?" },
      opts: [
        { vi: "Một ngôi sao đang rơi khỏi trời", en: "A star falling out of the sky" },
        { vi: "Một vệ tinh nhân tạo đang bay qua", en: "An artificial satellite passing by" },
        { vi: "Ánh sáng phản chiếu từ Mặt Trăng", en: "Light reflecting off the Moon" },
        { vi: "Vệt sáng do đá không gian lao vào khí quyển và cháy lên", en: "The streak of light as a space rock enters the atmosphere and burns up" }
      ],
      a: 3,
      ok: { vi: "Đúng! Sao băng chẳng phải ngôi sao nào cả: đó là <b>vệt sáng</b> khi đá không gian lao vào khí quyển với tốc độ cực nhanh rồi <b>cháy lên</b>. Tiếng Anh gọi vui là “shooting star”.",
            en: "Correct! A shooting star is no star at all: it's the <b>streak of light</b> made when a space rock hits the atmosphere at huge speed and <b>burns up</b>." },
      no: { vi: "Chưa đúng! Ngôi sao thì to hơn Trái Đất rất nhiều và ở cách ta hàng nghìn tỉ km. Sao băng chỉ là <b>đá không gian đang cháy trong khí quyển</b>.",
            en: "Not quite! Stars are vastly bigger than Earth and unimaginably far away. A meteor is just <b>a space rock burning up in the atmosphere</b>." },
      hint: { vi: "Nếu nó thật là ngôi sao thì trời đã hết sao từ lâu rồi…",
              en: "If those really were stars, the sky would have run out long ago…" },
      src: S.meteor
    },
    {
      term: "meteor-fireball",
      topic: { vi: "SAO BĂNG", en: "METEOR" },
      q: { vi: "Một sao băng sáng hơn cả Sao Kim thì được NASA gọi là gì?",
           en: "What does NASA call a meteor that shines brighter than Venus?" },
      opts: [
        { vi: "Sao chổi", en: "A comet" },
        { vi: "Siêu tân tinh", en: "A supernova" },
        { vi: "Nhật thực", en: "A solar eclipse" },
        { vi: "Quả cầu lửa (fireball)", en: "A fireball" }
      ],
      a: 3,
      ok: { vi: "Chuẩn! NASA gọi những sao băng <b>sáng hơn Sao Kim</b> là <b>quả cầu lửa (fireball)</b>. Chúng sáng đến mức có thể thấy được cả lúc trời còn chưa tối hẳn.",
            en: "Exactly! NASA calls meteors <b>brighter than Venus</b> <b>fireballs</b>. They can be bright enough to spot before the sky is fully dark." },
      no: { vi: "Chưa đúng! Đó là <b>quả cầu lửa (fireball)</b> — vẫn là một sao băng, chỉ là sáng khác thường.",
            en: "Not quite! It's a <b>fireball</b> — still a meteor, just an unusually bright one." },
      hint: { vi: "Tên gọi rất “nóng”, và nó vẫn thuộc họ sao băng.",
              en: "The name sounds hot — and it's still a meteor." },
      src: S.meteor
    },

    /* ══════════════════ 9. METEORITE — Thiên thạch ══════════════════ */
    {
      term: "meteorite",
      topic: { vi: "THIÊN THẠCH", en: "METEORITE" },
      q: { vi: "Khi nào một hòn đá không gian được gọi là meteorite (thiên thạch)?",
           en: "When does a space rock earn the name meteorite?" },
      opts: [
        { vi: "Khi nó bắt đầu cháy trong khí quyển", en: "When it starts burning in the atmosphere" },
        { vi: "Khi nó bay ngang qua Mặt Trăng", en: "When it passes the Moon" },
        { vi: "Khi nó sống sót qua khí quyển và chạm tới mặt đất", en: "When it survives the atmosphere and reaches the ground" },
        { vi: "Khi nó lớn hơn 1 km", en: "When it is larger than 1 km" }
      ],
      a: 2,
      ok: { vi: "Chính xác! Meteoroid nào <b>sống sót qua khí quyển và rơi xuống đất</b> thì được gọi là <b>meteorite</b>. NASA cho biết phần lớn thiên thạch tìm được chỉ to bằng viên sỏi đến nắm tay.",
            en: "Exactly! A meteoroid that <b>survives its trip through the atmosphere and hits the ground</b> is a <b>meteorite</b>. NASA notes most are pebble to fist sized." },
      no: { vi: "Chưa đúng! Lúc còn đang cháy trên trời thì nó là <b>meteor</b>. Chỉ khi <b>chạm được mặt đất</b> nó mới là <b>meteorite</b>.",
            en: "Not quite! While it's still blazing overhead it's a <b>meteor</b>. Only once it <b>reaches the ground</b> is it a <b>meteorite</b>." },
      hint: { vi: "Đây là cái tên dành cho hòn đá mà con người có thể <b>cầm lên tay</b>.",
              en: "This is the name for the rock you could actually <b>pick up</b>." },
      src: S.meteor
    },
    {
      term: "meteorite-survive",
      topic: { vi: "THIÊN THẠCH", en: "METEORITE" },
      q: { vi: "Theo NASA, phần khối lượng của một vật thể lao vào khí quyển mà tới được mặt đất thường là bao nhiêu?",
           en: "According to NASA, how much of an object entering the atmosphere usually makes it to the ground?" },
      opts: [
        { vi: "Gần như toàn bộ", en: "Almost all of it" },
        { vi: "Khoảng một nửa", en: "About half" },
        { vi: "Đúng 25%", en: "Exactly 25%" },
        { vi: "Thường dưới 5%", en: "Usually less than 5%" }
      ],
      a: 3,
      ok: { vi: "Đúng! NASA cho biết <b>thường dưới 5%</b> khối lượng ban đầu tới được mặt đất — phần còn lại cháy hết trên đường. Mỗi ngày có khoảng <b>48,5 tấn</b> vật chất thiên thạch rơi xuống Trái Đất.",
            en: "Correct! NASA says <b>less than 5%</b> of the original object usually reaches the ground — the rest burns away. About <b>48.5 tons</b> of meteoritic material falls on Earth every day." },
      no: { vi: "Chưa đúng! <b>Dưới 5%</b> thôi. Khí quyển Trái Đất là một tấm khiên rất hiệu quả.",
            en: "Not quite! <b>Less than 5%</b>. Earth's atmosphere is a remarkably good shield." },
      hint: { vi: "Khí quyển bảo vệ chúng ta rất tốt — nên con số này <b>rất nhỏ</b>.",
              en: "The atmosphere protects us well — so this number is <b>very small</b>." },
      src: S.meteor
    },

    /* ══════════════════ 10. EXOPLANET — Ngoại hành tinh ══════════════════ */
    {
      term: "exoplanet",
      topic: { vi: "NGOẠI HÀNH TINH", en: "EXOPLANET" },
      q: { vi: "Ngoại hành tinh (exoplanet) là gì?", en: "What is an exoplanet?" },
      opts: [
        { vi: "Hành tinh nằm ngoài hệ Mặt Trời của chúng ta", en: "A planet beyond our solar system" },
        { vi: "Hành tinh ở rìa ngoài cùng hệ Mặt Trời", en: "A planet at the outer edge of our solar system" },
        { vi: "Hành tinh lùn chưa được đặt tên", en: "A dwarf planet that hasn't been named yet" },
        { vi: "Vệ tinh của một hành tinh khác", en: "A moon belonging to another planet" }
      ],
      a: 0,
      ok: { vi: "Chuẩn! Ngoại hành tinh là <b>hành tinh nằm ngoài hệ Mặt Trời</b>. Phần lớn quay quanh một ngôi sao khác, nhưng cũng có “hành tinh lang thang” không thuộc ngôi sao nào. NASA đã xác nhận <b>hơn 6.000</b> ngoại hành tinh.",
            en: "Exactly! An exoplanet is <b>any planet beyond our solar system</b>. Most orbit other stars, though some free-floating “rogue planets” belong to no star at all. NASA has confirmed <b>more than 6,000</b> of them." },
      no: { vi: "Chưa đúng! Tiền tố “exo-” nghĩa là <b>bên ngoài</b>: đó là hành tinh <b>ngoài hệ Mặt Trời</b> của chúng ta.",
            en: "Not quite! The prefix “exo-” means <b>outside</b>: it's a planet <b>outside our solar system</b>." },
      hint: { vi: "Tiền tố “exo-” trong tiếng Hy Lạp nghĩa là <b>bên ngoài</b>.",
              en: "The Greek prefix “exo-” means <b>outside</b>." },
      src: S.exo
    },
    {
      term: "exoplanet-transit",
      topic: { vi: "NGOẠI HÀNH TINH", en: "EXOPLANET" },
      q: { vi: "Một cách phổ biến để tìm ngoại hành tinh là quan sát điều gì?",
           en: "One common way to find exoplanets is to watch for what?" },
      opts: [
        { vi: "Âm thanh phát ra từ ngôi sao", en: "Sounds coming from the star" },
        { vi: "Ngôi sao mờ đi một chút khi hành tinh đi ngang trước mặt nó", en: "The star dimming slightly as a planet crosses in front of it" },
        { vi: "Nhiệt độ trên Trái Đất tăng lên", en: "Earth's temperature going up" },
        { vi: "Ngắm bằng mắt thường vào đêm rằm", en: "Looking with the naked eye on a full-moon night" }
      ],
      a: 1,
      ok: { vi: "Đúng! Đó là <b>phương pháp quá cảnh (transit)</b>: hành tinh đi ngang trước ngôi sao thì che bớt ánh sáng, khiến ngôi sao <b>mờ đi một chút</b> — kính thiên văn đo được độ mờ ấy. Một cách khác là đo <b>độ lắc</b> của ngôi sao do hành tinh kéo (radial velocity).",
            en: "Correct! That's the <b>transit method</b>: a planet crossing in front of its star blocks a little starlight, so the star <b>dims slightly</b> — and telescopes can measure it. Another way is to measure the star's <b>wobble</b> (radial velocity)." },
      no: { vi: "Chưa đúng! Cách phổ biến là <b>phương pháp quá cảnh</b> — đo lúc ngôi sao mờ đi vì hành tinh che ngang. Âm thanh không truyền được trong chân không vũ trụ.",
            en: "Not quite! The common way is the <b>transit method</b> — measuring the dip in starlight as a planet crosses. Sound can't travel through the vacuum of space." },
      hint: { vi: "Nếu có ai đi ngang qua trước bóng đèn, ánh sáng sẽ <b>tối đi một chút</b>.",
              en: "When someone walks in front of a lamp, the light <b>dips a little</b>." },
      src: S.exo
    },


    /* ═════════ 11. LỖ ĐEN — Black Hole ═════════ */
    {
      term: "black-hole",
      topic: { vi: "LỖ ĐEN", en: "BLACK HOLE" },
      q: { vi: "Đường biên của lỗ đen — nơi không gì thoát ra được nữa — gọi là gì?",
           en: "What is the boundary of a black hole, beyond which nothing can escape, called?" },
      opts: [
        { vi: "Vành đai Kuiper", en: "The Kuiper Belt" },
        { vi: "Chân trời sự kiện", en: "The event horizon" },
        { vi: "Ranh giới ngày/đêm", en: "The day–night terminator" },
        { vi: "Quầng khí quyển", en: "The atmospheric halo" }
      ],
      a: 1,
      ok: { vi: "Chính xác! NASA gọi đường biên đó là <b>chân trời sự kiện</b>. Nó <b>không phải một mặt đất</b> — đó là đường biên chứa toàn bộ vật chất làm nên lỗ đen.",
            en: "Correct! NASA calls that boundary the <b>event horizon</b>. It is <b>not a surface</b> like Earth's — it is a boundary containing all the matter that makes up the black hole." },
      no: { vi: "Chưa đúng! Đường biên đó là <b>chân trời sự kiện</b>. Qua nó thì không gì thoát ra được, kể cả ánh sáng.",
            en: "Not quite! That boundary is the <b>event horizon</b>. Past it, nothing escapes — not even light." },
      hint: { vi: "Nó nghe như một <b>đường chân trời</b>: qua khỏi vạch đó là không quay lại được.",
              en: "It sounds like a <b>horizon</b>: cross that line and there is no coming back." },
      src: S.bh
    },
    {
      term: "black-hole-light",
      topic: { vi: "LỖ ĐEN", en: "BLACK HOLE" },
      q: { vi: "Thứ gì có thể thoát ra từ bên trong chân trời sự kiện của lỗ đen?",
           en: "What can escape from inside a black hole's event horizon?" },
      opts: [
        { vi: "Ánh sáng thì thoát được, vật chất thì không", en: "Light can escape, but matter cannot" },
        { vi: "Sóng vô tuyến thì thoát được", en: "Radio waves can escape" },
        { vi: "Vật gì đi đủ nhanh cũng thoát được", en: "Anything moving fast enough can escape" },
        { vi: "Không gì cả — kể cả ánh sáng", en: "Nothing at all — not even light" }
      ],
      a: 3,
      ok: { vi: "Đúng rồi! Lỗ đen đặc tới mức lực hấp dẫn ngay dưới chân trời sự kiện mạnh đến mức <b>không gì thoát ra được, kể cả ánh sáng</b>. Vì thế ta không thể nhìn thấy phần bên trong.",
            en: "Right! A black hole is so dense that gravity just beneath the event horizon is strong enough that <b>nothing can escape — not even light</b>. That's why we cannot see inside." },
      no: { vi: "Chưa đúng! <b>Không gì</b> thoát ra được, và ánh sáng cũng vậy — đó chính là lý do nó “đen”.",
            en: "Not quite! <b>Nothing</b> escapes, light included — that is exactly why it looks black." },
      hint: { vi: "Nghĩ về cái tên: vì sao ta gọi nó là lỗ <b>đen</b>?",
              en: "Think about the name: why do we call it a <b>black</b> hole?" },
      src: S.bh
    },

    /* ═════════ 12. LỰC HẤP DẪN — Gravity ═════════ */
    {
      term: "gravity",
      topic: { vi: "LỰC HẤP DẪN", en: "GRAVITY" },
      q: { vi: "Lực hấp dẫn của một hành tinh kéo các vật về đâu?",
           en: "Where does a planet's gravity pull objects toward?" },
      opts: [
        { vi: "Về phía tâm của hành tinh", en: "Toward the centre of the planet" },
        { vi: "Về phía cực Bắc", en: "Toward the North Pole" },
        { vi: "Ra xa khỏi hành tinh", en: "Away from the planet" },
        { vi: "Về phía ngôi sao gần nhất", en: "Toward the nearest star" }
      ],
      a: 0,
      ok: { vi: "Chính xác! NASA định nghĩa lực hấp dẫn là lực mà một hành tinh dùng để kéo các vật <b>về phía tâm của nó</b>. Vì thế em nhảy lên rồi lại rơi xuống sân.",
            en: "Correct! NASA defines gravity as the force by which a planet draws objects <b>toward its centre</b>. That's why you land back on the ground when you jump." },
      no: { vi: "Chưa đúng! Lực hấp dẫn kéo mọi vật <b>về phía tâm</b> của hành tinh — không phải về một cực, cũng không đẩy ra ngoài.",
            en: "Not quite! Gravity pulls everything <b>toward the centre</b> of the planet — not toward a pole, and it never pushes away." },
      hint: { vi: "Ở Việt Nam hay ở Nam Mỹ, thả tay ra là đồ vật đều rơi <b>xuống</b> — “xuống” là về hướng nào?",
              en: "In Vietnam or in South America, a dropped object always falls <b>down</b> — which direction is “down”?" },
      src: S.grav
    },
    {
      term: "gravity-distance",
      topic: { vi: "LỰC HẤP DẪN", en: "GRAVITY" },
      q: { vi: "Theo NASA, lực hấp dẫn thay đổi thế nào khi hai vật ở xa nhau hơn?",
           en: "According to NASA, what happens to gravity as two objects get farther apart?" },
      opts: [
        { vi: "Mạnh lên", en: "It gets stronger" },
        { vi: "Không đổi", en: "It stays the same" },
        { vi: "Yếu đi", en: "It gets weaker" },
        { vi: "Đổi chiều thành lực đẩy", en: "It flips into a push" }
      ],
      a: 2,
      ok: { vi: "Đúng rồi! Hai điều quyết định lực hấp dẫn mạnh hay yếu: vật càng <b>nhiều khối lượng</b> thì lực càng lớn, và lực <b>yếu dần khi khoảng cách xa ra</b>.",
            en: "Right! Two things set how strong gravity is: objects with <b>more mass</b> have more gravity, and gravity <b>gets weaker with distance</b>." },
      no: { vi: "Chưa đúng! Càng xa thì lực hấp dẫn càng <b>yếu</b> — nó không bao giờ đổi thành lực đẩy.",
            en: "Not quite! The farther apart, the <b>weaker</b> gravity gets — and it never turns into a push." },
      hint: { vi: "Mặt Trời rất nặng, nhưng ở đây em không bị nó hút bay đi. Vì sao?",
              en: "The Sun is enormously massive, yet it doesn't yank you off the ground. Why not?" },
      src: S.grav
    },

    /* ═════════ 13. TINH VÂN — Nebula ═════════ */
    {
      term: "nebula",
      topic: { vi: "TINH VÂN", en: "NEBULA" },
      q: { vi: "Các ngôi sao được sinh ra ở đâu?",
           en: "Where are stars born?" },
      opts: [
        { vi: "Trong vành đai tiểu hành tinh", en: "In the asteroid belt" },
        { vi: "Trong những đám mây khí và bụi khổng lồ", en: "In large clouds of gas and dust" },
        { vi: "Trong lõi của một hành tinh", en: "Inside a planet's core" },
        { vi: "Trong đuôi của sao chổi", en: "In the tail of a comet" }
      ],
      a: 1,
      ok: { vi: "Chính xác! NASA cho biết các ngôi sao hình thành trong những <b>đám mây khí và bụi khổng lồ</b> gọi là mây phân tử. Mây đầy cụm sao mới sinh còn được gọi là “vườn trẻ của các ngôi sao”.",
            en: "Correct! NASA says stars form in <b>large clouds of gas and dust</b> called molecular clouds. Clouds full of newly formed clusters are called stellar nurseries." },
      no: { vi: "Chưa đúng! Ngôi sao sinh ra trong <b>đám mây khí và bụi</b>, không phải trong đá hay trong lõi hành tinh.",
            en: "Not quite! Stars are born in <b>clouds of gas and dust</b>, not in rock or inside planets." },
      hint: { vi: "Muốn nặn một quả cầu khí khổng lồ thì trước hết phải có… rất nhiều <b>khí</b>.",
              en: "To build a giant ball of gas, you first need a great deal of… <b>gas</b>." },
      src: S.star
    },
    {
      term: "nebula-gas",
      topic: { vi: "TINH VÂN", en: "NEBULA" },
      q: { vi: "Điều gì làm phần giữa một đám mây khí co lại và nóng lên đủ để một ngôi sao ra đời?",
           en: "What makes the middle of a gas cloud collapse and heat up until a star is born?" },
      opts: [
        { vi: "Gió Mặt Trời thổi mây lại", en: "The solar wind squeezing the cloud" },
        { vi: "Từ trường của thiên hà", en: "The galaxy's magnetic field" },
        { vi: "Va chạm với một tiểu hành tinh", en: "A collision with an asteroid" },
        { vi: "Lực hấp dẫn hút thêm vật chất về chỗ đặc", en: "Gravity pulling more matter into the dense clumps" }
      ],
      a: 3,
      ok: { vi: "Đúng rồi! Ở những chỗ mây đặc lại, <b>lực hấp dẫn hút thêm vật chất về</b>; phần giữa bị ép ngày càng chặt và nóng lên — đủ nóng để phản ứng nhiệt hạch khởi động, và một ngôi sao ra đời.",
            en: "Right! Where the cloud grows denser, <b>gravity attracts additional matter</b>; the middle is squeezed ever tighter and heats up — hot enough for nuclear fusion to start, and a star is born." },
      no: { vi: "Chưa đúng! Chính <b>lực hấp dẫn</b> làm chỗ đặc co lại và nóng lên, chứ không phải gió hay va chạm.",
            en: "Not quite! It is <b>gravity</b> that makes the dense clumps collapse and heat up — not wind or collisions." },
      hint: { vi: "Cùng một lực giữ em không bay khỏi mặt đất, nhưng ở đây nó bóp cả một đám mây.",
              en: "The same force that keeps you on the ground — here it squeezes an entire cloud." },
      src: S.star
    },

    /* ═════════ 14. SIÊU TÂN TINH — Supernova ═════════ */
    {
      term: "supernova",
      topic: { vi: "SIÊU TÂN TINH", en: "SUPERNOVA" },
      q: { vi: "Siêu tân tinh xảy ra khi nào?",
           en: "When does a supernova happen?" },
      opts: [
        { vi: "Khi hai hành tinh đâm vào nhau", en: "When two planets crash into each other" },
        { vi: "Khi một sao chổi lao vào Mặt Trời", en: "When a comet dives into the Sun" },
        { vi: "Khi một ngôi sao khối lượng lớn cạn nhiên liệu và lõi sụp xuống", en: "When a massive star runs out of fuel and its core collapses" },
        { vi: "Mỗi lần một ngôi sao mọc lên ở chân trời", en: "Every time a star rises over the horizon" }
      ],
      a: 2,
      ok: { vi: "Chính xác! Ngôi sao khối lượng lớn cạn nhiên liệu thì <b>lõi sắt sụp xuống</b> cho tới lúc lực giữa các hạt nhân “đạp phanh”, rồi <b>nảy trở lại</b> — cú nảy đó tạo sóng xung kích và một vụ nổ khổng lồ.",
            en: "Correct! When a high-mass star runs out of fuel its <b>iron core collapses</b> until forces between the nuclei push the brakes, then it <b>rebounds</b> — creating a shock wave and a huge explosion." },
      no: { vi: "Chưa đúng! Siêu tân tinh là lúc một <b>ngôi sao rất lớn</b> kết thúc cuộc đời, không phải chuyện hành tinh hay sao chổi.",
            en: "Not quite! A supernova is how a <b>very massive star</b> ends its life — not a planet or comet event." },
      hint: { vi: "Nó là <b>cái chết</b> của một ngôi sao rất lớn, không phải một vụ đâm nhau.",
              en: "It is the <b>death</b> of a very massive star, not a crash." },
      src: S.star
    },
    {
      term: "supernova-elements",
      topic: { vi: "SIÊU TÂN TINH", en: "SUPERNOVA" },
      q: { vi: "Vật chất bị siêu tân tinh bắn vào không gian sẽ đi đâu?",
           en: "What happens to the material a supernova throws into space?" },
      opts: [
        { vi: "Làm giàu cho các mây phân tử, rồi thành thế hệ ngôi sao kế tiếp", en: "It enriches molecular clouds and becomes the next generation of stars" },
        { vi: "Biến mất hoàn toàn khỏi vũ trụ", en: "It vanishes from the universe completely" },
        { vi: "Rơi hết trở lại vào lỗ đen ngay lập tức", en: "It falls straight back into a black hole" },
        { vi: "Đông lại thành một hành tinh duy nhất", en: "It freezes into one single planet" }
      ],
      a: 0,
      ok: { vi: "Đúng rồi! NASA cho biết vật chất bị vụ nổ bắn ra sẽ <b>làm giàu cho các mây phân tử sau này</b>, rồi đi vào thành phần của <b>thế hệ ngôi sao kế tiếp</b>. Gạch của căn nhà cũ được dùng lại để xây nhà mới.",
            en: "Right! NASA says material cast into the cosmos <b>enriches future molecular clouds</b> and becomes part of the <b>next generation of stars</b>. The old bricks get reused to build new houses." },
      no: { vi: "Chưa đúng! Vật chất không mất đi — nó <b>làm giàu cho mây phân tử</b> và trở thành nguyên liệu của các ngôi sao sinh sau.",
            en: "Not quite! The material isn't lost — it <b>enriches molecular clouds</b> and becomes raw material for later stars." },
      hint: { vi: "Nhớ lại câu hỏi về tinh vân: ngôi sao được sinh ra từ <b>mây khí và bụi</b>.",
              en: "Recall the nebula question: stars are born from <b>clouds of gas and dust</b>." },
      src: S.star
    },

    /* ═════════ 15. BỨC XẠ NỀN VŨ TRỤ — Cosmic Microwave Background ═════════ */
    {
      term: "cmb",
      topic: { vi: "BỨC XẠ NỀN VŨ TRỤ", en: "COSMIC MICROWAVE BACKGROUND" },
      q: { vi: "Bức xạ nền vũ trụ là gì?",
           en: "What is the cosmic microwave background?" },
      opts: [
        { vi: "Ánh sáng của ngôi sao gần Trái Đất nhất", en: "Light from the star nearest to Earth" },
        { vi: "Ánh sáng CỔ NHẤT mà ta quan sát được", en: "The OLDEST light we can observe" },
        { vi: "Sóng vô tuyến do các kính thiên văn phát ra", en: "Radio waves sent out by telescopes" },
        { vi: "Ánh sáng phản chiếu từ bụi trong Ngân Hà", en: "Light reflected off dust in the Milky Way" }
      ],
      a: 1,
      ok: { vi: "Chính xác! NASA gọi nó là <b>ánh sáng cổ nhất ta quan sát được</b> — vẫn còn đo được tới hôm nay. Bản đồ của nó cho thấy những chênh lệch nhiệt độ <b>13,8 tỉ năm tuổi</b>, chính là mầm mống lớn dần thành các thiên hà.",
            en: "Correct! NASA calls it the <b>oldest light we can observe</b> — still detectable today. Its map shows <b>13.8-billion-year-old</b> temperature fluctuations: the seeds that grew into galaxies." },
      no: { vi: "Chưa đúng! Đó là <b>ánh sáng cổ nhất</b> ta quan sát được, còn lại từ thuở vũ trụ sơ sinh — không phải ánh sáng của một ngôi sao nào.",
            en: "Not quite! It is the <b>oldest light</b> we can observe, left over from the infant universe — not light from any one star." },
      hint: { vi: "Hãy nghĩ nó như <b>tấm ảnh sơ sinh</b> của cả vũ trụ.",
              en: "Think of it as the universe's <b>newborn photo</b>." },
      src: S.cosmos
    },
    {
      term: "cmb-when",
      topic: { vi: "BỨC XẠ NỀN VŨ TRỤ", en: "COSMIC MICROWAVE BACKGROUND" },
      q: { vi: "Ánh sáng của bức xạ nền được phát ra vào khoảng bao lâu sau Big Bang?",
           en: "Roughly how long after the big bang was the background light released?" },
      opts: [
        { vi: "Khoảng 1 giây sau", en: "About 1 second after" },
        { vi: "Khoảng 1 triệu tỉ năm sau", en: "About a quadrillion years after" },
        { vi: "Đúng vào lúc Big Bang xảy ra", en: "At the very instant of the big bang" },
        { vi: "Khoảng 380.000 năm sau", en: "About 380,000 years after" }
      ],
      a: 3,
      ok: { vi: "Đúng rồi! Khoảng <b>380.000 năm</b> sau Big Bang, vũ trụ nguội đủ để các hạt nhân bắt được electron — giai đoạn gọi là <b>kỷ nguyên tái kết hợp</b>. Ánh sáng phát ra khi đó chính là bức xạ nền.",
            en: "Right! About <b>380,000 years</b> after the big bang the universe cooled enough for nuclei to capture electrons — the <b>epoch of recombination</b>. The light released then is the background radiation." },
      no: { vi: "Chưa đúng! Con số NASA ghi là khoảng <b>380.000 năm</b> sau Big Bang.",
            en: "Not quite! The figure NASA gives is about <b>380,000 years</b> after the big bang." },
      hint: { vi: "Không phải ngay lập tức, cũng không phải hàng tỉ năm — mà là <b>vài trăm nghìn</b> năm.",
              en: "Not instantly, and not billions of years — a few <b>hundred thousand</b> years." },
      src: S.cosmos
    },

    /* ═════════ 16. Bộ câu hỏi lập trình / robot (bài học, không phải số liệu) ═════════ */
    {
      term: "algorithm",
      topic: { vi: "TRÍ TUỆ NHÂN TẠO", en: "ARTIFICIAL INTELLIGENCE" },
      q: { vi: "Thuật toán nào giúp Byte rẽ trái để né thiên thạch?", en: "Which command turns Byte left to dodge the asteroid?" },
      opts: [{ vi: "MoveForward()", en: "MoveForward()" }, { vi: "TurnLeft()", en: "TurnLeft()" }, { vi: "Jump()", en: "Jump()" }, { vi: "Stop()", en: "Stop()" }],
      a: 1,
      ok: { vi: "Chính xác! Thuật toán <b>TurnLeft()</b> giúp Byte đổi hướng sang trái!", en: "Correct! <b>TurnLeft()</b> steers Byte to the left!" },
      no: { vi: "Rất tiếc! <b>MoveForward()</b> sẽ làm Byte đâm thẳng vào thiên thạch đấy. Hãy thử lại!", en: "Oops! <b>MoveForward()</b> would crash Byte into the asteroid. Try again!" },
      hint: { vi: "Suy nghĩ kỹ nhé! Thuật toán nào giúp tớ <b>rẽ trái</b>?", en: "Think carefully! Which command turns me <b>left</b>?" }
    },
    {
      term: "loop",
      topic: { vi: "VÒNG LẶP", en: "LOOPS" },
      q: { vi: "Byte cần nhặt 3 tinh thể giống nhau. Nên dùng cấu trúc nào?", en: "Byte must collect 3 identical crystals. Which structure fits best?" },
      opts: [{ vi: "Repeat / Vòng lặp", en: "Repeat / Loop" }, { vi: "If / Nếu", en: "If" }, { vi: "Print / In ra", en: "Print" }, { vi: "Delete / Xoá", en: "Delete" }],
      a: 0,
      ok: { vi: "Tuyệt! <b>Vòng lặp Repeat</b> giúp lặp lại một việc nhiều lần mà không viết lại lệnh.", en: "Great! A <b>Repeat loop</b> runs the same action many times without rewriting it." },
      no: { vi: "Chưa đúng! Để làm lặp lại một việc, ta dùng <b>vòng lặp</b> chứ không phải lệnh này.", en: "Not quite! To repeat an action, use a <b>loop</b>, not this command." },
      hint: { vi: "Làm đi làm lại cùng một việc — cấu trúc nào hợp nhất nhỉ?", en: "Doing the same thing over and over — which structure fits?" }
    },
    {
      term: "condition",
      topic: { vi: "ĐIỀU KIỆN", en: "CONDITIONS" },
      q: { vi: "“NẾU phía trước có thiên thạch THÌ dừng lại.” Đây là loại lệnh gì?", en: "“IF an asteroid is ahead THEN stop.” What kind of command is this?" },
      opts: [{ vi: "Lệnh điều kiện (If)", en: "Condition (If)" }, { vi: "Vòng lặp", en: "Loop" }, { vi: "Biến số", en: "Variable" }, { vi: "Hàm vẽ", en: "Draw function" }],
      a: 0,
      ok: { vi: "Đúng rồi! <b>Lệnh điều kiện If</b> giúp Byte quyết định dựa trên tình huống.", en: "Right! An <b>If condition</b> lets Byte decide based on the situation." },
      no: { vi: "Chưa đúng! “Nếu… thì…” chính là <b>lệnh điều kiện (If)</b>.", en: "Not quite! “If… then…” is exactly an <b>If condition</b>." },
      hint: { vi: "“Nếu… thì…” — nghe giống loại lệnh nào?", en: "“If… then…” — which command does that sound like?" }
    },
    {
      term: "sensor",
      topic: { vi: "CẢM BIẾN", en: "SENSORS" },
      q: { vi: "Byte dùng bộ phận nào để “nhìn thấy” thiên thạch phía trước?", en: "Which part does Byte use to 'see' the asteroid ahead?" },
      opts: [{ vi: "Bánh xe", en: "Wheels" }, { vi: "Pin năng lượng", en: "Battery" }, { vi: "Cảm biến (Sensor)", en: "Sensor" }, { vi: "Loa phát", en: "Speaker" }],
      a: 2,
      ok: { vi: "Chuẩn! <b>Cảm biến</b> giúp robot thu thập thông tin về môi trường xung quanh.", en: "Exactly! A <b>sensor</b> lets a robot gather information about its surroundings." },
      no: { vi: "Chưa đúng! Robot “nhìn” bằng <b>cảm biến</b>, không phải bộ phận này.", en: "Not quite! A robot 'sees' with a <b>sensor</b>, not this part." },
      hint: { vi: "Bộ phận nào giúp robot <b>thu thập thông tin</b> xung quanh?", en: "Which part helps a robot <b>gather info</b> around it?" }
    },
    {
      term: "sequence",
      topic: { vi: "TRÌNH TỰ", en: "SEQUENCING" },
      q: { vi: "Để tới đích: tiến 2 ô rồi rẽ phải. Trình tự lệnh đúng là?", en: "To reach the goal: go 2 tiles then turn right. Correct order?" },
      opts: [{ vi: "MoveForward(2) → TurnRight()", en: "MoveForward(2) → TurnRight()" }, { vi: "TurnRight() → MoveForward(2)", en: "TurnRight() → MoveForward(2)" }, { vi: "TurnRight() → TurnLeft()", en: "TurnRight() → TurnLeft()" }, { vi: "Stop() → MoveForward(2)", en: "Stop() → MoveForward(2)" }],
      a: 0,
      ok: { vi: "Hoàn hảo! Máy tính chạy lệnh <b>theo thứ tự từ trên xuống</b> — tiến trước, rẽ sau.", en: "Perfect! Computers run commands <b>in order, top to bottom</b> — move first, then turn." },
      no: { vi: "Chưa đúng! Đề yêu cầu <b>tiến trước, rẽ phải sau</b> — đúng thứ tự nhé.", en: "Not quite! It says <b>move first, then turn right</b> — order matters." },
      hint: { vi: "Thứ tự rất quan trọng: việc nào làm <b>trước</b>?", en: "Order matters: which step comes <b>first</b>?" }
    }
  ];

  /* Trộn một BẢN SAO — trộn tại chỗ thì lượt sau thứ tự ALL đã bị đổi, và mọi
     phép kiểm dựa vào thứ tự khai báo sẽ hỏng một cách khó hiểu. */
  function shuffled(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var r = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[r]; a[r] = t;
    }
    return a;
  }

  /* Chọn n câu cho một lượt. ƯU TIÊN KHÔNG TRÙNG `term` — bank có 2 câu cho mỗi
     thuật ngữ, không lọc thì một lượt 5 câu có thể hỏi Sao chổi hai lần trong khi
     bỏ qua 9 thuật ngữ khác. Hết term mới thì mới lấy bù từ phần còn lại. */
  function pickRound(n, bank) {
    var pool = shuffled(bank || ALL);
    var seen = {}, out = [], rest = [], i;
    for (i = 0; i < pool.length && out.length < n; i++) {
      var k = pool[i].term;
      if (seen[k]) { rest.push(pool[i]); continue; }
      seen[k] = 1; out.push(pool[i]);
    }
    for (i = 0; i < pool.length && out.length < n; i++) {
      if (out.indexOf(pool[i]) < 0) out.push(pool[i]);
    }
    for (i = 0; out.length < n && i < rest.length; i++) out.push(rest[i]);
    return out;
  }

  /* Lọc theo thuật ngữ — để trang khác mở đúng bộ câu hỏi của một bài đọc. */
  function byTerms(terms) {
    return ALL.filter(function (it) { return terms.indexOf(it.term) >= 0; });
  }

  return { ALL: ALL, pickRound: pickRound, byTerms: byTerms, shuffled: shuffled };
})();
