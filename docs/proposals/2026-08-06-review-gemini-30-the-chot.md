# RÀ SOÁT DANH SÁCH 30 THẺ — trước khi chạy Đợt 2

> Ngày 06/08/2026 · Đã đối chiếu từng thẻ với 15 thẻ đang chạy **và với 3 thẻ vừa nộp ở
> Đợt 1**. Danh sách tốt hơn hẳn bản trước; còn ba chỗ phải chốt.

## ⛔ ① `term_event_horizon` là NỘI DUNG LÕI của `term_black_hole` đã có

Bạn đã bỏ `term_black_hole` (đúng), nhưng `term_event_horizon` chính là **phần định nghĩa
chính** của thẻ đó. Đây là `def` đang chạy thật, nguyên văn:

> *"NASA định nghĩa lỗ đen là vật thể đặc tới mức lực hấp dẫn ngay dưới bề mặt của nó —
> gọi là **chân trời sự kiện** — mạnh đến mức KHÔNG GÌ thoát ra được, kể cả ánh sáng.
> **Chân trời sự kiện không phải một mặt…**"*

Hai trong ba câu của thẻ Lỗ Đen là về chân trời sự kiện. Tách nó ra thành thẻ riêng thì
hai thẻ nói cùng một điều, và thẻ nào cũng thiếu một nửa.

⇒ **Bỏ `term_event_horizon`.** Muốn đào sâu thì thêm câu hỏi vào chính `term_black_hole`
ở Đợt 2 — nó đang có **đúng 2 câu** (`black-hole`, `black-hole-light`).

---

## ⚠️ ② `term_lunar_eclipse` MÂU THUẪN với thẻ bạn vừa nộp ở Đợt 1

Đợt 1 bạn nộp **một** thẻ `term_solar_eclipse`, tên **"Nhật Thực & Nguyệt Thực"**, `def`
nói về **cả hai**, và 20 câu trộn lẫn cả hai (`eclipse-02`, `-05`, `-06`, `-15` là về
nguyệt thực). Nay danh sách lại tách thành hai thẻ.

**Phải chốt một hướng — và tôi nghiêng về TÁCH**, vì chính dự án đã có tiền lệ: họ
`meteoroid` / `meteor` / `meteorite` được tách thành **BA thẻ riêng** dù cùng một hiện
tượng. Với trẻ đang sưu tập, hai hiện tượng phân biệt được = hai thứ sưu tập được.

⇒ Nếu tách thì **phải sửa lại Đợt 1**:
- `term_solar_eclipse` — đổi tên thành **"Nhật Thực"**, `def` chỉ nói nhật thực
- `term_lunar_eclipse` — thẻ mới, **"Nguyệt Thực"**
- **Chia lại 20 câu** thành ~10 + ~10, và đổi khoá cho đúng nghĩa
- **Đợt 1 thành 4 thẻ**, không phải 3

---

## ⚠️ ③ `term_star_colour` BIẾN MẤT khỏi danh sách 30

Đợt 1 đã làm xong thẻ này, nhưng nó **không có trong cả ba nhóm A/B/C**. Nhóm A có 10,
B có 15, C có 5 — tổng đúng 30, nên phép cộng bên trong khớp; chỉ là thẻ đã làm rơi ra
ngoài.

### Phép cộng đúng sau khi sửa cả ba chỗ

```
30 thẻ đề nghị
 −  1  bỏ term_event_horizon
 +  1  thêm lại term_star_colour
 = 30 thẻ mới  →  30 icon SVG  (không phải 33)
```

Con số **33 icon** ở bảng của bạn đếm trùng: `term_solar_eclipse` và
`term_earth_atmosphere` nằm ở **cả** Đợt 1 **và** danh sách 30.

### Tổng số câu cũng phải sửa theo

| Đợt | Việc | Câu |
|---|---|---:|
| 1 | 4 thẻ (sau khi tách nhật/nguyệt thực) | 80 |
| 2 | Đào sâu 15 thẻ đã có: 2 → 20 câu | **270** |
| 3–5 | 26 thẻ mới còn lại × 20 | 520 |
| | **Tổng** | **870** |

**870, không phải 930.** Vẫn là con số tốt — và nếu muốn tròn 1.000 thì nâng vài thẻ
giàu nội dung lên 25–30 câu, đừng thêm thẻ.

---

## Bốn chỗ nhỏ

**① `term_magnetic_field` mất chữ "earth".** Bản trước là `term_earth_magnetic_field`.
Nó nằm trong nhóm Trái Đất nhưng cái tên thì không nói vậy — mà Sao Mộc, Mặt Trời đều có
từ trường. Giữ **`term_earth_magnetic_field`**.

**② `term_artificial_satellite` ↔ `term_moon` là một CẶP ĐẸP.** Thẻ đã có tên là
**"Vệ tinh tự nhiên"**. Hai thẻ nên trỏ vào nhau ngay trong `def` — đó là cách trẻ hiểu
ra vì sao Mặt Trăng và ISS lại cùng gọi là "vệ tinh".

**③ `term_neutron_star` chồng lấn `term_supernova` (đã có)** — sao neutron là thứ *còn
lại sau* siêu tân tinh. Giữ được, nhưng `def` phải quy chiếu về thẻ gốc như bảy thẻ mở
rộng kia.

**④ `term_weather_vs_climate` là thẻ MỚI, không có trong danh sách 35 ban đầu** — và nó
là một bổ sung tốt: phân biệt thời tiết với khí hậu đúng là chỗ trẻ (và người lớn) hay
lẫn. Giữ.

---

## Việc tiếp theo

1. Chốt **tách hay không tách** nhật/nguyệt thực. Tách thì sửa lại Đợt 1 trước.
2. Bỏ `term_event_horizon`, thêm lại `term_star_colour`, đổi `term_magnetic_field` →
   `term_earth_magnetic_field`. Xác nhận **30 thẻ**.
3. **Vẫn còn nợ Đợt 1:** 13 câu không có nguồn · `eclipse-05` trích sai · toàn bộ đáp án
   sai phải viết lại theo hiểu lầm có thật · **Mục 0** · **5 bài đọc**.
4. Rồi mới chạy **Đợt 2** (270 câu cho 15 thẻ đã có — rẻ nhất, 0 icon mới).

⚠️ Đợt 2 tuy rẻ nhưng **không được lỏng tay hơn**: 15 thẻ đó đang nằm trong tay trẻ thật,
nên một câu sai nguồn ở đó tới người dùng nhanh hơn bất cứ đợt nào khác. Luật `srcQuote`
vẫn nguyên: **đọc riêng câu trích, nó có làm đáp án đúng trở thành đúng không?**
