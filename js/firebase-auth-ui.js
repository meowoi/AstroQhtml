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
        /* Email này đã có một đăng ký đang chờ kích hoạt, và server GIỮ mật khẩu
           của lượt đầu (chốt chặn chiếm quyền — xem AuthEndpoints). Không nói ra
           thì người dùng kích hoạt xong sẽ đăng nhập bằng mật khẩu vừa gõ và không
           vào được, mà chẳng có gì giải thích. */
        v_pwkept:"Email này đang có một đăng ký chờ kích hoạt. Mình đã gửi lại link, nhưng mật khẩu vẫn là mật khẩu bạn đặt lần đầu nhé.",
        /* ─── Đăng ký xong và ĐÃ Ở TRONG PHIÊN (04/09/2026) ───────────────────────
           ⚠️ CÂU NÀY LÀ CHỖ DUY NHẤT CÒN MỜI NGƯỜI TA MỞ HÒM THƯ trên đường đăng ký,
              nên nó phải nói cái ĐƯỢC (quà khởi đầu) chứ không phải cái PHẢI LÀM.
              "Xác minh email của bạn" là câu của bức tường vừa gỡ; nó không cho người
              đọc một lý do nào để đứng lên đi mở hòm thư. */
        r_in_gift:"Xong! Tàu của con đã sẵn sàng 🚀 Mở email bấm link kích hoạt để nhận Purple Meteors quà khởi đầu nhé!",
        r_in_nomail:"Xong! Tàu của con đã sẵn sàng 🚀 (Thư kích hoạt chưa gửi được — vào Hồ sơ bấm “Gửi lại” để nhận quà khởi đầu nhé.)",
        /* Tài khoản đã có nhưng chưa vào được phiên — việc cần làm là ĐĂNG NHẬP. */
        r_signin:"Tài khoản đã tạo xong! Đăng nhập bằng email và mật khẩu vừa đặt để lên tàu nhé.",
        r_pwkept:"Email này đã có tài khoản từ trước. Mật khẩu vẫn là mật khẩu bạn đặt lần đầu — đăng nhập bằng mật khẩu đó nhé.",
        /* Đăng nhập bằng một tài khoản CHƯA kích hoạt. Trước 29/08/2026 ca này nhận
           câu "Email hoặc mật khẩu không đúng." của Firebase — sai, và đẩy người ta
           đi sửa đúng cái đang không hỏng. Xem `pendingState` ở js/firebase-auth.js. */
        v_title_notyet:"Tài khoản chưa kích hoạt",
        v_sub_notyet:"Mật khẩu của bạn đúng rồi! Chỉ còn thiếu một bước: mở email và bấm link kích hoạt là vào được ngay.",
        v_sub_expired:"Mật khẩu của bạn đúng rồi! Nhưng link trong email đã hết hạn — bấm “Gửi lại link” để nhận link mới nhé.",
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
        v_pwkept:"This email already has a sign-up waiting to be activated. We resent the link, but your password stays the one you set the first time.",
        // Signed up AND already in the session (04/09/2026) — see the VI note above.
        r_in_gift:"You're in! Your ship is ready 🚀 Open your email and tap the activation link to claim your starter Purple Meteors!",
        r_in_nomail:"You're in! Your ship is ready 🚀 (We couldn't send the activation email — tap “Resend” in your Profile to claim your starter gift.)",
        r_signin:"Account created! Sign in with the email and password you just set to board the ship.",
        r_pwkept:"This email already had an account. Your password stays the one you set the first time — please sign in with that one.",
        v_title_notyet:"Account not activated yet",
        v_sub_notyet:"Your password is correct! One step left: open your email and tap the activation link.",
        v_sub_expired:"Your password is correct! But the link in your email has expired — tap “Resend link” to get a new one.",
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

/* Đích đến sau khi vào được: đã chọn nhân vật thì vào khoang lái, chưa thì đi chọn.
   TÀI KHOẢN ADMIN ĐI CÙNG ĐƯỜNG NÀY — nó là tài khoản chơi bình thường, chỉ thêm một
   đường vào trang báo cáo ở hồ sơ (xem js/admin-link.js).

   ⚠️ CỐ Ý KHÔNG rẽ admin sang `admin-report.html` ở đây. Bản trước làm vậy và nó phải
      `await` một lời gọi đọc claim TRƯỚC khi chuyển trang — biến đường vào app của
      MỌI đứa trẻ thành phụ thuộc vào một lời gọi chỉ dùng để chọn trang (và lời gọi
      đó đo được là có thể không bao giờ resolve khi không có phiên). Giờ cờ admin đã
      được `login()` đóng dấu vào hồ sơ máy, nên không cần chờ gì ở đây nữa. */
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

/* `reason` quyết định hai dòng chữ trên cùng của pane:
     ""        → vừa đăng ký xong, thư đang trên đường (chữ mặc định trong HTML)
     "notyet"  → đang ĐĂNG NHẬP bằng tài khoản chưa kích hoạt
     "expired" → như trên, và link trong thư đã quá 10 phút

   ⚠️ ĐƯỜNG ĐĂNG NHẬP PHẢI ĐỔI CHỮ, không được dùng lại chữ mặc định. Câu mặc định là
      "Chúng tớ VỪA GỬI một email kích hoạt" — người đăng ký từ hôm qua rồi hôm nay
      mới thử đăng nhập mà đọc câu đó sẽ đi tìm một lá thư không tồn tại.

   ⚠️ Ghi đè bằng `textContent` chứ không đụng `data-i18n`: bộ chuyển ngôn ngữ của
      landing-app.html quét đúng thuộc tính đó và sẽ ghi đè lại chữ của mình ngay lần
      bấm cờ tiếp theo. Nên xoá luôn `data-i18n` khỏi hai thẻ này khi đã đổi chữ —
      và trả lại khi về ca mặc định, không thì pane sau khi đăng ký mất tiếng Anh. */
function showVerify(email, reason){
  verifyEmail = email || "";
  $("auth-login").hidden = true;
  $("auth-register").hidden = true;
  $("auth-verify").hidden = false;
  const slot = $("verify-mail");
  if(slot) slot.textContent = verifyEmail;

  const title = $("auth-verify").querySelector(".auth-title");
  const sub   = $("auth-verify").querySelector(".auth-sub");
  const notActivated = reason === "notyet" || reason === "expired";
  if(title) setPaneText(title, notActivated ? tx("v_title_notyet") : "", "verify_title");
  if(sub)   setPaneText(sub,
              reason === "expired" ? tx("v_sub_expired")
            : reason === "notyet"  ? tx("v_sub_notyet") : "", "verify_sub");
}

/* Đặt chữ tuỳ ca, hoặc trả thẻ về cho bộ i18n của trang lo (khi `text` rỗng).

   ⚠️ TRẢ VỀ thì phải VIẾT LẠI chữ ngay, không chỉ gắn lại `data-i18n`: `applyTexts`
      của js/ui-common.js chỉ chạy khi ĐỔI ngôn ngữ, nên chỉ gắn thuộc tính thôi là
      để nguyên câu của ca trước nằm đó cho tới lần bấm cờ tiếp theo. Lấy chữ qua
      `UI.t` (từ điển của chính trang) nên nó luôn đúng ngôn ngữ đang hiển thị.
   ⚠️ `dataset.orig` là lưới đỡ cho trường hợp `UI.t` là bản dự phòng trả về chính
      cái khoá — thà hiện lại câu tiếng Việt gốc còn hơn hiện chữ "verify_sub". */
function setPaneText(el, text, i18nKey){
  if(!el.dataset.orig) el.dataset.orig = el.textContent;
  if(text){
    el.removeAttribute("data-i18n");
    el.textContent = text;
    return;
  }
  el.setAttribute("data-i18n", i18nKey);
  const back = UI.t(i18nKey);
  el.textContent = (back && back !== i18nKey) ? back : el.dataset.orig;
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
  /* Đúng mật khẩu nhưng chưa vào được. `notActivated` = đăng ký còn đang chờ ở
     DynamoDB, tài khoản Firebase còn chưa ra đời (ca thường gặp); không có cờ đó là
     tài khoản Firebase cũ có `emailVerified=false` (dữ liệu trước kiến trúc 2 giai
     đoạn). Cả hai đều dừng ở pane này, chỉ khác lời giải thích.
     ⚠️ CÓ TOAST, không chỉ đổi pane. Popup đổi nội dung mà không ai nói gì thì người
        dùng không chắc mình vừa bấm sai hay trang vừa hỏng — và câu cần nói nhất
        ("mật khẩu bạn không sai đâu") chính là câu đang thiếu suốt từ đầu. */
  if(res.needVerify){
    showVerify(res.email || email,
               res.notActivated ? (res.linkExpired ? "expired" : "notyet") : "");
    if(res.message) UI.toast(res.message);
    return;
  }
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

  /* ══════════ ĐƯỜNG THƯỜNG TỪ 04/09/2026: ĐÃ Ở TRONG PHIÊN, VÀO CHƠI LUÔN ══════════
     ⚠️⚠️ KHÔNG hiện màn chờ kích hoạt ở đây nữa. Màn đó là bức tường mà việc 2 gỡ
        xuống: nó nói "mở hòm thư đi" với một người ĐÃ đăng nhập xong, tức chỉ họ đi
        làm một việc không cần thiết để đi tiếp — và 2 trong 3 người ngoài đo được đã
        rời đi đúng ở chỗ này.
     ⚠️ NHƯNG VẪN PHẢI NHẮC MỘT CÂU VỀ CÁI LINK, vì quà khởi đầu chỉ cấp SAU khi bấm
        link (chốt của chủ dự án). Ví đang 0 tt: nhiệm vụ và quiz chơi được ngay, còn
        mini-game thì chưa — không nói ra thì trẻ gặp "không đủ Purple Meteors" ở games
        mà chẳng biết tiền nằm ở đâu. Đây là toast MỜI, không phải cửa chặn. */
  if(res.signedIn){
    UI.close();
    UI.toast(res.mailSent ? tx("r_in_gift") : tx("r_in_nomail"));
    go();
    return;
  }

  /* Tài khoản CÓ nhưng chưa vào được phiên. Hai ca, và ca nào cũng phải nói ra vì
     người dùng vừa gõ một mật khẩu mà nó không dùng được:
       · `passwordKept` — server giữ mật khẩu của lượt đăng ký ĐẦU.
       · còn lại        — Firebase không với tới (mất mạng / chưa cấu hình).
     Cả hai đưa về ô Đăng nhập với email điền sẵn, không phải màn chờ kích hoạt: việc
     cần làm là ĐĂNG NHẬP, không phải mở hòm thư. */
  if(res.account){
    backToLogin(res.email || email);
    UI.toast(res.passwordKept ? tx("r_pwkept") : tx("r_signin"));
    return;
  }

  /* CHƯA có tài khoản nào cả — chỉ còn xảy ra với bản ghi chờ KIỂU CŨ (đăng ký trước
     04/09/2026, xem `register()` ở js/firebase-auth.js). Giữ nguyên hành vi cũ.
     Không truyền `reason`: đây ĐÚNG là ca "vừa gửi thư", tức chữ mặc định trong HTML. */
  showVerify(res.email || email, "");
  /* Một toast thôi. Không gửi được email là việc CẦN LÀM NGAY ("bấm Gửi lại"),
     nên nó thắng; chồng hai toast lên nhau thì cái sau che mất cái trước. */
  if(!res.mailSent)          UI.toast(tx("v_nomail"));
  else if(res.passwordKept)  UI.toast(tx("v_pwkept"));
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
