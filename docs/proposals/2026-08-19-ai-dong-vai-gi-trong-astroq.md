# Đề xuất: AI đóng vai gì trong astroQ

**Người viết:** Claude · **Ngày:** 19/08/2026
**Dựa trên:** `docs/research/2026-08-19-ai-trong-app-hoc-tap-cho-tre.md` (khung sáu vai)
**Trạng thái:** đang mở — chủ dự án quyết

> ⚠️ Khác các file trong `docs/proposals/` do ChatGPT/Gemini viết, mục "giả định" ở
> khuôn `_TEMPLATE.md` **đã được thay bằng SỐ ĐO từ chính mã nguồn** (mục 3). Tôi là
> phía đối chiếu mã nguồn theo `docs/PHAN-VAI.md`, nên để lại giả định chưa kiểm là
> bỏ đúng việc của mình.

---

## 1. Vấn đề cần giải

astroQ hiện **không có một dòng AI nào trong sản phẩm** (đã đo, mục 3). Câu hỏi không
phải "có nên thêm AI không" mà là: **trong sáu vai AI đang đóng ở thị trường, vai nào
giải được một vấn đề astroQ ĐANG CÓ, và vai nào chỉ thêm rủi ro?** Vấn đề lớn nhất của
dự án lúc này không phải thiếu tính năng — mà là **nợ nội dung**: 106/870 câu hỏi,
67/100 bài đọc, 23/30 thẻ Sổ Tay, và mỗi chặng nhiệm vụ tốn ~200 dòng viết tay.

---

## 2. Đề xuất, nói thẳng

**Làm hai vai. Hoãn một vai có điều kiện. Bác ba vai.**

| Vai | Quyết định | Lý do một câu |
|---|---|---|
| ⑤ Máy sản xuất nội dung, người biên tập | **LÀM — ưu tiên 1** | Nó giải đúng vấn đề đang có, và **0 bề mặt AI cho trẻ** |
| ② Điều độ khó | **LÀM — ưu tiên 2, và KHÔNG cần LLM** | Móc treo `lv` đã khai ở 71 file, **0 chỗ đọc** |
| ① Gia sư dẫn dắt | **HOÃN, có điều kiện đo được** | 15% adoption ở Khanmigo + astroQ là *tự học* |
| ③ Nghe trẻ đọc | **BÁC ở vòng này** | Giọng trẻ em tiếng Việt — Amira tiêu ~10 tr USD cho riêng bài toán này ở tiếng Anh |
| ④ Bạn hội thoại có kịch bản | **BÁC ở vòng này** | Nó THAY thứ đang là điểm mạnh, không bù thứ đang thiếu |
| ⑥ Bạn đồng hành tự do | **BÁC HẲN** | Ba phía độc lập đã trả lời: đánh giá, nền tảng, luật |

⚠️⚠️ **Điểm quan trọng nhất của cả đề xuất: hai vai được chọn đều KHÔNG có bề mặt AI
nào cho trẻ chạm vào.** Nghĩa là chúng không kéo theo bất kỳ nghĩa vụ nào ở mục 6
(công bố AI, nhắc nghỉ, quy trình tự hại, nhãn tuổi), và không mở ra ô chat nào để mô
hình nói sai với một đứa trẻ.

---

## 3. Số đo từ mã nguồn (thay cho mục "giả định")

Đo ngày 19/08/2026 trên chính repo:

| Điều | Số đo | Cách đo |
|---|---|---|
| AI trong sản phẩm | **0** | `grep -ri "openai\|anthropic\|gemini\|gpt-4\|claude-"` ra **2 kết quả, cả hai là CHÚ THÍCH** nhắc quy trình làm việc với ChatGPT/Gemini |
| Câu hỏi quiz | **106** / kế hoạch 870 | `ls js/quiz/*.js` |
| Câu có `srcQuote` (đã đối chiếu trang thật) | **71** | `grep -l srcQuote js/quiz/*.js` |
| Bài đọc | **67** / kế hoạch 100 | `ls js/article/*.js` |
| Thẻ Sổ Tay | **23** / kế hoạch 30 | `grep -c 'id: *"term_' js/codex-terms.js` |
| Trường `lv` (độ khó câu hỏi) | khai ở **71/106** file, **0 chỗ ĐỌC** | `quiz-index.js` chỉ *gán* nó vào object; `game-dodge.html` là biến trùng tên |
| Nội dung một chặng nhiệm vụ | `mission-orbit.html` **985 dòng / 5 chặng** ≈ 197 dòng/chặng (chưa tính vỏ 823 dòng dùng chung) | `wc -l` |
| Bộ đo đối chiếu trích dẫn với trang nguồn | **có** (`check_srcquote.py`) | đã có sẵn |
| `AstroQDepth` (hai bậc độ sâu junior/senior) | **7 file đọc** | `grep -rln AstroQDepth` |
| Báo cáo phụ huynh | `GET /me/report` + `POST /me/report/email` (SES) | `MeEndpoints.cs:1045,1077` |
| Doanh thu | **0** — `SALE_OPEN` không khai trong `template.yaml` | `template.yaml:64` |

⚠️ **Số cuối là số quyết định nhịp độ:** app **chưa thu một đồng nào**, nên mọi chi phí
LLM là chi phí thuần. Vai ⑤ tiêu tiền **một lần lúc soạn nội dung**; vai ① tiêu tiền
**mỗi lần một đứa trẻ mở miệng**, mãi mãi.

---

## 4. Vai ⑤ — LÀM: AI soạn nháp, người và bộ kiểm giữ cửa

**Vấn đề nó giải:** 764 câu hỏi và 33 bài đọc còn thiếu. Đợt 1 do Gemini soạn đã đo
được tỉ lệ hỏng thật: **13/40 câu trượt** (ghi ở nhật ký). Tức AI **không** thay được
người ở đây — nhưng nó thay được phần *soạn nháp*.

**Cách làm — dùng lại đúng đường ống đã có, không dựng cái mới:**

1. AI soạn nháp theo đề bài ở `docs/PHAN-VAI.md` (đã có sẵn quy trình này).
2. **Cửa kiểm 1 — máy:** `check_quiz_bank.py` + `check_srcquote.py` (đã có) đối chiếu
   **từng câu trích với trang nguồn thật**, kiểm URL trả 200, kiểm phân bố đáp án.
3. **Cửa kiểm 2 — người:** giữ nguyên. Nghiên cứu nói thẳng: *"grounding cắt được
   đáng kể chứ không bao giờ về 0, nên cửa người là **không phải tuỳ chọn**"*.

**Việc code cần làm: gần như bằng 0.** Đường ống đã tồn tại. Thứ cần thêm là **kỷ
luật**, không phải tính năng.

⚠️ **Ba luật KHÔNG được nới**, vì cả bốn lần suýt bịa của dự án đều nằm đúng ở đây
(Nam Cực · IAU · CHNOPS · "170 km"): *mở trang nguồn ra đọc rồi mới viết* · *chỗ nào
trang không nói thì KHÔNG viết* · *một URL trả 200 vẫn có thể là nguồn sai*.

---

## 5. Vai ② — LÀM: nối `lv`, và nó KHÔNG cần LLM

⚠️⚠️ **Đây là chỗ tôi cho là đáng làm nhất, và nó không phải "thêm AI" — nó là DỌN MỘT
MÓN NỢ.** Trường `lv` được khai ở **71 file câu hỏi** từ 25/07/2026 với **0 chỗ đọc**.
Chú thích trong `quiz-index.js` ghi rõ đích đến: *"server tính cấp độ rồi client rút đề
theo cấp độ"*.

**Cách làm:**
- Server đã biết cấp độ trẻ (`Achievements.Level(xp)`), đã biết `bests`, đã biết
  `terms` đã trả lời đúng.
- `quiz.html` **cố ý không nạp SDK Firebase** nên không có token → phải đi qua **cache
  do dashboard ghi**, đúng khuôn `astroq-route-gate` và `astroq-mission-steps` đã dựng
  hai lần.
- `pickKeys()` (đã có, đã chống trùng THẺ) nhận thêm một tham số lọc theo `lv`.

**Cái được:** đúng thứ meta-phân tích gọi là *personalized pacing* — thành phần xuất
hiện trong **mọi** ca có bằng chứng dương. **Cái mất: 0 rủi ro trẻ-gặp-AI, 0 đồng
inference.**

⚠️ Nhưng phải nói rõ: **đây là adaptive bằng LUẬT, không phải bằng mô hình.** Gọi nó
là "AI" trên trang bán hàng là nói quá — và một sản phẩm cho trẻ em nói quá về AI là
đúng thứ FTC đang điều tra (mục 6).

---

## 6. Vai ① — HOÃN, và điều kiện để mở lại phải ĐO ĐƯỢC

Gia sư kiểu Khanmigo là vai hấp dẫn nhất, và tôi vẫn đề nghị **hoãn**, vì bốn số đo:

1. **15% adoption.** Khan Academy phát hiện chỉ 15% học sinh có Khanmigo thật sự dùng.
   astroQ đã có **ba** tiền lệ mã chết vì không ai gọi tới (`AstroQRanks.ALL` ngủ 8
   ngày · `lv` 71 file 0 chỗ đọc · `termsData.ts` phải sửa hai lần).
2. **g = 0,401 nhưng "học có giáo viên dẫn cao hơn hẳn học tự định hướng."** astroQ là
   *tự học ở nhà, không ai dẫn* — tức đúng nhánh yếu của bằng chứng.
3. **Không có tiền lệ ở thiên văn.** Mọi ca có bằng chứng đều ở **toán** và **đọc** —
   hai môn có thang đo chuẩn hoá. Thiên văn không có thang đo, nên **không đo được là
   nó có tác dụng hay không**, mà dự án này ra quyết định bằng số đo.
4. **Chi phí là chi phí mỗi lượt, và doanh thu đang bằng 0.**

**Điều kiện mở lại (chốt trước, đo sau — đừng để "cảm thấy đến lúc"):**
- Nội dung đủ để có gì mà dẫn: **≥300 câu hỏi** và **≥3 nhiệm vụ** (đúng mốc `009` đã
  đặt cho việc mở bán);
- **đã bán được** — tức có nguồn bù chi phí mỗi lượt;
- và khi làm thì **bó đúng khuôn Khanmigo**: không đưa đáp án · **có bộ kiểm riêng cho
  phần định lượng** (Khanmigo có "math agent" kiểm phép tính; astroQ sẽ cần một bộ kiểm
  đối chiếu với `learningdata/`) · đọc được `terms`/`bests` để biết trẻ đã nắm gì · và
  **chỉ trong phạm vi một chặng đang chơi**, không phải một ô chat tự do.

---

## 7. Vai ③④ — BÁC ở vòng này (không phải bác vĩnh viễn)

**③ Nghe trẻ đọc.** Amira đang cùng Digital Promise chi **~10 triệu USD** cho riêng bài
toán nhận giọng **trẻ em nói tiếng Anh**. *[Suy luận]* Tiếng Việt có thanh điệu và ít
dữ liệu giọng trẻ hơn hẳn, nên đây là bài toán khó hơn ở một dự án nhỏ hơn nhiều lần.
Thêm nữa astroQ **không dạy đọc** — nó dạy thiên văn; kỹ năng mà ③ chấm không nằm trong
mục tiêu của app.

**④ Bạn hội thoại có kịch bản.** Đây là chỗ dễ nhầm nhất, nên nói rõ: astroQ **đã có**
Comet và Byte với lời thoại viết tay, và lời thoại đó là chỗ **mang bài học** — bốn cái
bẫy nội dung của bước ② nhiệm vụ 01, câu bác bỏ "vì gần Mặt Trời hơn" ở bước ③, câu nói
thật *"vành khí quyển đang được vẽ dày quá"*. Thay nó bằng văn bản sinh ra là **đổi một
điểm mạnh đã trả giá để lấy một rủi ro mới**.

⚠️ Và một chi tiết kỹ thuật đáng ghi: Lily của Duolingo **có bộ nhớ xuyên phiên** —
theo đúng luật Roblox thì đó là *extended interaction*, tức **nhãn Restricted, dưới 18
không vào được**. Nếu vòng sau muốn làm ④, thì **không được có bộ nhớ xuyên phiên**, và
phải giữ đủ bốn nhịp của Duolingo (mở đầu định trước · câu hỏi đầu sinh riêng · kiểm
giữa cuộc · **tự đóng**).

---

## 8. Vai ⑥ — BÁC HẲN, và đây là quyết định pháp lý chứ không phải thẩm mỹ

Ba phía độc lập đã trả lời:
- **Tổ chức đánh giá:** Common Sense Media — social AI companion **rủi ro không thể
  chấp nhận với người dưới 18**, *không nên dùng*. Đồ chơi AI: **27% đầu ra không phù
  hợp với trẻ** (tự hại, ma tuý, hành vi nguy hiểm).
- **Nền tảng lớn nhất dành cho trẻ:** Roblox dán nhãn `Restricted` cho AI chat liên tục
  / có bộ nhớ → **dưới 18 không vào được**.
- **Luật:** California SB 243 (hiệu lực 01/01/2026) — công bố đây là AI · **nhắc nghỉ
  mỗi 3 giờ** với trẻ vị thành niên · công bố *có thể không phù hợp với trẻ* · quy trình
  xử lý khi trẻ nói tới tự hại · **1.000 USD/vi phạm** + quyền khởi kiện riêng.

Và phụ huynh — nhóm trả tiền cho astroQ theo `009` — **50% không muốn thiết bị làm chỗ
nương tựa cảm xúc cho con** (chỉ 19% muốn), **83% lo về thu thập dữ liệu**.

⇒ Với một app cho trẻ 8–15, vai ⑥ **không mang lại thứ gì mà ①–⑤ không làm được**, mà
mang theo toàn bộ nghĩa vụ trên. **Không làm.**

---

## 9. Việc code phải làm (nếu chốt mục 4 + 5)

**Vai ⑤ — 0 dòng code sản phẩm.** Chỉ là kỷ luật quy trình + hai bộ kiểm đã có.

**Vai ② — ước lượng, cần đo lại khi làm:**

| Chỗ | Việc | Ghi chú |
|---|---|---|
| `AstroqSV/Services/Achievements.cs` | thêm `lv` mục tiêu vào `Snapshot` | server đã có `Level(xp)`; **đừng để client tự tính** |
| `js/progress.js` | ghi cache `astroq-quiz-lv` | đúng khuôn `astroq-route-gate` |
| `js/quiz-index.js` | `pickKeys()` nhận bộ lọc `lv` | giữ nguyên phép chống trùng THẺ |
| `quiz.html` | đọc cache, không nạp SDK | trang này **cố ý** không có token |
| `scratchpad/check_quiz_split.py` | phép kiểm: rút đề theo `lv` không bao giờ trả về **rỗng** | 35/106 câu **chưa có `lv`** — lọc chặt là hết câu |

⚠️⚠️ **Cái bẫy thật của vai ②: 35 câu chưa khai `lv`.** Lọc theo `lv` mà không có đường
lùi thì một cấp độ nào đó sẽ ra **0 câu** và trẻ mở quiz lên thấy trang trống — đúng
lớp lỗi im lặng dự án đã trả giá nhiều lần. Đường lùi phải là: **thiếu câu ở cấp đó thì
nới ra cấp lân cận**, không phải trả về rỗng.

---

## 10. Cái tôi KHÔNG chắc

- **Chưa tra luật Việt Nam** về AI với trẻ em và dữ liệu cá nhân của trẻ. Toàn bộ phần
  pháp lý ở mục 6/8 là **Mỹ/California** — nó cho biết *ngành đang đi hướng nào*, không
  tự động áp cho astroq.org.
- **Chưa đo chi phí thật** một lượt gia sư AI ở quy mô astroQ. Con số "inference gần như
  không đáng kể" là của người khác, ở quy mô khác.
- **Không có số nào về giữ chân.** Không nguồn nào cho biết tính năng AI làm trẻ quay
  lại nhiều hơn — chỉ có số về *thành tích* và *tỉ lệ dùng*. Nên nếu mục tiêu là D30
  (điều kiện mở bán ở `009`), **không có bằng chứng nào nói AI giúp được**.
- **Con số 764 câu còn thiếu là theo kế hoạch 870 của `docs/decisions`** — nếu kế hoạch
  đó đổi thì vai ⑤ nhỏ đi tương ứng.

---

## 11. ĐÃ LÀM — 19/08/2026 (viết thêm sau khi thực hiện)

Chủ dự án chốt: *"tập trung trả khoản nợ nội dung đi"* rồi *"và làm vai 2"*. Đã làm cả hai
trong cùng lượt, vì đo ra chúng là **một việc**, không phải hai.

### Chỗ hai việc gặp nhau
Bảng số liệu ở mục 3 nói "35/106 câu chưa có `lv`". Đo sâu thêm một bước
(`scratchpad/gap_lv.py`, mới) thì thấy điều quan trọng hơn: **18 trong 23 thẻ Sổ Tay thiếu
hẳn một hoặc hai cấp độ — 20 chỗ thiếu**. `term_black_hole` có cả hai câu ở cấp 2;
`term_meteor` và `term_meteorite` là {2,3}, không có cấp 1 nào.

⇒ Nên "trả nợ nội dung" ở lượt này **không phải rải đều cho đủ số**, mà là lấp đúng 20 chỗ
ấy. Kết quả: bộ lọc theo cấp đi từ *gần đúng* thành **đúng tuyệt đối** — đo được trên
Chromium thật, cấp 1 ra **100%** câu lv1 (trước khi lấp: 72,9%, và 27,1% câu lv2 lọt vào
đề của trẻ mới).

### Con số thật, đo sau khi làm
| Việc | Trước | Sau | Đo bằng |
|---|---|---|---|
| Câu hỏi quiz | 106 | **126** | `ls js/quiz/*.js` |
| Câu khai `lv` | 71 | **126** (đủ 100%) | `split_quiz_bank.py` |
| Thẻ đủ cả 3 cấp | 5/23 | **23/23** | `scratchpad/gap_lv.py` |
| Chỗ ĐỌC `lv` | **0** | server + mục lục + `quiz.html` | mục [31] `check_pages.py` |
| Câu dẫn đúng nguyên văn | 71 | **91/91** | `check_srcquote.py` |

### Vai ② đi hết đường, không dừng ở client
- `AstroqSV/.../Services/Adapt.cs` (mới) — luật cấp độ ở **một chỗ duy nhất**. Tín hiệu là
  **tỉ lệ trả lời đúng**, không phải `xp`/`level` (đúng cảnh báo ở mục 7: `level` đo *thời
  gian đã chơi*). Mốc cấp 2 **trỏ vào** `Wallet.QuizPassRatio` chứ không gõ lại số.
- Mốc cấp 3 để ở **75%**, không phải 85% — và lý do là số học, có kiểm: một đứa trẻ đã trả
  lời 100 câu đúng 70 thì với mốc 75% cần thêm **20 câu** (4 lượt) để lên cấp; với mốc 85%
  cần thêm **100 câu**, tức cấp độ đóng băng và chữ "tự điều chỉnh" thành nói sai.
- `js/progress.js` — cache `astroq-quiz-lv` **đóng dấu uid**, đúng khuôn `astroq-route-gate`.
  Đây là điều mục 5 đòi trước khi được phép nối `lv`.
- `pickKeys(n, lv)` — cấp độ quyết định **chọn câu nào trong thẻ**, KHÔNG quyết định thẻ nào
  được vào đề. Nhờ vậy số thẻ ra đề không đổi theo cấp (đo: 23 thẻ ở cả ba cấp), tức độ khó
  tự điều chỉnh **không thu hẹp kiến thức** của trẻ.

### Còn treo
- ⚠️ **Backend chưa deploy.** `Adapt.cs` build sạch nhưng `aws lambda update-function-code`
  vẫn bị bộ phân loại quyền chặn (từ 16/08). Chưa deploy thì `progress.quizLv` không tồn
  tại, `absorbQuizLv` trả `false`, và Quiz rơi về "chưa biết cấp" — **an toàn, đã đo**
  (`smoke_quiz_lv.py` mục [1]: 0 lỗi trang, vẫn rút đủ đề). Nhưng cũng có nghĩa **vai ②
  chưa có tác dụng với người dùng thật** cho tới khi deploy được.
- Nợ nội dung còn lại: **744/870 câu**, cổng `009` cần ≥300. Nghĩa là còn **174 câu** nữa
  mới tới cổng mở bán.
