# 010 — Sáu nhánh kiến thức cho Góc Khám Phá, và khối "Mở rộng"

- **Ngày:** 14/08/2026
- **Trạng thái:** **đang chạy** (LIFE SCIENCE 5/5 · *lập trình* 2/2 · MATHEMATICS 5/7 — mục 4b–4c; còn PHYSICS + ENGINEERING)
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

## 4b. Mắt xích đã giao thêm: LẬP TRÌNH (2/2) — 14/08/2026

Mắt xích còn thiếu của nhánh COMPUTING, và nó **dọn một món nợ đã ghi từ 25/07/2026**:
khoá quiz `loop` khai trong bank mà **không bài đọc nào dạy vòng lặp**, nên câu đó chưa
bao giờ được rút ra hỏi một cách tử tế.

| ord | id | Nguồn |
|---:|---|---|
| 4002 | `art-code-written-before-launch` | `jpl.nasa.gov/edu/resources/project/code-a-mars-landing/` |
| 4006 | `art-loop-you-can-see-on-mars` | `science.nasa.gov/resource/autonomous-hazard-checks-…-stereo/` |

Đặt `cat: "it"` chứ **không mở chủ đề thứ bảy** cho hai bài — CNTT đã là chỗ của chuỗi
*lập trình → dữ liệu* (`art-how-data-gets-home` 4010 trở đi), và `ord` 4002/4006 giữ đúng
thứ tự chuỗi: lập trình **trước** dữ liệu.

**Đo được sau khi làm: 0 khoá lập trình còn mồ côi** — cả 5 (`algorithm` · `sequence` ·
`condition` · `sensor` · `loop`) đều đã có bài đọc nhận.

### ⚠️ Ranh giới phải giữ: NASA mô tả một THAO TÁC LẶP LẠI, không nói "vòng lặp"

Trang NASA mô tả rover xoay **17,5 độ** rồi chụp ảnh, **lặp lại sau mỗi 1,2 mét**, và cái
hoa văn hình bước nhảy mà nó để lại trên vết bánh xe. Trang **không dùng chữ "vòng lặp"**
và không nói gì về cấu trúc lập trình.

⇒ **Thân bài** chỉ kể đúng thứ NASA quan sát được. **Phần `more`** mới giải thích khái niệm
vòng lặp, và nó **nói thẳng ra rằng chữ đó là của astroQ, không phải chữ NASA dùng trong
trang ấy**. Đặt một thuật ngữ lập trình vào miệng NASA là đúng lớp lỗi đã mắc ba lần
(Nam Cực *"châu lục cao nhất"* · ba tiêu chí IAU · CHNOPS).

### ⚠️ `jpl.nasa.gov` trả 403 với bot, 200 với trình duyệt thật

Đo ngày 14/08/2026: `curl` trần → **403** · Chromium **headless** → **403** · `curl` kèm
User-Agent thật → **200**. Đó là bộ lọc bot của CloudFront trước `jpl.nasa.gov`, **không
phải trang chết** — trẻ bấm bằng trình duyệt thật thì mở được. Ghi lại để lần sau ai đó
chạy một bộ kiểm URL tự động thì **không báo "nguồn chết" oan rồi đi thay một nguồn tốt**.

### ⚠️ Đã bác: dùng diễn đàn Scratch làm nguồn cho `loop`

Tìm nguồn cho vòng lặp thì phần lớn kết quả trên `scratch.mit.edu` là **bài diễn đàn người
dùng** (`/discuss/`) — nội dung do người dùng viết, không dùng làm nguồn cho một trang trẻ
em dù tên miền nằm trong allowlist. Trang tips chính thức thì quá mỏng (hai câu, và nói về
`repeat until`, trong khi câu quiz hỏi **lặp một số lần**). ⇒ Đi tìm một vòng lặp trong một
cỗ máy CÓ THẬT, và kết quả tốt hơn hẳn: một vòng lặp **nhìn thấy được trên đất Sao Hoả**.

⚠️ **`mit.edu` nằm trong `OKDOM` không có nghĩa là mọi URL dưới nó đều dùng được.**
Allowlist lọc *tên miền*, không lọc *chất lượng trang*. Người viết vẫn phải mở trang ra đọc.

---

## 4c. Nhánh đã giao: MATHEMATICS (5/7) — 14/08/2026

| ord | id | Mắt xích | Nguồn (kiểm 200 · 14/08/2026) |
|---:|---|---|---|
| 7010 | `art-units-lost-a-spacecraft` | Đo lường | `science.nasa.gov/mission/mars-climate-orbiter/` |
| 7020 | `art-light-year-is-a-distance` | Khoảng cách **+ tỉ lệ** | `science.nasa.gov/exoplanets/what-is-a-light-year/` |
| 7030 | `art-measuring-stars-with-angles` | Góc | `science.nasa.gov/asset/hubble/stellar-parallax/` |
| 7040 | `art-orbit-is-a-balance` | Quỹ đạo | `nasa.gov/…/what-is-an-orbit-grades-5-8/` |

Chủ đề mới `math` (+ icon `ruler`), tông vàng hổ phách — khác hẳn 6 tông đang có.

⚠️ **`OKDOM` VẪN CHƯA PHẢI NỚI.** Mục 3d dự đoán MATHEMATICS sẽ cần `nist.gov`; đo lại
thì **cả 4 bài đều có trang NASA tử tế**, trong đó bản *Grades 5-8* cho quỹ đạo đúng độ
tuổi. Dự đoán sai theo hướng tốt — và nó xác nhận luật *"nới đúng lúc thật sự cần"* là
đúng: nới sẵn theo dự đoán thì hôm nay đã mở thừa một tên miền.

### Mắt xích "tỉ lệ" nằm trong phần `more` của bài khoảng cách — có chủ đích

Chuỗi có 7 mắt xích nhưng **không bắt buộc 7 bài**. So sánh *8 phút ánh sáng* với
*4,25 năm ánh sáng* là bài học về tỉ lệ đẹp hơn bất cứ ví dụ bịa nào, **và nó dùng đúng
số liệu đã có nguồn ở thân bài**. Tách ra thành bài riêng là phải đi tìm một bộ số liệu
thứ hai cho cùng một ý. Đây chính là việc mà khối "Mở rộng" sinh ra để làm.

### ⚠️ Con số "170 km" — chỗ suýt bịa thứ tư, và là chỗ cám dỗ nhất

Bản tóm tắt của bộ tra cứu nêu *"quỹ đạo thấp hơn dự tính khoảng 170 km"* cho vụ Mars
Climate Orbiter. Mở trang ra thì **trang không có con số đó** (nó nằm ở báo cáo của ban
điều tra, một tài liệu khác). Bài viết vì thế **không dùng nó**, và chỉ nói đúng hai câu
trang nói. ⚠️ Lần này cám dỗ hơn ba lần trước vì con số nghe rất "chắc" và rất hợp bài.

### ⚠️ Ba chỗ khác giữ đúng ranh giới "lời NASA" vs "lời astroQ"

Cùng khuôn đã đặt ở `art-loop-you-can-see-on-mars`: phần suy luận của astroQ **nói thẳng
ra là của astroQ**, không để lẫn vào lời trang nguồn.
- phép chia ra *260.000 lần* và *260 km* (bài tỉ lệ)
- phép ví **ngón tay / nhắm một mắt** (bài thị sai) — trang NASA **không** có phép ví này
- lập luận *vì sao đường đi thành hình bầu dục* (bài quỹ đạo)

### Còn thiếu 2 mắt xích: **toạ độ** và **vận tốc**

`vận tốc` hiện đã có coverage **từ nhánh khác** (17.500 dặm/giờ ở `art-microgravity-is-falling`,
7 phút trễ tín hiệu ở `art-code-written-before-launch`) nên nó không phải lỗ hổng gấp;
`toạ độ` thì chưa có gì.

---

## 5. Còn lại — 2 nhánh + 3 mắt xích lẻ

Thứ tự đề nghị, theo mức trống và mức sẵn nguồn:

1. **PHYSICS (3/9)** — thiếu 6: lực · chuyển động · năng lượng · nhiệt · điện · chân không.
   ⚠️ **Đã thử tra nguồn 14/08 và HỎNG HAI LẦN**, ghi lại để lượt sau khỏi đi lại đường cũ:
   `grc.nasa.gov/www/k-12/rocket/newton3r.html` → **lỗi chứng chỉ SSL** (`unable to verify
   the first certificate`) · `nasa.gov/stem-content/the-law-of-action-and-reaction-…` →
   trang **chỉ là vỏ của một video**, không có chữ nào phát biểu định luật. ⇒ Lượt sau nên
   thử `www1.grc.nasa.gov/beginners-guide-to-aeronautics/` (đã thấy trong kết quả tìm kiếm)
   hoặc các bản PDF bài giảng của NASA, và **kiểm chứng chỉ + nội dung TRƯỚC khi viết**.
2. **ENGINEERING (2/6)** — thiếu 4: cơ cấu máy · điện · động cơ tên lửa · hỗ trợ sự sống.
3. **Ba mắt xích lẻ** — `toạ độ` + `vận tốc` (MATHEMATICS, mục 4c) và bài nhập môn thiên văn.
4. **Một mắt xích lẻ còn lại** — bài nhập môn thiên văn cho đầu chuỗi SPACE SCIENCE.
   ✅ Mắt xích *lập trình* **đã xong 14/08/2026** — xem mục 4b.

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
