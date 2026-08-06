# Claude đối chiếu mã nguồn — Đề xuất "Tổng quát hoá hệ thống Activities"

**Ngày rà:** 2026-08-04 · **Đầu vào:** đề xuất của ChatGPT ngày 2026-08-03
**Vai:** đối chiếu mã nguồn · ước lượng chi phí · chỉ chỗ giả định sai (`docs/PHAN-VAI.md`)

---

## Kết luận ngắn

**Nguyên tắc đúng, và nó đã được chốt rồi** — `docs/decisions/002` (31/07/2026) đã quyết
đúng cái này: bộ khuôn tương tác dùng chung, nhiệm vụ chỉ còn là dữ liệu. Đề xuất không
mâu thuẫn với hướng đi; nó **lặp lại hướng đi đó ở một quy mô đã bị bác một lần**.

Ba chỗ phải sửa trước khi dùng được:

1. **Mục 7 (nội dung) là chỗ giết đề xuất.** 215 mục nội dung cho **riêng Trái Đất**,
   trong khi **toàn bộ app hiện có ~85 mục** sau nhiều tuần làm. Riêng "100 nhiệm vụ ngày"
   đã gấp gần **3 lần toàn bộ ngân hàng quiz** (35 câu) — mà quiz là thứ `PHAN-VAI.md` gọi
   là *"nút thắt lớn nhất của dự án"*.
2. **5 trong 8 nhóm hoạt động ĐÃ TỒN TẠI**, nhưng ở tầm **toàn app**, không phải per-planet.
   Nên đề xuất thật ra không phải "dựng 8 hệ thống mới" mà là **"kéo 5 khu dùng chung xuống
   thành per-planet + dựng 3 hệ thống mới"**. Phần kéo xuống là phần đắt và rủi ro nhất,
   và đề xuất không nhắc tới nó.
3. **Giả định "nội dung quản lý bằng JSON" là SAI hoàn toàn.** Đo được: **0 lời gọi `fetch`
   một file `.json` nào trong toàn bộ client.** Thư mục `learningdata/` chỉ được nhắc trong
   **chú thích**, không trang nào nạp. Mọi nội dung đang hard-code trong JS/HTML.

---

## A. Bảy giả định ở mục 3 — đối chiếu mã nguồn

| # | Giả định của ChatGPT | Thực tế trong mã | Kết |
|---|---|---|---|
| 1 | "Mỗi hành tinh đều có một màn hình riêng" | **KHÔNG.** Chỉ có `mission-earth.html`. `explorer.html` là **một** màn 3D dùng chung cho **22 điểm đến** (8 hành tinh + Mặt Trời + Mặt Trăng + 12 mục vùng lân cận), mỗi điểm đến là một bảng thông tin trong cùng trang | ❌ **Sai** |
| 2 | "Các hành tinh sẽ tiếp tục được bổ sung" | Đúng về ý định, nhưng lộ trình đã chốt hẹp hơn: `Missions.Route = ["earth", "moon"]` — **2 điểm đến**, và Mặt Trăng chưa có nhiệm vụ | ⚠️ **Đúng một nửa** |
| 3 | "Hệ nhiệm vụ hiện tại có thể mở rộng thêm nhiều loại hoạt động" | Trình điều phối **có thật** (`js/mission-engine.js`, 176 dòng) nhưng nó chỉ biết **một** hình dạng: *một nhiệm vụ = một dãy bước tuyến tính, mỗi bước tính một lần*. Nó không có khái niệm nhóm hoạt động, không có nhiệm vụ lặp lại, không có nhiệm vụ theo ngày | ⚠️ **Đúng một nửa** |
| 4 | "Phần lớn gameplay tái sử dụng được giữa các hành tinh" | **Chưa chứng minh được, và hiện đang ngược lại.** `002` chốt 5 khuôn từ 31/07; tới nay **1/5 khuôn đã thật sự tách ra file dùng chung** (`js/pick-place.js`, 243 dòng). `buildAsk()`, `buildXsec()`, mã marker vẫn nằm **trong** `mission-earth.html` | ❌ **Chưa đúng** |
| 5 | "Nội dung quản lý bằng JSON / dữ liệu cấu hình thay vì hard-code" | **SAI.** `grep` cả client: **0** lời gọi nạp file `.json`. `mission-earth.html` chứa **408 khoá i18n** và toàn bộ dữ liệu bước viết thẳng trong file. `learningdata/astronomy/earth_codex.json` **chưa từng được trang nào đọc** | ❌ **Sai** |
| 6 | "Giao diện hiện tại hiển thị được nhiều nhóm hoạt động trong một màn hình" | Đúng — `dashboard.html` đã là lưới 6 card `MOD-nn`, `missions.html`/`games.html` đã là lưới thẻ dựng bằng dữ liệu. **Đây là giả định đúng nhất trong bảy cái** | ✅ **Đúng** |
| 7 | "Không cần gameplay mới cho từng hành tinh" | Đúng về nguyên tắc, **nhưng va vào một luật đã có**: `docs/decisions/006` — *một nhiệm vụ không dùng cùng một khuôn quá **2 lần***, đếm được bằng `grep` và **đã bác hai vòng đề xuất trước**. 8 nhóm hoạt động × 5 khuôn (1 khuôn hiện **0 người dùng**) là không đủ chỗ | ⚠️ **Đúng nhưng thiếu ràng buộc** |

---

## B. Sáu câu "tôi KHÔNG chắc" ở mục 8 — trả lời bằng mã nguồn

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Đã có abstraction cho Mission chưa? | **Có một nửa.** `js/mission-engine.js` (176 dòng) lo: vào bước · chốt bước · báo server · sang bước kế · vẽ dãy chấm. Nhưng **nội dung** thì chưa: `mission-earth.html` vẫn **2.771 dòng**. Nghĩa là *khung* đã dùng lại được, *thân* thì chưa |
| 2 | Backend lưu tiến độ theo Mission hay theo Step? | **Theo STEP.** Bản ghi `missions.<missionId>.<stepId>` trong DynamoDB, ghi có điều kiện nên **mỗi bước chỉ tính một lần vĩnh viễn**. ⚠️ Đây là điều quan trọng nhất cho đề xuất: **cấu trúc hiện tại KHÔNG diễn đạt được "nhiệm vụ ngày"** — một việc làm lại được mỗi ngày thì mô hình "tính một lần" từ chối nó tận gốc, không phải sửa nội dung mà là **thêm một hình dạng dữ liệu mới** |
| 3 | Mỗi hành tinh có route riêng hay dùng chung template? | **Không có cái nào.** Có đúng **một** trang nhiệm vụ (`mission-earth.html`) và **một** trang bản đồ dùng chung cho mọi điểm đến. Chưa có template nào để nhân bản |
| 4 | Dữ liệu hard-code hay đọc từ JSON? | **Hard-code 100%.** Xem giả định #5 ở trên |
| 5 | Thêm nhiều loại Activity có ảnh hưởng cấu trúc hiện tại không? | **Có, ở ba chỗ.** ① `Missions.Mission` là record `(Id, Planet, Steps[], DoneMeteors, DoneXp, Unlocks)` — không có chỗ cho "nhóm hoạt động"; ② **cổng lộ trình** đếm `số bước đã xong ≥ ceil(tổng bước × 0,70)`, thêm loại hoạt động khác vào cùng nhiệm vụ là **đổi mẫu số của cổng**; ③ 22 huy hiệu và 21 mẫu vật mở khoá bằng **bộ đếm toàn app** (`quizCorrect`, `lessonsRead`, `planets`…), không phải bộ đếm theo hành tinh |
| 6 | UI đã có component dùng chung giữa các hành tinh chưa? | **Có, và nhiều hơn ChatGPT tưởng:** `css/common.css` · `css/page-shell.css` (khung trang nội dung) · `css/game-shell.css` (khung mini-game) · `css/mascot.css` (box thoại Comet/Byte) · `js/ui-common.js` · `js/icons.js` · `js/mission-engine.js` · `js/pick-place.js`. Phần **thiếu** không phải component chung, mà là **một trang mẫu cho hành tinh** |

---

## C. Ba phát hiện đề xuất bỏ qua

### 1. 5/8 nhóm hoạt động ĐÃ TỒN TẠI — nhưng ở tầm toàn app

| Nhóm ChatGPT đề xuất | Hiện có gì | Ở tầm nào |
|---|---|---|
| Main Missions | `missions.html` + `mission-earth.html` | **Theo hành tinh** ✅ |
| Knowledge (Tri thức) | `learn.html` · `library.html` (8 bài) · `codex.html` (15 thuật ngữ) | Toàn app |
| Training (Huấn luyện) | `games.html` + 3 mini-game | Toàn app |
| Collections (Bộ sưu tập) | `specimen-vault.html` (21 mẫu) + `achievements.html` (22 huy hiệu) | Toàn app |
| Research Lab | Card **MOD-05** ở dashboard, **chưa có trang** | — |
| Side Missions | **chưa có** | — |
| Daily Missions | **chưa có** | — |
| Events | **chưa có** | — |

⇒ Đề xuất thật sự gồm **hai việc rất khác nhau về giá**:
- **(a)** Kéo 3 khu đang dùng chung (Tri thức · Huấn luyện · Bộ sưu tập) xuống thành per-planet
  — đây là **tái cấu trúc điều hướng**, đụng vào điều kiện mở khoá của 22 huy hiệu + 21 mẫu vật,
  và đụng `docs/decisions/003` (luồng onboarding + cổng lộ trình).
- **(b)** Dựng 3 hệ thống mới (Side · Daily · Events).

Gộp hai việc vào một đề xuất làm cả hai trông rẻ hơn thực tế.

### 2. "Nhiệm vụ ngày" là việc BACKEND, không phải việc nội dung

`grep` toàn bộ `AstroqSV/`: **không có khái niệm ngày, không có bảng sự kiện, không có
đường phát hành nội dung theo mùa.** Mọi `DateTime.UtcNow` trong mã chỉ dùng làm **dấu thời
gian** (`joinedAt`, `earnedAt`, TTL của bản ghi tạm), chưa chỗ nào dùng làm **ranh giới ngày**.

Muốn có Daily Mission thì phải thêm, tối thiểu: múi giờ để cắt ngày (trẻ Việt Nam chơi 23h
đêm) · luật chọn nhiệm vụ của ngày (server chọn, không thì client tự chọn = tự thưởng) ·
bản ghi `DAILY#<uid>#<ngày>` có TTL · và **đảo hình dạng dữ liệu** từ "mỗi bước tính một lần
vĩnh viễn" sang "tính một lần mỗi ngày".

`docs/decisions/001` đã xếp Daily/Event **xuống cuối cùng**, kèm lý do: *"chỉ có ý nghĩa khi
đã đủ nội dung để đáng quay lại"*. Đề xuất này đưa chúng lên phiên bản đầu.

### 3. Ngân sách khuôn đã bác hai vòng đề xuất trước

`docs/decisions/006`: **một nhiệm vụ không dùng cùng một khuôn quá 2 lần**, và luật này
đếm được bằng `grep` trên mã thật. Hiện trạng ở Trái Đất: `dragDrop(` **2/2 đã đầy** ·
`buildAsk(` **2/2 đã đầy** · `signal_scan` từng lên **3/2** và đó là lý do bước ⑤ phải
đổi hẳn cơ chế.

Bộ khuôn có 5 tên, nhưng đếm thật: **1 đã tách thành file dùng chung**, 3 còn nằm trong
`mission-earth.html`, 1 (`orientation_align`) **chưa từng được cài đặt và hiện 0 người dùng**.
8 nhóm hoạt động × mỗi nhóm cần một cảm giác chơi khác nhau ⇒ đâm thẳng vào luật này ngay
ở hành tinh đầu tiên.

---

## D. Mục 7 — con số nội dung, đối chiếu với thứ đang có

| Loại | ChatGPT đề xuất (riêng Trái Đất) | Toàn app hiện có |
|---|---|---|
| Nhiệm vụ chính | 8 | **7 bước** (Trái Đất) |
| Nhiệm vụ phụ | 30 | 0 |
| Nhiệm vụ ngày | **100** | 0 |
| Sự kiện | 8 | 0 |
| Module nghiên cứu | 4 | 0 |
| Bài tri thức | 20 | **12** (8 library + 4 learn, có trùng chủ đề) |
| Bài huấn luyện | 15 | **3** mini-game |
| Mục sưu tập | 30 | **21** mẫu vật |
| *(kèm theo)* ngân hàng quiz | — | **35 câu** |
| **Tổng** | **215 mục** | **~85 mục, cho CẢ app** |

Và đó mới là hành tinh **thứ nhất**. Câu *"các hành tinh khác chỉ cần thay nội dung"* đúng
về mã nguồn nhưng **đảo ngược vấn đề**: thay nội dung *chính là* toàn bộ chi phí. Với 9 điểm
đến, con số này là **~1.900 mục**.

⚠️ Và mỗi mục có **giá ẩn** mà đề xuất không tính: dự án song ngữ `{vi, en}` bắt buộc, mọi
số liệu khoa học phải có **URL nguồn đã kiểm trả 200**, mọi khoá i18n phải có ở **cả hai**
từ điển. Một "nhiệm vụ ngày" không phải một dòng — nó là tên VI + EN, mô tả VI + EN, lời
Comet VI + EN, và nếu có dữ kiện thì kèm nguồn.

---

## E. Ước lượng

*[Suy luận]* — dựa trên quy mô mã hiện có, **không phải** trên tốc độ làm việc thực tế.

Chi phí mỗi bước nhiệm vụ **đo lại hôm nay**: `mission-earth.html` 2.771 + `js/earth2d.js` 615
= 3.386 dòng cho **7 bước** ⇒ **~484 dòng/bước**. (Con số ghi ở `001` là ~410 dòng/bước — file
đã **phình thêm**, không co lại, vì bộ khuôn chưa được rút ra.)

| Việc | Quy mô | Ghi chú |
|---|---|---|
| Rút 4 khuôn còn lại ra file dùng chung | **Vừa** | Việc đã chốt ở `002` từ 31/07, chưa làm; mọi thứ khác chờ nó |
| Chuyển 7 bước Trái Đất sang dữ liệu | **Vừa–lớn**, rủi ro hồi quy | Có `smoke_mission_earth` 226/226 đỡ lưng |
| Trang mẫu cho một hành tinh (nạp dữ liệu, không viết tay) | **Vừa** | Chưa tồn tại; đây là thứ đề xuất tưởng đã có |
| Đường nạp nội dung từ JSON | **Nhỏ–vừa** | Hiện là **0**; cần cả cách phát hành + version |
| Side Missions | **Nhỏ** (mã) | Cùng hình dạng "tính một lần" như bước hiện tại |
| **Daily Missions** | **Lớn** | Backend: múi giờ · luật chọn · bản ghi theo ngày · đảo hình dạng dữ liệu |
| **Events** | **Lớn** | Cần đường phát hành nội dung theo mùa; site là **tĩnh trên GitHub Pages**, "ra sự kiện" hiện tại = một cú `git push` |
| Research Lab | **Vừa** | Chưa có trang, chưa có concept — `PHAN-VAI.md` giao concept cho ChatGPT (Lane A) |
| Kéo Tri thức/Huấn luyện/Sưu tập xuống per-planet | **Lớn**, rủi ro cao | Đụng điều kiện mở khoá của 22 huy hiệu + 21 mẫu vật + `decisions/003` |

---

## F. Mục 9 (phương án nhỏ hơn) — vẫn còn quá lớn

ChatGPT đề nghị cắt xuống: 2 hành tinh × 4 nhóm (Main · Daily · Events · Research).
**Nhưng nó giữ lại đúng hai nhóm đắt nhất** (Daily + Events) và bỏ đi hai nhóm rẻ nhất.

Phương án nhỏ hơn nên là:

1. **Rút nốt 4 khuôn ra file dùng chung** — việc đã chốt ở `002`, đang chặn mọi thứ khác.
2. **Chuyển 7 bước Trái Đất sang dữ liệu.** Đây là phép thử: bộ khuôn có đủ dùng không.
   Nếu Trái Đất không diễn đạt lại được thì mọi con số ở mục 7 là vô nghĩa.
3. **Làm đầy Mặt Trăng bằng bộ khuôn đó** — rồi **ĐO** một điểm đến tốn bao nhiêu thật.
   `001` đã ghi: *"đừng chốt tỉ lệ trước khi có số đó"*.
4. Giữ Tri thức · Huấn luyện · Sưu tập **ở tầm toàn app** cho tới khi có lý do đo được để
   tách. Chúng đang chạy tốt và đang là nơi 22 huy hiệu móc vào.
5. Daily · Events: **sau cùng**, đúng thứ tự `001` đã xếp.

---

## G. Điểm tốt của đề xuất

- **Đúng lane** (`PHAN-VAI.md`): không khẳng định dữ kiện khoa học nào, không tự ước lượng
  công sức thực hiện — đúng hai điều Lane A bị cấm.
- **Mục 8 khai thật.** Cả sáu câu "tôi không chắc" đều là câu đúng chỗ, và chính chúng dẫn
  tới ba phát hiện ở mục C. Một đề xuất giả vờ biết sẽ không tạo ra được điều đó.
- **Mục 6 (ảnh hưởng người chơi cũ) nêu đúng rủi ro migrate** — và tin tốt: id bước là khoá
  DynamoDB, nên **thêm** loại hoạt động mới thì an toàn, chỉ **đổi id** mới phá dữ liệu.
- Nhận định gốc — *"mỗi hành tinh xây logic riêng thì phát sinh mã lặp"* — **đúng, và đã
  được chứng minh bằng số**: 484 dòng/bước, 1/5 khuôn được rút ra sau 4 ngày.

---

## H. Việc tiếp theo — đề bài vòng sau cho ChatGPT

Nếu chốt đi tiếp hướng này, đề bài vòng sau nên nói thẳng những con số dưới đây (nó không
đọc được mã, nên mọi thứ không nói ra là nó sẽ đoán):

1. **KHÔNG có route riêng cho hành tinh, KHÔNG có nạp JSON, KHÔNG có khái niệm ngày ở server.**
   Ba thứ này đề xuất giả định là đã có.
2. **5/8 nhóm đã tồn tại ở tầm toàn app** — hỏi thẳng: có lý do nào đủ mạnh để kéo chúng
   xuống per-planet không? Nếu không, bộ khuôn chỉ cần phục vụ **Main + Side**.
3. **Ngân sách khuôn ≤ 2 lần/nhiệm vụ** (`006`) và **hiện có 4 khuôn dùng được**. Hỏi: 8 nhóm
   hoạt động thì mỗi nhóm dùng khuôn nào, và chỗ nào phải đề xuất khuôn mới?
4. **Ước lượng lại mục 7 cho ĐÚNG MỘT điểm đến là Mặt Trăng**, không phải cho cả 9 — và ghi
   rõ mỗi mục cần bao nhiêu trường (VI + EN + nguồn).
5. **Research Lab (MOD-05)** vẫn là ô trống chưa ai biết nó là gì — `PHAN-VAI.md` đã giao
   concept này cho Lane A. Đó là chỗ đề xuất này có giá trị cao nhất và ít rủi ro nhất.
