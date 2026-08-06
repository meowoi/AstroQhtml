# ⛔ ĐỀ BÀI NÀY ĐÃ BỊ THAY — ĐỪNG DÁN

> **Thay bằng `2026-08-05-de-bai-gemini-VONG-2-theo-thuat-ngu.md`** (cùng ngày).
>
> Phần **quiz** ở đây sai hướng: nó yêu cầu 1.000 câu chia **5 chủ đề × 12 cấp độ**
> đổ vào `learningdata/`. Khảo sát Duolingo · Prodigy · Kahoot/Quizizz/Blooket ·
> IXL/Khan cho thấy **không app nào bắt trẻ chọn ô trong một ma trận 60 ô** — hệ
> thống chọn, hoặc người lớn chọn. Và đo lại thì **1.000 câu ≈ 1,78 MB**, không thể
> nạp bằng một thẻ `<script>`.
>
> Giữ file này làm **mục "đã bác — và vì sao"**: ba điều tuyệt đối ở mục 5 (bắt buộc
> `source_quote` · đừng rải đáp án A/B/C/D · `reward_purple_meteors` không phải tiền)
> vẫn đúng và đã được mang sang bản vòng 2.

---

# ĐỀ BÀI CHO Gemini — 1.000 câu quiz · 100 bài đọc

> Ngày 05/08/2026 · Vai: **Gemini = tra nguồn & kiểm chứng** (câu hỏi quiz · kho
> `learningdata/` · đúng–sai khoa học · URL còn sống · chất lượng bản EN).
> Dán **toàn bộ** file này vào Gemini. Nếu chưa dán `docs/BRIEFING.md` thì dán nó trước.

---

## 0. BỐN ĐIỀU PHẢI ĐỌC TRƯỚC, KHÔNG BỎ QUA

### ⛔ ① ĐỪNG RẢI ĐỀU ĐÁP ÁN A/B/C/D. Luật đó đã CHẾT.

Trang quiz có `shuffleOptions()` **trộn lại 4 lựa chọn mỗi lần hiện câu**, nên thứ tự
bạn khai báo **không bao giờ tới người chơi**. Đếm phân bố đáp án là đo một thứ không ai
nhìn thấy.

Đây không phải lời khuyên chung chung: dự án **đã tiêu trọn một vòng phối hợp** vì
chuyện này — một model được yêu cầu đi rải lại đáp án cho 25 câu, và toàn bộ đầu ra đó
vô ích. Cũng **đừng chạy** `learningdata/_tools/rebalance_answers.py`.

### ⛔ ② ĐỪNG GHI SỐ THƯỞNG NHƯ MỘT CON SỐ TIỀN.

`schema.json` hiện có trường `reward_purple_meteors` **bắt buộc** ở mỗi câu. Nhưng phần
thưởng do **server** quyết (`Services/Wallet.cs`) và client không có bản sao — một con số
tiền nằm trong dữ liệu nội dung là **1.000 chỗ nói sai về tiền**. Hãy điền nó như **băng
độ khó** theo bảng level của README (10 → 60), và hiểu rằng nó sẽ **không** được dùng làm
số tiền. Nếu thấy nên bỏ hẳn trường đó, nói ở mục "cái tôi không chắc".

### ⚠️ ③ HAI KHO CÂU HỎI KHÁC NHAU — ĐỪNG TRỘN. 1.000 câu đi vào kho THỨ HAI.

| | `js/quiz-questions.js` | `learningdata/` ← **đích của việc này** |
|---|---|---|
| Đang có | **35 câu / 15 thuật ngữ** | **50 câu** (`ai/level_01`, `ai/level_02`) |
| Vai trò | ngân hàng của Đấu Trường Kiến Thức; mỗi lượt rút **5 câu** | kho học tập theo chủ đề × level |
| Cấu trúc | `term · topic · q · opts[4] · a · ok · no · hint · src`, **đủ cả `vi` và `en`** | `schema.json`, xem mục 1 |
| Luật riêng | **đúng 2 câu mỗi thuật ngữ**, `pickRound` ưu tiên không trùng thuật ngữ | 12 level × 25 câu × 5 chủ đề |

⇒ **Đừng nhồi 1.000 câu vào `js/quiz-questions.js`.** Bank đó cố ý nhỏ.

### ⚠️ ④ KHO `learningdata/` HIỆN CHƯA CÓ TRANG NÀO ĐỌC.

Đã kiểm: **0 lời gọi `fetch` nào** trỏ vào các file `level_*.json`. 50 câu đang có nằm
đó **chưa từng tới tay một đứa trẻ nào**. Nói ra để bạn không tưởng nó đang chạy — và để
bạn biết việc nối nó vào giao diện là **việc của Claude**, không phải việc của bạn. Bạn
cứ viết đúng schema.

---

## 1. VIỆC 1 — 1.000 CÂU QUIZ

### Phân bổ đề nghị

Kế hoạch gốc (`learningdata/README.md`): **1.500 câu = 5 chủ đề × 300, chia 12 level ×
25 câu**. Đã có 50. Đề nghị 1.000 câu lần này:

| Chủ đề | Mã | Đã có | Thêm | Ghi chú |
|---|---|---:|---:|---|
| Thiên văn học | `ASTRO` | 0 | **300** | **ưu tiên số 1** — đây là nội dung app đang thật sự dùng |
| Trí tuệ nhân tạo | `AI` | 50 | **250** | lấp cho đủ 300 |
| Vật lý lượng tử | `QP` | 0 | **150** | ⚠️ khó nhất để giữ đúng ở tuổi này, xem mục 4 |
| Lập trình & tư duy thuật toán | `PROG` | 0 | **150** | |
| CNTT & Mạng | `IT` | 0 | **150** | |

Nếu bạn cho rằng phân bổ khác hợp lý hơn, **nói ở mục "cái tôi không chắc"** và cứ làm
theo đề nghị này trước.

### Schema — bám đúng, Claude sẽ kiểm bằng máy

Một file = một level. Meta bắt buộc: `topic · topic_id · level · grade_target ·
reward_purple_meteors · count · questions`.
Mỗi câu bắt buộc: `id · topic · level · grade_target · mascot_dialog · question_text ·
options[4] (mỗi cái có `id` A–D và `text`) · correct_option_id · explanation ·
source_reference · reward_purple_meteors`.

`id` theo khuôn `ASTRO_<MÃ>_LV<xx>_Q<nnn>` — ví dụ `ASTRO_ASTRO_LV03_Q014`.

### Bốn thứ phải thêm vào so với 50 câu đang có

50 câu cũ có `source_reference` là chuỗi kiểu `"Khan Academy – Intro to Computing"` —
**không phải URL, không kiểm chứng được**, và README đã ghi rõ chúng cần giáo viên rà
lại. Với 1.000 câu mới, hãy nâng chuẩn bằng **bốn trường phụ**:

```json
"source_url":   "https://science.nasa.gov/...",
"source_quote": "<TRÍCH NGUYÊN VĂN câu trên trang đó chứng minh đáp án>",
"source_checked": "2026-08-05",
"verified": true
```

⚠️⚠️ **`source_quote` là trường quan trọng nhất của cả việc này.** Dự án đã **hai lần**
dẫn một trang NASA cho một câu mà **trang đó không hề nói** — cả hai lần đều vì tin vào
đoạn tóm tắt của cỗ máy tìm kiếm thay vì mở trang ra đọc. Nếu bạn **không mở được** trang
để trích nguyên văn, thì:
- đặt `verified: false`,
- **và viết lại câu hỏi cho không cần con số đó nữa.**

⛔ Không bao giờ giữ một con số mà không trích được câu nguồn nói ra nó.

### Nguồn ưu tiên

NASA (`science.nasa.gov`; `spaceplace.nasa.gov` cho lứa nhỏ — đó là trang NASA viết cho
trẻ em) · ESA · NOAA (đại dương/khí quyển) · NPS (địa chất, thang thời gian) · USGS ·
MIT/Nature cho AI & lượng tử. **Mọi URL phải trả 200** ở ngày kiểm.

### Bốn ràng buộc nội dung

1. **Đúng lứa tuổi theo level.** Level 1 = lớp 1: câu ngắn, không thuật ngữ, có
   `mascot_dialog` của Byte hoặc Comet. Level 12 = lớp 12.
2. **`explanation` phải DẠY, không chỉ phán.** Trẻ chọn sai vẫn phải hiểu ra vì sao — đó
   là chỗ bài học thật sự nằm.
3. **Ba lựa chọn sai phải hợp lý.** Một câu có 3 đáp án nhảm là một câu không đo được gì.
   Tốt nhất: mỗi đáp án sai là một **hiểu lầm phổ biến có thật**.
4. **Không hai câu hỏi cùng một ý** trong cùng một chủ đề, kể cả khác level.

### Ba cái bẫy nội dung đã có thật trong dự án — đừng lặp lại

- ⛔ **"Nóng lạnh vì gần Mặt Trời hơn"** — quan niệm sai phổ biến nhất; nguyên nhân là
  **góc chiếu**. Nếu ra câu về khí hậu thì phải bác nó ra mặt.
- ⛔ **"Nam Cực là châu lục cao nhất"** — cỗ máy tìm kiếm tóm tắt đúng câu đó *từ một
  trang NASA*, nhưng đọc cả trang thì trang **không nói vậy**.
- ⛔ **Quy đổi đơn vị rồi coi kết quả là số của nguồn.** NASA ghi "tens of thousands of
  **miles** per hour" — đổi sang km/h rồi ghi như số của NASA là tự tạo ra một con số
  không có nguồn.

### ⚠️ Một khoảng trống: schema hiện CHỈ CÓ TIẾNG VIỆT

App song ngữ VI/EN, nhưng `schema.json` không có trường tiếng Anh nào. Đề nghị: viết
**tiếng Việt trước cho đủ 1.000 câu**, và ở mục cuối hãy **đề xuất cách thêm EN** (thêm
`question_text_en` cạnh, hay tách file `xx/en/level_01.json`?) — nói rõ cái nào bạn thấy
đỡ sai lệch hơn khi sửa nội dung về sau. Đừng tự đổi schema.

---

## 2. VIỆC 2 — 100 BÀI ĐỌC

### ⚠️ Vấn đề phải biết trước: hiện có HAI mảng bài viết TRÙNG NHAU

`learn.html` có 4 bài, `library.html` có 8 bài, **hai mảng `ARTICLES` riêng biệt và trùng
chủ đề** (Gaia · hố đen EHT · ngoại hành tinh) — sửa nội dung phải sửa hai nơi. 100 bài
đổ vào đó là nhân đôi đúng vấn đề này.

⇒ Hãy viết ra **một kho JSON duy nhất**, không viết theo hình dạng của hai mảng cũ.
Việc gộp hai mảng cũ vào kho đó là việc của Claude.

### Mỗi bài gồm

```json
{
  "id": "art-<slug>",
  "topic": "astronomy | ai | quantum | programming | it | earth",
  "age": "8-10 | 11-13 | 14-15",
  "title_vi": "...", "title_en": "...",
  "answer_vi": "<40–60 TỪ trả lời thẳng tiêu đề>", "answer_en": "...",
  "body_vi": "<3–6 đoạn, chữ cho trẻ>", "body_en": "...",
  "image_url": "<ảnh NASA/ESA, PHẢI trả 200>",
  "image_credit": "NASA/JPL-Caltech",
  "source_url": "...", "source_quote": "...", "source_checked": "2026-08-05",
  "terms": ["<khoá thuật ngữ liên quan trong Sổ Tay, nếu có>"],
  "verified": true
}
```

### Bốn ràng buộc

1. **`answer_vi` đúng 40–60 từ.** Đây là khuôn *Direct Answer* mà 20 bài wiki của dự án
   đang dùng và có phép kiểm tự động đếm — dài hay ngắn hơn là hỏng phép kiểm.
2. ⛔ **Đừng viết "đọc xong nhận Thiên thạch tím".** Đọc bài **không còn thưởng tt** từ
   30/07/2026 (`Wallet.MaxPerLesson = 0`); nó chỉ ghi vào hồ sơ. Hứa sai là lỗi đã phải
   đi sửa một lần.
3. **Ảnh phải là ảnh thật, có credit, URL trả 200.** Bài không có ảnh chắc chắn thì để
   `image_url: null` — thà không có ảnh còn hơn một ô ảnh vỡ trước mặt trẻ.
4. ⛔ **Không sao chép nguyên văn tài liệu NASA/ESA.** Viết lại cho trẻ em bằng lời của
   mình; `source_quote` là chỗ duy nhất được trích nguyên văn, và nó để **kiểm chứng**,
   không để đăng.

### Phân bổ đề nghị

Thiên văn 40 · Trái Đất & khí hậu 20 · AI 15 · Lập trình 10 · Lượng tử 8 · CNTT 7.

---

## 3. CÁCH GIAO NỘP

Việc này lớn, **đừng cố nhét vào một câu trả lời**. Chia thành từng đợt và **nộp từng
file JSON hoàn chỉnh**, để Claude chạy được máy kiểm ngay từ đợt đầu:

1. **Đợt 1 (làm trước, chờ phản hồi rồi mới đi tiếp):** `astronomy/level_01.json` (25 câu)
   + **5 bài đọc** thiên văn. Đây là mẫu chuẩn — đúng rồi mới nhân lên.
2. Đợt 2+: từng level một, hoặc từng nhóm 25 câu.

Sau mỗi đợt, ghi kèm **3 dòng ngắn**: số câu · số URL đã mở đọc thật · số câu để
`verified: false` và vì sao.

---

## 4. KHUÔN TRẢ LỜI BẮT BUỘC

**Mục 0 — Cái tôi ĐÃ MỞ ĐỌC và cái tôi KHÔNG mở được.** Bao nhiêu URL bạn thật sự truy
cập được, bao nhiêu chỉ dựa vào trí nhớ. Đây là mục Claude tin cậy nhất — nói thật thì
phần còn lại dùng được.

**Mục 1 — Đợt 1**: `astronomy/level_01.json` + 5 bài đọc, đúng schema, dán JSON đầy đủ.

**Mục 2 — Kế hoạch cho 975 câu còn lại**: chủ đề nào ở level nào, và bạn định lấy nguồn
từ đâu cho từng chủ đề.

**Mục 3 — Đề xuất cách thêm tiếng Anh** vào schema (xem mục 1).

**Mục 4 — Giả định & cái tôi KHÔNG chắc.** Bắt buộc. Ghi thẳng: chủ đề nào bạn thấy
**không đủ nguồn uy tín cho lứa tuổi này** (nghi ngờ nhất: vật lý lượng tử ở level thấp —
dự án đã cố ý **chưa phát hành** 4 thuật ngữ AI/Lượng tử vì thiếu nguồn) · chỗ nào cần
giáo viên rà trước khi phát hành · con số nào bạn không trích được câu nguồn.

---

## 5. BA ĐIỀU TUYỆT ĐỐI

1. ⛔ **Không con số nào không có `source_quote`.** Không trích được thì viết lại câu hỏi.
2. ⛔ **Không rải đều đáp án A/B/C/D** — vô ích, xem mục 0①.
3. ⛔ **Không coi `reward_purple_meteors` là tiền** — server quyết, xem mục 0②.
