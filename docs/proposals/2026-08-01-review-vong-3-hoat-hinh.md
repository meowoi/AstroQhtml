# Claude đối chiếu mã nguồn — Vòng 3 (01/08/2026): "bỏ điều khiển bản đồ, dùng hoạt hình"

Đầu vào: đề xuất của ChatGPT (5 kịch bản thay thế cho bước mở đầu Nhiệm Vụ 01) + báo cáo của
chủ dự án sau khi chơi thật: *"luồng dễ lỗi, hình Trái Đất lúc tròn lúc méo"*.

---

# 0. Kết luận trước, lý do sau

| Phần | Xử |
|---|---|
| **Chẩn đoán "trẻ đang tương tác với engine, không phải nội dung học"** | **Nhận** — đúng, nhưng chỉ đúng với **bước 1**, không đúng với cả nhiệm vụ |
| **"Tutorial tốt là tutorial không cần đọc"** | **Nhận** — nguyên tắc đáng giá nhất của cả đề xuất |
| **Bỏ hẳn kéo/zoom khỏi bước 1** | **Nhận** |
| **Bỏ hẳn điều khiển bản đồ khỏi cả nhiệm vụ** | **BÁC** — giết nội dung địa lý thật của bước `life` |
| **Phim hoạt hình 30 giây mở màn** | **BÁC** — vừa cho một cái y hệt nghỉ hưu hôm nay (`003`) |
| **"Khởi động AI: POWER · SCAN · READY"** | **Nhận một phần** — làm *chuyển cảnh 4 giây*, KHÔNG làm một bước |
| **3 robot trinh sát bay quanh** | **Hoãn** — cần art mới, chưa có trong `img/` |
| **Trái Đất phát sáng / rung / vòng scan quét** | **Đã có sẵn trong mã** — `showGrid` + `fadeGrid` |

Việc thật cần làm không phải "thêm hoạt hình". **Mã nguồn đã có 7 hoạt hình có kịch bản**
(`js/earth2d.js`: `panTo` · `fadeGrid` · `dimSun` · `igniteSun` · `sendDrone` · `shield` ·
`setSatelliteSignal`, cộng `setEra`/`--smog` bằng CSS ở `mission-earth.html`). Nhiệm vụ **không**
tĩnh. Vấn đề là mấy hoạt hình đó đang bị gắn vào một bước mà **thao tác** của nó gây lỗi.

---

# 1. Số đo cho đúng lỗi chủ dự án báo: "lúc tròn lúc méo"

Đếm lời gọi `setMap` trong `mission-earth.html` — **7 lời gọi, và trẻ thấy hình đổi 3 lần**:

| Bước | Dòng | Map | Trẻ thấy |
|---|---|---|---|
| ① `scan` | 804 | `globe` | quả cầu (cảnh đầu tiên) |
| ① `scan` | **821** | **`flat`** | **ĐỔI HÌNH #1 — ngay giữa bước 1**, sau câu Comet |
| ② `timeline` | 891 | `globe` | **ĐỔI HÌNH #2** |
| ③ `sun` | 953 | `globe` | — |
| ④ `energy` | 998 | `globe` | — |
| ⑤ `rotation` | **1043** | **`flat`** | **ĐỔI HÌNH #3** |
| ⑥ `life` | 1103 | `flat` | — |
| ⑦ `eco` | *(không khai)* | thừa hưởng `flat` | — |
| ⑧ `core` | *(không khai)* | thừa hưởng `flat` | — |

Hai điều đọc ra được từ bảng này:

1. **Cú đổi hình tệ nhất nằm ngay trong bước 1.** Trẻ vừa nhìn thấy Trái Đất tròn, nghe một câu
   thoại, rồi hành tinh **dẹt ra thành hình chữ nhật** trước khi nó kịp làm gì. Đây là cảnh mở
   màn của cả nhiệm vụ. Ba đổi hình còn lại nằm ở ranh giới bước nên nhẹ hơn nhiều.
2. ⚠️ **Ràng buộc CLAUDE.md ghi hôm nay đã bị vi phạm sẵn:** *"MỖI BƯỚC KHAI MAP TƯỜNG MINH —
   `setMap` là trạng thái THỪA HƯỞNG"*. Bước ⑦ và ⑧ **không khai**. Chúng đang đúng nhờ may mắn
   (bước ⑥ để lại `flat`); đổi bước ⑥ là hai bước sau đổi theo mà không ai biết. Việc nhỏ, nên
   sửa cùng lượt.

**Vì sao cú đổi hình ở bước 1 lại tồn tại** (đọc chú thích `mission-earth.html:795-803`, đo được
hôm nay): ảnh quả cầu sáng trung bình **113,9**, bản đồ phẳng **24,3** — tối hơn **4,7 lần**. Mở
màn bằng bản đồ phẳng là mở màn bằng một hình gần đen. Nhưng trên ảnh quả cầu thì
`js/earth2d.js:201` đặt `translate` bằng **0**, tức **kéo không dịch được ảnh**. Bước 1 dạy kéo
→ buộc phải sang bản đồ phẳng → buộc phải đổi hình.

**Cả cái vòng đó chỉ tồn tại vì bước 1 quyết định dạy KÉO.** Bỏ việc dạy kéo là vòng tự tháo.

---

# 2. Chỗ ChatGPT chẩn đoán sai

## 2.1. "Đứa trẻ không quan tâm lat/lon, map thật hay méo" → đúng ở bước 1, SAI ở bước 6

Bước ⑥ `life` có 4 thẻ mẫu vật khẳng định **địa điểm thật**: Đại Tây Dương (12°, −42°) · Rừng
Amazon (−4°, −62°) · Nam Cực (−75°, 20°) · Himalaya. Bản đồ phẳng ở đó **không phải là chi tiết
kỹ thuật, nó là nội dung bài học** — và dự án đã trả giá đúng chỗ này: bản 3D đầu tiên sinh lục
địa bằng nhiễu fBm rồi neo thẻ *"🌳 Rừng Amazon"* vào giữa đại dương.

Bỏ điều khiển bản đồ khỏi cả nhiệm vụ = bước `life` mất chỗ đứng. Đó là lý do bác.

## 2.2. "Cho xem hoạt hình 30 giây rồi mới cho chơi"

`js/mission-intro.js` là **đúng cái đó**: cutscene ~30 giây, Luna vòng vào quỹ đạo, Comet giao
nhiệm vụ, pop-up kích hoạt. Nó **bị xoá hôm nay** (`docs/decisions/003`), lý do ghi nguyên văn
trong nhật ký: trẻ nghe *"gần một phút giới thiệu trước khi được chạm vào bất cứ thứ gì"*.

Đề xuất này là hoàn tác một quyết định vừa chốt cách đây vài giờ. ChatGPT không thể biết —
nó không đọc được repo. Nhưng đây đúng là chỗ nguy hiểm nhất của việc hỏi model không có mã nguồn:
**nó đề xuất lại thứ vừa bị bỏ, kèm lý lẽ nghe rất hợp lý.**

## 2.3. "Khởi động AI: POWER · SCAN · READY" và "3 robot" — hai kịch bản này là CÙNG MỘT khuôn

Cả hai đều là *bấm 3 vật phát sáng*. Đó đúng là khuôn **`signal_scan`** đã chốt ở `002` và đã
chạy ở bước 1. Nghĩa là:

- **Tin tốt:** rẻ. Không phải cơ chế mới, chỉ là đổi lớp vỏ nội dung.
- **Tin xấu:** ChatGPT trình bày nó như một thiết kế lại. Nó không phải. Đừng trả giá "thiết kế
  lại" cho một cú đổi vỏ.
- **Và:** POWER/SCAN/READY **không dạy gì cả**. Với một app giáo dục, tiêu một id bước của server
  cho ba cái nút không mang nội dung là một cú đổi tồi. Nó chỉ đáng giá khi làm **chuyển cảnh**
  (không phải bước, không báo server, không thưởng) — 4 giây, dùng `AstroQSfx.arp` + `ready` đã có.

## 2.4. "Trái Đất phát sáng, có vòng scan chạy quanh"

Đã có: `world.showGrid(true)` bật Lưới Chẩn Đoán bọc ngoài, `world.fadeGrid(900)` cho lưới tan
khi quét xong. Đề xuất này đang mô tả code đang chạy.

Phần *"rung nhẹ"* thì nên bỏ: nó cần một nhánh `prefers-reduced-motion` riêng, và rung **vật thể
chính** ở cảnh mở màn là thứ dễ gây khó chịu nhất trong bộ hiệu ứng.

## 2.5. "Máy quét: Scanning... █████ 100%"

Bảng mục tiêu đã có `progress(n, total)` với thanh tiến độ thật (có phép kiểm đo bề rộng > 2px).
Thêm một thanh ASCII nữa là **hai chỗ nói cùng một điều** — và sớm muộn lệch nhau.

## 2.6. So sánh Mario Galaxy / Kirby / Pokémon

Kết luận đúng nhưng lý do sai. Mario Galaxy **có** dạy điều khiển camera; nó chỉ không dạy bằng
chữ. Nguyên tắc thật không phải *"đừng cho điều khiển camera"* mà là **"đừng dạy bằng chữ và
bằng bàn tay hướng dẫn — hãy để cú thao tác đầu tiên tự thưởng cho mình"**. Cách phát biểu đó
mới dùng được, vì nó không đòi bỏ bước `life`.

---

# 3. Kịch bản tối ưu

Nguyên tắc: **giữ 8 id bước** (id là khoá DynamoDB — đổi là người chơi cũ mất tiến độ),
**một hình cho một chương**, **không dạy thao tác bằng chữ**.

## 3.1. Đổi hình: 3 lần → 1 lần, và lần đó là một nhịp truyện

| Chương | Bước | Map | Trẻ làm gì |
|---|---|---|---|
| **I — Quan sát** | ① `scan` ② `timeline` ③ `sun` ④ `energy` | **`globe`** suốt | chạm vào vật trong cảnh |
| **II — Khảo sát bề mặt** | ⑤ `rotation` ⑥ `life` ⑦ `eco` ⑧ `core` | **`flat`** suốt | kéo đi khắp bề mặt |

Cú đổi duy nhất nằm ở đầu bước ⑤, và **chính lời thoại nói ra việc đổi**: *"Quan sát từ xa xong
rồi. Giờ mình mở CHẾ ĐỘ BẢN ĐỒ để đi khắp bề mặt nhé."* Bản đồ phẳng lúc này không còn là "Trái
Đất bị méo" — nó là **một dụng cụ khác của con tàu**, và trẻ vừa được nghe lý do bật nó.

Bước ⑦ ⑧ khai `setMap('flat')` tường minh (đang thiếu).

## 3.2. Bước ① `scan` viết lại — bỏ hẳn kéo và zoom

**Trước:** quả cầu → Comet nói → **đổi sang bản đồ phẳng** → bàn tay dạy `zoom` → chờ 1,4s →
bàn tay dạy `drag` → bàn tay dạy `tap` → 3 điểm ở toạ độ thật, trong đó **chỉ 2/3 nằm trong
khung** (phép kiểm hiện tại chỉ đòi `>= 2`), điểm thứ ba **bắt buộc phải kéo mới thấy** → lời
nhắc sau 9 giây nếu trẻ kẹt.

**Sau:**

```
[cảnh] Quả cầu Trái Đất, đứng yên, sáng rõ. Lưới Chẩn Đoán bọc ngoài.
       panTo(dist 4.0) đang phóng nhẹ vào — chuyển động duy nhất trên màn hình.

Comet: "Chúng ta đã vào quỹ đạo Trái Đất rồi!
        Máy quét vừa bắt được ba tín hiệu lạ trên bề mặt."

[cảnh] fadeGrid chạy MỘT vòng quét (không tan hẳn) → 3 đốm sáng cyan hiện ra,
       nhấp nháy, CẢ BA nằm trong khung nhìn.

Comet: "Chạm vào từng tín hiệu để mình xem đó là gì nhé."

→ trẻ chạm.  beep cao dần theo số điểm (980 → 1120 → 1260 Hz)  →  progress(n, 3)
→ đủ 3/3: fadeGrid tan hết + sfx('ready')

Byte: "Quét xong! Ba tín hiệu đều là dữ liệu về hành tinh này. Mình đọc nó theo
       thứ tự thời gian nhé — Trái Đất ngày xưa trông KHÁC HẲN bây giờ."
       (câu này bắc cầu sang bước ② timeline)
```

Cái mất và cái được:

- **Mất:** `hand('zoom')` · `hand('drag')` · khoảng chờ 1,4 giây · lời nhắc 9 giây (giữ lại làm
  bảo hiểm, chỉ là không còn ai cần) · và **toạ độ tuyệt đối của `SCAN_POINTS`**.
- **`SCAN_POINTS` quay về `dlat`/`dlon` TƯƠNG ĐỐI với chỗ đang nhìn** — trên ảnh quả cầu đó là hệ
  toạ độ duy nhất đúng (`js/earth2d.js:20-23`). ⚠️ **Điều này KHÔNG dạy sai địa lý**, và lý do
  nằm trong chính chú thích của bước: *"CỐ Ý không đặt tên địa danh cho ba điểm — bước 1 dạy cách
  điều khiển, không dạy địa lý"*. Ba đốm không khẳng định vị trí nào cả. Bước ⑥ mới là bước khẳng
  định vị trí, và nó có `BIOMES` riêng trên bản đồ phẳng — **không đụng tới**.
- **Được:** cảnh mở màn là Trái Đất **tròn, sáng, không đổi hình**. Trẻ thấy **3/3** đốm ngay
  (siết được phép kiểm từ `>= 2` lên `== 3`). Thao tác duy nhất là **chạm** — thao tác không thể
  làm sai, không có trạng thái thua, không cần bàn tay hướng dẫn.

## 3.3. Dạy KÉO ở bước ⑤, nơi cú kéo tự dạy nó

Bước ⑤ `rotation` là **bước duy nhất của cả nhiệm vụ có phản hồi liên tục** (`002` ghi rõ: thanh
"Signal strength", dung sai 20°, **không có trạng thái thua**). Nghĩa là đây đúng là chỗ mà
*"tutorial không cần đọc"* hoạt động thật: trẻ kéo bừa → thanh nhích lên hoặc tụt xuống → nó tự
hiểu quy tắc trong vài giây, không cần một dòng chữ nào.

Bàn tay `hand('drag')` chuyển từ bước ① sang đây, và **chỉ hiện sau 6 giây nếu trẻ chưa kéo** —
không hiện ngay. Vòng ngắm `.e2-aim` đã có, giữ nguyên.

Đây là chỗ ChatGPT nói đúng nhất mà không biết mình đúng: nguyên tắc của nó áp vào bước ⑤ thì
cho ra một cải tiến thật, còn áp vào bước ① thì chỉ cho ra "bỏ đi cho rồi".

## 3.4. Chuyển cảnh "khởi động hệ thống" — 4 giây, KHÔNG phải một bước

Salvage phần đáng giá của kịch bản "Khởi động AI": đặt nó **trước** bước ①, làm nhịp mở màn.

```
[nền đen 0,3s]  →  ba nhãn HUD sáng lên lần lượt, mỗi cái 0,5s:
   ⬢ NGUỒN            ●  ONLINE      sfx: beep 720Hz
   ⬢ MÁY QUÉT         ●  ONLINE      sfx: beep 880Hz
   ⬢ LIÊN LẠC         ●  ONLINE      sfx: beep 1040Hz
[0,4s]  "HỆ THỐNG SẴN SÀNG"          sfx: arp
[cảnh Trái Đất hiện ra qua panTo]
```

**Không có nút để bấm** — đúng cái ChatGPT đề xuất là *bấm* 3 nút thì tôi bác: bắt trẻ bấm 3 cái
nút không mang nội dung là thêm 3 cú bấm vào con đường tới bài học. Để nó **tự chạy** thì được
đúng cảm giác "chuyên nghiệp" mà không tốn một cú bấm nào, và tôn trọng `prefers-reduced-motion`
bằng cách hiện thẳng trạng thái cuối.

Dùng lại `AstroQSfx.beep/arp` (đã có), `css/mascot.css` cho box thoại (đã có). Ước lượng ~40 dòng
HTML+CSS, 0 asset mới.

## 3.5. Cái KHÔNG làm

- **Không** thêm engine hoạt hình mới. `js/space-scene.js` (388 dòng) + `js/warp-screen.js`
  (270 dòng) đã vẽ được Trái Đất + tàu Luna bằng canvas 2D, có nút "Bỏ qua ›", có nhánh
  reduced-motion — nhưng nó đang làm **chuyển cảnh dashboard → Bản Đồ** (`003`) và **cố ý không
  dùng cho đường vào nhiệm vụ** vì ở onboarding trẻ đã đi qua `#nm-warp` của explorer rồi. Kéo
  nó vào đây là hai màn chuyển cảnh liên tiếp — đúng cái `003` đặt ra để bỏ.
- **Không** thêm robot/nhân vật mới: `img/` chỉ có `luna2.png` · `luna-side.png` · `m1/b1`. Cần
  art thì chủ dự án đặt ảnh gốc vào `img/`, tôi không tự sinh.
- **Không** đổi id bước, không đổi thứ tự bước, không đụng backend. `Missions.cs` nguyên vẹn.

---

# 4. Chi phí thật — kể cả phần đắt

| Việc | Ước lượng |
|---|---|
| Viết lại `steps.scan.enter()` (bỏ setMap/zoom/drag/chờ) | ~25 dòng bỏ, ~10 dòng thêm |
| `SCAN_POINTS` về `dlat`/`dlon` + `facingLatLon()` | ~8 dòng *(là revert một phần của lượt 01/08)* |
| `setMap('globe')` cho ② ③ ④ *(đã có)* · `setMap('flat')` tường minh cho ⑦ ⑧ | 2 dòng |
| Dời `hand('drag')` sang ⑤ + hẹn 6 giây | ~10 dòng |
| Chuyển cảnh "khởi động hệ thống" | ~40 dòng HTML/CSS + 6 khoá i18n × 2 ngôn ngữ |
| Viết lại lời thoại `s1_*` (`say1` `say2` `done` `hint`) | 4 khoá × 2 ngôn ngữ |
| **⚠️ Đảo chiều ~6 phép kiểm trong `smoke_mission_earth.py`** | **phần đắt nhất** |

⚠️ **Bộ kiểm thử hiện đang BẢO VỆ đúng cái hành vi cần đổi** — cùng loại lỗi đã giữ nút Mặt Trăng
sống sót một tháng. Cụ thể, mục `[scan]` của `smoke_mission_earth.py` khẳng định:

- `world.map == "flat"` sau lời thoại → phải thành `"globe"` *(dòng ~584)*
- *"KHÔNG dạy KÉO trong lúc còn ở ảnh quả cầu"* → thành vô nghĩa, bỏ *(~600)*
- *"bàn tay KÉO CÓ hiện sau khi đã sang bản đồ"* → bỏ khỏi scan, dựng lại ở ⑤ *(~602)*
- *"kéo làm ảnh dịch thật > 100px"* → chuyển sang mục ⑤ *(~629)*
- *"3 điểm đứng yên tại toạ độ thật"* → chuyển sang mục ⑥ `life` *(~634)*
- *"KÉO để xoay đổi được góc nhìn"* → chuyển sang mục ⑤ *(~672)*
- `vis >= 2` → **siết lên `== 3`** *(~573)* — đây là cái duy nhất chặt hơn chứ không lỏng hơn

Sáu cái đầu là **đổi có lý do**, không phải nới lỏng: điều chúng bảo vệ (*trẻ không bị dạy một
thao tác chưa có tác dụng*) được bảo vệ **tốt hơn** bằng cách không dạy thao tác đó ở đó nữa.
Phải ghi rõ lý do vào chính script, không thì lượt sau có người tưởng bộ kiểm bị nới.

Bộ `smoke_mission_earth` chạy ~10 phút một lượt (nó chơi hết nhiệm vụ 5 lần).

---

# 5. Cái tôi KHÔNG chắc — cần chủ dự án chốt

1. **Bước ① còn dạy gì không?** Kịch bản của tôi biến nó thành "chạm 3 lần" — an toàn, nhưng
   **nội dung học gần bằng 0** (nó chỉ bắc cầu sang bước ②). Đó là đánh đổi có ý thức: bước mở
   màn nên dễ tuyệt đối. Nhưng nếu muốn nó dạy một điều gì thật thì phải nói, và khi đó 3 đốm cần
   có nội dung (ví dụ: mỗi đốm mở một câu về khí quyển / đại dương / lục địa).
2. **"Chương I — Chương II" có cần nói ra cho trẻ không?** Tôi đang để nó ngầm, chỉ hiện qua một
   câu thoại ở bước ⑤. Có thể hiện rõ hơn (một thẻ "CHƯƠNG II · KHẢO SÁT BỀ MẶT" 2 giây) — rõ hơn
   nhưng thêm một nhịp chờ.
3. **Bước ③ `sun` còn một câu thoại sai từ bản 3D:** `s2_hint` = *"Kéo sang phải để nhìn ra xa
   hơn"*, mà Mặt Trời ở bước đó là một `<button class="e2-sun">` **cố định trên màn hình**, chỉ
   việc chạm. Nhật ký 01/08 đã ghi phát hiện này nhưng tôi chưa kiểm nó đã được sửa chưa — cần
   kiểm trước khi làm.
4. **Có nên chọn ngược lại: `flat` cho cả 8 bước, bỏ hẳn ảnh quả cầu?** Được 0 lần đổi hình thay
   vì 1. Nhưng mất ba thứ **bám vào hình cầu**: đổi tông theo thời đại (②), ranh giới ngày/đêm
   (③), khói phủ khí quyển (④) — trên hình chữ nhật thì "ranh giới ngày/đêm" không còn đọc ra
   được. Tôi không đề xuất đường này, nhưng nó là đường duy nhất đạt 0 lần đổi hình.
5. **Tôi chưa chạy thử bản sửa.** Mọi con số trong tài liệu này là đo trên code **hiện tại**
   (`setMap` đếm bằng grep, độ sáng 113,9 / 24,3 lấy từ chú thích của lượt đo 01/08), không phải
   đo trên bản đề xuất.

---

# 6. Ghi cho vòng sau — dán vào ChatGPT/Gemini

Những thứ **không đề xuất lại**, kèm lý do (hai model kia không nhớ vòng trước):

- **Cutscene 30 giây mở màn nhiệm vụ.** Đã có (`js/mission-intro.js`), đã **xoá 01/08/2026** vì
  trẻ phải nghe gần một phút trước khi được chạm vào gì. Xem `docs/decisions/003`.
- **Bỏ điều khiển bản đồ khỏi cả nhiệm vụ.** Bước ⑥ `life` khẳng định 4 địa điểm thật; bỏ bản đồ
  là dạy sai địa lý — dự án đã trả giá đúng lỗi này ở bản 3D.
- **Đổi / bỏ / gộp id bước.** `scan·timeline·sun·energy·rotation·life·eco·core` là khoá trong
  DynamoDB. Đổi là người chơi cũ mất tiến độ. Có phép kiểm `check_pages` mục [3c] đối chiếu với
  `Missions.cs`.
- **Thêm "vòng scan quét quanh Trái Đất".** Đã có: `world.showGrid` + `world.fadeGrid`.
- **Thêm thanh "Scanning… 100%".** Đã có `progress(n, total)` với thanh thật.
- **Bắt trẻ bấm 3 nút không mang nội dung** (POWER/SCAN/READY). Dùng làm chuyển cảnh tự chạy thì
  được; làm một bước có thưởng thì không.
- **Thêm nhân vật/robot mới.** `img/` chưa có art; chủ dự án tự đặt ảnh gốc vào.
