/* ============================================================
   viz.js — bộ vẽ biểu đồ dùng chung, KHÔNG phụ thuộc thư viện ngoài.

   Bốn hình dạng, đủ cho mọi biểu đồ của trang báo cáo admin:
     AstroQViz.line(el, cfg)     đường theo thời gian   (+ crosshair)
     AstroQViz.stack(el, cfg)    cột chồng theo thời gian
     AstroQViz.columns(el, cfg)  cột đơn (nhịp theo giờ / theo thứ / phân bố)
     AstroQViz.hbars(el, cfg)    thanh ngang (phễu, xếp hạng, giữ chân)
     AstroQViz.table(el, cfg)    bảng số — BẢN SONG SINH của mọi biểu đồ

   ── BỐN LUẬT ĐÃ ĐÓNG VÀO ĐÂY, ĐỪNG PHÁ Ở PHÍA GỌI ────────────────────────
   ① MÀU NẰM TRONG CSS, KHÔNG NẰM TRONG JS. Mọi hình chỉ gắn class
      (`.s1`…`.s5` cho màu phân loại, `.r0`…`.r6` cho dải một-tông); giá trị hex
      khai ở `css/admin.css`. Đổi bảng màu là sửa một file, và không có hex nào
      lọt vào JS để rồi lệch với CSS.
      ⚠️ Bảng màu đó ĐÃ KIỂM bằng `scripts/validate_palette.py` của bộ kỹ năng
         dataviz (dải phân loại: CVD ΔE 8.1 · normal-vision 17.5 trên nền
         #0e1527). Thêm màu series thứ 6 thì PHẢI kiểm lại, không đoán.
   ② 1 ĐƠN VỊ SVG = 1 PIXEL CSS. Bề rộng đo từ chính khung chứa lúc vẽ, và vẽ
      lại khi khung đổi cỡ. Nếu để `viewBox` tự co giãn thì chữ co theo, và trên
      màn 390px nhãn trục nhỏ tới mức không đọc được.
   ③ KHÔNG VẼ VIỀN QUANH HÌNH ĐỂ TÁCH CHÚNG. Cái tách hai khối là KHE 2px màu
      nền (`GAP`), và cái giúp điểm cuối đường đọc được là VÒNG 2px màu nền.
      Viền là thêm mực không phải dữ liệu.
   ④ TOOLTIP KHÔNG BAO GIỜ LÀ ĐƯỜNG DUY NHẤT ĐỌC ĐƯỢC SỐ. Mọi biểu đồ đều có
      `AstroQViz.table` sinh ra từ CÙNG dữ liệu — nút "Bảng số" ở trang admin.
      Bàn phím Tab qua từng hình cũng hiện đúng nội dung như trỏ chuột.

   ⚠️ CHỖ DUY NHẤT ĐẶT `style` TRỰC TIẾP TỪ JS là toạ độ tooltip đi theo con trỏ
      (`left`/`top`). Đó là HÌNH HỌC theo con trỏ, không có cách nào khai trước
      trong CSS. Mọi thứ thuộc về hình thức — màu, nét, cỡ chữ, bóng — nằm hết ở
      `css/admin.css`.
   ============================================================ */
(function(){
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  /* ── Hằng số hình học. Lấy từ bộ kỹ năng dataviz, không phải chọn bừa ──
     BAR_MAX  cột/thanh dày tối đa 24px — dày hơn thì đọc ra "khối đặc", ồn.
     RADIUS   4px bo ở ĐẦU MANG DỮ LIỆU, đầu ở vạch gốc thì vuông.
     GAP      khe 2px màu nền, dùng CẢ giữa các tầng cột chồng LẪN giữa hai cột
              cạnh nhau — một bề rộng duy nhất cho cả biểu đồ.
     DOT      điểm cuối đường bán kính 4 (đường kính 8) + vòng 2px màu nền.
     HIT      vùng chạm tối thiểu 24px, rộng hơn chính cái hình. */
  var BAR_MAX = 24, RADIUS = 4, GAP = 2, DOT = 4, HIT = 24;

  var PAD = { t: 14, r: 14, b: 26, l: 40 };

  function el(name, attrs){
    var n = document.createElementNS(NS, name);
    if (attrs) for (var k in attrs) if (attrs[k] != null) n.setAttribute(k, attrs[k]);
    return n;
  }

  /* Nhãn series/hạng mục đến TỪ API — luôn đặt bằng textContent, không bao giờ
     ghép vào innerHTML. Cùng luật `AstroQ.esc` nhưng ở đây khỏi cần escape. */
  function txt(parent, s, attrs){
    var n = el("text", attrs);
    n.textContent = s;
    parent.appendChild(n);
    return n;
  }

  /* ── Vạch trục: làm tròn về số đẹp. Trục mang những giá trị KHÔNG được dán
        nhãn trực tiếp, nên số phải đọc được ngay: 0 / 20 / 40, không 0 / 17 / 34. */
  function niceMax(v){
    if (!(v > 0)) return 1;
    var pow = Math.pow(10, Math.floor(Math.log10(v)));
    var n = v / pow;
    return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * pow;
  }

  function ticks(max, n){
    var out = [];
    for (var i = 0; i <= n; i++) out.push(max * i / n);
    return out;
  }

  function fmt(v){
    v = Number(v) || 0;
    if (Math.abs(v) >= 1000000) return (v/1000000).toFixed(1).replace(/\.0$/,"") + "M";
    if (Math.abs(v) >= 10000)   return Math.round(v/1000) + "K";
    return String(Math.round(v));
  }

  /* ── Đường bo MỘT ĐẦU. `up` = cột mọc lên (bo hai góc trên), ngược lại là
        thanh mọc sang phải (bo hai góc phải). Bán kính tự hạ xuống khi hình quá
        nhỏ — bo 4px trên một cột cao 3px thì hình méo thành viên thuốc. ── */
  function capPath(x, y, w, h, up){
    if (up){
      var r = Math.max(0, Math.min(RADIUS, w/2, h));
      return "M" + x + "," + (y+h) + "V" + (y+r) +
             "a" + r + "," + r + " 0 0 1 " + r + ",-" + r +
             "H" + (x+w-r) +
             "a" + r + "," + r + " 0 0 1 " + r + "," + r +
             "V" + (y+h) + "Z";
    }
    var r2 = Math.max(0, Math.min(RADIUS, h/2, w));
    return "M" + x + "," + y + "H" + (x+w-r2) +
           "a" + r2 + "," + r2 + " 0 0 1 " + r2 + "," + r2 +
           "V" + (y+h-r2) +
           "a" + r2 + "," + r2 + " 0 0 1 -" + r2 + "," + r2 +
           "H" + x + "Z";
  }

  /* ══════════════════ TOOLTIP ══════════════════
     Một cái cho mỗi khung chứa. GIÁ TRỊ đứng trước và đậm, TÊN series đi sau và
     mờ hơn — ngược thứ bậc của chú giải, vì ở đây người đọc đã biết series và
     đang cần con số. Mỗi dòng gắn một NÉT ngắn màu series (không phải ô vuông:
     ở mật độ này ô vuông là mực nặng làm việc của một cái nhãn). */
  function tipFor(box){
    var tip = box.querySelector(".viz-tip");
    if (tip) return tip;
    tip = document.createElement("div");
    tip.className = "viz-tip";
    tip.setAttribute("role", "status");
    box.appendChild(tip);
    return tip;
  }

  function showTip(box, x, y, title, rows){
    var tip = tipFor(box);
    tip.textContent = "";

    var h = document.createElement("b");
    h.className = "viz-tip-h";
    h.textContent = title;
    tip.appendChild(h);

    (rows || []).forEach(function(r){
      var line = document.createElement("span");
      line.className = "viz-tip-row";
      var key = document.createElement("i");
      key.className = "viz-key " + (r.cls || "s1");
      line.appendChild(key);
      var v = document.createElement("b");
      v.textContent = r.value;                 // giá trị dẫn
      line.appendChild(v);
      var nm = document.createElement("span");
      nm.textContent = r.name;                 // tên theo sau
      line.appendChild(nm);
      tip.appendChild(line);
    });

    tip.classList.add("on");
    /* ⚠️ ĐÂY LÀ CHỖ DUY NHẤT VIẾT `style` TỪ JS (xem đầu file): toạ độ đi theo
       con trỏ. Kẹp trong khung để tooltip không tràn ra ngoài mép phải. */
    var w = tip.offsetWidth, bw = box.clientWidth;
    tip.style.left = Math.max(4, Math.min(bw - w - 4, x - w/2)) + "px";
    tip.style.top  = Math.max(4, y - tip.offsetHeight - 12) + "px";
  }

  function hideTip(box){
    var tip = box.querySelector(".viz-tip");
    if (tip) tip.classList.remove("on");
  }

  /* Gắn cùng một nội dung cho CHUỘT và BÀN PHÍM. Thiếu nhánh bàn phím thì con
     số chỉ tới được bằng chuột — và tooltip trở thành cửa duy nhất, phá luật ④. */
  function hoverable(node, box, get){
    node.setAttribute("tabindex", "0");
    node.setAttribute("role", "img");
    function on(ev){
      var d = get();
      var r = node.getBoundingClientRect(), b = box.getBoundingClientRect();
      var x = (ev && ev.clientX ? ev.clientX : r.left + r.width/2) - b.left;
      var y = (ev && ev.clientY ? ev.clientY : r.top) - b.top;
      node.classList.add("hot");
      showTip(box, x, y, d.title, d.rows);
    }
    function off(){ node.classList.remove("hot"); hideTip(box); }
    node.addEventListener("pointermove", on);
    node.addEventListener("pointerenter", on);
    node.addEventListener("pointerleave", off);
    node.addEventListener("focus", on);
    node.addEventListener("blur", off);
    // Nhãn cho trình đọc màn hình — cùng nội dung, không phụ thuộc tooltip.
    var d = get();
    node.setAttribute("aria-label", d.title + ": " +
      (d.rows || []).map(function(r){ return r.value + " " + r.name; }).join(", "));
  }

  /* ══════════════════ KHUNG CHUNG ══════════════════
     Đo bề rộng THẬT của khung chứa rồi vẽ 1:1, và vẽ lại khi khung đổi cỡ
     (luật ②). Không có ResizeObserver thì lùi về sự kiện `resize`. */
  /* ⚠️ `minW` LÀ SÀN BỀ RỘNG, VÀ NÓ PHẢI KHÁC NHAU THEO HÌNH DẠNG. 240px là sàn
     đúng cho biểu đồ có trục (hẹp hơn thì nhãn trục chồng nhau), nhưng SAI cho
     đường tí hon nằm trong ô số liệu rộng ~130px: SVG bị ép rộng 240 rồi TRÀN sang
     ô bên cạnh — đã thấy đúng như vậy trên ảnh chụp. Dấu nhỏ tự đặt sàn của nó. */
  function mount(box, h, draw, minW){
    if (box._vizOff) box._vizOff();
    var floorW = minW || 240;

    function paint(){
      var w = Math.max(floorW, box.clientWidth || floorW);
      var old = box.querySelector("svg");
      if (old) old.remove();
      var svg = el("svg", {
        width: w, height: h, viewBox: "0 0 " + w + " " + h,
        class: "viz", "aria-hidden": "false", role: "group"
      });
      box.insertBefore(svg, box.firstChild);
      draw(svg, w, h);
    }

    paint();

    if (window.ResizeObserver){
      var last = box.clientWidth;
      var ro = new ResizeObserver(function(){
        // Chỉ vẽ lại khi bề RỘNG đổi. Tooltip hiện lên làm khung cao thêm, và vẽ
        // lại vì chuyện đó là xoá đúng cái hình con trỏ đang trỏ vào.
        if (Math.abs(box.clientWidth - last) < 1) return;
        last = box.clientWidth;
        paint();
      });
      ro.observe(box);
      box._vizOff = function(){ ro.disconnect(); box._vizOff = null; };
    } else {
      var t = null;
      var onR = function(){ clearTimeout(t); t = setTimeout(paint, 150); };
      window.addEventListener("resize", onR);
      box._vizOff = function(){ window.removeEventListener("resize", onR); box._vizOff = null; };
    }
  }

  function grid(svg, w, h, max, yTicks){
    var g = el("g", { class: "viz-grid" });
    yTicks.forEach(function(v){
      var y = h - PAD.b - (max ? (v/max) * (h - PAD.t - PAD.b) : 0);
      // Hairline LIỀN, một bậc lệch khỏi nền. Gạch nét đứt đọc ra "ngưỡng".
      g.appendChild(el("line", { x1: PAD.l, y1: y, x2: w - PAD.r, y2: y }));
      txt(g, fmt(v), { x: PAD.l - 7, y: y + 3.5, class: "viz-ytick" });
    });
    svg.appendChild(g);
  }

  /* Nhãn trục X.
     ⚠️ ĐO BỀ RỘNG THẬT RỒI MỚI BỎ NHÃN, KHÔNG ĐẾM THEO SỐ LƯỢNG. Cách cũ ("in
        một nhãn mỗi N ô, N tính từ plotW/64") đoán bề rộng chữ, và nó đoán SAI
        ngay khi nhãn dài hơn "22/08": năm nhãn phân bố độ chính xác
        ("Chưa làm câu nào", "Dưới 50%"…) vừa số lượng nhưng đè nhau trên màn.
        Ở đây in nhãn rồi ĐO (`getComputedTextLength`), nhãn nào chạm vào nhãn
        vừa in thì bỏ. Không có cách đếm nào thay được phép đo. */
  function xLabels(svg, w, h, labels, plotW, step){
    var g = el("g", { class: "viz-xtick" });
    svg.appendChild(g);                      // phải nằm trong DOM mới đo được chữ

    var n = labels.length;
    var placed = [];                         // { node, left, right }

    labels.forEach(function(s, i){
      if (step && i % step !== 0 && i !== n - 1) return;

      var x = PAD.l + (n > 1 ? (i + 0.5) * (plotW / n) : plotW/2);
      var t = txt(g, s, { x: x, y: h - PAD.b + 15 });
      // Nhãn đầu/cuối canh vào trong để không tràn khỏi hai mép.
      if (i === n - 1)  t.setAttribute("text-anchor", "end");
      else if (i === 0) t.setAttribute("text-anchor", "start");

      var len;
      try { len = t.getComputedTextLength(); } catch(e){ len = String(s).length * 5.6; }
      var left  = i === 0 ? x : (i === n - 1 ? x - len : x - len/2);
      var last  = placed[placed.length - 1];

      if (last && left < last.right + 8){
        /* ⚠️ NHÃN CUỐI THẮNG, KHÔNG PHẢI NHÃN TỚI TRƯỚC. Nó là mốc "hôm nay" —
           một trục thời gian không ghi ngày cuối là trục đọc không ra. Nên khi
           hai cái chạm nhau ở mép phải thì bỏ cái ĐÃ IN, giữ cái cuối. */
        if (i === n - 1){ last.node.remove(); placed.pop(); }
        else { t.remove(); return; }
      }
      placed.push({ node: t, left: left, right: left + len });
    });
  }

  function empty(box, msg){
    if (box._vizOff) box._vizOff();
    box.textContent = "";
    var p = document.createElement("p");
    p.className = "viz-empty";
    p.textContent = msg;
    box.appendChild(p);
  }

  /* ══════════════════ ĐƯỜNG THEO THỜI GIAN ══════════════════
     cfg = { series:[{name, cls, values:[số]}], labels:[chuỗi], unit, emptyMsg }
     ⚠️ MỘT TRỤC Y DUY NHẤT cho mọi series. Hai thang đo trên một khung là lỗi
        biểu đồ nặng nhất: chỗ hai đường cắt nhau là ngẫu nhiên theo cách chọn
        thang, nên khung hình tự bịa ra một mối liên hệ không có trong dữ liệu.
        Cần vẽ hai đại lượng khác cỡ thì DÙNG HAI KHUNG. */
  function line(box, cfg){
    var series = cfg.series || [], labels = cfg.labels || [];
    var all = series.reduce(function(a, s){ return a.concat(s.values || []); }, []);
    if (!labels.length || !all.length){ return empty(box, cfg.emptyMsg || "Chưa có số liệu."); }

    var max = niceMax(Math.max.apply(null, all.concat([0])));
    var h = cfg.h || 190;

    mount(box, h, function(svg, w){
      var plotW = w - PAD.l - PAD.r, plotH = h - PAD.t - PAD.b;
      var yT = ticks(max, 4);
      grid(svg, w, h, max, yT);
      xLabels(svg, w, h, labels, plotW);

      var stepX = labels.length > 1 ? plotW / (labels.length - 1) : 0;
      var X = function(i){ return PAD.l + (labels.length > 1 ? i * stepX : plotW/2); };
      var Y = function(v){ return h - PAD.b - (max ? (v/max) * plotH : 0); };

      series.forEach(function(s){
        var vals = s.values || [], d = "";
        vals.forEach(function(v, i){ d += (i ? "L" : "M") + X(i) + "," + Y(v); });
        // Vùng tô là MỘT LỚP RỬA ~10%, không phải khối đặc — độ mờ khai ở CSS.
        var area = "M" + X(0) + "," + Y(0) + d.slice(1) + "L" + X(vals.length-1) + "," + Y(0) + "Z";
        svg.appendChild(el("path", { d: area, class: "viz-area " + (s.cls || "s1") }));
        svg.appendChild(el("path", { d: d, class: "viz-line " + (s.cls || "s1") }));
        // Điểm cuối: bán kính 4 + VÒNG 2px màu nền, để nó đọc được ở chỗ chồng lên đường.
        var lastI = vals.length - 1;
        svg.appendChild(el("circle", {
          cx: X(lastI), cy: Y(vals[lastI]), r: DOT, class: "viz-dot " + (s.cls || "s1")
        }));
      });

      /* Crosshair TÌM TRỤC X. Người đọc nhắm vào một NGÀY, không nhắm vào một
         đường dày 2px — nên vùng chạm là cả cột dọc, và tooltip liệt kê MỌI
         series tại ngày đó. */
      var cross = el("line", { class: "viz-cross", y1: PAD.t, y2: h - PAD.b, x1: -9, x2: -9 });
      svg.appendChild(cross);

      var hit = el("rect", {
        x: PAD.l - stepX/2, y: PAD.t, width: plotW + stepX, height: plotH,
        class: "viz-hit", tabindex: "0"
      });
      var focusI = labels.length - 1;

      function at(i){
        i = Math.max(0, Math.min(labels.length - 1, i));
        cross.setAttribute("x1", X(i)); cross.setAttribute("x2", X(i));
        cross.classList.add("on");
        var rows = series.map(function(s){
          return { cls: s.cls || "s1", name: s.name,
                   value: fmt((s.values || [])[i]) + (cfg.unit ? " " + cfg.unit : "") };
        });
        return { i: i, title: labels[i], rows: rows };
      }

      hit.addEventListener("pointermove", function(ev){
        var b = svg.getBoundingClientRect();
        var i = stepX ? Math.round((ev.clientX - b.left - PAD.l) / stepX) : 0;
        var d = at(i);
        showTip(box, X(d.i), PAD.t + 8, d.title, d.rows);
      });
      hit.addEventListener("pointerleave", function(){
        cross.classList.remove("on"); hideTip(box);
      });
      // Bàn phím: mũi tên trái/phải đi từng ngày, cùng nội dung như chuột.
      hit.addEventListener("keydown", function(ev){
        var k = ev.key;
        if (k !== "ArrowLeft" && k !== "ArrowRight") return;
        ev.preventDefault();
        focusI += (k === "ArrowRight" ? 1 : -1);
        var d = at(focusI); focusI = d.i;
        showTip(box, X(d.i), PAD.t + 8, d.title, d.rows);
      });
      hit.addEventListener("focus", function(){
        var d = at(focusI);
        showTip(box, X(d.i), PAD.t + 8, d.title, d.rows);
      });
      hit.addEventListener("blur", function(){ cross.classList.remove("on"); hideTip(box); });
      svg.appendChild(hit);
    });
  }

  /* ══════════════════ CỘT CHỒNG THEO THỜI GIAN ══════════════════
     cfg = { series:[{name, cls, values:[]}], labels:[], emptyMsg }
     Mỗi tầng cách tầng dưới đúng GAP pixel màu nền (luật ③). */
  function stack(box, cfg){
    var series = cfg.series || [], labels = cfg.labels || [];
    var totals = labels.map(function(_, i){
      return series.reduce(function(a, s){ return a + (Number((s.values||[])[i]) || 0); }, 0);
    });
    if (!labels.length || !totals.some(function(v){ return v > 0; }))
      return empty(box, cfg.emptyMsg || "Chưa có số liệu.");

    var max = niceMax(Math.max.apply(null, totals));
    var h = cfg.h || 200;

    mount(box, h, function(svg, w){
      var plotW = w - PAD.l - PAD.r, plotH = h - PAD.t - PAD.b;
      grid(svg, w, h, max, ticks(max, 4));
      xLabels(svg, w, h, labels, plotW);

      var slot = plotW / labels.length;
      // Cột KHÔNG BAO GIỜ lấp kín ô của nó — phần dư là khoảng thở, và trần
      // BAR_MAX chặn cột phình thành khối đặc khi chỉ có vài ngày dữ liệu.
      var bw = Math.max(2, Math.min(BAR_MAX, slot - GAP - 2));

      labels.forEach(function(lab, i){
        var x = PAD.l + i * slot + (slot - bw) / 2;
        var acc = 0;
        var g = el("g", { class: "viz-colgrp" });

        series.forEach(function(s){
          var v = Number((s.values||[])[i]) || 0;
          if (v <= 0) return;
          var y0 = h - PAD.b - (acc / max) * plotH;
          var y1 = h - PAD.b - ((acc + v) / max) * plotH;
          acc += v;
          var segH = y0 - y1;
          // Khe 2px cắt vào ĐÁY tầng, nên tầng trên không dính tầng dưới.
          var drawH = Math.max(1, segH - GAP);
          var isTop = Math.abs(acc - totals[i]) < 1e-9;
          g.appendChild(el("path", {
            d: capPath(x, y1, bw, drawH, isTop),      // chỉ tầng trên cùng được bo
            class: "viz-bar " + (s.cls || "s1")
          }));
        });

        // Vùng chạm rộng hơn cột (luật HIT) và nằm TRÊN các tầng, nên trỏ vào
        // đâu trong cột cũng ra tooltip liệt kê cả 5 loại việc của ngày đó.
        var hw = Math.max(HIT, slot);
        var hitR = el("rect", {
          x: PAD.l + i*slot + (slot - hw)/2, y: PAD.t, width: hw, height: plotH,
          class: "viz-hit"
        });
        g.appendChild(hitR);
        hoverable(hitR, box, function(){
          var rows = series.map(function(s){
            return { cls: s.cls || "s1", name: s.name, value: fmt((s.values||[])[i]) };
          }).filter(function(r){ return r.value !== "0"; });
          rows.push({ cls: "total", name: cfg.totalName || "tổng", value: fmt(totals[i]) });
          return { title: lab, rows: rows };
        });
        svg.appendChild(g);
      });
    });
  }

  /* ══════════════════ CỘT ĐƠN ══════════════════
     cfg = { labels:[], values:[], name, cls, xStep, emptyMsg }
     ⚠️ MỘT SERIES = MỘT MÀU cho mọi cột. KHÔNG tô đậm-theo-giá-trị: cột cao
        thấp đã nói lên độ lớn rồi, tô thêm là đốt kênh màu duy nhất còn trống
        để nhắc lại thứ biểu đồ đang hiện. */
  function columns(box, cfg){
    var labels = cfg.labels || [], values = cfg.values || [];
    if (!labels.length || !values.some(function(v){ return v > 0; }))
      return empty(box, cfg.emptyMsg || "Chưa có số liệu.");

    var max = niceMax(Math.max.apply(null, values));
    var h = cfg.h || 170;

    mount(box, h, function(svg, w){
      var plotW = w - PAD.l - PAD.r, plotH = h - PAD.t - PAD.b;
      grid(svg, w, h, max, ticks(max, 3));
      xLabels(svg, w, h, labels, plotW, cfg.xStep);

      var slot = plotW / labels.length;
      var bw = Math.max(2, Math.min(BAR_MAX, slot - GAP - 2));

      labels.forEach(function(lab, i){
        var v = Number(values[i]) || 0;
        var x = PAD.l + i*slot + (slot - bw)/2;
        var bh = max ? (v/max) * plotH : 0;
        var g = el("g");
        if (v > 0)
          g.appendChild(el("path", {
            d: capPath(x, h - PAD.b - bh, bw, bh, true),
            class: "viz-bar " + (cfg.cls || "s1")
          }));
        var hw = Math.max(HIT, slot);
        var hitR = el("rect", {
          x: PAD.l + i*slot + (slot-hw)/2, y: PAD.t, width: hw, height: plotH, class: "viz-hit"
        });
        g.appendChild(hitR);
        hoverable(hitR, box, function(){
          return { title: lab, rows: [{ cls: cfg.cls || "s1",
                   name: cfg.name || "", value: fmt(v) + (cfg.unit ? " " + cfg.unit : "") }] };
        });
        svg.appendChild(g);
      });
    });
  }

  /* ══════════════════ THANH NGANG ══════════════════
     cfg = { rows:[{label, value, note, cls}], max, unit, emptyMsg }
     Dùng cho phễu, xếp hạng, giữ chân. `cls` để phía gọi chọn `r0`…`r6` khi các
     hạng mục CÓ THỨ TỰ (phễu, bước nhiệm vụ) — đó là dải một-tông, không phải
     màu phân loại. Hạng mục không có thứ tự thì để mặc định `s1` cho tất cả.

     ⚠️ NHÃN GIÁ TRỊ ĐẶT NGOÀI ĐẦU THANH, LUÔN LUÔN. Đặt trong thanh thì thanh
        ngắn sẽ cắt mất chữ, và `overflow:hidden` chỉ biến nó thành chữ bị gặm
        đầu — tệ hơn không có nhãn. */
  function hbars(box, cfg){
    var rows = cfg.rows || [];
    if (!rows.length) return empty(box, cfg.emptyMsg || "Chưa có số liệu.");

    /* `null` không được tính vào thang: một hàng "chưa đo" không phải hàng bằng 0,
       và nó cũng không được kéo trần xuống. */
    var known = rows.map(function(r){ return r.value == null ? null : (Number(r.value)||0); })
                    .filter(function(v){ return v != null; });
    var max = cfg.max != null ? cfg.max
            : niceMax(Math.max.apply(null, known.concat([0])));
    var rowH = 30, valW = 52;
    var h = rows.length * rowH + 8;

    mount(box, h, function(svg, w){
      /* ⚠️ CỘT NHÃN CO THEO BỀ RỘNG THẬT. `cfg.labelW` là bề rộng MONG MUỐN ở màn
         rộng; trên điện thoại 390px thì 196px nhãn chỉ còn ~90px cho thanh, và biểu
         đồ thanh mà thanh ngắn hơn nhãn thì không còn là biểu đồ. Trần 42% bề rộng
         giữ cho thanh luôn là phần lớn hơn; phần nhãn thiếu chỗ thì `fitLabel` cắt,
         và chữ đầy đủ vẫn còn ở tooltip + "Bảng số". */
      var labelW = Math.max(56, Math.min(cfg.labelW || 132, Math.round(w * 0.42)));
      var trackX = labelW + 8;
      var trackW = Math.max(30, w - trackX - valW - 8);

      rows.forEach(function(r, i){
        var y = i * rowH + 4;
        /* ⚠️ `null` KHÁC 0. null = "chưa đo được" → KHÔNG vẽ thanh nào và in dấu
           "—"; 0 = "đã đo, bằng 0" → vẫn in "0". Gộp hai thứ là khẳng định sai:
           mốc giữ chân 30 ngày mà chưa ai đăng ký đủ 30 ngày thì in "0%" nghĩa là
           "đủ tuổi mà không ai quay lại" — một câu dữ liệu chưa cho phép nói. */
        var known = r.value != null && r.value !== "";
        var v = known ? (Number(r.value) || 0) : 0;
        var bw = known && max ? Math.max(v > 0 ? 3 : 0, (v/max) * trackW) : 0;
        var bh = Math.min(BAR_MAX, rowH - 10);
        var by = y + (rowH - 10 - bh)/2 + 2;
        var g = el("g");
        svg.appendChild(g);                  // vào DOM trước, để đo được chữ

        // Nhãn hạng mục — chữ ĐEO TOKEN CHỮ, không đeo màu series (màu series
        // nhạt thì làm chữ không đọc được trên nền).
        var t = txt(g, r.label, { x: labelW, y: by + bh/2 + 4, class: "viz-rowlab" });
        t.setAttribute("text-anchor", "end");
        // Cắt cho vừa cột nhãn — chừa 6px để chữ không dính vào rãnh.
        fitLabel(t, r.label, labelW - 6);

        // Rãnh: một bậc NHẠT HƠN của cùng dải, để trạng thái đọc được suốt thanh.
        g.appendChild(el("rect", {
          x: trackX, y: by, width: trackW, height: bh, rx: RADIUS, class: "viz-track"
        }));
        if (bw > 0)
          g.appendChild(el("path", {
            d: capPath(trackX, by, bw, bh, false),
            class: "viz-bar " + (r.cls || "s1")
          }));

        // Giá trị ở đầu thanh, NGOÀI thanh (xem cảnh báo trên).
        var shown = known ? fmt(v) + (cfg.unit ? cfg.unit : "") : "—";
        txt(g, shown, { x: trackX + trackW + 6, y: by + bh/2 + 4, class: "viz-rowval" });

        var hitR = el("rect", {
          x: trackX, y: y, width: trackW, height: Math.max(HIT, rowH), class: "viz-hit"
        });
        g.appendChild(hitR);
        hoverable(hitR, box, function(){
          // Tooltip mang nhãn ĐẦY ĐỦ (chưa cắt) — đó là nơi phần chữ bị "…" ăn
          // mất quay lại được, cùng với "Bảng số".
          var out = [{ cls: r.cls || "s1", name: cfg.name || "", value: shown }];
          if (r.note) out.push({ cls: "total", name: r.note, value: "" });
          return { title: r.label, rows: out };
        });
      });
    });
  }

  /* ══════════════════ BẢNG SỐ ══════════════════
     Bản song sinh của mọi biểu đồ (luật ④): cùng dữ liệu, không cần màu, không
     cần trỏ chuột. `head` là mảng chuỗi, `rows` là mảng mảng.
     ⚠️ Dựng bằng createElement + textContent, KHÔNG ghép innerHTML: nhãn hạng
        mục đến từ API và có thể chứa ký tự HTML. */
  /* ══════════════════ ĐƯỜNG TÍ HON TRONG Ô SỐ LIỆU ══════════════════
     cfg = { values:[số], cls, unit, name, labels }
     Không trục, không lưới, không nhãn — nó là phần "trend" của một ô số liệu:
     hình dáng của con số theo thời gian, đọc bằng một cái nhìn.

     ⚠️ NÉT 1,5px CHỨ KHÔNG PHẢI 2px như biểu đồ lớn. Trên khung cao 26px, nét 2px
        chiếm gần 8% chiều cao và đường biến thành một dải dày — dấu nhỏ cần nét
        nhỏ tương ứng, không phải cùng một con số tuyệt đối.
     ⚠️ KHÔNG PHẢI CỬA DUY NHẤT ĐỌC SỐ: mỗi đường tí hon ở đây đều có một biểu đồ
        LỚN tương ứng bên dưới trang, kèm bản "Bảng số". Tooltip chỉ nói ba mốc
        (cao nhất / thấp nhất / mới nhất) vì đó là thứ đọc được ở cỡ này. */
  function spark(box, cfg){
    var vals = (cfg.values || []).map(function(v){ return Number(v) || 0; });
    if (!vals.length){ if (box._vizOff) box._vizOff(); box.textContent = ""; return; }

    var max = Math.max.apply(null, vals);
    var min = Math.min.apply(null, vals);
    var h = cfg.h || 26;

    // Chuỗi phẳng tuyệt đối (thường là toàn 0 vì nhật ký chưa chảy) thì vẽ đường
    // giữa khung, KHÔNG chia cho 0.
    var span = max > 0 ? max : 1;

    mount(box, h, function(svg, w){
      var n = vals.length;
      var X = function(i){ return n > 1 ? 1 + i * (w - 2) / (n - 1) : w/2; };
      var Y = function(v){ return h - 3 - (v/span) * (h - 8); };

      var d = "";
      vals.forEach(function(v, i){ d += (i ? "L" : "M") + X(i) + "," + Y(v); });

      svg.appendChild(el("path", {
        d: "M" + X(0) + "," + (h-1) + d.slice(1) + "L" + X(n-1) + "," + (h-1) + "Z",
        class: "viz-area " + (cfg.cls || "s1")
      }));
      svg.appendChild(el("path", { d: d, class: "viz-spark " + (cfg.cls || "s1") }));
      // Điểm cuối = kỳ hiện tại, mang màu nhấn (phần còn lại của đường lùi lại sau).
      svg.appendChild(el("circle", {
        cx: X(n-1), cy: Y(vals[n-1]), r: 2.5, class: "viz-spark-dot " + (cfg.cls || "s1")
      }));

      var hit = el("rect", { x: 0, y: 0, width: w, height: h, class: "viz-hit" });
      svg.appendChild(hit);
      hoverable(hit, box, function(){
        var u = cfg.unit ? " " + cfg.unit : "";
        return { title: cfg.name || "", rows: [
          { cls: cfg.cls || "s1", name: "mới nhất", value: fmt(vals[n-1]) + u },
          { cls: "total", name: "cao nhất",  value: fmt(max) + u },
          { cls: "total", name: "thấp nhất", value: fmt(min) + u }
        ]};
      });
    }, 40);   // sàn 40px: dấu nhỏ co theo ô chứa nó, không có trục nào để chồng
  }

  /* ══════════════════ THANH ĐO TỈ LỆ ══════════════════
     cfg = { pct, left, right, cls, trackCls, tone }
     Một phần của một tổng, dạng MỘT thanh — không phải bánh 2 miếng (bánh hai
     miếng thì mắt phải so hai góc để đọc một tỉ lệ đã biết sẵn).

     ⚠️ RÃNH LÀ MỘT BẬC NHẠT CỦA CHÍNH DẢI ĐÓ, không phải màu xám trung tính: nhờ
        vậy trạng thái đọc được trên SUỐT thanh, kể cả phần chưa đầy.
     ⚠️ HAI NHÃN ĐẶT NGOÀI THANH, hai đầu. Nhãn trong thanh thì tỉ lệ nhỏ sẽ cắt
        mất chữ — cùng luật đã ghi ở `hbars`. */
  function meter(box, cfg){
    var pct = cfg.pct;
    var known = pct != null;
    var v = known ? Math.max(0, Math.min(100, Number(pct) || 0)) : 0;
    var h = 56;

    mount(box, h, function(svg, w){
      var bh = 22, by = 22;

      // Nhãn trên: bên trái là phần ĐÃ đầy, bên phải là phần còn lại.
      txt(svg, cfg.left || "", { x: 0, y: 13, class: "viz-mlab" });
      var r = txt(svg, cfg.right || "", { x: w, y: 13, class: "viz-mlab" });
      r.setAttribute("text-anchor", "end");

      svg.appendChild(el("rect", {
        x: 0, y: by, width: w, height: bh, rx: RADIUS,
        class: "viz-track " + (cfg.trackCls || "")
      }));

      if (known && v > 0){
        // Trừ GAP để phần đầy không dính vào phần rãnh còn lại — cùng khe 2px
        // dùng ở cột chồng, một bề rộng cho cả trang.
        var fw = Math.max(3, (v/100) * w - (v < 100 ? GAP : 0));
        svg.appendChild(el("path", {
          d: capPath(0, by, fw, bh, false), class: "viz-bar " + (cfg.cls || "s1")
        }));
      }

      // Con số ĐẶT TRÊN thanh ở giữa — chỗ duy nhất luôn có chỗ, và nó là con số
      // duy nhất của hình này nên không có gì để đè.
      var c = txt(svg, known ? Math.round(v) + "%" : "—",
                  { x: w/2, y: by + bh/2 + 4.5, class: "viz-mval" });
      c.setAttribute("text-anchor", "middle");

      var hit = el("rect", { x: 0, y: by - 4, width: w, height: bh + 8, class: "viz-hit" });
      svg.appendChild(hit);
      hoverable(hit, box, function(){
        return { title: cfg.name || "", rows: [
          { cls: cfg.cls || "s1", name: cfg.left || "",  value: known ? Math.round(v) + "%" : "—" },
          { cls: "total",         name: cfg.right || "", value: known ? (100 - Math.round(v)) + "%" : "—" }
        ]};
      });
    });
  }

  /* Cắt nhãn cho VỪA bề rộng đã cấp, có dấu "…".
     ⚠️ ĐO RỒI MỚI CẮT, và cắt bằng cách BỎ KÝ TỰ — không dùng `overflow:hidden`.
        `overflow:hidden` gặm mất chữ đầu (nhãn canh phải) nên "AI giúp tìm hành
        tinh ngoài Hệ Mặt Trời" thành "…oài Hệ Mặt Trời" hoặc tràn hẳn sang thẻ
        bên cạnh — cả hai đều tệ hơn một dấu "…" đúng chỗ.
     ⚠️ Nhãn đầy đủ KHÔNG BỊ MẤT: nó nằm ở tooltip (`aria-label` + trỏ chuột) và
        ở "Bảng số" — nơi không cắt gì cả. */
  function fitLabel(node, full, maxW){
    node.textContent = full;
    var len;
    try { len = node.getComputedTextLength(); } catch(e){ return; }
    if (len <= maxW) return;

    var s = String(full);
    // Tìm nhị phân số ký tự vừa chỗ — nhanh hơn bỏ từng ký tự với nhãn dài.
    var lo = 1, hi = s.length;
    while (lo < hi){
      var mid = (lo + hi + 1) >> 1;
      node.textContent = s.slice(0, mid) + "…";
      var l2;
      try { l2 = node.getComputedTextLength(); } catch(e){ break; }
      if (l2 <= maxW) lo = mid; else hi = mid - 1;
    }
    node.textContent = s.slice(0, lo).replace(/[\s·,;:-]+$/, "") + "…";
  }

  function table(box, cfg){
    if (box._vizOff) box._vizOff();
    box.textContent = "";
    var wrap = document.createElement("div");
    wrap.className = "viz-tablewrap";          // cuộn ngang NẰM TRONG khung này
    var t = document.createElement("table");
    t.className = "viz-table";

    if (cfg.caption){
      var cap = document.createElement("caption");
      cap.textContent = cfg.caption;
      t.appendChild(cap);
    }

    var thead = document.createElement("thead");
    var htr = document.createElement("tr");
    (cfg.head || []).forEach(function(s, i){
      var th = document.createElement("th");
      th.scope = "col";
      if (i > 0) th.className = "num";
      th.textContent = s;
      htr.appendChild(th);
    });
    thead.appendChild(htr);
    t.appendChild(thead);

    var tb = document.createElement("tbody");
    (cfg.rows || []).forEach(function(r){
      var tr = document.createElement("tr");
      r.forEach(function(c, i){
        var cell = document.createElement(i === 0 ? "th" : "td");
        if (i === 0) cell.scope = "row"; else cell.className = "num";
        // null → "—", KHÔNG phải 0. Cùng luật đã dùng ở parent.html: "chưa có
        // số" và "bằng 0" là hai câu khác nhau.
        cell.textContent = (c == null || c === "") ? "—" : String(c);
        tr.appendChild(cell);
      });
      tb.appendChild(tr);
    });
    t.appendChild(tb);
    wrap.appendChild(t);
    box.appendChild(wrap);
  }

  window.AstroQViz = {
    line: line, stack: stack, columns: columns, hbars: hbars,
    spark: spark, meter: meter, table: table,
    fmt: fmt
  };
})();
