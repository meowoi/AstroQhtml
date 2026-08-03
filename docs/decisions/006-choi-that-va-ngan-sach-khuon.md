# 006. Mười điểm chơi thật, và ngân sách khuôn tương tác

**Ngày:** 02/08/2026 · **Trạng thái:** đã chốt · **Quyết:** chủ dự án
**Liên quan:** `002` (bộ khuôn) · `004` (một hình cho cả nhiệm vụ) · `005` (7 bước)

---

## Vấn đề

Chủ dự án chơi thật Nhiệm Vụ 01 sau khi `005` xong và báo **10 điểm**. Chúng không phải
mười lỗi rời rạc — đọc lại thì phần lớn cùng một gốc: **nhiệm vụ nói một đằng, màn hình
làm một nẻo**, và **cùng một việc bị dựng hai lần bằng hai cỗ máy khác nhau**.

Kèm một ràng buộc chi phí do chủ dự án đặt giữa lượt việc:

> *"để tránh phải đụng tới các bước trên server, cần sửa nội dung và lời dẫn của những
> bước nào?"*

⇒ **Giữ nguyên 7 id bước** (chúng là khoá DynamoDB), chỉ đổi **việc trẻ làm** bên trong.

---

## Mười điểm và quyết định cho từng điểm

| # | Điểm chủ dự án nêu | Quyết định |
|---|---|---|
| 1 | Đã bấm Trái Đất rồi mà nhãn "Bắt đầu từ đây" vẫn còn | Gỡ nhãn sau cú chạm (`_gateTouched`) |
| 2 | *"nitơ và oxy — thứ mình đang thở"* dễ hiểu là hít cả hai | Viết lại; và **thêm nhịp dẫn** vì sau đó không hiện gì |
| 3 | Nam Cực bị box thoại Comet đè, trẻ không tự tìm được | `focusMarker` + **nút OK trên thẻ** (bỏ tự đóng 3,4 s) |
| 4 | Mặt Trời bị ảnh Trái Đất đè → không tìm được | **Bỏ hẳn việc đi tìm Mặt Trời** — xem "Ba lần viết lại bước ③" |
| 5 | Không có lời dẫn nào tới `SYS.online`, trẻ không hiểu vì sao phải quét | Thêm lời dẫn |
| 6 | Sao phải zoom trước bước dòng thời gian? | Bỏ cú zoom — nó không mang gì |
| 7 | Giải thích bằng góc chiếu có đúng khoa học không? | **Đây là câu hỏi, không phải yêu cầu sửa.** Đã trả lời kèm nguồn NASA; không đổi code |
| 8 | Rải 3 ống khói lên bản đồ 2D, vùng mờ → sáng | Làm; ống khói thành **marker của cảnh** |
| 9 | Tự dưng drone quét mẫu làm gì? Đã có 7 châu lục rồi | **Bỏ drone**, rồi bỏ luôn cả cú chạm marker — xem dưới |
| 10 | Bỏ nhiệm vụ kéo viên ngọc, không logic | **Bỏ 3 viên ngọc**, thay bằng hồ sơ 3 dòng + một cú đóng dấu |

⚠️ **Điểm 7 đáng ghi riêng vì nó là một câu hỏi bị dễ đọc thành một lệnh.** Trả lời:
đúng khoa học, nguồn nguyên văn NASA — *"From the equator to the poles, the Sun's rays
meet Earth at smaller and smaller angles, and the light gets spread over larger and
larger surface areas"*. Sửa code ở đây là sửa một thứ không sai.

---

## Ba lần viết lại bước ③, và gốc chung của cả ba

Bước ③ (`sun`) bị viết lại **ba lần trong một ngày**. Ghi lại vì gốc của cả ba là một, và
nó là một lỗi dễ mắc lại:

1. **Bản 1** — trẻ đi tìm và chạm nút Mặt Trời. Nút `.e2-sun` neo `top:9%; right:8%` của
   khung, mà bản đồ đã lùi hết cỡ và phủ kín → ngôi sao **lẫn vào chính bức ảnh Trái
   Đất**. Trẻ không tìm ra. Đúng cái bẫy bước `rotation` bản 3D đã mắc.
2. **Bản 2** — bỏ việc đi tìm, Mặt Trời tự cháy. Nhưng lời thoại nói *"ngôi sao của chúng
   ta đang lên kìa"* trong khi **không có vật thể nào hiện ra** → chủ dự án: *"trẻ hiểu
   rằng mặt trời nằm trên trái đất. Vẫn vô lý"*.
3. **Bản 3 (đang chạy)** — bản đồ ĐANG SÁNG → Comet hỏi *"nếu Mặt Trời tắt thì sao?"* →
   trẻ đoán → **cú đoán đó chính là thứ làm màn hình tối đi** → kể ba vai trò → sáng lại.

⚠️ **GỐC CHUNG:** ở bản 1 và 2, cú tối/sáng **không có nguyên nhân nào trong tay trẻ**,
nên lời thoại buộc phải bịa ra một nguyên nhân nhìn thấy được. Cách chữa không phải là
viết lại lời thoại lần thứ ba — mà là **cho trẻ tự tạo ra nguyên nhân**.

⚠️ Ba lựa chọn của câu đố **đều đúng**, cố ý: Mặt Trời làm cả ba việc cùng lúc, và chính
điều đó là bài học. Không có đáp án sai ở một bước đang dạy kiến thức mới.

---

## Ngân sách khuôn tương tác — phần đáng giá nhất của quyết định này

Điểm 9 ("bỏ drone") lúc đầu được xử bằng cách **giữ cú chạm marker, chỉ bỏ hoạt cảnh
drone**. Rồi khi soạn đề bài cho ChatGPT, tôi đếm lại số lần dùng mỗi khuôn của `002` và
phát hiện bước ⑤ **vẫn vi phạm** — chỉ là vi phạm một luật khác.

`002` dòng 120: *một nhiệm vụ không dùng cùng một khuôn quá 2 lần.* Đếm bằng công cụ trên
mã nguồn, không phải cảm nhận:

| Khuôn | Trước `006` | Ở bước nào |
|---|---|---|
| `signal_scan` (chạm marker) | **3 / 2 ⛔** | ① ③ ⑤ |
| `profile_builder` (thẻ → ô) | 2 / 2 | ④ ⑥ |
| câu đố chọn đáp án | 2 / 2 | ① ③ |
| `sequence_reconstruction` | 1 / 2 | ② |
| `orientation_align` | 0 / 2 | *(bước dùng nó đã bỏ)* |

⇒ **Bước ⑤ phải đổi hẳn cơ chế, không chỉ bỏ hoạt cảnh.** Và nó không được dùng lại
`dragDrop` (đã đầy) hay `buildAsk` (đã đầy).

### Kết quả: khuôn thứ sáu — "lát cắt Trái Đất"

Camera vẫn bay tới bốn toạ độ THẬT và marker vẫn nhấp nháy — trẻ **phải nhìn thấy** nơi
đó trên ảnh vệ tinh. Nhưng cú bấm dời xuống **một cột độ cao 4 nấc**: trẻ **đoán** nơi
vừa bay tới nằm nấc nào, rồi mới hé lộ.

⚠️ **VÌ SAO NÓ KHÔNG PHẢI MỘT CÂU ĐỐ 4 LỰA CHỌN TRÁ HÌNH:** câu đố hỏi xong là vứt câu
hỏi đi. Ở đây mỗi lượt để lại một con chip trên cột, và **cái cột dựng dần lên mới là thứ
mang bài học** — xong bốn lượt thì chính nó là bằng chứng cho tiêu đề bước, *"Sự sống ở
khắp nơi"*: từ đáy đại dương tới đỉnh núi, nấc nào cũng có sinh vật. Thứ trẻ tạo ra là
một biểu đồ, không phải một điểm số.

⚠️ **Thứ tự đi thăm cố ý KHÔNG đơn điệu** (`LIFE_ORDER` cho rank **3 → 4 → 2 → 1**). Đi
theo độ cao tăng dần thì sau hai nơi đầu trẻ đoán được nốt bằng quy luật "cái sau cao hơn
cái trước", và cú bất ngờ ở Nam Cực mất sạch. Cũng cân cả quãng lướt: thứ tự đang dùng
cho 20° · 62° · 67°, một thứ tự "bất ngờ" khác từng thử cho ra cú lướt **149°** — dài gấp
đôi mọi cú lướt trong cả nhiệm vụ.

⚠️ **Nhãn 4 nấc KHÔNG gọi tên địa hình.** Bản nháp đầu dùng "đỉnh núi / đáy biển / cao
nguyên băng" và nó **tự trả lời hộ trẻ**: "Himalaya → đỉnh núi" thì không còn gì để nghĩ.
Nhãn theo **dải độ cao** ("rất cao / cao / ngay trên / dưới mực nước biển") thì trẻ buộc
phải hình dung từng nơi cao bao nhiêu — và **Nam Cực trở thành câu hỏi thật sự**, vì băng
làm ai cũng đoán nó thấp.

⚠️ **ĐOÁN SAI KHÔNG PHẠT.** Chip luôn về ĐÚNG nấc dù đoán nấc nào; hai nhánh khác nhau
đúng một câu chữ. Ở một bước đang DẠY độ cao thì bắt đoán đúng mới cho qua là dựng cái
bẫy, không phải mời suy nghĩ.

### Hai con số, và cái bẫy dẫn nguồn suýt mắc

Chỉ có **hai** con số ở bước này, cả hai viết **đúng bằng câu nguồn nói**:

- **Nam Cực "cao tới 4.000 mét"** — NASA Earth Observatory, nguyên văn *"Red shows the
  highest elevations (up to 4,000 meters above sea level)"*.
- **"Đáy đại dương sâu trung bình khoảng 3.682 mét"** — NOAA, nguyên văn *"The average
  depth of the ocean is about 3,682 meters (12,080 feet)."*

⚠️ **HAI CHỖ SUÝT BỊA, cả hai đều nghe rất hợp lý:**

1. **"Nam Cực là châu lục cao nhất"** — cỗ máy tìm kiếm tóm tắt đúng câu này *từ trang
   NASA đó*, và các trang phổ thông đều nói thế. Tôi mở trang ra đọc lại toàn bộ: **trang
   NASA KHÔNG nói câu đó.** Con số trung bình thì mỗi nguồn một khác (2.200 · 2.300 ·
   2.500 m) — chính sự vênh đó là lý do chỉ dùng con số NASA phát biểu được.
   *Đây là lần thứ hai dự án mắc đúng lỗi này: `term_planet` từng dẫn trang* About the
   Planets *cho ba tiêu chí IAU mà trang đó không liệt kê.*
2. **Gán 3.682 m cho riêng Đại Tây Dương** — NOAA nói về **đại dương nói chung**. Câu
   tiếng Việt vì thế phải viết "đáy đại dương", và có phép kiểm canh đúng chuyện này.

Hai nơi còn lại viết **định tính, không con số** — an toàn tuyệt đối và đủ dùng, vì cột
chỉ cần thứ tự tương đối.

---

## Bước ⑦ — quyết định là KHÔNG ĐỔI

ChatGPT vòng 2 tự chọn phương án *"giữ nguyên"*, và đó là quyết định đúng. Bản đang chạy
(hồ sơ 3 dòng ✓ + một nút đóng dấu) đã thay 3 viên ngọc từ điểm 10 ở trên, và:

- không tiêu thêm một chỗ nào trong ngân sách khuôn;
- không nhồi kiến thức mới ở đúng lúc trẻ tưởng đã xong (3 dòng = 3 thứ các bước trước
  ĐÃ dạy: 71% ← ① · góc chiếu ← ③ · oxy ← ② và nhịp mở đầu);
- giữ được câu chốt khoa học mạnh nhất: **phải có đủ cả ba cùng một lúc.**

⚠️ Bản 7 dòng mà ChatGPT đề xuất ở vòng 1 (mỗi dòng một bước đã qua) **đánh đổi mất câu
chốt đó** — ba điều kiện của sự sống là một ý mạnh hơn bảy việc vừa làm.

⚠️ **BƯỚC CUỐI KHÔNG ĐƯỢC LÀ CÂU ĐỐ.** Nó nằm ngay trước màn thưởng; bắt trả lời đúng
mới cho qua là dựng một cửa chặn ở đúng chỗ trẻ tưởng đã xong. Có phép kiểm đòi **0 lựa
chọn** ở bước này.

---

## Làm việc với ChatGPT — bài học về cách ra đề bài

Vòng 1 **bị bác cả hai bản**, và không phải vì kịch bản dở: cả hai vượt **cùng một ràng
buộc đếm được** mà đề bài vòng 1 đã ghi ra thành một câu luật.

⚠️ **Một câu luật thì lách được; một bảng có số chỗ trống thì không.** Vòng 2 đổi từ
*"không dùng cùng một khuôn quá 2 lần"* sang một bảng ghi `⛔ ĐÃ ĐẦY 2/2` cho từng khuôn.
Kèm hai thứ vòng 1 thiếu:

- **Đặt tên hai lối thoát sai** để không đi lại: *"dùng khuôn đã đầy rồi biện minh bằng
  cách trình bày khác"* và *"gỡ bỏ tương tác để tránh trùng lặp"*. Cái thứ hai là lỗi
  riêng của bản ⑤ vòng 1: nó khác bản đang chạy **đúng một điều — chỗ trẻ bấm** — và dời
  cú bấm **ra khỏi tấm ảnh vệ tinh**, tài sản duy nhất của cả nhiệm vụ.
- **Nói thẳng bước ⑦ đã dựng xong**, kèm nguyên ba dòng đang chạy. Vòng 1 ChatGPT đề xuất
  lại gần đúng thứ đã có vì nó không biết thứ đó tồn tại. Và cho phép **"giữ nguyên" là
  một câu trả lời hợp lệ** — nếu không thì đang bắt nó bịa ra một thay đổi.
- Thêm hai mục bắt buộc vào khuôn trả lời: **mục 0 "khuôn tôi dùng và chỗ trống tôi
  tiêu"** (viết trước mọi thứ khác) và **mục 3 "trẻ QUYẾT ĐỊNH điều gì"** kèm ghi chú
  *"bấm để đọc tiếp KHÔNG tính là quyết định"*. Hai mục này bắt nó tự khai đúng hai chỗ
  đã hỏng, thay vì để lộ ra sau khi tôi đếm.

⚠️ **Và một giới hạn của chính luật này phải nói ra:** `002` chỉ **đặt tên** 5 khuôn, không
đặc tả cái nào. Vòng 1 bác được chắc chắn vì đếm được lời gọi hàm có thật (`buildAsk(`
2 lần, `dragDrop(` 2 lần) — **không phải vì tôi biết định nghĩa khuôn**. Với khuôn thứ sáu
thì không đếm được, vì nó là mã chưa có; xếp một vật vào một nấc trên trục **gần
`profile_builder`** nếu cài bằng thẻ→ô. Nên nó được cài bằng **mã riêng**, và quyết định
ghi ở đây theo *tinh thần* của luật (rủi ro đơn điệu), không theo tên gọi.

---

## Đã bác — và vì sao

- **Bỏ bớt / gộp bước.** Id bước là khoá DynamoDB; đổi là người chơi cũ mất tiến độ và
  phải phát hành lại máy chủ. Ràng buộc do chủ dự án đặt.
- **Giữ cú chạm marker ở bước ⑤, chỉ bỏ hoạt cảnh drone.** Đây là bản sửa ĐẦU TIÊN của
  điểm 9, và nó chưa đủ: vẫn là `signal_scan` lần thứ 3.
- **"Nhật ký quan sát" (ChatGPT vòng 1, bước ⑤).** Nhịp giữa thành 8 cú bấm xác nhận liên
  tiếp, không một quyết định nào — một đoạn phim có nút. Và phần có quyết định (ghép
  biểu tượng vào câu) là `profile_builder` lần thứ 3.
- **"Báo cáo sứ mệnh" 7 dòng + 3 lựa chọn (ChatGPT vòng 1, bước ⑦).** Câu đố lần thứ 3,
  và đánh đổi mất câu chốt "đủ cả ba cùng lúc".
- **Nhãn 4 nấc gọi tên địa hình.** Tự trả lời hộ trẻ.
- **Đặt câu hé lộ độ cao vào dòng nhắc dưới bảng.** Dòng đó bị chính cái thẻ che, và tới
  lúc thẻ đóng thì câu hỏi kế tiếp đã ghi đè lên nó. Nên nó nằm **trong thẻ**
  (`#card-sub`).
- **Dùng `max-height` + `object-fit:cover` để chặn ảnh minh hoạ bước ②.** `cover` cắt đều
  trên–dưới, mà ở tranh `dino` con thú nhỏ (chi tiết đáng giá nhất: thú xuất hiện CÙNG
  THỜI khủng long) nằm sát mép dưới. Giới hạn **bề rộng** thay vì chiều cao.

---

## Số đo đáng giữ

| Đo được | Con số | Vì sao còn cần |
|---|---|---|
| Bảng bước ② khi ảnh tràn bề rộng, trên 1366×768 | chiếm **84,5% khung**, còn **30px** bản đồ | Mà bước ② đổi tông màu cả hành tinh — `004` chốt đó là **nội dung bài học** |
| Sau khi chặn `max-width:min(100%,52vh)` | còn **225px** bản đồ | Ảnh nhỏ hơn nhưng **không bị cắt** |
| Tải ảnh 4 mốc thời gian | 8,99 MB → **162 KB** thực tải | Nạp lười từng mốc |
| PNG-256 vs AVIF cho tranh `dino` @700px | **159 KB vs 49 KB** | **Ngược** kết luận của logo — tranh có 44k–223k màu, logo thì không. Phải ĐO, đừng chép tiền lệ |
| Bảng lát cắt bước ⑤ trên 390×844 | *(phép kiểm đòi chừa ≥150px bản đồ)* | Trẻ phải thấy nơi đang hỏi mới đoán được độ cao |

---

## Lỗi có sẵn tìm ra khi làm lượt này

⚠️ **Đổi VI/EN giữa bước ④ không đổi được nhãn ống khói nào.** Khối đổi ngôn ngữ còn dò
`#energy-slots .me-stack`, trong khi ba ống khói đã dời lên **bản đồ** thành marker của
cảnh (điểm 8) và `#energy-slots` nay luôn rỗng → vòng lặp chạy **0 lần**. Im lặng tuyệt
đối: không ngoại lệ, không console, chỉ là một việc lặng lẽ không xảy ra. Đã sửa sang
`.e2-mk.e2-stack` + `aria-label` (ống khói không có phần tử `.lb`; gọi
`.querySelector('.lb').textContent` ở đó là `TypeError` ngay lần đổi ngôn ngữ đầu tiên).

⚠️ **`sizes` đặt trên `<img>` không áp cho `<source>`** trong `<picture>` → trình duyệt
mặc định `100vw` và tải bản 1120 thay vì 700, **nặng gấp đôi trên đúng nhóm mạng yếu mà
việc này sinh ra để phục vụ**. Bằng chứng: `naturalWidth` báo **1440** cho một file
1120×747. Mỗi `<source>` phải có `sizes` riêng.

⚠️ **Bộ smoke đã đỏ từ TRƯỚC lượt việc này mà không ai biết.** `read_card` ngồi chờ thẻ
tự đóng, trong khi mốc tự đóng 3,4 giây đã bị bỏ (điểm 3) — nó hết hạn 12s rồi trả `None`,
và `showCard` không bao giờ resolve nên cờ `busy` kẹt mãi ở `true`. Triệu chứng đọc ra y
như *"chạm châu lục không hiện thẻ"* và *"sản phẩm treo"*.
**Bài học: đổi một component DÙNG CHUNG (`showCard` phục vụ ba bước) thì chạy lại bộ
smoke ngay, đừng để dồn sang lượt sau.**

---

## Điểm 11 — mốc cuối của bước ② tự cắt phần lý giải

Báo sau khi 10 điểm trên đã xử xong, và nó là **một lỗi mã**, không phải chuyện nội dung:

> *"nhiệm vụ lần theo dòng thời gian phát triển của trái đất vẫn cần 1 hình ảnh minh họa
> ngày nay, lý do ấn vào mốc cuối bị cắt luôn phần lý giải, nhìn như lỗi giật giật, ra
> màn hình này luôn."*

Nguyên nhân, đọc thẳng từ mã:

```js
busy = false;
if (this.seen >= ERAS.length) await finishStep('timeline');   // ← mốc cuối
```

`openEra` vừa gọi `paintEraBody()` ghi chữ ra thì `finishStep` chạy ngay → `outro()` gọi
`$('time').classList.remove('show')` → **bảng biến mất cùng lúc chữ hiện ra**. Mốc "Ngày
nay" vì thế **không bao giờ đọc được một chữ nào**.

⚠️ **Vì sao bốn mốc đầu không lộ lỗi:** ở chúng, trẻ tự bấm chấm kế tiếp theo nhịp của
mình, nên không có cú tự nhảy nào. Chỉ mốc cuối là **không còn chấm nào để bấm**, và chỗ
đó lại là chỗ duy nhất mã tự quyết thay trẻ. Một lỗi chỉ tồn tại ở phần tử cuối của một
dãy thì mọi phép kiểm chạy trên "một mốc bất kỳ" đều đi qua nó.

**Sửa:** mốc cuối chỉ HIỆN NÚT; `onDone()` mới chốt bước. Cùng nguyên tắc đã áp cho thẻ
nội dung khi bỏ mốc tự đóng 3,4 giây — *thứ MANG BÀI HỌC thì để trẻ tự quyết lúc nào đọc
xong, đừng để hệ thống quyết bằng đồng hồ hay bằng một cú nhảy.* Nút nhận tiêu điểm sẵn
để đường bàn phím không phải Tab đi tìm.

**Và thêm tranh cho mốc ⑤ "Ngày nay"** — đảo lại quyết định của chính `005` mục ⑩.
Lập luận cũ (*"ảnh vệ tinh THẬT đang nằm ngay sau lưng bảng, vẽ tranh lên đó là thay ảnh
thật bằng tranh ở đúng mốc duy nhất có ảnh thật"*) **vẫn đúng về nội dung**, nhưng nó
không thắng được thứ trẻ nhìn thấy: bốn mốc có tranh rồi mốc thứ năm trống thì đọc ra như
một chỗ bị thiếu, không như một quyết định. Prompt sinh ảnh:
`docs/proposals/2026-08-02-prompt-anh-moc-ngay-nay.md`.
⚠️ **CHƯA thêm `img:'now'` vào `ERAS`** cho tới khi có file thật — trỏ vào file chưa tồn
tại là 404 cộng một ô ảnh vỡ trước mặt trẻ, và một khung ảnh trống là một lời hứa hệ
thống chưa giữ.

⚠️ Hai ràng buộc của prompt mà đề bài dễ bỏ sót, ghi lại để vòng sau không mất công:
**cảnh trên mặt đất chứ không nhìn từ vũ trụ** (bốn bức kia đều là cảnh mặt đất; bay lên
nhìn quả cầu là phá mạch cả dãy) và **không người / không thành phố / không ống khói** —
bước NGAY SAU nói về ô nhiễm, nên bức "ngày nay" có nhà máy là kể trước phần của bước sau
và trẻ đọc ra thành "ngày nay = ô nhiễm", trong khi đoạn chữ đi kèm chỉ nói về sự sống
phong phú.

**Kèm một việc còn treo từ 31/07 nay làm luôn:** `.me-stamp` từ `min-height:44px` lên
**48px**. 44 là mốc TỐI THIỂU của WCAG 2.5.5 nên đặt đúng 44 là không còn biên an toàn —
`CLAUDE.md` đã ghi một ca chập chờn có thật vì đúng lý do đó (nút VI/EN của
`explorer.html` đo ra đúng 44×44, hai lượt chạy khác nhau mà không đụng dòng nào). Nút
này nay là đường ra **DUY NHẤT** của cả bước ② và ⑦ — bấm trượt là trẻ kẹt lại.

---

## Kết quả kiểm thử

| Bộ | Kết quả |
|---|---|
| `check_pages` | **626 / 0** (thêm mục [3f] 15 phép kiểm + 5 phép kiểm mốc cuối + asset bức thứ 5) |
| `smoke_mission_earth` | **229 / 0** (mục [4] · [5] · [7] viết lại hẳn) |
| `smoke_map_onboard` | **67 / 0** |
| `audit_viewports` | **684 / 0** |

### Ba lỗi trong BỘ ĐO, không phải trong sản phẩm

Đáng ghi vì mỗi cái đều từng đọc ra như một lỗi sản phẩm, và một cái thì **xanh trong khi
sản phẩm sai**.

1. **`read_card` chưa bao giờ bấm "Đã hiểu!"** → thẻ không đóng → `showCard` không resolve
   → cờ `busy` kẹt mãi. Triệu chứng: *"chạm châu lục không hiện thẻ"* rồi *"sản phẩm treo"*.
   Bộ smoke đã đỏ từ TRƯỚC lượt việc này mà không ai biết, vì mốc tự đóng 3,4 giây bị bỏ ở
   lượt trước và không ai chạy lại bộ đo.
   ⚠️ Tôi vá theo TỪNG NHÁNH ở bốn chỗ, và chính đó là cách dẫn trở lại đúng lỗi này lần
   thứ hai: thẻ hé lộ 71% mở SAU khi marker đã bị xoá, nên `close_card` nằm trong vòng
   chạm marker không bao giờ chạy. Cách đúng là **đóng thẻ ở đầu mỗi lượt, một chỗ duy
   nhất** — bất kỳ thẻ nào đang mở cũng chặn hết.

2. **`fast_play` không tự khai trạng thái** (trái quy tắc 6 mục 6). Nó chỉ trả `bool`, nên
   một bước không qua được thì vòng lặp quay hết 320 lượt, **mất ~20 phút**, và tất cả ta
   biết là *"không chơi hết được 7 bước"*. **Mất hai lượt chạy 20+ phút** vì đúng lý do đó.
   Nay nó thoát sau 25 lượt không tiến triển và in ra bước đang kẹt · bảng đang mở · `busy`
   · `rungWanted` · số marker — lượt sau chỉ ra ngay `scan` + *thẻ đang mở*.

3. **Một phép kiểm ĐẠT trong khi sản phẩm SAI** — nặng nhất trong ba cái:
   `[ok] EN: tiêu đề tổng kết dịch → SỨ MỆNH TRÁI ĐẤT HOÀN THÀNH!`
   Nó dò 6 ký tự có dấu **chữ thường**, mà chuỗi kia toàn **chữ HOA**. Đây là **lần thứ ba**
   dự án mắc lỗi "gõ một nhúm ký tự để hỏi đã dịch chưa"; hai lần trước là *báo hỏng oan*,
   lần này là *đạt trong khi sai*. Bản sửa lần 1 chỉ áp cho một chỗ nên lần 3 xảy ra ở chỗ
   ngay bên cạnh. Nay có `co_dau_viet()` dùng chung.
   **Bài học: sửa một lỗi loại này thì đi tìm hết các bản sao của nó.**

### Và một ca chập chờn cuối cùng, treo từ 31/07 nay đóng

`audit_viewports` báo `explorer.html: vung cham >= 44px ([{"t":"VI","w":44,"h":44}])` —
**683/1 rồi 684/0 với cùng một mã**. Nguyên nhân: 44 là mốc TỐI THIỂU của WCAG 2.5.5, đặt
đúng 44 là không còn biên an toàn nào. Đã nâng `.lang-switch button` và `.me-stamp` lên
**48px**. ⚠️ *Một phép kiểm hay báo oan thì sớm muộn người ta bỏ qua nó — đó mới là cái giá
thật, không phải một dòng đỏ trong báo cáo.*

Kèm một phát hiện về môi trường: **Chrome hãm `setInterval` ở trang không hiện, đo được
~124ms/ký tự thay vì 22ms**, và nó xảy ra **cả khi chạy một mình** (bộ đó mở nhiều context;
trong headless, trang không phải trang đang hiện đều bị coi là ẩn). Dấu vân tay để nhận ra:
**đúng những câu dài nhất hỏng, câu ngắn nhất đạt**. Một lỗi sản phẩm thì không quan tâm độ
dài câu.

---

## Còn treo

1. **Deploy + push.** Lambda còn ở bản 8 bước
   (`CodeSha256 = gnb5T7uqHVesSKfn/+lzzuiWZLL4RzBlwzzhCdlwBuA=`), client cũng chưa push.
   ⚠️ **Hai thứ phải ra CÙNG NHAU** — deploy backend một mình là để bản thật lệch pha.
2. **Mốc "ngày nay" của bước ② cố ý không có tranh minh hoạ.** Thứ trung thực nhất đang
   nằm ngay sau lưng bảng: chính bức ảnh vệ tinh THẬT. Vẽ tranh lên đó là thay ảnh thật
   bằng tranh, ở đúng mốc duy nhất có ảnh thật.
3. **Nội dung chưa qua rà soát chuyên môn** (`reviewed_by_teacher: false`). Cần giáo viên
   đọc lại, nhất là bốn câu hé lộ độ cao mới thêm.
