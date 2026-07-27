/* ============================================================
   firebase-auth-ui.js — nối Firebase Auth vào popup Đăng nhập/Đăng ký
   có sẵn ở landing-app.html.

   Chia đôi trách nhiệm: firebase-auth.js lo logic, file này lo giao diện.
   Nếu js/firebase-config.js chưa điền → tự lùi về CHẾ ĐỘ DEMO y như code cũ
   (ghi thẳng localStorage, không kiểm tra mật khẩu) để trang không bị vỡ.
   ============================================================ */
import AstroQAuth            from "./firebase-auth.js";
import { API_BASE, API_MODE } from "./api.js";

const $  = (id) => document.getElementById(id);
/* Bản dự phòng phải có ĐỦ mọi phương thức file này gọi — thiếu một cái là
   ném TypeError và chết cả module, đúng lúc trang đang ở trạng thái hỏng sẵn. */
const UI = window.AstroQAuthUI || {
  close(){}, toast(m){ if(m) alert(m); }, t(k){ return k; },
  showPane(){}, open(){}
};

/* File này chỉ có việc khi popup tồn tại. Nạp nhầm ở trang khác thì thoát êm,
   không ném lỗi làm hỏng phần JS còn lại của trang. */
if(!$("auth-login") || !$("auth-register")){
  console.warn("[AstroQ] firebase-auth-ui.js: không tìm thấy form đăng nhập — bỏ qua.");
} else {

const TXT = {
  vi: { wait:"Đang xử lý…", demo:"Chế độ demo: chưa cấu hình Firebase.",
        need_email:"Nhập email của bạn trước đã nhé.",
        sent:"Đã gửi email đặt lại mật khẩu. Kiểm tra hòm thư nhé!",
        v_sent:"Đã gửi lại email kích hoạt!",
        v_nomail:"Chưa gửi được email. Bấm “Gửi lại” giúp mình nhé.",
        // Thông báo sau khi bấm link trong email (server chuyển hướng kèm ?activated=…&reason=…)
        a_ok:"Kích hoạt thành công! Đăng nhập để lên tàu nhé.",
        a_already:"Tài khoản này đã kích hoạt rồi. Đăng nhập thôi!",
        a_expired:"Link đã hết hạn. Đăng ký lại để nhận link mới nhé.",
        a_badtoken:"Link không hợp lệ. Thử bấm lại link mới nhất trong hòm thư.",
        a_notfound:"Không tìm thấy đăng ký nào. Đăng ký lại giúp mình nhé.",
        a_error:"Kích hoạt chưa xong. Thử lại sau ít phút nhé." },
  en: { wait:"Please wait…", demo:"Demo mode: Firebase is not configured.",
        need_email:"Enter your email first.",
        sent:"Password reset email sent. Check your inbox!",
        v_sent:"Activation email sent again!",
        v_nomail:"We couldn't send the email. Please tap “Resend”.",
        a_ok:"Activated! Sign in to board the ship.",
        a_already:"This account is already active. Just sign in!",
        a_expired:"That link has expired. Register again to get a new one.",
        a_badtoken:"That link isn't valid. Try the newest link in your inbox.",
        a_notfound:"No pending sign-up found. Please register again.",
        a_error:"Activation didn't finish. Please try again in a few minutes." }
};
const tx = (k) => (TXT[AstroQ.getLang()] || TXT.vi)[k] || "";

/* Khoá nút + đổi nhãn trong lúc gọi mạng, tránh bấm hai lần. */
function busy(form, on){
  const btn = form.querySelector(".auth-submit");
  if(!btn) return;
  if(!btn.dataset.label) btn.dataset.label = btn.textContent.trim();
  btn.disabled = on;
  btn.textContent = on ? tx("wait") : btn.dataset.label;
}

/* Đích đến sau khi vào được: đã chọn nhân vật thì vào khoang lái, chưa thì đi chọn. */
function go(){
  const u = AstroQ.getUser() || {};
  setTimeout(() => { location.href = u.character ? "dashboard.html" : "select.html"; }, 900);
}

/* ---------------- CHẾ ĐỘ DEMO (giữ đúng hành vi cũ) ---------------- */
function demoLogin(email){
  if(!AstroQ.getUser()) AstroQ.setUser({ name: email.split("@")[0], email });
  UI.close();
  const u = AstroQ.getUser() || {};
  UI.toast(UI.t("auth_success") + " " + UI.t("auth_hello") + " " + (u.name || email) + "!");
  go();
}
function demoRegister(name, email){
  AstroQ.setUser({ name: name || email.split("@")[0], email });
  UI.close();
  UI.toast(UI.t("auth_reg_success"));
  setTimeout(() => { location.href = "select.html"; }, 900);
}

/* ---------------- Màn chờ kích hoạt ---------------- */
/* Ở luồng mới CHƯA có phiên Firebase nào lúc này (tài khoản còn chưa tồn tại),
   nên phải tự nhớ email để còn gọi "Gửi lại" và điền sẵn ô đăng nhập. */
let verifyEmail = "";

function showVerify(email){
  verifyEmail = email || "";
  $("auth-login").hidden = true;
  $("auth-register").hidden = true;
  $("auth-verify").hidden = false;
  const slot = $("verify-mail");
  if(slot) slot.textContent = verifyEmail;
}

/* Về pane Đăng nhập, điền sẵn email vừa dùng để người dùng chỉ phải gõ mật khẩu. */
function backToLogin(email){
  UI.showPane(false);              // showPane cũng tự ẩn pane xác minh
  const box = $("login-email");
  if(box && email){ box.value = email; }
  const pass = $("login-pass");
  if(pass) setTimeout(() => pass.focus(), 60);
}

/* ---------------- Đăng nhập ---------------- */
$("auth-login").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const email = ($("login-email").value || "").trim();
  const pass  = $("login-pass").value || "";
  if(!email){ $("login-email").focus(); return; }

  if(!AstroQAuth.isConfigured){ demoLogin(email); return; }
  if(!pass){ $("login-pass").focus(); return; }

  busy(form, true);
  const res = await AstroQAuth.login(email, pass);
  busy(form, false);
  if(res.needVerify){ showVerify(res.email || email); return; }   // đúng mật khẩu nhưng chưa xác minh
  if(!res.ok){ UI.toast(res.message); $("login-pass").focus(); return; }

  UI.close();
  const u = AstroQ.getUser() || {};
  UI.toast(UI.t("auth_success") + " " + UI.t("auth_hello") + " " + (u.name || email) + "!");
  go();
});

/* ---------------- Đăng ký ---------------- */
$("auth-register").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const name  = ($("reg-name").value || "").trim();
  const email = ($("reg-email").value || "").trim();
  const pass  = $("reg-pass").value || "";
  if(!email){ $("reg-email").focus(); return; }

  // Đăng ký đi qua backend AstroqSV, nên điều kiện lùi về demo là THIẾU BACKEND
  // (khác với đăng nhập — cái đó phụ thuộc Firebase).
  if(!AstroQAuth.hasBackend){ demoRegister(name, email); return; }
  if(!pass){ $("reg-pass").focus(); return; }

  busy(form, true);
  const res = await AstroQAuth.register(name, email, pass);
  busy(form, false);
  if(!res.ok){ UI.toast(res.message); return; }

  // CHƯA có tài khoản nào cả — chỉ mới ghi nhận đăng ký và gửi link kích hoạt.
  showVerify(res.email || email);
  if(!res.mailSent) UI.toast(tx("v_nomail"));
});

/* ---------------- Nút trong màn chờ kích hoạt ---------------- */
const vCheck = $("verify-check"), vResend = $("verify-resend"), vBack = $("verify-back");

// "Tôi đã kích hoạt xong" — việc kích hoạt do server làm khi bấm link trong email,
// nên ở đây không có gì để hỏi lại; chỉ đưa về ô đăng nhập với email điền sẵn.
if(vCheck) vCheck.addEventListener("click", () => backToLogin(verifyEmail));

if(vResend) vResend.addEventListener("click", async () => {
  vResend.disabled = true;
  const res = await AstroQAuth.resendVerification(verifyEmail);
  vResend.disabled = false;
  UI.toast(res.ok ? tx("v_sent") : res.message);
});

if(vBack) vBack.addEventListener("click", () => backToLogin(verifyEmail));

/* ---------------- Chỉ báo môi trường ----------------
   Chỉ hiện khi KHÔNG phải bản thật: đang xem ở máy, hoặc đã ép ?api=… Người test
   nhìn một cái là biết dữ liệu mình vừa tạo nằm ở đâu, khỏi phải mở DevTools.
   Trên astroq.org với cấu hình mặc định thì không dựng gì cả.                     */
(function envBadge(){
  const atHome = location.hostname === "localhost" || location.hostname === "127.0.0.1";
  if(!atHome && API_MODE === "prod") return;

  const el = document.createElement("div");
  el.className = "env-badge env-badge--" + API_MODE;
  el.textContent = (atHome ? "LOCAL · " : "") + "API " + API_MODE;
  el.title = API_BASE + "  —  ?api=prod | ?api=local | ?api=reset";
  document.body.appendChild(el);
})();

/* ---------------- Quay về từ link kích hoạt ----------------
   Server chuyển hướng tới landing-app.html?activated=1&reason=ok (hoặc 0 + lý do).
   Mở popup ở pane Đăng nhập kèm thông báo tương ứng, rồi DỌN tham số khỏi thanh
   địa chỉ để tải lại trang không hiện lại thông báo cũ.                          */
(function handleActivation(){
  const q = new URLSearchParams(location.search);
  if(!q.has("activated")) return;

  const reason  = q.get("reason") || "error";
  const emailQ  = q.get("e") || "";
  const success = q.get("activated") === "1";

  history.replaceState(null, "", location.pathname + location.hash);

  // Hết hạn thì đưa thẳng sang form Đăng ký — người dùng cần link mới, không phải mật khẩu.
  const toRegister = reason === "expired" || reason === "notfound";
  UI.open(toRegister);
  if(emailQ){
    const box = $(toRegister ? "reg-email" : "login-email");
    if(box) box.value = emailQ;
  }
  UI.toast(tx("a_" + reason) || tx(success ? "a_ok" : "a_error"));
})();

/* ---------------- Quên mật khẩu ---------------- */
const forgot = $("auth-forgot");
if(forgot) forgot.addEventListener("click", async () => {
  const email = ($("login-email").value || "").trim();
  if(!email){ UI.toast(tx("need_email")); $("login-email").focus(); return; }
  if(!AstroQAuth.isConfigured){ UI.toast(tx("demo")); return; }

  forgot.disabled = true;
  const res = await AstroQAuth.resetPassword(email);
  forgot.disabled = false;
  UI.toast(res.ok ? tx("sent") : res.message);
});

}   // hết khối "popup tồn tại"
