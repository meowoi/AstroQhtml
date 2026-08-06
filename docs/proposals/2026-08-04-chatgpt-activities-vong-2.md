# ChatGPT — trả lời VÒNG 2 (Activities) + Claude đối chiếu mã nguồn

**Người viết bản gốc:** ChatGPT · **Ngày:** 2026-08-04
**Đề bài:** `2026-08-04-de-bai-activities-VONG-2.md` · **Rà vòng 1:** `2026-08-04-review-activities-tong-quat.md`

---

## Phần 1 — Bản trả lời của ChatGPT (nguyên văn, rút gọn định dạng)

Nó **chấp nhận toàn bộ phản biện** và mô tả nó *sẽ* viết lại thế nào:

- Không thiết kế cho 9 hành tinh nữa, chỉ cho Mặt Trăng để có số đo được.
- Không mặc định mọi thứ per-planet · không mặc định có engine chạy bằng dữ liệu ·
  không đề xuất Daily/Event vì máy chủ chưa có khái niệm ngày.
- Coi Phòng Nghiên Cứu là module duy nhất còn trống để đầu tư ý tưởng.

**Phạm vi nó chọn:**

| Nhóm | Giữ hay bỏ |
|---|---|
| Main Missions | Giữ |
| Side Missions | Giữ |
| Research Lab | **Giữ — trọng tâm** |
| Daily | Bỏ khỏi V1 |
| Events | Bỏ khỏi V1 |
| Knowledge · Training · Collections | **Giữ ở tầm toàn app** |

**Phòng Nghiên Cứu — đổi hẳn cách nghĩ:** không phải nơi đọc thêm kiến thức, mà là
*"phòng thí nghiệm để trẻ tự khám phá quy luật"*. Ví dụ: kéo Mặt Trăng xa/gần xem thuỷ
triều đổi · đổi độ nghiêng Trái Đất xem mùa · đổi khối lượng xem lực hấp dẫn · đổi khí
quyển xem nhiệt độ. **Không đúng/sai · không quiz · không điểm.**

Một phiên: ① Comet đặt câu hỏi → ② trẻ kéo một thanh / đổi một giá trị → ③ thế giới đổi
ngay → ④ Comet giải thích → ⑤ trẻ lưu "phát hiện" vào sổ tay.

Và: đếm nội dung bằng số trường chữ · số lời thoại · số dữ kiện cần tra nguồn · số trường
song ngữ, thay vì đếm bằng "số nhiệm vụ".

---

## Phần 2 — Claude đối chiếu mã nguồn (2026-08-04)

### Kết luận ngắn

**Hướng đúng, và ý tưởng Phòng Nghiên Cứu là thứ tốt nhất ba vòng vừa qua tạo ra.** Nó
lấp đúng một ô trống có thật, và — điều nó không biết — **nó khớp với hai thứ đã có sẵn
trong mã mà chưa ai dùng tới**.

Nhưng đây **chưa phải bản đề xuất**: nó là bản *"tôi sẽ viết gì nếu viết lại"*. Bốn mục
bắt buộc của đề bài đều chưa có (bảng ngân sách khuôn ở mục 0 · từng nhóm hoạt động ở
mục 3 · kịch bản từng nhịp ở mục 4 · bảng số trường chữ cho Mặt Trăng ở mục 5). Cần thêm
một lượt ngắn, không phải một vòng mới.

### A. Ba tin tốt nó chưa biết

**① Ô khuôn thứ năm đang trống, và Phòng Nghiên Cứu là ứng viên đầu tiên có lý cho nó.**
`docs/decisions/002` chốt 5 khuôn; khuôn thứ năm `orientation_align` **chưa từng được cài
đặt**, bước cần nó đã bỏ hẳn, và tài liệu ghi: *"giữ hay bỏ là câu của World thứ hai"*.
Lý lẽ sinh ra nó là *"thanh đo liên tục duy nhất của cả nhiệm vụ"* — tức **đầu vào liên
tục + phản hồi tức thì**, đúng bằng thứ "kéo một thanh, thế giới đổi ngay" cần.
*[Suy luận]* Đây không phải cùng một khuôn (`orientation_align` có mục tiêu và dung sai;
sandbox thì không có đúng/sai), nhưng chúng cần **cùng một hạ tầng còn thiếu**. Nên đề
nghị: ô thứ năm đổi thành **`parameter_sandbox`**, và câu hỏi treo của `002` coi như có
lời đáp.

**② Máy chủ đã sẵn sàng cho "không đúng/sai", không phải sửa gì.** `Services/Missions.cs`
thưởng theo **id bước**, không hề kiểm đáp án. Nghĩa là một phiên thí nghiệm không có
điều kiện thắng vẫn báo lên được y như mọi bước khác: trẻ lưu một phát hiện → client gửi
`{mission, step}` → server tra bảng. **Không cần hình dạng dữ liệu mới** — khác hẳn
Nhiệm vụ ngày.

**③ "Sổ tay phát hiện" đã tồn tại, đừng dựng cái thứ tư.** Mỗi bước nhiệm vụ có sẵn
trường `Step.Codex` — id mẫu dữ liệu ghi vào **Hồ sơ hành tinh** khi xong bước (Trái Đất
hiện có 8 mẫu). Một "phát hiện" ánh xạ thẳng vào đó. Dự án **đã có ba bộ sưu tập** (Hồ sơ
hành tinh · Sổ Tay Thuật Ngữ 15 mục · Kho Mẫu Vật 21 mục); thêm bộ thứ tư là thêm một
chỗ phải giải thích cho trẻ.

**④ Thanh trượt là khuôn DỄ làm bàn phím nhất — ngược hẳn kéo-thả.** `explorer.html` đã
có `<input type="range">` thật (thanh tốc độ mô phỏng, có `aria-label`): phím mũi tên
chạy sẵn, không phải viết một dòng nào. Mọi khuôn trước đều phải dựng đường bàn phím
riêng từ đầu.

### B. Bốn ví dụ thí nghiệm — chi phí lệch nhau rất xa

Đây là chỗ **cùng cái bẫy "chỉ thay dữ liệu"** đang lặp lại ở quy mô nhỏ hơn: bốn ví dụ
nghe như một khuôn với bốn bộ dữ liệu, nhưng đo trên mã thì chúng là **bốn thứ khác nhau**.

| Ví dụ | Mã hiện có | Chi phí *[Suy luận]* |
|---|---|---|
| **Độ nghiêng → mùa** | `tilt` **đã là tham số của từng thiên thể** trong cảnh 3D (Trái Đất `0.41` rad ≈ 23,5°), Mặt Trời là **nguồn sáng thật** (`PointLight`, đo được hai nửa chênh 106,5 điểm sáng) | **Nhỏ–vừa** — nối thanh trượt vào một giá trị đã có |
| **Mặt Trăng xa/gần** | Mặt Trăng **là vật thể quỹ đạo thật** (`orbitR:3.4`, `orbitSpeed:0.8`) → kéo xa/gần thì rẻ. **Nhưng phần thuỷ triều thì KHÔNG có gì** — phải vẽ mới | **Vừa** |
| **Khối lượng → hấp dẫn** | Không có mô phỏng lực nào. Quỹ đạo trong cảnh là **chuyển động theo kịch bản**, không phải tính từ khối lượng | **Lớn** |
| **Khí quyển → nhiệt độ** | Không có gì | **Lớn** |

⇒ Đề nghị: **chọn 2 thí nghiệm rẻ nhất cho phiên bản đầu** (độ nghiêng · khoảng cách
Mặt Trăng), rồi mới đo. Hai cái sau cần một bộ mô phỏng vật lý mà dự án chưa có.

### C. Rủi ro lớn nhất, và nó nằm đúng chỗ đề xuất tưởng là an toàn

*"Không đúng/sai"* nghe như **giảm** gánh nặng khoa học. Thực tế là **tăng**: một câu quiz
khẳng định đúng **một** điều và có **một** URL chống lưng; một thanh trượt khẳng định
**cả một dải** — mỗi vị trí trẻ kéo tới là một phát biểu về thế giới.

Dự án đã trả giá đúng loại lỗi này ba lần: thẻ *"Rừng Amazon"* rơi giữa đại dương · vành
khí quyển vẽ dày gấp đôi bán kính hành tinh (phải nói thật ra với trẻ vì sửa hình quá đắt)
· *"Nam Cực là châu lục cao nhất"* — một câu cỗ máy tìm kiếm tóm tắt từ trang NASA mà
trang đó **không** nói.

Với luật *"không con số nào không có nguồn"*, hệ quả cụ thể:

- **Đầu ra của sandbox phải ĐỊNH TÍNH** ("cao hơn · thấp hơn · lâu hơn"), **trừ vài mốc
  neo** có nguồn kiểm 200 (ví dụ: độ nghiêng thật 23,5° · khoảng cách Mặt Trăng thật).
- Mọi vị trí **không phải mốc neo** là *"chuyện gì sẽ xảy ra nếu…"* và **phải được nói
  thẳng ra như vậy** cho trẻ, không được hiện như một số đo.
- Cảnh 3D vốn đã phóng đại (vành khí quyển, `orbitR` của Mặt Trăng là **tỉ lệ nghệ thuật**,
  không phải tỉ lệ thật) — nên bản thân cảnh **không** dùng làm bằng chứng định lượng được.

### D. Ba ràng buộc phải nói trước khi nó viết bản thật

1. **Cảnh 3D là PHẦN THÊM, không phải phần bắt buộc** (`docs/decisions/005`). Nó kéo
   ~308 KB three.js từ tên miền ngoài và đã có đường lùi 12 giây cho mạng yếu. ⇒ Phòng
   Nghiên Cứu dựng trên cảnh 3D thì **không được mang bài học bắt buộc nào**, và phải
   nói được nó rơi về gì khi cảnh không dựng được.
2. **Ngược lại, đây là cách dùng AN TOÀN NHẤT của quả cầu 3D.** Có một luật cứng:
   *"quả cầu 3D không bao giờ được mang điều kiện thắng"* — sinh ra từ một bước cũ khiến
   trẻ **không thể hoàn thành** vì kéo là xoay camera chứ không xoay hành tinh, và **treo
   vĩnh viễn** khi tắt hoạt cảnh. Sandbox **không có điều kiện thắng** ⇒ thoả luật đó
   ngay từ thiết kế. Đây là điểm mạnh thật của ý tưởng, nên nói cho nó biết.
3. **`prefers-reduced-motion` phải hoàn thành được.** "Thế giới đổi ngay" không được đòi
   trẻ chờ một hoạt cảnh chạy xong.

### E. Một chỗ nên hỏi lại: Side Missions ở V1?

Nó giữ Side Missions trong V1. **Về mã thì rẻ** (cùng hình dạng "tính một lần" như bước
hiện có, không cần gì mới). **Về nội dung thì không rẻ** — và nội dung mới là nút thắt
đã bác cả vòng 1. Mặt Trăng V1 = Main + Research Lab đã là hai thứ chưa từng tồn tại.

*[Suy luận]* Nên hoãn Side Missions tới sau khi có số đo của Mặt Trăng. Nhưng đây là câu
của chủ dự án, không phải của tôi.

### F. Việc còn thiếu — cần một lượt ngắn, không phải một vòng mới

Nó chưa nộp: **mục 0** (bảng khuôn: nhóm nào dùng khuôn nào, tiêu mấy chỗ trên 2, khuôn
nào là mới) · **mục 3** (từng nhóm + lối chơi bàn phím) · **mục 4** (kịch bản từng nhịp —
nó mới cho 5 gạch đầu dòng, chưa phải kịch bản) · **mục 5** (bảng số trường chữ cho
Mặt Trăng). Câu nhắc để dán lại ở phần 3 dưới đây.

---

## Phần 3 — Câu nhắc dán tiếp cho ChatGPT (ngắn, dán sau bản nó vừa gửi)

```
Đúng hướng — chốt phạm vi như bạn đề nghị, và ý tưởng Phòng Nghiên Cứu được nhận.
Nhưng bản vừa rồi mới là "tôi sẽ viết gì", chưa phải bản đề xuất. Viết bản thật đi,
theo đúng khuôn trả lời đã gửi. Bốn tin từ mã nguồn để bạn viết cho đúng:

① Ô khuôn thứ NĂM đang trống thật (khuôn `orientation_align` chưa từng được cài đặt,
   bước cần nó đã bỏ). "Kéo một thanh, thế giới đổi ngay" được nhận vào ô đó. Bạn
   KHÔNG tiêu chỗ nào của 4 khuôn kia. Hãy đặt tên cho khuôn này.

② Máy chủ KHÔNG kiểm đáp án, nên "không đúng/sai" chạy được ngay, không phải sửa gì.
   Và "sổ tay phát hiện" ĐÃ TỒN TẠI: mỗi bước nhiệm vụ vốn đã trao một mẫu dữ liệu vào
   Hồ Sơ Hành Tinh. Hãy dùng lại nó — dự án đã có BA bộ sưu tập, đừng thêm bộ thứ tư.

③ BỐN VÍ DỤ THÍ NGHIỆM CỦA BẠN CÓ GIÁ RẤT KHÁC NHAU, không phải một khuôn bốn bộ dữ liệu:
   · độ nghiêng → mùa      : RẺ  — độ nghiêng đã là tham số có sẵn, Mặt Trời đã là đèn thật
   · Mặt Trăng xa/gần      : VỪA — Mặt Trăng đã là vật thể quỹ đạo thật, nhưng thuỷ triều
                                   thì chưa có gì, phải vẽ mới
   · khối lượng → hấp dẫn  : ĐẮT — không có mô phỏng lực nào; quỹ đạo hiện là chuyển động
                                   theo kịch bản, không tính từ khối lượng
   · khí quyển → nhiệt độ  : ĐẮT — không có gì
   ⇒ Chọn ĐÚNG 2 thí nghiệm cho phiên bản đầu và nói vì sao chọn hai cái đó.

④ ⚠️ RỦI RO LỚN NHẤT NẰM ĐÚNG CHỖ BẠN TƯỞNG LÀ AN TOÀN. "Không đúng/sai" không làm giảm
   gánh nặng khoa học, nó LÀM TĂNG: một câu quiz khẳng định MỘT điều và có MỘT nguồn
   chống lưng; một thanh trượt khẳng định CẢ MỘT DẢI — mỗi chỗ trẻ kéo tới là một phát
   biểu về thế giới. Dự án có luật "không con số nào không có nguồn". Vì vậy:
   · Đầu ra của thí nghiệm phải ĐỊNH TÍNH ("cao hơn · lâu hơn · lạnh hơn"), TRỪ vài
     mốc neo có nguồn thật (ví dụ độ nghiêng thật của Trái Đất).
   · Mọi vị trí không phải mốc neo phải được nói thẳng với trẻ là "nếu như…", không
     được hiện ra như một số đo.
   · Cảnh 3D vốn đã phóng đại tỉ lệ, nên chính cảnh đó không dùng làm bằng chứng
     định lượng được.
   Hãy viết lời thoại Comet theo đúng ràng buộc này, và đánh dấu [CẦN KIỂM: …] cho mọi
   mốc neo cần tra nguồn.

⑤ Ba ràng buộc kỹ thuật: cảnh 3D là PHẦN THÊM (mạng yếu có đường lùi) nên Phòng Nghiên
   Cứu KHÔNG được mang bài học bắt buộc nào · phải chơi được khi tắt hoạt cảnh · và tin
   tốt: quả cầu 3D có luật cứng "không bao giờ mang điều kiện thắng" — sandbox của bạn
   không có điều kiện thắng nên nó thoả luật đó ngay từ thiết kế, hãy giữ đúng như vậy.

Còn một câu hỏi: bạn giữ Side Missions ở V1. Về mã thì rẻ, về NỘI DUNG thì không —
mà nội dung là thứ đã bác vòng 1. Mặt Trăng V1 đã có hai thứ chưa từng tồn tại (Main +
Research Lab). Bạn vẫn giữ Side chứ? Trả lời có hoặc không, kèm một lý do.
```

---

## Ghi chú cho Claude ở vòng sau

- **Mục 0 và mục 5 là hai mục phải đọc trước.** Vòng này nó bỏ cả hai — nếu lượt sau vẫn
  thiếu thì vấn đề không phải đề bài, mà là nó đang trả lời ở tầm ý tưởng thay vì tầm đặc tả.
- Nếu bản thật dùng được: `docs/decisions/001` **đang mở** là chỗ ghi phạm vi đã chốt
  (Main + Side + Research Lab · ba khu giữ ở tầm toàn app · Daily/Event xuống sau cùng),
  và `docs/decisions/002` cần một dòng cập nhật cho **ô khuôn thứ năm**.
- Gom mọi `[CẦN KIỂM: …]` một lượt gửi Gemini — điểm giao duy nhất giữa hai lane.
  Với hướng sandbox thì **mốc neo** là thứ phải tra trước tiên (độ nghiêng thật, khoảng
  cách Mặt Trăng thật, và **cẩn thận với thuỷ triều** — mối liên hệ khoảng cách ↔ biên độ
  thuỷ triều rất dễ viết quá tay).
