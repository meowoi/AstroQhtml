# Đề xuất: Phòng Nghiên Cứu (MOD-05) — nội dung về HẤP DẪN cho trẻ 8–15

> ⚠️ **ĐÍNH CHÍNH 12/08/2026 — dải tuổi là 8–15, không phải 8–12.** Bản đầu của tài liệu này
> ghi 8–12 vì tôi lấy theo câu hỏi mở đầu; dải thật của dự án là **8–15** (`CLAUDE.md` ghi
> "trẻ 8–15" ở 3 chỗ). Sửa này **làm nhẹ hẳn** phát hiện số 3 ở *Kết luận ngắn* — xem **mục 17**.

**Người viết:** Claude · **Ngày:** 2026-08-12
**Đầu vào:** ý tưởng Phòng Nghiên Cứu của ChatGPT (`2026-08-04-chatgpt-activities-vong-2.md`,
đã được nhận về hướng) + bản đối chiếu mã của tôi cùng ngày
**Vai:** đối chiếu mã nguồn · tra nguồn · đề xuất nội dung (`docs/PHAN-VAI.md`)

---

## Kết luận ngắn

**Hướng hấp dẫn hoá ra là đường RẺ NHẤT, không phải đắt nhất — và thẻ MOD-05 đã hứa đúng nó
từ trước.** Trong bảng chi phí ngày 04/08 tôi xếp *"khối lượng → hấp dẫn"* là **Lớn**, vì
hiểu nó là mô phỏng lực/quỹ đạo. Nhưng đọc lại lời hứa đang hiện trên thẻ:

> `lab_desc` — *"Tự tay làm thí nghiệm: trộn nguyên tố, **thả rơi vật thể ở các mức trọng
> lực khác nhau**."* (và bản EN: *"drop objects under different gravity"*)

**Thả rơi ≠ mô phỏng quỹ đạo.** Rơi tự do là `s = ½gt²` — một dòng, 2D canvas, không cần
three.js, không cần bộ mô phỏng lực nào. Nên đề xuất này **không mở phạm vi mới**, nó chỉ
giao đúng thứ thẻ đã hứa.

Ba điều phải chốt trước khi code, cả ba đều là chuyện NGUỒN chứ không phải chuyện mã:

1. **Số `m/s²` trong `explorer.html` KHÔNG dẫn nguồn nào** — 10 điểm đến đều có `gravity:` mà
   cả file chỉ có **1** lần nhắc `nasa.gov`.
2. **NASA viết cho trẻ KHÔNG dùng `m/s²`** — họ dùng **tỉ lệ** và **cân nặng**. Nên Phòng
   Nghiên Cứu nên nói cùng thứ tiếng đó.
3. ~~**Hai hoạt động hấp dẫn kinh điển của NASA nhắm grades 5–9**, tức trên đầu dải tuổi ta
   nhắm. Phải hạ mức trừu tượng, không chỉ dịch.~~ **← ĐÃ ĐÍNH CHÍNH, xem mục 17:** với dải
   thật 8–15 thì grades 5–9 nằm **TRONG** dải, không phải trên nó. Việc phải làm không còn là
   *hạ mức trừu tượng* mà là **phục vụ hai đầu dải bằng hai độ sâu** — đúng câu hỏi 4 của chủ
   dự án.

---

## 1. Vấn đề cần giải

MOD-05 là **ô khoá cuối cùng** trên dashboard (5 card kia đã có trang thật). Thẻ đang ở
trạng thái `soon` của `js/locks.js` — nói thật là *"đang được xây"*, nhưng chưa ai biết nó
là **gì**. Trong khi đó thẻ đã hứa hai thí nghiệm cụ thể với người dùng ở **cả VI và EN**.

---

## 2. Đề xuất

**Hai thí nghiệm, cả hai về hấp dẫn, cả hai đều rơi tự do — không có mô phỏng quỹ đạo.**

### TN-01 · "Tháp thả rơi" — phá quan niệm sai
Trẻ chọn **hai vật khối lượng lệch hẳn nhau** (búa & lông chim), chọn **nơi** (Trái Đất /
Mặt Trăng), rồi bấm thả. Trên Mặt Trăng chúng **chạm đất cùng lúc**; trên Trái Đất lông chim
rơi chậm hơn — **vì không khí, không phải vì nhẹ hơn**.

Đây chính là màn diễn của Apollo 15, có băng hình thật và trang NASA riêng. Nó là hoạt động
hấp dẫn duy nhất tôi tìm được vừa **đúng dải tuổi** (không công thức, không đơn vị) vừa
**phá được đúng quan niệm sai phổ biến nhất** ("nặng hơn thì rơi nhanh hơn").

### TN-02 · "Cân của em ở đâu" — tách KHỐI LƯỢNG khỏi CÂN NẶNG
Trẻ chọn nơi, lab hiện **cân nặng của em ở đó** cạnh **khối lượng không đổi**. Thông điệp là
một câu NASA viết sẵn: *"Mass stays the same regardless of location and gravity."*

⚠️ **Chỉ hiện những nơi có nguồn** — xem mục 7. Hôm nay là **4 nơi**, không phải 10.

### Một phiên (đúng nhịp ChatGPT đã đề xuất, tôi giữ nguyên)
① Comet đặt câu hỏi → ② trẻ chọn/bấm → ③ thế giới đổi ngay → ④ Comet giải thích →
⑤ trẻ lưu "phát hiện" vào **Hồ sơ hành tinh** (`Step.Codex`, đã tồn tại).

**Không đúng/sai · không quiz · không điểm** — và đó cũng là lý do nó thoả một luật cứng
của dự án, xem mục 4.

---

## 3. Giả định tôi đang dựa vào

- **Tôi giả định thẻ MOD-05 sẽ giữ lời hứa "thả rơi vật thể"**, không viết lại thành thứ
  khác. Nếu đổi lời hứa thì đề xuất này mất chỗ dựa.
- **Tôi giả định "trộn nguyên tố" (nửa còn lại của thẻ) KHÔNG vào phiên bản đầu** — xem
  mục 9. Nếu chủ dự án muốn giữ thì phải chốt riêng, vì nó là hoá học, không phải hấp dẫn,
  và dự án chưa có một dòng dữ liệu hay một nguồn nào cho nó.
- **Tôi giả định Phòng Nghiên Cứu là một KHU (như `codex.html`), không phải một nhiệm vụ.**
  Nghĩa là nó không đi qua `js/mission-engine.js` và không nằm trong cổng lộ trình 70%.
- *[Suy luận]* Tôi giả định trẻ 8 tuổi và trẻ 12 tuổi dùng **cùng một** thí nghiệm được, chỉ
  khác lời giải thích. **Chưa kiểm chứng** — dự án chưa từng thử nội dung với trẻ thật.

---

## 4. Thay đổi ở phía client

| Việc | Ghi chú |
|---|---|
| `lab.html` + `css/lab.css` mới | Nạp `css/page-shell.css` — **đừng copy khung**, luật mục 2 CLAUDE.md |
| `js/lab-drop.js` — cảnh rơi 2D | Canvas 2D, hệ toạ độ ảo cố định như 3 mini-game (`setTransform`), **không dùng three.js** |
| `dashboard.html` — MOD-05 đổi `soon` → có trang | Bỏ `.soon`, đèn `standby` → `ok`, nút `lk-open` → `<a href>`. ⚠️ `check_pages` mục [7b] đang canh **đúng 1** card khoá → phải đổi phát biểu phép kiểm |
| `js/locks.js` | Bỏ mục `lab` khỏi bảng khoá |

⚠️ **KHÔNG dựng bộ sưu tập thứ tư.** Dự án đã có ba (Hồ sơ hành tinh · Sổ Tay Thuật Ngữ ·
Kho Mẫu Vật); "sổ tay phát hiện" ánh xạ thẳng vào `Step.Codex` đã có.

⚠️ **KHÔNG dùng cảnh 3D.** `docs/decisions/005` chốt cảnh 3D là **phần thêm**; và một tháp
thả rơi 2D thì nhìn rõ hơn hẳn — thứ trẻ cần thấy là **hai vật ở cùng độ cao theo thời gian**,
đó là bài toán 2D.

---

## 5. Thay đổi ở phía backend

**Không đụng gì, nếu Phòng Nghiên Cứu là một KHU.** Hai đường có sẵn:

- Muốn lưu "phát hiện" → dùng `POST /me/progress`. ⚠️ **Nhưng `reason` lạ trả 400** —
  `Wallet` không có mục nào cho `lab`, đúng như đã ghi ngày 12/08 cho việc-hàng-ngày. Nên
  phiên bản đầu **không thưởng Thiên thạch tím** (lab là chỗ khám phá, không phải chỗ kiếm
  tiền — cùng lý do đọc bài không thưởng tt).
- Muốn ghi mẫu codex → cần `Step.Codex`, mà cái đó gắn với **bước nhiệm vụ**. ⇒ Phiên bản
  đầu: **không ghi gì lên server**, lab là chỗ chơi tự do.

⚠️ Nếu sau này muốn lab có tiến độ thật thì đó là **thêm một mục trần thưởng ở
`Services/Wallet.cs`** + một loại `reason` mới — việc backend, phải deploy, đừng gộp vào
phiên bản đầu.

---

## 6. Ảnh hưởng tới người chơi cũ

**Không có.** Thêm một khu mới, không đổi id nào, không đụng bộ đếm nào. Cổng lộ trình 70%
đếm theo **bước nhiệm vụ**, mà lab không sinh bước nào → mẫu số không đổi.

Một thứ **được lợi**: `dashboard.html` từ **1 card khoá** về **0**, tức trẻ không còn thấy ô
nào bấm vào rồi bị nói "chưa mở".

---

## 7. Cần bao nhiêu NỘI DUNG mới — và nguồn cho từng con số

### Đã tra và xác minh (đọc trang thật ngày 12/08/2026)

| Nguồn | Nguyên văn dùng được | Độ tuổi trang nhắm |
|---|---|---|
| [NASA — The Apollo 15 Hammer-Feather Drop](https://science.nasa.gov/resource/the-apollo-15-hammer-feather-drop/) | *"a 1.32-kg aluminum geological hammer"* · *"a 0.03-kg falcon feather"* · thả từ *"approximately 1.6 m"* · *"Because they were essentially in a vacuum, there was no air resistance and the feather fell at the same rate as the hammer"* · *"as Galileo had concluded hundreds of years before — all objects released together fall at the same rate regardless of mass"* · người diễn: *"Commander David Scott"* | — (trang tư liệu) |
| [NASA Space Place — How Do We Weigh Planets?](https://spaceplace.nasa.gov/planets-weight/en/) | *"If you weigh 100 pounds on Earth, you would weigh only 38 pounds on Mercury."* · *"If, on the other hand, you were on heavy Jupiter, you would weigh a whopping 253 pounds!"* · *"Mass stays the same regardless of location and gravity. You would have the same mass on Mars or Jupiter as you do here on Earth."* | Space Place = **cho trẻ em** |
| [NASA — Moon Facts](https://science.nasa.gov/moon/facts/) | *"the gravity on the surface of the Moon is one-sixth of Earth's"* | — |
| [NASA — Newton's Law of Gravitation](https://imagine.gsfc.nasa.gov/observatories/learning/swift/classroom/law_grav_guide.html) | *"Count backwards from three, and on 'zero' drop the objects at the same time."* → *"the acceleration due to gravity is independent of its mass"* · *"they would have different weights on different planets"* | **grades 6–9** |
| [NASA — Mass vs. Weight Activities](https://www.nasa.gov/stem-content/mass-vs-weight-activities/) | *"Students often confuse the terms 'mass' and 'weight.'"* | **grades 5–8** |

⚠️⚠️ **HAI HOẠT ĐỘNG HẤP DẪN KINH ĐIỂN CỦA NASA NHẮM GRADES 5–9 (≈10–15 tuổi), TRÊN ĐẦU DẢI
TUỔI TA NHẮM.** Hệ quả thiết kế, không phải chuyện dịch thuật:

- **Bỏ hẳn công thức.** Hoạt động của `imagine.gsfc` phần 2 bắt trẻ **tính** cân nặng ở hành
  tinh khác (cần `F = GMm/r²`). Với trẻ 8 tuổi thì đó là một bức tường. TN-02 vì thế **cho
  sẵn kết quả**, việc của trẻ là **so sánh**, không phải tính.
- **Bỏ hẳn đơn vị `m/s²`.** Không một trang NASA cho trẻ nào dùng nó cho việc này.
- **Giữ nguyên phần THAO TÁC.** *"Đếm ngược từ ba, tới 'không' thì thả cả hai cùng lúc"* là
  câu 8 tuổi làm được ngay, và nó chính là hạt nhân của cả hoạt động.

⚠️⚠️ **SỐ `m/s²` TRONG `explorer.html` CHƯA CÓ NGUỒN, VÀ NASA CHO TRẺ KHÔNG NÓI BẰNG ĐƠN VỊ
ĐÓ.** 10 điểm đến đều khai `gravity:` (Mặt Trời 274 · Sao Thuỷ 3,7 · Sao Kim 8,9 · Trái Đất
9,8 · Mặt Trăng 1,6 · Sao Hoả 3,7 · Sao Mộc 24,8 · Sao Thổ 10,4 · Thiên Vương 8,7 · Hải
Vương 11,0) — `grep nasa.gov` cả file ra **1** kết quả. Trang Moon Facts của NASA nói
**"một phần sáu"**, không nói 1,6 m/s².

⇒ **Phòng Nghiên Cứu chỉ được dùng TỈ LỆ và CÂN NẶNG**, đúng thứ tiếng NASA dùng với trẻ.
Và hôm nay chỉ có nguồn cho **4 nơi**:

| Nơi | Tỉ lệ so với Trái Đất | Nguồn |
|---|---|---|
| Trái Đất | 1× (mốc) | — |
| Mặt Trăng | **1/6** | Moon Facts, nguyên văn |
| Sao Thuỷ | **0,38×** (suy từ 100 lb → 38 lb) | Space Place, nguyên văn |
| Sao Mộc | **2,53×** (suy từ 100 lb → 253 lb) | Space Place, nguyên văn |

⚠️ **Sáu nơi còn lại KHÔNG có nguồn ở mức trẻ em** ⇒ **đừng hiện chúng** ở phiên bản đầu.
Bốn nơi là **đủ** cho bài học (nhẹ hơn nhiều · nhẹ hơn · mốc · nặng hơn nhiều), và bốn nơi
có nguồn tốt hơn mười nơi trong đó sáu là con số không ai chống lưng. Muốn đủ 10 thì **tra
nguồn trước**, đừng lấy số đang có trong `explorer.html`.

### Đếm nội dung (theo lối `2026-08-04`: đếm số trường chữ, không đếm "số nhiệm vụ")

| Loại | Số mục | × song ngữ | Ghi chú |
|---|---|---|---|
| Tên + mô tả 2 thí nghiệm | 4 | 8 | |
| Lời Comet (câu hỏi · giải thích · chốt) mỗi TN | 2 × 5 = 10 | 20 | |
| Nhãn vật thể / nơi | 6 | 12 | búa · lông chim · 4 nơi |
| Câu "phát hiện" trẻ lưu lại | 2 | 4 | |
| Dòng nguồn hiện trên màn | 4 | 4 | URL không cần dịch |
| Nhãn giao diện (nút thả, đặt lại, đếm ngược…) | ~8 | 16 | |
| **Tổng** | **~34 mục** | **~64 trường chữ** | |

Dữ kiện cần tra nguồn: **6** (2 khối lượng + 1 độ cao + 1 câu chân không + 2 tỉ lệ) — **đã
tra xong cả 6**, ghi ở bảng trên.

---

## 8. Cái tôi KHÔNG chắc

- **[Chưa kiểm chứng] Trẻ 8 tuổi có đọc được câu "vì không có không khí" không**, hay nó cần
  một bước trung gian (thổi vào tờ giấy?). Dự án chưa từng thử nội dung với trẻ thật.
- **[Suy luận] Mô phỏng lực cản không khí cho ca Trái Đất.** Rơi trong chân không là `½gt²`,
  nhưng lông chim trên Trái Đất thì cần lực cản. Cách rẻ nhất: **không mô phỏng** — cho lông
  chim rơi với một gia tốc nhỏ cố định và **nói thẳng đây là minh hoạ**, không phải số đo.
  Chưa chắc đây là đánh đổi đúng.
- **Tôi không chắc "trộn nguyên tố" có nên giữ trên thẻ hay không.** Đó là câu của chủ dự án.
- **Ngân sách khuôn.** `docs/decisions/006` đếm *"một nhiệm vụ không dùng cùng một khuôn quá
  2 lần"*. Lab không phải nhiệm vụ nên luật có thể không buộc — nhưng nếu buộc thì hai thí
  nghiệm này **tiêu đúng 2/2** ô của khuôn thứ năm (`parameter_sandbox`, xem `002` — ô đó
  hiện **0 người dùng**). Cần chủ dự án xác nhận cách đếm.

---

## 9. Phương án nhỏ hơn nếu quá tốn

**Giữ TN-01, bỏ TN-02.**

Lý do: TN-01 một mình đã là **một bài học hoàn chỉnh** và nó phá đúng quan niệm sai phổ biến
nhất; nó cũng là cái **có băng hình NASA thật** chống lưng. TN-02 hay, nhưng nó phụ thuộc vào
việc có nguồn cho từng nơi — mà hôm nay chỉ có 4.

**Cắt sâu hơn nữa:** TN-01 chỉ với **hai nơi** (Trái Đất · Mặt Trăng) và **hai vật** (búa ·
lông chim). Đó đúng bằng màn diễn Apollo 15, không thiếu gì.

⚠️ **KHÔNG cắt theo hướng "giữ cả hai nhưng bỏ nguồn"** — với luật *"không con số nào không
có nguồn"*, bỏ nguồn không phải cắt phạm vi mà là **đổi sang một dự án khác**.

---

## 10. Ba thứ tôi CỐ Ý KHÔNG đề xuất

1. **Mô phỏng quỹ đạo / lực hấp dẫn giữa hai vật.** Cảnh 3D ở `explorer.html` là **chuyển
   động theo kịch bản** (`orbitR`, `orbitSpeed`), không tính từ khối lượng. Làm thật thì là
   một bộ mô phỏng vật lý — và `orbitR` của Mặt Trăng là **tỉ lệ nghệ thuật**, nên cảnh đó
   không dùng làm bằng chứng định lượng được.
2. **Thanh trượt liên tục cho trọng lực.** Rủi ro đã ghi ngày 04/08: *"một câu quiz khẳng
   định MỘT điều và có MỘT URL chống lưng; một thanh trượt khẳng định CẢ MỘT DẢI"*. Nên
   TN-02 dùng **4 nơi rời rạc có nguồn**, không dùng dải liên tục.
3. ~~**"Trộn nguyên tố"** — đề nghị sửa `lab_desc`.~~ **ĐÃ RÚT 12/08/2026.** Chủ dự án chốt
   Phòng Nghiên Cứu là **một lưới thẻ hoạt động**, mỗi thẻ một loại. Thiết kế đó gỡ đúng chỗ
   vướng: "trộn nguyên tố" thành **một thẻ riêng ở trạng thái `soon`**, nên `lab_desc` ở ngoài
   **không cần sửa** và lời hứa cũ vẫn đúng. Xem mục 12.

---

## 11. Việc phải làm trước khi code

1. **Chủ dự án chốt:** giữ TN-01+TN-02 hay chỉ TN-01 · "trộn nguyên tố" giữ hay bỏ khỏi thẻ.
2. **Chốt cách đếm ngân sách khuôn** cho một KHU (không phải nhiệm vụ).
3. *(Nên làm, không bắt buộc)* **Tra nguồn cho 10 con số `gravity:` ở `explorer.html`** —
   đó là một lỗ hổng có thật, độc lập với Phòng Nghiên Cứu, và nó sẽ lộ ra ngay khi lab nói
   về trọng lực bằng tỉ lệ trong khi bảng thông tin ngay cạnh nói bằng `m/s²` không nguồn.


---
---

# BẢN CẬP NHẬT — 12/08/2026: Phòng Nghiên Cứu là MỘT LƯỚI THẺ

> Chủ dự án: *"khi trẻ mở vào sẽ có 1 loạt thẻ hoạt động khác nhau. mỗi thẻ 1 loại hoạt động.
> Vậy ta sẽ có thể có nhiều hoạt động được đề xuất trong này mà ko cần đổi tên thẻ phòng
> nghiên cứu bên ngoài"*

Quyết định này **đúng, và nó gỡ được hai chỗ vướng** của bản trên: `lab_desc` không phải sửa,
và "trộn nguyên tố" có chỗ đứng thật thay vì bị bỏ. Nhưng khi đối chiếu mã để dựng lưới thẻ,
tôi tìm ra **hai thứ chặn việc code, cả hai nằm ở tầng cao hơn nội dung.**

---

## 12. Khuôn lưới thẻ — DÙNG LẠI `games.html`, đừng dựng cái thứ tư

Dự án đã có **ba** lưới thẻ chạy thật (`games.html` · `missions.html` cũ · `mission-planet.html`).
Cái khớp nhất là `games.html`, vì nó đã có sẵn đúng thứ lab cần: **thẻ `ready` lẫn `soon` trong
cùng một lưới**, và trạng thái khoá đi qua `js/locks.js`.

```
css/common.css → css/page-shell.css → css/locks.css → css/lab.css
+ mảng dữ liệu {key, code, cls, icon, status, file, name{vi,en}, desc{vi,en}}
```

⚠️ **ĐẶT MÃ `LAB-nn` CỐ ĐỊNH NGAY TỪ THẺ ĐẦU TIÊN.** `games.html` đã trả giá bài học này:
`code:"ARCADE-nn"` từng được **sinh theo vị trí sau khi sort**, nên mỗi lần một game `soon`
thành `ready` là số hiệu cả dãy nhảy hết — trong khi số hiệu đã đi vào tài liệu và cách người
dùng gọi tên. Thẻ mới lấy số kế tiếp, **không đánh số lại**.

⚠️ **Icon: dùng `sic()`**, ô icon của thẻ là 62px nên đạt sàn 22px của bộ sticker. Cần vẽ thêm
vài icon (`flask` đã có; cần `drop`/`scale`/`astronaut-float`) — mỗi cái phải vào danh sách
đang dùng, không để thành icon ngủ (`check_pages` mục [21] canh hai chiều).

⚠️ **Lưới thẻ dịch chuyển ô khoá xuống một tầng, không xoá nó.** Một lý do dựng lab là để
dashboard hết ô "bấm vào rồi bị nói chưa mở". Nếu lab mở ra lại có thẻ `soon` thì ô khoá vẫn
còn, chỉ sâu hơn một tầng. **Không phải lỗi** — `games.html` đang là 3 `ready` / 3 `soon` và
chạy tốt — nhưng phải nói ra để không tưởng là đã giải quyết xong.

---

## 13. ⚠️⚠️ CHẶN VIỆC: Phòng Nghiên Cứu đã được CHỐT là khu TRẢ PHÍ

`docs/decisions/009` (phần GIÁ và GÓI **đã chốt** 09/08/2026), mục *Trả phí* dòng 3:

> **3. Phòng Nghiên Cứu (MOD-05) — dựng thẳng thành khu trả phí**

Và `js/locks.js` đang khai `"lab": { state:"soon", plan:"astronaut" }` với **ba lời hứa bán
hàng** hiện trong modal cho phụ huynh:

| Khoá | Hứa gì |
|---|---|
| `f_lab_1` | "Trộn nguyên tố xem ra chất gì" |
| `f_lab_2` | "Thả rơi đồ vật trên **cả 8 hành tinh**" |
| `f_lab_3` | "Sổ nghiên cứu của riêng bạn" |

Cộng thêm hai điều kiện nữa của `009`:

- **"Miễn phí vĩnh viễn (không lấy lại thứ đã cho)"** — nguyên tắc đã chốt.
- **`SALE_OPEN` không khai trong `template.yaml`** → hôm nay **không ai trả tiền được**.

⇒ Ba đường, và đây là **câu của chủ dự án, không phải của tôi**:

| Đường | Được | Mất |
|---|---|---|
| **(a)** Dựng và để **miễn phí** | Trẻ dùng được ngay; dashboard hết ô khoá | Theo nguyên tắc "không lấy lại thứ đã cho", lab **vĩnh viễn ra khỏi tầng trả phí** — mất 1 trong 7 trục giá trị của `009` |
| **(b)** Dựng và **khoá theo gói** | Giữ nguyên `009` | Xây một khu **không ai mở được** cho tới ngày mở bán; và modal vẫn nói "đang được xây" trong khi nó đã xây xong |
| **(c)** Dựng **một thẻ miễn phí + phần còn lại trả phí** | Trẻ có thứ chơi ngay, tầng trả phí vẫn còn trục | Phải chốt thẻ nào miễn phí; và `f_lab_*` phải viết lại cho khớp |

*[Suy luận]* Tôi nghiêng về **(c)**: `games.html` đã có tiền lệ một lưới vừa `ready` vừa khoá,
và nó cho trẻ chưa trả tiền một lý do quay lại. Nhưng nó là quyết định kinh doanh.

---

## 14. ⚠️⚠️ `f_lab_2` hứa 8 hành tinh, và bảng NASA kinh điển ĐÃ CHẾT

Lời hứa bán hàng nói *"cả 8 hành tinh"*. Tôi đi tìm nguồn cho 8 con số đó và:

| URL | Trạng thái đo 12/08/2026 |
|---|---|
| `nssdc.gsfc.nasa.gov/planetary/factsheet/planet_table_ratio.html` | **307** → `www.nasa.gov/nssdc/` |
| `nssdc.gsfc.nasa.gov/planetary/factsheet/` | **307** → `www.nasa.gov/nssdc/` |

**Bảng "Planetary Fact Sheet — Ratio to Earth Values" không còn ở URL đó.** Đây đúng là bảng
mà mọi tài liệu giáo dục dẫn tới, và nó là nguồn duy nhất tôi biết cho **tỉ lệ trọng lực của
cả 8 hành tinh**.

⚠️ **Và cỗ máy tìm kiếm đã tóm tắt SAI chính bảng đó** — nó trả về *"Mars (0.166), Jupiter
(0.377)"*, tức đảo lộn giá trị (Sao Hoả ~0,38 · Sao Mộc ~2,4). Nếu tôi tin bản tóm tắt thì
Phòng Nghiên Cứu sẽ dạy trẻ rằng **Sao Mộc nhẹ hơn Trái Đất**. Đây là **lần thứ ba** dự án
gặp đúng lỗi này (trước là *"Nam Cực là châu lục cao nhất"* và ba tiêu chí IAU của
`term_planet`) — và lần này nó suýt đi vào một khu trả phí.

⇒ Hôm nay chỉ có nguồn ở mức trẻ em cho **4 nơi** (bảng mục 7). Ba đường:
1. **Sửa `f_lab_2`** thành số nơi giao được — nhưng đó là **sửa một lời hứa bán hàng**.
2. **Tìm nguồn khác cho 8 hành tinh** (JPL `ssd.jpl.nasa.gov/planets/phys_par.html` là ứng
   viên, **tôi chưa kiểm**) — nhưng đó là trang dành cho người làm khoa học, không phải cho trẻ.
3. **Giao 4 nơi trước**, và chỉ mở thêm nơi khi có nguồn.

⚠️ Dù chọn đường nào: **đừng lấy 10 con số `m/s²` đang có trong `explorer.html`** — chúng không
dẫn nguồn nào, và một khu trả phí là chỗ tệ nhất để đặt con số không ai chống lưng.

---

## 15. Lưới thẻ đề xuất — và một phát hiện làm hai thẻ gần như miễn phí

**MỘT ENGINE PHỤC VỤ BA THẺ.** Cả ba thẻ đầu đều là *"vật rơi trong một trường trọng lực"* —
cùng một cảnh 2D, cùng một vòng vẽ, khác nhau ở **câu hỏi** và **cái gì rơi**. Nên thẻ thứ hai
và thứ ba gần như chỉ tốn nội dung.

| Mã | Thẻ | Hạt nhân | Nguồn | Chi phí |
|---|---|---|---|---|
| **LAB-01** | Tháp thả rơi | Búa & lông chim, Trái Đất / Mặt Trăng → trên Mặt Trăng chạm đất **cùng lúc** | ✅ Apollo 15, nguyên văn | **Nhỏ** — engine |
| **LAB-02** | Vì sao phi hành gia trôi | Buông một vật trong trạm → **cả hai rơi cùng nhau** nên trông như trôi. Trạm ở độ cao đó vẫn còn **~90%** trọng lực Trái Đất | ✅ NASA Microgravity **K-4 và 5-8**, nguyên văn | **Nhỏ** — dùng lại engine LAB-01 |
| **LAB-03** | Cân của em ở đâu | Chọn nơi → cân nặng đổi, **khối lượng không đổi** | ✅ Space Place, nhưng **chỉ 4 nơi** | **Nhỏ** |
| **LAB-04** | Ném xa ở các nơi | Cùng một cú ném, trọng lực khác → bay xa khác | ⚠️ **Chưa tra** | Nhỏ (engine + vận tốc ngang) |
| **LAB-05** | Thuỷ triều & Mặt Trăng | Kéo Mặt Trăng xa/gần → thuỷ triều đổi | ⚠️ `term_gravity` đã có câu NASA về thuỷ triều, nhưng **phần hình phải vẽ mới** | **Vừa–lớn** |
| **LAB-06** | Trộn nguyên tố | *(giữ lời hứa `f_lab_1`)* | ⚠️ **0 dữ liệu, 0 nguồn** | Chưa ước lượng được |

**Phiên bản đầu đề nghị: LAB-01 + LAB-02 `ready`, LAB-03 `ready` nếu chốt 4 nơi, còn lại `soon`.**
Ba thẻ `ready` là đúng tỉ lệ `games.html` đang chạy (3/6).

### LAB-02 là thẻ tôi muốn nói thêm — nó là món có giá trị cao nhất

Nó phá một quan niệm sai **phổ biến hơn cả** quan niệm "nặng thì rơi nhanh": trẻ (và người lớn)
tin rằng trong không gian **không có trọng lực**. Trích nguyên văn NASA:

- *"At that altitude, Earth's gravity is about 90 percent of what it is on the planet's surface."*
- *"The spacecraft, its crew and any objects aboard are all falling toward but around Earth.
  Since they are all falling together, the crew and objects appear to float."* (grades 5–8)
- *"The spacecraft, its crew and everything aboard are all falling around Earth."* · *"But small
  amounts of gravity are everywhere."* (grades K-4)
- Tốc độ trạm: *"is moving at a very fast speed – 17,500 miles per hour"*

⚠️ **HAI THỨ TÔI ĐÃ BỎ vì trang KHÔNG nói.** Bản tóm tắt của cỗ máy tìm kiếm cho tôi (a) ví dụ
*"phi hành gia buông quả táo"* và (b) so sánh với *"trò rơi tự do ở công viên, quả bóng trôi
trước mặt bạn"*. Đọc lại trang thì **không có cái nào** — trang nói về bóng chày và lông chim,
và về máy bay bay parabol *"free fall for about 20-30 seconds"*. Hai chi tiết kia rất hợp với
trẻ, nhưng **không được gán cho NASA**. Muốn dùng thì phải tìm trang khác.

### Và một phát hiện trả lời được câu tôi để mở ở mục 8

Tôi đã ghi *"[Chưa kiểm chứng] trẻ 8 tuổi và 12 tuổi dùng cùng một thí nghiệm được không"*.
**NASA tự trả lời:** cùng một chủ đề Microgravity họ xuất bản **hai bản — K-4 và 5-8** — cùng
nội dung, khác độ sâu câu chữ. Dải **8–15** của ta **nằm vắt qua đúng hai bản đó** *(bản đầu
ghi 8–12 — đã đính chính, xem mục 17)*.

⇒ Đề nghị: mỗi thẻ có **một thí nghiệm, hai độ sâu lời giải thích** (câu ngắn trước, "tìm hiểu
thêm" mở ra câu dài). Đó là khuôn NASA đã dùng, và nó rẻ hơn hẳn việc làm hai thí nghiệm.
⚠️ Kèm chi phí thật: **gấp đôi số trường chữ giải thích** (×2 ngôn ngữ = ×4).

---

## 16. Việc phải chốt — bản cập nhật

1. ⚠️⚠️ **Lab miễn phí, trả phí, hay một-thẻ-miễn-phí?** (mục 13) — chặn mọi thứ còn lại.
2. ⚠️ **`f_lab_2` "cả 8 hành tinh"**: sửa lời hứa, hay tra nguồn khác, hay giao 4 nơi trước?
3. Ba thẻ `ready` cho phiên bản đầu có đúng không, hay chỉ LAB-01 + LAB-02?
4. Có làm "hai độ sâu lời giải thích" không (mục 15)?
5. *(Nên làm)* Tra nguồn cho 10 con số `gravity:` ở `explorer.html` — nay càng cần, vì lab sẽ
   nói về trọng lực bằng **tỉ lệ** ngay cạnh một bảng nói bằng **`m/s²` không nguồn**.

---

# BẢN CẬP NHẬT 2 — 12/08/2026: bốn quyết định + đính chính dải tuổi

## 17. Đính chính: dải tuổi là 8–15, và nó đổi một kết luận của chính tài liệu này

**Bằng chứng.** `CLAUDE.md` dùng **"trẻ 8–15"** ở 3 chỗ (mục *hệ thống tài chính*: *"Trẻ 8–15
tuổi không có thẻ ngân hàng"*; mục *tương thích*: *"app cho trẻ 8–15 dùng máy tính bảng"*; mục
*AI/Robot*: *"đúng thứ trẻ 8–15 gặp mỗi ngày"*). Chuỗi "8–12" xuất hiện **một lần duy nhất** và
là về **độ dài bài đọc**, không phải dải tuổi sản phẩm.

**Cái đổi.** Phát hiện số 3 ở *Kết luận ngắn* nói hai hoạt động NASA nằm **trên** dải tuổi:

| Hoạt động NASA | Cấp lớp | So với dải 8–12 | So với dải **8–15** |
|---|---|---|---|
| Newton's Law of Gravitation | grades 6–9 | **trên dải** | **trong dải** |
| Mass vs. Weight | grades 5–8 | vắt qua mép trên | **trong dải** |
| Microgravity (bản K-4) | K–4 | dưới dải | **ở đúng đầu dưới** |
| Microgravity (bản 5-8) | grades 5–8 | vắt qua mép trên | **trong dải** |

⚠️ *[Suy luận]* phép quy đổi cấp lớp Mỹ → tuổi (grade 5 ≈ 10–11, grade 9 ≈ 14–15) là hiểu biết
phổ thông, **tôi không mở nguồn để kiểm**. Kết luận không phụ thuộc con số chính xác: điểm cần
là grades 5–9 **không còn nằm ngoài** dải.

**Việc phải làm vì thế đổi hẳn tính chất.** Không còn là *"hạ mức trừu tượng cho vừa 8–12"* —
làm thế là làm nghèo nội dung cho một đứa 15 tuổi. Việc thật là **phục vụ cả hai đầu dải**: một
đứa 8 tuổi và một đứa 15 tuổi mở **cùng một thẻ**, nhận **cùng một thí nghiệm**, nhưng **khác độ
sâu lời giải thích**. Đó đúng là câu hỏi 4.

⚠️ **Phần vẫn đúng nguyên:** đầu dưới của dải (8 tuổi) **vẫn cần bản nông**, và NASA vẫn không
dùng `m/s²` khi viết cho trẻ. Đính chính này không nới lỏng luật nguồn nào.

---

## 18. Câu hỏi 4 — "có thể có biến số để một thí nghiệm đưa ra hai lời giải thích không?"

**Có. Và biến số đó ĐÃ TỒN TẠI, đã có 71 câu hỏi dán nhãn chờ nó, nhưng nó đang đo sai thứ.**

### 18.1 Cái đã có

| Thứ | Trạng thái đo được | Ai đọc |
|---|---|---|
| `lv` (độ khó 1/2/3) trong `js/quiz/<câu>.js` | khai ở **71 file** | **0 chỗ đọc** |
| `level` (1–50, từ XP) do server tính | trả trong `GET /me/achievements` | `dashboard.html:582` · `achievements.html:254` (qua `AstroQRanks`) |

`js/quiz-index.js` ghi thẳng lý do `lv` còn ngủ, và **chốt chặn của nó giống hệt cái `lab.html`
sẽ gặp**:

> *"⚠️ HIEN CHUA AI DOC `lv`. Chu du an chot 07/08/2026: GIU truong nay, cho duong 'server tinh
> cap do roi client rut de theo cap do'. Muon noi day thi quiz.html can doc duoc cap do cua tre,
> ma trang do CO Y khong nap SDK Firebase (233 KB) nen khong co token — phai them mot cache do
> dashboard ghi, dung khuon `astroq-route-gate`. Dung noi lai ma chua lam cai cache do."*

⇒ **Khuyến nghị kiến trúc: MỘT cơ chế cho cả hai**, không phải hai. Cái cache mà `lv` đang chờ
(`astroq-level`, do `dashboard.html`/`achievements.html` ghi — hai trang đó **đã** gọi
`/me/achievements` nên **0 lượt mạng thêm**) chính là cái `lab.html` cần. Dựng một cơ chế phân
tầng thứ hai cạnh một cơ chế đang ngủ là lỗi dự án đã trả giá nhiều lần (`termsData.ts` phải sửa
hai lần · `AstroQRanks.ALL` ngủ 8 ngày · `cat` khai mà 0 chỗ đọc).

### 18.2 ⚠️ Nhưng `level` đo THỜI GIAN ĐÃ CHƠI, không đo tuổi

Đây là chỗ tôi phải nói ngược lại một phần:

- **Trong hành trình của MỘT đứa trẻ theo thời gian:** level tăng dần khi nó chơi nhiều thêm →
  lời giải thích sâu dần. **Khớp đúng ý** *"trẻ sẽ lớn dần và thụ hưởng độ sâu nhận thức khác
  nhau"*.
- **Giữa HAI đứa trẻ:** một đứa 15 tuổi vừa đăng ký là **level 1** → nhận bản viết cho trẻ 8
  tuổi. Một đứa 8 tuổi chơi ba tháng là level 20 → nhận bản sâu. **Ngược hẳn ý muốn.**

Và `achievements.html:316` đã ghi sẵn luật liên quan: `var cur = VIEW.level ? VIEW.level.level
: 0;   // 0 = chưa biết, KHÔNG phải cấp 1`. Trẻ chưa đăng nhập / mất mạng thì **không biết
level** — lúc đó mặc định phải là **bản nông** (thà nói đơn giản với một đứa 15 tuổi hơn là nói
khó với một đứa 8 tuổi).

### 18.3 Đề nghị: hai bậc, làm bậc 1 trước

**Bậc 1 (làm ngay, gói trong lab):** nút **"Tìm hiểu thêm →"** dưới lời giải thích ngắn, trẻ tự
bấm, lựa chọn được nhớ (`localStorage["astroq-depth"]`, đồng bộ giữa tab đúng khuôn `astroq-sfx`).
Bốn cái được:
- Đúng khuôn NASA đã xuất bản (K-4 và 5-8 là **hai bản**, không phải một bản tự đoán tuổi trẻ).
- **Không phụ thuộc cache level** → không vướng chốt chặn của `lv`, làm được ngay.
- Trẻ 15 tuổi tự bấm sâu, trẻ 8 tuổi bỏ qua — **không đứa nào bị máy đoán sai**.
- Chi phí đúng bằng con số mục 15 đã ghi: **×2 trường chữ × 2 ngôn ngữ = ×4**.

**Bậc 2 (sau, khi có cache level):** `level` quyết định độ sâu **MẶC ĐỊNH**, nút vẫn còn để trẻ
lật. Lúc đó nối `lv` của quiz vào **cùng cache đó** — một lần cho cả hai khu.

⚠️ **Đừng làm bậc 2 trước bậc 1**, và đừng nối `lv` nửa vời — `js/quiz-index.js` đã cảnh báo
đúng câu đó.

---

## 19. Bốn quyết định của chủ dự án (12/08) — và một BẾ TẮC phải xử trước khi code

| # | Quyết định | Ảnh hưởng |
|---|---|---|
| 1 | **Lab có 1 thẻ miễn phí để trải nghiệm** | LAB-01 `free` |
| 2 | **Bỏ lời hứa "cả 8 hành tinh"** | viết lại `f_lab_2`, xem mục 20 |
| 3 | **3 thẻ `ready`** | LAB-01 + LAB-02 + LAB-03 |
| 4 | **Có biến số cho hai độ sâu** | mục 18 — đề nghị bậc 1 trước |

### ⚠️⚠️ 19.1 BẾ TẮC: quyết định 1 + 3 cộng lại ra 2 thẻ `pro`, mà HÔM NAY `pro` là ngõ cụt

3 thẻ ready − 1 thẻ free = **2 thẻ `pro`**. Đường đi của một đứa trẻ bấm vào thẻ đó hôm nay:

```
LAB-02 (pro) → modal "Dành cho gói Phi Hành Gia" → [Xem các gói]
   → pricing.html → dải nhắc "chưa mở bán" + 0 nút thanh toán
   → hết đường.
```

Hai lý do nó là bế tắc thật, không phải chuyện nhỏ:

1. **`SALE_OPEN` không khai trong `template.yaml`** (chủ đích, ghi ở `CLAUDE.md`) → `/checkout`
   trả `sale-closed`. Nên `body_pro` — *"Mở gói {plan} là vào được ngay."* — là **một câu SAI**:
   hôm nay không ai mở được gói nào.
2. **Nhánh `pro` của `js/locks.js` chưa từng có mục nào dùng tới.** Lần dùng đầu tiên của nó sẽ
   là lần dùng trong trạng thái hỏng.

Và nó phạm đúng nguyên tắc dự án đã chốt cho `checkout.html`: *"chưa mở bán thì BỎ HẲN cổng phụ
huynh… một ngày thu cụ thể cho một giao dịch không thể xảy ra là một câu nói sai dù phép tính
đúng."*

### 19.2 Ba đường, và đường tôi khuyến nghị

| Đường | Được | Mất |
|---|---|---|
| **(a)** để 2 thẻ `pro` như hiện tại | đúng quyết định 1+3 nguyên văn | trẻ gặp ngõ cụt; `body_pro` nói sai |
| **(b)** chưa mở bán thì cả 3 thẻ `free`, mở bán thì 2 thẻ thành `pro` | không ngõ cụt | **lấy lại thứ đã cho** — ngược tinh thần *"những gì con kiếm được là của con"* |
| **(c) ⬅ khuyến nghị** — thêm **biến thể lời văn thứ tư** vào `js/locks.js`: nội dung ĐÃ CÓ · cần gói · **nhưng chưa mở bán** → nói thật và **KHÔNG có nút dẫn sang trang giá** | không ngõ cụt · không lấy lại gì · đúng quyết định 1+3 · làm cho lần dùng đầu của nhánh `pro` là lần dùng ĐÚNG | thêm 1 nhánh copy + 1 lời gọi `GET /billing/catalog` (route **công khai**, `pricing.html` đã dùng) |

Nháp lời văn cho (c) — VI: *"Thí nghiệm này nằm trong gói Phi Hành Gia. Gói chưa mở bán nên bọn
mình chưa mời bạn mua gì cả — sắp có nhé!"* · EN: *"This experiment is part of the Astronaut plan.
It is not on sale yet, so there is nothing to buy right now — coming soon!"*

⚠️ **Đừng đọc `saleOpen` ở client rồi tin luôn** — vẫn hỏi route công khai `/billing/catalog` như
`pricing.html`; đọc không được thì **nghiêng về (c)**, tức không bao giờ mời mua.

⚠️ **Cần chốt (a)/(b)/(c) trước khi tôi viết `lab.html`** — nó quyết định cả `js/locks.js` lẫn
lời văn của 3 thẻ.

---

## 20. Nháp lời văn mới cho `f_lab_1/2/3` (quyết định 2)

**⚠️ Cả BA lời hứa hiện tại đều nói về thứ chưa có, không chỉ riêng `f_lab_2`:**

| Khoá | Đang hứa | Vấn đề |
|---|---|---|
| `f_lab_1` | *"Trộn nguyên tố xem ra chất gì"* | = LAB-06, **0 dữ liệu, 0 nguồn** (mục 15) |
| `f_lab_2` | *"Thả rơi đồ vật trên cả 8 hành tinh"* | nguồn chỉ chống lưng **4 nơi** — chủ dự án đã chốt bỏ |
| `f_lab_3` | *"Sổ nghiên cứu của riêng bạn"* | **chưa từng được đề xuất**, và tôi cố ý không đề xuất bộ sưu tập thứ tư |

Ba dòng này là **lời chào mời trong modal khoá**, nên chúng phải mô tả đúng thứ 2 thẻ trả phí
giao — không mô tả tương lai.

**Nháp (VI):**
1. `f_lab_1` — *"Vì sao phi hành gia trôi trong không gian"* ← LAB-02, đúng thứ sẽ giao
2. `f_lab_2` — *"Cân của em ở Mặt Trăng, Sao Hoả, Sao Mộc"* ← LAB-03, **kể tên đúng số nơi có nguồn**
3. `f_lab_3` — *"Lời giải thích có hai độ sâu, lớn thêm là đọc sâu thêm"* ← mục 18, món **có thật**

**Nháp (EN):**
1. *"Why astronauts float in space"*
2. *"Your weight on the Moon, Mars and Jupiter"*
3. *"Two depths of explanation — read deeper as you grow"*

⚠️ **Dòng 2 phải khớp ĐÚNG số nơi thật sẽ ship.** Mục 15 ghi Space Place chống lưng **4 nơi**;
nháp trên kể **3** để chừa biên. Chốt 4 nơi thì sửa dòng này — đừng để nó nói "3" khi lab có 4
hay ngược lại, đó đúng loại lỗi mà quyết định 2 sinh ra để chữa.

⚠️ **`f_lab_3` chỉ đúng NẾU chốt câu 4.** Không làm hai độ sâu thì phải đổi dòng này, không thì
lặp lại đúng lỗi của `f_lab_2`.

---

## 21. Việc phải chốt — bản cập nhật 2

1. ⚠️⚠️ **Đường (a)/(b)/(c) ở mục 19.2** — chặn `lab.html`, chặn `js/locks.js`, chặn lời văn.
2. ⚠️ **Bậc 1 hay bậc 2 cho hai độ sâu** (mục 18.3). Đề nghị bậc 1 (nút "Tìm hiểu thêm").
3. **LAB-03 chốt 3 hay 4 nơi** — quyết định luôn lời văn `f_lab_2` mới.
4. Lời văn `f_lab_*` ở mục 20 có dùng được không.
5. *(Còn nguyên từ bản 1)* Tra nguồn cho 10 con số `gravity:` ở `explorer.html`.
6. *(Kèm theo khi MOD-05 mở)* `check_pages.py` mục **[7b]** đang canh **đúng 1** card khoá trên
   dashboard — mở MOD-05 là con số đó về **0**, phải đổi phát biểu phép kiểm cùng lúc, không thì
   nó báo hỏng đúng lúc sản phẩm làm đúng (lỗi này đã lặp nhiều lần trong dự án).
