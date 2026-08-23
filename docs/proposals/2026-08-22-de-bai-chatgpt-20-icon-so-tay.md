# ĐỀ BÀI CHO ChatGPT — vẽ 20 icon `cx-*` cho Sổ Tay Thuật Ngữ

> **Cách dùng:** dán TOÀN BỘ file này vào ChatGPT. Không cần dán `docs/BRIEFING.md`
> — mọi thứ cần biết đã nằm trong đây.
>
> **Vì sao cần:** kho câu hỏi hiện có **32 câu lẻ chưa thuộc thẻ Sổ Tay nào**.
> Gom chúng theo chủ đề ra **20 thẻ**, và mỗi thẻ Sổ Tay cần **đúng 1 icon vẽ tay**
> (tỉ lệ 1 icon / 1 thẻ, đã giữ suốt 19 thẻ đang chạy). Đây là 20 icon còn thiếu.

---

## 1. Bạn phải nộp cái gì

Đúng **20 dòng**, mỗi dòng một icon, theo khuôn:

```
'cx-<ten>':'<...cac the SVG con...>',
```

Ví dụ **thật** (đang chạy trong sản phẩm — hãy bắt chước y hệt mức chi tiết này):

```
'cx-nebula':'<path d="M6.4 16.2a3.4 3.4 0 0 1-.5-6.7 4.6 4.6 0 0 1 8.6-2.2 3.8 3.8 0 0 1 3.6 6.1 3.2 3.2 0 0 1-2.3 2.8Z"/><circle cx="10" cy="12.2" r="1.15" fill="currentColor" stroke="none"/><circle cx="14.4" cy="10.6" r="0.8" fill="currentColor" stroke="none"/>',
'cx-sensor':'<circle cx="12" cy="17.6" r="2.4"/><path d="M12 15.2V9.4"/><path d="M8.1 9.1a5.6 5.6 0 0 1 7.8 0M5.5 6.3a9.4 9.4 0 0 1 13 0"/>',
'cx-exoplanet':'<circle cx="7.6" cy="8.6" r="4.6"/><circle cx="10.4" cy="8.6" r="1.7" fill="currentColor" stroke="none"/><path d="M2.6 18.4h4l1-2.6h3.4l1-2.4h1.2l1 2.4h3.4l1 2.6h2.4"/>',
```

## 2. Khuôn kỹ thuật — BẮT BUỘC

Chuỗi bạn nộp được nhét vào giữa một thẻ `<svg>` mà **chương trình tự dựng**:

```html
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
     stroke-width="2" stroke-linecap="round" stroke-linejoin="round">…của bạn…</svg>
```

⇒ Vì thế:

| Luật | Chi tiết |
|---|---|
| **KHÔNG** viết thẻ `<svg>` | chỉ nộp phần **con** bên trong |
| **KHÔNG** màu, `id`, `class`, `<defs>`, gradient, `filter`, `mask`, `<text>` | icon phải đổi màu được bằng `currentColor` từ bên ngoài, và có 20 icon trên cùng một trang nên `id` sẽ đè nhau |
| **KHÔNG** đặt `stroke-width` / `stroke` / `fill="none"` trên từng phần tử | thẻ `<svg>` đã đặt |
| Thẻ được dùng | `<path>` · `<circle>` · `<rect>` · `<ellipse>` · `<line>` |
| Hệ toạ độ | `viewBox` **24×24**. Mọi nét nằm trong khoảng **2,4 → 21,6** (nét dày 2 nên sát mép là bị cắt) |
| Tô ĐẶC một hình | ghi ngay trên phần tử đó: `fill="currentColor" stroke="none"` |
| Nét đứt | `stroke-dasharray="2.4 2.2"` (số tuỳ ý, giữ cỡ tương tự) |
| Số phần tử | **3–7**. Nhiều hơn là ở cỡ nhỏ nó thành một vệt mực |
| Chấm nhỏ nhất | bán kính **≥ 0,6**. Nhỏ hơn thì biến mất |
| Hai nét gần nhau | cách nhau **≥ 2,2** (mép-tới-mép). Gần hơn thì ở cỡ nhỏ chúng **hàn lại thành một khối** |

## 3. BỐN LUẬT ĐÃ TRẢ GIÁ BẰNG LỖI THẬT — đọc trước khi vẽ

⚠️ **① Icon phải đọc được ở 26px.** Nó hiện ở **26px** (chip trên thẻ) và 54px
(màn soi chi tiết). **26px là cỡ quyết định.** Một chi tiết chỉ nhìn ra ở 64px là
một chi tiết **nên bỏ đi**. Dự án đã phải bỏ một dấu gạch chéo vì ở 26px nó lẫn
hoàn toàn vào nét tròn bên dưới.

⚠️ **② Vẽ đúng Ý mà sai HÌNH thì người xem đọc ra một đồ vật khác.** Lỗi này đã
xảy ra **8 lần** trong dự án: một cái cân lệch đọc ra y như cái cân thẳng · hai
nét gãy song song đọc thành **chữ số 17** · dấu chia đọc thành **viên kim cương**
· sao chổi đọc thành **cái thìa**, rồi **cái micro**, rồi **chùm xúc xích** · một
bộ não đối xứng đọc thành **con bướm** · một thiên hà bầu dục có đĩa sáng ở tâm
đọc thành **con mắt**. ⇒ **Tự vẽ ra giấy ở cỡ móng tay và hỏi: nó giống cái gì
KHÁC?** Hai cách chữa hiệu quả nhất: **phá đối xứng**, và cho các nét **toả ra từ
MỘT điểm** thay vì xếp song song.

⚠️ **③ Icon phải khác các icon ĐỨNG CẠNH nó.** Chúng nằm cùng một lưới thẻ, nên
"đúng nghĩa" là chưa đủ — phải **phân biệt được với hàng xóm**. Mỗi icon dưới đây
có một dòng `⚠️ ĐỪNG GIỐNG` ghi rõ nó dễ lẫn với cái nào. **Đọc dòng đó trước
khi vẽ.**

⚠️ **④ Tuyệt đối không vẽ chữ, số, hay ký tự.** Icon dùng cho cả bản tiếng Việt
lẫn tiếng Anh, và `<text>` không đổi ngôn ngữ được.

### Bộ icon đã có (để bạn biết cái gì đã tồn tại, ĐỪNG vẽ lại)

`cx-star` sao có tia · `cx-planet` **hành tinh CÓ VÀNH** · `cx-dwarf` hình tròn
với **quỹ đạo nét đứt** quanh nó · `cx-moon` · `cx-asteroid` · `cx-comet` ·
`cx-meteoroid` · `cx-meteor` · `cx-meteorite` · `cx-exoplanet` · `cx-blackhole` ·
`cx-gravity` · `cx-nebula` **đám mây có chấm bên trong** · `cx-supernova` ·
`cx-cmb` **hình bầu dục có nhiều chấm bên trong** · `cx-ai` · `cx-machine-learning`
· `cx-algorithm` · `cx-sensor` **ăng-ten: đế tròn + trụ + hai cung sóng** ·
`cx-ai-ethics` cái cân · `cx-algorithmic-bias` · `cx-star-colour` ·
`cx-solar-eclipse` · `cx-earth-atmosphere` **ba cung vòm lồng nhau**.

---

## 4. Hai mươi icon cần vẽ

Xếp theo nhóm, vì **nguy cơ lẫn nhau nằm TRONG nhóm**.

### Nhóm THIÊN VĂN (4 icon)

**1. `cx-galaxy`** — Thiên hà. *Nghĩa cần đọc ra:* một đảo sao khổng lồ có **cánh
xoắn**.
⚠️ ĐỪNG GIỐNG `cx-cmb` (bầu dục + chấm) và `cx-nebula` (mây + chấm). **Một hình
bầu dục có chấm bên trong là SAI** — đó đúng là hai icon đã có, và nó còn đọc ra
thành **con mắt**. Phải thấy được **ít nhất hai cánh xoắn** cong ra từ lõi.

**2. `cx-saturn-cassini`** — Sao Thổ và tàu Cassini.
⚠️ ĐỪNG GIỐNG `cx-planet` — icon đó **đã là** một hành tinh có vành. Phải thêm
được hai điều: vành **gồm nhiều mảnh rời** (vài chấm nhỏ nằm trên đường vành, đó
chính là bài học của thẻ), và **một con tàu nhỏ** với đường bay nét đứt quanh
hành tinh.

**3. `cx-webb`** — Kính thiên văn James Webb.
*Nghĩa cần đọc ra:* gương **ghép từ các mảnh hình lục giác** (dấu hiệu nhận dạng
riêng của Webb) đặt trên **tấm chắn nắng nhiều lớp** hình thoi/tam giác dẹt.
⚠️ ĐỪNG GIỐNG `cx-gaia` bên dưới (cũng là tàu có tấm chắn nắng). Điểm phân biệt
duy nhất đọc được ở 26px là **tổ ong lục giác**. 3–4 lục giác là đủ; 18 mảnh như
thật thì thành một vệt mực.

**4. `cx-gaia`** — Tàu Gaia dựng bản đồ 3D thiên hà.
*Nghĩa cần đọc ra:* một **đĩa/mái che tròn dẹt** (tấm chắn nắng của Gaia) và phía
trên là **vài ngôi sao được nối bằng lưới toạ độ** — ý "vẽ bản đồ".
⚠️ ĐỪNG GIỐNG `cx-webb` (không có lục giác nào ở đây) và `cx-star` (sao ở đây là
**chấm đặc nhỏ**, không có tia).

### Nhóm VẬT LÝ (4 icon)

**5. `cx-four-forces`** — Bốn lực trên một tên lửa.
*Nghĩa:* **bốn mũi tên** ra bốn hướng từ một thân nhỏ ở giữa (lên/xuống =
đẩy/trọng lực, ngang = cản/nâng).
⚠️ ĐỪNG vẽ thân tên lửa chi tiết — bốn mũi tên là thứ phải đọc ra. Và ĐỪNG GIỐNG
`cx-supernova` (cũng là các tia ra bốn phía): ở đây đầu mút phải là **mũi tên có
chóp**, không phải nét trơn, và **hai mũi hướng vào, hai mũi hướng ra**.

**6. `cx-newton-inertia`** — Định luật 1: vật giữ nguyên chuyển động.
*Nghĩa:* một quả cầu nhỏ, phía sau là **đường đã đi (nét liền)**, phía trước là
**đường sẽ đi tiếp (nét đứt)** — ý "không có gì đẩy thì nó cứ đi mãi".
⚠️ ĐỪNG GIỐNG `cx-comet` (cũng là hình tròn có vệt sau). Điểm khác: ở đây **nét
trước và nét sau nằm trên MỘT đường thẳng**, và phần trước là **nét đứt**.

**7. `cx-rocket-thrust`** — Lực đẩy: khí phun ra sau, tên lửa đi tới trước.
*Nghĩa:* một **miệng ống đẩy hình phễu**, luồng khí là **mũi tên chỉ XUỐNG/RA
SAU**, và **một mũi tên nhỏ hơn chỉ NGƯỢC LẠI** — cặp tác dụng ↔ phản tác dụng.
⚠️ ĐỪNG GIỐNG `cx-rocket-engine` bên dưới. Ở đây thứ nhìn thấy là **hai mũi tên
ngược chiều**; ở kia là **bên trong khối thuốc phóng**.

**8. `cx-solar-cell`** — Tấm pin biến ánh sáng thành điện.
*Nghĩa:* một **hình chữ nhật nghiêng có vài vạch chia** (tấm pin), **một tia sáng
chỉ vào nó**, và **một tia điện đi ra** ở phía đối diện.
⚠️ ĐỪNG GIỐNG `cx-station-power` (cũng có tấm pin). Ở đây chỉ có **MỘT** tấm, và
điểm nhấn là **tia vào ↔ điện ra**.

### Nhóm KỸ THUẬT (4 icon)

**9. `cx-rocket-engine`** — Động cơ tên lửa rắn: thuốc phóng trộn sẵn trong vỏ.
*Nghĩa:* một **vỏ hình viên nang cắt dọc**, bên trong là **các vạch chéo song
song** (khối thuốc phóng đặc), đáy có **miệng ống đẩy nhỏ**.
⚠️ ĐỪNG GIỐNG `cx-rocket-thrust` — ở đây **không có mũi tên nào**.

**10. `cx-station-power`** — Tấm pin cuộn THÊM vào bộ pin cũ trên trạm.
*Nghĩa:* một tấm pin **chữ nhật đã mở** đứng cạnh một tấm **đang cuộn ra từ một
cuộn tròn** — chữ "thêm vào" phải đọc được từ việc có **hai tấm cạnh nhau**, một
cũ một mới.
⚠️ ĐỪNG GIỐNG `cx-solar-cell` (chỉ một tấm, có tia sáng). Ở đây **không vẽ tia
sáng nào**, và bắt buộc có **cái cuộn**.

**11. `cx-life-support`** — Hệ giữ mạng sống: nước · khí · oxy quay thành vòng.
*Nghĩa:* **ba khối nhỏ** xếp thành tam giác, nối bằng **ba mũi tên cong thành một
vòng kín** — ý "tái chế, dùng lại".
⚠️ ĐỪNG GIỐNG `cx-machine-learning` (cũng là các hình tròn nối nét). Điểm khác:
ở đây các nét là **mũi tên cong cùng một chiều**, tạo thành **vòng tròn**.

**12. `cx-mars-rover`** — Robot tự hành trên Sao Hoả.
*Nghĩa:* **thân hộp trên sáu bánh** (vẽ 3 bánh nhìn ngang là đủ), có **một cột
cần mang đầu camera**, đứng trên **một vạch mặt đất**.
⚠️ Chưa có icon nào giống. Nhưng ⚠️ **đừng vẽ vệt bánh xe** — ở 26px nó hàn vào
vạch mặt đất.

### Nhóm SINH HỌC & SỰ SỐNG (4 icon)

**13. `cx-body-space`** — Cơ thể người đổi khác khi không có trọng lực.
*Nghĩa:* một **hình người rất đơn giản** (đầu tròn + thân + tay chân), và **một
mũi tên nhỏ chạy dọc thân hướng LÊN ĐẦU** — ý dịch chuyển dịch thể lên đầu.
⚠️ ĐỪNG vẽ mặt (mắt/miệng): ở 26px chúng thành ba vết mực.

**14. `cx-space-biology`** — Nghiên cứu sinh vật trong không gian.
*Nghĩa:* một **đĩa petri tròn dẹt** có **hai ba chấm sinh vật bên trong**, và
**một kính lúp** soi vào nó.
⚠️ ĐỪNG GIỐNG `cx-nebula` và `cx-cmb` (hình có chấm bên trong). Cái **kính lúp
với cán** là thứ giữ cho nó không lẫn — hãy vẽ cán rõ ràng.

**15. `cx-plants-space`** — Trồng cây trong không gian.
*Nghĩa:* một **mầm cây hai lá** mọc từ **một hộp trồng hình thang**, và **một
giọt nước** bên cạnh (bài học của thẻ là chuyện NƯỚC, không phải ánh sáng).
⚠️ **ĐỪNG vẽ đèn hay tia sáng** — bài đọc nói rõ chỗ khó nhất *không* phải ánh
sáng, nên vẽ đèn là dạy sai trọng tâm.

**16. `cx-life-needs`** — Sự sống cần ba thứ.
*Nghĩa:* **đúng ba biểu tượng nhỏ xếp thành hàng hoặc tam giác**: một **giọt
nước**, một **hình tròn có tia** (nguồn năng lượng), một **cung vòm** (khí quyển
che chắn).
⚠️ ĐỪNG GIỐNG `cx-earth-atmosphere` (ba cung vòm lồng nhau) — ở đây **chỉ MỘT**
cung, và nó đứng cạnh hai thứ khác.

### Nhóm TOÁN & ĐO LƯỜNG (4 icon)

**17. `cx-light-year`** — Năm ánh sáng là một KHOẢNG CÁCH.
*Nghĩa:* **hai chấm sao** ở hai đầu, giữa là **một mũi tên hai đầu** có **vài
vạch chia như cây thước** — chữ "khoảng cách" phải đọc được từ mũi tên hai đầu.
⚠️ Đây là chỗ dễ sai nhất của cả bộ: **đừng vẽ đồng hồ hay mặt số**. Cả thẻ tồn
tại để nói nó KHÔNG phải thời gian.

**18. `cx-parallax`** — Đo khoảng cách bằng GÓC, ngắm từ hai chỗ.
*Nghĩa:* **một ngôi sao ở trên**, **hai điểm quan sát ở dưới cách nhau**, hai
**đường ngắm** từ hai điểm đó lên ngôi sao, và **một cung nhỏ đánh dấu góc** ở
đỉnh.
⚠️ Cung góc phải nằm **sát đỉnh** ngôi sao. Vẽ cung to là nó thành một cái quạt.

**19. `cx-units`** — Hai bên dùng hai đơn vị khác nhau thì mất tàu.
*Nghĩa:* **hai cây thước ngắn nằm cạnh nhau**, vạch chia **thưa** ở cây này và
**dày** ở cây kia — ý "cùng một chiều dài, hai cách đo".
⚠️ ĐỪNG vẽ dấu bằng, dấu khác, hay chữ. Sự khác nhau phải đọc được từ **mật độ
vạch chia**.

**20. `cx-orbit`** — Quỹ đạo là một thế cân bằng, và nó là hình bầu dục.
*Nghĩa:* một **đường elip rõ ràng KHÔNG phải hình tròn** (trục dài hơn trục ngắn
thấy rõ), một **vật nặng ở một tiêu điểm** (lệch khỏi tâm — chính chỗ này là bài
học), và **một vật nhỏ trên đường elip**.
⚠️ ĐỪNG GIỐNG `cx-dwarf` — icon đó **đã là** một hình tròn với quỹ đạo nét đứt
quanh nó. Hai điểm phân biệt: ở đây đường là **elip dẹt rõ rệt**, và vật nặng
**nằm lệch tâm**.

---

## 5. Tự kiểm trước khi nộp

Với **từng** icon, trả lời:

1. Có đúng **3–7** phần tử? Mọi toạ độ trong **2,4 → 21,6**?
2. Có phần tử nào mang `id`, `class`, màu, `stroke-width`, `<text>`, gradient
   không? (**phải KHÔNG**)
3. Thu nó về **cỡ móng tay** trong đầu: nó **giống đồ vật nào khác**? Nếu có, vẽ
   lại.
4. Đọc lại dòng `⚠️ ĐỪNG GIỐNG` của nó: nó **có** khác cái đó ở 26px không?
5. Có cặp nét nào cách nhau **dưới 2,2** không? (chúng sẽ hàn thành một khối)

Nộp **20 dòng, không kèm giải thích**, rồi ở cuối ghi riêng một mục ngắn:
*"icon nào tôi thấy còn rủi ro đọc sai, và vì sao"* — mục đó quan trọng, đừng bỏ.
