# AstroqSV — Backend .NET 10 trên AWS Lambda

Kế hoạch triển khai backend cho astroQ.org: **AWS Lambda + .NET 10 + DynamoDB + SES**,
API Gateway đứng trước, client là site tĩnh hiện có.

Liên quan: [`firebase-auth.md`](firebase-auth.md) — phần xác thực đang chạy.

---

## 0. Tình trạng hiện tại — ĐÃ CHẠY THẬT *(cập nhật 27/07/2026)*

| Hạng mục | Trạng thái |
|---|---|
| Stack CloudFormation `astroqsv` | ✅ `ap-southeast-1` |
| API | ✅ `https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com` |
| Bảng DynamoDB `astroq-main` | ✅ PAY_PER_REQUEST, bật TTL + PITR |
| Lambda `AstroqSV` | ✅ `dotnet10`, arm64, 512 MB |
| SES gửi email kích hoạt | ✅ từ `no-reply@astroq.org` |
| Đăng ký 2 giai đoạn | ✅ **34/34 phép kiểm tự động đạt** |

Còn thiếu: `POST /auth/login`, `GET /me`, `POST /me/wallet` (đăng nhập hiện chạy
thẳng bằng Firebase Web SDK ở client, chưa cần qua Lambda).

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
   │ PK=PENDING#<email> │ ─────────────────▶ │ 2. import vào Firebase │
   │ SK=SIGNUP          │      (SES)         │    (emailVerified=true)│
   │ + pwdHash/pwdSalt  │                    │ 3. tạo PROFILE + WALLET│
   │ + tokenHash, ttl   │                    │ 4. xoá bản ghi chờ     │
   └────────────────────┘                    │ 5. redirect ?activated │
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
| Hồ sơ | `USER#<uid>` | `PROFILE` | `name`, `email`, `character`, `avatar`, `createdAt` |
| Ví | `USER#<uid>` | `WALLET` | `meteors`, `diamonds`, `updatedAt` |
| Lịch sử | `USER#<uid>` | `HIST#<ISO8601>` | `type`, `refId`, `delta`, `score` |
| Bài đã đọc | `USER#<uid>` | `READ#<lessonId>` | `readAt`, `rewarded` |
| Bài học | `LESSON#<id>` | `META` | `title`, `topic`, `level`, `body`, `reward` |

**Vì sao gộp một bảng:** lấy toàn bộ dữ liệu của một người chỉ cần **một** query
`PK = USER#<uid>` — nhanh và rẻ hơn nhiều so với gọi 4 bảng.

**Điểm phải nhớ:** `HIST#<ISO8601>` cho phép sắp xếp lịch sử theo thời gian mà không cần index phụ,
vì chuỗi ISO 8601 sắp xếp theo thứ tự từ điển trùng với thứ tự thời gian.

**Chế độ:** `PAY_PER_REQUEST` (on-demand). Lưu lượng của astroQ giai đoạn đầu rất thấp và không đều
— on-demand không phải đoán capacity và gần như miễn phí ở mức nhỏ.

**TTL:** bật trên thuộc tính `ttl` cho các bản ghi lịch sử cũ nếu muốn tự dọn sau N tháng.

---

## 5. Danh sách API

Tất cả (trừ `/health` và `/lessons`) yêu cầu header `Authorization: Bearer <Firebase ID token>`.

| Method | Đường dẫn | Việc |
|---|---|---|
| `GET` | `/health` | Kiểm tra sống — không cần token |
| `GET` | `/me` | Hồ sơ + ví + tiến độ, gộp trong một lần gọi |
| `PUT` | `/me` | Cập nhật tên, nhân vật đã chọn |
| `POST` | `/me/wallet` | Cộng/trừ meteors, diamonds — **server tự tính, không nhận số dư từ client** |
| `GET` | `/me/history` | Lịch sử hoạt động, phân trang bằng `cursor` |
| `POST` | `/me/history` | Ghi một sự kiện (làm quiz, đọc bài, chơi game) |
| `GET` | `/lessons` | Danh sách bài học — công khai, cache được |
| `GET` | `/lessons/{id}` | Chi tiết một bài |
| `POST` | `/me/lessons/{id}/complete` | Đánh dấu đã học xong + cộng thưởng |

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

Hiện `economy.js` đang cho client tự cộng số dư trong localStorage. Khi lên server phải đảo ngược
hoàn toàn hướng tin cậy này, nếu không thì backend chỉ là chỗ lưu điểm giả.

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

### `Endpoints/MeEndpoints.cs` — mẫu một nhóm endpoint

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
sam build                     # biên dịch .NET 10 cho arm64
sam deploy --guided           # lần đầu: chọn region ap-southeast-1 (Singapore, gần VN nhất)
                              # các lần sau chỉ cần: sam deploy
```

`sam deploy` **tự tạo bảng DynamoDB, Lambda, API Gateway, IAM role** theo `template.yaml`.
Không cần bấm gì trên AWS Console. Kết thúc sẽ in ra `ApiUrl`.

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
`js/index.js` (gửi form waitlist lên Formspree) và nó chạy tốt.

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
