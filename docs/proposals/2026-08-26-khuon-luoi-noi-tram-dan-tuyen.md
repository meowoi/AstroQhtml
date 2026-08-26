# Khuôn LƯỚI-NỐI cho Trạm Huấn Luyện — Trạm Dẫn Tuyến (ARCADE-11)

- **Ngày:** 26/08/2026
- **Loại:** đề xuất (**chưa viết một dòng mã nào**)
- **Nguồn:** chủ dự án — lồng ghép cơ chế hai game *Flow Free* và *Pipes* vào Trạm Huấn Luyện
- **Người đo:** Claude — mọi con số dưới đây **đếm từ mã nguồn**, không ước lượng.
  Ý kiến thiết kế của Claude đánh dấu `[Inference]`.
- **Ai quyết:** chủ dự án — **đã chốt 3 câu**, xem mục 0.

---

## 0. BA CÂU CHỦ DỰ ÁN ĐÃ CHỐT (26/08/2026)

| Câu | Chốt |
|---|---|
| 4 game lớp quyết định đang khoá (ARCADE-07…10) | **MỞ TRƯỚC**, trước khi xây game thứ 11 |
| Làm cả hai game hay một | **MỘT** — chỉ khuôn *Pipes* (xoay ống). Flow Free **để lại**, chưa hứa |
| Pack nội dung đầu tiên | **ĐIỆN** (pa-nô → pin → động cơ), **không phải oxy** |

## Bốn kết luận đọc trước

1. **Phần "cấu trúc chung cho Trạm Huấn luyện" của đề xuất — dự án ĐÃ CÓ RỒI.**
   `css/decision-game.css` (`.dg-brief` → `.dg-body` → `.dg-why` → `.dg-read`) +
   `js/game-run.js` đã đúng chuỗi *Briefing → Puzzle → Micro knowledge → XP*, đang
   chạy ở 4 game. Game mới **nạp lại**, không thiết kế lại. Đây là phần đắt nhất của
   đề xuất và nó **tốn 0 đồng**.
2. ⚠️⚠️ **Hai "dataset Pipes" trong đề xuất đè thẳng lên game đã có** — oxy/nước đè
   ARCADE-09, liên lạc Luna→Earth đè ARCADE-08, **kể cả dùng chung bài đọc**. Đã cắt
   ở mục 3; đây là lý do pack đầu là ĐIỆN.
3. ⚠️ **Flow Free và Pipes KHÔNG phải hai khuôn — là MỘT khuôn dùng hai lần.**
   `docs/decisions/002` trần 2 lần/khuôn ⇒ làm cả hai là **đóng luôn khuôn lưới-nối**.
   Chốt làm một ⇒ khuôn còn **1 suất dự trữ**, và suất đó **thuộc về Flow Free**.
4. ⚠️ **Dự án có 10 game nhưng trẻ chỉ chơi được 6.** ARCADE-07…10 ở trạng thái
   `soon` từ 19/08/2026. Xây game thứ 11 trong khi 4 game xong nằm khoá là tồn kho —
   nên **đợt 0 của việc này không phải viết game, mà là mở bốn cái đã có**.

---

## 1. Hiện trạng đo được

| Chỉ số | Số đo |
|---|---|
| Game đã có mã chạy | **10** (ARCADE-01…10) |
| Trẻ chơi được | **6** lúc đo — 4 game lớp quyết định đang `soon`. ✅ **Đã mở cả 4 trong cùng ngày**, nay là **10/10** (xem mục 7 đợt 0) |
| Chương trình huấn luyện | **9** (`Services/Training.cs`, `js/training.js`) |
| Lớp HÀNH ĐỘNG / QUYẾT ĐỊNH | 6 / 4 |
| Khung dùng chung đã có | `css/game-shell.css` 526 · `js/game-shell.js` 430 · `css/decision-game.css` · `js/game-run.js` · `js/sfx.js` · `js/progress.js` |
| Khuôn kéo-thả + bàn phím đã có | `js/pick-place.js` **243 dòng** (4 bước nhiệm vụ dùng chung) |
| Cỡ 4 game lớp quyết định | 568 – 647 dòng (`recycle` · `comms` · `survival` · `units`) |
| Bài đọc trong kho | **70** (`js/article/`) |

**Bốn khuôn lớp quyết định đã dùng:** *chọn thẻ* (07) · *xếp thứ tự* (08) ·
*chia ngân sách* (09) · *soi lỗi trong bảng* (10). `docs/decisions/002` ⇒ game thứ
năm **không được dùng lại cái nào trong bốn**. Khuôn lưới-nối là khuôn **mới**, hợp lệ.

---

## 2. Đề xuất đúng ở đâu — bằng chứng, không phải lời khen

| Điều đề xuất nói | Bằng chứng trong mã |
|---|---|
| Byte dẫn phần huấn luyện hệ thống | `js/characters.js:37` — Byte `role` **đã là** *"Kỹ sư hệ thống / Systems Engineer"*. Trùng khớp, không phải bịa vai mới |
| Không đặt tên menu là tên game gốc | Bắt buộc, và `games.html` đã theo hệ **"Trạm …"** (Sinh Tồn · Liên Lạc · Tuần Hoàn · Đối Chiếu) |
| Một engine, thay dataset | Đúng tinh thần `002`; có tiền lệ thật là `js/pick-place.js` (243 dòng / 4 bước) |
| Chương trình có **cấp**, không phải "ĐÃ ĐẠT" | `Training.cs` đã là thang 4 mốc mỗi khoá — đúng thứ chủ dự án bác ngày 14/08 |
| **Không dùng đồng hồ đếm ngược thật** ở màn khẩn cấp | Đồng ý, và đã có tiền lệ: ARCADE-09 dồn hậu quả qua **5 ngày** chứ không đặt đồng hồ |
| Nối *đọc → làm* | `.dg-read` dẫn sang `library.html?a=<id>`, **chỉ ở màn KẾT QUẢ** (luật đã chốt 15/08) |

Và **phần mạnh nhất của đề xuất bị xếp sai chỗ**: *"Level 6 — không nói trước
destination"*. Đó là level **duy nhất** khiến game này khác Flow Free thường —
xem mục 6a.

---

## 3. Ba chỗ chồng lấn — đã cắt

| Dataset đề xuất | Đè lên | Bằng chứng |
|---|---|---|
| Oxygen Route · Water Recycling · **nhiều đích** (Lab + Cabin + Greenhouse) | **ARCADE-09 Trạm Tuần Hoàn**, chương trình `lifesupport` | `js/training.js`: *"Chia một nguồn có hạn cho những thứ đều cần, và thấy được cái vòng nối chúng"* — câu đó **chính là** bản Pipes nhiều đích |
| Communication (Luna → Ground Station) | **ARCADE-08 Trạm Liên Lạc**, chương trình `communication` | Cùng bài đọc `art-code-written-before-launch` · `art-how-data-gets-home` · `art-three-stations-120-degrees` |
| Tên **"Resource Routing"** | chương trình `resource` = Đường Đua Sao Chổi (`Training.cs:127`) | Một cái tên cho hai thứ ⇒ mọi phép đối chiếu trượt qua |

⚠️ **Bản Pipes "nhiều đích" vì thế KHÔNG được làm** — nó không phải level khó hơn của
game mới, nó là game cũ vẽ lại. Trạm Dẫn Tuyến giữ đúng **một nguồn → một đích** cộng
các nhánh chết, và cái khó nằm ở **độ dài tuyến + ô gây nhiễu**, không ở việc chia.

---

## 4. Nền nội dung từng pack — vì sao pack đầu là ĐIỆN

Đếm trên `js/article/` (**70 file**):

| Pack | Bài đọc đã có | Kết luận |
|---|---|---|
| **ĐIỆN** — pa-nô → pin → động cơ | `art-sunlight-into-electricity` · `art-rollout-solar-arrays` | ✅ **làm được ngay, và CHƯA GAME NÀO CHIẾM** |
| **DỮ LIỆU** — cảm biến → máy tính → quyết định | `art-what-is-ai-nasa` · `art-ai-tags-nasa-data` · `art-rover-drives-itself-mars` · `art-autonomous-vs-remote` | ✅ làm được (pack thứ hai) |
| Nhiên liệu → động cơ | `art-solid-and-liquid-rocket-engines` · `art-rockets-work-in-vacuum` | ✅ làm được |
| Robot wiring (camera → bộ xử lý ảnh) | `art-canadarm2-robot-arm` · `art-astrobee-flying-robots` · `art-robonaut-first-humanoid` | ⚠️ có bài nhưng **không bài nào nói camera → bộ xử lý ảnh** ⇒ phải viết mới |
| **Cooling → Reactor** | **không có bài nào** | ❌ nhánh ENGINEERING đang 2/6 (`decisions/010`) |
| **Human body** (phổi → oxy, tim → máu) | `art-body-in-space-changes` · `art-microgravity-is-falling` | ❌ nhánh LIFE SCIENCE **0/5**; và ghép phổi–oxy là *ghép cặp*, **không phải dẫn tuyến** |

⇒ Lời hứa *"5 pack, chỉ thay dataset"* **rẻ về mã nhưng đắt về nội dung** — mà
`decisions/008` Luật B đã ghi: *nội dung là nút thắt của dự án*. **Khai 2 pack, không
khai 5**, đúng luật `Specimens.cs` cấm hứa một thứ chưa tồn tại.

---

## 5. Vì sao chỉ làm MỘT game

| | **Pipes** (xoay ống) — LÀM | Flow Free (kéo đường) — để lại |
|---|---|---|
| Sinh màn | **Thuật toán**: dựng cây từ nguồn rồi xoay lệch ⇒ **luôn có lời giải** | `[Inference]` ràng buộc *phủ kín bàn + lời giải duy nhất* không sinh được rẻ ⇒ **soạn tay từng màn** |
| Kỹ thuật | Lưới `<button>` + `transform:rotate`. **Không cần canvas** | Bám vệt `pointermove` qua nhiều ô, hoàn tác, kiểm cắt nhau |
| Bàn phím | Gần như miễn phí (Enter = xoay) | Phải dựng riêng: Enter = cầm dây · ↑↓←→ = kéo dài · Esc = bỏ |
| Ước lượng | **~500 dòng** (cỡ `game-recycle` 568) | **~800–900 dòng** + chi phí soạn màn **mỗi pack** |

⚠️ **Cái giá của việc làm cả hai không phải 1.400 dòng — mà là đóng hẳn một khuôn.**
Làm một ⇒ khuôn lưới-nối còn 1 suất, và suất đó dành cho Flow Free **nếu** engine
chứng minh dùng lại được. Đúng đường `css/game-shell.css` đã đi: dựng cho 2 game rồi
mới lan ra 6.

Bộ sinh màn — lý do Pipes rẻ:

```js
/* Dựng CÂY nối nguồn tới đích trên lưới, rồi xoay lệch đi.
   Luôn có lời giải, vì lời giải chính là cái cây vừa dựng. */
function makeBoard(w, h, src, dest) {
  var tree = spanTree(w, h, src, dest);          // DFS ngẫu nhiên, giữ nhánh tới đích
  return tree.map(function (cell) {
    return { shape: cell.shape,                  // ─  ┐  ┬  ┼ …
             sol:   cell.rot,                    // hướng đúng
             rot:   (cell.rot + 1 + Math.floor(Math.random() * 3)) % 4 };
  });                                            // lệch ≥1 nhịp ⇒ không ô nào "đúng sẵn"
}
```

⚠️ **Phải có phép kiểm duyệt HẾT bàn sinh ra** và đòi: (1) mọi bàn giải được;
(2) **không ô nào đã đúng từ đầu**; (3) có ít nhất một nhánh chết. Đúng bài học
`play_recycle.py` mục [2]: *cân bằng là tính chất phải ĐO, không phải lời hứa*.

---

## 6. Ba chỗ sửa hẳn nội dung đề xuất

### 6a. "Level 6" phải lên sớm — và cơ chế hiện tại vô hiệu hoá chính nó

Đề xuất nói *"màu sắc mới là thứ xác định cặp"*. Nếu hai đầu **đã cùng màu** thì trẻ
**không cần biết gì** về pin hay pa-nô — nó nối màu, xong. Kiến thức chỉ có giá khi màu
**không** nói ra cặp:

```
[ ☀️ ] [ 📡 ] [ 🌡 ] [ 🫁 ]     ← nguồn, CÙNG một màu xám
[ 🔋 ] [ 🖥 ] [ 🤖 ] [ 🚪 ]     ← đích, cũng xám
```

Trẻ tự quyết cặp; nối đúng **rồi mới** đổi màu để chốt. `[Inference]` Đây là thay đổi
**một cờ dữ liệu** (`paired:false`) nhưng là thứ duy nhất biến trò này từ *Flow Free dán
nhãn vũ trụ* thành *bài kiểm tra kỹ thuật*. Nên có từ **cấp 2**, không phải cấp 6.

### 6b. "Đường không được cắt nhau" — đừng nói đó là vật lý

Dây trên tàu thật cắt nhau liên tục, chỉ khác **lớp**. Tiền lệ xử lý đúng đã có:
`game-recycle` gắn nhãn **MÔ PHỎNG** thường trực vì không dùng số thật. Ở đây gọi là
**"sơ đồ MỘT LỚP"** — bảng mạch một lớp là ràng buộc kỹ thuật **thật**, nên luật chơi
trở thành kiến thức thay vì thành một câu nói sai.

### 6c. Một chương trình, không phải hai

`[Inference]` Khai **`systems` — Kỹ thuật hệ thống**, một chương trình, khoá đầu tiên là
`route`. `Training.cs` đã có tiền lệ `reaction` = 2 khoá và luật *cấp chương trình =
cấp THẤP NHẤT của các khoá* ⇒ nếu sau này có Flow Free thì nó vào **làm khoá thứ hai của
chính chương trình này**, và trẻ phải giỏi **cả** *nhận quan hệ* **và** *dựng tuyến* —
đúng ý phân vai của đề xuất, mà hồ sơ không phình từ 9 lên 11 chương trình.

Byte nói câu tổng kết ở màn kết quả — đúng `role` đã khai của nó.

### 6d. Tên — và một cảnh báo không phải ý kiến pháp lý

Không để chữ *Flow Free* / *Pipes* ở bất kỳ chỗ trẻ đọc được, kể cả nhãn menu.
`[Unverified — không phải ý kiến pháp lý]` cơ chế chơi thường không được bảo hộ, nhưng
**tên và hình ảnh** thì có; Flow Free là sản phẩm thương mại. **Cũng đừng chép art**
trong ảnh chụp.

| | Chốt đề nghị |
|---|---|
| Tên VI/EN | **Trạm Dẫn Tuyến** / **Route Station** |
| `key` | `route` — dùng y hệt ở `games.html` · `Wallet.Fees` · `Training.cs` · `economy.js` · game (bài học `match` → `constellation`, phép kiểm [27]) |
| Số hiệu | **ARCADE-11** — cấp số kế tiếp, **không sửa số cũ** |
| Chương trình | `systems` (mới) |

---

## 7. Thứ tự làm

| Đợt | Việc | Chi phí | Được gì |
|---|---|---|---|
| **0** ✅ **XONG 26/08/2026** | ⚠️ **MỞ 4 game đang khoá** (ARCADE-07…10) | ~20 dòng + chạy lại `smoke_locks` | Trẻ chơi được **10 game thay vì 6**. Đứng độc lập, đáng làm dù không bao giờ làm đợt 1 |
| **1** ✅ **XONG 26/08/2026** | Engine lưới-nối + **pack ĐIỆN** (ARCADE-11 Trạm Dẫn Tuyến) | **~640 dòng HTML/JS + ~150 dòng CSS** (ước ~500; phần vượt là bộ sinh bàn + nhánh bẫy) | Khuôn thứ 5 của lớp quyết định · chương trình thứ 10 · nối vào 2 bài đọc chưa game nào dùng |
| **2** | **Pack DỮ LIỆU** (cảm biến → máy tính → quyết định) | **~30 dòng dữ liệu** | Phép thử thật cho lời hứa "một engine, nhiều pack" |
| **3** | *(chưa hứa)* Flow Free = khoá thứ hai của `systems` | ~800–900 dòng + soạn màn tay | Chỉ làm **nếu** đợt 2 chứng minh engine dùng lại được |

⚠️ **Đợt 0 không phụ thuộc đợt 1.** Làm ngay, không chờ.

---

## 8. Những chân phải cắm cùng lúc (đếm từ mã — thiếu chân nào là phép kiểm báo hỏng)

### Đợt 0 — mở 4 game

| Chỗ | Việc |
|---|---|
| `games.html` | bỏ `status:"soon"` ở 4 thẻ (dòng 213 · 220 · 227 · 233) |
| `js/locks.js` | gỡ 4 mục `"game:survival"` · `"game:comms"` · `"game:recycle"` · `"game:units"` |
| `scratchpad/smoke_locks.py` [3] | phép kiểm đối chiếu **SỐ thẻ `soon`** với **SỐ mục `"game:`** ⇒ gỡ một chân mà quên chân kia là báo ngay |
| `scratchpad/play_*.py` | chạy lại 4 bộ đo đã có (`play_survival` · `play_comms` · `play_recycle` · `play_units`) |

### Đợt 1 — game mới

| Chỗ | Việc |
|---|---|
| `game-route.html` + `css/game-route.css` | nạp `game-shell.css` + `decision-game.css`, dùng **`js/game-run.js`** (đừng chép ~90 dòng vòng đời lượt) |
| ⚠️ CSS sân | khai **CẢ HAI** `--ar` **và** `aspect-ratio` ≈ **1** (lưới vuông). Bản chỉ khai `--ar` từng đo được sân **1086×2px** — đọc CSS thấy hợp lệ, chỉ RENDER mới thấy |
| ⚠️ `data-rotate="off"` trên `.stage` | lưới vuông thì nhắc xoay ngang là bảo trẻ làm cho tệ đi. `smoke_game_layout` [3g] kiểm **hai chiều** |
| `games.html` `GAMES[]` | `key:"route"` · `code:"ARCADE-11"` · `prog:"systems"` · `cost:3` · `diff:"easy"` · icon **`bolt`** (`js/sticker-icons.js` đã có) · `pal` — `sic--slate` còn trống, hoặc dùng lại `sic--gold` theo tiền lệ đã ghi ở `css/games.css:86` · thêm `.card--route` |
| ⚠️ Mô tả thẻ | **không gõ một con số nào** (số màn, số cấp) — bài học thẻ Đường Đua hứa "1.200 m" khi `raceLen` đã là 14.000 |
| `Services/Wallet.cs` | `Diff["route"] = "easy"` ⇒ **3 tt**. `[Inference]` đúng luật đang dùng: *không có cách nào thua* ⇒ easy (như `survival` · `maze` · `constellation`). `check_pages` [3d] đối chiếu `CONFIG.COST` với bảng phí server |
| `Services/Training.cs` | `Program("systems", …)` + `Course("route", "best:route", 4 mốc)`. **4 mốc lấy từ `CONFIG.tiers` của chính game**, không phải số nghĩ ra. `score` = **cấp bàn vừa giải** — đúng lối `maze` sau lần đổi 15/08 |
| `js/training.js` | tên + kỹ năng VI/EN. ⚠️ **KHÔNG được chứa một con số mốc nào** (phép kiểm [27]) |
| `js/progress.js` | không sửa — `AstroQProgress.game()` đã là chỗ duy nhất báo lên server |
| ⚠️ **Không** đặt màn ở `learningdata/` | thư mục đó là **nhánh chết**: `decisions/008` đo được **0 lời gọi `fetch`** trỏ vào `level_*.json`. Dữ liệu màn ở **trong file game**, đúng lối `ROUNDS` của `game-comms` |
| Bộ đo mới `scratchpad/play_route.py` | mục [1] duyệt hết bàn sinh ra (mục 5) · mục [2] chơi thắng một lượt · mục [3] đường **bàn phím** hoàn thành được một bàn |

---

## 9. Đã bác — và vì sao

*(Mục này để dán trả lời khi đề xuất tương tự quay lại.)*

| Đề xuất | Vì sao bác |
|---|---|
| **Làm cả hai game** | Một khuôn, hai lần dùng ⇒ đóng hẳn khuôn lưới-nối; và hai game **nhìn giống nhau** sẽ đọc ra như *một game chơi hai lần* — đúng câu đã ghi cho 4 game lớp quyết định |
| **Pack oxy / nước làm pack đầu** | Đè `lifesupport` (ARCADE-09), cùng bài đọc `art-life-support-recycles-water` |
| **Bản Pipes NHIỀU ĐÍCH** (Lab + Cabin + Greenhouse) | Đó **chính là** câu kỹ năng của ARCADE-09: *chia một nguồn có hạn cho những thứ đều cần*. Không phải level khó hơn — là game cũ vẽ lại |
| **Pack Communication** | Đè ARCADE-08, cùng 3 bài đọc |
| **Pack Cooling → Reactor** | **0 bài đọc**; luật *nội dung lấy từ kho đã có, không tra nguồn mới* |
| **Pack Human Body** | LIFE SCIENCE 0/5; và phổi→oxy là **ghép cặp**, không phải dẫn tuyến — sai bản chất khuôn |
| **Khai sẵn 5 pack** | Hứa thứ chưa tồn tại — bẫy `Specimens.cs` (*"đừng viết Mở khoá tại Mission 02"*) |
| **Hai chương trình riêng** (Logical Connections + Systems Engineering) | Một game không đỡ được hai chương trình; và `reaction` đã có tiền lệ **một chương trình, nhiều khoá** |
| **Tên "Resource Routing"** | Trùng chương trình `resource` đang có |
| **Ghép cặp bằng MÀU** ở mọi cấp | Màu nói ra cặp thì kiến thức thành đồ trang trí (mục 6a) |
| **Đồng hồ đếm ngược thật** ở màn khẩn cấp | Chính đề xuất đã tự bác — và ARCADE-09 đã có cách khác: hậu quả dồn qua nhiều lượt |
| **Dựng lại chuỗi Briefing → Puzzle → Knowledge → XP** | Đã có: `css/decision-game.css` + `js/game-run.js` |

---

## 10. Hai chỗ tôi KHÔNG chắc — ĐÃ CHỐT KHI LÀM ĐỢT 1

1. **Bảng màu thẻ → dùng lại `sic--gold`** (lần thứ ba, sau Ghép Chòm Sao và Trạm Đối
   Chiếu), icon `bolt`. `sic--slate` là bảng duy nhất còn trống nhưng xám cho một trò về
   **điện** thì sai nghĩa. Thứ phân biệt thẻ trong lưới là `--neon` của `.card--route`
   (vàng chanh 250,204,21) — đậm hơn hẳn vàng nhạt 255,207,107 của ARCADE-10. Tiền lệ
   dùng lại bảng icon đã ghi ở `css/games.css`. **Đã soi ảnh chụp lưới 11 thẻ:** hai thẻ
   đọc ra là hai thẻ.
2. **Năm "cấp" và bốn mốc — hết xung đột, vì chúng đo hai thứ khác nhau.** Một LƯỢT có
   **5 bàn** khó dần (4×4 → 6×6; nhận biết → nối → sửa vòng qua ô cháy → cổng kiến thức
   → hai pa-nô), còn **cấp chương trình** đếm *số bàn nối xong trong một lượt* với mốc
   `{2,3,4,5}` — đúng 4 cấp, đúng luật *"mọi chương trình đều 4 cấp"*, và cùng cách đo
   với `units`. Không phải gộp cấp nào.

### Ba thứ phát hiện khi làm thật (không có trong bản đề xuất)

1. ⚠️⚠️ **Cổng kiến thức suýt thành đồ trang trí.** Nối thiết bị sai vào mạng thì lời
   giải tưới cả ba thiết bị ⇒ luật *"chỉ đúng một cái"* thành vô nghiệm; **không** nối
   thì trẻ *không thể* chọn sai ⇒ không phải chọn. Chữa bằng **nhánh bẫy**: một dây
   riêng, đầu dây có miệng hướng vào cây mà cây không hướng lại.
2. ⚠️ **Luật thắng phải có điều kiện "không tưới thiết bị khác", và điều đó là ràng buộc
   của TÌNH HUỐNG (điện có hạn), không phải một định luật** — một thanh cái điện thật thì
   cấp cho nhiều thiết bị. Vì thế lời brief bàn 4 nói thẳng *"điện lúc này chỉ đủ cho một
   cái"*.
3. ⚠️ **Đoạn thẳng có chu kỳ 2**: gieo lệch bằng số chẵn là ô "đúng sẵn". Bộ đo đòi
   `prealigned() == 0` ở mọi bàn — thứ đọc mã rất khó thấy.

---

## 11. Nội dung mới cần bao nhiêu

| Loại | Số lượng | Nguồn |
|---|---|---|
| Bài đọc mới | **0** | Pack ĐIỆN dùng `art-sunlight-into-electricity` + `art-rollout-solar-arrays` (đã có, URL đã kiểm) |
| Câu brief (VI+EN) | **4–5** × 2 ngôn ngữ | 1 câu/cấp, cỡ `game-comms` |
| Câu kiến thức chốt sau mỗi bàn | **4–5** × 2 ngôn ngữ | **trích từ 2 bài trên**, không viết mới |
| Asset ảnh | **0** | Lưới ống vẽ bằng CSS/SVG — đúng trần *≤1 asset, mặc định 0* (`decisions/008` Luật B) |
| Câu Byte nói ở màn kết quả | **1–2** × 2 ngôn ngữ | — |

⚠️ **Pack thứ hai (DỮ LIỆU) tốn ~30 dòng dữ liệu và 0 bài đọc mới** — nếu con số đó
đúng khi làm thật thì lời hứa *"một engine, nhiều pack"* đã được chứng minh, và lúc đó
mới nên nói tới đợt 3.
