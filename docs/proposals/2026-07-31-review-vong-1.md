# Claude đối chiếu mã nguồn — Vòng 1 (31/07/2026)

Đầu vào: đề xuất **8 khuôn tương tác** của ChatGPT và **25 câu quiz Mặt Trăng** của Gemini.

> ⚠️ Bản dán của Gemini **bị cắt ở câu 018**. Phần rà dưới đây chỉ áp cho 18/25 câu đọc được.

---

# A. ChatGPT — Bộ 8 khuôn tương tác

## Kết luận ngắn

Hướng **đúng**, chất lượng tốt, và nó **tuân thủ đúng lane** (không khẳng định dữ kiện khoa học
nào, dùng `[CẦN KIỂM: …]` xuyên suốt). Nó cũng tự hạ quy mô từ 20–42 nhiệm vụ/World xuống
**3–5 bước/World** — sát với thực tế hơn hẳn vòng trước.

Vấn đề chính: **8 khuôn là quá nhiều cho lần đầu**, và hai khuôn đắt nhất lại là hai khuôn ít
dùng lại được nhất.

## Trả lời 22 câu "tôi không chắc" của ChatGPT

| # | Câu hỏi | Trả lời từ mã nguồn |
|---|---|---|
| 1 | "Chín hành tinh" là chín World nào? | **8 hành tinh** (`js/planets.js`) **+ Mặt Trăng**. `explorer.html` có thêm Mặt Trời. Mặt Trăng **chưa có** trong `planets.js` → phải tách world-id khỏi planet-id |
| 2 | Có nạp được cấu hình từ JSON không? | **Chưa.** Toàn bộ nằm trong `mission-earth.html`, không có đường nạp dữ liệu ngoài |
| 3 | Có trình điều phối bước dùng chung không? | **CÓ MỘT PHẦN — tin tốt.** `mission-earth.html:801` đã là `const steps = { scan:{}, timeline:{}, … }` chạy bằng `STEP_IDS[]` + `stepIdx`. Khung điều phối đã tồn tại, chỉ là thân mỗi bước viết cứng và cả cụm nằm trong 1 file |
| 4 | Bước Trái Đất gửi gì lên backend? | **Chỉ `{mission, step, opId}`** (`js/progress.js:273`). Không gửi đáp án, không gửi điểm |
| 5 | Backend chấm đáp án hay chỉ nhận "xong bước"? | **Chỉ nhận "xong bước".** `Missions.cs` tra bảng thưởng theo id bước. **Server không hề kiểm đúng/sai** |
| 6 | Cần endpoint mới lấy cấu hình nhiệm vụ? | Không bắt buộc — phát hành file tĩnh cùng client là đủ, vì server không dùng tới nội dung |
| 7 | Đưa nội dung vào file tĩnh có hợp với cách server kiểm không? | Hợp, vì server **không kiểm gì cả** (xem #5) |
| 8 | Cấu trúc song ngữ hiện tại? | `{vi, en}` lồng trong từng trường — đúng như giả định. Xem `js/quiz-questions.js` |
| 9 | Comet/Byte có component hội thoại dùng chung? | **KHÔNG.** CSS linh vật đang lặp ở **5 file**: `codex.css`, `index.css`, `mission-earth.css`, `quiz.css`, `wiki.css`. Đây là vi phạm chính luật tái sử dụng của dự án — tách ra là việc đáng làm và đã quá hạn |
| 10 | Toạ độ asset là pixel, %, hay three.js? | **`lat`/`lon` địa lý thật** — không phụ thuộc engine. Đây là **tin tốt nhất trong cả lượt rà**: khuôn `signal_scan` dùng được cho cả cảnh 2D lẫn 3D mà không phải đổi dữ liệu. Đã có sẵn cờ `SCENE = 2d\|3d` |
| 11 | Có cơ chế version dữ liệu nhiệm vụ? | Chưa có |
| 12 | DynamoDB lưu theo bước, theo lượt thử, hay danh sách bước xong? | Lưu bản ghi `missions.<id>.<step>`; mỗi bước tính **một lần duy nhất** |
| 13 | Có cần lưu lựa chọn chi tiết của branching / resource? | Hiện **không có chỗ nào lưu**. Muốn lưu là phải thêm trường mới |
| 14 | Chống gửi trùng thế nào? | `opId` sinh **một lần lúc tạo việc**, server dedupe theo đó (`js/progress.js`) |
| 15 | Nhiệm vụ có trừ Thiên thạch tím như mini-game không? | **Không.** Nhiệm vụ là phần học; `Wallet.cs` không có mục phí nào cho nhiệm vụ |
| 16 | Có sẵn hệ accessibility để dùng lại? | **Gần như không.** `mission-earth.html` có 37 thuộc tính aria/role nhưng **chỉ 1 handler `keydown`**, mà là để mở khoá âm thanh. Lối chơi bằng bàn phím thay cho kéo-thả **chưa tồn tại ở đâu cả** |
| 17 | Bao nhiêu bước/World là hợp lý? | Chưa đo được. Phải làm xong World thứ hai mới có số thật |
| 18 | Chạy song song hai hệ nhiệm vụ trong giai đoạn chuyển tiếp? | Được. `missions.html` đã đọc danh mục theo `key`, thêm nhiệm vụ chạy bằng khuôn mới không đụng nhiệm vụ cũ |
| 19 | Trường JSON tối thiểu nào phải khớp API? | Chỉ **`missionId` + `stepId`**. Mọi trường khác là chuyện riêng của client |
| 20 | Xáo thứ tự thẻ ở client hay cần seed từ server? | Client. `quiz.html` đã trộn thứ tự đáp án ở client và không có vấn đề gì, vì server không chấm |
| 21 | Cấu trúc song ngữ hai file tách hay một? | Một đối tượng, hai trường `vi`/`en` |
| 22 | **`successRules` mô tả bằng dữ liệu có an toàn không?** | **Câu hỏi hay nhất, và câu trả lời làm nó thành không cần thiết.** Server không kiểm đáp án (#5), nên client **đã** là bên duy nhất quyết định bước nào xong. Đưa `successRules` vào JSON **không làm yếu thêm gì**, vì chưa từng có gì mạnh. Lưu ý thật: nội dung JSON tĩnh thì trẻ mở DevTools là đọc được đáp án — **nhưng hiện tại đáp án cũng nằm ngay trong JS**, nên đây không phải bước lùi |

## Chỗ cần sửa trong đề xuất

**1. 8 khuôn là sai phép tính.** Chính ChatGPT ước 36 bước cho 9 điểm đến. 36 ÷ 8 = **4,5 bước
mỗi khuôn**. Chi phí dựng một khuôn lớn hơn chi phí viết một dòng dữ liệu rất nhiều — dựng 8 cỗ
máy để chạy 36 lượt là lỗ. Với 36 bước thì **4–5 khuôn** là điểm hoà vốn hợp lý hơn.

**2. Hai khuôn nên bỏ khỏi đợt đầu:**
- `branching_field_log` — cây hội thoại phân nhánh cần công cụ soạn thảo riêng, và tốn lời thoại
  gấp nhiều lần các khuôn khác. Chính ChatGPT cũng xếp nó vào nhóm cắt đầu tiên.
- `mission_resource_balance` — `successRules` với toán tử `>=` là một bộ máy luật thu nhỏ.
  Phình phạm vi, mà #22 cho thấy nó cũng không mua được sự an toàn nào.

**3. `relationship_map`** (nối dây) là khuôn khó làm accessibility nhất, mà dự án hiện **không có
sẵn hạ tầng bàn phím nào** để dựa vào (#16). Để sau.

**4. Nhận định "nhiệm vụ Trái Đất không bắt buộc chuyển đổi ngay" — tôi không đồng ý.**
Không chuyển thì tồn tại song song hai hệ nhiệm vụ, và bộ khuôn không bao giờ bị thử lửa bằng
nội dung thật. Chuyển Trái Đất sang khuôn mới chính là **phép kiểm** xem bộ khuôn có đủ dùng
hay không. Nhờ #3 và #10 (đã có sổ đăng ký bước, toạ độ đã độc lập engine) nên việc này rẻ hơn
ChatGPT tưởng.

## Ước lượng

*[Suy luận]* — dựa trên quy mô mã hiện tại, không phải trên tốc độ làm việc thực tế:

| Việc | Quy mô |
|---|---|
| Tách trình điều phối + component linh vật dùng chung ra khỏi `mission-earth.html` | **Vừa** — cấu trúc đã có (#3), chủ yếu là di chuyển và làm sạch |
| Khuôn thứ nhất (kèm khung dữ liệu, i18n, reduced-motion, bàn phím) | **Vừa–lớn** — khuôn đầu gánh toàn bộ hạ tầng |
| Mỗi khuôn tiếp theo | **Nhỏ** — đã có hạ tầng |
| Chuyển 8 bước Trái Đất sang dữ liệu | **Vừa**, có rủi ro hồi quy — có `smoke_earth_done` 33/33 đỡ lưng |
| Lối chơi bằng bàn phím thay kéo-thả | **Vừa**, và là **việc hoàn toàn mới**, không tái sử dụng được gì (#16) |

---

# B. Gemini — 25 câu quiz Mặt Trăng

## Kết luận ngắn

**Nội dung viết tốt, nhưng phần được giao đúng sở trường thì hỏng: nguồn tham chiếu.**
Gemini được giao vai tra nguồn, và đây là chỗ nó sai nặng nhất.

Không dùng được nguyên trạng. Cần Gemini làm lại phần nguồn và phần rải đáp án.

## ❌ Lỗi 1 — Nguồn: 11/12 URL kiểm được đều hỏng

Tôi đã `curl` từng URL:

| URL Gemini đưa | Kết quả thật |
|---|---|
| `moon.nasa.gov/overview/in-depth/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/facts/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/inside-and-out/about-the-moon/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/about/exosphere/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/moon-in-motion/moon-phases/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/observe/craters/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/resources/180/footprint-on-the-moon/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/inside-and-out/what-is-inside/` | **301** → `science.nasa.gov/moon/` |
| `moon.nasa.gov/inside-and-out/history/` | **301** → `science.nasa.gov/moon/` |
| `www.nasa.gov/mission_pages/apollo/apollo11.html` | **301** → trang lịch sử Apollo 11 (còn sống) |
| `science.nasa.gov/eclipses/lunar-eclipses/` | **404** |
| `www.nasa.gov/topics/moon-to-mars/water-on-the-moon` | **404** |
| `scijinks.gov/tides/` | **không kết nối được** từ máy này (mã 000) — cần kiểm lại |
| `science.nasa.gov/moon/tidal-locking/` | ✅ **200** |
| `www.nasa.gov/specials/apollo50th/missions.html` | ✅ **200** |

**Toàn bộ tên miền `moon.nasa.gov` đã bị NASA gộp vào `science.nasa.gov`.** Mọi đường dẫn cụ thể
đều đổ về một trang chung — tức là **nguồn không còn trỏ tới dữ kiện mà nó chống lưng**.
Với một dự án có luật "viết một con số không có nguồn là bịa", đây là lỗi chặn.

Đáng chú ý về cách diễn đạt: Gemini viết *"tất cả các đường dẫn đều dẫn tới **domain** chính thức
của NASA"* — một khẳng định đúng nhưng **không phải điều được yêu cầu**. Đề bài yêu cầu URL đã
tra và xác nhận còn sống. Lần sau nên bắt nó ghi mã HTTP của từng URL.

### URL thay thế tôi đã kiểm trả 200

```
https://science.nasa.gov/moon/facts/
https://science.nasa.gov/moon/moon-phases/
https://science.nasa.gov/moon/tidal-locking/
https://science.nasa.gov/moon/formation/
https://science.nasa.gov/moon/top-moon-questions/
https://science.nasa.gov/eclipses/
https://www.nasa.gov/humans-in-space/artemis/
https://www.nasa.gov/specials/apollo50th/missions.html
https://oceanservice.noaa.gov/facts/moon-tide.html   ← thay cho scijinks (thuỷ triều)
```

## ❌ Lỗi 2 — Đáp án đúng dồn hết vào B

Đếm 18 câu đọc được (`correct` là chỉ số 0–3):

| Vị trí đáp án đúng | Số câu |
|---|---|
| A (0) | **1** |
| **B (1)** | **15** |
| C (2) | **2** |
| D (3) | **0** |

**83% câu có đáp án đúng ở vị trí B, và không câu nào có đáp án D.**

Đây không phải lỗi nhỏ. Luật rải đều A/B/C/D được ghi ngay đầu `js/quiz-questions.js`, kèm lý do:
*"trẻ học 'cứ chọn B' thì bài kiểm tra mất tác dụng"*. Bộ 35 câu hiện có rải 8/6/6/5, riêng 20 câu
thêm ngày 30/07 rải đúng 5/5/5/5. Nhập bộ này vào là phá vỡ tính chất đó.

*[Suy luận]* Nguyên nhân có thể là mẫu hình sinh văn bản: viết đáp án đúng ở vị trí thứ hai rồi
bổ sung các phương án nhiễu quanh nó. Cách chữa: yêu cầu Gemini **khai bảng phân bố A/B/C/D**
kèm bộ câu hỏi, giống cách file hiện tại đang làm.

## ❌ Lỗi 3 — Schema lệch với `AstroQQuestions`

| | Hiện có (`js/quiz-questions.js`) | Gemini đề xuất |
|---|---|---|
| Khoá chống hỏi trùng | `term` | **thiếu** — `pickRound()` dùng khoá này để mỗi lượt không hỏi trùng thuật ngữ |
| Chủ đề | `topic: {vi, en}` | `topic: "Moon - Basics"` — **chỉ một ngôn ngữ**, mà nó hiện trên badge cho trẻ đọc |
| Đáp án đúng | `a` — **một** chỉ số | `correct` **lặp trong cả `vi` và `en`** — hai bản có thể lệch nhau, và không có gì canh |
| Lời khi sai | `no: {vi, en}` | **thiếu** — Gemini chỉ có `hint` + `explanation` |
| Nguồn | `src: {name, url}` | `source_url` — thiếu tên hiển thị |

Không phải lỗi của Gemini (nó đã tự nêu ở mục 8 là không chắc schema), nhưng phải nắn lại trước
khi nhập. **Chỗ nguy hiểm nhất là `correct` lặp hai lần** — sửa một bản quên bản kia thì bản
tiếng Anh chấm sai mà không ai biết.

## ⚠️ Lỗi nhỏ

- **`quiz_moon_0010`** — thừa một số 0, lệch khỏi dãy `quiz_moon_0NN`.
- **Tự đoán độ tuổi "8–14"** dù briefing ghi rõ là chưa chốt và đừng giả định. Đây đúng là điều
  đã dặn trước. *(Ghi chú: `js/quiz-questions.js` có một chú thích nhắc "8–15" khi chọn nguồn
  NASA Space Place — vẫn không phải con số đã chốt trong tài liệu dự án.)*
- Câu 012 nêu **−246 °C ở hố cực** — con số này cần nguồn riêng, không nằm trong trang facts chung.

## ✅ Điểm tốt

- Nội dung khoa học **đúng** ở 18 câu đọc được; không phát hiện sai sự thật nào.
- Phần giải thích **giải thích được vì sao**, không chỉ khen — đúng yêu cầu.
- Phương án nhiễu hợp lý, là hiểu lầm thật, không phải đáp án ngớ ngẩn.
- Bản tiếng Anh đọc tự nhiên, không có dấu vết dịch máy.
- **Ở đúng lane** — không lấn sang thiết kế cơ chế chơi.
- Tự nêu đúng chỗ nó không chắc (schema). Tiếc là chỗ nó *tưởng* chắc mới là chỗ sai.

---

# C. Việc tiếp theo

**Gemini — làm lại, không phải làm mới:**
1. Thay toàn bộ URL `moon.nasa.gov`. **Ghi kèm mã HTTP đã kiểm cho từng URL.**
2. Rải lại đáp án cho gần đều A/B/C/D, **kèm bảng phân bố**.
3. Đổi sang schema `AstroQQuestions`; `a` chỉ khai **một lần**, ngoài `vi`/`en`.
4. Bổ sung `term` cho mỗi câu và `no` (lời khi trả lời sai).
5. Gửi lại đủ **25 câu** — lần trước bị cắt ở câu 18.

**ChatGPT — thu hẹp:**
1. Chọn **4 khuôn** cho đợt đầu, không phải 8. Bỏ `branching_field_log`,
   `mission_resource_balance`, `relationship_map` sang đợt sau.
2. Thiết kế lại có tính tới: **đã có sẵn** sổ đăng ký bước và toạ độ `lat`/`lon` độc lập engine;
   **chưa có** component linh vật dùng chung và lối chơi bằng bàn phím.
3. Với mỗi khuôn trong 4 khuôn, mô tả **lối chơi bằng bàn phím** thay cho kéo-thả — đây là việc
   mới hoàn toàn, không có gì để dựa.
4. Ánh xạ đủ 8 bước Trái Đất vào 4 khuôn đó. Bước nào không ánh xạ được thì nói thẳng.
