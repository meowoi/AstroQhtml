/* ============================================================
   sticker-icons.js — BỘ ICON PHONG CÁCH STICKER, khớp art nhân vật + thiên thạch tím.
   Dùng: element.innerHTML = sic("meteor");   // hoặc AstroQ.sic(...)

   ⚠️ ĐÂY LÀ BỘ THỨ HAI, KHÔNG THAY `js/icons.js`. Hai bộ hai việc khác nhau:
      • `lic()` — nét mảnh đơn sắc, kế thừa `currentColor`. Dùng cho icon CHỨC NĂNG
        cỡ nhỏ (nút, nhãn, dòng chữ) — chỗ mà một hình nhiều màu sẽ hút mắt sai chỗ.
      • `sic()` — sticker nhiều lớp, có gradient + gloss + sparkle. Dùng cho icon
        NHẬN DIỆN cỡ lớn (thẻ HUD, thẻ game, tiêu đề khu, nhóm mẫu vật) — chỗ đang
        dùng emoji, tức chỗ mà mỗi hệ điều hành vẽ ra một kiểu khác nhau.
      Gộp hai bộ là một trong hai đằng sai: hoặc nút bấm rực rỡ quá, hoặc thẻ HUD
      nhạt như một dòng chữ.

   ── CÔNG THỨC STICKER (đọc trước khi vẽ thêm) ──────────────────────────────
   Mỗi icon dựng 5 LỚP, JS tự nhân bản hình nên KHÔNG chép path ba lần:
      ⓪ edge — chính hình đó, nét navy DÀY NHẤT            → nét ngoài cùng
      ① rim  — chính hình đó, tô trắng + nét trắng dày     → rìa sticker
      ② ink  — chính hình đó, tô gradient + nét navy       → thân icon
      ③ line — nét navy mảnh, không tô                     → chi tiết bên trong
      ④ lite — trắng, không nét                            → gloss + sparkle + đốm sao
   Vì ⓪ ① ② dùng CÙNG một chuỗi hình, sửa hình là ba lớp đổi theo. Đừng tách ra.

   ⚠️⚠️ LỚP ⓪ LÀ BẮT BUỘC, KHÔNG PHẢI TRANG TRÍ. Soi `img/tt.png` thì thứ tự thật
      là: thân tím → khe TRẮNG → **nét navy ngoài cùng**. Bản đầu của tôi bỏ lớp
      ngoài này, và hậu quả đo được ngay khi render trên nền sáng: rìa trắng nằm
      trên nền trắng thì **biến mất hoàn toàn**, icon trông như bị cắt mất viền.
      Chính nét navy ngoài mới là thứ làm sticker đọc được trên MỌI nền.

   ⚠️ TOẠ ĐỘ TRONG KHUNG 64×64, viewBox nới ra `-8 -8 80 80` để chừa chỗ cho ba nét
      vẽ RA NGOÀI đường bao (13 + 9 + 4). Hình chạm mép 64 thì vẫn an toàn, nhưng
      **đừng vẽ ra ngoài 0..64** — phần đó ăn vào lề của lớp ⓪ và rìa bị cắt phẳng
      một bên, nhìn ra ngay như ảnh bị crop.

   ⚠️ ĐỪNG VẼ CHI TIẾT NHỎ HƠN ~3 ĐƠN VỊ. Icon này hiển thị ở 28–56px, tức 1 đơn vị
      ≈ 0,5–0,9px. Bộ `lic()` vẽ được chi tiết mảnh vì nó chỉ có nét; ở đây mỗi hình
      còn phải cõng thêm rìa trắng 9 + nét navy 4 nên chi tiết nhỏ bị bịt kín.

   ⚠️ GRADIENT KHAI TRONG TỪNG SVG, ID CÓ HẬU TỐ ĐẾM — không dùng một sprite defs
      chung. Lý do: `<use>` dựng shadow tree nên CSS của trang KHÔNG với tới được
      hình bên trong, mà các lớp trên cần đúng chuyện đó (`.f-cy`, `.f-dk`…). Và id
      trùng nhau trong một trang thì mọi icon lấy gradient của cái đầu tiên.
   ⚠️ Stop màu đọc `var(--sic-a/--sic-b)` nên đổi bảng màu bằng CLASS ở ngoài
      (`sic--cyan`, `sic--gold`…) — xem `css/sticker-icons.css`. Biến CSS thừa
      hưởng theo DOM, mà gradient nằm TRONG chính svg đó, nên nó nhận đúng biến.
   ============================================================ */
(function (global) {
  "use strict";

  /* Sparkle 4 cánh — thành ngữ lặp lại nhiều nhất của bộ art (thiên thạch tím có
     một cái ở giữa, nhân vật có vài cái quanh người). Sinh bằng hàm để mọi sparkle
     trong bộ có cùng tỉ lệ thắt eo; vẽ tay từng cái là sớm muộn mỗi chỗ một dáng. */
  function sp(x, y, r) {
    var w = r * 0.30; /* eo: 30% bán kính — mảnh hơn thì thành dấu cộng, dày hơn thành ngôi sao */
    return 'M' + x + ' ' + (y - r) +
      'C' + (x + w) + ' ' + (y - w) + ' ' + (x + w) + ' ' + (y - w) + ' ' + (x + r) + ' ' + y +
      'C' + (x + w) + ' ' + (y + w) + ' ' + (x + w) + ' ' + (y + w) + ' ' + x + ' ' + (y + r) +
      'C' + (x - w) + ' ' + (y + w) + ' ' + (x - w) + ' ' + (y + w) + ' ' + (x - r) + ' ' + y +
      'C' + (x - w) + ' ' + (y - w) + ' ' + (x - w) + ' ' + (y - w) + ' ' + x + ' ' + (y - r) + 'Z';
  }
  function spark(x, y, r) { return '<path d="' + sp(x, y, r) + '"/>'; }

  /* Đốm sao li ti — `img/tt.png` rải kín mặt đá bằng thứ này, và nó là chi tiết
     rẻ nhất để một hình phẳng đọc ra "có chiều sâu, đang phát sáng".
     ⚠️ Bán kính ≥0.9 đơn vị: nhỏ hơn thì ở 24px nó biến mất, tức là một chi tiết
        chỉ tồn tại trên bản thiết kế chứ không tồn tại với người dùng. */
  function dust() {
    var s = '', i, a = arguments;
    for (i = 0; i < a.length; i += 3) {
      s += '<circle cx="' + a[i] + '" cy="' + a[i + 1] + '" r="' + a[i + 2] + '"/>';
    }
    return s;
  }

  /* body: hình chính (vào CẢ lớp rim và lớp ink) · line: nét chi tiết · lite: gloss+sparkle */
  var SIC = {

    /* ══ CHƯA CÓ CHỖ DÙNG — ĐỌC TRƯỚC KHI THÊM CÁI THỨ BẢY ═══════════════
       Sáu icon dưới đây vẽ xong nhưng CHƯA trang nào gọi tới, và đó là chuyện
       có chủ đích chứ không phải bỏ quên. Ghim thành một danh sách kín (giống
       lối `LEGACY_SRC` / `PENDING_BANK` đã dùng ở chỗ khác) để thêm một icon
       ngủ thứ bảy là phép kiểm `check_pages` mục [21] báo ngay.

       ⚠️ `leaf` ĐÃ THÔI NGỦ 16/08/2026 — thẻ Trạm Tuần Hoàn (ARCADE-09) ở
          `games.html` dùng nó, và ô icon của thẻ game là **64px**, thừa sàn 22px.
          Đó đúng là cách danh sách này được rút ngắn: tìm một ô ĐỦ LỚN cho icon
          đã vẽ, chứ không nhét icon vào ô nhỏ.

       ⚠️ `wave` · `rock` (và `leaf` trước 16/08) vẽ cho 4 NHÓM QUYỂN của Kho Mẫu Vật, rồi ĐO
          mới thấy nhóm quyển không có ô nào đủ lớn: chip `.cc` **10,5px**, nút
          lọc là chữ inline, tiêu đề `.panel h2 .ic` **19px** — đều dưới sàn
          22px của bộ này. Ô thật sự lớn ở trang đó là **`.pod .sp` 46px**, tức
          21 mẫu vật RIÊNG chứ không phải 4 nhóm; đó là một đợt vẽ khác.
       ⚠️ `globe` · `map` · `lock` cùng cảnh: chỗ đang dùng 🌍/🗺️/🔒 đều là
          tiêu đề 19px hoặc nhãn 10px.
       ⇒ Muốn dùng chúng thì NỚI Ô TRƯỚC, đừng nhét icon vào ô nhỏ rồi chấp
         nhận nó thành một vệt màu. */

    globe: { /* 🌍 */
      body: '<circle cx="32" cy="32" r="25"/>',
      line: '<path d="M32 7c-9 8-9 42 0 50M32 7c9 8 9 42 0 50M8 24h48M8 40h48"/>',
      lite: '<path d="M17 19a22 22 0 0 1 13-8 26 26 0 0 0-9 11Z"/>' + spark(54, 11, 5)
    },
    map: { /* 🗺️ */
      body: '<path d="M6 16 22 10l20 8 16-6v36l-16 6-20-8-16 6Z"/>',
      line: '<path d="M22 10v36M42 18v36"/>',
      lite: '<circle cx="32" cy="30" r="3.4"/>' + spark(52, 45, 5)
    },
    lock: { /* 🔒 */
      body: '<path d="M20 28v-8a12 12 0 0 1 24 0v8h-8v-8a4 4 0 0 0-8 0v8Z"/>' +
            '<rect x="13" y="27" width="38" height="29" rx="6"/>' +
            '<circle class="f-dk" cx="32" cy="39" r="4.4"/>' +
            '<path class="f-dk" d="M29.6 41h4.8l1.2 8h-7.2Z"/>',
      lite: '<path d="M17 33a4 4 0 0 1 4-3v20h-4Z"/>' + spark(52, 16, 5)
    },
    wave: { /* 🌊 Thuỷ quyển */
      body: '<path d="M6 25c6-6 12-6 18 0s12 6 18 0 12-6 16 0v11c-4-6-10-6-16 0s-12 6-18 0-12-6-18 0Z"/>' +
            '<path d="M6 44c6-6 12-6 18 0s12 6 18 0 12-6 16 0v10c-4-6-10-6-16 0s-12 6-18 0-12-6-18 0Z"/>',
      lite: spark(49, 13, 6) + dust(14, 18, 1.3)
    },
    leaf: { /* 🌿 Sinh quyển */
      body: '<path d="M53 7c4 23-9 41-31 45-6 1-11-3-12-9C7 24 26 9 53 7Z"/>',
      line: '<path d="M50 10C36 22 24 37 13 51M40 16c1 6 0 11-2 15M30 25c2 5 2 10 0 14"/>',
      lite: spark(19, 13, 5)
    },
    rock: { /* 🪨 Địa quyển — CỐ Ý dẹt hơn và nhiều mặt cắt hơn `meteor`. Hai hình
                cùng là khối đá thì phải tách nhau ra được ở cỡ 24px, không thì
                nhóm Địa quyển đọc ra thành đồng tiền.
             ⚠️ Nét mặt cắt phải toả ra từ MỘT đỉnh. Bản đầu là hai nét gãy song song
                và render ra đọc thành chữ số "17" nằm trong hòn đá — mắt gom nét
                thành ký tự trước khi gom thành hình khối. */
      body: '<path d="M14 53 6 38l9-15 14-8 18 6 12 15-7 17Z"/>',
      line: '<path d="M29 22 20 40M29 22 45 31M29 22 32 47"/>',
      lite: '<path d="M22 30 33 25l4 3-12 5Z"/>' + dust(50, 40, 1.3, 15, 44, 1.2)
    },

    /* ══ Từ đây trở xuống là icon ĐANG ĐƯỢC DÙNG ═══════════════════════ */

    /* ── Thiên thạch tím: hình neo của cả bộ, dựng theo đúng `img/tt.png`
          (khối đá lệch cạnh, hố lõm sẫm, một sparkle lớn giữa mặt). */
    meteor: {
      body: '<path d="M29 6 46 9 58 22 55 41 43 56 25 58 10 47 6 29 15 12Z"/>' +
            '<circle class="f-dk" cx="20" cy="25" r="4.4"/>' +
            '<circle class="f-dk" cx="41" cy="37" r="5.4"/>' +
            '<circle class="f-dk" cx="45" cy="18" r="3.2"/>',
      line: '<path d="M15 12 24 22M55 41 44 44"/>',
      lite: spark(30, 30, 13) + spark(48, 47, 5) + spark(15, 40, 4) +
            dust(34, 14, 1.2, 52, 30, 1.1, 26, 45, 1.2, 13, 33, 1)
    },

    /* ── 6 thẻ HUD của Trung Tâm Điều Hướng ─────────────────────────── */

    target: { /* 🎯 Trung Tâm Nhiệm Vụ */
      body: '<circle cx="32" cy="32" r="25"/>' +
            '<circle class="f-w" cx="32" cy="32" r="15.5"/>' +
            '<circle class="f-mag" cx="32" cy="32" r="6.5"/>',
      lite: '<path d="M14 20a22 22 0 0 1 16-11 26 26 0 0 0-14 15Z"/>' + spark(50, 13, 6)
    },

    /* ⚠️ ĐÃ VẼ LẠI: bản đầu là một khối đối xứng hoàn hảo với một nét dọc giữa,
          và render ra thì nó đọc là CON BƯỚM, không phải bộ não. Hai thứ chữa được
          chuyện đó, cả hai đều phải có: ① khối LỆCH (thuỳ trước phình hơn thuỳ sau,
          có cuống não thò xuống phải) nên không còn trục đối xứng để mắt bắt;
          ② nếp gấp là ĐƯỜNG CUỘN chạy ngang, không phải hai cung phản chiếu nhau.
          Ở 24px nét gấp mảnh sẽ nhoè thành một mảng — chấp nhận được, vì lúc đó
          hình khối lệch vẫn còn đọc ra; hai cánh bướm thì không. */
    brain: { /* 🧠 Trạm Tri Thức */
      body: '<path d="M20 53C13 53 8 47 9 40 5 37 5 29 9 26 8 19 14 12 21 13 24 8 33 7 38 11 45 10 51 15 51 22 56 25 56 33 52 37 53 45 47 51 40 50L40 53Z"/>',
      line: '<path d="M22 22c6 2 8 7 4 11-3 3-1 7 3 8M35 17c5 1 8 5 7 10M41 32c4 2 5 6 3 9M16 33c4 0 6 2 7 5"/>',
      lite: '<path d="M22 18c3-4 8-6 13-6-6 2-10 5-11 9Z"/>' + spark(52, 9, 5) + dust(30, 45, 1.2)
    },

    gamepad: { /* 🎮 Khu Huấn Luyện */
      body: '<path d="M21 21h22c9 0 15 7 15 15s-6 12-12 10l-7-4H25l-7 4c-6 2-12-1-12-10s6-15 15-15Z"/>' +
            '<circle class="f-cy" cx="41" cy="31" r="3.6"/>' +
            '<circle class="f-lime" cx="49" cy="36" r="3.6"/>',
      line: '<path d="M16 33h11M21.5 27.5v11"/>',
      lite: '<path d="M14 26a14 14 0 0 1 9-3 16 16 0 0 0-6 6Z"/>' + spark(33, 12, 5)
    },

    /* ⚠️ ĐÃ VẼ LẠI: bản đầu là một hình bầu dục có ĐĨA TRẮNG giữa, và render ra thì
          nó đọc là CON MẮT (đúng khuôn mống mắt + con ngươi). Chữa bằng cách bỏ hẳn
          đĩa trắng ở tâm và làm hai CÁNH XOẮN rời nhau — hai khối lệch tâm thì không
          còn bố cục đồng tâm nào để mắt đọc thành con ngươi nữa. Tâm là một sparkle
          của lớp ④ chứ không phải một hình đặc. */
    galaxy: { /* 🌌 Bản Đồ Thiên Hà */
      /* ⚠️ CÁNH PHẢI DÀY: bản mảnh hơn đọc được ở 56px nhưng ở 26px hai cánh tan
            thành một nét cong, ra hình số 6. Dày lên thì khe giữa hai cánh hẹp lại
            và sparkle ở tâm lấp đúng chỗ đó — bố cục vẫn là hai cánh lệch tâm, nên
            không quay về lỗi "con mắt" của bản đồng tâm. */
      body: '<path d="M32 26c-10-7-23-4-26 6-3 9 5 17 15 16-8-3-11-9-8-15 3-7 12-9 19-3Z"/>' +
            '<path d="M32 38c10 7 23 4 26-6 3-9-5-17-15-16 8 3 11 9 8 15-3 7-12 9-19 3Z"/>',
      line: '',
      lite: spark(32, 32, 9) + spark(53, 11, 5) + spark(11, 53, 4) +
            dust(20, 22, 1.3, 45, 43, 1.3, 48, 24, 1.1, 17, 41, 1.1)
    },

    book: { /* 📖 Sổ Tay Thuật Ngữ */
      body: '<path d="M32 17C26 12 16 11 8 13v35c8-2 18-1 24 4Z"/>' +
            '<path d="M32 17c6-5 16-6 24-4v35c-8-2-18-1-24 4Z"/>',
      line: '<path d="M32 17v35M14 22c4-1 9 0 12 2M14 31c4-1 9 0 12 2M50 22c-4-1-9 0-12 2M50 31c-4-1-9 0-12 2"/>',
      lite: spark(32, 8, 5)
    },

    flask: { /* 🔬 Phòng Nghiên Cứu */
      body: '<path d="M24 7h16v15l14 26c2 4-1 8-6 8H16c-5 0-8-4-6-8l14-26Z"/>',
      line: '<path d="M24 7h16M17 34h30"/>',
      lite: '<circle cx="25" cy="45" r="3.4"/><circle cx="36" cy="50" r="2.4"/><circle cx="30" cy="41" r="1.8"/>' +
            spark(48, 12, 5)
    },

    /* ── Ba ô Bảng Phi Hành Gia + Kho Mẫu Vật ───────────────────────── */

    trophy: { /* 🏆 Thành tích */
      body: '<path d="M18 9h28v17c0 10-6 17-14 17s-14-7-14-17Z"/>' +
            '<path d="M18 13h-7c-4 0-4 10 1 13l6 2Z"/>' +
            '<path d="M46 13h7c4 0 4 10-1 13l-6 2Z"/>' +
            '<path d="M27 43h10v8h-10Z"/>' +
            '<path d="M19 51h26c2 0 3 2 3 4H16c0-2 1-4 3-4Z"/>',
      line: '<path d="M26 16h12"/>',
      lite: '<path d="M23 13a14 14 0 0 1 5-3 18 18 0 0 0-3 5Z"/>' + spark(50, 8, 5)
    },

    astronaut: { /* 👨‍🚀 Hồ sơ Phi Hành Gia — MŨ, không phải người: ở 28px một hình
                    người cả thân chỉ còn vài pixel mỗi chi, đọc không ra gì. */
      body: '<circle cx="32" cy="32" r="25"/>' +
            '<path class="f-cy" d="M18 27c4-7 24-7 28 0 2 8-4 15-14 15s-16-7-14-15Z"/>' +
            '<path d="M52 26h4c2 0 3 2 3 5s-1 5-3 5h-4Z"/>',
      lite: '<path d="M22 28c3-4 8-5 12-5-5 2-8 5-9 9Z"/>' + spark(14, 12, 6)
    },

    crate: { /* 📦 Kho Mẫu Vật */
      body: '<path d="M8 21 32 10l24 11v23L32 55 8 44Z"/>',
      line: '<path d="M8 21l24 11 24-11M32 32v23"/>',
      lite: '<path d="M12 21 32 12l7 3-20 9Z"/>' + spark(50, 13, 5)
    },

    /* ── Dùng nhiều chỗ ──────────────────────────────────────────────── */

    rocket: { /* 🚀 */
      body: '<path class="f-mag" d="M26 44c1 8 6 14 6 14s5-6 6-14Z"/>' +
            '<path d="M21 33 10 44l3 7 10-6Z"/>' +
            '<path d="M43 33 54 44l-3 7-10-6Z"/>' +
            '<path d="M32 5c8 8 12 20 12 32l-4 10H24l-4-10c0-12 4-24 12-32Z"/>' +
            '<circle class="f-cy" cx="32" cy="25" r="6.5"/>',
      lite: '<path d="M28 12a30 30 0 0 0-4 14 34 34 0 0 1 6-16Z"/>' + spark(50, 12, 5)
    },

    /* ⚠️ VÀNH ĐÃ ĐỔI: bản đầu để vành màu MAGENTA và dày, render ra thì nó đọc là
          VÀNH MŨ chứ không phải vành Sao Thổ — vì màu hồng nằm dưới một quả cầu tím
          thì mắt tách nó thành một vật thể KHÁC, không phải cùng một hành tinh. Nay
          vành cùng họ tím (`f-lt`, sáng hơn thân) và dẹt hơn, nên nó đọc là "cái
          vành của chính quả cầu đó". */
    planet: { /* 🪐 */
      body: '<ellipse class="f-lt" cx="32" cy="35" rx="28" ry="6.5" transform="rotate(-16 32 35)"/>' +
            '<circle cx="31" cy="27" r="17"/>',
      line: '<path d="M18 21c8 4 18 4 26-1M21 33c6 2 13 1 19-2"/>',
      lite: '<path d="M21 19a17 17 0 0 1 10-6 20 20 0 0 0-7 8Z"/>' + spark(53, 11, 5) + dust(38, 15, 1.2)
    },



    /* ⚠️ NÉT DỌC GIỮA ĐÃ BỎ: nó chạy hết chiều cao khiên nên render ra trông như
          cái khiên bị GẤP LÀM HAI. Thay bằng một sparkle giữa mặt khiên — cùng thành
          ngữ với thiên thạch tím, và nó nói "đang bảo vệ" rõ hơn một đường kẻ. */
    shield: { /* 🛡️ */
      body: '<path d="M32 6 55 14v18c0 14-11 23-23 26C20 55 9 46 9 32V14Z"/>',
      lite: spark(32, 30, 11) + '<path d="M15 17 30 12v6L15 23Z"/>' + dust(43, 43, 1.3, 21, 42, 1.1)
    },

    bolt: { /* ⚡ */
      body: '<path d="M37 5 13 35h15l-3 24 24-32H33Z"/>',
      lite: '<path d="M33 10 20 27h5Z"/>' + spark(50, 12, 5)
    },

    star: { /* ⭐ */
      body: '<path d="M32 6 40 23 58 26 45 39 48 58 32 49 16 58 19 39 6 26 24 23Z"/>',
      lite: '<path d="M32 12 27 24l-8 1Z"/>' + spark(52, 46, 4)
    },

    spark: { /* ✨ — sparkle đứng một mình, cỡ lớn */
      body: '<path d="' + sp(30, 30, 25) + '"/>' + '<path d="' + sp(52, 50, 10) + '"/>',
      lite: '<path d="M30 12c1 8 4 12 10 14-8 1-12 4-14 10-1-8-4-12-10-14 8-1 12-4 14-10Z"/>'
    },


    comet: { /* ☄️ — Đường Đua Sao Chổi (ARCADE-03).
                ⚠️ ĐỪNG dùng `meteor` cho chỗ nào nói về sao chổi: `meteor` là hình
                   của ĐỒNG TIỀN (Thiên thạch tím, `img/tt.png`), đặt nó cạnh badge
                   phí là trẻ đọc thành "trò này trả thưởng bao nhiêu". */
      /* ⚠️⚠️ ĐUÔI LÀ BA VỆT RỜI, KHÔNG PHẢI MỘT KHỐI LIỀN VỚI ĐẦU. Đã thử ba bản và
            render cả ba: đuôi tam giác thót → ra CÁI THÌA · đuôi chia bậc → ra CHÌA
            KHOÁ · đuôi loe rộng liền đầu → ra QUẢ BÓNG BAY BUỘC DÂY (một khối nón
            dính vào một quả cầu thì mắt đọc thành cái phễu, bất kể tỉ lệ).
            Ba vệt RỜI thì không còn khối nào dính vào đầu để đọc nhầm, và ba vạch
            song song ngắn dần chính là thành ngữ ai cũng đọc ra là "đang bay". */
      /* ⚠️⚠️ MỘT HÌNH LIỀN (giọt lệ), KHÔNG PHẢI ĐẦU RỜI + ĐUÔI RỜI. Đây là RÀNG BUỘC
            HÌNH HỌC CỦA CẢ BỘ, đã trả giá bằng 4 lần vẽ lại và render lại:
            rìa trắng vẽ ra ngoài đường bao 4,5 đơn vị mỗi phía, nên **hai hình cách
            nhau dưới ~9 đơn vị bị HÀN thành một khối** — và cái khối hàn đó đọc ra
            thành đồ vật khác. Đo được: 3 vệt thẳng hàng → CÂY GẬY PHÉP · 3 vệt lệch
            trục cách nhau 10 → CHÙM XÚC XÍCH · đầu + một nón cách 11 → CÁI MICRO.
            Gộp đầu và đuôi vào MỘT đường bao thì không còn khe nào để hàn, và bóng
            của nó là thành ngữ sao chổi ai cũng đọc ra ngay ở 24px.
         ⇒ Vẽ icon nhiều mảnh thì đo khe MÉP-TỚI-MÉP trước, đừng đo khoảng cách tâm;
           dưới ~9 thì gộp thành một đường bao, đừng cố nhích cho xa nhau. */
      body: '<path d="M52.4 28.6A12 12 0 1 0 35.6 11.4L5 58Z"/>',
      lite: spark(44, 20, 7.5) + dust(24, 41, 1.4, 15, 50, 1.2)
    },

    maze: { /* 🌀 — Mê Cung Thiên Hà (ARCADE-05) */
      body: '<path d="M32 6c14 0 25 11 25 25 0 10-8 18-18 18-8 0-14-6-14-13 0-6 4-10 10-10 4 0 7 3 7 7 0 3-2 5-5 5 6 0 10-4 10-10 0-7-6-13-14-13-10 0-18 8-18 19 0 4 1 8 3 11C10 49 7 41 7 31 7 17 18 6 32 6Z"/>',
      lite: spark(52, 12, 5) + dust(14, 46, 1.3)
    },

    /* ── Nhóm huy hiệu (`js/badges.js`) ─────────────────────────────── */

    books: { /* 📚 nhóm Học tập */
      body: '<rect x="9" y="17" width="12" height="39" rx="3"/>' +
            '<rect x="23" y="24" width="12" height="32" rx="3"/>' +
            '<path d="M40 21 55 25 47 56 32 52Z"/>',
      line: '<path d="M9 26h12M23 32h12M42 28l12 3"/>',
      lite: spark(50, 11, 5)
    },

    grad: { /* 🎓 */
      body: '<path d="M32 9 60 22 32 35 4 22Z"/>' +
            '<path d="M14 27v13c0 5 8 9 18 9s18-4 18-9V27L32 36Z"/>',
      line: '<path d="M53 25v16"/>',
      lite: '<path d="M32 13 48 21 32 28 16 21Z"/>' + spark(53, 45, 4.5)
    },

    bulb: { /* 💡 */
      body: '<path d="M32 5c10 0 18 8 18 18 0 7-4 12-7 17H21c-3-5-7-10-7-17C14 13 22 5 32 5Z"/>' +
            '<rect x="23" y="42" width="18" height="13" rx="3.5"/>',
      line: '<path d="M25 46h14M25 51h14M32 22v18"/>',
      lite: '<path d="M23 18a12 12 0 0 1 8-8c-4 3-6 6-6 10Z"/>' + spark(51, 10, 5)
    },

    medal: { /* 🏅 */
      body: '<path d="M17 5 27 27H15L7 8Z"/>' +
            '<path d="M47 5 37 27h12l8-19Z"/>' +
            '<circle cx="32" cy="41" r="17"/>',
      lite: '<path d="M32 30 35.5 37.5 43 39l-5.5 5.5L39 53l-7-4-7 4 1.5-8.5L21 39l7.5-1.5Z"/>'
    },

    crown: { /* 👑 */
      body: '<path d="M6 47 10 17l11 11 11-17 11 17 11-11 4 30Z"/>',
      line: '<path d="M12 40h40"/>',
      lite: spark(32, 22, 6) + dust(19, 33, 1.4, 45, 33, 1.4)
    },

    ribbon: { /* 🎖️ — hoa cài, KHÁC `medal` (đĩa tròn có dải treo trên). Hai huy hiệu
                 khác nhau thì hình phải khác nhau, không thì chúng nói cùng một thứ. */
      body: '<path d="M24 33 13 58l10-4 5 8 8-25Z"/>' +
            '<path d="M40 33 51 58l-10-4-5 8-8-25Z"/>' +
            '<circle cx="32" cy="22" r="16"/>',
      lite: spark(32, 21, 9) + dust(46, 47, 1.2)
    },

    sprout: { /* 🌱 */
      body: '<path d="M29 57h6V31h-6Z"/>' +
            '<path d="M29 33c-11 0-19-7-19-16 11-2 19 5 19 16Z"/>' +
            '<path d="M35 33c0-12 9-19 20-17-1 10-9 17-20 17Z"/>',
      line: '<path d="M17 21c5 3 8 7 10 12M47 20c-5 4-8 8-10 13"/>',
      lite: spark(52, 44, 4.5) + dust(14, 44, 1.2)
    },

    /* ⚠️ ĐÃ VẼ LẠI: bản đầu là ba hình thoi chồng nhau, render ra đọc là VIÊN KIM
          CƯƠNG có dấu cộng. Nay dựng theo bố cục vệ tinh THẬT và nằm ngang: hai tấm
          pin hai bên + thân giữa + một chảo ăng-ten chìa lên. Bố cục ngang đọc được
          ở cỡ nhỏ vì ba khối tách nhau rõ, không chồng lên nhau. */
    sat: { /* 🛰️ */
      body: '<rect class="f-cy" x="4" y="22" width="15" height="20" rx="2.5"/>' +
            '<rect class="f-cy" x="45" y="22" width="15" height="20" rx="2.5"/>' +
            '<rect x="19" y="24" width="26" height="16" rx="4"/>' +
            '<ellipse cx="39" cy="12" rx="9" ry="5" transform="rotate(-26 39 12)"/>',
      line: '<path d="M11.5 22v20M52.5 22v20M4 32h15M45 32h15M25 32h14M34 24l3-7"/>',
      lite: '<path d="M22 27h7v3h-7Z"/>' + spark(53, 48, 4.5) + dust(9, 51, 1.2)
    },

    /* ⚠️ Vach chia PHAI dai ngan xen ke va toa ra tu MOT canh. Ke deu tap tap thi
          o co nho no doc ra thanh cai thang; xen ke moi ra cai thuoc. Cung ho voi
          bai hoc `rock` (hai net song song doc thanh chu so "17"). */
    ruler: { /* 📏 Tram Doi Chieu (ARCADE-10) — chuong trinh Kiem chung du lieu */
      body: '<path d="M56 19 45 8 8 45l11 11Z"/>',
      line: '<path d="M38.8 14.2 44.5 19.9M32.7 20.3 36.2 23.8M26.5 26.5 32.2 32.2' +
            'M20.3 32.7 23.8 36.2M14.2 38.8 19.9 44.5"/>',
      lite: '<path d="M45 8 34 19l3 3L48 11Z"/>' + spark(14, 15, 5) + dust(52, 47, 1.3)
    },

    tag: { /* 🏷️ Tram Phan Loai (ARCADE-12) — chuong trinh Day may hoc.
       ⚠️ VE CAI NHAN chu khong ve mot con chip: chan chip la nhung net manh dat
          sat nhau, ma khe mep-toi-mep duoi ~2,2 don vi la hai net HAN thanh mot
          khoi o co 26px (bai hoc `comet` phai ve lai BON lan, va `rock` doc ra
          thanh chu so "17"). Cai nhan la MOT khoi lien — khong co gi de han.
       ⚠️ LO TRON PHAI DU TO. Tam (46,17) ban kinh 5, cach canh tren va canh phai
          deu 11 don vi, nen o co nho no van la mot cai lo chu khong bi bit lai.
          Vong tron ve NGUOC CHIEU voi ngu giac de `fill-rule` mac dinh (nonzero)
          khoet thanh lo that. */
      body: '<path d="M34 6 H56 V28 L28 56 6 34 Z' +
            'M46 12 a5 5 0 1 0 0 10 5 5 0 1 0 0-10 Z"/>',
      lite: '<path d="M34 6 H45 L23 28 19 24Z"/>' + spark(50, 48, 4.6) + dust(13, 41, 1.2)
    }
  };

  var n = 0; /* hậu tố id gradient — xem ghi chú đầu file về chuyện id trùng */

  /* Trả về chuỗi SVG sticker; cls: class phụ (vd "sic--cyan"). */
  function sic(name, cls) {
    var d = SIC[name];
    if (!d) return '';
    var id = 'sicg' + (++n);
    return '<svg class="sic ' + (cls || '') + '" viewBox="-8 -8 80 80" aria-hidden="true">' +
      '<defs><linearGradient id="' + id + '" x1="0.15" y1="0" x2="0.7" y2="1">' +
      '<stop offset="0" stop-color="var(--sic-a)"/>' +
      '<stop offset=".52" stop-color="var(--sic-b)"/>' +
      '<stop offset="1" stop-color="var(--sic-c)"/></linearGradient></defs>' +
      '<g class="sic-edge">' + d.body + '</g>' +
      '<g class="sic-rim">' + d.body + '</g>' +
      '<g class="sic-ink" fill="url(#' + id + ')">' + d.body + '</g>' +
      (d.line ? '<g class="sic-line">' + d.line + '</g>' : '') +
      (d.lite ? '<g class="sic-lite">' + d.lite + '</g>' : '') +
      '</svg>';
  }

  /* Vẽ mọi phần tử khai `data-sic="<tên>"` (kèm `data-sic-cls` nếu cần bảng màu).
     Nhờ nó, markup TĨNH chỉ cần một thuộc tính — không trang nào phải tự viết một
     vòng lặp, và cũng không phải nhét chuỗi SVG vào HTML (mất khả năng grep tên
     icon, và mỗi lần sửa hình là phải sửa lại từng trang).
     ⚠️ Trang nào sinh markup BẰNG JS thì gọi `sic()` thẳng trong chuỗi, đừng đợi
        `paint()` — nó chỉ chạy một lần lúc tải xong. Muốn quét lại một khối vừa
        dựng thì gọi `AstroQ.sicPaint(el)`. */
  function paint(root) {
    var list = (root || document).querySelectorAll('[data-sic]'), i, el;
    for (i = 0; i < list.length; i++) {
      el = list[i];
      el.innerHTML = sic(el.getAttribute('data-sic'), el.getAttribute('data-sic-cls') || '');
    }
  }
  if (global.document) {
    if (global.document.readyState === 'loading') {
      global.document.addEventListener('DOMContentLoaded', function () { paint(); });
    } else { paint(); }
  }

  global.AstroQSticker = SIC;
  if (!global.sic) global.sic = sic;
  (global.AstroQ = global.AstroQ || {}).sicPaint = paint;
  (global.AstroQ = global.AstroQ || {}).SIC = SIC;
  global.AstroQ.sic = sic;
})(window);
