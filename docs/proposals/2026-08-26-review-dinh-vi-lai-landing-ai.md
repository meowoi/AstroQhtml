# Review: định vị lại landing theo hướng AI / STEM

**Đề xuất gốc:** chủ dự án (26/08/2026) — *"đổi positioning, không đổi lõi"*: nâng
headline lên tầng "học khoa học bằng cách khám phá", thêm 3 trụ **Space & Astronomy ·
AI & Technology · Scientific Thinking**, và sửa câu lead "Du hành qua Hệ Mặt Trời 3D".

**Người đối chiếu mã nguồn:** Claude · **Ngày:** 26/08/2026
**Vai:** phía kiểm giả định bằng số đo (`docs/PHAN-VAI.md`)
**Liên quan:** `docs/proposals/2026-08-19-ai-dong-vai-gi-trong-astroq.md`

---

## 1. Kết luận ngắn

**Đồng ý với hướng đi, nhưng một giả định của đề xuất đã đo ra là SAI — và sai theo
hướng có lợi.**

Đề xuất viết: *"AI nên là hook thị trường, không nên trở thành lời hứa sản phẩm nếu
AstroQ chưa thực sự có nội dung AI đủ sâu."*

Đo trên repo: **AstroQ đã có nội dung AI, và nó là phần LỚN NHẤT của kho bài đọc — lớn
hơn thiên văn.** Đây không phải promise–product mismatch. Đây là **promise–cửa-trước
mismatch**: hàng có trong kho, cửa trước không trưng ra.

⇒ Nên không cần "định vị lại" theo nghĩa nói rộng ra để đỡ nói quá. Cần **nói đúng thứ
đang có**. Việc phải làm nhẹ hơn đề xuất tưởng, và trung thực hơn.

---

## 2. Số đo — kho nội dung theo chủ đề (26/08/2026)

**Bài đọc** — `grep -ho 'cat: "[a-z]*"' js/article/*.js | sort | uniq -c`, tổng 70 bài:

| Chủ đề | Số bài | % |
|---|---:|---:|
| `ai` | 14 | 20% |
| `robot` | 11 | 16% |
| `it` | 7 | 10% |
| **⇒ AI + máy tính + robot** | **32** | **46%** |
| `astronomy` | 17 | 24% |
| `physics` | 6 | 9% |
| `life` | 5 | 7% |
| `math` | 4 | 6% |
| `quantum` | 3 | 4% |
| `engineering` | 3 | 4% |

**Câu hỏi quiz** — `ls js/quiz/*.js` = **190 câu**; đếm theo nhãn `topic` thì **38 câu
(20%)** thuộc AI / thuật toán / học máy / chatbot / cảm biến / robot / đạo đức AI /
thiên lệch thuật toán.

**Wiki** (`wiki/`, 10 bài): **3 bài** là AI/lập trình — `ai-va-robotics-khac-nhau.html`,
`comet-va-byte-la-ai.html`, `tre-em-may-tuoi-hoc-lap-trinh.html`.

**Sổ Tay** (`js/codex-terms.js`, 28 thẻ): **7 thẻ** `ai`/`robot`.

⚠️ Con số 46% không mới — `docs/decisions/010` đã ghi từ 14/08/2026: *"kho hiện tại lệch
hẳn về thiên văn + AI/robot"*. Điều mới là **AI đã vượt thiên văn** ở kho bài đọc.

---

## 3. Số đo quan trọng hơn: nội dung ĐÚNG KIỂU quảng cáo đang hứa

Quảng cáo nói **"AI NEEDS CRITICAL THINKING"**. Đây là những file đã có trong repo:

**Bài đọc** (`js/article/`):
- `art-algorithms-are-opinions.js` — thuật toán là một quan điểm
- `art-algorithmic-bias.js` — thiên lệch thuật toán
- `art-chatbot-confidently-wrong.js` — chatbot sai mà nói rất chắc
- `art-chatbot-does-not-remember.js` — chatbot không nhớ
- `art-nobody-fully-understands-llm.js` — không ai hiểu hết LLM
- `art-what-is-ai-nasa.js`, `art-ai-tags-nasa-data.js`, `art-ai-predicts-solar-flares.js`…

**Câu hỏi** (`js/quiz/`):
- `algorithm-is-an-opinion.js` · `bias-not-on-purpose.js` · `bias-who-is-served.js`
- `chatbot-confidently-wrong.js` · `chatbot-does-not-remember.js`
- `ai-does-not-think-like-human.js` · `ai-language-limited.js`
- `ai-training-data-from-people.js` · `ml-humans-still-check.js`
- `ai-ethics-trustworthy.js` · `ai-ethics-governance.js`

⚠️⚠️ **Lời hứa của quảng cáo đã được sản phẩm chống lưng đầy đủ.** Người bấm vào bài "AI
cần tư duy phản biện" mà vào được `library.html` lọc chip **AI** sẽ thấy đúng thứ họ
được hứa. Vấn đề duy nhất: **không có đường nào từ quảng cáo tới đó** — họ hạ cánh xuống
một trang nói về Hệ Mặt Trời.

---

## 4. Chỗ đề xuất nói đúng: phần TƯƠNG TÁC thì đúng là thiên văn 100%

Đây là ranh giới thật, và nó phải được giữ trong mọi câu chữ mới:

| Lớp sản phẩm | Nội dung | Đo bằng |
|---|---|---|
| **Kho đọc + quiz + Sổ Tay** | **đa ngành, AI là nhánh lớn nhất** | mục 2 |
| **Nhiệm vụ** | **thiên văn 100%** — `mission-earth` · `mission-orbit` · `mission-planet` (+ `mission-map`, `mission-tree` là vỏ) | `ls mission-*.html` |
| **Mini-game** | arcade-không gian; `game-units` là đo lường, còn lại né/bắn/đua | `ls game-*.html` (10 game) |
| **Bản đồ 3D** | thiên văn | `explorer.html` |

⇒ Câu *"thiên văn là cánh cửa đầu tiên"* trong đề xuất là **đúng theo số đo**, không phải
một cách nói cho hay. Vũ trụ là **thế giới chơi**; AI là **nhánh kiến thức lớn nhất**.
Câu chữ mới phải phản ánh đúng hai vai đó — đừng hứa "nhiệm vụ AI", chưa có.

---

## 5. Lỗi nằm ở HAI trang, và trang tệ hơn KHÔNG phải trang chủ

Đề xuất chỉ nói tới một landing. Thực tế đường đi của một lượt bấm quảng cáo là hai
trang, và trang thứ hai tệ hơn:

### 5a. `/` (`index.html`) — đã nói AI, nhưng nói ở màn thứ ba
- `<title>`: "Khám Phá Ngân Hà Tri Thức | Vũ Trụ · AI · Lượng Tử" — có
- `.lede` dòng 2 của hero: *"chủ đề Vũ trụ, AI & Vật lý Lượng tử"* — có
- **Nhưng 4 trụ (`<ul class="pillars">`) nằm trong `<section class="aeo" id="what-is">`,
  SAU khối waitlist** → màn thứ 3 khi cuộn. Hero chỉ có: eyebrow "MISSION 001", h1 "Khám
  Phá Ngân Hà Tri Thức", đồng hồ, 3 nút, và **hai linh vật mèo + robot**.
- Khách lạ ở lại đúng trang này: `js/index-gate.js` chỉ đẩy người **đã có `uid`**.
- Khuôn link chiến dịch ở `astroQMkt/README.md` là `https://astroq.org/?utm_source=fb…`
  ⇒ lưu lượng quảng cáo hạ cánh **ở đây**.

### 5b. `landing-app.html` — 100% thiên văn, và nó là trang NGAY TRƯỚC nút đăng ký

```
badge : "Bản đồ 3D tương tác"
h1    : "Chào mừng đến AstroQ"
lead  : "Du hành qua Hệ Mặt Trời trong không gian 3D thời gian thực — xoay, phóng to…"
card1 : 🪐 8 hành tinh
card2 : 🔭 Tương tác 3D
card3 : ✨ Thông tin trực quan
footer: "AstroQ · Solar System Explorer"
```

**Không một chữ nào về AI, tư duy, hay bất cứ nhánh nào ngoài thiên văn.** Đây là ảnh
chụp mà đề xuất đang nói tới.

⚠️⚠️ **Đây là chỗ sửa rẻ nhất và lời nhất trong cả dự án:**
1. Nó mang `noindex,follow` (có chủ ý, xét lại 18/08/2026) ⇒ **sửa câu chữ ở đây không
   tốn một đồng SEO nào**, không phải cân nhắc từ khoá, không phải sinh lại `en/`.
2. Nó là **trang cuối trước quyết định đăng ký**. Trang chủ tạo tò mò; trang này chốt.
3. i18n của nó là hằng `I18N` **nội trang** ⇒ sửa một file, không lan ra `js/index.js`.

---

## 6. Chỗ đang nói quá THẬT SỰ — và đề xuất tình cờ sửa đúng nó

Không phải AI. Là **Lượng Tử**.

`<title>` và `og:*` của `/` đặt **"Vũ Trụ · AI · Lượng Tử"** — ba thứ ngang hàng nhau.
Đo ra: `quantum` có **3 bài đọc (4%)** và ~**1 câu quiz** (`qubit-superposition.js`).
Robotics thì có 11 bài + 10 câu (cảm biến / robot) mà **không nằm trong title**.

⇒ Đề xuất gộp 4 trụ → 3 trụ vô tình chữa đúng lỗi này: nó hạ lượng tử khỏi hàng đầu và
gộp robotics vào "AI & Công nghệ" — nơi có 32 bài chống lưng. **Tôi ủng hộ, và lý do là
số đo chứ không phải thẩm mỹ.**

---

## 7. ⚠️⚠️ Luật cứng phải giữ: "AI" trên landing là CHỦ ĐỀ HỌC, không phải công nghệ trong sản phẩm

Đề xuất 19/08/2026 đã chốt và **chưa có gì thay đổi**: astroQ **không có bề mặt AI nào
cho trẻ chạm vào**. Vai ② (điều độ khó theo `lv`) là **adaptive bằng LUẬT**
(`AstroqSV/Services/Adapt.cs`), không phải bằng mô hình. Nguyên văn cảnh báo ở mục 5 của
file đó:

> *"Gọi nó là 'AI' trên trang bán hàng là nói quá — và một sản phẩm cho trẻ em nói quá về
> AI là đúng thứ FTC đang điều tra."*

Câu chữ đề xuất lần này **đi qua được cửa đó**, và đó là điểm mạnh của nó:

| Câu | Phán | Vì sao |
|---|---|---|
| "🤖 AI & Technology — hiểu công nghệ, biết đặt câu hỏi và kiểm chứng" | an toàn | nói về **thứ trẻ học**, có 32 bài chống lưng |
| "AstroQ giúp trẻ khám phá thiên văn, công nghệ và tư duy khoa học" | an toàn | chủ đề, không phải tính năng |
| ❌ "AI cá nhân hoá lộ trình cho con" | **cấm** | `Adapt.cs` là ngưỡng tỉ lệ đúng, không có mô hình nào |
| ❌ "gia sư AI kèm con học" | **cấm** | vai ① đã HOÃN, chưa có một dòng code |
| ❌ "trợ lý AI Byte giải thích cho con" | **cấm** | Byte là **lời thoại viết tay**; `wiki/comet-va-byte-la-ai.html` đã nói thật điều này ra |

⚠️ Thẻ Sổ Tay + linh vật Byte tạo ra một cái bẫy tự nhiên: rất dễ viết "trợ lý AI" vì
trong truyện Byte *là* robot AI. Trên trang bán hàng thì đó là nói về **nhân vật**, mà
người đọc sẽ hiểu là **tính năng**. Nếu dùng Byte trong copy mới, phải viết rõ nó là
nhân vật.

---

## 8. Cảnh báo: có một giả thuyết CẠNH TRANH cho "click nhưng không hành động tiếp"

Lưu lượng quảng cáo Facebook phần lớn là điện thoại. *[Suy luận — chưa có số Meta của
chính chiến dịch này để đối chiếu.]*

Đo được trên repo, chắc chắn:
- `js/index.js:293` — mọi khách `(max-width:860px) and (pointer:coarse)` thấy dải
  `#mob-note`: *"**Trải nghiệm tốt nhất trên máy tính** — astroQ có bản đồ thiên hà 3D và
  mini-game cần màn hình rộng… hãy mở bằng **laptop hoặc PC** để chơi trọn vẹn nhé!"*
- `css/landing-app.css` — `.floaty` và `.iscene` đều `display:none` ở `max-width:880px`.

⇒ Một phụ huynh bấm quảng cáo trên điện thoại, hạ cánh, và **được chính trang web bảo là
hãy quay lại sau bằng máy tính**. "Quay lại sau" trong marketing nghĩa là không quay lại.

⚠️ **Đây không phải lý do để bỏ việc định vị lại** — hai chuyện độc lập, và cả hai đều
nằm trên cùng một đường đi. Nhưng nếu chỉ sửa câu chữ mà tỉ lệ không nhúc nhích thì đây
là chỗ nhìn tiếp, đừng kết luận "positioning không có tác dụng".

---

## 9. Đo trước khi sửa — dự án có sẵn bộ đo, và nó trả lời được đúng câu này

`admin-report.html` mục **"Người đến từ đâu"** (`#h-src`) vẽ theo từng nhãn chiến dịch:
**lượt đến → tài khoản đã kích hoạt → còn hoạt động 7 ngày**. Nguồn số: `POST /visit`
(`js/utm-beacon.js`, đếm **khách mới** chứ không đếm lượt bấm) đối chiếu với bộ đếm
server.

⇒ Câu *"người ta click nhưng không có hành động tiếp theo"* **kiểm được ngay hôm nay**,
không cần đoán: mở bảng đó, đọc hàng của chiến dịch AI.

⚠️ Nhưng phải biết bộ đo này **không** nói được gì:
- **Không có phân tích hành vi trang** — không đo được cuộn tới đâu, bỏ đi ở màn nào.
  Nên không có cách nào chứng minh "họ bỏ đi vì thấy Hệ Mặt Trời". Đó là **giả thuyết**,
  và cách kiểm duy nhất là **sửa rồi so hai chiến dịch**.
- Số của Meta luôn ≥ số ở đây (ghi rõ ở đầu `js/utm-beacon.js`) — đừng lấy hai con số của
  hai hệ mà tính ra một tỉ lệ.
- ⚠️ **Nhãn chiến dịch phải sống sót bộ lọc server** (`AstroqSV/Services/Campaign.cs`):
  chỉ `a-z 0-9 . _ -`, ≤24 ký tự/phần, ≤3 phần. Muốn so A/B thì đặt hai nhãn khác nhau
  **trước khi** chạy, ví dụ `fb/ads/ai-v1` và `fb/ads/ai-v2`.

---

## 10. Đề xuất câu chữ cụ thể

### 10a. `landing-app.html` — làm TRƯỚC (rẻ nhất, tác động lớn nhất, 0 chi phí SEO)

| Khoá | Đang là | Đề nghị |
|---|---|---|
| `badge` | "Bản đồ 3D tương tác" | **"Khoa học · Công nghệ · Vũ trụ"** |
| `hero_welcome` + h1 | "Chào mừng đến **AstroQ**" | giữ nguyên |
| `lead` | "Du hành qua Hệ Mặt Trời trong không gian 3D thời gian thực — xoay, phóng to và tìm hiểu từng hành tinh…" | **"Bắt đầu từ Hệ Mặt Trời, trẻ 8–15 khám phá thiên văn, AI và tư duy khoa học qua nhiệm vụ, bài đọc và trò chơi."** |
| `cta_try` | "Trải nghiệm ngay" | **"Bắt đầu khám phá"** |
| card 1 | 🪐 8 hành tinh | **🌌 Vũ trụ 3D tương tác** — Xoay, phóng to và bay tới từng hành tinh trong Hệ Mặt Trời 3D — đủ cả 8 hành tinh, mỗi chặng một nhiệm vụ. |
| card 2 | 🔭 Tương tác 3D | **🤖 AI & Công nghệ** — máy học từ đâu, robot cảm nhận thế nào, và vì sao chatbot sai mà nói rất chắc. |
| card 3 | ✨ Thông tin trực quan | **🧠 Tư duy khoa học** — quan sát, đặt câu hỏi, và kiểm chứng bằng nguồn thật. |
| footer | "AstroQ · Solar System Explorer" | **"AstroQ · Khoa học cho nhà khám phá trẻ"** |

⚠️ Câu thẻ 2 **cố ý** trích đúng nội dung đã có (`art-chatbot-confidently-wrong.js`) —
nó là lời hứa **đã trả trước bằng nội dung**, không phải lời hứa đi mượn.
⚠️ Thẻ 3 nói "kiểm chứng bằng nguồn thật" là dựa vào `srcQuote` + `check_srcquote.py`
(**91/91 câu dẫn đúng nguyên văn** theo mục 11 của đề xuất 19/08) — một trong ít lời hứa
marketing của dự án có bộ đo riêng chứng minh.
⚠️ Thẻ 1 **giữ lại con số "8 hành tinh"**. Con số cụ thể bán tốt hơn lời chung; cái phải
bỏ là việc nó chiếm cả ba thẻ, không phải bản thân con số.
⚠️ Sửa `I18N` thì phải sửa **cả `vi` và `en`** trong cùng file — thiếu một bên là đổi
ngôn ngữ xong trang nói ngược. Và `<title>` của trang này cũng nên theo
("AstroQ — Khám phá Hệ Mặt Trời" là mô tả cũ), dù nó `noindex` nên chỉ ảnh hưởng tab.

### 10b. `/` (`index.html`) — làm SAU, và cẩn thận hơn nhiều

**Việc rẻ và an toàn: DỜI, đừng viết lại.** Đưa `<ul class="pillars">` (đã có sẵn, đã có
CSS ở `css/index.css:258`, đã có 4 khoá i18n ở cả `vi` và `en`) **lên ngay dưới hero**,
trước `<section class="waitlist">`. Không đổi một chữ nào ⇒ không đụng SEO, không đụng
JSON-LD, không đụng FAQ. **Chỉ chuyển một khối DOM, và trẻ nhìn thấy AI ở màn đầu thay
vì màn thứ ba.**

Nếu muốn đi tiếp tới 3 trụ như đề xuất, thì đây là cái phải trả — **KHÔNG phải sửa một
chỗ**:

| Chỗ | Việc | Rủi ro |
|---|---|---|
| `index.html` `<ul class="pillars">` | 4 `<li>` → 3 | — |
| `css/index.css:258` | `repeat(4,…)` → `repeat(3,…)` | ⚠️ `.pillars li:nth-child(2/3/4)` gán **màu theo vị trí** — bỏ 1 trụ là màu trụ 4 mất, 3 trụ còn lại đổi màu |
| `js/index.js` khoá `p1..p4` | ở **cả `vi` và `en`** | thiếu một bên là hiện khoá thô |
| `<title>` · `og:title/description` · `twitter:*` | "Lượng Tử" → gì? | ⚠️ **đang xếp hạng bằng chính chuỗi đó** — đổi từ khoá của trang duy nhất được lập chỉ mục |
| JSON-LD `EducationalApplication.about` + `featureList` | 4 chủ đề | phải **khớp** phần hiển thị |
| JSON-LD `FAQPage` + `<details>` a3 | *"Bốn nhóm chủ đề chính"* | ⚠️ **khớp 1-1 là bắt buộc** (ghi trong chú thích HTML); sửa một bên là schema nói khác trang |
| `en/index.html` | sinh lại bằng `scratchpad/gen_home_en.py` | ⚠️ đừng sửa tay |
| `scratchpad/check_pages.py` | chạy lại | mục [32] đối chiếu số **100** với `Wallet.StarterBonus` |

⚠️⚠️ **Khuyến nghị của tôi: KHÔNG gộp 4 trụ thành 3 ở vòng này.** Bốn trụ hiện có
(Thiên văn · AI · Lượng tử · Robotics) đọc ra **đúng cùng một thông điệp** mà đề xuất
muốn — "đây là nền tảng STEM rộng, không phải web thiên văn" — mà **không phải chạm vào
`<title>`, hai khối JSON-LD, FAQ và bộ sinh EN**. Đổi 4→3 là trả giá SEO thật cho một
cái được về câu chữ; **dời khối lên trên** thì được gần hết cái lợi với giá gần bằng 0.

Việc duy nhất tôi đề nghị **sửa chữ** ở `/`: trụ số 3 hiện là *"Vật lý Lượng tử — Hạt,
sóng và những điều kỳ lạ nhất của vũ trụ"* nhưng chỉ có **3 bài + 1 câu**. Hoặc bổ nội
dung, hoặc đổi trụ đó thành **"Tư duy khoa học"** — trụ này có nội dung sẵn (mục 3), chỉ
là đang nằm dưới `cat:"ai"`.

---

## 11. Nội dung mới cần bao nhiêu

**Cho mục 10a + phương án "dời khối" ở 10b: 0 bài đọc, 0 câu quiz.** Toàn bộ lời hứa mới
đã có nội dung chống lưng (mục 2, 3). Đây là **lý do chính** tôi đồng ý với đề xuất — nó
không đẻ thêm nợ nội dung, mà **thu hồi nội dung đã trả tiền rồi nhưng chưa ai thấy**.

Nếu muốn "Tư duy khoa học" thành một nhánh thật (không chỉ là một nhãn):
- thêm `cat: "thinking"` vào **4 chỗ + 1 icon** (luật ở `docs/decisions/010` mục 3c:
  `cats` ở `library.html` · `CAT_ICON` · khoá `cat_thinking` ở **cả** `vi`/`en` · rule
  `.cat--thinking` ở `css/library.css` · icon mới ở `js/icons.js`);
- ⚠️ **rồi phải quyết một bài thuộc mấy `cat`.** `art-algorithmic-bias.js` là `ai` **và**
  tư duy phản biện. Cấu trúc hiện tại là **một `cat` cho một bài** ⇒ chuyển 5 bài sang
  `thinking` là **rút chúng khỏi chip AI**, làm chip AI mỏng đi đúng lúc đang muốn dày
  lên. *[Chưa kiểm chứng: có thể `library.html` chịu được `cat` dạng mảng — tôi chưa đọc
  kỹ `render()`.]* Việc này cần một vòng riêng, đừng gộp vào đợt sửa câu chữ.

**Nợ nội dung vẫn là nút thắt thật:** 190/870 câu, cổng mở bán ở `009` cần ≥300 ⇒ còn
**110 câu**. Đợt sửa landing này không được lấy công của việc đó.

---

## 12. Ảnh hưởng tới người chơi cũ

**Không.** Toàn bộ thay đổi là câu chữ + thứ tự DOM ở hai trang trước đăng nhập. Không
đụng hồ sơ, tiến độ, ví Purple Meteors, hay bất cứ khoá `localStorage` nào.

---

## 13. Cái tôi KHÔNG chắc

- **Chưa có số thật của chiến dịch AI.** Bảng "Người đến từ đâu" kiểm được ngay, nhưng
  tôi chưa đọc dữ liệu đó — mọi con số ở file này là số **kho nội dung**, không phải số
  chuyển đổi. **Chưa có bằng chứng nào nói tỉ lệ đăng ký sẽ tăng.**
- **[Suy luận]** "Bỏ đi vì thấy Hệ Mặt Trời" là giả thuyết hợp lý nhưng **không đo được**
  bằng bộ đo hiện có (mục 9). Giả thuyết cạnh tranh ở mục 8 (dải "hãy dùng máy tính")
  cũng chưa được loại trừ, và tôi không có cơ sở để nói cái nào lớn hơn.
- **Chưa tra** mức độ quan tâm AI so với thiên văn của phụ huynh Việt Nam, và **không
  kiểm chứng được** chủ trương AI của Bộ GD&ĐT năm học 2026–2027 mà đề xuất viện dẫn.
  Đó là tiền đề thị trường của đề xuất, không phải của bản review này — và bản review
  không phụ thuộc vào chúng: lập luận ở đây đứng được chỉ bằng *"kho nội dung đã có AI mà
  cửa trước không nói"*.
- **Chưa đo chi phí SEO** của việc đổi `<title>` — tôi không biết `/` đang xếp hạng bằng
  từ khoá nào, nên khuyến nghị "đừng chạm `<title>`" ở mục 10b là **thận trọng theo mặc
  định**, không phải kết luận từ số đo.

---

## 14. Việc, theo thứ tự

1. **Đọc bảng "Người đến từ đâu"** cho chiến dịch AI. 5 phút, và nó nói cái đang xảy ra
   có thật hay không.
2. **Sửa `landing-app.html`** theo mục 10a. Rẻ nhất, `noindex` nên 0 chi phí SEO, và là
   trang ngay trước nút đăng ký.
3. **Dời `<ul class="pillars">` lên trên khối waitlist** ở `index.html` + sinh lại
   `en/index.html` qua `gen_home_en.py`. Không đổi chữ.
4. **Đặt nhãn chiến dịch mới** (`fb/ads/ai-v2`) cho đợt quảng cáo sau khi sửa, để bảng
   nguồn so được hai bên. Không đặt nhãn mới thì không bao giờ biết việc sửa có tác dụng.
5. *(vòng sau)* Quyết trụ "Lượng tử": bổ nội dung, hay đổi thành "Tư duy khoa học".
6. *(vòng sau, riêng)* `cat: "thinking"` cho `library.html`, sau khi đã quyết chuyện một
   bài thuộc mấy `cat`.

---

## 15. ĐÃ LÀM — 26/08/2026 (viết thêm sau khi thực hiện)

Chủ dự án chốt: *"làm 10a"*. Đã làm **mục 10a**, và trong lúc đo thì lộ ra một lỗi bố
cục phải sửa kèm (mục 15b) — không sửa thì đợt này tự phá đúng nhóm máy nó nhắm tới.

### 15a. Câu chữ `landing-app.html`

Đổi ở **cả `vi` và `en`** trong hằng `I18N` nội trang, kèm chữ tĩnh trong DOM:

| Khoá | Trước | Sau |
|---|---|---|
| `<title>` / `title` | "AstroQ — Khám phá Hệ Mặt Trời" | "AstroQ — Vũ trụ, AI và tư duy khoa học" |
| `badge` | "Bản đồ 3D tương tác" | "Khoa học · Công nghệ · Vũ trụ" |
| `lead` | "Du hành qua Hệ Mặt Trời trong không gian 3D thời gian thực…" | "Bắt đầu từ Hệ Mặt Trời, trẻ 8–15 khám phá thiên văn, AI và tư duy khoa học qua nhiệm vụ, bài đọc và trò chơi." |
| `cta_try` | "Trải nghiệm ngay" | "Bắt đầu khám phá" |
| `f1_*` 🪐→🌌 | "8 hành tinh" | "**Vũ trụ 3D tương tác**" — *"Xoay, phóng to và bay tới từng hành tinh… đủ cả 8 hành tinh, mỗi chặng một nhiệm vụ."* |
| `f2_*` 🔭→🤖 | "Tương tác 3D" | "AI & Công nghệ" — *"…vì sao chatbot sai mà nói rất chắc"* |
| `f3_*` ✨→🧠 | "Thông tin trực quan" | "Tư duy khoa học" — *"…kiểm chứng bằng nguồn thật"* |
| `foot_tag` (**khoá mới**) | *(chữ tĩnh "AstroQ · Solar System Explorer", không có `data-i18n`)* | "AstroQ · Khoa học cho nhà khám phá trẻ" |

⚠️⚠️ **THẺ 1 SỬA LẠI TRONG NGÀY — chủ dự án bắt đúng lỗi.** Bản đầu tôi đặt tiêu đề thẻ
là *"Vũ trụ để khám phá"* rồi đẩy "xoay, phóng to" xuống cuối câu mô tả. Chủ dự án nói:
*"phần này cần phải nêu bật được tương tác 3D chứ, cái quan trọng nhất mà."* Đúng — và
đây là một cái bẫy của chính việc mở rộng định vị: **bản đồ 3D là thứ cụ thể nhất và
khác biệt nhất astroQ có** (thứ người ta không xem được ở một trang chữ), nên nó phải
đứng ở dòng người đọc lướt qua, không nằm ở vế sau của một câu. Mở rộng định vị là để
**THÊM nhánh**, không phải để pha loãng nhánh mạnh nhất. Bảng 10a ở trên đã sửa theo.

⚠️ `foot_tag` là khoá **mới**: dòng chân trang trước đây là chữ tĩnh **không dịch được**
— khách tiếng Việt vẫn đọc một dòng tiếng Anh, mà dòng đó lại thu cả sản phẩm về đúng
một nhánh ngay ở chân trang. Nay nó đi qua `applyTexts` như mọi chữ khác.

⚠️ Sửa luôn một chú thích đã trôi: khối JS quanh `#btn-try` còn gọi nút bằng nhãn cũ
("Trải nghiệm ngay"). Nay trỏ vào **khoá** `cta_try` thay vì chép lại nhãn — nhãn sẽ còn
đổi nữa, khoá thì không.

### 15b. ⚠️ Lỗi bố cục lộ ra khi đo — chip `.badge` chui dưới nút ngôn ngữ

`.lang-pick` là `position:fixed; top:20px; right:20px` nên **không chiếm chỗ trong
luồng**, còn `.badge` căn giữa và giãn theo độ dài chữ. Hai thứ gặp nhau ở góc trên phải.

**Đây là lỗi CŨ, nhưng câu chữ mới làm nó rộng ra** — đo trên Chromium thật:

| Chữ trong chip | Bề rộng | Đè nhau ở |
|---|---:|---|
| cũ "Bản đồ 3D tương tác" | 237px | ≤ **360px** |
| mới "Khoa học · Công nghệ · Vũ trụ" | 324px | ≤ **480px** |

⇒ Nó vỡ đúng trên nhóm máy mà chính đợt sửa này nhắm tới (mục 8: lưu lượng quảng cáo
Facebook phần lớn là điện thoại). Sửa câu chữ mà bỏ qua chỗ này là đổi một lời hứa rõ
hơn lấy một cái chip bị cắt ngang.

**Cách sửa:** `@media (max-width:620px){ .badge{margin-top:34px;} }` trong
`css/landing-app.css` (CSS ở file .css, không `<style>`, không inline — luật mục 2
`CLAUDE.md`). File này **chỉ `landing-app.html` nạp** (`grep -l landing-app.css *.html`
ra đúng một file), nên không trang nào khác bị ảnh hưởng.

⚠️ Đã bác hai cách khác, ghi lại để khỏi thử lại: **chừa `padding-right` ở `.wrap`** làm
lệch tâm cả `h1`/lead/nút — sửa một chip mà lệch cả trang; **ép `max-width` cho chip** ở
320px chỉ còn ~150px, tức chữ xuống hai dòng trong một viên thuốc.

### 15c. Đã đo sau khi làm

| Phép kiểm | Kết quả |
|---|---|
| `scratchpad/check_pages.py` | **1649 đạt / 0 hỏng** |
| Mọi khoá `data-i18n` có ở **cả** `vi` và `en` | 39/39, không lệch bên nào |
| Chip đè nút ngôn ngữ (vi/en × 11 bề rộng 320→1440 × 4 bề cao 600→1000) | **88/88 đạt, 0 đè**, không cắt đỉnh, không tràn ngang |
| Lỗi console / pageerror (vi + en, desktop + 390px) | **0** |
| Bấm `#btn-try` → mở đúng ô **Đăng ký** (`auth-register`) | đạt |
| Bấm VI→EN ngay trên trang → title/badge/thẻ/chân trang đổi hết | đạt |
| Chuỗi cũ còn sót trong file | chỉ còn trong **chú thích** trích lại bản cũ (cố ý) |

### 15d. Còn treo

- **Chưa deploy.** Thay đổi mới ở máy.
- **Chưa đặt nhãn chiến dịch mới** (`fb/ads/ai-v2`) — việc 4 ở mục 14. Không có nhãn mới
  thì bảng "Người đến từ đâu" không so được trước/sau, và **đợt sửa này sẽ không đo được
  là có tác dụng hay không**.
- **Chưa đọc bảng "Người đến từ đâu"** (việc 1) — vẫn chưa có bằng chứng nào về tỉ lệ
  chuyển đổi, đúng như đã ghi ở mục 13.
- `index.html` (mục 10b) **chưa đụng tới**.
