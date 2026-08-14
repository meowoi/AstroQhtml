# 010 — Sáu nhánh kiến thức cho Góc Khám Phá, và khối "Mở rộng"

- **Ngày:** 14/08/2026
- **Trạng thái:** **đang chạy** (nhánh 1/6 đã giao; 5 nhánh còn lại chờ)
- **Người quyết:** chủ dự án
- **Đối chiếu mã nguồn:** Claude

---

## 1. Yêu cầu

Thêm nội dung cho sáu nhánh kiến thức vào Góc Khám Phá (`library.html`), giọng viết
cho trẻ 8–15, được phép mở rộng nguồn ngoài NASA/MIT, và **nếu cần phân cấp độ nhận
thức thì bổ sung ngay tại bài đọc bằng một phần "Mở rộng"**.

Sáu chuỗi chủ đề: SPACE SCIENCE · PHYSICS · LIFE SCIENCE · ENGINEERING · COMPUTING ·
MATHEMATICS.

---

## 2. Số đo trước khi làm — khoảng trống THẬT là 25 bài, không phải 39

Sáu chuỗi cộng lại có **39 mắt xích**. Nhưng ánh xạ 49 bài đang có vào chúng thì:

| Nhánh | Đã phủ | Thiếu | Ghi chú |
|---|---:|---:|---|
| SPACE SCIENCE | 15/6 | ~1 | **dư** — chỉ thiếu bài nhập môn "quan sát bầu trời" |
| COMPUTING | 22/6 | ~2 | **dư** — thiếu mắt xích **lập trình** |
| PHYSICS | 3/9 | 6 | có trọng lực · ánh sáng · lá chắn bức xạ |
| ENGINEERING | 2/6 | 4 | có cảm biến · cánh tay robot |
| **LIFE SCIENCE** | **0/5** | **5** | ❌ trống hoàn toàn |
| **MATHEMATICS** | **0/7** | **7** | ❌ trống hoàn toàn |

⇒ **~25 bài mới.** Hai nhánh đã dư sẵn vì kho hiện tại lệch hẳn về thiên văn + AI/robot
(19 astronomy · 11 robot · 11 ai · 5 it · 3 quantum).

⚠️ Con số này là lý do KHÔNG nhận đề bài "39 bài" theo mệnh giá. Cùng bài học đã ghi ở
`009` và ở phụ lục của đề xuất 500 khái niệm: **đếm lại trước khi nhận một con số quy mô.**

---

## 3. Đã chốt

### 3a. Phần "Mở rộng" TÁI DÙNG `js/depth.js`, không dựng cơ chế phân cấp thứ hai

Dự án **đã có** hai bậc độ sâu từ 12/08/2026 (`junior` 8–10 · `senior` 11+), do trẻ tự
khai lúc cấp thẻ ID, lưu ở hồ sơ server. Trước hôm nay nó chỉ có **một** người dùng
(`lab.html`). Khối "Mở rộng" là người dùng **thứ hai** — và nó thừa hưởng nguyên luật đã
chốt:

- `senior` → phần Mở rộng **mở sẵn**
- `junior` → **gấp lại**
- ⚠️ **nút bấm LUÔN CÓ Ở CẢ HAI BẬC.** Bậc chỉ quyết cái *mặc định*, không khoá gì. Máy
  đoán sai tuổi thì trẻ sửa bằng một cú bấm; ẩn hẳn nút ở một bậc là máy chốt hộ trẻ.
- Chưa khai bậc → tự lùi về `junior` (fail-safe: thà nói đơn giản với một đứa 15 tuổi
  hơn nói khó với một đứa 8 tuổi).

**Đã bác:** dựng thang cấp độ riêng cho bài đọc (1–3 sao, hay "cơ bản/nâng cao"). Hai hệ
phân cấp song song cho cùng một đứa trẻ thì sớm muộn nói hai điều khác nhau — đúng lỗi
"hai nguồn sự thật" mà dự án đã trả giá nhiều lần.

### 3b. `js/more-box.js` là MODULE DÙNG CHUNG, không phải 25 dòng chép hai lần

Có **hai** trình đọc bài (`library.html` và `learn.html`). Khối Mở rộng mang bốn thứ:
bậc độ sâu · trạng thái gấp/mở · nhãn song ngữ · vẽ lại khi đổi ngôn ngữ. Chép hai bản là
đúng loại sẽ trôi khỏi nhau — hai trang đó **đã có tiền lệ xấu**: trước 09/08/2026 chúng
giữ hai mảng `ARTICLES` riêng, trùng chủ đề.

CSS đặt ở **`css/page-shell.css`** vì cả hai trang đều nạp nó. Module tự mang chuỗi
song ngữ của mình, đúng khuôn `js/weeklog.js` và `js/daily.js`.

### 3c. Chủ đề mới `life` — thêm một `cat` là phải sửa ĐỦ 4 CHỖ + 1 icon

`cats` (library.html) · `CAT_ICON` · khoá i18n `cat_life` ở **cả** `vi` và `en` ·
rule `.cat--life` (css/library.css) · và icon `leaf` trong `js/icons.js`. Thiếu một chỗ
là chip hiện khoá thô hoặc không có màu. `smoke_library_featured` có phép kiểm
*"mọi `cat` trong dữ liệu phải có chip ở sidebar"* nên chỗ thiếu bị bắt ngay.

### 3d. ⛔ **CHƯA nới allowlist nguồn** — và đó là một quyết định, không phải bỏ sót

Chủ dự án cho phép mở rộng ngoài NASA/MIT. Nhưng nhánh LIFE SCIENCE cần **0 nguồn
ngoài NASA** — cả 5 bài đều có trang NASA tử tế, trong đó có bản *viết cho lớp 5–8*
đúng độ tuổi. Nên `OKDOM` giữ nguyên.

Luật từ nay: **nới allowlist đúng lúc một nhánh THẬT SỰ cần, và nới đúng tên miền đó.**
Chính `smoke_library_featured.py` đã ghi: *"Nới rộng OKDOM thì mọi trang thương mại đều
lọt"*, và dự án đã một lần phải gỡ `ibm.com/quantum` khỏi kho bài đọc.

⚠️ Nhánh sẽ cần nới trước nhất là **MATHEMATICS** (NASA có `spacemath.gsfc.nasa.gov`,
nhưng đo lường/chuẩn đơn vị thì `nist.gov` mới đúng địa chỉ) và **PHYSICS** (`energy.gov`).
Khi tới đó thì mở một mục riêng ở đây, đừng nới lặng lẽ.

---

## 4. Nhánh đã giao: LIFE SCIENCE (5/5)

| ord | id | Mắt xích | Nguồn (kiểm 200 ngày 14/08/2026) |
|---:|---|---|---|
| 6010 | `art-body-in-space-changes` | Cơ thể người | `nasa.gov/hrp/bodyinspace/` |
| 6020 | `art-microgravity-is-falling` | Vi trọng lực | `nasa.gov/…/what-is-microgravity-grades-5-8/` |
| 6030 | `art-what-life-needs` | Sự sống | `science.nasa.gov/astrobiology/…/what-does-life-need-for-survival/` |
| 6040 | `art-growing-plants-in-space` | Môi trường sống | `nasa.gov/…/growing-plants-in-space/` |
| 6050 | `art-space-biology-questions` | Sinh học không gian | `science.nasa.gov/biological-physical/programs/space-biology/` |

Cả 5 bài **đều có phần `more`** — nhánh đầu tiên của dự án làm vậy.

### ⚠️ Ba chỗ suýt bịa, ghi lại để vòng sau không mắc

1. **CHNOPS.** Bộ tra cứu tóm tắt ra dãy nguyên tố C-H-N-O-P-S cho trang *What does life
   need for survival?*. Mở trang ra hỏi thẳng thì **trang KHÔNG có chữ đó**. Bài viết vì
   thế chỉ nói đúng ba điều trang nói: **nước · nguồn năng lượng · khí quyển bảo vệ**.
   Đây là **lần thứ ba** dự án suýt mắc đúng lớp lỗi này (Nam Cực *"châu lục cao nhất"* ·
   ba tiêu chí IAU).
2. **Đơn vị.** NASA chỉ cho `17,500 miles per hour`. Bài viết *"17.500 dặm một giờ"* và
   **nói rõ đó là đơn vị NASA dùng** — không tự quy sang km/h rồi ghi như con số của NASA.
   Cùng luật đã áp cho Canadarm2 (foot/pound) và tốc độ sao băng.
3. **"Xương mất 1%/tháng".** Trang nói **xương CHỊU LỰC** và là con số **trung bình**. Bỏ
   hai chữ đó là biến một phép đo thành một lời khẳng định rộng hơn trang nói.

### ⚠️ Một URL đoán theo mẫu trả 404

`spaceplace.nasa.gov/microgravity/en/` — đúng bài học đã ghi 09/08/2026: **đường dẫn NASA
không suy được theo mẫu, phải tìm rồi mở.** Tìm lại ra bản *Grades 5-8*, còn tốt hơn.

---

## 5. Còn lại — 4 nhánh, ~20 bài

Thứ tự đề nghị, theo mức trống và mức sẵn nguồn:

1. **MATHEMATICS (0/7)** — trống hoàn toàn. Cần nới allowlist trước (xem 3d).
2. **PHYSICS (3/9)** — thiếu 6: lực · chuyển động · năng lượng · nhiệt · điện · chân không.
3. **ENGINEERING (2/6)** — thiếu 4: cơ cấu máy · điện · động cơ tên lửa · hỗ trợ sự sống.
4. **Hai mắt xích lẻ** — bài nhập môn thiên văn, và **lập trình** (nhánh COMPUTING).
   ⚠️ Mắt xích *lập trình* đáng làm sớm vì nó **dọn một món nợ đã ghi**: khoá quiz `loop`
   khai từ 25/07/2026 tới nay **vẫn chưa có bài đọc nào dạy vòng lặp**.

⚠️ **Đừng viết cả 20 bài trong một lượt.** Tỉ lệ hỏng của việc dẫn nguồn ở quy mô lớn là
thứ đã đo được (Đợt 1 của Gemini: **13/40 câu** trượt). Làm theo nhánh, mỗi nhánh mở
nguồn thật rồi mới viết — đúng cách nhánh LIFE SCIENCE vừa làm.

---

## 6. Đã bác — và vì sao

- **Dựng thang cấp độ riêng cho bài đọc.** Đã có `js/depth.js` từ 12/08/2026; xem mục 3a.
- **Nới `OKDOM` sẵn cho cả 6 nhánh.** Nới trước khi cần là mở cửa cho trang thương mại;
  xem 3d.
- **Nhận con số "39 bài" theo mệnh giá.** Đếm lại ra 25; xem mục 2.
- **Chép khối Mở rộng vào cả hai trình đọc.** Xem 3b.
- **Gắn `more` vào mục lục (`js/articles-index.js`).** Nó là phần NẶNG, phải nằm lại ở
  `js/article/<id>.js` và tải khi cần — mục lục hiện 20,9 KB thô cho 54 bài, nhét `more`
  vào là hoàn tác đúng lượt chia file ngày 09/08/2026.

---

## 7. Kiểm thử

- `scratchpad/smoke_more_box.py` **MỚI, 18/0** — mở bài thật trên Chromium: junior gấp
  lại · senior mở sẵn · **nút có ở CẢ HAI bậc** · bấm mở/gấp thật (đo `computedStyle`,
  không đọc thuộc tính) · bài không có `more` thì ẩn hẳn · EN dịch nhãn · `learn.html`
  cũng có khối đó.
- **Phép thử phá hoại:** bỏ `.mb-body[hidden]{display:none}` → **hỏng đúng 2 phép kiểm**.
  Đó là cái bẫy `[hidden]` dự án đã trả giá **chín lần**.
- `smoke_library_featured` **62/0** (mục [8] nay validate cả `more`: đủ song ngữ · cùng
  số đoạn · không lọt thẻ HTML) · `check_pages` **1256/0** · `smoke_lang_switch` 256/0 ·
  `smoke_codex` 40/0 · `smoke_vault` 83/0 · `audit_viewports` (library+learn) 38/0.
