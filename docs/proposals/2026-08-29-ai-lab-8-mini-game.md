# Đề xuất: Q-LAB — AI Training Center, 8 mini-game 3–8 phút

**Người viết:** ChatGPT (chủ dự án chuyển tiếp) · **Ngày:** 29/08/2026
**Trạng thái:** đã có bản đối chiếu — xem `2026-08-29-review-ai-lab.md`

> Lưu nguyên văn theo quy trình `docs/PHAN-VAI.md`: đề xuất của ChatGPT/Gemini lưu
> thành file để Claude đọc trực tiếp và để có lịch sử đối chiếu về sau.

---

## 1. Luận điểm gốc

AstroQ **không nên** làm một "khóa học AI được game hóa", mà nên làm một **AI Lab**
gồm các mini-game 3–8 phút, trong đó trẻ **trực tiếp làm cho AI học, làm AI sai, sửa
dữ liệu và thử thách AI**.

Game AI tốt không mở đầu bằng *"Artificial Intelligence is…"* mà bằng:

> *"Byte không biết đâu là thiên thạch. Bạn có thể dạy Byte không?"*

Trẻ chơi trước → sau vài phút tự phát hiện *"mình dạy sai nên Byte cũng đoán sai"* →
lúc ấy khái niệm mới xuất hiện. Đây là đường **learn by doing → observe what happened
→ reflect on why**.

---

## 2. Sản phẩm được viện dẫn làm tham chiếu

| Sản phẩm | Tuổi | Trẻ làm gì | Thứ đáng học |
|---|---|---|---|
| Code.org – AI for Oceans | 7–11 | Gắn nhãn cá / không phải cá → huấn luyện → xem AI phân loại dữ liệu mới | Quan hệ data → training → prediction |
| Google Quick, Draw! | ~8+ | Vẽ 20 giây để mạng nơ-ron đoán | AI nhìn, đoán, và **sai**; phản hồi tức thì |
| Google Teachable Machine | ~8+ | Tự thu ảnh/âm thanh/pose → Train → Test | Trẻ thật sự dạy một mô hình, không cần code |
| MIT Cognimates | 7–10 | Train AI, lập trình robot/game | Từ người dùng thành người tạo AI |
| Google Semantris | ~10+ | Cho từ gợi ý để AI tìm từ liên quan | Máy xử lý ngữ nghĩa thế nào |
| Day of AI – AI or Not? | Year 5–10 | Nhận diện đâu là AI | Critical thinking + digital literacy |
| Day of AI – Pyramid Puzzle | Year 7–10 | Giải mã ký hiệu | Máy xử lý pattern nhưng không "hiểu" |
| Sunny's Mindful AI Day | Year 5–10 | Chọn tình huống nên/không nên dùng AI | Quyết định cách dùng AI, không phải cấm |
| Breakable Machine | 10–15 | Cố tình đánh lừa image classifier | Biến **lỗi** của AI thành gameplay |

Kèm nghiên cứu 2025 về game **Hello!AI** (lớp 2–6) dùng ba lớp: học khái niệm → suy
nghĩ về thuật toán → áp dụng AI giải quyết vấn đề.

---

## 3. Tám game đề xuất

1. **TRAIN BYTE** — gắn nhãn 10 mẫu (🪨 thiên thạch · 🛰 vệ tinh · 🚀 tàu · ☄️ sao chổi)
   → bấm TRAIN → Byte đoán 10 mẫu chưa từng thấy, kèm % chắc chắn.
   **Twist:** cho trẻ một dataset tệ (thiên thạch đều xám, vệ tinh đều trắng) rồi đưa
   một thiên thạch **đỏ** → Byte đoán "SATELLITE 81%" → *"I LEARNED FROM YOUR DATA."*
2. **DATA RESCUE** — chọn dữ liệu dạy Byte nhận "có dấu hiệu nước". Dataset lệch
   (90 băng / 10 đá) cho accuracy 91% nhưng sai liên tục trên hành tinh đá.
3. **BREAK BYTE** — *"CAN YOU FOOL BYTE?"* Đổi nền, màu, hướng, độ sáng, che một phần
   → làm Byte đoán sai → game hiện **phần mà AI chú ý**.
4. **Q-CORE: NEXT TOKEN** — `EARTH IS THE THIRD ___ FROM THE SUN` → planet 87% ·
   object 6% · … Sau đó: *"Comet ate the…"* → AI vẫn đoán food/fish/cake dù **không
   biết** Comet đã ăn gì. ⇒ *Predicting language ≠ knowing reality.*
5. **PROMPT THE ROBOT** — "Find a planet" → Byte đem về Trái Đất. Chấm theo 4 thành
   phần: TASK · CONTEXT · CONSTRAINT · OUTPUT.
6. **AI OR REAL?** — không dạy "AI hay vẽ sai tay" (sẽ lỗi thời) mà dạy kiểm **nguồn,
   tác giả, cơ quan, metadata, bằng chứng đối chứng**. Câu chốt: *"Don't ask only:
   Does it look real? Ask: Where did it come from?"*
7. **SHOULD I ASK AI?** — theo Sunny một ngày: khi nào hỏi AI, khi nào tự nghĩ, khi
   nào không chia sẻ thông tin riêng tư.
8. **ALGORITHM OR AI?** — Máy tính bỏ túi · thang máy · gợi ý YouTube · cửa tự động ·
   ChatGPT → AI hay không? Chữa định kiến *tự động = AI*.

---

## 4. Cấu trúc curriculum đề xuất — 5 hệ thống của Q-Core

| Q-Core system | Khái niệm | Game |
|---|---|---|
| 👁 PERCEPTION | AI nhìn/nghe | Train Byte |
| 🧠 LEARNING | AI học từ data | Data Rescue |
| 🔍 REASONING | AI dùng representation/pattern | Break Byte |
| 💬 LANGUAGE | LLM, token, prompt | Next Token + Prompt Robot |
| ⚖️ AI & HUMANS | bias, truth, ethics | AI or Real + Should I Ask AI? |

Viện dẫn **Five Big Ideas in AI** của AI4K12 và ba cấp **Understand → Apply → Create**
của UNESCO.

---

## 5. Nếu chỉ chọn 3 game

🥇 **TRAIN BYTE** (AI learns from data) · 🥈 **Q-CORE: NEXT TOKEN** (cách LLM hoạt
động — thứ phụ huynh đang quan tâm) · 🥉 **BREAK BYTE** (AI can be wrong).

Ba game tạo một mạch: **Teach AI → Understand AI → Challenge AI**.

---

## 6. Định vị lại marketing

> **Explore Space. Train AI. Think Smarter.**
> hoặc mạnh hơn: **Don't just use AI. Learn how it thinks.**

Landing hiện ngay ba khối: TRAIN AN AI · BREAK AN AI · UNDERSTAND GENERATIVE AI.
Phụ huynh bấm quảng cáo AI + critical thinking sẽ **lập tức thấy sản phẩm thực sự có
AI literacy**, còn thiên văn là thế giới game để học AI — thay vì hai chủ đề tách rời.
