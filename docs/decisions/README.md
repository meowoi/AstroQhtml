# Sổ quyết định

Mỗi quyết định lớn = một file `NNN-<ten-ngan>.md`, đánh số tăng dần, **không sửa lại số đã dùng**.

## Vì sao cần sổ này

ChatGPT và Gemini **không nhớ gì giữa các cuộc trò chuyện**, và không đọc được mã nguồn.
Không có sổ này thì vòng bàn sau chúng sẽ đề xuất lại đúng cái bạn vừa bác ở vòng trước,
và bạn phải giải thích lại từ đầu mỗi lần.

Có sổ rồi thì chỉ cần dán mục **"Đã bác — và vì sao"** của các quyết định liên quan vào đầu
cuộc trò chuyện, kèm `docs/BRIEFING.md`.

Mục **"Đã bác"** quan trọng ngang mục "Đã chọn": nó là thứ chặn được vòng lặp vô ích.

## Trạng thái

| Trạng thái | Nghĩa là |
|---|---|
| `đang mở` | Đang bàn, chưa chốt. Được phép đề xuất thêm phương án. |
| `đã chốt` | Đã quyết. **Không mở lại** trừ khi có dữ kiện mới. |
| `đã thay thế` | Bị quyết định số NNN khác thay. Ghi rõ số đó. |

## Khuôn

```markdown
# NNN. <Tên quyết định>

**Trạng thái:** đang mở | đã chốt | đã thay thế bởi NNN
**Ngày mở:** YYYY-MM-DD · **Ngày chốt:** YYYY-MM-DD
**Người quyết:** <tên chủ dự án>

## Bối cảnh
<Vì sao phải quyết. Có gì đang cản trở.>

## Các phương án đã cân nhắc
### A. <tên> — đề xuất bởi <ChatGPT/Gemini/Claude/chủ dự án>
<mô tả · ưu · nhược>
### B. <tên>
<...>

## Đã chọn
<Phương án nào. Một đoạn.>

## Đã bác — và vì sao
<Gạch đầu dòng. Mỗi dòng: phương án + lý do bác.
 Viết đủ rõ để dán thẳng vào ChatGPT/Gemini mà không cần giải thích thêm.>

## Số liệu đã kiểm bằng mã nguồn
<Những con số Claude đã đếm được, dùng làm căn cứ. Ghi lại để lần sau không phải đếm lại.>

## Hệ quả
<Cái gì phải làm theo. Cái gì từ nay không được làm nữa.>
```
