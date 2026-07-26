/* ============================================================
   firebase-auth-ui.js — nối Firebase Auth vào popup Đăng nhập/Đăng ký
   có sẵn ở landing-app.html.

   Chia đôi trách nhiệm: firebase-auth.js lo logic, file này lo giao diện.
   Nếu js/firebase-config.js chưa điền → tự lùi về CHẾ ĐỘ DEMO y như code cũ
   (ghi thẳng localStorage, không kiểm tra mật khẩu) để trang không bị vỡ.
   ============================================================ */
import AstroQAuth from "./firebase-auth.js";

const $  = (id) => document.getElementById(id);
const UI = window.AstroQAuthUI || {
  close(){}, toast(m){ if(m) alert(m); }, t(k){ return k; }
};

/* File này chỉ có việc khi popup tồn tại. Nạp nhầm ở trang khác thì thoát êm,
   không ném lỗi làm hỏng phần JS còn lại của trang. */
if(!$("auth-login") || !$("auth-register")){
  console.warn("[AstroQ] firebase-auth-ui.js: không tìm thấy form đăng nhập — bỏ qua.");
} else {

const TXT = {
  vi: { wait:"Đang xử lý…", demo:"Chế độ demo: chưa cấu hình Firebase.",
        need_email:"Nhập email của bạn trước đã nhé.",
        sent:"Đã gửi email đặt lại mật khẩu. Kiểm tra hòm thư nhé!" },
  en: { wait:"Please wait…", demo:"Demo mode: Firebase is not configured.",
        need_email:"Enter your email first.",
        sent:"Password reset email sent. Check your inbox!" }
};
const tx = (k) => (TXT[AstroQ.getLang()] || TXT.vi)[k];

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

  if(!AstroQAuth.isConfigured){ demoRegister(name, email); return; }
  if(!pass){ $("reg-pass").focus(); return; }

  busy(form, true);
  const res = await AstroQAuth.register(name, email, pass);
  busy(form, false);
  if(!res.ok){ UI.toast(res.message); return; }

  UI.close();
  UI.toast(UI.t("auth_reg_success"));
  setTimeout(() => { location.href = "select.html"; }, 900);   // → chọn nhân vật
});

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
