/* ============================================================
   admin-report.js — trang báo cáo hệ thống (admin-report.html).

   Nhiệm vụ: gọi `GET /admin/stats` một lần, rồi vẽ. Không tính toán chỉ số nào ở
   đây — mọi con số do `Services/Insights.cs` tính; file này chỉ ĐỔI KHOÁ THÀNH TÊN
   và chọn hình dạng biểu đồ.

   ── BỐN LUẬT ────────────────────────────────────────────────────────────────
   ① KHÔNG KIỂM QUYỀN Ở ĐÂY. Server quyết ai được đọc (`ADMIN_EMAILS` +
      `email_verified`, xem Services/AdminAuth.cs). Ẩn/hiện theo một biến trong JS
      là kiểm quyền trang trí — ai cũng sửa được JS trong tab của họ. Ở đây chỉ có:
      gọi, rồi đọc câu trả lời của server (403 → hiện dải nhắc).
   ② `null` HIỆN "—", KHÔNG HIỆN 0. Server cố ý trả null cho "chưa đo được" và số
      cho "đã đo". Gộp hai thứ lại là khẳng định sai: "độ chính xác 0%" nói trẻ làm
      mà sai hết, còn sự thật có thể là chưa ai làm câu nào.
   ③ ĐỔI KHOẢNG KHÔNG GỌI LẠI API. Server trả sẵn 90 ngày; nút 7/30/90 chỉ cắt
      chuỗi ở client. Gọi lại mỗi lần bấm là mỗi lần quét cả bảng DynamoDB.
   ④ TÊN NẰM Ở CLIENT, MỐC NẰM Ở SERVER. Server trả `comet-tail` / `quiz-1` /
      `mercury`; tên hiển thị tra từ js/quiz-index.js, js/badges.js, js/planets.js,
      js/articles-index.js — mỗi cái tên khai đúng MỘT chỗ trong dự án.
   ============================================================ */
(function(){
  "use strict";

  var $ = AstroQ.$;
  var V = window.AstroQViz;
  var DASH = "—";
  var LANG = "vi";                 /* trang này một ngôn ngữ — lý do ở admin-report.html */

  /* ── Tên các bậc phễu. Thứ tự do SERVER quyết (Insights.Build); ở đây chỉ có
        tên. Bậc lạ (thêm ở server, chưa thêm tên ở đây) hiện chính khoá — xấu,
        nhưng thật, và nhìn là biết phải thêm tên. ── */
  var FUNNEL = {
    signup:     "Đăng ký & kích hoạt",
    tour:       "Xem Comet dẫn tham quan",
    map:        "Qua màn Bản Đồ Thiên Hà",
    mission:    "Vào màn mở đầu Nhiệm Vụ 01",
    quiz:       "Làm Đấu Trường lần đầu",
    earth_done: "Xong chuỗi Trái Đất",
    badge:      "Mở huy hiệu đầu tiên"
  };

  /* Năm loại việc — MÀU GẮN THEO THỰC THỂ, không theo hạng: quiz luôn là s1, dù
     tháng này nó xếp thứ mấy. Lọc bỏ một loại thì các loại còn lại giữ nguyên màu. */
  var TYPES = [
    { key:"quiz",    cls:"s1", name:"Đấu Trường" },
    { key:"game",    cls:"s2", name:"Huấn luyện" },
    { key:"lesson",  cls:"s3", name:"Bài đọc" },
    { key:"planet",  cls:"s4", name:"Hành tinh" },
    { key:"mission", cls:"s5", name:"Nhiệm vụ" }
  ];

  /* ⚠️ BẢNG TÊN BƯỚC NHIỆM VỤ — CHỈ LÀ NHÃN. Danh sách bước và THỨ TỰ do
     `Services/Missions.cs` quyết và server trả về; ở đây không được suy ra thứ tự.
     Bước `rotation` đã bỏ 02/08/2026 nên không có trong bảng này; bước mới thêm ở
     server mà quên thêm tên thì hiện chính id. */
  var STEPS = {
    scan:"Quét hành tinh", timeline:"Dòng thời gian", sun:"Mặt Trời",
    life:"Sự sống", energy:"Năng lượng", eco:"Sống xanh", core:"Lõi Trái Đất"
  };

  var DOWS = ["Hai","Ba","Tư","Năm","Sáu","Bảy","CN"];

  /* HAI bộ nhãn cho cùng một khoá là CÓ Ý: trục X có chỗ hẹp (5 nhãn cạnh nhau
     trên một khung nửa bề rộng), còn bảng số thì không. Dùng nhãn dài cho trục là
     chúng đè nhau; dùng nhãn ngắn cho bảng là mất nghĩa ("Chưa làm" cái gì?). */
  var ACC_TICK  = { none:"Chưa làm", lt50:"<50%", "50_69":"50–69%", "70_84":"70–84%", gte85:"≥85%" };
  var ACC_LABEL = { none:"Chưa làm câu nào", lt50:"Dưới 50%", "50_69":"50–69%",
                    "70_84":"70–84%", gte85:"85% trở lên" };
  var LV_TICK   = { lv1:"1", lv2_3:"2–3", lv4_5:"4–5", lv6_10:"6–10", lv11:"11+" };
  var LV_LABEL  = { lv1:"Cấp 1", lv2_3:"Cấp 2–3", lv4_5:"Cấp 4–5",
                    lv6_10:"Cấp 6–10", lv11:"Cấp 11+" };
  var BADGE_TICK  = { b0:"0", b1_2:"1–2", b3_5:"3–5", b6_10:"6–10", b11:"11+" };
  var BADGE_LABEL = { b0:"Chưa có cái nào", b1_2:"1–2 huy hiệu", b3_5:"3–5 huy hiệu",
                      b6_10:"6–10 huy hiệu", b11:"11 huy hiệu trở lên" };

  /* ── Trạng thái ── */
  var RANGE = 30;                  /* 7 | 30 | 90 — chỉ cắt ở client (luật ③) */
  var TOPKIND = "lesson";
  var R = null;                    /* thân báo cáo; null = chưa có số nào */
  var META = null;                 /* { cached, stale, ageSeconds, buildMs } */
  var ASTABLE = {};                /* card nào đang hiện bảng số */

  /* ════════════════ ĐỊNH DẠNG ════════════════ */

  function num(v){ return (v == null) ? DASH : Number(v).toLocaleString("vi-VN"); }
  function pct(v){ return (v == null) ? DASH : v + "%"; }

  function dmy(iso){
    var d = new Date(iso);
    if (isNaN(d)) return "?";
    return ("0"+d.getDate()).slice(-2) + "/" + ("0"+(d.getMonth()+1)).slice(-2);
  }

  function when(iso){
    var d = new Date(iso);
    if (isNaN(d)) return DASH;
    return dmy(iso) + " " + ("0"+d.getHours()).slice(-2) + ":" + ("0"+d.getMinutes()).slice(-2);
  }

  function hours(sec){
    if (!sec) return "0 phút";
    var m = Math.round(sec/60);
    return m < 90 ? m + " phút" : (m/60).toFixed(1).replace(".",",") + " giờ";
  }

  /* Tên chủ đề: server trả KHOÁ CÂU, `groupOf` đổi thành thẻ Sổ Tay + tên song
     ngữ. Khoá đã gỡ khỏi ngân hàng vẫn phải hiện — trẻ đã làm nó thật, bỏ đi là
     âm thầm nuốt mất một phần kết quả (cùng luật parent.html). */
  function termName(k){
    var g = window.AstroQQuestions ? AstroQQuestions.groupOf(k) : null;
    return (g && g.t && (g.t[LANG] || g.t.vi)) || k;
  }
  function badgeName(id){
    return window.AstroQBadges ? AstroQBadges.name(id, LANG) : id;
  }
  function badgeIcon(id){
    return window.AstroQBadges ? AstroQBadges.icon(id) : "🎖️";
  }
  function contentName(type, id){
    if (type === "planet" && window.AstroQPlanets) return AstroQPlanets.name(id, LANG) || id;
    if (type === "lesson" && window.AstroQArticles){
      var a = AstroQArticles.byId(id);
      if (a && a.title) return a.title[LANG] || a.title.vi || id;
    }
    if (type === "mission") return STEPS[id] || id;
    return id;                                  /* game: khoá đã là tên đọc được */
  }

  /* Cắt chuỗi ngày theo khoảng đang chọn (luật ③). */
  function slice(){ return (R && R.days ? R.days : []).slice(-RANGE); }
  function labels(){ return slice().map(function(d){ return dmy(d.day); }); }

  /* ════════════════ Ô SỐ LIỆU ════════════════ */

  function tiles(el, cells){
    el.textContent = "";
    var pending = [];        // đường tí hon, vẽ ở LƯỢT HAI — xem ghi chú cuối hàm

    cells.forEach(function(c){
      var cell = document.createElement("div");
      cell.className = "cell";

      var ic = document.createElement("span");
      ic.className = "ic"; ic.setAttribute("aria-hidden","true");
      ic.textContent = c.ic;
      cell.appendChild(ic);

      var b = document.createElement("span");
      b.className = "b";
      var v = document.createElement("span");
      v.className = "v"; v.textContent = c.v;
      b.appendChild(v);
      var k = document.createElement("span");
      k.className = "k"; k.textContent = c.k;
      // KHÔNG đặt `title` trùng chữ đang hiện: css/admin.css cho nhãn xuống dòng
      // nên không còn bị cắt, và một `title` lặp lại nội dung nhìn thấy được sẽ
      // bị trình đọc màn hình đọc hai lần.
      b.appendChild(k);
      if (c.sub){
        var s = document.createElement("span");
        s.className = "sub" + (c.tone ? " " + c.tone : "");
        s.textContent = c.sub;
        b.appendChild(s);
      }
      /* Đường tí hon — CHỈ khi chỉ số này có chuỗi theo ngày.

         ⚠️ ĐẶT TRONG `.b`, KHÔNG ĐẶT TRONG `.cell`. `.cell` là flex HÀNG NGANG
            (biểu tượng | khối chữ), nên thêm vào đó là sinh ra CỘT THỨ BA: khối
            chữ bị bóp còn một chữ mỗi dòng, và đường tí hon đo được một bề rộng
            vô lý rồi tràn sang ô bên cạnh — đã thấy đúng như vậy trên ảnh chụp.
            `.b` là flex CỘT, nên đường nằm đúng dưới dòng phụ.
         ⚠️ KHÔNG BỊA CHUỖI CHO CHỈ SỐ KHÔNG CÓ TRỤC THỜI GIAN. "Độ dính", "đang
            rời đi", "chờ kích hoạt" là ẢNH CHỤP MỘT THỜI ĐIỂM, tính từ trạng thái
            hiện tại của từng người — không có bản "hôm qua" nào để vẽ. Đặc biệt
            WAU/MAU KHÔNG suy ra được từ chuỗi người/ngày: cộng người của 7 ngày
            lại là đếm một người nhiều lần, mà tập người của từng ngày thì server
            không trả (và trả thì bản chụp phình lên). Vẽ một đường "gần đúng" ở
            đây là bịa số. Ô nào không có chuỗi thì không có đường, và CSS ẩn luôn
            ô rỗng để không ai đọc khoảng trắng đó thành "biểu đồ hỏng". */
      if (c.spark && c.spark.values && c.spark.values.length){
        var sp = document.createElement("div");
        sp.className = "spark";
        b.appendChild(sp);
        pending.push({ box: sp, cfg: c.spark, name: c.k });
      }

      cell.appendChild(b);
      el.appendChild(cell);
    });

    /* ⚠️ VẼ Ở LƯỢT HAI, SAU KHI ĐÃ THÊM ĐỦ MỌI Ô. `.kv` là lưới `auto-fit`, nên bề
       rộng mỗi cột PHỤ THUỘC TỔNG SỐ Ô: vẽ ngay sau khi thêm từng ô thì ô đầu đo
       một lưới 1 cột, ô cuối đo một lưới 8 cột — và ảnh chụp cho ra tám đường dài
       ngắn khác nhau trong tám ô bằng nhau. Thêm hết rồi mới đo là mỗi đường lấy
       đúng bề rộng cuối cùng của ô nó nằm trong. */
    pending.forEach(function(p){
      V.spark(p.box, { values:p.cfg.values, cls:p.cfg.cls || "s1",
                       unit:p.cfg.unit, name:p.cfg.name || p.name });
    });
  }

  function health(){
    var since = R.logSince ? dmy(R.logSince) : DASH;
    var s = slice();
    var col = function(k){ return s.map(function(d){ return d[k] || 0; }); };

    tiles($("kv-health"), [
      { ic:"🌱", v:num(R.newD7),  k:"Người mới 7 ngày",
        sub:"30 ngày: " + num(R.newD30),
        spark:{ values:col("signups"), cls:"s3", unit:"người", name:"Đăng ký mỗi ngày" } },
      { ic:"🔥", v:num(R.dau),    k:"Hoạt động hôm nay",
        sub:"7 ngày " + num(R.wau) + " · 30 ngày " + num(R.mau),
        spark:{ values:col("users"), cls:"s1", unit:"người", name:"Người hoạt động mỗi ngày" } },
      /* Độ dính = DAU/MAU. Diễn giải kèm chữ, KHÔNG chỉ đổi màu — màu một mình
         không bao giờ được là kênh duy nhất mang nghĩa. */
      { ic:"🧲", v:pct(R.stickiness), k:"Độ dính (ngày/tháng)",
        sub: R.stickiness == null ? "chưa có ai hoạt động"
           : R.stickiness >= 20 ? "khá — người dùng quay lại thường xuyên"
           : "thấp — phần lớn chỉ vào thưa thớt",
        tone: R.stickiness == null ? "" : (R.stickiness >= 20 ? "good" : "warn") },
      { ic:"🤫", v:num(R.silent), k:"Đăng ký rồi im lặng",
        sub:"trong số người đăng ký từ " + since },
      { ic:"🚪", v:num(R.churn),  k:"Đang rời đi",
        sub:"có việc trong 30 ngày, im 7 ngày gần nhất",
        tone: R.churn > 0 ? "warn" : "" },
      { ic:"✉️", v:num(R.pending), k:"Chờ bấm link kích hoạt",
        sub:"bản ghi hết hạn tự xoá, nên đây là số đang chờ" },
      { ic:"📮", v:num(R.waitlist), k:"Trong hàng chờ",
        sub:"chưa thành tài khoản",
        spark:{ values:col("waitlist"), cls:"s4", unit:"người", name:"Vào hàng chờ mỗi ngày" } },
      { ic:"🎯", v:pct(R.accuracy), k:"Độ chính xác toàn hệ thống",
        sub: R.quizAnswered ? num(R.quizCorrect) + "/" + num(R.quizAnswered) + " câu"
                            : "chưa ai làm câu nào" }
    ]);

    $("hero-n").textContent = num(R.totalUsers);

    /* ⚠️ NÓI RA KHI TÀI KHOẢN ADMIN ĐANG NẰM TRONG SỐ NÀY. Ở giai đoạn đầu nó có thể
       là phần lớn dữ liệu (bảng từng có ĐÚNG một người dùng, và đó là tài khoản admin).
       Server cố ý KHÔNG trừ nó ra — lý do ở Services/Insights.cs — nên trang phải nói,
       không thì "1 phi hành gia" đọc ra một người dùng thật mà thực ra là chính mình. */
    var u = $("hero-u");
    u.textContent = "phi hành gia đã kích hoạt tài khoản";
    if (R.adminAccounts > 0){
      var w = document.createElement("b");
      w.className = "hero-warn";
      w.textContent = " — trong đó " + num(R.adminAccounts) +
                      " tài khoản admin, vẫn được tính vào mọi chỉ số";
      u.appendChild(w);
    }
  }

  function econ(){
    var s = slice();
    var secs = s.reduce(function(a,d){ return a + (d.seconds||0); }, 0);
    tiles($("kv-econ"), [
      { ic:"💜", v:num(R.meteorsEarned), k:"Tổng tt đã trao",
        sub:"cả đời, mọi tài khoản",
        // Chuỗi này là tt TRAO RA theo nhật ký — cộng lại KHÔNG bằng ô bên trên
        // (ô đó là bộ đếm cả đời, có từ trước nhật ký). Hai câu khác nhau.
        spark:{ values:s.map(function(d){ return d.meteors || 0; }), cls:"s4",
                unit:"tt", name:"tt trao mỗi ngày" } },
      { ic:"🏦", v:num(R.meteorsBalance), k:"Đang giữ trong ví",
        sub:"chưa tiêu" },
      { ic:"🛒", v:pct(R.spentPct), k:"Tỉ lệ đã tiêu",
        sub: R.spentPct == null ? "chưa trao tt nào"
           : R.spentPct < 20 ? "thấp — tích mà không tiêu thì thưởng mất nghĩa"
           : R.spentPct > 80 ? "cao — giá vào lượt game có thể đang quá thấp"
           : "cân bằng",
        tone: R.spentPct == null ? "" : (R.spentPct < 20 || R.spentPct > 80 ? "warn" : "good") },
      { ic:"⏱️", v:hours(secs), k:"Giờ chơi game trong khoảng",
        sub:"chỉ tính lượt có ghi số giây",
        spark:{ values:s.map(function(d){ return Math.round((d.seconds||0)/60); }),
                cls:"s2", unit:"phút", name:"Phút chơi mỗi ngày" } }
    ]);
  }

  /* ════════════════ CHÚ GIẢI ════════════════
     CÓ MẶT bất cứ khi nào ≥ 2 series (biểu đồ một series thì tiêu đề đã nói nó là
     gì, thêm một ô chú giải là nhắc lại tiêu đề). Ô vuông cho khối, nét cho đường
     — khớp với hình thật của dấu trên biểu đồ. */
  function legend(el, items, asLine){
    el.textContent = "";
    items.forEach(function(it){
      var s = document.createElement("span");
      var i = document.createElement("i");
      i.className = it.cls + (asLine ? " line" : "");
      s.appendChild(i);
      var t = document.createElement("span");
      t.textContent = it.name;
      s.appendChild(t);
      el.appendChild(s);
    });
  }

  /* ════════════════ ĐĂNG KÝ BIỂU ĐỒ ════════════════
     Mỗi card có HAI cách vẽ từ CÙNG dữ liệu: `chart` và `table`. Nút "Bảng số"
     chỉ đổi cách vẽ — không có con số nào chỉ tới được bằng một trong hai (luật ④
     ở js/viz.js). */
  var CARDS = {

    /* ⚠️ HAI CON SO TREN MOT HANG, va chung KHONG cung don vi nguoi:
          "hang cho" la dia chi email, "tai khoan" la nguoi da kich hoat. Ve chung
          mot khung thanh la doc ra nhu mot dai luong bi chia doi. Nen khung chi ve
          TAI KHOAN (thu dang quan tam), con hang cho va ti le o lai nam o dong ghi
          chu ben canh — noi du ma khong bia ra mot phep so sai.
       ⚠️ NHAN RONG = "khong ro nguon", KHONG phai mot nguon ten rong. Phai doi ten
          ra chu, khong thi hang do ve ra mot thanh khong co nhan. */
    /* ⚠️ HAI HANG MOI NGUON, KHONG PHAI MOT. Cot dang doc nhat la "con hoat dong" -
          no phan biet mot bai mang toi dung nguoi voi mot bai chi mang toi luot bam.
          Bo do dau tien nhet no vao `note`, ma `note` cua hbars CHI HIEN O TOOLTIP:
          tren dien thoai khong re chuot duoc, tuc con so quan trong nhat bien mat o
          dung thiet bi phu huynh hay dung. Hai hang thi mat doc thang bang mat.
       ⚠️ KHONG TRUYEN `unit` LA MOT CHU cho hbars: no noi thang vao sau so, khong co
          khoang trang (`fmt(v)+unit`, xem js/viz.js) - dung vi co noi truyen "%" va
          "78 %" moi la sai. Do duoc: "17tai khoan" vua dinh chu vua TRAN ra ngoai
          khung 12px, vi o giu cho gia tri chi rong 52px. Don vi noi o tieu de.
       ⚠️ NHAN RONG = "khong ro nguon", KHONG phai mot nguon ten rong. Phai doi ra chu,
          khong thi hang do ve ra mot thanh khong co nhan. */
    sources: {
      plot: "p-src",
      rows: function(){
        return (R.sources || []).map(function(x){
          return {
            src:  x.src || "",
            name: x.src ? x.src : "(không rõ nguồn)",
            wait: x.waitlist  || 0,
            n:    x.signups   || 0,
            a7:   x.active7   || 0,
            done: x.earthDone || 0
          };
        });
      },
      chart: function(el){
        var out = [];
        CARDS.sources.rows().forEach(function(r){
          out.push({
            label: r.name, value: r.n, cls: r.src ? "s1" : "s2",
            note: r.wait + " địa chỉ trong hàng chờ · " + r.done + " người xong Trái Đất"
          });
          /* Nguon chua ra tai khoan nao thi KHONG ve hang thu hai: mot thanh 0 kem
             chu "con hoat dong" doc ra thanh mot loi phan xet, trong khi that ra
             chua co gi de do. */
          /* ⚠️ DAU "·" (U+00B7) CHU KHONG PHAI "↳" (U+21B3). Font tu host chi co
             subset latin + vietnamese (dot cat 621->101 KB ngay 26/07/2026), va
             U+21B3 KHONG nam trong do - render that ra mot glyph khac han cua font
             he thong. Doc bang unicode-range o css/fonts.css truoc khi dung mot ky
             hieu moi; muc [29] cua check_pages canh dung chuyen nay. */
          if (r.n > 0)
            out.push({ label: "· còn hoạt động", value: r.a7, cls: "s3",
                       note: "trong " + r.n + " tài khoản đến từ nguồn này" });
        });
        V.hbars(el, {
          rows: out, labelW: 240,
          emptyMsg:"Chưa có ai đến từ một link có gắn nhãn chiến dịch."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Nhãn chiến dịch lấy từ chính link mình đăng. Mỗi người được tính theo LƯỢT CHẠM ĐẦU TIÊN — đăng ký lại không đổi nguồn.",
          head:["Nguồn","Hàng chờ","Tài khoản","Còn hoạt động (7 ngày)","Xong Trái Đất"],
          rows: CARDS.sources.rows().map(function(r){
            return [r.name, num(r.wait), num(r.n), num(r.a7), num(r.done)];
          })
        });
      }
    },

    dau: {
      plot: "p-dau",
      chart: function(el){
        var s = slice();
        V.line(el, {
          labels: labels(),
          series: [{ name:"Người hoạt động", cls:"s1", values: s.map(function(d){ return d.users; }) }],
          unit: "người",
          emptyMsg: "Chưa có ngày nào ghi được hoạt động trong khoảng này."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Người hoạt động mỗi ngày (một người tính một lần/ngày).",
          head:["Ngày","Người","Việc","Đăng ký mới"],
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day), num(d.users), num(d.events), num(d.signups)];
          })
        });
      }
    },

    /* Đăng ký + hàng chờ: HAI series trên MỘT trục, và đó là hợp lệ vì cả hai cùng
       đơn vị "người/ngày". Luật cấm hai trục Y áp cho hai đại lượng KHÁC đơn vị
       (người vs số việc) — chỗ đó phải tách hai khung, xem `dau` và `mix`. */
    signup: {
      plot: "p-signup",
      series: [{ name:"Đăng ký & kích hoạt", cls:"s3", key:"signups" },
               { name:"Vào hàng chờ",        cls:"s4", key:"waitlist" }],
      chart: function(el){
        var s = slice(), me = CARDS.signup;
        V.line(el, {
          labels: labels(), unit:"người",
          series: me.series.map(function(x){
            return { name:x.name, cls:x.cls, values: s.map(function(d){ return d[x.key] || 0; }) };
          }),
          emptyMsg:"Chưa có ai đăng ký hay vào hàng chờ trong khoảng này."
        });
        legend($("lg-signup"), me.series, true);
      },
      table: function(el){
        var me = CARDS.signup;
        V.table(el, {
          caption:"Người đăng ký (đã kích hoạt) và người vào hàng chờ, theo ngày.",
          head:["Ngày","Đăng ký","Hàng chờ"],
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day), num(d.signups), num(d.waitlist)];
          })
        });
        legend($("lg-signup"), me.series, true);
      }
    },

    /* DAU/WAU/MAU là BA CỬA SỔ của cùng một câu hỏi, cùng đơn vị (người) → ba cột
       trên một trục. Không vẽ được thành đường theo thời gian: WAU/MAU cần TẬP
       người của từng cửa sổ trượt, mà chuỗi người/ngày không suy ra được (cộng
       lại là đếm một người nhiều lần). Ba cột là cách nói thật ở đây. */
    reach: {
      plot: "p-reach",
      chart: function(el){
        V.columns(el, {
          labels: ["Hôm nay", "7 ngày", "30 ngày"],
          values: [R.dau, R.wau, R.mau],
          cls:"s1", name:"người",
          emptyMsg:"Chưa ai hoạt động — nhật ký có thể chưa chảy trong khoảng này."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số người KHÁC NHAU có ít nhất một việc trong mỗi cửa sổ. Độ dính = hôm nay / 30 ngày.",
          head:["Cửa sổ","Người"],
          rows: [["Hôm nay", num(R.dau)], ["7 ngày", num(R.wau)], ["30 ngày", num(R.mau)],
                 ["Độ dính", pct(R.stickiness)]]
        });
      }
    },

    mix: {
      plot: "p-mix",
      chart: function(el){
        var s = slice();
        V.stack(el, {
          labels: labels(),
          totalName: "tổng",
          series: TYPES.map(function(t){
            return { name:t.name, cls:t.cls, values: s.map(function(d){ return d[t.key] || 0; }) };
          }),
          emptyMsg: "Chưa có việc nào được ghi trong khoảng này."
        });
        legend($("lg-mix"), TYPES);
      },
      table: function(el){
        V.table(el, {
          caption:"Số việc mỗi ngày, theo loại.",
          head:["Ngày"].concat(TYPES.map(function(t){ return t.name; })).concat(["Tổng"]),
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day)]
              .concat(TYPES.map(function(t){ return num(d[t.key] || 0); }))
              .concat([num(d.events)]);
          })
        });
        legend($("lg-mix"), TYPES);
      }
    },

    xp: {
      plot: "p-xp",
      chart: function(el){
        V.line(el, {
          labels: labels(), unit:"XP",
          series: [{ name:"XP trao", cls:"s1",
                     values: slice().map(function(d){ return d.xp || 0; }) }],
          emptyMsg:"Chưa trao XP nào trong khoảng này."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"XP trao mỗi ngày, theo nhật ký.",
          head:["Ngày","XP","Việc","Người"],
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day), num(d.xp), num(d.events), num(d.users)];
          })
        });
      }
    },

    secs: {
      plot: "p-secs",
      chart: function(el){
        V.columns(el, {
          labels: labels(),
          // Đổi sang PHÚT ngay ở đây: trục ghi bằng giây thì "7.200" đọc ra vô nghĩa.
          values: slice().map(function(d){ return Math.round((d.seconds||0)/60); }),
          cls:"s2", name:"phút",
          emptyMsg:"Chưa có lượt game nào ghi được số giây."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Thời gian chơi game mỗi ngày. Chỉ từ lượt CÓ ghi số giây, nên đây là chặn dưới.",
          head:["Ngày","Phút","Lượt game"],
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day), num(Math.round((d.seconds||0)/60)), num(d.game)];
          })
        });
      }
    },

    mt: {
      plot: "p-mt",
      chart: function(el){
        V.line(el, {
          labels: labels(), unit:"tt",
          series: [{ name:"tt trao", cls:"s4",
                     values: slice().map(function(d){ return d.meteors || 0; }) }],
          emptyMsg:"Chưa trao Thiên thạch tím nào trong khoảng này."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Thiên thạch tím TRAO RA mỗi ngày. ⚠️ Không phải số dư — tiền TIÊU không đi qua nhật ký, nên cộng chuỗi này không bằng ví.",
          head:["Ngày","tt trao","XP trao"],
          rows: slice().slice().reverse().map(function(d){
            return [dmy(d.day), num(d.meteors), num(d.xp)];
          })
        });
      }
    },

    spend: {
      plot: "p-spend",
      chart: function(el){
        V.meter(el, {
          pct: R.spentPct,                 // null → thanh rỗng + "—", không phải 0%
          left: "Đã tiêu", right: "Còn giữ trong ví",
          name: "Thiên thạch tím",
          // Dải MỘT TÔNG: "đã tiêu / còn giữ" là một tỉ lệ, không phải hai danh
          // tính — dùng hai màu phân loại ở đây sẽ đụng màu của quiz/game.
          cls: "r5", trackCls: "r1"
        });
      },
      table: function(el){
        var spent = R.meteorsEarned == null ? null
                  : Math.max(0, R.meteorsEarned - (R.meteorsBalance || 0));
        V.table(el, {
          caption:"Đã tiêu = tổng đã trao − số dư còn lại. Kẹp ở 0: hồ sơ cũ có ví trước khi có bộ đếm `meteorsEarned`, nên hiệu có thể âm.",
          head:["Mục","tt"],
          rows: [["Tổng đã trao", num(R.meteorsEarned)],
                 ["Còn giữ trong ví", num(R.meteorsBalance)],
                 ["Đã tiêu", num(spent)],
                 ["Tỉ lệ đã tiêu", pct(R.spentPct)]]
        });
      }
    },

    funnel: {
      plot: "p-funnel",
      chart: function(el){
        var f = R.funnel || [];
        V.hbars(el, {
          labelW: 168,
          max: f.length ? f[0].n : 0,
          name: "người",
          /* Bậc phễu CÓ THỨ TỰ → dải MỘT TÔNG (`r0`…`r6`), không phải màu phân
             loại. Càng vào sâu càng đậm. */
          rows: f.map(function(st, i){
            return {
              label: FUNNEL[st.key] || st.key,
              value: st.n,
              cls: "r" + Math.min(6, i),
              note: st.drop == null ? (st.pct == null ? "bậc đầu" : "")
                                    : "rơi " + st.drop + "% so với bậc trước"
            };
          }),
          emptyMsg:"Chưa có người dùng nào."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Phễu onboarding. Cột “rơi” so với bậc liền trước; một bậc không bao hàm bậc trước nên số có thể tăng.",
          head:["Bậc","Người","% so bậc đầu","Rơi so bậc trước"],
          rows: (R.funnel || []).map(function(st){
            return [FUNNEL[st.key] || st.key, num(st.n),
                    st.pct == null ? null : st.pct + "%",
                    st.drop == null ? null : st.drop + "%"];
          })
        });
      }
    },

    ret: {
      plot: "p-ret",
      chart: function(el){
        var rt = R.retention || [];
        V.hbars(el, {
          labelW: 108, max: 100, unit:"%", name:"giữ chân",
          rows: rt.map(function(x, i){
            return {
              label: "Ngày " + x.days,
              /* ⚠️ TRUYỀN THẲNG `null`, KHÔNG ĐỔI THÀNH 0. `V.hbars` in "—" cho
                 null và "0" cho 0. Bản đầu đổi null→0 ở đây, và mốc 30 ngày hiện
                 "0%" khi chưa ai đăng ký đủ 30 ngày — tức nói "đủ tuổi mà không
                 ai quay lại", đúng lời khẳng định sai mà luật ② cấm. */
              value: x.pct,
              cls: "r" + [2,4,6][i],
              note: x.cohort === 0 ? "chưa ai đăng ký đủ " + x.days + " ngày"
                                   : x.returned + "/" + x.cohort + " người quay lại"
            };
          }),
          emptyMsg:"Chưa đo được."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Giữ chân kiểu “trôi”: có việc từ ngày thứ N trở đi. Chỉ tính người đăng ký sau mốc bắt đầu ghi nhật ký.",
          head:["Mốc","Nhóm đủ tuổi","Quay lại","Tỉ lệ"],
          rows: (R.retention || []).map(function(x){
            return ["Ngày " + x.days, num(x.cohort), num(x.returned),
                    x.pct == null ? null : x.pct + "%"];
          })
        });
      }
    },

    hours: {
      plot: "p-hours",
      chart: function(el){
        V.columns(el, {
          labels: (R.hours || []).map(function(_, h){ return ("0"+h).slice(-2) + "h"; }),
          values: R.hours || [], cls:"s1", name:"việc", xStep: 3,
          emptyMsg:"Chưa có việc nào được ghi."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số việc theo giờ trong ngày (giờ Việt Nam), toàn bộ 90 ngày.",
          head:["Giờ","Việc"],
          rows: (R.hours || []).map(function(v, h){ return [("0"+h).slice(-2)+"h", num(v)]; })
        });
      }
    },

    dows: {
      plot: "p-dows",
      chart: function(el){
        V.columns(el, {
          labels: DOWS, values: R.weekdays || [], cls:"s1", name:"việc",
          emptyMsg:"Chưa có việc nào được ghi."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số việc theo thứ trong tuần, toàn bộ 90 ngày.",
          head:["Thứ","Việc"],
          rows: DOWS.map(function(d, i){ return [d, num((R.weekdays||[])[i])]; })
        });
      }
    },

    weak: {
      plot: "p-weak",
      chart: function(el){
        var w = R.weakTerms || [];
        V.hbars(el, {
          labelW: 150, name:"lượt sai",
          /* Hạng mục KHÔNG có thứ tự tự nhiên → MỘT màu cho mọi thanh. Tô
             đậm-theo-giá-trị ở đây là đốt kênh màu để nhắc lại độ dài thanh. */
          rows: w.map(function(t){
            return { label: termName(t.term), value: t.wrong, cls:"s1",
                     note: t.wrong + " sai / " + (t.ok + t.wrong) + " lượt · " + t.pct + "% sai" };
          }),
          emptyMsg:"Chưa ghi được câu sai nào — hoặc chưa ai làm quiz, hoặc nhật ký chưa chảy."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Chủ đề trẻ sai nhiều nhất. Xếp theo số lượt sai.",
          head:["Chủ đề","Sai","Đúng","% sai","Khoá câu"],
          rows: (R.weakTerms || []).map(function(t){
            return [termName(t.term), num(t.wrong), num(t.ok), t.pct + "%", t.term];
          })
        });
      }
    },

    top: {
      plot: "p-top",
      chart: function(el){
        var list = (R.topContent || {})[TOPKIND] || [];
        var t = TYPES.filter(function(x){ return x.key === TOPKIND; })[0] || TYPES[0];
        V.hbars(el, {
          // Rộng hơn các thẻ khác: tên bài đọc là câu hoàn chỉnh ("AI giúp tìm hành
          // tinh ngoài Hệ Mặt Trời"), không phải một từ như tên chủ đề quiz.
          labelW: 196, name:"lượt",
          // MÀU THEO THỰC THỂ: bài đọc luôn lục, hành tinh luôn tím — khớp biểu
          // đồ chồng ở trên, nên người đọc không phải học lại màu.
          rows: list.map(function(c){
            return { label: contentName(TOPKIND, c.key), value: c.n, cls: t.cls, note: c.key };
          }),
          emptyMsg:"Chưa ghi được lượt nào cho loại này."
        });
      },
      table: function(el){
        var list = (R.topContent || {})[TOPKIND] || [];
        V.table(el, {
          caption:"Nội dung được dùng nhiều nhất, theo nhật ký 90 ngày.",
          head:["Nội dung","Lượt","Khoá"],
          rows: list.map(function(c){ return [contentName(TOPKIND, c.key), num(c.n), c.key]; })
        });
      }
    },

    acc: {
      plot: "p-acc",
      chart: function(el){
        var d = R.accuracyDist || [];
        V.columns(el, {
          labels: d.map(function(b){ return ACC_TICK[b.key] || b.key; }),
          values: d.map(function(b){ return b.n; }),
          cls:"s1", name:"người",
          emptyMsg:"Chưa có người dùng nào."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số người theo khoảng độ chính xác (bộ đếm cả đời).",
          head:["Khoảng","Người"],
          rows: (R.accuracyDist || []).map(function(b){
            return [ACC_LABEL[b.key] || b.key, num(b.n)];
          })
        });
      }
    },

    lv: {
      plot: "p-lv",
      chart: function(el){
        var d = R.levelDist || [];
        V.columns(el, {
          labels: d.map(function(b){ return LV_TICK[b.key] || b.key; }),
          values: d.map(function(b){ return b.n; }),
          cls:"s1", name:"người",
          emptyMsg:"Chưa có người dùng nào."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số người theo cấp độ (tính từ XP, xem Services/Achievements.cs).",
          head:["Cấp","Người"],
          rows: (R.levelDist || []).map(function(b){ return [LV_LABEL[b.key] || b.key, num(b.n)]; })
        });
      }
    },

    steps: {
      plot: "p-steps",
      chart: function(el){
        var m = (R.missions || []).filter(function(x){ return x.id === "earth"; })[0];
        var st = m ? m.steps : [];
        V.hbars(el, {
          labelW: 128, name:"người",
          // Bước CÓ THỨ TỰ → dải một tông, càng sâu càng đậm.
          rows: st.map(function(s, i){
            return { label: STEPS[s.key] || s.key, value: s.n, cls:"r" + Math.min(6, i), note: s.key };
          }),
          emptyMsg:"Chưa ai bắt đầu nhiệm vụ."
        });
      },
      table: function(el){
        var m = (R.missions || []).filter(function(x){ return x.id === "earth"; })[0];
        V.table(el, {
          caption:"Số người đã xong từng bước, đúng thứ tự chơi. Cột giảm ở đâu là trẻ bỏ dở ở đó.",
          head:["Bước","Người","Khoá"],
          rows: (m ? m.steps : []).map(function(s){
            return [STEPS[s.key] || s.key, num(s.n), s.key];
          })
        });
      }
    },

    badges: {
      plot: "p-badges",
      chart: function(el){
        var d = R.badgeDist || [];
        V.columns(el, {
          labels: d.map(function(b){ return BADGE_TICK[b.key] || b.key; }),
          values: d.map(function(b){ return b.n; }),
          cls:"s1", name:"người",
          emptyMsg:"Chưa có người dùng nào."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Số người theo số huy hiệu đang có.",
          head:["Số huy hiệu","Người"],
          rows: (R.badgeDist || []).map(function(b){
            return [BADGE_LABEL[b.key] || b.key, num(b.n)];
          })
        });
      }
    },

    rare: {
      plot: "p-rare",
      chart: function(el){
        var list = (R.rareBadges || []).slice(0, 10);
        V.hbars(el, {
          labelW: 168, name:"người mở",
          rows: list.map(function(b){
            return { label: badgeIcon(b.key) + " " + badgeName(b.key), value: b.n, cls:"s1", note: b.key };
          }),
          emptyMsg:"Chưa khai huy hiệu nào."
        });
      },
      table: function(el){
        V.table(el, {
          caption:"Huy hiệu ít người mở nhất. Chỉ liệt kê huy hiệu đang khai ở server.",
          head:["Huy hiệu","Người mở","Khoá"],
          rows: (R.rareBadges || []).map(function(b){
            return [badgeIcon(b.key) + " " + badgeName(b.key), num(b.n), b.key];
          })
        });
      }
    }
  };

  /* Bảng người dùng: bản thân nó ĐÃ là bảng, nên không có biểu đồ song sinh. */
  function users(){
    V.table($("p-users"), {
      caption:"Xếp theo số việc giảm dần. Không có email, không có tên — chỉ 8 ký tự đầu của mã tài khoản. Dòng ghi “admin” là tài khoản quản trị, vẫn được tính vào mọi chỉ số.",
      head:["Mã","Đăng ký","Ngày hoạt động","Việc","XP","Cấp","Huy hiệu","Độ chính xác","Lần cuối"],
      rows: (R.userTable || []).map(function(u){
        // Đánh dấu ngay ở cột mã: người đọc thấy dòng nào là của mình mà không phải
        // đối chiếu uid bằng mắt.
        return [u.uid + (u.isAdmin ? " · admin" : ""),
                u.since ? dmy(u.since) : null,
                num(u.activeDays), num(u.events), num(u.xp), num(u.level), num(u.badges),
                u.accuracy == null ? null : u.accuracy + "%",
                u.last ? when(u.last) : null];
      })
    });
  }

  /* ════════════════ VẼ ════════════════ */

  function paintCard(id){
    var c = CARDS[id], el = $(c.plot);
    if (!el) return;
    (ASTABLE[id] ? c.table : c.chart)(el);
  }

  function paint(){
    if (!R) return;

    ["sec-health","sec-activity","sec-funnel","sec-rhythm","sec-content",
     "sec-progress","sec-econ","sec-users"].forEach(function(id){ $(id).hidden = false; });
    $("bar").hidden = false;

    health();
    econ();
    Object.keys(CARDS).forEach(paintCard);
    users();

    $("note-since").textContent = R.logSince ? dmy(R.logSince) + "/" + new Date(R.logSince).getFullYear() : DASH;
    stamp();
  }

  /* Nhãn "số liệu tính lúc…". Bản chụp quá hạn vì lượt tính lại HỎNG thì phải nói
     ra bằng CHỮ, không chỉ đổi màu đèn (màu một mình không mang nghĩa được). */
  function stamp(){
    var el = $("stamp");
    el.textContent = "";
    el.className = "ad-stamp" + (META && (META.stale || R.truncated) ? " stale" : "");

    var dot = document.createElement("span");
    dot.className = "dot"; dot.setAttribute("aria-hidden","true");
    el.appendChild(dot);

    var txt = document.createElement("span");
    var mins = META ? Math.round((META.ageSeconds || 0)/60) : 0;
    var parts = ["Số liệu tính lúc " + when(R.generatedAt)];
    if (META && META.ageSeconds > 90) parts.push(mins + " phút trước");
    if (META && META.stale) parts.push("lượt tính lại vừa hỏng — đây là bản chụp cũ");
    if (META && META.throttled) parts.push("vừa tính lại xong, thử lại sau ít phút");
    if (R.truncated) parts.push("⚠ bảng quá lớn nên báo cáo BỊ CẮT");
    parts.push(num(R.scannedItems) + " bản ghi");
    txt.textContent = parts.join(" · ");
    el.appendChild(txt);
  }

  /* ════════════════ NÚT ════════════════ */

  function segRange(){
    var box = $("range");
    box.textContent = "";
    [7, 30, 90].forEach(function(n){
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = n + " ngày";
      if (n === RANGE) b.className = "on";
      b.setAttribute("aria-pressed", n === RANGE);
      b.addEventListener("click", function(){
        RANGE = n;
        segRange();
        /* Chỉ vẽ lại thứ ĐỌC CHUỖI NGÀY (`slice()`), cộng cả hai khối ô số liệu vì
           chúng mang đường tí hon.
           ⚠️ CỐ Ý KHÔNG vẽ lại `reach`, `funnel`, `ret`, `hours`, `dows`, `weak`,
              `top`, `acc`, `lv`, `badges`, `steps`, `rare`, `spend`: chúng là số
              TỔNG của cả 90 ngày (hoặc cả đời), server tính một lần. Cắt chúng ở
              client là bịa — muốn chúng theo khoảng thì phải tính lại ở SERVER.
              Vì thế mô tả từng thẻ nói rõ nó tính trên khoảng nào. */
        ["dau","mix","signup","xp","secs","mt"].forEach(paintCard);
        health();
        econ();
      });
      box.appendChild(b);
    });
  }

  function segTopKind(){
    var box = $("top-kind");
    box.textContent = "";
    TYPES.filter(function(t){ return t.key !== "quiz"; }).forEach(function(t){
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = t.name;
      if (t.key === TOPKIND) b.className = "on";
      b.setAttribute("aria-pressed", t.key === TOPKIND);
      b.addEventListener("click", function(){
        TOPKIND = t.key; segTopKind(); paintCard("top");
      });
      box.appendChild(b);
    });
  }

  function wireSwaps(){
    Array.prototype.forEach.call(document.querySelectorAll(".ad-card"), function(card){
      var id = card.getAttribute("data-card");
      var btn = card.querySelector(".swap");
      if (!id || !btn || !CARDS[id]) return;
      btn.addEventListener("click", function(){
        ASTABLE[id] = !ASTABLE[id];
        btn.setAttribute("aria-pressed", ASTABLE[id] ? "true" : "false");
        btn.textContent = ASTABLE[id] ? "Biểu đồ" : "Bảng số";
        paintCard(id);
      });
    });
  }

  /* ════════════════ TẢI ════════════════ */

  /* ⚠️ DẢI NHẮC PHẢI CÓ ĐƯỜNG ĐI TIẾP, KHÔNG ĐƯỢC LÀ NGÕ CỤT. Bản đầu chỉ ghi
     "cần đăng nhập" rồi dừng — mà trang này KHÔNG có form đăng nhập (form đó nằm ở
     `landing-app.html`, và `js/firebase-auth-ui.js` gắn chặt vào popup của trang
     đó nên không mượn sang đây được). Không có link thì người đọc phải tự đoán ra
     tên file. Đó là lỗi thật, không phải thiếu sót nhỏ.
     `link` = { href, text } — dựng bằng createElement, KHÔNG ghép innerHTML. */
  function gate(msg, icon, link){
    var box = $("gate-msg");
    box.textContent = msg;
    if (link){
      box.appendChild(document.createTextNode(" "));
      var a = document.createElement("a");
      a.href = link.href;
      a.textContent = link.text;
      box.appendChild(a);
    }
    $("gate").querySelector(".ic").textContent = icon || "🔒";
    $("gate").classList.add("show");
  }

  function busy(on){
    Array.prototype.forEach.call(document.querySelectorAll(".ad-card"), function(c){
      c.classList.toggle("busy", !!on);
    });
  }

  function load(refresh){
    if (!window.AstroQAuth || !AstroQAuth.getAdminStats){
      // SDK chưa nạp xong — chờ một nhịp. Đừng kết luận "chưa đăng nhập".
      setTimeout(function(){ load(refresh); }, 400);
      return;
    }

    busy(true);
    $("refresh").disabled = true;

    AstroQAuth.getAdminStats(refresh).then(function(r){
      busy(false);
      $("refresh").disabled = false;

      if (r && r.ok){
        $("gate").classList.remove("show");
        META = r.data;
        R = r.data.report;
        paint();
        return;
      }

      /* Luật ①: server quyết, client chỉ đọc câu trả lời. Bốn lý do bốn câu khác
         nhau — gộp thành "lỗi" là nói sai trong ba trường hợp. */
      if (r && r.status === 403)
        /* ⚠️ KHÔNG in ra email nào đang được phép. Trang này không nối từ đâu, nhưng
           ai vào được link cũng đọc được dòng nhắc — và một dòng "chỉ a@b.com mới
           xem được" là tự khai đích cho người muốn thử. Nói CÁCH SỬA, không nói AI. */
        gate("Bạn đang đăng nhập bằng một tài khoản không nằm trong danh sách admin. " +
             "Đăng xuất rồi vào lại bằng email admin, hoặc thêm email này vào tham số " +
             "AdminEmails của stack rồi deploy lại (xem AstroqSV/template.yaml).", "⛔",
             { href:"landing-app.html", text:"Đổi tài khoản" });
      else if (r && (r.reason === "auth" || r.status === 401))
        gate("Chưa đăng nhập. Trang này không có form đăng nhập riêng — vào bằng tài " +
             "khoản admin ĐÃ KÍCH HOẠT ở trang đăng nhập chung, rồi quay lại đường dẫn " +
             "/admin-report.html.", "🔑",
             { href:"landing-app.html", text:"Tới trang đăng nhập" });
      else if (r && r.status === 503)
        gate("Server không quét được bảng và chưa có bản chụp nào để hiện. Thử lại sau.", "📡");
      /* ⚠️ 404 KHÔNG PHẢI LỖI MẠNG — phải nói khác hẳn. Nhóm route `/admin` chỉ tồn tại
         sau khi deploy AstroqSV; trang tĩnh thì lên GitHub Pages ngay khi push, còn
         Lambda phải `sam deploy` riêng. Hai thứ lệch nhịp là chuyện BÌNH THƯỜNG, và
         gộp nó vào "kiểm tra mạng" là chỉ người đọc đi sửa đúng thứ không hỏng.
         (Đã gặp thật: frontend live, `/health` trả 200, `/admin/stats` trả 404.) */
      else if (r && r.status === 404)
        gate("Server chưa có route /admin/stats — backend AstroqSV chưa được deploy " +
             "bản mới. Chạy `sam deploy` trong thư mục AstroqSV rồi tải lại trang.", "🛠️");
      else
        gate("Không gọi được server. Kiểm tra mạng rồi tải lại trang.", "📡");
    }).catch(function(){
      busy(false);
      $("refresh").disabled = false;
      gate("Không gọi được server. Kiểm tra mạng rồi tải lại trang.", "📡");
    });
  }

  /* ════════════════ KHỞI ĐỘNG ════════════════ */

  $("back").addEventListener("click", function(){ location.href = "dashboard.html"; });
  $("refresh").addEventListener("click", function(){ load(true); });

  segRange();
  segTopKind();
  wireSwaps();
  load(false);
})();
