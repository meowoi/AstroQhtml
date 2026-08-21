# ĐỀ BÀI ART: 3 tàu đối thủ + thiên thạch xám + thùng nhiên liệu (ARCADE-03)

> **Ngày:** 21/08/2026 · **Cho:** ChatGPT (lane *sáng tác*, theo `docs/PHAN-VAI.md`)
> **Dán TOÀN BỘ phần "ĐỀ BÀI DÁN THẲNG" bên dưới vào ChatGPT.**
> Phần trước đó là bối cảnh cho Claude/chủ dự án, không cần dán.

---

## 0. Vì sao có đề bài này

Ba đối thủ trong Đường Đua Sao Chổi hiện **vẽ bằng code** (`drawRivalShip` trong
`game-racer.html`) — đọc ra là phi thuyền, nhưng không cùng đẳng cấp với art vẽ
tay của Luna. Thiên thạch xám và thùng nhiên liệu cũng là hình vẽ code (đa giác 9
đỉnh + hình chữ nhật bo góc). Chủ dự án chốt: đưa ChatGPT vẽ, rồi Claude tối ưu +
nối vào.

⚠️ **Claude không sinh được ảnh raster** — đã đếm kho: `img/` có 30 file và **0
file nào là tàu đua thứ hai** (chỉ 3 bản của cùng một Luna). Nên đây là đường
đúng, không phải đường vòng.

## 1. Số đo THẬT — đo trên Chromium, không phỏng đoán

Hệ toạ độ ảo của sân là **800×500**; sân co giãn theo màn hình rồi `setTransform`.

| Khổ máy | 1 đơn vị ảo = ? pixel thật | Tàu (56×30 ảo) | Đá lớn nhất (r=29) | Thùng (19,8×32 ảo) |
|---|---|---|---|---|
| Full HD, DPR 2 | **2,45** | **137×74 px** | **142 px** đường kính | **49×78 px** |
| MacBook 1440, DPR 2 | 2,45 | 137×74 | 142 | 49×78 |
| Điện thoại 390, DPR 3 | **0,91** | **51×27 px** | 53 px | 18×29 px |

⇒ Hai con số quyết định mức chi tiết:
- **Lớn nhất 137px rộng** → chi tiết nhỏ hơn ~3 px thật sẽ biến mất, tức **≥1/45
  chiều rộng tàu**. Trên khung xuất 1024px thì tương đương **≥22px**.
- **Nhỏ nhất 51px rộng** (điện thoại) → ở đó **chỉ SILHOUETTE còn đọc được**. Mọi
  hoa văn bên trong biến mất. Đây là ràng buộc mạnh nhất của cả đề bài.

## 2. Cách nối vào sau khi có ảnh (Claude làm)

1. Cắt theo bbox alpha → hạ cỡ LANCZOS về **~1,8× cỡ hiển thị lớn nhất**
   (tàu ~256×140 · đá ~256×256 · thùng ~128×208) → `quantize(FASTOCTREE)` 256 màu.
   ⚠️ **KHÔNG dùng `convert("P", palette=ADAPTIVE)`** — nó làm phẳng alpha thành
   trong-suốt-nhị-phân, chặt hết viền mềm (bài học 30/07).
2. Thêm `CONFIG.rivalSprites` + `rockSprite` + `canSprite`, vẽ theo lối *contain*
   như `CONFIG.spritePath` đang làm, **giữ nguyên bản vẽ code làm đường lùi** khi
   ảnh lỗi.
3. Chạy lại `play_racer.py` (83 phép kiểm) + `shot_rivals.py` (soi mắt) +
   `check_pages.py`.

⚠️ **Bản gốc >200 KB thì KHÔNG commit** (repo này deploy công khai qua Pages) —
đặt vào `img/originals/` và thêm vào `.gitignore`, đúng cách đã làm với
`img/luna ngang.png` 1,7 MB.

---

# ĐỀ BÀI DÁN THẲNG

Tôi cần **5 asset** cho một game đua phi thuyền 2D dành cho trẻ **8–15 tuổi**
(web, canvas, nhìn NGANG từ bên hông, cảnh vũ trụ nền xanh navy đậm).

## A. Style phải khớp — đây là ràng buộc, không phải gợi ý

Game đã có một phi thuyền do hoạ sĩ vẽ (nhân vật của người chơi, tên **Luna**).
Năm asset mới phải đọc ra là **cùng một xưởng đóng tàu** với nó:

- **Kiểu:** sci-fi hoạt hình bóng bẩy, nhiều mảng vỏ ghép, viền ngoài **tối đậm**
  bao trọn hình, bên trong chia mảng sáng–tối rõ (kiểu vinyl/cel-shading), có
  vài chấm/vệt bắt sáng trắng ở mép trên. Không phải pixel-art, không phải ảnh
  thực, không phải phác thảo bút chì, không phải low-poly 3D render.
- **Độ "sạch":** đường nét dứt khoát, mảng màu lớn, tương phản cao — vì nó phải
  đọc được ở cỡ **51 px rộng** trên điện thoại.
- **Bảng màu của Luna** (đo trực tiếp từ file, dùng làm chuẩn về *cách phối*,
  không phải để copy màu): trắng ngà `#FDF9FD` · hồng-trắng `#F6E8F9` · tử đinh
  hương `#D6C7EB` `#CDB8E6` `#AE97D3` · tím `#32178B` · và **navy-tím rất tối**
  `#291770` `#13094D` `#0A0532` làm viền + mảng bóng. Điểm nhấn nhỏ màu vàng chanh
  và xanh lá neon.
- **Bảng màu chung của cả app** (để 5 asset không lạc khỏi giao diện):
  cyan neon `#38BDF8` · tím `#8F7BFF` · vàng nắng `#FFCF6B` · nền deep-space
  `#0B0F19`→`#1A103C`.

## B. Năm asset

### 1–3. Ba tàu đối thủ

**Cả ba nhìn NGANG, MŨI CHỈ SANG PHẢI** (đó là hướng đua — vẽ ngược là tàu chạy
lùi trên sân). Cùng một góc nhìn, cùng đường chân trời, cùng mức chi tiết.

| # | Tên trong game | Màu nhận dạng (BẮT BUỘC) | Dáng phải khác nhau |
|---|---|---|---|
| 1 | **Sao Băng** (`blaze`) — nhanh nhất | **cam `#FF8A5C`** | **mũi kim dài, thân mảnh, hai cánh delta xuôi hẳn ra sau** — dáng "phi tiêu", đọc ra là tàu tốc độ |
| 2 | **Vệt Lửa** (`ember`) | **vàng `#FFD166`** | **thân bầu, đuôi chẻ đôi với HAI ống đẩy tách rời trên–dưới** — dáng "lực" |
| 3 | **Bụi Sao** (`dust`) — chậm nhất | **lam nhạt `#7DD3FC`** | **mũi tù, thân dẹt và rộng, một cặp cánh bè ngang** — dáng "tàu chở", nặng nề |

⚠️⚠️ **BA DÁNG PHẢI PHÂN BIỆT ĐƯỢC KHI BỎ HẾT MÀU.** Trong game, ở cỡ nhỏ nhất
chỉ còn silhouette; và có trẻ không phân biệt được màu. Hãy tự thử: chuyển ba
hình sang đen trắng rồi thu về 51 px rộng — nếu không nói ngay được cái nào là
cái nào thì dáng chưa đủ khác.

⚠️ **Màu nhận dạng là CHỨC NĂNG, không phải thẩm mỹ:** mỗi đối thủ có một cái dấu
cùng màu đó trên dải đua ở đầu sân. Lệch màu là trẻ không nối được "cái dấu này
là cái tàu kia".

⚠️ **Mỗi tàu phải có một buồng lái kính nhìn ra được**, đặt **lệch về phía mũi**,
dạng **giọt dài theo hướng bay** (rộng hơn cao). ⛔ Đừng vẽ một khối tròn tối ở
**giữa** thân — đã thử trong game và nó đọc ra thành **cái nơ**, rồi thành **đầu
đinh tán**. Đây là lỗi đã trả giá hai lần.

⚠️ **Không vẽ luồng lửa / vệt khói / hào quang vào ảnh.** Game tự vẽ chúng bằng
code (chúng phải dài ra khi tàu tăng tốc). Chỉ vẽ **miệng ống đẩy** như một chi
tiết vỏ tàu.

### 4. Thiên thạch xám (chướng ngại — đâm vào là mất nhiên liệu)

- Khối đá **không đều**, 8–12 mặt, nhìn ra ngay là **đá vũ trụ** chứ không phải
  quả cầu hay viên sỏi tròn.
- Tông **xám-lam nguội**: sáng `#8291B0` → thâm `#4B5570`, viền ngoài
  `#141C30`. Vài hố lõm và vết nứt để bắt sáng.
- ⚠️ **Nó phải đọc ra là NGUY HIỂM** mà không cần màu đỏ: góc cạnh, sắc, nặng.
  ⛔ Đừng vẽ mặt mũi, đừng vẽ nó đáng yêu — trẻ phải muốn tránh nó.
- ⚠️⚠️ **NỘI DUNG PHẢI NẰM TRONG ĐƯỜNG TRÒN NỘI TIẾP KHUNG VUÔNG.** Vùng va chạm
  trong game là một **hình tròn**; phần hình chìa ra ngoài vòng đó sẽ cho ra cảm
  giác *"trông như chưa chạm mà đã mất nhiên liệu"*. Đây là lỗi đã trả giá ở hai
  game khác. Hình xoay tròn trong game nên nó phải cân ở mọi góc.

### 5. Thùng nhiên liệu (vật thưởng — hứng được thì nạp 22% nhiên liệu)

- Một **bình/can nhiên liệu** đứng, **khung dọc tỉ lệ 5:8**, có nắp, có quai hoặc
  vành đai, có một **ô cửa sổ phát sáng** ở giữa để đọc ra "trong này có năng
  lượng".
- Tông **xanh lá neon** `#63E6A8` (màu này đã dùng cho nhiên liệu ở khắp game:
  chip HUD, hạt nổ, toast) trên vỏ tối `#0D2A1D`.
- ⚠️ **Phải đọc ra là THỨ NÊN LẤY** — sáng, gọn, mời gọi; ngược hẳn với thiên
  thạch. Hai vật này xuất hiện cạnh nhau trên cùng làn đường, trẻ phải phân biệt
  trong một phần giây.
- ⛔ **Không viết chữ hay số nào lên thùng** (app song ngữ Việt–Anh; chữ nướng vào
  ảnh thì bản tiếng Anh vẫn hiện tiếng Việt — đây là luật của cả dự án).

## C. Không vẽ những thứ sau

- ⛔ **Tinh thể tím / đồng tiền của game** — đã có ảnh chính thức (`img/tt.png`),
  dùng ở 33 chỗ trong app. Vẽ lại là dựng một đồng tiền thứ hai.
- ⛔ **Tàu của người chơi** — đã có Luna.
- ⛔ **Nền, sao, đường kẻ làn, bóng đổ xuống mặt đất** — game tự vẽ.
- ⛔ **Chữ, số, logo, watermark, khung viền, nhãn tên.**

## D. Định dạng xuất — phần dễ hỏng nhất, đọc kỹ

1. **NỀN TRONG SUỐT (PNG có alpha).**
   ⚠️ *[Suy luận — dựa trên hành vi thường thấy của các bộ sinh ảnh, tôi không
   kiểm chứng được bản ChatGPT hiện tại]* nhiều bộ sinh ảnh **không xuất được
   alpha thật** mà vẽ ra nền trắng, hoặc vẽ ra hoa văn ô cờ *giả* làm nền.
   **Đường lùi bắt buộc nếu không có alpha:** đặt nền là **MỘT màu phẳng tuyệt
   đối, không gradient, không đổ bóng** — dùng **xanh lá chói `#00FF00`** (không
   màu nào trong 5 asset dùng tông đó) để tách nền bằng script. **Đừng** dùng
   nền trắng: Luna và thùng nhiên liệu đều có mảng trắng.
2. **Ba tàu vẽ TRONG MỘT ảnh, xếp DỌC, cách nhau rõ, cùng tỉ lệ.** Lý do: các bộ
   sinh ảnh cho ra style lệch nhau giữa hai lượt chạy, mà ba tàu này phải đọc ra
   là cùng một xưởng. Đá và thùng thì mỗi thứ một ảnh riêng.
3. **Cỡ xuất lớn nhất có thể** (1024×1024 hoặc hơn). Đừng cố xuất đúng cỡ nhỏ —
   việc hạ cỡ và nén sẽ làm ở bước sau.
4. **Nội dung chiếm ≥85% khung theo cạnh dài**, canh giữa, không chừa lề rộng.
5. Nếu xuất được thêm bản **có nét viền dày hơn**, gửi luôn — nét mảnh hay biến
   mất khi thu về 51 px.

## E. Tự soi trước khi gửi

- [ ] Ba tàu **mũi đều chỉ sang PHẢI**?
- [ ] Chuyển đen trắng + thu về 51 px rộng: còn **nói ngay được cái nào là cái
      nào** không?
- [ ] Buồng lái là **giọt dài lệch về mũi**, không phải khối tròn giữa thân?
- [ ] Ba màu nhận dạng đúng `#FF8A5C` / `#FFD166` / `#7DD3FC`?
- [ ] Thiên thạch **nằm trong đường tròn nội tiếp** khung vuông?
- [ ] Thùng nhiên liệu **đọc ra là thứ nên lấy**, đá **đọc ra là thứ nên tránh**?
- [ ] **0 chữ, 0 số, 0 watermark, 0 luồng lửa, 0 hào quang** trong ảnh?
- [ ] Nền **trong suốt** — hoặc **một màu phẳng `#00FF00`**?
