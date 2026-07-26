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
  apiKey:            "AIzaSyDljo-O_8S6D8l4KP8YHxutLjO9LqLNx-A",
  authDomain:        "astroq-782f7.firebaseapp.com",
  projectId:         "astroq-782f7",
  storageBucket:     "astroq-782f7.firebasestorage.app",
  messagingSenderId: "553344918184",
  appId:             "1:553344918184:web:83aa45a74b10a0f9e8589d"
  // measurementId: "G-DPJ0N2306C"  ← chỉ dùng cho Google Analytics.
  // Cố ý KHÔNG bật: thêm một SDK nữa (~50 KB) và là script theo dõi hành vi
  // trên nền tảng dành cho trẻ em. Bật sau nếu thực sự cần đo lường.
};

/* Đã cấu hình hay chưa — chỉ cần 3 trường bắt buộc là đủ để khởi tạo. */
export const isConfigured = Boolean(
  firebaseConfig.apiKey && firebaseConfig.authDomain && firebaseConfig.projectId
);
