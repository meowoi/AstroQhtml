# 004. Một hình cho cả nhiệm vụ — bản đồ phẳng suốt 8 bước

**Trạng thái:** đã chốt (thiết kế) · **chưa triển khai**
**Ngày mở:** 2026-08-01 · **Ngày chốt:** 2026-08-01
**Người quyết:** chủ dự án

## Bối cảnh

Chủ dự án chơi thật Nhiệm Vụ 01 và báo hai điều: **luồng dễ lỗi**, và **hình Trái Đất lúc tròn
lúc méo**. Đo lại mã nguồn thì đúng, và đo được con số: `mission-earth.html` gọi `setMap` **7
lần**, trẻ thấy hình đổi **3 lần** — cú tệ nhất nằm **ngay giữa bước ①**
([mission-earth.html:804](../../mission-earth.html) quả cầu → :821 bản đồ phẳng), tức trước khi
trẻ kịp làm gì.

Vòng khép kín gây ra nó: bước ① dạy KÉO → trên ảnh quả cầu `translate` = 0
([earth2d.js:201](../../js/earth2d.js)) nên kéo không dịch được ảnh → buộc sang bản đồ phẳng →
nhưng phẳng tối hơn quả cầu **4,7 lần** nên không dám mở màn bằng nó → buộc đổi hình giữa bước.

Đề xuất "bỏ điều khiển bản đồ, dùng hoạt hình" của ChatGPT và phần đối chiếu mã nguồn nằm ở
`docs/proposals/2026-08-01-review-vong-3-hoat-hinh.md`.

## Đã chọn — ba quyết định

### 1. Bản đồ phẳng cho **cả 8 bước**. Không còn ảnh quả cầu.

**0 lần đổi hình.** Chấp nhận mất ảnh quả cầu ở cảnh mở màn.

### 2. Bước ① bỏ hẳn kéo/zoom. Ba đốm mang **nội dung thật**: khí quyển · đại dương · lục địa.

Thao tác duy nhất là **chạm** — không thể làm sai, không có trạng thái thua, không cần bàn tay
hướng dẫn. Việc dạy KÉO chuyển sang bước ⑤ `rotation`, nơi thanh tín hiệu tự dạy luật.

### 3. Ba hiệu ứng bám vào hình cầu chuyển sang **kể chuyện**, không tương tác.

Thời đại (②) · ranh giới ngày/đêm (③) · màng khí quyển (⑧).

### 4. Bước ③ `sun`: **GIỮ id, đổi nội dung.** Không bỏ bước.

Chủ dự án cho phép bỏ nếu cần. **Không nên bỏ** — giá đo được ở mục "Đã bác" dưới.

### 5. **KHÔNG CÓ CÚ KÉO NÀO trong cả nhiệm vụ.** Bước ⑤ `rotation` cũng bỏ kéo.

Chủ dự án chốt: *"tóm lại ko có hành động hay hướng dẫn co kéo gì hết"*, rồi hỏi đúng câu chặn
được cả thiết kế: **"bản đồ 2D flat làm sao xoay được?"**

⚠️ **Câu đó bắt ra một lỗi ĐANG CHẠY TRÊN BẢN THẬT, không phải lỗi của bản đề xuất.**
[earth2d.js:213](../../js/earth2d.js) trên bản đồ phẳng:
`var px = m.flat ? -wrapLon(facing.lon) / 360 * 100 : 0;` — tức `facing.lon` **dịch ảnh**. Còn
[earth2d.js:281](../../js/earth2d.js) cho cú kéo ghi thẳng vào `facing.lon`. Hệ quả:

> Trên bản đồ phẳng, **"xoay Trái Đất" và "đi khắp bề mặt" là CÙNG MỘT phép biến hình** — cùng một
> biến, cùng một dòng `transform`, cùng một hình trên màn hình. Chỉ khác cái cờ đang bật
> (`dragRotate` vs `earthDrag`).

Và `stationAngleTo(lat, lon)` là góc giữa trạm và **điểm đang ở giữa khung**
([earth2d.js:463](../../js/earth2d.js) → `angleBetween(facing.lat, facing.lon, …)`), còn vòng ngắm
`.e2-aim` được chiếu bằng `project(facing.lat, facing.lon)` — chính điểm đó.

[Suy luận từ code, chưa đo trên màn hình] Nên việc bước ⑤ **thật sự** yêu cầu, kể từ khi nó chuyển
sang `setMap('flat')` ngày 01/08 ([mission-earth.html:1043](../../mission-earth.html)), là: *kéo
bản đồ cho tới khi trạm phát sóng trùng vòng ngắm ở giữa khung*. Biểu tượng vệ tinh nằm ở
`top:16%; left:12%` **cố định trên màn hình** ([mission-earth.css:645](../../css/mission-earth.css))
và **không tham gia phép tính nào**. Thanh "Cường độ tín hiệu" đang đo **khoảng cách tới giữa màn
hình**, không đo sự thẳng hàng vật lý nào.

**Đã bác hai đường chữa dễ:** đổi cú kéo thành nút `◀ XOAY ▶` chỉ là **dán chữ "xoay" lên một cú
dịch ảnh** — dạy sai mô hình tư duy, tệ hơn giữ nguyên. Giữ cú kéo là giữ nguyên lỗi.

**Đã chọn: vùng tối trượt, bản đồ đứng yên.** Xoay hành tinh **không làm bề mặt đổi** — bản đồ
*chính là* bề mặt nên nó phải đứng yên; thứ di chuyển là **ranh giới ngày/đêm**. Đó đúng là cách
mọi widget "day/night map" ngoài đời hoạt động, và dự án đã có sẵn nửa phần: `.e2-view::after` là
gradient vùng tối, **cố ý đặt trên `.e2-view` chứ không trên `.e2-layer`** với chú thích
*"ranh giới này thuộc về MẶT TRỜI nên không được pan/zoom theo bề mặt hành tinh"*
([mission-earth.css:552](../../css/mission-earth.css)) — tức đã nằm đúng lớp để trượt ngang được.

```
[cảnh] Bản đồ ĐỨNG YÊN. 📡 trạm phát sóng ở toạ độ thật (STATION lat 16, lon 108).
       🛰️ vệ tinh treo trên một đường kinh tuyến, cũng đứng yên.
       Vùng tối trượt ngang qua bản đồ.

Comet: "Trái Đất tự quay một vòng mỗi ngày. Nên trạm này chỉ liên lạc được với
        vệ tinh vào một số giờ thôi — mình chờ tới đúng lúc nhé."

              [ ⏩ GIỮ ĐỂ CHỜ ]        06:40 → 11:20 → 14:05

   Cường độ tín hiệu  ███████████████░░░░░  74%
   Byte: "Gần rồi! Giữ tiếp đi."

→ giữ nút: vùng tối trượt, giờ chạy, thanh lên; quá đà thì thanh tụt
→ KHÔNG có trạng thái thua. Quá lố thì chờ thêm một vòng.
```

Giữ được đúng ba thứ `002` đã lấy làm lý lẽ để tạo khuôn `orientation_align`: **thanh đo liên tục
duy nhất của cả nhiệm vụ** · **không có trạng thái thua** · và vẫn là *trải nghiệm* chuyển động
quay chứ không phải *bài kiểm tra về* nó. Thêm: thứ trẻ điều khiển (thời gian) đúng bằng thứ được
chấm điểm, và nó nối thẳng vào bài học ngày/đêm ở bước ③.

Phải trả: `stationAngleTo` đổi nghĩa từ *"góc giữa trạm và tâm khung"* sang *"chênh kinh độ giữa
trạm và vệ tinh"*, cộng một biến `time` lái vùng tối. Ước lượng **~40–60 dòng** trong
`js/earth2d.js`, **0 đồng backend**, id `rotation` giữ nguyên.

---

## Nội dung bước ① — 3 đốm, đã tra nguồn

Cả ba con số đến từ **một trang NASA duy nhất**, đã kiểm trả **200** ngày 01/08/2026:
`https://science.nasa.gov/earth/facts/`

| Đốm | Trích nguyên văn NASA | Dùng trong bài |
|---|---|---|
| 🌫️ Khí quyển | *"Earth has an atmosphere that consists of 78% nitrogen, 21% oxygen, and 1% other gases"* | 78% nitơ · 21% oxy |
| 🌊 Đại dương | *"Earth's global ocean, which covers about 71% of the planet's surface … contains 97% of Earth's water"* | 71% bề mặt · 97% lượng nước |
| 🏔️ Lục địa | *"the North American plate moves west over the Pacific Ocean basin, roughly at a rate equal to the growth of our fingernails"* | mảng Bắc Mỹ trôi nhanh cỡ móng tay dài ra |

Nguồn thứ hai, chỉ cho phần *"khí quyển làm gì cho ta"* (trang NASA viết **cho trẻ em**, đúng độ
tuổi 8–15), đã kiểm **200**: `https://spaceplace.nasa.gov/atmosphere/en/` —
*"It keeps us warm, it gives us oxygen to breathe, and it's where our weather happens."*

### Chữ dùng thật

```
p1  🌫️  KHÍ QUYỂN
vi: Lớp không khí bọc quanh hành tinh: 78% nitơ, 21% oxy. Nó giữ ấm Trái Đất,
    cho ta oxy để thở, và là nơi thời tiết xảy ra.
en: The blanket of air around the planet: 78% nitrogen, 21% oxygen. It keeps Earth
    warm, gives us oxygen to breathe, and is where our weather happens.
src: science.nasa.gov/earth/facts/ · spaceplace.nasa.gov/atmosphere/en/

p2  🌊  ĐẠI DƯƠNG
vi: Đại dương phủ khoảng 71% bề mặt Trái Đất và chứa 97% toàn bộ nước của hành tinh.
    Sâu trung bình 3,6 km.
en: The ocean covers about 71% of Earth's surface and holds 97% of all the planet's
    water. Its average depth is 3.6 km.
src: science.nasa.gov/earth/facts/

p3  🏔️  LỤC ĐỊA
vi: Đất liền chiếm phần còn lại — khoảng 29%. Và nó ĐANG DI CHUYỂN: mảng Bắc Mỹ trôi
    về phía tây nhanh cỡ tốc độ móng tay em dài ra.
en: Land makes up the rest — about 29%. And it is MOVING: the North American plate
    drifts west about as fast as your fingernails grow.
src: science.nasa.gov/earth/facts/
```

### Ba chỗ phải cẩn thận khi viết ba câu này

1. ⚠️ **"29%" là PHÉP TRỪ của tôi (100 − 71), không phải câu NASA viết.** Nó suy ra từ đúng câu
   NASA trong cùng trang nên an toàn, nhưng phải biết đó là số dẫn xuất — đừng gắn nó vào một
   trang nguồn như thể trang đó viết ra con số ấy.
2. ⚠️ **KHÔNG được tổng quát hoá cái móng tay.** NASA nói về **mảng Bắc Mỹ**, không nói "các lục
   địa đều trôi nhanh cỡ móng tay". Viết "các lục địa di chuyển nhanh cỡ móng tay" là bịa một
   câu NASA không nói — đúng loại lỗi đã ghi ở lượt 30/07 (tự quy đổi mph sang km/h rồi ghi như
   số liệu có nguồn).
3. ⚠️ **XUNG ĐỘT SỐ LIỆU TRONG CHÍNH NHIỆM VỤ NÀY — phải sửa cùng lượt.** Thẻ mẫu vật `water` ở
   bước ⑥ đang ghi *"Nước bao phủ khoảng **70%** bề mặt Trái Đất!"*
   ([mission-earth.html:600](../../mission-earth.html)), trong khi đốm mới ghi **71%**. Hai chỗ
   trong **cùng một nhiệm vụ** nói hai con số cho cùng một sự thật — trẻ đọc cả hai và không biết
   tin cái nào. **Chốt 71% ở cả hai chỗ**, kèm nguồn; phải sửa cả entry `water` trong
   `learningdata/astronomy/earth_codex.json` nếu nó cũng ghi 70%.

### Vì sao ba đốm này KHÔNG dạy sai địa lý

Bản đồ phẳng equirectangular quy lat/lon ra phần trăm **bằng một phép chia**, chính xác tuyệt
đối. Nhưng ba đốm này **cố ý không khẳng định vị trí**: chúng nói về *khí quyển / đại dương / đất
liền nói chung*, không phải "chỗ này là Amazon". Nên đặt chúng ở đâu trong khung cũng đúng, và
điều kiện duy nhất là **cả ba nằm trong khung nhìn lúc mở màn** (siết phép kiểm hiện tại từ
`>= 2` lên `== 3`).

Bước ⑥ `life` vẫn là bước duy nhất khẳng định địa điểm thật, và nó **không bị đụng tới** —
`BIOMES` giữ nguyên toạ độ Amazon · Himalaya · Nam Cực · Đại Tây Dương.

---

## Kịch bản 8 bước sau khi sửa

```
[0]  KHỞI ĐỘNG HỆ THỐNG — chuyển cảnh 4 giây, TỰ CHẠY, không có nút bấm
     ⬢ NGUỒN      ● ONLINE     beep 720Hz
     ⬢ MÁY QUÉT   ● ONLINE     beep 880Hz
     ⬢ LIÊN LẠC   ● ONLINE     beep 1040Hz
     "HỆ THỐNG SẴN SÀNG"       arp
     → bản đồ Trái Đất hiện ra qua panTo

①  scan · CHẠM 3 ĐỐM  (bỏ hẳn kéo + zoom)
     Comet: "Chúng ta đã vào quỹ đạo Trái Đất! Máy quét vừa bắt được ba tín hiệu."
     [Lưới Chẩn Đoán quét MỘT vòng] → 3 đốm hiện, CẢ BA trong khung
     Comet: "Chạm vào từng tín hiệu để xem đó là gì nhé."
     → chạm ×3, beep cao dần 980/1120/1260Hz, mỗi đốm mở một thẻ nội dung
     → fadeGrid tan hết + sfx('ready')
     Byte: "Quét xong! Giờ mình xem hành tinh này ngày xưa trông thế nào." → bắc cầu ②

②  timeline · KỂ CHUYỆN 4 MỐC        (giữ nguyên cơ chế, hiệu ứng vẫn chạy trên phẳng)
③  sun      · KỂ CHUYỆN NGÀY/ĐÊM     (viết lại, xem dưới)
④  energy   · KÉO-THẢ 3 nguồn sạch   (giữ nguyên, khói vẫn chạy trên phẳng)
⑤  rotation · CHỜ TỚI ĐÚNG GIỜ — vùng tối trượt, bản đồ đứng yên, 0 cú kéo
     Giữ nút [⏩] → thời gian chạy → thanh tín hiệu lên/xuống. Không có trạng thái thua.
⑥  life     · 4 mẫu sự sống ở TOẠ ĐỘ THẬT   (không đụng tới)
⑦  eco      · 7 thẻ NÊN / KHÔNG NÊN          (thêm setMap('flat') tường minh)
⑧  core     · 3 viên ngọc + KỂ CHUYỆN màng khí quyển  (thêm setMap('flat') tường minh)
```

### Bước ③ `sun` viết lại — bỏ "đi tìm", giữ id

**Vì sao bản hiện tại hỏng trên bản đồ phẳng.** Bước này thiết kế theo lối *"hành tinh chìm vào
bóng tối, trẻ xoay camera ra TÌM Mặt Trời rồi chạm"*. Trên bản đồ phẳng, **cả thế giới hiện ra
cùng lúc nên không còn không gian để tìm**; và `dimSun` hạ `--lit` về 0 làm `.e2-sun` chỉ còn
**opacity 0,28** với quầng sáng co từ 64px xuống 18px
([mission-earth.css:633](../../css/mission-earth.css)), trên một cảnh vừa bị
`brightness(.26)`. Tức là trẻ được yêu cầu tìm một vật đã bị cố tình làm gần như vô hình, mà
không còn chỗ nào để tìm. *(Chủ dự án mô tả là "Mặt Trời bị ẩn sau bản đồ phẳng" —
[Suy luận] cơ chế thật có lẽ là chìm về 28% opacity chứ không phải bị lớp khác che, vì `.e2-sun`
có `z-index:2` và nằm SAU `.e2-layer` trong DOM. Chưa đo trên màn hình.)*

**Bản mới — đổi từ "tìm" sang "hiểu", một cú chạm:**

```
[cảnh] Bản đồ tối dần (dimSun). Mặt Trời góc trên-phải MỜ nhưng CÓ vòng nhấp nháy
       chỉ vào nó — không bắt tìm, chỉ bắt chạm.

Comet: "Ơ... tối hết rồi! Trái Đất không tự phát sáng đâu — toàn bộ ánh sáng và
        hơi ấm ở đây đều đến từ MỘT ngôi sao. Chạm vào nó xem!"

→ chạm  →  igniteSun + sfx('ignite')  →  ranh giới ngày/đêm hiện rõ

Byte: "Đó là Mặt Trời. Nhìn kỹ bản đồ đi: cùng MỘT lúc, nửa này đang là ban ngày
       còn nửa kia đang là ban đêm. Trái Đất tự quay, nên chỗ nào rồi cũng lần lượt
       được chiếu sáng."
```

⚠️ **Đây là chỗ bản đồ phẳng TỐT HƠN quả cầu, không phải kém hơn.** Trên quả cầu trẻ chỉ thấy
một nửa hành tinh nên câu "nửa này ngày, nửa kia đêm" không kiểm chứng được bằng mắt. Trên bản đồ
phẳng thì cả hai nửa cùng trong khung. Và ranh giới ngày/đêm **đã được cài sẵn đúng cách**:
`.e2-view::after` là gradient đặt trên `.e2-view` chứ không trên `.e2-layer`, nên nó **không
pan/zoom theo bề mặt** — đúng vì nó thuộc về Mặt Trời, không thuộc về hành tinh.

### Bước ⑧ — màng khí quyển phải vẽ lại

⚠️ `.e2-shield` là **vành sáng ở MÉP TRONG hình cầu** (ghi rõ trong CSS, và có lịch sử: bản 3D
từng vẽ nét stroke dày và ảnh chụp ra "một cái vòng rời lơ lửng cạnh hành tinh"). Trên hình chữ
nhật, một vành cong ở mép trong **không còn nghĩa gì**. Đây là hiệu ứng **duy nhất** thật sự bám
vào hình cầu.

Thay bằng: **ánh xanh lam mờ dâng lên phủ toàn bản đồ** (`opacity` 0 → 1 trên một lớp
`inset:0`), kèm lời Byte nói ra điều đang xảy ra — *"Màng khí quyển đã bọc kín hành tinh. Nó là
lớp áo giữ ấm và chắn thiên thạch cho mọi sinh vật bên dưới."* Kể chuyện thay cho hình học.

---

## Bốn việc BẮT BUỘC mà quyết định này sinh ra

### 0. Mọi mục tiêu phải NẰM TRONG KHUNG ngay lúc bước mở ra

Hệ quả cứng của "0 cú kéo": trẻ **không có cách nào** đi tới một thứ ngoài khung. Đáng lo nhất là
bước ⑥ `life` — Nam Cực ở `lat −75` (gần đáy bản đồ) và Amazon ở `lon −62`, hai cái cách nhau xa,
nên `panTo({dist})` của bước đó phải thu đủ rộng để **cả 4 mẫu vật cùng trong khung**. Thiếu một
cái là trẻ kẹt cứng vĩnh viễn.

**Phép kiểm mới:** ở mỗi bước có marker, **mọi** marker phải `visible` ngay sau `enter()`. Hiện chỉ
bước ① có phép kiểm loại này và nó còn đang nới ở mức `>= 2/3` — siết lên **toàn bộ**.

### A. Cảnh mở màn phải sáng — nhưng KHÔNG sửa bằng cách sinh lại ảnh

⚠️ **ĐÍNH CHÍNH SỐ LIỆU ĐÃ GHI TRONG HỒ SƠ DỰ ÁN.** Bản đầu của quyết định này (và chú thích ở
[mission-earth.html:797](../../mission-earth.html) + chú thích phép kiểm ở
`smoke_mission_earth.py`) ghi *"quả cầu 113,9 vs bản đồ phẳng 24,3 — tối hơn 4,7 lần"*, và con số
đó là **cơ sở cho quyết định 01/08 mở màn bằng quả cầu rồi đổi sang bản đồ giữa bước**. Đo lại thì
**quy con số đó cho "bản đồ phẳng tối" là sai địa chỉ.**

Đo trên **chính file ảnh** (`scratchpad/probe_earth_flat.py`):

| Ảnh | Sáng TB | Đất TB | Nước TB | Tương phản đất↔nước |
|---|---|---|---|---|
| `_src/flat.jpg` (gốc NASA 5400×2700) | 73,4 | 96,4 | 14,4 | 82,0 |
| `flat-2048.webp` (asset đang dùng) | **73,6** | 101,1 | 13,8 | **87,3** |
| `_src/globe.jpg` (vùng giữa) | **115,6** | — | — | — |

Tức asset **chênh 1,57 lần**, không phải 4,7 lần. Đo trên **màn hình**, đúng `pix()` và đúng vùng
`(0.3, 0.3, 0.4, 0.4)` của phép kiểm cũ (`scratchpad/probe_flat_dark.py` + `probe_flat_framing.py`):

| Cấu hình | Sáng TB |
|---|---|
| Quả cầu, **tắt** gradient vùng tối | 116,7 |
| **Quả cầu, như đang chạy** | **87,0** ← mốc thật cần đạt |
| Phẳng, khung nhìn mặc định, như đang chạy | **26,8** |
| Phẳng, `facing` (10, 20) châu Phi | 36,6 |
| Phẳng, `facing` (30, 95) | **69,3** |
| Phẳng, `facing` (30, 95) + gradient nhẹ | **84,0** |

**Nguyên nhân thật là KHUNG NHÌN, không phải loại bản đồ.** Trên bản đồ phẳng, tâm khung mặc định
rơi vào đại dương — mà nước đo được **13,8** còn đất **101,1** trên cùng bức ảnh. Đổi khung nhìn
thôi đã đưa 26,8 → 69,3 (**2,6 lần**, cùng gradient, cùng asset). Nhân tố thứ hai là
`.e2-view::after`: nó ăn **29,6 điểm** của quả cầu (116,7 → 87,0).

**Nên KHÔNG sinh lại asset.** Làm tối một bức ảnh NASA để chữa một lỗi khung nhìn là chữa sai chỗ,
và kéo sáng quá tay sẽ nhoè tương phản đất↔nước (87,3) mà bước ⑥ đang dựa vào để trẻ nhận ra
Amazon / Himalaya / Nam Cực. **Hai việc phải làm, cả hai đều 0 byte:**

**A1. Khung nhìn mở màn = `facing` (30, 95).** Đạt **84,0** so với mốc 87,0 của quả cầu như đang
chạy — thấp hơn **3,4%**, [Suy luận] dưới ngưỡng nhìn thấy được, so với khoảng cách 4,7 lần đã
từng dùng để biện minh cho cú đổi hình. Đã soi ảnh chụp (`scratchpad/framing-1.png`): khung đó cho
thấy **Đại Tây Dương · châu Phi · bán đảo Ả Rập · Ấn Độ Dương · Himalaya · dải mây ở phía bắc** —
tức có **cả nước, cả đất, cả mây** trong một khung. Đúng ba thứ mà ba đốm nói tới, nên khung nhìn
này được chọn vì **nội dung**, không chỉ vì độ sáng.

**A2. `.e2-view::after` khởi đầu NHẸ, bước ③ mới dâng lên đủ.** Hiện nó chạy hết cỡ
(`rgba(2,6,20,.82)` ở mép phải) **từ bước ① và không bao giờ đổi** — `igniteSun` chỉ sửa `--lit`
của Mặt Trời và cờ `.e2-night`, không đụng gradient này.

> ⚠️ **Hệ quả là phần thưởng của bước ③ đã bị tiêu trước.** Bước ③ định "hiện ra ranh giới
> ngày/đêm", nhưng trẻ đã nhìn đúng cái gradient đó từ cảnh đầu tiên. Nó không hiện ra gì cả.

Hạ mặc định xuống khoảng `.16 → .30` rồi để bước ③ dâng lên cỡ hiện tại: vừa được **+14,7 điểm**
sáng ở mọi bước, vừa khiến cú hiện ra ở bước ③ **thật sự hiện ra một cái gì**.

### B. `setSpin` phải về 0 ở mọi bước

[Cần đo] Trên ảnh quả cầu, `setSpin(1)` cho hành tinh tự quay. Trên bản đồ phẳng thì
`paint()` lấy `px` từ `facing` ([earth2d.js:201](../../js/earth2d.js)), nên [Suy luận] tự quay sẽ
thành **bản đồ trượt ngang vô tận** — trẻ đang đọc lời kể ở bước ② mà cả bản đồ bò sang một bên.
Các bước ②③④ hiện gọi `setSpin(1)`.

**Hệ quả cần bù bằng lời:** hành tinh không còn quay trước mắt trẻ nữa, nên ý "Trái Đất tự quay"
phải do **lời thoại** mang (đã đưa vào câu Byte ở bước ③) và do **cú kéo của trẻ** ở bước ⑤.

### C. `setMap('flat')` phải khai TƯỜNG MINH ở cả 8 bước

Hiện bước ⑦ `eco` và ⑧ `core` **không khai** — chúng đang đúng nhờ thừa hưởng từ bước ⑥. Trái đúng
ràng buộc ghi trong CLAUDE.md ngày 01/08. Sau quyết định này thì cả 8 bước cùng một giá trị, nên
càng dễ: khai đủ 8 lần, và thêm phép kiểm đếm `setMap('globe')` **phải bằng 0**.

---

## Đã bác — và vì sao

*(Phần này để dán cho ChatGPT/Gemini vòng sau — chúng không nhớ vòng trước.)*

- **Bỏ bước ③ `sun` khỏi nhiệm vụ.** Chủ dự án cho phép, nhưng giá đo được từ
  `AstroqSV/Services/Missions.cs`: mất **20 tt + 30 XP**; entry codex `"sun"` trong
  `earth_codex.json` (9 entry) **thành mồ côi** và `check_pages` mục [3c] báo hỏng; số bước
  8 → 7 nên cổng lộ trình đổi từ **6/8 sang 5/7** (`ceil(7 × 0.70)`); và **phải deploy backend**.
  Chú thích ngay trong `Missions.cs:47` nói rõ: *"THÊM bước mới thì an toàn"* — hàm ý bỏ thì
  không. Giữ id + đổi nội dung đạt đúng mục tiêu của chủ dự án với **0 đồng chi phí backend**.
- **Phim hoạt hình 30 giây mở màn.** Đã tồn tại (`js/mission-intro.js`), đã **xoá 01/08/2026**
  cùng ngày, vì trẻ phải nghe gần một phút trước khi được chạm vào gì. Xem `003`.
- **Bỏ điều khiển bản đồ khỏi cả nhiệm vụ.** Bước ⑥ `life` khẳng định 4 địa điểm thật; bỏ bản đồ
  là dạy sai địa lý — dự án đã trả giá đúng lỗi này ở bản 3D (thẻ "Rừng Amazon" giữa đại dương).
- **Bắt trẻ bấm 3 nút POWER / SCAN / READY.** Ba nút không mang nội dung = thêm 3 cú bấm chắn
  đường tới bài học. Giữ ý tưởng nhưng cho nó **tự chạy** 4 giây.
- **Thêm "vòng scan quét quanh Trái Đất"** và **thanh "Scanning… 100%"**. Cả hai đã có:
  `world.showGrid`/`fadeGrid`, và `progress(n, total)` với thanh đo bề rộng thật.
- **Rung nhẹ Trái Đất ở cảnh mở màn.** Cần nhánh `prefers-reduced-motion` riêng, và rung vật thể
  chính là thứ dễ gây khó chịu nhất trong bộ hiệu ứng.
- **Kéo `js/warp-screen.js` + `js/space-scene.js` vào làm màn phim mở nhiệm vụ.** Ở luồng
  onboarding trẻ đã đi qua `#nm-warp` của explorer rồi mới sang nhiệm vụ → thêm nữa là **hai màn
  chuyển cảnh liên tiếp**, đúng cái `003` đặt ra để bỏ.
- **Thêm robot/nhân vật mới.** `img/` chỉ có `luna2.png` · `luna-side.png` · `m1/b1`. Chủ dự án
  tự đặt ảnh gốc vào.
- **Nút `◀ XOAY ▶` cho bước ⑤.** Dán chữ "xoay" lên một cú dịch ảnh = dạy sai mô hình tư duy.
  Xem mục "Đã chọn 5".

### Biến Trái Đất thành "bảng nhiệm vụ" — 4 mission, 6–8 icon đặt không theo toạ độ *(ChatGPT, vòng 3)*

Đề xuất: coi bản đồ phẳng là *bảng minh hoạ*, không phải bản đồ; 6–8 icon chủ đề đặt ở vị trí
"trực quan" **không cần đúng toạ độ**; chia Trái Đất thành 4 mission (giới thiệu POI → phân loại
môi trường sống → dấu hiệu sự sống → hiện tượng khí quyển). **Bác cho Trái Đất, NHẬN cho World 2.**

- **Bỏ 17/24 phần tử nội dung đã có.** Đếm được: 6 bảng dữ liệu / **24 phần tử** / **653 dòng**
  logic bước / **297 khoá i18n × 2 ngôn ngữ** / 9 entry codex. Luồng đề xuất giữ `SCAN_POINTS` (3)
  và `BIOMES` (4), **bỏ** `ERAS` (4) · `ENERGY` (3) · `ECO` (7) · `GEMS` (3), kèm hoạt hình đổi tông
  thời đại, khói `--smog`, vệ tinh, drone quét laser, màng khí quyển và cú kích hoạt màn tổng kết.
  Nhận lại ~12 phần tử mới **chưa có nguồn**.
- ⚠️ **HAI PHẦN THƯỞNG SẼ KHOÁ VĨNH VIỄN — phần đắt nhất, và nó vô hình.**
  `Achievements.cs:87` → `new("eco-warrior", "mission", "mission:earth:eco", 1)`;
  `Specimens.cs:88` → `"mission:earth:timeline"`. Bỏ bước `eco` là **huy hiệu 🌱 Chiến Binh Xanh
  không ai mở được nữa**; bỏ `timeline` là **mẫu vật 🪨 Nham Thạch Cổ Đại khoá vĩnh viễn**. Đúng
  loại lỗi đã thành ràng buộc trong `Specimens.cs` (*"đừng viết Mở khoá tại Mission 02"*) — chỉ
  ngược chiều: điều kiện có thật, cái bị xoá là **bước**.
- **Bỏ 4 bước = 4/9 entry codex thành mồ côi** → `check_pages` [3c] hỏng. Và "4 mission" thay cho
  8 bước là đổi `Missions.Route` + gate + `missions.html` + **deploy backend**.
- ⚠️ **"Không cần đúng toạ độ" — độ chính xác đang MIỄN PHÍ, nên phép đổi này không mua được gì.**
  Toàn bộ chi phí đặt icon đúng chỗ trên bản đồ phẳng là **hai phép chia**
  ([earth2d.js:192](../../js/earth2d.js)). Không có phép chiếu nào để bỏ, không có "đồng bộ toạ độ"
  nào để bỏ. Và yêu cầu chính xác **không đến từ hệ marker — nó đến từ việc nền là ảnh chụp thật**:
  đặt 🏜️ Sa mạc "trực quan" lên ảnh NASA thì trẻ **nhìn thấy** icon sa mạc nằm trên rừng nhiệt đới.
  Trên ảnh thật, "gần đúng" chính là sai, và bức ảnh tự tố cáo.
- **Có một bản mạch lạc của ý này, và nó tốn art:** nếu độ chính xác không quan trọng thì đừng dùng
  ảnh vệ tinh thật — dùng **bản đồ vẽ cách điệu**. Ảnh thật + icon đặt lỏng là tổ hợp tự mâu thuẫn;
  bản đồ vẽ + icon đặt lỏng thì nhất quán. Cái giá: một asset art `img/` chưa có, và mất khả năng
  dạy địa lý thật ở bước ⑥. Muốn đi đường đó thì việc đầu tiên là **art, không phải code**.
- ⚠️ **"Claude sẽ dễ triển khai hơn" — đo được là ngược lại.** Kéo/zoom/chiếu bản đồ **đã viết xong
  và đã được 151 phép kiểm chứng minh**. Bỏ kéo = xoá ~15 dòng listener, bỏ zoom = ~6 dòng, giữ
  marker đúng toạ độ = **0 dòng**. Dựng một hệ icon-trên-overlay-cố-định = **thêm** JS + CSS + phép
  kiểm mới. Đề xuất này *cộng* code, và ném đi phần đã trả giá để debug.
- ✅ **NHẬN phần kiến trúc, và chuyển sang `001`:** ý *"6–8 icon chủ đề lặp lại cho mọi hành tinh"*
  (Đại dương/Rừng/Núi lửa/Cực/Sa mạc/Lịch sử/Thời tiết/Con người → Sao Hoả: Tàu đổ bộ/Olympus
  Mons/Băng cực/Robot) trả lời đúng câu **đang mở ở `001`**: làm 9 điểm đến mà không tốn 70 nghìn
  dòng. Nó biến việc soạn một World từ *thiết kế riêng* thành *điền vào chỗ trống* — tức cấp cho
  bộ 5 khuôn của `002` cái **lớp nội dung** mà `002` còn thiếu. **Đáng làm ở Mặt Trăng, nơi chưa có
  gì để ném đi.** Ở Trái Đất nó phải trả bằng 17 phần tử + 2 phần thưởng khoá vĩnh viễn + một lượt
  deploy, cho một mục tiêu mà quyết định này đã đạt với **0 đồng backend**.
- Ba con số trong lời thoại đề xuất: *"đại dương ~71%"* **khớp** câu NASA đã tra ✓ · *"rừng tạo oxy
  và là nơi sinh sống của hàng triệu loài"* thì `BIOMES` **đã có sẵn gần như nguyên văn** ·
  *"hơn 8 tỷ con người"* **cần nguồn** (UN, không phải NASA) trước khi dùng.

## Hệ quả — thứ tự triển khai

1. ~~Sinh lại ảnh bản đồ phẳng sáng hơn~~ — **BỎ, đo xong thấy không cần.** Thay bằng: **khung
   nhìn mở màn `facing` (30, 95)** + **hạ gradient `.e2-view::after` mặc định, bước ③ dâng lên**.
   Xem mục A. Làm trước vì mọi phép đo ảnh chụp sau đó dựa vào nó. *(Asset `flat-2048` giữ nguyên —
   0 byte đổi.)*
2. **Bước ①**: bỏ `setMap('globe')`, bỏ `hand('zoom')`/`hand('drag')`/khoảng chờ 1,4s; `SCAN_POINTS`
   mang nội dung 3 đốm + thẻ nội dung; siết phép kiểm `vis == 3`.
3. **`setMap('flat')` đủ 8 bước** + `setSpin(0)` + phép kiểm `setMap('globe')` == 0.
4. **Bước ③** viết lại theo kịch bản trên (vòng nhấp nháy chỉ vào Mặt Trời, bỏ "đi tìm").
5. **Bước ⑤** viết lại: vùng tối trượt theo biến `time`, `stationAngleTo` đổi nghĩa sang *chênh
   kinh độ trạm ↔ vệ tinh*, nút `[⏩ GIỮ ĐỂ CHỜ]`. **Xoá `setEarthDrag` khỏi nhiệm vụ.**
6. **Bước ⑧** đổi `.e2-shield` sang ánh xanh phủ toàn bản đồ + lời Byte.
7. **`panTo({dist})` của mọi bước** thu đủ rộng để mọi marker trong khung + phép kiểm việc đó.
8. **Chuyển cảnh "khởi động hệ thống"** 4 giây tự chạy.
9. **Thống nhất 70% → 71%** ở thẻ `water` (bước ⑥) và trong `earth_codex.json`.
10. **Đảo chiều ~6 phép kiểm** trong `scratchpad/smoke_mission_earth.py` mục `[scan]` + dời các
    phép kiểm cú kéo sang bước ⑤ (nay không còn kéo → phải viết lại chứ không chỉ dời), ghi lý do
    vào chính script.

**Ràng buộc từ nay:**
- **Không dùng `setMap('globe')` trong nhiệm vụ Trái Đất.** Ảnh `img/earth/globe-640.*` vẫn giữ
  trong repo (51 KB) — chưa xoá, vì `002` còn để mở khả năng một World khác cần nó.
- **Không đổi / bỏ / gộp id bước.** `scan·timeline·sun·energy·rotation·life·eco·core` là khoá
  DynamoDB. **Và bỏ một bước còn kéo theo thứ ở NGOÀI nhiệm vụ:** huy hiệu `eco-warrior` móc vào
  `mission:earth:eco` (`Achievements.cs:87`), mẫu vật `ancient-lava-rock` móc vào
  `mission:earth:timeline` (`Specimens.cs:88`) — bỏ bước là khoá vĩnh viễn phần thưởng đó. Trước khi
  bỏ bất cứ bước nào, `grep "mission:earth"` trong `AstroqSV/src/AstroqSV.Api/Services/`.
- **Không có cú kéo nào**, và vì thế `world.setEarthDrag` không được gọi ở nhiệm vụ Trái Đất. Phép
  kiểm đếm `setEarthDrag` phải bằng 0.
- **Mọi bước khai `setMap` tường minh**, dù cả 8 bước cùng một giá trị. Thừa hưởng là chỗ lỗi im
  lặng sinh ra.
- **Số liệu khoa học phải trỏ đúng trang NASA đã đối chiếu**, và **không tổng quát hoá** câu
  nguồn (xem cái bẫy "móng tay" ở trên).

**Còn mở, không thuộc quyết định này:** bước ① sau khi sửa có nội dung học rất mỏng (3 đốm là
toàn bộ) — nếu muốn nó dạy nhiều hơn thì phải thêm, và khi đó cân nhắc nó với thời lượng mở màn ·
số bước mỗi World (`001`) · độ tuổi mục tiêu.
