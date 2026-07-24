# AstroQ — Hướng dẫn làm việc (đọc trước khi bắt đầu)

> File này để Claude nắm cách làm việc & quy trình deploy — **không hỏi lại** những điều đã ghi ở đây.

## 1. Dự án
- Web **tĩnh, giáo dục** về Hệ Mặt Trời cho trẻ em. **HTML/CSS/JS thuần**, không framework, không build step.
- Thư mục mã nguồn (đồng thời là git repo): **`AstroQhtml/`** (chính là thư mục chứa file này).
- Phong cách UI: **glassmorphism + sci-fi/cockpit**, tông không gian (deep space, neon cyan `#38bdf8`, sun `#ffcf6b`, tím `#8f7bff`).
- **Song ngữ VI/EN**, đồng bộ qua `localStorage["astroq-lang"]` (mọi trang lắng nghe event `storage`). VI mặc định.
- Luôn tôn trọng `@media (prefers-reduced-motion: reduce)`.
- Ngôn ngữ trao đổi với người dùng: **Tiếng Việt**.

## 2. Cấu trúc file
- `index.html` — landing: màn kịch nhân vật bay, **1 nút "Trải nghiệm ngay"** mở popup Đăng ký/Đăng nhập.
- `select.html` — **Cấp Thẻ ID & Chọn Nhân Vật** (ID card glassmorphism, roster 3D, HUD info).
- `dashboard.html` — **khoang tàu (cockpit)**: header trạng thái tàu, 3 card HUD (Trạm Tri Thức / Phòng Trái Lực / Bản Đồ Thiên Hà), Holo-Desk nhân vật.
- `explorer.html` — bản đồ **3D Hệ Mặt Trời + Solar Neighborhood** (three.js qua CDN, ES module).
- `economy.js` — số dư **"Thiên thạch tím"** (`getAsteroids/addAsteroids/useAsteroids`).
- `js/auth-flow.js` — roster nhân vật + chọn + lưu hồ sơ + chuyển hướng.
- `img/` (2D), `3d/` (ảnh 3D nhân vật), `ava/` (avatar tròn).

## 3. Luồng người dùng
- **Khách mới**: `index` → "Trải nghiệm ngay" → popup **Đăng ký** → `select.html` (điền tên + chọn nhân vật → "BẮT ĐẦU HÀNH TRÌNH") → `dashboard.html`.
- **Người cũ**: trong popup bấm link **"Đăng nhập"** → `dashboard.html` (dùng lại avatar/nhân vật đã lưu).
- Đã có hồ sơ trong máy → bấm "Trải nghiệm ngay" vào thẳng `dashboard.html`.
- `dashboard` → card "Bản Đồ Thiên Hà" → `explorer.html`. Trong explorer nút **"Quay lại"** → `dashboard.html`.

## 4. localStorage (không có backend)
- `astroq-user` = `{ name, pilotName, character, selectedCharacter, avatar, email, purpleAsteroids }`
- `astroq-asteroids` = số dư Thiên thạch tím (chuỗi số). Pilot mới bắt đầu **0** (kiếm qua Quiz).
- `astroq-lang` = `"vi" | "en"`
- Mapping nhân vật (3d ↔ ava) ở mảng `CHARACTERS` trong `js/auth-flow.js`. **role/trait/stats đang là placeholder — chờ cập nhật.**

## 5. GIT & DEPLOY  ⚠️ (đã chốt — KHÔNG hỏi lại)
- **Remote**: `https://github.com/meowoi/AstroQhtml.git`
- **Repo gốc = thư mục `AstroQhtml/`**. Nhánh chính: **`main`**.
- **Deploy**: GitHub Pages từ `main`, custom domain **astroq.org** (file `CNAME`). Sau push, Pages tự build ~1–2 phút.
- **Khi người dùng nói "push / đẩy lên git"** → chạy ngay (trong `AstroQhtml/`), không hỏi URL:
  ```bash
  cd AstroQhtml
  git add -A
  git commit -m "<mô tả ngắn>" -m "<chi tiết>" -m "Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  git push origin main
  ```
- Push thẳng `main` là ĐÚNG (Pages deploy từ main). Cảnh báo LF→CRLF vô hại. `gh` CLI không có trên máy.

## 6. Quy ước làm việc
1. **Mỗi lần code: ghi requirement** vào mục "Nhật ký yêu cầu" bên dưới (ngày · yêu cầu tóm tắt · file ảnh hưởng).
2. Giữ vanilla JS, không thêm dependency/build. Hỏi tên file ảnh nếu chưa rõ ánh xạ nhân vật.
3. Không sửa được pixel bên trong ảnh PNG (đổi màu vùng cụ thể) → báo người dùng chỉnh ảnh, hoặc dùng CSS filter cho cả ảnh.
4. Thêm text cho trang song ngữ → thêm khóa vào **cả** từ điển `vi` và `en`.

## 7. Nhật ký yêu cầu (Requirement Log)
> Ghi mới nhất lên trên.

### 2026-07-25
- Avatar khung tròn: bỏ zoom mặc định (100%, không lẹm đầu); zoom riêng theo `zoom` mỗi nhân vật (Castor=1.6 vì đầu nhỏ trong ảnh). Đồng bộ zoom sang avatar header dashboard (`avatarZoom`). — `select.html`, `js/auth-flow.js`, `dashboard.html`
- Thẻ bí ẩn: bỏ bóng đen, giữ dấu "?" phát sáng. — `select.html`
- Thêm 2 thẻ nhân vật bí ẩn (khoá) ở màn chọn: bóng đen + dấu "?" phát sáng, click hiện toast "sắp mở khoá". — `js/auth-flow.js`, `select.html`
- Đổi tên nhân vật ở màn chọn: raica→Castor, báo→Umbra, chim→Ignis, chó→Sirius, chuột→Lyrae, cú→Moros, cua→Karkinos. Đồng bộ cỡ avatar trong khung (zoom nhẹ + căn giữa; ảnh đều 1080²). — `js/auth-flow.js`, `select.html`
- Bỏ nút "Đăng nhập" riêng ở index; chỉ còn 1 nút "Trải nghiệm ngay" → mở popup (đăng nhập nằm trong popup). — `index.html`
- Luồng mới: Đăng ký → `select.html` → `dashboard.html`; đăng nhập → thẳng dashboard, dùng lại avatar. — `index.html`, `select.html`, `js/auth-flow.js`, `dashboard.html`
- Tạo `select.html` (ID card glassmorphism, roster 3D bounce, HUD role/trait/stats neon, dấu APPROVED) + `js/auth-flow.js`. Dùng ảnh `3d/` + `ava/`.
- Dashboard: avatar header = ảnh nhân vật đã chọn + tên phi hành gia.
- Bỏ icon thư ở nút Contact Us; làm sáng raica1 (CSS filter). — `index.html`
- Redesign dashboard thành khoang tàu: nền deep space + sao lấp lánh + Trái Đất, khung vỏ tàu kim loại, Holo-Desk (bệ hologram + đai năng lượng + slime bob), card HUD glassmorphism 4 góc neon. — `dashboard.html`

### 2026-07-24
- Tạo `economy.js` (số dư Thiên thạch tím; pilot mới đổi thành 0 khi đăng ký).
- Tạo `dashboard.html` (3 card, gating game <5 tt → modal nhắc Quiz, quiz demo +10 tt, song ngữ + đổi ngôn ngữ + Đăng xuất).
- index: popup Đăng nhập/Đăng ký (giả lập demo) + giả lập đăng nhập thành công.
- explorer: thêm bảng thông tin **Mặt Trời** (số liệu NASA), **Solar Neighborhood 3D** (sao theo RA/Dec/khoảng cách, click zoom + info), Sao Kim quay ngược chiều, toggle "Giảm cấu hình", popup xác nhận đi tới vùng khác / mở khóa nhiệm vụ; fix toggle quỹ đạo/nhãn ở region 2; đồng bộ ngôn ngữ + màn loading.
- index: nhiều màn hoạt cảnh nhân vật (b1/m1/luna1/cho1/raica1 bay vào; qg1+qb1+q1 → 3qok vòng vàng; q1 văng ra tự xoay); đồng bộ kích thước.
