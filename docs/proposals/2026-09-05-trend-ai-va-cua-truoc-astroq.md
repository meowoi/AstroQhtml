# Trend AI lớn hơn thiên văn — cửa trước astroQ nên đổi thế nào?

**Ngày:** 05/09/2026 · **Người viết:** Claude (đối chiếu mã nguồn + tra nguồn ngoài)
**Trạng thái:** đang mở — chủ dự án chốt
**Câu hỏi của chủ dự án:** *"trend AI đang lớn hơn các trend khác, tôi ko thể quảng cáo AI mà vào
trang lại là thiên văn học được"*

---

## 0. Kết luận trước, lý lẽ sau

**Đừng đổi astroQ thành một app AI. Hãy kéo cây cầu AI↔vũ trụ đã có sẵn trong kho BÀI ĐỌC
sang phần trẻ CHƠI.**

Đo được: kho nội dung **đã nghiêng về AI rồi** (32/70 bài là AI+robot+CNTT, so với 17/70 thiên
văn), và **8/14 bài AI đã dùng bối cảnh vũ trụ để dạy AI**. Nhưng **11/11 mini-game và 2/2
nhiệm vụ đều thuần thiên văn**. Trẻ bấm quảng cáo AI, vào app, và mọi thứ nó **chạm vào** đều là
vũ trụ — vì phần AI nằm ở chỗ nó đọc ít nhất.

Đó là chỗ hỏng. Nó **không sửa được bằng câu chữ ở landing** (đã thử 26/08/2026 và câu hỏi này
vẫn được đặt ra), vì thứ nói dối không phải cái tiêu đề — mà là cái trẻ làm sau khi bấm vào.

---

## 1. Số đo (đếm từ mã nguồn, không phải ước lượng)

### 1a. Kho nội dung — đã nghiêng về AI

| Chủ đề | Số bài đọc | Tỉ lệ |
|---|---:|---:|
| astronomy | 17 | 24% |
| **ai** | **14** | **20%** |
| **robot** | **11** | **16%** |
| **it** | **7** | **10%** |
| physics · life · math · quantum · engineering | 21 | 30% |
| **Tổng** | **70** | |

**AI + robot + CNTT = 32/70 (46%)**, gần gấp đôi thiên văn.

### 1b. Nhưng phần TƯƠNG TÁC thì thuần thiên văn

| Bề mặt | Số lượng | Bao nhiêu cái nói về AI/công nghệ |
|---|---:|---:|
| Mini-game | 11 | **0** |
| Nhiệm vụ | 2 | **0** |
| Thẻ Sổ Tay Thuật Ngữ | 28 | 7 (ai) + 1 (robot) = **8** |
| Bản đồ / bối cảnh chính | 1 (Hệ Mặt Trời 3D) | **0** |

11 tên game: *Né Thiên Thạch · Đường Đua Sao Chổi · Phòng Thủ Không Gian · Ghép Chòm Sao · Mê Cung
Thiên Hà · Bắt Sao Băng · Trạm Sinh Tồn · Trạm Liên Lạc · Trạm Tuần Hoàn · Trạm Đối Chiếu ·
Trạm Dẫn Tuyến*. Không một cái nào dạy AI.

### 1c. Cửa trước vẫn đặt thiên văn ĐẦU TIÊN

- `<title>` trang chủ: *"Khám Phá Ngân Hà Tri Thức | **Vũ Trụ** · AI · Lượng Tử"*
- `meta description`: *"…STEM 3D về **Vũ trụ**, AI và Vật lý Lượng tử…"*
- 4 trụ kiến thức, theo thứ tự: **Thiên văn học** → Trí tuệ nhân tạo → Tư duy khoa học → Robotics
- `landing-app`: *"AstroQ — **Vũ trụ**, AI và tư duy khoa học"*
- Và tên thương hiệu: **astro**Q.

### 1d. Cây cầu ĐÃ TỒN TẠI — chỉ nằm sai chỗ

14 bài `cat:"ai"` chia làm hai nhánh:

- **AI trong không gian (8 bài)** — AI tìm tiểu hành tinh trong kho ảnh Hubble · AI + người tìm
  hơn 10.000 cặp sao đôi · AI dựng bản đồ hố tối · AI đoán trước bão Mặt Trời · AI gắn nhãn kho
  dữ liệu NASA · AI đếm bạt sau bão · AI tìm ngoại hành tinh · *AI là gì — câu trả lời của NASA*.
- **AI trong đời sống / tư duy phản biện (6 bài)** — *AI đã ở quanh bạn* · *Một thuật toán cũng là
  một ý kiến* · *Máy không cố ý thiên vị* · *Chatbot nói sai mà nghe rất đáng tin* · *Chatbot không
  nhớ điều bạn vừa kể* · *Ngay cả nhà khoa học cũng chưa hiểu hết cách chatbot hoạt động*.

⇒ astroQ **không thiếu nội dung AI**, và cũng **không phải chọn giữa AI và vũ trụ**. Nó đã có sẵn
8 bài chứng minh hai thứ đó là một.

---

## 2. Bằng chứng bên ngoài

### 2a. Nền tảng uy tín dạy AI bằng cách GẮN VÀO MỘT BỐI CẢNH — đúng khuôn astroQ cần

**Code.org — "AI for Oceans"**, dành cho trẻ **từ 8 tuổi** (đúng nhóm 8–15 của astroQ). Trẻ tự
**gán nhãn dữ liệu huấn luyện** để dạy một bot phân loại cá / rác, rồi **tự chọn nhãn của mình**
cho ảnh cá sinh ngẫu nhiên — bộ nhãn đó huấn luyện một mô hình để tự gán nhãn ảnh mới. Bài học
đi kèm là **training data & bias**. (Kỹ thuật bên dưới là transfer learning trên MobileNet.)

Đây là bằng chứng mạnh nhất của cả bản này: **bối cảnh (đại dương) và kỹ năng (AI) không xung
đột.** Bối cảnh là vỏ, AI là ruột. astroQ đang có một cái vỏ tốt hơn hẳn — một buồng lái phi
thuyền 3D — mà chưa nhét ruột AI vào.

Code.org cũng nói thẳng định hướng ở cấp trung học cơ sở: *"puts AI fluency at the center, so that
every student leaves knowing not just how to use AI, but how to think about it."*

### 2b. UNESCO: chuẩn AI cho học sinh KHÔNG đòi sản phẩm phải có AI

**AI competency framework for students** (UNESCO) có **4 dimensions**: *A human-centred mindset ·
Ethics of AI · AI techniques and applications · AI system design*, qua **3 mức**: *Understand ·
Apply · Create*.

Hai dimension **đứng đầu** là tư duy lấy con người làm trung tâm và đạo đức AI — tức **thứ astroQ
đã có 6 bài**. Nghĩa là astroQ dẫn được chuẩn quốc tế cho phần nội dung AI của mình **mà không
cần dựng một cỗ máy AI nào trong sản phẩm**.

*[Chưa kiểm chứng]* danh sách đầy đủ 12 competencies — trang tóm tắt của UNESCO không liệt kê,
phải đọc bản PDF gốc trước khi trích chi tiết.

### 2c. ⚠️ Phụ huynh — người TRẢ TIỀN — đang nghi ngờ AI

Đây là dữ kiện làm đảo hướng cách quảng cáo:

- **EdTrust** (Massachusetts, hơn **1.300 phụ huynh**, công bố 01/2026): *"Only a third feel
  positively, a third feel negatively and another third are unsure."*
- **Quinnipiac** (30/03/2026): **64% phụ huynh** cho rằng AI trong trường học **hại nhiều hơn lợi**.
- **Deloitte 2026 Back-to-School** (n=1.207): **49%** lo con **phụ thuộc AI quá mức**.
- Khoảng cách nhận thức: **86%** học sinh 13–17 thấy AI hữu ích, so với **64%** phụ huynh.

⚠️ **Tôi đã suýt trích một câu không có thật.** Kết quả tìm kiếm tóm tắt rằng *"niềm tin phụ huynh
GIẢM khi tiếp xúc TĂNG"*; mở trang gốc ra đọc thì **câu đó không có trong bài**. Đã bỏ. (Đúng lớp
lỗi CHNOPS / "170 km" / Nam Cực mà dự án đã mắc bốn lần.)

### 2d. Hệ quả marketing — quan trọng nhất của cả phần này

**"Trend AI lớn" KHÔNG có nghĩa là phụ huynh muốn AI dạy con.** Hai lời chào mời khác hẳn nhau:

| Lời chào | Phụ huynh nghe ra | astroQ có làm được không |
|---|---|---|
| *"Con bạn học **BẰNG** AI"* | đúng thứ 64% đang lo | **KHÔNG** — astroQ không có bề mặt AI nào |
| *"Con bạn học **VỀ** AI, để không bị AI dắt mũi"* | đánh trúng nỗi lo phụ thuộc (49%) | **CÓ** — 6 bài tư duy phản biện đã viết |

⇒ Không cần dựng AI tutor. **Chỗ đứng trống và astroQ vào được là: nền tảng dạy trẻ HIỂU AI, không
phải nền tảng dùng AI dạy trẻ.** Ràng buộc "AI là CHỦ ĐỀ trẻ học, không phải công nghệ trong sản
phẩm" (đã ghi ở `CLAUDE.md` từ 26/08) vì thế **không phải điểm yếu — nó là điểm bán hàng**, miễn
là nói thẳng ra.

---

## 3. Đề xuất — ba đợt, xếp theo tỉ lệ công/lợi

### Đợt 1 — "AI FOR SPACE": một mini-game trẻ TỰ HUẤN LUYỆN một bộ phân loại

**Đây là việc quan trọng nhất, và là thứ duy nhất thật sự chữa được mâu thuẫn được nêu.**

Khuôn: **ARCADE-12 · Trạm Phân Loại** (hoặc tên tương đương). Trẻ nhận một chồng "ảnh quét" từ
kho dữ liệu tàu → **tự gán nhãn** vài chục mẫu (ví dụ *có tiểu hành tinh* / *không có*) → bấm
**Huấn luyện** → máy tự phân loại một chồng ảnh MỚI trước mặt trẻ → trẻ thấy máy đúng bao nhiêu,
sai chỗ nào, và **vì sao nó sai** (vì bộ nhãn trẻ đưa vào bị lệch).

Vì sao khuôn này đúng cho astroQ:

- **Có nguồn NASA thật, đã viết rồi**: `art-ai-finds-asteroids-hubble` (AI lục kho ảnh cũ của
  Hubble), `art-ai-found-binary-stars` (AI + người, hơn 10.000 cặp sao đôi), `art-ai-tags-nasa-data`.
  Không phải đi tra nguồn mới — đúng lối `docs/decisions/002` đã dùng cho 5 game lớp quyết định.
- **Nó là khuôn THỨ SÁU của lớp quyết định** (chọn thẻ · xếp thứ tự · chia ngân sách · soi lỗi
  bảng · nối tuyến — nay thêm *dạy máy*), nên không vi phạm luật "một khuôn không quá 2 lần".
- **Bài học trung tâm là THIÊN LỆCH DỮ LIỆU** — thứ mà bảng `art-algorithmic-bias` và
  `art-algorithms-are-opinions` đã dạy bằng chữ, nay trẻ **tự gây ra rồi tự nhìn thấy**.
- ⚠️ **KHÔNG cần TensorFlow, không cần một byte mạng nào.** Một bộ phân loại k-NN hoặc perceptron
  trên 2–3 đặc trưng số (độ sáng · độ tròn · số điểm sáng) viết bằng vanilla JS là **đủ** để dạy
  *dữ liệu huấn luyện → mô hình → thiên lệch*. Kéo một thư viện ML về là hoàn tác đúng đợt gỡ
  `unpkg`/`gstatic` ngày 07/08 và đóng lại đường PWA.
- ⚠️ **Nhãn "MÔ PHỎNG" là bắt buộc**, cùng lối `game-recycle` / `game-units` / `mission-orbit`:
  đây là một bộ phân loại đồ chơi, không phải mô hình NASA dùng thật.

**Cái được, nói bằng câu quảng cáo:** *"Con bạn tự dạy một AI nhận ra tiểu hành tinh — rồi tự phát
hiện ra vì sao nó đoán sai."* Câu đó **đúng sự thật**, dùng được cho quảng cáo AI, và người bấm
vào **thấy đúng thứ đã hứa**.

### Đợt 2 — Nhiệm vụ thứ ba: "MẮT MÁY" (AI đọc dữ liệu)

Hai nhiệm vụ hiện có đều ở Trái Đất/quỹ đạo và đều thuần thiên văn. Nhiệm vụ thứ ba, 5 chặng, đi
qua đúng chuỗi UNESCO *Understand → Apply → Create*:

1. **Máy "nhìn" bằng gì** — ảnh là những con số (nguồn: `art-ai-tags-nasa-data`).
2. **Dạy máy một khái niệm** — dùng lại engine của Đợt 1.
3. **Máy đoán sai** — thiên lệch dữ liệu (`art-algorithmic-bias`).
4. **Người vẫn phải kiểm** — 10.000 cặp sao đôi là **AI cộng với người**
   (`art-ai-found-binary-stars`); đây là chặng chống lại đúng nỗi lo "phụ thuộc AI".
5. **Chốt** — con quyết định điều gì, máy quyết định điều gì.

Chi phí: vỏ màn chơi `js/mission-stage.js` đã dùng chung, nên nhiệm vụ mới chủ yếu là **nội dung +
một khuôn tương tác**, không phải dựng lại hạ tầng.

### Đợt 3 — Cửa trước nói đúng thứ bên trong có

Chỉ làm **SAU** đợt 1, không làm trước. Lý do: sửa câu chữ trước khi có nội dung là lặp lại đúng
lượt 26/08 — chữ đổi, cảm giác "vào trang lại là thiên văn" thì không.

- Trụ **"Trí tuệ nhân tạo" lên VỊ TRÍ ĐẦU** trong 4 trụ (hôm nay thiên văn đứng đầu).
- Thêm một dòng **nói ra chỗ đứng**: *"Học VỀ AI — không phải để AI làm bài hộ con."*
- ⚠️ **`<title>` / `meta description` / `og:*` là bề mặt bị Google và Facebook CACHE** — đổi thứ
  tự từ khoá ở đó là một quyết định SEO riêng, phải chốt tách bạch (luật đã ghi 26/08 và 18/08).
- ⚠️ **Đặt một nhãn chiến dịch MỚI** (ví dụ `sep2026-ai-lab`) trước khi đổi, không thì bảng
  *Người đến từ đâu* ở `admin-report.html` **không so được trước/sau** và cả lượt sửa này không đo
  được là có tác dụng hay không. Đây cũng là việc còn treo ⑤ của bản duyệt 04/09.

---

## 4. Đã bác — và vì sao

| Đường | Vì sao bác |
|---|---|
| **Đổi tên sản phẩm khỏi "astroQ"** | Tên miền đã go-live, 22 trang wiki + sitemap + hreflang + JSON-LD đều neo vào nó, và Google đã lập chỉ mục. Cái giá là toàn bộ SEO đã dựng; cái được là một chữ. |
| **Bỏ/giấu phần thiên văn** | Bác bằng chính số đo: nó là **17/70 bài** nhưng là **11/11 game và 2/2 nhiệm vụ** — tức gần như toàn bộ phần chơi được. Bỏ nó là bỏ sản phẩm. Và Code.org chứng minh không cần bỏ. |
| **Gắn một chatbot / AI tutor cho trẻ** | Ba lý do: 64% phụ huynh nói AI trong trường hại nhiều hơn lợi · astroQ chưa từng có một bề mặt AI nào nên đây là một sản phẩm khác chứ không phải một tính năng · và nó kéo theo cả một hạng mục an toàn cho trẻ em (nội dung sinh tự do, dữ liệu gửi ra ngoài) mà dự án đã cố ý từ chối từ đầu. |
| **Chỉ sửa câu chữ ở landing rồi chạy quảng cáo tiếp** | Đã làm 26/08. Câu hỏi hôm nay chính là bằng chứng nó chưa đủ. |
| **Dựng một khu AI RỜI, tách khỏi vũ trụ** | Thành hai app trong một app: bối cảnh buồng lái mất nghĩa, và mọi thứ dùng chung (`game-shell` · `mission-stage` · Sổ Tay · huy hiệu) phải có bản thứ hai. |

---

## 5. Cái tôi KHÔNG chắc — đọc trước khi quyết

1. ⚠️⚠️ **Đề xuất này KHÔNG chắc chữa được con số 99,6%.** Phễu thật (bản rà soát 04/09) mất
   ~99,6% **TRƯỚC form đăng ký**, và 14 ngày chỉ có **3 người ngoài** đăng ký. Chưa có phép đo nào
   chứng minh nguyên nhân là *chủ đề lệch*; hai giả thuyết khác vẫn còn sống (dải "hãy dùng máy
   tính" — đã bỏ 29/08; và **bước kích hoạt qua email**, nơi mất **2 trong 3** người ngoài). Đợt 1
   là việc đáng làm ngay cả khi giả thuyết chủ đề sai — nhưng **đừng kỳ vọng nó một mình đảo số**.
2. **[Chưa kiểm chứng]** Không có số liệu nào cho thấy "trend AI lớn hơn" **ở thị trường Việt Nam
   cho nhóm 8–15**; các con số ở mục 2c đều là khảo sát Mỹ. Trước khi đổi cả cửa trước theo một
   trend, nên đọc bảng *Người đến từ đâu* cho chiến dịch AI đang chạy — việc còn treo ② của bản
   rà soát 26/08, tới nay **vẫn chưa có một con số chuyển đổi nào**.
3. **[Chưa kiểm chứng]** 12 competencies của UNESCO (xem 2b).
4. **Chi phí Đợt 1 chưa ước lượng bằng số dòng.** Năm game lớp quyết định gần nhất mất ~400–600
   dòng mỗi cái; game này thêm phần bộ phân loại nên **[Suy luận]** có thể cao hơn, nhưng chưa đo.

---

## 6. Thứ tự đề nghị

1. Chủ dự án chốt: **có làm Đợt 1 không** (đây là quyết định thật sự, hai đợt sau phụ thuộc nó).
2. **Đọc bảng nguồn** cho chiến dịch AI đang chạy trước khi đổi cửa trước — hoặc thừa nhận rằng
   ta đang quyết mà không có số.
3. Đợt 1 → đo → Đợt 2 → Đợt 3 (kèm nhãn chiến dịch mới).

## Nguồn

- Code.org — AI for Oceans / AI curriculum: https://code.org/ai · https://code.org/oceans
- UNESCO — AI competency framework for students:
  https://www.unesco.org/en/articles/ai-competency-framework-students
- EdTech Magazine (dẫn khảo sát EdTrust MA 01/2026 và Quinnipiac 30/03/2026):
  https://edtechmagazine.com/k12/article/2026/04/parents-divided-artificial-intelligence-heres-how-schools-can-build-trust
- Common Sense Media — *Generation AI: What Kids and Families Think About AI*:
  https://www.commonsensemedia.org/sites/default/files/research/report/commonsensemedia_generationai.pdf
