# 002. Bộ khuôn tương tác cho nhiệm vụ

**Trạng thái:** đã chốt
**Ngày mở:** 2026-07-31 · **Ngày chốt:** 2026-07-31
**Người quyết:** chủ dự án

## Bối cảnh

Mỗi bước nhiệm vụ hiện là một màn viết tay riêng — nhiệm vụ Trái Đất tốn ~3.300 dòng cho 8 bước
(~410 dòng/bước). Không nhân được cách đó ra 9 điểm đến. Cần một bộ khuôn tương tác dùng lại
bằng dữ liệu, đủ nhỏ để đáng đầu tư và đủ mạnh để diễn đạt lại toàn bộ nhiệm vụ Trái Đất.

Xem `docs/decisions/001-cau-truc-world-quest.md` cho câu hỏi rộng hơn (bao nhiêu bước mỗi World)
— câu đó **vẫn đang mở**, phải đo bằng World thứ hai mới trả lời được.

## Các phương án đã cân nhắc

### A. 8 khuôn — ChatGPT, vòng 1
signal_scan · profile_builder · sequence_reconstruction · expedition_loadout ·
evidence_investigation · relationship_map · mission_resource_balance · branching_field_log

### B. 4 khuôn — ChatGPT, vòng 2 (sau khi Claude đối chiếu mã)
signal_scan · sequence_reconstruction · profile_builder · evidence_investigation

Claude ánh xạ 8 bước Trái Đất vào bộ này (việc ChatGPT không làm): **6/8 khớp · `sun` cần biến
thể · `rotation` KHÔNG khớp**. `rotation` là thao tác liên tục trên vật thể 3D — kéo xoay chính
hành tinh cho trạm phát sóng thẳng hàng vệ tinh — không phải chọn, sắp thứ tự hay phân loại.

### Ba đường cho `rotation`
- **(a)** thêm khuôn thứ 5 `orientation_align`
- **(b)** để `rotation` là màn riêng ngoài hệ khuôn
- **(c)** thiết kế lại bằng khuôn đã có, chấp nhận mất khoảnh khắc tự tay xoay hành tinh

## Đã chọn

**Phương án B + (a): năm khuôn.**

| Khuôn | Bước Trái Đất phủ được |
|---|---|
| `signal_scan` | `scan` · `sun` *(biến thể: mục tiêu trong cảnh, không nằm ở lat/lon)* |
| `sequence_reconstruction` | `timeline` |
| `profile_builder` | `energy` · `life` · `eco` · `core` |
| `evidence_investigation` | *(chưa dùng ở Trái Đất — dành cho World sau)* |
| `orientation_align` | `rotation` |

Toàn bộ 8 bước Trái Đất **sẽ được chuyển** sang bộ khuôn này.

## Đã bác — và vì sao

*(Phần này để dán thẳng vào ChatGPT/Gemini ở vòng sau — chúng không nhớ những gì đã bàn.)*

- **8 khuôn.** 36 bước ÷ 8 khuôn = 4,5 lượt dùng mỗi khuôn. Chi phí dựng một khuôn lớn hơn chi
  phí viết một dòng dữ liệu rất nhiều — dựng 8 cỗ máy để chạy 36 lượt là lỗ.
- **`branching_field_log`.** Số lời thoại tăng gần cấp số nhân theo số nhánh, mà nội dung đang
  là nút thắt của dự án.
- **`mission_resource_balance`.** `successRules` với toán tử sinh ra một bộ máy luật thu nhỏ,
  trong khi **server không kiểm đáp án** nên nó không mua được sự an toàn nào.
- **`relationship_map`.** Nối dây là dạng khó làm bàn phím nhất, mà dự án **không có hạ tầng
  bàn phím nào** để dựa vào. Phần lớn giá trị của nó đã được `profile_builder` hấp thụ.
- **`expedition_loadout`.** Gộp được vào `profile_builder` (thẻ → ô), không cần engine riêng.
- **Phương án (b) — màn riêng ngoài hệ khuôn.** Mất hết hạ tầng dùng chung: focus bàn phím,
  giảm chuyển động, i18n, luồng chốt bước và trao thưởng. Đây **đúng là cách `mission-earth.html`
  phình lên 1.707 dòng**, và nó sẽ tái diễn ở mỗi World có một bước "đặc biệt". Bằng chứng nằm
  trong chính mã: bước này từng xoay camera thay vì xoay hành tinh khiến trẻ **không thể hoàn
  thành** và **treo vĩnh viễn** ở chế độ giảm chuyển động — màn một-lần là nơi lỗi loại đó sống.
- **Phương án (c) — thiết kế lại `rotation` bằng khuôn có sẵn.** Ba cái mất, đều thuộc về trải
  nghiệm: (1) mất **thanh đo liên tục duy nhất của cả nhiệm vụ** — 7 bước kia đều rời rạc
  đúng/sai, chỉ bước này cho phản hồi nóng-lạnh và **không có trạng thái thua**; (2)
  `profile_builder` từ 4/8 lên **5/8 bước**, hơn nửa nhiệm vụ cùng một cảm giác thao tác;
  (3) **đổi bản chất dạy học** — trắc nghiệm "trạm nên hướng về đâu" là *bài kiểm tra về*
  chuyển động quay, kéo tới khi bắt được tín hiệu là *trải nghiệm* nó.
- **"Chưa cần chuyển nhiệm vụ Trái Đất"** (ChatGPT nêu ở cả vòng 1 và 2). Không chuyển thì tồn
  tại song song hai hệ nhiệm vụ và bộ khuôn **không bao giờ bị thử lửa bằng nội dung thật**.
  Việc chuyển chính là phép kiểm xem bộ khuôn có đủ dùng hay không.

## Số liệu đã kiểm bằng mã nguồn (31/07/2026)

| Số liệu | Giá trị | Nguồn |
|---|---|---|
| Sổ đăng ký bước | **đã tồn tại** — `const steps = {…}` + `STEP_IDS[]` + `stepIdx` | `mission-earth.html:801` |
| Toạ độ điểm trên hành tinh | **`lat`/`lon` địa lý thật**, độc lập engine; có cờ `SCENE = 2d\|3d` | `mission-earth.html` |
| Server kiểm đáp án? | **KHÔNG.** Client chỉ gửi `{mission, step, opId}`, server tra bảng thưởng | `js/progress.js:273` · `Missions.cs` |
| Bước có phản hồi liên tục | **chỉ `rotation`** — thanh "Signal strength", dung sai 20° | `mission-earth.html:1021` |
| API xoay/ngắm | **cả hai engine đã cài đủ**: `setEarthDrag` · `stationAngleTo` · `setSatelliteVisible/Signal` | `earth3d.js:959-988` · `earth2d.js:406-430` |
| Component hội thoại Comet/Byte | **chưa có** — box thoại lặp ở **3** file *(đã sửa 31/07/2026 → `css/mascot.css`)* | `mission-earth.css` · `mission-intro.css` · `onboard-tour.css` |
| Hạ tầng bàn phím | **gần như không có** — 1 handler `keydown`, dùng để mở khoá âm thanh | `mission-earth.html:1596` |
| 8 bước Trái Đất | `scan · timeline · sun · energy · rotation · life · eco · core` | `Missions.cs` |

## Hệ quả

**Thứ tự thực hiện** — mỗi bước mở đường cho bước sau:
1. ✅ **Gom component hội thoại Comet/Byte dùng chung** → `css/mascot.css` (xong 31/07/2026).
   ⚠️ **Đính chính con số ghi ban đầu:** tôi ghi "CSS linh vật lặp ở 5 file" từ một lệnh `grep`
   bắt chữ *"byte"* — nhưng phần lớn là bắt nhầm: `codex.css` trúng câu **"0 byte ảnh"** (byte
   là đơn vị dữ liệu), còn `index.css` (`.crew-comet`) và `wiki.css` (`.corner .comet`) là hai
   component **khác hẳn**, chỉ tình cờ nhắc tên linh vật. Box thoại thật chỉ lặp ở **3 file**:
   `mission-earth.css` · `mission-intro.css` · `onboard-tour.css`. *Bài học: đếm bằng `grep`
   một từ rồi báo con số là cách nhanh nhất để ghi một con số sai vào tài liệu.*
2. ✅ **Tách trình điều phối bước** ra khỏi `mission-earth.html` → `js/mission-engine.js`
   (xong 31/07/2026). `AstroQMission.create({mission, stepIds, steps, stepsEl, …})` giữ trạng
   thái bước, chốt bước, báo server, sang bước kế, vẽ dãy chấm. Nhiệm vụ chỉ còn khai **nội
   dung** `steps` và cảnh của riêng nó.
3. ✅ **Khuôn đầu tiên + hạ tầng focus bàn phím dùng chung** → `js/pick-place.js` +
   `css/pick-place.css` (xong 31/07/2026). Chọn `profile_builder` làm khuôn đầu vì nó phủ 4/8
   bước Trái Đất **và** là ca khó nhất cho bàn phím — hạ tầng được thử đúng chỗ khó.
   Chuột và bàn phím đi qua **cùng một hàm `resolve(thẻ, ô)`**, nên không thể lệch luật.
4. **Chuyển 8 bước Trái Đất** sang dữ liệu. Có `smoke_earth_done` 33/33 đỡ lưng.
5. **Đo** — một World tốn bao lâu thật. Số này mở khoá quyết định 001.

**Ràng buộc từ nay:**
- **`orientation_align` giữ tối giản:** một mục tiêu, một dung sai, một thanh đo. Không đa trục,
  không giới hạn thời gian, không nhiều mục tiêu. Cần phức tạp hơn thì **thêm bước, đừng thêm tham số**.
- **Một nhiệm vụ không dùng cùng một khuôn quá 2 lần**, và nếu dùng 2 lần thì phải khác hẳn cách
  trình bày. `profile_builder` đang gánh 4/8 bước Trái Đất — đây là rủi ro đơn điệu có thật.
- **Không đổi id bước** (`scan`…`core`) — id là khoá trong DynamoDB, đổi là người chơi cũ mất tiến độ.
- **Phải có phép đo chứng minh bản 2D và 3D trả CÙNG một góc** cho cùng dữ liệu vào. Hai cách
  tính khác nhau (`quaternion` vs `facing.lon`); lệch nhau thì cùng một nhiệm vụ khó dễ khác nhau
  tuỳ máy của trẻ.
- **Mỗi khuôn phải có lối chơi bằng bàn phím** tương đương chuột — không phải chỉ thêm `aria-label`.
  Với `orientation_align` đây lại là khuôn dễ nhất: mũi tên xoay từng nấc, thanh đo đọc ra số,
  Byte xướng mức tín hiệu. Trẻ dùng bàn phím nhận đúng phản hồi nóng-lạnh như trẻ dùng chuột.

**Còn mở, không thuộc quyết định này:** số bước mỗi World · cổng mở khoá 70% · Daily Mission /
Event · độ tuổi mục tiêu. Xem `001`.
