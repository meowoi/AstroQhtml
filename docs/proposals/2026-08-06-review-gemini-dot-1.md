# RÀ SOÁT ĐỢT 1 CỦA GEMINI — 3 thẻ + 60 câu

> Ngày 06/08/2026 · Đã **mở từng trang nguồn và tìm từng câu trích bằng máy**, không
> đọc lướt. Kết quả đo ghi nguyên ở dưới để bạn kiểm lại được.

## Phần làm ĐÚNG — nói trước cho công bằng

**Bốn URL đều sống (200)** và **các câu trích đều CÓ THẬT trên trang.** Đây là điều đáng
kể: hai vòng trước dự án đã hai lần dẫn một trang NASA cho một câu mà trang đó không hề
nói, nên tôi vào kiểm với kỳ vọng thấp. Gemini **không bịa nguồn**.

Cấu trúc cũng đúng: `term` duy nhất, song ngữ đủ, `lv` ba bậc, 20 câu mỗi thẻ, `q` của
thẻ khớp khoá câu. Ba thẻ đọc lên đều dùng được — phần `gr` (ví dụ đời thường) là phần
tốt nhất: *"giống ngọn lửa bếp gas, chân lửa xanh nóng hơn ngọn cam"* và *"giơ bàn tay
che đèn phòng"* đúng là chỗ trẻ hiểu ra.

---

## ⛔ NHƯNG: 13 / 40 câu khẳng định điều NGUỒN KHÔNG NÓI

Đây không phải bịa nguồn — nó tinh vi hơn và vì thế nguy hiểm hơn: **lấy một câu CÓ THẬT
nhưng không chứng minh được điều câu hỏi khẳng định.**

Rõ nhất là câu *"A star's color tells us how hot or cold it is."* — một câu chung chung,
được dùng làm `srcQuote` cho **sáu** câu hỏi khác nhau, trong đó có phân loại quang phổ,
định luật Planck và máy quang phổ của Hubble.

### Đo được: `spaceplace.nasa.gov/star-cookies/en/` KHÔNG chứa

```
OBAFGKM · spectral · Planck · white dwarf · red dwarf · spectrometer · Betelgeuse · Rigel
```

⇒ **8 câu dẫn một trang không nói gì về nội dung của chúng:**

| Câu | Khẳng định | Trang có nói? |
|---|---|---|
| `star-color-08` | Betelgeuse là sao đỏ ~3.000 °C | ✗ không nhắc Betelgeuse |
| `star-color-09` | Rigel là sao xanh >11.000 °C | ✗ không nhắc Rigel |
| `star-color-11` | Dãy quang phổ O B A F G K M | ✗ không có chữ "spectral" |
| `star-color-12` | Sao lùn trắng | ✗ |
| `star-color-13` | Mặt Trời là lớp G2V | ✗ |
| `star-color-14` | Định luật Planck | ✗ |
| `star-color-15` | **Sao lùn đỏ chiếm 70–75%** | ✗ — và đây là một **CON SỐ** |
| `star-color-20` | Hubble/JWST dùng máy quang phổ | ✗ |

### Đo được: `science.nasa.gov/moon/eclipses/` KHÔNG chứa

```
Baily · Saros · 375 · "at least 2" · diamond ring
```

⇒ **5 câu nữa:** `eclipse-13` (Hạt Baily) · `eclipse-14` (**375 năm**) ·
`eclipse-17` (Vòng Nhẫn Kim Cương) · `eclipse-19` (**ít nhất 2 lần/năm**) ·
`eclipse-20` (**chu kỳ Saros 18 năm 11 ngày**).

⚠️ Trang này thì **có** `umbra` · `penumbra` · `corona` · `annular` · `hybrid` ·
`5 degrees` — nên `eclipse-09`, `-10`, `-11`, `-12`, `-08`, `-18` là **đúng nội dung**,
chỉ **trích sai câu**. Bốn câu đó chỉ cần thay `srcQuote` bằng câu thật, ví dụ:
*"The Moon travels through Earth's penumbra, or the faint outer part of its shadow."*

---

## ⛔ Một câu trích là DIỄN GIẢI được viết như trích nguyên văn

`eclipse-05` (Trăng Máu) ghi:

> `srcQuote: "The remaining light reflects onto the Moon's surface with a red glow"`

Câu đó **không có trên trang**. Câu thật là:

> *"When Earth is positioned precisely between the Moon and Sun, Earth's shadow falls upon
> the surface of the Moon, dimming it and sometimes turning the lunar surface a striking
> red over the course of a few hours."*

Viết lại một ý rồi đặt trong dấu ngoặc kép là **đúng thứ trường `srcQuote` sinh ra để
chặn**. Nếu chỉ đọc câu trích mà không mở trang thì không có cách nào phát hiện.

⚠️ Kèm một chỗ nhỏ nhưng phải sửa: bốn câu (`-02`, `-09`, `-11`, `-15`) trích
*"…between the Moon and **the** Sun"* trong khi trang viết *"…between the Moon and
**Sun**"*. Thừa một chữ. Trích nguyên văn thì phải nguyên văn.

---

## ⛔ `star-color-05` rơi đúng cái bẫy đề bài đã đặt tên

Câu hỏi: *"Nhiệt độ bề mặt Mặt Trời khoảng bao nhiêu?"* → đáp án **5.500 °C**,
`srcQuote: "and 10,000 degrees Fahrenheit on the surface."`

Nguồn nói **°F**, câu hỏi hỏi **°C**. Con số quy đổi đúng, nhưng **NASA không nói
5.500 °C** — và đề bài liệt kê đúng ca này: *"quy đổi đơn vị rồi coi kết quả là số của
nguồn"*. Sửa: hỏi thẳng theo °F, hoặc viết *"khoảng 5.500 °C (10.000 °F theo NASA)"*.

---

## ⚠️ `a: 0` ở gần như MỌI câu — và đó là cùng một triệu chứng với đáp án nhảm

Đáp án đúng nằm ở vị trí 0 ở hầu hết 40 câu. Trên màn hình thì **không sao** —
`shuffleOptions()` trộn lại mỗi lần hiện câu. Nhưng nó là dấu vết của cách viết: **viết
đáp án đúng trước, rồi độn ba cái sau cho đủ.** Và ba cái độn đó lộ ra ngay:

> *"Do người ngoài hành tinh bật đèn đỏ"* · *"Kính bơi chống nước"* · *"Phải chui xuống
> đất"* · *"Máy chụp ảnh đĩa mềm"* · *"Vì sao xanh lá bị Trái Đất hút mất"* ·
> *"Phải đeo kính râm dính keo"* · *"Trái Đất ngừng di chuyển"*

Đề bài yêu cầu **mỗi đáp án sai là một hiểu lầm phổ biến CÓ THẬT**. Một câu bốn lựa chọn
mà ba cái vô lý thì **không đo được gì** — trẻ chọn đúng bằng cách loại trừ chứ không
bằng cách hiểu. Đây là lỗi hệ thống, không phải vài chỗ lẻ.

Ví dụ sửa cho `eclipse-04` (kính xem nhật thực):
- ✗ *"Kính bơi chống nước"* → ✓ *"Kính râm thường"* (rất nhiều người lớn tin là đủ)
- ✗ *"Phải chui xuống đất"* → ✓ *"Phim chụp X-quang hoặc kính hàn"* (mẹo dân gian có thật)
- ✗ *"Không cần đeo gì"* → ✓ *"Nhìn qua mặt nước phản chiếu"* (cũng là mẹo có thật, cũng sai)

---

## Ba chỗ nhỏ

**① Dùng URL dạng chuẩn có `/en/`.** Cả bốn link đều **chuyển hướng**:
`spaceplace.nasa.gov/star-cookies/` → `…/star-cookies/en/`. Ghi thẳng dạng đích.

**② `term` đặt theo SỐ THỨ TỰ (`star-color-01…20`) — bank hiện tại đặt theo NỘI DUNG**
(`star-fusion`, `planet-count`, `dwarf-ceres`). Khoá theo số thì xoá một câu là cả dãy
lệch nghĩa, và đọc log tiến độ của trẻ không hiểu gì. Đề nghị: `star-color-hottest`,
`star-color-sun-yellow`, `eclipse-moon-between`…

**③ `cat: "earth"` — an toàn, đã kiểm.** `cat` được khai ở cả 15 thẻ nhưng **không có
dòng nào trong `codex.html` đọc tới nó** (bộ lọc Phân loại chưa dựng). Nên thêm giá trị
mới không làm vỡ gì. Cứ dùng.

---

## Chưa đọc được

Tin nhắn bị cắt ở giữa `eclipse-20`, nên tôi **chưa xem**: 5 bài đọc · **Mục 0** (bao
nhiêu URL bạn thật sự mở) · **Mục 2** (danh sách 35 thẻ đề nghị) · Mục 3. Mục 2 mới là
thứ quyết định hình dạng cả 1.000 câu — gửi riêng phần đó.

---

## Việc tiếp theo — theo thứ tự

1. **13 câu không có nguồn: chọn một trong hai** — đổi sang trang NASA thật sự nói điều
   đó, **hoặc viết lại câu hỏi cho không cần khẳng định đó**. ⛔ Đừng giữ nguyên câu hỏi
   rồi đổi câu trích cho có.
2. **Sửa `eclipse-05`** — dùng câu thật đã trích ở trên.
3. **Viết lại toàn bộ đáp án sai** theo hiểu lầm có thật. Đây là việc nặng nhất và cũng
   là việc làm nên chất lượng bộ câu hỏi.
4. **Đổi khoá `term` sang tên theo nội dung.**
5. Gửi **Mục 0 · Mục 2 · 5 bài đọc**.
6. Rồi **dừng chờ phản hồi** — vẫn chưa nhân lên.

## Và một luật mới cho `srcQuote`, thêm vào đề bài từ nay

> **Đọc riêng câu trích, không nhìn câu hỏi: nó có làm cho đáp án đúng trở thành đúng
> không?**
>
> Nếu câu trích đúng với cả bốn lựa chọn — hoặc đúng với một chủ đề rộng hơn nhiều so với
> điều câu hỏi khẳng định — thì nó **không phải bằng chứng**, chỉ là một câu cùng chủ đề.

Đó chính là chỗ 13 câu ở trên trượt: *"A star's color tells us how hot or cold it is"* là
một câu thật, đúng, và **không chứng minh được bất cứ điều gì về Planck hay Betelgeuse**.
