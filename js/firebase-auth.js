/* ============================================================
   firebase-auth.js — Đăng ký / Đăng nhập cho astroQ.

   HAI NƠI GIỮ TÀI KHOẢN, HAI VAI TRÒ KHÁC NHAU:

     ĐĂNG KÝ  →  backend AstroqSV (AWS)      — js/api.js
        Lưu đăng ký vào DynamoDB rồi gửi email kích hoạt sống 10 phút.
        CHƯA có tài khoản Firebase nào được tạo ở bước này.
        Người dùng bấm link trong email → server mới tạo tài khoản Firebase
        (đã sẵn emailVerified=true) rồi chuyển hướng về landing-app.html?activated=1.

     ĐĂNG NHẬP → Firebase Authentication      — SDK tải động
        Firebase là nơi giữ danh tính chính thức, chỉ chứa tài khoản ĐÃ kích hoạt.

   Vì sao không để client tự gọi createUserWithEmailAndPassword: Firebase tạo tài
   khoản NGAY khi gọi, không có luồng "xác minh xong mới tạo" — làm vậy sẽ tích tụ
   tài khoản rác chưa xác thực, và không đặt được hạn 10 phút cho link.

   ES MODULE: nạp bằng <script type="module">, nên luôn chạy SAU mọi script cổ điển
   → AstroQ (js/ui-common.js) và Economy chắc chắn đã tồn tại.

   Chưa điền js/firebase-config.js → mọi hàm trả về { ok:false, notConfigured:true }
   để phía giao diện tự lùi về chế độ demo cũ. Trang không bao giờ vỡ.
   ============================================================ */
import { firebaseConfig, isConfigured } from "./firebase-config.js";
import { apiPost, apiGet, apiGetAuth, apiPutAuth, apiPostAuth, isApiConfigured } from "./api.js";

/* SDK Firebase TỰ HOST, không còn gstatic.com (07/08/2026). Tải lại/nâng cấp
   bằng `python scratchpad/vendor_deps.py` — đừng tải tay.

   ⚠️⚠️ TẢI HAI FILE VỀ LÀ CHƯA ĐỦ, VÀ ĐÓ LÀ CÁI BẪY IM LẶNG NHẤT Ở ĐÂY:
        `firebase-auth.js` nhúng URL **tuyệt đối** tới gstatic ngay trong lệnh
        import của chính nó. Chỉ đổi hằng này thôi thì bản local vẫn tự đi kéo
        `firebase-app.js` từ mạng ngoài — phụ thuộc **chưa hề bị gỡ**, mà đọc mã
        của dự án thì không thấy gì sai. Script vendor viết lại đúng URL đó
        thành `./firebase-app.js` và có phép kiểm canh.
        (Ngược lại, 2 chuỗi gstatic còn sót trong `firebase-app.js` là TÊN
        COMPONENT + nhãn logger của sổ đăng ký nội bộ Firebase — **cố ý không
        đụng**; sửa nội tạng thư viện mà không có lý do là thứ không ai rà lại
        được ở lần nâng cấp sau.)

   ⚠️ Đường dẫn TƯƠNG ĐỐI TỪ FILE NÀY, không phải từ trang. `import()` trong
      module giải đường dẫn theo URL của **module**, nên `../vendor/…` là đúng
      dù trang gọi nó (`landing-app.html`) nằm ở gốc. Viết `vendor/…` là 404.

   Vẫn giữ import ĐỘNG: chưa điền config thì không tải byte nào (64 KB gzip). */
const SDK = "../vendor/firebase/12.16.0";

let auth = null;
let fb = null;                 // các hàm của firebase-auth SDK, nạp động
let pendingName = "";          // tên nhập lúc đăng ký, ghi vào hồ sơ sau khi xác minh xong

/* Chỉ tải SDK khi đã có config — tránh kéo 64 KB gzip vô ích.
   Mất mạng / file vendor thiếu → trả null chứ KHÔNG ném lỗi: mọi hàm bên dưới
   đều bắt đầu bằng `if(!(await boot()))`, ném ra ở đây là làm vỡ cả chuỗi
   promise của phía gọi (đã gặp: màn giới thiệu không hiện khi mất mạng). */
async function boot(){
  if(!isConfigured) return null;
  if(auth) return auth;
  try{
    const [{ initializeApp }, mod] = await Promise.all([
      import(`${SDK}/firebase-app.js`),
      import(`${SDK}/firebase-auth.js`)
    ]);
    fb = mod;
    auth = mod.getAuth(initializeApp(firebaseConfig));
    // Giữ phiên sau khi đóng trình duyệt (mặc định đã vậy, khai báo cho rõ ý)
    try{ await mod.setPersistence(auth, mod.browserLocalPersistence); }catch(e){}
    return auth;
  }catch(e){
    console.warn("[AstroQ] Không tải được SDK Firebase:", e && e.message);
    return null;
  }
}

/* ---------------- Thông báo lỗi song ngữ ----------------
   Firebase trả mã tiếng Anh; ánh xạ sang câu người dùng đọc được.            */
const ERR = {
  vi: {
    "auth/email-already-in-use":  "Email này đã có tài khoản rồi. Thử đăng nhập nhé!",
    "auth/invalid-email":         "Email chưa đúng định dạng.",
    "auth/missing-password":      "Bạn chưa nhập mật khẩu.",
    "auth/weak-password":         "Mật khẩu quá ngắn — cần ít nhất 6 ký tự.",
    "auth/invalid-credential":    "Email hoặc mật khẩu không đúng.",
    "auth/user-not-found":        "Không tìm thấy tài khoản với email này.",
    "auth/wrong-password":        "Mật khẩu không đúng.",
    "auth/user-disabled":         "Tài khoản này đã bị khoá.",
    "auth/too-many-requests":     "Thử sai quá nhiều lần. Đợi vài phút rồi thử lại nhé.",
    "auth/network-request-failed":"Mất kết nối mạng. Kiểm tra lại đường truyền.",
    "auth/unauthorized-domain":   "Tên miền này chưa được cho phép trong Firebase Console.",
    "auth/operation-not-allowed": "Chưa bật đăng nhập bằng Email/Password trong Firebase Console.",
    "auth/requires-recent-login":  "Phiên đã cũ. Đăng nhập lại rồi thử tiếp nhé.",
    // Mã do backend AstroqSV trả về (không có tiền tố "auth/")
    "name-too-long":              "Tên hơi dài — dùng tối đa 60 ký tự nhé.",
    "no-pending":                 "Không có đăng ký nào đang chờ với email này. Đăng ký lại nhé.",
    "net":                        "Không kết nối được máy chủ. Kiểm tra mạng rồi thử lại nhé.",
    _default:                     "Có lỗi xảy ra. Thử lại sau ít phút nhé."
  },
  en: {
    "auth/email-already-in-use":  "That email already has an account. Try signing in!",
    "auth/invalid-email":         "That email address looks invalid.",
    "auth/missing-password":      "Please enter your password.",
    "auth/weak-password":         "Password too short — use at least 6 characters.",
    "auth/invalid-credential":    "Wrong email or password.",
    "auth/user-not-found":        "No account found for that email.",
    "auth/wrong-password":        "Wrong password.",
    "auth/user-disabled":         "This account has been disabled.",
    "auth/too-many-requests":     "Too many attempts. Please wait a few minutes.",
    "auth/network-request-failed":"Network error. Check your connection.",
    "auth/unauthorized-domain":   "This domain is not authorised in the Firebase Console.",
    "auth/operation-not-allowed": "Email/Password sign-in is not enabled in the Firebase Console.",
    "auth/requires-recent-login":  "Session too old. Please sign in again.",
    // Codes returned by the AstroqSV backend (no "auth/" prefix)
    "name-too-long":              "That name is a bit long — 60 characters max.",
    "no-pending":                 "No pending sign-up for that email. Please register again.",
    "net":                        "Can't reach the server. Check your connection and try again.",
    _default:                     "Something went wrong. Please try again."
  }
};
function errMsg(code){
  const d = ERR[(window.AstroQ && AstroQ.getLang()) || "vi"] || ERR.vi;
  // Backend dùng mã trần ("invalid-email"), Firebase dùng "auth/invalid-email".
  // Thử cả hai để một bảng lo được cả hai nguồn lỗi.
  return d[code] || d["auth/" + code] || d._default;
}
/* Hạn chờ ký xuất khỏi Firebase. 2,5 giây — cùng mốc `waitAuth` của js/progress.js;
   quá mốc thì vẫn cho trẻ đi, phần ký xuất để lượt mở trang sau lo. */
const SIGNOUT_MS = 2500;
/* Hạn chờ KÉO HỒ SƠ về ngay sau khi đăng nhập. Rộng hơn `SIGNOUT_MS` vì đây là một
   vòng HTTP thật ra tận API Gateway, không phải một lời gọi trong SDK; và nút đăng
   nhập đang hiện "Đang xử lý…" nên chờ ở đây là chờ CÓ NÓI RA. Quá mốc thì vẫn cho
   vào — xem `hydrateProfile`. */
const HYDRATE_MS = 5000;
/* Dấu "còn nợ một lần ký xuất". Đặt ở localStorage chứ không sessionStorage: trẻ
   đóng hẳn trình duyệt rồi mở lại thì món nợ đó vẫn phải trả. */
const LS_SIGNOUT = "astroq-signout-pending";

const fail = (e) => ({ ok: false, code: e && e.code, message: errMsg(e && e.code) });
const NOT_CONFIGURED = { ok: false, notConfigured: true, message: "" };

/* ---------------- Cờ admin: ĐỌC MỘT LẦN, ĐÓNG DẤU VÀO HỒ SƠ MÁY ----------------
   Claim `admin` nằm trong ID token do Google ký. Đọc nó cần một `User` của SDK, tức
   cần SDK đã nạp — mà `select.html` cố ý KHÔNG nạp SDK, và `dashboard.html` thì nạp
   nhưng gọi thêm một vòng bất đồng bộ chỉ để ẩn/hiện một cái link là tốn vô ích.

   Nên: đọc claim ĐÚNG MỘT LẦN lúc đăng nhập (lúc đó đã có `cred.user` trong tay,
   không phải chờ `onAuthStateChanged`), rồi ghi `admin:true|false` vào hồ sơ trong
   máy. Mọi trang sau đó chỉ cần `AstroQ.getUser().admin` — không lời gọi nào.

   ⚠️ ĐÂY LÀ GỢI Ý GIAO DIỆN, KHÔNG PHẢI QUYỀN. Ai cũng sửa được localStorage bằng
      DevTools và làm cái link hiện ra — bấm vào thì server trả 403, vì cổng thật là
      allowlist `ADMIN_EMAILS` (Services/AdminAuth.cs). Cùng đúng khuôn `route-gate.js`
      đã ghi: "cổng là lời dẫn đường, không phải hàng rào an ninh".
   ⚠️ Không bao giờ dùng cờ này để quyết ẩn/hiện DỮ LIỆU — chỉ để chọn đường đi. */
async function readAdminClaim(user){
  try{
    const r = await user.getIdTokenResult();
    return !!(r && r.claims && r.claims.admin === true);
  }catch(e){ return false; }
}

/* ---------------- Đồng bộ hồ sơ Firebase → localStorage ----------------
   Giữ nguyên khoá "astroq-user" để dashboard / select / quiz không phải sửa gì.
   Object.assign để KHÔNG xoá mất character, avatar… đã có sẵn.               */
function syncProfile(user, extra){
  const old = (window.AstroQ && AstroQ.getUser()) || {};
  AstroQ.setUser(Object.assign({}, old, {
    uid:   user.uid,
    email: user.email || old.email || "",
    name:  (extra && extra.name) || user.displayName || old.name ||
           (user.email || "").split("@")[0]
  }, extra || {}));
}

/* ---------------- KÉO HỒ SƠ TỪ SERVER VỀ CACHE, NGAY LÚC ĐĂNG NHẬP ----------------

   ⚠️⚠️ LỖI THẬT, SỬA 22/08/2026 — *"đã đăng nhập nhiều lần rồi mà đăng nhập lại vẫn
      phải chọn nhân vật"*. Chuỗi vỡ gồm hai mắt, mỗi mắt một mình đã đủ gây lỗi:
        ① `logout()` xoá SẠCH mọi khoá `astroq-*` (cố ý — máy dùng chung trong nhà /
           phòng máy trường học, xem `clearAccountData` ở js/ui-common.js), mà
           `syncProfile()` ngay trên chỉ ghi lại uid · email · name · admin. Nên
           `astroq-user.character` LUÔN rỗng sau khi đăng nhập.
        ② `go()` ở js/firebase-auth-ui.js và biến `authed` ở landing-app.html đọc
           ĐÚNG trường đó để chọn `dashboard.html` hay `select.html`.
      ⇒ mọi lượt đăng nhập đều bị đưa về màn cấp thẻ ID.

   ⚠️ PHẢI `await` BÊN TRONG `login()`, KHÔNG bỏ chạy nền: người gọi chuyển trang ngay
      sau khi `login()` trả về, nên một lời gọi nền sẽ bị `unload` cắt giữa đường và
      lỗi trên quay lại y nguyên.
   ⚠️ CÓ HẠN CHỜ, VÀ HẾT HẠN THÌ VẪN CHO VÀO. Mạng chậm thì cùng lắm trẻ đi qua màn
      chọn nhân vật một lượt (chọn lại đúng con cũ là xong) — chứ không đứng ngoài cửa
      vì một lời gọi chỉ dùng để CHỌN TRANG. Cùng khuôn fail-open của `SIGNOUT_MS`.
   ⚠️ KHÁC hẳn ca `readAdminClaim` mà chú thích trên cảnh báo: ở đây
      `signInWithEmailAndPassword` VỪA trả về nên đã có phiên thật, `idToken()` không
      có ca chờ mãi không resolve.
   ⚠️ KHÔNG ghi `avatarZoom`: mức zoom là luật của js/characters.js (`zoomOf` tự tra
      theo `character`), server không lưu nó. Ghi một giá trị đoán ở đây là để hai chỗ
      cùng giữ một luật.
   ⚠️ CHỈ GHI TRƯỜNG SERVER CÓ. Hồ sơ server rỗng (trẻ chọn nhân vật trước khi có cầu
      nối này) thì đừng ghi "" đè lên — cứ để `go()` đưa về `select.html`, rồi
      `AstroQChars.sync()` ở dashboard đẩy lên cho lượt sau. */
async function hydrateProfile(auth){
  try{
    const r = await Promise.race([
      auth.getProfile(),
      new Promise(res => setTimeout(() => res({ ok:false, reason:"timeout" }), HYDRATE_MS))
    ]);
    if(!r || !r.ok) return false;
    const p = (r.data && r.data.profile) || {};
    const old = (window.AstroQ && AstroQ.getUser()) || {};
    const next = Object.assign({}, old);
    if(p.name)      { next.name = p.name; next.pilotName = p.name; }
    if(p.character) { next.character = p.character; next.selectedCharacter = p.character; }
    if(p.avatar)      next.avatar = p.avatar;
    if(p.depth)       next.depth  = p.depth;     // js/depth.js đọc đúng trường này
    if(window.AstroQ && AstroQ.setUser) AstroQ.setUser(next);
    /* ⚠️ CỜ ONBOARDING PHẢI VỀ CACHE, và đây KHÔNG phải tối ưu.
       `logout()` xoá cả `astroq-map01-seen`, mà `select.html` CỐ Ý không nạp SDK
       nên nó không hỏi được cờ đó. Thiếu dòng này thì một trẻ CŨ bị buộc qua màn
       chọn lại nhân vật sẽ bị `startJourney()` ném vào `explorer.html?onboard=1`
       — chạy lại cả màn Comet dẫn đường dù đã xong nhiệm vụ từ lâu.
       Cũng đỡ cho `mapFirst()` ở dashboard: nó đọc cache TRƯỚC nên khỏi phải chờ
       `getOnboarding()` ở mọi lượt đăng nhập.
       ⚠️ CHỈ ghi khi server nói `true` — ghi "chưa xem" đè lên là xoá dấu của một
          trẻ đã xem, tức bắt nó xem lại. Server cũ không trả trường này thì
          `undefined !== true` nên không đụng gì. */
    try{ if(p.map01Seen === true) localStorage.setItem("astroq-map01-seen", "1"); }catch(e){}
    return !!p.character;
  }catch(e){ return false; }
}

/* ============================ API công khai ============================ */
const AstroQAuth = {
  isConfigured,

  /** Có backend AstroqSV hay không — giao diện dùng để chọn lời nhắc phù hợp. */
  hasBackend: isApiConfigured,

  /** Đăng ký qua backend AstroqSV. KHÔNG tạo tài khoản Firebase ở bước này —
      chỉ ghi nhận vào DynamoDB và gửi email kích hoạt sống `expiresInMinutes` phút.
      Tài khoản Firebase chỉ ra đời khi người dùng bấm link trong email.
      → { ok:true, needVerify:true, email, expiresInMinutes } | { ok:false, message } */
  async register(name, email, password){
    if(!isApiConfigured) return NOT_CONFIGURED;
    pendingName = name || "";

    const src = (typeof window !== "undefined" && window.AstroQUtm) ? window.AstroQUtm.get() : "";
    const r = await apiPost("/auth/register", { name, email, password, src });
    if(r.netError)       return { ok: false, code: "net", message: errMsg("net") };
    if(r.notConfigured)  return NOT_CONFIGURED;
    if(!r.ok)            return { ok: false, code: r.data.code, message: errMsg(r.data.code) };

    return {
      ok: true, needVerify: true,
      email: r.data.email || email,
      expiresInMinutes: r.data.expiresInMinutes || 10,
      // Email gửi hỏng thì vẫn trả ok (bản ghi chờ đã lưu) nhưng báo để mời bấm "Gửi lại".
      mailSent: r.data.mailSent !== false,
      /* Email này đã có một đăng ký đang chờ, và mật khẩu vừa gõ KHÁC mật khẩu của lượt
         đầu nên server BỎ QUA nó (chốt chặn chiếm quyền đăng ký chưa kích hoạt — xem
         AuthEndpoints). Giao diện phải nói ra: người dùng kích hoạt xong rồi đăng nhập
         bằng mật khẩu vừa gõ sẽ không vào được, mà không có gì giải thích vì sao.
         ⚠️ `=== true`, không phải truthy: server cũ chưa có trường này thì `undefined`
            → false, và màn hình giữ nguyên như trước. */
      passwordKept: r.data.passwordKept === true
    };
  },

  /** Đăng nhập. Email chưa xác minh → KHÔNG cho vào, trả needVerify.
      → { ok:true } | { ok:false, needVerify:true, email } | { ok:false, message } */
  async login(email, password){
    if(!(await boot())) return NOT_CONFIGURED;
    try{
      const cred = await fb.signInWithEmailAndPassword(auth, email, password);
      await fb.reload(cred.user);                    // lấy trạng thái emailVerified mới nhất
      if(!cred.user.emailVerified){
        // Giữ nguyên phiên (không signOut) để còn gửi lại được email xác minh.
        // Không ghi hồ sơ → vẫn không vào được app.
        return { ok: false, needVerify: true, email: cred.user.email };
      }
      /* Đóng dấu cờ admin NGAY ĐÂY — chỗ duy nhất trong dự án đọc claim. Đọc từ
         `cred.user` (đã có trong tay) nên không phải chờ `onAuthStateChanged`, tức
         không có nguy cơ treo đường đăng nhập. Lý do đầy đủ ở `readAdminClaim`.
         ⚠️ Ghi cả khi FALSE, không phải chỉ khi true: tài khoản bị rút quyền admin mà
            hồ sơ cũ trong máy còn `admin:true` thì cái link vẫn hiện mãi. */
      syncProfile(cred.user, { admin: await readAdminClaim(cred.user) });
      /* Rồi kéo hồ sơ (nhân vật · tên · bậc) về cache TRƯỚC khi trả lời, vì người
         gọi dùng cache đó để chọn trang đích. Lý do đầy đủ ở `hydrateProfile`. */
      await hydrateProfile(this);
      return { ok: true, user: cred.user };
    }catch(e){ return fail(e); }
  },

  /** Gửi lại link kích hoạt. Cần `email` vì lúc này CHƯA có phiên Firebase nào —
      tài khoản còn chưa tồn tại, chỉ có bản ghi chờ trong DynamoDB.
      Token cũ mất hiệu lực ngay khi token mới được cấp. */
  async resendVerification(email){
    if(!isApiConfigured) return NOT_CONFIGURED;
    if(!email) return { ok: false, message: errMsg("invalid-email") };

    const r = await apiPost("/auth/resend", { email });
    if(r.netError)      return { ok: false, code: "net", message: errMsg("net") };
    if(r.notConfigured) return NOT_CONFIGURED;
    if(!r.ok)           return { ok: false, code: r.data.code, message: errMsg(r.data.code) };
    return { ok: true, expiresInMinutes: r.data.expiresInMinutes || 10 };
  },

  /** Tên người dùng nhập ở form đăng ký, giữ trong bộ nhớ để điền sẵn sau khi kích hoạt.
      Mất khi tải lại trang — không sao, `displayName` trên Firebase mới là nguồn thật. */
  takePendingName(){
    const n = pendingName; pendingName = ""; return n;
  },

  /** Gửi email đặt lại mật khẩu. */
  async resetPassword(email){
    if(!(await boot())) return NOT_CONFIGURED;
    try{ await fb.sendPasswordResetEmail(auth, email); return { ok: true }; }
    catch(e){ return fail(e); }
  },

  /** Đăng xuất: xoá dấu vết trong máy TRƯỚC, rồi mới cố ký xuất khỏi Firebase.
   *
   * ⚠️⚠️ THỨ TỰ NÀY LÀ CẢ BẢN SỬA. Bản cũ là `await boot()` rồi `await signOut()`,
   *    tức cả đường đăng xuất treo trên MỘT lần `import()` qua mạng. Đo được
   *    20/08/2026 trên bản thật: SDK bị chặn hẳn thì `import()` lỗi ngay → bắt
   *    được → vẫn điều hướng; nhưng SDK tải CHẬM thì `await boot()` TREO, hàm này
   *    không bao giờ resolve, `.then(done, done)` ở dashboard không bao giờ chạy →
   *    **bấm Đăng xuất mà không có gì xảy ra, không một lời nào**. Đúng triệu
   *    chứng chủ dự án báo. Nay hồ sơ được xoá ĐỒNG BỘ nên trẻ luôn đăng xuất
   *    được khỏi app, kể cả khi Firebase không với tới.
   * ⚠️ HẠN CHỜ nằm TRONG hàm này, không ở phía gọi: mọi người gọi đều cần cùng
   *    một bảo đảm, và hai chỗ giữ một hạn chờ thì sớm muộn lệch nhau.
   * ⚠️ Ký xuất chưa xong thì ĐÓNG DẤU `astroq-signout-pending` và thử lại ở lượt
   *    mở trang sau (xem khối cuối file). Bỏ qua nó là phiên Firebase còn sống:
   *    `idToken()` vẫn trả token của trẻ CŨ, nên một trang như `profile.html` sẽ
   *    hỏi server rồi hiện dữ liệu của đứa trẻ TRƯỚC cho đứa SAU.
   * → { ok:true, signedOut:boolean, cleared:number }
   */
  async logout(){
    var cleared = 0;
    if(window.AstroQ){
      cleared = AstroQ.clearAccountData ? AstroQ.clearAccountData() : 0;
      AstroQ.clearUser();   /* lưới an toàn: bản ui-common cũ chưa có hàm trên */
    }
    let signedOut = false;
    try{
      signedOut = await Promise.race([
        (async () => { if(await boot()){ await fb.signOut(auth); return true; }
                       return false; })(),
        new Promise(r => setTimeout(() => r(false), SIGNOUT_MS))
      ]);
    }catch(e){}
    try{
      if(signedOut) localStorage.removeItem(LS_SIGNOUT);
      else          localStorage.setItem(LS_SIGNOUT, "1");
    }catch(e){}
    return { ok:true, signedOut: signedOut === true, cleared: cleared };
  },

  /** Người dùng đang đăng nhập (null nếu chưa). Chờ Firebase khôi phục phiên xong. */
  async currentUser(){
    if(!(await boot())) return null;
    return new Promise(resolve => {
      const off = fb.onAuthStateChanged(auth, u => { off(); resolve(u); });
    });
  },

  /** Theo dõi thay đổi trạng thái đăng nhập. cb(user|null) → hàm huỷ đăng ký. */
  async onChange(cb){
    if(!(await boot())){ cb(null); return () => {}; }
    return fb.onAuthStateChanged(auth, cb);
  },

  /** ID token của phiên hiện tại (null nếu chưa đăng nhập / chưa cấu hình).
      SDK tự làm mới khi token gần hết hạn, nên gọi lại mỗi lần cần thay vì cache. */
  async idToken(){
    try{
      const u = await this.currentUser();
      if(!u) return null;
      return await u.getIdToken();
    }catch(e){ return null; }
  },

  /* ---------------- Onboarding (màn Comet dẫn tham quan tàu Luna) ----------------
     Cờ nằm trong DynamoDB chứ không phải localStorage: trẻ hay đổi máy/trình duyệt,
     mà màn giới thiệu chỉ nên chạy ĐÚNG MỘT LẦN cho mỗi tài khoản.
     Chưa đăng nhập / mất mạng / chưa cấu hình → trả { ok:false } và phía gọi tự lùi
     về bộ nhớ máy (xem js/onboard-tour.js). Trang không bao giờ vỡ vì việc này.   */

  /** → { ok:true, tourSeen } | { ok:false, reason:"auth"|"net"|"notConfigured"|"http" } */
  async getOnboarding(){
    if(!isApiConfigured) return { ok:false, reason:"notConfigured" };
    const token = await this.idToken();
    if(!token) return { ok:false, reason:"auth" };

    const r = await apiGetAuth("/me/onboarding", token);
    if(r.netError)      return { ok:false, reason:"net" };
    if(r.notConfigured) return { ok:false, reason:"notConfigured" };
    if(!r.ok)           return { ok:false, reason:"http", status:r.status };
    /* ⚠️ PHẢI TRẢ VỀ **ĐỦ BỐN CỜ**. Lớp bọc này từng bỏ rơi `earth1Greeted`, và đó là
       một lỗi THẬT chạy im lặng: `earthDoneGuide()` ở `dashboard.html` đọc
       `o.earth1Greeted` ra `undefined` → điều kiện "đã chào rồi thì thôi" không bao giờ
       đúng → **Comet chúc mừng lại MỖI LẦN trẻ mở dashboard**, kể cả hai tuần sau. Cờ
       vẫn được GHI lên server đầy đủ, chỉ là không ai ĐỌC lại.
       Bộ `smoke_earth_done.py` không bắt được vì nó **giả lập chính `AstroQAuth`** —
       bản giả trả cờ đầy đủ nên nó đo một lớp không phải lớp đang chạy thật.
       `check_pages.py` mục [16] nay đối chiếu danh sách cờ ở đây với `OnboardingDto`
       của server, để cờ thứ năm không lặp lại chuyện này. */
    return {
      ok:true,
      tourSeen:        r.data.tourSeen === true,
      tourSeenAt:      r.data.tourSeenAt || null,
      // Màn mở đầu Nhiệm Vụ 01 "Hành Tinh Xanh" — cờ ĐỘC LẬP với tourSeen
      intro01Seen:     r.data.intro01Seen === true,
      intro01SeenAt:   r.data.intro01SeenAt || null,
      // Comet đã chúc mừng xong chuỗi Trái Đất chưa
      earth1Greeted:   r.data.earth1Greeted === true,
      earth1GreetedAt: r.data.earth1GreetedAt || null,
      // Đã đi qua màn Comet dẫn đường ở Bản Đồ Thiên Hà chưa (docs/decisions/003)
      map01Seen:       r.data.map01Seen === true,
      map01SeenAt:     r.data.map01SeenAt || null
    };
  },

  /**
   * Ghi cờ đã xem một màn giới thiệu.
   *
   *   setOnboarding(true)                  → tourSeen = true   (cách gọi cũ, giữ nguyên)
   *   setOnboarding(false)                 → tourSeen = false  (để xem lại khi test)
   *   setOnboarding({ map01Seen:true })    → CHỈ ghi cờ đó, KHÔNG đụng tourSeen
   *
   * Nhận cả boolean lẫn object vì `js/onboard-tour.js` gọi kiểu cũ, còn `dashboard.html`
   * (cờ `map01Seen`, `earth1Greeted`) gọi kiểu mới — đổi hết sang object thì phải sửa
   * 2 chỗ ở tour, mà cách gọi cũ vẫn đúng nghĩa "đã xem tour xong".
   * *(Người gọi kiểu mới đầu tiên là `js/mission-intro.js`, đã xoá 01/08/2026.)*
   */
  async setOnboarding(patch){
    if(!isApiConfigured) return { ok:false, reason:"notConfigured" };
    const token = await this.idToken();
    if(!token) return { ok:false, reason:"auth" };

    const body = (patch !== null && typeof patch === "object")
      ? patch
      : { tourSeen: patch !== false };

    const r = await apiPutAuth("/me/onboarding", body, token);
    if(r.netError)      return { ok:false, reason:"net" };
    if(r.notConfigured) return { ok:false, reason:"notConfigured" };
    if(!r.ok)           return { ok:false, reason:"http", status:r.status, code:r.data.code };
    // ⚠️ Trả về ĐỦ BỐN CỜ, cùng lý do đã ghi ở `getOnboarding` ngay trên.
    return {
      ok:true,
      tourSeen:      r.data.tourSeen === true,
      intro01Seen:   r.data.intro01Seen === true,
      earth1Greeted: r.data.earth1Greeted === true,
      map01Seen:     r.data.map01Seen === true
    };
  },

  /* ---------------- Hồ sơ Phi Hành Gia + Kho Thành Tích ----------------
     Ba hàm dưới đây là lớp mỏng quanh /me/*: lấy token, gọi, chuẩn hoá kết quả
     về đúng MỘT hình dạng { ok, ... } cho phía giao diện. Không hàm nào ném lỗi.
     Luật chơi (XP, cấp độ, điều kiện huy hiệu) nằm HẾT ở server — xem
     js/progress.js để biết cách phân công.                                    */

  /** Hồ sơ + ví + cấp độ + tiến độ, một lần gọi. → { ok:true, data } */
  async getProfile(){
    const r = await this._authed(t => apiGetAuth("/me/profile", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Đổi tên / nhân vật (trang phục). patch = { name?, character?, avatar? } */
  async updateProfile(patch){
    const r = await this._authed(t => apiPutAuth("/me/profile", patch || {}, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /* ---------------- Cửa hàng trang trí (buồng lái của con) ----------------
     ⚠️ GIÁ do server trả trong `getShop()`. Client KHÔNG bao giờ gửi số tiền lên —
        gửi được thì ai cũng mua 0 đồng. Xem AstroqSV/Services/Cosmetics.cs. */

  /** { items[{id,kind,price}], owned[], equipped{}, ship, wallet } */
  async getShop(){
    const r = await this._authed(t => apiGetAuth("/me/shop", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Mua một món. `opId` sinh MỘT LẦN cho mỗi lượt mua để gửi lại không trừ hai lần. */
  async buyCosmetic(itemId, opId){
    const r = await this._authed(t => apiPostAuth("/me/shop/buy", { itemId, opId }, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Đeo một món đã có (hoặc món mặc định). Server kiểm quyền đeo, không tin client. */
  async equipCosmetic(itemId){
    const r = await this._authed(t => apiPutAuth("/me/shop/equip", { itemId }, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Kho thành tích: { summary, badges[] } + cấp độ + tiến độ. */
  async getAchievements(){
    const r = await this._authed(t => apiGetAuth("/me/achievements", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Báo MỘT việc đã làm. Server tự quyết XP + huy hiệu + tiền. Xem js/progress.js. */
  async postProgress(ev){
    const r = await this._authed(t => apiPostAuth("/me/progress", ev, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Kho Mẫu Vật: { summary, desk, specimens[] } + ví. Trạng thái mở khoá do
      server SUY RA từ bộ đếm tiến độ — không có route "thu thập mẫu vật". */
  async getSpecimens(){
    const r = await this._authed(t => apiGetAuth("/me/specimens", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Treo mẫu vật lên móc ở vách khoang lái. `items` = mảng `{hook, id}`, tối đa 3.
      Gửi mẫu chưa mở khoá / trùng / móc lạ / móc đã có mẫu khác / quá 3
      → { ok:false, code:"bad-specimen", rejected }.
      ⚠️ Gửi nguyên object chứ không rút ra mảng id: móc là thứ TRẺ chọn, rút mất
         thì server tự xếp lại từ đầu và mọi mẫu vật nhảy chỗ sau mỗi lần lưu. */
  async setSpecimenDesk(items){
    const r = await this._authed(t =>
      apiPutAuth("/me/specimens/desk", { desk: Array.isArray(items) ? items : [] }, t));
    if(r.ok) return { ok:true, data:r.data };
    return Object.assign({}, r, { rejected: r.data && r.data.rejected });
  },

  /** Báo xong một bước nhiệm vụ. body = { mission, step, opId }.
      ⚠️ KHÔNG gửi số thưởng — server tra Services/Missions.cs. */
  async missionStep(body){
    const r = await this._authed(t => apiPostAuth("/me/missions/step", body || {}, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Trạng thái nhiệm vụ (bước đã xong, mẫu dữ liệu Codex). */
  async getMissions(){
    const r = await this._authed(t => apiGetAuth("/me/missions", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Việc hôm nay + chuỗi ngày → { ok:true, data:{ daily, dailyPaid, wallet } }.
      ⚠️ KHÔNG có route "nhận thưởng": thưởng được cộng ngay lúc việc xong, nên lời gọi
         này chỉ ĐỌC — trừ một việc, nó **tự cấp bù** khi có việc đã xong mà lượt cộng
         ví trước đó hỏng giữa đường (`dailyPaid > 0`). Xem Services/Daily.cs.
      ⚠️ Server cố ý KHÔNG trả về mốc hết hạn nào; đừng tự tính nửa đêm ở client để
         dựng đồng hồ đếm ngược — đó là thứ cả tính năng này quyết định không làm. */
  async getDaily(){
    const r = await this._authed(t => apiGetAuth("/me/daily", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Báo cáo tuần cho phụ huynh. `week` = 0 tuần này, 1 tuần trước…
      → { ok:true, data:{ week, child, current, previous, badges[], lifetime } }
      ⚠️ Nguồn là NHẬT KÝ sự kiện (`HIST#…`), chảy từ 09/08/2026 — tuần nào trước
         đó cũng trả `current.empty = true`, và trang phải NÓI THẬT chứ đừng vẽ 0. */
  async getReport(week){
    const w = Number(week) > 0 ? Math.floor(Number(week)) : 0;
    const r = await this._authed(t => apiGetAuth("/me/report?week=" + w, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Gửi báo cáo tuần về email của tài khoản.
      → { ok:true, data:{ sent:true, to } } hoặc { sent:false, reason:"cooldown"|"empty"|"mail-failed" }
      ⚠️ `sent:false` KHÔNG phải lỗi — đó là câu trả lời thật (tuần rỗng thì không
         gửi thư "con bạn học 0 phút"). Giao diện phải phân biệt hai thứ đó. */
  async sendReportEmail(week){
    const w = Number(week) > 0 ? Math.floor(Number(week)) : 0;
    const r = await this._authed(t => apiPostAuth("/me/report/email?week=" + w, {}, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Số dư ví thật. → { ok:true, data:{ meteors } } */
  async getWallet(){
    const r = await this._authed(t => apiGetAuth("/me/wallet", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Trừ phí một lượt. body = { reason:"game", game, opId }.
      ⚠️ KHÔNG gửi số tiền — server tra bảng phí của nó (Services/Wallet.cs).
      Không đủ tiền → { ok:false, code:"insufficient", meteors, need }. */
  async spendWallet(body){
    const r = await this._authed(t => apiPostAuth("/me/wallet/spend", body || {}, t));
    if(r.ok) return { ok:true, data:r.data };
    // Kèm số dư server báo về để phía gọi chỉnh lại cache ngay
    return Object.assign({}, r, { meteors: r.data && r.data.meteors, need: r.data && r.data.need });
  },

  /* ══════════════════════════════════════════════════════════════════════
     THANH TOÁN — xem AstroqSV/src/AstroqSV.Api/Endpoints/BillingEndpoints.cs

     ⚠️⚠️ KHÔNG hàm nào ở đây gửi SỐ TIỀN lên. Client chỉ nói mua GÓI nào, chu kỳ
        nào; server tra bảng giá của nó (Services/Billing.cs). Cùng phân công đã
        dùng cho phí mini-game ở `spendWallet` ngay phía trên — và ở đây thì
        "client gửi số tiền" nghĩa là ai cũng mua gói năm bằng 1₫.
     ⚠️⚠️ KHÔNG có hàm nào đánh dấu đơn "đã trả tiền". Trạng thái đó chỉ do webhook
        của cổng đặt; trang thanh toán chỉ ĐỌC bằng `getOrder`.
     ══════════════════════════════════════════════════════════════════════ */

  /** Bảng giá + trạng thái bán. CÔNG KHAI — không cần đăng nhập.
      → { ok:true, data:{ saleOpen, provider, currency, trialDays, offers[] } } */
  async getCatalog(cur){
    const q = cur ? "?cur=" + encodeURIComponent(cur) : "";
    const r = await apiGet("/billing/catalog" + q);
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Mở một lượt thanh toán. body = { plan, cycle, currency, opId, returnUrl }.
      → { ok:true, data:{ ok:true, order, payUrl, firstChargeAt } }
      → data.ok === false kèm `reason`: "sale-closed" | "no-provider" | …
        ⚠️ `reason:"sale-closed"` KHÔNG phải lỗi — đó là câu trả lời thật của hôm
           nay (chưa chọn cổng thanh toán). Giao diện phải phân biệt hai thứ đó,
           đúng như `sendReportEmail` đã phải làm với `sent:false`. */
  async startCheckout(body){
    const r = await this._authed(t => apiPostAuth("/me/billing/checkout", body || {}, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Trạng thái MỘT đơn của chính mình. Đây là NGUỒN SỰ THẬT duy nhất về việc đã
      trả tiền hay chưa — đừng đọc trạng thái từ query string lúc cổng trả về. */
  async getOrder(id){
    const r = await this._authed(t => apiGetAuth("/me/billing/order/" + encodeURIComponent(id), t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** 20 đơn gần nhất của chính mình. */
  async getOrders(){
    const r = await this._authed(t => apiGetAuth("/me/billing/orders", t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /**
   * XÁC MINH cờ admin TỪ ID TOKEN (không phải từ localStorage), rồi đồng bộ lại hồ sơ
   * trong máy. Đây là hàm mà giao diện phải dùng khi quyết định CÓ HIỆN mục quản trị
   * hay không.
   *
   * ⚠️ VÌ SAO KHÔNG ĐỌC `AstroQ.getUser().admin` ĐỂ HIỆN/ẨN: hồ sơ trong máy là dữ
   *    liệu ai cũng sửa được bằng DevTools, nên một tài khoản thường có thể tự làm
   *    mục quản trị hiện lên. Bấm vào thì server trả 403 (cổng thật là allowlist
   *    `ADMIN_EMAILS`) nên KHÔNG lộ dữ liệu — nhưng người dùng của app này là TRẺ EM,
   *    và một mục "chỉ tài khoản được cấp phép mới thấy" mà thấy được bằng cách sửa
   *    một dòng JSON thì không giữ được lời hứa đó. Claim nằm trong JWT do Google ký,
   *    SDK tự đối chiếu — không sửa được bằng localStorage.
   *    Cờ trong hồ sơ máy vẫn giữ, nhưng CHỈ để `select.html` (trang cố ý không nạp
   *    SDK) biết có bỏ onboarding hay không. Sửa cờ đó thì chỉ bỏ được màn giới thiệu
   *    của chính mình — không phải thứ cần bảo vệ.
   *
   * @param force Buộc lấy token MỚI. Token sống ~1 giờ, nên claim vừa gắn ở server có
   *   thể chưa có trong token đang giữ. Mặc định `false` → đọc token đã cache, KHÔNG
   *   gọi mạng, nên gọi hàm này lúc mở trang là gần như miễn phí.
   *
   * ⚠️ CHỜ `onAuthStateChanged` nên CÓ THỂ LÂU (đo được: không có phiên thì nó không
   *    bao giờ resolve). ĐỪNG `await` nó trên đường đăng nhập hay trước một lần
   *    chuyển trang — đã từng đặt ở đó và nó biến một lời gọi phụ thành chỗ kẹt cả
   *    đường vào app.
   */
  async verifyAdmin(force){
    try{
      const u = await this.currentUser();
      if(!u) return false;
      if(force) await u.getIdToken(true);
      const admin = await readAdminClaim(u);
      /* ⚠️ CHỈ CẬP NHẬT hồ sơ ĐANG CÓ, TUYỆT ĐỐI KHÔNG dựng hồ sơ mới. Việc của
         hàm này là trả lời "tôi có phải admin không", mà `syncProfile` thì GHI
         `astroq-user`. `js/admin-link.js` gọi nó ở NỀN trên dashboard/profile,
         nên nếu phiên Firebase còn sống sau khi đã đăng xuất thì đúng lời gọi này
         ÂM THẦM ĐĂNG NHẬP LẠI cho trẻ — đo được 20/08/2026. Một tác dụng phụ
         không ai đọc tên hàm mà đoán ra được. */
      if(window.AstroQ && AstroQ.getUser()) syncProfile(u, { admin });
      return admin;
    }catch(e){ return false; }
  },

  /* ---------------- Báo cáo toàn hệ thống (admin-report.html) ----------------
     ⚠️ ĐÂY LÀ LỜI GỌI DUY NHẤT KHÔNG NẰM DƯỚI `/me`. Server quyết ai được đọc —
        allowlist `ADMIN_EMAILS` + `email_verified` (xem Services/AdminAuth.cs) —
        nên client KHÔNG tự đoán "mình có phải admin không" rồi ẩn/hiện gì cả.
        Kiểm quyền ở client là kiểm trang trí: ai cũng sửa được JS trong tab của
        họ. Ở đây chỉ có: gọi, rồi đọc câu trả lời của server. */

  /** Báo cáo sức khoẻ dự án + hành vi người dùng.
      → { ok:true, data:{ cached, throttled, stale, ageSeconds, buildMs, report } }
      → { ok:false, reason:"http", status:403 } khi không phải admin
      `refresh` = true thì BẮT server quét lại bảng (server tự chặn bấm liên tục). */
  async getAdminStats(refresh){
    /* ⚠️ GỬI `true`, KHÔNG GỬI `1`. Minimal API của server bind cờ query bằng
       `bool.TryParse`, mà `TryParse` từ chối "1" — bản đầu gửi `?refresh=1` và cả
       request trả **400 với thân rỗng**, tức nút "Tính lại ngay" hỏng hoàn toàn trong
       khi dải nhắc lại báo "không gọi được server". Server nay cũng nhận "1" cho ai gõ
       tay vào thanh địa chỉ, nhưng client thì gửi đúng dạng. */
    const q = refresh ? "?refresh=true" : "";
    const r = await this._authed(t => apiGetAuth("/admin/stats" + q, t));
    return r.ok ? { ok:true, data:r.data } : r;
  },

  /** Lấy token rồi gọi `fn(token)`; gói mọi lỗi thành { ok:false, reason }. */
  async _authed(fn){
    if(!isApiConfigured) return { ok:false, reason:"notConfigured" };
    const token = await this.idToken();
    if(!token) return { ok:false, reason:"auth" };
    const r = await fn(token);
    if(r.netError)      return { ok:false, reason:"net" };
    if(r.notConfigured) return { ok:false, reason:"notConfigured" };
    // Kèm `data` cả khi lỗi: 409 "insufficient" mang theo số dư thật + số tiền cần,
    // phía gọi dùng để chỉnh lại cache ngay thay vì phải gọi thêm một vòng nữa.
    if(!r.ok)           return { ok:false, reason:"http", status:r.status,
                                 code:r.data.code, data:r.data };
    return { ok:true, data:r.data };
  }
};

/* ---------------- Trả nốt món nợ ký xuất ----------------
   Lượt đăng xuất trước có thể đã hết hạn chờ 2,5 giây trước khi Firebase ký xuất
   xong. Phiên còn sống nghĩa là `idToken()` vẫn trả token của trẻ CŨ, nên phải
   dọn nốt — và dọn ở NỀN, không ai chờ nó.
   ⚠️ Chỉ chạy khi KHÔNG có hồ sơ trong máy. Có hồ sơ nghĩa là đã có người đăng
      nhập lại rồi, ký xuất lúc đó là đá chính người đang dùng ra ngoài. */
(function(){
  try{
    if(localStorage.getItem(LS_SIGNOUT) !== "1") return;
    if(window.AstroQ && AstroQ.getUser()) return;
    (async () => {
      try{
        if(await boot()){
          await fb.signOut(auth);
          localStorage.removeItem(LS_SIGNOUT);
        }
      }catch(e){}
    })();
  }catch(e){}
})();

window.AstroQAuth = AstroQAuth;
if(!isConfigured){
  console.warn("[AstroQ] Chưa cấu hình js/firebase-config.js — đăng nhập đang chạy ở CHẾ ĐỘ DEMO " +
               "(không kiểm tra mật khẩu). Xem docs/firebase-auth.md.");
}
if(!isApiConfigured){
  console.warn("[AstroQ] Chưa đặt API_BASE trong js/api.js — đăng ký chạy ở CHẾ ĐỘ DEMO. " +
               "Xem docs/backend-astroqsv.md.");
}
export default AstroQAuth;
