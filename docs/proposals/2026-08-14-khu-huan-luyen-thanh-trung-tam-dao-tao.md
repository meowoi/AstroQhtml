# Khu Huấn Luyện → TRUNG TÂM ĐÀO TẠO PHI HÀNH GIA

- **Ngày:** 14/08/2026
- **Loại:** đề xuất (chưa viết một dòng mã nào)
- **Người đo:** Claude — mọi con số dưới đây **đếm từ mã nguồn**, không ước lượng
- **Ai quyết:** chủ dự án

> Đề xuất của chủ dự án: khu này nên là **ASTRONAUT TRAINING CENTER**, game chỉ là
> *phương thức* huấn luyện chứ không phải *bản chất* của khu. Kèm bảng 10 chương
> trình đào tạo ánh xạ sang 10 game.

---

## 0. Bốn kết luận đọc trước

1. ⚠️⚠️ **Thứ đáng giá nhất của đề xuất KHÔNG PHẢI 10 game — mà là việc ĐỔI VAI
   của khu.** Đổi vai gần như **không tốn gì** (tên, nhãn, cách nhóm thẻ) nhưng đổi
   hẳn điều đứa trẻ hiểu về việc nó đang làm. **Nên làm việc này TRƯỚC, và độc lập
   với mọi game mới.**
2. **Đếm lại: 10 chương trình, nhưng 6 game đang có đã phủ được ~3.** Bảng ánh xạ ở
   mục 2. Còn **7 chương trình** chưa có gì.
3. ⚠️⚠️ **10 chương trình chia làm HAI LỚP CHI PHÍ khác nhau tới 3 lần**, và dự án
   **mới chỉ xây lớp đắt**. Đây là phát hiện quan trọng nhất của cả lượt đo — xem
   mục 3.
4. ⚠️ **Chốt chặn kiến trúc: server hiện chỉ có MỘT bộ đếm `gamesPlayed` chung.**
   Không có chỗ nào ghi "trẻ đã đạt chương trình nào". Muốn có chứng chỉ theo
   chương trình thì phải sửa server **TRƯỚC khi thêm game thứ 7**, không phải sau.

---

## 1. Hiện trạng đo được

| Chỉ số | Số đo |
|---|---|
| Game đã chạy | **6** (ARCADE-01…06, tất cả `ready`) |
| Dòng mã mỗi game | **755 – 1.400**, trung bình **~1.006** dòng HTML + ~40 dòng CSS |
| Hạ tầng dùng chung đã có | `css/game-shell.css` 328 · `js/game-shell.js` 298 · `js/sfx.js` 188 · `economy.js` 237 · `js/progress.js` 566 |
| Cỡ toàn bộ client | ~22.400 dòng HTML + ~27.700 dòng JS/CSS |

⇒ **Hạ tầng khung đã xong và dùng lại tốt** — `game-catch` chỉ tốn 755 dòng vì nó
thừa hưởng khung, HUD, lớp phủ, lời nhắc xoay ngang, trần pixel. Đây là lý do
thêm game mới **rẻ hơn nhiều** so với 6 tháng trước.

---

## 2. Ánh xạ 10 chương trình vào 6 game đang có

| # | Chương trình | Đã có? | Game |
|---|---|:--:|---|
| 1 | **Reaction Training** | ✅✅ | Né Thiên Thạch · Bắt Sao Băng (**hai** game) |
| 2 | Docking Training | ❌ | — |
| 3 | EVA Training | ❌ | — |
| 4 | Robotic Arm | ❌ | — |
| 5 | Emergency Training | ❌ | — |
| 6 | Navigation | ⚠️ một phần | Mê Cung Thiên Hà (định hướng không gian) |
| 7 | Communication | ❌ | — |
| 8 | Resource Management | ⚠️ một phần | Đường Đua Sao Chổi (quản lý nhiên liệu) |
| 9 | Landing | ❌ | — |
| 10 | Survival | ❌ | — |

⚠️ **Hai game KHÔNG nằm trong danh sách 10, và cả hai đều đáng giữ:**
**Phòng Thủ Không Gian** (ngắm 360° — kỹ năng nhận thức không gian, đúng thứ đề xuất
muốn lấy từ T-38) và **Ghép Chòm Sao** (thứ duy nhất trong khu dạy **kiến thức thiên
văn thật**). Danh sách 10 nên **mở rộng chứ không thay thế** — đừng để một bảng ánh
xạ đẹp làm mất hai game đang chạy tốt.

⇒ **Còn 7 chương trình chưa có gì.**

---

## 3. ⚠️⚠️ HAI LỚP CHI PHÍ — phát hiện chính

7 chương trình còn lại **không cùng một giá**:

### Lớp A — game HÀNH ĐỘNG (canvas, vòng vẽ 60fps, va chạm, vật lý)

| Chương trình | Cơ chế | Ước lượng |
|---|---|---|
| **Landing** | lực đẩy chống trọng lực, ngân sách nhiên liệu | ~900 dòng |
| **Docking** | khớp vị trí **và** khớp vận tốc, điều khiển chậm | ~1.000 dòng |
| **EVA** | quán tính, không ma sát, dây an toàn | ~1.000 dòng |
| **Robotic Arm** | điều khiển nhiều khớp | ~1.200 dòng |

### Lớp B — game QUYẾT ĐỊNH (không có vòng vẽ, không va chạm)

| Chương trình | Cơ chế | Ước lượng |
|---|---|---|
| **Survival** | chọn vật dụng, giải thích vì sao | ~300 dòng |
| **Communication** | truyền lệnh đúng thứ tự, có độ trễ | ~400 dòng |
| **Emergency** | quy trình xử lý sự cố có hẹn giờ | ~450 dòng |
| **Resource Management** | phân bổ oxy/nước/điện theo lượt | ~450 dòng |

> **Cả 4 chương trình lớp B cộng lại (~1.600 dòng) vẫn RẺ HƠN hai game lớp A.**

⇒ Dự án đã xây **6/6 game thuộc lớp A**. Lớp B chưa có cái nào — mà đó lại là lớp
**rẻ hơn 3 lần** và, theo tôi, **dạy được nhiều hơn**: kỹ năng thật của phi hành gia
phần lớn là *ra quyết định đúng dưới áp lực*, không phải bấm nhanh.

---

## 4. ⚠️ Chốt chặn kiến trúc: chưa có chỗ ghi "đã đạt chương trình nào"

Đo trên `Services/Achievements.cs`: bộ đếm hiện có là `gamesPlayed` · `quizCorrect`
· `quizAnswered` · `quizTaken` · `quizPerfect` · `lessonsRead` · `planets`, cộng
`bests` (kỷ lục **theo từng game**) và `consts`.

Tức là:

- ✅ **Kỷ lục từng game đã có** (`bests`) — dùng được ngay.
- ❌ **Không có** trường nào nói *"chương trình Docking: ĐẠT"*.
- ❌ **Không có** khái niệm "chứng chỉ" / "cấp huấn luyện".

⇒ Một Trung Tâm Đào Tạo mà không nói được *"con đã qua 4/10 chương trình"* thì nó
vẫn là sảnh game, chỉ đổi tên. **Việc server phải làm trước:** thêm
`training: { <mã chương trình>: { passed, best, at } }` vào bản ghi `SK=PROGRESS`,
theo đúng phân công đã dùng cho huy hiệu và mẫu vật — **server giữ MỐC ĐẠT, client
giữ TÊN chương trình**.

⚠️ Đây là việc **phải làm TRƯỚC game thứ 7**, không phải sau: làm sau thì 7 game đã
xây xong đều phải sửa lại chỗ báo kết quả.

---

## 5. ⚠️ Ngân sách khuôn tương tác — luật đã có, áp cho khu này

`docs/decisions/002` chốt: *một nhiệm vụ không dùng cùng một khuôn quá 2 lần*. Khu
huấn luyện chưa bị luật đó ràng, nhưng tinh thần thì đúng y hệt: **10 chương trình
mà 7 cái là "ngắm rồi bấm" thì trẻ chơi 3 cái là biết hết**.

Phân loại khuôn của 6 game đang có:

| Khuôn | Đang dùng | Còn chỗ? |
|---|---|:--:|
| Né / phản xạ | dodge · catch | **ĐẦY 2/2** |
| Ngắm & bắn | defender | 1/2 |
| Đi trong lưới | maze | 1/2 |
| Nối theo thứ tự | constellation | 1/2 |
| Đua theo làn | racer | 1/2 |

⇒ **Đừng thêm game phản xạ thứ ba.** Và 4 game lớp B ở mục 3 đều là **khuôn mới
hoàn toàn** — thêm một lý do nữa để làm chúng trước.

---

## 6. ⚠️ Cơ hội đang bỏ lỡ: Trạm Tri Thức và Khu Huấn Luyện KHÔNG hề biết nhau

Đo được: **0 chỗ** trong 6 game nhắc tới một bài đọc nào, và 0 bài đọc nào dẫn sang
một game nào. Hai khu lớn nhất của app đứng rời nhau.

Mà kho bài đọc **vừa mới có sẵn đúng nguyên liệu** cho lớp B:

| Chương trình | Bài đọc đã có |
|---|---|
| Resource Management | `art-life-support-recycles-water` (ECLSS: nước · không khí · oxy) |
| Communication | `art-code-written-before-launch` (lệnh gửi trước, 7 phút trễ tín hiệu) |
| Landing | `art-newtons-three-laws` · `art-rockets-work-in-vacuum` |
| EVA | `art-microgravity-is-falling` · `art-newtons-three-laws` (quán tính) |
| Robotic Arm | `art-canadarm2-*` |

⇒ Trung Tâm Đào Tạo là **chỗ tự nhiên nhất** để nối *đọc → làm*: học bài xong thì
có chỗ dùng thứ vừa học. Đây là giá trị mà bảng 10 chương trình mở ra, và nó
**không tốn thêm nội dung nào** — bài đã viết rồi.

---

## 7. Đề nghị thứ tự làm

| Đợt | Việc | Chi phí | Được gì |
|---|---|---|---|
| **1** | **Đổi vai khu + gom 6 game thành chương trình** (tên, nhãn, nhóm, mô tả "huấn luyện kỹ năng gì") | ~150 dòng, **0 game mới** | Khu có bản sắc mới ngay, không phải chờ game nào |
| **2** | **Server: `training` trong `SK=PROGRESS`** + màn "hồ sơ huấn luyện" | ~200 dòng + deploy | Nói được "4/10 chương trình" — thứ biến sảnh game thành trung tâm đào tạo |
| **3** | **4 game lớp B** (Survival → Communication → Emergency → Resource) | ~1.600 dòng | +4 chương trình, 4 khuôn mới, nối thẳng vào 5 bài đọc đã có |
| **4** | **Landing** (lớp A, rẻ nhất và dạy đúng nhánh Vật lý vừa viết) | ~900 dòng | +1 |
| **5** | Docking · EVA · Robotic Arm | ~3.200 dòng | +3, đủ 10 |

⚠️ **Đợt 1 và 2 đáng làm dù không bao giờ làm đợt 3–5.** Chúng đứng độc lập, và
chúng mới là thứ trả lời được câu *"khu này là gì"*.

---

## 8. Hai chỗ tôi KHÔNG chắc, cần chủ dự án chốt

1. **Có bỏ hẳn chữ "game" không?** Đề xuất nói *"game chỉ là phương thức"*. Nhưng
   với trẻ 8–15 thì chữ "game" là **lời mời**, còn "huấn luyện" nghe như bài tập.
   Tôi nghiêng về: **tên khu và cách nhóm là "đào tạo", nhưng từng thẻ vẫn được
   gọi là trò chơi** — giữ được cả sức hút lẫn ý nghĩa. Cần chốt.
2. **Có bắt học xong mới được huấn luyện không?** Tức Landing có đòi đọc bài Newton
   trước không. Tôi nghiêng về **KHÔNG khoá** — chỉ *gợi ý* bài đọc liên quan ngay
   trên thẻ. Khoá là dựng thêm một cổng lộ trình thứ hai, mà `js/route-gate.js` đã
   dạy một bài đắt: cổng bật vĩnh viễn thì khoá chết 7 mẫu vật và 2 huy hiệu.

---

## 9. ⚠️ Về T-38: đồng ý, và ghi lại vì sao

Đề xuất nói *không cần mô phỏng T-38 thật; thứ lấy từ nó là phản xạ + nhận thức
không gian + quyết định nhanh + phối hợp nhiệm vụ*. **Đúng, và dự án đã vô tình làm
đúng điều đó rồi** — `game-defender` (ngắm 360°, quyết định nhanh, câu đố chen
giữa) chính là bốn thứ ấy mà không có một chiếc máy bay nào.

⇒ Ghi lại thành luật cho các chương trình sau: **lấy KỸ NĂNG của một khoá đào tạo
thật, đừng lấy CỖ MÁY của nó.**
