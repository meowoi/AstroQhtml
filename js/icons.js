/* ============================================================
   icons.js — bộ icon lucide-style dùng chung cho mọi trang AstroQ.
   Dùng: element.innerHTML = lic("telescope");  // hoặc AstroQ.lic(...)
   SVG kế thừa currentColor, cỡ 1em (class .lic trong css/common.css).
   ============================================================ */
(function(global){
  "use strict";
  var LIC = {
    atom:'<circle cx="12" cy="12" r="1"/><path d="M20.2 20.2c2.04-2.03.02-7.36-4.5-11.9-4.54-4.52-9.87-6.54-11.9-4.5-2.04 2.03-.02 7.36 4.5 11.9 4.54 4.52 9.87 6.54 11.9 4.5Z"/><path d="M15.7 15.7c4.52-4.54 6.54-9.87 4.5-11.9-2.03-2.04-7.36-.02-11.9 4.5-4.52 4.54-6.54 9.87-4.5 11.9 2.03 2.04 7.36.02 11.9-4.5Z"/>',
    award:'<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    book:'<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    bot:'<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    clock:'<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    cpu:'<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    ext:'<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    flame:'<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    hourglass:'<path d="M5 22h14"/><path d="M5 2h14"/><path d="M17 22v-4.17a2 2 0 0 0-.59-1.41L12 12l-4.41 4.42A2 2 0 0 0 7 17.83V22"/><path d="M7 2v4.17a2 2 0 0 0 .59 1.41L12 12l4.41-4.42A2 2 0 0 0 17 6.17V2"/>',
    layers:'<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 12.5-9.17 4.16a2 2 0 0 1-1.66 0L2 12.5"/>',
    leaf:'<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    orbit:'<circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><path d="M10.4 21.9a10 10 0 0 0 9.94-15.42M13.5 2.1a10 10 0 0 0-9.84 15.42"/>',
    radar:'<path d="M19.07 4.93A10 10 0 0 0 6.99 3.34"/><path d="M4 6h.01"/><path d="M2.29 9.62A10 10 0 1 0 21.31 8.35"/><path d="M16.24 7.76A6 6 0 1 0 8.23 16.67"/><path d="M12 18h.01"/><path d="M17.99 11.66A6 6 0 0 1 15.77 16.67"/><circle cx="12" cy="12" r="2"/><path d="m13.41 10.59 5.66-5.66"/>',
    rocket:'<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91 0z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    ruler:'<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
    satellite:'<path d="M13 7 9 3 5 7l4 4"/><path d="m17 11 4 4-4 4-4-4"/><path d="m8 12 4 4 6-6-4-4Z"/><path d="m16 8 3-3"/><path d="M9 21a6 6 0 0 0-6-6"/>',
    search:'<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    shield:'<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    sparkles:'<path d="M9.94 15.5A2 2 0 0 0 8.5 14.06l-6.13-1.58a.5.5 0 0 1 0-.96L8.5 9.94A2 2 0 0 0 9.94 8.5l1.58-6.13a.5.5 0 0 1 .96 0L14.06 8.5A2 2 0 0 0 15.5 9.94l6.13 1.58a.5.5 0 0 1 0 .96L15.5 14.06a2 2 0 0 0-1.44 1.44l-1.58 6.13a.5.5 0 0 1-.96 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>',
    target:'<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    telescope:'<path d="m10.07 12.49-6.18 1.32a.93.93 0 0 1-1.11-.7l-.54-2.15a1.07 1.07 0 0 1 .69-1.27l13.5-4.44"/><path d="m13.56 11.75 4.33-.92"/><path d="m16 21-3.1-6.21"/><path d="M16.49 5.94a2 2 0 0 1 1.45-2.43l1.09-.27a1 1 0 0 1 1.21.73l1.52 6.06a1 1 0 0 1-.73 1.21l-1.09.27a2 2 0 0 1-2.42-1.45z"/><path d="m6.16 8.63 1.11 4.46"/><path d="m8 21 3.1-6.21"/><circle cx="12" cy="13" r="2"/>',
    timer:'<line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/>',
    trophy:'<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/><path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    zap:'<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>',

    /* ───────────── Sổ Tay Thuật Ngữ (codex.html) ─────────────
       Tiền tố `cx-` để không đụng 22 icon dùng chung ở trên: `star`/`moon`/`comet`
       là những cái tên rất dễ có ngày trang khác cần dùng cho việc khác.
       ⚠️ Nét vẽ theo đúng khuôn `lic()`: viewBox 24×24, `fill="none"` +
          `stroke="currentColor"` đặt ở thẻ <svg>. Chỗ nào cần TÔ ĐẶC thì ghi
          `fill="currentColor"` ngay trên phần tử đó (thuộc tính của phần tử thắng
          thuộc tính của <svg>) — đó là cách duy nhất tô đặc mà vẫn đổi màu được
          bằng class bên ngoài. */
    'cx-star':'<circle cx="12" cy="12" r="4.4"/><circle cx="12" cy="12" r="1.6"/><path d="M12 2.6v2.4M12 19v2.4M2.6 12h2.4M19 12h2.4"/><path d="M5.6 5.6l1.7 1.7M16.7 16.7l1.7 1.7M18.4 5.6l-1.7 1.7M7.3 16.7l-1.7 1.7"/>',
    'cx-planet':'<circle cx="12" cy="11" r="5.6"/><path d="M3.2 14.4c4.6 2.5 12.2 2.5 17.6-.6"/>',
    'cx-dwarf':'<circle cx="12" cy="12" r="3.4"/><path stroke-dasharray="2.6 2.4" d="M12 3.2a8.8 8.8 0 1 0 0 17.6 8.8 8.8 0 0 0 0-17.6Z"/><circle cx="12" cy="3.2" r="1" fill="currentColor" stroke="none"/><circle cx="20.4" cy="14" r="0.9" fill="currentColor" stroke="none"/><circle cx="4.6" cy="9" r="0.9" fill="currentColor" stroke="none"/>',
    'cx-moon':'<circle cx="10.4" cy="13.4" r="5.2"/><circle cx="19.2" cy="5.6" r="2.2"/><path stroke-dasharray="2.2 2.6" d="M17.4 7.8a9 9 0 0 1-11.2 8.4"/>',
    'cx-asteroid':'<path d="M9.6 3.6 4.4 7.2l-.6 5.6 3.8 4.9 5.9 1.4 5.1-3.7.8-5.9-4-4.6Z"/><circle cx="10" cy="9.4" r="1.5"/><circle cx="14.8" cy="13.6" r="1.1"/>',
    'cx-comet':'<circle cx="16.6" cy="7.6" r="3.2"/><path d="M13.9 9.6 4.2 18.4M14.9 12.2 8.6 19M11.5 8.2 3.4 12.6"/>',
    'cx-meteoroid':'<path d="M13.4 6.6 9.2 8.4l-1 4.2 3.1 3 4.3-1.2 1.2-4.3-3.4-3.5Z"/><circle cx="4.6" cy="5.2" r="0.9" fill="currentColor" stroke="none"/><circle cx="19.4" cy="18.6" r="0.9" fill="currentColor" stroke="none"/>',
    'cx-meteor':'<path stroke-dasharray="2.4 2.2" d="M2.8 19.6c2.2-5.6 7.4-9.4 13.4-9.6"/><path d="M20.4 3.6 9.8 14.2"/><circle cx="9" cy="15" r="2"/><path d="M17.6 3.2 12.4 8.4M21 7l-5.2 5.2"/>',
    'cx-meteorite':'<path d="M2.6 19.4h18.8"/><path d="M9.4 10.6 6.4 13l-.4 3.6 2.6 2.8h6l1.8-3.2-.7-4-3.2-1.8Z"/><path stroke-dasharray="1.8 2" d="M12 3.2v3.6"/>',
    'cx-exoplanet':'<circle cx="7.6" cy="8.6" r="4.6"/><circle cx="10.4" cy="8.6" r="1.7" fill="currentColor" stroke="none"/><path d="M2.6 18.4h4l1-2.6h3.4l1-2.4h1.2l1 2.4h3.4l1 2.6h2.4"/>',
    'cx-blackhole':'<circle cx="12" cy="12" r="3.6" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="3.6"/><path d="M3.4 12c0-2.1 3.9-3.8 8.6-3.8s8.6 1.7 8.6 3.8-3.9 3.8-8.6 3.8S3.4 14.1 3.4 12Z"/>',
    'cx-gravity':'<circle cx="12" cy="15.6" r="4.4"/><path d="M12 2.8v3.2M12 6l-1.5-1.6M12 6l1.5-1.6"/><path d="M5.2 5.4l1.9 2.2M18.8 5.4l-1.9 2.2"/>',
    'cx-nebula':'<path d="M6.4 16.2a3.4 3.4 0 0 1-.5-6.7 4.6 4.6 0 0 1 8.6-2.2 3.8 3.8 0 0 1 3.6 6.1 3.2 3.2 0 0 1-2.3 2.8Z"/><circle cx="10" cy="12.2" r="1.15" fill="currentColor" stroke="none"/><circle cx="14.4" cy="10.6" r="0.8" fill="currentColor" stroke="none"/>',
    'cx-supernova':'<circle cx="12" cy="12" r="2.4" fill="currentColor" stroke="none"/><path d="M12 1.9v3.4M12 18.7v3.4M1.9 12h3.4M18.7 12h3.4"/><path d="M4.9 4.9l2.4 2.4M16.7 16.7l2.4 2.4M19.1 4.9l-2.4 2.4M7.3 16.7l-2.4 2.4"/><circle cx="12" cy="12" r="6.4" stroke-dasharray="1.8 2.6"/>',
    'cx-cmb':'<ellipse cx="12" cy="12" rx="9" ry="6.2"/><circle cx="8.2" cy="10.4" r="1.05" fill="currentColor" stroke="none"/><circle cx="14.8" cy="9.8" r="0.75" fill="currentColor" stroke="none"/><circle cx="11.4" cy="14" r="0.85" fill="currentColor" stroke="none"/><circle cx="16.4" cy="13.6" r="0.6" fill="currentColor" stroke="none"/><circle cx="6.4" cy="13.4" r="0.6" fill="currentColor" stroke="none"/>',

    /* ── 4 icon của Đợt AI/Robot (09/08/2026) ───────────────────────────
       ⚠️ Cùng luật hai chiều như 4 icon Đợt 1: mọi `ic` của thẻ phải có bản vẽ,
          và không bản vẽ nào được bỏ không — nên bốn cái này chỉ hợp lệ khi 4 thẻ
          `term_ai` · `term_machine_learning` · `term_algorithm` · `term_sensor`
          cùng có mặt trong `js/codex-terms.js`. */
    'cx-ai':'<rect x="4.6" y="4.6" width="14.8" height="14.8" rx="3.2"/><circle cx="12" cy="12" r="3.1"/><path d="M12 4.6V2.4M12 21.6v-2.2M4.6 12H2.4M21.6 12h-2.2M7.2 7.2 5.6 5.6M18.4 18.4l-1.6-1.6M16.8 7.2l1.6-1.6M5.6 18.4l1.6-1.6"/>',
    'cx-machine-learning':'<circle cx="5.4" cy="7" r="1.7"/><circle cx="5.4" cy="17" r="1.7"/><circle cx="12" cy="12" r="1.9"/><circle cx="18.6" cy="7.6" r="1.7"/><circle cx="18.6" cy="16.4" r="1.7"/><path d="M7 7.7l3.3 3.1M7 16.3l3.3-3.1M13.8 11.2l3.1-2.7M13.8 12.9l3.1 2.6"/>',
    'cx-algorithm':'<rect x="8.6" y="2.8" width="6.8" height="4" rx="1.1"/><path d="M12 6.8v3.1"/><path d="M12 9.9 8.4 13.4h7.2z"/><path d="M12 13.4v3.2"/><rect x="8.6" y="16.6" width="6.8" height="4.2" rx="1.1"/><path d="M15.4 18.7h3.4v-9.1"/>',
    'cx-sensor':'<circle cx="12" cy="17.6" r="2.4"/><path d="M12 15.2V9.4"/><path d="M8.1 9.1a5.6 5.6 0 0 1 7.8 0M5.5 6.3a9.4 9.4 0 0 1 13 0"/>',
    /* ⚠️ Hai icon cho hai the DAO DUC AI. Ve bang HINH CO NGHIA, khong ve chu.
          `cx-ai-ethics` = CAI CAN (tru + don ganh + hai dia) — nghia "can nhac".

       ⚠️⚠️ `cx-algorithmic-bias` BAN DAU LA MOT CAI CAN LECH, VA DA PHAI VE LAI.
          Render that o 26px (co the ve tren the So Tay) thi hai cai can doc ra gan
          nhu MOT — do nghieng khong du de phan biet, ma chung lai dung canh nhau
          trong cung nhom "AI". Day dung lop loi da tra gia 7 lan voi bo icon sticker
          (dem thanh chu so 17 · dau chia thanh vien kim cuong · comet thanh cai thia):
          **ve dung y ma sai HINH thi nguoi xem doc ra mot do vat khac.**
          Ban moi lay thang phep vi cua chinh bai doc: day may nhan ra "con chim" ma
          chi cho xem chim se — gap da dieu no noi khong phai chim. Nen hinh la MOT
          KHUNG (tap vi du duoc cho xem) co ba cham BEN TRONG va mot cham BI BO RA
          NGOAI. Khac hoan toan cai can, va doc duoc o 26px.
       ⚠️ Ban thu hai co them mot dau GACH CHEO qua cham ngoai (y: bi loai). Da bo:
          render that thi o 26px no lan hoan toan vao net tron (stroke-width 2 tren
          ban kinh 1,7), tuc no khong song noi o CO SE DUNG, ma o 64px thi chi them
          nhieu. Mot chi tiet chi doc duoc o co khong ai nhin la mot chi tiet nen bo. */
    'cx-ai-ethics':'<path d="M12 3.4v16.4"/><path d="M8.4 20.2h7.2"/><path d="M5.2 7.4h13.6"/><path d="M5.2 7.4 2.9 12.6h4.6z"/><path d="M18.8 7.4l-2.3 5.2h4.6z"/>',
    'cx-algorithmic-bias':'<rect x="2.6" y="6.2" width="12.4" height="11.6" rx="2.4"/><circle cx="6.4" cy="10.4" r="1.15"/><circle cx="11.2" cy="10.4" r="1.15"/><circle cx="8.8" cy="14.4" r="1.15"/><circle cx="19.9" cy="12" r="1.7"/>',

    /* ── 4 icon của Đợt 1 (06/08/2026) ──────────────────────────────────
       ⚠️ Phép kiểm `check_pages` mục [12] canh icon HAI CHIỀU: mọi `ic` của thẻ
          phải có bản vẽ, VÀ không bản vẽ nào được bỏ không. Nên bốn icon này chỉ
          hợp lệ khi 4 thẻ tương ứng cũng có mặt trong `js/codex-terms.js`.
       ⚠️ `lic(name)` trả về `LIC[name] || ""` — icon thiếu thì ra một ô SVG RỖNG,
          không lỗi, không cảnh báo. Đó là lý do phép kiểm hai chiều đáng giữ. */

    /* Màu sắc & nhiệt độ của sao: một ngôi sao, dưới là THANG BA NẤC to→nhỏ.
       Nét vẽ đơn sắc không dùng được màu để nói nóng–nguội, nên cỡ chấm là thứ
       duy nhất còn lại để đọc ra "một cái thang". */
    'cx-star-colour':'<circle cx="12" cy="8.6" r="3.6"/><path d="M12 1.8v1.9M4.9 8.6H3M21 8.6h-1.9M6.9 3.5l1.4 1.4M17.1 3.5l-1.4 1.4"/><path d="M4.6 18.6h14.8"/><circle cx="7" cy="18.6" r="2.1" fill="currentColor" stroke="none"/><circle cx="12" cy="18.6" r="1.4" fill="currentColor" stroke="none"/><circle cx="16.8" cy="18.6" r="0.85" fill="currentColor" stroke="none"/>',

    /* Nhật thực: đĩa Mặt Trời có tia + một đĩa ĐẶC che lệch lên trên.
       Đĩa che phải ĐẶC — hai vòng tròn rỗng chồng nhau đọc ra như hai hành tinh
       cạnh nhau chứ không phải cái này che cái kia. */
    'cx-solar-eclipse':'<circle cx="12" cy="12" r="5.4"/><path d="M12 3.1v1.6M12 19.3v1.6M3.1 12h1.6M19.3 12h1.6M5.7 5.7l1.2 1.2M17.1 17.1l1.2 1.2M18.3 5.7l-1.2 1.2M6.9 17.1l-1.2 1.2"/><circle cx="14.1" cy="9.9" r="4.3" fill="currentColor" stroke="none"/>',

    /* Nguyệt thực: đĩa Mặt Trăng + cung NÉT ĐỨT = mép bóng Trái Đất đang bò lên,
       cộng chấm nhỏ bên ngoài là Trái Đất đổ bóng đó.
       ⚠️ Dùng lại đúng thành ngữ `stroke-dasharray` của `cx-moon` — hai thẻ cùng
          họ Mặt Trăng thì phải nhìn ra là cùng họ. */
    'cx-lunar-eclipse':'<circle cx="10.6" cy="12.6" r="5.6"/><path stroke-dasharray="2.1 2.4" d="M6.2 9.1a5.6 5.6 0 0 0 8.8 6.9"/><circle cx="20" cy="5.4" r="1.9"/><path d="M18.4 6.6l-2.3 2.3"/>',

    /* Khí quyển: vòm hành tinh ở đáy + hai cung đồng tâm phía trên = các TẦNG.
       Chỉ vẽ nửa dưới của hành tinh — vẽ cả quả cầu thì hai cung trên trông như
       vành đai Sao Thổ chứ không như lớp khí bọc lấy mặt đất. */
    'cx-earth-atmosphere':'<path d="M2.9 20.4a9.1 9.1 0 0 1 18.2 0"/><path d="M5.1 13.9a7.4 7.4 0 0 1 13.8 0"/><path stroke-dasharray="2.4 2.6" d="M3.3 9.6a9.6 9.6 0 0 1 17.4 0"/><circle cx="9.2" cy="17.6" r="0.9" fill="currentColor" stroke="none"/><circle cx="14.6" cy="18.4" r="0.7" fill="currentColor" stroke="none"/>'
  };

  /* Trả về chuỗi SVG của icon; cls: class phụ (tuỳ chọn). */
  function lic(name, cls){
    return '<svg class="lic '+(cls||"")+'" viewBox="0 0 24 24" fill="none" stroke="currentColor"'+
           ' stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+
           (LIC[name]||"")+'</svg>';
  }

  global.AstroQIcons = LIC;
  if(!global.lic) global.lic = lic;
  (global.AstroQ = global.AstroQ || {}).LIC = LIC;
  global.AstroQ.lic = lic;
})(window);
