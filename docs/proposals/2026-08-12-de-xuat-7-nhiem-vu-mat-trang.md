# Đề xuất: 7 nhiệm vụ ở điểm đến MẶT TRĂNG (MOON-01 → MOON-07)

**Người viết:** Claude · **Ngày:** 2026-08-12
**Vai:** đối chiếu mã nguồn · ước lượng chi phí · đề xuất nội dung (`docs/PHAN-VAI.md`)
**Đầu vào:** rà lại toàn bộ `docs/proposals/` của ChatGPT và Gemini + đối chiếu `Missions.cs`,
`js/mission-catalog.js`, `js/locks.js`, `js/earth2d.js`, `mission-earth.html`

---

## Kết luận ngắn

**Chưa có model nào đề xuất một nhiệm vụ nào Ở Mặt Trăng — và đó không phải thiếu sót, đó là
một quyết định đã chốt.** ChatGPT viết M-02 → M-06 **toàn bộ ở Trái Đất**; nhiệm vụ duy nhất
từng chạm tới Mặt Trăng (M-05 · thuỷ triều) đã bị đính chính là **sai tầng** và chốt phương án
**(a)**: giữ thuỷ triều ở Trái Đất, Mặt Trăng chỉ là *lời giải thích*, không phải thứ trẻ điều
khiển. Gemini không viết nhiệm vụ — lane của nó là tra nguồn.

Nên đề xuất này **không chồng lên gì cả**, nhưng nó chạm vào **sáu chốt chặn ở mã nguồn**, và
hai cái đầu phải sửa **trước khi viết dòng mã nhiệm vụ đầu tiên**:

1. ⚠️⚠️ `Mission.Planet` đang làm **hai việc**, nên một nhiệm vụ Mặt Trăng sẽ **đếm Mặt Trăng
   là hành tinh thứ 9** và mở sai huy hiệu `planet-8`.
2. ⚠️⚠️ **Không có một tấm bản đồ Mặt Trăng nào trong kho** — `img/earth/` chỉ có Trái Đất.
3. Ba trong sáu khuôn tương tác **chưa dùng lại được**: chúng nằm trong `mission-earth.html`.
4. `mission-planet.html` **chưa có cơ chế gấp** — 7 nhiệm vụ ở một nơi là đúng ca kích hoạt nó.
5. `js/locks.js` đang hứa *"Cả **một** nhiệm vụ dài"* và *"mở đường bay tới hành tinh kế tiếp"* —
   câu thứ hai nói về một thứ **chưa tồn tại**.
6. `MissionOfPlace()` lấy `FirstOrDefault` → cổng lộ trình 70% sẽ tính trên **một** nhiệm vụ tuỳ ý.

---

## 1. Vấn đề cần giải

Mặt Trăng là **điểm đến thứ hai và cuối cùng** của lộ trình (`Missions.Route = ["earth","moon"]`),
đã mở được bằng cổng 70% của Trái Đất, đã có đĩa + nhãn trên bản đồ nhiệm vụ, đã có mục trong
`js/locks.js` với ba lời hứa bán hàng — **và không có một nhiệm vụ nào**. Trẻ xong Trái Đất thì
bay tới đó, chạm vào, và nhận một hộp thoại "đang được xây".

Câu hỏi của chủ dự án: **7 nhiệm vụ ở đó là gì.**

---

## 2. Kiểm lại đề xuất của ChatGPT và Gemini — đã tìm được gì

### 2.1 ChatGPT — 0 nhiệm vụ Mặt Trăng, và có lý do

| File | Nội dung liên quan |
|---|---|
| `2026-08-05-de-bai-chatgpt-20-nhiem-vu-daily-su-kien.md` | Đề bài **20 nhiệm vụ ở TRÁI ĐẤT** (M-02 → M-21). Gợi ý chủ đề có *"thuỷ triều & Mặt Trăng"* — nhưng đặt trong danh sách chủ đề **của Trái Đất** |
| `2026-08-05-dinh-chinh-chatgpt-vong-1-5.md` §③ | **M-05 · Mặt Trăng & thuỷ triều → "sai tầng, phải sửa"**. Chốt **(a)**: kể hoàn toàn từ phía Trái Đất, *"bỏ hết chặng đưa Mặt Trăng vào vị trí"* |
| `2026-08-04-chatgpt-activities-vong-2.md` | *"Không thiết kế cho 9 hành tinh nữa, chỉ cho Mặt Trăng để có số đo được"* — nhưng đó là **hoạt động phòng lab**, không phải nhiệm vụ |
| `2026-08-05-review-chatgpt-M02-M04.md` | Ba lỗi ở M-02→M-04 (lỗi cộng ngân sách · khuôn 5 bị dùng làm khuôn 3 · chặng cuối là bài kiểm tra thứ sáu). **Ba luật đó áp thẳng cho Mặt Trăng** |

⇒ **Ba luật rút ra từ vòng Trái Đất, đề xuất này tuân đủ:**
- *tổng một dòng ngân sách phải bằng đúng số chặng* (phép thử một giây);
- *khuôn 5 chỉ dùng khi bốn lựa chọn xếp được thành một **thang có thứ tự***;
- *chặng cuối là chỗ **chốt**, 0 lựa chọn* — có phép kiểm tự động canh điều này ở M-01.

### 2.2 Gemini — không có đề xuất nhiệm vụ, nhưng có hai thứ dùng được

Lane của Gemini là **tra nguồn & kiểm chứng**, nên nó không viết nhiệm vụ nào — `grep` toàn bộ
`docs/proposals/` cho "mission moon" ra **0 kết quả**. Hai thứ nó đã kiểm và dùng lại được:

- `2026-08-06-review-gemini-35-the.md:87` — **thuỷ triều có hai chỗ nước dâng cùng lúc**, kể cả
  phía **đối diện** Mặt Trăng; nói mỗi *"Mặt Trăng kéo nước lên"* là **bán phần**.
  ⇒ Ràng buộc cho bất cứ chặng nào chạm tới thuỷ triều — **kể cả khi nó nằm ở Trái Đất**.
- `2026-08-06-review-gemini-30-the-chot.md:81` — vì sao **Mặt Trăng và ISS cùng gọi là "vệ tinh"**.
  ⇒ Dùng được làm câu chốt của MOON-01.

### 2.3 Hai con số ChatGPT đã bị bác — đừng lặp lại ở Mặt Trăng

- **Khuôn 6 (`ngắm-định-hướng`) là 0 DÒNG MÃ**, không phải "đã dựng, đang chờ". Nguyên liệu
  (`setEarthDrag`, `stationAngleTo`) **đã bị xoá** khỏi `js/earth2d.js` cùng bước `rotation`.
  Luật đã chốt: **tối đa 2 nhiệm vụ trong cả bộ** được dùng nó, và hai nhiệm vụ đó phải
  **dùng chung MỘT định nghĩa góc** — tức viết được **một** hàm phục vụ cả hai.
- **Lớp phủ CSS KHÔNG phải asset.** Asset ảnh là thứ **chờ chủ dự án đặt vào `img/`**; lớp phủ
  là mã, viết xong là xong. Bảng dưới đây tách hai dòng đó, đúng như §⑥ của bản đính chính.

---

## 3. ⚠️ Sáu chốt chặn ở mã nguồn — đo được, không phải phỏng đoán

### 3.1 ⚠️⚠️ `Mission.Planet` làm hai việc → Mặt Trăng sẽ bị đếm là hành tinh thứ 9

Trường `Planet` của một nhiệm vụ được đọc ở **đúng hai chỗ**, và chúng cần hai thứ khác nhau:

```
Services/Missions.cs:197   All.FirstOrDefault(m => m.Planet == place)   ← cần ID ĐIỂM ĐẾN
Endpoints/MeEndpoints.cs:924  justFinished ? m.Planet : null            ← ghi vào PROGRESS.planets
```

Nghĩa là khai `new("moon-surface", "moon", …)` thì **xong nhiệm vụ là "moon" được ghi vào tập
`planets`**. Hậu quả đo được từ `Services/Achievements.cs`:

```
147:  "planets" => p.Planets.Count
96-98: planet-1 (1) · planet-3 (3) · planet-8 (8)
```

⇒ Trẻ mở được huy hiệu **"đã ghé 8 hành tinh"** khi mới ghé **7 hành tinh + Mặt Trăng**. Đây
đúng cái `js/mission-catalog.js` đã cảnh báo bằng chữ đậm (*"nhét nó vào danh sách hành tinh là
hồ sơ đếm sai và hai huy hiệu kia thành bất khả thi"*) — cảnh báo đó viết cho client, nhưng
**lỗ hổng nằm ở server**.

**Cách sửa (backend, nhỏ):** tách record `Mission` thành hai trường — `Place` (id điểm đến, dùng
cho `MissionOfPlace`) và `Planet?` (**null** với Mặt Trăng, dùng cho câu "đã ghé"). Với Trái Đất
hai trường trùng nhau nên **không phá dữ liệu cũ**. Kèm một phép kiểm ở `check_pages` mục [20]:
*mọi `Planet` khác null phải có thật trong `js/planets.js`* — mục [20] **đã có** phép kiểm đúng
dạng đó cho điểm đến, chỉ cần mở rộng sang nhiệm vụ.

### 3.2 ⚠️⚠️ Không có tấm bản đồ Mặt Trăng nào

```
img/earth/ : flat-2048.{avif,webp} · globe-640.{avif,webp} · graticule.svg
js/earth2d.js:45  MAPS = { globe: img/earth/globe-640…, flat: img/earth/flat-2048… }
```

Cả `MAPS` lẫn thư mục ảnh **chỉ có Trái Đất**. Không có bản đồ thì **cả 7 nhiệm vụ đều không có
cảnh** — đây là chốt chặn nặng thứ hai, và nó là loại **chờ người**, không phải chờ mã (5 ảnh
`img/era/*` đã phải chờ đúng như vậy, tốn hẳn một file đề xuất riêng).

**Tin tốt:** đây là **một asset dùng cho cả 7 nhiệm vụ**, không phải một asset mỗi nhiệm vụ —
trả tiền một lần. Cần **hai** bức từ cùng một bộ: **mặt gần** và **mặt xa** (MOON-03 dựa hẳn vào
sự khác nhau giữa hai mặt).

Ứng viên nguồn, **đã kiểm trả 200 ngày 12/08/2026** nhưng **[Chưa kiểm chứng] tôi chưa tải và
chưa xem file** — phải soi ảnh thật trước khi chốt (bài học Blue Marble: *"ảnh Blue Marble là
QUẢ CẦU tâm Bắc Mỹ, không phải bản đồ phẳng"* — đặt lat/lon lên nhầm loại ảnh là **dạy sai địa lý**):

| URL | Mã | Ghi chú |
|---|---|---|
| `https://svs.gsfc.nasa.gov/4720/` | 200 | CGI Moon Kit — ứng viên mạnh nhất cho bản đồ phẳng |
| `https://science.nasa.gov/mission/lro/` | 200 | trang sứ mệnh LRO, nơi lần ra ảnh mosaic |
| `https://moon.nasa.gov/` | 200 | cổng vào |

⚠️ **Phải xử lại đúng quy trình đã dùng cho `flat-2048`**: cắt/thu/nén rồi kiểm **độ sáng khung
nhìn mở màn** — bản đồ Mặt Trăng là ảnh **xám**, nên nguy cơ "cảnh mở màn tối và phẳng" cao hơn
hẳn Trái Đất. Con số mốc đã có sẵn để so: khung mở màn của M-01 đạt **82,7** điểm sáng.

### 3.3 Ba trong sáu khuôn **chưa dùng lại được**

```
dragDrop( · buildAsk( · buildXsec(   → 14 lời gọi, TẤT CẢ trong mission-earth.html (2.955 dòng)
js/pick-place.js (243 dòng)          → khuôn DUY NHẤT đã tách ra dùng chung
js/mission-engine.js (245 dòng)      → trình điều phối bước, dùng chung được
js/earth2d.js (615 dòng)             → gắn cứng asset Trái Đất trong MAPS
```

⇒ Dựng MOON-01 hôm nay = **hoặc** chép ba khuôn sang file thứ hai (hai bản sẽ lệch nhau, đúng
lỗi `termsData.ts` đã phải sửa hai lần), **hoặc** tách chúng ra trước. Bước 4 của
`docs/decisions/002` (*"chuyển 8 bước Trái Đất sang dữ liệu"*) **chưa làm**, và Mặt Trăng chính
là chỗ nó phải được trả.

### 3.4 `mission-planet.html` chưa có cơ chế GẤP

CLAUDE.md ghi rõ nó **cố ý** chưa mang sang: *"hôm nay mỗi nơi có nhiều nhất MỘT nhiệm vụ, nên
chép vào là ~80 dòng không bao giờ chạy"*, và *"thêm nhiệm vụ thứ hai ở một nơi thì mang sang"*.
**7 nhiệm vụ ở một nơi là đúng ca đó.** Lời giải đã có sẵn ở `scratchpad/proto-planet.js`
(216 dòng): gấp phần đã xong · chỉ hiện 2 nhiệm vụ kế · gấp phần còn lại.

⚠️ Kèm theo: `mission-map.html` hiện **bỏ qua màn hành tinh khi một nơi chỉ có MỘT nhiệm vụ**
(`goWorld()`). Mặt Trăng có 7 thì màn đó **thành cửa chính** — đúng như thiết kế đã dự trù, nhưng
phải kiểm lại nhánh rẽ đó chứ đừng cho là nó tự đúng.

### 3.5 `js/locks.js` đang hứa hai điều sẽ sai

```
js/locks.js:127  f_moon_1: "Cả một nhiệm vụ dài trên Mặt Trăng"
js/locks.js:129  f_moon_3: "Mở đường bay tới hành tinh kế tiếp"
```

- `f_moon_1` nói **một** nhiệm vụ. Bảy thì phải viết lại (và viết lại theo hướng **tốt hơn**).
- `f_moon_3` ⚠️ **hôm nay là một câu sai**: `Missions.Route = ["earth", "moon"]` **kết thúc ở
  Mặt Trăng** — không có hành tinh kế tiếp nào để mở. Đây đúng loại lỗi `f_lab_2` đã phải sửa
  ngày 12/08 (*"cả 8 hành tinh"* trong khi nguồn chỉ chống lưng 4 nơi).
  ⇒ Hoặc **sửa lời văn**, hoặc **thêm điểm đến thứ ba vào `Route`** — nhưng thêm điểm đến là hứa
  thêm một nơi chưa có nội dung, tức lặp lại đúng cái bẫy. **Đề nghị: sửa lời văn.**

### 3.6 Cổng 70% sẽ tính trên **một** nhiệm vụ tuỳ ý

```
Services/Missions.cs:197  MissionOfPlace(place) => All.FirstOrDefault(m => m.Planet == place)
```

`UnlockedPlaces` gọi hàm này để hỏi *"nơi này đã đạt cổng chưa"*. Với **một** nhiệm vụ mỗi nơi
thì đúng; với **bảy** thì nó lấy cái đầu tiên trong mảng, tức **thứ tự khai báo quyết định cổng** —
một hành vi không ai cố ý chọn.

Hôm nay hậu quả bằng 0 (Mặt Trăng là chặng cuối của `Route`, không mở tiếp gì). Nhưng nó là **mìn
hẹn giờ**: thêm điểm đến thứ ba là nó nổ, và nổ **im lặng**. ⇒ Chốt luật ngay khi thêm nhiệm vụ
thứ hai vào một nơi: *cổng của một NƠI = đạt cổng của **nhiệm vụ đầu tiên** của nơi đó*, khai
tường minh bằng một trường thay vì suy từ thứ tự mảng.

---

## 4. Chi phí — con số trước, đề xuất sau

| | Số đo | Nguồn |
|---|---|---|
| Chi phí một chặng | **~410–445 dòng mã** | `docs/decisions/002` (3.300 dòng / 8 bước), đề bài 05/08 |
| 7 nhiệm vụ × ~5,1 chặng | **36 chặng** | bảng ở mục 5 |
| Ước tính thô | *[Suy luận]* **~15.000 dòng** nếu viết tay như M-01 | 36 × 410 |
| Cả dự án hiện tại | ~23.500 dòng | BRIEFING |

⇒ **Viết 7 nhiệm vụ theo lối M-01 là thêm ~64% khối lượng mã của cả dự án.** Con số đó không
phải lý do bỏ Mặt Trăng — nó là lý do **tách khuôn ra trước** (mục 3.3). Nếu ba khuôn kia trở
thành thư viện dùng chung như `js/pick-place.js`, chi phí một chặng rơi về **dữ liệu + lời thoại**;
*[Chưa kiểm chứng]* mức giảm thật là bao nhiêu — **đó chính là con số `docs/decisions/001` đang
chờ**, và MOON-01 là phép đo đó.

**Vì thế đề nghị: dựng MOON-01 trước, ĐO, rồi mới quyết 6 cái còn lại.** Bảy nhiệm vụ dưới đây
là **bản đồ đường đi**, không phải một đơn hàng gửi đi cùng lúc.

---

## 5. Đề xuất — 7 nhiệm vụ

Khuôn đánh số theo đề bài 05/08: **K1** chạm-điểm-trên-bản-đồ · **K2** đi-theo-thứ-tự ·
**K3** câu-đố-4-lựa-chọn · **K4** kéo-thả-vào-ô · **K5** xếp-lên-thang · **K6** ngắm-định-hướng.

### Mục 0 — Ngân sách khuôn (tự cộng; tổng mỗi dòng = đúng số chặng)

| Nhiệm vụ | K1 | K2 | K3 | K4 | K5 | K6 | chốt | tổng |
|---|---|---|---|---|---|---|---|---|
| MOON-01 Bề mặt chị Hằng | 2 | 0 | 1 | 0 | 1 | 0 | 1 | **5** |
| MOON-02 Vì sao Trăng đổi hình | 0 | 1 | 1 | 0 | 1 | **1** | 1 | **5** |
| MOON-03 Một mặt luôn quay về ta | 1 | 0 | 1 | 1 | 0 | **1** | 1 | **5** |
| MOON-04 Một ngày trên Mặt Trăng | 1 | 0 | 1 | 1 | 1 | 0 | 1 | **5** |
| MOON-05 Dấu chân đầu tiên | 1 | 1 | 1 | 1 | 0 | 0 | 1 | **5** |
| MOON-06 Nước đá trong bóng tối | 1 | 0 | 1 | 1 | 1 | 0 | 1 | **5** |
| MOON-07 Hồ Sơ Mặt Trăng | 1 | 1 | 1 | 0 | 0 | 0 | 1 | **4** |

**Không dòng nào vượt 2 lần/khuôn.** **K6 dùng ở đúng 2 nhiệm vụ** (MOON-02, MOON-03) — đúng
trần đã chốt, và mục 5.8 chỉ ra chúng **dùng chung một định nghĩa góc**.

---

### MOON-01 · Bề mặt chị Hằng
- **Chủ đề:** những vệt tối trên Mặt Trăng không phải biển nước.
- **Câu hỏi lớn:** *Nhìn lên Mặt Trăng thấy vệt sáng vệt tối — đó là gì?*
- **Cảnh dùng lại:** bản đồ Mặt Trăng **mặt gần** (asset mới, dùng chung cả 7).
- **Asset ảnh mới:** ✅ bản đồ mặt gần *(một lần cho cả bộ)* · **Lớp phủ cần vẽ:** không

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Chạm vào những vệt tối | K1 | chạm 4 vùng tối/sáng nó tự chọn, theo thứ tự nào cũng được | mỗi vùng mở một thẻ tên thật |
| 2 | Biển… mà không có nước? | K3 | đoán vệt tối là gì | chính cú đoán lật thẻ "biển đá" |
| 3 | Hố to hố nhỏ | K5 | xếp 4 hố lên thang **đường kính** | cột dựng dần = dải cỡ hố |
| 4 | Ai đục ra những cái hố này? | K1 | chạm hố nó muốn soi kỹ | thẻ nội dung + vành hố sáng lên |
| 5 | Đóng dấu: một quả cầu đá | — | **0 lựa chọn** — 3 dòng ✓ + 1 nút | con dấu Hồ Sơ Mặt Trăng, phần 1 |

⚠️ Chặng 5 phải theo đúng khuôn bước ⑦ của M-01: **ba dòng có dấu ✓ nhắc lại thứ trẻ vừa tự tìm
ra, một nút, không lựa chọn nào.**

---

### MOON-02 · Vì sao Trăng đổi hình
- **Chủ đề:** pha Mặt Trăng do **hướng nhìn**, không do bóng Trái Đất che.
- **Câu hỏi lớn:** *Trăng khuyết đi đâu mất?*
- **Cảnh dùng lại:** sơ đồ Mặt Trời–Trái Đất–Mặt Trăng nhìn từ trên (SVG, **không** phải ảnh).
- **Asset ảnh mới:** không · **Lớp phủ cần vẽ:** ⟳ **nửa sáng/nửa tối của một quả cầu** (dùng lại ở MOON-03)

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Đi một vòng | K2 | mở lần lượt các pha theo đúng thứ tự | vòng pha khép kín |
| 2 | Có phải Trái Đất che không? | K3 | đoán nguyên nhân | cảnh **bác** đáp án phổ biến ra mặt |
| 3 | Đưa Trăng về đúng chỗ | **K6** | kéo Mặt Trăng trên quỹ đạo tới vị trí cho ra pha đang hỏi | thanh đo góc chạy **liên tục**, không có trạng thái thua |
| 4 | Sáng ít, sáng nhiều | K5 | xếp 4 pha lên thang **phần được chiếu sáng** | cột pha từ tối tới tròn |
| 5 | Đóng dấu: nửa quả cầu luôn có nắng | — | **0 lựa chọn** | con dấu, phần 2 |

⚠️ **Bẫy nội dung:** *"một nửa Mặt Trăng luôn được chiếu sáng"* là câu đúng và mạnh; *"nửa kia là
mặt tối vĩnh viễn"* là câu **sai** — nửa được chiếu sáng **đổi chỗ**. MOON-03 sống nhờ đúng chỗ này.

---

### MOON-03 · Một mặt luôn quay về ta
- **Chủ đề:** khoá thuỷ triều — và **"mặt xa" ≠ "mặt tối"**.
- **Câu hỏi lớn:** *Vì sao từ Trái Đất ta chưa bao giờ nhìn thấy phía bên kia?*
- **Cảnh dùng lại:** sơ đồ của MOON-02 + bản đồ **mặt xa**.
- **Asset ảnh mới:** ✅ bản đồ mặt xa *(bức thứ hai của cùng bộ)* · **Lớp phủ cần vẽ:** ⟳ dùng lại của MOON-02

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Chỉnh nhịp quay | **K6** | chỉnh tốc độ tự quay cho khớp vòng quanh Trái Đất | mặt có hình thỏ **đứng yên** hướng về Trái Đất |
| 2 | "Mặt tối" có tối không? | K3 | đoán | cảnh bác đáp án, nắng quét qua mặt xa |
| 3 | Bên kia trông thế nào | K1 | chạm các vùng trên bản đồ mặt xa | thẻ: gần như **không có** vệt tối lớn |
| 4 | Gần hay xa? | K4 | kéo 6 đặc điểm vào hai rổ *mặt gần / mặt xa* | hai cột đầy dần |
| 5 | Đóng dấu: bị khoá | — | **0 lựa chọn** | con dấu, phần 3 |

---

### MOON-04 · Một ngày trên Mặt Trăng
- **Chủ đề:** không có không khí thì mọi thứ khác đi.
- **Câu hỏi lớn:** *Đứng trên Mặt Trăng thì thấy gì, nghe gì?*
- **Cảnh dùng lại:** bản đồ mặt gần + lớp phủ. **Asset ảnh mới:** không
- **Lớp phủ cần vẽ:** ⟳ **bầu trời đen giữa ban ngày** (dùng lại ở MOON-05)

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Xếp ba lô | K4 | chọn mang gì, bỏ lại gì | ba lô đầy dần, món sai bị trả lại nhẹ nhàng |
| 2 | Vì sao trời đen? | K3 | đoán | trời chuyển đen ngay giữa ban ngày |
| 3 | Nắng và bóng râm | K5 | xếp 3–4 nơi lên thang **nóng ↔ lạnh** | cột nhiệt độ |
| 4 | Dấu chân còn đó | K1 | chạm nơi có dấu chân | thẻ: không gió, không mưa |
| 5 | Đóng dấu: một nơi không có không khí | — | **0 lựa chọn** | con dấu, phần 4 |

⚠️ `[CẦN KIỂM]` **mọi con số nhiệt độ.** Chặng 3 làm được bằng **thang định tính** (rất nóng /
nóng / lạnh / rất lạnh) nếu không mở được nguồn ở mức trẻ em — đúng lối bước ④ của M-01 đã dùng
cho hai trong bốn nơi.
⚠️ **Không đụng "trọng lực 1/6 · thả rơi"** — Phòng Nghiên Cứu **đã dạy** (LAB-01 miễn phí,
LAB-03 cân nặng 4 nơi). Dạy lại là một khu nói lại thứ khu kia vừa nói.

---

### MOON-05 · Dấu chân đầu tiên
- **Chủ đề:** con người đã tới đó thật, ở những nơi có toạ độ thật.
- **Câu hỏi lớn:** *Người ta lên Mặt Trăng rồi làm gì ở đó?*
- **Cảnh dùng lại:** bản đồ mặt gần + marker. **Asset ảnh mới:** không · **Lớp phủ:** ⟳ dùng lại của MOON-04

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Những nơi đã đặt chân | K1 | chạm các điểm hạ cánh trên bản đồ | mỗi điểm một thẻ tên + năm |
| 2 | Một chuyến đi gồm những gì | K2 | mở lần lượt các chặng của chuyến bay | đường đi khép kín: đi → tới → về |
| 3 | Mang gì về nhà? | K4 | kéo thứ mang về vào khay mẫu vật | khay đầy dần |
| 4 | Vì sao dấu chân còn nguyên | K3 | đoán | cảnh trả lời bằng chính bài học MOON-04 |
| 5 | Đóng dấu: có người từng đứng đây | — | **0 lựa chọn** | con dấu, phần 5 |

⚠️ **Toạ độ điểm hạ cánh phải là toạ độ THẬT trên bản đồ thật** — đây đúng ca `js/earth2d.js`
đã ghi luật: bản đồ **phẳng** thì lat/lon quy ra phần trăm chính xác tuyệt đối; ảnh **quả cầu**
thì không. Đặt marker lên nhầm loại ảnh là **dạy sai địa lý**.

---

### MOON-06 · Nước đá trong bóng tối
- **Chủ đề:** có những chỗ ở hai cực **chưa bao giờ thấy nắng**, và ở đó có nước đá.
- **Câu hỏi lớn:** *Trên một nơi khô cằn như thế, tìm nước ở đâu?*
- **Cảnh dùng lại:** bản đồ mặt gần, khung nhìn vùng cực. **Asset ảnh mới:** không
- **Lớp phủ cần vẽ:** vùng bóng vĩnh cửu *(chỉ dùng ở đây — để trần, không đánh ⟳)*

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Đáy hố ở vùng cực | K1 | chạm các hố vùng cực | thẻ: đáy hố không nhận nắng |
| 2 | Nơi nào nắng chiếu tới? | K5 | xếp 4 chỗ lên thang **nhận nắng nhiều ↔ không bao giờ** | cột dựng lên = lời giải thích |
| 3 | Vì sao lại tìm nước ở đó? | K3 | đoán | thẻ nội dung |
| 4 | Nước để làm gì | K4 | kéo 4 công dụng vào ô | bảng đầy dần |
| 5 | Đóng dấu: có nước ở đây | — | **0 lựa chọn** | con dấu, phần 6 |

⚠️⚠️ `[CẦN KIỂM — nhiều nhất trong cả bộ]`: *có nước đá ở vùng cực Mặt Trăng không · ở dạng gì ·
bao nhiêu*. **Không viết một con số nào trước khi Gemini mở được trang NASA và trích nguyên văn.**
Đây là chủ đề mà tóm tắt của cỗ máy tìm kiếm hay nói quá tay, và dự án **đã ba lần** dẫn một
trang NASA cho một câu trang đó không hề nói.

---

### MOON-07 · Đóng dấu Hồ Sơ Mặt Trăng
- **Chủ đề:** chốt cả chuỗi — Mặt Trăng là **vệ tinh** của Trái Đất, và vì sao ta quay lại.
- **Câu hỏi lớn:** *Mặt Trăng là gì đối với Trái Đất?*
- **Cảnh dùng lại:** sơ đồ MOON-02 + bản đồ. **Asset ảnh mới:** không · **Lớp phủ:** ⟳ dùng lại

| # | Chặng | Khuôn | Trẻ QUYẾT ĐỊNH điều gì | Kết quả nhìn thấy được |
|---|---|---|---|---|
| 1 | Vệ tinh nghĩa là gì | K3 | đoán vì sao **Mặt Trăng và trạm vũ trụ cùng gọi là "vệ tinh"** | thẻ nội dung *(câu này lấy từ review của Gemini)* |
| 2 | Ai đang bay quanh ai | K1 | chạm để soi từng vật thể | quan hệ quay quanh hiện ra |
| 3 | Vì sao quay lại | K2 | mở lần lượt các lý do | danh sách đầy dần |
| 4 | Đóng dấu Hồ Sơ Mặt Trăng | — | **0 lựa chọn** — 6 con dấu của 6 nhiệm vụ trước ghép lại | hồ sơ hoàn chỉnh |

⚠️ **Không viết một mốc thời gian nào** cho chương trình quay lại Mặt Trăng: ngày phóng là thứ
đổi liên tục, và một con số đúng hôm nay sẽ thành **một câu sai** trong sáu tháng — cùng loại
lỗi với đồng hồ đếm ngược đứng ở `00 00 00 00` suốt ba ngày.

---

## 6. Ba thứ CỐ Ý không đề xuất

1. **Thuỷ triều.** Đã chốt ở Trái Đất (phương án (a) của bản đính chính). Đưa lên Mặt Trăng là
   **mở lại một quyết định đã chốt** — và nếu mở thì phải mở tường minh, không phải lặng lẽ.
   *(Ghi chú: `lab:tide` ở Phòng Nghiên Cứu cũng đang giữ chỗ cho chủ đề này.)*
2. **Nhật thực / nguyệt thực.** Nó cần **cả ba** thiên thể và một sơ đồ tỉ lệ; nhét vào MOON-02
   là chặng thứ sáu của một nhiệm vụ đã đủ. Để dành làm **MOON-08** nếu 7 cái này đo ra rẻ.
3. **Trọng lực 1/6 và thả rơi.** Phòng Nghiên Cứu đã giao (LAB-01 · LAB-03, có nguồn Apollo 15
   nguyên văn). Một nhiệm vụ dạy lại đúng thứ đó là hai khu nói cùng một câu.

---

## 7. Giả định tôi đang dựa vào

- Tôi giả định **7 nhiệm vụ ở một ĐIỂM ĐẾN**, không phải 7 chặng của một nhiệm vụ. Nếu ý là
  *"một nhiệm vụ Mặt Trăng có 7 chặng"* thì bản này **thừa 6 nhiệm vụ** — nói một câu là tôi gộp
  lại thành một MOON-01 bảy chặng, và khi đó 5 trong 6 chốt chặn ở mục 3 **vẫn còn nguyên**
  (chỉ mục 3.4 và 3.6 biến mất).
- Tôi giả định **tách 3 khuôn ra dùng chung** là việc sẽ làm, chứ không chép sang file thứ hai.
- Tôi giả định **cổng 70% giữ nguyên** và Mặt Trăng vẫn là điểm đến cuối của `Route`.
- *[Suy luận]* Tôi giả định một bản đồ Mặt Trăng xám vẫn đủ hấp dẫn cho trẻ nếu có marker màu và
  lớp phủ — **chưa kiểm chứng**, và đây là rủi ro thẩm mỹ lớn nhất của cả bộ.

## 8. Cái tôi KHÔNG chắc

- **Toàn bộ số liệu khoa học** trong 7 nhiệm vụ: tôi **chưa đọc** một trang NASA nào cho chúng —
  chỉ kiểm URL trả 200. Mọi chặng đều phải qua Gemini trích nguyên văn trước khi viết chữ.
- **Mức giảm chi phí sau khi tách khuôn** — con số này chỉ có sau MOON-01.
- **Chất lượng ảnh bản đồ Mặt Trăng** ở cỡ hiển thị thật: chưa tải, chưa xem, chưa đo độ sáng.
- **7 nhiệm vụ ở một nơi có quá dài không** cho một đứa trẻ 8–15 — `docs/decisions/001` vẫn
  đang mở đúng câu này.

## 9. Phương án nhỏ hơn nếu quá tốn

**Giữ MOON-01 · MOON-02 · MOON-03, bỏ bốn cái còn lại.**

Ba cái đó là một hành trình hoàn chỉnh (*bề mặt là gì → vì sao đổi hình → vì sao chỉ thấy một
mặt*), dùng **cả hai bức ảnh** của cùng một bộ asset, và **trả trọn tiền cho khuôn 6** bằng hai
ca dùng chung một định nghĩa góc — tức món đắt nhất được dùng đúng số lần đáng dùng.

**Cắt sâu hơn nữa:** chỉ **MOON-01**, 5 chặng, 1 asset, 0 lớp phủ mới, 0 khuôn mới. Đó là phép
đo mà `decisions/001` đang chờ, và nó biến ô "đang được xây" của Mặt Trăng thành một nơi chơi được.

⚠️ **Không cắt theo hướng "giữ 7 nhiệm vụ nhưng mỗi cái 3 chặng"** — dưới 5 chặng thì không thành
một hành trình, và luật 5–7 chặng đã chốt ở đề bài 05/08.

---

## 10. Việc phải chốt trước khi code

1. ⚠️⚠️ **Tách `Mission.Planet` thành `Place` + `Planet?`** (mục 3.1) — chặn mọi thứ còn lại,
   vì không sửa thì nhiệm vụ Mặt Trăng đầu tiên mở sai huy hiệu `planet-8`.
2. ⚠️⚠️ **Chủ dự án đặt ảnh bản đồ Mặt Trăng** (mặt gần + mặt xa) vào `img/` (mục 3.2).
3. **Tách `dragDrop` / `buildAsk` / `buildXsec`** khỏi `mission-earth.html` (mục 3.3) —
   đây là bước 4 của `decisions/002`, chưa làm.
4. **Sửa `f_moon_1` và `f_moon_3`** ở `js/locks.js` (mục 3.5) — `f_moon_3` hôm nay đang sai.
5. **Chốt luật cổng cho một nơi có nhiều nhiệm vụ** (mục 3.6).
6. **Mang cơ chế gấp** từ `scratchpad/proto-planet.js` sang `mission-planet.html` (mục 3.4).
7. **Gửi Gemini** danh sách `[CẦN KIỂM]` của cả 7 nhiệm vụ, nặng nhất là MOON-06 (nước đá).
