/* ============================================================
   js/mission-catalog.js — DANH MỤC NHIỆM VỤ & CHẶNG, chỗ DUY NHẤT khai TÊN.

   Nạp như script thường:
     <script src="js/mission-catalog.js"></script>
     AstroQCatalog.worlds() · .missions() · .find(id) · .byWorld(wid)
     AstroQCatalog.stepIds(id) · .step(id, stepId) · .name(id, lang)

   ⚠️⚠️ KHÔNG CÓ MỘT CON SỐ THƯỞNG NÀO TRONG FILE NÀY, VÀ ĐÓ LÀ LUẬT CHỨ KHÔNG
   PHẢI THIẾU SÓT. Bảng thưởng nằm ở `AstroqSV/Services/Missions.cs`; `GET /me/missions`
   hiện **không** trả thưởng theo từng bước, nên client không có cách nào biết một
   chặng cho bao nhiêu tt/XP mà không CHÉP LẠI bảng của server. Chép là hai nơi giữ
   một luật, và ngày đổi độ khó thì bản ở client vẫn nói con số cũ — tức nói SAI với
   trẻ ngay ở màn mời nó chơi. Cùng phân công đã dùng cho huy hiệu (`js/badges.js`),
   mẫu vật (`js/specimens.js`) và bậc (`js/ranks.js`): **server giữ MỐC, client giữ TÊN.**
   Bảng chi tiết một chặng vì thế nói *chặng đó dạy gì*, không nói *được bao nhiêu*.
   Con số thật hiện ở màn tổng kết của `mission-earth.html`, do server trả về.

   ⚠️ `steps[].id` PHẢI KHỚP `Missions.All` Ở SERVER, ĐÚNG THỨ TỰ. Đó là khoá dùng
   trong `missions.<nv>.<bước>` của DynamoDB và trong `AstroQProgress.missionStep()`.
   `check_pages.py` mục [20] đối chiếu ba nơi cùng lúc: file này ↔ `STEP_IDS` của
   `mission-earth.html` ↔ `Missions.cs`. Lệch một chỗ là trang vẽ một chặng mà server
   không biết, và lỗi đó IM LẶNG.

   ⚠️ WORLD-ID KHÁC PLANET-ID — ĐỪNG GỘP. `js/planets.js` có ĐÚNG 8 hành tinh và id
   của nó là chỗ ghi "đã ghé hành tinh nào" cho hồ sơ + huy hiệu (`planet-3`/`planet-8`).
   Mặt Trăng là một ĐIỂM ĐẾN của bản đồ nhiệm vụ nhưng KHÔNG phải hành tinh; nhét nó
   vào danh sách hành tinh là hồ sơ đếm sai và hai huy hiệu kia thành bất khả thi.
   Nên `worlds()` có `moon` với `planet:null`, còn tên/màu 8 hành tinh vẫn lấy từ
   `js/planets.js` — không gõ lại ở đây.
   ============================================================ */
(function (global) {
  "use strict";

  /* ───────── ĐIỂM ĐẾN TRÊN BẢN ĐỒ ─────────
     `orbit` là bố cục TRANG TRÍ cho dễ nhìn (bán kính rx + góc đặt + đường kính đĩa),
     KHÔNG phải khoảng cách thật. Bản đồ này là chỗ ĐIỀU HƯỚNG, không phải chỗ dạy tỉ
     lệ — đừng để bước nào của nhiệm vụ dạy khoảng cách dựa trên nó.

     ⚠️ Toạ độ tính theo hệ ảo 1000×760 rồi quy ra %, và ĐĨA lẫn ĐƯỜNG QUỸ ĐẠO dùng
        CHUNG một phép tính ellipse trong `js/mission-map.js`. Gán cứng vị trí đĩa rồi
        vẽ quỹ đạo riêng là kiểu lỗi đã có tiền lệ (vòng ngắm `.e2-aim` phải chiếu bằng
        đúng `project()` của marker). */
  var WORLDS = [
    { id: "mercury", planet: "mercury", orbit: { r: 175, a: 25, d: 34 } },
    { id: "venus",   planet: "venus",   orbit: { r: 285, a: 40, d: 44 } },
    { id: "earth",   planet: "earth",   orbit: { r: 400, a: 28, d: 54 } },
    /* Mặt Trăng bám cạnh Trái Đất chứ không có quỹ đạo quanh Mặt Trời: `moonOf` nói
       nó treo lệch khỏi điểm nào, đơn vị là hệ ảo. Màu khai tại chỗ vì `js/planets.js`
       cố ý không có nó (xem khối cảnh báo ở đầu file). */
    { id: "moon",    planet: null, vi: "Mặt Trăng", en: "Moon",
      c: "#d3cfc4", c2: "#74706a",
      moonOf: { world: "earth", dx: 62, dy: -46, d: 26 } },
    { id: "mars",    planet: "mars",    orbit: { r: 520, a: 58, d: 40 } },
    { id: "jupiter", planet: "jupiter", orbit: { r: 645, a: 30, d: 80 } },
    { id: "saturn",  planet: "saturn",  orbit: { r: 760, a: 48, d: 64, ring: true } },
    { id: "uranus",  planet: "uranus",  orbit: { r: 880, a: 40, d: 54 } },
    /* `flip`: đĩa sát mép phải → nhãn tên kéo vào trong, không thì chữ bị khung cắt. */
    { id: "neptune", planet: "neptune", orbit: { r: 985, a: 32, d: 52, flip: true } }
  ];

  /* ───────── NHIỆM VỤ ─────────
     ⚠️ CHỈ KHAI NHIỆM VỤ CÓ THẬT. Dự án có luật đã trả giá nhiều lần: đừng hứa một
        nhiệm vụ chưa tồn tại (`js/specimens.js`: *"đừng viết Mở khoá tại Mission 02"*).
        Thêm nhiệm vụ mới thì thêm một dòng ở ĐÂY **và** một dòng ở `Missions.All`,
        rồi dựng trang chơi — thiếu bất kỳ chân nào là mục [20] báo hỏng. */
  var MISSIONS = [
    {
      id: "earth", world: "earth", file: "mission-earth.html", ic: "🌍",
      vi: { nm: "Hành Tinh Xanh", tag: "Nhiệm vụ 01 · Trái Đất" },
      en: { nm: "The Blue Planet", tag: "Mission 01 · Earth" },
      steps: [
        { id: "scan", ic: "🛰️",
          vi: { nm: "Bề mặt hành tinh xanh",
                p: "Chạm 7 châu lục trên ảnh vệ tinh thật, rồi tự đoán: nước hay đất nhiều hơn?" },
          en: { nm: "The blue planet's surface",
                p: "Touch all 7 continents on a real satellite photo, then guess: is there more water or more land?" } },
        { id: "timeline", ic: "⏳",
          vi: { nm: "Lần theo dòng thời gian",
                p: "Đi qua 5 mốc trong 4,54 tỷ năm — từ hành tinh nóng chảy tới Trái Đất hôm nay." },
          en: { nm: "Follow the timeline",
                p: "Walk through 5 milestones across 4.54 billion years — from a molten planet to Earth today." } },
        { id: "sun", ic: "☀️",
          vi: { nm: "Mặt Trời và ba vùng khí hậu",
                p: "Nếu Mặt Trời tắt thì sao? Đoán thử, rồi xem vì sao xích đạo nóng còn hai cực lạnh." },
          en: { nm: "The Sun and three climate zones",
                p: "What if the Sun went out? Take a guess, then find out why the equator is hot and the poles are cold." } },
        { id: "life", ic: "🌳",
          vi: { nm: "Sự sống ở khắp nơi",
                p: "Bay tới 4 nơi có thật trên Trái Đất và đoán xem mỗi nơi nằm ở nấc nào của cột độ cao." },
          en: { nm: "Life is everywhere",
                p: "Fly to 4 real places on Earth and guess which rung of the height column each one sits on." } },
        { id: "energy", ic: "⚡",
          vi: { nm: "Kích hoạt năng lượng sạch",
                p: "Khói đen đang phủ kín khí quyển. Thay ba ống khói bằng ba nguồn năng lượng sạch." },
          en: { nm: "Switch on clean energy",
                p: "Black smoke is covering the atmosphere. Replace three smokestacks with three clean energy sources." } },
        { id: "eco", ic: "♻️",
          vi: { nm: "Eco-Hero: nên hay không nên?",
                p: "Bảy việc hằng ngày, hai cái rổ. Việc nào nên làm, việc nào không?" },
          en: { nm: "Eco-Hero: should we or shouldn't we?",
                p: "Seven everyday actions, two baskets. Which ones should we do, which ones shouldn't we?" } },
        { id: "core", ic: "🗂️",
          vi: { nm: "Đóng dấu Hồ Sơ Trái Đất",
                p: "Ba điều bạn vừa học, một con dấu. Và câu chốt: phải có đủ cả ba cùng một lúc." },
          en: { nm: "Stamp the Earth File",
                p: "Three things you just learned, one stamp. And the point: you need all three at once." } }
      ]
    }
  ];

  function lang(l) { return l === "en" ? "en" : "vi"; }

  /** Tên + màu một điểm đến. 8 hành tinh lấy từ `js/planets.js`; Mặt Trăng khai tại chỗ. */
  function worldInfo(id, l) {
    l = lang(l);
    for (var i = 0; i < WORLDS.length; i++) {
      var w = WORLDS[i];
      if (w.id !== id) continue;
      if (w.planet && global.AstroQPlanets) {
        var all = global.AstroQPlanets.all();
        for (var j = 0; j < all.length; j++) {
          if (all[j].id === w.planet) {
            return { id: w.id, nm: all[j][l], c: all[j].c, c2: all[j].c2 };
          }
        }
      }
      return { id: w.id, nm: w[l] || w.id, c: w.c || "#889", c2: w.c2 || "#334" };
    }
    return { id: id, nm: id, c: "#889", c2: "#334" };
  }

  function find(id) {
    for (var i = 0; i < MISSIONS.length; i++) if (MISSIONS[i].id === id) return MISSIONS[i];
    return null;
  }

  global.AstroQCatalog = {
    worlds: function () { return WORLDS.slice(); },
    missions: function () { return MISSIONS.slice(); },
    find: find,
    worldInfo: worldInfo,

    /** Các nhiệm vụ CÓ THẬT ở một điểm đến (mảng rỗng = nơi đó chưa có nhiệm vụ nào). */
    byWorld: function (wid) {
      var out = [];
      for (var i = 0; i < MISSIONS.length; i++) if (MISSIONS[i].world === wid) out.push(MISSIONS[i]);
      return out;
    },

    /** Id các chặng, ĐÚNG THỨ TỰ CHƠI — phải khớp `Missions.All` ở server. */
    stepIds: function (id) {
      var m = find(id);
      return m ? m.steps.map(function (s) { return s.id; }) : [];
    },

    /** Một chặng theo id, hoặc null. */
    step: function (id, stepId) {
      var m = find(id);
      if (!m) return null;
      for (var i = 0; i < m.steps.length; i++) if (m.steps[i].id === stepId) return m.steps[i];
      return null;
    },

    /** Tên nhiệm vụ theo ngôn ngữ. */
    name: function (id, l) {
      var m = find(id);
      return m ? m[lang(l)].nm : String(id || "");
    }
  };
})(window);
