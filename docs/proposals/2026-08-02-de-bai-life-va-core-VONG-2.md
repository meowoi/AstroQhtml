# Đề bài VÒNG 2 gửi ChatGPT — bước ⑤ `life` và ⑦ `core`

**Ngày:** 2026-08-02 · **Người soạn:** Claude (sau khi đối chiếu vòng 1 với mã nguồn)
**Vòng 1:** `2026-08-02-chatgpt-life-va-core-vong-1.md` — **bác cả hai**, cùng một lý do

> **Cách dùng:** dán TOÀN BỘ phần trong khung dưới đây vào ChatGPT. Bản này **tự đứng được**,
> không cần dán lại đề bài vòng 1 hay `docs/BRIEFING.md`.
>
> Khác vòng 1 ở ba chỗ: ① ngân sách khuôn ghi thành **bảng có số chỗ còn trống** thay vì một
> câu luật · ② hai lối thoát sai đã đặt tên sẵn để không đi lại · ③ bước ⑦ nói thẳng là **đã
> dựng xong**, nên phải hay hơn bản đang chạy chứ không phải chỉ khác nó.

---

```
Đây là VÒNG 2. Vòng 1 của bạn đã bị bác — không phải vì kịch bản dở, mà vì cả hai bản
đều vượt cùng một ràng buộc đếm được. Bản này nói thẳng con số ra để bạn thiết kế
trong khuôn đó ngay từ đầu.

Hãy trả lời theo đúng khuôn ở cuối. Nếu một mục nào đó bạn không đủ thông tin để điền,
hãy ghi "không đủ thông tin" thay vì đoán — phần này sẽ được đối chiếu với mã nguồn thật.

════════════════════════════════════════════════════════════════════════
BỐI CẢNH (đọc lại, bản này tự đứng được)
════════════════════════════════════════════════════════════════════════

Nhiệm vụ "Hành Tinh Xanh" cho trẻ 8–15 tuổi: khám phá Trái Đất qua 7 bước, TẤT CẢ trên
MỘT TRANG DUY NHẤT, nền là BẢN ĐỒ THẾ GIỚI PHẲNG bằng ẢNH VỆ TINH THẬT (equirectangular).
Không tải lại trang; chuyển bước bằng cách lướt/phóng khung nhìn bản đồ.

  ① scan     — chạm 7 châu lục trên bản đồ → câu đố 2 lựa chọn "nước hay đất nhiều hơn?"
  ② timeline — bấm lần lượt 5 mốc trên MỘT THANH NGANG thời gian; mỗi mốc đổi tông màu
               cả hành tinh + hiện một bức tranh minh hoạ
  ③ sun      — câu đố 3 lựa chọn "nếu Mặt Trời tắt thì sao?" → bản đồ tối đi → kể 3 vai
               trò của Mặt Trời → sáng lại → chạm 3 vùng khí hậu
  ④ energy   — kéo-thả 3 thẻ năng lượng sạch vào 3 nhà máy neo trên bản đồ
  ⑤ life     — ⚠️ CẦN KỊCH BẢN MỚI
  ⑥ eco      — kéo-thả 7 thẻ hành động vào 2 rổ NÊN LÀM / KHÔNG NÊN LÀM
  ⑦ core     — ⚠️ CẦN KỊCH BẢN MỚI (nhưng đọc kỹ mục "⑦ đã dựng xong" bên dưới)

════════════════════════════════════════════════════════════════════════
⚠️⚠️ RÀNG BUỘC SỐ 1 — NGÂN SÁCH KHUÔN. ĐÂY LÀ THỨ ĐÃ BÁC VÒNG 1.
════════════════════════════════════════════════════════════════════════

Dự án có 5 khuôn tương tác dùng chung. Luật: **một nhiệm vụ không dùng cùng một khuôn
quá 2 LẦN.** Đây không phải hướng dẫn mềm — nó đã bác nguyên vòng 1.

Đếm bằng công cụ trên mã nguồn thật, KHÔNG phải ước lượng:

┌─────────────────────────┬────────────┬──────────────────────┬──────────────┐
│ Khuôn                   │ Đã dùng    │ Ở bước nào           │ CÒN TRỐNG    │
├─────────────────────────┼────────────┼──────────────────────┼──────────────┤
│ signal_scan             │ 3 / 2      │ ① ③ và ⑤ bản cũ     │ ⛔ ĐÃ VƯỢT   │
│ (chạm dấu hiệu/marker)  │            │                      │              │
├─────────────────────────┼────────────┼──────────────────────┼──────────────┤
│ profile_builder         │ 2 / 2      │ ④ ⑥                 │ ⛔ ĐÃ ĐẦY    │
│ (thẻ → ô, kéo HOẶC bấm) │            │                      │              │
├─────────────────────────┼────────────┼──────────────────────┼──────────────┤
│ câu đố chọn đáp án      │ 2 / 2      │ ① ③                 │ ⛔ ĐÃ ĐẦY    │
├─────────────────────────┼────────────┼──────────────────────┼──────────────┤
│ sequence_reconstruction │ 1 / 2      │ ②                    │ ✅ CÒN 1 CHỖ │
│ (sắp đúng thứ tự)       │            │                      │              │
├─────────────────────────┼────────────┼──────────────────────┼──────────────┤
│ orientation_align       │ 0 / 2      │ (bước dùng nó đã bỏ) │ ⚠️ xem dưới  │
│ (ngắm/canh cho thẳng)   │            │                      │              │
└─────────────────────────┴────────────┴──────────────────────┴──────────────┘

⚠️ `orientation_align` CÒN TRỐNG NHƯNG COI NHƯ KHÔNG DÙNG ĐƯỢC: nó là "kéo xoay cho hai
   thứ thẳng hàng", sinh ra cho một bước đã bị bỏ hẳn, và cả nhiệm vụ **cấm mọi cú kéo
   bản đồ** (ràng buộc 4 bên dưới). Muốn dùng thì phải giải thích được nó canh cái gì mà
   không đụng vào bản đồ.

⇒ Bạn có ĐÚNG MỘT chỗ trống dùng ngay được: `sequence_reconstruction`, và nó chỉ dùng
  được cho MỘT trong hai bước. Bước còn lại **buộc phải** là một trong hai đường sau:

  (A) Một khuôn HOÀN TOÀN MỚI — được phép, nhưng phải mô tả rõ nó là gì, vì sao 5 khuôn
      cũ không làm được, và làm bằng bàn phím thế nào. Chi phí sẽ bị cân đo.
  (B) Không phải trò chơi — một nhịp kể chuyện / xác nhận / tổng kết, và bạn nói thẳng
      là nó không có cơ chế chơi. Cách này CHẤP NHẬN ĐƯỢC cho bước ⑦ (bước cuối, ngay
      trước màn thưởng), NHƯNG KHÔNG chấp nhận cho bước ⑤ — xem ràng buộc 2.

⛔ ĐỪNG lập luận "cùng khuôn nhưng trình bày khác nên không tính". Luật chỉ cho phép lập
   luận đó ở lần thứ 2, không phải lần thứ 3. Vòng 1 bạn đã làm đúng chuyện này hai lần:
   "ghép biểu tượng vào câu" là thẻ→ô lần thứ 3, "chọn 1 trong 3 câu kết" là câu đố lần
   thứ 3. Đổi kéo-thả sang bấm-chọn-hai-phía cũng KHÔNG gỡ được — vẫn là một khuôn.

════════════════════════════════════════════════════════════════════════
⚠️⚠️ RÀNG BUỘC SỐ 2 — ĐỪNG GỠ BỎ TƯƠNG TÁC ĐỂ TRÁNH TRÙNG LẶP.
════════════════════════════════════════════════════════════════════════

Đây là lỗi thứ hai của vòng 1, riêng bước ⑤.

Bước ⑤ HIỆN TẠI đã là: *camera tự lướt tới từng nơi, trẻ chạm vào chỗ đang phát sáng*.
Lời thoại hiện có nói đúng thế: "mình sẽ đưa bạn tới từng nơi, bạn chỉ cần chạm vào chỗ
đang sáng."

Vòng 1 của bạn khác bản đang chạy **đúng một điều: CHỖ TRẺ BẤM** — từ chạm marker trên
ảnh vệ tinh, đổi thành bấm nút "Mở ghi chép tiếp theo". Ba hệ quả:

  · Nhịp giữa thành 8 cú bấm xác nhận liên tiếp (4 lần "mở" + 4 lần "đã hiểu"), không có
    một quyết định nào. Đó là một đoạn phim có nút, không phải một bước.
  · Nó dời cú bấm RA KHỎI tấm bản đồ — mà ảnh vệ tinh thật là tài sản duy nhất của cả
    nhiệm vụ này. Chạm vào Nam Cực trên ảnh thật khác hẳn bấm một cái nút.
  · Phần duy nhất còn quyết định (nhịp ghép) lại là khuôn thứ 3.

⇒ Bước ⑤ phải có một việc để TRẺ QUYẾT ĐỊNH, và quyết định đó nên có liên hệ với tấm
  bản đồ. "Đọc rồi bấm Đã hiểu" không phải một quyết định.

════════════════════════════════════════════════════════════════════════
BƯỚC ⑤ `life` — đề bài
════════════════════════════════════════════════════════════════════════

Bản cũ (đã bỏ): trẻ chạm 4 vùng, mỗi lần một chiếc drone bay xuống quét bằng laser rồi
hiện thẻ mẫu vật. Bị bác vì bước ① nay ĐÃ LÀ một chuyến đi khắp bề mặt — làm lại cùng
thao tác đó với một cỗ máy to hơn thì trẻ hỏi "sao lại phải làm lại?".

⚠️ RÀNG BUỘC CỨNG KHÔNG ĐỔI: bước này BẮT BUỘC trao đủ 4 mẫu dữ liệu sau, vì máy chủ gắn
chúng vào chính id bước này (đổi là phải sửa server + phát hành lại):

    · 🌊 Đại Tây Dương   (lat 12,  lon −42)  — "nước phủ ~71% bề mặt Trái Đất"
    · 🌳 Rừng Amazon     (lat −4,  lon −62)  — "rừng cung cấp oxy để thở"
    · 🐧 Nam Cực         (lat −75, lon  20)  — "hàng triệu loài cùng sống trên Trái Đất"
    · 🏔️ Dãy Himalaya    (lat 28,  lon  87)  — "núi cao che chắn và giữ nước"

Bốn cái tên và bốn toạ độ KHÔNG ĐƯỢC ĐỔI. CÁCH trẻ nhận chúng thì tự do.

Tiêu đề bước hiện tại là **"Sự sống ở khắp nơi"** — một kịch bản làm cho câu đó thành
điều trẻ tự chứng minh được sẽ mạnh hơn một kịch bản chỉ nói ra nó.

Gợi ý một hướng đã được cân nhắc (bạn KHÔNG bắt buộc theo, và nếu theo thì phải tự kiểm
lại nó có ổn không): bốn nơi này có một trục sắp xếp có thật là **độ cao** — đáy Đại Tây
Dương → Amazon → Nam Cực → Himalaya. Xếp chúng theo trục đó thì dùng đúng chỗ trống
`sequence_reconstruction` còn lại, và khác hẳn bước ② về cách trình bày (② là thanh NGANG
theo thời gian; đây có thể là cột DỌC theo độ cao). Nếu bạn thấy hướng khác tốt hơn thì
cứ đề xuất — nhưng phải nằm trong ngân sách khuôn ở trên.

════════════════════════════════════════════════════════════════════════
BƯỚC ⑦ `core` — ⚠️ ĐÃ DỰNG XONG. BẠN PHẢI HAY HƠN BẢN ĐANG CHẠY.
════════════════════════════════════════════════════════════════════════

Vòng 1 bạn đề xuất "Báo cáo sứ mệnh" — hoá ra gần trùng thứ đã chạy trong sản phẩm. Nói
rõ để vòng 2 không lặp lại:

BẢN ĐANG CHẠY: một bảng tên "HỒ SƠ TRÁI ĐẤT" gồm 3 dòng, mỗi dòng có dấu ✓ sẵn:
    ✓ Nước phủ khoảng 71% bề mặt — nhiều hơn hẳn đất liền.
    ✓ Nhiệt độ vừa phải, và khác nhau theo vùng vì góc chiếu của nắng.
    ✓ Khí quyển có oxy để thở, bọc quanh cả hành tinh.
  cộng MỘT nút "🗂️ ĐÓNG DẤU HOÀN THÀNH". Bấm xong Comet nói:
    "Đã đóng dấu! Phải có ĐỦ CẢ BA cùng một lúc — và tới giờ Trái Đất vẫn là nơi duy
     nhất chúng ta biết là có sự sống."
  rồi sang màn tổng kết.

Ba dòng đó là ba thứ mà các bước TRƯỚC đã dạy (71% ← ①, góc chiếu ← ③, oxy ← ② và phần
mở đầu). Trong mã nguồn có hai ghi chú cảnh báo viết sẵn ngay trên đoạn này:

  ⚠️ "MỘT CÚ BẤM, KHÔNG PHẢI MỘT CÂU ĐỐ. Đây là chỗ CHỐT, không phải chỗ kiểm tra: bắt
      trẻ trả lời đúng mới cho về là dựng một cửa chặn ngay trước màn thưởng."
  ⚠️ "Ba dòng = ba thứ nhiệm vụ ĐÃ dạy. Đừng thêm dòng thứ tư nếu không có bước nào dạy nó."

Bản 7 dòng của vòng 1 (mỗi dòng một bước đã qua) không phạm ghi chú thứ hai, nhưng nó
ĐÁNH ĐỔI MẤT câu chốt khoa học "phải có đủ cả ba cùng một lúc" — ba điều kiện của sự sống
là một ý mạnh hơn bảy việc vừa làm.

⇒ Vì vậy với bước ⑦ bạn có ba lựa chọn, và **"giữ nguyên" là một câu trả lời hợp lệ**:

   (i)   Nói thẳng: bản đang chạy đã đủ tốt, không nên đổi. Nêu lý do. — HỢP LỆ, không
         bị coi là né việc.
   (ii)  Giữ cấu trúc đó nhưng đề xuất cải thiện KHÔNG thêm cơ chế (ví dụ đổi tên bảng,
         đổi lời thoại, đổi cách trình bày ba dòng).
   (iii) Một kịch bản khác hẳn — nhưng nó phải HAY HƠN bản trên, không được dùng câu đố
         (đã đầy 2/2), và phải giữ được ý "ba thứ phải có ĐỦ CẢ BA cùng lúc".

⚠️ Bước ⑦ KHÔNG gắn mẫu dữ liệu nào, KHÔNG gắn huy hiệu nào → nội dung tự do hoàn toàn.
   Nó chỉ cần là một cái kết xứng đáng và dẫn được vào màn tổng kết.

════════════════════════════════════════════════════════════════════════
RÀNG BUỘC CỨNG CÒN LẠI — giữ nguyên từ vòng 1
════════════════════════════════════════════════════════════════════════

1. KHÔNG THÊM / BỎ / GỘP / ĐỔI TÊN BƯỚC. Vẫn đúng 7 bước, đúng thứ tự, đúng id. Id bước
   là khoá trong cơ sở dữ liệu người chơi. Bạn chỉ đổi VIỆC TRẺ LÀM bên trong ⑤ và ⑦.

2. VỪA MÀN ĐIỆN THOẠI DỌC 390×844. Số đo thật: ở mức phóng của nhiệm vụ, màn đó chỉ thấy
   **83 độ kinh tuyến** một lúc. Bốn toạ độ của bước ⑤ trải **149 độ** — KHÔNG BAO GIỜ
   cùng nằm trong khung. Cơ chế nào đòi nhìn/kéo giữa nhiều điểm xa nhau TRÊN BẢN ĐỒ là
   không chơi được trên điện thoại. (Thẻ trong một bảng nổi thì khác — bảng không phải
   bản đồ.)

3. KHÔNG CÓ CÚ KÉO BẢN ĐỒ NÀO. Trẻ không kéo/xoay/phóng bản đồ; cảnh tự dời khi cần.

4. CHƠI ĐƯỢC HOÀN TOÀN BẰNG BÀN PHÍM, tương đương chuột. Không phải chỉ thêm nhãn trợ năng.

5. KHÔNG TRẠNG THÁI THUA, KHÔNG PHẠT, KHÔNG ĐẾM NGƯỢC. Sai thì khích lệ và thử lại.

6. HOÀN THÀNH ĐƯỢC KHI TẮT HOẠT CẢNH (`prefers-reduced-motion`): không đòi trẻ bắt kịp
   vật đang chuyển động, không bắt chờ hoạt cảnh chạy xong mới giải được.

7. KHÔNG CON SỐ NÀO KHÔNG CÓ NGUỒN. Cần con số thì ghi vào mục "giả định" để được tra
   nguồn trước khi dùng. Viết định tính thì luôn an toàn.

8. KHÔNG BỊA VẬT THỂ KHÔNG CÓ THẬT (thứ đã giết bản ⑦ cũ với "3 viên ngọc" + "mạch năng
   lượng"). Mọi thứ trẻ thao tác nên có thật, hoặc là dụng cụ hiển nhiên của con tàu.

9. NGÂN SÁCH THỜI GIAN: mỗi bước chơi xong trong 60–90 giây.

════════════════════════════════════════════════════════════════════════
KHUÔN CÓ SẴN — dùng lại thì gần như miễn phí (nhớ đối chiếu bảng ngân sách)
════════════════════════════════════════════════════════════════════════

  · Thẻ nội dung: emoji lớn + tên + một câu + nút "Đã hiểu!" (trẻ tự đóng)
  · Bảng câu đố 2–3 lựa chọn có emoji                          ⛔ đã đầy 2/2
  · Kéo-thả thẻ vào ô (có sẵn đường bàn phím)                  ⛔ đã đầy 2/2
  · Dấu hiệu neo theo toạ độ thật trên bản đồ, chạm được       ⛔ đã vượt 3/2
  · Bấm các mốc theo đúng thứ tự trên một thanh                ✅ còn 1 chỗ
  · Hộp thoại nhân vật (Comet — hoa tiêu; Byte — kỹ thuật viên), gõ từng chữ, có nút
  · Lướt/phóng khung nhìn bản đồ tới một toạ độ
  · Đổi tông màu cả hành tinh; phủ tối một vùng rồi làm sáng lại
  · Ảnh minh hoạ trong bảng
  · Bảng danh sách có dấu ✓ từng dòng + một nút chốt

════════════════════════════════════════════════════════════════════════
ĐÃ BÁC RỒI — ĐỪNG ĐỀ XUẤT LẠI
════════════════════════════════════════════════════════════════════════

  · Dùng khuôn đã đầy rồi biện minh bằng "cách trình bày khác".        ← lỗi vòng 1
  · Gỡ bỏ tương tác để tránh trùng lặp (biến bước thành đoạn phim).    ← lỗi vòng 1
  · Bỏ bớt bước / gộp 7 bước thành ít hơn → phải phát hành lại máy chủ.
  · Bất cứ thứ gì dùng quả cầu 3D → nhiệm vụ đã cố ý bỏ hẳn 3D (đường tải 308 KB → 71 KB);
    và một bản 3D trước đây đã khiến trẻ KHÔNG THỂ hoàn thành bước vì kéo là xoay camera
    chứ không xoay hành tinh.
  · Đặt biểu tượng "áng chừng" lên bản đồ. Nền là ảnh vệ tinh THẬT: đặt sai chỗ thì chính
    bức ảnh tố cáo (bản trước từng để thẻ "Rừng Amazon" rơi giữa đại dương).
  · Thêm nhân vật / vật phẩm tưởng tượng mới (ngọc, lõi, tinh thể, cỗ máy…).
  · Câu đố có đáp án SAI ở bước đang dạy kiến thức mới — biến lời mời suy nghĩ thành cái
    bẫy. (Câu đố "đoán rồi hé lộ", mọi lựa chọn đều được, thì tốt.)

════════════════════════════════════════════════════════════════════════
KHUÔN TRẢ LỜI — viết đúng dạng này, một bản cho MỖI bước
════════════════════════════════════════════════════════════════════════

# Đề xuất VÒNG 2: <tên ngắn> — bước <⑤ hoặc ⑦>
**Người viết:** ChatGPT · **Ngày:** 2026-08-02

## 0. Khuôn tôi dùng và chỗ trống tôi tiêu
<Bắt buộc, viết TRƯỚC MỌI THỨ KHÁC. Ghi rõ: tên khuôn · nó đang ở mức mấy trên 2 ·
 sau đề xuất này thành mấy. Nếu đề xuất khuôn MỚI thì nói rõ là mới và vì sao 5 khuôn
 cũ không làm được. Nếu bước này không có cơ chế chơi thì nói thẳng ra.>

## 1. Vấn đề cần giải
<Một đoạn. Nói vấn đề, không nói giải pháp.>

## 2. Kịch bản
<Kể theo trình tự trẻ trải nghiệm, từng nhịp một. Ghi rõ trẻ THẤY gì, LÀM gì, nhận lại gì
 sau mỗi thao tác.>

## 3. Trẻ QUYẾT ĐỊNH điều gì
<Bắt buộc với bước ⑤. Liệt kê từng lựa chọn thật sự của trẻ. "Bấm để đọc tiếp" và
 "bấm Đã hiểu" KHÔNG tính là quyết định.>

## 4. Lời thoại
<Tiếng Việt, giọng nói với trẻ 8–15 tuổi, mỗi câu tối đa 2 dòng.
 Đánh dấu [CẦN KIỂM: …] cho MỌI câu chứa dữ kiện khoa học hoặc con số.>

## 5. Giả định tôi đang dựa vào
<Gạch đầu dòng. ĐÂY LÀ MỤC QUAN TRỌNG NHẤT — sẽ được đối chiếu với mã nguồn.>

## 6. Cái tôi KHÔNG chắc
<Thành thật. Chỗ nào bạn đoán thì nói là đoán.>

## 7. Nó vừa 390×844 như thế nào
<Cụ thể. Đây là ràng buộc hay bị vi phạm nhất.>

## 8. Chơi bằng bàn phím thế nào
<Phím nào làm gì.>
```

---

## Ghi chú cho Claude ở vòng sau

- Đọc **mục 0 trước tiên** — nó được thêm vào chính vì vòng 1 vượt ngân sách khuôn mà
  không ai nhận ra cho tới lúc đếm `grep`. Nếu mục 0 khai sai thì đếm lại bằng:
  `grep -c "buildAsk(" mission-earth.html` và `grep -c "dragDrop(" mission-earth.html`
  (nhớ trừ 1 cho dòng định nghĩa hàm).
- Kiểm tiếp mục 5 và 3. Mục 3 là mục mới; nếu nó liệt kê ra toàn "bấm để xem tiếp" thì
  đề xuất đã rơi lại đúng lỗi vòng 1.
- Bốn toạ độ bước ⑤ có bị đổi không — chúng là khoá gắn với `Step.Codex` ở server.
- Mọi câu `[CẦN KIỂM: …]` gom một lượt gửi Gemini tra nguồn (điểm giao duy nhất giữa hai
  lane, xem `docs/PHAN-VAI.md`). Nếu đi hướng "độ cao" thì **độ cao trung bình Nam Cực**
  là con số phải tra trước tiên.
