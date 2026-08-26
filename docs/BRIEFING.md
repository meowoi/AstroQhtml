# AstroQ — Bản tóm tắt bối cảnh (dán vào ChatGPT / Gemini)

> **Cách dùng:** dán TOÀN BỘ file này vào đầu mỗi cuộc trò chuyện mới với ChatGPT hoặc Gemini,
> trước khi hỏi bất cứ điều gì về AstroQ. Kèm theo phần "Quyết định đã chốt" ở `docs/decisions/`
> nếu chủ đề đã từng bàn.
>
> **Số liệu trong file này là số ĐẾM THẬT từ mã nguồn**, cập nhật 31/07/2026. Nếu đề xuất của bạn
> dựa trên giả định khác với các con số dưới đây, hãy nói rõ giả định đó ra để được kiểm lại.

---

## 1. Dự án là gì

Web **giáo dục về Hệ Mặt Trời cho trẻ em**, song ngữ Việt–Anh, phong cách giao diện
glassmorphism + sci-fi khoang lái phi thuyền. Người chơi tạo thẻ ID phi hành gia, học qua
quiz và nhiệm vụ, chơi mini-game, khám phá bản đồ thiên hà 3D, thu thập mẫu vật và huy hiệu.

Đơn vị tiền trong game: **Thiên thạch tím (Purple Meteors)** — dùng để trả phí chơi mini-game.
Hai linh vật: **Comet** (bạn đồng hành nhiệt tình) và **Byte** (robot phân tích).

Trang chủ `astroq.org` đã go-live ở dạng landing "sắp ra mắt"; phần ứng dụng chưa mở cửa.

---

## 2. Công nghệ — và những gì KHÔNG được đề xuất đổi

**Client:** HTML + CSS + JavaScript **thuần**. Không framework, không npm, không build step,
không TypeScript. Thư viện ngoài duy nhất là **three.js** (nạp qua CDN, **chỉ còn ở bản đồ
thiên hà 3D**). Nhiệm vụ Trái Đất đã bỏ three.js ngày 31/07/2026 — cảnh của nó nay là 2D
(`js/earth2d.js`), đo được đường tải đầu **308 KB → 71 KB**.

**Backend:** AWS Lambda + **.NET 10** + **DynamoDB single-table** (`astroq-main`) + SES gửi email,
qua API Gateway HTTP API, vùng `ap-southeast-1`. Mã nguồn nằm **ngoài repo client**.

**Đăng nhập:** Firebase Authentication (Email/Password). Chia vai rõ: **đăng ký đi qua backend**
(2 giai đoạn, có email kích hoạt), **đăng nhập đi thẳng Firebase**.

> ❌ **Đừng đề xuất:** chuyển sang React/Vue/Next, thêm bundler, thêm npm dependency,
> viết CSS trong `<style>` hoặc `style="..."` inline, đổi nhà cung cấp cloud,
> đổi tên 6 khu vực đã chốt, đánh số lại các mã `MOD-nn` / `ARCADE-nn` / `MISSION-nn`.

---

## 3. Quy mô thật — dùng những con số này để ước lượng

| Hạng mục | Con số thật (09/08/2026) |
|---|---|
| Trang HTML chính | 20 |
| Bài wiki SEO | 10 bài × 2 ngôn ngữ (trang tĩnh, không nạp JS) |
| File CSS / file JS | 30 / 29 (+ **100 file câu hỏi** ở `js/quiz/`, một câu một file) |
| Tổng dòng (JS + HTML chính) | **~23.500** |
| **Nhiệm vụ (Mission)** | **1 chạy được** — Trái Đất, **7 bước**. Mặt Trăng: "sắp ra mắt" |
| Mini-game *(đếm lại 26/08/2026)* | **11 khai báo, 11 chạy được và ĐÃ MỞ HẾT** — 6 game lớp HÀNH ĐỘNG (né thiên thạch · phòng thủ 360° · ghép chòm sao · đường đua · mê cung · bắt sao băng) + **5** game lớp QUYẾT ĐỊNH (sinh tồn · liên lạc · tuần hoàn · đối chiếu · **dẫn tuyến**). ⚠️ Bốn game lớp quyết định bị khoá 19/08 → **mở 26/08/2026**, và ARCADE-11 thêm cùng ngày. ⚠️ **5 khuôn** lớp quyết định đã dùng: *chọn thẻ · xếp thứ tự · chia ngân sách · soi lỗi bảng · **lưới-nối*** — game thứ 12 **không được dùng lại** cái nào (`docs/decisions/002`). ⚠️⚠️ Khuôn **lưới-nối đã dùng 1/2 suất và suất còn lại ĐÃ CÓ CHỦ**: cơ chế "kéo đường nối hai đầu cùng loại" (kiểu Flow Free) là **cùng khuôn đó**, không phải khuôn mới — đừng đề xuất nó như một game thứ sáu của lớp này |
| Câu hỏi quiz | **100** — phủ 19 thẻ codex; 65 câu có `srcQuote` |
| Thuật ngữ codex | **19** (18 `space` + 1 `earth`) — và **19 icon SVG vẽ tay**, tỉ lệ 1:1 |
| **Bài đọc** (`js/articles.js`) | **34** — 18 thiên văn · 8 robot · 5 AI · 3 lượng tử |
| Mẫu vật | **21** (server là nguồn sự thật) |
| Huy hiệu | **22**, chia 5 nhóm (học · huấn luyện · khám phá · nhiệm vụ · cấp độ) |
| Hành tinh trong dữ liệu | **8** (`js/planets.js`). Bản đồ 3D có thêm Mặt Trời + Mặt Trăng |
| Kho nội dung học (`learningdata/`) | **Rất mỏng** — 1 file codex Trái Đất + vài bài NASA. ⚠️ **0 trang nào đọc `level_*.json`** |
| Endpoint API | 19 |

⚠️ **Dây chuyền nội dung ĐANG CHẠY — đừng đề xuất lại từ đầu.** Đã chốt **30 thẻ · 870 câu ·
5 đợt** (`docs/proposals/2026-08-06-review-gemini-30-the-chot.md`) và **100 bài đọc**
(`2026-08-05-de-bai-gemini-VONG-2-theo-thuat-ngu.md` mục 5). Đợt 1 đã giao: 15→19 thẻ ·
20→100 câu · 9→14 bài đọc. **Đợt 2 đang chờ:** 270 câu đào sâu 15 thẻ cũ.
⛔ Và **AI · Lượng tử · Lập trình · CNTT đang được HOÃN** khỏi vòng thẻ/câu hỏi — lý do ở
chính file đó. Đề xuất mở lại thì phải nói rõ dữ kiện mới là gì.

### ⚠️ Chi phí đơn vị — con số quan trọng nhất khi bạn đề xuất thêm nội dung

**Nhiệm vụ Trái Đất = 7 bước = 3.115 dòng mã viết tay** (`mission-earth.html` 2.526 dòng
+ `js/earth2d.js` 589), tức **~445 dòng cho mỗi bước**. Đếm lại ngày 02/08/2026.
*(Lịch sử con số này: ~410 dòng/bước khi còn `js/earth3d.js` → ~261 sau khi bỏ three.js
31/07 → **~445** sau ba vòng chơi thật `004`/`005`/`006`. Nó TĂNG vì mỗi vòng thêm phần
lời dẫn, phần tra nguồn và phần chú thích giải thích vì sao KHÔNG làm cách khác — không
phải vì thêm tính năng.)*

Nghĩa là: mọi đề xuất kiểu "mỗi hành tinh có N nhiệm vụ" phải nhân với **~445 dòng**, **trừ khi**
đề xuất đó kèm theo một bộ khuôn tương tác dùng lại được. Hãy nói rõ bạn chọn hướng nào.

### ⚠️⚠️ NGÂN SÁCH KHUÔN TƯƠNG TÁC — đọc trước khi đề xuất bất cứ cơ chế chơi nào

`docs/decisions/002` chốt: **một nhiệm vụ không dùng cùng một khuôn quá 2 lần.** Đây không
phải hướng dẫn mềm — nó đã **bác nguyên một vòng đề xuất** ngày 02/08/2026, vì cả hai bản
đều tiêu một chỗ trống không còn.

Đếm bằng công cụ trên mã nguồn thật, KHÔNG phải ước lượng:

| Khuôn | Đã dùng | Ở bước nào | Còn trống |
|---|---|---|---|
| `signal_scan` (chạm dấu hiệu trên bản đồ) | 2 / 2 | ① scan · ③ sun | ⛔ ĐÃ ĐẦY |
| `profile_builder` (thẻ → ô, kéo HOẶC bấm) | 2 / 2 | ④ energy · ⑥ eco | ⛔ ĐÃ ĐẦY |
| câu đố chọn đáp án | 2 / 2 | ① scan · ③ sun | ⛔ ĐÃ ĐẦY |
| `sequence_reconstruction` (sắp đúng thứ tự) | 1 / 2 | ② timeline | ✅ còn 1 chỗ |
| "xếp lên thang đo" *(khuôn thứ 6, mới 02/08)* | 1 / 2 | ⑤ life | ✅ còn 1 chỗ |
| `orientation_align` (ngắm/canh cho thẳng) | 0 / 2 | *(bước dùng nó đã bỏ)* | ⚠️ cấm mọi cú kéo bản đồ nên gần như không dùng được |

⚠️ Bước ⑤ `life` từng đẩy `signal_scan` lên **3/2** và đó là lý do THẬT khiến nó phải viết
lại — không phải vì hoạt cảnh drone. Nay nó là khuôn thứ sáu, có mã riêng ~90 dòng.

⚠️ **Giới hạn của chính luật này, nói ra để bạn không bị hỏi một câu bất khả thi:** `002`
chỉ ĐẶT TÊN 5 khuôn, **không đặc tả cái nào**. Nên bác được chắc chắn khi đếm được lời gọi
hàm có thật; với một khuôn mới thì xét theo *tinh thần* (rủi ro đơn điệu), không theo tên.

### Nút thắt thật

**Nội dung, không phải mã.** Đề xuất giúp *sản xuất nội dung nhanh hơn* có giá trị hơn đề
xuất thêm tính năng.

Trong nội dung thì **BÀI ĐỌC từng là chỗ hẹp nhất**, nay đã đỡ: Đợt A (09/08/2026) thêm 20
bài, kho lên **34 bài** và kế hoạch 100 bài đã giao **25/100**. Ba chủ đề trước đây trơ
(AI 1 · Robot 1 · Lượng tử 2) nay là **AI 5 · Robot 8 · Lượng tử 3** — viết qua góc *"robot
và AI trong không gian"* nên vẫn đúng bộ nguồn NASA/ESA.

⇒ **Chỗ hẹp nhất hiện giờ là CÂU HỎI và THẺ:** câu đã giao **80/850**, thẻ **4/30**.
**Đợt 2 (270 câu đào sâu 15 thẻ cũ, 0 icon mới) là việc rẻ nhất đang chờ.**

---

## 4. Kiến trúc đang có (để không đề xuất lại thứ đã có)

**6 khu vực** ở Trung Tâm Điều Hướng (`dashboard.html`) — **tên đã chốt, dùng đúng nguyên văn**:

| Mã | Tiếng Việt | English | Trạng thái |
|---|---|---|---|
| MOD-04 | Trung Tâm Nhiệm Vụ | Mission Control | có trang |
| MOD-01 | Trạm Tri Thức | Knowledge Station | có trang |
| MOD-02 | Khu Huấn Luyện | Training Simulator | có trang |
| MOD-03 | Bản Đồ Thiên Hà | Galaxy Map | có trang (3D) |
| MOD-05 | Phòng Nghiên Cứu | Research Lab | **chưa có trang** |
| MOD-06 | Thư Viện Thiên Văn | Star Archive | **chưa có trang** |

Ngoài ra đã có: Hồ sơ phi hành gia · Kho Thành Tích · Kho Mẫu Vật · Codex · màn Comet dẫn
tham quan cho người mới.

**Luồng hiện tại (đổi 01/08/2026, `docs/decisions/003`):** landing → đăng ký/đăng nhập →
cấp thẻ ID & chọn nhân vật → **Bản Đồ Thiên Hà** (chỉ Trái Đất bấm được, Comet dẫn đường) →
**Nhiệm vụ 01 "Hành Tinh Xanh"** → Trung Tâm Điều Hướng (Comet chúc mừng → tour 7 bước) →
chọn 1 trong 6 khu. Xem luật 12 ở mục 5.

**Bản đồ thiên hà** đã có dữ liệu khoa học đầy đủ song ngữ cho cả 8 hành tinh + Mặt Trời +
Mặt Trăng (đường kính, khối lượng, trọng lực, khí quyển, khả năng có sự sống, khám phá mới…).
Đây là tài sản lớn đang bị dùng chưa hết — hiện chỉ là bách khoa toàn thư để xem.

---

## 5. Luật bất di bất dịch (vi phạm là đề xuất bị bác)

1. **Server quyết mọi phần thưởng.** Client chỉ báo "đã làm gì", không tự tính XP, không tự mở
   huy hiệu, không tự trừ tiền. Đề xuất nào để client quyết điểm số sẽ bị bác.
2. **Chưa đăng nhập hoặc mất mạng → hiện dấu `—`, KHÔNG hiện `0`.** "0/7 bước" là một lời khẳng
   định sai về tiến độ của người chơi.
3. **Mọi chữ mới phải có cả tiếng Việt và tiếng Anh**, không có ngoại lệ.
4. **CSS nằm ở file `.css` riêng.** Không `<style>` trong HTML, không `style="..."` inline
   (trừ giá trị động do JS sinh).
5. **Thứ dùng chung thì tách ra dùng lại**, không copy-paste giữa các trang.
6. **Tôn trọng `prefers-reduced-motion`** — có trẻ nhạy cảm với chuyển động.
7. **Đổi id của bước nhiệm vụ đã phát hành là phá dữ liệu người chơi cũ** (id được dùng làm khoá
   trong DynamoDB). Thêm bước mới thì an toàn, đổi tên bước cũ thì không.
8. **Tính năng nào cũng làm cả client lẫn backend** — không có tính năng chỉ sống ở localStorage.
9. Nguồn khoa học phải dẫn được về **NASA / ESA / NOAA** hoặc tương đương, và URL phải sống thật.
10. **Cổng lộ trình 70% đã chốt và luật nằm ở SERVER** (`docs/decisions/003`): xong **5/7 bước**
    Trái Đất mới mở điểm đến kế tiếp; `GET /me/missions` trả sẵn `unlockedPlaces`, client không
    tự tính tỉ lệ. ⚠️ Cổng chỉ bật trong **lượt onboarding đầu tiên**, KHÔNG bật vĩnh viễn —
    khoá vĩnh viễn 6 hành tinh chưa có nhiệm vụ sẽ làm **7 mẫu vật không bao giờ thu được** và
    **2 huy hiệu bất khả thi**. Đề xuất nào mở rộng lộ trình phải kèm nhiệm vụ cho hành tinh đó.
11. **Nhiệm vụ Trái Đất chạy trên cảnh 2D, và đã BÁC BỎ việc chạy nó trên quả cầu 3D của bản đồ
    thiên hà** (`docs/decisions/003`) — quả cầu đó là texture nhiễu fBm không có lục địa thật, và
    nhiệm vụ cần 21 hàm cảnh mà nó không có hàm nào. Đừng đề xuất lại.
12. **LUỒNG ONBOARDING ĐÃ CHỐT (`003`), đừng đề xuất lại thứ tự khác:**
    `select.html` → `explorer.html?onboard=1` (bản đồ 3D, chỉ Trái Đất bấm được) →
    `mission-earth.html` → dashboard → Comet chúc mừng → **rồi mới** tour 7 bước.
    Nguyên tắc: **trẻ phải chạm được vào thứ gì đó trong vài giây đầu**; mọi đề xuất thêm
    màn giới thiệu vào TRƯỚC lúc đó sẽ bị bác. Cutscene 30s cũ (`js/mission-intro.js`) đã
    nghỉ hưu vì trùng nhịp với màn dẫn đường ở bản đồ.
13. **Bốn cờ onboarding ở server, ĐỘC LẬP nhau** (`tourSeen` · `intro01Seen` ·
    `earth1Greeted` · `map01Seen`). Thêm màn giới thiệu mới thì thêm cờ RIÊNG, đừng dùng
    lại cờ có sẵn — gộp là xem màn này sẽ xoá dấu màn kia.

---

## 6. Bạn được giao gì (và không được giao gì)

Dự án này hỏi ý **ba model, mỗi bên một vai không chồng lấn**. Đề bài cụ thể của bạn nằm ở
phần gửi kèm bên dưới bản tóm tắt này — hãy làm **đúng phần được giao**, đừng lấn sang phần
của bên kia, kể cả khi bạn thấy mình làm được.

| Vai | Ai | Sở hữu |
|---|---|---|
| **Sáng tác** | ChatGPT | cơ chế chơi · cấu trúc quest · lời thoại Comet/Byte · chữ hiển thị cho trẻ |
| **Tra nguồn & kiểm chứng** | Gemini | câu hỏi quiz · kho dữ liệu học · kiểm chính xác khoa học · kiểm URL sống · chất lượng bản EN |
| **Mã nguồn** | Claude | đối chiếu mã · ước lượng chi phí · kiến trúc & backend · viết code & tự kiểm |

**Không phù hợp để giao cho bạn** (vì cần đọc và chạy được mã nguồn):
- Ước lượng chi phí thực hiện, hay bất kỳ câu nào dạng "chỗ này sửa nhẹ thôi"
- Quyết định kiến trúc và thiết kế cơ sở dữ liệu

**Nếu bạn ở vai Sáng tác:** đừng khẳng định số liệu khoa học nào. Cần một con số hay dữ kiện
thiên văn thì viết `[CẦN KIỂM: …]` rồi đi tiếp — sẽ có bên khác tra.

**Nếu bạn ở vai Tra nguồn:** đừng sửa giọng văn dành cho trẻ và đừng thiết kế cơ chế chơi.
URL nào không xác minh được là còn sống thì ghi rõ *"chưa xác minh được"*, đừng đoán.

**Khi trả lời, hãy dùng đúng khuôn ở `docs/proposals/_TEMPLATE.md`**, đặc biệt là hai mục
*"Giả định tôi đang dựa vào"* và *"Cái tôi KHÔNG chắc"* — đó là phần được kiểm lại bằng mã nguồn.

---

## 7. Chưa chốt — đang cần bàn

- **Độ tuổi mục tiêu cụ thể** chưa ghi trong tài liệu dự án. Hỏi lại chủ dự án thay vì tự giả định.
- **Cấu trúc World / Quest cho 8 hành tinh** — xem `docs/decisions/001-cau-truc-world-quest.md`.
- Hai khu **Phòng Nghiên Cứu** và **Thư Viện Thiên Văn** chưa có nội dung.
