# Đề bài gửi ChatGPT — kịch bản mới cho bước ⑤ `life` và bước ⑦ `core`

**Ngày:** 2026-08-02 · **Người soạn:** Claude (đối chiếu mã nguồn) · **Vai:** ChatGPT = sáng tác
(xem `docs/PHAN-VAI.md`)

> **Cách dùng:** dán TOÀN BỘ phần trong khung dưới đây vào ChatGPT, kèm `docs/BRIEFING.md`.
> Nhận câu trả lời thì lưu thành `docs/proposals/2026-08-02-<ten>.md` rồi bảo Claude đọc.
>
> ⚠️ Đề bài này cố ý DÀI ở phần ràng buộc. ChatGPT **không đọc được repo**, nên mọi ràng
> buộc không viết ra đây đều sẽ bị vi phạm — và vòng trước đã mất trọn một lượt vì thiếu
> đúng loại thông tin này (nó đề xuất cấu trúc quest kéo theo ~70–80 nghìn dòng mã).

---

```
Bạn đang giúp thiết kế lại HAI BƯỚC trong một nhiệm vụ học tập cho trẻ 8–15 tuổi.
Hãy trả lời theo đúng khuôn ở cuối. Nếu một mục nào đó bạn không đủ thông tin để
điền, hãy ghi "không đủ thông tin" thay vì đoán — phần này sẽ được đối chiếu với mã
nguồn thật.

════════════════════════════════════════════════════════════════════════
BỐI CẢNH
════════════════════════════════════════════════════════════════════════

Nhiệm vụ "Hành Tinh Xanh": trẻ khám phá Trái Đất qua 7 bước, tất cả diễn ra TRÊN MỘT
TRANG DUY NHẤT, trên nền một BẢN ĐỒ THẾ GIỚI PHẲNG bằng ẢNH VỆ TINH THẬT (equirectangular).
Không tải lại trang giữa các bước; chuyển bước bằng cách lướt/phóng khung nhìn bản đồ.

Bảy bước và CƠ CHẾ CHƠI hiện tại:

  ① scan     — chạm 7 châu lục trên bản đồ (mỗi cái hiện một thẻ), rồi một câu đố
               2 lựa chọn: "nước hay đất nhiều hơn?" → hé lộ 71% / 29%
  ② timeline — bấm lần lượt 5 mốc trên một thanh thời gian; mỗi mốc đổi tông màu cả
               hành tinh + hiện một bức tranh minh hoạ
  ③ sun      — câu đố 3 lựa chọn "nếu Mặt Trời tắt thì sao?" → bản đồ tối đi → kể 3 vai
               trò của Mặt Trời → sáng lại → chạm 3 vùng khí hậu trên bản đồ
  ④ energy   — kéo-thả 3 thẻ năng lượng sạch vào 3 nhà máy neo trên bản đồ; vùng quanh
               nhà máy đang bị tối, thả đúng thì sáng lại
  ⑤ life     — ⚠️ CẦN KỊCH BẢN MỚI (xem dưới)
  ⑥ eco      — kéo-thả 7 thẻ hành động vào 2 rổ "NÊN LÀM" / "KHÔNG NÊN LÀM"
  ⑦ core     — ⚠️ CẦN KỊCH BẢN MỚI (xem dưới)

════════════════════════════════════════════════════════════════════════
HAI BƯỚC CẦN BẠN THIẾT KẾ LẠI
════════════════════════════════════════════════════════════════════════

▸ BƯỚC ⑤ `life` — "sự sống trên Trái Đất"

  Bản cũ: trẻ chạm 4 vùng trên bản đồ, mỗi lần một chiếc drone bay xuống quét bằng tia
  laser (~1,5 giây hoạt cảnh) rồi hiện thẻ mẫu vật.

  ĐÃ BỊ BÁC vì: bước ① nay ĐÃ LÀ một chuyến đi khắp bề mặt (chạm 7 châu lục). Dựng thêm
  một chuyến khám phá thứ hai bằng cùng một thao tác, chỉ khác ở chỗ có thêm hoạt cảnh
  drone, là LẶP LẠI CÙNG MỘT VIỆC bằng một cỗ máy to hơn. Trẻ hỏi "sao lại phải làm lại?"

  ⚠️ RÀNG BUỘC CỨNG: bước này BẮT BUỘC phải trao đủ 4 "mẫu dữ liệu" sau, vì máy chủ gắn
  chúng vào chính id bước này (đổi là phải sửa server + phát hành lại):
      · 🌊 Đại Tây Dương   (lat 12, lon −42)  — "nước phủ ~71% bề mặt Trái Đất"
      · 🌳 Rừng Amazon     (lat −4, lon −62)  — "rừng cung cấp oxy để thở"
      · 🐧 Nam Cực         (lat −75, lon 20)  — "hàng triệu loài cùng sống trên Trái Đất"
      · 🏔️ Dãy Himalaya    (lat 28, lon 87)   — "núi cao che chắn và giữ nước"
  Bốn cái tên và bốn toạ độ này KHÔNG ĐƯỢC ĐỔI. Nhưng CÁCH trẻ nhận chúng thì tự do.

▸ BƯỚC ⑦ `core` — bước CUỐI, ngay trước màn tổng kết

  Bản cũ: kéo 3 "viên ngọc" (Ngọc Mặt Trời · Ngọc Giọt Nước · Ngọc Khí Quyển) vào 3 ô của
  một "Mạch Năng Lượng Sự Sống".

  ĐÃ BỊ BÁC vì: ba viên ngọc và cái mạch đó là VẬT THỂ BỊA — không có trong bất cứ thứ gì
  sáu bước trước dạy. Cả nhiệm vụ đứng trên một bức ảnh vệ tinh THẬT với toạ độ THẬT, rồi
  bước cuối lại bắt trẻ lắp đồ chơi khoa học viễn tưởng. Đó là chỗ duy nhất câu chuyện tự
  phản bội chính nó.

  ⚠️ Bước này KHÔNG gắn mẫu dữ liệu nào, KHÔNG gắn huy hiệu nào → nội dung TỰ DO HOÀN TOÀN.
  Nó chỉ cần: là một cái kết xứng đáng, và dẫn được vào màn tổng kết.

════════════════════════════════════════════════════════════════════════
RÀNG BUỘC CỨNG — vi phạm là đề xuất không dùng được
════════════════════════════════════════════════════════════════════════

1. KHÔNG ĐƯỢC THÊM, BỎ, GỘP HAY ĐỔI TÊN BƯỚC. Vẫn đúng 7 bước, đúng thứ tự, đúng id.
   Lý do: id bước là khoá trong cơ sở dữ liệu người chơi; đổi là người chơi cũ mất tiến
   độ, và mọi thay đổi ở đây buộc phải phát hành lại máy chủ. Bạn chỉ được đổi VIỆC TRẺ
   LÀM bên trong hai bước ⑤ và ⑦.

2. KHÔNG TRÙNG CƠ CHẾ VỚI BƯỚC KHÁC. Luật của dự án: *một nhiệm vụ không dùng cùng một
   khuôn tương tác quá 2 lần; nếu dùng 2 lần thì phải khác hẳn cách trình bày.*
   Đếm hiện tại: "chạm marker trên bản đồ" đã dùng **3 lần** (①③ và ⑤ cũ) — ĐÃ VƯỢT.
   "Kéo-thả thẻ" đã dùng **2 lần** (④⑥). "Câu đố chọn đáp án" đã dùng **2 lần** (①③).
   ⇒ Hai bước mới NÊN dùng cơ chế thứ tư, hoặc dùng lại một cơ chế cũ nhưng với cách
     trình bày khác hẳn — và phải nói rõ khác ở chỗ nào.

3. MỌI THỨ PHẢI VỪA MỘT MÀN HÌNH ĐIỆN THOẠI DỌC 390×844. Đây là con số đo được, không
   phải ước lượng: ở mức phóng của nhiệm vụ, màn đó chỉ nhìn thấy **83 độ kinh tuyến**
   bản đồ một lúc. Hệ quả: nếu cơ chế đòi trẻ nhìn/kéo giữa nhiều điểm cách xa nhau trên
   bản đồ, nó KHÔNG chơi được trên điện thoại. (Bốn toạ độ của bước ⑤ trải 149 độ — tức
   không bao giờ cùng nằm trong khung.)

4. KHÔNG CÓ CÚ KÉO BẢN ĐỒ NÀO. Trẻ không kéo/xoay/phóng bản đồ; cảnh tự dời khi cần.
   (Kéo-thả một tấm THẺ thì được — đó là chuyện khác.)

5. PHẢI CHƠI ĐƯỢC HOÀN TOÀN BẰNG BÀN PHÍM, tương đương chuột. Không phải chỉ thêm nhãn
   trợ năng.

6. KHÔNG CÓ TRẠNG THÁI THUA, KHÔNG PHẠT, KHÔNG ĐỒNG HỒ ĐẾM NGƯỢC. Làm sai thì được
   khích lệ và thử lại. Đây là phần HỌC, không phải trò chơi tính điểm.

7. PHẢI HOÀN THÀNH ĐƯỢC KHI TẮT HOẠT CẢNH (`prefers-reduced-motion`). Nghĩa là: không
   bước nào được đòi trẻ bắt kịp một vật đang chuyển động, hoặc chờ một hoạt cảnh chạy
   xong mới giải được.

8. KHÔNG CON SỐ NÀO KHÔNG CÓ NGUỒN. Nếu kịch bản của bạn cần một con số (tuổi, kích
   thước, tỉ lệ…), hãy ghi rõ ở mục "giả định" để nó được tra nguồn trước khi dùng.
   Viết định tính thì luôn an toàn.

9. KHÔNG BỊA VẬT THỂ KHÔNG CÓ THẬT (đây chính là thứ đã giết bước ⑦ cũ). Mọi thứ trẻ
   thao tác nên là thứ có thật hoặc là dụng cụ hiển nhiên của con tàu.

10. NGÂN SÁCH: mỗi bước nên chơi xong trong **60–90 giây**. Nhiệm vụ đã có 7 bước; một
    bước dài hơn thế sẽ làm cả nhiệm vụ quá tải.

════════════════════════════════════════════════════════════════════════
NHỮNG KHUÔN ĐÃ CÓ SẴN — dùng lại thì gần như miễn phí
════════════════════════════════════════════════════════════════════════

Nếu kịch bản của bạn dựng được từ những thứ này thì chi phí gần bằng 0. Cần thứ hoàn
toàn mới thì cứ đề xuất, nhưng hãy nói rõ để còn cân chi phí.

  · Thẻ nội dung: emoji lớn + tên + một câu + nút "Đã hiểu!" (trẻ tự đóng)
  · Bảng câu đố: một câu hỏi + 2–3 nút lựa chọn có emoji
  · Kéo-thả thẻ vào ô (có sẵn cả đường bàn phím)
  · Dấu hiệu neo theo toạ độ thật trên bản đồ, chạm được
  · Hộp thoại nhân vật (Comet — hoa tiêu; Byte — kỹ thuật viên), gõ từng chữ, có nút
  · Lướt/phóng khung nhìn bản đồ tới một toạ độ
  · Đổi tông màu cả hành tinh; phủ tối một vùng rồi làm sáng lại
  · Ảnh minh hoạ trong bảng

════════════════════════════════════════════════════════════════════════
ĐÃ BÁC RỒI — ĐỪNG ĐỀ XUẤT LẠI
════════════════════════════════════════════════════════════════════════

  · Bỏ bớt bước / gộp 7 bước thành ít hơn → phải sửa và phát hành lại máy chủ.
  · Bất cứ thứ gì dùng quả cầu 3D → nhiệm vụ đã cố ý bỏ hẳn 3D (đường tải giảm từ
    308 KB xuống 71 KB); và một phiên bản 3D trước đây đã khiến trẻ KHÔNG THỂ hoàn
    thành bước vì kéo xoay camera chứ không xoay hành tinh.
  · Đặt biểu tượng "áng chừng" lên bản đồ. Nền là ảnh vệ tinh THẬT: đặt sai chỗ thì
    chính bức ảnh tố cáo (bản trước từng để thẻ "Rừng Amazon" rơi giữa đại dương).
  · Thêm nhân vật/vật phẩm tưởng tượng mới (ngọc, lõi, tinh thể, cỗ máy...).
  · Câu đố có đáp án SAI ở bước đang dạy kiến thức mới — biến lời mời suy nghĩ thành
    cái bẫy. (Câu đố "đoán rồi hé lộ", mọi lựa chọn đều được, thì tốt.)

════════════════════════════════════════════════════════════════════════
KHUÔN TRẢ LỜI — viết đúng dạng này, một bản cho MỖI bước
════════════════════════════════════════════════════════════════════════

# Đề xuất: <tên ngắn> — bước <⑤ hoặc ⑦>
**Người viết:** ChatGPT · **Ngày:** 2026-08-02

## 1. Vấn đề cần giải
<Một đoạn. Nói vấn đề, không nói giải pháp.>

## 2. Kịch bản
<Kể theo trình tự trẻ trải nghiệm, từng nhịp một. Ghi rõ trẻ THẤY gì, LÀM gì,
 và nhận lại gì sau mỗi thao tác.>

## 3. Vì sao cơ chế này KHÔNG trùng với 6 bước kia
<Nói thẳng nó khác bước nào ở chỗ nào.>

## 4. Lời thoại
<Viết sẵn tiếng Việt, giọng nói với trẻ 8–15 tuổi, mỗi câu tối đa 2 dòng.
 Đánh dấu [CẦN KIỂM: …] cho mọi câu có chứa dữ kiện khoa học.>

## 5. Giả định tôi đang dựa vào
<Gạch đầu dòng. ĐÂY LÀ MỤC QUAN TRỌNG NHẤT — nó sẽ được đối chiếu với mã nguồn.>

## 6. Cái tôi KHÔNG chắc
<Thành thật. Chỗ nào bạn đoán thì nói là đoán.>

## 7. Nó vừa 390×844 như thế nào
<Trả lời cụ thể, vì đây là ràng buộc hay bị vi phạm nhất.>

## 8. Chơi bằng bàn phím thế nào
<Phím nào làm gì.>
```

---

## Ghi chú cho Claude ở vòng sau

- Nhận được đề xuất thì **đối chiếu mục 5 và 6 với mã nguồn trước tiên** — đó là chỗ
  ChatGPT hay sai nhất vì nó không đọc được repo.
- Kiểm ngay hai con số: bốn toạ độ của bước ⑤ có bị đổi không, và cơ chế mới có làm
  "chạm marker" lên **4 lần** trong một nhiệm vụ không.
- Mọi câu có `[CẦN KIỂM: …]` gom một lượt gửi Gemini tra nguồn (đúng điểm giao duy nhất
  giữa hai lane, xem `docs/PHAN-VAI.md`).
