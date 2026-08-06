# ĐỀ BÀI GEMINI — VÒNG 2: câu hỏi theo THUẬT NGỮ, không theo cấp độ

> Ngày 05/08/2026 · **THAY HẲN** `2026-08-05-de-bai-gemini-1000-quiz-100-bai-doc.md`.
> Đề bài vòng 1 sai hướng ở phần quiz; lý do ghi ở mục 0. Phần **bài đọc** thì giữ,
> chỉ cập nhật đích đến. Dán **toàn bộ** file này vào Gemini (kèm `docs/BRIEFING.md`
> nếu chưa dán).

---

## 0. VÌ SAO ĐỔI — và đây là lỗi của đề bài, không phải của bạn

Vòng 1 yêu cầu **1.000 câu chia 5 chủ đề × 12 cấp độ**, đổ vào `learningdata/`.
Sau khi khảo sát bốn app đang chạy tốt cho cùng lứa tuổi, hướng đó bị bác:

| App | Ai chọn câu hỏi tiếp theo cho trẻ? |
|---|---|
| Duolingo | **Hệ thống** — bản Path đã **bỏ hẳn** quyền chọn bài của bản tree cũ |
| Prodigy Math | **Thuật toán** — trẻ *"thậm chí không biết mình đang được đánh giá"* |
| Kahoot · Quizizz · Blooket | **Giáo viên** chọn bộ câu; trẻ chỉ chọn *chế độ chơi* |
| IXL / Khan | **Bài chẩn đoán** định vị rồi tự phục vụ |

Lý do Duolingo nêu: bản tree cũ gây *"bối rối thường trực — không biết nên làm kỹ năng
này hay không, và khi nào thì sang bài kế"*. Hướng dẫn UX cho lứa 8–12 cũng chốt
**tối đa 3–5 lựa chọn mỗi màn**.

⇒ Một bảng **5 chủ đề × 12 cấp = 60 ô** là đúng thứ không app nào dám đặt trước mặt trẻ.
**AstroQ sẽ không có màn chọn chủ đề/cấp độ nào.** Hệ thống rút đề; quyền chọn duy nhất
của trẻ là **chọn MỤC TIÊU** ở Sổ Tay Thuật Ngữ (*"làm câu hỏi để mở thẻ này"*).

---

## 1. HAI CON SỐ ĐỌC TRƯỚC KHI VIẾT

### ① Một câu hỏi của AstroQ nặng **1.825 byte** — nên 1.000 câu ≈ **1,78 MB**

Đo trên `js/quiz-questions.js`: 35 câu / 62,4 KB. Câu ở đây song ngữ đầy đủ, có lời khen,
lời an ủi, gợi ý và nguồn — không phải một dòng text.

Để so: cả dự án đã phải cắt font **621 → 101 KB**, ảnh **72 MB → 2,79 MB**, và bỏ three.js
khỏi nhiệm vụ để đường tải đầu từ **308 → 71 KB**. Một file 1,78 MB nạp bằng `<script>` ở
trang quiz sẽ là **thứ nặng nhất dự án**, gấp 25 lần cả bộ font.

⇒ **Nộp thành NHIỀU FILE, mỗi file một thuật ngữ.** Trang chỉ tải đúng nhóm câu nó cần —
việc chia file là phần bạn phải làm đúng ngay từ đầu, không phải việc gộp lại sau.

### ② Số câu và số **thẻ Sổ Tay** đi liền nhau — không tách rời được

Sổ Tay Thuật Ngữ hiện có **15 thẻ**. Một thẻ mở khoá khi trẻ trả lời đúng **BẤT KỲ MỘT**
câu hỏi trong danh sách của nó. Nên:

- Giữ 15 thẻ mà đổ 1.000 câu ⇒ 66 câu/thẻ, và **vẫn chỉ có 15 thứ để sưu tập**.
- Muốn 1.000 câu có ý nghĩa thì Sổ Tay phải lớn lên: **~50 thẻ × ~20 câu**.

⇒ Việc này vì thế là **hai việc**: viết thẻ Sổ Tay mới, và viết câu hỏi cho từng thẻ.
Bạn làm cả hai, **theo từng thẻ một** — mỗi lượt nộp là một thẻ hoàn chỉnh kèm bộ câu
hỏi của nó.

---

## 2. HÌNH DẠNG DỮ LIỆU — bám đúng, sẽ có máy kiểm

### ② a) Một CÂU HỎI (`js/quiz-questions.js`)

```js
{ term: "star-color",                     // KHOÁ DUY NHẤT toàn bank, kebab-case
  topic: { vi: "Thiên văn", en: "Astronomy" },
  lv: 2,                                   // 1 dễ · 2 vừa · 3 khó  (xem ⚠️ dưới)
  q:    { vi: "…?", en: "…?" },
  opts: { vi: ["…","…","…","…"], en: ["…","…","…","…"] },
  a: 2,                                    // chỉ số đáp án đúng trong opts
  ok:   { vi: "Chính xác! …", en: "…" },   // lời khen + kiến thức
  no:   { vi: "Chưa đúng. …", en: "…" },   // lời an ủi + chỉ ra đáp án đúng
  hint: { vi: "…", en: "…" },
  src:  S.star,                            // ⚠️ THAM CHIẾU, không phải URL — xem dưới
  srcQuote: "<TRÍCH NGUYÊN VĂN câu trên trang đó chứng minh đáp án>",
  srcChecked: "2026-08-06" }
```

⚠️⚠️ **`src` KHÔNG phải một URL viết thẳng — nó trỏ vào BẢNG NGUỒN DÙNG CHUNG `S`.**
Bank hiện tại khai **12 URL** ở một chỗ rồi dùng **30 lần**:

```js
var S = {
  star:  { name: "NASA Science — Stars", url: "https://science.nasa.gov/universe/stars/" },
  planet:{ name: "NASA Science — About the Planets", url: "https://…" },
  …
};
…
{ term: "star-hottest", …, src: S.star, srcQuote: "The bluish stars are the hottest ones." }
```

Viết URL thẳng vào từng câu thì **870 câu = ~870 bản sao của ~40 địa chỉ**, và ngày NASA
đổi một đường dẫn thì phải sửa hàng trăm dòng. Vì thế:
- **`src` = khoá trỏ vào `S`** (thêm khoá mới vào `S` nếu nguồn chưa có ở đó)
- **`srcQuote` thì viết THẲNG ở từng câu** — mỗi câu một câu trích khác nhau, không dùng chung được

⚠️ **`lv` chỉ có BA bậc, không phải 12 cấp.** Nó **không bao giờ hiện ra cho trẻ chọn** —
chỉ để hệ thống rút đề hợp với cấp độ mà server đã tính sẵn. Ba bậc là đủ để điều tiết;
mười hai cấp là một cái menu trá hình.

⚠️ `term` là **khoá của CÂU**, không phải khoá của khái niệm — mỗi câu một khoá riêng
(`star`, `star-fusion`, `star-color`…). Trùng khoá là hai câu đè lên nhau trong bộ nhớ
tiến độ của trẻ.

### ② b) Một THẺ SỔ TAY (`js/codex-terms.js`)

```js
{ id: "term_star_colour", cat: "space", ic: "cx-star-colour",
  q: ["star-color", "star-temp", "star-red", …],   // các khoá câu mở được thẻ này
  src: [{ label: "NASA Science — Stars", url: "https://…" }],
  vi: { t: "…",            // tên thuật ngữ
        an: "…",           // biệt danh một dòng, gợi hình
        sum: "…",          // MỘT câu tóm tắt cho lưới thẻ
        def: "…",          // định nghĩa 3–5 câu, chính xác
        gr: "…",           // ví dụ đời thường, 2–4 câu — chỗ trẻ THẬT SỰ hiểu ra
        dg: ["…", "…", "…"] },   // ĐÚNG 3 nhãn cho sơ đồ
  en: { …y hệt… } }
```

⚠️ **`ic` là khoá icon — bạn chỉ ĐẶT TÊN, không vẽ.** Bản vẽ SVG do Claude làm (dự án đã
có 15 icon `cx-*` cùng phong cách). Đặt tên theo hình muốn thấy, ví dụ `cx-star-colour`.

---

## 3. VIỆC — theo từng THẺ, không theo cấp độ

### Phân bổ đề nghị

| Nhóm | Thẻ hiện có | Thẻ thêm | Câu hỏi |
|---|---:|---:|---:|
| Thiên văn nền (sao · hành tinh · vệ tinh · thiên thạch…) | 15 | +20 | ~700 |
| Trái Đất & khí quyển | 0 | +10 | ~200 |
| Dụng cụ & khám phá (kính thiên văn · tàu thăm dò · quỹ đạo) | 0 | +5 | ~100 |
| **Tổng** | **15** | **+35** | **~1.000** |

⚠️ **KHÔNG làm AI · Lượng tử · Lập trình · CNTT ở vòng này.** Dự án đã **cố ý không phát
hành** 4 thuật ngữ AI/Lượng tử vì bản nháp không có nguồn — thêm nữa là lặp lại đúng
quyết định đã bị bác. Đề xuất được, nhưng để thành một vòng riêng có nguồn tử tế.

### Mỗi thẻ nộp thành MỘT khối hoàn chỉnh

1. Định nghĩa thẻ (mục 2b) — đủ `vi` + `en`.
2. **~20 câu hỏi** cho thẻ đó, khoá duy nhất, `lv` rải đều 1/2/3.
3. Ba dòng tự khai: bao nhiêu URL bạn **mở đọc thật** · bao nhiêu câu `srcQuote` rỗng và
   vì sao.

---

## 4. BỐN ĐIỀU TUYỆT ĐỐI

**① `srcQuote` là trường quan trọng nhất của cả việc này.**
Dự án đã **hai lần** dẫn một trang NASA cho một câu mà **trang đó không hề nói** — cả hai
lần đều vì tin đoạn tóm tắt của cỗ máy tìm kiếm thay vì mở trang ra đọc. Không trích được
nguyên văn thì **viết lại câu hỏi cho không cần con số đó**. ⛔ Không bao giờ giữ một con
số mà không trích được câu nguồn nói ra nó.

**② ĐỪNG rải đều đáp án A/B/C/D.** `quiz.html` có `shuffleOptions()` **trộn lại 4 lựa
chọn mỗi lần hiện câu** — thứ tự bạn khai báo không bao giờ tới người chơi. Luật này đã
chết, và nó **đã tiêu trọn một vòng phối hợp** khi một model được yêu cầu đi rải lại đáp
án cho 25 câu.

**③ Ba đáp án sai phải là HIỂU LẦM PHỔ BIẾN CÓ THẬT**, không phải đáp án nhảm. Một câu có
ba lựa chọn vô lý là một câu không đo được gì. Ví dụ đã dùng trong dự án: *"vùng cực lạnh
vì ở xa Mặt Trời hơn"* — sai, nhưng gần như đứa trẻ nào cũng nghĩ vậy.

**④ `no` (lời khi trả lời sai) phải DẠY, không phải phán.** Đây là chỗ bài học thật sự
nằm — trẻ chọn sai vẫn phải hiểu ra vì sao.

### Ba cái bẫy nội dung đã có thật trong dự án

- ⛔ **"Nóng lạnh vì gần Mặt Trời hơn"** — quan niệm sai phổ biến nhất; nguyên nhân là
  **góc chiếu**. Ra câu về khí hậu thì phải bác nó ra mặt.
- ⛔ **"Nam Cực là châu lục cao nhất"** — cỗ máy tìm kiếm tóm tắt đúng câu đó *từ một
  trang NASA*, nhưng đọc cả trang thì trang **không nói vậy**.
- ⛔ **Quy đổi đơn vị rồi coi kết quả là số của nguồn.** NASA ghi *"tens of thousands of
  **miles** per hour"* — đổi sang km/h rồi ghi như số của NASA là tự tạo ra một con số
  không nguồn.

### Nguồn ưu tiên

NASA (`science.nasa.gov`; **`spaceplace.nasa.gov`** là trang NASA viết *cho trẻ em*, rất
hợp lứa 8–12) · ESA · NOAA · USGS · NPS. Mọi URL phải trả **200** ở ngày kiểm.

---

## 5. VIỆC 2 — 100 BÀI ĐỌC

**Đích đến nay đã có thật: `js/articles.js`** (gộp ngày 05/08/2026 từ hai mảng `ARTICLES`
riêng ở `learn.html` và `library.html` — chúng từng mang **hai id cho cùng một bài**, gây
hai lỗi thật). Hiện có **9 bài**. Bài mới bám đúng hình dạng đó:

```js
{ id: "art-<slug>", src: "NASA", cat: "astronomy", em: "🌌",
  c: ["#8ee0ff","#2f6fd0","#0e2a5e"],     // 3 màu gradient cho thẻ
  img: IMG + "PIA25433/PIA25433~large.jpg",  // hoặc null
  credit: "NASA / JPL-Caltech", url: "https://…",
  title: { vi: "…", en: "…" },
  body:  { vi: ["đoạn 1", "đoạn 2", …], en: […] },
  terms: ["star-color", …] }                // khoá câu hỏi liên quan, nếu có
```

Bốn ràng buộc:
1. ⛔ **Đừng viết "đọc xong nhận Thiên thạch tím".** Đọc bài **không còn thưởng** từ
   30/07/2026; nó chỉ ghi vào hồ sơ. Hứa sai là lỗi đã phải đi sửa một lần.
2. **Ảnh phải thật, có credit, URL trả 200.** Không chắc thì để `img: null` — cả hai chỗ
   vẽ đều đã có nhánh không ảnh. Thà không ảnh còn hơn một ô ảnh vỡ trước mặt trẻ.
3. ⛔ **Không sao chép nguyên văn tài liệu NASA/ESA.** Viết lại cho trẻ bằng lời của mình;
   `srcQuote` là chỗ duy nhất được trích, và nó để **kiểm chứng**, không để đăng.
4. **`terms` nối bài đọc với câu hỏi** — đọc xong bài về màu sao thì gặp câu hỏi về nó.

Phân bổ: thiên văn 55 · Trái Đất & khí hậu 25 · dụng cụ & khám phá 20.

---

## 6. GIAO NỘP — ĐỢT 1 RỒI DỪNG

**Đợt 1 (làm ngay, rồi CHỜ phản hồi):**
- **3 thẻ Sổ Tay mới** hoàn chỉnh (đủ vi + en + nguồn + tên icon)
- **60 câu hỏi** cho 3 thẻ đó (20 câu/thẻ, `lv` rải đều)
- **5 bài đọc** thiên văn

Đây là mẫu chuẩn. **Đúng rồi mới nhân lên** — 1.000 câu sai hình dạng là 1.000 câu phải
làm lại.

## 7. KHUÔN TRẢ LỜI BẮT BUỘC

**Mục 0 — Cái tôi ĐÃ MỞ ĐỌC và cái tôi KHÔNG mở được.** Bao nhiêu URL bạn thật sự truy
cập, bao nhiêu chỉ dựa vào trí nhớ. Đây là mục được tin cậy nhất — nói thật thì phần còn
lại dùng được.

**Mục 1 — Đợt 1** (3 thẻ + 60 câu + 5 bài đọc), dán JSON/JS đầy đủ.

**Mục 2 — Danh sách 35 thẻ đề nghị** cho cả vòng: tên thuật ngữ + một dòng vì sao nó đáng
là một thẻ sưu tập cho trẻ 8–15. Đây là thứ quyết định hình dạng cả 1.000 câu, nên nộp
sớm để chốt trước.

**Mục 3 — Giả định & cái tôi KHÔNG chắc.** Bắt buộc: thẻ nào bạn thấy **không đủ nguồn
uy tín cho lứa tuổi này** · chỗ nào cần giáo viên rà trước khi phát hành · con số nào bạn
không trích được câu nguồn.
