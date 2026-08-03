# 005. Bảy bước, quả cầu 3D dạy ngày/đêm, và bỏ mọi vùng tối trên bản đồ phẳng

**Trạng thái:** đã chốt · **đã triển khai 02/08/2026**, trừ mục ⑩ (ảnh minh hoạ 5 mốc — chờ
chủ dự án đặt ảnh gốc vào `img/`)
**Ngày mở:** 2026-08-02 · **Ngày chốt:** 2026-08-02
**Người quyết:** chủ dự án

> ✅ **ĐÃ LÀM (02/08/2026)** — theo đúng thứ tự ở mục *Hệ quả* dưới:
> ① đo · ② tra nguồn góc chiếu (2 URL NASA kiểm 200) · ③ server 7 bước + lọc `doneSteps` ·
> ④ bản đồ phủ kín khung + phép kiểm · ⑤ nhịp 0 ở `explorer.html` + `READ_MS` 10 → **15 giây** ·
> ⑥ bỏ hẳn `.e2-terminator` · ⑦ bước ① 7 châu lục + câu đố 71%/29%, bước ② **5 mốc**,
> bước ③ **3 vùng khí hậu**, bước ⑦ giọng ôn tập · ⑧ `perfMode` thành khoá dùng chung
> `astroq-perf` + dải nhắc mạng kém · ⑨ đảo chiều/viết lại phép kiểm.
>
> ⚠️ **CÒN LẠI ĐÚNG MỘT VIỆC — mục ⑩:** 5 ảnh minh hoạ cho 5 mốc của bước ②. Chủ dự án tự
> đặt ảnh gốc vào `img/`; đã kiểm 02/08 là chưa có ảnh nào. **Cố ý KHÔNG dựng ô ảnh rỗng**
> trong markup: một khung ảnh trống là một lời hứa hệ thống chưa giữ — đúng loại lỗi mà
> chính `005` đang đi sửa. Cảnh ①–④ khi có ảnh thì **bắt buộc dán nhãn MINH HOẠ**
> (không tồn tại ảnh chụp Trái Đất thời đó), chỉ cảnh ⑤ là ảnh chụp thật.
>
> ⚠️ **PHÁT SINH TRONG LÚC TRIỂN KHAI — MỘT LỖI CÓ SẴN, ĐÃ SỬA:** `.e2-layer` ở chế độ bản đồ
> phẳng bị **neo mép trái** (CSS `inset:0 + margin:auto + width` quá ràng buộc; trục dọc thì CSS
> chia đều margin nên căn giữa, trục ngang thì bỏ `right` nên neo trái). Hậu quả nặng: **mọi kinh
> độ đông hơn ~83° không thể đưa vào khung trên điện thoại dọc** — tức dãy Himalaya (lon 87) của
> bước ⑤ `life` **chưa bao giờ nhìn thấy được** trên máy tính bảng dọc. Đã sửa bằng
> `left:50% + right:auto + margin-left:-nửa bề rộng`; đo lại `probe_map_cover` **203/203** và mọi
> kinh độ đều đưa được vào khung. Đây cũng là thứ làm mục ⑤ của `004` (*"phép kiểm mọi marker
> `visible` ngay lúc vào bước"*) trước đây không thể đạt.
>
> ⚠️ **VÀ MỘT LỖI CÓ SẴN THỨ HAI, CÙNG HỌ, LỘ RA NGAY SAU ĐÓ:** `measure()` của `js/earth2d.js`
> chỉ chạy lúc dựng (khi map còn là `globe`) và khi `resize`, nhưng `.e2-layer` **đổi cỡ** theo
> chế độ bản đồ. Trên 1440×900 hai cỡ trùng nhau nên không ai thấy; trên **390×844 thì lệch
> 390 vs 844** → `maxPyPct()` ra **0** → phép dịch **dọc** bị kẹp về 0 → **vĩ độ cao không vào
> được khung**: Nam Cực (lat −75) ở `dist:3,1` rơi xuống **y = 921 trên khung cao 844**.
> ⚠️ Hai lỗi này cùng một bài học: **`probe_map_cover.py` mù với cả hai** (203/203 xanh suốt) vì
> nó chỉ hỏi *"bản đồ có hở không"*. Thứ bắt được chúng là phép kiểm mới **"marker kế tiếp có
> nhìn thấy được không"**, chạy trên **màn dọc**. Cùng một câu đã ghi ở mục *Phát hiện đáng giá
> nhất về bộ kiểm thử*: bộ kiểm chỉ tìm được thứ nó chịu hỏi.
>
> ⚠️ **HAI PHÁT HIỆN CỦA MỤC 1 CHƯA XỬ, CỐ Ý** (chúng không nằm trong danh sách *Hệ quả*):
> nhãn "Mặt Trăng" đè nhãn "Trái Đất", và Sao Kim chiếm góc dưới-phải TO HƠN Trái Đất ở
> đúng khoảnh khắc chỉ nên nói về Trái Đất. Cả hai làm nhịp 0 kém đi nhưng là **việc bố cục
> của cảnh 3D**, cần chủ dự án chốt hướng (dời camera? ẩn nhãn hàng xóm trong lúc onboarding?).

**Thay `004`.** `004` vẫn đọc được để biết vì sao dự án tới được đây, nhưng **ba quyết định của
nó bị đảo** — ghi rõ ở mục "Đảo khỏi `004`" dưới. Đừng thi hành `004` mục ⑤ và mục A2 nữa.

## Bối cảnh

Chủ dự án chơi thật bước ⑤ `rotation` và gửi ảnh chụp. Ảnh cho thấy `.e2-terminator` —
gradient đen **82%** ở mép phải ([mission-earth.css:574](../../css/mission-earth.css)) — trông
như một bức tường đen, không như ranh giới ngày/đêm. Nhận xét: *"bỏ bước vùng tối trượt đi, xấu
lắm, hình ảnh đính kèm là sự thật tôi đã trải nghiệm"*.

Đó là **bằng chứng thị giác chống lại chính `004`**: `004` mục A2 định hạ gradient mặc định rồi
cho bước ③ **dâng lên đúng mức trong ảnh đó**. Mức đó không dùng được.

Cùng lượt, chủ dự án đề xuất một kịch bản luồng khác (5 nhịp) và một ý mà `004` đã bỏ:
**cho quả cầu 3D một việc**.

## Đã chọn

### 1. Ngày/đêm dạy trên **quả cầu 3D của `explorer.html`**, không dạy trên bản đồ phẳng

`004` mục 3 và bước ③ định dạy ngày/đêm bằng `.e2-view::after` trên bản đồ phẳng, với lý lẽ
*"đây là chỗ bản đồ phẳng TỐT HƠN quả cầu"* (cả hai nửa cùng trong khung). Lý lẽ đó vẫn đúng về
**nội dung**, nhưng sai về **hình ảnh** — xem ảnh chụp.

**Đã kiểm trong mã: quả cầu ở `explorer.html` có ranh giới ngày/đêm THẬT.**

| Kiểm | Kết quả |
|---|---|
| Vật liệu hành tinh | `MeshStandardMaterial` ([explorer.html:1138](../../explorer.html)) → ăn sáng thật |
| Nguồn sáng | `PointLight(0xfff0d0, 3.4, 0, 0.12)` gắn **vào chính `this.sun`** ([:1322](../../explorer.html)) |
| Lớp mây | `ProceduralTextures.clouds()` ([:1163](../../explorer.html)) |
| Dữ liệu khí quyển | bảng thông tin Trái Đất **đã có** `atmosphere:'Nitơ + oxy'` ([:426](../../explorer.html)), khoá i18n `kAtmo` đã có |

Nửa hướng về Mặt Trời sáng, nửa kia tối — và đó là **Mặt Trời thật trong cảnh**, không phải một
cái đèn đặt bừa. Trẻ xoay camera quanh Trái Đất thấy đúng thứ phi hành gia thấy.

⚠️ **Cái bẫy của bản 3D KHÔNG tái diễn, và lý do phải ghi lại.** Bước `rotation` bản 3D chết vì
kéo xoay **camera** chứ không xoay **hành tinh**, nên góc trạm–vệ tinh không đổi →
**không thể hoàn thành**, và `prefers-reduced-motion` thì **treo vĩnh viễn**. Ở nhịp mới:

> **Không có điều kiện thắng.** Đây là *quan sát*, không phải *giải*. Không có gì để đo sai,
> không có gì để treo. Và xoay camera quanh Trái Đất **chính là** thao tác đúng về vật lý cho
> việc ngắm ngày/đêm.

Vì thế đưa **ngày/đêm** sang quả cầu là an toàn, trong khi đưa **`rotation`** sang đó thì không.
Hai việc khác nhau — đừng đọc quyết định này thành "3D được phục hồi".

✅ **ĐÃ ĐO 02/08/2026 — `scratchpad/probe_globe_daynight.py`. Lo ngại của tôi bị BÁC bằng số.**

Tôi đã lo `AmbientLight 0.55` + `HemisphereLight 0.35` ([:1323–1324](../../explorer.html)) ≈ 0,9
ánh sáng nền sẽ làm sáng cả nửa tối và khiến ranh giới nhạt. **Không phải.** Đo trên đĩa rắn
(tâm 775,400 · r 52px · khung 1440×900), profile ngang qua tâm:

| dx | −52 | −38 | −10 | +4 | +18 | +25 | +32 | +39 | +46 |
|---|---|---|---|---|---|---|---|---|---|
| độ sáng | 139,6 | 181,6 | 114,6 | 124,3 | 120,3 | **87,9** | **65,3** | **47,5** | 46,3 |

**20% tối nhất 55,0 · 20% sáng nhất 161,5 → chênh 106,5 điểm · tỉ số 2,94×.** Ranh giới nằm rõ ở
mép phải và tụt dứt khoát. **KHÔNG cần chỉnh đèn** — bỏ việc "hạ ánh sáng nền" khỏi kế hoạch.

⚠️ **Nhưng đo xong lại lộ BA việc khác, cả ba chỉ thấy khi nhìn ảnh chụp** (`scratchpad/globe-crop-x2.png`):

1. ⛔ **VÀNH KHÍ QUYỂN TO GẤP ~2 LẦN BÁN KÍNH HÀNH TINH VÀ TRÔNG ĐẶC NHƯ BI THUỶ TINH.**
   Đây là chỗ Comet định chỉ vào để nói *"đây là bầu khí quyển"* — mà khí quyển Trái Đất là **lớp
   da rất mỏng**, không phải cái vỏ dày gấp đôi hành tinh. Chỉ vào đó mà không nói gì thêm là
   **dạy sai mô hình tư duy**, đúng loại lỗi `005` đang cố tránh ở bước ③ (*"không phải vì gần
   Mặt Trời"*). Hai đường: **thu vành trong nhịp onboarding**, hoặc để Comet **nói thẳng** *"khí
   quyển thật mỏng hơn thế nhiều — ở đây vẽ dày lên cho em thấy được"*. Đường hai rẻ hơn và trung
   thực hơn.
2. ⚠️ **Nhãn "Mặt Trăng" đè lên nhãn "Trái Đất"** ở đúng khung sau khi camera bay tới.
3. ⚠️ **Sao Kim chiếm góc dưới-phải và TO HƠN Trái Đất trên màn hình**, ở đúng khoảnh khắc lẽ ra
   chỉ nói về Trái Đất. Đĩa Trái Đất chỉ **~104px đường kính** trên khung 1440 — nhỏ cho một bài
   học phải nhìn kỹ.

⚠️ **Ba lỗi trong CHÍNH BỘ ĐO của tôi, ghi lại vì cùng một họ với các lỗi dự án đã trả giá:**
(a) probe quét **đúng một hàng ngang** qua vị trí nhãn tên — mà nhãn nằm **phía trên** hành tinh,
nên nó đo nền trời và báo "đĩa rộng 759px, mọi giá trị 12–54"; (b) đổi sang dò vùng với ngưỡng 55
thì nó **bắt cả vành khí quyển và tinh vân nền**, ra bán kính 327px trong khi đĩa thật 52px;
(c) script patch in `patched` **vô điều kiện** dù `str.replace` không khớp gì — báo thành công cho
một thay đổi chưa hề xảy ra. **Cả ba đều tự nhận là "đo xong" trong khi chưa đo đúng thứ gì.**

### 2. **KHÔNG có vùng tối nào trên bản đồ phẳng.** `.e2-terminator` bỏ hẳn

Kể cả mức mặc định nhẹ (`.16 → .30`) cũng xem lại khi đo — nó **ăn độ sáng** của mọi bước mà
không còn bài học nào để trả lại, vì bài học đã chuyển sang quả cầu.

### 3. Bỏ hẳn bước ⑤ `rotation`. Nhiệm vụ còn **7 bước**

Ngày/đêm đã sang quả cầu; vùng tối trượt bị bác; cú kéo đã bị bác từ `004`. Không còn việc gì
cho bước này mà không phải bịa ra một cơ chế mới — ngược mục tiêu "đơn giản".

**Đã kiểm: bỏ bước này AN TOÀN.** Không phần thưởng nào bị khoá vĩnh viễn:

| Móc | Trỏ vào | Sau khi bỏ |
|---|---|---|
| `rookie-astronaut` | `mission:earth` (cả nhiệm vụ) | ✅ không đụng |
| `eco-warrior` | `mission:earth:eco` ([Achievements.cs:87](../../../AstroqSV/src/AstroqSV.Api/Services/Achievements.cs)) | ✅ bước `eco` còn |
| `ancient-lava-rock` | `mission:earth:timeline` ([Specimens.cs:88](../../../AstroqSV/src/AstroqSV.Api/Services/Specimens.cs)) | ✅ bước `timeline` còn |

Đây **đúng là điểm khác biệt** với việc bỏ `eco` hay `timeline` — hai bước đó đã bị bác ở `004`
chính vì chúng khoá phần thưởng vĩnh viễn.

Giá phải trả:

| Mục | Giá |
|---|---|
| Thưởng | **−20 tt · −30 XP** → nhiệm vụ còn **235 tt · 355 XP** |
| Cổng lộ trình | 6/8 → **5/7** (`ceil(7 × 0.70)`), server tự tính, client tự đúng |
| Codex | xoá entry `"rotation"` ([earth_codex.json:205](../../learningdata/astronomy/earth_codex.json)), 9 → 8 |
| Backend | **phải deploy** — `Missions.cs` đổi |

**Logic server chịu được bản ghi cũ:** `AllStepsDone` và `GateMet` đều lọc theo `m.Steps`
([Missions.cs:96](../../../AstroqSV/src/AstroqSV.Api/Services/Missions.cs) · `:148`), nên tài
khoản đã xong `rotation` không phá gì.

⚠️ **NHƯNG có một lỗi hiển thị cụ thể, phải sửa cùng lượt.** `doneSteps` trả về client là
**danh sách thô, chưa lọc** ([MeEndpoints.cs:737](../../../AstroqSV/src/AstroqSV.Api/Endpoints/MeEndpoints.cs)
+ `:758` — `st.Keys.Where(k => k != "done")`). Ba tài khoản thật nào đã xong `rotation` sẽ thấy
`missions.html` ghi **"8/7 bước"**. Sửa bằng một dòng lọc `doneSteps` theo id còn tồn tại — dòng
đó còn chặn luôn mọi lần bỏ/đổi bước sau này.

### 4. Mã client bỏ được cùng bước ⑤

`steps.rotation` · `.e2-aim` · `.e2-sat` · khoá i18n `s3_*` · và trong `js/earth2d.js` thì
`setEarthDrag` · `stationAngleTo` · `setSatelliteVisible/Signal` **mất người dùng cuối cùng**.

⚠️ `002` đã dựng khuôn `orientation_align` **chỉ để phục vụ bước này**, với lý lẽ *"thanh đo liên
tục duy nhất của cả nhiệm vụ"*. Bỏ bước là **bỏ luôn lý do tồn tại của khuôn thứ 5**. Không xoá
`002` — nhưng phải ghi vào đó rằng khuôn ấy hiện **0 người dùng**, và quyết định giữ hay bỏ nó
thuộc World thứ hai, không thuộc quyết định này.

### 5. Quả cầu 3D là **PHẦN THÊM**, không phải bài học bắt buộc

Chủ dự án chốt phương án (a). Hệ quả:

- Nhiệm vụ 7 bước **đứng một mình đủ** — mạng kém không mất bài học bắt buộc nào.
- Chế độ giảm tải được phép **bỏ hẳn** quả cầu → cắt được three.js + `unpkg.com` khỏi luồng
  onboarding bắt buộc. Đây là phần tiết kiệm thật.
- Đường lùi 12 giây ([map-onboard.js:134](../../js/map-onboard.js)) thay vì im lặng nhảy trang
  thì **nói một câu** + mời bật "Giảm cấu hình".

### 6. Nút giảm tải: đã có một nửa, nâng thành thứ dùng chung

**Đã có:** `perfMode` "Giảm cấu hình" / "Reduce quality" trong bảng trái `explorer.html`
([:163](../../explorer.html)).

**Còn thiếu ba thứ:**
1. Không tự phát hiện, không có thông báo — trẻ phải tự tìm ra nút.
2. **Không dùng chung giữa các trang.** Phải thành **một khoá `localStorage`** như `astroq-sfx` /
   `astroq-lang` (quy tắc 2 mục 2 của CLAUDE.md).
3. Nó chỉ hạ chất lượng cảnh 3D, **không cắt byte tải về** — mà thứ nặng thật là three.js.

⚠️ **Tự phát hiện KHÔNG ĐỦ.** [Chưa kiểm chứng] Network Information API
(`navigator.connection.saveData` / `effectiveType`) **Safari/iOS không hỗ trợ**, mà iPad là thiết
bị hay chơi nhiệm vụ này nhất. Nên hai lớp: (a) `saveData`/`effectiveType` khi có · (b) mốc 12
giây đã tồn tại làm lớp chắc chắn.

---

## Nhiệm vụ Trái Đất sau khi chốt — 7 bước

**0 vùng tối · 0 cú kéo · 0 lần đổi hình · 0 lần `setMap('globe')`.**

```
[nhịp 0]  Ở `explorer.html?onboard=1` — QUẢ CẦU 3D THẬT. Phần THÊM, không bắt buộc.
          Comet: bầu khí quyển (neo vào lớp mây + dòng "Khí quyển: Nitơ + oxy" đã có)
                 → mời trẻ XOAY để ngắm nửa ngày / nửa đêm
          → chạm Trái Đất → sang nhiệm vụ

①  scan      · "Trước hết mình trải phẳng Trái Đất ra thành bản đồ nhé"
               → 7 CHÂU LỤC (chạm từng cái, sáng lên + hiện tên)
               → "Vậy nước hay đất nhiều hơn?" → đoán → hé lộ 71% / 29%
②  timeline  · 5 MỐC (xem mục riêng dưới) · popup rộng + ảnh to · mẫu vật 🪨
③  sun       · XÍCH ĐẠO · ÔN ĐỚI · CỰC + VÌ SAO (góc chiếu, KHÔNG phải khoảng cách)
④  energy    · Trái Đất nóng lên → kéo-thả 3 nguồn năng lượng sạch
⑤  life      · 4 mẫu sự sống ở toạ độ thật — GIỮ NGUYÊN, 0 dòng sửa
⑥  eco       · 7 thẻ NÊN / KHÔNG NÊN · huy hiệu 🌱
⑦  core      · 3 viên ngọc ☀️💧🌬️ — ôn lại đúng ba thứ vừa học
             → màn tổng kết → dashboard → Comet chúc mừng → tour 7 bước (đã có)
```

**Vì sao 7 châu lục ở bước ① chứ không phải bước riêng.** Nó là bài học về *bề mặt Trái Đất*,
cùng nhà với câu "biển hay đất nhiều hơn" — một arc, một bước. Và nó lấp đúng lỗ hổng `004` để
mở: *"bước ① sau khi sửa có nội dung học rất mỏng (3 đốm là toàn bộ)"*.

**Vì sao ⑦ `core` giữ nguyên cơ chế.** 3 viên ngọc ☀️ nhiệt độ · 💧 nước · 🌬️ khí thở đúng bằng ba
thứ nhiệm vụ vừa dạy (③ nhiệt độ · ① nước · khí quyển ở nhịp 0). Chỉ đổi **lời** để nó đọc ra như
một câu ôn lại, không đổi cơ chế.

---

## Bước ② — 5 mốc, đã tra nguồn

Bản 4 mốc cũ (dung nham → đại dương → khủng long → ngày nay) có **một lỗi nội dung**, chủ dự án
phát hiện:

> Khủng long **không** xuất hiện ngay sau khi đại dương hình thành, và Trái Đất **đã xanh từ rất
> lâu** trước khi khủng long tuyệt chủng.

**Đo được từ nguồn:** đại dương (~4,4 tỷ) → khủng long (233 triệu) là khoảng **4,2 tỷ năm**, tức
**~92% lịch sử Trái Đất** nằm trong đúng cái khoảng trống mà bản 4 mốc nhảy qua. Và cây lên cạn
(kỷ Silur, ~443–419 triệu) → khủng long tuyệt chủng (66 triệu) là **~370 triệu năm Trái Đất đã
xanh**. Thêm 1 mốc, sửa một hiểu sai lớn.

### Năm mốc — chữ dùng thật

Mọi URL đã kiểm trả **200** ngày 02/08/2026.

| Mốc | Con số **có nguồn** | Trích nguyên văn |
|---|---|---|
| ① Trái Đất nóng bỏng | **4,54 tỷ** | NPS: Precambrian = *"4,540 million years ago to 542 million years ago"* |
| ② Đại dương đầu tiên | **~4,4 tỷ** | NASA: *"Individual crystals of zircon within the rocks are **4.4 billion years old**"* · *"the chemical make up of the Jack Hills crystals suggests that they formed in the presence of liquid water, **likely even an ocean**"* |
| ③ Sự sống bắt đầu | **~3,8 tỷ** | NASA: *"Earth's vast oceans provided a convenient place for life to begin about **3.8 billion** years ago"* |
| ③ cây lên cạn | **kỷ Silur, 443,3–419,2 triệu** | NPS: *"first land plants (Silurian)"* |
| ③ động vật lên cạn | **kỷ Devon, 419,2–358,9 triệu** | NPS: *"first amphibians (Devonian)"* |
| ④ Khủng long | **233 → 66 triệu** | NPS: *"True dinosaurs evolved by approximately **233 million years ago**, early in the Late Triassic"* · *"mass extinction (end Cretaceous)"* **66,0** |
| ⑤ Ngày nay | *(không con số)* | — |

**Nguồn:**
- `https://science.nasa.gov/earth/facts/` — tuổi Trái Đất · sự sống 3,8 tỷ · khí quyển 78/21
- `https://science.nasa.gov/earth/earth-observatory/ancient-crystals-suggest-earlier-ocean/` — zircon 4,4 tỷ + đại dương
- `https://www.nps.gov/subjects/geology/time-scale.htm` — mọi mốc kỷ · 66,0
- `https://www.nps.gov/articles/000/the-precambrian.htm` — 4.540 triệu
- `https://www.nps.gov/subjects/fossils/triassic-dinosaurs.htm` — 233 triệu

### ⚠️ Bốn cái bẫy khi viết năm mốc này

1. ⛔ **3,8 tỷ — KHÔNG phải 3,7.** Bản đề xuất ban đầu ghi 3,7. Nhưng
   `science.nasa.gov/earth/facts/` — **chính trang dự án đang dẫn cho 3 đốm của bước ①** — viết
   **3.8 billion**. Ghi 3,7 là **tái tạo đúng lỗi 70% / 71%** mà `004` phải đi sửa 5 chỗ: cùng
   một nhiệm vụ dẫn cùng một trang NASA nhưng nói hai con số.
2. ⛔ **233 — KHÔNG phải 230.** 230 là con số phổ biến, nhưng trang NPS đọc được viết **233**, và
   dùng 233 thì **cùng một nguồn với mốc 66** ở đầu bên kia của cùng cảnh.
3. ⛔ **THÚ XUẤT HIỆN CÙNG LÚC VỚI KHỦNG LONG, không phải sau.** NPS: *"first dinosaurs **and
   first mammals** (Triassic)"*. Cảnh ⑤ phải viết *"động vật có vú **phát triển mạnh**"* — viết
   *"thú xuất hiện"* là **sai**. Chỗ này rất dễ bị "sửa" thành sai bởi người đọc sau.
4. ⛔ **CÂY LÊN CẠN TRƯỚC, CON VẬT THEO SAU — cách nhau một kỷ.** Gộp thành *"thực vật và động vật
   … tiến lên đất liền"* là gộp hai mốc cách nhau ~60 triệu năm.

⚠️ **Số 4,3 tỷ đã BỎ.** Bản đề xuất ghi khoảng "4,4–4,3 tỷ". Trang NASA đọc được **không phát
biểu 4,3**; nó chỉ có 4,4. Một số có nguồn chắc còn dễ cho trẻ hơn một khoảng. *(Có một trang
`astrobiology.nasa.gov` [Chưa kiểm chứng] có thể nói "4.3 to 4.4" — chưa mở, chưa dùng.)*

⚠️ **Điều trớ trêu phải biết:** cảnh ③ phủ 3,8 tỷ → ~440 triệu, tức **~74% lịch sử Trái Đất trong
MỘT cảnh** — chính là cái nó sinh ra để chống. Vẫn hơn hẳn bản 4 mốc. Nếu muốn xử lý thì cách rẻ
nhất là **vẽ một thanh thời gian** trong popup cho thấy cảnh này chiếm bao nhiêu phần lịch sử —
biến chỗ nén thành chính bài học, **không** thêm mốc thứ 6.

### Câu dẫn của bước ② *(dùng làm chữ bảng mục tiêu)*

> *"Trái Đất không biến đổi chỉ trong vài bước. Từ một hành tinh nóng bỏng đến thế giới xanh hôm
> nay là hành trình kéo dài hơn 4,5 tỷ năm."*

### Giá của 4 → 5 mốc

**0 đồng backend.** Bước `timeline` có **một** codex id cho cả bước (`earth-formation`,
[Missions.cs:60](../../../AstroqSV/src/AstroqSV.Api/Services/Missions.cs)), không phải một id mỗi
mốc.

- `ERAS` +1 phần tử · khoá i18n mới ở **cả `vi` và `en`** (`check_pages` [3c] canh sẵn)
- ⚠️ **CSS tông màu mới cho cảnh ③.** Hiện có `era-magma` · `era-ocean` · `era-dino`. Tông cảnh ③
  phải **khác rõ `era-ocean`** — hai cảnh liền nhau trông giống nhau thì trẻ tưởng bấm không ăn.
- Cập nhật entry `earth-formation` trong `earth_codex.json` cho khớp chữ trên bảng
- Mẫu vật 🪨 vẫn ở mốc dung nham = cảnh ① → **không đụng**
- **Ảnh minh hoạ: 5, không phải 4.** Cảnh ①–④ **bắt buộc dán nhãn MINH HOẠ** (không tồn tại ảnh
  chụp Trái Đất thời đó, và NASA Image Library không có tranh dựng — đã tra 30/07); cảnh ⑤ là ảnh
  chụp thật. **Chủ dự án tự đặt ảnh gốc vào `img/`** — đã kiểm 02/08: chưa có ảnh nào.

---

## Bước ③ `sun` — vì sao xích đạo nóng

⛔ **KHÔNG được viết "vì gần Mặt Trời hơn".** Đây là quan niệm sai phổ biến. Chênh lệch khoảng
cách xích đạo ↔ cực là ~6.400 km trên tổng ~150 triệu km.

Nguyên nhân là **góc chiếu**: ở xích đạo tia nắng gần thẳng đứng nên cùng một lượng năng lượng
dồn vào diện tích nhỏ; ở cực nó chiếu xiên nên rải ra diện tích lớn hơn (và đi qua nhiều khí
quyển hơn).

⚠️ [Chưa kiểm chứng] **Chưa có URL nào cho câu giải thích này.** Phải tra và kiểm 200 một trang
`science.nasa.gov` hoặc `spaceplace.nasa.gov` **trước khi viết ba thẻ này**. Chưa có nguồn thì
chưa viết con số nào — quy tắc mục 6 CLAUDE.md, và cái bẫy "móng tay" ở `004`.

---

## Lỗi ĐANG CHẠY: bản đồ không phủ kín khung — ĐÃ ĐO, ĐÃ BIẾT NGUYÊN NHÂN

Từ ảnh chủ dự án gửi (khung ~1900px): bản đồ chỉ tới **x ≈ 1243**; bên phải **đen thuần**, bảng
vệ tinh trôi lơ lửng trong vùng đen. ✅ **Đã đo 02/08/2026 — `scratchpad/probe_map_cover.py`.**

### Nguyên nhân: MỘT lỗi, hai trục

```
css/mission-earth.css:550   .e2.e2-flat .e2-layer{width:max(100vw,200vh);
                                                  height:max(50vw,100vh);}
js/earth2d.js:213 (paint)   px = -wrapLon(facing.lon)/360*100     // tới ±50% BỀ RỘNG
                            py =  facing.lat/180*100              // tới ±50% CHIỀU CAO
```

> Lớp được cỡ để phủ khung **KHI phép dịch = 0**. Rồi `paint()` dịch nó theo `facing` — và
> **không có chỗ nào kẹp phép dịch lại trong giới hạn còn phủ kín.** Mọi `facing` khác (0, 0)
> đều đẩy lớp ra khỏi khung.

Trên 1900×985: lớp cao `max(950, 985)` = **985 = đúng bằng chiều cao khung** → dư dọc = **0** →
mọi `lat ≠ 0` hở trên hoặc dưới. Đó là vì sao có cả `T` gap lẫn `R` gap.

### 5/9 cấu hình bước thật HỞ, trên MỌI cỡ màn đã thử (6/9 trên điện thoại)

| Bước | lon · dist | 1900×985 | 2560×1080 | 390×844 |
|---|---|---|---|---|
| ③ `sun` | 95 · 5,2 | **R602 T240** (31,7%) | R873 T212 (34,1%) | T206 (52,7%) |
| ⑤ `rotation` sau khi kéo | 108 · 4,4 | **R521 T55** (27,4%) | R768 (30,0%) | T47 (12,0%) |
| ④ `energy` | 95 · 3,8 | R294 T86 (15,5%) | R473 T12 (18,5%) | T74 (19,0%) |
| ② `timeline` | 95 · 3,4 | R160 T19 (8,4%) | R299 (11,7%) | T17 (4,3%) |
| ⑤ `rotation` lúc vào | 20 · 4,4 | R39 T55 (2,9%) | R142 (5,6%) | T47 (12,0%) |

**R521 ở bước ⑤ khớp đúng ảnh chủ dự án** (~657px; chênh vì `dist` lúc chụp rộng hơn).

⚠️ **TỆ NHẤT LÀ BƯỚC ③ `sun` — đúng cái bước `004` muốn đặt bài học ngày/đêm lên.** Nó lùi ra xa
nhất (`dist:5.2` → zoom 0,846 < 1) nên hở cả hai trục. Một lý do nữa để chuyển bài học đó sang
quả cầu.

### ⛔ KHÔNG chữa được bằng cách kẹp phép dịch

Ở zoom 1 với khung 1900 và lớp 1970, dư mỗi bên chỉ 35px → **|lon| ≤ 6,4°**. Kẹp là **ném bỏ khung
nhìn `FACE_OPEN` (30, 95)** mà `004` đã chọn **vì nội dung** (Đại Tây Dương · châu Phi · Ả Rập ·
Ấn Độ Dương · Himalaya · dải mây). Không được đánh đổi nội dung để chữa một lỗi hình học.

### ✅ ĐÃ SỬA 02/08/2026 — hai trục xử khác nhau, vì chúng khác nhau về địa lý

| Trục | Cách chữa | Vì sao không dùng cách kia |
|---|---|---|
| **Kinh tuyến** | **LÁT BA BẢN ẢNH** (`mkPic` + `.e2-wrap-w/-e` ở `left:∓100%`) | equirectangular **lặp liền mạch** (180°Đ = 180°T). Kẹp `px` thì mất `FACE_OPEN` |
| **Vĩ tuyến** | **KẸP `py`** theo phần dư dọc thật (`maxPyPct()`) | **không lặp được** — hai cực là mép thật của thế giới |
| **Sàn phóng** | `ZOOM_MIN` **0,8 → 1** | zoom < 1 là lớp nhỏ hơn khung → dải đen **đối xứng** trên/dưới, không liên quan `facing` |

⚠️⚠️ **KHÔNG ĐƯỢC ĐỔI CỠ HAY TỈ LỆ `.e2-layer` ĐỂ CHỮA.** Marker định vị bằng **phần trăm của
lớp đó** (`project()` trả `x = (lon+180)/360*100`) — đổi cỡ lớp là dời **toàn bộ toạ độ địa lý**,
đúng lỗi *"thẻ Amazon rơi giữa đại dương"* của bản 3D. Hai bản sao nằm **ngoài hộp** của lớp và
chỉ để lấp mắt; kẹp `py` chỉ đổi **khung nhìn**, không đổi địa lý (marker là con của lớp nên dịch
cùng lớp).

**Đo lại sau khi sửa: `probe_map_cover.py` 203/203 đạt, 0 hỏng** — 7 cỡ màn × 9 bước thật, cộng
ma trận `lon` × `dist` đầy đủ (gồm `lon=180` và `dist=5,2` trên điện thoại).

**Phép thử phá hoại — probe có răng:** tắt hai bản sao thì hở trở lại đúng như trước
(`lon=95` → 450px · `lon=108` → **521px** · `lon=180` → 985px).

⚠️ **Việc còn phải làm cùng lượt:** chuyển hình dạng phép đo này vào `smoke_mission_earth.py` —
153 phép kiểm hiện có **không có phép nào hỏi "bản đồ có phủ kín khung không"**, và đó là lý do
lỗi sống tới lúc chủ dự án chơi thật.

### ⚠️ Phát hiện đáng giá nhất về bộ kiểm thử

**153 phép kiểm không có phép nào hỏi "bản đồ có phủ kín khung không".** Đó là lý do lỗi này sống
tới lúc chủ dự án chơi thật. Phép kiểm mới phải đo **cả 4 phía × mọi bước × nhiều tỉ lệ màn** —
`probe_map_cover.py` đã có sẵn hình dạng đó, chuyển vào `smoke_mission_earth.py`.

⚠️ **Hai lỗi trong chính probe của tôi:** (a) lượt chạy đầu **đo giữa lúc tween mở màn của trang
còn đang chạy**, cho ra số **không đơn điệu** (`lon=95` hở 535px nhưng `lon=108` hở 0) — đã sửa
bằng cách chờ `facing` đứng yên **và** đối chiếu `facingLatLon()` thật với số vừa truyền vào, lệch
thì **bỏ mẫu**; (b) phép kiểm cũ tin con số truyền vào thay vì con số đọc lại được.

*(Câu chẩn đoán "thanh SIGNAL đã đầy sẵn khi vừa vào chưa?" **tự hết** — bước đó không còn tồn
tại để tự thắng.)*

---

## Đảo khỏi `004` — và vì sao

| `004` chốt | `005` chốt | Vì sao |
|---|---|---|
| Mục ⑤: bước `rotation` = **vùng tối trượt**, giữ id | **Bỏ hẳn bước `rotation`**, 8 → 7 bước | Ảnh chụp cho thấy gradient vùng tối trông như bức tường đen. Không phần thưởng nào bị khoá — đã kiểm 3 chỗ móc |
| Mục A2: hạ gradient mặc định, **bước ③ dâng lên** | **Bỏ hẳn `.e2-terminator`** | Mức "dâng lên" chính là mức trong ảnh |
| Mục 3 + bước ③: ngày/đêm trên bản đồ phẳng, *"chỗ phẳng TỐT HƠN quả cầu"* | Ngày/đêm trên **quả cầu 3D** ở explorer | Lý lẽ nội dung vẫn đúng, nhưng hình ảnh không dùng được. Quả cầu explorer có `PointLight` gắn vào Mặt Trời thật — đã kiểm mã |
| Mục ⑤: `stationAngleTo` đổi nghĩa, +40–60 dòng `earth2d.js` | **Xoá** `stationAngleTo` · `setEarthDrag` · `setSatelliteVisible/Signal` | Không còn người dùng |
| Hệ quả B: *"ý Trái Đất tự quay phải do LỜI THOẠI mang"* | Trẻ **thấy thật** ở quả cầu | Không phải bù bằng lời nữa |
| Bước ② 4 mốc | **5 mốc** | Bản 4 mốc dạy sai: khủng long như thể xuất hiện ngay sau đại dương |

**`004` giữ nguyên hiệu lực ở:** bản đồ phẳng cả nhiệm vụ · 0 cú kéo · bỏ `hand('drag')`/`hand('zoom')` ·
`setMap` khai tường minh mọi bước · `setSpin(0)` · khung nhìn mở màn `FACE_OPEN` (30, 95) ·
mọi marker phải trong khung ngay lúc `enter()` · 71% (không phải 70%) · bước ⑧ `.e2-shield` đổi
sang ánh xanh phủ toàn bản đồ · chuyển cảnh "khởi động hệ thống" 4 giây tự chạy.

## Đã bác — và vì sao

*(Phần này để dán cho ChatGPT/Gemini vòng sau — chúng không nhớ vòng trước.)*

- **Gom 8 bước thành 5 mission** *(ChatGPT, vòng 4)*. Bỏ `timeline` · `energy` · `eco` · `core` →
  **huy hiệu 🌱 Chiến Binh Xanh và mẫu vật 🪨 Nham Thạch Cổ Đại khoá VĨNH VIỄN**
  (`Achievements.cs:87` · `Specimens.cs:88`), mất **95 tt + 145 XP**, 4/9 entry codex mồ côi →
  `check_pages` [3c] hỏng. Gần nguyên văn phương án đã bác ở `004`.
- **Màn 3D cuối "xoay Trái Đất tự do"** *(ChatGPT, vòng 4)*. Đây **chính là** bước `rotation` bản
  3D đã hỏng — kéo xoay camera nên trẻ **không thể hoàn thành**, `reduced-motion` thì treo. Và
  hoàn tác thắng lợi đo được: 308 KB → 71 KB, `unpkg.com` khỏi onboarding bắt buộc, 154/154.
- **"Map transforms into the existing 3D Earth. No loading screen."** [Suy luận] không có phép
  biến hình nào giữa ảnh + `transform` CSS và WebGL. "Chuyển mượt" = nạp **cả hai** engine, tức
  nhận đủ chi phí 3D mà không bỏ được gì của 2D.
- **Thay `life` bằng icon môi trường đặt "trực quan"** *(ChatGPT, vòng 4)*. Bước `life` khẳng định
  **4 toạ độ thật** kèm nguồn. Trên ảnh vệ tinh thật, "gần đúng" chính là sai và bức ảnh tự tố
  cáo — trẻ **nhìn thấy** icon sa mạc nằm trên rừng nhiệt đới. Cùng lý do `004` đã bác.
- **`rotation` = vệ tinh bay qua** *(Claude đề nghị, chủ dự án chọn khác)*. Giữ được thanh đo liên
  tục và câu chuyện "khôi phục tín hiệu", nhưng là **thêm một cơ chế mới** — ngược mục tiêu
  "đơn giản" của chủ dự án. Bỏ bước thì đơn giản hơn và không mất phần thưởng nào.
- **`rotation` = 7 châu lục** *(cân nhắc rồi bỏ)*. Codex id vẫn là `"rotation"` mà nội dung là
  châu lục → lệch nghĩa cho người đọc mã sau; đổi codex id = sửa `Missions.cs` = **deploy**.
  Châu lục về bước ① đúng nhà hơn: nó là bài học về bề mặt, cùng arc với "biển hay đất".
- **Mốc thứ 6 để tách cảnh ③** *(cân nhắc rồi bỏ)*. Cảnh ③ nén 74% lịch sử, nhưng thêm mốc làm
  bước ② dài nhất nhiệm vụ. Thanh thời gian trong popup đạt cùng mục tiêu với 0 mốc thêm.

## Hệ quả — thứ tự triển khai

1. **ĐO trước, sửa sau** — hai phép đo, không đụng code sản phẩm:
   (a) bề rộng thật `.e2-img` vs khung ở nhiều tỉ lệ màn *(lỗi bản đồ không phủ kín)*;
   (b) độ sáng hai nửa quả cầu Trái Đất ở explorer *(tương phản ngày/đêm có đủ đọc được không)*.
2. **Tra nốt nguồn còn hở:** câu giải thích góc chiếu cho bước ③. Chưa có URL 200 thì chưa viết.
3. **Server:** `Missions.cs` bỏ bước `rotation` · lọc `doneSteps` theo id còn tồn tại ·
   `earth_codex.json` xoá entry `"rotation"` → **deploy** → chạy lại `test_missions`.
4. **Sửa lỗi bản đồ không phủ kín khung** + **thêm phép kiểm** cho nó.
5. **Nhịp 0 ở `explorer.html`:** lời Comet (khí quyển → mời xoay → ngày/đêm) × 2 ngôn ngữ ·
   chỉnh ánh sáng **chỉ nếu bước 1(b) đo thấy cần** · nới `READ_MS`.
   ⚠️ Có một phép kiểm **đọc thẳng `READ_MS` mặc định** để chắc bản thật vẫn 10 giây — đổi số thì
   phải đổi cả phép kiểm đó, không thì nó báo hỏng đúng lúc code làm đúng.
6. **Bỏ `.e2-terminator`** + phép kiểm đếm nó phải bằng 0.
7. **Bước ①:** 7 châu lục + đoán biển/đất. **Bước ②:** 5 mốc + popup rộng + tông màu cảnh ③.
   **Bước ③:** 3 vùng khí hậu. **Bước ⑦ `core`:** đổi lời sang giọng ôn tập.
8. **Thông báo mạng kém** + `perfMode` thành khoá `localStorage` dùng chung.
9. **Đảo chiều / viết lại phép kiểm** trong `smoke_mission_earth.py`: xoá cả mục `[rotation]`
   (gồm mục `[8b]` vòng ngắm), sửa mọi phép đếm bước 8 → 7, ghi lý do vào chính script.
10. **Ảnh minh hoạ 5 mốc** — chờ chủ dự án đặt vào `img/`, làm phần còn lại trước.

**Ràng buộc từ nay:**
- **Không có vùng tối / terminator nào trên bản đồ phẳng.** Phép kiểm đếm `.e2-terminator` = 0.
- **Không dùng `setMap('globe')`** trong nhiệm vụ Trái Đất. Quả cầu chỉ ở `explorer.html`.
- **Quả cầu 3D không bao giờ được mang điều kiện thắng.** Nó là nơi *quan sát*. Điều kiện thắng
  trên camera-orbit chính là lỗi đã làm bước `rotation` bản 3D không thể hoàn thành.
- **Không đổi id của 7 bước còn lại.** Trước khi bỏ bất cứ bước nào:
  `grep "mission:earth" AstroqSV/src/AstroqSV.Api/Services/`.
- **Mọi bài học BẮT BUỘC phải nằm trong 7 bước.** Thứ ở `explorer.html` là phần thêm — mạng kém
  bỏ qua được. Đừng để một bài học bắt buộc trôi sang đó.
- **Số liệu khoa học phải trỏ đúng trang đã đối chiếu, và không tổng quát hoá câu nguồn.**
  Bốn cái bẫy của bước ② ghi ở trên — nhất là "thú xuất hiện cùng lúc khủng long".

**Còn mở, không thuộc quyết định này:** khuôn `orientation_align` của `002` nay **0 người dùng** —
giữ hay bỏ thuộc World thứ hai · số bước mỗi World (`001`) · độ tuổi mục tiêu · ý *"6–8 icon chủ
đề lặp cho mọi hành tinh"* đã **nhận cho Mặt Trăng** ở `004`, chưa làm.
