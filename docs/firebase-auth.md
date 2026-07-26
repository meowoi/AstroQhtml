# Tích hợp Đăng ký / Đăng nhập bằng Firebase Authentication

Hướng dẫn viết riêng cho astroQ.org — bám đúng cấu trúc file hiện có
(`landing-app.html`, `js/ui-common.js`, `js/auth-flow.js`, `economy.js`).

---

## 0. Đọc trước khi bắt tay

Bốn điều nên biết trước, để không phải làm lại:

**a) Đây là dependency đầu tiên của dự án.** `CLAUDE.md` mục 6 ghi "giữ vanilla JS, không thêm
dependency". Firebase phá lệ đó. Đổi lại, đăng nhập *thật* bắt buộc phải có backend, và Firebase là
cách rẻ nhất để một site tĩnh trên GitHub Pages có backend mà không cần server. Nếu chấp nhận thì
nên cập nhật luôn `CLAUDE.md` để lần sau không ai xoá nhầm.

**b) Firebase Auth chỉ lo *danh tính*, không lo *tiến độ học*.**
Sau khi tích hợp, đăng nhập trên máy khác vẫn thấy hồ sơ trắng: số Purple Meteors, nhân vật đã chọn,
bài đã đọc đều đang nằm trong `localStorage` của từng máy. Muốn đồng bộ thật phải thêm Firestore —
xem [Bước 7](#bước-7-tuỳ-chọn-đồng-bộ-tiến-độ-bằng-firestore).

**c) API key của Firebase Web là công khai theo thiết kế.** Nó nằm lộ trong mã nguồn client và điều đó
bình thường — nó chỉ để định danh project, không phải mật khẩu. An toàn đến từ **Authorized domains**
và **Security Rules**, không phải từ việc giấu key. Đừng mất công đưa nó vào biến môi trường.

**d) astroQ.org là nền tảng cho trẻ em.** Thu thập email và mật khẩu của trẻ có ràng buộc pháp lý:
ở Việt Nam là Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân, nếu có người dùng ở Mỹ thì còn COPPA.
Thông lệ phổ biến là **dùng email của phụ huynh** và ghi rõ điều đó trên form đăng ký.
*(Đây là lưu ý kỹ thuật, không phải tư vấn pháp lý — nên hỏi luật sư trước khi mở đăng ký công khai.)*

---

## Bước 1 — Tạo project trên Firebase Console

1. Vào <https://console.firebase.google.com> → **Add project** → đặt tên (vd `astroq`).
   Google Analytics có thể tắt, không cần cho việc này.
2. Menu trái → **Build → Authentication** → **Get started**.
3. Tab **Sign-in method** → chọn **Email/Password** → bật **Enable** → **Save**.
   (Ô "Email link (passwordless)" bên dưới cứ để tắt.)
4. Vào **Project settings** (bánh răng góc trái) → cuộn xuống **Your apps** → bấm biểu tượng
   **`</>`** (Web) → đặt nickname → **Register app**.
   → Firebase hiện đoạn `const firebaseConfig = {...}`. **Copy giữ lại.**
5. Quay lại **Authentication → Settings → Authorized domains** → **Add domain** → nhập `astroq.org`.
   `localhost` đã có sẵn nên chạy thử ở máy vẫn được.

> **Đính chính:** với đăng nhập Email/Password thuần thì Authorized domains **không** chặn — danh sách này áp cho luồng OAuth (popup Google/Facebook) và cho link trong email hệ thống. Vẫn nên thêm `astroq.org` ngay: cần cho email đặt lại mật khẩu, và cho việc thêm đăng nhập Google sau này.

---

## Bước 2 — Tạo `js/firebase-auth.js`

File này là **ES module** (`type="module"`), khác với các file JS còn lại của dự án.
Dán config lấy ở Bước 1 vào đầu file.

```js
/* ============================================================
   firebase-auth.js — Đăng ký / Đăng nhập thật bằng Firebase Auth.
   ES MODULE: nạp bằng <script type="module">, chạy SAU mọi script cổ điển.
   Phụ thuộc: js/ui-common.js (AstroQ.setUser / getUser / clearUser / getLang).
   ============================================================ */
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.16.0/firebase-app.js";
import {
  getAuth, setPersistence, browserLocalPersistence,
  createUserWithEmailAndPassword, signInWithEmailAndPassword,
  signOut, onAuthStateChanged, updateProfile, sendPasswordResetEmail
} from "https://www.gstatic.com/firebasejs/12.16.0/firebase-auth.js";

/* ---- Dán nguyên khối config từ Firebase Console vào đây ---- */
const firebaseConfig = {
  apiKey:            "…",
  authDomain:        "astroq-xxxx.firebaseapp.com",
  projectId:         "astroq-xxxx",
  storageBucket:     "astroq-xxxx.appspot.com",
  messagingSenderId: "…",
  appId:             "…"
};

const app  = initializeApp(firebaseConfig);
const auth = getAuth(app);

/* Giữ phiên đăng nhập sau khi đóng trình duyệt (mặc định đã là local, khai báo cho rõ ràng). */
await setPersistence(auth, browserLocalPersistence);

/* ---------------- Thông báo lỗi song ngữ ----------------
   Firebase trả về mã lỗi tiếng Anh; ánh xạ sang câu người dùng đọc được.       */
const ERR = {
  vi: {
    "auth/email-already-in-use": "Email này đã có tài khoản rồi. Thử đăng nhập nhé!",
    "auth/invalid-email":        "Email chưa đúng định dạng.",
    "auth/weak-password":        "Mật khẩu quá ngắn — cần ít nhất 6 ký tự.",
    "auth/invalid-credential":   "Email hoặc mật khẩu không đúng.",
    "auth/user-not-found":       "Không tìm thấy tài khoản với email này.",
    "auth/wrong-password":       "Mật khẩu không đúng.",
    "auth/too-many-requests":    "Thử sai quá nhiều lần. Đợi vài phút rồi thử lại nhé.",
    "auth/network-request-failed":"Mất kết nối mạng. Kiểm tra lại đường truyền.",
    "auth/unauthorized-domain":  "Tên miền này chưa được cho phép trong Firebase Console.",
    _default:                    "Có lỗi xảy ra. Thử lại sau ít phút nhé."
  },
  en: {
    "auth/email-already-in-use": "That email already has an account. Try signing in!",
    "auth/invalid-email":        "That email address looks invalid.",
    "auth/weak-password":        "Password too short — use at least 6 characters.",
    "auth/invalid-credential":   "Wrong email or password.",
    "auth/user-not-found":       "No account found for that email.",
    "auth/wrong-password":       "Wrong password.",
    "auth/too-many-requests":    "Too many attempts. Please wait a few minutes.",
    "auth/network-request-failed":"Network error. Check your connection.",
    "auth/unauthorized-domain":  "This domain is not authorised in the Firebase Console.",
    _default:                    "Something went wrong. Please try again."
  }
};
function errMsg(code){
  const d = ERR[AstroQ.getLang()] || ERR.vi;
  return d[code] || d._default;
}

/* ---------------- Đồng bộ hồ sơ Firebase → localStorage ----------------
   Giữ nguyên khoá "astroq-user" để toàn bộ code hiện có (dashboard, select,
   quiz…) không phải sửa gì. Chỉ bổ sung uid.                                  */
function syncProfile(user, extra){
  const old = AstroQ.getUser() || {};
  AstroQ.setUser(Object.assign({}, old, {
    uid:   user.uid,
    email: user.email || old.email || "",
    name:  (extra && extra.name) || user.displayName || old.name || (user.email || "").split("@")[0]
  }, extra || {}));
}

/* ---------------- API công khai cho các trang ---------------- */
const AstroQAuth = {
  /** Đăng ký. Trả về { ok:true } hoặc { ok:false, message } */
  async register(name, email, password){
    try{
      const cred = await createUserWithEmailAndPassword(auth, email, password);
      if(name) await updateProfile(cred.user, { displayName: name });
      syncProfile(cred.user, { name });
      return { ok: true, user: cred.user };
    }catch(e){ return { ok: false, code: e.code, message: errMsg(e.code) }; }
  },

  /** Đăng nhập */
  async login(email, password){
    try{
      const cred = await signInWithEmailAndPassword(auth, email, password);
      syncProfile(cred.user);
      return { ok: true, user: cred.user };
    }catch(e){ return { ok: false, code: e.code, message: errMsg(e.code) }; }
  },

  /** Gửi email đặt lại mật khẩu */
  async resetPassword(email){
    try{ await sendPasswordResetEmail(auth, email); return { ok: true }; }
    catch(e){ return { ok: false, code: e.code, message: errMsg(e.code) }; }
  },

  /** Đăng xuất: xoá cả phiên Firebase lẫn hồ sơ trong máy */
  async logout(){
    try{ await signOut(auth); }catch(e){}
    AstroQ.clearUser();
  },

  /** Lắng nghe trạng thái đăng nhập. cb(user|null) */
  onChange(cb){ return onAuthStateChanged(auth, cb); },

  /** Promise: chờ Firebase xác định xong phiên hiện tại (chạy 1 lần) */
  ready: new Promise(resolve => {
    const off = onAuthStateChanged(auth, u => { off(); resolve(u); });
  })
};

window.AstroQAuth = AstroQAuth;
document.dispatchEvent(new CustomEvent("astroq-auth-ready"));
export default AstroQAuth;
```

> **Vì sao `updateProfile` gọi sau `createUser`?** Firebase không nhận `displayName` ngay lúc tạo
> tài khoản; phải cập nhật ở bước riêng.

---

## Bước 3 — Nối vào popup ở `landing-app.html`

### 3a. Bỏ hai handler giả

Trong khối `<script>` cuối `landing-app.html`, **xoá** hai đoạn `loginPane.addEventListener("submit", …)`
và `regPane.addEventListener("submit", …)`. Chúng đang bỏ qua mật khẩu hoàn toàn và chỉ ghi thẳng
vào localStorage — đó là đăng nhập giả.

Giữ nguyên mọi thứ khác: `open()`, `close()`, `showPane()`, `showToast()`, nút chuyển tab.

### 3b. Cho phép module gọi lại các hàm nội bộ

Ở cuối IIFE trong `landing-app.html`, thêm một dòng để module dùng lại được popup:

```js
  // Cho js/firebase-auth-ui.js dùng lại phần đóng popup + toast của trang
  window.AstroQAuthUI = { close: close, toast: showToast, t: t };
```

### 3c. Tạo `js/firebase-auth-ui.js`

Tách riêng phần gắn form ra khỏi `firebase-auth.js` để file kia thuần logic, dễ tái dùng:

```js
/* firebase-auth-ui.js — gắn Firebase Auth vào popup đăng nhập/đăng ký của landing-app.html */
import AstroQAuth from "./firebase-auth.js";

const UI = window.AstroQAuthUI || { close(){}, toast(m){ alert(m); }, t(k){ return k; } };
const $  = (id) => document.getElementById(id);

function busy(form, on){
  const btn = form.querySelector(".auth-submit");
  btn.disabled = on;
  btn.dataset.label = btn.dataset.label || btn.textContent;
  btn.textContent = on ? (AstroQ.getLang() === "en" ? "Please wait…" : "Đang xử lý…")
                       : btn.dataset.label;
}

/* ---------------- Đăng nhập ---------------- */
$("auth-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form  = e.currentTarget;
  const email = $("login-email").value.trim();
  const pass  = $("login-pass").value;
  if(!email || !pass) return;

  busy(form, true);
  const res = await AstroQAuth.login(email, pass);
  busy(form, false);

  if(!res.ok){ UI.toast(res.message); return; }

  UI.close();
  const u = AstroQ.getUser() || {};
  UI.toast(UI.t("auth_success") + " " + UI.t("auth_hello") + " " + (u.name || email) + "!");
  // Đã chọn nhân vật rồi thì vào thẳng khoang lái, chưa thì đi chọn
  setTimeout(() => { location.href = u.character ? "dashboard.html" : "select.html"; }, 900);
});

/* ---------------- Đăng ký ---------------- */
$("auth-register").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form  = e.currentTarget;
  const name  = $("reg-name").value.trim();
  const email = $("reg-email").value.trim();
  const pass  = $("reg-pass").value;
  if(!email || !pass) return;

  busy(form, true);
  const res = await AstroQAuth.register(name, email, pass);
  busy(form, false);

  if(!res.ok){ UI.toast(res.message); return; }

  UI.close();
  UI.toast(UI.t("auth_reg_success"));
  setTimeout(() => { location.href = "select.html"; }, 900);   // → chọn nhân vật
});
```

### 3d. Nạp module

Ngay trước `</body>` của `landing-app.html`, **sau** thẻ nạp `economy.js`:

```html
<script type="module" src="js/firebase-auth-ui.js"></script>
```

> **Vì sao đặt cuối và dùng `type="module"`?** Module luôn bị hoãn (defer) — nó chạy sau khi HTML
> đã parse xong và sau tất cả script cổ điển. Nhờ vậy `AstroQ`, `Economy` và `AstroQAuthUI` chắc chắn
> đã tồn tại, và `getElementById` chắc chắn tìm thấy form.

---

## Bước 4 — Đăng xuất ở `dashboard.html`

Tìm dòng xử lý nút Đăng xuất và đổi thành gọi Firebase:

```js
// Cũ:
if(logoutBtn) logoutBtn.addEventListener("click", function(){
  AstroQ.clearUser(); window.location.href="landing-app.html";
});

// Mới:
if(logoutBtn) logoutBtn.addEventListener("click", function(){
  var done = function(){ window.location.href = "landing-app.html"; };
  if(window.AstroQAuth) AstroQAuth.logout().then(done);   // xoá cả phiên Firebase
  else { AstroQ.clearUser(); done(); }                    // dự phòng nếu module chưa nạp
});
```

Và nạp module ở `dashboard.html` (trước `</body>`):

```html
<script type="module" src="js/firebase-auth.js"></script>
```

---

## Bước 5 — Sửa `js/auth-flow.js` để không mất `uid`

`startJourney()` hiện **ghi đè toàn bộ** hồ sơ, làm mất `uid` và `email` vừa lưu khi đăng ký:

```js
// Cũ — mất uid
var profile={ name:name, pilotName:name, /* … */ email:existing.email||"", purpleAsteroids:0 };

// Mới — giữ lại mọi trường cũ, chỉ ghi đè phần chọn nhân vật
var profile = Object.assign({}, existing, {
  name:name, pilotName:name,
  character:selected.id, selectedCharacter:selected.id,
  avatar:selected.ava, avatarZoom:selected.zoom||1,
  purpleAsteroids: existing.purpleAsteroids || 0
});
```

Đồng thời **bỏ dòng reset số dư** `localStorage.setItem(LS_AST, "0")` nếu không muốn người dùng
cũ đổi nhân vật bị mất sạch Purple Meteors.

---

## Bước 6 — (Tuỳ chọn) Chặn trang app khi chưa đăng nhập

Thêm vào các trang cần bảo vệ (`dashboard`, `quiz`, `learn`, `library`, `games`, `game-*`):

```html
<script type="module">
  import AstroQAuth from "./js/firebase-auth.js";
  const user = await AstroQAuth.ready;
  if(!user) location.replace("landing-app.html");
</script>
```

**Cân nhắc trước khi bật:** hiện tại mọi trang chạy được offline hoàn toàn. Bật chặn nghĩa là mất
mạng thì không vào được — với một nền tảng học cho trẻ em, đó có thể là đánh đổi không đáng.
Một phương án nhẹ hơn: vẫn cho vào, chỉ hiện banner "Đăng nhập để lưu tiến độ".

---

## Bước 7 — (Tuỳ chọn) Đồng bộ tiến độ bằng Firestore

Đây là bước làm cho đăng nhập *có ý nghĩa thật* — không có nó, đăng nhập máy khác vẫn là hồ sơ trắng.

1. Console → **Build → Firestore Database** → **Create database** → chọn **production mode**.
2. Tab **Rules** → dán:

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Mỗi người chỉ đọc/ghi được đúng hồ sơ của mình
    match /users/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }
  }
}
```

3. Trong code: sau khi đăng nhập thì `getDoc(doc(db,"users",uid))` để kéo tiến độ về localStorage;
   mỗi lần `Economy.addAsteroids()` thì `setDoc(..., { merge:true })` để đẩy lên.
   Điểm cần nghĩ kỹ: **xử lý xung đột** khi cùng một tài khoản chơi trên 2 máy — thường lấy giá trị
   lớn hơn cho số dư, và lấy mốc thời gian mới hơn cho phần còn lại.

Bước này đáng làm thành một việc riêng, không nên gộp vào lần tích hợp đầu.

---

## Bước 8 — Kiểm thử

Chạy `python -m http.server 5173` trong thư mục `AstroQhtml/` rồi mở `http://127.0.0.1:5173/landing-app.html`.
Mở **DevTools → Console** để thấy lỗi Firebase nếu có.

- [ ] Đăng ký email mới → Console Firebase (**Authentication → Users**) hiện tài khoản
- [ ] Đăng ký lại đúng email đó → hiện "Email này đã có tài khoản rồi"
- [ ] Mật khẩu 3 ký tự → hiện "Mật khẩu quá ngắn"
- [ ] Đăng nhập sai mật khẩu → hiện "Email hoặc mật khẩu không đúng"
- [ ] Đăng nhập đúng → vào `select.html` (hoặc `dashboard.html` nếu đã chọn nhân vật)
- [ ] Tải lại trang → vẫn đăng nhập (nhờ `browserLocalPersistence`)
- [ ] Bấm Đăng xuất ở dashboard → về landing, `localStorage["astroq-user"]` đã bị xoá
- [ ] Đổi ngôn ngữ sang EN rồi thử sai mật khẩu → thông báo lỗi ra tiếng Anh
- [ ] Đẩy lên `astroq.org` và thử lại (nếu quên Bước 1.5 sẽ dính `auth/unauthorized-domain`)

---

## Bảng mã lỗi hay gặp

| Mã Firebase | Nguyên nhân thật |
|---|---|
| `auth/invalid-credential` | Sai email **hoặc** sai mật khẩu. SDK mới gộp chung để chống dò email — đừng cố tách ra thông báo riêng, làm vậy là mở đường cho kẻ xấu dò xem email nào đã đăng ký. |
| `auth/unauthorized-domain` | Quên thêm `astroq.org` vào Authorized domains (Bước 1.5). |
| `auth/operation-not-allowed` | Quên bật Email/Password ở Sign-in method (Bước 1.3). |
| `auth/too-many-requests` | Firebase tự chặn tạm khi thử sai nhiều lần. Đợi vài phút. |
| `auth/network-request-failed` | Mất mạng, hoặc trình chặn quảng cáo chặn `googleapis.com`. |

---

## Ảnh hưởng tới hiệu năng

Firebase Auth qua CDN nặng khoảng **vài trăm KB** — nhiều hơn *toàn bộ* trang chủ hiện tại (233 KB).
Vì vậy **chỉ nạp ở trang thực sự cần**: `landing-app.html` và các trang app. **Tuyệt đối không nạp
ở `index.html`** (trang chủ waitlist) và `wiki/` — hai khu này đang được tối ưu cho SEO/AEO và tốc độ.
