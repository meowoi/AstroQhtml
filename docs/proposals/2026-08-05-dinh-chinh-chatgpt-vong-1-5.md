# ĐÍNH CHÍNH ĐỀ BÀI — gửi ChatGPT TRƯỚC KHI viết Phần 2

> Ngày 05/08/2026 · Dán nguyên file này vào cùng cuộc trò chuyện, ngay sau Phần 1.

Phần 1 làm đúng khuôn, tự cộng ngân sách và không nhiệm vụ nào vượt 2 lần/khuôn — đã
đối chiếu lại từng bảng, chính xác. Nhưng khi đếm chi phí trên mã nguồn thì có **ba
việc phải sửa trước khi viết tiếp**, và việc thứ nhất là **lỗi của đề bài, không phải
của bạn**.

---

## ① SỬA ĐỀ BÀI: khuôn 6 KHÔNG PHẢI "đang trống" — nó là **0 DÒNG MÃ**

Đề bài viết *"khuôn 6 · ngắm-định-hướng · đã đặc tả, đang trống"* và *"ô số 6 đáng dùng
nhất"*. Câu đó dẫn bạn đi sai đường, và đây là số đo:

```
dragDrop(        7 lần gọi      ← khuôn 4, đã chạy thật
buildAsk(        5 lần gọi      ← khuôn 3, đã chạy thật
buildXsec(       2 lần gọi      ← khuôn 5, đã chạy thật
setEarthDrag(    0              ← nguyên liệu của khuôn 6
stationAngleTo(  0              ← nguyên liệu của khuôn 6
```

Hai hàm cuối **đã bị xoá khỏi `js/earth2d.js`** cùng với bước `rotation` (`docs/005`).
Nghĩa là khuôn 6 hiện **không có hàm dùng lại được, và cũng không còn nguyên liệu**.
"Đang trống" trong đề bài nên đọc là *"ô đã đặt tên nhưng chưa ai viết"*, chứ không phải
*"đã dựng sẵn, chờ dùng"*.

**Hệ quả trên Phần 1:** khuôn 6 được dùng **9 lần / 5 nhiệm vụ** (M-03, M-04, M-05, M-06
mỗi cái ×2). Suy ra cho 20 nhiệm vụ là **~36 lần**. Và chúng **không phải một khuôn**:
xoay hướng gió · canh mũi tên hải lưu · đưa Mặt Trăng vào vị trí · chỉnh độ nghiêng trục
· lái đường bão — mỗi cái là **một cảnh riêng, một định nghĩa góc riêng, một thanh đo
riêng**. Đó là ~36 cơ chế mới, không phải một khuôn dùng 36 lần.

### Luật mới cho khuôn 6

- **Tối đa 2 nhiệm vụ trong cả 20** được dùng khuôn 6.
- Và hai nhiệm vụ đó phải **dùng chung MỘT định nghĩa góc** — tức viết được **một** hàm
  phục vụ cả hai. Nếu không chỉ ra được điều đó thì đừng dùng.
- Phần 1 vì thế phải sửa lại: **giữ khuôn 6 ở đúng một chỗ** (đề nghị: M-04 "canh mũi
  tên dòng biển" — đó là ca thuần tuý nhất), các chỗ còn lại đổi sang khuôn 1–5.

⚠️ Đừng hiểu thành "khuôn 6 bị cấm". Nó vẫn là khuôn duy nhất có phản hồi liên tục và
không có trạng thái thua — chỉ là nó phải được **trả tiền một lần rồi dùng lại**, chứ
không phải trả 36 lần.

---

## ② NGÂN SÁCH THỨ HAI CHƯA AI ĐẾM: **ASSET ẢNH**

Phần 1 khai `Cần asset mới` cho 5 nhiệm vụ: giọt nước · hiệu ứng bốc hơi · mây động ·
mưa · sông · ánh sáng quét · thành phố ngày/đêm · cây thay lá · đồng hồ · hải lưu động ·
thuyền · cá · biển lên xuống · Mặt Trăng lớn · bãi triều · cua · sao biển · các loại mây
· gió · bão xoáy · radar ≈ **22 asset / 5 nhiệm vụ** ⇒ **~88 cho 20 nhiệm vụ**.

Số đo để so: dự án hiện có **đúng 5 ảnh minh hoạ** (`img/era/*` cho bước ② của M-01), và
chúng tốn **một file đề xuất riêng** cộng thời gian chờ chủ dự án đặt ảnh gốc vào `img/`.
Tức mỗi asset minh hoạ ≈ một vòng việc, không phải một dòng mã.

### Ngôn ngữ hình ảnh của dự án — quan trọng hơn con số

M-01 **không vẽ hoạt cảnh**. Nó dùng **ảnh vệ tinh NASA thật** (`img/earth/flat-2048`) +
marker + **lớp phủ CSS** (khói `--smog`, đêm `.e2-night`, đổi tông `.era-*`). Cá bơi,
cua bò, thuyền chạy, mây động là **một hướng nghệ thuật khác hẳn** mà dự án chưa có.

### Luật mới cho asset

- **Tối đa 1 asset ảnh mới cho mỗi nhiệm vụ.** Nhiều hơn thì cắt.
- Ưu tiên tuyệt đối: **ảnh vệ tinh thật đã có + marker + lớp phủ CSS**. Gió, dòng biển,
  mây, thuỷ triều, ngày/đêm — tất cả đều vẽ được bằng lớp phủ trên chính tấm bản đồ đó.
- Mỗi bảng nhiệm vụ thêm **một dòng**: `Cảnh dùng lại: <bản đồ phẳng Trái Đất | ảnh vệ
  tinh vùng X | chỉ lớp phủ CSS>`. Cảnh là phần đắt nhất, nên nó phải nằm trong bảng.

---

## ③ HAI CHỖ TRÙNG NỘI DUNG — một là do đề bài thiếu, một là lỗi tầng

### M-03 · Ngày đêm & mùa → **cắt phần ngày/đêm**

Đề bài liệt kê 7 chặng của M-01 nhưng **quên một bài học nằm ngoài nhiệm vụ**: ở
`explorer.html`, **nhịp 0** của màn Comet dẫn đường đã mời trẻ **xoay quả cầu 3D để tự
thấy nửa ngày / nửa đêm**, và ở đó ranh giới sáng–tối là **thật** (đèn gắn vào Mặt Trời
trong cảnh). Đây là lỗi của đề bài, không phải của bạn.

⇒ M-03 chặng 1–2 ("xoay Trái Đất đến khi thành phố đón nắng", "chạm nơi vừa sang ban
ngày") **dạy lại đúng thứ trẻ đã làm trước khi vào nhiệm vụ đầu tiên**. Hãy thu M-03 về
**chỉ còn MÙA** — trục nghiêng, tại sao nửa cầu bắc hè thì nửa cầu nam đông. Phần mùa
thì M-01 chưa dạy.

⚠️ Kèm một bẫy nội dung: bước ③ của M-01 đã dạy **nóng lạnh do GÓC CHIẾU, không phải
khoảng cách**. Mùa cũng vậy — **mùa không do Trái Đất gần hay xa Mặt Trời**. Nếu M-03
chạm tới đó thì phải bác quan niệm sai ra mặt, đúng như bước ③ đang làm.

### M-05 · Mặt Trăng & thuỷ triều → **sai tầng, phải sửa**

Mặt Trăng **là một NƠI khác**, không phải một chủ đề của Trái Đất: server đã khai
`Route = ["earth", "moon"]` và **MISSION-02 Mặt Trăng** đã có chỗ (đang "sắp ra mắt").
Đặt một nhiệm vụ về Mặt Trăng vào Trái Đất là **đúng cái lỗi chủ dự án đã bắt** khi thấy
một nút Mặt Trăng nằm trong cây chặng của Trái Đất: *"nhiệm vụ mặt trăng phải ở bên mặt
trăng chứ?"*.

⇒ Hai đường, chọn một và nói rõ:
- **(a)** Giữ thuỷ triều nhưng kể **hoàn toàn từ phía Trái Đất**: trẻ nhìn nước lên
  xuống ở bờ biển, sinh vật bãi triều, đi biển theo con nước — Mặt Trăng chỉ là **lời
  giải thích**, không phải thứ trẻ điều khiển. Bỏ hết chặng "đưa Mặt Trăng vào vị trí".
- **(b)** Chuyển hẳn M-05 sang danh sách nhiệm vụ **của Mặt Trăng**, và thay chỗ nó ở
  Trái Đất bằng một chủ đề khác.

---

## ④ MỘT LỖI CỘNG NHỎ

Bảng Mục 0, dòng **M-02** ghi `K1=2, K5=1`. Bảng chi tiết và dòng "Khuôn đã tiêu" của
chính M-02 lại là `K5=2, K1=1` (chặng 1 và chặng 6 đều là khuôn 5). Bốn dòng còn lại
khớp. Bảng Mục 0 là thứ dùng để soát, nên nó phải đúng.

---

## ⑤ VIỆC TIẾP THEO — theo thứ tự này

1. **Viết lại Phần 1** (M-02 → M-06) theo bốn luật mới: khuôn 6 chỉ còn một chỗ · mỗi
   nhiệm vụ ≤ 1 asset mới · thêm dòng `Cảnh dùng lại` · M-03 thu về mùa · M-05 chọn (a)
   hoặc (b). Kèm bảng Mục 0 đã sửa.
2. **Dừng lại chờ phản hồi.** Đúng rồi mới nhân lên — 20 nhiệm vụ viết sai khuôn là 20
   lần phải làm lại.
3. Sau đó mới tới Phần 2 → 5 như bạn đã chia (cách chia đó hợp lý, giữ nguyên).

Và giữ nguyên cách bạn đang dùng `[CẦN KIỂM: …]` — hai chỗ ở Phần 1 đánh dấu đúng, chúng
sẽ được gom gửi Gemini xác minh.

---

# PHỤ LỤC — trả lời bản tóm tắt của bạn (cùng ngày)

Bốn quyết định của bạn đều nhận. **Chọn (a) cho M-05 là đúng** — thuỷ triều là hiện
tượng *của Trái Đất*, và giữ Mặt Trăng ở vai "lời giải thích" thay vì "thứ trẻ điều
khiển" là cách duy nhất không đụng Mission Moon. **Cứ viết lại Phần 1.** Bốn chỗ hiệu
chỉnh dưới đây để khỏi tốn thêm một vòng.

## ⑥ "Lớp phủ CSS" KHÔNG phải asset — đây là tin tốt cho bạn

Bảng asset của bạn ghi *overlay dòng hải lưu · overlay mực nước · overlay mây/bão* là
"asset mới". Chúng **không phải asset**: lớp phủ vẽ bằng CSS/SVG là **mã**, viết xong là
xong. Asset ảnh thì **chờ chủ dự án đặt ảnh gốc vào `img/`** — đó mới là thứ chặn tiến độ
(5 ảnh `img/era/*` đã phải chờ đúng như vậy).

⇒ Đếm lại theo cách đó, Phần 1 của bạn chỉ còn **1 asset thật** (icon giọt nước). Và
ngay cả cái đó cũng thử **emoji trước** đã — M-01 dùng emoji cho toàn bộ marker và thẻ
nội dung (🛰️ ⏳ ☀️ 🌳 ⚡ ♻️ 🗂️), nên 💧 gần như chắc chắn là đủ. Nếu đủ thì **cả 5 nhiệm vụ
cần 0 asset mới**.

⇒ Bảng nhiệm vụ nên tách thành **hai dòng** thay vì một: `Asset ảnh mới:` (chờ người) và
`Lớp phủ cần vẽ:` (mã). Trộn hai thứ vào một dòng là làm chi phí đọc ra sai.

## ⑦ M-03 "Bốn Mùa" — hai trong ba trọng tâm bạn nêu, M-01 ĐÃ DẠY

Bạn ghi trọng tâm M-03 là *trục nghiêng · góc chiếu · bác hiểu lầm "gần Mặt Trời hơn nên
nóng"*. Nhưng bước ③ của M-01 **đã dạy góc chiếu** và **đã bác hiểu lầm khoảng cách** —
lặp lại nguyên hai thứ đó là M-03 thành bản sao có tên khác.

Ranh giới đúng, xin bám sát:

| | Câu hỏi | Trục |
|---|---|---|
| **M-01 ③** *(đã dạy)* | Vì sao **nơi này** nóng hơn **nơi kia** *cùng một lúc*? | góc chiếu theo **VĨ ĐỘ** |
| **M-03** *(mới)* | Vì sao **cùng một nơi** lúc nóng lúc lạnh *theo thời gian*? | trục nghiêng theo **MÙA** |

Cùng một nguyên lý, hai câu hỏi khác nhau — đó là chỗ M-03 đứng được.

**Và hãy bác hiểu lầm bằng một bằng chứng MỚI, đừng lặp lại lập luận của ③.** Bằng chứng
mạnh nhất và ③ chưa dùng: **cùng một lúc, nửa cầu bắc là hè thì nửa cầu nam là đông**.
Nếu mùa do khoảng cách tới Mặt Trời thì cả hai nửa phải cùng mùa. Một câu, không cãi lại
được — và trẻ tự kiểm được trên chính tấm bản đồ.

⚠️ Kèm một chỗ dễ nói quá tay: **đừng viết "vùng cực lúc nào cũng nhận ít năng lượng
hơn"**. Chính trang NASA dự án đang dẫn ghi rằng năng lượng nhận **trong một ngày** cao
nhất lại ở vĩ độ cao vào mùa hè.

## ⑧ M-05 — hiểu lầm về thuỷ triều còn sắc hơn cả hiểu lầm về mùa

Nếu chặng tổng kết chỉ nói *"Mặt Trăng kéo nước lên"* thì đó là **bán phần**, và nó để
lại đúng một hiểu lầm phổ biến: rằng nước chỉ dâng ở phía **gần** Mặt Trăng. Thực tế có
**hai chỗ nước dâng cùng lúc**, kể cả phía **đối diện**. Đó là lý do một ngày có **hai**
lần triều lên — một sự thật trẻ kiểm được bằng chính lịch con nước.

Hãy đánh dấu `[CẦN KIỂM: hai lần triều mỗi ngày · vai trò của Mặt Trời trong triều cường
/ triều kém]` để Gemini tra NOAA. **Đừng tự viết con số nào.**

## ⑨ Khuôn 6 dùng ĐÚNG MỘT lần thì nó không phải khuôn

Bạn giữ khuôn 6 ở riêng M-04 và nêu lý do đúng (một bài toán góc duy nhất, viết được một
hàm chung). Nhưng nếu cả 20 nhiệm vụ chỉ dùng nó **một** lần thì ta trả tiền dựng một
khuôn để dùng đúng một chỗ — lúc đó nó là **cơ chế riêng của M-04**, không phải khuôn.

⇒ Hãy **để ngỏ một chỗ thứ hai** ở M-07 → M-21, và chỉ lấp khi tìm được ca dùng **cùng
một định nghĩa góc** với M-04 (gợi ý đáng thử: hướng gió mậu dịch · hướng vòi rồng ·
hướng nhìn của một vệ tinh). Trả tiền một lần rồi dùng hai lần thì mới đáng. Nếu tới cuối
vẫn không tìm được ca thứ hai, cứ để một — nhưng khi đó **nói rõ trong Mục 0** rằng đây
là cơ chế riêng, để chi phí được nhìn đúng tên.

---

# ⑩ MỘT CÂU CUỐI — RỒI VIẾT LUÔN, ĐỪNG TÓM TẮT NỮA

Năm nguyên tắc bạn vừa nêu đều nhận, không sửa gì thêm. Và câu bạn tự rút ra —
*"một nhiệm vụ mới không phải một màn chơi mới, mà là một cách đặt câu hỏi mới trên cùng
tấm bản đồ Trái Đất"* — chính là kết luận đáng giá nhất của cả vòng này. Giữ nó.

Chỉ thêm **một** ràng buộc, và nó là **chính nguyên tắc bạn vừa nhận ở mục ⑨, áp cho lớp
phủ**: lớp phủ cũng là mã, nên nó cũng phải *trả tiền một lần rồi dùng nhiều lần*.
M-01 có đúng bốn lớp phủ cho bảy bước (khói `--smog` · đổi tông `.era-*` · trời `.me-era`
· đêm `.e2-night`) — đó là mật độ đáng noi theo, không phải 3 lớp phủ mới cho mỗi nhiệm vụ.

⇒ Ở dòng `Lớp phủ cần vẽ:`, đánh dấu **⟳** cho lớp phủ **dùng lại được ở ≥2 nhiệm vụ**, và
đặt tên chung cho nó. Ví dụ: `⟳ mũi tên hướng (gió · hải lưu · bão)` thay vì ba lớp phủ
mang ba tên khác nhau. Cái nào chỉ dùng một chỗ thì để trần, không đánh dấu.

**Giờ viết Phần 1 đã sửa** (Mục 0 + M-02 → M-06), rồi **dừng chờ phản hồi**. Không cần
tóm tắt nguyên tắc thêm lần nào nữa — ba vòng vừa rồi đã thống nhất đủ; thứ còn thiếu là
nội dung.
