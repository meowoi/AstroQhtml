/* ══════════════════════════════════════════════════════════════════════════
   AstroQLab — CHỖ DUY NHẤT khai 6 thẻ hoạt động của Phòng Nghiên Cứu (MOD-05):
   mã, trạng thái, nội dung song ngữ, và NGUỒN cho từng con số.

   Dùng bởi lab.html. Nạp SAU js/ui-common.js.
   Đề xuất đầy đủ + bảng nguồn: docs/proposals/2026-08-12-de-xuat-phong-nghien-cuu-hap-dan.md

   ⚠️⚠️ BA LUẬT CỦA CẢ FILE, mỗi luật đã trả giá ở nơi khác trong dự án:

   ① CHỈ DÙNG TỈ LỆ VÀ CÂN NẶNG, TUYỆT ĐỐI KHÔNG DÙNG `m/s²`.
      Không một trang NASA viết cho trẻ nào dùng đơn vị đó cho việc này — họ nói
      "một phần sáu", "100 pound thành 38 pound". Và 10 con số `gravity:` trong
      `explorer.html` (Sao Thuỷ 3,7 · Mặt Trăng 1,6 …) KHÔNG dẫn nguồn nào:
      `grep nasa.gov` cả file đó ra ĐÚNG 1 kết quả. Đừng chép chúng sang đây.

   ② CHỈ HIỆN NƠI CÓ NGUỒN — hôm nay là BỐN nơi, không phải mười.
      Bốn nơi đã đủ dạy bài học (nhẹ hơn nhiều · nhẹ hơn · mốc · nặng hơn nhiều),
      và bốn nơi có nguồn tốt hơn mười nơi trong đó sáu con số không ai chống lưng.
      ⚠️ SAO HOẢ KHÔNG NẰM TRONG BỐN NƠI ĐÓ. Trang Space Place chỉ nhắc Sao Hoả
      khi nói về KHỐI LƯỢNG ("same mass on Mars or Jupiter"), không cho tỉ lệ CÂN
      NẶNG nào. Thêm Sao Hoả vào là bịa một con số ở đúng chỗ trẻ đọc kỹ nhất.

   ③ KHÔNG HIỆN THỜI GIAN RƠI TUYỆT ĐỐI (không "0,57 giây").
      Đó là một khẳng định định lượng cần nguồn, mà bài học không cần nó: điều
      TN-01 dạy là CÁI NÀO CHẠM ĐẤT TRƯỚC. Phần vẽ vì thế chỉ cần TỈ LỆ thời gian
      giữa hai nơi, và tỉ lệ đó suy được từ chính con số có nguồn (t ∝ 1/√g nên
      Mặt Trăng lâu hơn Trái Đất √6 ≈ 2,45 lần) — xem `js/lab-drop.js`.

   ⚠️ HAI ĐỘ SÂU LỜI GIẢI THÍCH (`say` ngắn + `more` dài) là khuôn của CHÍNH NASA:
      cùng chủ đề Microgravity họ xuất bản HAI bản, K-4 và 5-8. Dải tuổi của dự án
      là 8–15 nên nó vắt qua đúng hai bản đó. Trẻ TỰ bấm "Tìm hiểu thêm"; KHÔNG
      đoán theo `level` của server — `level` đo THỜI GIAN ĐÃ CHƠI, không đo tuổi,
      nên một đứa 15 tuổi vừa đăng ký (level 1) sẽ nhận bản viết cho trẻ 8 tuổi.

   Thêm một thẻ: thêm một phần tử vào `CARDS` + khoá chữ ở CẢ `vi` và `en`.
   Mã `LAB-nn` GHI CỐ ĐỊNH, không đánh số lại theo vị trí — cùng bài học với
   `ARCADE-nn` của games.html và `MOD-nn` của dashboard (số hiệu đã đi vào tài
   liệu và cách người dùng gọi tên).
   ══════════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  /* ── BỐN NƠI CÓ NGUỒN ──────────────────────────────────────────────────
     `ratio` = cân nặng ở đó so với Trái Đất. Chỉ dùng cho phần VẼ và cho câu
     "cân của em"; không bao giờ in ra dưới dạng m/s².
     ⚠️ Mặt Trăng khai `1/6` bằng phép chia, KHÔNG gõ 0.1667 — nguồn nói "một
        phần sáu", nên giữ đúng hình dạng con số của nguồn. */
  var PLACES = [
    { id: "earth",   ratio: 1,        base: true,  src: null },
    { id: "moon",    ratio: 1 / 6,    src: "moonfacts" },
    { id: "mercury", ratio: 0.38,     src: "weigh" },   // 100 lb → 38 lb
    { id: "jupiter", ratio: 2.53,     src: "weigh" }    // 100 lb → 253 lb
  ];

  /* ── NGUỒN: khoá → URL. Câu trích nguyên văn để trong `quote` (không dịch —
     nó là bằng chứng, dịch là mất tư cách bằng chứng). Cả 4 URL kiểm 200 ngày
     12/08/2026. ── */
  var SRC = {
    apollo15: {
      url: "https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop/",
      quote: "Because they were essentially in a vacuum, there was no air resistance " +
             "and the feather fell at the same rate as the hammer"
    },
    moonfacts: {
      url: "https://science.nasa.gov/moon/facts/",
      quote: "the gravity on the surface of the Moon is one-sixth of Earth's"
    },
    weigh: {
      url: "https://spaceplace.nasa.gov/planets-weight/en/",
      quote: "If you weigh 100 pounds on Earth, you would weigh only 38 pounds on " +
             "Mercury. If, on the other hand, you were on heavy Jupiter, you would " +
             "weigh a whopping 253 pounds!"
    },
    /* ⚠️⚠️ URL CŨ ĐÃ CHẾT — `nasa.gov/audience/foreducators/microgravity/index.html`
       trả **404** (kiểm 12/08/2026). Đây là lần thứ hai dự án gặp một nguồn NASA tự
       chết sau lượt dời cấu trúc site của họ (lần đầu: bảng NSSDC Planetary Fact
       Sheet trả 307 về www.nasa.gov/nssdc/). ⇒ Mọi URL nguồn phải KIỂM 200 LẠI, đừng
       tin một URL đã từng đúng: `scratchpad/check_lab_sources.py` làm việc đó.
       ⚠️ VÀ TRANG MỚI KHÔNG NÓI "90%". Bản đầu của `more_float` khẳng định *"trọng
       lực Trái Đất vẫn còn khoảng 90%"* — con số đó lấy từ trang ĐÃ CHẾT và trang
       sống KHÔNG phát biểu nó, nên đã bỏ. Thay bằng đúng câu trang nói: trường hấp
       dẫn ở đó *"still quite strong"*, và độ cao **120–360 dặm**. */
    /* ⚠️ Cả hai nguồn dưới kiểm 200 ngày 12/08/2026 bằng
       `scratchpad/check_lab_sources.py`. `spaceplace` là trang NASA viết CHO TRẺ EM
       nên nó đúng độ tuổi của dự án — cùng lý do `term_gravity` đã dùng nó. */
    bluesky: {
      url: "https://spaceplace.nasa.gov/blue-sky/en/",
      quote: "Sunlight reaches Earth's atmosphere and is scattered in all directions " +
             "by all the gases and particles in the air. Blue light is scattered more " +
             "than the other colors because it travels as shorter, smaller waves."
    },
    water: {
      url: "https://spaceplace.nasa.gov/water/en/",
      quote: "Water covers 71 percent of Earth's surface. And almost all of it—96.5 " +
             "percent—is salt water. ... Just 3.5 percent of the water on Earth is " +
             "fresh water we can drink. And most of that fresh water, 68 percent, is " +
             "trapped in ice and glaciers."
    },
    micro: {
      url: "https://www.nasa.gov/general/what-is-microgravity/",
      quote: "That's because they're all falling together: the apple, the astronaut " +
             "and the station. But they're not falling towards Earth, they're falling " +
             "around it. Because they're all falling at the same rate, objects inside " +
             "of the station appear to float."
    }
  };

  /* ── SÁU THẺ ──────────────────────────────────────────────────────────────
     kind : "drop"   — tháp thả rơi (hai vật, chọn nơi)
            "float"  — buông một vật trong trạm
            "weight" — cân của em ở đâu
            null     — chưa dựng
     lock : null (miễn phí) | khoá của js/locks.js
     ⚠️ Ba thẻ đầu dùng CHUNG một engine (`js/lab-drop.js`): cả ba đều là "vật
        rơi trong một trường trọng lực", khác nhau ở CÂU HỎI và CÁI GÌ RƠI. */
  var CARDS = [
    { code: "LAB-01", id: "tower",  kind: "drop",   ic: "🔨", tone: "cyan",
      lock: null,           places: ["earth", "moon"], src: ["apollo15"] },
    { code: "LAB-02", id: "float",  kind: "float",  ic: "🧑‍🚀", tone: "purple",
      lock: "lab:float",    src: ["micro"] },
    { code: "LAB-03", id: "weigh",  kind: "weight", ic: "⚖️", tone: "gold",
      lock: "lab:weigh",    places: ["earth", "moon", "mercury", "jupiter"],
      src: ["moonfacts", "weigh"] },
    /* ⚠️ LAB-07 và LAB-08 KHÔNG phải về hấp dẫn — chúng là vật lý ánh sáng và
       nước/hoá học ở mức trẻ em. Lưới thẻ chịu được điều đó: mỗi thẻ MỘT loại hoạt
       động, nên thêm môn mới không phải đổi tên khu ngoài (chính lý do chủ dự án
       chốt hình dạng lưới thẻ). Mã LAB-nn cấp theo số kế tiếp, KHÔNG chèn vào giữa. */
    { code: "LAB-07", id: "sky",    kind: "sky",   ic: "🌇", tone: "gold", tall: true,
      lock: "lab:sky",      places: ["noon", "evening", "horizon"], src: ["bluesky"] },
    { code: "LAB-08", id: "drops",  kind: "drops", ic: "💧", tone: "cyan",
      lock: "lab:drops",    places: ["all", "salt", "fresh", "ice"], src: ["water"] },
    { code: "LAB-04", id: "throw",  kind: null, ic: "🎯", tone: "lime",  lock: "lab:throw" },
    { code: "LAB-05", id: "tide",   kind: null, ic: "🌊", tone: "cyan",  lock: "lab:tide"  },
    { code: "LAB-06", id: "mix",    kind: null, ic: "⚗️", tone: "mag",   lock: "lab:mix"   }
  ];

  var T = {
    vi: {
      /* ── tên nơi + vật ── */
      p_earth: "Trái Đất", p_moon: "Mặt Trăng", p_mercury: "Sao Thuỷ", p_jupiter: "Sao Mộc",
      o_hammer: "Búa", o_feather: "Lông chim", o_ball: "Quả bóng", o_apple: "Quả táo",

      /* ── LAB-01 ── */
      t_tower: "Tháp thả rơi",
      d_tower: "Thả búa và lông chim cùng lúc. Cái nào chạm đất trước?",
      q_tower: "Trên Mặt Trăng, búa nặng hơn lông chim rất nhiều. Em nghĩ cái nào chạm đất trước?",
      say_tower_moon: "Cùng lúc! Trên Mặt Trăng không có không khí, nên chẳng có gì cản lông chim lại.",
      say_tower_earth: "Ở đây lông chim chậm hơn hẳn — nhưng không phải vì nó nhẹ, mà vì KHÔNG KHÍ cản nó.",
      more_tower: "Phi hành gia David Scott đã làm đúng thí nghiệm này trên Mặt Trăng năm 1971, với một cái búa địa chất 1,32 kg và một cái lông chim ưng 0,03 kg. Nặng gấp 44 lần mà vẫn chạm đất cùng lúc. Galileo đã kết luận điều đó từ mấy trăm năm trước: mọi vật thả cùng lúc thì rơi nhanh như nhau, bất kể khối lượng.",
      find_tower: "Không có không khí thì mọi vật rơi nhanh như nhau.",

      /* ── LAB-02 ── */
      t_float: "Vì sao phi hành gia trôi",
      d_float: "Buông một quả táo trong trạm vũ trụ. Nó sẽ rơi xuống chứ?",
      q_float: "Trong trạm vũ trụ, em buông một quả táo ra. Em nghĩ nó làm gì?",
      say_float: "Nó trôi cạnh em! Không phải vì hết trọng lực — mà vì em VÀ quả táo đang rơi cùng nhau.",
      more_float: "Rất nhiều người tưởng trong không gian không có trọng lực. Nhưng trạm chỉ bay cách mặt đất khoảng 120–360 dặm, và ở đó lực hấp dẫn vẫn còn rất mạnh. Trạm cũng không hề đứng yên: nó lao đi 17.500 dặm một giờ, nên nó rơi mà cứ đi VÒNG QUANH Trái Đất chứ không chạm xuống. Em, quả táo và cả cái trạm đều rơi cùng một nhịp — nên nhìn nhau thì thấy như đang trôi. Khối lượng của em không đổi một chút nào; chỉ có cái cân là chỉ số 0.",
      find_float: "Trôi trong không gian là đang rơi cùng nhau, không phải hết trọng lực.",

      /* ── LAB-03 ── */
      t_weigh: "Cân của em ở đâu",
      d_weigh: "Cùng một em, bốn nơi khác nhau. Cân chỉ số khác nhau.",
      q_weigh: "Chọn một nơi rồi xem cái cân nói gì.",
      say_weigh: "Cân đổi, nhưng lượng vật chất trong người em thì KHÔNG đổi.",
      more_weigh: "Cân nặng là lực mà một nơi kéo em xuống, nên nó đổi theo nơi. Khối lượng là lượng vật chất làm nên em, và nó ở đâu cũng vậy — trên Sao Hoả hay Sao Mộc thì khối lượng của em vẫn y như trên Trái Đất. Đó là lý do phi hành gia không hề gầy đi khi bay lên trạm, dù cái cân ở đó chỉ số 0.\n\nCÓ MỘT CÔNG THỨC, và nó chỉ là một phép nhân:\n\n    cân nặng ở đó = cân nặng ở Trái Đất × tỉ lệ trọng lực của nơi đó\n\nMặt Trăng có tỉ lệ 1/6, Sao Thuỷ 0,38 và Sao Mộc 2,53. Nên nếu ở Trái Đất em nặng 30 kg thì trên Sao Mộc cái cân chỉ 30 × 2,53 = 75,9 kg — em thử gõ cân nặng thật của mình vào ô bên trên rồi tự nhân xem có khớp không nhé. Chính NASA cũng làm đúng phép nhân này: họ viết nếu em nặng 100 pound ở Trái Đất thì ở Sao Thuỷ em nặng 38 pound (100 × 0,38), còn ở Sao Mộc là 253 pound (100 × 2,53).",
      find_weigh: "Cân nặng đổi theo nơi; khối lượng thì không.",

      /* ── LAB-07 · vật lý ánh sáng ── */
      p_noon: "Giữa trưa", p_evening: "Chiều muộn", p_horizon: "Sát chân trời",
      t_sky: "Vì sao trời xanh",
      d_sky: "Kéo Mặt Trời xuống thấp dần. Trời đổi màu — vì sao?",
      q_sky: "Chọn một lúc trong ngày rồi xem trời màu gì.",
      say_sky_noon: "Giữa trưa trời xanh nhất: ánh sáng xanh bị TÁN XẠ đi khắp nơi trong không khí, nên nhìn đâu cũng thấy xanh.",
      say_sky_evening: "Mặt Trời thấp hơn thì ánh sáng phải đi qua nhiều không khí hơn, nên màu xanh bị tán xạ mất dần.",
      say_sky_horizon: "Sát chân trời, xanh bị tán xạ hết — chỉ còn đỏ và vàng đi thẳng tới mắt em. Đó là ráng chiều.",
      more_sky: "Ánh sáng Mặt Trời chứa đủ mọi màu. Khi tới khí quyển, nó bị các chất khí và hạt bụi trong không khí tán xạ ra mọi hướng. Màu xanh bị tán xạ nhiều hơn các màu khác vì nó đi thành những đợt sóng NGẮN HƠN, NHỎ HƠN — nên bầu trời phần lớn thời gian có màu xanh. Lúc Mặt Trời xuống thấp, ánh sáng của nó phải xuyên qua nhiều khí quyển hơn để tới được em, xanh bị tán xạ đi càng nhiều, và đỏ với vàng mới là những màu đi thẳng qua được.",
      find_sky: "Trời xanh vì ánh sáng xanh bị không khí tán xạ mạnh nhất.",

      /* ── LAB-08 · nước & muối ── */
      p_all: "Tất cả nước", p_salt: "Nước mặn", p_fresh: "Nước ngọt", p_ice: "Đóng thành băng",
      t_drops: "Nước của Trái Đất",
      d_drops: "Một trăm giọt nước. Bao nhiêu giọt em uống được?",
      q_drops: "Bấm lần lượt từng nút để xem 100 giọt nước chia ra thế nào.",
      say_drops_all: "Nước phủ 71% bề mặt Trái Đất. Coi tất cả nước đó là 100 giọt nhé.",
      say_drops_salt: "96,5 giọt là nước MẶN — chủ yếu là muối natri clorua, đúng thứ muối ta cho vào thức ăn.",
      say_drops_fresh: "Chỉ 3,5 giọt là nước ngọt uống được. Ít đến thế thôi.",
      say_drops_ice: "Và 68% chỗ nước ngọt đó lại đang đóng thành băng và sông băng.",
      more_drops: "Nước ở khắp nơi: trong đất, trong đại dương, trong khí quyển, và trong cả cơ thể sống — người em phần lớn là nước. Nước phủ 71% bề mặt Trái Đất, nhưng gần như tất cả — 96,5% — là nước mặn. Muối trong đó chủ yếu là natri clorua, cùng loại muối ta rắc vào thức ăn. Chỉ 3,5% lượng nước trên Trái Đất là nước ngọt uống được, mà phần lớn chỗ đó — 68% — lại bị giữ trong băng và sông băng.",
      find_drops: "Trong 100 giọt nước của Trái Đất, chỉ hơn 3 giọt là uống được.",

      /* ── ba thẻ chưa dựng ── */
      t_throw: "Ném xa ở các nơi", d_throw: "Cùng một cú ném, trọng lực khác nhau thì bay xa khác nhau.",
      t_tide: "Thuỷ triều & Mặt Trăng", d_tide: "Kéo Mặt Trăng xa rồi gần, xem nước biển đổi thế nào.",
      t_mix: "Trộn nguyên tố", d_mix: "Ghép hai nguyên tố xem ra chất gì.",

      /* ── giao diện ── */
      ui_pick_place: "Chọn nơi:",
      ui_drop: "Thả!",
      ui_slow: "Xem chậm",
      ui_slow_off: "Xem tốc độ thường",
      ui_strobe: "Mỗi vệt mờ là vị trí sau cùng một khoảng thời gian",
      ui_again: "Làm lại",
      ui_more: "Tìm hiểu thêm",
      ui_less: "Thu lại",
      ui_back_grid: "Về Phòng Nghiên Cứu",
      ui_guess_same: "Cùng lúc",
      ui_guess_hammer: "Búa trước",
      ui_guess_feather: "Lông chim trước",
      ui_guess_fall: "Rơi xuống sàn",
      ui_guess_float: "Trôi lơ lửng",
      ui_result_same: "Cùng lúc!",
      ui_result_hammer: "Búa chạm đất trước.",
      ui_finding: "Phát hiện của em",
      ui_source: "Nguồn:",
      ui_scale: "Cân chỉ",
      ui_your_kg: "Cân nặng của em ở Trái Đất:",
      ui_kg: "kg",
      ui_mass: "Khối lượng",
      ui_unchanged: "không đổi",
      ui_free_badge: "MIỄN PHÍ",
      ui_soon_badge: "SẮP RA MẮT",
      ui_you_weigh: "Nếu ở Trái Đất em nặng 30 kg thì ở đây cân chỉ:"
    },
    en: {
      p_earth: "Earth", p_moon: "the Moon", p_mercury: "Mercury", p_jupiter: "Jupiter",
      o_hammer: "Hammer", o_feather: "Feather", o_ball: "Ball", o_apple: "Apple",

      t_tower: "The drop tower",
      d_tower: "Drop a hammer and a feather together. Which one lands first?",
      q_tower: "On the Moon, the hammer is far heavier than the feather. Which do you think lands first?",
      say_tower_moon: "Together! There's no air on the Moon, so nothing slows the feather down.",
      say_tower_earth: "Here the feather is much slower — not because it's light, but because AIR holds it back.",
      more_tower: "Astronaut David Scott ran this exact experiment on the Moon in 1971, with a 1.32-kg geological hammer and a 0.03-kg falcon feather. Forty-four times heavier, and they still landed together. Galileo worked this out hundreds of years earlier: objects released together fall at the same rate, whatever their mass.",
      find_tower: "With no air, everything falls at the same rate.",

      t_float: "Why astronauts float",
      d_float: "Let go of an apple inside a space station. Will it drop?",
      q_float: "Inside the station you let go of an apple. What do you think it does?",
      say_float: "It floats beside you! Not because gravity is gone — because you AND the apple are falling together.",
      more_float: "Lots of people think there is no gravity in space. But the station orbits only about 120–360 miles above Earth's surface, and the gravitational field is still quite strong up there. The station isn't parked either: it travels at 17,500 miles per hour, so it falls but keeps going AROUND Earth instead of hitting it. You, the apple and the whole station all fall at the same rate — so to each other you look like you're floating. Your mass doesn't change at all; it's only a scale that would read zero.",
      find_float: "Floating in space means falling together, not gravity switching off.",

      t_weigh: "What you weigh, and where",
      d_weigh: "The same you, four different places. The scale reads differently.",
      q_weigh: "Pick a place and see what the scale says.",
      say_weigh: "The scale changes, but how much stuff you're made of does NOT.",
      more_weigh: "Weight is the pull a place has on you, so it changes from place to place. Mass is how much stuff you are made of, and that is the same everywhere — on Mars or on Jupiter your mass is exactly what it is on Earth. That's why astronauts don't get thinner on the way up, even though a scale up there would read zero.\n\nTHERE IS A FORMULA, and it is just a multiplication:\n\n    weight there = weight on Earth × that place's gravity ratio\n\nThe Moon's ratio is 1/6, Mercury's is 0.38 and Jupiter's is 2.53. So if you weigh 30 kg on Earth, a scale on Jupiter reads 30 × 2.53 = 75.9 kg — type your own weight in the box above and do the multiplication yourself to check. NASA does this very multiplication: they write that if you weigh 100 pounds on Earth you would weigh 38 pounds on Mercury (100 × 0.38) and 253 pounds on Jupiter (100 × 2.53).",
      find_weigh: "Weight changes with where you are; mass does not.",

      p_noon: "Midday", p_evening: "Late afternoon", p_horizon: "At the horizon",
      t_sky: "Why the sky is blue",
      d_sky: "Bring the Sun lower and lower. The sky changes colour — why?",
      q_sky: "Pick a time of day and see what colour the sky is.",
      say_sky_noon: "At midday the sky is at its bluest: blue light is SCATTERED all around by the air, so you see blue wherever you look.",
      say_sky_evening: "With the Sun lower, its light travels through more air, so the blue gets scattered away.",
      say_sky_horizon: "Near the horizon the blue is all scattered away — only red and yellow come straight to your eyes. That's a sunset.",
      more_sky: "Sunlight contains every colour. When it reaches the atmosphere it is scattered in all directions by the gases and particles in the air. Blue light is scattered more than the other colours because it travels as SHORTER, SMALLER waves — which is why the sky is blue most of the time. As the Sun gets lower, its light passes through more atmosphere to reach you, even more of the blue is scattered away, and the reds and yellows are what pass straight through.",
      find_sky: "The sky is blue because air scatters blue light the most.",

      p_all: "All the water", p_salt: "Salt water", p_fresh: "Fresh water", p_ice: "Locked in ice",
      t_drops: "Earth's water",
      d_drops: "One hundred drops of water. How many can you drink?",
      q_drops: "Press each button in turn to see how 100 drops split up.",
      say_drops_all: "Water covers 71% of Earth's surface. Let's call all of it 100 drops.",
      say_drops_salt: "96.5 drops are SALT water — mostly sodium chloride, the very salt we put on our food.",
      say_drops_fresh: "Only 3.5 drops are fresh water you could drink. That little.",
      say_drops_ice: "And 68% of that fresh water is locked up in ice and glaciers.",
      more_drops: "Water is everywhere: in the ground, in the oceans, in the atmosphere, and in living things — your body is mostly water. Water covers 71 percent of Earth's surface, but almost all of it — 96.5 percent — is salt water. That salt is mostly sodium chloride, the same salt we add to our food. Just 3.5 percent of Earth's water is fresh water we can drink, and most of that, 68 percent, is trapped in ice and glaciers.",
      find_drops: "Of Earth's 100 drops of water, only about 3 are drinkable.",

      t_throw: "Throwing distance", d_throw: "The same throw, different gravity, different distance.",
      t_tide: "Tides and the Moon", d_tide: "Pull the Moon closer and further, watch the sea change.",
      t_mix: "Mix elements", d_mix: "Put two elements together and see what you get.",

      ui_pick_place: "Pick a place:",
      ui_drop: "Drop!",
      ui_slow: "Slow motion",
      ui_slow_off: "Normal speed",
      ui_strobe: "Each faint copy is where it was after the same slice of time",
      ui_again: "Again",
      ui_more: "Tell me more",
      ui_less: "Close",
      ui_back_grid: "Back to the Research Lab",
      ui_guess_same: "Together",
      ui_guess_hammer: "Hammer first",
      ui_guess_feather: "Feather first",
      ui_guess_fall: "Drops to the floor",
      ui_guess_float: "Floats in place",
      ui_result_same: "Together!",
      ui_result_hammer: "The hammer landed first.",
      ui_finding: "What you found",
      ui_source: "Source:",
      ui_scale: "Scale reads",
      ui_your_kg: "Your weight on Earth:",
      ui_kg: "kg",
      ui_mass: "Mass",
      ui_unchanged: "unchanged",
      ui_free_badge: "FREE",
      ui_soon_badge: "COMING SOON",
      ui_you_weigh: "If you weigh 30 kg on Earth, here the scale reads:"
    }
  };

  function lang() {
    return (window.AstroQ && AstroQ.getLang && AstroQ.getLang() === "en") ? "en" : "vi";
  }
  function t(k, L) {
    var d = T[L || lang()];
    return (d && d[k] != null) ? d[k] : k;
  }
  function card(id) {
    for (var i = 0; i < CARDS.length; i++) if (CARDS[i].id === id) return CARDS[i];
    return null;
  }
  function place(id) {
    for (var i = 0; i < PLACES.length; i++) if (PLACES[i].id === id) return PLACES[i];
    return null;
  }
  function ratio(id) {
    var p = place(id);
    return p ? p.ratio : 1;
  }
  /* Cân nặng ở một nơi, làm tròn tới 0,1 kg. Mốc 30 kg là một đứa trẻ, và nó
     chỉ là VÍ DỤ nên không cần nguồn — thứ cần nguồn là TỈ LỆ, đã có ở PLACES. */
  function weighAt(id, kgOnEarth) {
    return Math.round((kgOnEarth || 30) * ratio(id) * 10) / 10;
  }

  window.AstroQLab = {
    CARDS: CARDS, PLACES: PLACES, SRC: SRC,
    card: card, place: place, ratio: ratio, weighAt: weighAt,
    text: t, dict: T
  };
})();
