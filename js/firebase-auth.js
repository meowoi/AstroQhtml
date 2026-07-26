/* ============================================================
   firebase-auth.js — Đăng ký / Đăng nhập bằng Firebase Authentication
   (provider Email/Password — tức "tài khoản & mật khẩu", khác đăng nhập Google/Facebook).

   ES MODULE: nạp bằng <script type="module">, nên luôn chạy SAU mọi script cổ điển
   → AstroQ (js/ui-common.js) và Economy chắc chắn đã tồn tại.

   Chưa điền js/firebase-config.js → mọi hàm trả về { ok:false, notConfigured:true }
   để phía giao diện tự lùi về chế độ demo cũ. Trang không bao giờ vỡ.
   ============================================================ */
import { firebaseConfig, isConfigured } from "./firebase-config.js";

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
    _default:                     "Something went wrong. Please try again."
  }
};
function errMsg(code){
  const d = ERR[(window.AstroQ && AstroQ.getLang()) || "vi"] || ERR.vi;
  return d[code] || d._default;
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

  /** Đăng ký. Tài khoản được tạo ngay (Firebase không có luồng "xác minh trước khi tạo"),
      nhưng CHƯA ghi hồ sơ vào máy và CHƯA cho vào app cho tới khi xác minh email.
      → { ok:true, needVerify:true, email } | { ok:false, message } */
  async register(name, email, password){
    if(!(await boot())) return NOT_CONFIGURED;
    try{
      const cred = await fb.createUserWithEmailAndPassword(auth, email, password);
      // displayName không đặt được lúc tạo, phải cập nhật ở bước riêng
      if(name) await fb.updateProfile(cred.user, { displayName: name });
      pendingName = name || "";
      await fb.sendEmailVerification(cred.user);
      // Cố ý KHÔNG gọi syncProfile: chưa xác minh thì chưa có hồ sơ trong máy,
      // nhờ vậy mọi lối vào app (đều dựa trên uid trong localStorage) đều bị chặn.
      return { ok: true, needVerify: true, email: cred.user.email };
    }catch(e){ return fail(e); }
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

  /** Gửi lại email xác minh cho tài khoản đang ở trạng thái chờ. */
  async resendVerification(){
    if(!(await boot())) return NOT_CONFIGURED;
    const u = auth.currentUser;
    if(!u) return { ok: false, message: errMsg("auth/requires-recent-login") };
    try{ await fb.sendEmailVerification(u); return { ok: true }; }
    catch(e){ return fail(e); }
  },

  /** Người dùng bấm "Tôi đã xác minh xong" → hỏi lại Firebase.
      Xác minh rồi thì mới ghi hồ sơ vào máy. */
  async checkVerified(){
    if(!(await boot())) return NOT_CONFIGURED;
    const u = auth.currentUser;
    if(!u) return { ok: false, message: errMsg("auth/requires-recent-login") };
    try{
      await fb.reload(u);
      if(!u.emailVerified) return { ok: false, stillPending: true };
      syncProfile(u, pendingName ? { name: pendingName } : null);
      pendingName = "";
      return { ok: true, user: u };
    }catch(e){ return fail(e); }
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
export default AstroQAuth;
