/* ==========================================================
   proto-mission-map.js — BẢN MẪU bản đồ nhiệm vụ 2D. Dữ liệu tiến độ là GIẢ.

   ⚠️ TÊN HÀNH TINH LẤY TỪ `js/planets.js`, KHÔNG gõ lại ở đây. Đó là chỗ duy nhất
      khai tên song ngữ; gõ lại là hai bản sẽ lệch nhau, và bản lệch sẽ là bản nói
      với trẻ. Bản mẫu này cố ý nạp đúng file thật để chứng minh việc đó làm được.

   ⚠️ MẶT TRĂNG KHÔNG NẰM TRONG `js/planets.js` (file đó có đúng 8 hành tinh) —
      nó khai riêng ở đây. Trang thật sẽ phải TÁCH world-id khỏi planet-id: trường
      `Planet` của nhiệm vụ đang được dùng để ghi "đã ghé hành tinh nào" cho hồ sơ
      và huy hiệu, nên nhét Mặt Trăng vào danh sách hành tinh là hồ sơ đếm sai.

   ⚠️ HỆ TOẠ ĐỘ ẢO 1000×760, quy ra % khi vẽ. Nhờ vậy đĩa hành tinh luôn nằm ĐÚNG
      trên đường quỹ đạo của nó ở mọi cỡ màn — cả hai dùng CHUNG một phép tính
      ellipse. Gán cứng vị trí rồi vẽ quỹ đạo riêng là kiểu lỗi đã có tiền lệ trong
      dự án (vòng ngắm `.e2-aim` phải chiếu bằng đúng `project()` của marker).

   ⚠️ THAY ẢNH THẬT: giữ nguyên `BODIES` (toạ độ + trạng thái), bỏ phần vẽ `.orbit`,
      và cho `.map` một `background-image`. Nhãn tên GIỮ NGUYÊN là DOM.
   ========================================================== */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var VW = 1000, VH = 760;              // hệ toạ độ ảo
  var SUN = { x: 55, y: 715 };          // tâm Mặt Trời = tâm mọi quỹ đạo
  var RY = 0.82;                        // quỹ đạo là ellipse: ry = rx × hằng số này

  /* Bán kính quỹ đạo (rx) và góc đặt hành tinh (độ, 0° = sang phải, 90° = lên trên).
     Đây là bố cục TRANG TRÍ cho dễ nhìn, KHÔNG phải khoảng cách thật — bản đồ này
     là chỗ điều hướng, không phải chỗ dạy khoảng cách. Đừng để bước nào dạy tỉ lệ
     dựa trên nó. */
  var ORBIT = {
    mercury:{ r:175, a:25, d:34 },
    venus:  { r:285, a:40, d:44 },
    earth:  { r:400, a:28, d:54 },
    mars:   { r:520, a:58, d:40 },
    jupiter:{ r:645, a:30, d:80 },
    saturn: { r:760, a:48, d:64, ring:true },
    uranus: { r:880, a:40, d:54 },
    neptune:{ r:985, a:32, d:52, flip:true }
  };

  /* Mặt Trăng: vệ tinh của Trái Đất, đặt lệch khỏi Trái Đất chứ không nằm trên quỹ
     đạo quanh Mặt Trời. Màu khai tại chỗ vì js/planets.js không có nó (xem đầu file). */
  var MOON = { id:"moon", vi:"Mặt Trăng", en:"Moon", c:"#d3cfc4", c2:"#74706a", d:26 };

  var doneCount = 0;    // số chặng đã xong của Trái Đất — 0 · 5 · 7
  var picked = null;

  /* ───────── Toast ───────── */
  var toastT = null;
  function toast(msg) {
    var el = $("toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastT);
    toastT = setTimeout(function () { el.classList.remove("show"); }, 2600);
  }

  /* ───────── Trạng thái một thiên thể ─────────
     Ba trạng thái, và chúng nói ba điều KHÁC NHAU:
       open — có nhiệm vụ, chơi được ngay
       soon — tới được rồi, nhưng nhiệm vụ chưa tồn tại
       lock — chưa có nhiệm vụ nào ở đây

     ⚠️ `lock` ở bản đồ NHIỆM VỤ khác hẳn cổng ở Bản Đồ Thiên Hà (`js/route-gate.js`).
        Cổng kia khoá ĐIỂM ĐẾN nên mặc định TẮT — bật vĩnh viễn là khoá chết 7 mẫu vật
        và 2 huy hiệu. Ở đây chỉ khoá VIỆC CHƠI NHIỆM VỤ, không mẫu vật/huy hiệu nào
        phụ thuộc, nên khoá vĩnh viễn được. Đừng dùng chung một cờ cho hai thứ. */
  function stateOf(id) {
    if (id === "earth") return "open";
    if (id === "moon")  return doneCount >= 5 ? "soon" : "lock";
    return "lock";
  }

  function reasonOf(id) {
    if (id === "moon") {
      return doneCount >= 5
        ? "Bạn đã mở được điểm đến này. Nhiệm vụ Mặt Trăng đang được làm — chưa chơi được."
        : "Xong 5 trong 7 chặng ở Trái Đất là mở được điểm đến Mặt Trăng.";
    }
    /* Nói THẬT: 6 hành tinh này chưa có nhiệm vụ nào, và cũng KHÔNG bị khoá đường
       thăm — Bản Đồ Thiên Hà vẫn bay tới được. Viết "chưa mở khoá" ở đây là nói sai. */
    return "Chưa có nhiệm vụ nào ở đây. Nhưng bạn vẫn ghé thăm và đọc bảng thông tin "
         + "của nơi này trên Bản Đồ Thiên Hà.";
  }

  /* ───────── Vẽ bản đồ ───────── */
  function paintMap() {
    var map = $("map");
    map.innerHTML = "";

    var list = window.AstroQPlanets.all();

    // Quỹ đạo trước (nằm dưới), thiên thể sau
    list.forEach(function (p) {
      var o = ORBIT[p.id];
      var el = document.createElement("div");
      el.className = "orbit" + (stateOf(p.id) === "open" ? " on" : "");
      el.style.left   = pct(SUN.x, VW);
      el.style.top    = pct(SUN.y, VH);
      el.style.width  = pct(o.r * 2, VW);
      el.style.height = pct(o.r * 2 * RY, VH);
      map.appendChild(el);
    });

    // Mặt Trời — TRANG TRÍ, bấm không được
    map.appendChild(body({
      id:"sun", nm:"Mặt Trời", c:"#ffcf6b", c2:"#b45309",
      x:SUN.x, y:SUN.y, d:150, cls:"deco sun", st:""
    }));

    list.forEach(function (p) {
      var o = ORBIT[p.id];
      var a = o.a * Math.PI / 180;
      map.appendChild(body({
        id:p.id, nm:p.vi, c:p.c, c2:p.c2,
        x:SUN.x + o.r * Math.cos(a),
        y:SUN.y - o.r * RY * Math.sin(a),
        d:o.d, ring:o.ring, flip:o.flip,
        cls:stateOf(p.id), st:label(stateOf(p.id))
      }));
    });

    // Mặt Trăng bám cạnh Trái Đất
    var oe = ORBIT.earth, ae = oe.a * Math.PI / 180;
    map.appendChild(body({
      id:"moon", nm:MOON.vi, c:MOON.c, c2:MOON.c2,
      x:SUN.x + oe.r * Math.cos(ae) + 62,
      y:SUN.y - oe.r * RY * Math.sin(ae) - 46,
      d:MOON.d, cls:stateOf("moon"), st:label(stateOf("moon"))
    }));
  }

  function label(st) {
    return st === "open" ? "Có nhiệm vụ" : st === "soon" ? "Sắp ra mắt" : "Chưa có";
  }
  function pct(v, total) { return (v / total * 100) + "%"; }

  function body(o) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "body " + (o.cls || "") + (o.flip ? " flip" : "");
    b.dataset.id = o.id;
    b.style.left = pct(o.x, VW);
    b.style.top  = pct(o.y, VH);
    /* Bề rộng đặt ở CHÍNH cái nút; đĩa dùng `aspect-ratio:1` nên luôn tròn và luôn
       nằm đúng tâm toạ độ (nhãn treo tuyệt đối, không kéo tâm đi — xem ghi chú
       `.body` trong proto-mission-map.css). */
    b.style.width = pct(o.d, VW);
    b.setAttribute("aria-label", o.nm);
    if (o.cls && o.cls.indexOf("deco") >= 0) b.setAttribute("aria-disabled", "true");

    var orb = el("span", "orb");
    orb.style.background = "radial-gradient(circle at 36% 30%, " + o.c + ", " + o.c2 + " 78%)";
    if (o.ring) orb.appendChild(el("span", "ring"));
    b.appendChild(orb);

    var lb = el("span", "lb");
    var nm = el("span", "nm"); nm.textContent = o.nm; lb.appendChild(nm);
    if (o.st) { var st = el("span", "st"); st.textContent = o.st; lb.appendChild(st); }
    b.appendChild(lb);
    return b;
  }
  function el(tag, cls) { var e = document.createElement(tag); e.className = cls; return e; }

  /* ───────── Lối tắt "đang dở" ─────────
     Trẻ quay lại hôm sau chỉ muốn chơi tiếp. Bắt nó đi Bản đồ → hành tinh → cây →
     nhiệm vụ → chặng là 5 cú chạm cho một việc nó đã biết mình muốn làm. */
  var STEP_NM = ["Bề mặt hành tinh xanh", "Lần theo dòng thời gian",
                 "Mặt Trời và ba vùng khí hậu", "Sự sống ở khắp nơi",
                 "Kích hoạt năng lượng sạch", "Eco-Hero: nên hay không nên?",
                 "Đóng dấu Hồ Sơ Trái Đất"];
  function paintResume() {
    var on = doneCount > 0 && doneCount < STEP_NM.length;
    $("resume").hidden = !on;
    if (!on) return;
    $("r-nm").textContent = STEP_NM[doneCount];
    $("r-sub").textContent = "Trái Đất · chặng " + pad(doneCount + 1) + " / " + pad(STEP_NM.length);
  }
  function pad(n) { return n < 10 ? "0" + n : String(n); }

  function paintTop() {
    var tt = [0, 0, 20, 20, 20, 25, 30, 20];   // thưởng tt từng chặng (Missions.cs)
    var sum = 0;
    for (var i = 1; i <= doneCount; i++) sum += tt[i];
    if (doneCount === 7) sum += 100;
    $("bal").textContent = sum;
    /* Câu này phải nói ĐÚNG việc sẽ xảy ra: nay chạm vào nơi có nhiệm vụ là **vào
       thẳng**, không phải "xem" rồi bấm tiếp. Hứa một cửa trung gian không còn tồn
       tại thì trẻ mất một nhịp để hiểu chuyện gì vừa xảy ra. */
    $("intro").textContent = doneCount === 0
      ? "Chạm vào một thiên thể để bắt đầu nhiệm vụ ở đó. Bắt đầu từ Trái Đất."
      : doneCount === 7
        ? "Chạm vào một thiên thể để xem nhiệm vụ ở đó."
        : "Chạm vào Trái Đất là vào thẳng chỗ bạn đang chơi dở.";
  }

  /* ───────── Bảng chi tiết ───────── */
  function openSheet(id) {
    picked = id;
    var st = stateOf(id);
    var nm = id === "moon" ? MOON.vi : window.AstroQPlanets.name(id, "vi");
    var c  = id === "moon" ? MOON.c  : colorOf(id);
    var c2 = id === "moon" ? MOON.c2 : colorOf(id, true);

    $("sh-orb").style.background = "radial-gradient(circle at 36% 30%, " + c + ", " + c2 + " 78%)";
    $("sh-tag").textContent = st === "open" ? "CÓ NHIỆM VỤ"
                            : st === "soon" ? "SẮP RA MẮT" : "CHƯA CÓ NHIỆM VỤ";
    $("sh-h").textContent = nm;

    if (st === "open") {
      $("sh-p").textContent = "Nhiệm vụ 01 “Hành Tinh Xanh” — 7 chặng. "
        + (doneCount === 0 ? "Bạn chưa bắt đầu."
           : doneCount === 7 ? "Bạn đã đi hết cả bảy chặng."
           : "Bạn đang ở chặng " + pad(doneCount + 1) + ".");
      note("");
      btn("Xem nhiệm vụ ở đây", true);
    } else {
      $("sh-p").textContent = reasonOf(id);
      note(st === "soon"
        ? "Đây là lời nói thật, không phải lời hứa: nhiệm vụ này chưa tồn tại."
        : "Chưa có nhiệm vụ ở đây không có nghĩa là bị cấm tới — hai chuyện khác nhau.");
      btn(st === "soon" ? "Nhiệm vụ đang được làm" : "Mở Bản Đồ Thiên Hà", st !== "soon");
    }
    $("sheet").hidden = false;
  }
  function colorOf(id, alt) {
    var all = window.AstroQPlanets.all();
    for (var i = 0; i < all.length; i++) if (all[i].id === id) return alt ? all[i].c2 : all[i].c;
    return alt ? "#334" : "#889";
  }
  function note(txt) { var e = $("sh-note"); e.textContent = txt; e.hidden = !txt; }
  function btn(lb, on) { var b = $("sh-go"); b.textContent = lb; b.disabled = !on; }

  /* ───────── Sự kiện ───────── */
  /* ⚠️ ĐỔI 04/08/2026 — CÓ NHIỆM VỤ THÌ ĐI THẲNG, KHÔNG CÓ THÌ NÓI VÌ SAO.
     Chủ dự án: *"click Trái Đất không cần pop-up có nhiệm vụ nữa mà vào thẳng
     Mission 01, tại điểm đang dừng dở luôn"*. Đúng — cái bảng đó đang chen vào giữa
     một ý định rõ ràng để nói lại chính thứ trẻ vừa bấm, rồi bắt bấm thêm một nút
     nữa. Với nơi ĐÃ CÓ nhiệm vụ thì nó là một cửa không mở ra thông tin nào mới.
     ⚠️ NHƯNG GIỮ BẢNG cho nơi CHƯA có nhiệm vụ / chưa mở: ở đó bảng là chỗ DUY NHẤT
        nói ra điều kiện mở và phân biệt "chưa có nội dung" với "bị cấm tới" — bỏ nó
        là trẻ bấm vào rồi không có gì xảy ra, tức chỉ tưởng mình bấm trượt. */
  $("map").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".body") : null;
    if (!b || b.classList.contains("deco")) return;
    var id = b.dataset.id;
    if (stateOf(id) === "open") { goMission(id); return; }
    openSheet(id);
  });

  /* Một chỗ DUY NHẤT quyết định "bấm vào nơi có nhiệm vụ thì đi đâu" — lối tắt
     "Chơi tiếp" và cú chạm trên bản đồ phải dẫn tới cùng một chỗ, không thì hai
     đường vào cho một việc và sớm muộn lệch nhau. */
  function goMission(id) {
    location.href = "proto-mission-tree-c.html?done=" + doneCount;
  }

  $("sh-x").addEventListener("click", function () { $("sheet").hidden = true; });
  $("sheet").addEventListener("click", function (e) {
    if (e.target === $("sheet")) $("sheet").hidden = true;
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !$("sheet").hidden) $("sheet").hidden = true;
  });

  $("sh-go").addEventListener("click", function () {
    /* Bảng nay chỉ còn dành cho nơi CHƯA có nhiệm vụ — đường ra duy nhất là bản đồ
       thiên hà để ngắm, không phải một nhiệm vụ nào. */
    toast("→ explorer.html (bản mẫu: không điều hướng)");
  });

  /* Lối tắt "Chơi tiếp" đi CÙNG một đường với cú chạm trên bản đồ. */
  $("r-go").addEventListener("click", function () { goMission("earth"); });

  $("seg").addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest("button") : null;
    if (!b) return;
    Array.prototype.forEach.call(this.querySelectorAll("button"), function (x) {
      x.classList.toggle("on", x === b);
    });
    doneCount = parseInt(b.dataset.case, 10);
    $("sheet").hidden = true;
    paintTop(); paintResume(); paintMap();
  });

  paintTop(); paintResume(); paintMap();
})();
