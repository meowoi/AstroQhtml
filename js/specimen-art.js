/* ============================================================
   specimen-art.js — TRANH VẼ 21 MẪU VẬT, mỗi mẫu một SVG riêng.

   Dùng:
     <script src="js/specimen-art.js"></script>   (sau js/specimens.js)
     AstroQSpecimenArt.svg("mars-red-ice")   → chuỗi "<svg …>…</svg>"

   ────────── VÌ SAO CÓ FILE NÀY (21/08/2026) ──────────
   Trước đó `js/specimens.js` khai mỗi mẫu vật bằng MỘT KÝ TỰ EMOJI (`ic`), và
   trang chỉ việc in ký tự đó ra. Chủ dự án chơi trên Mac rồi chơi trên PC Windows
   và gửi hai ảnh chụp cùng một trang: *"vì sao có sự khác biệt giữa hình ảnh các
   mẫu vật khi chơi trên mac và khi chơi trên máy PC win?"*

   ⚠️⚠️ EMOJI KHÔNG PHẢI MỘT HÌNH — NÓ LÀ MỘT KÝ TỰ, VÀ **MỖI HỆ ĐIỀU HÀNH VẼ NÓ
      BẰNG PHÔNG CHỮ CỦA RIÊNG MÌNH.** macOS/iOS dùng *Apple Color Emoji* (khối,
      có khối sáng tối, trông như tượng nhỏ); Windows dùng *Segoe UI Emoji* (phẳng,
      nét vector, ít khối); Android dùng *Noto Color Emoji*. Cùng một dòng mã, ba
      máy ra ba bức tranh khác nhau — và **không có tuỳ chọn CSS nào chữa được**,
      vì thứ khác nhau là PHÔNG, không phải kiểu chữ.

   ⚠️⚠️ KHÔNG THỂ "LẤY BỘ CỦA MAC" DÙNG CHO WINDOWS. *Apple Color Emoji* là phông
      độc quyền của Apple, giấy phép **không cho nhúng/phát hành lại**; tự nhúng là
      vi phạm bản quyền, và cũng không hợp với một web tĩnh (phông emoji nặng >30 MB).
      Đường đúng — và cũng là đường chủ dự án yêu cầu ở chính câu sau (*"các mẫu vật
      yêu cầu phải vẽ chi tiết, sát thực tế nhất có thể"*) — là **TỰ VẼ**. SVG do
      mình vẽ thì mọi máy hiện y hệt nhau, và vẽ được đúng thứ mà mẫu vật đó LÀ.

   ⚠️⚠️ EMOJI CÒN NÓI SAI NỘI DUNG, KHÔNG CHỈ KHÁC KIỂU VẼ. Chủ dự án bắt đúng một
      ví dụ: *"Ví dụ Tinh thể băng đỏ sao lại màu xanh?"* — mẫu `mars-red-ice` dùng
      💎, tức viên kim cương XANH, trong khi nó là băng H₂O nhuốm bụi oxit sắt ở
      vùng cực Sao Hoả, tức phải ĐỎ HỒNG. Không có emoji nào tên là "băng đỏ".
      Danh sách nói sai tương tự (đã sửa hết trong file này):
        🌑 → đá thuỷ tinh núi lửa   🪨 → tinh thể thạch anh   🏜️ → cát sa mạc
        🌕 → bụi mịn Mặt Trăng      ⚪ → phiến đá Sao Thuỷ    🟠 → bazan Sao Kim
        ☄️ → thiên thạch sắt        🪐 → hạt băng vành đai    🔵 → sương metan
        🐛 → bọ gấu nước (Tardigrada có TÁM chân, không phải sâu bướm)
      ⇒ Emoji là thứ GẦN GIỐNG nhất tìm được trong một bộ ký tự có sẵn. Với một
        trang dạy về vũ trụ thì "gần giống" là nói sai.

   ────────── CÁCH VẼ (đọc trước khi thêm mẫu vật thứ 22) ──────────
   ⚠️ KHUNG `0 0 64 64`, và vẽ TRONG khoảng 4..60. Không có lớp viền vẽ ra ngoài
      như `js/sticker-icons.js` (bộ đó nới viewBox ra `-8 -8 80 80` để chừa chỗ cho
      ba nét vẽ ngoài đường bao); ở đây hình tự thân là một khối có sáng tối, nên
      chạm mép 64 là bị cắt phẳng thật.

   ⚠️ CỠ ĐO ĐƯỢC, ĐỪNG ĐOÁN — hình này hiện ở NĂM cỡ khác nhau:
        `.slot .sp` 19px · `.hk-sp` 20px · `.pod .sp` **46px** ·
        `.scope .sp` 96px · `.scope.zoom .sp` **170px**
      ⇒ **ĐƯỜNG BAO phải đọc được ở 19px** (mỗi mẫu một dáng khác hẳn nhau: giọt ·
        trụ · lá · lông · con vật · khối đá góc cạnh · lăng trụ sáu phương · cụm
        tinh thể · đám mây) **và CHI TIẾT TRONG phải chịu được 170px** (thớ, mặt
        cắt, bọt khí, gân lá, vân Widmanstätten). Một hình chỉ đạt một đầu là hỏng
        một nửa số chỗ nó xuất hiện.
      ⚠️ Chi tiết nhỏ hơn ~1 đơn vị thì ở 19px nó biến mất (1 đơn vị ≈ 0,3px) —
        chấp nhận được cho THỚ, nhưng đường bao và khối màu chính thì không.

   ⚠️ NỀN LÀ KHOANG TỐI (`.pod .glass` navy + hào quang tím). Hình TỐI (obsidian,
      thiên thạch sắt, bazan Sao Kim) **phải có nét sáng ở rìa** — không thì nó
      chìm hẳn vào nền và trẻ chỉ thấy một vệt đen. Đã kiểm bằng ảnh chụp thật.

   ⚠️ CỠ THEO `font-size` CỦA Ô CHỨA (`.spart{width:1em;height:1em}` ở
      `css/common.css`), KHÔNG gán cứng px. Nhờ vậy năm cỡ trên **không phải sửa
      một dòng CSS nào**, kể cả hiệu ứng phóng to ở màn soi — nó là
      `transition:font-size` sẵn có, và `1em` đi theo.

   ⚠️ ID GRADIENT PHẢI DUY NHẤT MỖI LẦN GỌI — dùng `{n}` trong chuỗi, hàm `svg()`
      thay bằng số đếm. Trang Kho Mẫu Vật vẽ 21 khoang cùng lúc và màn soi vẽ lại
      thêm một bản nữa; id trùng thì bản sau "ăn" gradient của bản trước và cả lưới
      đổi màu theo — cùng lý do đã ghi ở đầu `js/sticker-icons.js`.

   ⚠️ KHÔNG `style="…"` TRONG SVG (quy tắc 2 mục 1 của CLAUDE.md). Ở đây dùng
      THUỘC TÍNH trình bày (`fill=`, `stroke=`, `opacity=`) — chúng là thuộc tính
      SVG, không phải CSS inline, và `js/sticker-icons.js` cũng làm đúng vậy.

   ⚠️ KHÔNG CÓ FILTER (`feGaussianBlur`…). Chỗ cần "mềm" thì dùng gradient có chặng
      trong suốt. Lý do: 21 khoang × filter là 21 lần rasterize thêm mỗi khung hình,
      mà `.pod .sp` đang có `animation:podFloat` chạy liên tục — đo trên máy yếu thì
      đó là cả một trang tụt khung hình, đổi lấy một chỗ mờ.
   ============================================================ */
(function (global) {
  "use strict";

  /* ── Bút vẽ dùng lại ──────────────────────────────────────────────
     Ba thứ lặp ở gần hết 21 hình. Viết một lần ở đây thay vì chép chuỗi:
     sửa cỡ đốm sáng là 21 hình đổi theo. */

  /** Đốm sáng bốn cánh (lấp lánh trên băng, tinh thể, kim cương). */
  function glint(x, y, r, o) {
    return '<path d="M' + x + ' ' + (y - r) + 'Q' + x + ' ' + y + ' ' + (x + r) + ' ' + y +
           'Q' + x + ' ' + y + ' ' + x + ' ' + (y + r) +
           'Q' + x + ' ' + y + ' ' + (x - r) + ' ' + y +
           'Q' + x + ' ' + y + ' ' + x + ' ' + (y - r) + 'Z" fill="#fff" opacity="' + (o || 0.9) + '"/>';
  }

  /** Chuỗi đốm tròn: dots("#fff", .5, x,y,r, x,y,r, …) — hạt, bọt khí, thớ đá. */
  function dots(fill, op) {
    var s = '<g fill="' + fill + '" opacity="' + op + '">', i;
    for (i = 2; i < arguments.length; i += 3) {
      s += '<circle cx="' + arguments[i] + '" cy="' + arguments[i + 1] + '" r="' + arguments[i + 2] + '"/>';
    }
    return s + '</g>';
  }

  /* ⚠️ MỖI MỤC = { defs, body }. `defs` chỉ chứa gradient (id có `{n}`), `body` là
     hình. Tách ra vì `<defs>` phải nằm trước và gộp một lần cho cả hình. */
  var ART = {

    /* ═══════════ 🌊 THUỶ QUYỂN ═══════════ */

    /* Giọt nước biển sâu: xanh lục lam đậm dần xuống đáy (nước sâu hút hết đỏ),
       muối khoáng còn LƠ LỬNG bên trong — đúng câu Comet nói ở màn soi. */
    "ancient-seawater": {
      defs:
        '<radialGradient id="sw{n}" cx=".36" cy=".26" r=".85">' +
        '<stop offset="0" stop-color="#a8f0ff"/><stop offset=".38" stop-color="#3aa6d8"/>' +
        '<stop offset=".78" stop-color="#115a92"/><stop offset="1" stop-color="#062f55"/></radialGradient>' +
        '<linearGradient id="swg{n}" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0" stop-color="#fff" stop-opacity=".85"/>' +
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
      body:
        '<path d="M32 6C38 18 51 30 51 40A19 19 0 0 1 13 40C13 30 26 18 32 6Z" fill="url(#sw{n})"/>' +
        /* Rìa sáng: mặt cong của giọt nước bắt sáng vòng quanh */
        '<path d="M32 6C38 18 51 30 51 40A19 19 0 0 1 13 40C13 30 26 18 32 6Z" fill="none" ' +
        'stroke="#bdf0ff" stroke-opacity=".5" stroke-width="1.3"/>' +
        /* Vệt sáng dọc (gloss) — thứ làm một hình phẳng đọc ra "khối trong suốt" */
        '<path d="M25 15C21 22 18 28 18 34c0 4 1 7 3 9-5-3-7-8-7-13 0-6 4-12 11-15Z" fill="url(#swg{n})"/>' +
        /* Ánh khúc xạ đáy giọt (caustic) */
        '<path d="M22 46a13 13 0 0 0 20 0" fill="none" stroke="#9fe8ff" stroke-opacity=".55" stroke-width="1.6"/>' +
        /* Muối khoáng lơ lửng: tinh thể vuông nhỏ, KHÔNG phải bọt khí tròn */
        '<g fill="#e9fbff" opacity=".92">' +
        '<rect x="27" y="30" width="3.4" height="3.4" rx=".6" transform="rotate(24 28.7 31.7)"/>' +
        '<rect x="37" y="37" width="2.6" height="2.6" rx=".5" transform="rotate(-18 38.3 38.3)"/>' +
        '<rect x="23" y="40" width="2.2" height="2.2" rx=".4" transform="rotate(35 24.1 41.1)"/>' +
        '<rect x="33" y="24" width="2" height="2" rx=".4" transform="rotate(12 34 25)"/></g>' +
        dots("#cfefff", ".55", 30, 44, 1, 40, 30, 1, 25, 34, .9)
    },

    /* San hô cứng: bộ xương đá vôi PHÂN NHÁNH, ngọn nhạt (phần đang mọc) và có
       lỗ corallite trên thân — hai dấu hiệu để không đọc ra là một cành cây. */
    "coral-fragment": {
      defs:
        '<linearGradient id="co{n}" x1=".2" y1="1" x2=".8" y2="0">' +
        '<stop offset="0" stop-color="#a63c56"/><stop offset=".45" stop-color="#f4826c"/>' +
        '<stop offset="1" stop-color="#ffd7c0"/></linearGradient>',
      body:
        /* SAU NGON TOA RONG, KHONG PHAI HAI. Ban dau chi chia hai nhanh nen o 46px
           no doc ra thanh MOT CHU Y (hoac mot cai na cao su) - mat gom hai net cheo
           thanh mot ky tu truoc khi gom thanh mot khoi san ho. Cung ho voi bai hoc
           `rock` (hai net song song doc thanh chu so "17") o `js/sticker-icons.js`. */
        '<g fill="none" stroke="url(#co{n})" stroke-linecap="round">' +
        '<path d="M32 58V45" stroke-width="9.5"/>' +
        '<path d="M32 46 19 34M32 46v-15M32 46l13-12" stroke-width="7"/>' +
        '<path d="M19 34l-7-11M19 34l3-13M32 31l-4-13M32 31l6-12M45 34l7-11M45 34l-3-12" stroke-width="5"/></g>' +
        /* Ngon nhat - voi moi, chua co tao cong sinh nen trang hon han than */
        dots("#fff2e8", ".95", 12, 23, 2.8, 22, 21, 2.6, 28, 18, 2.6, 38, 19, 2.6, 52, 23, 2.8, 42, 22, 2.5) +
        /* Lo corallite: moi lo la cho mot ca the polyp tung o */
        dots("#8e2f47", ".5", 32, 52, 1.4, 32, 43, 1.3, 25, 40, 1.1, 39, 40, 1.1,
             20, 30, 1, 26, 26, 1, 44, 30, 1, 36, 26, 1) +
        /* Net sang doc than: khoi tron cua canh */
        '<g fill="none" stroke="#ffe6d6" stroke-opacity=".45" stroke-width="1.3" stroke-linecap="round">' +
        '<path d="M29 56V47M23.5 30l-2-5M40.5 27l1-4"/></g>'
    },
    /* Cột băng khoan: TRỤ có lớp theo năm. Lớp đục = tuyết mùa đông, lớp trong =
       băng nén mùa hè; bọt khí giữ không khí của chính năm đó. */
    "polar-ice-core": {
      defs:
        '<linearGradient id="ic{n}" x1="0" y1="0" x2="1" y2="0">' +
        '<stop offset="0" stop-color="#4d86ac"/><stop offset=".22" stop-color="#e6f7ff"/>' +
        '<stop offset=".6" stop-color="#a3daf2"/><stop offset="1" stop-color="#3f7398"/></linearGradient>',
      body:
        /* TRU CAO VA HEP, KHONG PHAI KHOI MAP. Ban dau rong 18 / cao 42 (ti le 1:2,3) nen o 46px
           no doc ra thanh MOT CAI LON NUOC; mot cot bang khoan len thi hinh dang
           mang nghia la DAI - do la thu noi "moi lop mot nam, doc tu tren xuong". */
        '<path d="M25 6h14v48a7 3.4 0 0 1-14 0Z" fill="url(#ic{n})"/>' +
        /* Mat cat tren: elip, thu noi "day la mot khoi TRU vua duoc khoan ra" */
        '<ellipse cx="32" cy="6" rx="7" ry="3.4" fill="#f2fcff"/>' +
        '<ellipse cx="32" cy="6" rx="7" ry="3.4" fill="none" stroke="#79b6d8" stroke-width=".9"/>' +
        '<ellipse cx="32" cy="5.5" rx="4.3" ry="1.9" fill="#c6ebfc" opacity=".85"/>' +
        /* Lop theo nam - day mong KHONG deu, vi moi nam tuyet roi mot khac */
        '<g fill="#f4fcff" opacity=".8">' +
        '<rect x="25" y="12" width="14" height="2.6"/><rect x="25" y="19" width="14" height="1.5"/>' +
        '<rect x="25" y="25" width="14" height="3"/><rect x="25" y="33" width="14" height="1.7"/>' +
        '<rect x="25" y="39" width="14" height="2.4"/><rect x="25" y="47" width="14" height="1.6"/></g>' +
        '<g stroke="#2f6c93" stroke-opacity=".55" stroke-width=".85">' +
        '<path d="M25 16h14M25 22.5h14M25 30h14M25 36.5h14M25 44h14M25 51h14"/></g>' +
        dots("#fff", ".85", 28, 16, .9, 36, 23, .8, 29, 30, .9, 36, 37, .8, 28, 44, .8, 35, 50, .7) +
        '<path d="M25 6v48a7 3.4 0 0 0 14 0V6" fill="none" stroke="#96d1ea" stroke-opacity=".7" stroke-width="1.1"/>'
    },
    /* ⚠️ ĐÂY LÀ MẪU CHỦ DỰ ÁN CHỈ RA: emoji cũ là 💎 (kim cương XANH).
       Thật: băng nước ở vùng cực Sao Hoả nhuốm BỤI OXIT SẮT → hồng đỏ, và bụi đó
       nằm KẸP TRONG băng nên phải thấy được các hạt sẫm bên trong, không phải một
       khối đỏ trơn. */
    "mars-red-ice": {
      defs:
        '<linearGradient id="mi{n}" x1=".15" y1="0" x2=".85" y2="1">' +
        '<stop offset="0" stop-color="#ffe4dd"/><stop offset=".3" stop-color="#f4a794"/>' +
        '<stop offset=".68" stop-color="#cf6a52"/><stop offset="1" stop-color="#8e3524"/></linearGradient>' +
        '<linearGradient id="mif{n}" x1="0" y1="0" x2="1" y2=".6">' +
        '<stop offset="0" stop-color="#fff" stop-opacity=".75"/>' +
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
      body:
        /* Mảnh băng vỡ: cạnh THẲNG và góc nhọn (băng vỡ theo mặt phẳng), không tròn */
        '<path d="M30 5l17 12-3 21-14 21-13-14 2-24Z" fill="url(#mi{n})"/>' +
        /* Mặt vỡ sáng — một mặt hứng sáng thì cả khối mới có chiều */
        '<path d="M30 5l17 12-13 6-15-4Z" fill="url(#mif{n})"/>' +
        /* Đường gờ giữa các mặt tinh thể */
        '<g fill="none" stroke="#ffd9cf" stroke-opacity=".55" stroke-width="1">' +
        '<path d="M19 19l15 4 10-6M34 23l-4 36M34 23l10 15"/></g>' +
        '<path d="M30 5l17 12-3 21-14 21-13-14 2-24Z" fill="none" stroke="#ffcdc0" stroke-opacity=".6" stroke-width="1.2"/>' +
        /* Bụi oxit sắt kẹt trong băng — chính thứ làm nó ĐỎ */
        dots("#7d2a17", ".62", 26, 30, 1.5, 33, 38, 1.7, 24, 41, 1.2, 37, 29, 1.1,
             30, 47, 1.4, 39, 44, 1, 22, 25, .9) +
        glint(43, 15, 4.6, .95) + glint(24, 47, 3, .7)
    },

    /* Nước mặn dưới vỏ băng Europa: một MẶT CẮT. Trên là vỏ băng trắng nứt, mang
       những vệt nâu đỏ (lineae) đúng như ảnh Galileo; dưới là đại dương mặn tối. */
    "europa-brine": {
      defs:
        '<linearGradient id="eu{n}" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".6" stop-color="#d3ecfa"/>' +
        '<stop offset="1" stop-color="#93bdd6"/></linearGradient>' +
        '<linearGradient id="eb{n}" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0" stop-color="#1a6a95"/><stop offset=".45" stop-color="#0a3a5e"/>' +
        '<stop offset="1" stop-color="#031428"/></linearGradient>',
      body:
        /* MANH VO GOC CANH, KHONG PHAI HOP BO GOC. Ban dau la mot khoi chu nhat bo
           goc va o 46px no doc ra thanh MOT CAI LY NUOC. Bang vo theo mat phang nen
           canh phai thang va goc phai nhon - dung nhu `mars-red-ice` da ghi. */
        '<path d="M9 27l15-9 21 2 10 9-4 21-19 7-19-9Z" fill="url(#eb{n})"/>' +
        /* Vo bang: nua tren cua chinh manh do, cat ngang bang mat tiep giap */
        '<path d="M9 27l15-9 21 2 10 9-3 6H10Z" fill="url(#eu{n})"/>' +
        /* Lineae - vet nut nhuom muoi/khoang, dau hieu nhan ra Europa ngay.
           CANH BAO: dam han len. O ban dau chung mo .85 tren nen trang nen o 46px
           doc ra nhu mot vet ban chu khong nhu he thong nut. */
        '<g fill="none" stroke="#a8482a" stroke-width="1.9" stroke-linecap="round">' +
        '<path d="M11 26c9-4 17 4 25 0M15 20c8 3 15-1 23 3M29 18v14"/></g>' +
        '<g fill="none" stroke="#6b2d18" stroke-width=".9" stroke-linecap="round" opacity=".75">' +
        '<path d="M12 30c8-3 16 3 23 0M22 19l3 13M40 21l3 10"/></g>' +
        /* Ranh gioi bang / nuoc - cho bang tan thanh nuoc man */
        '<path d="M10 33h42" stroke="#eafaff" stroke-width="1.4"/>' +
        /* Nuoc man: dong chay + bot, sang dan len phia mat tiep giap */
        '<g fill="none" stroke="#4fb4de" stroke-opacity=".55" stroke-width="1.4" stroke-linecap="round">' +
        '<path d="M15 40c6-3 12 3 18 0s9 1 11 2M18 48c7-3 13 2 19-1"/></g>' +
        dots("#8fdcff", ".75", 23, 44, 1.3, 33, 51, 1.1, 42, 45, 1, 28, 54, .9, 17, 51, .9) +
        '<path d="M9 27l15-9 21 2 10 9-4 21-19 7-19-9Z" fill="none" ' +
        'stroke="#8ecbe8" stroke-opacity=".6" stroke-width="1.2"/>'
    },
    /* ═══════════ 🌿 SINH QUYỂN ═══════════ */

    /* Lá cây mưa nhiệt đới: có MŨI NHỌN CHẢY NƯỚC (drip tip) ở đầu lá — đặc điểm
       của lá rừng mưa, giúp nước trút nhanh khỏi mặt lá. Gân giữa + gân phụ so le. */
    "amazon-leaf": {
      defs:
        '<linearGradient id="lf{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#9ae86a"/><stop offset=".42" stop-color="#3fae4a"/>' +
        '<stop offset="1" stop-color="#136b39"/></linearGradient>' +
        '<linearGradient id="lg{n}" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#fff" stop-opacity=".5"/>' +
        '<stop offset=".7" stop-color="#fff" stop-opacity="0"/></linearGradient>',
      body:
        '<path d="M50 7c-3 22-14 34-26 39l-3 11-2-1 3-11C13 39 14 22 50 7Z" fill="url(#lf{n})"/>' +
        /* Mặt lá bóng (lá rừng mưa có lớp sáp) */
        '<path d="M47 11C22 22 17 33 21 43c1-11 8-22 26-32Z" fill="url(#lg{n})"/>' +
        /* Gân giữa chạy suốt tới mũi nhọn */
        '<path d="M50 7C34 20 25 33 21 46" fill="none" stroke="#0e5b31" stroke-opacity=".85" stroke-width="1.5"/>' +
        /* Gân phụ SO LE hai bên, cong về phía ngọn — không kẻ đối xứng như xương cá */
        '<g fill="none" stroke="#12673a" stroke-opacity=".7" stroke-width=".9">' +
        '<path d="M44 13c-4 2-6 6-6 9M38 19c-4 2-6 5-7 9M32 27c-4 2-5 4-6 8"/>' +
        '<path d="M46 12c1 4 0 7-2 10M40 18c1 4 0 6-2 9M34 26c1 3 0 5-2 7"/></g>' +
        /* Cuống lá */
        '<path d="M19 57l2-11" fill="none" stroke="#8a6a35" stroke-width="2" stroke-linecap="round"/>' +
        '<path d="M50 7c-3 22-14 34-26 39l-3 11" fill="none" stroke="#b9f08a" stroke-opacity=".5" stroke-width="1"/>'
    },

    /* Lông chim cánh cụt: NGẮN, CỨNG, XẾP DÀY — không phải lông vũ mềm dài của
       chim bay. Đen ở ngoài, trắng ở gốc, có trục rachis rõ. */
    "penguin-feather": {
      defs:
        '<linearGradient id="pf{n}" x1=".7" y1="0" x2=".2" y2="1">' +
        '<stop offset="0" stop-color="#5a6580"/><stop offset=".45" stop-color="#1d2436"/>' +
        '<stop offset="1" stop-color="#080b14"/></linearGradient>' +
        '<linearGradient id="pw{n}" x1=".6" y1="0" x2=".1" y2="1">' +
        '<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#bcc6da"/></linearGradient>',
      body:
        /* PHIEN RONG, HAI TONG CHIA BOI TRUC RACHIS. Ban dau la mot vet manh va o
           46px no doc ra thanh MOT CAI BUT LONG - ma long chim canh cut thi NGAN,
           CUNG, XEP DAY (do chinh la thu lam no kin nuoc), nguoc han long vu mem
           dai cua chim bay. Duong bao phai rong moi noi ra duoc dieu do. */
        '<path d="M40 7c14 13 12 34 1 45L14 58Z" fill="url(#pf{n})"/>' +
        '<path d="M40 7L14 58c-2-15 3-33 12-43 4-5 9-8 14-8Z" fill="url(#pw{n})"/>' +
        /* Truc rachis - net cung chay suot, thu phan biet long voi mot cai la */
        '<path d="M41 6L13 59" fill="none" stroke="#2b3348" stroke-width="2.1" stroke-linecap="round"/>' +
        '<path d="M41 6L13 59" fill="none" stroke="#f2f5ff" stroke-opacity=".5" stroke-width=".8"/>' +
        /* Tia barb: NGAN va DAY, moc day sat nhau - chinh cai lam long kin nuoc */
        '<g fill="none" stroke="#0d1220" stroke-opacity=".5" stroke-width=".9" stroke-linecap="round">' +
        '<path d="M38 12l5 5M35 18l6 5M32 24l7 5M29 30l7 5M26 36l7 4M23 42l6 4M20 48l5 3"/></g>' +
        '<g fill="none" stroke="#8f9ab5" stroke-opacity=".55" stroke-width=".9" stroke-linecap="round">' +
        '<path d="M36 15l-6 3M33 21l-7 3M30 27l-7 3M27 33l-7 3M24 39l-6 3M21 45l-5 3"/></g>' +
        /* Goc long (calamus) - phan cam vao da, rong */
        '<path d="M14 57l-3 5" fill="none" stroke="#e6ecf8" stroke-width="1.8" stroke-linecap="round"/>'
    },
    /* ⚠️ Emoji cũ là 🐛 (SÂU BƯỚM) — sai lớp động vật. Tardigrada: thân THÙNG có
       khoanh, BỐN ĐÔI chân mập, mỗi chân có vuốt, đầu có ống miệng. Trong mờ, hổ phách. */
    "tardigrade-sample": {
      defs:
        '<radialGradient id="td{n}" cx=".35" cy=".3" r=".85">' +
        '<stop offset="0" stop-color="#ffeec4"/><stop offset=".45" stop-color="#e8b978"/>' +
        '<stop offset="1" stop-color="#a5713a"/></radialGradient>',
      body:
        /* Vòng trường kính hiển vi — nói ngay "đây là thứ chỉ thấy qua kính" */
        '<circle cx="32" cy="32" r="27" fill="#0a2233" opacity=".45"/>' +
        '<circle cx="32" cy="32" r="27" fill="none" stroke="#5fd0e8" stroke-opacity=".35" stroke-width="1"/>' +
        /* Bốn đôi chân — vẽ TRƯỚC thân để chân nằm dưới, đúng như soi từ trên */
        '<g fill="none" stroke="#c99553" stroke-width="4.6" stroke-linecap="round">' +
        '<path d="M23 41l-3 6M31 43l-1 6M39 42l2 6M46 39l4 5"/></g>' +
        '<g fill="none" stroke="#c99553" stroke-width="3.8" stroke-linecap="round" opacity=".7">' +
        '<path d="M22 25l-4-5M30 22l-1-6M38 23l2-6"/></g>' +
        /* Thân thùng có khoanh */
        '<path d="M17 32c0-8 7-12 16-12s16 4 16 12-7 12-16 12-16-4-16-12Z" fill="url(#td{n})"/>' +
        '<g fill="none" stroke="#96602c" stroke-opacity=".6" stroke-width="1.1">' +
        '<path d="M25 21.5c-2 7-2 14 0 21M32 20c-2 8-2 16 0 24M39 21c2 7 2 14 0 21"/></g>' +
        /* Đầu + ống miệng (stylet) hút dịch cây */
        '<path d="M49 26c4 1 6 4 6 6s-2 5-6 6" fill="url(#td{n})"/>' +
        '<path d="M55 32h5" fill="none" stroke="#e8b978" stroke-width="2" stroke-linecap="round"/>' +
        dots("#5c3413", ".8", 50, 29.5, 1.1, 50, 34.5, 1.1) +
        /* Vuốt ở đầu mỗi chân — dấu hiệu phân loại của Tardigrada */
        '<g fill="none" stroke="#7a4a1c" stroke-width="1" stroke-linecap="round">' +
        '<path d="M19 46l-2 3M18 47l2 3M29 48l-2 3M30 49l2 2M41 47l-2 3M42 48l2 3M50 43l-1 4M51 44l3 2"/></g>' +
        /* Khối sáng trên lưng — thân trong mờ nên bắt sáng thành một vệt */
        '<path d="M23 26c5-3 14-3 19 0-6-1-13-1-19 0Z" fill="#fff8e0" opacity=".6"/>'
    },

    /* Vi khuẩn hoá dưỡng ở miệng phun thuỷ nhiệt: hình QUE (bacillus) có roi, một
       con đang phân đôi. Vẽ trong trường kính hiển vi tối, tông lục lam. */
    "deep-sea-bacteria": {
      defs:
        '<linearGradient id="bc{n}" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#bdffe6"/><stop offset=".5" stop-color="#4fd6a8"/>' +
        '<stop offset="1" stop-color="#12856a"/></linearGradient>',
      body:
        '<circle cx="32" cy="32" r="27" fill="#04202b" opacity=".55"/>' +
        '<circle cx="32" cy="32" r="27" fill="none" stroke="#5fd0e8" stroke-opacity=".35" stroke-width="1"/>' +
        /* Roi (flagella) — nét lượn mảnh, vẽ trước để nằm dưới thân */
        '<g fill="none" stroke="#8ff0d0" stroke-opacity=".65" stroke-width=".9" stroke-linecap="round">' +
        '<path d="M17 22c-4 1-6 4-5 7s4 4 6 3M50 28c4-1 6 2 5 5s-4 4-6 3M24 47c-3 3-2 6 1 7s5-1 5-3"/></g>' +
        /* Que 1 — nằm chéo, có vách trong */
        '<rect x="16" y="17" width="20" height="9" rx="4.5" transform="rotate(18 26 21.5)" fill="url(#bc{n})"/>' +
        /* Que 2 — ĐANG PHÂN ĐÔI: eo thắt giữa, thứ nói "chúng đang sinh sôi" */
        '<rect x="30" y="27" width="22" height="9" rx="4.5" transform="rotate(-12 41 31.5)" fill="url(#bc{n})"/>' +
        '<path d="M41 26.5v10" fill="none" stroke="#0a5c48" stroke-opacity=".8" stroke-width="1.4" transform="rotate(-12 41 31.5)"/>' +
        /* Que 3 */
        '<rect x="20" y="40" width="17" height="8" rx="4" transform="rotate(9 28.5 44)" fill="url(#bc{n})"/>' +
        /* Hạt lưu huỳnh trong tế bào — vi khuẩn ở miệng phun sống bằng hoá chất,
           và các hạt sáng này là kho năng lượng của chúng */
        dots("#f0fff8", ".85", 22, 21, 1.4, 29, 23, 1.2, 36, 30, 1.3, 46, 33, 1.2, 26, 44, 1.2, 33, 45, 1) +
        '<g fill="none" stroke="#d6fff0" stroke-opacity=".5" stroke-width=".8">' +
        '<rect x="16" y="17" width="20" height="9" rx="4.5" transform="rotate(18 26 21.5)"/>' +
        '<rect x="30" y="27" width="22" height="9" rx="4.5" transform="rotate(-12 41 31.5)"/>' +
        '<rect x="20" y="40" width="17" height="8" rx="4" transform="rotate(9 28.5 44)"/></g>'
    },

    /* ═══════════ 🪨 ĐỊA QUYỂN ═══════════ */

    /* ⚠️ Emoji cũ là 🪨 (hòn đá) cho một TINH THỂ THẠCH ANH — mất hẳn thứ đáng nhìn.
       Thật: lăng trụ SÁU PHƯƠNG, đầu chóp nhọn, trong suốt, có mặt vân ngang. */
    "himalaya-crystal": {
      defs:
        '<linearGradient id="qz{n}" x1="0" y1="0" x2="1" y2=".3">' +
        '<stop offset="0" stop-color="#f4fdff"/><stop offset=".45" stop-color="#c3e6f2"/>' +
        '<stop offset="1" stop-color="#7ba9c0"/></linearGradient>' +
        '<linearGradient id="qd{n}" x1="0" y1="0" x2="1" y2=".2">' +
        '<stop offset="0" stop-color="#9fc9dd"/><stop offset="1" stop-color="#527f96"/></linearGradient>',
      body:
        /* Tinh thể phụ, đứng sau — cụm thạch anh thật không bao giờ mọc một mình */
        '<path d="M43 26l7 4v22l-7 4-6-4V30Z" fill="url(#qd{n})" opacity=".85"/>' +
        '<path d="M43 26l7 4-7 3-6-3Z" fill="#dff2fa" opacity=".8"/>' +
        /* Lăng trụ chính: hai mặt bên (sáng/tối) + chóp ba mặt */
        '<path d="M24 24l9 5v27l-9 4-9-4V29Z" fill="url(#qz{n})"/>' +
        '<path d="M33 29v27l-9 4V33Z" fill="url(#qd{n})"/>' +
        '<path d="M24 6l9 23-9 4-9-4Z" fill="#eaf8ff"/>' +
        '<path d="M24 6l9 23-9 4Z" fill="#bcdff0"/>' +
        /* Gờ giữa các mặt chóp — chóp thạch anh có SÁU mặt tam giác */
        '<g fill="none" stroke="#6f9db4" stroke-opacity=".7" stroke-width=".9">' +
        '<path d="M24 6v27M15 29l9 4 9-4M19.5 17.5l4.5 15M28.5 17.5L24 33"/></g>' +
        /* Vân ngang trên mặt trụ — dấu hiệu nhận dạng thạch anh, thấy rõ ở 170px */
        '<g fill="none" stroke="#fff" stroke-opacity=".45" stroke-width=".7">' +
        '<path d="M15 37h9M15 43h9M15 49h9M25 40h8M25 46h8"/></g>' +
        '<path d="M24 24l9 5v27l-9 4-9-4V29Z" fill="none" stroke="#e8fbff" stroke-opacity=".55" stroke-width="1"/>' +
        glint(19, 14, 3.4, .85) + glint(46, 30, 2.6, .6)
    },

    /* ⚠️ Emoji cũ là 🌑 (mặt trăng non) — một hình cầu, trong khi obsidian là
       MẢNH VỠ. Thật: thuỷ tinh núi lửa, vỡ theo mặt VỎ SÒ (conchoidal), rìa mỏng
       sắc như dao, đen bóng.
       ⚠️ Hình gần như đen trên nền tối → BẮT BUỘC có nét sáng ở rìa (ghi chú đầu file). */
    "volcano-obsidian": {
      defs:
        '<linearGradient id="ob{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#4a4658"/><stop offset=".38" stop-color="#1c1a26"/>' +
        '<stop offset="1" stop-color="#07060b"/></linearGradient>' +
        '<linearGradient id="og{n}" x1="0" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#fff" stop-opacity=".8"/>' +
        '<stop offset=".55" stop-color="#c9b8ff" stop-opacity=".18"/>' +
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
      body:
        '<path d="M20 10l24 6 9 20-13 20-22-5-6-22Z" fill="url(#ob{n})"/>' +
        /* Mặt vỡ vỏ sò: những cung lõm đồng tâm — dấu hiệu KHÔNG lẫn được của thuỷ tinh */
        '<path d="M20 10l24 6 4 12-20 8-13-6Z" fill="url(#og{n})"/>' +
        '<g fill="none" stroke="#a99ce0" stroke-opacity=".5" stroke-width="1">' +
        '<path d="M23 16c8 2 13 7 15 14M27 13c9 3 15 9 17 17M19 21c6 2 10 6 12 12"/></g>' +
        /* Rìa mỏng bắt sáng — chỗ mảnh obsidian sắc nhất */
        '<path d="M20 10l24 6 9 20-13 20-22-5-6-22Z" fill="none" stroke="#cfc6ff" stroke-opacity=".8" stroke-width="1.3"/>' +
        '<path d="M44 16l9 20-13 20" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width="1.9"/>' +
        /* Vệt sáng gương — thuỷ tinh phản chiếu thành một dải hẹp, không phải một đốm */
        '<path d="M33 24l6 3-10 18-5-3Z" fill="#fff" opacity=".16"/>' +
        glint(29, 20, 3.6, .8)
    },

    /* Bazan cổ: đá phun trào nguội nhanh → có LỖ BỌT KHÍ (vesicle). Chính các lỗ
       đó nói nó khác hẳn một hòn đá cuội. */
    "ancient-lava-rock": {
      defs:
        '<linearGradient id="ba{n}" x1=".25" y1="0" x2=".75" y2="1">' +
        '<stop offset="0" stop-color="#8d8ea0"/><stop offset=".4" stop-color="#4c4e60"/>' +
        '<stop offset="1" stop-color="#22232f"/></linearGradient>',
      body:
        '<path d="M15 24l12-11 19 3 8 15-6 19-19 6-14-11Z" fill="url(#ba{n})"/>' +
        /* Mặt trên hứng sáng */
        '<path d="M15 24l12-11 19 3 3 10-20 5Z" fill="#a4a5b6" opacity=".45"/>' +
        /* Lỗ bọt khí: mỗi lỗ tối ở giữa + gờ sáng ở mép trên (nó là một cái HỐC) */
        '<g fill="#191a24" opacity=".85">' +
        '<circle cx="26" cy="27" r="3.2"/><circle cx="38" cy="23" r="2.4"/>' +
        '<circle cx="34" cy="36" r="3.8"/><circle cx="45" cy="33" r="2.2"/>' +
        '<circle cx="24" cy="40" r="2.6"/><circle cx="42" cy="45" r="2.8"/>' +
        '<circle cx="30" cy="47" r="2"/><circle cx="19" cy="32" r="1.8"/></g>' +
        '<g fill="none" stroke="#b6b7c8" stroke-opacity=".5" stroke-width=".9">' +
        '<path d="M23 25.5a3.2 3.2 0 0 1 6 0M35.8 21.8a2.4 2.4 0 0 1 4.4 0' +
        'M30.6 34.5a3.8 3.8 0 0 1 6.8 0M21.6 38.7a2.6 2.6 0 0 1 4.8 0' +
        'M39.4 43.7a2.8 2.8 0 0 1 5.2 0"/></g>' +
        /* Thớ khoáng sáng rải trên nền đá (plagioclase) */
        dots("#d3d4e4", ".55", 21, 35, 1, 31, 20, .9, 44, 39, 1, 28, 42, .8, 47, 27, .9, 36, 49, .9) +
        '<path d="M15 24l12-11 19 3 8 15-6 19-19 6-14-11Z" fill="none" stroke="#b9bacb" stroke-opacity=".55" stroke-width="1.1"/>'
    },

    /* ⚠️ Emoji cũ là 🏜️ (CẢNH sa mạc có xương rồng) — một phong cảnh, không phải
       một mẫu vật. Thật: NHỮNG HẠT cát thạch anh, tròn cạnh vì gió mài, và một
       phần hạt bị "sương giá" mờ do mài mòn. */
    "desert-sand": {
      defs:
        '<linearGradient id="sd{n}" x1=".3" y1="0" x2=".7" y2="1">' +
        '<stop offset="0" stop-color="#ffe6a8"/><stop offset=".45" stop-color="#e0a44f"/>' +
        '<stop offset="1" stop-color="#96591f"/></linearGradient>',
      body:
        /* Đống cát: gò thấp, mép dưới rộng — đống hạt rời thì không dựng cao được */
        '<path d="M8 50c4-9 12-15 24-15s20 6 24 15Z" fill="url(#sd{n})"/>' +
        '<path d="M8 50c4-9 12-15 24-15-9 3-16 8-20 15Z" fill="#fff0c4" opacity=".35"/>' +
        /* Hạt RỜI thấy rõ từng hạt ở mép trên và bay quanh — thứ nói "đây là HẠT" */
        '<g stroke="#8a4f19" stroke-opacity=".45" stroke-width=".6">' +
        '<circle cx="20" cy="41" r="3.1" fill="#f6cd7e"/><circle cx="28" cy="37" r="2.6" fill="#ffe1a2"/>' +
        '<circle cx="36" cy="37" r="3" fill="#e8b665"/><circle cx="44" cy="41" r="2.5" fill="#f3c880"/>' +
        '<circle cx="32" cy="43" r="2.2" fill="#fff0cc"/><circle cx="24" cy="46" r="2" fill="#d8a45e"/>' +
        '<circle cx="41" cy="46" r="1.9" fill="#eab86a"/><circle cx="14" cy="46" r="2.1" fill="#f0c47a"/>' +
        '<circle cx="50" cy="46" r="1.8" fill="#e0ab5c"/></g>' +
        /* Vài hạt bay theo gió — sa mạc Sahara là cát DO GIÓ mang đi */
        '<g stroke="#a9682a" stroke-opacity=".4" stroke-width=".5">' +
        '<circle cx="46" cy="28" r="1.8" fill="#ffe0a0"/><circle cx="52" cy="22" r="1.3" fill="#f2c67f"/>' +
        '<circle cx="18" cy="30" r="1.5" fill="#ffdfa2"/><circle cx="12" cy="24" r="1.1" fill="#e9bd77"/></g>' +
        /* Đốm sáng trên hạt — thạch anh trong nên mỗi hạt là một mặt gương tí hon */
        dots("#fff", ".8", 19, 39.5, .8, 27, 35.5, .7, 35, 35.5, .8, 43, 39.5, .6, 31, 42, .6)
    },

    /* ⚠️ Emoji cũ là 🌕 (CẢ Mặt Trăng) cho một nhúm BỤI. Thật: bụi regolith xám,
       gồm mảnh vụn góc cạnh + hạt thuỷ tinh cầu (agglutinate) do thiên thạch nhỏ
       nung chảy — hạt cầu bóng là dấu hiệu chỉ có ở Mặt Trăng, không có ở cát Trái Đất. */
    "lunar-regolith": {
      defs:
        '<linearGradient id="lr{n}" x1=".3" y1="0" x2=".7" y2="1">' +
        '<stop offset="0" stop-color="#f0f1f5"/><stop offset=".42" stop-color="#a9aab4"/>' +
        '<stop offset="1" stop-color="#565764"/></linearGradient>' +
        '<radialGradient id="lb{n}" cx=".33" cy=".3" r=".75">' +
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".5" stop-color="#9aa0ad"/>' +
        '<stop offset="1" stop-color="#33363f"/></radialGradient>',
      body:
        /* SANG HAN LEN so voi ban dau: xam tren nen navy toi thi o 46px ca hinh chim
           vao nen, ma day la bui Mat Trang - thu duoc nang chieu truc tiep khong qua
           khi quyen. Cung ly do `volcano-obsidian` phai co net sang ria. */
        '<path d="M8 51c3-11 13-18 24-18s21 7 24 18Z" fill="url(#lr{n})"/>' +
        '<path d="M8 51c3-11 13-18 24-18-10 3-17 10-20 18Z" fill="#ffffff" opacity=".34"/>' +
        /* Manh vun GOC CANH - khong khi quyen nen khong bi mai tron nhu cat Trai Dat */
        '<g fill="#dcdde4" stroke="#4e5058" stroke-opacity=".55" stroke-width=".7">' +
        '<path d="M17 42l6-4 4 5-5 4Z"/><path d="M29 36l6 1 1 6-6 1Z"/>' +
        '<path d="M40 40l6-3 2 5-5 4Z"/><path d="M24 48l5-1 1 4-5 1Z"/>' +
        '<path d="M46 47l4-1 1 4-4 1Z"/><path d="M12 48l4-2 2 4-4 2Z"/>' +
        '<path d="M35 46h5l1 4-5 1Z"/></g>' +
        /* Hat thuy tinh CAU, bong - chi sinh ra khi thien thach nho nung chay dat da */
        '<circle cx="33" cy="46" r="4" fill="url(#lb{n})"/>' +
        '<circle cx="21" cy="34" r="2.8" fill="url(#lb{n})"/>' +
        '<circle cx="48" cy="42" r="2.3" fill="url(#lb{n})"/>' +
        dots("#fff", ".95", 32, 44.6, 1.2, 20.2, 33, .9, 47.2, 41, .7) +
        /* Bui min bay lo lung - regolith min nhu bot tan */
        dots("#e8e9ef", ".5", 15, 30, 1.3, 45, 27, 1.1, 53, 33, 1, 26, 26, .9, 38, 29, .8)
    },
    /* ⚠️ Emoji cũ là ⚪ (một hình tròn trắng) — không mang một thông tin nào. Thật:
       phiến đá silicat vỏ Sao Thuỷ, xám, và Sao Thuỷ gần như KHÔNG có khí quyển nên
       mặt nó rỗ HỐ VA CHẠM — vẽ ngay trên phiến đá thì mẫu vật tự nói nó đến từ đâu. */
    "mercury-slate": {
      defs:
        '<linearGradient id="ms{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#c8c4bb"/><stop offset=".45" stop-color="#8b877e"/>' +
        '<stop offset="1" stop-color="#4d4a45"/></linearGradient>',
      body:
        /* Phiến DẸT có bề dày — mặt trên là mặt nhìn, cạnh dưới cho thấy nó là tấm */
        '<path d="M12 26l22-9 20 10-4 15-24 9-16-11Z" fill="url(#ms{n})"/>' +
        '<path d="M12 26l22-9 20 10-22 9Z" fill="#d6d2c9" opacity=".55"/>' +
        '<path d="M12 26v14l16 11 4-15Z" fill="#3f3d39" opacity=".45"/>' +
        /* Hố va chạm: vành sáng + lòng tối + tia vật liệu bắn ra */
        '<g><ellipse cx="27" cy="25" rx="6" ry="3.4" fill="#5f5c56"/>' +
        '<ellipse cx="27" cy="24.2" rx="6" ry="3.4" fill="none" stroke="#e2ded4" stroke-opacity=".7" stroke-width="1"/>' +
        '<ellipse cx="27" cy="25.2" rx="2.6" ry="1.5" fill="#312f2c"/></g>' +
        '<g><ellipse cx="42" cy="28" rx="4" ry="2.3" fill="#5f5c56"/>' +
        '<ellipse cx="42" cy="27.4" rx="4" ry="2.3" fill="none" stroke="#e2ded4" stroke-opacity=".65" stroke-width=".9"/></g>' +
        '<g><ellipse cx="35" cy="33" rx="2.6" ry="1.5" fill="#57544f"/>' +
        '<ellipse cx="35" cy="32.6" rx="2.6" ry="1.5" fill="none" stroke="#d8d4ca" stroke-opacity=".55" stroke-width=".7"/></g>' +
        /* Tia ejecta mờ quanh hố lớn */
        '<g fill="none" stroke="#e8e4da" stroke-opacity=".3" stroke-width=".7">' +
        '<path d="M21 23l-4-2M33 22l4-2M27 21v-2.5M25 29l-2 3"/></g>' +
        dots("#efece3", ".45", 46, 23, 1, 19, 29, .9, 38, 22, .8, 31, 30, .7) +
        '<path d="M12 26l22-9 20 10-4 15-24 9-16-11Z" fill="none" stroke="#e6e2d8" stroke-opacity=".5" stroke-width="1.1"/>'
    },

    /* ⚠️ Emoji cũ là 🟠 (hình tròn cam) — không phải đá. Thật: bazan Sao Kim, đá
       núi lửa TỐI, nhưng mặt Sao Kim nóng ~470 °C nên khe nứt còn ĐỎ RỰC. Cái tương
       phản đen–cam đó vừa đúng khoa học vừa là thứ làm hình đọc được trên nền tối. */
    "venus-basalt": {
      defs:
        '<linearGradient id="vb{n}" x1=".25" y1="0" x2=".75" y2="1">' +
        '<stop offset="0" stop-color="#6b5b52"/><stop offset=".42" stop-color="#3a2f2b"/>' +
        '<stop offset="1" stop-color="#171210"/></linearGradient>' +
        '<linearGradient id="vh{n}" x1="0" y1="0" x2="0" y2="1">' +
        '<stop offset="0" stop-color="#ffd98a"/><stop offset=".5" stop-color="#ff7a1a"/>' +
        '<stop offset="1" stop-color="#b32a00"/></linearGradient>',
      body:
        '<path d="M14 23l14-11 21 5 5 17-9 18-20 4-12-12Z" fill="url(#vb{n})"/>' +
        '<path d="M14 23l14-11 21 5 2 8-22 6Z" fill="#84726a" opacity=".4"/>' +
        /* Khe nứt còn nóng: lớp DƯỚI rộng mờ (hào quang nhiệt) + lớp TRÊN mảnh sáng.
           Hai lớp thay cho một filter blur — xem ghi chú "KHÔNG CÓ FILTER" đầu file. */
        '<g fill="none" stroke="url(#vh{n})" stroke-opacity=".35" stroke-width="5" stroke-linecap="round">' +
        '<path d="M20 20l8 12-4 14M28 32l14-4M42 28l6 10"/></g>' +
        '<g fill="none" stroke="url(#vh{n})" stroke-width="2" stroke-linecap="round">' +
        '<path d="M20 20l8 12-4 14M28 32l14-4M42 28l6 10M28 32l-9 6"/></g>' +
        '<g fill="none" stroke="#ffe9b8" stroke-width=".8" stroke-linecap="round" opacity=".9">' +
        '<path d="M21 21l7 11M29 31l12-3"/></g>' +
        /* Lỗ bọt khí (bazan nào cũng có), một số lỗ hắt sáng cam từ bên trong */
        '<g fill="#120d0c" opacity=".8">' +
        '<circle cx="35" cy="20" r="2.2"/><circle cx="46" cy="21" r="1.7"/>' +
        '<circle cx="24" cy="44" r="2"/><circle cx="38" cy="45" r="2.4"/></g>' +
        dots("#ff9d3c", ".8", 35, 20, 1, 38, 45, 1.1, 46, 21, .7) +
        /* Rìa sáng — không có thì cả khối chìm vào nền navy */
        '<path d="M14 23l14-11 21 5 5 17-9 18-20 4-12-12Z" fill="none" stroke="#c9b6ab" stroke-opacity=".55" stroke-width="1.1"/>'
    },

    /* ═══════════ 🌌 CỔ VẬT VŨ TRỤ ═══════════ */

    /* ⚠️ Emoji cũ là ☄️ (sao chổi đang bay) — sai hẳn vật: sao chổi là băng+bụi
       đang bay, thiên thạch sắt là KHỐI KIM LOẠI đã rơi xuống. Thật: vỏ nung chảy
       đen, mặt rỗ "dấu ngón tay" (regmaglypt), và một MẶT CẮT MÀI BÓNG hiện vân
       Widmanstätten — hoa văn chỉ hình thành khi nguội trong hàng triệu năm, tức
       bằng chứng nó đến từ lòng một tiểu hành tinh. */
    "iron-meteorite": {
      defs:
        '<linearGradient id="im{n}" x1=".25" y1="0" x2=".75" y2="1">' +
        '<stop offset="0" stop-color="#6e6a63"/><stop offset=".4" stop-color="#33302c"/>' +
        '<stop offset="1" stop-color="#131110"/></linearGradient>' +
        '<linearGradient id="iw{n}" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#eef1f6"/><stop offset=".5" stop-color="#a8b0bd"/>' +
        '<stop offset="1" stop-color="#6d7581"/></linearGradient>',
      body:
        '<path d="M13 27l11-13 22 2 8 16-7 19-21 6-13-13Z" fill="url(#im{n})"/>' +
        /* Rỗ regmaglypt: hõm nông do khí quyển bào lúc rơi, mép trên sáng */
        '<g fill="#1c1a18" opacity=".75">' +
        '<ellipse cx="22" cy="24" rx="4.4" ry="3.2"/><ellipse cx="32" cy="19" rx="3.4" ry="2.4"/>' +
        '<ellipse cx="21" cy="37" rx="3.8" ry="2.8"/><ellipse cx="29" cy="45" rx="3.2" ry="2.2"/>' +
        '<ellipse cx="41" cy="47" rx="2.6" ry="1.9"/></g>' +
        '<g fill="none" stroke="#8b857c" stroke-opacity=".5" stroke-width=".9">' +
        '<path d="M17.6 24a4.4 3.2 0 0 1 8.8 0M28.6 19a3.4 2.4 0 0 1 6.8 0' +
        'M17.2 37a3.8 2.8 0 0 1 7.6 0M25.8 45a3.2 2.2 0 0 1 6.4 0"/></g>' +
        /* Mặt cắt mài bóng + vân Widmanstätten (hai họ nét chéo nhau) */
        '<path d="M38 22l14 5-4 15-13-4Z" fill="url(#iw{n})"/>' +
        '<g fill="none" stroke="#4e5560" stroke-opacity=".85" stroke-width=".8">' +
        '<path d="M40 23l7 15M44 22l6 14M37 27l13 4M36 33l12 4M36 38l11 3"/></g>' +
        '<g fill="none" stroke="#fdfefe" stroke-opacity=".55" stroke-width=".6">' +
        '<path d="M41.5 23l7 14M38 25l12 4M36.5 35l11 3"/></g>' +
        '<path d="M38 22l14 5-4 15-13-4Z" fill="none" stroke="#f2f5fa" stroke-opacity=".75" stroke-width="1"/>' +
        /* Rìa sáng — vỏ nung chảy gần như đen */
        '<path d="M13 27l11-13 22 2 8 16-7 19-21 6-13-13Z" fill="none" stroke="#b3aca2" stroke-opacity=".55" stroke-width="1.1"/>' +
        glint(45, 26, 3, .8)
    },

    /* ⚠️ Emoji cũ là 🪐 (CẢ Sao Thổ có vành) cho một HẠT băng trong vành. Thật:
       vành Sao Thổ là vô số cục băng nước, phần lớn nhỏ cỡ viên đá lạnh; vẽ đúng
       một cụm cục băng đang trôi, có mặt vỡ và sương giá. */
    "saturn-ring-ice": {
      defs:
        '<linearGradient id="ri{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".4" stop-color="#d5eefc"/>' +
        '<stop offset="1" stop-color="#7aa9c6"/></linearGradient>' +
        '<linearGradient id="rj{n}" x1="0" y1="0" x2="1" y2=".6">' +
        '<stop offset="0" stop-color="#a9d5ec"/><stop offset="1" stop-color="#5c8aa8"/></linearGradient>',
      body:
        /* Cục chính — khối đa diện, mặt trên sáng, mặt phải trong bóng */
        '<path d="M26 14l17 7 4 17-13 14-15-6-4-19Z" fill="url(#ri{n})"/>' +
        '<path d="M26 14l17 7-13 8-14-4Z" fill="#fbfeff"/>' +
        '<path d="M43 21l4 17-13 14 -4-23Z" fill="url(#rj{n})" opacity=".9"/>' +
        '<g fill="none" stroke="#6f9db8" stroke-opacity=".6" stroke-width=".9">' +
        '<path d="M16 26l14 4 13-9M30 30l4 22"/></g>' +
        /* Cục nhỏ đi kèm — hạt vành đai không bao giờ đi một mình */
        '<path d="M48 42l8 4-1 8-8 2-2-7Z" fill="url(#ri{n})" opacity=".95"/>' +
        '<path d="M48 42l8 4-8 3-3-4Z" fill="#fbfeff"/>' +
        '<path d="M9 40l7 2 1 7-6 3-4-6Z" fill="url(#ri{n})" opacity=".9"/>' +
        '<path d="M9 40l7 2-6 3-3-3Z" fill="#f4fbff"/>' +
        /* Sương giá trên mặt băng */
        dots("#fff", ".85", 22, 22, 1.2, 36, 26, 1, 27, 41, 1.1, 40, 36, .9, 51, 46, .8, 12, 44, .8) +
        glint(38, 19, 4, .95) + glint(53, 44, 2.4, .7) + glint(14, 42, 2.2, .65)
    },

    /* ⚠️ Emoji cũ là 🔵 (hình tròn xanh). Thật: sương metan — khí metan ĐÓNG BĂNG
       thành tinh thể hình KIM toả ra từ một mảnh nền, xanh lơ nhạt (metan hấp thụ
       ánh đỏ, nên Sao Thiên Vương mới có màu lam lục). */
    "uranus-frost": {
      defs:
        '<linearGradient id="uf{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#e6fbff"/><stop offset=".45" stop-color="#8fdff0"/>' +
        '<stop offset="1" stop-color="#3f8fa8"/></linearGradient>' +
        '<radialGradient id="uh{n}" cx=".5" cy=".5" r=".5">' +
        '<stop offset="0" stop-color="#bff4ff" stop-opacity=".55"/>' +
        '<stop offset="1" stop-color="#bff4ff" stop-opacity="0"/></radialGradient>',
      body:
        /* Hào quang lạnh — thay cho filter blur, chỉ là một gradient trong suốt */
        '<circle cx="32" cy="34" r="26" fill="url(#uh{n})"/>' +
        /* Mảnh nền để sương bám lên: không có nền thì các nét kim đọc ra như tia sáng */
        '<path d="M18 44l14-5 15 6-3 9-13 4-13-6Z" fill="#4a7f95"/>' +
        '<path d="M18 44l14-5 15 6-15 5Z" fill="#7ec2d6" opacity=".9"/>' +
        /* Tinh thể kim toả ra, mỗi kim có gai hai bên — đúng dáng sương giá thật */
        '<g fill="none" stroke="url(#uf{n})" stroke-width="1.8" stroke-linecap="round">' +
        '<path d="M32 39V13M32 39L15 24M32 39l17-15M32 39L20 34M32 39l12-5"/></g>' +
        '<g fill="none" stroke="#d8f8ff" stroke-width=".9" stroke-linecap="round" opacity=".85">' +
        '<path d="M32 20l-5-4M32 20l5-4M32 28l-5-4M32 28l5-4"/>' +
        '<path d="M23 32l-1-6M23 32l6-1M41 32l1-6M41 32l-6-1"/>' +
        '<path d="M20 29l-6 1M44 29l6 1"/></g>' +
        glint(32, 14, 4.2, .95) + glint(16, 25, 2.6, .75) + glint(48, 25, 2.6, .75)
    },

    /* Bụi kim cương Sao Hải Vương: carbon bị nén trong lòng hành tinh thành kim
       cương. Tinh thể kim cương tự nhiên mọc dạng BÁT DIỆN (hai chóp tứ giác úp
       vào nhau) — vẽ đúng dạng đó thay vì hình 💠 chung chung. */
    "neptune-diamond-dust": {
      defs:
        '<linearGradient id="dm{n}" x1=".2" y1="0" x2=".8" y2="1">' +
        '<stop offset="0" stop-color="#ffffff"/><stop offset=".45" stop-color="#bfe4ff"/>' +
        '<stop offset="1" stop-color="#5f86c4"/></linearGradient>' +
        '<linearGradient id="dn{n}" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#8fb6f0"/><stop offset="1" stop-color="#33518f"/></linearGradient>' +
        '<radialGradient id="dh{n}" cx=".5" cy=".5" r=".5">' +
        '<stop offset="0" stop-color="#9fd0ff" stop-opacity=".5"/>' +
        '<stop offset="1" stop-color="#9fd0ff" stop-opacity="0"/></radialGradient>',
      body:
        '<circle cx="30" cy="31" r="25" fill="url(#dh{n})"/>' +
        /* Bát diện chính: chóp trên 4 mặt, chóp dưới 4 mặt, gặp nhau ở đường xích đạo */
        '<path d="M30 8l14 15H16Z" fill="url(#dm{n})"/>' +
        '<path d="M30 8l14 15H30Z" fill="url(#dn{n})" opacity=".55"/>' +
        '<path d="M16 23h28L30 50Z" fill="url(#dm{n})" opacity=".92"/>' +
        '<path d="M30 23h14L30 50Z" fill="url(#dn{n})" opacity=".6"/>' +
        '<g fill="none" stroke="#f2faff" stroke-opacity=".8" stroke-width="1">' +
        '<path d="M30 8l14 15H16ZM16 23h28L30 50ZM30 8v42M23 23l7 27M37 23l-7 27"/></g>' +
        /* Hai tinh thể nhỏ — "bụi" nên phải có nhiều hạt, không chỉ một viên */
        '<path d="M50 33l7 7-7 8-6-8Z" fill="url(#dm{n})" opacity=".95"/>' +
        '<path d="M50 33l7 7h-7Z" fill="url(#dn{n})" opacity=".5"/>' +
        '<path d="M13 39l5 5-5 6-5-6Z" fill="url(#dm{n})" opacity=".9"/>' +
        '<path d="M13 39l5 5h-5Z" fill="url(#dn{n})" opacity=".5"/>' +
        glint(25, 17, 4.4, .95) + glint(53, 37, 2.8, .8) + glint(11, 43, 2.4, .7)
    },

    /* Bụi sao tinh vân Lạp Hộ: khí và bụi giữa các sao. Không có bề mặt cứng nên
       vẽ bằng những đám gradient trong suốt xếp lớp — hồng (hydro phát sáng) và
       lam (bụi tán xạ ánh sao), kèm mấy ngôi sao trẻ đang hình thành bên trong. */
    "orion-stardust": {
      defs:
        '<radialGradient id="n1{n}" cx=".42" cy=".4" r=".6">' +
        '<stop offset="0" stop-color="#ffb3e6" stop-opacity=".95"/>' +
        '<stop offset=".55" stop-color="#c05ad0" stop-opacity=".5"/>' +
        '<stop offset="1" stop-color="#6b2a8f" stop-opacity="0"/></radialGradient>' +
        '<radialGradient id="n2{n}" cx=".6" cy=".55" r=".6">' +
        '<stop offset="0" stop-color="#a8e6ff" stop-opacity=".85"/>' +
        '<stop offset=".55" stop-color="#4a8fe0" stop-opacity=".45"/>' +
        '<stop offset="1" stop-color="#25408f" stop-opacity="0"/></radialGradient>' +
        '<radialGradient id="n3{n}" cx=".5" cy=".5" r=".5">' +
        '<stop offset="0" stop-color="#fff6d0" stop-opacity=".9"/>' +
        '<stop offset="1" stop-color="#fff6d0" stop-opacity="0"/></radialGradient>',
      body:
        /* Ba đám khí lệch tâm nhau — tinh vân thật không đối xứng */
        '<ellipse cx="27" cy="27" rx="23" ry="19" fill="url(#n1{n})" transform="rotate(-18 27 27)"/>' +
        '<ellipse cx="40" cy="39" rx="20" ry="15" fill="url(#n2{n})" transform="rotate(14 40 39)"/>' +
        '<ellipse cx="22" cy="42" rx="14" ry="10" fill="url(#n1{n})" opacity=".6" transform="rotate(26 22 42)"/>' +
        /* Vệt khí bị sao trẻ thổi bạt — nét mảnh, cong theo dòng */
        '<g fill="none" stroke="#ffd6f5" stroke-opacity=".45" stroke-width="1.1" stroke-linecap="round">' +
        '<path d="M12 24c8-6 18-5 25 1M18 36c7 4 16 3 22-2M30 14c5 2 9 6 11 11"/></g>' +
        /* Quầng sáng của cụm sao trẻ ở giữa (vùng Trapezium) */
        '<circle cx="31" cy="30" r="9" fill="url(#n3{n})"/>' +
        /* Sao — cỡ khác nhau, có sao lớn thì mới ra chiều sâu */
        dots("#ffffff", ".95", 31, 30, 1.6, 26, 26, 1.1, 36, 33, 1, 20, 20, 1.2,
             45, 24, 1, 48, 44, 1.1, 15, 44, 1, 39, 50, .9, 24, 49, .8, 52, 33, .8) +
        glint(31, 30, 6, .9) + glint(20, 20, 3.4, .8) + glint(48, 44, 3, .75)
    }
  };

  var n = 0; /* hậu tố id gradient — xem ghi chú đầu file về chuyện id trùng */

  /**
   * Chuỗi SVG của một mẫu vật, hoặc "" nếu chưa vẽ.
   * ⚠️ TRẢ VỀ MARKUP — nơi gọi **đừng** `esc()` nó (chuỗi này do chính file này
   *    viết ra, không có một mẩu dữ liệu người dùng nào bên trong).
   */
  function svg(id) {
    var a = ART[id];
    if (!a) return "";
    var k = ++n;
    return ('<svg class="spart" viewBox="0 0 64 64" aria-hidden="true" focusable="false">' +
            '<defs>' + a.defs + '</defs>' + a.body + '</svg>').replace(/\{n\}/g, k);
  }

  global.AstroQSpecimenArt = {
    svg: svg,
    /** Đã vẽ id này chưa — bộ đo dùng để soi thiếu/thừa so với js/specimens.js. */
    has: function (id) { return Object.prototype.hasOwnProperty.call(ART, id); },
    ids: function () { return Object.keys(ART); }
  };
})(window);
