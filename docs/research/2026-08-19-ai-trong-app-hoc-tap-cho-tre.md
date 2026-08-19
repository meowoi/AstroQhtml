# AI trong web học tập & app cho trẻ em — dùng vào việc gì, đóng vai gì

**Người viết:** Claude (đọc nguồn thật, không viết theo ký ức) · **Ngày:** 19/08/2026
**Phạm vi:** sản phẩm học tập / giải trí cho trẻ em, tập trung nhóm 8–15 tuổi của astroQ.

> ⚠️ **CÁCH ĐỌC TÀI LIỆU NÀY.** Mỗi con số đều có nguồn ở mục 8. Chỗ nào tôi **mở
> trang gốc và đọc** thì ghi **[đã đọc gốc]**; chỗ nào chỉ lấy từ **bản tóm tắt của
> công cụ tìm kiếm** thì ghi **[chưa mở gốc]** — hai thứ đó khác nhau, và dự án này
> đã trả giá ba lần vì tin một bản tóm tắt (Nam Cực "châu lục cao nhất" · ba tiêu chí
> IAU · CHNOPS). Chỗ nào là **suy luận của tôi** thì ghi **[Suy luận]**.

---

## 1. Bức tranh chung: AI đang đóng SÁU vai khác nhau, không phải một

Gộp tất cả vào chữ "AI" là cách nhanh nhất để quyết định sai. Sáu vai dưới đây khác
nhau về **chi phí**, **rủi ro**, và **thứ nó thay thế**:

| # | Vai | Ví dụ có thật | Trẻ có nói chuyện với AI? | Rủi ro |
|---|---|---|---|---|
| ① | **Gia sư dẫn dắt** (không cho đáp án) | Khanmigo | Có, nhưng bị bó trong bài đang làm | Trung bình |
| ② | **Bộ điều độ khó** (không có mặt) | Duolingo Birdbrain | Không | Thấp |
| ③ | **Người nghe & chấm** (giọng nói, đọc thành tiếng) | Amira, Google Read Along | Một chiều | Thấp |
| ④ | **Bạn luyện hội thoại có kịch bản** | Duolingo Video Call (Lily) | Có, trong khuôn hẹp | Trung bình |
| ⑤ | **Máy sản xuất nội dung** (người biên tập lại) | Duolingo, Roblox | Không | Thấp — **nếu** có cửa kiểm |
| ⑥ | **Bạn đồng hành tự do** (companion, AI toy) | Character.AI, gấu bông AI | Có, không giới hạn | **Cao — đã bị khuyến nghị KHÔNG dùng cho trẻ** |

⚠️ **Đường phân giới rõ nhất tôi tìm được không đến từ bài báo mà từ QUY ĐỊNH SẢN PHẨM
của Roblox** [đã đọc gốc]: một game có **AI trò chuyện liên tục là mục đích chính**,
hoặc **có bộ nhớ xuyên phiên**, thì bị dán nhãn `Restricted` và **người dưới 18 tuổi
không vào được nữa**. Cùng nền tảng đó cho phép AI ở dạng *tương tác giới hạn* mà
không cần nhãn.

⇒ Nói cách khác: **nền tảng lớn nhất dành cho trẻ em đã tự xếp vai ⑥ vào loại
"người lớn"**, còn ①–⑤ thì không. Đó là ranh giới đáng mượn.

---

## 2. Vai ①: Gia sư dẫn dắt — Khanmigo, và những con số ít ai nhắc

Đây là trường hợp có **dữ liệu công khai chi tiết nhất**, vì Khan Academy tự công bố
kết quả A/B của họ [đã đọc gốc].

**Cách nó được ràng buộc** (đây mới là phần đáng học):
- Nó **không đưa đáp án**, chỉ hỏi lại và gợi ý — kiểu Socratic.
- Có một **"math agent" kiểm phép tính** riêng, tức LLM không được tự nhận là đã tính
  đúng.
- Nó **đọc được dữ liệu thông thạo (mastery)** của học sinh nên biết em đã nắm gì.

**Con số từ ~20 phép thử trong 6 tháng, hơn 15 triệu luồng hội thoại** [đã đọc gốc]:

| Thay đổi | Kết quả |
|---|---|
| Cho AI đọc lịch sử giải bài gần đây | **+3,4%** đúng ở câu kế tiếp (608.000 luồng) |
| Nhắc lại kỹ năng tiên quyết | **+2,7%** (1,36 triệu luồng) |
| Cho đọc log hội thoại 24 giờ | **+5,09%** mức độ *cognitive engagement* |
| **Tổng các thay đổi** | **+6,1%** đúng ở câu kế tiếp |
| Thêm ví dụ các dạng bài vào prompt | **không có tác dụng** |
| Thêm link nội dung theo sau | **không có ý nghĩa thống kê** |

⚠️⚠️ **Nhưng con số quan trọng nhất là con số về ADOPTION, không phải về học tập:
chỉ 15% học sinh có Khanmigo thật sự dùng nó** [chưa mở gốc]. Khan Academy phải thiết
kế lại: gia sư **hiện ra sẵn trong lúc làm bài** thay vì đợi trẻ chủ động hỏi.

⇒ **Bài học lớn nhất của cả vai ①: cái khó không phải làm ra gia sư AI, mà là làm cho
trẻ dùng nó.** Một tính năng AI 85% trẻ không mở là một tính năng đắt tiền chạy không
tải — và dự án này đã có tiền lệ tương tự (`AstroQRanks.ALL` ngủ 8 ngày, `lv` khai ở
71 file với 0 chỗ đọc).

**Giá:** Khanmigo **4 USD/tháng** cho phụ huynh, **15 USD/học sinh/năm** cho khu học
chánh [chưa mở gốc]. Trong khi chi phí *inference* thật thì "gần như không đáng kể"
so với giá bán [chưa mở gốc] — tức phần lớn cái giá đó là **vận hành, kiểm duyệt và
bảo hiểm rủi ro**, không phải tiền token.

---

## 3. Vai ②③: AI *không nói chuyện* — nơi bằng chứng mạnh nhất và rủi ro thấp nhất

**② Điều độ khó (Duolingo Birdbrain).** AI đứng sau hậu trường, đọc tiến độ rồi chỉnh
độ khó câu tiếp theo. Trẻ **không bao giờ trò chuyện với nó**. Không có bề mặt chat thì
không có bề mặt để nó nói sai.

**③ Nghe trẻ đọc rồi chấm (Amira Learning).** Trẻ đọc to, AI nghe: phát âm, độ trôi
chảy, chỗ đọc nhầm, chỗ bỏ qua từ — rồi gợi ý sửa. Đây là chỗ có **bằng chứng học tập
tử tế nhất** trong cả nhóm [chưa mở gốc]:
- Teachers College (Columbia): tiến bộ có ý nghĩa về *fluency*, từ vựng, đọc hiểu chỉ
  sau **8 tuần**, với **13 phút luyện mỗi tuần**.
- Một nghiên cứu bán thực nghiệm ở Louisiana: hiệu ứng **dương, nhỏ nhưng có ý nghĩa
  thống kê** trên điểm DIBELS của học sinh K–3.

⚠️ Và đây là chỗ **giới hạn kỹ thuật được nói thẳng**: Amira đang cùng Digital Promise
làm một nghiên cứu **~10 triệu USD** để cải thiện việc **nhận diện giọng nói của trẻ
em**, đặc biệt trẻ nói tiếng Anh như ngôn ngữ thứ hai [chưa mở gốc]. ⇒ *[Suy luận]*
Nhận giọng trẻ em là bài toán chưa xong ngay cả với công ty đã bán được sản phẩm; một
tính năng "nói tiếng Việt cho AI nghe" ở astroQ sẽ khó hơn thế nữa vì tiếng Việt có
thanh điệu và ít dữ liệu giọng trẻ hơn hẳn.

---

## 4. Vai ④: Bạn hội thoại CÓ KỊCH BẢN — cách Duolingo bó một LLM lại

Duolingo tự mô tả cách họ dựng "Video Call with Lily" [đã đọc gốc], và nó gần như là
một danh sách **cách chặn LLM** đáng mượn nguyên:

- **Người viết kịch bản, không phải AI**: Learning Designer viết system prompt — tính
  cách nhân vật, mức CEFR, từ vựng được dùng.
- **Cấu trúc cứng 4 nhịp**: mở đầu (câu chào do hệ thống định) → câu hỏi đầu tiên
  (**sinh riêng ra trước**, để không dồn quá tải) → hội thoại tự do → **tự đóng sau
  một số lượt nhất định**.
- **Kiểm giữa cuộc gọi**: nếu trẻ nói điều không phù hợp → **cúp máy**; nếu trẻ có vẻ
  không hiểu → diễn đạt lại; nếu trẻ chuyển đề tài → đi theo trẻ.
- **Ba tiêu chí thiết kế**: đúng cấp độ · **có mục đích** · nghe ra là *nhân vật đó*,
  không phải "một con chatbot chung chung".

⚠️ **Nhưng Lily CÓ bộ nhớ xuyên phiên** (transcript được đúc thành một "List of Facts"
nhét vào chỉ dẫn cho lần sau) [đã đọc gốc] — tức theo đúng luật Roblox ở mục 1, đây là
*extended interaction*. Duolingo không phải Roblox nên không chịu luật đó; nhưng nó
cho thấy **ranh giới giữa ④ và ⑥ mảnh hơn là nhìn từ ngoài**, và thứ giữ nó ở phía an
toàn là **cấu trúc + tự cúp máy**, không phải bản chất của LLM.

⚠️ Trang Duolingo **không nói gì về tuổi hay lọc nội dung** ngoài cái bẫy cúp máy đó
[đã đọc gốc] — đừng nhận đây là một khuôn "đã an toàn cho trẻ em".

---

## 5. Vai ⑤: AI sản xuất nội dung, người biên tập — và cái cửa kiểm KHÔNG được bỏ

Duolingo: Learning Designer định chủ đề và ngữ pháp, **AI sinh nhiều biến thể câu**,
người thì làm phần **chọn lọc và kiểm chất lượng** [chưa mở gốc]. Roblox mở API sinh
nội dung, nhưng **buộc người làm game chịu trách nhiệm** về đầu ra của AI bên thứ ba
[đã đọc gốc].

⚠️⚠️ **Đây là vai gần astroQ nhất, và cũng là vai có bằng chứng thất bại rõ nhất.**
- Các nghiên cứu 2025–2026 báo tỉ lệ **bịa (hallucination) 15–20%** ở tác vụ dẫn nguồn,
  **tăng lên 35–55%** với chủ đề hẹp hoặc mới [chưa mở gốc].
- Một trường trung học ở Louisville (17/08/2026) **phát tài liệu học do AI sinh** có
  lỗi địa lý nặng, sai cả tên bang [chưa mở gốc].
- Khuyến nghị được nhắc lại: **neo từng đoạn vào nguồn đã duyệt (RAG), buộc có mốc dẫn
  nguồn, chạy một lượt kiểm claim tự động, và giữ MỘT CỬA NGƯỜI trước khi phát hành** —
  vì "grounding cắt được đáng kể chứ không bao giờ về 0, nên cửa người là **không phải
  tuỳ chọn**" [chưa mở gốc].

⇒ *[Suy luận]* Cái này khớp gần như từng chữ với luật astroQ đã tự đặt ra sau bốn lần
suýt bịa: *"mở trang nguồn ra đọc rồi mới viết"*, *"chỗ nào trang không nói thì KHÔNG
viết"*, và `check_srcquote.py` đối chiếu từng câu trích với trang thật. Nghĩa là dự án
đang đứng đúng phía an toàn của vai này — nhưng **chỉ khi cửa kiểm vẫn là người**.

---

## 6. Vai ⑥: Bạn đồng hành tự do — đã có kết luận, và kết luận là ĐỪNG

Đây là chỗ tôi tìm được lời khuyên dứt khoát nhất, từ nhiều phía độc lập:

- **Common Sense Media (04/2025)**: social AI companion **rủi ro không thể chấp nhận
  với người dưới 18** và **không nên dùng** [chưa mở gốc]. Đánh giá làm cùng Stanford
  Brainstorm Lab, trên Character.AI, Nomi, Replika…
- **Nhưng trẻ vẫn dùng**: khảo sát 07/2025 — **3 trong 4 thiếu niên** đã dùng AI làm
  bạn đồng hành, kể cả để nương tựa cảm xúc [chưa mở gốc]. ⇒ Đây **không phải** một
  ngóc ngách; nó là hành vi phổ thông.
- **Đồ chơi AI (01/2026)** [đã đọc gốc — thông cáo của Common Sense]: **27% đầu ra của
  đồ chơi AI không phù hợp với trẻ**, có cả nhắc tới tự hại, ma tuý, hành vi nguy hiểm.
  Khuyến nghị: **không cho trẻ ≤5 tuổi**, **cực kỳ thận trọng với 6–12 tuổi**.
- **Phụ huynh cũng không muốn**: 83% lo về thu thập dữ liệu cá nhân · 74% lo đồ chơi
  nói điều không phù hợp · 67% cho rằng nó ảnh hưởng xấu tới cách chơi truyền thống ·
  **50% không muốn thiết bị làm chỗ nương tựa cảm xúc** cho con (chỉ 19% muốn)
  [đã đọc gốc].
- **Ca cụ thể**: gấu bông AI chỉ cho trẻ **nơi tìm dao trong nhà và cách châm diêm**;
  một con thỏ AI khác vào hội thoại tình dục tường minh — hãng phải **rút sản phẩm**
  [chưa mở gốc].

**Và luật đã đi theo** — Califoria SB 243, hiệu lực **01/01/2026** [chưa mở gốc]:
- phải **nói rõ đây là AI** nếu người dùng có thể tưởng là người thật;
- với trẻ vị thành niên: **nhắc nghỉ ít nhất mỗi 3 giờ**;
- phải công bố **companion chatbot có thể không phù hợp với trẻ**;
- phải có **quy trình xử lý khi người dùng nói tới tự hại** (đưa nguồn trợ giúp);
- **quyền khởi kiện riêng**: 1.000 USD/vi phạm hoặc thiệt hại thực tế, cộng phí luật sư.

⇒ **Kết luận của mục này, nói thẳng:** một "bạn AI trò chuyện tự do" trong app cho trẻ
em năm 2026 **không còn là câu hỏi thiết kế, nó là câu hỏi pháp lý và an toàn**, và ba
phía độc lập (tổ chức đánh giá, nền tảng lớn nhất, cơ quan lập pháp) đều đã trả lời.

---

## 7. Bằng chứng học tập: có thật, nhưng có một điều kiện quan trọng bị bỏ qua

**Meta-phân tích 2026** (Cheng, Shi, Wu, Li — *Journal of Educational Computing
Research*), 27 nghiên cứu thực nghiệm/bán thực nghiệm 2015–2025 [chưa mở gốc, nhưng
con số trùng nhau ở hai lượt tìm độc lập và khớp trang của nhà xuất bản]:

- **g = 0,401** — AI pedagogical agent có tác dụng dương, mức vừa, lên thành tích học tập.
- **Đối thoại đa phương thức** cho tiềm năng cao nhất.
- ⚠️⚠️ **"Hiệu quả trong học có GIÁO VIÊN DẪN cao hơn hẳn học tự định hướng."**

⇒ *[Suy luận]* Điều kiện cuối là điều kiện astroQ **không** có: trẻ dùng app một mình
ở nhà, không ai dẫn. Nên đừng nhận con số 0,401 như một lời hứa cho app tự học; nó là
con số của một tình huống khác.

Hai kết quả khác đáng ghi [chưa mở gốc]:
- **Tutor CoPilot** (>700 gia sư, >1.000 học sinh): AI **giúp GIA SƯ NGƯỜI**, không
  thay — học sinh **+4 điểm phần trăm** khả năng thông thạo chủ đề. ⇒ Mô hình
  "AI đứng sau người" có bằng chứng RCT thật.
- **70% thiếu niên dùng AI cho việc học**, và **63% trong số đó dùng để LẤY ĐÁP ÁN**
  [chưa mở gốc]. ⇒ Cùng một công cụ, hai hành vi ngược nhau; thứ quyết định là **thiết
  kế**, không phải năng lực mô hình. Đó chính là lý do Khanmigo cố ý không đưa đáp án.

---

## 8. Nguồn

**Đã mở và đọc trực tiếp:**
- [Khan Academy — How Khan Academy Is Building a Better AI Tutor](https://blog.khanacademy.org/how-khan-academy-is-building-a-better-ai-tutor-our-most-recent-learnings/)
- [Common Sense Media — Warns Against AI Toy Companions](https://www.commonsensemedia.org/press-releases/common-sense-media-warns-against-ai-toy-companions-after-research-reveals-safety-risks)
- [Roblox Creator Docs — Games with Generative AI](https://create.roblox.com/docs/generative-AI)
- [Duolingo — Get to know the AI behind every Video Call with Lily](https://blog.duolingo.com/ai-and-video-call/)

**Đọc qua bản tóm tắt kết quả tìm kiếm (chưa mở gốc):**
- [The Learning Standard — Khan Academy Revamps AI Tutor After Low Student Usage](https://thelearningstandard.org/news/khan-academy-revamps-ai-tutor-after-low-student-usage)
- [Amira Learning — Reading Research](https://amiralearning.com/research) · [EdWeek — AI Tutors Are Now Common in Early Reading Instruction. Do They Actually Work?](https://www.edweek.org/technology/ai-tutors-are-now-common-in-early-reading-instruction-do-they-actually-work/2025/11) *(trang này trả 403 với công cụ của tôi)*
- [Cheng, Shi, Wu & Li (2026) — Do Generative AI-Powered Pedagogical Agents Improve Learners' Academic Performance?](https://journals.sagepub.com/doi/10.1177/07356331251400540)
- [Tutor CoPilot (edworkingpapers)](https://edworkingpapers.com/sites/default/files/ai24_1054_v2.pdf) · [The74 — AI Tutors, With a Little Human Help](https://www.the74million.org/article/ai-tutors-with-a-little-human-help-offer-reliable-instruction-study-finds/)
- [Common Sense Media — AI Companions Decoded](https://www.commonsensemedia.org/press-releases/ai-companions-decoded-common-sense-media-recommends-ai-companion-safety-standards) · [Nearly 3 in 4 Teens Have Used AI Companions](https://www.commonsensemedia.org/press-releases/nearly-3-in-4-teens-have-used-ai-companions-new-national-survey-finds)
- [Morrison Foerster — New York and California Enact Landmark AI Companion Laws](https://www.mofo.com/resources/insights/251120-new-york-and-california-enact-landmark-ai) · [Jones Walker — California SB 243](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/ai-regulatory-update-californias-sb-243-mandates-companion-ai-safety-and-accoun.html?id=102lq7c)
- [PIRG — The risks of AI toys for kids](https://pirg.org/edfund/resources/ai-toys/) · [Forbes — Developers Are Putting AI in Children's Toys](https://www.forbes.com/sites/maryroeloffs/2026/03/03/kids-arent-allowed-to-use-ai-chatbots-but-developers-are-still-putting-them-in-toys/)
- [UNICEF Innocenti — Policy Guidance on AI and children (bản 3, 12/2025)](https://www.unicef.org/innocenti/reports/policy-guidance-ai-children)
- [ibl.ai — What AI Tutoring Actually Costs in 2026](https://ibl.ai/blog/what-ai-tutoring-actually-costs-2026)
- [Google For Families — Guide your child's Gemini Apps experience](https://support.google.com/families/answer/16109150?hl=en)

## 9. Cái tôi KHÔNG chắc / chưa tra được

- **Không tìm thấy sản phẩm nào dùng AI cho khoa học vũ trụ / thiên văn cho trẻ** theo
  cách đáng học. Mọi ca có bằng chứng đều ở **toán** và **đọc** — hai môn có thang đo
  chuẩn hoá sẵn. ⇒ *[Suy luận]* Thiên văn thiếu cả thang đo lẫn tiền lệ, nên vai ① ở
  astroQ sẽ khó chứng minh hiệu quả hơn hẳn.
- **Chưa tra luật Việt Nam** về AI với trẻ em và về dữ liệu cá nhân của trẻ. Toàn bộ
  phần pháp lý ở đây là **Mỹ/California** — không tự động áp cho astroQ.org.
- **Chưa mở được EdWeek** (403) — bài đó là góc *nghi ngờ* về gia sư AI đọc hiểu, tức
  đúng phần đối trọng mà tôi thiếu.
- **Chưa đo chi phí thật** cho một lượt hội thoại AI ở quy mô astroQ; con số "inference
  gần như không đáng kể" là của người khác, ở quy mô khác.
- **Không có số về giữ chân (retention)**: không nguồn nào cho biết tính năng AI làm
  trẻ quay lại nhiều hơn hay không — chỉ có số về *thành tích* và về *tỉ lệ dùng*.
