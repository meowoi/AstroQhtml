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
  "topic_id": "ai",
  "level": 1,
  "grade_target": "Lớp 1 · Tiểu học",
  "reward_purple_meteors": 10,
  "count": 25,
  "questions": [ { /* ...schema câu hỏi... */ } ]
}
```

## ⚠️ Ghi chú về tính xác thực (đọc kỹ)
- Nội dung được viết ở mức **kiến thức chuẩn, phổ thông (textbook-level)** — chính xác theo hiểu biết khoa học/CNTT đã được công nhận rộng rãi.
- Trường `source_reference` cho biết **loại nguồn uy tín** nơi khái niệm đó là kiến thức chuẩn (NASA, MIT OpenCourseWare, CERN, Khan Academy, IEEE, Stanford CS…). **Đây KHÔNG phải trích dẫn được truy xuất trực tiếp** trong phiên tạo dữ liệu.
- **Khuyến nghị:** trước khi phát hành, hãy cho một chuyên gia/giáo viên rà soát từng file (đặc biệt Level 10–12 và Vật lý lượng tử) và đối chiếu nguồn gốc thật.

## Tiến độ (Progress)
| Chủ đề | Đã tạo | Còn lại |
|--------|--------|---------|
| ai | L01, L02 (50/300) | L03–L12 |
| astronomy | — | L01–L12 |
| quantum_physics | — | L01–L12 |
| programming | — | L01–L12 |
| it | — | L01–L12 |

**Cách tiếp tục:** nhắn `Tiếp tục: <chủ đề> Level <a>-<b>` (ví dụ `Tiếp tục: astronomy Level 1-3`),
mình sẽ sinh đúng các file `level_xx.json` tương ứng, kiểm tra trùng lặp trong từng batch.

## Công cụ đảm bảo chất lượng (`_tools/`)
- `rebalance_answers.py` — phân bố lại vị trí đáp án đúng đều khắp A/B/C/D (tất định theo id), tránh việc đáp án luôn ở một vị trí. Chạy sau khi sinh mỗi file:
  ```bash
  python _tools/rebalance_answers.py ai/level_01.json ai/level_02.json
  ```
  Mọi file trong batch mình bàn giao đều đã chạy qua bước này + kiểm tra: parse hợp lệ, không trùng id/câu hỏi, đủ 4 lựa chọn A–D, đáp án đúng khớp.
- **Lưu ý cho app:** nên **xáo trộn thứ tự lựa chọn khi hiển thị** (client-side shuffle) để tăng tính khách quan, dù dữ liệu đã cân bằng sẵn.
