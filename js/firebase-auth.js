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
import { apiPost, isApiConfigured }     from "./api.js";

const SDK = "https://www.gstatic.com/firebasejs/12.16.0";

let auth = null;
let fb = null;                 // các hàm của firebase-auth SDK, nạp động
let pendingName = "";          // tên nhập lúc đăng ký, ghi vào hồ sơ sau khi xác minh xong

/* Chỉ tải SDK khi đã có config — tránh kéo vài trăm KB vô ích. */
async function boot(){
  if(!isConfigured) return null;
  if(auth) return auth;
  const [{ initializeApp }, mod] = await Promise.all([
    import(`${SDK}/firebase-app.js`),
    import(`${SDK}/firebase-auth.js`)
  ]);
  fb = mod;
  auth = mod.getAuth(initializeApp(firebaseConfig));
  // Giữ phiên sau khi đóng trình duyệt (mặc định đã vậy, khai báo cho rõ ý)
  try{ await mod.setPersistence(auth, mod.browserLocalPersistence); }catch(e){}
  return auth;
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
const fail = (e) => ({ ok: false, code: e && e.code, message: errMsg(e && e.code) });
const NOT_CONFIGURED = { ok: false, notConfigured: true, message: "" };

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

    const r = await apiPost("/auth/register", { name, email, password });
    if(r.netError)       return { ok: false, code: "net", message: errMsg("net") };
    if(r.notConfigured)  return NOT_CONFIGURED;
    if(!r.ok)            return { ok: false, code: r.data.code, message: errMsg(r.data.code) };

    return {
      ok: true, needVerify: true,
      email: r.data.email || email,
      expiresInMinutes: r.data.expiresInMinutes || 10,
      // Email gửi hỏng thì vẫn trả ok (bản ghi chờ đã lưu) nhưng báo để mời bấm "Gửi lại".
      mailSent: r.data.mailSent !== false
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
      syncProfile(cred.user);
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

  /** Đăng xuất: xoá cả phiên Firebase lẫn hồ sơ trong máy. */
  async logout(){
    try{ if(await boot()) await fb.signOut(auth); }catch(e){}
    if(window.AstroQ) AstroQ.clearUser();
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
  }
};

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
