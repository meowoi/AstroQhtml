# Đề xuất: làm astroQ hấp dẫn nhất với trẻ 8–15 — đọc nghiên cứu rồi đối chiếu mã nguồn

**Người viết:** Claude · **Ngày:** 2026-08-12
**Vai:** tra nguồn · đối chiếu mã nguồn · ước lượng chi phí (`docs/PHAN-VAI.md`)

> ⚠️ **Mức tin cậy của từng nguồn được ghi ngay tại chỗ.** Một bài tôi **đọc được toàn văn**;
> phần còn lại tôi **chỉ đọc bản tóm tắt kết quả tìm kiếm**, và một nhóm số là **blog thương
> mại** — mức đó không đủ để chốt một quyết định, chỉ đủ để đặt câu hỏi. Xem mục 7.

---

## Kết luận ngắn

**Dải 8–15 không phải một đối tượng — nó vắt qua đúng chỗ trẻ con đổi kiểu chơi, và mốc đó là
khoảng 11 tuổi.**

Bài duy nhất tôi đọc được toàn văn ([Game Developer — *Children and their desired game
experiences*](https://www.gamedeveloper.com/business/children-and-their-desired-game-experiences-a-developmental-look-at-game-aesthetics))
nói ba câu, và cả ba đều đổi thiết kế:

- *"Personal challenge is specifically preferred over social competition during middle
  childhood (7-11)"* — **thử thách với chính mình**, không phải với người khác.
- *"Social competition has shown to become pleasantly engaging from the age of 11"* — từ 11
  tuổi thì **ganh đua mới thành thứ vui**.
- *"The need for thrill is seen mostly during ages 11 to 16"* và **nhu cầu thể hiện bản thân**
  (`self-expression`) chạy suốt **7–16** qua "clothing, music, and art".

⇒ Dự án **đã tự tìm ra đúng mốc này một lần rồi**, bằng đường khác: NASA xuất bản cùng một chủ
đề Microgravity thành **hai bản K-4 và 5-8**, và `docs/proposals/…-hap-dan.md` mục 15 kết luận
*"mỗi thẻ một thí nghiệm, hai độ sâu lời giải thích"*. Nghiên cứu về **chơi** vừa nói y hệt thế
về **chơi**. Hai đường độc lập chỉ vào cùng một chỗ là tín hiệu đáng tin nhất trong cả file này.

**Việc đáng làm nhất không phải thêm nội dung — mà là làm cho thứ đã có phục vụ được cả hai đầu
dải.** astroQ hiện phục vụ rất tốt đầu dưới (thử thách cá nhân, sưu tập, không thua cuộc) và
**gần như không phục vụ đầu trên** (0 ganh đua, 0 thể hiện bản thân, 0 thrill).

---

## 1. Ba nhu cầu tâm lý — và astroQ đang thiếu đúng một cái

Các phân tích tổng hợp về học-qua-chơi đều quy về **thuyết tự quyết** (competence · autonomy ·
relatedness). *[Chưa đọc toàn văn — chỉ đọc tóm tắt kết quả tìm kiếm]* Hai điểm đáng ghi:

- Học-qua-chơi có hiệu ứng **trung bình** lên kết quả **nhận thức**, nhưng **nhỏ** lên
  **động lực–cảm xúc**. Tức *"làm thành game"* không tự động làm trẻ thích hơn.
- Cơ chế trung gian là **ba nhu cầu** kia được thoả.

Đối chiếu với mã nguồn:

| Nhu cầu | astroQ hôm nay | Đo được ở đâu |
|---|---|---|
| **Năng lực** (competence) | **Mạnh.** 22 huy hiệu · 21 mẫu vật · 50 cấp · 10 bậc · thanh tiến độ mọi nơi · thả sai không phạt | `Achievements.cs` · `Specimens.cs` · `js/ranks.js` |
| **Tự chủ** (autonomy) | **Trung bình.** Chọn nhân vật · chọn chòm sao · chạm châu lục thứ tự nào cũng được · nút "Tìm hiểu thêm" | `select.html` · `mission-earth.html` |
| **Kết nối** (relatedness) | ⚠️ **Gần như 0.** Không bạn bè, không bảng xếp hạng, không khoe, không chơi cùng ai. Chỉ có Comet & Byte | `grep` toàn repo: 0 tính năng xã hội |

⇒ **Kết nối là chỗ trống lớn nhất, và nó cũng là chỗ nguy hiểm nhất** (sản phẩm cho trẻ em).
Mục 4 đề xuất ba đường có kết nối mà **không cần** bạn bè hay chat.

---

## 2. Đối chiếu tuổi ↔ thứ astroQ đang có

| Nghiên cứu nói | astroQ đang | Khoảng cách |
|---|---|---|
| 7–11: **thử thách cá nhân** hơn ganh đua | đúng như vậy — kỷ lục cá nhân, không có bảng xếp hạng | ✅ khớp |
| 8+: bắt đầu thích **thực tế** hơn tưởng tượng | ảnh vệ tinh NASA thật, số liệu có nguồn, toạ độ thật | ✅ khớp, và đây là **thế mạnh lớn nhất** |
| 11+: **ganh đua** thành thứ vui | 0 cơ chế | ❌ trống |
| 11–16: **thrill** (cảm xúc mạnh) | 3 mini-game có, nhưng nhiệm vụ thì **không có trạng thái thua** | ⚠️ một nửa |
| 7–16: **thể hiện bản thân** qua trang phục/đồ vật | 10 nhân vật, đổi được; bàn trưng 3 mẫu vật | ⚠️ có hạt mầm, chưa lớn |
| 7–16: **bạn bè quan trọng** | 0 | ❌ trống |
| 11–16: **muốn độc lập / phá luật** | 0 | ❌ trống *(và có lẽ nên để trống)* |

---

## 3. Bốn số đo từ mã nguồn làm đổi thứ tự ưu tiên

### 3.1 ⚠️ Nhiệm vụ **không phải** động cơ tiến bộ — quiz và game mới là

| | XP | Nguồn |
|---|---|---|
| **Cả nhiệm vụ Trái Đất** (7 chặng) | **355** | `Missions.cs` (235 bước + 120 chốt) |
| Một lượt quiz đúng 5/5 | **180** | `XpPerCorrectAnswer 20 ×5 + 30 + 50` |
| Xong 100% Trái Đất → | **cấp 3 / 50**, vẫn bậc Tân Binh | `XpForLevel(n)=100(n−1)n/2` |

⇒ **Nội dung đắt nhất của dự án (~3.000 dòng) cho XP bằng hai lượt quiz.** Không đề nghị tăng
XP nhiệm vụ (nó sẽ làm thang cấp mất nghĩa) — đề nghị **nhìn đúng vai**: *nhiệm vụ là NỘI DUNG,
mini-game và quiz là NHỊP QUAY LẠI*. Điều đó đổi hẳn câu trả lời cho "làm gì tiếp theo".

### 3.2 ⚠️ Một mini-game rẻ hơn một nhiệm vụ, và nó là thứ trẻ 11+ quay lại

```
game-constellation.html  1.045 dòng
game-dodge.html          1.191 dòng
game-defender.html       1.400 dòng
mission-earth.html       2.955 dòng   ← 7 chặng
```

Một mini-game ≈ **1.200 dòng** ≈ chi phí **~3 chặng** nhiệm vụ, nhưng nó chơi lại **vô hạn lần**
còn một chặng thì chơi một lần. Hiện **3/6 thẻ game đã mở**, 3 thẻ còn `soon` và **sẽ miễn phí**
(`js/locks.js`: `plan: null`).

### 3.3 ⚠️⚠️ Thiên thạch tím có **nguồn thu nhưng chỉ một cửa tiêu**

```
Wallet.Fees = { dodge: 5, defender: 5, constellation: 3 }   ← TOÀN BỘ chỗ tiêu tiền
```

Trẻ xong nhiệm vụ Trái Đất có **235 tt**, tức **47 lượt** Né Thiên Thạch. Một nền kinh tế mà tiền
chỉ dùng để trả phí vào cửa thì **tiền không phải phần thưởng, nó là vé**. Đây là hạt mầm bị bỏ
phí lớn nhất — xem đề xuất **B2**.

### 3.4 ✅ Đã đo được D1/D7/D30 — điều kiện ở `009` đã lỗi thời

`docs/decisions/009` ghi *"D30 chưa đo được (chưa ra mắt)"*. Nhưng `Services/Insights.cs:455`
**đã tính retention D1/D7/D30** theo kiểu **trôi** (*"trong số người đã đăng ký đủ N ngày, bao
nhiêu người có việc ở ngày thứ N hoặc sau đó"*), và `admin-report.html` đã vẽ nó. Thứ còn thiếu
là **người dùng**, không phải công cụ.

⚠️ Kèm một câu hỏi cho chủ dự án: `009` đặt cổng mở bán ở **D30 ≥ 20%**. *[Chưa kiểm chứng —
nguồn là blog thương mại, không phải nghiên cứu]* các bảng benchmark thị trường nói app **giáo
dục** thường có **D30 dưới 3%**, và trung vị mọi ngành khoảng **7%**. Nếu con số đó đúng thì
**20% là một cái cổng cao gấp ba lần mức tốt của cả ngành** — tức có thể tự khoá mình không bao
giờ mở bán. Đề nghị: **đo trên chính 500 người Sáng Lập trước, rồi mới chốt ngưỡng**, đừng chốt
ngưỡng bằng một con số chưa ai kiểm.

---

## 4. Đề xuất — xếp theo lợi/chi phí

### Nhóm A — Phục vụ cả hai đầu dải tuổi *(việc quan trọng nhất)*

**A1. Hai độ sâu, chọn bằng TUỔI KHAI BÁO — không suy từ cấp độ.** *(chi phí: nhỏ)*
Thêm một bước ở `select.html`: *"Bạn bao nhiêu tuổi?"* → hai hồ sơ **Tập Sự (8–10)** / **Phi
Hành Gia (11–15)**, đổi được bất cứ lúc nào ở `profile.html`.
⚠️ **Đừng dùng `level`** — nó đo **thời gian đã chơi**, không đo tuổi; một đứa 15 tuổi vừa đăng
ký là cấp 1 và sẽ nhận bản viết cho trẻ 8 tuổi (cảnh báo này đã ghi ở đề xuất Phòng Nghiên Cứu
mục 18.2). Nút *"Tìm hiểu thêm →"* đã dựng ở lab **giữ nguyên** — tuổi chỉ quyết **mặc định**.
Cái được: mọi nội dung sau này chỉ cần khai hai độ sâu là phục vụ được cả dải; cái mất: một câu
hỏi thêm ở màn đăng ký.

**A2. Đầu trên của dải cần một thứ đầu dưới không cần: được so sánh.** *(chi phí: vừa)*
Từ 11 tuổi ganh đua mới thành thứ vui — nhưng **so với chính mình theo thời gian** là dạng an
toàn nhất và **dữ liệu đã có sẵn**: `Insights`/nhật ký đã ghi từng sự kiện kèm mốc thời gian.
Đề nghị **"Nhật ký phi hành"**: tuần này so tuần trước (số câu đúng, độ chính xác, kỷ lục game).
⚠️ **Không phải bảng xếp hạng giữa các trẻ** — xem mục 5.

### Nhóm B — Cho trẻ nhiều quyết định hơn, gần như không tốn nội dung mới

**B1. Buồng lái là của con.** *(chi phí: nhỏ–vừa)*
`specimen-vault.html` đã có **bàn trưng 3 mẫu vật** và dashboard đã là buồng lái thật. Mở rộng:
đặt tên phi thuyền · chọn ảnh nền/màu đèn HUD · trưng huy hiệu. **Thể hiện bản thân** là nhu cầu
chạy suốt 7–16 tuổi, và đây là cách rẻ nhất để có nó mà không cần một dòng nội dung khoa học nào.

**B2. Cho Thiên thạch tím một cửa hàng — chỉ đồ trang trí.** *(chi phí: vừa)*
Nối thẳng vào B1: tt mua **trang phục · sơn tàu · khung ảnh hồ sơ · icon**. Ba luật cứng:
- ⛔ **Không bán lượt chơi, không bán gợi ý, không bán XP** — `Wallet.cs` đã chốt tt chỉ đến từ
  *quiz đạt* và *thu trong game*; bán lợi thế là phá đúng vòng lặp "muốn chơi thì phải học".
- ⛔ **Không hộp ngẫu nhiên, không gacha** (mục 5).
- ✅ **Thấy trước mình mua gì** — giá hiện rõ, mua là nhận đúng thứ đã xem.

**B3. Ba mini-game còn lại — rẻ hơn một nhiệm vụ mới và đúng thứ giữ nhịp quay lại.**
*(chi phí: vừa, ~1.200 dòng/game, 0 nội dung khoa học mới)*
Chúng đã có chỗ trên lưới, đã hứa **miễn phí**, và `css/game-shell.css` + `js/game-shell.js` lo
sẵn khung · HUD · lời nhắc xoay ngang · thanh cấp.

### Nhóm C — Kết nối mà không cần bạn bè

**C1. Khoe với bố mẹ, không khoe với người lạ.** *(chi phí: nhỏ)*
`parent.html` + báo cáo tuần đã chạy. Thêm một nút *"Cho bố mẹ xem"* ở màn tổng kết → sinh một
**thẻ thành tích** (ảnh/khối HTML) mở trong máy. Đây là **relatedness qua gia đình** — nhu cầu
được thoả, rủi ro bằng 0.

**C2. Comet & Byte phản ứng thật.** *(chi phí: nhỏ, nhưng CHỜ ẢNH)*
`js/game-shell.js` **đã có sẵn móc** `cheer`/`ouch` trên `.gs-mate` và **chưa ai dùng**, vì mỗi
linh vật hiện chỉ có **một** ảnh. Cần chủ dự án đặt thêm 2 ảnh biểu cảm mỗi nhân vật.
⚠️ Đừng nối móc đó trước khi có ảnh — một linh vật "phản ứng" bằng đúng một khuôn mặt thì tệ
hơn không phản ứng.

**C3. "Phi hành đoàn đầu tiên".** *(chi phí: nhỏ)*
`009` đã hứa 500 người waitlist một chỗ trong danh sách này. Một trang tĩnh đọc tên (chỉ **biệt
danh phi hành gia**, không email, không tuổi) cho cảm giác *"mình thuộc về một nhóm"* — dạng kết
nối duy nhất không cần thu thêm dữ liệu nào của trẻ.

### Nhóm D — Nhịp quay lại hằng ngày, nếu làm thì phải làm tử tế

**D1. Việc hằng ngày** — đã có đề bài từ 05/08 nhưng **chưa dựng** (server chưa nhận `reason:
"daily"`, `POST /me/progress` trả **400**). Đây là cơ chế quay-lại mạnh nhất còn thiếu.

**D2. Chuỗi ngày — CÓ ÂN HẠN, hoặc đừng làm.** *(chi phí: vừa)*
*[Chưa đọc toàn văn — tóm tắt từ hai bài hội thảo ACM]* nghiên cứu về **thiết kế lừa dối** với
trẻ em xếp **Daily Rewards** và **Playing by Appointment** vào nhóm mẫu bị nêu tên nhiều nhất, và
ghi nhận trẻ **"thức dậy sớm để giữ chuỗi"**, **"ăn trong lúc chơi"** để vừa giữ chuỗi vừa kịp
việc thật. Chính các bài đó nêu hướng lành mạnh: **grace periods** (ân hạn để trẻ ưu tiên gia
đình/trường mà không bị phạt) và **effort-to-reward legible** (nói trước phải bỏ ra bao nhiêu).
⇒ Nếu làm chuỗi: **2 ngày ân hạn mỗi tuần · không bao giờ về 0 · không đếm ngược · không thông
báo giục · nói trước luật.** Không làm được đủ năm điều đó thì **đừng làm chuỗi** — dự án đã một
lần tự bỏ "CHUỖI BAY 7 ngày" vì nó là **số bịa**; làm lại nó thành số thật mà không có ân hạn thì
đổi một lời nói dối lấy một cái bẫy.

---

## 5. Năm thứ CỐ Ý không đề xuất

1. ⛔ **Bảng xếp hạng giữa các trẻ.** Trước 11 tuổi *"personal challenge is specifically
   preferred over social competition"*, và trẻ ở tuổi đó **đang hình thành niềm tin về năng lực
   của chính mình**. Một cái bảng xếp trẻ 8 tuổi dưới trẻ 15 tuổi dạy nó rằng nó dở.
2. ⛔ **Hộp ngẫu nhiên / gacha / loot box.** Nằm thẳng trong danh sách mẫu thiết kế lừa dối bị
   nêu tên với trẻ em.
3. ⛔ **Đồng hồ đếm ngược tạo khan hiếm giả** (*artificial deficit*, *playing by appointment*).
4. ⛔ **Bán lợi thế học tập bằng tiền** — trái luật đã chốt ở `009`.
5. ⛔ **Chat / kết bạn / nội dung do người dùng đăng.** Với trẻ 8–15 đây là cả một hạng mục an
   toàn và pháp lý riêng; C1–C3 lấy được phần lớn giá trị mà không mở cửa đó.

---

## 6. Thứ tự đề nghị

| # | Việc | Chi phí | Vì sao đứng đây |
|---|---|---|---|
| 1 | **A1** hai độ sâu theo tuổi | nhỏ | Mọi nội dung sau này đều rẻ hơn nhờ nó |
| 2 | **B1 + B2** buồng lái của con + cửa hàng trang trí | vừa | Mở cửa tiêu cho một nền kinh tế đang tắc, và thoả nhu cầu chạy suốt 7–16 |
| 3 | **B3** ba mini-game còn lại | vừa | Rẻ hơn nhiệm vụ, chơi lại vô hạn, đã hứa miễn phí |
| 4 | **C1** khoe với bố mẹ | nhỏ | Kết nối, rủi ro 0, dùng lại thứ đã có |
| 5 | **D1** việc hằng ngày *(kèm D2 chỉ khi có ân hạn)* | vừa | Nhịp quay lại — nhưng chỉ đáng làm khi đã có ①–④ để quay lại mà làm gì |
| 6 | **A2** nhật ký so với chính mình | vừa | Phục vụ đầu trên của dải |

⚠️ **Nhiệm vụ Mặt Trăng không nằm trong sáu mục trên, và đó là một khuyến nghị có chủ đích.**
Nó là nội dung đắt nhất (mục 3.1–3.2) trong khi cả sáu mục trên đều **làm cho thứ đã có hấp dẫn
hơn**. Nếu phải chọn giữa *"nhiệm vụ thứ hai"* và *"buồng lái của con + cửa hàng + 3 mini-game"*,
số đo nghiêng hẳn về vế sau.

---

## 7. Giả định & cái tôi KHÔNG chắc

- **Chỉ MỘT nguồn tôi đọc được toàn văn** (Game Developer). Các phân tích tổng hợp về học-qua-chơi
  và hai bài ACM về thiết kế lừa dối: **tôi chỉ đọc tóm tắt kết quả tìm kiếm** — bài ACM trả
  **403** khi tôi mở. Trước khi trích số liệu nào từ chúng vào sản phẩm, phải đọc bản đầy đủ.
- **Nhóm số retention là blog thương mại**, không phải nghiên cứu. Tôi dùng chúng để **đặt câu
  hỏi** về cổng D30 ≥ 20%, không để trả lời nó.
- *[Suy luận]* Mốc "khoảng 11 tuổi" là ranh giới **trung bình**; trẻ thật rải rộng quanh nó. Đó
  chính là lý do A1 đề nghị **cho đổi độ sâu bất cứ lúc nào** thay vì khoá theo tuổi khai báo.
- **[Chưa kiểm chứng] Không có một trẻ thật nào đã thử app này.** Mọi thứ trong file này, kể cả
  phần đọc nghiên cứu, đều thua **một buổi ngồi xem 5 đứa trẻ chơi**. Nếu chỉ làm được một việc
  trong tuần này, tôi đề nghị việc đó — nó rẻ hơn mọi mục ở bảng trên và bác được nhiều thứ hơn.

## 8. Phương án nhỏ hơn nếu quá tốn

**Chỉ làm A1 + B2.** Hỏi tuổi để chọn độ sâu (một trường hồ sơ) và mở một cửa hàng trang trí
(một trang + một route trừ tiền — `Wallet.cs` đã có sẵn đường trừ có điều kiện nguyên tử, chỉ
thêm một `reason`). Hai việc đó cộng lại nhỏ hơn một nhiệm vụ, và chúng chạm vào **hai** nhu cầu
đang thiếu (phù hợp tuổi · thể hiện bản thân) thay vì thêm nội dung cho nhu cầu **đã** được thoả
tốt nhất (năng lực).

---

## Nguồn

**Đã đọc toàn văn:**
- [Children and their desired game experiences: A developmental look at game aesthetics — Game Developer](https://www.gamedeveloper.com/business/children-and-their-desired-game-experiences-a-developmental-look-at-game-aesthetics)

**Chỉ đọc tóm tắt kết quả tìm kiếm — cần đọc lại trước khi trích:**
- [Game-based learning in early childhood education: a systematic review and meta-analysis — Frontiers in Psychology](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2024.1307881/full)
- [The Effect of Digital Game-Based Learning Interventions… A Meta-Analysis — Review of Educational Research](https://journals.sagepub.com/doi/abs/10.3102/00346543231167795)
- [The Impact of Game-Based Learning on Motivation, Self-Efficacy, and Academic Achievement in the Natural Sciences — Education Sciences (MDPI)](https://www.mdpi.com/2227-7102/16/1/122)
- [Learning Mechanics and Game Mechanics Under the Perspective of Self-Determination Theory — arXiv](https://arxiv.org/pdf/1805.08053)
- [A Game of Dark Patterns: Designing Healthy, Highly-Engaging Mobile Games — ACM CHI](https://dl.acm.org/doi/fullHtml/10.1145/3491101.3519837) *(trả 403 khi tôi mở)*
- [Understanding Deception: children's interactions with deceptive design in digital games — ACM IDC 2026](https://dl.acm.org/doi/10.1145/3773077.3806137)
- [Digital Games as a Context for Children's Cognitive Development — Social Policy Report (SRCD)](https://srcd.onlinelibrary.wiley.com/doi/full/10.1002/sop2.3)
- [The developmental appropriateness of digital games and its impact on young children's enjoyment and playtime — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2212868922000186)
- [Age-Appropriate Design — Digital Thriving Playbook](https://digitalthrivingplaybook.org/big-idea/age-appropriate-design/)

**Độ tin cậy thấp (blog thương mại) — chỉ dùng để đặt câu hỏi về cổng D30:**
- [App Retention Benchmarks 2026: D1/D7/D30 by Industry — vmobify](https://vmobify.com/blog/app-retention-benchmarks)
- [What Is a Good App Retention Rate? Benchmarks by Category — Lovable](https://lovable.dev/guides/what-is-a-good-retention-rate-for-an-app)
