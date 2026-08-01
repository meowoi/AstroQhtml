# 001. Cấu trúc World / Quest cho các hành tinh

**Trạng thái:** đang mở — *phần bộ khuôn đã tách ra và chốt ở `002-bo-khuon-tuong-tac.md`*
**Ngày mở:** 2026-07-31 · **Ngày chốt:** —
**Người quyết:** chủ dự án

> **Còn mở đúng những gì phải ĐO mới trả lời được:** bao nhiêu chủ đề / bước mỗi World ·
> cổng mở khoá 70% · Daily Mission & Event · độ tuổi mục tiêu.
> Con số mở khoá các câu này đến từ bước 5 của `002`: làm đầy Mặt Trăng bằng bộ khuôn mới
> rồi đo xem một World tốn bao lâu thật. **Đừng chốt tỉ lệ trước khi có số đó.**

## Bối cảnh

Hiện chỉ có **1 nhiệm vụ chạy được** (Trái Đất, 8 bước); Mặt Trăng đang để "sắp ra mắt" và
6 hành tinh còn lại chưa có nhiệm vụ nào. Cần một cấu trúc nội dung để nhân rộng ra nhiều
hành tinh mà không phải viết tay từng màn một.

Đồng thời có ý muốn đổi luồng điều hướng: thay vì Trung Tâm Điều Hướng dẫn thẳng tới 6 khu
dùng chung, thì đi qua Bản Đồ Thiên Hà → chọn hành tinh → 6 card đổi nội dung theo hành tinh đó.

## Các phương án đã cân nhắc

### A. Cấu trúc World/Quest theo tỉ lệ — đề xuất bởi ChatGPT (31/07/2026)

- Mỗi World (Trái Đất, Mặt Trăng, Sao Hoả…): 5–7 chủ đề lớn
- Mỗi chủ đề: 4–6 nhiệm vụ ngắn, 2–5 phút mỗi nhiệm vụ
- Hoàn thành ~70% nhiệm vụ chính là mở được World tiếp theo
- 20–30% còn lại là Side Quest / Daily Mission / Achievement / Event
- Luồng mới: Trung tâm điều hướng → Bản đồ thiên hà → Chọn hành tinh → 6 card đổi theo hành tinh
- Kèm nhận định: "không cần sửa lại hết, chỉ cần sửa theo luồng mới"

**Ưu:** người chơi luôn thấy có tiến độ, sớm được sang hành tinh mới; người mê thiên văn vẫn còn
việc để hoàn thành 100%; có chỗ bổ sung nội dung theo mùa.

**Nhược (Claude đối chiếu mã nguồn ngày 31/07/2026):**
- 5–7 chủ đề × 4–6 nhiệm vụ = **20–42 nhiệm vụ mỗi World**. Với ≥9 World là **180–378 nhiệm vụ**.
- Cách xây hiện tại tốn ~410 dòng mã viết tay cho mỗi bước ⇒ *[Suy luận]* khoảng 70–80 nghìn dòng,
  gấp ~4 lần toàn bộ dự án hiện tại. Không phải "sửa nhẹ".
- Nội dung mới là nút thắt thật, không phải mã: hiện chỉ có 35 câu quiz và 1 file dữ liệu học.
- Daily Mission / Event bị nói nhẹ tay: backend chưa có khái niệm ngày, chưa có bảng sự kiện,
  chưa có đường phát hành nội dung theo mùa. Đây là phần backend đắt nhất trong đề xuất.
- Coi Mặt Trăng là một World thì phải **tách world-id khỏi planet-id** — `js/planets.js` chỉ có
  8 hành tinh, và trường `Planet` của nhiệm vụ được dùng để ghi "đã ghé hành tinh nào" cho hồ sơ
  và thành tích. Không tách thì hồ sơ đếm sai.
- Đề xuất bàn về *cấu trúc nội dung* nhưng bỏ qua *cách sản xuất nội dung*.

### B. Bộ khuôn nhiệm vụ chạy bằng dữ liệu, làm trước — đề xuất bởi Claude (31/07/2026)

Giữ nguyên tinh thần phương án A, nhưng đảo thứ tự thực hiện và hạ quy mô lần đầu:

1. Rút ra **6–8 khuôn tương tác dùng lại được** (trắc nghiệm · kéo-thả phân loại · sắp thứ tự mốc
   thời gian · quét điểm nóng · ghép cặp · đọc codex), chuyển 8 bước Trái Đất hiện có sang dạng
   dữ liệu — giao diện người dùng không đổi một pixel. Mỗi nhiệm vụ sau đó chỉ còn là một dòng JSON.
2. Nối luồng Bản đồ → sảnh hành tinh cho cả 9 World, World chưa có nội dung thì để "sắp ra mắt".
3. Làm đầy Mặt Trăng bằng bộ khuôn mới, **đo xem một World tốn bao lâu thật**.
4. Có số đo thật rồi mới quyết 5–7 chủ đề mỗi World có khả thi không, hay nên hạ xuống 3–4.
5. Daily Mission / Event để sau cùng — chỉ có ý nghĩa khi đã đủ nội dung để đáng quay lại.

Căn cứ: 8 bước Trái Đất hiện có, xét theo *loại tương tác*, thực ra đã là 4 khuôn lặp lại
(quét điểm nóng · sắp thứ tự · kéo-thả phân loại · thu thập thẻ). Chúng đã tồn tại, chỉ đang
bị viết dính chặt vào Trái Đất.

## Đã chọn

*(chưa chốt)*

## Đã bác — và vì sao

*(chưa có)*

## Số liệu đã kiểm bằng mã nguồn (31/07/2026)

| Số liệu | Giá trị | Nguồn |
|---|---|---|
| Nhiệm vụ chạy được | 1 (Trái Đất, 8 bước) | `AstroqSV/Services/Missions.cs` |
| Chi phí nhiệm vụ Trái Đất | ~3.300 dòng ⇒ ~410 dòng/bước | `mission-earth.html` 1.707 + `earth3d.js` 1.114 + `earth2d.js` 460 |
| Tổng dòng dự án (JS + HTML chính) | ~19.600 | đếm `js/*.js` + `*.html` |
| Câu hỏi quiz | 35 | `js/quiz-questions.js` |
| Kho dữ liệu học | 1 file codex Trái Đất + vài bài NASA | `learningdata/` |
| Hành tinh trong dữ liệu | 8 (không có Mặt Trăng) | `js/planets.js` |
| Card ở Trung Tâm Điều Hướng | đã đúng 6, 2 card chưa có trang | `dashboard.html` |
| Dữ liệu bản đồ 3D | đủ 8 hành tinh + Mặt Trời + Mặt Trăng, song ngữ | `explorer.html` |
| Cổng hoàn thành hiện tại | bắt xong **100%** số bước | `Missions.AllStepsDone` |

## Hệ quả

*(điền sau khi chốt)*

## Vòng 1 đã chạy (31/07/2026)

ChatGPT trả về **8 khuôn tương tác**, Gemini trả về **25 câu quiz Mặt Trăng**.
Claude đối chiếu mã nguồn: `docs/proposals/2026-07-31-review-vong-1.md`.

Ba phát hiện đổi cách nghĩ về quyết định này:
- **Sổ đăng ký bước đã tồn tại** (`mission-earth.html:801`) và **toạ độ đã là `lat`/`lon` độc lập
  engine** → việc chuyển sang dữ liệu rẻ hơn ước tính ban đầu.
- **Server không kiểm đáp án** — chỉ nhận `{mission, step, opId}` rồi tra bảng thưởng. Client đã
  là bên duy nhất quyết định bước nào xong, nên đưa luật hoàn thành vào JSON không làm yếu thêm gì.
- **Chưa có component linh vật dùng chung** (CSS lặp ở 5 file) và **chưa có lối chơi bằng bàn phím**
  — hai khoản nợ phải trả trong bất kỳ phương án nào.

## Ghi chú cho vòng bàn tiếp theo

Ba điểm nên đưa cho ChatGPT/Gemini bàn tiếp, vì chúng cần ý tưởng nhiều hơn cần mã:

1. **Bộ khuôn tương tác nào là đủ?** 6–8 khuôn nào phủ được nhiều nội dung thiên văn nhất
   mà vẫn khác nhau đủ để trẻ không thấy lặp?
2. **Nội dung cho Mặt Trăng** — nếu một World cần ~20 nhiệm vụ, hãy soạn thử danh sách chủ đề
   và nội dung cho Mặt Trăng, song ngữ, có dẫn nguồn NASA.
3. **Chống cảm giác lặp:** cùng một bộ khuôn dùng cho 9 hành tinh thì làm sao để hành tinh thứ 5
   vẫn thấy mới?
