# BÀN GIAO — 02/08/2026: sửa lỗi bản đồ + bỏ bước `rotation`

> ✅ **ĐÃ TIẾP NHẬN VÀ LÀM XONG (02/08/2026).** Mục *"Việc còn treo của `005`"* ở cuối file này
> **KHÔNG CÒN ĐÚNG** — 1–7 đã làm hết. Đọc `CLAUDE.md` → *Nhật ký yêu cầu* → mục **"TẠO LẠI LUỒNG
> NHIỆM VỤ THEO `docs/decisions/005`"** để biết hiện trạng thật, và `docs/decisions/005` cho trạng
> thái từng mục. Giữ file này lại vì phần *"Ba lỗi phiên này tự gây ra rồi tự bắt"* vẫn đáng đọc.
>
> ✅ **ĐÃ DEPLOY VÀ ĐÃ PUSH (03/08/2026).** Lambda `gnb5T7uqHVesSKfn/+lzzuiWZLL4RzBlwzzhCdlwBuA=`
> (bản 8 bước) → **`xGlKDjhzwSKKl61iXSVTa0Uo2pyQllT7I/Ihh2TwY0Q=`** (7 bước), đo lại trên bản thật
> `test_missions` **101/101**. Client push cùng lượt — hai thứ ra CÙNG NHAU, đúng ràng buộc đã ghi:
> deploy backend một mình thì client 8 bước gửi `rotation` cho server không còn biết bước đó, còn
> push client một mình thì `AllStepsDone` của server đòi đủ 8 mà client chỉ gửi 7 ⇒ **nhiệm vụ không
> bao giờ hoàn thành và trẻ kẹt cứng**. Vì thế thứ tự là **Lambda trước, client ngay sau**.
>
> ⚠️ **CHỐT LẠI ĐIỂM SỐ 3 CỦA DANH SÁCH TREO ("5 hay 6 mốc"): LÀ 5 MỐC.** Căn cứ:
> `docs/decisions/005` — văn bản quyết định — liệt kê đúng 5 mốc kèm nguồn cho từng con số, và
> mục *"Đã bác"* của nó đã **bác hẳn việc thêm mốc thứ 6** ("thêm mốc làm bước ② dài nhất nhiệm
> vụ; thanh thời gian trong popup đạt cùng mục tiêu với 0 mốc thêm"). Con số 6 chỉ tồn tại trong
> **một dòng chú thích** của `Missions.cs` — đã sửa lại thành 5. Không có mã nào đọc con số đó.

**Phiên này ĐÃ DỪNG** theo yêu cầu chủ dự án, vì có **một phiên khác đang sửa cùng luồng nhiệm vụ**.
File này để phiên đó tiếp nhận.

> ⛔ **CHƯA DEPLOY. CHƯA PUSH.** Bản thật AWS và `astroq.org` **vẫn nguyên trạng 8 bước**.
> Mọi thay đổi dưới đây **chỉ nằm trên đĩa**.

## Vì sao dừng

Hệ thống báo ba file bị sửa **từ ngoài phiên này** trong lúc đang làm: `Missions.cs` ·
`js/earth2d.js` (2 lần) · `css/mission-earth.css`. Bằng chứng rõ nhất: phiên này tự tay viết
*"timeline … (**6 mốc**)"* vào chú thích `Missions.cs` (chủ dự án chốt 6 mốc), nhưng file hiện
ghi **5 mốc** và mô tả bước `sun` bằng chữ khác.

Hai việc kế tiếp là **deploy AWS** + **push GitHub Pages** — cả hai lấy **nguyên trạng trên đĩa**,
tức sẽ phát hành **trạng thái lai của hai phiên**, gồm cả phần đang làm nửa dở. Không rollback
sạch được. Nên dừng trước lệnh cập nhật.

---

## ⚠️ ĐIỀU QUAN TRỌNG NHẤT cho phiên tiếp nhận

**`Missions.cs` trên đĩa ĐÃ BỎ bước `rotation` → còn 7 bước:**

```
scan · timeline · sun · energy · life · eco · core
```

`check_pages` mục **[3c]** đòi `STEP_IDS` ở `mission-earth.html` khớp **ĐÚNG THỨ TỰ** với
`Missions.All`. Nên bất cứ ai dựng client cũng **phải dùng 7 bước**, không thì phép kiểm đỏ.

**Và server chưa deploy**, nên bản thật AWS vẫn là 8 bước. Hai bên lệch nhau cho tới khi deploy.

---

## Thay đổi trên đĩa, theo file

### A. Sửa lỗi bản đồ không phủ kín khung *(việc RIÊNG, không dính bỏ bước — nên giữ)*

Lỗi chủ dự án gặp khi chơi thật: bản đồ chỉ phủ tới x≈1243 trên khung ~1900px, bên phải đen thuần.

| File | Thay đổi |
|---|---|
`js/earth2d.js` | `mkPic()` dựng **3 bản ảnh** lát theo kinh tuyến (`.e2-wrap-w/-e` ở `left:∓100%`); `setMap` cập nhật cả 3 |
`js/earth2d.js` | `maxPyPct()` + kẹp `py` trong `paint()`; `measure()` nhớ bố cục, làm mới khi `resize` |
`js/earth2d.js` | `ZOOM_MIN = 1` (trước là `0.8` gán cứng ở 2 chỗ) |
`css/mission-earth.css` | `.e2-wrap` / `.e2-wrap-w` / `.e2-wrap-e`, **chỉ hiện ở `.e2-flat`** |

**Nguyên nhân gốc:** `paint()` dịch `.e2-layer` theo `facing` tới ±50% bề rộng, nhưng lớp chỉ đủ
phủ khung **khi phép dịch = 0** — không có chỗ nào kẹp lại.

⚠️⚠️ **KHÔNG ĐƯỢC ĐỔI CỠ/TỈ LỆ `.e2-layer` ĐỂ CHỮA.** Marker định vị bằng **phần trăm của lớp
đó** (`project()` trả `x = (lon+180)/360*100`); đổi cỡ lớp là dời **toàn bộ toạ độ địa lý** — đúng
lỗi *"thẻ Amazon rơi giữa đại dương"* của bản 3D. Hai bản sao nằm **ngoài hộp** lớp, chỉ lấp mắt.

**Đo được:** `probe_map_cover.py` **203/203 đạt** (7 cỡ màn × 9 cấu hình bước + ma trận lon/dist).
**Phép thử phá hoại:** tắt hai bản sao → hở lại 450/521/985px.

### B. Bỏ bước `rotation` — 8 → 7 bước

| File | Thay đổi |
|---|---|
`AstroqSV/.../Services/Missions.cs` | xoá `new("rotation", 20, 30, "rotation")` + viết lại chú thích liệt kê bước |
`AstroqSV/.../Endpoints/MeEndpoints.cs` | `DoneSteps()` **lọc theo `Missions.Find(...).Steps`** — chữa lỗi hiện *"8/7 bước"* cho người đã xong bước cũ |
`mission-earth.html` | `STEP_IDS` 8→7 · xoá khối `steps.rotation` · xoá 12 khoá i18n `s3_*` · xoá markup `#sat` · xoá `satAngle`/`STATION` · **`codexTotal` 9 → 8** · đánh số lại chú thích bước 6→5, 7→6, 8→7 · **1784 → 1679 dòng** |
`learningdata/astronomy/earth_codex.json` | xoá entry `"rotation"`, `count` 9 → 8 |
`js/earth2d.js` | xoá `setEarthDrag` · `stationAngleTo` · `setSatelliteVisible` · `setSatelliteSignal` · `showAim` · phần tử `.e2-aim` / `.e2-sat` · cờ `earthDrag` |
`css/mission-earth.css` | xoá `.me-sat` · `.e2-aim` · `.e2-sat` · `@keyframes e2Wave` (~2,9 KB) + sửa chú thích lạc hậu |

**Đã kiểm trước khi bỏ** (`grep "mission:earth"` trong `AstroqSV/.../Services/`): **không phần
thưởng nào bị khoá vĩnh viễn** — `eco-warrior` móc `mission:earth:eco`, `ancient-lava-rock` móc
`mission:earth:timeline`, cả hai bước còn.

**Giá:** −20 tt · −30 XP → nhiệm vụ còn **235 tt · 355 XP** · cổng lộ trình 6/8 → **5/7**.

### C. Bộ kiểm thử

| File | Thay đổi |
|---|---|
`scratchpad/probe_map_cover.py` | **MỚI** — đo phủ khung, 7 cỡ màn × 9 bước |
`scratchpad/probe_globe_daynight.py` | **MỚI** — đo tương phản ngày/đêm quả cầu explorer |
`scratchpad/smoke_mission_earth.py` | mục **`[8c]` MỚI** (33 phép kiểm phủ khung) · xoá mục `[5]` + `[8b]` + helper `drag_earth_until_aligned` · bảng thưởng 235/355/8 · nội suy `STUB_CODEX_TOTAL` vào bản giả |
`scratchpad/check_pages.py` | mục [3c]: **bỏ gán cứng số bước**, suy ra từ `Missions.cs` + phép kiểm *"không còn `rotation`"* + phép kiểm **`codexTotal` khớp số entry codex** |

### D. Tài liệu

| File | Thay đổi |
|---|---|
`docs/decisions/005-bay-buoc-va-qua-cau-3d.md` | **MỚI** — thay `004`; chốt 7 bước · ngày/đêm trên quả cầu 3D · 0 vùng tối trên bản đồ phẳng · nguồn cho các mốc timeline |
`docs/decisions/004-...md` | đánh dấu **"đã thay thế bởi 005"** + hộp cảnh báo ba mục bị đảo |
`docs/decisions/002-...md` | ghi chú **`orientation_align` nay 0 người dùng** |

---

## Số đo cuối cùng của phiên này

| Bộ | Kết quả |
|---|---|
`check_pages.py` | **489 / 0** |
`probe_map_cover.py` | **203 / 0** |
`test_missions.py` *(backend ở máy, code mới)* | **101 / 0** — dữ liệu test dọn sạch, 0 bản ghi sót |
`dotnet build -c Release` | 0 warning / 0 error |
`smoke_mission_earth.py` | ⚠️ **KHÔNG CÓ KẾT QUẢ ĐÁNG TIN** — xem dưới |

⚠️ **Bộ smoke phải chạy lại từ đầu.** Lượt cuối bị dừng giữa chừng khi phát hiện chồng chéo; hai
lượt trước đó thì phiên này sửa file **giữa lúc nó đang chạy** (nó nạp file qua HTTP nên đọc bản
mới), nên kết quả lẫn hai phiên bản. **Đừng tin `scratchpad/_r_smoke_7*.txt`.**

---

## Ba lỗi phiên này tự gây ra rồi tự bắt — ghi để phiên sau không lặp

1. ⚠️ **Cú cắt khối vòng ngắm trong `earth2d.js` ăn mất dấu `}` đóng của `paint()`** →
   `Unexpected token ')'` → `AstroQEarth2D` không tồn tại → **cả cảnh không dựng**. `check_pages`
   **mù** với lỗi này (488/488 vẫn xanh) vì nó soi văn bản; chỉ bộ smoke chạy Chromium thật mới
   thấy. **Hàm cắt của tôi kiểm độ dài và nội dung nhưng không kiểm cân bằng ngoặc.**
2. ⚠️ **`codexTotal` gán cứng 9 ở `mission-earth.html`** → sau khi mất một entry codex, màn tổng
   kết ghi *"8/9 mẫu dữ liệu"*, tức nói với trẻ nó bỏ sót một mẫu **không tồn tại**, ở đúng màn
   khen thưởng. Đã thêm phép kiểm nối hai con số đó vào `check_pages`.
3. ⚠️ **Bản giả trong bộ smoke gán cứng `codexTotal: 9`** trong khi phép kiểm đối chiếu
   `STUB_CODEX_TOTAL = 8` → bộ đo **tố cáo oan sản phẩm**, và tôi đã đi sửa `mission-earth.html`
   vì tin nó. Nay bản giả nội suy từ cùng một hằng số.

Kèm hai bài học về công cụ, đều đã có trong CLAUDE.md và đều lặp lại:
- `dotnet run -c Release` **không chạy được trên Windows** — `csproj` gán
  `RuntimeIdentifier=linux-arm64` cho Release. Chạy ở máy phải `-c Debug`.
- Viết script chứa `\` qua **heredoc của shell thì dấu `\` bị ăn mất** → `SyntaxError`.
  Tạo file bằng công cụ ghi file.
- `/tmp` của Git Bash và của Python **trỏ hai chỗ khác nhau** trên Windows.

---

## Nếu phiên sau muốn deploy + push

Đã tải sẵn **gói mốc rollback** (5,5 MB) — nhưng nó nằm ở thư mục tạm, **hãy tải lại cho chắc**:

```bash
aws lambda get-function --function-name AstroqSV --query Code.Location --output text
# curl gói đó về; rollback = aws lambda update-function-code --zip-file fileb://<goi>
```

`CodeSha256` đang chạy trước khi deploy: `gnb5T7uqHVesSKfn/+lzzuiWZLL4RzBlwzzhCdlwBuA=`

⚠️ **Thứ tự bắt buộc: client xong → chạy hết bộ kiểm → deploy backend → push client.**
Deploy trước khi push thì có một khoảng bản thật hỏng một phần: trẻ chơi tới bước 5 gửi
`rotation`, server trả **`400 bad-step`**, **mất 20 tt + 30 XP và thấy "+0"**. [Suy luận] nhiệm vụ
vẫn hoàn thành được (7 bước kia vẫn xong đủ, cổng 5/7 vẫn đạt) nên không kẹt cứng.

---

## Việc còn treo của `005`, chưa ai làm

1. **Bỏ `.e2-terminator`** khỏi bản đồ phẳng (chưa làm — chỉ mới quyết trong `005`)
2. **Bước ① 7 châu lục** + đoán biển/đất
3. **Bước ② 5–6 mốc** *(⚠️ hai phiên đang ghi hai con số khác nhau — phải chốt lại)*
4. **Bước ③ vùng khí hậu** — ⚠️ **chưa có URL nguồn** cho câu giải thích **góc chiếu**.
   Tuyệt đối **không viết "vì gần Mặt Trời hơn"** — đó là quan niệm sai.
5. **Bước ⑦ `core`** đổi lời sang giọng ôn tập
6. **Nhịp 0 ở `explorer.html`** — Comet nói về khí quyển + mời xoay ngắm ngày/đêm.
   ⚠️ Vành khí quyển ở đó **to gấp ~2 lần bán kính hành tinh và trông đặc như bi thuỷ tinh** →
   phải để Comet nói rõ *"khí quyển thật mỏng hơn thế nhiều, ở đây vẽ dày lên cho em thấy được"*,
   không thì dạy sai mô hình.
7. **`perfMode`** thành khoá `localStorage` dùng chung + thông báo mạng kém
8. **6 ảnh minh hoạ bước ②** — chủ dự án tự đặt vào `img/` (kiểm 02/08: chưa có ảnh nào).
   Mốc nào không phải ngày nay thì **bắt buộc dán nhãn MINH HOẠ**.
9. **`docs/BRIEFING.md` chưa cập nhật** — cố ý: nó mô tả *hiện trạng* (còn 8 bước ở bản thật).
   Cập nhật cùng lượt deploy, không sớm hơn.
10. **Nhật ký yêu cầu trong `CLAUDE.md` chưa ghi** — cố ý: ghi khi có mã đã phát hành.

---

## Dọn dẹp phiên này đã làm

- Đã dừng tiến trình `dotnet` chạy backend ở máy (cổng 5080 đã nhả).
- ⚠️ **Máy chủ tĩnh `python -m http.server 8123` VẪN ĐANG CHẠY** trong `AstroQhtml/` — phiên
  khác dùng được luôn, hoặc tự tắt.
- `test_missions.py` đã tự dọn tài khoản Firebase tạm + bản ghi DynamoDB (đã kiểm: 0 sót).
