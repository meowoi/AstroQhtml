# 008. Trung Tâm Nhiệm Vụ là cửa trước · cây chặng đường uốn · ba luật khuôn mới

> Ngày 04–05/08/2026 · Trạng thái: **đã chốt phần điều hướng** (có bản mẫu, có phép kiểm) ·
> **đang mở phần nội dung** (20 nhiệm vụ / 20 việc hàng ngày / 3 sự kiện còn ở vòng soạn)

## Vì sao có quyết định này

Chủ dự án chơi thật rồi báo một chuỗi vấn đề nối nhau, mỗi cái lộ ra sau khi cái trước
được sửa:

1. Xong Hành Tinh Xanh thì **không biết tiếp theo là gì**.
2. Cây chặng dựng ra thì *"rối, khó nhìn với trẻ con"*, rồi *"sẽ bị kéo dài ngoằng khi
   thêm nhiệm vụ"*.
3. Bản A (gấp) và bản B (liền mạch) đều bị bác cùng một lý do: *"nhiệm vụ bị căn hết về
   phía trái, trống hết bên phải"*.
4. Bản đồ → chạm hành tinh → **một bảng trung gian** nói lại đúng thứ vừa bấm.
5. *"Nhiệm vụ hàng ngày và sự kiện sẽ để ở đâu? Nó không thuộc bất kì hành tinh nào."*

---

## Quyết định 1 — Ba tầng, và cửa trước là TRUNG TÂM NHIỆM VỤ

```
dashboard (MOD-04) → TRUNG TÂM NHIỆM VỤ → bản đồ → hành tinh → cây chặng
                          ↑ hàng ngày · sự kiện sống ở đây
```

**Nguyên tắc quyết định chỗ đặt: bản đồ tổ chức theo NƠI.** Thứ không có nơi thì đặt lên
bản đồ là phải bịa cho nó một toạ độ — **đúng lỗi sai tầng chủ dự án đã bắt** khi thấy
một nút Mặt Trăng nằm trong cây chặng của Trái Đất.

| Loại nhiệm vụ | Có thuộc một nơi? | Ở đâu |
|---|---|---|
| chính tuyến | có | bản đồ → hành tinh → cây chặng |
| phụ | **có** | danh sách nhiệm vụ của hành tinh đó |
| hàng ngày | không | **Trung Tâm Nhiệm Vụ** |
| sự kiện | không | **Trung Tâm Nhiệm Vụ** |

`missions.html` (MOD-04, tên đã chốt từ 29/07) chính là chỗ đang trống: từ khi bản đồ
nhảy thẳng vào cây chặng thì nó mất việc.

⚠️ **Thêm một tầng là thêm một cú chạm** — bù bằng dòng **"Chơi tiếp"** ở ngay đầu trang:
**2 cú chạm từ dashboard** tới chặng đang dở, **ít hơn** luồng cũ. Dòng đó **dùng chung**
với bản đồ (`proto-resume.css`), không chép hai bản.

## Quyết định 2 — Chạm nơi CÓ nhiệm vụ thì đi thẳng; nơi CHƯA có thì mới mở bảng

Bảng trung gian ở Trái Đất là một cửa không mở ra thông tin nào mới. Nhưng ở Mặt Trăng và
Sao Hoả thì bảng là chỗ **duy nhất** nói ra điều kiện mở và phân biệt *"chưa có nội dung"*
với *"bị cấm tới"* — bỏ nó là trẻ bấm rồi không có gì xảy ra, tức chỉ tưởng mình bấm trượt
(bài học `js/route-gate.js`).

## Quyết định 3 — Cây chặng: BỎ NHÃN CHỮ, cột vòng tròn uốn lượn giữa màn (bản C)

Gốc của *"trống hết bên phải"* **không phải căn lề mà là cái nhãn chữ**: tên chặng dài
nhất cũng chỉ ~250px trong cột 1060px, nên bề rộng còn lại không có gì để lấp. Đo được ở
cùng dữ liệu:

| | trống trái | trống phải | lệch |
|---|---|---|---|
| A (gấp) | 21px | 755px | **734px** |
| B (nhãn) | 21px | 696px | **675px** |
| **C (uốn)** | 424px | 424px | **0px** |

Duolingo và Candy Crush không có lỗi này vì **không có nhãn nào để mà lệch**. Tên chặng
chuyển về ba chỗ: `aria-label` · bong bóng trên chặng đang mở · bảng chi tiết khi chạm.

⚠️ **Khác hẳn lối so le đã bị bác ở bản 1** — cái bị bác là *nhãn chữ* nhảy trái–phải
(mắt phải đi zíc-zắc để **đọc**). Ở đây không có chữ nào trên đường.

⚠️ **Danh sách 11 nhiệm vụ phải chữa KHÁC**: ở đó không bỏ được nhãn (11 thứ khác nhau,
phải đọc tên mới chọn được) → dùng **hàng thẻ trải hết bề rộng** `[vòng tròn][tên · giãn
hết chỗ][mũi chỉ ›]`. Cùng một lỗi, hai cách chữa.

## Quyết định 4 — Bốn câu chủ dự án chốt

| Câu | Chốt |
|---|---|
| gọi là gì | **"chặng"** |
| chạm chặng chưa mở | **chặn hẳn** — `disabled` ở chính cái nút, không chặn bằng `if` |
| chơi xong một chặng | **HỎI** "tiếp hay dừng", không tự quyết |
| cây chặng đặt ở đâu | **trang riêng**, có URL + tham số |

⚠️ **Chặn hẳn thì phải trả lại chỗ nói lý do.** Bảng đang là chỗ duy nhất nói điều kiện
mở; bỏ nó mà không thay bằng gì là đúng bẫy cổng lộ trình. Ở cây chặng luật không đổi bao
giờ (tuyến tính) nên **một câu cố định luôn hiển thị** là đủ.

⚠️ **Hỏi "tiếp hay dừng" thì PHẢI tắt đường về tự động 5 giây** khi còn chặng sau. Đặt câu
hỏi hai lựa chọn rồi để đồng hồ chọn hộ là **tệ hơn không hỏi**.

⚠️ **Trang riêng — khảo sát nói mạnh hơn ý ban đầu**: ở cả ba tham chiếu, đường đi **là
màn chủ** (Duolingo tab *Learn* · Candy Crush là màn mở app · battle pass là một tab).
Không ai nhét nó vào trong một trang khác.

---

## BA LUẬT KHUÔN MỚI — rút ra khi ra đề cho ChatGPT vòng 20 nhiệm vụ

Ba luật này **áp cho mọi nhiệm vụ về sau**, không riêng vòng này.

### Luật A — Khuôn 6 (`orientation_align`) là **0 dòng mã**, không phải "đang trống"

```
dragDrop(        7 lần gọi     buildAsk(   5     buildXsec(  2
setEarthDrag(    0             stationAngleTo(   0
```

Hai hàm cuối **đã bị xoá** khỏi `js/earth2d.js` cùng bước `rotation` (`005`). Đề bài vòng
đầu viết *"đã đặc tả, đang trống"* → ChatGPT đọc thành *"đã dựng sẵn, chờ dùng"* và tiêu
nó **9 lần / 5 nhiệm vụ** (suy ra ~36 lần cho 20). Mà chúng không phải một khuôn: xoay
gió · canh hải lưu · dời Mặt Trăng · chỉnh trục nghiêng · lái đường bão — **mỗi cái một
cảnh, một định nghĩa góc, một thanh đo**.

⇒ **Tối đa 2 nhiệm vụ trong cả 20**, và hai cái đó phải **dùng chung MỘT định nghĩa góc**
(viết được *một* hàm phục vụ cả hai). Dùng đúng một lần thì nó **không phải khuôn** — nó
là cơ chế riêng, và phải được gọi đúng tên để chi phí nhìn ra đúng.

### Luật B — Có HAI ngân sách, và chúng có nút thắt khác nhau

| | Nút thắt | Trần |
|---|---|---|
| **asset ảnh** | chờ chủ dự án đặt ảnh gốc vào `img/` | **≤ 1 mỗi nhiệm vụ**, mặc định **0** |
| **lớp phủ CSS/SVG** | chỉ là mã | dùng lại được ở ≥2 nhiệm vụ thì đánh dấu **⟳** |

Vòng đầu khai ~22 asset / 5 nhiệm vụ (~88 cho 20) vì gộp hai loại làm một. Số đo để so:
dự án có **đúng 5 ảnh minh hoạ** (`img/era/*`) và chúng tốn **một file đề xuất riêng** +
thời gian chờ. M-01 có **4 lớp phủ cho 7 bước** (`--smog` · `.era-*` · `.me-era` ·
`.e2-night`) — đó là mật độ đáng noi theo.

⚠️ **Ngôn ngữ hình ảnh**: M-01 **không vẽ hoạt cảnh**, nó dùng ảnh vệ tinh NASA thật +
marker + lớp phủ CSS. Cá bơi, cua bò, thuyền chạy là **một hướng nghệ thuật khác hẳn** mà
dự án chưa có.

### Luật C — Khuôn 5 chỉ hợp lệ khi có một THANG CÓ THỨ TỰ

`buildXsec` **không phải "câu hỏi 4 lựa chọn có cột minh hoạ"**. Bản chất: *mỗi lượt để
lại một chip trên cột, và **cái cột dựng dần lên mới là bài học**.*

> **Phép thử:** bốn lựa chọn có xếp thành một thang theo thứ tự không?
> Có → khuôn 5. Không → đó là khuôn 3, và khuôn 3 có trần 2 lần/nhiệm vụ.

Vòng đầu dùng khuôn 5 sáu lần, **4 lần thực chất là khuôn 3 hoặc 4** (biển/mây/sông/hồ
không có thứ tự · mùa là một **vòng** không phải thang · ghép cặp hai bán cầu là ghép cặp).
Đây đúng là lối thoát sai đề bài đã gọi tên: *"dùng khuôn đã đầy rồi biện minh bằng cách
trình bày khác"*.

⚠️ Nhưng thường **có sẵn một thang thật đang bị bỏ lỡ**: vòng tuần hoàn nước có **độ cao**
(mây → mưa → sông → biển); bốn mùa có **độ dài ngày**. Đổi sang thang thật thì vừa hợp lệ
vừa mạnh hơn — cột dựng lên *chính là* lời giải thích.

### Luật D (hệ quả) — Chặng cuối là chỗ CHỐT, không phải bài kiểm tra

Dự án đã có luật này cho bước ⑦ của M-01 và **đang canh bằng phép kiểm tự động** (đòi
**0 lựa chọn**). Lý do áp cho mọi nhiệm vụ: nó nằm ngay trước màn thưởng — *bắt trả lời
đúng mới cho qua là dựng một cửa chặn ở đúng chỗ trẻ tưởng mình đã xong*.

⇒ Cấu trúc chuẩn: **chặng 1–5 trẻ tự khám phá · chặng cuối Comet/Byte tổng hợp + một nút
đóng dấu**. Rẻ hơn (không tiêu suất khuôn nào) và trả lại mỗi nhiệm vụ một suất khuôn.

### Phép thử một giây cho bảng ngân sách

**Tổng một dòng phải bằng đúng số chặng của nhiệm vụ đó.** Hai lần bảng tổng sai đều bị
bắt bằng đúng phép này, không cần đọc lại bảng chi tiết.

---

## Đã bác — và vì sao

*(ChatGPT/Gemini không nhớ vòng trước nên sẽ đề xuất lại. Mục này để dán trả lời.)*

| Đề xuất | Vì sao bác |
|---|---|
| **Bản A** — gấp phần đã xong | Màn ngắn nhất (221px ở 5/7) nhưng vẫn lệch **734px** sang phải, và **không tham chiếu nào gấp phần đã xong** — cái đuôi đã đi qua chính là phần thưởng |
| **Bản B** — liền mạch, giữ nhãn | Lệch **675px**; nhãn chữ là gốc của lỗi |
| Đặt một dải **hàng ngày lên bản đồ** (phương án B của câu hỏi "để ở đâu") | Bản đồ tổ chức theo NƠI; và thành hai đường vào cho một khu (bài học `codex.html`) |
| Chuyển **thuỷ triều sang Mission Moon** | Thuỷ triều là hiện tượng **của Trái Đất**; giữ ở Trái Đất nhưng kể hoàn toàn từ phía Trái Đất, Mặt Trăng chỉ là lời giải thích |
| **Vẽ đoạn nối** giữa hai vòng tròn của đường uốn | Đường thẳng nối hai nút lệch nhau cắt chéo qua khoảng giữa → đọc ra như mạng lưới, không như lối đi. Duolingo cũng không có |
| Nhiệm vụ **ngày/đêm** ở Trái Đất | Đã dạy ở **nhịp 0** của `explorer.html` (xoay quả cầu 3D, ranh giới sáng–tối là **thật**) — trẻ làm việc đó **trước khi** vào nhiệm vụ đầu tiên |
| Nhiệm vụ **góc chiếu / bác "gần Mặt Trời hơn"** | M-01 bước ③ đã dạy. Mùa thì được, nhưng phải đổi **câu hỏi** (cùng một nơi theo *thời gian*) chứ không đổi ví dụ, và bác hiểu lầm bằng **bằng chứng mới**: cùng lúc bắc bán cầu hè thì nam bán cầu đông |

---

## Lỗi thật tìm ra khi làm lượt này

| Lỗi | Vì sao chỉ ảnh chụp / phép đo mới thấy |
|---|---|
| **Bong bóng tên phủ kín chặng ngay trên** | Khoảng cách hàng 86px, bong bóng cao ~68px. Đọc CSS không thấy; đo diện tích chồng lấn thì ra ngay. Chỗ trống nay lấy từ `margin-top` của chính chặng đang mở |
| **Đoạn nối dọc của bản A còn sót** | Neo `left:38px` (đúng cho cột thẳng) trong khi nút đã dời bằng `translateX` → **mấy vạch mờ lơ lửng không nối vào đâu**. Cùng họ `.e2-shield` / `.e2-terminator` |
| **Nút "Chơi tiếp" vẫn hiện ở chặng cuối** | `.pbtn` khai `display` nên **thắng** `display:none` mà trình duyệt áp cho `[hidden]` — **đúng ca `#time-ok`** ngày 03/08. Sửa ở CSS (`.pbtn[hidden]`), không đổi sang class do JS bật tắt |
| **Tiêu đề trang đọc lờ mờ xuyên qua thanh dính** | Nền `.94` → `.99`, vẫn giữ blur |
| **`learningdata/` là nhánh chết** | **0 lời gọi `fetch`** nào trỏ vào `level_*.json`; 50 câu đang có **chưa từng tới tay đứa trẻ nào**. Cùng lỗi `termsData.ts` đã bắt sửa hai lần |

### Hai lỗi trong phép kiểm của tôi

- **Đo `.seg button` rồi báo vùng chạm 32px** — `.seg` là component **dùng chung** và mốc
  44px của nó **cố ý** gắn vào `@media (pointer: coarse)`. **Lần thứ hai mắc đúng lỗi này.**
  Một phép kiểm hay báo oan thì sớm muộn bị bỏ qua — đó mới là cái giá.
- **Lệch một đơn vị**: đòi nút nói "chặng 06" trong khi chặng vừa xong là 06 nên chặng sau
  đúng là 07.

---

## Kết quả kiểm thử

Sáu bộ, chạy trên Chromium thật: bản đồ **96** · màn hành tinh **76** · cây bản A **100** ·
bản B **55** · bản C **130** · Trung Tâm Nhiệm Vụ **54** = **511 đạt / 0 hỏng**.

Ba bất biến được **đo**, không chỉ được nói:
- đồng hồ hàng ngày **đếm lùi từ số giây server gửi**, phép kiểm **quét mã nguồn** đòi 0
  lời gọi `Date.now(` / `new Date(` / `getHours(` — đổi giờ máy không làm mới được việc
- **không việc hàng ngày nào bị khoá** theo tiến độ (khoá là khoá vĩnh viễn ở ngày đầu tiên)
- lối tắt "Chơi tiếp" **chỉ hiện khi thật sự đang dở** (0 và 7/7 đều ẩn)

---

## Còn treo

1. **Dựng thật**: `mission-tree.html` + `?step=` ở `mission-earth.html` + **tắt đồng hồ 5
   giây** khi còn chặng sau.
2. **Hàng ngày / sự kiện chưa có backend**: `POST /me/progress` chỉ nhận
   `quiz`/`game`/`lesson`/`planet`; `Wallet` không có mục `daily` và `reason` lạ trả **400**.
   Cần hình dạng dữ liệu mới (`SK=DAILY#<ngày>` + TTL + chuỗi ngày) và một mục trần thưởng.
3. **Nối `learningdata/` vào một trang** trước khi đổ 1.000 câu vào đó.
4. **Gộp hai mảng `ARTICLES`** của `learn.html` và `library.html` (trùng chủ đề) trước khi
   thêm 100 bài đọc.
5. `docs/decisions/001` (cấu trúc World/Quest) vẫn **đang mở** — vòng 20 nhiệm vụ này
   chính là thứ nó chờ.
