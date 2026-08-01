# Khuôn đề xuất — yêu cầu ChatGPT / Gemini trả lời đúng dạng này

> **Cách dùng:** dán khuôn dưới đây kèm `docs/BRIEFING.md` khi hỏi ChatGPT/Gemini.
> Nhận được câu trả lời thì lưu thành `docs/proposals/YYYY-MM-DD-<ten-ngan>.md`
> (ghi rõ model nào viết), rồi bảo Claude đọc file đó.
>
> Lưu thành file thay vì dán vào chat có 2 cái lợi: Claude đọc file trực tiếp được,
> và bạn có lịch sử để đối chiếu về sau.

---

## Câu lệnh gửi kèm

```
Hãy trả lời theo đúng khuôn dưới đây, không thêm phần mở đầu hay kết luận.
Nếu một mục nào đó bạn không đủ thông tin để điền, hãy ghi "không đủ thông tin"
thay vì đoán — phần này sẽ được đối chiếu với mã nguồn thật.
```

---

## Khuôn

```markdown
# Đề xuất: <tên ngắn>
**Người viết:** ChatGPT / Gemini · **Ngày:** YYYY-MM-DD

## 1. Vấn đề cần giải
<Một đoạn. Nói rõ vấn đề, không nói giải pháp.>

## 2. Đề xuất
<Mô tả giải pháp. Ngắn gọn, cụ thể.>

## 3. Giả định tôi đang dựa vào
<Liệt kê thành gạch đầu dòng. Mỗi giả định một dòng.
 Đây là mục QUAN TRỌNG NHẤT — nó sẽ được kiểm bằng mã nguồn.
 Ví dụ: "Tôi giả định mỗi nhiệm vụ tốn khoảng 1 ngày công."
        "Tôi giả định bản đồ 3D đã có sẵn dữ liệu cho cả 8 hành tinh.">

## 4. Thay đổi ở phía client
<Trang nào, phần nào. Không cần viết mã.>

## 5. Thay đổi ở phía backend
<Endpoint mới? Trường dữ liệu mới? Hay không đụng tới backend?>

## 6. Ảnh hưởng tới người chơi cũ
<Dữ liệu tiến độ đã có bị ảnh hưởng không? Có ai phải làm lại từ đầu không?>

## 7. Cần bao nhiêu NỘI DUNG mới
<Số câu quiz, số bài đọc, số lời thoại... Ước lượng bằng con số.
 Nội dung là nút thắt của dự án này, nên mục này không được bỏ trống.>

## 8. Cái tôi KHÔNG chắc — nhờ Claude kiểm
<Gạch đầu dòng. Ghi thẳng những chỗ bạn đang đoán.>

## 9. Phương án nhỏ hơn nếu quá tốn
<Nếu phải cắt xuống 1/3 công sức thì giữ lại phần nào? Bỏ phần nào?>
```

---

## Vì sao khuôn này

- **Mục 3 và 8** biến một bài viết nghe-cho-hay thành một đề xuất kiểm được. Model không đọc
  được mã nguồn thì luôn đánh giá thấp chi phí — không phải vì nói dối, mà vì thiếu dữ liệu.
  Bắt nó nói ra giả định thì chỗ sai lộ ra ngay, thay vì lộ ra sau khi đã code nửa chừng.
- **Mục 6** là chỗ hay bị quên nhất, và cũng là chỗ đắt nhất khi quên.
- **Mục 7** ép nhìn thẳng vào nút thắt thật của AstroQ.
- **Mục 9** cho bạn một đường lui, thay vì lựa chọn nhị phân làm-hết hoặc bỏ-hết.
