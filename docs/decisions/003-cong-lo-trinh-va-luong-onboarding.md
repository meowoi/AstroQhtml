# 003. Cổng lộ trình 70% + luồng onboarding qua Bản Đồ Thiên Hà

**Trạng thái:** đã chốt
**Ngày mở:** 2026-08-01 · **Ngày chốt:** 2026-08-01
**Người quyết:** chủ dự án

## Bối cảnh

Luồng onboarding hiện tại (đo ở `dashboard.html:703-730`) đưa phi hành gia mới đi:

```
đăng ký/đăng nhập → select.html → dashboard.html
  → AstroQTour (Comet dẫn tham quan 7 bước)
  → AstroQWarp (~4,6s)
  → AstroQMissionIntro (~30s cutscene) → mission-earth.html
```

Trẻ mất khoảng một phút nghe giới thiệu **trước khi** được chạm vào bất cứ thứ gì, và
**không bao giờ thấy Hệ Mặt Trời** cho tới khi tự tìm ra thẻ MOD-03 ở dashboard. Trong khi đó
`explorer.html` — bản đồ 3D đẹp nhất của app — lại là một khu tuỳ chọn không ai dẫn tới.

Đồng thời `001` để mở câu "cổng mở khoá 70%": chưa có luật nào chặn trẻ bay tới Sao Hoả trước
khi làm gì ở Trái Đất, nên không có lộ trình nào cả.

## Các phương án đã cân nhắc

### A. Đưa Bản Đồ Thiên Hà vào đầu luồng, chỉ Trái Đất bấm được — chủ dự án (01/08/2026)

Sau đăng nhập → màn warp "ĐANG DU HÀNH TỚI · Hệ Mặt Trời" → trẻ thấy **toàn cảnh** Hệ Mặt Trời
nhưng **chỉ Trái Đất phản hồi** → Comet giới thiệu ở đáy màn hình → trẻ chạm Trái Đất → bảng
thông tin → sau ≥10s Comet hỏi "sẵn sàng chưa?" → OK → nhiệm vụ 01.

### B. Chạy nhiệm vụ TRÊN quả cầu 3D của bản đồ thiên hà — chủ dự án nêu để đánh giá

Dùng luôn Trái Đất trong `explorer.html` làm cảnh cho 8 bước nhiệm vụ, khỏi có hai Trái Đất.

### C. Đổi nội dung nhiệm vụ cho khớp cảnh 3D — chủ dự án nêu làm đường lùi cho B

Nếu B phức tạp/dễ lỗi thì thiết kế lại nội dung 8 bước cho vừa với thứ cảnh 3D làm được.

## Đã chọn

**Phương án A, và bốn quyết định kèm theo:**

| # | Quyết định |
|---|---|
| 1 | `AstroQTour` 7 bước **dời xuống sau nhiệm vụ 1** (lượt về dashboard đầu tiên) |
| 2 | `js/mission-intro.js` (~30s cutscene) **nghỉ hưu** |
| 3 | Cổng lộ trình = **70% làm tròn LÊN** = **6/8 bước** Trái Đất. Luật ở **server** |
| 4 | Cảnh bản đồ **dùng lại `explorer.html`**, không tách trang mới |

**Bản đồ = 3D (`explorer.html`, three.js). Nhiệm vụ = 2D (`mission-earth.html`, `js/earth2d.js`).**
Trái Đất ở bản đồ là **điểm đến**; Trái Đất trong nhiệm vụ là **bàn làm việc**. Hai vai khác nhau
thì để hai cảnh, nối bằng màn warp — đúng ngôn ngữ hình ảnh app đang dùng.

## Đã bác — và vì sao

*(Phần này để dán thẳng vào ChatGPT/Gemini ở vòng sau — chúng không nhớ những gì đã bàn.)*

- **Phương án B — chạy nhiệm vụ trên quả cầu 3D của bản đồ.** Bốn lý do, đều đo được:
  1. **Trái Đất ở bản đồ KHÔNG CÓ ĐỊA LÝ THẬT.** `ProceduralTextures.planet()`
     (`explorer.html:903`) sinh texture **512×256 bằng nhiễu fBm** từ hai màu. Không có lục địa.
     Mà bước `life` neo 4 thẻ mẫu vật vào lat/lon **thật** (Amazon · Himalaya · Nam Cực · Đại
     Tây Dương) — đặt chúng lên nhiễu là **lặp lại đúng lỗi dự án đã trả giá một lần** ở
     `earth3d.js` (thẻ "Rừng Amazon" rơi vào giữa đại dương → **dạy sai địa lý**).
  2. **Nhiệm vụ cần 21 hàm cảnh mà quả cầu ở bản đồ có 0/21.** Đếm trong `mission-earth.html`:
     **21 hàm `world.*` khác nhau, ~55 chỗ gọi** — `igniteSun`/`dimSun` (ranh giới ngày/đêm),
     `setSatelliteVisible`/`setSatelliteSignal`/`stationAngleTo` (bước ngắm vệ tinh), `sendDrone`,
     `shield`, `showGrid`/`fadeGrid`, `setEarthDrag`, `setMap('flat'|'globe')`, `screenOf`,
     `panTo`. Class `Body` của explorer có camera quỹ đạo + bloom + mây thủ tục, không có hàm nào
     trong số đó. "Dùng lại" ở đây nghĩa là **viết lại `earth3d.js` lần thứ hai**.
  3. **Đây là loại lỗi WebGL đã từng làm trẻ KHÔNG THỂ hoàn thành nhiệm vụ.** Bước `rotation` bản
     3D cũ: kéo xoay **camera** thay vì xoay hành tinh → góc trạm–vệ tinh không đổi → bước chỉ tự
     xong vì hành tinh tự quay, và ở `prefers-reduced-motion` thì **treo vĩnh viễn**.
  4. **Quay lại 3D là hoàn tác đợt đo của 31/07/2026.** Ghi ở `mission-earth.html:1531-1535`:
     bản 2D đạt **154/154** trên ĐÚNG bộ kiểm thử của bản 3D; đường tải đầu **308 KB → 71 KB**;
     và `unpkg.com` **biến mất khỏi luồng onboarding bắt buộc**.

- **Phương án C — đổi nội dung 8 bước.** Không cần, vì gốc vấn đề không ở nội dung mà ở việc
  chọn engine, và việc đó đã xong (2D). Thêm nữa: `Missions.cs` cảnh báo id bước là khoá trong
  DynamoDB nên **đổi là người chơi cũ mất tiến độ**; và `002` vừa chốt chuyển **cả 8 bước** sang
  bộ 5 khuôn — đổi nội dung bây giờ là đâm vào việc đang chạy.

- **Dựng animation warp mới.** Không cần: **màn trong ảnh yêu cầu chính là code đã có.**
  `#nm-warp` + `travelTo(region)` (`explorer.html:2296`) đã in đúng ba dòng
  `traveling` / tên vùng / `enterRegion` = *"ĐANG DU HÀNH TỚI / Hệ Mặt Trời / Đang tiến vào vùng"*,
  vệt sao toả từ tâm bằng 420 ngôi sao (`startWarp()`), đã song ngữ, đã tôn trọng
  `prefers-reduced-motion` (0 ngôi sao, 400ms). Việc cần làm chỉ là **cho nó chạy lúc vào trang**.

- **Tách một trang bản đồ riêng cho onboarding.** Là chép ~2.400 dòng `explorer.html`, trái
  quy tắc 2 mục 6 của `CLAUDE.md` ("thứ dùng chung thì tách ra dùng lại, không copy-paste").

- **Chặn cổng ở chỗ raycast (`_pick`).** `selectBody` có **6 đường vào**, chặn một là để hở năm:
  raycast (`:1556`) · bấm nhãn tên (`:1411`) · nút Fly to Sun (`:1505`) · danh sách hành tinh ở
  bảng trái (`:1533`) · Prev/Next `_cycle` (`:1595`) · điều hướng vùng `goTo` (`:1990`).

- **Tính cổng 70% ở client.** Client mở DevTools là sửa được, và hai nơi giữ một con số thì sớm
  muộn lệch — bên lệch sẽ là bên nói với trẻ. Cùng phân công đã dùng cho phí game, mốc huy hiệu
  và cấp độ: **server giữ luật, client giữ chữ**.

- **Bấm vào hành tinh đang khoá thì im lặng.** Trẻ chỉ tưởng mình bấm trượt. Phải nói rõ cần gì
  để mở, và cho một nút đi tới đúng chỗ làm được việc đó.

## Số liệu đã kiểm bằng mã nguồn (01/08/2026)

| Số liệu | Giá trị | Nguồn |
|---|---|---|
| Màn warp trong ảnh yêu cầu | **đã tồn tại** — `#nm-warp` + `travelTo()`, 420 vệt sao | `explorer.html:222-229` · `:2296` · `css/explorer.css:418-427` |
| Chữ trên màn warp | `traveling` = "Đang du hành tới" · `enterRegion` = "Đang tiến vào vùng" | `explorer.html:302` |
| In hoa + giãn chữ của dòng đầu | **do CSS**, không phải chữ gõ hoa | `css/explorer.css:425` |
| Đường vào `selectBody` | **6** | `explorer.html:1411 · 1505 · 1533 · 1556 · 1595 · 1990` |
| Texture hành tinh ở bản đồ | **nhiễu fBm 512×256**, không có lục địa thật | `explorer.html:903` |
| Hàm cảnh nhiệm vụ cần | **21 hàm `world.*`, ~55 chỗ gọi** | `mission-earth.html` |
| Engine nhiệm vụ hiện tại | **2D**, `js/earth2d.js`; `js/earth3d.js` đã xoá | `mission-earth.html:225 · 1531` |
| Nhãn hành tinh có móc sẵn | `#labels [data-body-id]`, `CSS2DRenderer` bám theo từng khung hình | `explorer.html:1133 · 2389` |
| Số bước Trái Đất | **8** → cổng 70% = 5,6 → **6** | `Services/Missions.cs` |
| Cờ onboarding hiện có | **3**: `tourSeen` · `intro01Seen` · `earth1Greeted` | `MeEndpoints.cs:43` |
| Lời thoại bước 7 của tour | *"hãy **khởi động động cơ** thôi!"* — sẽ vô nghĩa sau khi dời tour | `js/onboard-tour.js:120 · 132` |

## Hệ quả

**Thứ tự thực hiện** — mỗi bước mở đường cho bước sau:

1. ✅ **Cổng lộ trình ở server** → `Missions.UnlockRatio` + `UnlockGate` + `Route` +
   `UnlockedPlaces`, `GET /me/missions` trả thêm `gate` · `gateMet` · `route` · `unlockedPlaces`.
   **Đã deploy lên AWS 01/08/2026** (`CodeSha256` → `FAHD/F0qc5YEuPjOg+GRz8X2ZpWxRjiLe+6Fe4YrKBw=`),
   đo lại **359/359** trên bản thật.
2. ✅ **Cổng ở client** → trong `selectBody`, một chỗ duy nhất, + modal giải thích tử tế
   (dùng lại `#nm-modal` và khoá i18n `later` đã có; thêm `gateTitle`/`gateMsg`/`gateMsgOffline`/
   `gateGo`/`gateStart`).
3. ✅ **Chạy `#nm-warp` lúc vào trang** — buộc nhánh `traveling`, dùng lại phần VẼ
   (`startWarp`/`stopWarp`) chứ không đi qua `travelTo()`.
4. ✅ **Làm nổi Trái Đất** → class `.gate-start`/`.gate-locked` gắn vào **nhãn
   `[data-body-id]` đã có**. Kèm theo: chuyển style của nhãn từ **inline sang
   `.body-lbl`** ở `css/explorer.css` — bắt buộc, vì style inline thắng mọi class.
5. ✅ **Comet nói ở đáy explorer** → `js/map-onboard.js` + `.mo-say` dùng lại `.aq-say`
   của `css/mascot.css`. Chữ **17px** (to hơn `mission-intro` 14,5px).
6. ✅ **Mốc 10 giây + câu hỏi + nút OK** → `mission-earth.html`.
7. ✅ **Dời tour, cho cutscene nghỉ hưu, thêm cờ `map01Seen`.** Backend deploy lần hai
   (`CodeSha256` → `5rjzd18yVkY6FcLYu1nCORSJColmJz3k5OfVeyzvk1Y=`), đo lại **369/369**
   trên bản thật. Luồng mới: `select.html` → `explorer.html?onboard=1` →
   `mission-earth.html` → dashboard → **Comet chúc mừng → rồi mới tour 7 bước**.
8. ✅ **Đường lùi khi three.js không nạp được** — cảnh 3D không dựng xong trong 12s thì
   `location.replace('mission-earth.html')`. Trẻ mất màn phim, không mất nhiệm vụ.

9. ✅ **Việc mới cho `js/warp-screen.js` + `js/space-scene.js`.** Tám bước trên làm module
   này mất hết người gọi (tour không còn dẫn tới, `mission-intro` nghỉ hưu). Chủ dự án chốt
   **cho nó việc mới thay vì xoá 625 dòng đang chạy tốt**: nó là **chuyển cảnh dashboard →
   Bản Đồ Thiên Hà** (thẻ MOD-03). Chỗ khớp nhất, và chính tài liệu của module ghi ra lý do —
   *"đó là lúc con tàu thật sự rời bến"*. Trước đây bấm "Mở bản đồ" là trang nhảy khô sang
   một cảnh 3D; giờ là một cú rời bến có chủ ý.
   - ⚠️ **KHÔNG dùng cho đường vào NHIỆM VỤ.** Ở luồng onboarding trẻ đã đi qua `#nm-warp`
     của `explorer.html` rồi mới sang nhiệm vụ; chèn thêm màn Luna vào đó là **hai màn
     chuyển cảnh liên tiếp** — đúng cái quyết định này đặt ra để bỏ. Thẻ MOD-03 **không**
     nằm trên luồng onboarding (người mới đi `select` → `explorer`, không qua dashboard),
     nên ở đây không bao giờ có hai màn chồng nhau.
   - ⚠️ **Lời phủ riêng, phủ THEO TỪNG KHOÁ.** Bộ mặc định (*"Đã vào quỹ đạo Trái Đất ·
     Chuyến phiêu lưu của bạn bắt đầu từ đây"*) là lời của lượt ĐẦU TIÊN đi tới Trái Đất —
     dùng lại nguyên văn cho cú mở bản đồ là nói **sai đích** và nói **sai lần thứ mấy**.
     Phủ cả bảng thì nút *"Bỏ qua ›"* hiện ra rỗng, nên `txt()` tra khoá-theo-khoá; và `over`
     đặt lại **mỗi lượt** để lời của lượt trước không dính sang lượt sau.
   - ⚠️ **Tôn trọng mọi cách mở của trình duyệt.** Ctrl/Cmd-click (tab mới), Shift-click
     (cửa sổ mới), chuột giữa — chặn hết là lấy đi một hành vi mà người dùng **không hiểu
     vì sao mất**. Module không nạp được → để `<a href>` chạy như thường, không `preventDefault`.

**Toàn bộ quyết định này đã xong và đã push** (`f300a4e` · `772e8eb` · `b4abe6b` + lượt việc mới).

**Ràng buộc từ nay:**

- **Cổng lộ trình chỉ có MỘT nguồn sự thật: `Services/Missions.cs`.** Client không tính lại tỉ lệ,
  không gán cứng danh sách điểm đến. Có phép kiểm đối chiếu hai bên.
- **Cổng phải nằm trong `selectBody`**, không nằm ở `_pick`. Nhờ vậy đường **bàn phím** (danh sách
  hành tinh ở bảng trái vốn đã là `<button>`) tự đúng luật, không phải viết thêm.
- **Không đọc được tiến độ → KHOÁ (fail-closed), trừ điểm đến đầu tiên.** Mở hết là phá cổng;
  khoá cả Trái Đất là kẹt cứng. Kèm dải `.banner` nói rõ lý do, như `missions.html` đang làm.
- **10 giây là SÀN, không phải hạn.** Câu hỏi của Comet hiện ra *cạnh* bảng thông tin, **không
  đóng** nó; trẻ tự đóng. Dự án đã trả giá đúng chỗ này với đường về tự động 5 giây: *"trẻ đọc
  chậm hơn người lớn nhiều, một màn thưởng tự biến mất sau 5 giây là màn thưởng bị lấy đi giữa
  lúc đang đọc"*. Không đếm trong lúc camera còn đang bay tới.
- **`explorer.html` vào luồng onboarding BẮT BUỘC nên phải có đường lùi.** Nó nạp three.js +
  OrbitControls + EffectComposer + UnrealBloomPass + CSS2DRenderer từ `unpkg.com`. Cảnh 3D không
  dựng được trong ~8–12s → **đi thẳng `mission-earth.html`** (đã 2D, không cần tên miền ngoài).
  Trẻ mất màn phim, không mất nhiệm vụ.
- **Không dùng `filter:grayscale()`** để làm mờ hành tinh khoá — bài học đã ghi 3 lần: trên nền
  gradient sáng nó cho ra khối xám *sáng hơn* bình thường, tức hút mắt vào đúng cái không dùng được.
- **Mở khoá Mặt Trăng là mở một ĐIỂM ĐẾN, không phải một nhiệm vụ.** MISSION-02 chưa có trang chơi.
  Lời báo phải nói "điểm đến Mặt Trăng đã mở", **đừng** nói "nhiệm vụ Mặt Trăng đã mở" — cùng bài
  học của `js/specimens.js`: đừng hứa một nhiệm vụ chưa tồn tại.

**Ba chỗ sẽ ship sai nếu không sửa cùng lúc** *(đã phát hiện trước khi code)*:

1. ✅ **Màn warp sẽ hiện "Đang tới" thay vì "Đang du hành tới".** `explorer.html` chọn nhánh
   bằng `region.id === currentRegion.id`, mà lúc trang vừa nạp `currentRegion` **đã là**
   `REGIONS[0]` (solar-system) → rơi vào `arriving`. **Đã xử:** `gateWarpShow()` riêng, buộc
   `T('traveling')`, không đi qua `travelTo()` (hàm đó còn tự đặt `transitioning = true`,
   chặn cú du hành thật ngay sau đó).
2. **Lời thoại bước 7 của tour thành vô nghĩa.** *"hãy khởi động động cơ thôi!"* + nút *"Khởi động
   động cơ 🚀"* tồn tại vì tour **từng** dẫn vào màn warp. Dời tour xuống sau nhiệm vụ 1 thì động
   cơ đã khởi động từ lâu. Viết lại ở **cả `vi` và `en`**.
3. **`onFinish` của tour và `earthDoneGuide()` sẽ tranh nhau** — cả hai chờ ở đúng một thời điểm
   (lượt về dashboard sau nhiệm vụ). Thứ tự: **chúc mừng trước, tour sau** — trẻ vừa làm xong thì
   lời đầu tiên phải là lời khen, không phải bài giới thiệu con tàu. Nối tiếp qua callback; hai cờ
   `earth1Greeted` / `tourSeen` **ghi độc lập**.

**Quan hệ với `001`:** quyết định này **chốt con số 70%** mà `001` đang để mở, và `001` có ghi
*"Đừng chốt tỉ lệ trước khi có số đó"* (số = đo một World tốn bao lâu thật, từ bước 5 của `002`).
Chủ dự án chốt trước khi có số đó — **có ý thức**, và rủi ro nhỏ vì tỉ lệ là **một hằng số duy nhất
ở server** (`Missions.UnlockRatio`): đo xong thấy sai thì sửa một dòng, không phải migration, và
người chơi cũ tự tính lại đúng vì cổng **suy ra** từ số bước đã xong chứ không lưu thành cờ.

**Còn mở, không thuộc quyết định này:** số bước mỗi World (`001`) · Daily Mission / Event · độ tuổi
mục tiêu · có nên báo "điểm đến mới đã mở" ngay trong màn tổng kết nhiệm vụ hay không.
