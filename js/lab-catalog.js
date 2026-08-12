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
    micro: {
      url: "https://www.nasa.gov/audience/foreducators/microgravity/index.html",
      quote: "The spacecraft, its crew and any objects aboard are all falling toward " +
             "but around Earth. Since they are all falling together, the crew and " +
             "objects appear to float."
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
    { code: "LAB-04", id: "throw",  kind: null, ic: "🎯", tone: "lime",  lock: "lab:throw" },
    { code: "LAB-05", id: "tide",   kind: null, ic: "🌊", tone: "cyan",  lock: "lab:tide"  },
    { code: "LAB-06", id: "mix",    kind: null, ic: "⚗️", tone: "mag",   lock: "lab:mix"   }
  ];

  var T = {
    vi: {
      /* ── tên nơi + vật ── */
      p_earth: "Trái Đất", p_moon: "Mặt Trăng", p_mercury: "Sao Thuỷ", p_jupiter: "Sao Mộc",
      o_hammer: "Búa", o_feather: "Lông chim", o_ball: "Quả bóng", o_pen: "Cây bút",

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
      d_float: "Buông một vật trong trạm vũ trụ. Nó sẽ rơi xuống chứ?",
      q_float: "Trong trạm vũ trụ, em buông cây bút ra. Em nghĩ nó làm gì?",
      say_float: "Nó trôi cạnh em! Không phải vì hết trọng lực — mà vì em VÀ cây bút đang rơi cùng nhau.",
      more_float: "Ở độ cao của trạm, trọng lực Trái Đất vẫn còn khoảng 90% so với trên mặt đất. Trạm không hề đứng yên: nó lao đi rất nhanh — 17.500 dặm một giờ — nên nó rơi về phía Trái Đất mà cứ đi vòng quanh chứ không chạm xuống. Phi hành gia, cây bút và cả cái trạm đều rơi cùng nhau, nên nhìn nhau thì thấy như đang trôi.",
      find_float: "Trôi trong không gian là đang rơi cùng nhau, không phải hết trọng lực.",

      /* ── LAB-03 ── */
      t_weigh: "Cân của em ở đâu",
      d_weigh: "Cùng một em, bốn nơi khác nhau. Cân chỉ số khác nhau.",
      q_weigh: "Chọn một nơi rồi xem cái cân nói gì.",
      say_weigh: "Cân đổi, nhưng lượng vật chất trong người em thì KHÔNG đổi.",
      more_weigh: "Cân nặng là lực mà một nơi kéo em xuống, nên nó đổi theo nơi. Khối lượng là lượng vật chất làm nên em, và nó ở đâu cũng vậy — trên Sao Hoả hay Sao Mộc thì khối lượng của em vẫn y như trên Trái Đất. Đó là lý do phi hành gia không hề gầy đi khi bay lên trạm, dù cái cân ở đó chỉ số 0.",
      find_weigh: "Cân nặng đổi theo nơi; khối lượng thì không.",

      /* ── ba thẻ chưa dựng ── */
      t_throw: "Ném xa ở các nơi", d_throw: "Cùng một cú ném, trọng lực khác nhau thì bay xa khác nhau.",
      t_tide: "Thuỷ triều & Mặt Trăng", d_tide: "Kéo Mặt Trăng xa rồi gần, xem nước biển đổi thế nào.",
      t_mix: "Trộn nguyên tố", d_mix: "Ghép hai nguyên tố xem ra chất gì.",

      /* ── giao diện ── */
      ui_pick_place: "Chọn nơi:",
      ui_drop: "Thả!",
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
      ui_mass: "Khối lượng",
      ui_unchanged: "không đổi",
      ui_free_badge: "MIỄN PHÍ",
      ui_soon_badge: "SẮP RA MẮT",
      ui_you_weigh: "Nếu ở Trái Đất em nặng 30 kg thì ở đây cân chỉ:"
    },
    en: {
      p_earth: "Earth", p_moon: "the Moon", p_mercury: "Mercury", p_jupiter: "Jupiter",
      o_hammer: "Hammer", o_feather: "Feather", o_ball: "Ball", o_pen: "Pen",

      t_tower: "The drop tower",
      d_tower: "Drop a hammer and a feather together. Which one lands first?",
      q_tower: "On the Moon, the hammer is far heavier than the feather. Which do you think lands first?",
      say_tower_moon: "Together! There's no air on the Moon, so nothing slows the feather down.",
      say_tower_earth: "Here the feather is much slower — not because it's light, but because AIR holds it back.",
      more_tower: "Astronaut David Scott ran this exact experiment on the Moon in 1971, with a 1.32-kg geological hammer and a 0.03-kg falcon feather. Forty-four times heavier, and they still landed together. Galileo worked this out hundreds of years earlier: objects released together fall at the same rate, whatever their mass.",
      find_tower: "With no air, everything falls at the same rate.",

      t_float: "Why astronauts float",
      d_float: "Let go of something inside a space station. Will it drop?",
      q_float: "Inside the station you let go of a pen. What do you think it does?",
      say_float: "It floats beside you! Not because gravity is gone — because you AND the pen are falling together.",
      more_float: "At the station's altitude, Earth's gravity is still about 90 percent of what it is at the surface. The station isn't parked up there: it's moving very fast — 17,500 miles per hour — so it falls toward Earth but keeps going around instead of hitting it. The astronauts, the pen and the station are all falling together, so to each other they look like they're floating.",
      find_float: "Floating in space means falling together, not gravity switching off.",

      t_weigh: "What you weigh, and where",
      d_weigh: "The same you, four different places. The scale reads differently.",
      q_weigh: "Pick a place and see what the scale says.",
      say_weigh: "The scale changes, but how much stuff you're made of does NOT.",
      more_weigh: "Weight is the pull a place has on you, so it changes from place to place. Mass is how much stuff you are made of, and that is the same everywhere — on Mars or on Jupiter your mass is exactly what it is on Earth. That's why astronauts don't get thinner on the way up, even though a scale up there would read zero.",
      find_weigh: "Weight changes with where you are; mass does not.",

      t_throw: "Throwing distance", d_throw: "The same throw, different gravity, different distance.",
      t_tide: "Tides and the Moon", d_tide: "Pull the Moon closer and further, watch the sea change.",
      t_mix: "Mix elements", d_mix: "Put two elements together and see what you get.",

      ui_pick_place: "Pick a place:",
      ui_drop: "Drop!",
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
