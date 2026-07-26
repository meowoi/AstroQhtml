/* ============================================================
   firebase-config.js — CHỖ DUY NHẤT bạn cần sửa để bật đăng nhập thật.

   Lấy khối này ở đâu:
     console.firebase.google.com → chọn project → ⚙ Project settings
     → cuộn xuống "Your apps" → bấm biểu tượng </> (Web) → Register app
     → Firebase hiện sẵn "const firebaseConfig = {...}" → copy các giá trị vào dưới.

   Trước đó nhớ bật provider:
     Build → Authentication → Sign-in method → Email/Password → Enable

   Và cho phép tên miền:
     Authentication → Settings → Authorized domains → Add domain → astroq.org
     (localhost có sẵn nên chạy thử ở máy vẫn được)

   Lưu ý: apiKey của Firebase Web là CÔNG KHAI theo thiết kế — nó chỉ định danh
   project, không phải mật khẩu. An toàn đến từ Authorized domains + Security Rules.
   Không cần giấu, không cần biến môi trường.

   CHƯA điền → trang vẫn chạy bình thường ở chế độ demo như trước (ghi thẳng
   localStorage, không kiểm tra mật khẩu) và console in cảnh báo.
   ============================================================ */

export const firebaseConfig = {
  apiKey:            "",
  authDomain:        "",
  projectId:         "",
  storageBucket:     "",
  messagingSenderId: "",
  appId:             ""
};

/* Đã cấu hình hay chưa — chỉ cần 3 trường bắt buộc là đủ để khởi tạo. */
export const isConfigured = Boolean(
  firebaseConfig.apiKey && firebaseConfig.authDomain && firebaseConfig.projectId
);
