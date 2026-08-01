# Claude đối chiếu mã nguồn — Vòng 2 (31/07/2026)

Đầu vào: **bộ 4 khuôn tương tác** (ChatGPT) và **25 câu quiz Mặt Trăng bản sửa** (theo nhãn
người dùng ghi: cũng của ChatGPT — vòng này quiz đã ra khỏi lane của Gemini).

---

# 0. ĐÍNH CHÍNH — yêu cầu rải đều A/B/C/D của tôi là thừa

Tôi đã bảo sửa phân bố đáp án A/B/C/D. **Kiểm lại mã nguồn thì yêu cầu đó không còn tác dụng.**

`quiz.html:429` gọi `shuffleOptions()` bên trong `renderQuestion()` — **4 lựa chọn được trộn
lại mỗi lần hiển thị, cho mọi câu**. Chính chú thích ở `quiz.html:395` nói rõ lý do thêm cơ chế
này: *"trẻ chơi lại gặp câu cũ là nhớ được đáp án nằm ở ô D… đúng theo cách mà luật rải đều
A/B/C/D của bank sinh ra để tránh."*

Nghĩa là **thứ tự khai báo trong file không bao giờ tới được người chơi**. Tôi đọc luật ở phần
đầu `js/quiz-questions.js` (lệnh đếm phân bố) mà không kiểm xem trang có còn dùng nó theo cách
đó không. Luật đó có trước cơ chế trộn và giờ đã lỗi thời.

**Hệ quả:**
- Lỗi "15/18 câu đáp án ở B" mà tôi nêu ở vòng 1 **không tới được trẻ**. Vẫn nên sửa cho sạch,
  nhưng nó không phải lỗi chặn như tôi đã nói.
- Bản mới rải 7/6/6/6 — tôi đếm lại, đúng. Nhưng nó rải theo **chu kỳ lặp hoàn hảo
  A,B,C,D,A,B,C,D…** suốt 25 câu. Nếu KHÔNG có cơ chế trộn thì đây còn tệ hơn "luôn chọn B",
  vì đoán được tuyệt đối. Có trộn nên vô hại — nhưng nó cho thấy model đang tối ưu con số
  thống kê chứ không tối ưu điều con số đó phục vụ.
- **Việc nên làm:** cập nhật chú thích đầu `js/quiz-questions.js` cho khớp hành vi thật, để
  lần sau không ai (người hay model) lại đi đếm phân bố nữa.

Chỉ `quiz.html` đang dùng ngân hàng câu hỏi này (`library.html` chưa dùng dù chú thích nói là
để dùng chung), nên cơ chế trộn phủ 100% đường đi hiện tại.

---

# A. Bộ 25 câu quiz — bản sửa

## Đã sửa đúng

- Schema khớp: `term` · `topic{vi,en}` · `q` · `opts[{vi,en}]` · `a` đơn lẻ ngoài vi/en ·
  `ok` · `no` · `hint` · `src{name,url}`. **`a` không còn lặp hai ngôn ngữ** — lỗi nguy hiểm
  nhất của vòng 1 đã hết.
- `no` (lời khi trả lời sai) đã có, và **giải thích được vì sao lựa chọn kia sai**, không chỉ
  báo sai. Chất lượng tốt.
- Đủ 25 câu, id đánh số sạch, không còn `quiz_moon_0010`.
- Không phát hiện sai sự thật khoa học nào trong 25 câu. Các con số kiểm được đều đúng:
  1/6 trọng lực · 27,3 ngày · 384.400 km · 3,8 cm/năm · 12 phi hành gia · đường kính ~27%.
- Phương án nhiễu tốt hơn vòng 1 — dài hơn, hợp lý hơn, không còn kiểu loại trừ dễ dãi.

## ❌ Lỗi 1 — Sửa đúng câu chữ, trượt mất mục đích: nguồn không chứa dữ kiện

Bản mới dùng **đúng 9 URL tôi đã duyệt**, và tất cả đều trả 200. Nhưng nó **gán URL một cách
cơ học** thay vì tìm trang thật sự chứa dữ kiện.

Tôi tải hai trang được trích nhiều nhất rồi tìm từ khoá trong HTML nhận được:

**`science.nasa.gov/moon/top-moon-questions/`** — được trích cho **7 câu**:

| Từ khoá | Số lần xuất hiện | Câu trích nó |
|---|---|---|
| `far side` | 4 ✅ | mặt khuất |
| `crater` | 3 ✅ | hố va chạm |
| `moonquake` | 1 ⚠️ | động Mặt Trăng |
| `sound` | 1 ⚠️ | âm thanh không truyền |
| **`regolith`** | **0 ❌** | bụi regolith |
| **`water ice`** | **0 ❌** | băng nước ở cực |
| **`exosphere`** | **0 ❌** | ngoại quyển |

**`science.nasa.gov/moon/facts/`** — được trích cho **6 câu**:

| Từ khoá | Số lần | Câu trích nó |
|---|---|---|
| `384,400` | 1 ✅ | khoảng cách |
| `maria` | 1 ✅ | biển Mặt Trăng |
| `250` (°F) | 2 ✅ | nhiệt độ |
| **`27.3`** | **0 ❌** | chu kỳ quỹ đạo |
| **`fifth largest`** | **0 ❌** | vệ tinh lớn thứ 5 |
| **`quarter`** | **0 ❌** | tỉ lệ đường kính |

Cả hai trang đều trả về 290–306 KB HTML có nội dung thật (các từ khoá khác tìm thấy được),
nên việc thiếu từ khoá là có ý nghĩa, không phải do trang dựng bằng JavaScript.

*[Cần kiểm thêm]* Đây là phép tìm từ khoá trong HTML thô, không phải người đọc. Vài chỗ có thể
diễn đạt bằng từ khác (ví dụ "27.3" viết thành "27 days"). Nhưng ít nhất **6 câu đang trích một
trang không nói tới điều nó khẳng định**, và cần người mở ra xem.

**Đây là mẫu hình đáng ghi nhớ hơn cả lỗi:** tôi đưa 9 URL đã duyệt kèm yêu cầu "ghi mã HTTP",
và model tối ưu đúng hai thứ đó — mọi URL đều 200, mọi câu đều có nhãn `[HTTP 200]`. Cái nó bỏ
qua là điều đáng lẽ URL phải phục vụ: **nguồn phải chứa dữ kiện nó chống lưng.**
Lần sau phải yêu cầu *"trích dẫn câu/đoạn trên trang nguồn chứa dữ kiện này"*, chứ không phải
mã HTTP.

## ❌ Lỗi 2 — `[HTTP 200]` bị nhét vào chữ hiển thị cho trẻ

```
"src": { "name": "NASA Science — Moon Facts [HTTP 200]", ... }
```

`src.name` **hiện ở cuối popup giải thích cho trẻ đọc**. Mã HTTP là thứ để kiểm, không phải
thứ để hiển thị. Phải bỏ `[HTTP 200]` khỏi cả 25 câu trước khi nhập.

Lỗi do tôi ra đề không rõ — tôi bảo "ghi kèm mã HTTP" mà không nói ghi ở đâu.

## ❌ Lỗi 3 — 25 câu sinh ra 25 chủ đề mới

`topic` là **nhãn phân loại hiện trên badge** `[ CHỦ ĐỀ · CÂU n/m ]`. Ngân hàng hiện có
**20 chủ đề cho 35 câu** — mỗi chủ đề gom nhiều câu, đúng công dụng của một nhãn phân loại.

Bản mới đặt **một chủ đề riêng cho mỗi câu**: `MẶT TRĂNG HỌC`, `ÁNH SÁNG MẶT TRĂNG`,
`TRỌNG LỰC MẶT TRĂNG`, `QUỸ ĐẠO MẶT TRĂNG`, `KHÍ QUYỂN MẶT TRĂNG`, `BẢO TỒN VẾT TÍCH`… →
25 nhãn cho 25 câu, nhãn không còn gom được gì.

Ngân hàng **đã có sẵn** `VỆ TINH TỰ NHIÊN` / `NATURAL SATELLITE`. Phần lớn 25 câu này thuộc về
nó, hoặc cùng lắm chia 3–4 nhóm (ví dụ `MẶT TRĂNG`, `THÁM HIỂM MẶT TRĂNG`, `NGUYỆT THỰC`).

## ⚠️ Lỗi nhỏ

- **Trùng nội dung với câu đã có.** Ngân hàng đã có `term: "moon"` — *"Vệ tinh tự nhiên là gì?"*
  Câu mới `moon-satellite` — *"Mặt Trăng đóng vai trò gì đối với Trái Đất?"* — cùng đáp án,
  cùng ý. `pickRound()` dedupe theo `term` nên **hai câu này có thể cùng ra trong một lượt**.
  Bỏ câu mới hoặc đổi nó sang hỏi khía cạnh khác.
- **Mất phân tầng độ khó.** Vòng 1 yêu cầu 10 dễ / 10 vừa / 5 khó; bản mới bỏ trường
  `difficulty` vì mẫu schema tôi đưa không có nó — **lỗi của tôi**. Ngân hàng hiện cũng không
  có trường này. Cần quyết: thêm trường mới, hay bỏ yêu cầu phân tầng.
- **Định dạng JSON khoá có nháy** (`"term":`), còn ngân hàng là file JS khoá trần (`term:`).
  Chuyển đổi vặt, không phải lỗi.
- Bản dán **bị cắt ở bảng phân bố cuối**. Tôi tự đếm: đúng 7/6/6/6.
- Bộ này ra khỏi lane đã chia (quiz là phần của Gemini). Không sai nếu là chủ ý, nhưng vậy thì
  mất mất người kiểm chéo độc lập — mà lỗi 1 ở trên đúng là loại lỗi một bên kiểm chéo sẽ bắt.

---

# B. Bộ 4 khuôn tương tác

## Tốt

- **Chọn 4 khuôn hợp lý** và lý do vững: `profile_builder` hấp thụ phần lớn giá trị của
  `relationship_map` mà không phải dựng engine nối dây — đúng.
- **Phần bàn phím là phần mạnh nhất của cả đề xuất.** Cụ thể tới mức dùng được: thứ tự focus,
  phím nào làm gì, Byte đọc gì ở mỗi bước (*"Đang cầm thẻ số 3" · "Chèn trước thẻ Rotation"*).
  Đây đúng là thứ tôi yêu cầu và nó không né.
- **Ước lượng nội dung đã thu về đúng một World (Mặt Trăng)** như yêu cầu — có con số đo được.
- Vẫn không khẳng định dữ kiện khoa học nào, dùng `[CẦN KIỂM]`.
- Nhận định *"chỉ thay engine hiển thị, không đổi step id"* — khớp với mã nguồn.

## ❌ Không làm việc C — ánh xạ 8 bước Trái Đất

Đây là **deliverable quan trọng nhất của vòng 2**, vì nó quyết định 4 khuôn có đủ hay không.
Đề bài nói rõ: *"Bước nào không ánh xạ được thì NÓI THẲNG là không, đừng cố nhét."*

Nó không trả lời, mà chuyển `sun`, `core`, `eco` xuống mục 8 "cái tôi không chắc".

**Tôi đọc mã nguồn và ánh xạ hộ:**

| Bước | Cơ chế thật trong mã | Khuôn | Ghi chú |
|---|---|---|---|
| `scan` | chạm 3 điểm tín hiệu theo lat/lon | **signal_scan** | khớp hoàn toàn |
| `timeline` | sắp 4 mốc thời gian | **sequence_reconstruction** | khớp hoàn toàn |
| `sun` | lùi camera, `dimSun()`, trẻ **xoay cảnh** tìm Mặt Trời | **signal_scan (biến thể)** | ⚠️ mục tiêu **không nằm ở lat/lon nào** — nó ở ngoài hành tinh. Cần biến thể "mục tiêu trong cảnh" chứ không phải "điểm trên bề mặt" |
| `energy` | kéo-thả 3 nguồn vào 3 ô (`SLOTS`) | **profile_builder** | khớp |
| `rotation` | `world.setEarthDrag(true)` — **kéo xoay chính hành tinh** cho trạm phát sóng thẳng hàng vệ tinh | **❌ KHÔNG ánh xạ được** | xem dưới |
| `life` | thu 4 thẻ | **profile_builder** | khớp |
| `eco` | phân loại 7 thẻ NÊN / KHÔNG NÊN | **profile_builder** | khớp |
| `core` | `onFill(slot)` — lấp 3 ô ngọc | **profile_builder** | khớp, chỉ khác lớp vẽ |

**Kết quả: 6/8 khớp · 1 cần biến thể (`sun`) · 1 không khớp (`rotation`).**

### `rotation` là ca thật sự không nhét được

Nó là **thao tác liên tục trên vật thể 3D**: kéo cho tới khi hai điểm thẳng hàng. Không phải
chọn, không phải sắp thứ tự, không phải phân loại — ba thứ mà 4 khuôn kia làm.

Chú thích trong mã còn ghi lại một lỗi họ đã vấp đúng ở bước này: bản đầu để `OrbitControls`
xoay **camera**, nhìn thì giống nhau nhưng `earth.quaternion` không đổi nên **trẻ không thể
hoàn thành bước** — nó chỉ tự xong vì hành tinh tự quay, và ở chế độ giảm chuyển động thì
**treo vĩnh viễn**. Đây là lời cảnh báo cụ thể rằng khuôn dạng thao-tác-liên-tục khó hơn vẻ
ngoài, và **lối chơi bàn phím cho nó cũng chưa ai thiết kế**.

Ba đường đi, cần chọn một: (a) khuôn thứ 5 `orientation_align`, (b) viết `rotation` thành màn
riêng ngoài hệ khuôn, (c) đổi thiết kế bước này sang một khuôn đã có và chấp nhận mất cảm giác
"tự tay xoay hành tinh".

### Rủi ro tập trung

`profile_builder` gánh **4/8 bước**. Nó đúng là khuôn phủ rộng nhất, nhưng cũng nghĩa là một
nửa nhiệm vụ Trái Đất sẽ mang cùng một cảm giác thao tác. Chính ChatGPT đã cảnh báo điều này ở
mục 9 của nó. Cần quy tắc: **một nhiệm vụ không dùng cùng một khuôn quá 2 lần**, và nếu dùng 2
lần thì phải khác hẳn về cách trình bày.

## Trả lời mục 8 của ChatGPT

| Câu hỏi | Trả lời |
|---|---|
| `profile_builder` thay được `eco` không, hay cần biến thể phân loại? | **Thay được.** `eco` là phân loại 7 thẻ vào 2 nhóm — cùng cấu trúc thẻ→ô của `energy`, chỉ khác số ô |
| `sun` có cần nhiều hơn một `signal_scan`? | Cần **biến thể**, không cần khuôn mới. Mục tiêu ở ngoài hành tinh nên dữ liệu không thể là lat/lon |
| `core` có cần lớp hiển thị cắt ngang hành tinh? | Không. `core` đã là overlay DOM có 3 ô, `onFill(slot)` — đúng dạng thẻ→ô |
| Có bước nào trộn hai kiểu tương tác? | `sun` có trộn: xoay cảnh để tìm + chạm để chọn. Các bước khác thuần một kiểu |
| Dùng chung component focus cho cả 4 khuôn được không? | **Nên**, và bắt buộc phải làm chung — hiện chưa có gì cả, nên đây là cơ hội làm đúng một lần |
| Gom CSS Comet/Byte trước hay chuyển engine trước? | **Gom CSS linh vật trước.** Nó đang lặp ở 5 file; chuyển engine trước thì thành file thứ 6 |

---

# C. Việc tiếp theo

**Quiz — sửa nhỏ, không làm lại:**
1. Bỏ `[HTTP 200]` khỏi cả 25 `src.name`.
2. Gom 25 chủ đề về 3–4 nhóm, dùng lại `VỆ TINH TỰ NHIÊN` đã có.
3. Với 6 câu trích nguồn không chứa dữ kiện (27,3 ngày · vệ tinh lớn thứ 5 · tỉ lệ đường kính ·
   regolith · băng nước ở cực · ngoại quyển): tìm trang thật sự nói tới, **kèm trích một câu
   trên trang đó**.
4. Bỏ câu `moon-satellite` (trùng ý với `term:"moon"` đã có) hoặc đổi góc hỏi.
5. Quyết có thêm trường `difficulty` hay bỏ phân tầng.
6. **Không cần** động tới phân bố A/B/C/D — xem mục 0.

**Khuôn — một câu hỏi phải chốt trước khi code:**
Chọn đường nào cho `rotation` (a/b/c ở trên). Đây là quyết định của chủ dự án, không phải của
model, vì nó đánh đổi giữa chi phí và việc giữ lại một khoảnh khắc chơi đã có.

Sau đó thứ tự làm nên là: **gom component linh vật → tách trình điều phối → khuôn đầu tiên
(kèm hạ tầng focus dùng chung) → chuyển 8 bước Trái Đất → đo.**
