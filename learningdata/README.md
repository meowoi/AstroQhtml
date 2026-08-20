# AstroQ — Kho câu hỏi học tập (`learningdata/`)

Bộ dữ liệu câu hỏi trắc nghiệm (MCQ) song ngữ-thân thiện cho nền tảng **AstroQ**.
Mục tiêu: **300 câu / chủ đề × 5 chủ đề = 1.500 câu**, chia đều **12 Level × 25 câu**.

## Cấu trúc thư mục
```
learningdata/
├── ai/                 (Trí tuệ nhân tạo)
├── astronomy/          (Thiên văn học)
├── quantum_physics/    (Vật lý lượng tử)
├── programming/        (Lập trình & tư duy thuật toán)
└── it/                 (CNTT & Mạng)
     └── level_01.json ... level_12.json   (25 câu mỗi file)
```

## Quy ước `id`
`ASTRO_<TOPIC>_LV<xx>_Q<nnn>` — ví dụ `ASTRO_AI_LV01_Q001`.
Mã chủ đề: `AI`, `ASTRO`, `QP`, `PROG`, `IT`.

## Bản đồ Level → Lớp → Băng độ khó
| Level | Lớp (grade_target) | Băng | reward_purple_meteors |
|------:|--------------------|------|----------------------:|
| 1 | Lớp 1 · Tiểu học | Cơ bản / trực quan, mascot Byte & Comet | 10 |
| 2 | Lớp 2 · Tiểu học | Cơ bản | 14 |
| 3 | Lớp 3 · Tiểu học | Cơ bản | 17 |
| 4 | Lớp 4 · Tiểu học nâng cao | Cơ chế đơn giản, thuật ngữ | 21 |
| 5 | Lớp 5 · Tiểu học nâng cao | | 25 |
| 6 | Lớp 6 · THCS | | 28 |
| 7 | Lớp 7 · THCS | Ứng dụng, suy luận nhiều bước | 32 |
| 8 | Lớp 8 · THCS | | 35 |
| 9 | Lớp 9 · THCS | | 39 |
| 10 | Lớp 10 · THPT | Lý thuyết, định lượng, đọc/gỡ lỗi code | 43 |
| 11 | Lớp 11 · THPT | | 46 |
| 12 | Lớp 12 · Nâng cao | Cao cấp | 50 |

Công thức tham chiếu: `reward = round(10 + (level-1) × 40/11)`.

## Định dạng file
Mỗi `level_xx.json` là **một object bao (wrapper)** gồm metadata + mảng `questions`,
trong đó **mỗi phần tử `questions[]` tuân thủ đúng schema câu hỏi** đã yêu cầu
(xem `schema.json`). Bao ngoài giúp nạp file gọn hơn ở phía app.

```jsonc
{
  "topic": "Trí tuệ nhân tạo (AI)",
  "topic_en": "Artificial Intelligence (AI)",
  "topic_id": "ai",
  "level": 1,
  "grade_target": "Lớp 1 · Tiểu học",
  "grade_target_en": "Grade 1 · Primary",
  "reward_purple_meteors": 10,
  "count": 25,
  "questions": [ { /* ...schema câu hỏi... */ } ]
}
```

## Song ngữ — quy ước `*_en` (thêm 20/08/2026)

Tiếng Anh nằm **cùng file**, dưới dạng trường anh em có hậu tố `_en`; tiếng Việt
là trường gốc không hậu tố. Sáu chỗ có bản EN:

| Cấp | Trường VI | Trường EN |
|---|---|---|
| bao ngoài | `topic`, `grade_target` | `topic_en`, `grade_target_en` |
| câu hỏi | `topic`, `grade_target`, `mascot_dialog`, `question_text`, `explanation` | thêm `_en` |
| lựa chọn | `text` | `text_en` |

**Vì sao không tách file `en/` riêng, cũng không đổi sang dạng `{vi, en}`:**
`correct_option_id` phải ở **đúng một chỗ**. Tách file là hai nơi cùng giữ một
đáp án, và chúng sẽ lệch nhau vào ngày ai đó chạy `rebalance_answers.py` cho một
bên. Đổi sang `{vi, en}` thì phá `schema.json` hiện có và mọi công cụ đang đọc
`o["text"]`.

⚠️ **`text_en` PHẢI đi liền với `text` của CÙNG một lựa chọn.** Vị trí A/B/C/D
không có ý nghĩa cố định — `rebalance_answers.py` xáo chúng. Vì thế:

- Khi viết bản dịch, **khoá theo văn bản tiếng Việt**, đừng khoá theo chữ cái.
- `rebalance_answers.py` (đã sửa 20/08/2026) đổi chỗ **cả object lựa chọn** chứ
  không riêng `text`. Bản cũ chỉ đổi `text` — đo được **22/25 câu bị tách cặp
  VI↔EN** mà không có gì báo lỗi. Thêm trường ngôn ngữ mới thì công cụ tự đúng,
  không phải sửa lại.
- ⚠️ **Không có phép kiểm tự động nào bắt được ca hoán vị hai `text_en`.** Sau
  khi hoán vị, 4 chuỗi EN vẫn đủ và vẫn khác nhau — JSON hợp lệ, không còn dấu
  vết. `check_bilingual.py` canh được đầy đủ/trùng lặp/cấu trúc, **không** canh
  được nghĩa. Hàng rào thật là bản sửa `rebalance_answers.py` ở trên; rủi ro còn
  lại chỉ đến từ **sửa tay**, và chỉ người rà mới bắt được.

⚠️ Bản EN do máy dịch, **chưa có người bản ngữ rà**. Cùng mức cảnh báo với ghi
chú xác thực bên dưới: cần người rà trước khi phát hành.

⚠️ Thư mục này **không phải nguồn nội dung lúc chạy**. Câu hỏi trên web nằm ở
`js/quiz/*.js` (126 file, đã song ngữ đầy đủ theo dạng `{vi, en}`) và bài đọc ở
`js/article/*.js` (67 file). `learningdata/` là kho đang xây, để ngoài luồng chạy.

## ⚠️ Ghi chú về tính xác thực (đọc kỹ)
- Nội dung được viết ở mức **kiến thức chuẩn, phổ thông (textbook-level)** — chính xác theo hiểu biết khoa học/CNTT đã được công nhận rộng rãi.
- Trường `source_reference` cho biết **loại nguồn uy tín** nơi khái niệm đó là kiến thức chuẩn (NASA, MIT OpenCourseWare, CERN, Khan Academy, IEEE, Stanford CS…). **Đây KHÔNG phải trích dẫn được truy xuất trực tiếp** trong phiên tạo dữ liệu.
- **Khuyến nghị:** trước khi phát hành, hãy cho một chuyên gia/giáo viên rà soát từng file (đặc biệt Level 10–12 và Vật lý lượng tử) và đối chiếu nguồn gốc thật.

## Tiến độ (Progress)
| Chủ đề | Đã tạo | Bản EN | Còn lại |
|--------|--------|--------|---------|
| ai | L01, L02 (50/300) | ✅ đủ (20/08/2026) | L03–L12 |
| astronomy | — | — | L01–L12 |
| quantum_physics | — | — | L01–L12 |
| programming | — | — | L01–L12 |
| it | — | — | L01–L12 |

**File level mới sinh ra phải có luôn `*_en`** — xem mục "Song ngữ" ở trên. Thêm
tiếng Việt trước rồi bổ sung EN sau là tự tạo ra một đợt rà soát thứ hai.

**Cách tiếp tục:** nhắn `Tiếp tục: <chủ đề> Level <a>-<b>` (ví dụ `Tiếp tục: astronomy Level 1-3`),
mình sẽ sinh đúng các file `level_xx.json` tương ứng, kiểm tra trùng lặp trong từng batch.

## Công cụ đảm bảo chất lượng (`_tools/`)
- `rebalance_answers.py` — phân bố lại vị trí đáp án đúng đều khắp A/B/C/D (tất định theo id), tránh việc đáp án luôn ở một vị trí. **Đổi chỗ cả object lựa chọn nên mọi ngôn ngữ (`text`, `text_en`, …) đi cùng nhau.** Chạy sau khi sinh mỗi file:
  ```bash
  python _tools/rebalance_answers.py ai/level_01.json ai/level_02.json
  ```
  Mọi file trong batch mình bàn giao đều đã chạy qua bước này + kiểm tra: parse hợp lệ, không trùng id/câu hỏi, đủ 4 lựa chọn A–D, đáp án đúng khớp.
- **Lưu ý cho app:** nên **xáo trộn thứ tự lựa chọn khi hiển thị** (client-side shuffle) để tăng tính khách quan, dù dữ liệu đã cân bằng sẵn.
