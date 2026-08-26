# AstroqSV — Backend .NET 10 trên AWS Lambda

Kế hoạch triển khai backend cho astroQ.org: **AWS Lambda + .NET 10 + DynamoDB + SES**,
API Gateway đứng trước, client là site tĩnh hiện có.

Liên quan: [`firebase-auth.md`](firebase-auth.md) — phần xác thực đang chạy.

---

## 0. Tình trạng hiện tại — ĐÃ CHẠY THẬT *(cập nhật 29/07/2026)*

| Hạng mục | Trạng thái |
|---|---|
| Stack CloudFormation `astroqsv` | ✅ `ap-southeast-1` |
| API | ✅ `https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com` |
| Bảng DynamoDB `astroq-main` | ✅ PAY_PER_REQUEST, bật TTL + PITR |
| Email duy nhất | ✅ khoá bằng `EMAIL#<email>` trong DynamoDB (**không** dựa vào Firebase) |
| Lambda `AstroqSV` | ✅ `dotnet10`, arm64, 512 MB |
| SES gửi email kích hoạt | ✅ từ `no-reply@astroq.org` |
| Đăng ký 2 giai đoạn | ✅ **34/34 phép kiểm tự động đạt** |
| `GET\|PUT /me/onboarding` | ✅ route ĐẦU TIÊN đòi ID token — **25/25 đạt ở máy, 25/25 đạt lại trên AWS** (`scratchpad/test_onboarding.py`) |
| Hồ sơ + Kho Thành Tích | ✅ `/me/profile`, `/me/achievements`, `/me/progress` — **74/74 đạt ở máy, 74/74 đạt lại trên AWS** (`scratchpad/test_profile.py`) |
| Luật chơi (XP, cấp độ, huy hiệu) | ✅ `Services/Achievements.cs` — **chỉ ở server**, client không tính |
| Ví Thiên thạch tím | ✅ `Services/Wallet.cs` — **phí do server quyết**, trừ nguyên tử, chống trùng bằng `opId` — **50/50 đạt ở máy, 50/50 đạt lại trên AWS** (`scratchpad/test_wallet.py`) |

Còn thiếu: `POST /auth/login`, `GET /me/history`, `/lessons/*` (đăng nhập hiện chạy
thẳng bằng Firebase Web SDK ở client, chưa cần qua Lambda).

**Đường xác thực token đã chạy thật** kể từ `/me/onboarding`: client lấy ID token bằng
`AstroQAuth.idToken()`, `js/api.js` gửi kèm `Authorization: Bearer …` (`apiGetAuth`/`apiPutAuth`),
Lambda xác minh bằng JwtBearer với khoá công khai của Google rồi **lấy uid từ token**. Các route
`/me/*` còn lại chỉ việc thêm vào nhóm đã có, không phải dựng lại phần này.

⚠️ Tài khoản AWS đang gắn `AdministratorAccess` để deploy được. **Nên thay bằng bộ
quyền hẹp** ở mục 7 khi stack đã ổn định.

---

## 0b. Đăng ký 2 giai đoạn — hai DB, hai vai trò

Yêu cầu: Firebase **chỉ** được chứa tài khoản đã xác thực; DynamoDB là **tập cha**,
chứa thêm những đăng ký đang chờ. Email phải duy nhất trên **cả hai** nơi.

```
        POST /auth/register                    GET /auth/activate?e=&t=
             │                                          │
   ┌─────────▼──────────┐                    ┌──────────▼─────────────┐
   │ DynamoDB           │   email 10 phút    │ 1. kiểm token + hạn    │
   │ PK=PENDING#<email> │ ─────────────────▶ │ 2. GIÀNH CHỖ EMAIL#    │
   │ SK=SIGNUP          │      (SES)         │ 3. import vào Firebase │
   │ + pwdHash/pwdSalt  │                    │    (emailVerified=true)│
   │ + tokenHash, ttl   │                    │ 4. tạo PROFILE + WALLET│
   │ + continueUrl      │                    │ 5. xoá bản ghi chờ     │
   └────────────────────┘                    │ 6. redirect ?activated │
     CHƯA có Firebase                        └────────────────────────┘
```

**Mật khẩu không bao giờ được lưu ở dạng thô.** Lúc đăng ký, Lambda băm ngay bằng
**PBKDF2-SHA256, 100.000 vòng** (`Services/PasswordHasher.cs`) rồi vứt bản gốc; lúc
kích hoạt thì đẩy chính hash đó lên Firebase qua `ImportUsersAsync` +
`FirebaseAdmin.Auth.Hash.Pbkdf2Sha256`. Người dùng vẫn đăng nhập bằng mật khẩu ban đầu
— đã kiểm bằng `accounts:signInWithPassword` thật. *(Firebase cho tối đa 120.000 vòng.)*

**Token kích hoạt**: 32 byte ngẫu nhiên, gửi ở dạng hex trong link, nhưng DynamoDB
**chỉ lưu SHA-256 của nó** — rò bản ghi DB cũng không dựng lại được link. So sánh bằng
`CryptographicOperations.FixedTimeEquals` để không lộ thông tin qua thời gian phản hồi.

| Endpoint | Việc |
|---|---|
| `POST /auth/register` | 202 · ghi bản ghi chờ + gửi link 10 phút · 409 nếu email đã có tài khoản |
| `POST /auth/resend` | 200 · cấp token mới (token cũ chết ngay) + gia hạn 10 phút |
| `GET /auth/activate?e=&t=` | 302 về `VERIFY_CONTINUE_URL?activated=1|0&reason=…` |

`reason` có thể là `ok · already · expired · badtoken · notfound · missing · error` —
`js/firebase-auth-ui.js` ánh xạ từng giá trị sang một câu VI/EN.

### Email duy nhất — DynamoDB quyết, không phải Firebase

Bản ghi `PK=EMAIL#<email>, SK=ACCOUNT` là **chốt chặn duy nhất đáng tin**. Luồng
kích hoạt **giành chỗ trước, gọi Firebase sau**:

```
kiểm token + hạn
  └─ ClaimEmailAsync:  PutItem  ConditionExpression = attribute_not_exists(PK)
       ├─ thua  → reason=already, KHÔNG gọi Firebase
       └─ thắng → import Firebase → PROFILE+WALLET → LinkEmailAsync → xoá pending
                    └─ hỏng ở bất kỳ bước nào → ReleaseEmailAsync (nếu không
                       nhả thì email đó bị khoá vĩnh viễn, không ai đăng ký lại được)
```

⚠️ **Vì sao không tin `fb.EmailExistsAsync` một mình.** Ngày 27/07/2026 đã gặp thật:
một lượt `POST /auth/register` trả **202** dù email đó vừa kích hoạt xong 60 giây
trước — đáng lẽ phải 409. *Không tái hiện lại được* (thử ngay sau khi kích hoạt thì
409 đúng), nên nguyên nhân vẫn chưa rõ. Nhưng hậu quả thì rõ và nghiêm trọng, vì
**`ImportUsersAsync` khi trùng email sẽ ÂM THẦM ghi đè tài khoản cũ**: không ném lỗi,
`FailureCount = 0`, uid cũ biến mất. Hai lỗ hổng cộng lại = đăng ký lại email của
người khác là xoá được tài khoản của họ. Ghi có điều kiện của DynamoDB không phụ
thuộc vào hành vi của Firebase nên đóng được cả hai.

Còn một lớp nữa: sau khi giành chỗ vẫn kiểm `fb.EmailExistsAsync`, để bắt các tài
khoản tạo **trước** khi có cơ chế giữ chỗ (bản giữ chỗ mới không chặn được chúng) —
gặp thì báo `already` và **không import đè**.

**Chi tiết dễ vấp:**

- Bấm **Đăng ký lại** cùng email khi bản ghi chờ còn hạn thì **không báo lỗi** — cấp
  token mới và gửi lại (người dùng làm vậy thường là vì chưa thấy email).
- Bấm lại link **đã dùng** trả `reason=already`, không phải lỗi.
- Kích hoạt hỏng giữa chừng thì **giữ nguyên** bản ghi chờ để thử lại được.
- `ttl` = `expiresAt + 86400` — DynamoDB tự dọn, không cần cron; giữ thêm 1 ngày để
  còn tra cứu khi người dùng báo "bấm link mà kêu hết hạn".
- ❗ **Không** đặt `PUBLIC_API_URL: !Sub 'https://${Api}...'` vào environment của
  Lambda: `ApiFunction` sẽ phụ thuộc `Api`, mà `Api` lại route tới `ApiFunction` →
  CloudFormation báo *Circular dependency*. Link kích hoạt được dựng từ host của
  chính request (`AuthEndpoints.ActivateLink`), luôn đúng và không cần cấu hình.

---

## 0c. Chạy song song local và server

Ba chế độ, đổi bằng **tham số URL** (nhớ luôn cho các lần sau, lưu ở `localStorage["astroq-api"]`):

| Chế độ | Trang chạy ở | Gọi API nào | Bật thế nào |
|---|---|---|---|
| **prod** | `https://astroq.org` | Lambda trên AWS | mặc định |
| **dev** | `http://localhost:8000` | Lambda trên AWS | mặc định khi ở máy |
| **local** | `http://localhost:8000` | `dotnet run` ở máy, cổng 5080 | `?api=local` |

```
?api=prod      ép dùng API trên AWS
?api=local     dùng API chạy ở máy
?api=<url>     trỏ tới stack thử nghiệm bất kỳ
?api=reset     xoá lựa chọn, về mặc định
```

Khi **không phải bản thật** (đang ở máy, hoặc đã ép `?api=`) thì góc dưới-trái hiện
một huy hiệu `LOCAL · API prod` / `API local` — người test nhìn là biết dữ liệu mình
vừa tạo nằm ở đâu, khỏi mở DevTools. Trên `astroq.org` với cấu hình mặc định thì
phần tử này **không được dựng ra**.

### Xem thử ở máy

```powershell
# Cửa sổ 1 — trang tĩnh
cd AstroQhtml
python -m http.server 8000        # http://localhost:8000/landing-app.html

# Cửa sổ 2 — CHỈ khi muốn dùng backend ở máy
cd AstroqSV/src/AstroqSV.Api
dotnet run                        # http://localhost:5080  (health: /health)
```

`dotnet run` không cần Docker: `AddAWSLambdaHosting` chỉ kích hoạt khi thật sự chạy
trong Lambda, ở máy nó là một app Kestrel bình thường. **Nhưng nó vẫn dùng DynamoDB,
SES và Secrets Manager THẬT trên AWS** qua `~/.aws/credentials` — không có bản
DynamoDB local, nên dữ liệu test ở máy và ở server nằm chung một bảng.

### Link kích hoạt tự về đúng nơi đã đăng ký

Đây là phần khiến hai môi trường chạy song song được mà không cần hai backend.

Lambda đọc header `Origin` của lời gọi `POST /auth/register`, **đối chiếu allowlist**,
rồi ghi kết quả vào trường `continueUrl` của bản ghi chờ. Phải ghi ngay lúc đăng ký,
vì lúc bấm link thì request đến từ ứng dụng email — **không còn `Origin`** để biết
người này xuất phát từ đâu.

```
đăng ký ở localhost:8000  →  kích hoạt xong về  http://localhost:8000/landing-app.html
đăng ký ở astroq.org      →  kích hoạt xong về  https://astroq.org/landing-app.html
```

⚠️ **Bắt buộc đối chiếu allowlist.** Tin thẳng `Origin` thì kẻ tấn công đăng ký hộ
người khác rồi trỏ link kích hoạt về trang của hắn — đúng định nghĩa *open redirect*.
Đã kiểm: `Origin: https://astroq.org.evil.co` bị loại, rơi về mặc định.
Trước khi chuyển hướng còn đối chiếu **lần nữa**, phòng trường hợp allowlist bị thu
hẹp sau khi bản ghi đã nằm đó.

**Allowlist chỉ khai báo một chỗ**: tham số `AllowedOrigins` trong `template.yaml`,
dùng cho **cả hai** việc — CORS của API Gateway (`!Ref`) và biến `ALLOWED_ORIGINS`
mà `Services/Origins.cs` đọc. Thêm môi trường mới thì sửa đúng một dòng rồi deploy.
Bản chạy ở máy đọc cùng danh sách từ `appsettings.Development.json` (phải giữ khớp
tay, vì máy không đọc được CloudFormation).

Đã kiểm 5 trường hợp: astroq.org · localhost:8000 · 127.0.0.1:5173 · origin giả mạo ·
không gửi Origin — **15/15 đạt**.

---

## 1. Quyết định phải chốt TRƯỚC: ai lo xác thực?

Đây là điểm quan trọng nhất, quyết định luôn khối lượng công việc.

Bạn vừa tích hợp xong **Firebase Auth** (đăng ký, đăng nhập, xác minh email). Giờ danh sách API
lại có `đăng ký tài khoản`, `đăng nhập` và dùng **SES gửi email** — tức là **làm lại đúng việc đó
lần thứ hai**. Hai hệ xác thực chạy song song sẽ sinh mâu thuẫn: tài khoản tồn tại ở Firebase nhưng
không có ở DynamoDB, hoặc ngược lại.

### Phương án A — Firebase lo danh tính, Lambda lo dữ liệu *(khuyên dùng)*

```
Client ──(email+mật khẩu)──▶ Firebase Auth ──▶ trả ID token (JWT)
Client ──(Bearer <ID token>)──▶ API Gateway ──▶ Lambda ──▶ DynamoDB
                                     └── xác thực JWT bằng khoá công khai của Google
```

- **Không viết** `/auth/register`, `/auth/login`, `/auth/verify` — Firebase đã làm.
- Không phải tự lo: băm mật khẩu, phát/thu hồi token, luồng quên mật khẩu, chống dò mật khẩu.
- SES chỉ dùng cho **thông báo** (báo cáo tuần cho phụ huynh, nhắc học), không dùng cho xác thực.
- Lambda chỉ cần verify JWT → lấy `uid` → truy vấn DynamoDB.
- **Ít code hơn khoảng một nửa**, và không có rủi ro tự quản lý mật khẩu trẻ em.

### Phương án B — Lambda lo tất cả, bỏ Firebase

Đúng như danh sách bạn liệt kê. Nhưng phải tự viết thêm:

- Băm mật khẩu bằng Argon2id hoặc PBKDF2 (**tuyệt đối không** SHA256 trần).
- Phát JWT + refresh token, xử lý thu hồi.
- Sinh token xác minh email, hết hạn, chống dùng lại → gửi qua SES.
- Luồng quên mật khẩu với token một lần.
- Giới hạn tần suất chống dò mật khẩu (Firebase làm sẵn việc này).
- Gỡ bỏ toàn bộ Firebase khỏi client.

**Khuyến nghị: chọn A.** Đây là nền tảng cho trẻ em, dữ liệu cá nhân của trẻ chịu ràng buộc
Nghị định 13/2023/NĐ-CP. Tự quản lý mật khẩu là nhận thêm rủi ro mà không đổi lại lợi ích gì.

> Tài liệu bên dưới viết cho **phương án A**. Phần riêng của phương án B nằm ở [mục 9](#9-phụ-lục--nếu-chọn-phương-án-b).

---

## 2. Kiến trúc

```
                 ┌──────────────── AWS ────────────────────────────┐
astroq.org       │                                                  │
(GitHub Pages)   │   API Gateway (HTTP API)                         │
      │          │        │  CORS: https://astroq.org                │
      │  fetch   │        ▼                                          │
      └─────────▶│   Lambda  AstroqSV  (dotnet10, arm64)             │
   Bearer <JWT>  │        │                                          │
                 │        ├──▶ DynamoDB  astroq-main  (single-table) │
                 │        ├──▶ SES v2    (email thông báo)           │
                 │        └──▶ CloudWatch Logs  /aws/lambda/AstroqSV │
                 └──────────────────────────────────────────────────┘
```

**Vì sao `dotnet10`:** đã kiểm tra tài liệu AWS — `dotnet10` là **managed runtime** trên Amazon
Linux 2023, hỗ trợ tới **14/11/2028**. `dotnet9` chỉ chạy được dạng **container**, còn `dotnet8`
hết hỗ trợ **10/11/2026**. Chọn .NET 10 là đúng.

**Vì sao HTTP API (không phải REST API):** rẻ hơn đáng kể, độ trễ thấp hơn, CORS cấu hình gọn.
astroQ không cần các tính năng nâng cao của REST API.

**arm64 (Graviton):** rẻ hơn x86 khoảng 20% với cùng hiệu năng.

---

## 3. Cấu trúc thư mục

Đặt **ngang hàng** với `AstroQhtml/`, không đặt bên trong — repo đó deploy lên GitHub Pages,
mọi file trong đó đều công khai.

```
astroq/
├── AstroQhtml/            ← frontend hiện tại (GitHub Pages)
└── AstroqSV/              ← backend mới
    ├── AstroqSV.sln
    ├── template.yaml                    # AWS SAM — hạ tầng dạng mã
    ├── samconfig.toml
    ├── .gitignore
    ├── src/
    │   └── AstroqSV.Api/
    │       ├── AstroqSV.Api.csproj
    │       ├── Program.cs               # Minimal API + đăng ký Lambda host
    │       ├── Auth/
    │       │   └── FirebaseTokenValidator.cs
    │       ├── Endpoints/
    │       │   ├── MeEndpoints.cs       # hồ sơ, ví
    │       │   ├── LessonEndpoints.cs   # bài học
    │       │   └── HistoryEndpoints.cs  # lịch sử
    │       ├── Data/
    │       │   ├── DynamoContext.cs
    │       │   └── Entities.cs
    │       └── Services/
    │           └── EmailService.cs      # SES v2
    └── tests/
        └── AstroqSV.Tests/
```

---

## 4. Thiết kế DynamoDB — một bảng duy nhất

Bảng `astroq-main`, khoá `PK` (partition) + `SK` (sort). Kiểu **single-table design** — chuẩn của
DynamoDB, tránh join và giữ mọi truy vấn ở mức một lần đọc.

| Thực thể | PK | SK | Thuộc tính |
|---|---|---|---|
| Hồ sơ | `USER#<uid>` | `PROFILE` | `name`, `email`, `character`, `avatar`, `createdAt`, **`tourSeen`, `tourSeenAt`, `intro01Seen`, `intro01SeenAt`, `profileUpdatedAt`** |
| **Tiến độ** | `USER#<uid>` | **`PROGRESS`** | `xp`, `quizTaken/Answered/Correct/Perfect`, `gamesPlayed`, `lessonsRead`, `flightSeconds`, `meteorsEarned`, `planets` (SS), `bests` (M), `consts` (M), `desk` (L), `badges` (M: id → ngày mở), **`missions` (M: id nhiệm vụ → M: id bước → ngày xong)** |
| Ví | `USER#<uid>` | `WALLET` | `meteors`, `diamonds`, `updatedAt` |
| **Nhật ký** | `USER#<uid>` | **`HIST#<ISO8601>#<4 hex>`** | `type` (quiz/game/lesson/planet/mission), `refId`, `at`, `xp`, `meteors`, `ttl` (400 ngày) + tuỳ loại: `correct`/`total` (quiz), `score`/`seconds` (game) |
| Bài đã đọc | `USER#<uid>` | `READ#<lessonId>` | `readAt` — ghi có điều kiện, chống đọc lại để farm |
| **Chống trùng** | `USER#<uid>` | **`OP#<opId>`** | `at`, `ttl` (7 ngày) — xem mục 5 |
| Bài học | `LESSON#<id>` | `META` | `title`, `topic`, `level`, `body`, `reward` |

**Vì sao gộp một bảng:** lấy toàn bộ dữ liệu của một người chỉ cần **một** query
`PK = USER#<uid>` — nhanh và rẻ hơn nhiều so với gọi 4 bảng.

**Điểm phải nhớ:** `HIST#<ISO8601>` cho phép sắp xếp lịch sử theo thời gian mà không cần index phụ,
vì chuỗi ISO 8601 sắp xếp theo thứ tự từ điển trùng với thứ tự thời gian. Nhờ vậy báo cáo một
tuần chỉ là `SK BETWEEN :dauTuan AND :cuoiTuan` — không cần GSI.

⚠️ **Nhật ký là NGUYÊN LIỆU DUY NHẤT cho báo cáo gửi phụ huynh** (nối 09/08/2026). Bộ đếm ở
`PROGRESS` là **tổng cả đời, không có trục thời gian**, nên "tuần này con làm bao nhiêu câu"
không tính ra được từ chúng.

⚠️ **Hậu tố 4 hex sau mốc thời gian là bắt buộc:** `PutItem` ghi đè khi trùng khoá, mà hàng chờ
ở client (`astroq-progress-queue`, tối đa 40 việc) gửi lại thành một loạt liên tiếp — hai việc
rơi vào cùng một mốc là một dòng biến mất, im lặng. Tiền tố ISO vẫn quyết định thứ tự sắp xếp.

⚠️ **Chỉ ghi ở nhánh `counted:true`.** `POST /me/progress` có ba đường ra sớm không tính công
(trùng `opId` · đọc lại bài · ghé lại hành tinh); ghi trước chúng là báo cáo thổi phồng số lượt
của trẻ. Có phép kiểm riêng cho cả ba ở `scratchpad/test_history.py`.

⚠️ **`ttl` 400 ngày** — khác `WAITLIST#` (cố ý không có TTL). Đây là nhật ký sự kiện; tổng cả đời
nằm ở `PROGRESS` và không bao giờ hết hạn, nên chỉ mất phần chi tiết theo tuần cũ hơn ~13 tháng.

**Chế độ:** `PAY_PER_REQUEST` (on-demand). Lưu lượng của astroQ giai đoạn đầu rất thấp và không đều
— on-demand không phải đoán capacity và gần như miễn phí ở mức nhỏ.

**TTL:** bật trên thuộc tính `ttl` cho các bản ghi lịch sử cũ nếu muốn tự dọn sau N tháng.

---

## 5. Danh sách API

Tất cả (trừ `/health` và `/lessons`) yêu cầu header `Authorization: Bearer <Firebase ID token>`.

✅ = đã deploy và có bộ test chạy được. Còn lại là thiết kế, chưa viết.

| Method | Đường dẫn | Việc |
|---|---|---|
| `GET` | `/health` | ✅ Kiểm tra sống — không cần token |
| `GET` | `/me/onboarding` | ✅ Cờ các màn giới thiệu → `{tourSeen, tourSeenAt, intro01Seen, intro01SeenAt}` |
| `PUT` | `/me/onboarding` | ✅ Ghi cờ. Body `{tourSeen?, intro01Seen?}` — **chỉ ghi cờ được gửi**; body rỗng = `tourSeen:true` (giữ hành vi cũ) |
| `GET` | `/me/profile` | ✅ Hồ sơ + ví + cấp độ + tiến độ, một lần gọi (`profile.html`) |
| `GET` | `/me/wallet` | ✅ Số dư Thiên thạch tím |
| `POST` | `/me/wallet/spend` | ✅ Trừ phí một lượt. Body `{reason:"game", game, opId}` — **KHÔNG nhận số tiền** |
| `PUT` | `/me/profile` | ✅ Đổi tên / nhân vật / avatar. Body `{name?, character?, avatar?}` |
| `GET` | `/me/achievements` | ✅ Huy hiệu + tiến độ từng cái + cấp độ (`achievements.html`) |
| `POST` | `/me/progress` | ✅ Báo **một việc đã làm** → server tự cộng XP + mở huy hiệu |
| `GET` | `/me/missions` | ✅ Trạng thái nhiệm vụ → `{steps, doneSteps, done, doneAt, codex, codexTotal, unlocks}` |
| `POST` | `/me/missions/step` | ✅ Báo **xong một bước nhiệm vụ**. Body `{mission, step, opId}` — **KHÔNG nhận con số thưởng nào** |
| `GET` | `/me/specimens` | ✅ Kho Mẫu Vật (suy ra từ bộ đếm, không có route "đã thu thập") |
| `PUT` | `/me/specimens/desk` | ✅ Mẫu vật trưng ở khoang lái. Body `{desk:[id,…]}` |
| `GET` | `/me/report` | ✅ Báo cáo tuần cho phụ huynh (`parent.html`) |
| `POST` | `/me/report/email` | ✅ Gửi báo cáo tuần qua SES |
| `GET` | `/admin/stats` | ✅ **Báo cáo toàn hệ thống** cho chủ dự án (`admin-report.html`). `?refresh=1` = bắt tính lại |
| `GET` | `/me` | *(gộp vào `/me/profile`)* |
| `PUT` | `/me` | *(gộp vào `/me/profile`)* |
| `POST` | `/me/wallet` | *(đã thay bằng `/me/wallet/spend` + phần cộng thưởng trong `/me/progress`)* |
| `GET` | `/me/history` | Lịch sử hoạt động, phân trang bằng `cursor` |
| `POST` | `/me/history` | Ghi một sự kiện (làm quiz, đọc bài, chơi game) |
| `GET` | `/lessons` | Danh sách bài học — công khai, cache được |
| `GET` | `/lessons/{id}` | Chi tiết một bài |
| `POST` | `/me/lessons/{id}/complete` | Đánh dấu đã học xong + cộng thưởng |

### `/admin/stats` — nhóm route DUY NHẤT đọc được dữ liệu của mọi người *(thêm 11/08/2026)*

Mọi route `/me/*` lấy uid **từ token**, nên không ai đọc được hồ sơ người khác. `/admin/*`
là ngoại lệ có chủ ý: nó gộp cả bảng thành chỉ số sức khoẻ dự án. Vì thế nó có ba lớp mà
các nhóm khác không có.

**① Ai vào được — allowlist trong biến môi trường, mặc định RỖNG**

`Services/AdminAuth.cs` đọc `ADMIN_EMAILS` (tham số `AdminEmails` của stack). Policy
`"admin"` gắn ở **cấp group** trong `AdminEndpoints`, y như `/me` dùng `"verified"` — thêm
route vào nhóm đó là tự có bảo vệ.

Hiện `AdminEmails` mặc định là **`trangtt.tshn@gmail.com`** trong `template.yaml`, nên
`sam deploy` trơn là đủ. Đổi hoặc thêm admin:

```bash
sam deploy --parameter-overrides AdminEmails=a@x.com,b@y.com
```

Để địa chỉ thẳng trong `Default` được vì `AstroqSV/` **không phải git repo** — chỉ
`AstroQhtml/` mới đẩy lên GitHub Pages. Nếu sau này đưa backend vào một repo công khai
thì phải bỏ nó khỏi `Default` và truyền lúc deploy.

- **Rỗng = không ai vào được.** Khác cố ý với `ALLOWED_ORIGINS` (có `Fallback`): quên cấu
  hình CORS thì trang hỏng ầm ĩ, sửa ngay; còn để một địa chỉ dự phòng trong mã nguồn công
  khai thì đó là cửa đọc số liệu cả hệ thống.
- **Đòi cả `email_verified`.** Firebase cho client tự `signUp` bằng apiKey công khai, nên
  một tài khoản *khai* email của admin là chuyện dựng được. So khớp email mà không kiểm cờ
  xác minh là để bất kỳ ai cũng vào được.
- Chạy ở máy thì đặt `ADMIN_EMAILS` trong `appsettings.Development.json`.

**② Vì sao phải `Scan` cả bảng, và vì sao có bản chụp**

Bảng chỉ có PK/SK, **không có GSI**. Mọi câu hỏi dạng "tất cả người dùng…" (DAU, giữ chân,
phễu) đều cắt NGANG các PK — không có khoá nào query được. Đó là cái giá đã biết của thiết
kế một bảng.

Nên kết quả được cache thành **một bản ghi `PK=STATS#GLOBAL, SK=SNAPSHOT`** giữ JSON đã
serialize:

| | |
|---|---|
| Quá `15 phút` | lượt gọi tiếp theo tự quét lại |
| `?refresh=1` | bắt quét lại ngay, có cooldown `60s` (trả `throttled:true` + bản cũ, **không** 429) |
| Quét hỏng | trả **bản chụp cũ** kèm `stale:true` — số liệu 30 phút trước còn dùng được, một trang trắng thì không |
| Chưa có bản chụp nào và quét hỏng | `503 {code:"scan-failed"}` |
| Bản chụp > 380 KB | **vẫn trả cho client**, chỉ không lưu được; ghi `LogWarning` để còn hạ `Insights.TopN`/`UserRows` |

**Đường nâng cấp đã chừa sẵn:** khi bảng lớn tới mức quét không kịp 20 giây của Lambda,
thay chỗ **ghi** snapshot bằng một job EventBridge chạy đêm. Route đọc và cả trang admin
không phải sửa gì — chúng chỉ biết tới bản chụp.

### ⚠️ `?refresh=1` trả 400 — minimal API bind `bool?` bằng `bool.TryParse`

Đã xảy ra thật ngày 11/08/2026, ngay trên lượt deploy đầu tiên. Handler khai
`bool? refresh`, client gửi `?refresh=1` → **400 Bad Request với thân rỗng**, tức nút
"Tính lại ngay" hỏng hoàn toàn trong khi dải nhắc ở client lại báo *"không gọi được
server"*. `bool.TryParse` CHỈ nhận `"true"`/`"false"`; `"1"` và `"0"` đều trượt.

Không phép kiểm nào trước đó bắt được, và lý do đáng ghi lại:
* bộ kiểm `Insights` chạy trên dữ liệu bịa nên **không đi qua tầng bind**;
* test frontend **giả luôn `AstroQAuth`** nên không bao giờ dựng URL thật;
* `curl` lúc kiểm cổng gọi `/admin/stats` **không kèm tham số** (401 xảy ra trước bind).

Chỉ một lượt gọi thật với token thật + tham số thật mới lộ ra. **Sau mỗi lần deploy,
gọi endpoint mới bằng token thật kèm ĐỦ các tham số nó nhận** — không chỉ kiểm mã trạng
thái của đường trống.

Nay `refresh` nhận `string?` và tự đọc (`Truthy`): nhận `1` / `true` / `yes` / `on`,
mọi thứ khác là false. Cố ý dễ tính — trả 400 vì người ta gõ `1` thay vì `true` là bắt
người dùng học cú pháp bind của ASP.NET. Đọc không ra thì **không** tính lại: hướng hỏng
an toàn (dùng bản chụp) chứ không phải hướng đắt tiền (quét cả bảng).

**③ Báo cáo KHÔNG chứa email, tên hay avatar của ai**

Bảng người dùng chỉ có **8 ký tự đầu của uid**. Dữ liệu ở đây là của trẻ em, và một trang
theo dõi chỉ số không cần biết tên đứa trẻ để trả lời được "app có giữ được người dùng
không". Bộ kiểm ở `Insights` có phép kiểm khẳng định JSON không lọt email và không lọt uid
đầy đủ.

**Ba giới hạn `Services/Insights.cs` PHẢI nói ra, không được làm tròn thành 0**

1. **Nhật ký chỉ chảy từ `LogSince` (09/08/2026).** Mọi chỉ số theo trục thời gian đều rỗng
   trước mốc đó và **không backfill được**. `LogSince` nay là **bản chính** của mốc này và
   được trả ra client trong `report.logSince` — trước đó nó chỉ tồn tại ở `parent.html` dưới
   tên `LOG_SINCE`.
2. **"Im lặng" chỉ đếm người đăng ký TỪ mốc đó.** Tài khoản mở trước khi có nhật ký mà không
   có sự kiện nào thì không phải người dùng im lặng — chỉ là những ngày đầu của họ không
   được ghi. Gộp hai nhóm là bịa ra một tỉ lệ rời app.
3. **Phễu onboarding cố ý tính trên TẤT CẢ người dùng** — nó đọc cờ `PROFILE` và bộ đếm
   cả-đời `PROGRESS`, hai thứ có từ trước nhật ký. Cắt phễu theo mốc nhật ký là tự bỏ đi
   phần lớn dữ liệu đang có. Hệ quả: **một bậc không bao hàm bậc trước** (trẻ bỏ qua tour
   vẫn làm được quiz) nên số có thể TĂNG giữa hai bậc, và trang vẽ đúng con số chứ không kẹp
   cho phễu thu hẹp đẹp mắt.

Giữ chân tính kiểu **"trôi"** (có việc từ ngày thứ N trở đi), không phải "đúng ngày thứ N":
ở quy mô vài chục người, một trẻ vào app ngày thứ 8 chứ không phải ngày thứ 7 sẽ làm D7 tụt
về 0 và đọc ra kết luận sai.

**Cửa sổ 90 ngày, tính MỘT LẦN.** Nút 7/30/90 ngày ở trang admin chỉ cắt chuỗi ở client —
mỗi lựa chọn một lượt quét thì mỗi cú bấm là một lần đọc cả bảng và bản chụp mất tác dụng.

### Hệ nhiệm vụ — chỗ DUY NHẤT phần thưởng KHÔNG THỂ bịa

`Services/Missions.cs` giữ toàn bộ bảng luật; client **không gửi một con số nào**, chỉ gửi
`{mission, step}`:

```jsonc
POST /me/missions/step   { "mission":"earth", "step":"sun", "opId":"…" }
```

```csharp
new("earth", "earth", [
    new("scan",     0,  20, null),
    new("sun",      20, 30, "sun"),
    new("rotation", 20, 30, "rotation"),
    new("life",     20, 40, "water,forest,animal,mountain"),
    new("core",     20, 40, null)
], DoneMeteors: 100, DoneXp: 120, Unlocks: "moon");
```

**Vì sao nhiệm vụ khác hẳn mini-game.** Điểm mini-game là con số client tự khai (server chỉ kẹp
trần `Wallet.MaxRewardFor`) vì màn chơi chạy ở máy người dùng và server không xem lại được. Nhiệm vụ
thì mỗi bước có **id cố định**, nên server tra bảng là biết đúng phải cộng bao nhiêu — đây là chỗ
duy nhất trong app phần thưởng hoàn toàn không bịa được.

**Ba chốt chặn:**

1. **Mỗi bước tính MỘT lần** — `MarkMissionStepAsync` ghi `missions.<mission>.<step>` với
   `ConditionExpression attribute_not_exists(#m.#q.#s)`. Không phải đọc-rồi-so ở tầng ứng dụng
   (hai lời gọi song song đều thấy "chưa có").
2. **Hai map lồng nhau phải tạo bằng HAI lời gọi tường minh** (`missions`, rồi `missions.<mission>`),
   mỗi lời gọi có `attribute_not_exists` riêng — thứ tự `Dictionary.Keys` trong .NET **không được
   bảo đảm**, gộp lại thì có lúc ghi map con trước map cha và DynamoDB trả lỗi.
3. **`opId`** (`SK=OP#<opId>`, TTL 7 ngày) — gửi lại từ hàng chờ khi mất mạng thì không cộng lần hai.

**Xong bước cuối** → server tự ghi thêm `"done"`, cộng bó `DoneMeteors`/`DoneXp`, tính là **đã ghé
hành tinh** (`BumpProgressAsync` với `m.Planet`) và mở huy hiệu `rookie-astronaut`
(`metric = "mission:earth"`). Tổng của nhiệm vụ Trái Đất: **180 tt · 280 XP · Codex 6/6**.

⚠️ Cả hai nhánh trả về sớm (`opId` trùng · bước đã xong) **phải trả cùng hình dạng** với nhánh thành
công — có `missionDone:false, unlocks:null, counted:false`. Thiếu thì client phải tự đoán "không có
= false", rất dễ sai.

### Nguyên tắc bảo mật quan trọng nhất

**Không bao giờ để client gửi lên số dư.** Sai:

```jsonc
POST /me/wallet   { "meteors": 999999 }     // ❌ ai cũng sửa được bằng DevTools
```

Đúng — client báo *việc đã làm*, server tự quyết thưởng bao nhiêu:

```jsonc
POST /me/lessons/quantum-01/complete   { }  // ✅ server tra bảng, cộng đúng phần thưởng
POST /me/history  { "type":"quiz", "refId":"ai-l1-q3", "correct":true }
```

**Đã làm được tới đâu (29/07/2026).** `economy.js` giờ chỉ còn là *cache*:

| Việc | Ai quyết | Chốt chặn |
|---|---|---|
| **Phí** một lượt chơi | **SERVER hẳn** — client chỉ gửi `game`, server tra `Wallet.Fees` | `UpdateItem` + `ConditionExpression meteors >= :n` (nguyên tử, không âm, không trừ 2 lần) |
| **Thưởng** tt mỗi lượt | Server **đặt TRẦN** theo loại việc (`Wallet.Award`) | kẹp về `[0, trần]`; `opId` chống cộng 2 lần |
| **XP / cấp độ / huy hiệu** | **SERVER hẳn** (`Achievements.cs`) | client gửi xp/badges lên thì bị bỏ qua |
| **Đọc bài / ghé hành tinh** | Server, tính **một lần duy nhất** | `READ#<id>` ghi có điều kiện; `planets` là string set |

⚠️ **Chỗ còn hở, nói rõ để không tự lừa mình:** số tt thu được *trong* một lượt game
là con số client tự khai — game chạy trên máy người dùng nên server không có cách nào
tính lại. Trần chặn được mọi con số vô lý nhưng không chặn được người quyết tâm sửa
DevTools trong khoảng dưới trần. Muốn không thể bịa thì server phải sinh và kiểm câu
hỏi / màn chơi (server-authoritative gameplay) — việc lớn, chưa làm.

⚠️ **`opId` là bắt buộc, không phải tuỳ chọn.** Client xếp việc vào hàng chờ khi mất
mạng (`js/progress.js`). Nếu server đã xử lý xong mà phản hồi mất giữa đường thì client
gửi lại — không có `opId` thì một lượt quiz **cộng tiền hai lần** và một lượt game **bị
trừ phí hai lần**. Bản ghi `SK=OP#<opId>` ghi có điều kiện, TTL 7 ngày.

---

## 6. Mã nguồn

### `src/AstroqSV.Api/AstroqSV.Api.csproj`

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <!-- Lambda chạy arm64 (Graviton) — rẻ hơn x86 ~20% -->
    <RuntimeIdentifier>linux-arm64</RuntimeIdentifier>
    <PublishReadyToRun>true</PublishReadyToRun>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Amazon.Lambda.AspNetCoreServer.Hosting" Version="1.*" />
    <PackageReference Include="AWSSDK.DynamoDBv2" Version="4.*" />
    <PackageReference Include="AWSSDK.SimpleEmailV2" Version="4.*" />
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="10.*" />
  </ItemGroup>
</Project>
```

> Version dùng `*` để lấy bản mới nhất tương thích. Khi chốt production nên ghim số cụ thể
> (`dotnet list package` rồi copy) để build lặp lại được.

### `Program.cs`

```csharp
using Amazon.DynamoDBv2;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// Biến "ASP.NET Core minimal API" thành Lambda handler. Đây là toàn bộ phần "chạy trên Lambda".
// Bỏ dòng này thì app chạy y hệt như web thường ở máy — tiện để debug.
builder.Services.AddAWSLambdaHosting(LambdaEventSource.HttpApi);

builder.Services.AddSingleton<IAmazonDynamoDB>(_ => new AmazonDynamoDBClient());
builder.Services.AddSingleton<DynamoContext>();
builder.Services.AddSingleton<EmailService>();

// ---- Xác thực bằng Firebase ID token ----
// Google ký JWT bằng khoá xoay vòng; JwtBearer tự tải và cache bộ khoá công khai.
var projectId = builder.Configuration["FIREBASE_PROJECT_ID"] ?? "astroq-782f7";
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.Authority = $"https://securetoken.google.com/{projectId}";
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer   = true,  ValidIssuer   = $"https://securetoken.google.com/{projectId}",
            ValidateAudience = true,  ValidAudience = projectId,
            ValidateLifetime = true
        };
    });
builder.Services.AddAuthorization();

// ---- CORS: chỉ cho đúng tên miền của mình ----
const string Cors = "astroq";
builder.Services.AddCors(o => o.AddPolicy(Cors, p => p
    .WithOrigins("https://astroq.org", "http://127.0.0.1:5173", "http://localhost:5173")
    .AllowAnyHeader()
    .WithMethods("GET", "POST", "PUT", "OPTIONS")));

var app = builder.Build();
app.UseCors(Cors);
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/health", () => Results.Ok(new { ok = true, at = DateTime.UtcNow }));

app.MapMeEndpoints();        // /me, /me/wallet, /me/history
app.MapLessonEndpoints();    // /lessons
app.MapHistoryEndpoints();

app.Run();
```

### `Endpoints/MeEndpoints.cs`

> **File này ĐÃ TỒN TẠI thật** (`src/AstroqSV.Api/Endpoints/MeEndpoints.cs`) và hiện chứa
> `GET|PUT /me/onboarding`. Đoạn mã dưới đây là **bản thiết kế cho các route còn lại** —
> đọc mã thật để biết cách nhóm `/me` đang được bảo vệ và cách lấy `uid`.
>
> Ba điểm đã áp dụng trong mã thật, giữ nguyên khi thêm route:
> 1. `RequireAuthorization()` gắn ở **cấp group**, không gắn từng route — thêm route mới
>    là tự có bảo vệ, không phụ thuộc việc người viết có nhớ hay không.
> 2. **uid lấy từ token**, thử lần lượt `user_id` → `NameIdentifier` → `sub`.
> 3. Ghi bằng `UpdateItem` + `ConditionExpression attribute_exists(PK)` để **không âm thầm
>    sinh ra hồ sơ rỗng** khi uid không tồn tại — hồ sơ chỉ được tạo ở `CreateUserAsync`.
>
> Bộ test độc lập: `AstroQhtml/scratchpad/test_onboarding.py` (tự tạo tài khoản Firebase tạm
> để có ID token thật, tự dọn sạch sau khi chạy).

```csharp
public static class MeEndpoints
{
    public static void MapMeEndpoints(this WebApplication app)
    {
        var g = app.MapGroup("/me").RequireAuthorization();

        // Lấy uid từ JWT — KHÔNG bao giờ nhận uid từ body, client sửa được.
        static string Uid(HttpContext c) =>
            c.User.FindFirst("user_id")?.Value
            ?? c.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)!.Value;

        g.MapGet("/", async (HttpContext c, DynamoContext db) =>
        {
            var uid = Uid(c);
            var items = await db.QueryUserAsync(uid);          // 1 query lấy hết
            return Results.Ok(new
            {
                profile = items.Profile,
                wallet  = items.Wallet ?? new Wallet { Meteors = 0, Diamonds = 0 }
            });
        });

        // Server tự quyết thưởng. Client chỉ báo "đã hoàn thành cái gì".
        g.MapPost("/lessons/{id}/complete", async (
            string id, HttpContext c, DynamoContext db) =>
        {
            var uid = Uid(c);
            var lesson = await db.GetLessonAsync(id);
            if (lesson is null) return Results.NotFound();

            // Đã nhận thưởng bài này rồi thì không cộng lần hai.
            if (await db.HasReadAsync(uid, id))
                return Results.Ok(new { rewarded = false });

            await db.MarkReadAsync(uid, id);
            var wallet = await db.AddMeteorsAsync(uid, lesson.Reward);
            await db.AddHistoryAsync(uid, "lesson", id, lesson.Reward);
            return Results.Ok(new { rewarded = true, reward = lesson.Reward, wallet });
        });
    }
}
```

### `template.yaml` — hạ tầng dạng mã (AWS SAM)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: AstroqSV — backend astroQ.org

Globals:
  Function:
    Runtime: dotnet10
    Architectures: [arm64]
    MemorySize: 512          # .NET khởi động nhanh hơn khi có nhiều RAM; 512 là điểm cân bằng tốt
    Timeout: 15
    Environment:
      Variables:
        TABLE_NAME: !Ref MainTable
        FIREBASE_PROJECT_ID: astroq-782f7
        SES_FROM: no-reply@astroq.org

Resources:
  Api:
    Type: AWS::Serverless::HttpApi
    Properties:
      CorsConfiguration:
        AllowOrigins: ['https://astroq.org', 'http://127.0.0.1:5173']
        AllowHeaders: ['authorization', 'content-type']
        AllowMethods: [GET, POST, PUT, OPTIONS]

  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: AstroqSV
      CodeUri: src/AstroqSV.Api/
      Handler: AstroqSV.Api
      Events:
        Proxy:
          Type: HttpApi
          Properties: { ApiId: !Ref Api, Path: /{proxy+}, Method: ANY }
      Policies:
        - DynamoDBCrudPolicy: { TableName: !Ref MainTable }
        - SESCrudPolicy:      { IdentityName: astroq.org }

  MainTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: astroq-main
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - { AttributeName: PK, AttributeType: S }
        - { AttributeName: SK, AttributeType: S }
      KeySchema:
        - { AttributeName: PK, KeyType: HASH }
        - { AttributeName: SK, KeyType: RANGE }
      TimeToLiveSpecification: { AttributeName: ttl, Enabled: true }
      PointInTimeRecoverySpecification: { PointInTimeRecoveryEnabled: true }

Outputs:
  ApiUrl:
    Description: Dán giá trị này vào js/api-config.js của frontend
    Value: !Sub 'https://${Api}.execute-api.${AWS::Region}.amazonaws.com'
```

---

## 7. Triển khai

```bash
cd AstroqSV
rm -rf .aws-sam               # xem cảnh báo bên dưới — bỏ bước này là có ngày deploy gói rỗng
sam build                     # biên dịch .NET 10 cho arm64
ls .aws-sam/build/ApiFunction # PHẢI có file, không được rỗng
sam deploy --guided           # lần đầu: chọn region ap-southeast-1 (Singapore, gần VN nhất)
                              # các lần sau chỉ cần: sam deploy
```

`sam deploy` **tự tạo bảng DynamoDB, Lambda, API Gateway, IAM role** theo `template.yaml`.
Không cần bấm gì trên AWS Console. Kết thúc sẽ in ra `ApiUrl`.

Máy hiện tại chưa có `sam` trong PATH của bash; đường dẫn đầy đủ là
`C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd`. Không có `samconfig.toml` (đã
`.gitignore`), nên phải truyền tham số:

```powershell
& "C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy `
  --stack-name astroqsv --region ap-southeast-1 `
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-jte6tycqojsq `
  --s3-prefix astroqsv --capabilities CAPABILITY_IAM `
  --no-fail-on-empty-changeset --no-confirm-changeset
```

### Bật đường Conversions API của Meta *(thêm 26/08/2026)*

> **Dự án CỐ Ý không gắn Meta Pixel lên trang.** Việc báo chuyển đổi đi qua
> **Conversions API gửi từ server** (`Services/MetaCapi.cs`). Ba lý do, và cả ba đều
> là số đo chứ không phải sở thích: giữ được hàng rào *"không script từ tên miền
> ngoài"* (`check_pages` mục **[14]**) · không thêm ~50 KB vào trang của trẻ · và
> **không gửi hành vi duyệt của từng đứa trẻ cho bên thứ ba**. Thứ duy nhất rời khỏi
> server là một sự kiện *"đã tạo tài khoản"* kèm `fbc` — mã lượt bấm mà **chính Meta**
> đã gắn vào link nó phát đi. Không IP, không user-agent, không email.

**Dataset ID của astroQ: `1601174631375979`** (Events Manager, 26/08/2026).

⚠️⚠️ **Nó KHÔNG nằm trong `Default` của `MetaDatasetId`, và đừng đưa vào.**
`Default: ''` là **công tắc TẮT**; `scratchpad/check_meta_capi.py` mục **[2]** canh
đúng chuyện đó và báo hỏng nếu ai điền vào. Lý do: đặt số vào `Default` biến một
`sam deploy` trơn — kể cả lượt deploy chỉ để sửa một thứ chẳng liên quan — thành lượt
**âm thầm bắt đầu gửi dữ liệu cho Meta**. Bật một đường gửi ra ngoài phải là một câu
người ta **gõ ra**.

**Hai bước, theo thứ tự:**

```bash
# ① Cất access token (KHÔNG phải Dataset ID) vào Secrets Manager.
#    Lấy token ở Events Manager → dataset → Settings → Conversions API →
#    "Set up without Dataset Quality API" → Generate access token.
#    ⚠️ Dán token vào lệnh này ở terminal của bạn, đừng để nó vào file nào trong repo.
aws secretsmanager create-secret --region ap-southeast-1 \
  --name astroq/meta-capi-token --secret-string '<DÁN_TOKEN_VÀO_ĐÂY>'
# (đã tồn tại thì dùng: aws secretsmanager put-secret-value --secret-id astroq/meta-capi-token --secret-string '...')
```

```powershell
# ② Deploy KÈM cờ bật. Thiếu cờ = đường CAPI TẮT (hỏng nghiêng về không gửi gì cho ai).
& "C:\Program Files\Amazon\AWSSAMCLI\bin\sam.cmd" deploy `
  --stack-name astroqsv --region ap-southeast-1 `
  --s3-bucket aws-sam-cli-managed-default-samclisourcebucket-jte6tycqojsq `
  --s3-prefix astroqsv --capabilities CAPABILITY_IAM `
  --no-fail-on-empty-changeset --no-confirm-changeset `
  --parameter-overrides MetaDatasetId=1601174631375979
```

⚠️ **Muốn TẮT lại thì deploy KHÔNG kèm cờ đó** — đừng xoá secret. Xoá secret chỉ làm
lời gọi thất bại ở mỗi lượt đăng ký rồi nuốt lỗi (luật im lặng ở `MetaCapi.cs`), tức
tốn thời gian mỗi lần mà chẳng ai biết.

⚠️ **`check_meta_capi.py` soi VĂN BẢN, không gọi mạng — nó KHÔNG chứng minh được Meta
nhận sự kiện.** Việc đó phải kiểm bằng **Test Events** trong Events Manager với token
thật, sau khi deploy. Hai thứ bổ cho nhau: bộ đo canh *cái không được đổi*, Test Events
canh *cái có chạy*.

⚠️ **Bị chặn là chuyện thường gặp, KHÔNG phải chuyện chắc chắn:** `aws lambda
update-function-code` / `sam deploy` **thường** bị bộ phân loại quyền của Claude Code
chặn (mục 5 `CLAUDE.md`, ba đường đi ghi ở đó) — nhưng lượt **26/08/2026 chạy thẳng,
không chặn, không hỏi**. ⇒ Cứ **chuẩn bị gói cho xong** (tải gói đang chạy làm mốc
rollback · `dotnet publish` ra ngoài OneDrive · đối chiếu artifact) **rồi thử một lần**;
đừng bỏ cuộc trước khi thử, cũng đừng cho là sẽ chạy được.

### ⚠️ `sam build` hỏng giữa chừng → `sam deploy` gói thư mục RỖNG

Đã xảy ra thật ngày 29/07/2026. Dự án nằm trong OneDrive nên `sam build` có thể chết
với `PermissionError: [WinError 5]` khi xoá `.aws-sam/build/ApiFunction` cũ. Lúc đó
`sam build` **thất bại nhưng để lại thư mục rỗng**, và `sam deploy` chạy tiếp vẫn
đóng gói đúng cái thư mục đó → Lambda trả:

```
Uploaded file must be a non-empty zip (Status Code: 400)
```

CloudFormation tự `UPDATE_ROLLBACK_COMPLETE` nên **bản thật không bị hỏng** — nhưng
đừng dựa vào đó. Cách xử lý: xoá `.aws-sam` (có thể phải thử vài lần vì OneDrive giữ
file) rồi `sam build` lại. **Luôn kiểm thư mục artifact không rỗng trước khi deploy**
— `sam deploy` không tự phát hiện.

Sau khi deploy, chạy lại **cả hai** bộ test API lên bản thật, không chỉ bộ vừa viết:

```powershell
python scratchpad/test_onboarding.py https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com
python scratchpad/test_profile.py    https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com
```

### Quyền IAM tối thiểu cho người deploy

Đừng dùng root account. Tạo IAM user riêng với các policy: `AWSCloudFormationFullAccess`,
`AWSLambda_FullAccess`, `AmazonAPIGatewayAdministrator`, `AmazonDynamoDBFullAccess`,
`AmazonSESFullAccess`, `IAMFullAccess` *(cần để SAM tạo role cho Lambda)*, `AmazonS3FullAccess`
*(SAM dùng S3 làm nơi trung chuyển gói build)*.

Bản thân Lambda thì chỉ nhận đúng 2 quyền hẹp khai trong `Policies:` ở trên — nguyên tắc đặc quyền
tối thiểu.

---

## 8. Debug bằng CloudWatch

```bash
# Xem log trực tiếp, giống tail -f
sam logs -n ApiFunction --stack-name astroqsv --tail

# Hoặc bằng AWS CLI
aws logs tail /aws/lambda/AstroqSV --follow --since 10m

# Lọc chỉ dòng lỗi
aws logs filter-log-events --log-group-name /aws/lambda/AstroqSV \
  --filter-pattern 'ERROR' --start-time $(($(date +%s000) - 3600000))
```

Trong code cứ dùng `ILogger` bình thường, mọi thứ tự chảy vào CloudWatch:

```csharp
app.Logger.LogInformation("Cộng {Reward} meteors cho {Uid}", lesson.Reward, uid);
```

**Mẹo:** bật **Lambda Powertools for .NET** để log ra JSON có cấu trúc — CloudWatch Logs Insights
truy vấn được theo trường, đỡ phải grep chuỗi.

**Lưu ý chi phí:** đặt retention cho log group, mặc định là **giữ vĩnh viễn** và sẽ tốn tiền dần:

```bash
aws logs put-retention-policy --log-group-name /aws/lambda/AstroqSV --retention-in-days 14
```

---

## 9. SES — gửi email

**Trước khi gửi được cho người ngoài, phải thoát sandbox.** Tài khoản SES mới bị giới hạn: chỉ gửi
được tới địa chỉ đã tự xác minh. Mở ticket "Request production access" trong SES Console, thường
duyệt trong 24h.

Các bước:

1. SES Console → **Verified identities** → thêm domain `astroq.org` → thêm bản ghi DKIM vào DNS.
2. Xác minh domain xong thì gửi từ `no-reply@astroq.org` được.
3. Thiết lập **SPF** và **DMARC** trong DNS, nếu không email sẽ vào Spam.

```csharp
public class EmailService(IAmazonSimpleEmailServiceV2 ses, IConfiguration cfg)
{
    public async Task SendAsync(string to, string subject, string html)
    {
        await ses.SendEmailAsync(new SendEmailRequest
        {
            FromEmailAddress = cfg["SES_FROM"],
            Destination = new Destination { ToAddresses = [to] },
            Content = new EmailContent
            {
                Simple = new Message
                {
                    Subject = new Content { Data = subject, Charset = "UTF-8" },
                    Body = new Body { Html = new Content { Data = html, Charset = "UTF-8" } }
                }
            }
        });
    }
}
```

> Ở **phương án A**, SES **không** dùng cho xác minh tài khoản (Firebase lo rồi) — chỉ dùng cho
> báo cáo tiến độ gửi phụ huynh, nhắc học, thông báo huy hiệu mới.

---

## 10. Nối với frontend

Xem phần trả lời chi tiết ở [mục 12](#12-client-hiện-tại-có-gọi-được-api-không). Tóm tắt: thêm
`js/api.js` bọc `fetch`, tự đính kèm Firebase ID token.

```js
/* js/api.js — gọi AstroqSV. Vanilla, không thêm dependency. */
const API_BASE = "https://xxxx.execute-api.ap-southeast-1.amazonaws.com";

async function apiFetch(path, opts = {}){
  const headers = Object.assign({ "Content-Type": "application/json" }, opts.headers);
  // Lấy ID token mới nhất từ Firebase (tự làm mới khi hết hạn)
  const u = window.AstroQAuth && await AstroQAuth.currentUser();
  if(u) headers.Authorization = "Bearer " + await u.getIdToken();
  const res = await fetch(API_BASE + path, Object.assign({}, opts, { headers }));
  if(!res.ok) throw new Error("API " + res.status);
  return res.status === 204 ? null : res.json();
}

window.AstroQApi = {
  me:            ()             => apiFetch("/me"),
  history:       (cursor)       => apiFetch("/me/history" + (cursor ? "?cursor=" + cursor : "")),
  completeLesson:(id)           => apiFetch(`/me/lessons/${id}/complete`, { method: "POST" }),
  lessons:       ()             => apiFetch("/lessons")
};
```

`AstroQAuth.currentUser()` đã có sẵn trong `js/firebase-auth.js`. `getIdToken()` tự làm mới token
khi hết hạn (token Firebase sống 1 tiếng) nên không phải tự quản lý.

---

## 11. Ước lượng chi phí

[Ước lượng, không phải báo giá] Với lưu lượng giai đoạn đầu (dưới ~10.000 lượt gọi API/tháng),
gần như toàn bộ nằm trong free tier của AWS:

| Dịch vụ | Ghi chú |
|---|---|
| Lambda | Free tier 1 triệu request/tháng — dư sức |
| DynamoDB on-demand | Trả theo lượt đọc/ghi, mức nhỏ gần như bằng 0 |
| API Gateway HTTP API | Rẻ hơn REST API đáng kể |
| CloudWatch Logs | **Khoản dễ phát sinh nhất** nếu quên đặt retention |
| SES | Tính theo số email gửi đi |

Nên bật **AWS Budgets** cảnh báo ở ngưỡng vài USD ngay từ đầu — không phải vì sợ tốn, mà để phát
hiện sớm nếu có vòng lặp gọi API bất thường.

---

## 12. Client hiện tại có gọi được API không?

**Có. Không cần đổi công nghệ gì cả.**

HTML + vanilla JS gọi REST API bằng `fetch` là chuyện hoàn toàn bình thường — React/Vue không hề
có lợi thế nào ở khâu này, chúng chỉ khác ở cách quản lý giao diện. Dự án đã dùng `fetch` sẵn ở
`js/index.js` (gửi form waitlist lên `POST /waitlist` của chính backend này) và nó chạy tốt.

### Việc thật sự phải làm ở client

| Việc | Khối lượng |
|---|---|
| Thêm `js/api.js` (đoạn ở mục 10) | 1 file ~30 dòng |
| `economy.js`: đổi `localStorage` → gọi API | Sửa 3 hàm |
| `dashboard`/`quiz`/`learn`: đọc dữ liệu từ `/me` | Vài chỗ mỗi trang |
| Xử lý trạng thái đang tải và mất mạng | Việc mới |
| Cấu hình CORS ở API Gateway | Đã có trong `template.yaml` |

### Điểm khó thật sự — không nằm ở công nghệ client

**Chuyển từ "offline-first" sang "cần mạng".** Hiện mọi trang chạy được hoàn toàn offline. Khi số
dư và tiến độ nằm trên server, mất mạng là mất chức năng. Với nền tảng học cho trẻ em — có thể học
trên máy tính trường, mạng chập chờn — đây là đánh đổi cần cân nhắc kỹ.

Hướng xử lý: giữ `localStorage` làm **bộ nhớ đệm**, đọc từ nó trước để hiển thị ngay, gọi API nền
để đồng bộ. Ghi khi offline thì xếp hàng, gửi lại khi có mạng. Phức tạp hơn nhưng giữ được trải
nghiệm hiện tại.

### Khi nào mới nên đổi sang React/Vue

Không phải vì có backend. Chỉ nên đổi khi giao diện phức tạp tới mức tự quản lý DOM thành gánh
nặng — nhiều màn hình chia sẻ trạng thái, danh sách lồng nhau cập nhật liên tục. astroQ hiện chưa
tới ngưỡng đó. Đổi lúc này là **thêm bước build, thêm dependency, mất toàn bộ ưu thế tốc độ và SEO
đang có** (trang chủ 233 KB, wiki tĩnh thuần) mà không giải quyết vấn đề nào đang tồn tại.

---

## 13. Phụ lục — nếu chọn phương án B

Bỏ Firebase, Lambda tự lo xác thực. Cần thêm:

| Endpoint | Ghi chú |
|---|---|
| `POST /auth/register` | Băm mật khẩu **Argon2id** hoặc PBKDF2 ≥ 600k vòng lặp. Sinh token xác minh, gửi SES. |
| `GET /auth/verify?token=` | Token một lần, hết hạn sau 24h, xoá sau khi dùng |
| `POST /auth/login` | Trả JWT (15 phút) + refresh token (30 ngày, lưu DynamoDB để thu hồi được) |
| `POST /auth/refresh` | Đổi refresh token lấy JWT mới |
| `POST /auth/forgot` · `POST /auth/reset` | Token một lần qua SES |

Thêm vào DynamoDB:

| Thực thể | PK | SK |
|---|---|---|
| Tra cứu email → uid | `EMAIL#<email>` | `USER` |
| Token xác minh | `VERIFY#<token>` | `TOKEN` (kèm `ttl`) |
| Refresh token | `USER#<uid>` | `RT#<tokenId>` (kèm `ttl`) |

**Ba cái bẫy hay gặp:**

1. **Không tự nghĩ ra thuật toán băm.** Dùng `Konscious.Security.Cryptography.Argon2` hoặc
   `Rfc2898DeriveBytes` với số vòng lặp cao. SHA256 trần là sai.
2. **Chống dò mật khẩu.** Firebase làm sẵn. Tự làm thì phải đếm số lần sai theo email + IP trong
   DynamoDB và khoá tạm.
3. **So sánh token phải dùng hàm chống timing attack** (`CryptographicOperations.FixedTimeEquals`),
   không dùng `==`.

Đây chính là lý do khuyên chọn phương án A.
