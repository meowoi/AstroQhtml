/* ============================================================
   api.js — nói chuyện với backend AstroqSV (AWS Lambda + API Gateway).

   CHỖ DUY NHẤT chứa địa chỉ máy chủ. Đổi stack / đổi vùng / gắn custom domain
   thì sửa đúng một dòng dưới đây.

   Để rỗng ("") → mọi lời gọi trả { notConfigured:true } và phía trên tự lùi về
   luồng cũ, trang không bao giờ vỡ (cùng nguyên tắc với js/firebase-config.js).
   ============================================================ */
export const API_BASE = "https://ueqp4gjr0l.execute-api.ap-southeast-1.amazonaws.com";

export const isApiConfigured = /^https:\/\/\S+/.test(API_BASE);

const NOT_CONFIGURED = { ok: false, notConfigured: true, status: 0, data: {} };

/* Mạng yếu thì đừng để người dùng ngồi nhìn nút "Đang xử lý…" mãi. */
const TIMEOUT_MS = 20000;

/**
 * Gọi API, luôn trả về object — KHÔNG bao giờ ném lỗi ra ngoài, để phía giao diện
 * chỉ phải xử lý một hình dạng dữ liệu duy nhất.
 * @returns {Promise<{ok:boolean, status:number, data:object, netError?:boolean}>}
 */
export async function apiCall(method, path, body){
  if(!isApiConfigured) return NOT_CONFIGURED;

  const ctrl  = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), TIMEOUT_MS);
  try{
    const res = await fetch(API_BASE + path, {
      method,
      headers: body ? { "Content-Type": "application/json" } : undefined,
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
