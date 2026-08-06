# ĐỀ BÀI CHO ChatGPT — 20 nhiệm vụ chính ở Trái Đất · 20 việc hàng ngày · 3 sự kiện

> Ngày 05/08/2026 · Vai: **ChatGPT = sáng tác** (cơ chế chơi · cấu trúc quest · lời thoại · chữ cho trẻ).
> Dán **toàn bộ** file này vào ChatGPT. Nếu chưa dán `docs/BRIEFING.md` trong cuộc trò chuyện
> này thì dán nó trước.

---

## 0. HAI CON SỐ ĐỌC TRƯỚC KHI VIẾT MỘT CHỮ NÀO

**① Chi phí thật của một bước nhiệm vụ: ~410 dòng mã.** Đếm được: Nhiệm vụ 01 "Hành
Tinh Xanh" tốn ~3.300 dòng cho 7 bước. 20 nhiệm vụ × 6 bước ≈ **120 bước ≈ 49.000
dòng**, tức **gấp khoảng 4 lần toàn bộ dự án hiện tại**.

⇒ Vì thế **KHÔNG viết kịch bản đầy đủ.** Mỗi nhiệm vụ chỉ cần **một trang giấy**: tên,
chủ đề, 5–7 chặng, mỗi chặng dùng **khuôn nào** trong bộ có sẵn, và trẻ **quyết định**
điều gì. Viết chi tiết hơn thế là viết một thứ sẽ bị cắt.

**② Ngân sách khuôn tương tác — đếm được, và nó đã bác cả hai bản của vòng 1.**
Luật (`docs/decisions/002`): **một nhiệm vụ không dùng cùng một khuôn quá 2 lần.**
Đây là luật **theo từng nhiệm vụ**, không phải toàn cục — nên 20 nhiệm vụ đều được
dùng lại cả 6 khuôn, miễn mỗi nhiệm vụ không quá 2 lần/khuôn.

---

## 1. BỘ KHUÔN CÓ SẴN

| # | Khuôn | Trẻ làm gì | Đang dùng ở | Trạng thái |
|---|---|---|---|---|
| 1 | **chạm-điểm-trên-bản-đồ** | chạm các đốm trên ảnh vệ tinh thật để mở thẻ nội dung | ① *scan* (7 châu lục) | đã dựng |
| 2 | **đi-theo-thứ-tự** | mở lần lượt các mốc trên một trục, đúng thứ tự | ② *timeline* (5 mốc, 4,54 tỷ năm) | đã dựng |
| 3 | **câu-đố-4-lựa-chọn** (`buildAsk`) | đoán, rồi chính cú đoán làm cảnh thay đổi | ① *scan* · ③ *sun* — **ĐÃ ĐẦY 2/2** | đã dựng |
| 4 | **kéo-thả-vào-ô** (`dragDrop`) | kéo thẻ vào ô/rổ đúng | ⑤ *energy* · ⑥ *eco* — **ĐÃ ĐẦY 2/2** | đã dựng, chơi được bằng bàn phím |
| 5 | **xếp-lên-thang** (`buildXsec`) | đoán vị trí một nơi trên một thang 4 nấc; cột dựng dần lên **chính là bài học** | ④ *life* | đã dựng |
| 6 | **ngắm-định-hướng** (`orientation_align`) | xoay/kéo cho hai thứ thẳng hàng, có thanh đo phản hồi **liên tục** | *(bước dùng nó đã bị bỏ)* | đã đặc tả, **đang trống** |

⚠️ **Ô số 6 đang trống và đó là chỗ đáng dùng nhất.** Nó là khuôn **duy nhất** có phản hồi
liên tục (kéo tới đâu thanh đo chạy tới đó) và **không có trạng thái thua** — trẻ tự sửa.
Sáu nhiệm vụ đầu nên có ít nhất hai cái dùng nó.

⚠️ **`docs/002` đặt tên 5 khuôn nhưng chỉ đặc tả một phần.** Nghĩa là: chỉ **đếm được**
mới bác được chắc chắn. Với một cơ chế mới, hãy xét theo *tinh thần* (rủi ro đơn điệu),
đừng cãi bằng tên gọi.

### Muốn đề xuất khuôn thứ 7?

Được, **nhưng phải chỉ ra bước cụ thể không khớp cả 6 khuôn trên, và nói rõ vì sao.**
Đó đúng là cách khuôn 5 và 6 ra đời. **Không** được mở khuôn mới chỉ vì "cho đa dạng".

### Hai lối thoát sai, đã gặp ở vòng trước — đừng đi

1. ⛔ *"Dùng khuôn đã đầy rồi biện minh bằng cách trình bày khác."* Đổi màu, đổi số ô,
   đổi tên gọi — vẫn là cùng một khuôn. Nó **đếm bằng lời gọi hàm**, không đếm bằng lời văn.
2. ⛔ *"Gỡ bỏ tương tác để tránh trùng lặp."* Biến một chặng thành "đọc rồi bấm Tiếp"
   là làm cho hết vi phạm bằng cách làm cho hết trò chơi.

---

## 2. BẢY CHẶNG NHIỆM VỤ 01 ĐÃ DẠY GÌ — ĐỪNG TRÙNG

20 nhiệm vụ mới **không được dạy lại** những thứ này:

| # | Chặng | Đã dạy |
|---|---|---|
| ① | Bề mặt hành tinh xanh | 7 châu lục · **71% nước / 29% đất** |
| ② | Lần theo dòng thời gian | 5 mốc trong **4,54 tỷ năm** (dung nham → đại dương → sự sống → khủng long → nay) |
| ③ | Mặt Trời và ba vùng khí hậu | Mặt Trời nuôi sự sống · 3 vùng khí hậu · **nóng lạnh do GÓC CHIẾU, không phải khoảng cách** |
| ④ | Sự sống ở khắp nơi | sự sống ở mọi độ cao (Amazon · Himalaya · Nam Cực · đáy Đại Tây Dương) |
| ⑤ | Kích hoạt năng lượng sạch | 3 nguồn năng lượng sạch thay ống khói |
| ⑥ | Eco-Hero | 7 việc hằng ngày: nên / không nên |
| ⑦ | Đóng dấu Hồ Sơ Trái Đất | chốt: **phải có đủ cả ba cùng lúc** (nước lỏng · nhiệt độ · khí quyển có oxy) |

Gợi ý vùng chủ đề **chưa ai đụng** (không bắt buộc theo): đại dương & dòng hải lưu ·
núi lửa và mảng kiến tạo · vòng tuần hoàn nước · bão và thời tiết · từ trường và cực
quang · ngày–đêm và mùa · thuỷ triều & Mặt Trăng · rừng và oxy · băng hai cực · sa mạc ·
động đất · hoá thạch · đất và cây trồng · rác thải nhựa · sông ngòi · sấm sét · mây ·
âm thanh dưới nước · ánh sáng và cầu vồng · con người nhìn Trái Đất từ vũ trụ.

---

## 3. VIỆC 1 — 20 NHIỆM VỤ CHÍNH Ở TRÁI ĐẤT

Mỗi nhiệm vụ, **đúng một bảng như sau**, không dài hơn:

```
### M-02 · <Tên nhiệm vụ>
Chủ đề:        <một câu>
Câu hỏi lớn:   <câu trẻ sẽ trả lời được sau khi chơi xong>
Số chặng:      6
| # | Tên chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|-----------|-------|------------------------|------------------------|
| 1 | ...       | 5     | ...                    | ...                    |
Khuôn đã tiêu: 5 ×2 · 1 ×2 · 6 ×2      ← phải tự cộng, và không cái nào quá 2
Cần asset mới: <ảnh/âm thanh gì, hay không cần>
```

Ràng buộc:
- **5–7 chặng** mỗi nhiệm vụ. Ít hơn thì không thành một hành trình; nhiều hơn thì cây chặng dài quá.
- Cột *"Trẻ QUYẾT ĐỊNH điều gì"* **không được để trống**. Nếu một chặng chỉ có "đọc rồi
  bấm Tiếp" thì nó không phải một chặng — gộp nó vào chặng khác.
- ⛔ **Không viết một con số thưởng nào.** Thiên thạch tím và XP do **server** quyết
  (`Services/Missions.cs`); trong mã client không có một con số thưởng nào, cố ý.
  Muốn nói độ nặng thì viết `nhẹ` / `vừa` / `nặng`.
- ⛔ **Không hứa một nơi hoặc một nhiệm vụ chưa tồn tại.** Không viết "mở khoá ở Sao Hoả",
  "tiếp tục ở Mission 25". Dự án đã có luật vì việc này từng khoá vĩnh viễn 7 mẫu vật.
- Đặt số hiệu **M-02 … M-21** (M-01 là Hành Tinh Xanh, đã có).

---

## 4. VIỆC 2 — 20 VIỆC HÀNG NGÀY LUÂN PHIÊN

⚠️ **Chỉ được dùng những việc app THẬT SỰ ĐO ĐƯỢC.** Đây là danh sách đầy đủ, lấy từ
`js/progress.js` và bộ đếm trên server — **không có gì ngoài danh sách này**:

| Việc đo được | Ghi chú |
|---|---|
| làm một lượt Quiz **đạt** | đạt = đúng ≥ 60% (3/5 câu) |
| số câu Quiz trả lời đúng | cộng dồn |
| đọc một bài | mỗi bài chỉ tính một lần |
| chơi một lượt **Né Thiên Thạch** | có điểm, có thời gian trụ |
| chơi một lượt **Space Defender** | " |
| ghép xong một **chòm sao** | 4 chòm: Đại Hùng · Thiên Hậu · Lạp Hộ · Bọ Cạp |
| **ghé một hành tinh** ở Bản Đồ Thiên Hà | 8 hành tinh |
| chơi xong **một chặng** của một nhiệm vụ | |
| **giải mã một thuật ngữ** ở Sổ Tay | giải mã bằng cách trả lời đúng câu hỏi tương ứng |

⛔ **"Thu thập một mẫu vật" KHÔNG dùng được.** Mẫu vật **suy ra** từ bộ đếm, không có
đường ghi trực tiếp nào — không đặt được thành một việc trẻ "làm".

Ràng buộc thiết kế:
- ⚠️ **Không việc nào được đòi một tiến độ tối thiểu.** Việc hàng ngày mà khoá theo cấp
  độ hay theo cổng lộ trình thì với trẻ mới nó **khoá vĩnh viễn ở đúng ngày đầu tiên**.
- Mỗi ngày hiện **3 việc**. Hãy đề xuất **luật luân phiên** trả lời được: không lặp lại
  trong bao nhiêu ngày · có được 2 việc cùng loại trong một ngày không · có bắt buộc
  luôn có một việc **làm dưới 3 phút** không (trẻ có ngày bận).
- Mỗi việc ghi: tên (chữ cho trẻ, ≤ 40 ký tự) · dòng phụ nói rõ điều kiện · loại việc ·
  độ nặng `nhẹ`/`vừa`/`nặng`. **Không ghi số thưởng.**

---

## 5. VIỆC 3 — 3 SỰ KIỆN

Sự kiện = có **cửa sổ thời gian**, hết hạn thì biến mất khỏi màn hình.

- Cả 3 phải dựng được **chỉ bằng danh sách việc đo được ở mục 4** — không có cơ chế mới.
- Mỗi sự kiện: tên · câu dẫn (1–2 câu, giọng Comet hoặc Byte) · điều kiện hoàn thành ·
  độ dài cửa sổ (ngày) · vì sao nó đáng làm.
- ⚠️ **Đừng gắn sự kiện vào một hành tinh chưa có nhiệm vụ.** Hiện chỉ Trái Đất có.
- ⚠️ Một sự kiện nên làm được **trong một buổi**; hai cái kia dài hơn thì phải chia mốc,
  không thì trẻ vào muộn hai ngày là mất luôn cơ hội.

---

## 6. KHUÔN TRẢ LỜI BẮT BUỘC

Trả lời phải có **đủ năm mục này**, đúng thứ tự:

**Mục 0 — Khuôn tôi dùng và chỗ trống tôi tiêu.** Một bảng tổng: mỗi nhiệm vụ dùng
khuôn nào, mấy lần. Nếu có đề xuất khuôn thứ 7 thì nói ở đây, kèm bước cụ thể không
khớp cả 6 khuôn cũ.

**Mục 1 — 20 nhiệm vụ chính** (bảng như mục 3).

**Mục 2 — 20 việc hàng ngày + luật luân phiên.**

**Mục 3 — 3 sự kiện.**

**Mục 4 — Giả định & cái tôi KHÔNG chắc.** Bắt buộc, đây là phần Claude sẽ đối chiếu với
mã nguồn. Ghi thẳng: chỗ nào bạn đoán về app mà không được cho biết · chỗ nào bạn không
chắc dựng được · số liệu khoa học nào cần người khác kiểm.

---

## 7. BA ĐIỀU TUYỆT ĐỐI

1. ⛔ **Không con số thưởng nào.** Server quyết, client không có bản sao.
2. ⛔ **Không hứa nơi/nhiệm vụ chưa tồn tại.**
3. ⛔ **Không số liệu khoa học không nguồn.** Nếu một chặng cần một con số, hãy đánh dấu
   `[CẦN KIỂM: …]` — chỗ đó sẽ được gom gửi Gemini xác minh. Dự án đã **hai lần** dẫn một
   trang NASA cho một câu mà trang đó không hề nói.
