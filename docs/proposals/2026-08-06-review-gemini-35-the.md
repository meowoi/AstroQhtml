# RÀ SOÁT MỤC 2 — danh sách 35 thẻ đề nghị

> Ngày 06/08/2026 · Đã đối chiếu từng thẻ với **15 thẻ đang chạy thật**, với nội dung
> Nhiệm vụ 01, và với 20 nhiệm vụ ChatGPT đang viết song song.

## Trước hết: đây là lỗi của ĐỀ BÀI, không phải của bạn

Đề bài viết *"Sổ Tay Thuật Ngữ hiện có **15 thẻ**"* nhưng **không liệt kê 15 thẻ đó ra**.
Nên bạn không có cách nào biết mình đang đề xuất lại thứ đã có. Danh sách đầy đủ:

```
term_star  term_planet  term_dwarf_planet  term_moon  term_asteroid
term_comet  term_meteoroid  term_meteor  term_meteorite  term_exoplanet
term_black_hole  term_gravity  term_nebula  term_supernova  term_cmb
```

---

## ⛔ 5 thẻ TRÙNG với thẻ đã có

| Bạn đề nghị | Đã tồn tại | Mức |
|---|---|---|
| `term_black_hole` | **`term_black_hole`** | **trùng id y hệt** |
| `term_nebula` | **`term_nebula`** | **trùng id y hệt** |
| `term_supernova` | **`term_supernova`** | **trùng id y hệt** |
| `term_dwarf_planets` | `term_dwarf_planet` | ⚠️ **khác đúng một chữ `s`** |
| `term_exoplanets` | `term_exoplanet` | ⚠️ **khác đúng một chữ `s`** |

⚠️⚠️ **Hai cặp khác nhau một chữ `s` nguy hiểm hơn cả ba cặp trùng hẳn.** Trùng hẳn thì
lỗi nổ ra ngay lúc thêm vào. Còn `term_exoplanet` cạnh `term_exoplanets` thì **chạy êm**:
Sổ Tay hiện hai thẻ gần giống nhau, trẻ mở được thẻ này mà thẻ kia vẫn khoá, và người sửa
sau đọc lướt sẽ tưởng là một. Dự án đã trả giá đúng loại lỗi này một lần — một phép kiểm
lọt vì `"map01Seen"` là **tiền tố** của `map01SeenAt`.

⇒ **Bỏ 5 thẻ này khỏi danh sách.**

---

## ⚠️ 7 thẻ CHỒNG LẤN — giữ được, nhưng phải nói rõ quan hệ

| Bạn đề nghị | Chồng với | Nhận xét |
|---|---|---|
| `term_moon_phases` | `term_moon` | ✓ giữ — pha Trăng là thứ khác hẳn "vệ tinh tự nhiên là gì" |
| `term_asteroid_belt` | `term_asteroid` | ✓ giữ — vành đai là một NƠI, không phải một loại vật thể |
| `term_comet_tail` | `term_comet` | ✓ giữ — cấu tạo đuôi đủ sâu để đứng riêng |
| `term_gas_giants` | `term_planet` | ✓ giữ |
| `term_ice_giants` | `term_planet` | ✓ giữ |
| `term_rocky_planets` | `term_planet` | ✓ giữ |
| `term_meteor_shower` | **`term_meteoroid` + `term_meteor` + `term_meteorite`** | ⚠️ **ba thẻ đã có sẵn về đúng họ này** — mưa sao băng là thẻ thứ tư. Cân nhắc bỏ |

Bảy thẻ này là **mở rộng**, không phải trùng lặp — nhưng phần `def` của chúng **phải nối
vào thẻ gốc** (*"Đây là các pha của vệ tinh tự nhiên — xem thẻ Vệ tinh tự nhiên"*) chứ
đừng định nghĩa lại từ đầu. Định nghĩa hai lần là hai chỗ sẽ lệch nhau.

---

## ⚠️ 6 thẻ ĐỤNG VÀO NHIỆM VỤ — và đây là chỗ ĐÁNG GIÁ NHẤT của cả danh sách

ChatGPT **đang viết song song** 20 nhiệm vụ chính ở Trái Đất. Bốn thẻ của bạn trùng đúng
tên bốn nhiệm vụ đó:

| Thẻ bạn đề nghị | Nhiệm vụ ChatGPT đang viết |
|---|---|
| `term_water_cycle` | **M-02 · Hành Trình Của Một Giọt Nước** |
| `term_earth_seasons` | **M-03 · Bốn Mùa Trên Trái Đất** |
| `term_ocean_tides` | **M-05 · Con Nước Ven Biển** |
| `term_plate_tectonics` | nằm trong danh sách chủ đề đã gợi ý cho M-07→M-21 |

Cộng hai thẻ đụng nội dung **đã phát hành**:
- `term_earth_atmosphere` — Nhiệm vụ 01 bước ① đã dạy *78% nitơ / 21% oxy*
- `term_day_night_cycle` — đã dạy ở **nhịp 0** của màn Comet dẫn đường (trẻ tự xoay quả
  cầu 3D để thấy nửa ngày / nửa đêm), và M-03 vừa được yêu cầu **cắt bỏ** phần này

⚠️ **Đừng coi đây là xung đột — đây là thứ cả hệ thống đang thiếu.** Hiện tại chơi xong
một nhiệm vụ thì **không mở được thẻ Sổ Tay nào**; Sổ Tay chỉ mở bằng câu quiz. Nếu thẻ
khớp nhiệm vụ thì: *chơi xong M-02 → mở thẻ Vòng Tuần Hoàn Nước*. Đó chính là **hệ quả**
mà 1.000 câu đang thiếu.

⇒ **Giữ cả sáu thẻ**, nhưng viết `def`/`gr` **khớp với những gì nhiệm vụ dạy**, đừng dạy
một phiên bản thứ hai. Cụ thể, phải bám ba ràng buộc đã chốt của dự án:
- ⛔ **Mùa và khí hậu KHÔNG do khoảng cách tới Mặt Trời** — nguyên nhân là **góc chiếu**.
  Thẻ nào chạm tới thì phải **bác quan niệm đó ra mặt**, không chỉ tránh không nhắc.
- ⛔ **Đừng viết "vùng cực lúc nào cũng nhận ít năng lượng hơn"** — chính trang NASA dự
  án đang dẫn ghi rằng năng lượng nhận **trong một ngày** cao nhất lại ở vĩ độ cao vào
  mùa hè.
- ⚠️ **Thuỷ triều:** một ngày có **hai** lần triều lên vì có **hai** chỗ nước dâng, kể cả
  phía **đối diện** Mặt Trăng. Nói mỗi *"Mặt Trăng kéo nước lên"* là bán phần.

---

## ⚠️ Hai thứ cùng tên "codex" — nói ra để bạn không nhầm

Dự án có **hai** hệ thống khác nhau cùng mang chữ *codex*:

1. **`learningdata/astronomy/earth_codex.json`** — bài đọc mở theo **bước nhiệm vụ**
   (9 mẫu, khớp `Step.Codex` của server).
2. **`js/codex-terms.js`** — **Sổ Tay Thuật Ngữ**, mở theo **câu quiz** (15 thẻ) ← thứ
   bạn đang viết.

Hai cái **chưa nối với nhau**. Việc nối là của Claude; bạn cứ viết đúng hình dạng ở mục
2b của đề bài.

---

## Thứ tự làm — có một đợt RẺ HƠN HẲN mà danh sách đang bỏ qua

**15 thẻ đang chạy có ĐÚNG 2 CÂU HỎI MỖI THẺ.** Nâng chúng lên 20 câu là:

```
15 thẻ × 18 câu thêm = 270 câu
   0 thẻ mới · 0 icon mới · 0 rủi ro trùng id
```

Đây là chỗ rẻ nhất và chắc chắn nhất trong cả 1.000 câu — và nó làm **15 thẻ đã có
trong tay trẻ** dùng được lâu hơn ngay lập tức.

⇒ Đề nghị thứ tự:

| Đợt | Việc | Câu | Icon mới |
|---|---|---:|---:|
| **1** ✓ | 3 thẻ mới (đang sửa lại) | 60 | 3 |
| **2** | **Đào sâu 15 thẻ ĐÃ CÓ: 2 → 20 câu** | **270** | **0** |
| 3 | 10 thẻ Trái Đất & khí quyển | 200 | 10 |
| 4 | 15 thẻ thiên văn còn lại (sau khi bỏ 5 trùng) | 300 | 15 |
| 5 | 5 thẻ dụng cụ & khám phá | 100 | 5 |
| | **Tổng** | **930** | **33** |

**33 icon SVG là phần của Claude**, vẽ theo từng đợt cùng nhịp với nội dung.

---

## Ba thẻ đáng khen — chúng nối vào thứ app ĐÃ CÓ

- **`term_constellations`** — app đã có `js/constellations.js` (Đại Hùng · Thiên Hậu ·
  Lạp Hộ · Bọ Cạp) và cả một mini-game ghép chòm sao. Thẻ này nối thẳng vào đó.
- **`term_space_rovers`** — `js/articles.js` đã có bài về xe tự hành Perseverance.
- **`term_light_year`** — chưa chỗ nào trong app định nghĩa đơn vị này, mà nó xuất hiện
  trong bài đọc về tinh vân M42 (*"~1.300 năm ánh sáng"*). Đúng chỗ trống.

---

## Việc tiếp theo

1. **Bỏ 5 thẻ trùng**, xác nhận danh sách còn **30 thẻ**.
2. Với 7 thẻ mở rộng: viết `def` **nối vào thẻ gốc**, không định nghĩa lại.
3. Với 6 thẻ đụng nhiệm vụ: bám ba ràng buộc nội dung ở trên.
4. **Đợt 2 = đào sâu 15 thẻ đã có** (270 câu, 0 icon) — làm trước vì rẻ nhất và chắc nhất.
5. Và vẫn còn nợ **Mục 0** (bao nhiêu URL bạn thật sự mở) + **5 bài đọc** của Đợt 1.
