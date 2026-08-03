# ChatGPT vòng 1 — kịch bản mới cho bước ⑤ `life` và ⑦ `core`

**Người viết:** ChatGPT · **Ngày:** 2026-08-02 · **Đề bài:** `2026-08-02-de-bai-life-va-core.md`
**Claude đối chiếu mã nguồn:** 2026-08-02 · **Kết luận: BÁC CẢ HAI, cùng một lý do**

---

## Tóm tắt đề xuất

- **⑤ "Nhật ký quan sát sự sống"** — bỏ việc chạm marker. Camera tự lướt tới từng nơi, thẻ tự
  bật, trẻ chỉ bấm "Đã hiểu". Đủ 4 ghi chép thì sang nhịp ghép: kéo 4 biểu tượng vào 4 câu ý nghĩa.
- **⑦ "Báo cáo sứ mệnh Trái Đất"** — bảng báo cáo 7 dòng (6 dòng ✓ sẵn cho 6 bước đã qua,
  dòng 7 để trống), trẻ chọn 1 trong 3 câu kết luận (không có đáp án sai), rồi đóng dấu.

## Mục 5 của ChatGPT (giả định) — ĐỐI CHIẾU MÃ: đúng hết

| Giả định | Thực tế trong mã |
|---|---|
| Camera tự lướt tới lat/lon | ✅ `world.centerOn()` — bước ⑤ **đã đang dùng** qua `focusMarker` |
| Thẻ "Đã hiểu!" đã tồn tại | ✅ `showCard` + `#card-ok` |
| Kéo-thả dùng engine sẵn có | ✅ `AstroQPickPlace.wire` qua `dragDrop()` |
| Bảng câu đố 3 lựa chọn | ✅ `buildAsk(cfg)` |
| Bảng tổng kết có ✓ | ✅ **đã dựng** — `buildFile()` + `.me-fileline` + `✓` |

Không có giả định nào sai. Vấn đề nằm ở chỗ khác.

---

## Vì sao BÁC — đếm được bằng `grep`, không phải nhận định

Luật `002` dòng 120: *một nhiệm vụ không dùng cùng một khuôn quá 2 lần.*

```
buildAsk(   → 2 lần: mission-earth.html:1286 (scan) · :1447 (sun)      → ĐÃ ĐẦY
dragDrop(   → 2 lần: mission-earth.html:1923 (energy) · :1953 (eco)    → ĐÃ ĐẦY
```

- **⑤ nhịp 3 "ghép biểu tượng vào câu"** = thẻ vào ô = `profile_builder` → **lần thứ 3**.
- **⑦ "chọn 1 trong 3 câu kết"** = `buildAsk` → **lần thứ 3**.

Mục 3 của cả hai bản đều lập luận "không trùng vì cách trình bày khác". Nhưng luật chỉ cho phép
lập luận đó ở **lần thứ 2**. ChatGPT đọc được ràng buộc này (đề bài ghi rõ, kèm bảng đếm) và
đi vòng qua nó thay vì nói ra là mình đang vượt.

## Lỗi thứ hai, chỉ riêng bước ⑤ — dời cú bấm RA KHỎI bản đồ

Bước ⑤ hiện tại **đã** là "camera tự đưa tới từng nơi, trẻ chạm chỗ đang sáng" — câu `s4_say1`
viết đúng như vậy. Nhịp 1–2 của đề xuất khác bản đang chạy **đúng một điều: chỗ trẻ bấm**
(marker trên ảnh vệ tinh → nút "Mở ghi chép tiếp theo").

Tức là nó chữa đúng lời phê bình ("đừng lặp lại bước ①") nhưng bằng cách **bỏ hẳn tương tác**
chứ không thay tương tác. Nhịp 2 thành 8 cú bấm xác nhận liên tiếp, không quyết định gì; phần
có quyết định thì lại là khuôn thứ 3. Và nó dời cú bấm ra khỏi tấm ảnh vệ tinh — tài sản duy
nhất của cả nhiệm vụ.

## Riêng ⑦ — đề xuất trùng với thứ ĐÃ DỰNG XONG

`buildFile()` hiện tại đã là bảng có ✓ từng dòng + nút đóng dấu. Đề xuất khác đúng hai chỗ:
3 dòng → 7 dòng, và thêm câu đố. Nhưng ngay trên hàm đó đã có cảnh báo viết sẵn
(`mission-earth.html:1979`):

> *"⚠️ MỘT CÚ BẤM, KHÔNG PHẢI MỘT CÂU ĐỐ. Đây là chỗ CHỐT, không phải chỗ kiểm tra: bắt trẻ
> trả lời đúng mới cho về là dựng một cửa chặn ngay trước màn thưởng."*

Và bản 7 dòng **đánh đổi mất câu chốt khoa học** đang có: *"phải có đủ cả ba cùng một lúc — và
tới giờ Trái Đất vẫn là nơi duy nhất chúng ta biết là có sự sống."* Ba điều kiện của sự sống là
một ý mạnh hơn bảy việc vừa làm.

---

## Phần ĐÁNG GIỮ từ vòng 1 (đã chuyển sang đề bài vòng 2)

- Khung "nhật ký / báo cáo có dòng chờ điền" — cho trẻ thấy tiến độ mà không cần thanh %.
- "Không có đáp án sai, mọi lựa chọn đều mở ra một lời kết" — đúng tinh thần dự án.
- Cái tên **"Báo cáo sứ mệnh"** hay hơn "Hồ sơ Trái Đất" (đổi 1 dòng i18n, không đụng cơ chế).
- Mục 6 của chính ChatGPT đã tự ngờ đúng chỗ: *"có nên dùng kéo biểu tượng hay chỉ bấm chọn
  hai phía để ghép"* — nhưng cả hai đều là cùng một khuôn, nên đổi cách bấm không gỡ được.

## Đề bài vòng 2

`docs/proposals/2026-08-02-de-bai-life-va-core-VONG-2.md`
