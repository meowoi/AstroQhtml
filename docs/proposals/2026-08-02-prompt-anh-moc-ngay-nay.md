# Prompt sinh ảnh cho mốc ⑤ "Ngày nay" — bước ② dòng thời gian

**Ngày:** 02/08/2026 · **Người soạn:** Claude · **Dùng cho:** ChatGPT (gen ảnh)
**Đích:** `img/era/now.png` — bức thứ 5, bổ sung cho bộ 4 đã có

> **Cách dùng:** dán phần trong khung vào ChatGPT. Nhận ảnh về thì lưu thành
> **`img/era/now.png`** (đúng tên, chữ thường) rồi bảo Claude chạy
> `python scratchpad/make_era_assets.py` — nó tự sinh 4 file
> `now-{700,1120}.{avif,webp}` và gắn vào trang.

---

## Vì sao mốc này CẦN tranh, sau khi trước đó tôi bảo là không cần

Tôi từng chốt *"mốc ngày nay cố ý không có tranh"*, lý do: bức ảnh vệ tinh THẬT đang nằm
ngay sau lưng bảng, nên vẽ tranh lên đó là thay ảnh thật bằng tranh ở đúng mốc duy nhất
có ảnh thật.

Chủ dự án chơi thật và chỉ ra hệ quả: **bốn mốc có tranh rồi mốc thứ năm trống** đọc ra
như một chỗ bị thiếu, không như một quyết định. Quyết định: **thêm tranh**. Lập luận cũ
vẫn đúng về mặt nội dung, nhưng nó không thắng được sự bất nhất mà trẻ nhìn thấy.

⚠️ Vì thế bức này **vẫn phải mang nhãn "MINH HOẠ"** như bốn bức kia — nó là tranh vẽ, và
bảng đã có sẵn nhãn đó. Không đổi gì ở phần nhãn.

---

## Nội dung bức tranh phải khớp ĐÚNG đoạn chữ hiện cùng nó

Đây là ràng buộc quan trọng nhất: bảng hiện **tranh + tiêu đề + đoạn văn** cùng lúc, nên
tranh nói khác chữ là trẻ thấy ngay.

Nguyên văn đoạn chữ đang chạy (khoá `era_now_p`):

> *"Sau khi khủng long biến mất, các loài thú phát triển mạnh. Nước phủ khoảng 71% bề
> mặt, không khí có oxy để thở, hàng triệu loài cùng sinh sống. Tới giờ đây vẫn là hành
> tinh duy nhất chúng ta biết là có sự sống."*

Tiêu đề: **"Hành tinh xanh"** · Mốc: **"Ngày nay"** · Emoji trên thanh mốc: 🌍

⇒ Bức tranh phải cho thấy: **nước nhiều hơn đất** · **thú** (không phải khủng long) ·
**nhiều loài khác nhau cùng lúc** · **không khí trong, có sự sống**.

---

```
Vẽ MỘT bức tranh minh hoạ cho trẻ 8–15 tuổi, mô tả TRÁI ĐẤT NGÀY NAY.

Đây là bức thứ 5 trong một bộ 5 bức về các thời kỳ của Trái Đất. Bốn bức trước là:
Trái Đất nóng bỏng đầy dung nham · đại dương đầu tiên · sự sống đơn giản trong nước rồi
lên cạn · thời khủng long. Bức này là hiện tại — cái kết của cả chuỗi.

════════════════════════════════════════════════════════════════════
PHONG CÁCH — phải KHỚP với 4 bức trước
════════════════════════════════════════════════════════════════════

· Tranh vẽ 2D phẳng, kiểu sách khoa học cho học sinh: hình khối rõ, viền sạch,
  màu tươi nhưng không chói. KHÔNG phải ảnh chụp, KHÔNG giả ảnh chụp, KHÔNG 3D render.
· Bố cục NGANG, tỉ lệ 3:2 (ví dụ 1536×1024).
· Nhìn từ ngoài không gian? KHÔNG — nhìn CẢNH TRÊN MẶT ĐẤT, ngang tầm mắt, giống bốn bức
  trước. Bốn bức kia đều là cảnh mặt đất/mặt biển, nên bức này bay lên nhìn từ vũ trụ là
  phá vỡ mạch của cả dãy.
· KHÔNG có chữ, KHÔNG có số, KHÔNG có nhãn, KHÔNG có mũi tên trong tranh. Chữ nằm ngoài
  tranh, do trang tự hiện.
· KHÔNG có con người, KHÔNG có nhà cửa, thành phố, xe cộ, cột khói, đường dây điện.
  ⚠️ Lý do quan trọng: bước NGAY SAU đó nói về ô nhiễm và năng lượng sạch. Nếu bức
  "ngày nay" đã có nhà máy hay thành phố thì nó kể trước phần của bước sau, và trẻ đọc
  ra thành "ngày nay = ô nhiễm" — trong khi đoạn chữ đi kèm chỉ nói về sự sống phong phú.

════════════════════════════════════════════════════════════════════
NỘI DUNG — bám sát đoạn chữ hiện cùng tranh
════════════════════════════════════════════════════════════════════

Một cảnh Trái Đất khoẻ mạnh hôm nay, có ĐỦ bốn thứ sau và không thêm gì gây phân tán:

1. NƯỚC CHIẾM PHẦN LỚN KHUNG. Biển xanh trong, chiếm khoảng hai phần ba bức tranh
   (đoạn chữ nói "nước phủ khoảng 71% bề mặt" — bức tranh nên cho cảm giác đó mà không
   cần ghi con số).
2. MỘT DẢI ĐẤT XANH ở tiền cảnh hoặc một bên: cây cối, đồng cỏ, vài rặng núi xa.
3. THÚ — đây là điểm nhấn, vì đoạn chữ mở đầu bằng "sau khi khủng long biến mất, các
   loài THÚ phát triển mạnh". Vẽ vài con thú có thật, dễ nhận, mỗi con một loại:
   ví dụ một con voi, một con hươu, một con thú nhỏ ở gần. KHÔNG có khủng long.
4. NHIỀU LOÀI KHÁC NHAU CÙNG LÚC ("hàng triệu loài cùng sinh sống"): thêm chim đang bay,
   cá hoặc rùa biển thấy được dưới mặt nước trong, vài bông hoa hoặc bụi cây khác loại.
   Sự đa dạng là thông điệp — đừng vẽ một loài duy nhất chiếm hết.

Bầu trời xanh trong, có mây trắng, ánh nắng dịu. Không khí sáng, sạch, dễ thở.

⚠️ ĐỪNG vẽ: khủng long · người · thành phố · nhà máy · ống khói · rác · băng tan ·
   cháy rừng · bất cứ thứ gì mang nghĩa cảnh báo. Bức này là cái kết ẤM ÁP của một
   chuỗi 4,54 tỷ năm; phần "hành tinh đang gặp vấn đề" thuộc về bước sau.

════════════════════════════════════════════════════════════════════
CHẤT LƯỢNG KỸ THUẬT — bức này phải xem được ở nơi mạng yếu
════════════════════════════════════════════════════════════════════

· Xuất PNG, cạnh dài khoảng 1536px, tỉ lệ 3:2.
· Ưu tiên MẢNG MÀU PHẲNG và ít chi tiết vụn. Tranh càng nhiều hạt nhiễu, nhiều vệt cọ
  nhỏ, nhiều đốm li ti thì file nén càng nặng — mà bức này sẽ được hạ xuống 700px và nén
  lại để trẻ ở vùng mạng kém tải được. Nét to, khối rõ nén tốt hơn nhiều.
· Đừng thêm khung viền, đừng thêm hiệu ứng giấy cũ, đừng thêm bóng mờ toàn ảnh.
· Chi tiết quan trọng (mấy con thú) ĐỪNG đặt sát mép dưới hay sát mép trên: bức có thể
  bị thu nhỏ, và chi tiết ở mép là chi tiết mất trước.
```

---

## Việc của Claude sau khi có ảnh

1. Kiểm ảnh gốc (cỡ, tỉ lệ 3:2, nội dung khớp đoạn chữ, không có chữ/người/thành phố).
2. `python scratchpad/make_era_assets.py` → sinh `now-{700,1120}.{avif,webp}`.
3. Thêm `img: 'now'` vào phần tử `{ id: 'now', … }` của `const ERAS`, và **xoá dòng chú
   thích "cố ý không có tranh"** — để lại là một chú thích lỗi thời, thứ dự án đã trả giá.
4. ⚠️ Kiểm lại **`sizes` phải có trên CẢ HAI `<source>`**, không chỉ trên `<img>` — lỗi
   này đã mắc một lần và làm trình duyệt tải bản 1120 thay vì 700, **nặng gấp đôi trên
   đúng nhóm mạng yếu mà việc này sinh ra để phục vụ**.
5. ⚠️ Kiểm lại chiều cao bảng: `.era-fig{max-width:min(100%,52vh)}` đang giữ cho bản đồ
   còn nhìn thấy được (đo được 1366×768 từng chỉ còn **30px** bản đồ khi ảnh tràn bề
   rộng). Thêm bức thứ 5 không đổi ràng buộc này, nhưng phải đo lại.
6. Cập nhật phép kiểm ảnh trong `check_pages` mục [3e] (đang đếm **4** bức) và chạy lại
   `smoke_mission_earth`.
