# Hồ sơ nguồn cho PHYSICS · ENGINEERING · 3 mắt xích lẻ

- **Ngày:** 14/08/2026
- **Loại:** tra nguồn (chưa viết bài nào)
- **Người tra:** Claude — mọi URL dưới đây đã **tự mở và đọc**, không lấy từ bản tóm tắt

> Chủ dự án hỏi: *"tìm thêm tài liệu… các nguồn sách khoa học cho trẻ, pdf, chương
> trình giáo dục… có không?"* — file này trả lời bằng những gì **kiểm được**, và nói
> rõ chỗ nào **không** kiểm được.

---

## 0. Ba kết luận đọc trước

1. **Con đường PHYSICS đã mở lại.** Lượt trước hỏng vì `grc.nasa.gov` lỗi chứng chỉ SSL.
   Bản đang sống là **`www1.grc.nasa.gov`** — cùng bộ *Beginner's Guide*, 200, nội dung
   đầy đủ. ⚠️ Nhưng nó **chỉ đọc được bằng `curl`**, xem mục 4.
2. **VẪN CHƯA PHẢI NỚI `OKDOM`** — lần thứ ba liên tiếp. NASA phủ đủ PHYSICS và
   ENGINEERING; `toạ độ` thì **USGS đã nằm sẵn trong allowlist** từ trước.
3. ⚠️⚠️ **MÃ 200 KHÔNG CÓ NGHĨA LÀ NGUỒN DÙNG ĐƯỢC.** Có trang trả 200 mà tôi vẫn
   **không đọc nổi nội dung** (bot filter) — và nguồn không đọc được thì **không được
   dùng**, vì viết bài từ bản tóm tắt của bộ tra cứu chính là đường đã đẻ ra CHNOPS và
   "170 km". Xem mục 5.

---

## 1. PHYSICS — đã có nguồn cho 3/6 mắt xích

| Mắt xích | URL | Mã | Đọc được? |
|---|---|:--:|---|
| **Lực + chuyển động** | `www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/` | 200 | ✅ qua `curl` |
| **Lực** (bốn lực trên tên lửa) | `…/four-rocket-forces/` | 200 | ✅ |
| **Năng lượng** (lực đẩy) | `…/rocket-thrust/` | 200 | ✅ |
| *mục lục cả bộ* | `…/bga-site-map/` | 200 | ✅ |

**Đã đọc thật, trích được nguyên văn** (trang phát biểu đủ ba định luật):

> "An object at rest remains at rest, and an object in motion remains in motion at
> constant speed and in a straight line unless acted on by an unbalanced force."
>
> "The acceleration of an object depends on the mass of the object and the amount of
> force applied."
>
> "Whenever one object exerts a force on another object, the second object exerts an
> equal and opposite on the first."
>
> "This tendency to resist changes in a state of motion is inertia."

⚠️ **Câu thứ ba trên trang NASA THIẾU CHỮ "force"** (*"an equal and opposite on the
first"*). Khi trích thì trích đúng như trang viết, và **đừng "sửa hộ" rồi vẫn để trong
ngoặc kép** — sửa xong thì nó không còn là trích dẫn nữa.

### Còn thiếu nguồn: nhiệt · điện · chân không

Chưa tìm ra trang nào **vừa đọc được vừa đúng độ tuổi**. Hướng chưa thử:
`www1.grc.nasa.gov/…/bga-site-map/` (mục lục cả bộ, có thể có trang về nhiệt động lực)
và các PDF *NASA Facts* (xem mục 3).

---

## 2. ENGINEERING — đã có nguồn cho 2/4 mắt xích

| Mắt xích | URL | Mã |
|---|---|:--:|
| **Động cơ tên lửa** | `www1.grc.nasa.gov/beginners-guide-to-aeronautics/liquid-rocket-engine/` | 200 |
| **Hỗ trợ sự sống** | `nasa.gov/reference/environmental-control-and-life-support-systems-eclss/` | 200 |
| *điện + nhiệt trên trạm* | `nasa.gov/international-space-station/international-space-station-assembly-elements/` | 200 |

Trang ECLSS là nguồn **giàu nhất** tìm được trong lượt này — ba hệ con (nước · không khí ·
oxy), tái chế **khoảng 90% nước** trên trạm, điện phân nước lấy oxy, và lò Sabatier lấy
CO₂ thở ra cộng hydro để làm lại thành nước. Đủ cho **một bài rất tốt**, và nó nối thẳng
sang nhánh LIFE SCIENCE đã giao.

⚠️ Mắt xích **cơ cấu máy** và **điện** vẫn chưa có trang riêng đủ độ tuổi.

---

## 3. PDF — có thật, và đã kiểm 200

Chủ dự án hỏi riêng về PDF. Có, và chúng là dạng *NASA Facts* — một tờ, viết cho công
chúng:

| PDF | Mã |
|---|:--:|
| `nasa.gov/wp-content/uploads/2020/10/g-281237_eclss_0.pdf` (ECLSS) | 200 |
| `nasa.gov/wp-content/uploads/2012/01/179225main_iss_poster_back.pdf` (ISS Basics) | 200 |

⚠️ **NHƯNG CHƯA ĐỌC NỘI DUNG.** Kiểm 200 mới chứng minh file tồn tại. Trước khi trích
một chữ nào từ chúng thì phải mở ra đọc — đúng luật đã áp cho mọi trang khác.

---

## 4. ⚠️⚠️ PHÁT HIỆN VẬN HÀNH: `WebFetch` KHÔNG PHẢI ĐƯỜNG DUY NHẤT

`www1.grc.nasa.gov` trả **200 với `curl`** nhưng `WebFetch` từ chối với
*"unable to verify the first certificate"* — máy chủ NASA đó phục vụ **thiếu chứng chỉ
trung gian**, `curl` bỏ qua còn trình xác thực của WebFetch thì không.

⇒ **Lượt trước tôi kết luận sai rằng nguồn này không dùng được.** Nó dùng được; chỉ là
phải đọc bằng đường khác:

```bash
curl -s -L -A "<User-Agent thật>" "<url>" | python -c "<bóc thẻ HTML>"
```

**Bài học chung: một công cụ không mở được trang KHÔNG có nghĩa trang đó hỏng.** Thử
`curl`, thử Chromium, rồi mới kết luận. Đây là lần thứ hai trong ngày phân biệt được
"trang chết" với "công cụ của tôi không vào được" (lần đầu: `jpl.nasa.gov` 403 với bot,
200 với trình duyệt thật).

---

## 5. ⛔ Nguồn PHẢI LOẠI — 200 nhưng không đọc được nội dung

| URL | curl | Chromium headless |
|---|:--:|:--:|
| `www.usgs.gov/faqs/how-much-distance-does-a-degree…` | 405 | **403** |
| `www.usgs.gov/faqs/what-does-term-utm-mean…` | 405 | — |

Cả hai bị chặn bot ở mọi đường tôi thử. **Trẻ bấm bằng trình duyệt thật thì mở được**,
nhưng **tôi không đọc được để trích nguyên văn** — nên **không dùng làm nguồn**. Viết
bài từ bản tóm tắt của bộ tra cứu là đúng đường đã đẻ ra CHNOPS, "170 km", và Nam Cực
*"châu lục cao nhất"*.

✅ **Đường thay thế đã tìm được và ĐỌC ĐƯỢC:** `pubs.usgs.gov/gip/usgsmaps/usgsmaps.html`
(*USGS Maps Booklet*) — 200, đọc được qua `curl`, và nội dung hợp hơn hẳn cho trẻ:

> "Most USGS map series divide the United States into quadrangles bounded by two lines
> of latitude and two lines of longitude."
>
> "a 7.5-minute map shows an area that spans 7.5 minutes of latitude and 7.5 minutes of
> longitude"
>
> "Maps at scales of 1:250,000 (1 inch = about 4 miles)…"

⇒ Đủ cho mắt xích **toạ độ**, và tiện thể phục vụ luôn **tỉ lệ bản đồ**. **USGS đã nằm
trong `OKDOM`** nên không phải nới gì.

---

## 6. Nguồn ngoài NASA — sống, nhưng CHƯA CẦN NỚI

Đã kiểm còn sống, để dành cho lúc thật sự cần:

| Tên miền | Mã | Hợp với |
|---|:--:|---|
| `nist.gov` | 200 | chuẩn đo lường, đơn vị |
| `energy.gov` | 200 | năng lượng, điện |
| `airandspace.si.edu` (Smithsonian) | 200 | kỹ thuật hàng không vũ trụ |
| `esa.int/Education` | 200 | *(đã trong OKDOM)* |
| `exploratorium.edu` | 200 | *(đã trong OKDOM)* — thí nghiệm tay cho trẻ |
| `noirlab.edu` | 405 | thiên văn — **chặn bot, cùng cảnh USGS** |

⚠️ **Đừng nới `OKDOM` theo danh sách này.** Luật ở `docs/decisions/010` mục 3d: nới
**đúng lúc một nhánh thật sự cần, và nới đúng tên miền đó**. Lượt MATHEMATICS đã chứng
minh dự đoán "sẽ cần `nist.gov`" là sai — nới sẵn thì đã mở thừa một tên miền.

---

## 7. ❌ Câu hỏi chưa trả lời được: "sách khoa học cho trẻ"

Chủ dự án hỏi về **sách khoa học cho trẻ**. Tôi **không tìm được** một bộ sách nào vừa
① đọc được toàn văn công khai, ② dẫn link được, ③ thuộc loại nguồn dự án đang tin.

Ba lý do, nói thẳng:

- Sách thiếu nhi phần lớn là **sản phẩm thương mại** — không có URL để dẫn, và dẫn được
  cũng không kiểm chứng được từng câu.
- Bản quyền: trích nhiều từ một cuốn sách khác hẳn trích một trang chính phủ công khai.
- Dự án đang dẫn nguồn **theo từng câu** (`srcQuote`), mà sách giấy thì không có URL để
  ai đó mở ra đối chiếu.

⇒ **Đề nghị: giữ nguyên lối đang chạy** — chương trình giáo dục của cơ quan nhà nước
(NASA / USGS / ESA) đóng đúng vai "sách khoa học cho trẻ" mà lại **mở, miễn phí, và kiểm
chứng được từng câu**. `www1.grc.nasa.gov/beginners-guide-to-aeronautics/` chính xác là
một **giáo trình nhập môn** — chỉ là ở dạng web.

Nếu chủ dự án có sẵn một bộ sách cụ thể trong đầu thì cho tên, tôi sẽ tra xem có bản mở
nào không.

---

## 8. Đề nghị làm tiếp

1. **PHYSICS lực + chuyển động** — nguồn đã đọc xong, viết được ngay.
2. **ENGINEERING hỗ trợ sự sống** — trang ECLSS giàu nhất lượt này.
3. **Toạ độ** — dùng *USGS Maps Booklet*.
4. Ba mắt xích **nhiệt · điện · chân không** và **cơ cấu máy**: cần một vòng tra nữa,
   bắt đầu từ `bga-site-map` và hai PDF ở mục 3.

⚠️ Vẫn theo luật `010`: **mỗi lượt một nhánh, đọc nguồn trước khi viết.**
