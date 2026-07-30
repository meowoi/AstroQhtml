/* ============================================================
   api.js — nói chuyện với backend AstroqSV (AWS Lambda + API Gateway).

   BA CHẾ ĐỘ CHẠY SONG SONG
   ─────────────────────────────────────────────────────────────
     prod   https://astroq.org            → API trên AWS      (mặc định khi ở astroq.org)
     dev    http://localhost:8000         → API trên AWS      (mặc định khi ở máy)
     local  http://localhost:8000         → API `dotnet run`  (phải tự bật)

   Đổi chế độ bằng THAM SỐ URL, nhớ luôn cho các lần sau:
     ?api=prod     → ép dùng API trên AWS
     ?api=local    → dùng API chạy ở máy (http://localhost:5080)
     ?api=https://…→ trỏ tới một địa chỉ bất kỳ (stack thử nghiệm chẳng hạn)
     ?api=reset    → xoá lựa chọn, quay về mặc định theo tên miền

   Vì sao mặc định ở máy vẫn trỏ lên AWS: xem thử giao diện là việc thường xuyên,
   còn bật backend là việc hiếm. Cái nào hay làm hơn thì để nó khỏi phải cấu hình.

   BACKEND TỰ BIẾT CHUYỂN HƯỚNG VỀ ĐÂU — cả hai bản dùng chung một API, nhưng Lambda
   đọc header Origin của lời gọi đăng ký (có đối chiếu allowlist) rồi ghi vào bản ghi
   chờ, nên link kích hoạt trong email sẽ đưa bạn về đúng nơi đã đăng ký: đăng ký ở
   localhost thì quay về localhost, ở astroq.org thì quay về astroq.org.

   Để API_BASE rỗng ("") → mọi lời gọi trả { notConfigured:true } và phía trên tự lùi
   về luồng cũ, trang không bao giờ vỡ (cùng nguyên tắc với js/firebase-config.js).
   ============================================================ */

/** API đã deploy trên AWS. Đổi stack / đổi vùng / gắn custom domain thì sửa dòng này. */
const PROD_API  = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com";

/** Cổng của `dotnet run` trong AstroqSV/src/AstroqSV.Api (xem Properties/launchSettings.json). */
const LOCAL_API = "http://localhost:5080";

const STORE_KEY = "astroq-api";

/* Tham số ?api=… có quyền cao nhất và được ghi nhớ, để bấm quanh site không mất lựa chọn. */
function readOverride(){
  let saved = null;
  try{ saved = localStorage.getItem(STORE_KEY); }catch(e){}   // chế độ riêng tư chặn localStorage

  const q = new URLSearchParams(location.search).get("api");
  if(!q) return saved;

  const picked = q === "local" ? LOCAL_API
               : q === "prod"  ? PROD_API
               : q === "reset" ? null
               : /^https?:\/\/\S+/.test(q) ? q.replace(/\/+$/, "")
               : saved;

  try{
    if(picked) localStorage.setItem(STORE_KEY, picked);
    else       localStorage.removeItem(STORE_KEY);
  }catch(e){}
  return picked;
}

export const API_BASE = readOverride() || PROD_API;

/** "prod" | "local" | "custom" — dùng để hiện chỉ báo cho người test khỏi nhầm. */
export const API_MODE = API_BASE === PROD_API  ? "prod"
                      : API_BASE === LOCAL_API ? "local"
                      : "custom";

export const isApiConfigured = /^https?:\/\/\S+/.test(API_BASE);

/* Đang chạy ở máy thì in ra để biết mình đang gọi vào đâu — đỡ mất công đoán khi
   thấy dữ liệu lạ. Trên astroq.org thì im lặng. */
if(location.hostname === "localhost" || location.hostname === "127.0.0.1"){
  console.info(`[AstroQ] API (${API_MODE}): ${API_BASE}` +
               (API_MODE === "prod" ? "  ·  đổi bằng ?api=local" : "  ·  về mặc định bằng ?api=reset"));
}

const NOT_CONFIGURED = { ok: false, notConfigured: true, status: 0, data: {} };

/* Mạng yếu thì đừng để người dùng ngồi nhìn nút "Đang xử lý…" mãi. */
const TIMEOUT_MS = 20000;

/**
 * Gọi API, luôn trả về object — KHÔNG bao giờ ném lỗi ra ngoài, để phía giao diện
 * chỉ phải xử lý một hình dạng dữ liệu duy nhất.
 *
 * `token` = ID token Firebase cho các route /me/* (server lấy uid TỪ token, nên
 * client không bao giờ gửi uid lên — gửi uid thì ai cũng đọc được hồ sơ người khác).
 * @returns {Promise<{ok:boolean, status:number, data:object, netError?:boolean}>}
 */
export async function apiCall(method, path, body, token){
  if(!isApiConfigured) return NOT_CONFIGURED;

  const ctrl  = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try{
    const headers = {};
    if(body)  headers["Content-Type"]  = "application/json";
    if(token) headers["Authorization"] = "Bearer " + token;

    const res = await fetch(API_BASE + path, {
      method,
      headers: Object.keys(headers).length ? headers : undefined,
      body:    body ? JSON.stringify(body) : undefined,
      signal:  ctrl.signal
    });
    // 204 và lỗi tầng hạ tầng không có thân JSON — nuốt lỗi parse thay vì để vỡ.
    let data = {};
    try{ data = await res.json(); }catch(e){}
    return { ok: res.ok, status: res.status, data };
  }catch(e){
    // Mất mạng, DNS hỏng, CORS chặn, hoặc quá TIMEOUT_MS
    return { ok: false, status: 0, data: {}, netError: true };
  }finally{
    clearTimeout(timer);
  }
}

export const apiPost = (path, body) => apiCall("POST", path, body);
export const apiGet  = (path)       => apiCall("GET",  path);

/* Bản có token — dùng cho /me/*. Tách tên riêng để đọc code là thấy ngay
   lời gọi nào cần đăng nhập, không phải đếm tham số. */
export const apiGetAuth  = (path, token)       => apiCall("GET",  path, undefined, token);
export const apiPutAuth  = (path, body, token) => apiCall("PUT",  path, body, token);
export const apiPostAuth = (path, body, token) => apiCall("POST", path, body, token);
