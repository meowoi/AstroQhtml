# Review: Q-Lab — AI Lab gồm mini-game, thay cho "khóa học AI được game hóa"

**Đề xuất gốc:** `docs/proposals/2026-08-29-ai-lab-8-mini-game.md` (ChatGPT, 29/08/2026)
**Người đối chiếu mã nguồn:** Claude · **Ngày:** 29/08/2026
**Vai:** phía kiểm giả định bằng số đo (`docs/PHAN-VAI.md`)
**Liên quan:** `2026-08-19-ai-dong-vai-gi-trong-astroq.md` · `2026-08-26-review-dinh-vi-lai-landing-ai.md` · `docs/decisions/010`

---

## 1. Kết luận ngắn

**Đồng ý với hướng đi. Nhưng lý do thật mạnh hơn lý do đề xuất đưa ra, và phạm vi
phải nhỏ hơn nhiều — một thẻ, không phải tám game.**

Đề xuất lập luận bằng **sư phạm** ("learn by doing hơn bài giảng"). Đúng, nhưng đó là
lập luận chung, đúng với mọi app. Ba lý do mạnh hơn nằm ở chỗ đề xuất không đọc được:

1. **AstroQ đã có AI là nhánh nội dung LỚN NHẤT** (46% kho bài đọc — lớn hơn thiên
   văn), nhưng **lớp tương tác thì 100% thiên văn**. Đây không phải "thêm một môn mới",
   mà là **làm cho môn lớn nhất chơi được**. Rẻ hơn và trung thực hơn.
2. **Nội dung AI hiện có đang ở ĐÚNG cái format mà đề xuất phản đối.**
   `learningdata/ai/level_01.json` là 25 câu trắc nghiệm, câu đầu tiên:
   *"Byte trong AstroQ là loại nhân vật gì? → B. Một chú robot"*. Tức đề xuất không
   xin thêm cái mới — nó chỉ ra một cái **đang sai format**.
3. **Việt Nam vừa bắt buộc dạy AI, 11 ngày trước.** Quyết định **2422/QĐ-BGDĐT**
   (18/08/2026). Năm học 2026–2027 bắt đầu trong khoảng một tuần nữa. Chi tiết ở mục 3
   — và nó đổi câu hỏi từ *"có nên làm không"* thành *"làm kịp bao nhiêu"*.

**Chỗ tôi KHÔNG đồng ý:** danh sách 8 game có **hai chỗ trùng lặp** và **một khoảng
trống** so với khung Việt Nam. Và cả 8 game đều đứng trên một giả định không nói ra
mà tôi đo ra là **sai** — xem mục 5.

---

## 2. Số đo từ mã nguồn (29/08/2026)

| Điều | Số đo | Cách đo |
|---|---|---|
| Kho bài đọc | 70 bài · **`ai` 14 + `robot` 11 + `it` 7 = 32 bài (46%)** vs `astronomy` 17 (24%) | review 26/08, mục 2 |
| Câu hỏi quiz | 190 câu · **38 câu (20%) là AI/thuật toán/học máy** | review 26/08 |
| Ngân hàng AI chuyên biệt | `learningdata/ai/level_01.json` + `level_02.json` — **50 câu trắc nghiệm** | `ls learningdata/ai/` |
| Lớp **tương tác** (nhiệm vụ + game) | **thiên văn 100%** — 5 nhiệm vụ, 11 game, 0 nội dung AI | `ls mission-*.html game-*.html` |
| Vỏ nhiệm vụ dùng chung | **`js/mission-stage.js` 823 dòng** — có sẵn `say` · `objective` · `showCard` · **`dragDrop`** · `buildAsk` · `showWin`, tự mang chuỗi song ngữ | `wc -l` + đọc API |
| Vỏ phòng thí nghiệm dùng chung | **`lab.html` 530 dòng** (lưới thẻ LAB-01…08, 5 đã dựng · 3 khoá) + `js/lab-catalog.js` 396 + `js/lab-drop.js` 719 | `wc -l` |
| Thưởng nhiệm vụ | `Services/Missions.cs` — client gửi **`{mission, step}`**, KHÔNG gửi con số nào; server tra bảng rồi cộng | đọc mã |
| Script từ tên miền ngoài | **`_KNOWN_CDN = set()`** — bằng 0, có phép kiểm canh | `check_pages.py` [14] |
| Vẽ vật thể bằng vector | **đã có** — `rockPts`, `rockBox: 2.41`, dùng làm đường lùi khi ảnh hỏng | `game-dodge.html:250` |
| Kho ngữ liệu tiếng Việt+Anh | **96.560 từ · 12.244 từ khác nhau · 55.362 cặp bigram** | `scratchpad/corpus.py` (mới) |
| Nợ nội dung (cổng mở bán `009`) | 190/300 câu ⇒ **còn 110 câu** | review 26/08 |

⚠️ **Số cuối vẫn là số kìm nhịp.** Mọi việc ở file này **cạnh tranh** với 110 câu đó.
Đó là lý do mục 7 đề nghị **một thẻ**, không phải tám game.

---

## 3. ⚠️⚠️ Cửa sổ chính sách — và một đính chính cho bản review 26/08

Bản review 26/08 ghi ở mục 13: *"**không kiểm chứng được** chủ trương AI của Bộ GD&ĐT
năm học 2026–2027 mà đề xuất viện dẫn."*

**Nay kiểm chứng được, và nó có số hiệu quyết định.**

| Điều | Nội dung |
|---|---|
| Văn bản | **Quyết định 2422/QĐ-BGDĐT**, ngày **18/8/2026** |
| Phạm vi | Khung nội dung giáo dục AI cho học sinh phổ thông, **lớp 1 → lớp 12** |
| Hiệu lực | Triển khai **đại trà** từ năm học **2026–2027** |
| Thời lượng | **12 tiết/lớp/năm học** cho nội dung cốt lõi |
| Bốn mạch kiến thức | ① **Tư duy lấy con người làm trung tâm** ② **Đạo đức AI** ③ **Các kĩ thuật và ứng dụng AI** ④ **Thiết kế hệ thống AI** |
| Ba hình thức triển khai | môn/chuyên đề riêng · tích hợp vào môn đang có · **câu lạc bộ / hoạt động ngoại khoá** |
| Đánh giá | ⚠️ **"không có bài kiểm tra và đầu điểm riêng"** |
| Yêu cầu với nhà trường | *"lựa chọn, rà soát công cụ AI phù hợp với độ tuổi học sinh"* |

**Ba dòng in đậm là ba cái chốt thương mại, theo thứ tự quan trọng:**

⚠️⚠️ **"Không có bài kiểm tra và đầu điểm riêng" là câu quan trọng nhất trong cả văn
bản đối với AstroQ.** Không có điểm số nghĩa là **không có gì ép học sinh đi hết 12
tiết** — tài liệu phải tự hấp dẫn mới sống được. Đó chính xác là khoảng trống mà một
**game** lấp được và một **ngân hàng trắc nghiệm thì không**. Và AstroQ đang có 50 câu
trắc nghiệm AI, tức đang đứng đúng phía sai của câu này.

⚠️ **"Câu lạc bộ / hoạt động ngoại khoá" là một trong ba hình thức được công nhận.**
AstroQ không cần trở thành sách giáo khoa để vào trường — nó vào được bằng cửa CLB.

⚠️ **Yêu cầu trường phải "rà soát công cụ AI phù hợp độ tuổi"** là lợi thế trực tiếp
cho kiến trúc ở mục 5: một mô hình **chạy hẳn trong máy trẻ, không gọi ra ngoài, không
có ô chat** thì phần rà soát gần như không có gì để rà.

⚠️ **Bốn mạch của Việt Nam KHÁC năm Big Ideas của AI4K12** mà đề xuất viện dẫn. AI4K12
(đã kiểm: Perception · Representation & Reasoning · Learning · Natural Interaction ·
Societal Impact) là khung **Mỹ**. Với một sản phẩm Việt bán cho phụ huynh Việt đúng năm
AI thành bắt buộc, **bám bốn mạch của 2422 đáng giá hơn hẳn**. Ánh xạ lại ở mục 7.

⚠️ *[Chưa kiểm chứng]* Tôi **chưa đọc được toàn văn phụ lục** của Quyết định 2422 —
các trang tin chỉ đăng phần tóm tắt. Yêu cầu cần đạt theo từng cấp mà tôi trích ở mục 7
là **theo tường thuật báo chí**, không phải nguyên văn phụ lục. Trước khi in bất cứ
dòng nào lên trang bán hàng, **phải đọc phụ lục gốc**.

---

## 4. Kiểm chứng các sản phẩm được viện dẫn

Đề xuất viện dẫn 9 sản phẩm + 1 nghiên cứu. Tôi kiểm ba cái **ít quen nhất** (ba cái
dễ bịa nhất); các cái còn lại (Code.org, Quick Draw!, Teachable Machine, Cognimates,
Semantris) là sản phẩm phổ biến, không kiểm lại.

| Tuyên bố | Phán | Bằng chứng |
|---|---|---|
| **Breakable Machine** — game cho 10–15 tuổi, đánh lừa image classifier, có khung nhìn XAI | ✅ **đúng, và mạnh hơn đề xuất nói** | Bài AAAI, arXiv **2508.14201**. Đúng độ tuổi 10–15. Có **feature saliency view** + bảng xếp hạng lớp học |
| **Day of AI** — AI or Not? · Pyramid Puzzle · Sunny's Mindful AI Day | ✅ đúng | Day of AI Australia; đã tới **>340.000 học sinh** từ 2022 |
| **Hello!AI** — nghiên cứu 2025, lớp 2–6, ba lớp khái niệm→suy nghĩ→áp dụng | ✅ đúng | *Int. J. Human–Computer Interaction*, đăng 30/10/2025. Ba module: Algorithm Adventure · Algorithm Handbook · City Builder |
| **AI4K12 Five Big Ideas** | ✅ đúng tên năm ý | ai4k12.org |

⚠️⚠️ **Một chi tiết của Breakable Machine mà đề xuất bỏ qua, và nó là chi tiết quyết
định:** game đó chạy bằng **camera của học sinh** + WebRTC ngang hàng, trẻ thay đổi
**ngoại hình và bối cảnh thật của mình** để đánh lừa máy. AstroQ **không được** đi
đường đó — một app cho trẻ 8–15 bật camera là mở toàn bộ chương nghĩa vụ mà đề xuất
19/08 đã dựng hàng rào để tránh. Bản AstroQ phải đánh lừa bằng **thao tác trên vật thể
vẽ ra**, không phải trên khuôn mặt trẻ. Cùng bài học, không cùng bề mặt rủi ro.

⚠️ **Ánh xạ "REASONING → Break Byte" ở mục 4 của đề xuất là sai.** Break Byte đo
**giới hạn của PERCEPTION** (mô hình nhìn nhầm) chứ không phải representation &
reasoning. Nói sai chỗ này thì bảng curriculum trông đủ năm ý nhưng thật ra **thiếu
một ý và thừa một ý** — đúng loại lỗi sẽ bị bắt nếu đem bán cho trường.

---

## 5. ⚠️⚠️ Câu hỏi kỹ thuật quyết định — và một giả định SAI của cả 8 game

Cả tám game đều đứng trên một giả định không ai nói ra: **"chạy được một mô hình học
máy trong trình duyệt"**. Với AstroQ, giả định đó chạm hai bức tường:

- **`_KNOWN_CDN = set()`** — dự án cấm **tuyệt đối** script từ tên miền ngoài, có phép
  kiểm canh (`check_pages` [14]). TensorFlow.js chỉ vào được bằng cách tự host.
- **Ngân sách byte.** Dự án đã trả giá để có nó: font 621→101 KB, ảnh 72 MB→2,79 MB,
  và **cố ý không nạp SDK Firebase 233 KB** ở trang cần mượt. Tự host ~1 MB TF.js là
  đi ngược đúng thứ đó.

**Nên tôi không đoán. Tôi dựng nguyên mẫu rồi đo.**

### 5a. Kết quả: không cần mạng nơ-ron

`scratchpad/proto-classifier.js` — bộ phân loại **k-NN** trên 4 đặc trưng nhìn thấy
được (độ xám · độ tròn · độ sáng · tỉ lệ dài/rộng):

| Số đo | Giá trị |
|---|---:|
| Dòng mã (kể cả chú thích) | **70** |
| Kích thước gzip | **1.792 B** (~1,8 KB) |
| Phụ thuộc | **0** |
| Build step | **0** |
| So với TensorFlow.js (~1 MB) | **nhỏ hơn ~550 lần** |

Và nó **học thật**: mô hình là chính những mẫu trẻ vừa gắn nhãn.

### 5b. Hai phát hiện từ việc DỰNG THẬT — cả hai đều đổi thiết kế

Nếu chỉ đọc đề xuất rồi viết code, hai lỗi này đã lọt ra bản thật dưới dạng **lỗi nội
dung im lặng** — game vẫn chạy, vẫn vui, và **dạy sai**.

**① Nearest-centroid làm HỎNG nửa sau của bài học.**
Bản đầu tôi dùng trọng tâm mỗi lớp. Nó chạy, nhẹ hơn, và **vẫn cho ra cú twist của đề
xuất** (dữ liệu lệch → Byte đoán sai). Nhưng phép thử tiếp theo làm nó đổ: **thêm dữ
liệu đa dạng vào thì Byte VẪN đoán sai** — vì lấy trung bình chính là **xoá mất sự đa
dạng vừa thêm**.

⇒ Nửa sau của bài học (*"thêm dữ liệu đa dạng thì AI khá lên"*) **không tái hiện
được**. Một game dạy machine learning mà bước sửa không có tác dụng thì nó dạy điều
ngược lại. k-NN sửa được: mỗi mẫu trẻ thêm vào là **một láng giềng thật**. Và nó đúng
về sư phạm hơn — *"Byte NHỚ những mẫu bạn dạy, rồi tìm mẫu giống nhất"* là câu một đứa
8 tuổi hình dung được.

**② Saliency ngây thơ NÓI DỐI — và đây là thứ Break Byte sống bằng.**
Khung nhìn XAI đầu tiên của tôi lấy *"đặc trưng nào gần láng giềng nhất"*. Nó khai
`dài` là lý do — trong khi **mọi mẫu trong bộ đều có tỉ lệ dài/rộng = 1.0**, tức đặc
trưng đó không phân biệt được gì cả. **Một đặc trưng HẰNG SỐ trông ra quan trọng nhất.**

⇒ Luật đúng: đo **sức phân biệt**, không đo độ giống — so khoảng cách theo từng trục
tới lớp **thắng** với lớp **thua**. Trục nào cho lớp thắng lợi thế lớn nhất mới là lý
do thật. Không có sửa này thì Break Byte **chỉ cho trẻ cái cảm giác đã hiểu**.

### 5c. Phép đo bài học, sau khi sửa cả hai

Vật thử: **một thiên thạch màu ĐỎ (sáng)** — Byte chưa từng thấy.

| Dạy bằng | Byte đoán | Chắc | Byte tự khai đã nhìn vào |
|---|---|---:|---|
| bộ dữ liệu **LỆCH** (thiên thạch đều xám, vệ tinh đều sáng) | ❌ `vệ tinh` | 100% | **độ sáng** |
| bộ dữ liệu **ĐA DẠNG** (thêm thiên thạch đỏ, vệ tinh trong bóng tối) | ✅ `thiên thạch` | 67% | **độ tròn** |

**4/4 phép kiểm đạt.** Và hãy để ý cột cuối — đó mới là phần đắt giá: dữ liệu lệch thì
Byte **tự nói ra** rằng nó quyết định bằng *màu sáng*; dữ liệu đa dạng thì nó chuyển
sang *hình dạng*. Bài học *"AI học từ dữ liệu bạn cho nó"* **hạ cánh bằng cơ học**,
không phải bằng một dòng chữ hiện lên cuối màn.

### 5d. Next Token — khả thi, trên chính kho chữ của dự án

Đo được: **96.560 từ · 55.362 cặp bigram khác nhau** trong `js/article` + `js/quiz` +
`learningdata`. Đủ để dựng một mô hình n-gram **thật**, và nó nói về đúng thiên
văn/AI — tức mô hình *của AstroQ*, không phải một đồ chơi mượn.

⚠️ Nhưng **không được ship bigram thô**: kho song ngữ trộn lẫn nên phân bố nhiễu (đo
được `the → Sun 3%`), và cả bảng ~1 MB JSON là quá nặng. Đường đúng: **tính offline
bằng Python** (dự án đã có sẵn khuôn `scratchpad/*.py` sinh dữ liệu), chọn tay ~30 câu
làm bài, ship một JSON vài KB. Xác suất **có thật, đo từ kho thật**; câu thì **chọn để
dạy**. Và nó tất định ⇒ **viết được bộ kiểm**.

### 5e. Bộ dữ liệu: SINH RA, đừng đi chụp

Đây là chỗ đề xuất bỏ trống hoàn toàn, và nó là **nút thắt thật** của Train Byte: game
cần một tập ảnh **đã gắn nhãn, có kiểm soát được thuộc tính**. Dự án hiện có **58 ảnh
tổng cộng**, và luật của chủ dự án là **người dùng tự đặt ảnh gốc**.

⇒ Đừng làm bằng ảnh. **Vẽ vật thể bằng vector trên canvas** — dự án đã làm sẵn việc
này (`rockPts` trong `game-dodge.html`, giữ làm đường lùi khi ảnh hỏng). Cái được:

- đặc trưng **biết trước theo cấu tạo**, không phải trích xuất từ pixel ⇒ mô hình gọn
  và giải thích được;
- **cú twist điều khiển được**: muốn bộ dữ liệu lệch thì sinh ra bộ lệch, chính xác;
- **0 phụ thuộc mỹ thuật**, 0 KB ảnh mới;
- tất định ⇒ **bộ kiểm chạy được**, đúng chuẩn của dự án.

---

## 6. Ba chỗ tôi đề nghị SỬA trong danh sách 8 game

**① `TRAIN BYTE` và `BREAK BYTE` là MỘT lượt dựng, không phải hai.**
Break Byte **cần** đúng mô hình đã huấn luyện + khung nhìn XAI của Train Byte. Khi
Train Byte xong thì Break Byte là một **chế độ thứ hai** trên cùng engine — ước ~30%
thêm, không phải 100%. Tách ra còn làm hỏng mạch cảm xúc: *"dạy nó → phá nó"* là **một
cung**, không phải hai lượt chơi cách nhau vài tuần.

**② `DATA RESCUE` (game 2) TRÙNG với chính cú twist của Train Byte.**
Bài học của nó — dữ liệu mất cân bằng → accuracy cao mà vẫn sai — **đã là** phần hay
nhất của Train Byte. Làm hai game cho một bài học là chẻ bài học làm đôi. Đường đúng:
Data Rescue thành **Cấp 2 của Train Byte** (Understand → Apply, đúng ba cấp mà chính
đề xuất đưa ra ở mục 12).

**③ Khung Việt Nam có mạch ④ "Thiết kế hệ thống AI" mà KHÔNG game nào phủ.**
Ánh xạ lại theo Quyết định 2422 thay vì AI4K12:

| Mạch (QĐ 2422) | Game phủ | Phán |
|---|---|---|
| ③ Các kĩ thuật và ứng dụng AI | Train Byte · Next Token · Algorithm or AI? | **phủ tốt** |
| ② Đạo đức AI | AI or Real? · Should I Ask AI? | **phủ tốt** |
| ① Tư duy lấy con người làm trung tâm | Break Byte · Should I Ask AI? | phủ một phần |
| ④ **Thiết kế hệ thống AI** | *(không có)* | ⚠️ **trống** |

⚠️ **Tôi đề nghị KHÔNG lấp mạch ④ ở vòng này.** Nói thật *"phủ 3/4 mạch"* mạnh hơn
nhiều so với vẽ thêm một game nửa vời rồi bảo là đủ bốn — và cửa kiểm ở trường sẽ đọc
được sự khác nhau đó. Ghi khoảng trống ra, lấp sau.

---

## 7. Đề xuất của tôi: DỰNG ĐÚNG MỘT THẺ

> **`LAB-AI-01` — "Dạy Byte nhìn"**, gồm **hai chế độ trên một engine**:
> **DẠY** (Train Byte + cú twist dữ liệu lệch) và **PHÁ** (Break Byte + khung nhìn XAI).

**Vì sao chỉ một:** nợ nội dung 110 câu vẫn là cổng mở bán của `009`, và mọi việc ở
đây cạnh tranh với nó. Một thẻ đủ để trả lời câu hỏi thật — *trẻ có chơi hết không* —
mà không đặt cược cả quý vào một hướng chưa ai đo.

### 7a. Nó sống ở đâu

**Không dựng kiến trúc trang mới.** `lab.html` đã là "Phòng Nghiên Cứu" với đúng khuôn
cần: lưới thẻ có mã (`LAB-01`…`LAB-08`), thẻ khoá **vẫn bấm được** và mở hộp nói vì sao
khoá, đọc `AstroQDepth` (junior/senior). Một thí nghiệm ≈ **1 mục trong catalog + 1
module JS** (`js/lab-drop.js` = 719 dòng cho cả bộ mô phỏng vật lý).

⚠️ **Nhưng `lab.html` đang là phòng VẬT LÝ.** Trộn thẻ AI vào làm nhoè cả hai. Hai
đường, và tôi **chưa chốt** — đây là chỗ chủ dự án quyết:
- **(a) Cùng lưới, mã `LAB-AI-01`.** Rẻ nhất, 0 trang mới. Mất: "Q-Lab" không có
  danh tính riêng để bán.
- **(b) Trang `ailab.html` riêng, dùng lại khuôn.** Được danh tính (khớp mục 6 của đề
  xuất: *TRAIN AN AI / BREAK AN AI*). Phải trả: **tách phần vỏ lưới thẻ ra dùng chung**
  — đúng luật quy tắc 2 mục 6, và **đó là chi phí thật phải nói ra**, không phải chép
  530 dòng.

*[Nghiêng về (b)]* vì cửa CLB ở mục 3 cần một cái tên gọi được, nhưng chỉ khi chấp nhận
trả phần tách vỏ.

### 7b. Thưởng đi đường NHIỆM VỤ, không đi đường GAME

Quyết định kiến trúc, đáng nói rõ: điểm game do **client khai** (server chỉ đặt trần,
`Wallet.cs`); nhiệm vụ thì client **chỉ gửi `{mission, step}`** và server tra
`Services/Missions.cs` rồi cộng — *"chỗ thưởng không thể bịa"*.

⇒ AI Lab là **hoạt động học**, không phải arcade. Thưởng phải đi đường nhiệm vụ. Thêm
một dòng vào `Missions.All`, **không** sửa endpoint.

### 7c. Vì sao kiến trúc này KHÔNG phá quyết định 19/08

Đề xuất 19/08 chốt: *"astroQ không có bề mặt AI nào cho trẻ chạm vào"*, và bác vai ⑥
vì cả chương nghĩa vụ pháp lý. **`LAB-AI-01` không đụng một dòng nào của quyết định
đó**, và điều này phải nói rõ vì nghe qua thì tưởng ngược lại:

| Thứ 19/08 lo | `LAB-AI-01` |
|---|---|
| Mô hình nói sai với một đứa trẻ | **không có ô chat**, không có văn bản sinh ra |
| Chi phí inference mỗi lượt | **0** — mô hình chạy trong máy trẻ |
| Dữ liệu trẻ ra khỏi máy | **0 byte** — không gọi mạng, không camera |
| Bộ nhớ xuyên phiên (nhãn Restricted của Roblox) | không có |
| Công bố AI · nhắc nghỉ · quy trình tự hại (SB 243) | không kích hoạt — đây là **đồ chơi dạy học**, không phải bạn đồng hành |

⇒ Đây **là** cách duy nhất thêm chữ "AI" vào sản phẩm mà không mở một nghĩa vụ nào.
Và nó **hợp pháp hoá câu chữ trên landing**: thẻ 2 hiện hứa *"máy học từ đâu"* — hôm
nay lời hứa đó được trả bằng **bài đọc**; có `LAB-AI-01` thì nó được trả bằng **một
việc trẻ tự làm**.

---

## 8. Chi phí — ước lượng, phải đo lại khi làm

| Phần | Ước lượng | Cơ sở |
|---|---:|---|
| `js/ai-model.js` (k-NN + XAI) | **~120 dòng** | nguyên mẫu 70 dòng **đã chạy, 4/4 đạt** |
| `js/ai-specimens.js` (sinh vật thể vector + đặc trưng) | ~200 dòng | khuôn `rockPts` đã có |
| Chế độ DẠY (gắn nhãn → train → test) | ~250 dòng | `dragDrop`/`buildAsk` của `mission-stage.js` dùng lại được |
| Chế độ PHÁ (chỉnh vật thể → xem XAI) | ~150 dòng | dùng lại engine ở trên |
| Lời thoại Comet/Byte + i18n **vi & en** | ~60 khoá | ~197 dòng/chặng là mức đo được ở `mission-orbit` |
| CSS | ~150 dòng | `css/page-shell.css` dùng lại |
| Backend | **~5 dòng** — 1 mục `Missions.All` | không endpoint mới |
| Bộ kiểm (`check_ai_model.py` + `smoke_ailab.py`) | ~250 dòng | bắt buộc theo quy tắc 6 |
| *(nếu chọn 7a-b)* tách vỏ lưới thẻ dùng chung | **~200 dòng** + hồi quy `lab.html` | rủi ro thật, đừng bỏ qua |

⚠️ **Ảnh mới cần: 0.** Đó là điểm mạnh nhất của mục 5e.
⚠️ **Con số này là ước lượng của tôi, chưa phải số đo.** Chỉ hai dòng đầu có bằng
chứng (nguyên mẫu đã chạy). Phần còn lại suy từ chi phí chặng nhiệm vụ đã đo — **đừng
nhận theo mệnh giá**, đúng luật đã ghi ở `010` và `009`.

---

## 9. Ảnh hưởng tới người chơi cũ

**Không.** Thêm một thẻ mới + một mục `Missions.All` mới. Không đụng hồ sơ, tiến độ,
ví, hay khoá `localStorage` nào. Bước nhiệm vụ mới chưa ai làm ⇒ ai cũng thấy nó ở
trạng thái *chưa xong*, không ai phải làm lại gì.

---

## 10. Nội dung mới cần bao nhiêu

| Thứ | Số lượng |
|---|---:|
| Ảnh mới | **0** (sinh bằng vector) |
| Câu quiz mới | **0** |
| Bài đọc mới | **0** |
| Lời thoại Comet/Byte (vi + en) | **~60 khoá** |
| Bộ dữ liệu mẫu | **0 tay** — sinh bằng mã, có tham số điều khiển độ lệch |

⇒ **Đây là lý do chính tôi ủng hộ.** Nó gần như không đẻ thêm nợ nội dung — khác hẳn
tám game, mà riêng Next Token đã cần chọn tay ~30 câu + một bộ sinh n-gram.

---

## 11. Cái tôi KHÔNG chắc

- **Chưa đọc toàn văn phụ lục QĐ 2422.** Bốn mạch và "không có bài kiểm tra" lấy từ
  cổng thông tin Bộ + báo chí. **Yêu cầu cần đạt theo từng cấp thì tôi chỉ có bản
  tường thuật.** Phải đọc phụ lục gốc trước khi in lên trang bán hàng.
- **Không có số nào nói trẻ sẽ chơi hết.** Không đo được trước khi dựng. Đây là rủi ro
  thật và nó là lý do đề nghị **một** thẻ.
- **Chưa đọc bảng "Người đến từ đâu"** — việc 1 của review 26/08 **vẫn còn treo**. Tức
  đợt sửa landing 26/08 tới giờ **vẫn chưa biết có tác dụng hay không**, và đợt này sẽ
  chồng lên nó nếu không đặt nhãn chiến dịch riêng.
- **Chưa kiểm** trường học Việt Nam mua tài liệu CLB theo đường nào, giá nào, ai quyết.
  Toàn bộ mục 3 nói *cơ hội có thật*; nó **không** nói *bán được*.
- **Ước lượng dòng mã ở mục 8** chưa phải số đo, trừ hai dòng đầu.
- **Chưa quyết 7a hay 7b** — cần chủ dự án chốt vì nó là đánh đổi *danh tính bán hàng*
  ↔ *chi phí tách vỏ*.

---

## 12. Việc, theo thứ tự

1. **Đọc bảng "Người đến từ đâu"** cho chiến dịch AI. Vẫn treo từ 26/08, 5 phút, và nó
   nói việc sửa câu chữ lần trước có tác dụng hay không. **Đừng chồng đợt hai lên một
   đợt chưa đo.**
2. **Tải và đọc toàn văn phụ lục QĐ 2422/QĐ-BGDĐT.** Nó quyết định câu chữ được phép
   nói và ánh xạ ở mục 6.
3. **Chủ dự án chốt 7a hay 7b** (cùng lưới `lab.html`, hay trang `ailab.html` riêng).
4. **Dựng `LAB-AI-01`** — hai chế độ, một engine, dữ liệu sinh bằng vector.
5. **Đo trẻ có chơi hết không.** Chỉ sau đó mới quyết game thứ hai.
6. *(vòng sau, nếu ①–⑤ đạt)* **Next Token** — sinh mô hình n-gram offline từ kho chữ
   của dự án, ship JSON vài KB.
7. *(vòng sau)* quyết mạch ④ "Thiết kế hệ thống AI" — lấp hay ghi là trống.

⚠️ **Đừng làm cả 8 game.** Không phải vì chúng dở — mà vì cổng `009` vẫn cần 110 câu
nữa, và tám game là đủ để nuốt trọn quý mà không trả lời được câu hỏi mà **một** thẻ
đã trả lời được.

---

## 13. Nguồn

- Quyết định 2422/QĐ-BGDĐT — [moet.gov.vn](https://moet.gov.vn/tin-tuc/ban-hanh-khung-noi-dung-giao-duc-tri-tue-nhan-tao-cho-hoc-sinh-pho-thong2.html) · [Cổng TTĐT Chính phủ](https://xaydungchinhsach.chinhphu.vn/quyet-dinh-so-2422-qd-bgddt-ve-khung-noi-dung-giao-duc-tri-tue-nhan-tao-ai-cho-hoc-sinh-pho-thong-119260820163256297.htm) · [LuatVietnam — bốn mạch, không có đầu điểm riêng](https://luatvietnam.vn/tin-van-ban-moi/quyet-dinh-2422-bgddt-noi-dung-giao-duc-ai-khong-co-bai-kiem-tra-va-dau-diem-rieng-186-111628-article.html)
- Breakable Machine — [arXiv 2508.14201](https://arxiv.org/abs/2508.14201) · [AAAI](https://ojs.aaai.org/index.php/AAAI/article/view/41525)
- Day of AI Australia — [studios.dayofaiaustralia.com](https://studios.dayofaiaustralia.com/)
- Hello!AI — [Int. J. Human–Computer Interaction (2025)](https://www.tandfonline.com/doi/full/10.1080/10447318.2025.2574514)
- AI4K12 Five Big Ideas — [ai4k12.org](https://ai4k12.org/)
