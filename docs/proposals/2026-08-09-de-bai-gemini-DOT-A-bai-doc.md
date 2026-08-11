# ⛔ ĐÃ THỰC HIỆN XONG 09/08/2026 — ĐỪNG DÁN CHO Gemini NỮA

> Chủ dự án chốt *"chạy đợt A"*, và **Claude đã tự làm trọn 20 bài** (mở từng trang nguồn,
> trích nguyên văn, kiểm 200). Dán lại file này là nhận thêm 20 bài **trùng nội dung**.
>
> **Kết quả:** kho bài đọc **14 → 34 bài**; phân bổ **18 thiên văn · 8 robot · 5 AI ·
> 3 lượng tử** (trước: 10/1/1/2). Đúng phân bổ đề ra ở mục 1: +8 thiên văn · +7 robot ·
> +4 AI · +1 lượng tử. Kế hoạch 100 bài nay đã giao **25/100**.
>
> **20 nguồn NASA, tất cả kiểm 200 ngày 09/08/2026, không chuyển hướng.** Hai URL đoán
> theo mẫu đã trả **404** (`/universe/stars/supernovae/`, `/mission/ingenuity/`) và được
> thay bằng URL thật — đúng lý do mục 3④ bắt kiểm 200 trước khi ghi.
>
> **Bốn chỗ CỐ Ý KHÔNG VIẾT vì trang nguồn `NOT ON PAGE`** (ghi rõ trong `js/articles.js`):
> ① *"nguyên tố trong cơ thể bạn đến từ ngôi sao"* · ② tốc độ quay cánh quạt Ingenuity ·
> ③ vì sao chọn hình dạng người cho Robonaut · ④ ⚠️ trang *What is Quantum Computing?*
> **không định nghĩa qubit** và **không nói câu "0 và 1 cùng lúc"** — nên bài lượng tử viết
> về **chồng chập** và **rối lượng tử** đúng theo lời NASA, không đặt một định nghĩa qubit
> nào vào miệng NASA.
>
> **Việc kèm theo:** 4/5 câu lập trình mồ côi của bank (`sensor` · `condition` · `sequence` ·
> `algorithm` — khai từ 25/07/2026 mà **chưa bao giờ được rút ra hỏi**) nay được bài
> `art-rover-drives-itself-mars` nhận qua `terms`. Đo được: mở
> `quiz.html?terms=sensor,condition,sequence,algorithm` thì **4/5 câu của lượt là 4 câu đó**.
> `loop` **cố ý để trống** — bài không dạy khái niệm vòng lặp.
>
> **Còn nợ của Đợt A:** `loop` chưa có bài nhận · `moon-largest` chưa có bài nào dạy
> (Ganymede lớn hơn Sao Thuỷ nằm ở trang Ganymede, không ở trang Moons) · và **`lib-qubit`
> vẫn dẫn `ibm.com/quantum`** — nay đã có nguồn thay tử tế là
> `nasa.gov/technology/computing/what-is-quantum-computing/`.
>
> Giữ file này làm **đặc tả**: mọi luật ở dưới (hình dạng dữ liệu · 5 điều tuyệt đối ·
> 3 cái bẫy nội dung) vẫn là luật cho các đợt bài đọc sau.

---

# ĐỀ BÀI CHO Gemini — ĐỢT A: 20 BÀI ĐỌC

> Ngày 09/08/2026 · Vai: **Gemini = tra nguồn & kiểm chứng** (`docs/PHAN-VAI.md`).
> Dán **toàn bộ** file này. Nếu chưa dán `docs/BRIEFING.md` thì dán nó trước.

## ⚠️ ĐÂY KHÔNG PHẢI MỘT NHÁNH MỚI

Đây là **phần bài đọc của kế hoạch 05/08 được kéo lên trước** —
`2026-08-05-de-bai-gemini-VONG-2-theo-thuat-ngu.md` mục 5 (100 bài đọc). Mọi luật của
đề bài đó **còn nguyên hiệu lực**; file này chỉ đổi **thứ tự làm** và **phân bổ chủ đề**,
kèm lý do đo được ở mục 0.

⛔ **KHÔNG mở rộng Sổ Tay Thuật Ngữ ở đợt này.** Việc 30 thẻ / 870 câu vẫn chạy theo
`2026-08-06-review-gemini-30-the-chot.md`, và **Đợt 2 (270 câu đào sâu 15 thẻ cũ) vẫn là
việc kế tiếp** của dây chuyền đó. Đợt A chạy **song song**, không thay thế.

---

## 0. VÌ SAO KÉO BÀI ĐỌC LÊN TRƯỚC — ba con số

Đo trên mã nguồn ngày 09/08/2026:

| Kho | Có | Kế hoạch | Đã giao |
|---|---:|---:|---:|
| Thẻ Sổ Tay | **19** | 49 | 4/30 |
| Câu quiz | **100** | 870 | 80/850 |
| **Bài đọc** | **14** | **100** | **5/100** |

**Bài đọc là kho tụt lại xa nhất**, và nó là kho **duy nhất** trẻ ngồi *đọc*. Thẻ Sổ Tay
là thứ sưu tập; câu hỏi là thứ kiểm tra; bài đọc mới là nội dung.

Và nó lệch chủ đề nặng. Sidebar `library.html` đang hiện đúng thế này:

```
Thiên văn 10  ·  Lượng tử 2  ·  AI 1  ·  Robot 1
```

Chủ dự án nhìn con số đó rồi nói *"trạm tri thức đang quá ít bài đọc"*. Ba chip cuối mỗi
chip chứa 1–2 bài — bấm vào gần như không có gì.

⇒ **Đợt A phải sửa cả hai: tăng số bài, và lấp ba chủ đề đang trơ.**

---

## 1. PHÂN BỔ ĐỢT A — 20 bài

| Chủ đề | `cat` | Có | Thêm | Ghi chú |
|---|---|---:|---:|---|
| Thiên văn & Trái Đất | `astronomy` | 10 | **8** | bám 19 thẻ Sổ Tay đang chạy |
| Robot | `robot` | 1 | **7** | **góc "robot trong không gian"** — xem ⚠️ dưới |
| AI | `ai` | 1 | **4** | **góc "AI trong khoa học vũ trụ"** — xem ⚠️ dưới |
| Lượng tử | `quantum` | 2 | **1** | chỉ 1 — xem ⚠️ mục 4 |

### ⚠️⚠️ CÁCH LẤP ROBOT VÀ AI MÀ KHÔNG PHÁ LUẬT NGUỒN

Đề bài vòng 2 ghi rõ: *"**KHÔNG làm AI · Lượng tử · Lập trình · CNTT ở vòng này** — dự án
đã cố ý không phát hành 4 thuật ngữ AI/Lượng tử vì bản nháp không có nguồn."*

**Quyết định đó KHÔNG bị nới lỏng ở đây**, vì hai thứ khác nhau:

| | Thẻ Sổ Tay | Bài đọc |
|---|---|---|
| Tạo ra thứ sưu tập được? | có | không |
| Mở khoá gì không? | có | không |
| Cần icon SVG vẽ tay? | có | không |
| Trẻ có phải trả lời đúng mới thấy? | có | không |

⇒ Bài đọc là **bề mặt nhẹ hơn nhiều**, và `library.html` **đã đăng** 1 bài AI + 1 bài
robot rồi. Nhưng luật nguồn thì y nguyên.

**Cách giữ được cả hai: viết robot và AI qua ĐÚNG những nguồn dự án đã tin.** Robot và AI
trong không gian là chủ đề NASA/ESA nói rất nhiều — nên không phải mở một danh sách nguồn
mới nào.

**Gợi ý góc bài** *(gợi ý, không phải danh sách chốt — bạn tự chọn theo trang bạn mở được)*:

- **Robot:** rover trên Sao Hỏa đi thế nào khi lệnh từ Trái Đất mất nhiều phút mới tới ·
  cánh tay robot trên trạm vũ trụ · trực thăng bay trên Sao Hỏa · robot lấy mẫu đá ·
  vì sao gửi robot đi trước con người · robot tự tránh chướng ngại vật khi không ai lái.
- **AI:** máy tính giúp tìm ngoại hành tinh trong hàng triệu đường cong ánh sáng · phân
  loại thiên hà từ ảnh · AI chọn chỗ đáng chụp cho tàu thăm dò · lọc nhiễu khỏi ảnh
  kính thiên văn.

⛔ **KHÔNG viết bài về ChatGPT, deepfake, mô hình ngôn ngữ, prompt** ở đợt này. Đó là chủ
đề của một vòng riêng có nguồn riêng, không phải NASA/ESA.

*[Chưa kiểm chứng]* Tôi tin NASA có trang cho từng góc kể trên nhưng **chưa mở kiểm từng
cái**. Nếu một góc không có trang nguồn mở được, **bỏ góc đó và nói ở Mục 0**, đừng viết
bù bằng trí nhớ.

---

## 2. HÌNH DẠNG DỮ LIỆU — bám đúng, có máy kiểm

Đích đến: **`js/articles.js`** (chỗ duy nhất khai bài đọc). Nộp đúng khuôn của 5 bài Đợt 1:

```js
{
  id: "art-<slug>",              // BẮT ĐẦU BẰNG `art-`, kebab-case, duy nhất cả kho
  src: "NASA",                   // "NASA" | "ESA" | "AI & Tech"  — nhãn lọc nguồn
  cat: "astronomy",              // "astronomy" | "ai" | "quantum" | "robot"
  em: "🌍",                      // 1 emoji, dùng khi không có ảnh
  c: ["#8ee0ff", "#2f6fd0", "#0e2a5e"],   // 3 màu gradient cho thẻ, sáng → tối
  url: "https://…",              // trang nguồn, PHẢI trả 200
  img: null, credit: null,       // xem ⚠️ ẢNH ở dưới
  title: { vi: "…", en: "…" },
  body: {
    vi: ["đoạn 1", "đoạn 2", "đoạn 3", "đoạn 4"],
    en: ["…", "…", "…", "…"]
  },
  term: {                        // khung thoại linh vật — giải thích MỘT thuật ngữ
    who: "comet",                // "comet" | "byte"
    word: { vi: "Tầng đối lưu", en: "Troposphere" },
    text: { vi: "<b>Tầng đối lưu</b> là… ☄️", en: "The <b>troposphere</b> is… ☄️" }
  },
  terms: ["atmo-tropo-weather", "atmo-strato-ozone"]   // khoá CÂU HỎI có thật
}
```

### Bốn trường dễ sai nhất

**① `terms` phải là khoá CÂU HỎI CÓ THẬT — tức có file `js/quiz/<khoá>.js`.**
Nó là dây nối *"đọc xong bài này thì gặp câu hỏi về nó"* (`AstroQQuestions.byTerms()`).
Sai một chữ là dây đứt **im lặng**. Bank hiện có **100 khoá**; ví dụ có thật:
`atmo-tropo-weather` · `star-color-temp-determine` · `eclipse-corona-visible-totality` ·
`lunar-red-filtered-atmosphere` · `black-hole-light` · `nebula-gas` · `exoplanet-transit`.

⚠️ Bài về **robot / AI** hiện **chưa có câu hỏi nào** trong bank → để **`terms: []`**.
⛔ Đừng bịa khoá cho có.

**② `img` — mặc định `null`, và đó là lựa chọn đúng.**
Đợt 1 để `img: null` cả 5 bài, cố ý: **đã đo, `~large` KHÔNG tồn tại với mọi ảnh NASA**,
nên đoán đường dẫn theo mẫu là một ô ảnh vỡ trước mặt trẻ. Chỉ điền `img` khi bạn **mở
được đúng URL đó và nó trả 200**; lúc đó `credit` bắt buộc điền theo (`"NASA/JPL-Caltech"`).
`img: null` thì `credit: null`. Cả hai chỗ vẽ đều đã có nhánh không ảnh.

**③ `body` là MẢNG đoạn văn, 4 đoạn, ~3.000 ký tự tổng cho mỗi ngôn ngữ.**
Đo trên kho hiện tại: trung bình **~3.100 ký tự/bài**. Đừng viết 1 đoạn dài, cũng đừng
viết 8 đoạn vụn.

**④ `term` (số ít) khác `terms` (số nhiều).** `term` là **khung thoại linh vật** giải
thích một thuật ngữ khó trong bài; `terms` là danh sách khoá câu hỏi. Hai trường khác
nhau hoàn toàn, tên gần giống nhau — đọc kỹ khuôn ở trên.

---

## 3. NĂM ĐIỀU TUYỆT ĐỐI

**① MỌI CON SỐ TRONG BÀI PHẢI TRÍCH ĐƯỢC TỪ TRANG NGUỒN.**
Không trích được thì **viết lại câu cho không cần con số đó**. Dự án đã **hai lần** dẫn
một trang NASA cho điều trang đó không nói.

⚠️ **Luật mới rút ra từ Đợt 1 của bạn** (`2026-08-06-review-gemini-dot-1.md`) — 13/40 câu
đã trượt đúng chỗ này:

> **Đọc riêng câu nguồn, không nhìn câu bạn viết: nó có chứng minh được điều bạn khẳng
> định không?**
> Nếu câu nguồn đúng với một chủ đề **rộng hơn nhiều** so với điều bạn viết, thì nó
> **không phải bằng chứng** — chỉ là một câu cùng chủ đề.

Ví dụ đã trượt: *"A star's color tells us how hot or cold it is"* là câu có thật, đúng, và
**không chứng minh được bất cứ điều gì** về Betelgeuse, định luật Planck hay dãy quang phổ.

**② KHÔNG SAO CHÉP NGUYÊN VĂN tài liệu NASA/ESA.** Viết lại cho trẻ bằng lời của bạn.
Câu trích nguyên văn chỉ dùng để **kiểm chứng**, không để đăng.

**③ ⛔ ĐỪNG VIẾT "ĐỌC XONG NHẬN THIÊN THẠCH TÍM".**
Đọc bài **không còn thưởng** từ 30/07/2026 (`Wallet.MaxPerLesson = 0`); nó chỉ ghi vào hồ
sơ. Hứa sai là lỗi dự án đã phải đi sửa một lần.

**④ URL PHẢI TRẢ 200 Ở NGÀY BẠN KIỂM, và ghi dạng ĐÍCH.**
Đợt 1 có 4/4 link bị chuyển hướng (`spaceplace.nasa.gov/star-cookies/` →
`…/star-cookies/en/`). Ghi thẳng dạng sau chuyển hướng.

**⑤ SONG NGỮ ĐỦ.** Mọi trường có `{vi, en}` phải có cả hai. `body.vi` và `body.en` phải
**cùng số đoạn**. Bản EN là bản viết lại cho người đọc tiếng Anh, không phải dịch máy.

### Ba cái bẫy nội dung đã có thật trong dự án

- ⛔ **"Nóng lạnh vì ở gần Mặt Trời hơn"** — quan niệm sai phổ biến nhất; nguyên nhân là
  **góc chiếu**. Viết về khí hậu thì phải bác nó ra mặt.
- ⛔ **"Nam Cực là châu lục cao nhất"** — cỗ máy tìm kiếm tóm tắt đúng câu đó *từ một trang
  NASA*, nhưng đọc cả trang thì trang **không nói vậy**.
- ⛔ **Quy đổi đơn vị rồi coi kết quả là số của nguồn.** NASA ghi *"tens of thousands of
  **miles** per hour"* — đổi sang km/h rồi ghi như số của NASA là tự tạo một con số không
  nguồn. Muốn dùng thì viết *"khoảng X (theo NASA là Y dặm/giờ)"*.

### Nguồn ưu tiên

NASA (`science.nasa.gov` · `www.nasa.gov` · **`spaceplace.nasa.gov`** là trang NASA viết
*cho trẻ em*, rất hợp lứa 8–15) · ESA · NOAA · USGS · NPS.

---

## 4. ⚠️ LƯỢNG TỬ — CHỈ 1 BÀI, VÀ ĐÂY LÀ LÝ DO

Đây là chủ đề dễ **sai một cách nghe rất hợp lý** nhất trong cả bốn, và dự án đã cố ý
chưa phát hành 4 thuật ngữ AI/Lượng tử vì bản nháp không có nguồn.

⇒ Viết **đúng một bài**, chọn góc **nào bạn mở được nguồn chắc chắn nhất**, và nếu không
tìm được nguồn đủ tốt cho lứa 8–15 thì **nộp 0 bài lượng tử và nói ở Mục 0**. Nộp thiếu
một bài là chuyện nhỏ; đăng một bài sai về lượng tử cho trẻ thì không.

---

## 5. GIAO NỘP — 5 BÀI RỒI DỪNG

**Nộp 5 bài trước** (3 thiên văn/Trái Đất · 1 robot · 1 AI) rồi **CHỜ phản hồi**.

Đây là mẫu chuẩn — **đúng rồi mới nhân lên**. 20 bài sai hình dạng là 20 bài phải làm lại,
và Đợt 1 đã cho thấy lỗi nguồn không lộ ra nếu không mở từng trang.

Nộp thành **một khối JS dán thẳng được** vào `js/articles.js`, không phải bảng hay văn xuôi.

---

## 6. KHUÔN TRẢ LỜI BẮT BUỘC

**Mục 0 — CÁI TÔI ĐÃ MỞ ĐỌC và CÁI TÔI KHÔNG MỞ ĐƯỢC.**
Bao nhiêu URL bạn **thật sự truy cập được**, bao nhiêu chỉ dựa vào trí nhớ. Với **mỗi con
số** xuất hiện trong bài, ghi câu nguồn nguyên văn chứng minh nó.
⚠️ Đây là mục được tin cậy nhất — nói thật thì phần còn lại dùng được. Đợt 1 bạn **không
gửi mục này** (tin nhắn bị cắt), nên lần này để nó **lên đầu**, trước cả nội dung.

**Mục 1 — 5 bài đọc**, dán khối JS đầy đủ đúng khuôn mục 2.

**Mục 2 — Danh sách 15 bài còn lại** của Đợt A: tiêu đề + `cat` + URL nguồn dự định, mỗi
bài một dòng. Nộp sớm để chốt trước khi viết.

**Mục 3 — Giả định & cái tôi KHÔNG chắc.** Bắt buộc, không được bỏ trống:
- góc bài nào **không tìm được nguồn** và bạn đã bỏ;
- chỗ nào cần **giáo viên rà** trước khi phát hành;
- con số nào bạn **không trích được** câu nguồn nói ra nó;
- bài nào bạn thấy **quá khó cho lứa 8–15** dù nguồn có thật.
