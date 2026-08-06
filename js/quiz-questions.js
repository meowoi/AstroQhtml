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

  /* ── Nguon cua ĐỢT 1 · 06/08/2026. Ca 20 URL da kiem tra 200 va nam trong
     `OK_HOSTS` cua scratchpad/check_quiz_bank.py — xem khoi ly do tung
     ten mien o do TRUOC khi them ten mien moi. */
  S.nasaEarthFacts        = { name: "NASA Science — Facts About Earth",              url: "https://science.nasa.gov/earth/facts/" };
  S.nasaGeneralAtmosphere = { name: "NASA Science — What Is Earth's Atmosphere?",    url: "https://www.nasa.gov/general/what-is-earths-atmosphere/" };
  S.nasaSpaceplaceTropo   = { name: "NASA Space Place — Troposphere",               url: "https://spaceplace.nasa.gov/troposphere/" };
  S.nasaSpaceplaceStrato  = { name: "NASA Space Place — Stratosphere",              url: "https://spaceplace.nasa.gov/stratosphere/" };
  S.nasaSpaceplaceMeso    = { name: "NASA Space Place — Mesosphere",                url: "https://spaceplace.nasa.gov/mesosphere/" };
  S.ucarTroposphere       = { name: "UCAR — The Troposphere",                       url: "https://scied.ucar.edu/learning-zone/atmosphere/troposphere" };
  S.ucarStratosphere      = { name: "UCAR — The Stratosphere",                      url: "https://scied.ucar.edu/learning-zone/atmosphere/stratosphere" };
  S.ucarOzoneLayer        = { name: "UCAR — The Ozone Layer",                       url: "https://scied.ucar.edu/learning-zone/atmosphere/ozone-layer" };

  S.nasaStarTypes         = { name: "NASA Science — Star Types",                    url: "https://science.nasa.gov/universe/stars/types/" };
  S.lcoStarColors         = { name: "Las Cumbres Observatory — Magnitude and Color", url: "https://lco.global/spacebook/distance/magnitude-and-color/" };
  S.nasaSpaceplaceMagic   = { name: "NASA Space Place — Explore the Electromagnetic Spectrum", url: "https://spaceplace.nasa.gov/magic-windows/" };

  S.nasaEclipseTypes      = { name: "NASA Science — Types of Solar Eclipses",        url: "https://science.nasa.gov/eclipses/types/" };
  S.nasaEclipseGeometry   = { name: "NASA Science — Why Do Eclipses Happen?",        url: "https://science.nasa.gov/eclipses/geometry/" };
  S.nasaEclipseSafety     = { name: "NASA Science — Eclipse Viewing Safety",         url: "https://science.nasa.gov/eclipses/safety/" };
  S.nasaEclipsesMain      = { name: "NASA Science — Eclipses Overview",              url: "https://science.nasa.gov/eclipses/" };
  S.nasaSunCorona         = { name: "NASA Space Place — What Is the Sun's Corona?",  url: "https://spaceplace.nasa.gov/sun-corona/en/" };
  S.exploratoriumEclipse  = { name: "Exploratorium — What Causes a Solar Eclipse?",  url: "https://www.exploratorium.edu/eclipse/what-is-a-solar-eclipse" };

  S.nasaMoonEclipses      = { name: "NASA Science — Eclipses and the Moon",          url: "https://science.nasa.gov/moon/eclipses/" };
  S.nasaSpaceplaceEclipses= { name: "NASA Space Place — Lunar and Solar Eclipses",   url: "https://spaceplace.nasa.gov/eclipses/" };
  S.exploratoriumCup      = { name: "Exploratorium — Eclipse in a Cup",              url: "https://www.exploratorium.edu/eclipse/snacks/eclipse-in-a-cup" };



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
    },

    /* ═══════ ĐỢT 1 · 06/08/2026 · 65 cau cho 4 the moi ═══════
       Moi `srcQuote` da doi chieu NGUYEN VAN voi trang nguon —
       `python scratchpad/check_dot1.py` muc [7], 65/65 dat.
       4 the tuong ung o `js/codex-terms.js`, 4 icon o `js/icons.js`. */
    {
    term: "atmo-comp-nitrogen",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Khí nào chiếm tỉ lệ thể tích lớn nhất trong bầu khí quyển Trái Đất?",
         en: "Which gas makes up the largest volume percentage of Earth's atmosphere?" },
    opts: [
      { vi: "Khí Oxy", en: "Oxygen" },
      { vi: "Khí Nitơ", en: "Nitrogen" },
      { vi: "Khí Carbon dioxide", en: "Carbon dioxide" },
      { vi: "Khí Argon", en: "Argon" }
    ],
    a: 1,
    ok: { vi: "Chính xác! Khí Nitơ chiếm 78% thể tích không khí Trái Đất.",
          en: "Correct! Nitrogen gas makes up 78% of Earth's atmosphere by volume." },
    no: { vi: "Chưa đúng. Tuy con người cần thở oxy, nhưng khí Nitơ mới chiếm tỉ lệ lớn nhất (78%).",
          en: "Incorrect. Though humans breathe oxygen, nitrogen is the most abundant gas (78%)." },
    hint: { vi: "Khí này chiếm tới hơn 3/4 thể tích bầu khí quyển.",
            en: "This gas accounts for more than three-quarters of the atmosphere." },
    src: S.nasaEarthFacts,
    srcQuote: "Earth's atmosphere is 78% nitrogen, 21% oxygen and 1% other ingredients.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-comp-ratio",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Tỉ lệ thành phần không khí của bầu khí quyển Trái Đất gồm những gì?",
         en: "What is the exact composition breakdown of Earth's atmosphere?" },
    opts: [
      { vi: "78% nitơ, 21% oxy và 1% các thành phần khác", en: "78% nitrogen, 21% oxygen and 1% other ingredients" },
      { vi: "78% oxy, 21% nitơ và 1% các khí khác", en: "78% oxygen, 21% nitrogen and 1% other ingredients" },
      { vi: "50% oxy, 50% nitơ", en: "50% oxygen, 50% nitrogen" },
      { vi: "99% carbon dioxide và 1% oxy", en: "99% carbon dioxide and 1% oxygen" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Khí quyển Trái Đất gồm 78% nitơ, 21% oxy và 1% các khí vết.",
          en: "Correct! Earth's atmosphere consists of 78% nitrogen, 21% oxygen and 1% trace gases." },
    no: { vi: "Chưa đúng. Nhiều người hay nhầm oxy chiếm 78%, nhưng thực tế Nitơ mới chiếm 78% và Oxy chiếm 21%.",
          en: "Incorrect. Many confuse the ratio: Nitrogen is actually 78% and Oxygen is 21%." },
    hint: { vi: "Nitơ luôn chiếm tỉ lệ áp đảo lớn hơn Oxy.",
            en: "Nitrogen always holds a far larger majority than oxygen." },
    src: S.nasaEarthFacts,
    srcQuote: "Earth's atmosphere is 78% nitrogen, 21% oxygen and 1% other ingredients.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-tropo-lowest",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Tầng khí quyển nào thấp nhất, tiếp giáp trực tiếp với bề mặt Trái Đất?",
         en: "Which layer of the atmosphere is the lowest, right next to Earth's surface?" },
    opts: [
      { vi: "Tầng bình lưu", en: "Stratosphere" },
      { vi: "Tầng đối lưu (Troposphere)", en: "Troposphere" },
      { vi: "Tầng trung lưu", en: "Mesosphere" },
      { vi: "Tầng nhiệt", en: "Thermosphere" }
    ],
    a: 1,
    ok: { vi: "Chính xác! Tầng đối lưu (Troposphere) là tầng khí quyển thấp nhất sát mặt đất.",
          en: "Correct! The troposphere is the lowest atmospheric layer nearest the ground." },
    no: { vi: "Chưa đúng. Tầng đối lưu (Troposphere) mới là tầng thấp nhất nơi con người sinh sống.",
          en: "Incorrect. The troposphere is the lowest layer where humans live." },
    hint: { vi: "Đây là tầng khí quyển nơi các đám mây hình thành.",
            en: "This is the atmospheric layer where clouds form." },
    src: S.ucarTroposphere,
    srcQuote: "The troposphere is the lowest layer of Earth's atmosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-tropo-weather",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Tầng đối lưu (Troposphere) có đặc điểm nổi bật gì về hiện tượng tự nhiên?",
         en: "What prominent natural phenomenon occurs constantly in the troposphere?" },
    opts: [
      { vi: "Thời tiết liên tục thay đổi và xáo động không khí", en: "Weather that is constantly changing and mixing up gases" },
      { vi: "Hoàn toàn không có mây hay gió", en: "Complete absence of clouds and wind" },
      { vi: "Không khí đứng yên không di chuyển", en: "Air stands completely still" },
      { vi: "Chỉ có tuyết rơi quanh năm", en: "Snow falls constantly year-round" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tên gọi Troposphere bắt nguồn từ đặc tính thời tiết luôn xáo động và thay đổi.",
          en: "Correct! The name troposphere comes from weather constantly changing and mixing." },
    no: { vi: "Chưa đúng. Tầng đối lưu là nơi các hiện tượng thời tiết như mây, mưa, gió diễn ra liên tục.",
          en: "Incorrect. The troposphere is where weather events like rain and wind occur constantly." },
    hint: { vi: "Từ 'Tropos' có nghĩa là sự thay đổi, xáo trộn.",
            en: "The word 'Tropos' relates to change and mixing." },
    src: S.nasaSpaceplaceTropo,
    srcQuote: "This layer gets its name from the weather that is constantly changing and mixing up the gases in this part of our atmosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-tropo-mass",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Tầng đối lưu chứa khoảng bao nhiêu phần khối lượng của toàn bộ bầu khí quyển?",
         en: "About how much of the total atmospheric mass is contained in the troposphere?" },
    opts: [
      { vi: "Chỉ 10% khối lượng", en: "Only 10% of mass" },
      { vi: "Một nửa (50%) khối lượng", en: "Half (50%) of mass" },
      { vi: "Ba phần tư (75%) khối lượng", en: "Three-quarters (75%) of mass" },
      { vi: "100% khối lượng", en: "100% of mass" }
    ],
    a: 2,
    ok: { vi: "Chính xác! Tầng đối lưu chứa khoảng 3/4 (75%) tổng khối lượng khí quyển Trái Đất.",
          en: "Correct! The troposphere holds roughly three-quarters (75%) of total atmospheric mass." },
    no: { vi: "Chưa đúng. Nhiều người nghĩ không khí chia đều, nhưng trọng lực làm 3/4 khối lượng khí tập trung ở tầng đối lưu.",
          en: "Incorrect. Gravity concentrates roughly three-quarters of atmospheric mass in the troposphere." },
    hint: { vi: "Trọng lực hút hầu hết phân tử khí về gần bề mặt Trái Đất.",
            en: "Gravity pulls most air molecules close to Earth's surface." },
    src: S.nasaSpaceplaceTropo,
    srcQuote: "In fact, the troposphere contains three-quarters of the mass of the entire atmosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-tropo-watervapor",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Tại sao các hiện tượng thời tiết như mây, mưa, tuyết lại diễn ra chủ yếu ở tầng đối lưu mà không có ở các tầng cao hơn?",
         en: "Why do weather events like clouds and rain occur almost entirely in the troposphere?" },
    opts: [
      { vi: "Vì đây là nơi tập trung phần lớn khối lượng khí quyển, bao gồm hầu hết lượng hơi nước", en: "Because it is where much of the atmospheric mass, including most of the water vapor, is found" },
      { vi: "Vì các tầng cao hơn gần Mặt Trời hơn nên hơi nước bị bốc cháy hết", en: "Because higher layers are closer to the Sun so water vapor burns away" },
      { vi: "Vì khí ôzôn ở tầng bình lưu đẩy tất cả các đám mây xuống dưới", en: "Because ozone in the stratosphere pushes all clouds downward" },
      { vi: "Vì nhiệt độ ở tầng bình lưu luôn cố định ở 0°C", en: "Because stratosphere temperature is fixed at 0°C" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Thời tiết diễn ra ở tầng đối lưu vì tầng này tập trung phần lớn khối lượng không khí và hầu hết hơi nước.",
          en: "Correct! Weather occurs in the troposphere because it contains much of the atmospheric mass and most water vapor." },
    no: { vi: "Chưa đúng. Tầng đối lưu chứa phần lớn khối lượng không khí và hầu hết hơi nước, nên mây mưa chỉ hình thành ở tầng này.",
          en: "Incorrect. The troposphere contains much of the air mass and most water vapor, so weather forms here." },
    hint: { vi: "Hơi nước là nguyên liệu cốt lõi để tạo nên mây và mưa.",
            en: "Water vapor is the core ingredient needed to form clouds and rain." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "Earth's weather occurs in this layer, as it is where much of the atmospheric mass, including most of the water vapor, is found.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-tropo-density",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 3,
    q: { vi: "Mật độ không khí có đặc điểm gì ở tầng thấp nhất (tầng đối lưu)?",
         en: "What is the characteristic of air density in the lowest layer (troposphere)?" },
    opts: [
      { vi: "Không khí đặc nhất ở tầng thấp nhất này", en: "The air is densest in this lowest layer" },
      { vi: "Không khí loãng nhất so với tất cả các tầng", en: "Air is thinner than all other layers" },
      { vi: "Hoàn toàn không có không khí", en: "Complete absence of air" },
      { vi: "Mật độ không khí biến đổi ngẫu nhiên mỗi giây", en: "Density changes randomly every second" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Do lực hấp dẫn hút khí về bề mặt, không khí đặc nhất ở tầng đối lưu.",
          en: "Correct! Gravity pulls air molecules down, making air densest in the troposphere." },
    no: { vi: "Chưa đúng. Càng lên cao không khí càng loãng; không khí đặc nhất chính là ở tầng đối lưu sát mặt đất.",
          en: "Incorrect. Air gets thinner as you go up; air is densest in the lowest troposphere layer." },
    hint: { vi: "Trọng lực hút hầu hết phân tử không khí dồn xuống sát bề mặt Trái Đất.",
            en: "Gravity pulls most air molecules down towards Earth's surface." },
    src: S.nasaSpaceplaceTropo,
    srcQuote: "The air is densest in this lowest layer.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-strato-ozone",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Lớp ôzôn (Ozone layer) bảo vệ sự sống nằm ở tầng khí quyển nào?",
         en: "In which atmospheric layer will you find the vital ozone layer?" },
    opts: [
      { vi: "Tầng bình lưu (Stratosphere)", en: "Stratosphere" },
      { vi: "Tầng đối lưu", en: "Troposphere" },
      { vi: "Tầng trung lưu", en: "Mesosphere" },
      { vi: "Tầng ngoại lưu", en: "Exosphere" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Lớp ôzôn tập trung ở tầng bình lưu (Stratosphere).",
          en: "Correct! The protective ozone layer resides in the stratosphere." },
    no: { vi: "Chưa đúng. Nhiều người nghĩ ôzôn ở sát mặt đất, nhưng lớp ôzôn bảo vệ thực sự nằm ở tầng bình lưu.",
          en: "Incorrect. While surface ozone is a pollutant, the protective ozone layer is in the stratosphere." },
    hint: { vi: "Đây là tầng khí quyển ngay phía trên tầng đối lưu.",
            en: "This is the atmospheric layer directly above the troposphere." },
    src: S.nasaSpaceplaceStrato,
    srcQuote: "The stratosphere is where you'll find the very important ozone layer.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-strato-uv",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Lớp ôzôn ở tầng bình lưu bảo vệ con người và sinh vật khỏi tác hại của yếu tố nào?",
         en: "What does the ozone layer in the stratosphere protect living things from?" },
    opts: [
      { vi: "Bức xạ cực tím (UV) từ Mặt Trời", en: "Ultraviolet radiation (UV) from the sun" },
      { vi: "Ánh sáng nhìn thấy ban ngày", en: "Visible daylight" },
      { vi: "Tất cả các loại mây mưa", en: "All rain clouds" },
      { vi: "Gió và không khí lạnh", en: "Wind and cold air" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Lớp ôzôn giúp hấp thụ hầu hết tia cực tím (UV) có hại từ Mặt Trời.",
          en: "Correct! The ozone layer protects us by absorbing harmful UV radiation from the sun." },
    no: { vi: "Chưa đúng. Lớp ôzôn cản trở bức xạ cực tím (UV) chứ không cản ánh sáng nhìn thấy.",
          en: "Incorrect. The ozone layer blocks harmful UV radiation, not visible light." },
    hint: { vi: "Đây là loại tia bức xạ gây bỏng da và tổn thương mắt nếu không có ôzôn bảo vệ.",
            en: "This radiation type causes sunburns and eye damage without ozone shielding." },
    src: S.nasaSpaceplaceStrato,
    srcQuote: "The ozone layer helps protect us from ultraviolet radiation (UV) from the sun.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-strato-location",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 3,
    q: { vi: "Tầng bình lưu (Stratosphere) là tầng thứ mấy của bầu khí quyển khi đi từ dưới mặt đất lên?",
         en: "Which layer is the stratosphere as you go upward from ground level?" },
    opts: [
      { vi: "Là tầng thứ hai (nằm trên tầng đối lưu)", en: "Second layer as you go upward" },
      { vi: "Là tầng đầu tiên sát mặt đất", en: "First layer closest to ground" },
      { vi: "Là tầng cao nhất tiếp giáp vũ trụ", en: "Highest layer touching space" },
      { vi: "Là tầng ranh giới ngoài cùng", en: "Outermost boundary layer" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tầng bình lưu là tầng thứ hai tính từ mặt đất lên, nằm ngay trên tầng đối lưu.",
          en: "Correct! The stratosphere is the second layer going upward, sitting above troposphere." },
    no: { vi: "Chưa đúng. Tầng đối lưu mới là tầng thứ nhất; tầng bình lưu là tầng thứ hai tính từ mặt đất lên.",
          en: "Incorrect. The troposphere is the first layer; the stratosphere is the second layer going up." },
    hint: { vi: "Tầng này nằm ngay phía trên tầng đối lưu nơi có mây mưa.",
            en: "This layer sits directly above the troposphere where rain clouds form." },
    src: S.ucarStratosphere,
    srcQuote: "The stratosphere is a layer of Earth's atmosphere. It is the second layer of the atmosphere as you go upward.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-meso-location",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    /* ⚠️ Lựa chọn sai thứ 2 đã đổi 06/08/2026: "Nằm sát bên trong lòng đại dương" (nhảm)
       → "Nằm ngay dưới tầng đối lưu sát mực nước biển" (hiểu lầm CÓ THẬT về thứ tự tầng). */
    q: { vi: "Tầng trung lưu (Mesosphere) nằm ở vị trí nào trong cấu trúc khí quyển?",
         en: "Where is the mesosphere located within Earth's atmospheric structure?" },
    opts: [
      { vi: "Nằm giữa tầng bình lưu và tầng nhiệt", en: "Middle layer between the stratosphere and the thermosphere" },
      { vi: "Nằm ngay dưới tầng đối lưu sát mực nước biển", en: "Located directly below the troposphere at sea level" },
      { vi: "Nằm ngoài cùng ranh giới vũ trụ", en: "Outermost boundary in space" },
      { vi: "Nằm bên trong lớp ôzôn", en: "Inside the ozone layer" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tầng trung lưu nằm ở giữa tầng bình lưu và tầng nhiệt.",
          en: "Correct! The mesosphere is the middle layer between stratosphere and thermosphere." },
    no: { vi: "Chưa đúng. Từ 'Meso' có nghĩa là ở giữa: tầng trung lưu nằm giữa tầng bình lưu và tầng nhiệt.",
          en: "Incorrect. 'Meso' means middle: the mesosphere is between stratosphere and thermosphere." },
    hint: { vi: "Tên gọi 'Meso' có nguồn gốc từ từ có nghĩa là ở giữa.",
            en: "The name 'Meso' originates from a word meaning middle." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "The mesosphere is the middle layer between the stratosphere and the thermosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-meso-meteors",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Các thiên thạch (meteors) bị bốc cháy tạo vệt sao băng ở tầng khí quyển nào?",
         en: "In which atmospheric layer do meteors burn up and streak across the sky?" },
    opts: [
      { vi: "Tầng đối lưu", en: "Troposphere" },
      { vi: "Tầng trung lưu (Mesosphere)", en: "Mesosphere" },
      { vi: "Tầng ngoại lưu", en: "Exosphere" },
      { vi: "Tầng nhiệt", en: "Thermosphere" }
    ],
    a: 1,
    ok: { vi: "Chính xác! Hầu hết các thiên thạch bốc cháy trong tầng trung lưu (Mesosphere).",
          en: "Correct! Most meteors burn up in the mesosphere." },
    no: { vi: "Chưa đúng. Dù ta nhìn thấy sao băng từ mặt đất, hiện tượng bốc cháy thực sự diễn ra ở tầng trung lưu.",
          en: "Incorrect. Though visible from ground, meteors actually burn up in the mesosphere." },
    hint: { vi: "Tầng này nằm ở giữa cấu trúc các tầng khí quyển.",
            en: "This layer occupies the middle region of atmospheric layers." },
    src: S.nasaSpaceplaceMeso,
    srcQuote: "Those meteors are burning up in the mesosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-meso-friction",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    /* ⚠️ Lựa chọn sai thứ 2 đã đổi 06/08/2026: "Tầng trung lưu chứa dung nham" (nhảm)
       → "càng cao càng gần Mặt Trời nên càng nóng" — ĐÚNG quan niệm sai phổ biến nhất
       mà CLAUDE.md liệt là cái bẫy số 1. Lời `no` vì thế BÁC nó ra mặt, không né. */
    q: { vi: "Yếu tố nào ở tầng trung lưu khiến thiên thạch bốc cháy khi đâm vào tầng này?",
         en: "What causes meteors to burn up when hitting the mesosphere?" },
    opts: [
      { vi: "Lượng phân tử khí đủ nhiều để tạo ra ma sát và nhiệt lượng", en: "Enough gases to cause friction and create heat" },
      { vi: "Do tầng trung lưu ở cao hơn nên gần Mặt Trời hơn và nóng hơn", en: "Because higher layers are closer to the Sun and thus hotter" },
      { vi: "Tia lửa điện tự phát từ vũ trụ", en: "Spontaneous electric sparks from space" },
      { vi: "Tốc độ thiên thạch tự dưng dừng lại", en: "Meteors suddenly stopping" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Mật độ khí ở tầng trung lưu đủ để tạo ra ma sát cực mạnh thiêu rụi thiên thạch.",
          en: "Correct! Gas molecules in the mesosphere generate friction and heat that burns meteors." },
    no: { vi: "Chưa đúng — và đây là chỗ rất dễ nhầm: lên cao KHÔNG làm ta gần Mặt Trời hơn đáng kể. Thứ đốt cháy thiên thạch là MA SÁT với các phân tử khí, không phải nhiệt từ Mặt Trời.",
          en: "Incorrect — and this is a common trap: going higher does not meaningfully bring you closer to the Sun. What burns meteors is FRICTION with gas molecules, not solar heat." },
    hint: { vi: "Khi hai vật cọ xát với tốc độ cực lớn sẽ sinh ra nhiệt năng rất cao.",
            en: "Extreme speed friction between objects generates high thermal heat." },
    src: S.nasaSpaceplaceMeso,
    srcQuote: "But when they hit the mesosphere, there are enough gases to cause friction and create heat.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-thermo-location",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Tầng nhiệt (Thermosphere) nằm ở vị trí nào so với tầng trung lưu?",
         en: "Where does the thermosphere reside relative to the mesosphere?" },
    opts: [
      { vi: "Nằm phía trên tầng trung lưu", en: "Resides above the mesosphere" },
      { vi: "Nằm phía dưới tầng đối lưu", en: "Resides below the troposphere" },
      { vi: "Nằm sát mực nước biển", en: "Resides at sea level" },
      { vi: "Nằm bên trong tầng bình lưu", en: "Resides inside the stratosphere" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tầng nhiệt (Thermosphere) nằm phía trên tầng trung lưu.",
          en: "Correct! The thermosphere resides directly above the mesosphere." },
    no: { vi: "Chưa đúng. Tầng nhiệt nằm ở vị trí phía trên tầng trung lưu và dưới tầng ngoại lưu.",
          en: "Incorrect. The thermosphere sits above the mesosphere and below the exosphere." },
    hint: { vi: "Đây là tầng khí quyển cao thứ tư tính từ mặt đất lên.",
            en: "This is the fourth atmospheric layer going upward from ground." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "The thermosphere resides above the mesosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-thermo-iss",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Trạm Vũ trụ Quốc tế (ISS) bay quanh Trái Đất ở tầng khí quyển nào?",
         en: "Which atmospheric layer is notable for being home to the International Space Station?" },
    opts: [
      { vi: "Tầng nhiệt (Thermosphere)", en: "Thermosphere" },
      { vi: "Tầng đối lưu sát mặt đất", en: "Troposphere near ground" },
      { vi: "Tầng bình lưu", en: "Stratosphere" },
      { vi: "Tầng trung lưu", en: "Mesosphere" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Trạm Vũ trụ Quốc tế (ISS) hoạt động ở quỹ đạo thuộc tầng nhiệt.",
          en: "Correct! The International Space Station orbits Earth within the thermosphere." },
    no: { vi: "Chưa đúng. Mặc dù ISS ở ngoài không gian gần Trái Đất, nó hoạt động ở độ cao thuộc tầng nhiệt.",
          en: "Incorrect. Though in low Earth orbit, the ISS operates within the thermosphere layer." },
    hint: { vi: "Tầng này có không khí cực kỳ loãng ở độ cao rất lớn.",
            en: "This layer features extremely thin air at very high altitude." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "This layer is notable for being home to the International Space Station and other low-Earth-orbit satellites.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-thermo-aurora",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 3,
    /* ⚠️ Lựa chọn sai thứ 4 đã đổi 06/08/2026: "Băng ở hai cực tự phát sáng" (nhảm)
       → "ánh sáng Mặt Trời phản chiếu từ băng ở vùng cực" (hiểu lầm CÓ THẬT). */
    q: { vi: "Hiện tượng Cực quang (bắc cực quang và nam cực quang) được tạo ra do yếu tố nào?",
         en: "What process creates auroras (the northern and southern lights) in the atmosphere?" },
    opts: [
      { vi: "Các hạt tích điện bị kích thích va chạm với nhau tỏa sáng", en: "Excited particles collide to create auroras" },
      { vi: "Do ánh sáng Mặt Trời phản chiếu trực tiếp từ các tảng băng ở vùng cực", en: "Due to sunlight directly reflecting off polar ice sheets" },
      { vi: "Ánh đèn từ các thành phố lớn phản chiếu lên mây", en: "City lights reflecting onto clouds" },
      { vi: "Mặt Trăng chiếu ánh sáng đỏ vào ban đêm", en: "Red moonlight shining at night" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Khi các hạt tích điện bị kích thích va chạm trong tầng khí quyển sẽ tạo nên cực quang.",
          en: "Correct! Excited charged particles colliding in the upper atmosphere create auroras." },
    no: { vi: "Chưa đúng. Cực quang không phải ánh sáng phản chiếu từ băng hay đèn thành phố — nó là ánh sáng do chính các hạt năng lượng cao va chạm mà PHÁT RA, nên vẫn thấy được vào những đêm không trăng.",
          en: "Incorrect. Auroras are not reflected light from ice or city lights — high-energy particles collide and EMIT the light themselves, which is why they shine on moonless nights." },
    hint: { vi: "Đây là sự tương tác giữa hạt năng lượng Mặt Trời và khí quyển Trái Đất.",
            en: "This is an interaction between solar energy particles and Earth's atmosphere." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "When these particles are excited, they collide to create auroras – also known as the northern and southern lights.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-exo-outermost",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 1,
    q: { vi: "Tầng nào là tầng ngoài cùng của bầu khí quyển Trái Đất, nơi hầu hết các vệ tinh quỹ đạo hoạt động?",
         en: "Which layer is the outermost layer of Earth's atmosphere, where most satellites orbit?" },
    opts: [
      { vi: "Tầng ngoại lưu (Exosphere)", en: "Exosphere" },
      { vi: "Tầng nhiệt", en: "Thermosphere" },
      { vi: "Tầng trung lưu", en: "Mesosphere" },
      { vi: "Tầng bình lưu", en: "Stratosphere" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tầng ngoại lưu (Exosphere) là tầng khí quyển ngoài cùng tiếp giáp vũ trụ.",
          en: "Correct! The exosphere is the outermost layer merging into space." },
    no: { vi: "Chưa đúng. Tầng ngoại lưu (Exosphere) mới là tầng ngoài cùng của khí quyển Trái Đất.",
          en: "Incorrect. The exosphere is the outermost layer of Earth's atmosphere." },
    hint: { vi: "Tiền tố 'Exo-' ám chỉ vị trí ngoài cùng.",
            en: "The prefix 'Exo-' signifies the outermost position." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "The exosphere is the outermost layer of the Earth's atmosphere, where most satellites orbit.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-exo-end",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 3,
    q: { vi: "Tầng ngoại lưu (Exosphere) đánh dấu điều gì và có giới hạn độ cao đỉnh cố định hay không?",
         en: "What does the exosphere denote, and does it have a definitive top altitude?" },
    opts: [
      { vi: "Đánh dấu điểm kết thúc của khí quyển và bắt đầu vũ trụ, không có độ cao đỉnh cố định", en: "Denotes the end of our atmosphere and beginning of outer space, with no definitive top altitude" },
      { vi: "Kết thúc bằng một ranh giới nhiệt độ đóng băng cố định ở độ cao 100 km", en: "Ends at a fixed freezing temperature boundary at 100 km altitude" },
      { vi: "Được ngăn cách bằng một lớp mây dày đặc cố định", en: "Separated by a permanent thick cloud barrier" },
      { vi: "Kết thúc đột ngột do trọng lực Trái Đất biến mất hoàn toàn", en: "Ends abruptly where Earth's gravity disappears completely" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tầng ngoại lưu đánh dấu sự kết thúc của khí quyển và bắt đầu của vũ trụ nhưng không có độ cao đỉnh cố định.",
          en: "Correct! The exosphere denotes the end of atmosphere and start of space without a definitive top altitude." },
    no: { vi: "Chưa đúng. Khí quyển không có ranh giới cứng, tầng ngoại lưu chuyển tiếp dần vào vũ trụ mà không có độ cao đỉnh cố định.",
          en: "Incorrect. The atmosphere lacks a hard boundary; the exosphere fades into space without a fixed top altitude." },
    hint: { vi: "Khí quyển mờ nhạt dần chứ không kết thúc tại một độ cao cố định.",
            en: "The atmosphere thins out gradually rather than ending at a fixed height." },
    src: S.nasaGeneralAtmosphere,
    srcQuote: "The exosphere denotes the end of our atmosphere and the beginning of outer space, though there is not a definitive top altitude where the exosphere ends.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-shield-meteoroids",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 2,
    q: { vi: "Bầu khí quyển bảo vệ Trái Đất khỏi các thiên thạch bay vào như thế nào?",
         en: "How does our atmosphere protect us from incoming meteoroids?" },
    opts: [
      { vi: "Hầu hết thiên thạch bị vỡ vụn trong khí quyển trước khi đâm xuống bề mặt", en: "Most break up in our atmosphere before they can strike the surface" },
      { vi: "Khí quyển thổi thiên thạch bay ngược lại vũ trụ", en: "Atmosphere blows meteoroids back to space" },
      { vi: "Khí quyển biến thiên thạch thành mây mưa", en: "Atmosphere turns meteoroids into rain clouds" },
      { vi: "Khí quyển đóng băng hoàn toàn thiên thạch", en: "Atmosphere freezes meteoroids solid" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ma sát và sức nén khí quyển làm hầu hết thiên thạch vỡ tan trước khi va chạm mặt đất.",
          en: "Correct! Atmospheric pressure and friction break up most meteoroids before surface impact." },
    no: { vi: "Chưa đúng. Khí quyển hoạt động như chiếc khiên làm vỡ vụn và thiêu rụi thiên thạch va chạm.",
          en: "Incorrect. The atmosphere acts as a shield, breaking up and burning incoming meteoroids." },
    hint: { vi: "Nhờ đó bề mặt Trái Đất không bị dày đặc hố thiên thạch như Mặt Trăng.",
            en: "This shields Earth's surface from becoming heavily cratered like the Moon." },
    src: S.nasaEarthFacts,
    srcQuote: "Our atmosphere protects us from incoming meteoroids, most of which break up in our atmosphere before they can strike the surface.",
    srcChecked: "2026-08-06"
    },
    {
    term: "atmo-shield-radiation",
    topic: { vi: "Trái Đất & Khí Quyển", en: "Earth & Atmosphere" },
    lv: 3,
    q: { vi: "Các phân tử ôzôn và oxy ở tầng bình lưu cùng nhau hấp thụ khoảng bao nhiêu bức xạ cực tím từ Mặt Trời?",
         en: "How much solar ultraviolet radiation do ozone and oxygen molecules together absorb?" },
    opts: [
      { vi: "Hấp thụ từ 95% đến 99.9% bức xạ cực tím", en: "Absorb 95 to 99.9% of ultraviolet radiation" },
      { vi: "Chỉ hấp thụ 10% bức xạ", en: "Absorb only 10% of radiation" },
      { vi: "Không hấp thụ bức xạ nào", en: "Absorb zero radiation" },
      { vi: "Hấp thụ 100% ánh sáng nhìn thấy", en: "Absorb 100% of visible light" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ôzôn và oxy phối hợp hấp thụ từ 95% đến 99.9% tia UV nguy hiểm.",
          en: "Correct! Ozone and oxygen together absorb 95 to 99.9% of harmful UV radiation." },
    no: { vi: "Chưa đúng. Nhờ có phân tử ôzôn và oxy, 95% đến 99.9% tia UV độc hại bị ngăn chặn trước khi chạm mặt đất.",
          en: "Incorrect. Together ozone and oxygen block 95% to 99.9% of dangerous UV rays from hitting ground." },
    hint: { vi: "Tỉ lệ che chắn này gần như tuyệt đối, bảo vệ tế bào sinh vật khỏi bị hủy hoại.",
            en: "This near-total absorption shields biological cells from destruction." },
    src: S.ucarOzoneLayer,
    srcQuote: "Together, ozone and oxygen molecules are able to absorb 95 to 99.9% of the ultraviolet radiation that gets to our planet.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-color-temp-determine",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Yếu tố nào của ngôi sao quyết định màu sắc ánh sáng mà nó phát ra?",
         en: "What property of a star determines the color of light it emits?" },
    opts: [
      { vi: "Nhiệt độ bề mặt của ngôi sao", en: "The surface temperature of the star" },
      { vi: "Khoảng cách từ sao tới Trái Đất", en: "The distance from the star to Earth" },
      { vi: "Số lượng hành tinh quay quanh sao", en: "The number of planets orbiting the star" },
      { vi: "Tốc độ di chuyển của sao", en: "The speed at which the star moves" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nhiệt độ bề mặt ngôi sao trực tiếp quyết định màu sắc ánh sáng phát ra.",
          en: "Correct! A star's surface temperature directly determines its emitted light color." },
    no: { vi: "Chưa đúng. Khoảng cách hay hành tinh không làm đổi màu sao; chính nhiệt độ bề mặt quyết định màu sắc.",
          en: "Incorrect. Distance or planets don't change color; surface temperature determines the color." },
    hint: { vi: "Hãy nghĩ đến nhiệt độ nóng hay nguội của bề mặt ngôi sao.",
            en: "Think about how hot or cool the star's surface is." },
    src: S.lcoStarColors,
    srcQuote: "The surface temperature of a star determines the color of light it emits.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-blue-hotter-red",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "So sánh giữa các ngôi sao màu xanh, sao màu vàng và sao màu đỏ, sao nào có nhiệt độ bề mặt nóng nhất?",
         en: "Comparing blue, yellow, and red stars, which stars have the hottest surface temperature?" },
    opts: [
      { vi: "Sao màu xanh dương nóng hơn sao màu vàng và sao màu đỏ", en: "Blue stars are hotter than yellow stars, which are hotter than red stars" },
      { vi: "Sao màu đỏ nóng hơn sao màu xanh", en: "Red stars are hotter than blue stars" },
      { vi: "Tất cả các sao màu có nhiệt độ hệt như nhau", en: "All star colors have identical temperatures" },
      { vi: "Sao màu vàng nóng nhất", en: "Yellow stars are the hottest" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ngược với ngọn lửa thông thường, trong vũ trụ sao màu xanh dương nóng hơn sao màu vàng và sao màu đỏ.",
          en: "Correct! Unlike campfire intuition, in space blue stars are hotter than yellow and red stars." },
    no: { vi: "Chưa đúng. Nhiều người nghĩ màu đỏ nóng nhất, nhưng trong thiên văn học sao màu xanh dương mới là sao nóng nhất.",
          en: "Incorrect. Many think red is hottest, but in astronomy blue stars are the hottest." },
    hint: { vi: "Sao tỏa năng lượng bức xạ ở dải màu xanh nóng hơn nhiều so với màu đỏ.",
            en: "Stars emitting blue radiation burn much hotter than red ones." },
    src: S.lcoStarColors,
    srcQuote: "Blue stars are hotter than yellow stars, which are hotter than red stars.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-color-spectrum-order",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Thứ tự dải màu sắc của các ngôi sao từ NÓNG NHẤT đến NGUỘI NHẤT xếp theo chiều nào?",
         en: "What is the correct order of star colors from HOTTEST to COOLEST?" },
    opts: [
      { vi: "Sao xanh dương → Sao vàng → Sao đỏ", en: "Blue stars → Yellow stars → Red stars" },
      { vi: "Sao đỏ → Sao vàng → Sao xanh dương", en: "Red stars → Yellow stars → Blue stars" },
      { vi: "Sao vàng → Sao đỏ → Sao xanh dương", en: "Yellow stars → Red stars → Blue stars" },
      { vi: "Sao đỏ → Sao xanh dương → Sao vàng", en: "Red stars → Blue stars → Yellow stars" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Thứ tự giảm dần nhiệt độ là Sao xanh dương (nóng nhất) → Sao vàng (trung bình) → Sao đỏ (nguội nhất).",
          en: "Correct! Temperature decreases from Blue stars (hottest) → Yellow stars (moderate) → Red stars (coolest)." },
    no: { vi: "Chưa đúng. Sao xanh dương nóng nhất, tiếp đến sao vàng và nguội nhất là sao đỏ.",
          en: "Incorrect. Blue stars are hottest, followed by yellow stars, and red stars are coolest." },
    hint: { vi: "Sao xanh dương có nhiệt độ cao nhất và sao đỏ có nhiệt độ thấp nhất.",
            en: "Blue stars have the highest temperature and red stars the lowest." },
    src: S.lcoStarColors,
    srcQuote: "Blue stars are hotter than yellow stars, which are hotter than red stars.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-surface-temp-color",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Yếu tố cốt lõi nào quyết định màu sắc chủ đạo của ngôi sao mà các kính thiên văn quan sát được?",
         en: "What core factor determines the primary color of a star observed by telescopes?" },
    opts: [
      { vi: "Nhiệt độ bề mặt của ngôi sao", en: "The surface temperature of the star" },
      { vi: "Nhiệt độ không ảnh hưởng đến màu sắc", en: "Temperature has zero effect on color" },
      { vi: "Nhiệt độ làm sao đổi màu liên tục mỗi giây", en: "Temperature causes color to shift every second" },
      { vi: "Nhiệt độ khiến sao biến thành màu xanh lục thuần túy", en: "Temperature turns stars pure green" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nhiệt độ bề mặt quyết định dải bước sóng bức xạ phát ra mạnh nhất.",
          en: "Correct! Surface temperature dictates the peak radiation wavelength emitted." },
    no: { vi: "Chưa đúng. Nhiệt độ bề mặt là yếu tố cốt lõi quyết định màu sắc ngôi sao.",
          en: "Incorrect. Surface temperature is the fundamental factor dictating star color." },
    hint: { vi: "Quy luật bức xạ vật đen gắn liền nhiệt độ với đỉnh màu sắc phát ra.",
            en: "Blackbody radiation laws link temperature to peak color emission." },
    src: S.lcoStarColors,
    srcQuote: "The surface temperature of a star determines the color of light it emits.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-red-dwarf-coolest",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Đặc điểm về kích thước và nhiệt độ bề mặt của các sao lùn đỏ (Red dwarfs) là gì?",
         en: "What are the characteristics of red dwarfs regarding size and temperature?" },
    opts: [
      { vi: "Là những sao dãy chính nhỏ nhất và nguội nhất", en: "They are the smallest main sequence stars and the coolest" },
      { vi: "Là những sao lớn nhất và nóng nhất vũ trụ", en: "They are the largest and hottest stars in the universe" },
      { vi: "Là những ngôi sao không tỏa nhiệt", en: "They are stars that emit no heat" },
      { vi: "Là những sao màu xanh dương cực nóng", en: "They are extremely hot blue stars" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sao lùn đỏ có kích thước nhỏ và nhiệt độ bề mặt nguội nhất trong dải sao chính.",
          en: "Correct! Red dwarfs are the smallest and coolest main sequence stars." },
    no: { vi: "Chưa đúng. Sao lùn đỏ là những ngôi sao nhỏ bé và có nhiệt độ bề mặt nguội nhất.",
          en: "Incorrect. Red dwarfs are small stars with the coolest surface temperatures." },
    hint: { vi: "Các ngôi sao màu đỏ nằm ở nhóm nhiệt độ thấp nhất trên biểu đồ.",
            en: "Red stars occupy the lowest temperature group on the scale." },
    src: S.nasaStarTypes,
    srcQuote: "Red dwarfs are the smallest main sequence stars – just a fraction of the Sun's size and mass. They're also the coolest",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-coolest-star-temperature",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Trong số các loại sao thuộc dải sao chính, loại sao nào có nhiệt độ bề mặt nguội nhất?",
         en: "Among main sequence stars, which type has the coolest surface temperature?" },
    opts: [
      { vi: "Các sao lùn đỏ (Red dwarfs)", en: "Red dwarfs" },
      { vi: "Các sao khổng lồ xanh", en: "Blue giants" },
      { vi: "Các sao lùn vàng", en: "Yellow dwarfs" },
      { vi: "Các sao siêu tân tinh", en: "Supernovas" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sao lùn đỏ là những sao dải chính nhỏ nhất và có nhiệt độ nguội nhất.",
          en: "Correct! Red dwarfs are the smallest main sequence stars and the coolest." },
    no: { vi: "Chưa đúng. Các sao lùn đỏ chính là những ngôi sao nhỏ nhất và nguội nhất dải chính.",
          en: "Incorrect. Red dwarfs are the smallest and coolest stars on the main sequence." },
    hint: { vi: "Đây là loại sao lùn tỏa ra ánh sáng màu đỏ mờ.",
            en: "This is a dwarf star emitting dim reddish light." },
    src: S.nasaStarTypes,
    srcQuote: "Red dwarfs are the smallest main sequence stars – just a fraction of the Sun's size and mass. They're also the coolest",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-sun-age-main-sequence",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Mặt Trời của chúng ta hiện nay ước tính bao nhiêu tuổi và thuộc nhóm sao nào?",
         en: "How old is our Sun estimated to be, and what group of stars does it belong to?" },
    opts: [
      { vi: "Khoảng 4,6 tỷ năm tuổi, là một sao thuộc dải sao chính", en: "About 4.6 billion years old, a main sequence star" },
      { vi: "Khoảng 100 triệu năm tuổi, là sao khổng lồ đỏ", en: "About 100 million years old, a red giant" },
      { vi: "Khoảng 1.000 năm tuổi, là sao lùn trắng", en: "About 1,000 years old, a white dwarf" },
      { vi: "Mới sinh ra được 1 ngày", en: "Formed just 1 day ago" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Mặt Trời khoảng 4,6 tỷ năm tuổi và đang là một ngôi sao thuộc dải sao chính.",
          en: "Correct! Our Sun is ~4.6 billion years old and currently a main sequence star." },
    no: { vi: "Chưa đúng. Mặt Trời là một sao thuộc dải sao chính với tuổi hiện tại khoảng 4,6 tỷ năm.",
          en: "Incorrect. Our Sun is a main sequence star with a current age of 4.6 billion years." },
    hint: { vi: "Mặt Trời đã tồn tại được hơn 4,5 tỷ năm.",
            en: "Our Sun has existed for more than 4.5 billion years." },
    src: S.nasaStarTypes,
    srcQuote: "NASA's Solar Dynamics Observatory captured this image of our 4.6-billion-year-old Sun, a main sequence star.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-sirius-brightest",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Ngôi sao nào sáng nhất trên bầu trời đêm mà con người có thể quan sát bằng mắt thường?",
         en: "Which star is the brightest star in the night sky visible to the unaided eye?" },
    opts: [
      { vi: "Sao Sirius (Sao Thiên Lang)", en: "Sirius" },
      { vi: "Sao Proxima Centauri", en: "Proxima Centauri" },
      { vi: "Sao Arcturus", en: "Arcturus" },
      { vi: "Sao Procyon B", en: "Procyon B" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sirius là ngôi sao sáng nhất trên bầu trời đêm thuộc chòm sao Đại Khuyển.",
          en: "Correct! Sirius is the brightest star in the night sky, located in Canis Major." },
    no: { vi: "Chưa đúng. Sirius (Sao Thiên Lang) mới là ngôi sao tỏa sáng rực rỡ nhất bầu trời đêm.",
          en: "Incorrect. Sirius is the brightest glowing star in our nighttime sky." },
    hint: { vi: "Ngôi sao này tỏa ánh sáng màu trắng xanh rực rỡ.",
            en: "This star shines with a brilliant blue-white light." },
    src: S.nasaStarTypes,
    srcQuote: "Sirius – the brightest star in the night sky – in the northern constellation Canis Major.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-proxima-red-dwarf",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Ngôi sao hàng xóm gần Trái Đất nhất ngoài Mặt Trời — Proxima Centauri — thuộc loại sao nào?",
         en: "What type of star is Proxima Centauri, our closest stellar neighbor?" },
    opts: [
      { vi: "Sao lùn đỏ (Red dwarf)", en: "Red dwarf" },
      { vi: "Sao khổng lồ xanh", en: "Blue giant" },
      { vi: "Sao siêu tân tinh", en: "Supernova" },
      { vi: "Lỗ đen", en: "Black hole" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Proxima Centauri cách Trái Đất hơn 4 năm ánh sáng là một sao lùn đỏ.",
          en: "Correct! Proxima Centauri, just over 4 light-years away, is a red dwarf." },
    no: { vi: "Chưa đúng. Proxima Centauri là một sao lùn đỏ nhỏ bé nằm ở chòm sao Bán Nhân Mã.",
          en: "Incorrect. Proxima Centauri is a small red dwarf in the Centaurus constellation." },
    hint: { vi: "Đây là loại sao màu đỏ nguội có số lượng đông đảo nhất vũ trụ.",
            en: "This is the most abundant type of cool red star in the universe." },
    src: S.nasaStarTypes,
    srcQuote: "Our closest stellar neighbor, shown here in this Hubble image, is the red dwarf Proxima Centauri.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-closest-main-sequence",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Ngôi sao dải chính nào gần Trái Đất nhất mà con người có thể nhìn thấy bằng mắt thường?",
         en: "Which main sequence star is the closest to Earth that can be seen with the unaided eye?" },
    opts: [
      { vi: "Rigil Kentaurus (Alpha Centauri)", en: "Rigil Kentaurus (better known as Alpha Centauri)" },
      { vi: "Sao Sirius", en: "Sirius" },
      { vi: "Sao Polaris", en: "Polaris" },
      { vi: "Sao Betelgeuse", en: "Betelgeuse" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Rigil Kentaurus (Alpha Centauri) thuộc chòm sao Bán Nhân Mã là sao dải chính gần nhất quan sát được bằng mắt thường.",
          en: "Correct! Rigil Kentaurus (Alpha Centauri) is the closest main sequence star visible to unaided eyes." },
    no: { vi: "Chưa đúng. Rigil Kentaurus (Alpha Centauri) chính là ngôi sao dải chính gần nhất nhìn thấy bằng mắt thường.",
          en: "Incorrect. Rigil Kentaurus (Alpha Centauri) is the closest main sequence star seen with naked eyes." },
    hint: { vi: "Ngôi sao này nằm ở chòm sao Bán Nhân Mã thuộc bầu trời phương Nam.",
            en: "This star is located in the southern constellation Centaurus." },
    src: S.nasaStarTypes,
    srcQuote: "Rigil Kentaurus (better known as Alpha Centauri) in the southern constellation Centaurus is the closest main sequence star that can be seen with the unaided eye.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-arcturus-red-giant",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Ngôi sao Arcturus trong chòm sao Mục Phu (Boötes) thuộc loại sao nào có thể nhìn thấy bằng mắt thường?",
         en: "Which type of star visible to the unaided eye is Arcturus in Boötes?" },
    opts: [
      { vi: "Sao khổng lồ đỏ (Red giant)", en: "Red giant" },
      { vi: "Sao lùn trắng", en: "White dwarf" },
      { vi: "Sao neutron", en: "Neutron star" },
      { vi: "Sao lùn nâu", en: "Brown dwarf" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Arcturus là một sao khổng lồ đỏ tỏa sáng rõ rệt trên bầu trời đêm.",
          en: "Correct! Arcturus is a prominent red giant visible in the night sky." },
    no: { vi: "Chưa đúng. Arcturus là một ngôi sao khổng lồ đỏ đã mở rộng kích thước ở cuối vòng đời.",
          en: "Incorrect. Arcturus is a red giant star that expanded late in its lifecycle." },
    hint: { vi: "Đây là ngôi sao đã giãn nở lớn ra và bề mặt nguội đi chuyển màu đỏ.",
            en: "This star expanded in size and cooled down into a reddish hue." },
    src: S.nasaStarTypes,
    srcQuote: "Arcturus in the northern constellation Boötes and Gamma Crucis in the southern constellation Crux (the Southern Cross) are red giants visible to the unaided eye.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-betelgeuse-red-giant",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Trong các tài liệu minh họa của NASA, những ngôi sao như Betelgeuse hay Antares được miêu tả là loại sao nào?",
         en: "In NASA illustrations, stars like Betelgeuse or Antares depict what type of star?" },
    opts: [
      { vi: "Một ngôi sao khổng lồ đỏ (Red giant star)", en: "A red giant star" },
      { vi: "Một sao lùn trắng cực nhỏ", en: "An extremely small white dwarf" },
      { vi: "Một trạm vũ trụ nhân tạo", en: "An artificial space station" },
      { vi: "Một hành tinh đá khô hạn", en: "A dry rocky planet" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Betelgeuse và Antares là những ví dụ minh họa điển hình về sao khổng lồ đỏ.",
          en: "Correct! Betelgeuse and Antares are prime illustrative examples of red giant stars." },
    no: { vi: "Chưa đúng. Betelgeuse và Antares đại diện cho loại sao khổng lồ đỏ có màu sắc rực rỡ.",
          en: "Incorrect. Betelgeuse and Antares represent vividly colored red giant stars." },
    hint: { vi: "Đây là loại sao lớn màu đỏ xuất hiện ở giai đoạn sau của tiến hóa sao.",
            en: "This represents large reddish stars in late stellar evolution." },
    src: S.nasaStarTypes,
    srcQuote: "This illustration depicts a red giant star, like Betelgeuse or Antares.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-red-giant-expansion",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Khi phản ứng tổng hợp hydro chuyển ra các lớp vỏ ngoài của ngôi sao, hiện tượng gì sẽ xảy ra?",
         en: "When hydrogen fusion moves into a star's outer layers, what occurs as a result?" },
    opts: [
      { vi: "Làm các lớp vỏ ngoài giãn nở ra và tạo thành sao khổng lồ đỏ", en: "Causes outer layers to expand, resulting in a red giant" },
      { vi: "Làm ngôi sao thu nhỏ lại thành lỗ đen ngay lập tức", en: "Causes the star to instantly shrink into a black hole" },
      { vi: "Làm ngôi sao nổ tung không để lại vết tích", en: "Causes the star to explode leaving zero trace" },
      { vi: "Làm ngôi sao biến thành sao băng đá", en: "Turns the star into an icy meteor" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sự di chuyển phản ứng ra vỏ ngoài khiến ngôi sao giãn nở thành sao khổng lồ đỏ.",
          en: "Correct! Fusion moving outward causes outer layers to expand into a red giant." },
    no: { vi: "Chưa đúng. Phản ứng hạt nhân ở lớp vỏ ngoài làm cho ngôi sao giãn nở lớn ra thành sao khổng lồ đỏ.",
          en: "Incorrect. Outer shell fusion causes the star's layers to expand into a red giant." },
    hint: { vi: "Quá trình này làm kích thước ngôi sao tăng lên gấp nhiều lần.",
            en: "This process causes the star's physical size to expand dramatically." },
    src: S.nasaStarTypes,
    srcQuote: "Hydrogen fusion begins moving into the star's outer layers, causing them to expand. The result is a red giant",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-properties-range",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Các ngôi sao trên bầu trời dao động trong dải phạm vi đa dạng ở những yếu tố nào?",
         en: "In what range of properties do stars in the universe vary?" },
    opts: [
      { vi: "Độ sáng, màu sắc và kích thước", en: "Luminosity, color, and size" },
      { vi: "Chỉ khác nhau về hình dạng vuông hay tròn", en: "Only differ in square or round shape" },
      { vi: "Tất cả các sao đều giống hệt nhau mọi thông số", en: "All stars are identical in every parameter" },
      { vi: "Chỉ khác nhau về số lượng vệ tinh", en: "Only differ in number of moons" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Các ngôi sao rất đa dạng về độ sáng, màu sắc và kích thước từ nhỏ đến khổng lồ.",
          en: "Correct! Stars vary widely in luminosity, color, and physical size." },
    no: { vi: "Chưa đúng. Ngôi sao trong vũ trụ có sự chênh lệch lớn về độ sáng, màu sắc và kích cỡ.",
          en: "Incorrect. Cosmos stars vary greatly in brightness, color hue, and scale." },
    hint: { vi: "Ba đặc tính quan trọng nhất khi nhìn vào một ngôi sao trên bầu trời.",
            en: "The three most key observational features of stars." },
    src: S.nasaStarTypes,
    srcQuote: "They range in luminosity, color, and size – from a tenth to 200 times the Sun's mass",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-red-dwarf-faint",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Tại sao các nhà quan sát bầu trời không thể dùng mắt thường để nhìn thấy các sao lùn đỏ?",
         en: "Why can't stargazers see red dwarfs with the unaided eye?" },
    opts: [
      { vi: "Vì chúng quá mờ đối với mắt thường", en: "Because red dwarfs are too faint to see with the unaided eye" },
      { vi: "Vì sao lùn đỏ hoàn toàn không tỏa ra ánh sáng", en: "Because red dwarfs emit zero light" },
      { vi: "Vì sao lùn đỏ nấp đằng sau Mặt Trăng ban đêm", en: "Because red dwarfs hide behind the Moon" },
      { vi: "Vì bầu khí quyển Trái Đất hấp thụ toàn bộ ánh sáng đỏ", en: "Because the atmosphere absorbs all red light" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Mặc dù chiếm đa số trong thiên hà, sao lùn đỏ quá mờ để mắt thường nhìn thấy.",
          en: "Correct! Though most numerous in galaxy, red dwarfs are too faint for eyes." },
    no: { vi: "Chưa đúng. Sao lùn đỏ phát độ sáng rất nhỏ nên cường độ ánh sáng quá mờ so với mắt người.",
          en: "Incorrect. Red dwarfs produce low luminosity, making them too dim for naked eyes." },
    hint: { vi: "Độ sáng phát ra của chúng rất nhỏ so với các sao lớn.",
            en: "Their emitted brightness is very low compared to large stars." },
    src: S.nasaStarTypes,
    srcQuote: "For Stargazers: Red dwarfs are too faint to see with the unaided eye.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-red-dwarf-longevity",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Tại sao các sao lùn đỏ lại có thể tồn tại và cháy ổn định hàng nghìn tỷ năm?",
         en: "Why can red dwarfs steadily burn through their hydrogen for trillions of years?" },
    opts: [
      { vi: "Sự cuộn đảo đối lưu liên tục mang nguồn hydro mới vào lõi giúp sao cháy rất chậm và ổn định", en: "Constant churning brings fresh hydrogen to the core, burning steadily over trillions of years" },
      { vi: "Vì chúng lấy nhiên liệu từ các hành tinh xung quanh", en: "Because they draw fuel from surrounding planets" },
      { vi: "Vì chúng không xảy ra phản ứng hạt nhân", en: "Because no nuclear fusion occurs inside them" },
      { vi: "Vì chúng được sưởi ấm từ các sao khác", en: "Because they are heated by other stars" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sự cuộn chảy đối lưu mang hydro liên tục vào lõi giúp sao lùn đỏ duy trì sự sống hàng nghìn tỷ năm.",
          en: "Correct! Convective churning brings fresh hydrogen fuel into the core over trillions of years." },
    no: { vi: "Chưa đúng. Sự cuộn đảo vật chất giúp sao lùn đỏ sử dụng cạn kiệt hydro rất chậm rãi.",
          en: "Incorrect. Material churning allows red dwarfs to consume hydrogen fuel very slowly." },
    hint: { vi: "Dòng đối lưu vật chất liên tục cung cấp nhiên liệu hydro mới cho lõi sao.",
            en: "Convective material currents constantly supply fresh hydrogen to the core." },
    src: S.nasaStarTypes,
    srcQuote: "Because of this constant churning, red dwarfs can steadily burn through their entire supply of hydrogen over trillions of years without changing their internal structures",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-prism-wavelengths",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Lăng kính (prism) có tác dụng gì khi ánh sáng trắng đi xuyên qua nó?",
         en: "What does a prism do when white light passes through it?" },
    opts: [
      { vi: "Tách ánh sáng trắng thành các bước sóng màu sắc khác nhau", en: "Separates white light into its different wavelengths" },
      { vi: "Hấp thụ hoàn toàn ánh sáng chiếu vào", en: "Absorbs all incoming light completely" },
      { vi: "Biến ánh sáng thành nguồn điện năng", en: "Turns light directly into electrical power" },
      { vi: "Làm ánh sáng biến mất không vết tích", en: "Makes light vanish leaving no trace" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Lăng kính phân tách ánh sáng trắng thành dải cầu vồng các bước sóng màu sắc.",
          en: "Correct! A prism separates white light into a rainbow spectrum of wavelengths." },
    no: { vi: "Chưa đúng. Lăng kính giúp tán sắc, tách ánh sáng trắng thành các dải bước sóng màu sắc.",
          en: "Incorrect. A prism disperses white light into its component color wavelengths." },
    hint: { vi: "Kết quả tạo nên dải màu cầu vồng khi ánh sáng trắng đi qua lăng kính.",
            en: "This creates a rainbow band when white light enters the prism." },
    src: S.nasaSpaceplaceMagic,
    srcQuote: "A prism separates white light into its different wavelengths.",
    srcChecked: "2026-08-06"
    },
    {
    term: "star-visible-wavelength-range",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Trong dải ánh sáng nhìn thấy, màu sắc nào có bước sóng dài nhất và màu sắc nào có bước sóng ngắn nhất?",
         en: "In the visible light range, which color has the longest wavelength and which has the shortest?" },
    opts: [
      { vi: "Màu đỏ có bước sóng dài nhất, màu tím có bước sóng ngắn nhất", en: "Red has the longest wavelength, while violet has the shortest" },
      { vi: "Màu xanh có bước sóng dài nhất, màu đỏ ngắn nhất", en: "Blue has the longest wavelength, red has the shortest" },
      { vi: "Tất cả các màu đều có bước sóng bằng nhau", en: "All colors have identical wavelengths" },
      { vi: "Màu vàng có bước sóng ngắn nhất", en: "Yellow has the shortest wavelength" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Trong dải quang phổ nhìn thấy, ánh sáng đỏ có bước sóng dài nhất còn tím có bước sóng ngắn nhất.",
          en: "Correct! In visible spectrum, red light has the longest wavelength and violet the shortest." },
    no: { vi: "Chưa đúng. Màu đỏ có bước sóng dài nhất và màu tím có bước sóng ngắn nhất trong dải quang phổ.",
          en: "Incorrect. Red light holds the longest wavelength and violet the shortest in the visible spectrum." },
    hint: { vi: "Màu đỏ nằm ở đầu sóng dài và màu tím ở đầu sóng ngắn.",
            en: "Red sits at the long-wavelength end and violet at the short-wavelength end." },
    src: S.nasaSpaceplaceMagic,
    srcQuote: "In the visible range, red has the longest wavelength, while violet has the shortest.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-definition-moon-between",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Hiện tượng nhật thực (solar eclipse) xảy ra khi nào?",
         en: "When does a solar eclipse happen?" },
    opts: [
      { vi: "Khi Mặt Trăng đi vào giữa Mặt Trời và Trái Đất, đổ bóng lên Trái Đất", en: "When the Moon passes between the Sun and Earth, casting a shadow on Earth" },
      { vi: "Khi Trái Đất đi vào giữa Mặt Trời và Mặt Trăng", en: "When Earth passes between the Sun and Moon" },
      { vi: "Khi Mặt Trời biến mất vào ban đêm", en: "When the Sun vanishes at night" },
      { vi: "Khi một sao băng đâm vào Mặt Trăng", en: "When a meteor crashes into the Moon" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nhật thực xảy ra khi Mặt Trăng di chuyển vào giữa Mặt Trời và Trái Đất, đổ bóng che khuất ánh sáng.",
          en: "Correct! A solar eclipse occurs when the Moon passes between the Sun and Earth, casting its shadow." },
    no: { vi: "Chưa đúng. Vị trí chính xác là Mặt Trăng nằm ở giữa Mặt Trời và Trái Đất.",
          en: "Incorrect. The exact alignment is the Moon positioned between the Sun and Earth." },
    hint: { vi: "Mặt Trăng là vật thể chắn ngang đường đi của ánh sáng Mặt Trời chiếu tới Trái Đất.",
            en: "The Moon is the body that blocks sunlight traveling from the Sun to Earth." },
    src: S.nasaEclipseTypes,
    srcQuote: "A solar eclipse happens when the Moon passes between the Sun and Earth, casting a shadow on Earth that either fully or partially blocks the Sun's light in some areas.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-annular-farthest-ring",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    /* ⚠️ "biểu ảo" (không phải thuật ngữ) đã sửa thành "biểu kiến" — 06/08/2026. */
    q: { vi: "Hiện tượng nhật thực hình khuyên (annular solar eclipse) xảy ra khi nào?",
         en: "When does an annular solar eclipse happen?" },
    opts: [
      { vi: "Khi Mặt Trăng ở điểm xa Trái Đất nhất nên trông nhỏ hơn Mặt Trời, tạo thành vòng lửa xung quanh", en: "When the Moon is at or near its farthest point from Earth, creating a bright ring around it" },
      { vi: "Khi Mặt Trăng tiến cực gần Trái Đất che kín hoàn toàn Mặt Trời", en: "When the Moon is extremely close to Earth completely covering the Sun" },
      { vi: "Khi Mặt Trăng biến thành màu đỏ thẫm", en: "When the Moon turns deep red" },
      { vi: "Khi Trái Đất che khuất hoàn toàn Mặt Trăng", en: "When Earth fully blocks the Moon" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Do Mặt Trăng ở xa Trái Đất nên đường kính biểu kiến nhỏ hơn, tạo ra dải vành lửa xung quanh.",
          en: "Correct! Because the Moon is farther, it appears smaller than the Sun, creating a ring of fire." },
    no: { vi: "Chưa đúng. Nhật thực hình khuyên xuất hiện khi Mặt Trăng ở xa Trái Đất nên không che hết đĩa Mặt Trời.",
          en: "Incorrect. An annular eclipse happens when the Moon is farther away, leaving a visible outer ring." },
    hint: { vi: "Khoảng cách xa khiến đĩa Mặt Trăng trông nhỏ hơn đĩa Mặt Trời.",
            en: "Greater distance makes the Moon's disk appear smaller than the Sun's disk." },
    src: S.nasaEclipseTypes,
    srcQuote: "An annular solar eclipse happens when the Moon passes between the Sun and Earth, but when it is at or near its farthest point from Earth.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-partial-crescent-shape",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    /* ⚠️ srcQuote đã ĐỔI 06/08/2026. Câu cũ ("…are not perfectly lined up") CÓ THẬT
       nhưng KHÔNG nói gì về hình dạng — tức là không chứng minh đáp án "lưỡi liềm".
       Câu mới là câu ngay sau đó trên chính trang ấy. */
    q: { vi: "Khi xảy ra nhật thực một phần (partial solar eclipse), Mặt Trời có hình dạng như thế nào?",
         en: "What shape does the Sun appear to have during a partial solar eclipse?" },
    opts: [
      { vi: "Mặt Trời có hình lưỡi liềm", en: "The Sun appears to have a crescent shape" },
      { vi: "Mặt Trời có hình ngôi sao năm cánh", en: "The Sun turns into a five-pointed star" },
      { vi: "Mặt Trời hoàn toàn biến mất trong bóng tối đen thẫm", en: "The Sun vanishes completely in total darkness" },
      { vi: "Mặt Trời biến thành hình vuông", en: "The Sun turns into a square" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Do ba thiên thể không thẳng hàng tuyệt đối, phần Mặt Trời còn lộ ra tạo thành hình lưỡi liềm.",
          en: "Correct! Because alignment is not perfect, the unblocked part of the Sun looks like a crescent." },
    no: { vi: "Chưa đúng. Nhật thực một phần chỉ che khuất một góc, làm Mặt Trời có hình lưỡi liềm khuyết.",
          en: "Incorrect. A partial eclipse covers only a section, giving the Sun a crescent shape." },
    hint: { vi: "Hình dạng khuyết hệt như hình dáng Mặt Trăng đầu tháng.",
            en: "The shape resembles a crescent moon." },
    src: S.nasaEclipseTypes,
    srcQuote: "Only a part of the Sun will appear to be covered, giving it a crescent shape.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-hybrid-annular-total",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Hiện tượng nhật thực lai (hybrid solar eclipse) là gì?",
         en: "What is a hybrid solar eclipse?" },
    opts: [
      { vi: "Nhật thực chuyển đổi giữa hình khuyên và toàn phần do độ cong bề mặt Trái Đất", en: "An eclipse shifting between annular and total as the shadow moves across Earth's curved surface" },
      { vi: "Nhật thực diễn ra đồng thời với nguyệt thực", en: "An eclipse occurring simultaneously with a lunar eclipse" },
      { vi: "Nhật thực chỉ kéo dài đúng 1 giây", en: "An eclipse lasting exactly 1 second" },
      { vi: "Nhật thực xuất hiện cùng lúc ở hai hành tinh", en: "An eclipse appearing on two planets at once" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Do bề mặt Trái Đất cong, bóng Mặt Trăng di chuyển làm nhật thực đổi giữa dạng hình khuyên và toàn phần.",
          en: "Correct! Earth's curvature causes the eclipse to transition between annular and total along its path." },
    no: { vi: "Chưa đúng. Nhật thực lai là sự chuyển đổi giữa nhật thực toàn phần và nhật thực hình khuyên.",
          en: "Incorrect. A hybrid eclipse shifts between annular and total along its track." },
    hint: { vi: "Độ cong của Trái Đất làm thay đổi khoảng cách từ bóng Mặt Trăng tới bề mặt.",
            en: "Earth's spherical curve changes the distance to the Moon's shadow tip." },
    src: S.nasaEclipseTypes,
    srcQuote: "Because Earth's surface is curved, sometimes an eclipse can shift between annular and total as the Moon's shadow moves across the globe. This is called a hybrid solar eclipse.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-shadow-umbra-penumbra",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Bóng của Mặt Trăng đổ xuống Trái Đất trong kỳ nhật thực bao gồm hai vùng nón nào?",
         en: "What two concentric shadow cones are cast by the Moon during an eclipse?" },
    opts: [
      { vi: "Vùng bóng tối trong cùng (umbra) và vùng bóng nửa tối bên ngoài (penumbra)", en: "A dark inner shadow called the umbra and a lighter outer shadow called the penumbra" },
      { vi: "Vùng màu xanh và vùng màu đỏ", en: "A blue region and a red region" },
      { vi: "Vùng khí nóng và vùng khí lạnh", en: "A hot gas region and a cold gas region" },
      { vi: "Vùng đại dương và vùng đất liền", en: "An ocean region and a land region" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Bóng Mặt Trăng gồm vùng bóng tối chính tâm (umbra) và vùng bóng nửa tối (penumbra).",
          en: "Correct! The Moon's shadow consists of an inner umbra and outer penumbra." },
    no: { vi: "Chưa đúng. Thuật ngữ thiên văn gọi hai vùng bóng này là umbra (bóng tối) và penumbra (bóng nửa tối).",
          en: "Incorrect. Astronomical terms for these two shadow cones are umbra and penumbra." },
    hint: { vi: "Tên tiếng Anh của hai vùng bóng này bắt đầu bằng chữ U và chữ P.",
            en: "The terms for these shadow regions begin with U and P." },
    src: S.nasaEclipseGeometry,
    srcQuote: "The shadow comprises two concentric cones, a dark inner shadow called the umbra and a lighter outer shadow called the penumbra.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-umbra-total-blocked",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Người quan sát đứng trong vùng bóng tối trung tâm (umbra) của Mặt Trăng sẽ nhìn thấy hiện tượng gì?",
         en: "What do observers standing within the Moon's central umbra see?" },
    opts: [
      { vi: "Nhìn thấy Mặt Trời bị che khuất hoàn toàn", en: "They see the Sun completely blocked" },
      { vi: "Nhìn thấy Mặt Trời chỉ bị che một phần nhỏ", en: "They see the Sun only partially covered" },
      { vi: "Nhìn thấy Mặt Trăng phát ra ánh sáng xanh", en: "They see the Moon emitting blue light" },
      { vi: "Không nhìn thấy bất kỳ bóng tối nào", en: "They see no shadow at all" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Đứng trong vùng umbra hẹp, bạn sẽ trải nghiệm nhật thực toàn phần với Mặt Trời bị che khuất hoàn toàn.",
          en: "Correct! Within the central umbra, observers witness the Sun completely covered." },
    no: { vi: "Chưa đúng. Vùng bóng tối đậm nhất umbra mang lại góc nhìn nhật thực toàn phần.",
          en: "Incorrect. The dark umbral cone provides a view of total solar obscuration." },
    hint: { vi: "Vùng umbra là vùng tâm bóng tối nhất trên Trái Đất.",
            en: "The umbra is the darkest central shadow zone on Earth." },
    src: S.nasaEclipseGeometry,
    srcQuote: "Observers on Earth who are within the smaller, central umbra see the Sun completely blocked.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-penumbra-partially-blocked",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Người quan sát đứng trong vùng bóng nửa tối rộng hơn (penumbra) sẽ quan sát được hiện tượng gì?",
         en: "What do observers within the larger penumbra witness during a solar eclipse?" },
    opts: [
      { vi: "Mặt Trời chỉ bị che khuất một phần", en: "The Sun is only partially blocked" },
      { vi: "Mặt Trời bị che khuất hoàn toàn", en: "The Sun is completely blocked" },
      { vi: "Mặt Trăng biến mất khỏi bầu trời", en: "The Moon vanishes from the sky" },
      { vi: "Trái Đất ngừng quay", en: "Earth stops rotating" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Vùng penumbra rộng lớn bên ngoài chỉ nhìn thấy nhật thực một phần.",
          en: "Correct! Inside the larger outer penumbra, only a partial eclipse is seen." },
    no: { vi: "Chưa đúng. Vùng penumbra nhận được một phần ánh sáng nên chỉ thấy Mặt Trời bị che một phần.",
          en: "Incorrect. The penumbral shadow only causes partial obscuration of the Sun." },
    hint: { vi: "Vùng bóng mờ bên ngoài vẫn nhận được một phần ánh sáng.",
            en: "The outer lighter shadow area still receives partial sunlight." },
    src: S.nasaEclipseGeometry,
    srcQuote: "Within the larger penumbra, the Sun is only partially blocked.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-corona-outermost-atmosphere",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Vành nhật hoa (corona) của Mặt Trời là bộ phận nào?",
         en: "What is the Sun's corona?" },
    opts: [
      { vi: "Là lớp khí ngoài cùng thuộc khí quyển Mặt Trời", en: "It is the outermost part of the Sun's atmosphere" },
      { vi: "Là lõi đá cứng rắn bên trong Mặt Trời", en: "It is the solid rocky core of the Sun" },
      { vi: "Là một đại dương nước trên Mặt Trời", en: "It is a water ocean on the Sun" },
      { vi: "Là một hành tinh nhỏ quay gần Mặt Trời", en: "It is a small planet orbiting near the Sun" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Corona (vành nhật hoa) là phần khí quyển phía ngoài cùng của Mặt Trời.",
          en: "Correct! The corona is the outermost layer of the Sun's atmosphere." },
    no: { vi: "Chưa đúng. Vành nhật hoa corona chính là dải khí quyển phía ngoài cùng phát sáng.",
          en: "Incorrect. The solar corona is the outermost atmospheric gaseous layer of the Sun." },
    hint: { vi: "Khí quyển Mặt Trời mở rộng ra không gian ngoài cùng gọi là vành nhật hoa.",
            en: "The solar atmosphere extends into outer space as the corona." },
    src: S.nasaSunCorona,
    srcQuote: "The Sun's corona is the outermost part of the Sun's atmosphere.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-corona-visible-totality",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    /* ⚠️ Gợi ý cũ sót chữ tiếng Anh "acting" giữa câu tiếng Việt — sửa 06/08/2026. */
    q: { vi: "Tại sao con người có thể quan sát thấy vành nhật hoa phát sáng bằng mắt thường trong kỳ nhật thực toàn phần?",
         en: "Why can people observe the glowing corona during a total solar eclipse?" },
    opts: [
      { vi: "Vì Mặt Trăng đã che khuất ánh chói lọi của bề mặt Mặt Trời", en: "Because the Moon blocks out the bright light of the Sun's surface" },
      { vi: "Vì vành nhật hoa tự nhiên bùng phát nóng hơn 100 lần", en: "Because the corona naturally bursts 100 times hotter" },
      { vi: "Vì Trái Đất tiến lại gần Mặt Trời hơn", en: "Because Earth moves closer to the Sun" },
      { vi: "Vì bầu khí quyển Trái Đất biến thành kính hiển vi", en: "Because Earth's atmosphere acts as a microscope" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Bình thường bề mặt quá rực rỡ che lấp vành nhật hoa; khi Mặt Trăng chắn ánh sáng bề mặt, vành nhật hoa trắng mờ hiện ra.",
          en: "Correct! When the Moon blocks the intense surface glare, the faint white corona emerges." },
    no: { vi: "Chưa đúng. Ánh sáng bề mặt quá mạnh bình thường làm lóa mắt; khi bị che đi vành nhật hoa mới lộ rõ.",
          en: "Incorrect. Normal surface glare hides the faint corona until blocked by the Moon." },
    hint: { vi: "Mặt Trăng đóng vai trò như một đĩa chắn sáng che đi phần đĩa rực rỡ.",
            en: "The Moon acts like an occulting disk blocking the bright solar face." },
    src: S.nasaSunCorona,
    srcQuote: "During a total solar eclipse, the moon passes between Earth and the Sun. When this happens, the moon blocks out the bright light of the Sun.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-safety-totality-viewing",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Thời điểm duy nhất nào người quan sát có thể nhìn trực tiếp Mặt Trời mà không cần kính bảo vệ?",
         en: "When is the only brief period observers can look directly at the Sun without protective eclipse glasses?" },
    opts: [
      { vi: "Chỉ duy nhất trong giai đoạn toàn phần khi Mặt Trăng che kín hoàn toàn Mặt Trời", en: "Only during the brief period of totality when the Moon completely obscures the Sun's bright face" },
      { vi: "Lúc bắt đầu nhật thực một phần", en: "During the start of a partial eclipse" },
      { vi: "Bất kỳ lúc nào ban ngày", en: "At any time during daytime" },
      { vi: "Khi Mặt Trời mọc buổi sáng", en: "When the Sun rises in the morning" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Chỉ khi đĩa Mặt Trời bị che khuất hoàn toàn trong kỳ toàn phần mới an toàn để nhìn bằng mắt thường.",
          en: "Correct! Only during exact totality, when the bright face is fully hidden, is direct viewing safe." },
    no: { vi: "Chưa đúng. Mọi giai đoạn khác dù chỉ lộ ra một sợi ánh sáng Mặt Trời cũng nguy hại cho mắt nếu nhìn trực tiếp.",
          en: "Incorrect. Any partial phase exposing even a sliver of sunlight demands protective eyewear." },
    hint: { vi: "Giai đoạn này gọi là totality — khi đĩa Mặt Trời hoàn toàn bị che lấp.",
            en: "This brief window is called totality." },
    src: S.nasaEclipseSafety,
    srcQuote: "You can view the eclipse directly without proper eye protection only when the Moon completely obscures the Sun's bright face – during the brief and spectacular period known as totality.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-safety-glasses-reappear",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Ngay khi một tia ánh sáng Mặt Trời nhỏ nhất xuất hiện trở lại sau pha toàn phần, bạn phải làm gì?",
         en: "What must you do immediately as soon as even a small piece of bright Sun reappears after totality?" },
    opts: [
      { vi: "Đeo ngay kính xem nhật thực chuyên dụng trở lại để bảo vệ mắt", en: "Immediately put your eclipse glasses back on or use a handheld solar viewer" },
      { vi: "Tháo kính ra và nhìn chằm chằm vào Mặt Trời", en: "Take off your glasses and stare at the Sun" },
      { vi: "Nhắm mắt ngủ trong 2 tiếng", en: "Close your eyes and sleep for 2 hours" },
      { vi: "Dùng kính râm thông thường để nhìn", en: "Use regular sunglasses to look" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ngay khi pha toàn phần kết thúc và ánh sáng xuất hiện, phải lập tức đeo lại kính chuyên dụng.",
          en: "Correct! The moment totality ends, specialized solar filters must be worn again instantly." },
    no: { vi: "Chưa đúng. Kính râm thông thường không đủ an toàn; phải dùng kính lọc nhật thực đạt chuẩn.",
          en: "Incorrect. Regular sunglasses are unsafe; certified solar filters are strictly required." },
    hint: { vi: "Ánh sáng Mặt Trời trực tiếp ló ra sau pha toàn phần rất mạnh đối với võng mạc.",
            en: "Direct sunlight emerging post-totality carries intense radiation." },
    src: S.nasaEclipseSafety,
    srcQuote: "As soon as you see even a little bit of the bright Sun reappear after totality, immediately put your eclipse glasses back on or use a handheld solar viewer to look at the Sun.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-coincidence-size-distance-ratio",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Sự trùng hợp ngẫu nhiên nào về kích thước và khoảng cách giúp Mặt Trăng che vừa vặn Mặt Trời trên bầu trời Trái Đất?",
         en: "What coincidence of size and distance ratio allows the Moon to appear the same size as the Sun in Earth's sky?" },
    opts: [
      { vi: "Mặt Trời có đường kính lớn gấp 400 lần Mặt Trăng nhưng cũng ở xa gấp 400 lần", en: "The Sun is 400 times the diameter of the Moon, but also 400 times farther away" },
      { vi: "Mặt Trời nhỏ hơn Mặt Trăng 100 lần nhưng ở gần hơn", en: "The Sun is 100 times smaller than the Moon but closer" },
      { vi: "Mặt Trăng và Mặt Trời có kích thước thực tế hệt như nhau", en: "The Sun and Moon are physically identical in size" },
      { vi: "Mặt Trời cách Trái Đất 10 km", en: "The Sun is 10 km from Earth" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tỷ lệ kỳ diệu 400 lần kích thước đi kèm 400 lần khoảng cách khiến đĩa hai thiên thể bằng nhau trên bầu trời.",
          en: "Correct! The 400x size paired with 400x distance makes their angular diameters equal." },
    no: { vi: "Chưa đúng. Tỷ lệ 400 lần đường kính đi cùng 400 lần khoảng cách tạo nên sự trùng hợp này.",
          en: "Incorrect. The twin 400x factors of diameter and distance create this cosmic match." },
    hint: { vi: "Con số kỳ diệu lặp lại ở cả kích thước và khoảng cách là 400.",
            en: "The magic number for both scale and distance factor is 400." },
    src: S.exploratoriumEclipse,
    srcQuote: "the Sun is 400 times the diameter of the moon. But it's also 400 times farther away from us, and this relationship between size and distance makes the Sun and the moon appear the same size in the sky.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-moon-shadows-umbra-penumbra",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    /* ⚠️ Câu này ĐÃ VIẾT LẠI 06/08/2026. Bản cũ hỏi "hai vùng bóng tên là gì" — trùng
       ý với `eclipse-shadow-umbra-penumbra`, chỉ khác nguồn, nên máy không bắt được
       mà trẻ thì gặp hai lần cùng một câu. Nay hỏi TRÌNH TỰ, đúng thứ câu trích nói. */
    q: { vi: "Trong diễn biến của một kỳ nhật thực ban ngày, bóng của Mặt Trăng đổ xuống Trái Đất theo trình tự nào?",
         en: "During the progression of a daytime solar eclipse, in what order do the Moon's shadows reach Earth?" },
    opts: [
      { vi: "Bóng nửa tối (penumbra) đến trước, tiếp theo bóng tối toàn phần (umbra) xuất hiện ở đỉnh điểm nhật thực", en: "The partial shadow (penumbra) arrives first, followed by the full shadow (umbra) at the height of the eclipse" },
      { vi: "Bóng tối toàn phần (umbra) xuất hiện trước, sau đó mới tới bóng nửa tối", en: "The full shadow (umbra) appears first, followed by the partial shadow" },
      { vi: "Cả hai bóng xuất hiện đồng thời cùng một giây", en: "Both shadows arrive at the exact same second" },
      { vi: "Chỉ có duy nhất bóng mờ xuất hiện, không có bóng tối", en: "Only a faint shadow appears with no dark shadow" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Khi Mặt Trăng lướt qua Mặt Trời, bóng nửa tối penumbra chạm vào Trái Đất trước, rồi bóng tối umbra mới xuất hiện ở pha đỉnh điểm.",
          en: "Correct! As the Moon passes, the partial penumbra touches Earth first, followed by the dark umbra at eclipse peak." },
    no: { vi: "Chưa đúng. Bóng phủ dần dần: bóng nửa tối mờ nhạt trùm trước, đến đỉnh nhật thực bóng tối umbra mới phủ kín.",
          en: "Incorrect. Shadow coverage builds progressively: the lighter penumbra hits first, then the deep umbra covers at peak." },
    hint: { vi: "Hãy nghĩ đến quá trình bóng mờ xuất hiện trước khi bầu trời tối sẫm hoàn toàn.",
            en: "Think about how partial darkness precedes total darkness during the event." },
    src: S.exploratoriumEclipse,
    srcQuote: "During the day, as the moon passes in front of the Sun, it begins to cast a partial shadow (called the penumbra) onto Earth. At the height of the eclipse, the Sun's light is entirely blocked, and the moon casts a full shadow called the umbra.",
    srcChecked: "2026-08-06"
    },
    {
    term: "eclipse-phase-new-moon",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Nhật thực chỉ có thể xảy ra trong pha Trăng nào của chu kỳ Mặt Trăng?",
         en: "During which Moon phase can a solar eclipse exclusively occur?" },
    opts: [
      { vi: "Pha Trăng mới (Trăng non)", en: "The new moon phase" },
      { vi: "Pha Trăng tròn (Trăng rằm)", en: "The full moon phase" },
      { vi: "Pha Trăng bán nguyệt", en: "The half moon phase" },
      { vi: "Bất kỳ pha Trăng nào", en: "Any moon phase" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nhật thực chỉ xảy ra ở pha Trăng mới, khi Mặt Trăng nằm về phía Mặt Trời.",
          en: "Correct! Solar eclipses occur exclusively during the new moon phase when aligned toward the Sun." },
    no: { vi: "Chưa đúng. Pha Trăng tròn là thời điểm xảy ra NGUYỆT thực; nhật thực diễn ra ở pha Trăng mới.",
          en: "Incorrect. Full moon is for LUNAR eclipses; solar eclipses require the new moon phase." },
    hint: { vi: "Pha Trăng này là lúc mặt hướng về Trái Đất của Mặt Trăng không được chiếu sáng.",
            en: "In this phase the Moon's Earth-facing side is unlit." },
    src: S.nasaEclipsesMain,
    srcQuote: "Lunar eclipses occur during the full moon phase, and solar eclipses occur during the new moon phase.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-definition-earth-shadow",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Hiện tượng nguyệt thực (lunar eclipse) xảy ra khi nào?",
         en: "When does a lunar eclipse happen?" },
    opts: [
      { vi: "Khi bóng của Trái Đất che khuất Mặt Trăng", en: "When Earth's shadow obscures the Moon" },
      { vi: "Khi bóng của Mặt Trăng che khuất Mặt Trời", en: "When the Moon's shadow blocks the Sun" },
      { vi: "Khi Mặt Trăng rơi xuống Trái Đất", en: "When the Moon falls onto Earth" },
      { vi: "Khi Mặt Trời ngừng phát sáng", en: "When the Sun stops shining" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nguyệt thực xảy ra khi Trái Đất cản ánh sáng Mặt Trời và đổ bóng lên Mặt Trăng.",
          en: "Correct! A lunar eclipse happens when Earth's shadow obscures the Moon." },
    no: { vi: "Chưa đúng. Nguyệt thực là do bóng của Trái Đất che khuất Mặt Trăng — còn bóng Mặt Trăng che Mặt Trời thì là NHẬT thực.",
          en: "Incorrect. A lunar eclipse is Earth's shadow on the Moon — the Moon's shadow on the Sun is a SOLAR eclipse." },
    hint: { vi: "Trái Đất đóng vai trò làm vật cản ánh sáng chiếu đến Mặt Trăng.",
            en: "Earth acts as the blocking body casting a shadow on the Moon." },
    src: S.nasaMoonEclipses,
    srcQuote: "During a lunar eclipse, Earth's shadow obscures the Moon.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-phase-full-moon",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Nguyệt thực chỉ có thể diễn ra vào pha Trăng nào trong tháng?",
         en: "During which Moon phase can a lunar eclipse exclusively occur?" },
    opts: [
      { vi: "Pha Trăng tròn (Trăng rằm)", en: "At the full Moon phase" },
      { vi: "Pha Trăng mới (Trăng non)", en: "At the new moon phase" },
      { vi: "Pha Trăng lưỡi liềm", en: "At the crescent moon phase" },
      { vi: "Bất kỳ pha Trăng nào", en: "At any moon phase" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Nguyệt thực chỉ xảy ra vào pha Trăng tròn khi Mặt Trăng nằm đối diện Mặt Trời qua Trái Đất.",
          en: "Correct! Lunar eclipses occur exclusively during the full Moon phase." },
    no: { vi: "Chưa đúng. Nhật thực diễn ra vào Trăng mới, còn nguyệt thực xảy ra vào pha Trăng tròn.",
          en: "Incorrect. Solar eclipses occur at new moon; lunar eclipses occur at full moon." },
    hint: { vi: "Đây là thời điểm Mặt Trăng tròn và sáng nhất trên bầu trời đêm.",
            en: "This is when the Moon is fully illuminated and round in the night sky." },
    src: S.nasaMoonEclipses,
    srcQuote: "Lunar eclipses occur at the full Moon phase.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-earth-between-sun-moon",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Vị trí của Trái Đất, Mặt Trời và Mặt Trăng như thế nào khi xảy ra nguyệt thực?",
         en: "How are Earth, the Sun, and the Moon aligned during a lunar eclipse?" },
    opts: [
      { vi: "Trái Đất nằm chính giữa Mặt Trời và Mặt Trăng, đổ bóng lên bề mặt Mặt Trăng", en: "Earth is positioned precisely between the Moon and Sun, casting its shadow on the Moon" },
      { vi: "Mặt Trăng nằm ở giữa Mặt Trời và Trái Đất", en: "The Moon is positioned between the Sun and Earth" },
      { vi: "Mặt Trời nằm ở giữa Trái Đất và Mặt Trăng", en: "The Sun is positioned between Earth and Moon" },
      { vi: "Cả ba nằm vuông góc 90 độ", en: "All three form a 90-degree right angle" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Trái Đất nằm chính giữa hai thiên thể còn lại, làm bóng Trái Đất phủ lên Mặt Trăng.",
          en: "Correct! Earth sits precisely between the Sun and Moon, casting its shadow on the Moon." },
    no: { vi: "Chưa đúng. Trong nguyệt thực, Trái Đất là thiên thể đứng ở vị trí giữa.",
          en: "Incorrect. In a lunar eclipse, Earth is the central body in alignment." },
    hint: { vi: "Hành tinh của chúng ta đứng ở giữa chắn ánh sáng chiếu tới Mặt Trăng.",
            en: "Our home planet is in the middle blocking light from hitting the Moon." },
    src: S.nasaMoonEclipses,
    srcQuote: "When Earth is positioned precisely between the Moon and Sun, Earth's shadow falls upon the surface of the Moon, dimming it and sometimes turning the lunar surface a striking red over the course of a few hours.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-umbra-inner-shadow",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 1,
    q: { vi: "Trong nguyệt thực toàn phần, Mặt Trăng đi vào dải bóng nào của Trái Đất?",
         en: "During a total lunar eclipse, the Moon moves into which part of Earth's shadow?" },
    opts: [
      { vi: "Vùng bóng tối bên trong (umbra)", en: "The inner part of Earth's shadow, or the umbra" },
      { vi: "Vùng khí quyển Mặt Trời", en: "The solar atmosphere region" },
      { vi: "Vùng vành đai bão từ", en: "The magnetic storm belt" },
      { vi: "Vùng bóng màu xanh", en: "The blue shadow region" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Khi đi vào vùng bóng tối đậm nhất umbra của Trái Đất, nguyệt thực toàn phần xảy ra.",
          en: "Correct! Moving into Earth's dark inner umbral cone creates a total lunar eclipse." },
    no: { vi: "Chưa đúng. Vùng bóng tối thẫm bên trong lòng bóng Trái Đất gọi là umbra.",
          en: "Incorrect. The dark central core of Earth's shadow is called the umbra." },
    hint: { vi: "Tên tiếng Anh của vùng bóng tối thẫm này là umbra.",
            en: "The name for this central dark shadow cone is umbra." },
    src: S.nasaMoonEclipses,
    srcQuote: "The Moon moves into the inner part of Earth's shadow, or the umbra.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-rayleigh-scattering-red-light",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Tại sao các chùm ánh sáng màu đỏ và cam lại đi tới được bề mặt Mặt Trăng trong kỳ nguyệt thực?",
         en: "Why do red and orange light wavelengths reach the Moon's surface during a lunar eclipse?" },
    opts: [
      { vi: "Vì ánh sáng bước sóng ngắn (xanh, tím) bị tán xạ dễ dàng, còn bước sóng dài (đỏ, cam) truyền qua khí quyển", en: "Colors with shorter wavelengths (blues, violets) scatter more easily than colors with longer wavelengths (red, orange)" },
      { vi: "Vì Mặt Trăng tự bùng phát ngọn lửa màu đỏ", en: "Because the Moon naturally bursts into flame" },
      { vi: "Vì bề mặt Mặt Trăng làm bằng đồng đỏ", en: "Because the lunar surface is made of copper" },
      { vi: "Vì Trái Đất sơn màu đỏ cho Mặt Trăng", en: "Because Earth paints the Moon red" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ánh sáng bước sóng ngắn bị khí quyển Trái Đất tán xạ đi, chỉ có bước sóng dài (đỏ) xuyên qua chiếu tới Mặt Trăng.",
          en: "Correct! Shorter blue wavelengths scatter away while longer red wavelengths travel directly through." },
    no: { vi: "Chưa đúng. Hiện tượng tán xạ trong khí quyển giữ lại ánh sáng xanh và cho ánh sáng đỏ truyền qua.",
          en: "Incorrect. Atmospheric scattering filters blue light while transmitting longer red wavelengths." },
    hint: { vi: "Ánh sáng đỏ có bước sóng dài nên ít bị tán xạ khi đi qua tầng khí quyển.",
            en: "Red light has longer wavelengths that travel more directly through air." },
    src: S.nasaMoonEclipses,
    srcQuote: "Colors with shorter wavelengths ― the blues and violets ― scatter more easily than colors with longer wavelengths, like red and orange.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-atmosphere-dust-redder",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Mức độ bụi hoặc mây trong khí quyển Trái Đất ảnh hưởng như thế nào đến màu sắc Mặt Trăng trong kỳ nguyệt thực?",
         en: "How does dust or clouds in Earth's atmosphere affect the Moon's color during an eclipse?" },
    opts: [
      { vi: "Càng nhiều bụi hoặc mây thì Mặt Trăng càng xuất hiện màu đỏ đậm hơn", en: "The more dust or clouds in Earth's atmosphere, the redder the Moon appears" },
      { vi: "Càng nhiều bụi thì Mặt Trăng biến thành màu xanh lục", en: "More dust turns the Moon green" },
      { vi: "Bụi và mây làm Mặt Trăng biến mất hoàn toàn vĩnh viễn", en: "Dust and clouds make the Moon vanish forever" },
      { vi: "Không có bất kỳ ảnh hưởng nào", en: "It has zero effect on color" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Bụi mịn và mây trong khí quyển Trái Đất làm tăng khả năng lọc ánh sáng, khiến đĩa Trăng đỏ sẫm hơn.",
          en: "Correct! Atmospheric dust and cloud particles enhance filtering, making the Moon appear redder." },
    no: { vi: "Chưa đúng. Càng nhiều hạt bụi trong bầu khí quyển thì sắc đỏ của Mặt Trăng càng trở nên đậm hơn.",
          en: "Incorrect. More particles in Earth's atmosphere deepen the reddish hue on the Moon." },
    hint: { vi: "Bụi khí quyển lọc bớt các dải màu khác khiến chỉ còn gam màu đỏ thẫm.",
            en: "Atmospheric dust scatters other colors out, leaving deeper red tones." },
    src: S.nasaMoonEclipses,
    srcQuote: "The more dust or clouds in Earth's atmosphere during the eclipse, the redder the Moon appears.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-partial-imperfect-alignment",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Hiện tượng nguyệt thực một phần (partial lunar eclipse) diễn ra khi nào?",
         en: "When does a partial lunar eclipse happen?" },
    opts: [
      { vi: "Khi sự thẳng hàng giữa Mặt Trời, Trái Đất và Mặt Trăng không hoàn hảo, làm Mặt Trăng chỉ đi qua một phần bóng umbra", en: "An imperfect alignment of Sun, Earth and Moon results in the Moon passing through only part of Earth's umbra" },
      { vi: "Khi Mặt Trăng bị nứt làm đôi", en: "When the Moon splits in half" },
      { vi: "Khi Trái Đất thu nhỏ kích thước", en: "When Earth shrinks in volume" },
      { vi: "Khi Mặt Trời tắt đi một nửa", en: "When the Sun turns off half its light" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Do sự thẳng hàng không tuyệt đối, đĩa Mặt Trăng chỉ lướt qua một phần của vùng bóng umbra.",
          en: "Correct! Imperfect alignment causes the Moon to cross only a portion of Earth's umbra." },
    no: { vi: "Chưa đúng. Nguyệt thực một phần xảy ra do ba thiên thể không xếp thẳng hàng hoàn hảo.",
          en: "Incorrect. Imperfect spatial alignment means only part of the Moon enters the umbra." },
    hint: { vi: "Sự thẳng hàng không hoàn hảo khiến chỉ một phần đĩa Trăng chìm vào bóng tối.",
            en: "Non-ideal positioning means only a segment of the lunar disk dips into shadow." },
    src: S.nasaMoonEclipses,
    srcQuote: "An imperfect alignment of Sun, Earth and Moon results in the Moon passing through only part of Earth's umbra.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-penumbral-faint-outer-shadow",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Trong kỳ nguyệt thực nửa tối (penumbral eclipse), Mặt Trăng di chuyển qua vùng nào?",
         en: "During a penumbral lunar eclipse, where does the Moon travel?" },
    opts: [
      { vi: "Qua vùng penumbra — dải bóng mờ phía ngoài cùng của Trái Đất", en: "The Moon travels through Earth's penumbra, or the faint outer part of its shadow" },
      { vi: "Vào lõi Trái Đất", en: "Travels inside Earth's core" },
      { vi: "Ra bên ngoài Dải Ngân Hà", en: "Travels outside the Milky Way" },
      { vi: "Vào bầu khí quyển Mặt Trời", en: "Travels into the solar atmosphere" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Mặt Trăng đi qua vùng bóng nửa tối mờ nhạt nên độ sáng chỉ giảm nhẹ, khó nhận biết.",
          en: "Correct! Passing through the faint outer penumbra causes a barely noticeable dimming." },
    no: { vi: "Chưa đúng. Vùng bóng phía ngoài mờ nhạt của Trái Đất được gọi là penumbra.",
          en: "Incorrect. The faint outer fringe of Earth's shadow is called the penumbra." },
    hint: { vi: "Hiện tượng này khiến Mặt Trăng chỉ tối đi rất nhẹ.",
            en: "This eclipse type causes only a slight, subtle darkening of the Moon." },
    src: S.nasaMoonEclipses,
    srcQuote: "The Moon travels through Earth's penumbra, or the faint outer part of its shadow.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-red-filtered-atmosphere",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 2,
    q: { vi: "Tại sao Mặt Trăng lại chuyển sang màu đỏ hoặc cam rực rỡ trong kỳ nguyệt thực toàn phần?",
         en: "Why does the Moon appear red or orange during a total lunar eclipse?" },
    opts: [
      { vi: "Vì ánh sáng Mặt Trời được lọc qua một lớp dày khí quyển Trái Đất trước khi tới Mặt Trăng", en: "Because any sunlight that's not blocked by our planet is filtered through a thick slice of Earth's atmosphere on its way to the lunar surface" },
      { vi: "Vì Mặt Trăng bị thiêu rụi bởi lửa", en: "Because the Moon burns in fire" },
      { vi: "Vì Mặt Trăng đổi sang màu sơn đỏ", en: "Because the Moon changes its paint color" },
      { vi: "Vì Mặt Trời sơn màu đỏ lên vũ trụ", en: "Because the Sun paints space red" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Ánh sáng Mặt Trời khúc xạ qua lớp khí quyển Trái Đất được lọc giữ lại dải đỏ cam chiếu lên đĩa Trăng.",
          en: "Correct! Sunlight refracts and filters through Earth's thick atmosphere onto the Moon." },
    no: { vi: "Chưa đúng. Khí quyển Trái Đất đóng vai trò bộ lọc, tán xạ sắc xanh và bẻ cong dải ánh sáng đỏ.",
          en: "Incorrect. Earth's atmosphere acts as a filter scattering blue and bending red light." },
    hint: { vi: "Chính bầu khí quyển Trái Đất lọc ánh sáng trước khi nó rọi tới Mặt Trăng.",
            en: "Earth's atmospheric layer filters the light traveling toward the Moon." },
    src: S.nasaMoonEclipses,
    srcQuote: "During a lunar eclipse, the Moon appears red or orange because any sunlight that's not blocked by our planet is filtered through a thick slice of Earth's atmosphere on its way to the lunar surface.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-sunrises-sunsets-projected",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Ánh sáng màu đỏ cam chiếu lên Mặt Trăng khi nguyệt thực được ví như hình ảnh nào?",
         en: "How is the reddish light projected onto the Moon during a lunar eclipse described?" },
    opts: [
      { vi: "Giống như tất cả các bình minh và hoàng hôn trên Trái Đất cùng chiếu lên Mặt Trăng", en: "It's as if all the world's sunrises and sunsets are projected onto the Moon" },
      { vi: "Giống như ánh đèn laser nhân tạo", en: "Like artificial laser beams" },
      { vi: "Giống như ngọn đèn đường ban đêm", en: "Like a street light at night" },
      { vi: "Giống như ánh sáng từ chiếc gương soi", en: "Like light reflecting off a mirror" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Sắc đỏ nguyệt thực chính là tổng hòa ánh sáng hoàng hôn và bình minh từ khắp vòng quanh Trái Đất.",
          en: "Correct! The reddish glow represents the combined light of all Earth's sunrises and sunsets." },
    no: { vi: "Chưa đúng. Ánh sáng đỏ lọc qua rìa khí quyển Trái Đất tương tự như ánh hoàng hôn đỏ thắm.",
          en: "Incorrect. Red light filtered around Earth's limb mirrors the glow of sunset and sunrise." },
    hint: { vi: "Hãy nghĩ đến màu đỏ cam đẹp đẽ của buổi chiều tà hoàng hôn.",
            en: "Think of the rich reddish-orange colors seen at sunset and sunrise." },
    src: S.nasaMoonEclipses,
    srcQuote: "It's as if all the world's sunrises and sunsets are projected onto the Moon.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-difference-name-darker",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Mẹo đơn giản nhất để phân biệt Nhật thực và Nguyệt thực qua tên gọi là gì?",
         en: "What is an easy way to remember the difference between a solar and lunar eclipse by name?" },
    opts: [
      { vi: "Tên gọi cho biết thiên thể nào bị tối đi: nhật thực thì Mặt Trời tối, nguyệt thực thì Mặt Trăng tối", en: "The name tells you what gets darker: in a solar eclipse the Sun gets darker, in a lunar eclipse the Moon gets darker" },
      { vi: "Tên gọi cho biết thiên thể nào biến thành màu xanh", en: "The name tells you which body turns blue" },
      { vi: "Tên gọi cho biết hiện tượng diễn ra ở mùa nào", en: "The name tells you which season it occurs in" },
      { vi: "Tên gọi không mang ý nghĩa nào", en: "The name holds zero meaning" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Tên gọi chỉ rõ đối tượng bị tối đi: Nhật thực thì Mặt Trời (Nhật) tối, Nguyệt thực thì Mặt Trăng (Nguyệt) tối.",
          en: "Correct! The name indicates what darkens: solar = Sun darkens, lunar = Moon darkens." },
    no: { vi: "Chưa đúng. Hãy nhớ quy tắc: tên gọi chỉ ra chính thiên thể bị che tối trong hiện tượng.",
          en: "Incorrect. Remember the simple rule: the name reveals which body gets darker." },
    hint: { vi: "Nhật có nghĩa là Mặt Trời, Nguyệt có nghĩa là Mặt Trăng.",
            en: "Solar refers to the Sun, and lunar refers to the Moon." },
    src: S.nasaSpaceplaceEclipses,
    srcQuote: "The name tells you what gets darker when the eclipse happens. In a solar eclipse, the Sun gets darker. In a lunar eclipse, the Moon gets darker.",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-shadow-huge-earth",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    /* ⚠️ Gợi ý cũ có con số "gần 4 lần" mà câu trích KHÔNG nói — đã bỏ 06/08/2026.
       Luật dự án: mọi con số phải trích được câu nguồn nói ra nó. */
    q: { vi: "Đặc điểm kích thước bóng của Trái Đất đổ lên Mặt Trăng khi xảy ra nguyệt thực là gì?",
         en: "What is the size characteristic of Earth's shadow cast onto the Moon during a lunar eclipse?" },
    opts: [
      { vi: "Bóng của Trái Đất đổ lên Mặt Trăng rất khổng lồ", en: "The shadow cast by the earth onto the moon is huge!" },
      { vi: "Bóng của Trái Đất nhỏ như một hạt cát", en: "The shadow is as small as a grain of sand" },
      { vi: "Bóng của Trái Đất có hình tam giác nhỏ", en: "The shadow is a small triangle" },
      { vi: "Trái Đất không tạo ra bóng nào cả", en: "Earth casts no shadow at all" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Vì Trái Đất lớn hơn Mặt Trăng rất nhiều, bóng Trái Đất đổ vào không gian vô cùng rộng lớn.",
          en: "Correct! Because Earth is much larger than the Moon, its shadow in space is huge." },
    no: { vi: "Chưa đúng. Trái Đất có kích thước lớn nên nón bóng tối đổ ra không gian vô cùng khổng lồ.",
          en: "Incorrect. Earth's large physical size produces a massive shadow cone in space." },
    hint: { vi: "Trái Đất lớn hơn Mặt Trăng rất nhiều.",
            en: "Earth is much larger than the Moon." },
    src: S.exploratoriumCup,
    srcQuote: "The shadow cast by the earth onto the moon is huge!",
    srcChecked: "2026-08-06"
    },
    {
    term: "lunar-night-side-visibility",
    topic: { vi: "Thiên Văn", en: "Astronomy" },
    lv: 3,
    q: { vi: "Ai trên Trái Đất có thể quan sát được hiện tượng nguyệt thực khi nó diễn ra?",
         en: "Who on Earth can see a lunar eclipse when it occurs?" },
    opts: [
      { vi: "Bất kỳ ai ở nửa bán cầu đang là ban đêm của Trái Đất, với bầu trời quang mây", en: "Anyone on the night side of Earth with clear skies at the right time" },
      { vi: "Chỉ duy nhất một người ở xích đạo", en: "Only one single person at the equator" },
      { vi: "Chỉ những người ở cực Bắc vào ban ngày", en: "Only people at the North Pole during daytime" },
      { vi: "Không ai trên Trái Đất có thể nhìn thấy", en: "Nobody on Earth can see it" }
    ],
    a: 0,
    ok: { vi: "Chính xác! Khác với nhật thực chỉ nhìn được trên một dải hẹp, nguyệt thực quan sát được từ toàn bộ nửa cầu ban đêm.",
          en: "Correct! Unlike narrow solar eclipse paths, lunar eclipses are visible from the entire night hemisphere." },
    no: { vi: "Chưa đúng. Toàn bộ những người nằm ở nửa cầu đang là ban đêm đều có thể ngắm nguyệt thực.",
          en: "Incorrect. Everyone on the night-side half of the globe can view a lunar eclipse." },
    hint: { vi: "Toàn bộ nửa cầu Trái Đất đang là ban đêm có thể quan sát sự kiện này.",
            en: "The entire night-side hemisphere of Earth gets a view of the event." },
    src: S.exploratoriumCup,
    srcQuote: "You can see a lunar eclipse if you're on the night side of Earth with clear skies at the right time of the event.",
    srcChecked: "2026-08-06"
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
