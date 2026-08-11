# 009. Hệ thống tài chính vận hành — mô hình thuê bao, giá và ưu đãi

**Trạng thái:** `đã chốt` — **phần GIÁ và GÓI**. Phần *thời điểm mở bán* vẫn theo điều kiện ở mục "Đã chọn" (3 nhiệm vụ · 300 câu quiz · D30 ≥ 20%).
**Ngày mở:** 2026-08-09 · **Ngày chốt:** 2026-08-09
**Người quyết:** chủ dự án (*"chốt giá theo như bản 009"*)
**Người đề xuất:** Claude (đối chiếu mã nguồn + tra giá thị trường)

> ⚠️ **CHỐT GIÁ ≠ MỞ BÁN.** Hai việc khác nhau và đừng gộp: bảng giá dưới đây nay
> là con số chính thức, nhưng app **chưa bán** — chưa chọn cổng thanh toán, và ba
> điều kiện bật Pha 1 chưa đạt (mới có **1/3 nhiệm vụ**, **100/300 câu quiz**, D30
> chưa đo được vì vừa ra mắt). Trang `pricing.html` vì thế vẫn không có nút thanh
> toán nào.
>
> ⚠️ **Đổi giá sau này là mở lại quyết định này**, không phải sửa `pricing.html`.
> Bảng trong trang đó là **bản sao**; sửa một bên mà quên bên kia thì bên lệch sẽ
> là bên nói với phụ huynh.

---

## Bối cảnh

Chủ dự án dự định **thu tiền theo tháng (subscription)** và hỏi mức giá USD/VND, các gói và ưu đãi.

Thời điểm hỏi: **09/08/2026** — tức **ngay sau mốc ra mắt** `2026-08-09T00:00+07:00` (`LAUNCH_AT` ở `js/index.js`), đồng hồ đếm ngược ở trang chủ đã về 0 được khoảng nửa ngày.

Câu hỏi thật sự phải trả lời trước khi bàn giá: **mỗi 30 ngày, gói tháng giao thêm được cái gì?**

---

## Số liệu đã kiểm bằng mã nguồn (09/08/2026)

Đây là căn cứ của mọi kết luận bên dưới. Đếm lại nếu nội dung thay đổi.

| Hạng mục | Con số thật |
|---|---|
| Nhiệm vụ **chạy được** | **1** (Trái Đất, 7 bước) — `MISSION-02` Mặt Trăng vẫn *sắp ra mắt* |
| Mini-game chạy được | **3 / 6** |
| Câu quiz | **100** (một lượt rút 5) |
| Thẻ Sổ Tay / mẫu vật / huy hiệu | 19 / 21 / 22 |
| Hành tinh **có nhiệm vụ** | **1 / 8** — 7 hành tinh còn lại chỉ để xem |
| Khu chưa có trang | **MOD-05 Phòng Nghiên Cứu** |
| Bề mặt dành cho **phụ huynh** | **0** |
| Chi phí sản xuất nội dung | **~445 dòng mã tay / mỗi BƯỚC nhiệm vụ** → 1 nhiệm vụ ≈ **3.115 dòng** |
| Trường `lv` (cấp độ câu hỏi) | khai ở **65/100** câu, **0 chỗ đọc** — nguyên liệu sẵn có cho tính năng trả phí |
| Nguồn thu Thiên thạch tím | **đúng hai**: quiz ĐẠT ≥60% · thu trong mini-game (`Wallet.cs`) |
| Waitlist đã hứa | **500 Thiên thạch tím** cho người đăng ký (`WaitlistEndpoints.cs`) |
| Hạ tầng | Pages (miễn phí) + Lambda/DynamoDB/SES — biên lợi nhuận gộp ~95% |

**[Suy luận]** Với khối lượng trên, một đứa trẻ đi hết phần nội dung *mới* trong khoảng **4–6 giờ**; phần chơi lại được chỉ có 3 mini-game.

### Giá thị trường đã tra (08/08/2026)

**[Chưa kiểm chứng độc lập]** — phần lớn giá VN lấy từ đại lý bán lại, không phải giá chính hãng.

| Sản phẩm | Giá |
|---|---|
| Monkey Junior | 699.000₫/năm · 1.399.000₫ trọn đời |
| Duolingo Super (VN, đại lý) | ~29.000₫/tháng · ~248.000₫/năm |
| Prodigy Math Premium (US) | $9,95/tháng |
| ABCmouse (US) | $12,99/tháng |
| Khan Academy Kids | **miễn phí hoàn toàn** |

---

## Các phương án đã cân nhắc

### A. Bật gói tháng ngay khi ra mắt — **BÁC**
Bán 99.000₫/tháng từ 09/08. Đơn giản, có doanh thu ngay.

### B. Freemium chặn theo THỜI GIAN (dùng thử 7 ngày rồi khoá) — **BÁC**

### C. Freemium chặn theo LƯỢT/NGÀY (energy) — **BÁC**

### D. **Freemium chặn theo NỘI DUNG + công cụ cho phụ huynh, bật theo 3 pha** — ✅ **ĐỀ XUẤT**

---

## Đã chọn (đề xuất, chờ chốt)

### Pha 0 — từ nay (trang chủ đã ra mắt 09/08/2026) đến khi đạt mốc nội dung

- Giữ **miễn phí toàn bộ**, không có paywall nào.
- Bán **một** thứ duy nhất: **Vé Sáng Lập** — trả một lần **1.490.000₫ / $69,99**, giới hạn **500 suất trong 60 ngày**.
- Dựng **trang phụ huynh + email tóm tắt tuần** (SES đã chạy sẵn).
- Đo: D1 / D7 / **D30** retention, số phút mỗi phiên, tỉ lệ hoàn thành Nhiệm vụ 01, số lượt quiz/tuần.

### Điều kiện bật Pha 1 — phải đạt **cả ba**

| Điều kiện | Hiện tại |
|---|---|
| ≥ **3 nhiệm vụ** chạy được | 1 |
| ≥ **300 câu quiz** | 100 (Gemini đang làm Đợt 2) |
| D30 retention ≥ **20%** | chưa đo được (chưa ra mắt) |

### Pha 1 — bật subscription

**Miễn phí vĩnh viễn** (không lấy lại thứ đã cho):
Nhiệm vụ 01 trọn 7 bước · Bản Đồ Thiên Hà đủ 8 hành tinh (tài sản SEO) · 3 mini-game **giữ nguyên luật tt hiện tại** · quiz 3 lượt/ngày · Sổ Tay · Kho Thành Tích · Hồ sơ · toàn bộ `wiki/`.

**Trả phí:**
1. **Nhiệm vụ 02+** (mỗi hành tinh) — trục giá trị chính
2. **Quiz không giới hạn + luyện theo cấp độ** ← nối `lv` vào, gần như 0 chi phí nội dung
3. **Phòng Nghiên Cứu (MOD-05)** — dựng thẳng thành khu trả phí
4. **Báo cáo cho phụ huynh** (xem mục *Hệ quả*)
5. Nhiều hồ sơ trẻ / một tài khoản
6. Chứng chỉ PDF hoàn thành nhiệm vụ
7. Mẫu vật hiếm + trang phục/tàu (thuần trang trí, **không** ảnh hưởng điểm)

**Bảng giá — Việt Nam**

| Gói | Tháng | Năm | ≈ /tháng | Cho ai |
|---|---|---|---|---|
| Phi Hành Gia Tập Sự | miễn phí | — | — | mọi người |
| **Phi Hành Gia** (1 trẻ) | **99.000₫** | **790.000₫** (−33%) | 65.800₫ | mặc định |
| **Phi Hành Đoàn** (tới 4 trẻ) | **169.000₫** | **1.290.000₫** (−36%) | 107.500₫ | nhà đông con |
| **Vé Sáng Lập** | — | **1.490.000₫ trọn đời** | — | 500 suất, 60 ngày đầu |
| Lớp học / Trường | báo giá | ~35.000₫/học sinh/tháng, tối thiểu 20 chỗ | | trung tâm, CLB |

**Bảng giá — quốc tế**

| Gói | Tháng | Năm |
|---|---|---|
| Astronaut (1 trẻ) | **$4,99** | **$39,99** (−33%) |
| Crew (tới 4 trẻ) | **$8,99** | **$69,99** (−35%) |
| Founder lifetime | — | **$69,99** (giới hạn) |

Hiển thị giá theo vùng bằng **chính cơ chế `guessLang`** đã có ở `js/ui-common.js` (múi giờ Việt Nam → bảng VND, còn lại → USD). Đừng dựng cơ chế thứ hai.

**Vì sao là những con số này:** rẻ hơn rõ rệt Prodigy/ABCmouse, nằm ở nửa dưới của Monkey, và **99.000₫ là mốc tâm lý "dưới 100k"** — ngưỡng phụ huynh Việt quyết được không cần hỏi ai. Mốc trọn đời 1.490.000₫ neo ngay trên Monkey trọn đời, hợp lý vì thị trường Việt đã quen khái niệm "trọn đời".

### Pha 2 — B2B2C
Gói lớp học/trường. ARPU cao hơn, churn thấp hơn nhiều: một hợp đồng 20 chỗ = 700.000₫/tháng ổn định, bằng 7 phụ huynh lẻ.

### Ưu đãi

| Ưu đãi | Nội dung | Vì sao |
|---|---|---|
| **Người Sáng Lập** | 500 người trong waitlist: **3 tháng gói Phi Hành Gia miễn phí** + huy hiệu 🏅 riêng vĩnh viễn + tên trong "phi hành đoàn đầu tiên" | Đã hứa họ 500 tt rồi — nâng lời hứa đó lên, và có ngay 500 người thật để **đo retention trước khi thu tiền** |
| Giảm gói năm 33–36% | như bảng | Gói năm là thứ cứu khỏi churn tháng 2. **Đẩy gói năm, đừng đẩy gói tháng** |
| Giới thiệu bạn | mời 1 bạn kích hoạt → **cả hai +1 tháng** | Kênh rẻ nhất cho app trẻ em (lan theo lớp học) |
| Dùng thử 14 ngày | **không cần thẻ**, kể cả gói năm | Điểm tin cậy lớn với phụ huynh Việt |
| Hoàn tiền 14 ngày | vô điều kiện, ghi rõ ở trang giá | |
| Gói Hè / Gói Tết | 3 tháng = giá 2 tháng | Đúng nhịp nghỉ học |
| Học bổng | 50 suất miễn phí/tháng cho trẻ khó khăn, đăng ký qua trường | Đúng với sản phẩm giáo dục trẻ em, và là PR thật |

⚠️ **Không dùng:** đồng hồ đếm ngược "chỉ còn 4 phút", giá gạch chân giả, gói tự gia hạn giấu nút huỷ. Một lần bị bóc là mất sạch niềm tin — và đây là sản phẩm cho trẻ em.

---

## Đã bác — và vì sao

*(Dán nguyên mục này vào ChatGPT/Gemini ở vòng bàn sau — chúng sẽ đề xuất lại đúng những thứ dưới đây.)*

- ⛔⛔ **BÁN THIÊN THẠCH TÍM BẰNG TIỀN THẬT.** Đây là điều bác mạnh nhất trong cả tài liệu. `Wallet.cs` chốt tt **chỉ** đến từ (1) quiz ĐẠT ≥60% và (2) thu trong mini-game — tức vòng lặp *muốn chơi game thì phải làm quiz đúng*. Bán tt bằng tiền là **trả tiền để khỏi phải học**, theo đúng nghĩa đen: trẻ có phụ huynh trả tiền thì không cần làm quiz nữa, và sản phẩm giáo dục thành sản phẩm giải trí. Cộng thêm: bán tiền tệ ảo cho người dưới 18 tuổi là vùng pháp lý nhạy cảm ở nhiều thị trường, và nó mâu thuẫn với **luật số 1 của dự án** (*server quyết mọi phần thưởng*).

- ⛔ **BÁN "CHƠI GAME KHÔNG TỐN tt" CHO GÓI TRẢ PHÍ.** Cùng một lỗi, chỉ đổi cách gói. Nghe hợp lý hơn ("quality of life thôi mà") nên dễ lọt hơn — vì thế phải ghi ra đây.
  ⇒ **Gói trả phí bán NỘI DUNG và CÔNG CỤ CHO PHỤ HUYNH, không bán tốc độ.**

- ⛔ **BẬT GÓI THÁNG NGAY NGÀY RA MẮT.** Gói tháng là một hợp đồng giao hàng mỗi 30 ngày, mà chi phí sản xuất đang là **~445 dòng mã tay cho MỖI BƯỚC** nhiệm vụ. Ký hợp đồng đó khi mới có 1/8 hành tinh có nội dung là tự tạo ra churn ở tháng 2 — và **churn tháng đầu thì không chiến dịch marketing nào cứu được**.

- ⛔ **DÙNG THỬ 7 NGÀY RỒI KHOÁ SẠCH.** Cắt ngang giữa lúc trẻ đang học. Và nó giết SEO: trang chủ + 22 trang `wiki/` đã được index, khoá nội dung sau 7 ngày là phá đúng thứ đang kéo người vào.

- ⛔ **GIỚI HẠN LƯỢT/NGÀY KIỂU ENERGY.** Dark pattern nhắm vào trẻ em. Rủi ro hình ảnh không đáng với doanh thu thu được.

- ⚠️ **GÓI TRỌN ĐỜI LÀM MỘT DÒNG SẢN PHẨM THƯỜNG TRỰC.** Nó giết LTV và buộc phải phục vụ người đó mãi mãi. Chỉ dùng **đúng một lần**, giới hạn **cả số lượng lẫn thời gian**, và coi là huy động vốn sớm để trả chi phí sản xuất nội dung.

- ⚠️ **ÉP TỰ ĐỘNG GIA HẠN BẰNG THẺ Ở VIỆT NAM.** **[Chưa kiểm chứng]** tỉ lệ lỗi cao và nhiều khiếu nại. Thực tế nên làm: **bán theo kỳ trả trước + email nhắc gia hạn trước 7 ngày** — SES đã chạy sẵn.

---

## Hệ quả — cái gì phải làm, cái gì từ nay không được làm

### Phải làm

1. **Trang phụ huynh + email tuần** — việc có ROI cao nhất, và **rẻ nhất**.
   ⚠️ **Đây là điểm mù lớn nhất hiện nay: người trả tiền không phải người chơi.** Trẻ 8–15 tuổi không có thẻ ngân hàng. Thứ khiến phụ huynh Việt trả 99k/tháng không phải *"con tôi vui"* mà là **"tôi thấy con tôi học được gì"**. Dữ liệu đã có sẵn trong DynamoDB (`SK=PROGRESS`, `missions`, `terms`, `achievements`) — chi phí ≈ 1 trang + 1 route + 1 mẫu email, **không cần thêm một dòng nội dung khoa học nào**.

2. **Entitlement do SERVER quyết**, đúng luật 1 của dự án:
   ```
   PK=USER#<uid>, SK=SUB
     plan       "free" | "astronaut" | "crew" | "founder"
     status     "trialing" | "active" | "past_due" | "canceled"
     periodEnd  <epoch>
     seats      1 | 4
     source     "vnpay" | "payos" | "stripe" | "manual"
     updatedAt

   PK=ORDER#<orderId>, SK=PAYMENT    ← chống webhook gọi 2 lần
   ```
   - Mọi `/me/*` trả kèm `entitlements: { plan, until }`; **client chỉ đọc, không bao giờ gửi lên**.
   - Chặn thật ở **endpoint**, không chặn ở giao diện. Client giấu nút mà server vẫn trả nội dung thì mở DevTools là qua.
   - Bản ghi `ORDER#` dùng đúng khuôn `opId` đã có ở `Wallet.cs` — đừng dựng cơ chế chống trùng thứ hai.
   - Tên bảng/tiền tố giữ nguyên `Astroq` theo quy tắc 3 mục 6.

3. ⚠️⚠️ **HẾT HẠN THÌ KHÔNG ĐƯỢC THU LẠI THỨ TRẺ ĐÃ KIẾM ĐƯỢC.** Huy hiệu, mẫu vật, tiến độ nhiệm vụ, Thiên thạch tím — **giữ vĩnh viễn**. Chỉ khoá **nội dung MỚI**. Lấy lại huy hiệu của một đứa trẻ vì bố mẹ nó quên gia hạn là thứ không bao giờ được làm, và nó đi ngược đúng nguyên tắc đã ghi nhiều lần trong dự án (*"0/7 bước" là một lời khẳng định SAI về tiến độ của trẻ*).

4. **Ân hạn 7 ngày** khi thanh toán lỗi, có email nhắc.

5. **Cổng phụ huynh trước paywall**: một bước xác nhận người lớn (nhập năm sinh / phép tính đơn giản) + xác nhận là phụ huynh ≥18 tuổi. **Không hiển thị lời chào mời trả tiền trực tiếp cho trẻ trong lúc chơi.**

6. **Ghi rõ chu kỳ, ngày thu tiếp theo, và cách huỷ NGAY TẠI trang giá.** Không giấu.

### Thanh toán

| Thị trường | Đề xuất | Ghi chú |
|---|---|---|
| Việt Nam | **payOS / SePay (QR chuyển khoản)** cho gói năm + trọn đời; **VNPay hoặc MoMo** cho gói tháng | Phí cổng trung gian **~1–3%**; mô hình A2A rẻ hơn nhiều **[Chưa kiểm chứng — phải đọc biểu phí hợp đồng thật]** |
| Quốc tế | **Paddle** (merchant of record) hơn Stripe | Paddle tự lo VAT/thuế ở EU/US — khỏi đăng ký thuế từng nước |

✅ **Lợi thế đang có, đừng đánh mất:** astroQ là web, **không qua App Store → không mất 15–30% hoa hồng**. Khi làm PWA (đã đủ điều kiện tiên quyết từ 07/08 sau khi tự host three.js + Firebase), **giữ thanh toán ở web**. Chỉ khi lên store thật mới phải tính lại giá.

### Chưa xác minh, cần người khác trả lời

- **[Chưa kiểm chứng]** Hoá đơn điện tử + thuế GTGT: dịch vụ giáo dục và phần mềm có thuế suất khác nhau ở Việt Nam. **Câu hỏi cho kế toán/luật sư, không phải cho Claude.** Đừng chọn mã ngành theo phỏng đoán.
- Nếu bán ra EU/UK: GDPR-K — thêm một lý do dùng merchant of record.

### Chỉ số phải theo dõi trước khi tin vào bảng giá này

| Chỉ số | Ngưỡng lành mạnh |
|---|---|
| D30 retention (miễn phí) | ≥ 20% |
| Free → Paid | 2–5% |
| Churn tháng | < 8% |
| Tỉ lệ chọn gói năm | > 40% |
| Hoàn thành Nhiệm vụ 01 | > 60% |

⚠️ Chi phí hạ tầng gần như bằng 0, nên **điểm hoà vốn không nằm ở hạ tầng mà ở chi phí sản xuất nội dung**. Đó là lý do mọi thứ ở trên xoay quanh đúng một câu: *mỗi tháng bạn giao thêm được gì?*

---

## Đã dựng ở client (09/08/2026)

Trang giá và cơ chế khoá **đã có**, nhưng bảng giá trong `pricing.html` chỉ là **bản sao** của tài liệu này — đổi giá thì **đổi ở đây trước**, rồi mới chép sang, và ghi vào Nhật ký yêu cầu.

| Thứ | Ở đâu |
|---|---|
| Ba trạng thái khoá (`free`/`soon`/`pro`) + modal giải thích | `js/locks.js` · `css/locks.css` |
| Huy hiệu + CTA trên thẻ khoá | `dashboard.html` (MOD-05) · `missions.html` (MISSION-02) · `games.html` (3 trò) |
| Trang Gói & Ưu đãi | `pricing.html` · `css/pricing.css` |
| Bộ đo | `scratchpad/smoke_locks.py` (57 phép kiểm) |
| **Báo cáo tuần cho phụ huynh** | `parent.html` · `css/parent.css` · `Services/Report.cs` · `GET /me/report` · `POST /me/report/email` |
| Bộ đo báo cáo | `scratchpad/test_report.py` (53) · `scratchpad/smoke_parent.py` (56) |

### Đơn vị của báo cáo là TUẦN LỊCH, nhưng tuần đầu bị cắt tại ngày đăng ký *(chốt 09/08/2026)*

Chủ dự án hỏi thẳng: *"báo cáo tuần tính theo 7 ngày kể từ lúc trẻ đăng ký có hợp lý hơn không?"* — câu trả lời là **giữ tuần lịch (T2–CN giờ VN) làm đơn vị**, và **chữa đúng chỗ hỏng thật** bằng cách cắt cửa sổ tại ngày đăng ký.

**Vì sao giữ tuần lịch:**
1. Chỉ tuần lịch mới đọc ra được **NHỊP học** ("con học ít vào cuối tuần"). Cửa sổ Năm→Năm thì cuối tuần nằm giữa, nhịp biến mất.
2. Gói **Phi Hành Đoàn** bán "tới 4 trẻ". Chung một mốc thì bốn con gộp được vào MỘT lá thư và so được với nhau; neo theo ngày đăng ký thì bốn con đăng ký bốn ngày khác nhau = **bốn mốc, bốn lá thư rời rạc**.
3. Thời khoá biểu ở trường cũng T2–CN, nên phụ huynh đối chiếu được.

⚠️ **Chỗ hỏng thật của tuần lịch, và nó là chỗ hỏng thật:** đăng ký thứ Bảy thì tuần đầu chỉ còn 2 ngày, mà mẫu số vẫn in "/7" → phụ huynh đọc **"1/7"** và hiểu là **một tuần lười học**, ngay ở lá thư đầu tiên họ nhận. Nên `Report.Clip()` đẩy mốc bắt đầu lên ngày đăng ký, trả về `days` (số ngày cửa sổ thật) + `partial`, và giao diện **NÓI RA**: *"tuần đầu, 2 ngày kể từ ngày đăng ký"*. Cùng nguyên tắc với dấu `—` thay cho 0 và dòng "bắt đầu ghi nhật ký từ…": **thà nói rõ giới hạn còn hơn để phụ huynh tự hiểu sai về con mình.**

⚠️ **`days == 0` là một câu KHÁC HẲN.** Cả tuần nằm trước ngày trẻ đăng ký → giao diện nói *"Tuần này nằm trước ngày con đăng ký"*, không nói *"chưa ghi được hoạt động nào"*. Nói nhầm câu là đổ cho đứa trẻ một tuần nó chưa tồn tại.

**Chi phí bằng 0 lượt đọc DB thêm:** `createdAt` đã có sẵn trên bản ghi PROFILE, và cả hai endpoint đều đã đọc profile để lấy tên con.

### Con vững chỗ nào, vướng chỗ nào *(chốt 09/08/2026)*

`pricing.html` hứa với phụ huynh: *"Thấy rõ con vững chủ đề nào, còn vướng chỗ nào"*. Trước 09/08/2026 lời hứa đó **không có nguyên liệu để giữ**: `PROGRESS.terms` chỉ nhận câu **ĐÚNG** (nó là chìa khoá mở Sổ Tay Thuật Ngữ), còn bộ đếm thì chỉ có tổng số câu đúng/sai cả đời — **câu SAI không được lưu ở đâu cả**.

Nay `quiz.html` gửi thêm `wrong: [khoá câu]`, server ghi cả `ok` lẫn `wrong` (string set) lên dòng nhật ký, `Report` gộp theo tuần, và `parent.html` vẽ bảng chủ đề — cần luyện thêm xếp lên trước.

⚠️⚠️ **CÂU SAI TUYỆT ĐỐI KHÔNG ĐƯỢC ĐI VÀO `PROGRESS.terms`.** Tập đó là chìa khoá mở thẻ Sổ Tay; nhét câu sai vào là **giải mã một thẻ bằng một câu trả lời sai**. Hai trường đi hai đường khác nhau ở server: `terms` → PROGRESS **và** nhật ký; `wrong` → **chỉ** nhật ký. Có phép kiểm riêng canh đúng chuyện này (và một phép thử phá hoại chứng minh nó bắt được).

⚠️ **Nhật ký ghi KHOÁ CÂU, không ghi tên/nhóm chủ đề.** Khoá câu là tên file trong `js/quiz/`, ổn định vĩnh viễn; còn cách gom câu thành **chủ đề** là một bảng ở client và nó sẽ đổi khi ngân hàng lớn từ 100 lên ~870 câu. Đóng băng cách gom vào một cuốn nhật ký **không backfill được** là mất luôn khả năng gom lại cho đúng.

⚠️ **Server KHÔNG giữ tên chủ đề — và vì thế EMAIL ĐẾM chủ đề chứ không GỌI TÊN.** Tên song ngữ nằm ở `js/quiz-index.js`; đó là đúng phân công đã dùng cho huy hiệu và mẫu vật (*server giữ mốc, client giữ tên*). Hai đường đã cân nhắc và bác:
- **Chép bảng tên sang server** để lá thư gọi tên được → bản sao thứ hai của một bảng tên, và nó sẽ lệch đúng vào ngày ai đó sửa tên một thẻ, tức **lá thư nói sai tên bài học của một đứa trẻ**.
- **Client gửi kèm tên đã dịch trong lời gọi gửi thư** → mở đường cho văn bản do người dùng chọn đi vào thư gửi từ `no-reply@astroq.org`.

Nên lá thư ghi *"Chủ đề cần luyện thêm: 3"* + một đường dẫn sang trang phụ huynh — nơi **duy nhất** gọi được tên. Nói ít hơn, nhưng không bao giờ nói sai. Có phép kiểm quét cả ba file server và đòi **0** tên chủ đề nào lọt sang.

⚠️ **Chủ đề "cần luyện thêm" tô HỔ PHÁCH, không tô ĐỎ.** Đây là báo cáo học tập của một đứa trẻ; đỏ đọc ra thành *"con bạn sai rồi"*. Cùng nguyên tắc với việc xu hướng **giảm** không bị tô đỏ ở chính trang này.

⚠️ **Hôm nay MỌI thứ bị khoá đều ở trạng thái `soon`, không cái nào là `pro`** — vì chưa cái nào có nội dung. Ngày nội dung xong thì đổi **một chữ** trong `ITEMS` của `js/locks.js`.

⚠️ **`pricing.html` VẪN `noindex` dù giá đã chốt** — lý do đổi chứ quyết định không đổi: ① mọi trang app đều `noindex` (chỉ `index.html` + `wiki/` được lập chỉ mục) và trang này link sang `dashboard.html`; ② **app chưa mở bán**, cho Google lập chỉ mục một bảng giá không mua được là dẫn người ta tới ngõ cụt. **Bỏ `noindex` không phải sửa một dòng**: còn phải thêm URL vào `sitemap.xml`, dựng bản `/en/` và khai `hreflang` chéo — đúng khuôn `wiki/` và trang chủ đã làm. Đó là một việc riêng, làm khi mở bán.

⚠️ **Chưa có nút thanh toán nào**, và đó là chủ đích: **giá đã chốt nhưng cổng thanh toán thì chưa chọn**, và ba điều kiện bật Pha 1 chưa đạt. Mọi CTA dẫn về form waitlist ở trang chủ.

---

## Còn treo

1. ~~Chủ dự án chưa chốt giá~~ — **đã chốt 09/08/2026.**
2. **Chưa đạt điều kiện bật Pha 1**: mới **1/3 nhiệm vụ**, **100/300 câu quiz**, D30 chưa đo được. Đây là thứ quyết định *ngày mở bán*, không phải giá.
3. ~~Trang phụ huynh + email tuần chưa làm~~ — **đã làm 09/08/2026.** Nhưng email mới là **gửi theo yêu cầu**; lên lịch tự động hàng tuần cần EventBridge + sửa `template.yaml` → cần `sam`, mà máy chưa cài. ⚠️ Đừng tạo rule bằng CLI ngoài luồng: nó nằm ngoài stack CloudFormation nên `sam deploy` sau này không biết tới.
3b. ~~Cột "yếu ở chủ đề nào" chưa làm được~~ — **đã làm 09/08/2026**, xem mục *Con vững chỗ nào, vướng chỗ nào* ở trên. Còn lại: nhật ký **không backfill được**, nên cột này chỉ có dữ liệu từ 09/08/2026 trở đi.
4. **Chưa chọn cổng thanh toán**; chưa đọc biểu phí hợp đồng thật. Đây là chốt chặn thật của việc mở bán.
5. Chưa có **cổng phụ huynh** (bước xác nhận người lớn) trước màn thanh toán — cần trước khi có nút mua đầu tiên.
6. Chưa hỏi kế toán về thuế/hoá đơn.
7. Bỏ `noindex` cho `pricing.html` + thêm vào `sitemap.xml` + bản `/en/` + `hreflang` — làm khi mở bán.
