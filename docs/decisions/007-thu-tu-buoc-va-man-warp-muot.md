# 007. Thứ tự bước của Nhiệm Vụ 01, và màn warp phải mượt

**Trạng thái:** đã chốt
**Ngày mở:** 2026-08-03 · **Ngày chốt:** 2026-08-03
**Người quyết:** chủ dự án (chơi thật rồi báo 9 việc trong một lượt)

## Bối cảnh

Chủ dự án chơi hết luồng `select → explorer?onboard=1 → mission-earth` và báo **chín**
chỗ. Bảy chỗ là lỗi trình bày hoặc rác còn sót (ảnh mốc thời gian trễ · khung mốc lệch cỡ
· nút không căn giữa · vành khí quyển hình tròn · đĩa Mặt Trời còn sót · bàn tay đứng
nguyên chỗ · thẻ và bảng che nhau). Hai chỗ còn lại đụng tới quyết định cũ nên vào sổ này:

⚠️ **Nhận xét xuyên suốt: không một lỗi nào là "code sai".** Cả chín đều là **hai thứ đúng
đặt cạnh nhau thì sai** — một hình vẽ đúng cho quả cầu để nguyên trên bản đồ phẳng · một
luật "chạm đốm nào trước cũng được" cạnh một bàn tay đi theo thứ tự khai báo · một thẻ canh
giữa khung cạnh một bảng neo đáy · một câu thoại nối vào bước A mà bước B chen vào giữa ·
một vòng `rAF` đúng nhưng không được chạy. Đọc từng file thì file nào cũng đúng. Thứ bắt
được chúng là **chơi thật**; thứ giữ chúng không quay lại là phép kiểm **đo được** (chồng
lấn px² · khung mới/giây · chênh chiều cao px · bàn tay chỉ vào id nào).

1. **Thứ tự bước** — *"sự kiện mực nước biển chen giữa vô duyên rồi, đổi 3 nhà máy xong
   lại đến đoán mực nước biển và phân loại 7 việc?"* `005` chốt 7 bước theo thứ tự
   `scan · timeline · sun · energy · life · eco · core`; câu hỏi này nhắm đúng vào chỗ
   `life` nằm giữa `energy` và `eco`.
2. **Màn warp bay vào Hệ Mặt Trời bị giật** — *"sau màn select, chuyển cảnh bay vào hệ
   mặt trời bị giật, tìm hiểu lý do"*. Trước lượt này chưa có phép đo nào cho câu đó.

## Các phương án đã cân nhắc

### 1. Thứ tự bước

**A. Giữ nguyên, viết lại lời thoại cho `life` đỡ lạc** — đề xuất bởi Claude (tự bác)
Ưu: 0 đồng backend. Nhược: không chữa được nguyên nhân. Câu mở của `eco` (`ec_say1`)
là *"Nhưng đổi được ba nhà máy thôi thì **chưa đủ** đâu…"* — nó **nối trực tiếp** vào
`energy`. Muốn giữ thứ tự cũ thì phải bỏ luôn câu đó, mà đó là câu mang cả lý do tồn
tại của bước `eco` (chủ dự án đưa nguyên ý: *"đã dùng năng lượng xanh để thay thế nhưng
chưa đủ, quan trọng hơn là Trái Đất đang ngày càng ô nhiễm, phải thay đổi thói quen"*).

**B. `life` lên trước `energy`** — chọn
Thứ tự mới: `scan · timeline · sun · life · energy · eco · core`.
Mạch: có gì → từ đâu tới → vì sao mỗi nơi mỗi khác → **sự sống ở đâu** → **đang bị đe
doạ** → **mình làm được gì** → chốt. Cặp "vấn đề → hành động" đứng liền nhau.

**C. Bỏ hẳn bước `life`** — bác
Nó là khuôn tương tác **thứ sáu** của nhiệm vụ (`006`), là bước duy nhất khẳng định toạ
độ thật, và mang 4 mẫu codex + 4 Thẻ Thu Thập. Bỏ là mất một phần ba nội dung để chữa
một lỗi thứ tự.

### 2. Màn warp giật

**A. Làm khung vẽ rẻ hơn** (ít sao · gộp lời `stroke` · hạ độ phân giải canvas) — bác
Số đo cho thấy vòng vẽ không *chạy chậm*, nó **không được chạy**. Một khối main thread
dài 2.879 ms thì khung vẽ tốn 0 ms cũng vẫn đứng cứng 2,9 giây.

**B. Bỏ màn warp / chờ cảnh 3D xong mới hiện** — bác
Màn warp tồn tại **đúng để che** quãng dựng cảnh đó. Bỏ nó là trẻ ngồi nhìn màn hình
trống trong cùng khoảng thời gian ấy.

**C. Chia nhỏ việc dựng cảnh three.js, nhường main thread từng nhịp** — bác
Phần đắt nhất là **biên dịch shader** của `EffectComposer`/`UnrealBloomPass`, không chia
nhỏ được. Và nó nằm trong 2.600 dòng của `explorer.html`, tức rủi ro sửa cao mà không
chắc chữa được.

**D. Vẽ vệt sao trong Web Worker + `OffscreenCanvas`** — chọn
Worker có luồng riêng nên khối 2.879 ms của main thread không chạm tới nó. Giữ **đúng**
hình ảnh chủ dự án đã chấp nhận (420 vệt sao toả từ tâm + ba dòng chữ).

### 3. Ba lỗi còn sót phát hiện trong cùng lượt (không có phương án nào để cân nhắc — đều là rác)

**Đĩa Mặt Trời `.e2-sun`** — quyết định bỏ nó đã chốt **02/08/2026** (bước ③ không còn
chạm Mặt Trời; lời thoại đã viết lại để nói rõ Mặt Trời không nằm trên tấm bản đồ; chính
chú thích phép kiểm đó ghi *"sau khi bỏ nút `.e2-sun`"*) — chỉ có **thẻ DOM là chưa ai
xoá**. Không phải quyết định mới, là việc chưa làm xong.

**Bàn tay đi theo thứ tự khai báo** — đổi sang **đốm gần nhất với đốm vừa chạm**. Đây là
lựa chọn duy nhất thoả cả hai luật: giữ được "chạm đốm nào trước cũng được" (`004`) mà
bàn tay vẫn chắc chắn dời chỗ sau mỗi cú chạm.

**Thẻ nội dung chồng lên bảng đáy** — dùng lại **đúng cơ chế `--board-h` + `.lift`** mà
`boardSay()` đã dùng cho box thoại, không dựng cơ chế thứ hai cho cùng một bài toán
(thứ neo giữa vs thứ neo đáy).

## Đã chọn

**B (thứ tự bước)** và **D (worker cho vệt sao)**, cộng ba việc dọn ở mục 3.

## Đã bác — và vì sao

- **Giữ thứ tự `energy → life → eco`** — câu mở của `eco` nối trực tiếp vào `energy`
  ("đổi được ba nhà máy thôi thì chưa đủ"), nên `life` nằm giữa là **cắt một câu làm
  hai bằng một bài học khác**. Đây là bằng chứng đọc được trong lời thoại, không phải
  cảm giác.
- **Bỏ bước `life`** — nó là khuôn thứ sáu (`006`), bước duy nhất khẳng định toạ độ
  thật, mang 4 mẫu codex.
- **Đổi *id* bước thay vì đổi *thứ tự*** — id là khoá `missions.earth.<id>` trong
  DynamoDB; đổi id là người chơi cũ mất tiến độ. Đổi thứ tự thì không, vì `GateMet` và
  `AllStepsDone` đếm theo **tập hợp**.
- **Chữa cái giật bằng cách tối ưu khung vẽ** — vòng vẽ không được chạy, không phải
  chạy chậm. Đo được ở dưới.
- **Bỏ / hoãn màn warp** — nó tồn tại đúng để che quãng dựng cảnh.
- **Dựng lại vành khí quyển hình tròn cho bản đồ phẳng** — cùng lỗi với
  `.e2-terminator` (`005` mục 2): hình đúng trên quả cầu, mang sang bản đồ phẳng thì
  đọc ra thành một đường tròn lơ lửng giữa châu Phi.
- **`min-height` gõ tay để bảng mốc thời gian bằng cỡ nhau** — số dòng của cùng một câu
  đổi theo bề rộng khung (390px vs 1440px) và theo ngôn ngữ, nên mọi giá trị cố định đều
  sai ở một khổ máy nào đó.
- **`#time-ok{display:block;margin:auto}` để căn giữa nút** — `display` của tác giả
  **thắng** `display:none` mà trình duyệt áp cho `[hidden]`, nút sẽ hiện ngay từ mốc thứ
  nhất, tức trẻ chốt được bước ② khi mới xem 1/5 mốc.
- **Đặt lại `loading="lazy"` cho ảnh mốc** — thẻ đó luôn nằm trong khung nhìn khi bảng
  hiện, nên `lazy` không tiết kiệm gì; nó chỉ làm lượt tải **bắt đầu muộn hơn**.
- **Giữ đĩa Mặt Trời `.e2-sun` "cho có hình ảnh Mặt Trời"** — trên bản đồ phẳng phủ kín
  khung thì mọi pixel đều là bề mặt Trái Đất, nên một đĩa sáng đặt lên đó nói rằng Mặt
  Trời nằm TRÊN mặt đất. Chủ dự án đã bác đúng câu này từ 02/08: *"trẻ hiểu rằng mặt trời
  nằm trên trái đất. Vẫn vô lý"*.
- **Bỏ luôn `igniteSun`/`dimSun` cùng với đĩa Mặt Trời** — bài học của bước ③ nằm ở
  `.e2-night` (cả bản đồ tối đi rồi sáng lại), không ở cái đĩa. Bỏ theo là bỏ mất bài học.
- **Chỉ nâng `z-index` cho thẻ nội dung mà không dời chỗ nó** — nâng z-index một mình chỉ
  đổi "ai che ai"; hai hộp vẫn chồng nhau và vẫn đọc ra như lỗi bố cục.
- **Ẩn bảng mục tiêu (`display:none`) trong lúc thẻ mở** — nó biến mất rồi hiện lại sau mỗi
  thẻ là một cú nháy ở đúng chỗ trẻ đang đọc. Chỉ làm mờ (`opacity:.3`).

## Số liệu đã kiểm bằng mã nguồn

**Màn warp — nguyên nhân** (`scratchpad/probe_warp_longtask.py`, `PerformanceObserver('longtask')`
trên `explorer.html?onboard=1`):

| | màn warp sống | long task chồng lên | khối dài nhất |
|---|---|---|---|
| máy thường | 2.142 ms | **1.908 ms (89%)** | 788 ms |
| CPU chậm ×4 | 3.788 ms | **3.687 ms (97%)** | **2.879 ms** |

Nguồn của các khối: 13 module three.js tải từ `unpkg.com` (165–385 ms) rồi dựng cảnh
(texture + biên dịch shader `EffectComposer`/`UnrealBloomPass`).

**Màn warp — sau khi sửa** (`scratchpad/probe_warp_frames.py`, `Page.startScreencast`,
A/B trên **cùng một mã nguồn** bằng cách `route` chặn file worker, CPU ×4):

| | khung MỚI / giây | quãng hình đứng cứng dài nhất |
|---|---|---|
| worker BẬT | **48,0** | **699 ms** |
| worker CHẶN (đường lùi main thread) | 11,3 | **4.013 ms** |

**Bảng mốc thời gian** (`probe_era_panel.py`, đo `#time` ở cả 5 mốc):

| khổ máy | chênh chiều cao bảng giữa 5 mốc — TRƯỚC | SAU (mốc ①–④) | nút mốc ⑤ lệch tâm |
|---|---|---|---|
| 1440×900 vi | lệch theo độ dài chữ | **0 px** (bodyH 438) | **0 px** |
| 1440×900 en | lệch theo độ dài chữ | **0 px** (bodyH 438) | **0 px** |
| 390×844 vi | lệch theo độ dài chữ | **0 px** (bodyH 374) | **0 px** |

Mốc ⑤ cao hơn ①–④ đúng **60 px** = nút 48 px + `margin-top` 12 px. **Cố ý**: chủ dự án
đã nói rõ nút *"chỉ xuất hiện tại mốc cuối"*, và giữ 60 px trống ở 4 mốc đầu sẽ lấy mất
chỗ của bản đồ (1366×768 hiện còn 214 px bản đồ).

Đo ngay **30 ms** sau cú bấm ở cả 5 mốc: `.era-wait` = `False` và `currentSrc` đúng file
của mốc vừa bấm → nhờ `preloadEra` thì ảnh đã nằm trong cache, **0 khung hình** nào lộ
tranh của mốc trước.

**Màng khí quyển** (chụp cùng khung, bật/tắt màng): độ sáng TB toàn ảnh
**81,0 → 90,5 (+9,6 điểm)**, **giữa khung +0,0 điểm**. So với **−29,6 điểm** mà lớp phủ
tối của `005` mục 2 đã ăn: **ngược dấu** — màng này làm sáng, không làm tối, và không
đụng tới phần bản đồ trẻ đang đọc.

**Đĩa Mặt Trời:** thẻ `.e2-sun` biến mất khỏi DOM (`querySelector` → null),
`screenOf('sun')` → `null` thay vì ném lỗi, trang 0 lỗi console.

**Bàn tay** (trẻ chạm từ GIỮA ra: `europe → africa → asia → oceania → antarctica → samerica`):

| | TRƯỚC | SAU |
|---|---|---|
| 1900×940 | tay đứng nguyên `(340,233)` chỉ vào `namerica` suốt **5 cú chạm liền** | **6/6 cú chạm tay đều đổi chỗ**, lệch khỏi đốm 7px (đúng offset thiết kế) |
| 390×844 | (cùng lỗi) | **6/6 đổi chỗ**, lệch 7px |

**Thẻ nội dung ↔ bảng đáy** (bước ④ `life`, bảng cao nhất cả nhiệm vụ):

| khổ máy | chồng lấn | nút "Đã hiểu!" trong khung | nút nhận cú bấm |
|---|---|---|---|
| 1440×900 | **0 px²** | có | có |
| 690×737 *(đúng khổ ảnh chủ dự án gửi)* | **0 px²** | có | có |
| 390×844 | **0 px²** | có | có |

Bước ① (không có bảng nào mở) → `.lift` **không** bật, thẻ vẫn về giữa khung như cũ.

**Bộ kiểm thử sau khi sửa:** `check_pages.py` **644/0** (thêm mục **[3g]** 18 phép kiểm
cho ba lỗi này) · `smoke_map_onboard.py` **68/0** · `smoke_lang_switch.py` **181/0**.
Lượt trước cùng ngày: `check_pages.py` **626/0** · `smoke_mission_earth.py`
**226/0** · `smoke_map_onboard.py` **68/0** · `smoke_lang_switch.py` **181/0** ·
`smoke_map_warp.py` **27/0** · `smoke_route_gate.py` **47/0** ·
`smoke_earth_done.py` **33/0** · `smoke_missions.py` **74/0**.

## Hệ quả

- **Thứ tự bước phải đổi ở BA chỗ cùng lúc:** `Missions.All` (`AstroqSV/…/Services/Missions.cs`)
  · `STEP_IDS` (`mission-earth.html`) · thứ tự chơi trong `scratchpad/smoke_mission_earth.py`.
  `check_pages.py` [3c] so hai chỗ đầu theo **đúng thứ tự**.
- **Dời `life` trở lại giữa `energy` và `eco` thì phải viết lại `ec_say1` trước.** Câu
  đó nối trực tiếp vào `energy`; để nguyên là tạo lại đúng lỗi này.
- **`s4_say1` đã viết lại**: bỏ *"Trái Đất sạch hơn rồi!"* (nói về việc trẻ chưa làm ở
  thứ tự mới) → nay nối từ ba vùng khí hậu của bước ③.
- **Từ nay `explorer.html` KHÔNG được gọi `getContext('2d')` trên `#nm-warp-cv`.**
  Quyền vẽ đã chuyển sang worker (`transferControlToOffscreen`, cú **một chiều**). Phải
  hỏi cờ `wTransferred` — hỏi `wWorkerOn` là ném `InvalidStateError` ở đúng lượt warp
  đầu tiên (lúc đó worker chưa kịp `ready`).
- **Đường lùi main thread phải còn nguyên** (`startWarpMain()`): chạy trang bằng
  `file://` là `new Worker` ném lỗi ngay. `onerror` thay hẳn thẻ `<canvas>` bằng thẻ mới
  rồi chạy bản cũ.
- **`smoke_map_onboard.py` không đọc pixel canvas bằng JS được nữa** — đã đổi sang ảnh
  chụp, và nhân đó thêm một phép kiểm **mạnh hơn**: hai ảnh cách 120 ms phải KHÁC nhau.
  Bản cũ chỉ chứng minh canvas có gì đó sáng, không chứng minh nó **đang chạy** — mà cái
  giật vừa sửa chính là "có hình mà không chạy".
- **Việc còn treo của `004` mục ③ (`.e2-shield` phủ toàn bản đồ) coi như XONG.**
- **Xoá một biến thì `grep` tên nó, đừng chỉ xoá chỗ khai báo.** Bỏ `var sun` để lại
  `sun.addEventListener` (chạy NGAY lúc dựng cảnh → **giết cả trang**, `window.__mission`
  không bao giờ tồn tại) và nhánh `screenOf('sun')`. Đúng vết đã ghi sẵn trong chính file
  đó cho nhánh `"sat"`: *"một `ReferenceError` nằm chờ đúng người gọi đầu tiên"*.
- **Đo thứ tự hai câu lệnh thì phải giới hạn phạm vi đúng bằng hàm chứa chúng.** Phép kiểm
  `index("liftCard();") < index("classList.add('show')")` chạy trên cả file thì hỏng oan —
  `classList.add('show')` có ở hàng chục chỗ khác.
- ⚠️ **MỘT PHÉP KIỂM CŨ ĐÃ PHẢI ĐỔI PHÁT BIỂU, và nó mạnh lên nhờ thế.**
  `smoke_mission_earth` mục [10] từng lấy `_left[0]` — châu lục chưa chạm đầu tiên **theo
  thứ tự khai báo** — rồi đòi nó luôn trong khung. Điều đó chỉ đúng khi cú lướt bản đồ
  cũng đi theo thứ tự khai báo; sau khi `nextLeft()` đổi sang "đốm gần nhất", `_left[0]`
  và đích thật của cú lướt không còn là một, nên **phép kiểm cũ báo hỏng đúng lúc sản phẩm
  làm đúng** (đo được: 1 hỏng / 227 đạt, đúng phép kiểm đó).
  Điều phải bảo vệ vẫn nguyên — *trẻ không bao giờ kẹt* — nhưng **phát biểu đúng của nó**
  là *"đốm mà BÀN TAY đang chỉ vào luôn bấm được"*, không phải *"đốm thứ n trong mảng luôn
  trong khung"*: trên màn dọc trẻ **chỉ bấm được thứ nó nhìn thấy**, và bàn tay chính là
  thứ nói cho nó bấm vào đâu. Bản mới lái vòng lặp bằng `handTarget` và thêm một phép kiểm
  thứ hai (*"luôn CÓ bàn tay khi còn đốm chưa chạm"*) — tức nó kiểm **cả bàn tay**, thứ
  bản cũ không hỏi tới. Cùng loại việc đã làm ở `005` (sáu phép kiểm của bước ① đảo chiều)
  và ở chính lượt này với `warp_pixels`.
- **Từ nay thêm marker mới vào `CONTINENTS`/`ZONES` thì KHÔNG cần nghĩ về thứ tự khai
  báo** — bàn tay và cú lướt đi theo khoảng cách, không theo vị trí trong mảng.
