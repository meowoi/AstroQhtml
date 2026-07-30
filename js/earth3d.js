/* ============================================================================
   earth3d.js — CẢNH TRÁI ĐẤT 3D cho Nhiệm Vụ 01 "Hành Tinh Xanh".
   ES module, Three.js nạp qua importmap (cùng phiên bản 0.160.0 với explorer.html).

   MỌI TEXTURE ĐỀU SINH BẰNG CODE (CanvasTexture) — không thêm một file ảnh nào,
   đúng cách explorer.html đang làm. Đổi lại phải tự vẽ: bản đồ ngày, đèn thành phố
   ban đêm, mây, lưới chẩn đoán.

   Cảnh gồm:
     · Trái Đất (bản đồ ngày + đèn đêm + mây quay chậm + vành khí quyển)
     · Mặt Trời ở xa: TỐI lúc đầu, `igniteSun()` thì bùng sáng và chiếu sáng một nửa
       hành tinh → ranh giới ngày/đêm hiện ra
     · Lưới Tín Hiệu Mờ bọc ngoài, `fadeGrid()` cho tan đi
     · Điểm tín hiệu nhấp nháy (`addMarkers`) — bấm được, có vòng sóng lan
     · Vệ tinh viễn thông, `satelliteAngle()` để biết trạm phát sóng đã quay tới chưa
     · Drone quét mẫu sự sống (`sendDrone`)
     · Màng khí quyển bảo bọc (`shield()`) cho lúc kết thúc

   Điều khiển: kéo để xoay, cuộn/chụm để zoom (OrbitControls).
   Chuyển cảnh giữa các nhiệm vụ: `panTo()` — di chuyển CAMERA mượt, KHÔNG tải lại
   trang, đúng yêu cầu.

   API dùng ở mission-earth.html:
     const w = await createEarthWorld(canvas);
     w.start(); w.panTo({...}); w.igniteSun(); w.addMarkers([...]);
     w.onPick(cb); w.sendDrone(...); w.shield(); w.dispose();
   ========================================================================== */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* ─────────────────────────── TEXTURE SINH BẰNG CODE ─────────────────────── */

/** Nhiễu fBm đơn giản, tất định theo `seed` — cùng seed thì luôn ra cùng hình. */
function makeNoise(seed) {
  const p = new Uint8Array(512);
  let s = seed >>> 0;
  const rnd = () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
  for (let i = 0; i < 256; i++) p[i] = Math.floor(rnd() * 256);
  for (let i = 0; i < 256; i++) p[256 + i] = p[i];
  const fade = t => t * t * t * (t * (t * 6 - 15) + 10);
  const lerp = (a, b, t) => a + (b - a) * t;
  const grad = (h, x, y) => ((h & 1) ? -x : x) + ((h & 2) ? -y : y);
  function noise2(x, y) {
    const X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
    x -= Math.floor(x); y -= Math.floor(y);
    const u = fade(x), v = fade(y);
    const a = p[X] + Y, b = p[X + 1] + Y;
    return lerp(lerp(grad(p[a], x, y), grad(p[b], x - 1, y), u),
                lerp(grad(p[a + 1], x, y - 1), grad(p[b + 1], x - 1, y - 1), u), v);
  }
  return (x, y, oct = 5) => {
    let v = 0, amp = 0.5, f = 1;
    for (let i = 0; i < oct; i++) { v += noise2(x * f, y * f) * amp; amp *= 0.5; f *= 2; }
    return v * 0.5 + 0.5;
  };
}

/**
 * Bản đồ ngày: đại dương + lục địa + sa mạc + mũ băng hai cực.
 * Trả về { day, night, mask } — `mask` là bản đồ ĐẤT/BIỂN (trắng = đất) dùng để
 * đặt đèn thành phố đúng trên đất liền, không thả đèn giữa đại dương.
 */
/* ─────────── ĐƯỜNG BỜ CÁC LỤC ĐỊA (thô, đơn vị [kinh độ, vĩ độ]) ───────────
   VÌ SAO PHẢI LÀ BẢN ĐỒ THẬT, không phải lục địa sinh bằng nhiễu:
   nhiệm vụ 4 gắn thẻ "🌊 Đại Tây Dương", "🌳 Rừng Amazon", "🐧 Nam Cực",
   "🏔️ Himalaya" vào ĐÚNG lat/lon thật của chúng. Nếu lục địa là ngẫu nhiên thì
   trẻ bấm vào chỗ ghi "Rừng Amazon" mà nhìn thấy giữa đại dương — dạy sai địa lý.
   Bản đầu dùng nhiễu và đúng là ra như vậy; ảnh chụp mới lộ ra.

   Đường bờ vẽ THÔ, đủ để nhận ra hình từng châu lục ở cỡ quả cầu trên màn hình
   (không phải bản đồ dùng để đo đạc). Không thêm file ảnh nào. */
const COASTS = [
  // Châu Phi + bán đảo Ả Rập
  [[-17,15],[-16,21],[-10,26],[-5,32],[10,37],[11,33],[20,32],[32,31],[34,28],
   [38,22],[43,12],[51,12],[45,5],[41,-1],[40,-10],[35,-19],[33,-26],[27,-34],
   [20,-35],[18,-30],[14,-22],[12,-17],[9,-1],[9,4],[3,6],[-8,4],[-13,9],[-17,15]],
  // Âu–Á
  [[-9,43],[-9,38],[0,38],[3,42],[10,44],[14,45],[19,40],[24,38],[28,41],[30,36],
   [36,36],[44,37],[48,30],[56,25],[61,25],[68,24],[72,20],[77,8],[80,9],[85,20],
   [89,22],[95,16],[99,10],[104,1],[110,10],[109,18],[117,23],[122,31],[122,37],
   [127,39],[129,43],[135,48],[140,53],[143,59],[160,61],[170,66],[180,66],
   [180,71],[160,71],[140,74],[125,74],[110,76],[95,76],[75,73],[60,71],[40,68],
   [30,70],[25,71],[20,70],[14,68],[10,63],[5,58],[8,54],[4,52],[-1,50],[-5,48],[-9,43]],
  // Bắc Mỹ
  [[-168,66],[-160,70],[-140,70],[-125,70],[-110,68],[-95,68],[-85,70],[-75,68],
   [-65,60],[-60,52],[-55,50],[-65,45],[-70,42],[-74,39],[-78,34],[-81,26],
   [-85,30],[-90,29],[-97,26],[-98,22],[-105,20],[-110,24],[-115,30],[-122,37],
   [-124,45],[-130,54],[-140,60],[-150,60],[-160,58],[-166,62],[-168,66]],
  // Nam Mỹ
  [[-81,8],[-76,10],[-70,11],[-62,10],[-52,5],[-50,0],[-44,-2],[-38,-6],[-35,-8],
   [-39,-14],[-42,-22],[-48,-25],[-53,-34],[-58,-38],[-62,-40],[-65,-45],
   [-68,-50],[-70,-55],[-75,-52],[-73,-45],[-73,-38],[-71,-30],[-70,-23],
   [-71,-18],[-77,-8],[-80,-3],[-79,2],[-81,8]],
  // Úc
  [[114,-22],[113,-26],[115,-32],[120,-34],[129,-32],[135,-35],[140,-38],
   [146,-39],[150,-37],[153,-30],[153,-25],[146,-19],[142,-11],[135,-12],
   [130,-11],[125,-14],[121,-20],[114,-22]],
  // Greenland
  [[-45,60],[-50,64],[-53,68],[-58,72],[-55,78],[-45,82],[-30,83],[-22,78],
   [-20,72],[-25,68],[-35,64],[-45,60]],
  // Madagascar
  [[44,-16],[47,-12],[50,-15],[50,-22],[47,-25],[44,-20],[44,-16]],
  // Đảo Anh
  [[-6,50],[-5,55],[-3,58],[0,54],[1,52],[-4,50]],
  // Nhật Bản
  [[130,32],[135,34],[139,36],[141,40],[145,44],[143,45],[138,37],[133,33],[130,32]],
  // Sumatra
  [[95,5],[100,2],[104,-3],[106,-6],[102,-5],[98,0],[95,5]],
  // Borneo
  [[109,2],[115,5],[119,4],[118,-2],[114,-4],[110,-3],[109,2]],
  // New Guinea
  [[131,-1],[140,-2],[147,-6],[150,-10],[143,-9],[137,-8],[131,-4],[131,-1]],
  // New Zealand
  [[166,-46],[170,-43],[174,-41],[178,-38],[176,-36],[172,-40],[168,-44],[166,-46]],
  // Bán đảo Nam Cực (phần Nam Cực còn lại vẽ bằng dải vĩ độ, xem dưới)
  [[-60,-63],[-57,-67],[-62,-72],[-72,-72],[-70,-66],[-63,-62],[-60,-63]]
];

/**
 * Bản đồ ngày + đèn đêm + mặt nạ đất/biển, vẽ từ `COASTS` (bản đồ THẬT).
 * Trả về { day, night, mask } — `mask` là bản đồ ĐẤT/BIỂN (trắng = đất) dùng để
 * đặt đèn thành phố đúng trên đất liền, không thả đèn giữa đại dương.
 */
function earthTextures(w = 2048, h = 1024) {
  const noise = makeNoise(20260729);
  const X = (lon) => ((lon + 180) / 360) * w;
  const Y = (lat) => ((90 - lat) / 180) * h;

  /* ---- 1. Mặt nạ đất/biển: tô các đa giác bờ biển ---- */
  const mk = document.createElement('canvas'); mk.width = w; mk.height = h;
  const mctx = mk.getContext('2d');
  mctx.fillStyle = '#000'; mctx.fillRect(0, 0, w, h);
  mctx.fillStyle = '#fff';
  for (const poly of COASTS) {
    mctx.beginPath();
    mctx.moveTo(X(poly[0][0]), Y(poly[0][1]));
    for (let k = 1; k < poly.length; k++) mctx.lineTo(X(poly[k][0]), Y(poly[k][1]));
    mctx.closePath(); mctx.fill();
  }
  // Nam Cực: dải liền từ vĩ độ −68 xuống cực nam
  mctx.fillRect(0, Y(-68), w, h - Y(-68));

  const maskData = mctx.getImageData(0, 0, w, h).data;

  /* ---- 2. Bản đồ ngày ---- */
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const ctx = cv.getContext('2d');
  const img = ctx.createImageData(w, h); const d = img.data;

  for (let y = 0; y < h; y++) {
    const lat = 90 - (y / h) * 180;
    const latN = Math.abs(lat) / 90;
    for (let x = 0; x < w; x++) {
      const i4 = (y * w + x) * 4;
      // 0..1 — mép đa giác có khử răng cưa nên dùng luôn làm hệ số trộn
      const land = maskData[i4] / 255;

      const lon = (x / w) * 360 - 180;
      const lonR = lon * Math.PI / 180, latR = lat * Math.PI / 180;
      const cy = Math.cos(latR);
      // Nhiễu theo HƯỚNG trên mặt cầu → liền mạch ở đường 180°, không có vệt dọc
      const n = noise(cy * Math.cos(lonR) * 3.1 + 5.1,
                      cy * Math.sin(lonR) * 3.1 + Math.sin(latR) * 3.1 + 2.7, 4);

      /* Biển: nông ở gần bờ (dùng chính độ mờ của mép), sâu ở xa */
      const deep = 0.55 + n * 0.45;
      let r = 20 + (1 - deep) * 34, g = 74 + (1 - deep) * 62, b = 138 + (1 - deep) * 60;

      if (land > 0.004) {
        /* Khí hậu theo VĨ ĐỘ + nhiễu: hoang mạc quanh chí tuyến, rừng ở xích đạo
           và ôn đới, lãnh nguyên xám ở vĩ độ cao. Đây là cách tô MÀU cho đúng cảm
           giác, không phải dữ liệu khí hậu. */
        /* Nhiễu phải ĐỦ NẶNG để phá vỡ dải hoang mạc: để `band*0.75 + n*0.45`
           với ngưỡng 0,62 thì ở giữa dải luôn vượt ngưỡng, ra một vành cát liền
           mạch vắt ngang hành tinh — nhìn ảnh chụp là thấy ngay, không giống Trái
           Đất chỗ nào. */
        const desertBand = Math.max(0, 1 - Math.abs(Math.abs(lat) - 24) / 15);
        const dry = desertBand * 0.5 + n * 0.62;
        let lr, lg, lb;
        if (dry > 0.78) { lr = 194 - n * 26; lg = 166 - n * 24; lb = 108 - n * 20; }  // hoang mạc
        else            { lr = 50 + n * 34;  lg = 104 + n * 50; lb = 56 + n * 26; }   // rừng/đồng
        if (latN > 0.62) {                                        // lãnh nguyên
          const k = Math.min(1, (latN - 0.62) / 0.16);
          lr += (150 - lr) * k; lg += (152 - lg) * k; lb += (140 - lb) * k;
        }
        r += (lr - r) * land; g += (lg - g) * land; b += (lb - b) * land;
      }

      /* Mũ băng hai cực — trùm lên cả biển (băng biển) */
      const ice = Math.max(0, latN - 0.755) / 0.11;
      if (ice > 0) {
        const k = Math.min(1, ice) * (0.82 + n * 0.18);
        r += (240 - r) * k; g += (247 - g) * k; b += (252 - b) * k;
      }
      d[i4] = r; d[i4 + 1] = g; d[i4 + 2] = b; d[i4 + 3] = 255;
    }
  }
  ctx.putImageData(img, 0, 0);

  /* ---- 3. Đèn thành phố ban đêm: chỉ trên đất liền, và tránh vùng băng ---- */
  const nv = document.createElement('canvas'); nv.width = w; nv.height = h;
  const nctx = nv.getContext('2d');
  nctx.fillStyle = '#000'; nctx.fillRect(0, 0, w, h);
  let placed = 0, tries = 0;
  while (placed < 1500 && tries < 60000) {
    tries++;
    const x = Math.floor(Math.random() * w), y = Math.floor(Math.random() * h);
    if (maskData[(y * w + x) * 4] < 160) continue;
    const lat = 90 - (y / h) * 180;
    if (Math.abs(lat) > 66) continue;             // không ai thắp đèn trên băng
    // 1,4–3,4px ở khổ 2048: để 3–10px thì ở mức phóng to của bước 4 mỗi đốm nở
    // ra ~30px trên màn hình và đọc thành đốm dung nham, không phải ánh đèn.
    const rad = 1.4 + Math.random() * 2;
    const g = nctx.createRadialGradient(x, y, 0, x, y, rad);
    g.addColorStop(0, 'rgba(255,226,150,0.95)');
    g.addColorStop(0.45, 'rgba(255,190,90,0.42)');
    g.addColorStop(1, 'rgba(255,170,60,0)');
    nctx.fillStyle = g; nctx.beginPath(); nctx.arc(x, y, rad, 0, Math.PI * 2); nctx.fill();
    placed++;
  }

  const mkTex = (canvas, srgb) => {
    const t = new THREE.CanvasTexture(canvas);
    if (srgb) t.colorSpace = THREE.SRGBColorSpace;
    t.anisotropy = 8;
    return t;
  };
  return { day: mkTex(cv, true), night: mkTex(nv, true), mask: mkTex(mk, false) };
}

/** Mây: mảng trắng mờ, alpha theo nhiễu. */
function cloudTexture(w = 1024, h = 512) {
  const noise = makeNoise(77111);
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h;
  const ctx = cv.getContext('2d');
  const img = ctx.createImageData(w, h); const d = img.data;
  for (let y = 0; y < h; y++) {
    const lat = (y / h) * 2 - 1;
    for (let x = 0; x < w; x++) {
      const lon = (x / w) * Math.PI * 2;
      const n = noise(Math.cos(lon) * 2.4 + 5.5, Math.sin(lon) * 2.4 + lat * 3.1, 4);
      // Dải mây theo vĩ độ cho giống ảnh vệ tinh thật (xích đạo và ôn đới nhiều mây)
      const band = 0.5 + 0.5 * Math.cos(lat * Math.PI * 2.6);
      const a = Math.max(0, (n * 0.75 + band * 0.25) - 0.52) / 0.48;
      const i = (y * w + x) * 4;
      d[i] = d[i + 1] = d[i + 2] = 255;
      d[i + 3] = Math.round(Math.min(1, a) * 205);
    }
  }
  ctx.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(cv); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/** Đốm sáng tròn — dùng cho hào quang Mặt Trời và điểm tín hiệu. */
function glowTexture(rgb) {
  const s = 128;
  const cv = document.createElement('canvas'); cv.width = cv.height = s;
  const ctx = cv.getContext('2d');
  const g = ctx.createRadialGradient(s / 2, s / 2, 0, s / 2, s / 2, s / 2);
  g.addColorStop(0, `rgba(${rgb},1)`);
  g.addColorStop(0.35, `rgba(${rgb},0.42)`);
  g.addColorStop(1, `rgba(${rgb},0)`);
  ctx.fillStyle = g; ctx.fillRect(0, 0, s, s);
  return new THREE.CanvasTexture(cv);
}

/* ─────────────────────────── SHADER TRÁI ĐẤT ───────────────────────────────
   Tự viết shader thay vì dùng MeshStandardMaterial vì cần đúng ba thứ cùng lúc:
   (1) trộn bản đồ NGÀY với ĐÈN ĐÊM theo hướng Mặt Trời, (2) ranh giới ngày–đêm
   mềm chứ không phải cắt gọn, (3) vành sáng khí quyển ở mép hướng về Mặt Trời.
   MeshStandardMaterial làm được (1) bằng emissiveMap nhưng không tắt đèn ở nửa
   ban ngày, nên ban ngày cũng thấy đèn thành phố — nhìn là biết sai. */
const EARTH_VERT = `
  varying vec2 vUv; varying vec3 vN; varying vec3 vWorld;
  void main() {
    vUv = uv;
    vN = normalize(normalMatrix * normal);
    vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;
const EARTH_FRAG = `
  uniform sampler2D dayMap; uniform sampler2D nightMap;
  uniform vec3 sunDir;        // hướng TỚI Mặt Trời, trong không gian thế giới
  uniform float sunOn;        // 0 = Mặt Trời chưa cháy (cảnh tối), 1 = đã cháy
  uniform float ambient;      // sáng nền tối thiểu để không đen tuyệt đối
  varying vec2 vUv; varying vec3 vN; varying vec3 vWorld;
  void main() {
    vec3 n = normalize(vN);
    float lambert = dot(normalize(vWorld), normalize(sunDir));
    // Ranh giới ngày–đêm mềm: smoothstep quanh 0 cho dải chuyển tiếp ~12°
    float dayAmt = smoothstep(-0.12, 0.24, lambert) * sunOn;

    vec3 day = texture2D(dayMap, vUv).rgb;
    vec3 night = texture2D(nightMap, vUv).rgb;

    // Đèn thành phố CHỈ hiện ở nửa tối, và mờ dần ở dải chuyển tiếp
    float nightAmt = (1.0 - dayAmt) * mix(0.35, 1.0, sunOn);
    vec3 col = day * (ambient + dayAmt * 1.15) + night * nightAmt * 1.25;

    // Vành khí quyển: mạnh ở mép nhìn nghiêng, và chỉ phía có nắng
    float rim = pow(1.0 - abs(dot(n, vec3(0.0, 0.0, 1.0))), 2.4);
    col += vec3(0.28, 0.55, 0.95) * rim * (0.25 + 0.75 * dayAmt);

    gl_FragColor = vec4(col, 1.0);
  }`;

/** Vành khí quyển vẽ trên một quả cầu lớn hơn, nhìn từ trong ra (BackSide). */
const ATMO_FRAG = `
  uniform vec3 glowColor; uniform float strength; uniform vec3 sunDir;
  varying vec3 vN; varying vec3 vWorld;
  void main() {
    vec3 n = normalize(vN);
    float rim = pow(1.0 - abs(dot(n, vec3(0.0, 0.0, 1.0))), 3.2);
    float lit = 0.35 + 0.65 * smoothstep(-0.4, 0.5,
                 dot(normalize(vWorld), normalize(sunDir)));
    gl_FragColor = vec4(glowColor, rim * strength * lit);
  }`;
const ATMO_VERT = `
  varying vec3 vN; varying vec3 vWorld;
  void main() {
    vN = normalize(normalMatrix * normal);
    vWorld = (modelMatrix * vec4(position, 1.0)).xyz;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }`;

/* ───────────────────────────── THẾ GIỚI ───────────────────────────────────── */

const R = 1;                       // bán kính Trái Đất, mọi thứ khác tính theo nó
const SUN_DIST = 26;               // Mặt Trời ở xa để tia sáng gần như song song

/** Đổi kinh/vĩ độ (độ) → vector trên mặt cầu bán kính r. */
export function latLonToVec(lat, lon, r = R) {
  const phi = (90 - lat) * Math.PI / 180;
  const theta = (lon + 180) * Math.PI / 180;
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta)
  );
}

export async function createEarthWorld(canvas, opt = {}) {
  const reduced = opt.reduced === true;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setClearColor(0x03050f, 1);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.05, 200);
  camera.position.set(0, 0.5, 4.2);

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.rotateSpeed = 0.55;
  controls.minDistance = 1.35;
  controls.maxDistance = 8;
  controls.enablePan = false;          // trẻ kéo lệch tâm là mất hành tinh khỏi khung
  controls.zoomSpeed = 0.75;

  /* ---- Trời sao (nền) ---- */
  {
    const n = reduced ? 500 : 1400;
    const pos = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const v = new THREE.Vector3().setFromSphericalCoords(
        70 + Math.random() * 40, Math.acos(2 * Math.random() - 1), Math.random() * Math.PI * 2);
      pos[i * 3] = v.x; pos[i * 3 + 1] = v.y; pos[i * 3 + 2] = v.z;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    scene.add(new THREE.Points(geo, new THREE.PointsMaterial({
      color: 0xdfe9ff, size: 0.42, sizeAttenuation: true, transparent: true, opacity: 0.85
    })));
  }

  /* ---- Trái Đất ---- */
  const tex = earthTextures(reduced ? 512 : 1024, reduced ? 256 : 512);
  const sunDir = new THREE.Vector3(1, 0.16, 0.35).normalize();

  const earthUniforms = {
    dayMap:  { value: tex.day },
    nightMap:{ value: tex.night },
    sunDir:  { value: sunDir.clone() },
    /* BẮT ĐẦU ĐÃ SÁNG. Theo bản mô tả, Trái Đất sáng bình thường ở nhiệm vụ 1
       (dạy điều khiển), rồi mới "bỗng chìm vào bóng tối" ở nhiệm vụ 2 — làm ngược
       lại thì cảnh đầu tiên trẻ thấy là một quả cầu đen, mất hết ấn tượng. */
    sunOn:   { value: 1 },
    ambient: { value: 0.08 }
  };
  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(R, reduced ? 48 : 96, reduced ? 32 : 64),
    new THREE.ShaderMaterial({
      vertexShader: EARTH_VERT, fragmentShader: EARTH_FRAG, uniforms: earthUniforms
    })
  );
  scene.add(earth);

  /* Mây quay chậm hơn hành tinh một chút → nhìn như khí quyển trôi riêng. */
  const clouds = new THREE.Mesh(
    new THREE.SphereGeometry(R * 1.012, reduced ? 40 : 72, reduced ? 26 : 48),
    new THREE.MeshBasicMaterial({
      map: cloudTexture(reduced ? 512 : 1024, reduced ? 256 : 512),
      transparent: true, opacity: 0.42, depthWrite: false
    })
  );
  scene.add(clouds);

  /* Vành khí quyển ngoài + Màng bảo bọc (bật ở nhiệm vụ 5) */
  const atmoU = {
    glowColor: { value: new THREE.Color(0x5fb7ff) },
    strength:  { value: 0.42 },
    sunDir:    { value: sunDir.clone() }
  };
  const atmo = new THREE.Mesh(
    new THREE.SphereGeometry(R * 1.045, 48, 32),   // 1.09 ra một vỏ nhựa xanh dày
    new THREE.ShaderMaterial({
      vertexShader: ATMO_VERT, fragmentShader: ATMO_FRAG, uniforms: atmoU,
      transparent: true, side: THREE.BackSide, depthWrite: false,
      blending: THREE.AdditiveBlending
    })
  );
  scene.add(atmo);

  const shieldU = {
    glowColor: { value: new THREE.Color(0x8fe4ff) },
    strength:  { value: 0 },                 // 0 = chưa bật
    sunDir:    { value: sunDir.clone() }
  };
  /* Bán kính 1,08·R, KHÔNG phải 1,22·R. Vẽ ở 1,22 thì màng nằm cách bề mặt 22%
     bán kính, ảnh chụp ra một VÒNG CYAN ĐẶC lơ lửng cạnh hành tinh chứ không phải
     lớp khí quyển bảo bọc — đúng lỗi "cung nét dày trông như vòng rời" đã gặp ở
     js/warp-screen.js. */
  const shieldMesh = new THREE.Mesh(
    new THREE.SphereGeometry(R * 1.08, 48, 32),
    new THREE.ShaderMaterial({
      vertexShader: ATMO_VERT, fragmentShader: ATMO_FRAG, uniforms: shieldU,
      transparent: true, side: THREE.BackSide, depthWrite: false,
      blending: THREE.AdditiveBlending
    })
  );
  scene.add(shieldMesh);

  /* ---- Lưới Tín Hiệu Mờ (Diagnostic Grid) ---- */
  const gridMat = new THREE.MeshBasicMaterial({
    color: 0x4de2ff, wireframe: true, transparent: true, opacity: 0.34, depthWrite: false
  });
  const grid = new THREE.Mesh(new THREE.SphereGeometry(R * 1.035, 24, 16), gridMat);
  scene.add(grid);

  /* ---- Mặt Trời ---- */
  const sunGroup = new THREE.Group();
  sunGroup.position.copy(sunDir.clone().multiplyScalar(SUN_DIST));
  const sunCore = new THREE.Mesh(
    new THREE.SphereGeometry(2.1, 32, 24),
    new THREE.MeshBasicMaterial({ color: 0xffd68a })     // sáng lúc đầu
  );
  sunGroup.add(sunCore);
  const sunGlow = new THREE.Sprite(new THREE.SpriteMaterial({
    map: glowTexture('255,196,96'), transparent: true, opacity: 0.95,
    depthWrite: false, blending: THREE.AdditiveBlending
  }));
  sunGlow.scale.setScalar(16);
  sunGroup.add(sunGlow);
  scene.add(sunGroup);

  /* Ánh sáng thật để drone/vệ tinh (vật liệu Standard) có khối, không bẹt.
     Trái Đất KHÔNG dùng đèn này — nó tự tính sáng trong shader. */
  const sunLight = new THREE.DirectionalLight(0xfff0d0, 1.5);
  sunLight.position.copy(sunGroup.position);
  scene.add(sunLight);
  scene.add(new THREE.AmbientLight(0x334466, 0.55));

  /* ---- Vệ tinh viễn thông ---- */
  const sat = new THREE.Group();
  {
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.12, 0.1),
      new THREE.MeshStandardMaterial({ color: 0xd8e4ff, metalness: 0.5, roughness: 0.4 }));
    sat.add(body);
    const panelMat = new THREE.MeshStandardMaterial({
      color: 0x4f7fd8, metalness: 0.3, roughness: 0.45,
      emissive: 0x24447f, emissiveIntensity: 0.9
    });
    for (const sx of [-1, 1]) {
      const pan = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.085, 0.01), panelMat);
      pan.position.x = sx * 0.16; sat.add(pan);
    }
    const dish = new THREE.Mesh(new THREE.SphereGeometry(0.06, 16, 10, 0, Math.PI * 2, 0, Math.PI / 2),
      new THREE.MeshStandardMaterial({ color: 0xff8a8a, side: THREE.DoubleSide,
                                       emissive: 0x8a1f1f, emissiveIntensity: 0.8 }));
    dish.rotation.x = Math.PI; dish.position.y = 0.09; dish.name = 'dish';
    sat.add(dish);
  }
  /* To hơn 1,8×: ở khoảng cách camera của bước 3, cỡ gốc chỉ vẽ ra ~14px và
     đọc thành "một thanh xám" chứ không ra hình vệ tinh. */
  sat.scale.setScalar(1.8);
  sat.position.set(2.3, 0.55, 0.5);
  /* Ẩn sẵn: chỉ nhiệm vụ 3 nói về vệ tinh. Để hiện suốt thì ở các bước khác nó
     lấp ló nửa cái ở mép màn hình khi camera pan — nhìn như một mảnh giao diện
     bị lỗi (thấy trên ảnh chụp bước 4). */
  sat.visible = false;
  scene.add(sat);

  /** Vòng sóng phát ra từ vệ tinh khi bắt được tín hiệu. */
  const satRings = [];
  function satRing() {
    const m = new THREE.Mesh(
      // Nét mảnh, mờ hơn — xem ghi chú ở `ripple()`
      new THREE.RingGeometry(0.115, 0.12, 48),
      new THREE.MeshBasicMaterial({ color: 0x5fffd0, transparent: true, opacity: 0.55,
                                    side: THREE.DoubleSide, depthWrite: false })
    );
    m.position.copy(sat.position);
    m.userData.t = 0;
    scene.add(m); satRings.push(m);
  }

  /* ---- Điểm tín hiệu / vùng sinh học (marker bấm được) ---- */
  const markers = [];
  const markerGroup = new THREE.Group();
  earth.add(markerGroup);                 // gắn vào Trái Đất để xoay cùng hành tinh

  function addMarkers(list) {
    clearMarkers();
    for (const m of list) {
      const pos = latLonToVec(m.lat, m.lon, R * 1.012);
      const g = new THREE.Group();
      g.position.copy(pos);

      const spr = new THREE.Sprite(new THREE.SpriteMaterial({
        map: glowTexture(m.rgb || '95,240,255'), transparent: true, opacity: 0.95,
        depthWrite: false, blending: THREE.AdditiveBlending
      }));
      spr.scale.setScalar(0.3);
      g.add(spr);

      const dot = new THREE.Mesh(new THREE.SphereGeometry(0.035, 12, 10),
        new THREE.MeshBasicMaterial({ color: m.color || 0xbdf5ff }));
      g.add(dot);

      markerGroup.add(g);
      markers.push({ id: m.id, group: g, sprite: spr, dot, done: false, data: m, pulse: Math.random() * 6 });
    }
  }
  function clearMarkers() {
    for (const m of markers) markerGroup.remove(m.group);
    markers.length = 0;
  }
  function markDone(id) {
    const m = markers.find(x => x.id === id);
    if (!m || m.done) return false;
    m.done = true;
    m.sprite.material.opacity = 0.28;
    m.dot.material.color.set(0x63e6a8);
    ripple(m.group.getWorldPosition(new THREE.Vector3()));
    return true;
  }

  /** Vòng sóng lan ra tại một điểm — phản hồi cho mỗi lần chạm đúng. */
  const ripples = [];
  function ripple(worldPos, color = 0x9ff0ff) {
    const m = new THREE.Mesh(
      /* Nét MẢNH (dày 6% bán kính) chứ không phải vành 43% như bản đầu: phóng
         to 7 lần thì vành dày thành một dải đặc, trông như lỗi vẽ. */
      new THREE.RingGeometry(0.094, 0.1, 44),
      new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.85,
                                    side: THREE.DoubleSide, depthWrite: false })
    );
    m.position.copy(worldPos);
    m.userData.t = 0;
    scene.add(m); ripples.push(m);
  }

  /* ---- Drone quét mẫu ---- */
  const drone = new THREE.Group();
  {
    /* `emissive` chứ KHÔNG phải thêm đèn: drone hay bay xuống nửa tối của hành
       tinh, ở đó nắng không tới nên vật liệu Standard vẽ ra một cái bóng đen. Đặt
       PointLight vào tâm drone thì vô ích — đèn nằm BÊN TRONG quả cầu nên không
       soi được mặt ngoài (đã thử, ảnh chụp vẫn ra bóng đen). */
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12),
      new THREE.MeshStandardMaterial({ color: 0xe6ecff, metalness: 0.35, roughness: 0.4,
                                       emissive: 0x9fb0e0, emissiveIntensity: 0.75 }));
    drone.add(body);
    const eye = new THREE.Mesh(new THREE.SphereGeometry(0.026, 12, 10),
      new THREE.MeshBasicMaterial({ color: 0x8f7bff }));
    eye.position.set(0, -0.03, 0.04); drone.add(eye);
    for (const sx of [-1, 1]) {
      const arm = new THREE.Mesh(new THREE.BoxGeometry(0.07, 0.008, 0.012),
        new THREE.MeshStandardMaterial({ color: 0xa9b8e8, emissive: 0x5a6a9a,
                                        emissiveIntensity: 0.7 }));
      arm.position.set(sx * 0.06, 0.02, 0); drone.add(arm);
    }
  }
  const beam = new THREE.Mesh(
    new THREE.ConeGeometry(0.055, 1, 22, 1, true),
    new THREE.MeshBasicMaterial({ color: 0xc084fc, transparent: true, opacity: 0,
                                  side: THREE.DoubleSide, depthWrite: false,
                                  blending: THREE.AdditiveBlending })
  );
  drone.add(beam);
  drone.visible = false;
  scene.add(drone);

  /* ---- Vòng lặp + trạng thái động ---- */
  let raf = 0, running = false, t = 0, last = 0;
  const anims = [];                       // các animation đang chạy (tween nhỏ)

  function tween(ms, onUpdate, onDone) {
    if (reduced) { onUpdate(1); if (onDone) onDone(); return Promise.resolve(); }
    return new Promise(res => {
      anims.push({ t: 0, ms, onUpdate, onDone: () => { if (onDone) onDone(); res(); } });
    });
  }
  const easeInOut = x => x < 0.5 ? 2 * x * x : 1 - Math.pow(-2 * x + 2, 2) / 2;

  function resize() {
    const w = canvas.clientWidth || window.innerWidth;
    const h = canvas.clientHeight || window.innerHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(1, h);
    camera.updateProjectionMatrix();
  }

  function frame(now) {
    if (!running) return;
    if (!last) last = now;
    const dt = Math.min((now - last) / 1000, 0.05);
    last = now; t += dt;

    // Tween
    for (let i = anims.length - 1; i >= 0; i--) {
      const a = anims[i];
      a.t += dt * 1000;
      const k = Math.min(1, a.t / a.ms);
      a.onUpdate(easeInOut(k));
      if (k >= 1) { anims.splice(i, 1); a.onDone(); }
    }

    if (!reduced) {
      earth.rotation.y += dt * 0.035 * spinScale;
      clouds.rotation.y += dt * 0.048 * spinScale;
    }

    // Điểm tín hiệu nhấp nháy
    for (const m of markers) {
      m.pulse += dt * 3.4;
      const s = m.done ? 0.24 : 0.26 + Math.sin(m.pulse) * 0.07;
      m.sprite.scale.setScalar(s * 1.15);
      if (!m.done) m.sprite.material.opacity = 0.7 + Math.sin(m.pulse) * 0.25;
    }

    // Vòng sóng lan
    for (let i = ripples.length - 1; i >= 0; i--) {
      const m = ripples[i]; m.userData.t += dt;
      const k = m.userData.t / 0.75;
      m.scale.setScalar(1 + k * 4);
      m.material.opacity = Math.max(0, 0.9 * (1 - k));
      m.lookAt(camera.position);
      if (k >= 1) { scene.remove(m); ripples.splice(i, 1); }
    }
    for (let i = satRings.length - 1; i >= 0; i--) {
      const m = satRings[i]; m.userData.t += dt;
      const k = m.userData.t / 1.1;
      m.scale.setScalar(1 + k * 4.5);                 // trước là 9 → vòng to quá nửa hành tinh
      m.material.opacity = Math.max(0, 0.55 * (1 - k));
      m.lookAt(camera.position);
      if (k >= 1) { scene.remove(m); satRings.splice(i, 1); }
    }

    controls.update();
    renderer.render(scene, camera);
    raf = requestAnimationFrame(frame);
  }

  let spinScale = 1;

  /* ---- Bấm chọn: raycast vào marker / Mặt Trời ---- */
  const ray = new THREE.Raycaster();
  const pickCbs = [];
  function onPointerDown(ev) {
    const rect = canvas.getBoundingClientRect();
    const nx = ((ev.clientX - rect.left) / rect.width) * 2 - 1;
    const ny = -((ev.clientY - rect.top) / rect.height) * 2 + 1;
    ray.setFromCamera(new THREE.Vector2(nx, ny), camera);

    const hit = ray.intersectObject(earth, false)[0];

    /* Mặt Trời — nhưng phải KIỂM CHE KHUẤT. Bản đầu kiểm Mặt Trời trước rồi
       `return` ngay, mà `intersectObject` không biết gì về vật chắn: Mặt Trời nằm
       sau lưng Trái Đất thì chạm vào chính hành tinh cũng tính là "đã tìm ra ngôi
       sao" — nhiệm vụ 2 tự thắng mà trẻ chưa hề xoay camera. */
    const sunHit = ray.intersectObject(sunCore, false)[0];
    if (sunHit && (!hit || sunHit.distance < hit.distance)) {
      for (const cb of pickCbs) cb({ type: 'sun' });
      return;
    }
    /* Marker: KHÔNG dùng intersectObjects lên sprite (sprite luôn hướng về camera
       nên vùng bấm rất khó đoán). Chiếu tia vào chính quả cầu rồi tìm marker gần
       điểm chạm nhất — trẻ chạm hơi lệch vẫn tính là đúng. */
    if (hit) {
      let best = null, bestD = Infinity;
      for (const m of markers) {
        if (m.done) continue;
        const wp = m.group.getWorldPosition(new THREE.Vector3());
        const d = wp.distanceTo(hit.point);
        if (d < bestD) { bestD = d; best = m; }
      }
      // Ngưỡng 0,26·R ≈ 15° cung — đủ rộng cho ngón tay trẻ, chưa tới mức bấm đâu cũng trúng
      if (best && bestD < R * 0.26) {
        for (const cb of pickCbs) cb({ type: 'marker', id: best.id, data: best.data });
        return;
      }
    }

    /* Tia TRƯỢT khỏi quả cầu (hoặc trúng cầu nhưng xa mọi marker) → thử lại bằng
       KHOẢNG CÁCH TRÊN MÀN HÌNH.
       Vì sao phải có nhánh này: marker nằm ở R·1,012, tức nhô lên trên bề mặt.
       Ở gần mép hành tinh nó chiếu ra NGOÀI đường bao của quả cầu (camera cách
       2,5·R thì đường bao chỉ rộng 0,92·R), nên trẻ thấy một đốm đang nhấp nháy,
       chạm đúng vào nó — mà không có gì xảy ra. Chỉ dựa vào raycast là bỏ rơi
       đúng những marker khó thấy nhất. */
    const rw = rect.width, rh = rect.height;
    const tapR = Math.max(22, Math.min(rw, rh) * 0.055);   // ~26px ở 1440×900, to hơn trên điện thoại
    const camDir = camera.position.clone().normalize();
    let sBest = null, sBestD = Infinity;
    const p = new THREE.Vector3();
    for (const m of markers) {
      if (m.done) continue;
      m.group.getWorldPosition(p);
      if (p.clone().normalize().dot(camDir) <= 0) continue;   // nửa bên kia hành tinh
      p.project(camera);
      const sx = (p.x * 0.5 + 0.5) * rw;
      const sy = (-p.y * 0.5 + 0.5) * rh;
      const d = Math.hypot(sx - (ev.clientX - rect.left), sy - (ev.clientY - rect.top));
      if (d < sBestD) { sBestD = d; sBest = m; }
    }
    if (sBest && sBestD < tapR) {
      for (const cb of pickCbs) cb({ type: 'marker', id: sBest.id, data: sBest.data });
      return;
    }
    if (hit) for (const cb of pickCbs) cb({ type: 'globe', point: hit.point });
  }
  canvas.addEventListener('pointerdown', onPointerDown);

  /* ---- Kéo để XOAY CHÍNH HÀNH TINH (nhiệm vụ 3) ----
     Mặc định OrbitControls quay CAMERA quanh hành tinh — nhìn thì giống nhau,
     nhưng `earth.quaternion` không đổi, nên "quay trạm phát sóng về phía vệ tinh"
     KHÔNG BAO GIỜ đạt được: vệ tinh cố định trong không gian, trạm cố định trên
     hành tinh, camera đi vòng quanh thì góc giữa hai cái đó y nguyên.
     Đo trên trang mới lộ ra: bước 3 vốn chỉ tự xong vì hành tinh TỰ quay, tức là
     trẻ ngồi chờ chứ không phải trẻ giải; mà ở `prefers-reduced-motion` thì hành
     tinh không tự quay nên bước đó treo vĩnh viễn.
     Chỉ quay quanh trục Y — đúng bài học "sự tự quay của Trái Đất" — và quay mây
     cùng một lượng để mây không trượt khỏi bề mặt. */
  let earthDrag = false, dragging = false, lastX = 0;
  function onDragDown(ev) {
    if (!earthDrag) return;
    dragging = true; lastX = ev.clientX;
    try { canvas.setPointerCapture(ev.pointerId); } catch (e) {}
  }
  function onDragMove(ev) {
    if (!earthDrag || !dragging) return;
    const dx = ev.clientX - lastX;
    lastX = ev.clientX;
    const k = (Math.PI * 2) / Math.max(1, canvas.clientWidth);   // kéo hết bề rộng = 1 vòng
    earth.rotation.y += dx * k;
    clouds.rotation.y += dx * k;
  }
  function onDragUp() { dragging = false; }
  canvas.addEventListener('pointerdown', onDragDown);
  canvas.addEventListener('pointermove', onDragMove);
  canvas.addEventListener('pointerup', onDragUp);
  canvas.addEventListener('pointercancel', onDragUp);

  const onResize = () => resize();
  window.addEventListener('resize', onResize);

  /* ═══════════════════════════ API CÔNG KHAI ═══════════════════════════ */
  const world = {
    THREE, scene, camera, controls, renderer, earth,

    start() { if (running) return; running = true; last = 0; resize(); raf = requestAnimationFrame(frame); },
    stop() { running = false; if (raf) cancelAnimationFrame(raf), raf = 0; },
    resize,

    onPick(cb) { pickCbs.push(cb); },
    addMarkers, clearMarkers, markDone,
    get markers() { return markers.map(m => ({ id: m.id, done: m.done })); },

    /**
     * Chiếu một vật trong cảnh ra toạ độ CSS của canvas.
     * Có để script kiểm thử **bấm thật vào chỗ nó đang hiện** thay vì gọi hàm
     * `pick()` tắt qua — gọi tắt thì raycast, che khuất và vùng chạm đều không
     * được kiểm, mà đó chính là những chỗ dễ sai nhất.
     * @param kind 'marker' | 'sun' | 'sat'
     * @returns {{x:number, y:number, visible:boolean}|null}
     */
    screenOf(kind, id) {
      let obj = null;
      if (kind === 'marker') { const m = markers.find(x => x.id === id); obj = m && m.group; }
      else if (kind === 'sun') obj = sunCore;
      else if (kind === 'sat') obj = sat;
      if (!obj) return null;
      const w = obj.getWorldPosition(new THREE.Vector3());
      // Trước mặt hay sau lưng camera — chiếu xong thì hai bên cho ra cùng toạ độ
      const front = w.clone().sub(camera.position).dot(
        camera.getWorldDirection(new THREE.Vector3())) > 0;
      /* Có bị chính quả cầu che không. Marker ở nửa bên kia hành tinh VẪN chiếu
         vào trong khung hình, nên thiếu phép kiểm này thì script test bấm vào một
         chỗ đúng toạ độ nhưng đang bị Trái Đất chắn — và báo hỏng oan. */
      let facing = true;
      if (kind === 'marker') {
        facing = w.clone().normalize().dot(camera.position.clone().normalize()) > 0.12;
      }
      const v = w.clone().project(camera);
      const r = renderer.domElement.getBoundingClientRect();
      return {
        x: r.left + (v.x * 0.5 + 0.5) * r.width,
        y: r.top + (-v.y * 0.5 + 0.5) * r.height,
        facing,
        visible: front && facing && Math.abs(v.x) <= 1 && Math.abs(v.y) <= 1
      };
    },

    /** Cho phép/khoá kéo-xoay và zoom (dùng khi đang chiếu cutscene). */
    setControls({ rotate, zoom } = {}) {
      if (rotate != null) controls.enableRotate = rotate;
      if (zoom != null) controls.enableZoom = zoom;
    },

    /**
     * CHUYỂN CẢNH GIỮA CÁC NHIỆM VỤ — di chuyển camera mượt, không tải lại trang.
     * @param {{lat?:number, lon?:number, dist?:number, ms?:number, target?:object}} o
     */
    panTo(o = {}) {
      const ms = o.ms != null ? o.ms : 1500;
      const fromPos = camera.position.clone();
      const fromTgt = controls.target.clone();
      const toTgt = o.target ? new THREE.Vector3(o.target.x || 0, o.target.y || 0, o.target.z || 0)
                             : new THREE.Vector3(0, 0, 0);
      const dist = o.dist != null ? o.dist : 4.2;
      let toPos;
      if (o.lat != null && o.lon != null) {
        /* Đứng thẳng trên điểm lat/lon, cách tâm `dist`.
           PHẢI nhân `earth.quaternion`: lat/lon là toạ độ TRÊN hành tinh, mà hành
           tinh có tự xoay — bỏ qua thì camera bay tới một chỗ trống trong không
           gian, không phải tới đúng vùng cần nhìn. */
        toPos = latLonToVec(o.lat, o.lon, dist)
          .applyQuaternion(earth.quaternion).add(toTgt);
      } else if (o.pos) {
        toPos = new THREE.Vector3(o.pos.x, o.pos.y, o.pos.z);
      } else {
        toPos = fromPos.clone().setLength(dist);
      }
      return tween(ms, k => {
        camera.position.lerpVectors(fromPos, toPos, k);
        controls.target.lerpVectors(fromTgt, toTgt, k);
        controls.update();
      });
    },

    /** Lưới chẩn đoán tan đi (xong nhiệm vụ 1). */
    fadeGrid(ms = 900) {
      return tween(ms, k => { gridMat.opacity = 0.34 * (1 - k); },
                   () => { grid.visible = false; });
    },
    showGrid(on) { grid.visible = on !== false; gridMat.opacity = 0.34; },

    /**
     * Bật/tắt Mặt Trời. Một hàm cho cả hai chiều vì hai cảnh đối xứng nhau:
     * nhiệm vụ 2 tắt trước (mất năng lượng) rồi bật lại (khoảnh khắc "WOW").
     * @param to 1 = cháy sáng, 0 = tối om
     */
    setSunLit(to, ms = 1500) {
      const from = earthUniforms.sunOn.value;
      // (atmo.strength giữ trong khoảng 0,42–0,72 — xem ghi chú ở chỗ tạo `atmo`)
      return tween(ms, k => {
        const v = from + (to - from) * k;
        earthUniforms.sunOn.value = v;
        earthUniforms.ambient.value = 0.13 - 0.05 * v;   // nền tối lại để nắng nổi hơn
        sunGlow.material.opacity = 0.95 * v;
        sunCore.material.color.setRGB(0.16 + 0.84 * v, 0.13 + 0.72 * v, 0.09 + 0.35 * v);
        sunLight.intensity = 1.5 * v;
        atmoU.strength.value = 0.42 + 0.30 * v;
      });
    },
    /** MẶT TRỜI BÙNG CHÁY — khoảnh khắc "WOW" của nhiệm vụ 2. */
    igniteSun(ms = 1700) { return world.setSunLit(1, ms); },
    /** Mất năng lượng: cả hành tinh chìm vào bóng tối. */
    dimSun(ms = 1200) { return world.setSunLit(0, ms); },
    get sunOn() { return earthUniforms.sunOn.value > 0.5; },

    /** Hướng TỚI Mặt Trời — mission dùng để biết điểm nào đang có nắng. */
    sunDirection() { return sunDir.clone(); },

    /* ---- Vệ tinh ---- */
    satellite: sat,
    /** Hiện/ẩn vệ tinh — chỉ nhiệm vụ 3 cần nó trong khung. */
    setSatelliteVisible(on) { sat.visible = on !== false; },
    setSatelliteSignal(on) {
      const dish = sat.getObjectByName('dish');
      if (dish) {
        dish.material.color.set(on ? 0x5fffd0 : 0xff8a8a);
        dish.material.emissive.set(on ? 0x0f6b52 : 0x8a1f1f);
      }
      if (on) { satRing(); setTimeout(satRing, 260); setTimeout(satRing, 520); }
    },
    /**
     * Góc lệch (độ) giữa trạm phát sóng trên mặt đất và hướng tới vệ tinh.
     * Nhỏ hơn ngưỡng thì coi như bắt được tín hiệu. Tính bằng vector THẬT nên
     * xoay hành tinh kiểu nào cũng đúng, không phải suy từ `earth.rotation.y`.
     */
    stationAngleTo(lat, lon) {
      const local = latLonToVec(lat, lon, R);
      const world_ = local.clone().applyQuaternion(earth.quaternion);
      const toSat = sat.position.clone().normalize();
      return THREE.MathUtils.radToDeg(world_.normalize().angleTo(toSat));
    },
    /** Cho hành tinh tự xoay nhanh/chậm/dừng (nhiệm vụ 3 để trẻ tự xoay). */
    setSpin(scale) { spinScale = scale; },

    /**
     * Đổi ý nghĩa của cú kéo: `true` = kéo xoay CHÍNH HÀNH TINH (camera đứng yên),
     * `false` = kéo xoay camera quanh hành tinh như bình thường.
     * Bật cái này thì phải TẮT `controls.enableRotate`, không thì một cú kéo làm
     * hai việc cùng lúc và trẻ mất phương hướng.
     */
    setEarthDrag(on) {
      earthDrag = on !== false;
      controls.enableRotate = !earthDrag;
      if (!earthDrag) dragging = false;
    },
    /** Góc hành tinh đã tự quay (radian) — để test chứng minh cú kéo có tác dụng. */
    get earthSpinY() { return earth.rotation.y; },

    /**
     * lat/lon của điểm trên bề mặt ĐANG hướng về camera, tính trong hệ toạ độ
     * CỦA Trái Đất (đã trừ phần hành tinh xoay) — nên truyền thẳng lại vào
     * `addMarkers`/`panTo` được.
     *
     * Dùng để đặt marker của bước hướng dẫn "quanh chỗ trẻ đang nhìn" thay vì
     * gán lat/lon cố định: hành tinh có tự xoay, nên toạ độ cố định thì tuỳ lúc
     * mở trang mà đốm nhấp nháy có thể nằm hết ở nửa bên kia — trẻ không thấy gì.
     */
    facingLatLon() {
      const v = camera.position.clone().normalize()
        .applyQuaternion(earth.quaternion.clone().invert());
      const lat = 90 - Math.acos(Math.max(-1, Math.min(1, v.y))) * 180 / Math.PI;
      // Đảo lại latLonToVec: x = -sinφ·cosθ, z = sinφ·sinθ, θ = (lon+180)°
      let lon = Math.atan2(v.z, -v.x) * 180 / Math.PI - 180;
      while (lon < -180) lon += 360;
      while (lon > 180) lon -= 360;
      return { lat, lon };
    },

    /**
     * Thả drone xuống một điểm, quét, rồi bay về tàu.
     * @returns Promise — resolve khi quét xong (để mission hiện thẻ thu thập).
     */
    async sendDrone(lat, lon) {
      /* Treo cách mặt đất 0,34·R, KHÔNG phải 0,06·R như bản đầu: chiều dài tia
         laser tính bằng `position.length() - R`, nên treo sát quá thì tia chỉ dài
         0,06 đơn vị — vẽ ra vài pixel và trên ảnh chụp trông như KHÔNG CÓ tia
         quét nào, dù mã vẫn chạy đúng. */
      const target = latLonToVec(lat, lon, R * 1.34).applyQuaternion(earth.quaternion);

      /* ĐẶT GÓC CAMERA TỪ CHÍNH ĐIỂM QUÉT, chứ không để trang gọi `panTo(lat±k)`.
         Hai đầu cùng tính một góc thì sớm muộn lệch nhau, và lệch bao nhiêu độ thì
         nhìn ra sao chỉ chỗ này biết:
           · 0°  (nhìn thẳng từ trên xuống): camera–drone–tâm Trái Đất thẳng hàng,
             tia laser chiếu THẲNG RA XA camera nên bị thân drone che kín.
           · ≳45°: drone rơi ra ngoài đường bao quả cầu (điểm ở 1,34·R, đường bao
             chỉ 0,94·R), tia trông như treo lơ lửng trong không gian.
         32° thì drone nằm gọn trong đĩa hành tinh mà tia vẫn thấy rõ đang chiếu
         xuống mặt đất. */
      const n = target.clone().normalize();
      /* Lệch NGANG (quay quanh trục Y của thế giới), không lệch dọc: lệch dọc đẩy
         drone lên đỉnh đĩa hành tinh, đúng chỗ dải toast "Drone đang quét…" đang
         nằm — hai thứ đè nhau. Gần cực thì quay quanh Y gần như không dịch được,
         lúc đó mới đổi sang trục ngang. */
      let axis = new THREE.Vector3(0, 1, 0);
      if (Math.abs(n.y) > 0.85) {
        axis = new THREE.Vector3(0, 1, 0).cross(n);
        if (axis.lengthSq() < 1e-6) axis.set(1, 0, 0);
        axis.normalize();
      }
      const camPos = n.clone().applyAxisAngle(axis, Math.PI * 26 / 180).multiplyScalar(2.9);
      await world.panTo({ pos: { x: camPos.x, y: camPos.y, z: camPos.z },
                          ms: reduced ? 0 : 800 });

      const from = camera.position.clone().multiplyScalar(0.55);
      drone.visible = true;
      drone.position.copy(from);
      beam.material.opacity = 0;

      await tween(900, k => {
        drone.position.lerpVectors(from, target, k);
        drone.lookAt(0, 0, 0);            // `lookAt` cho +Z hướng về tâm Trái Đất
      });

      /* Tia laser: hình nón CON của drone nên đi theo drone, không phải tính lại
         toạ độ thế giới mỗi khung.
         `drone.lookAt(0,0,0)` cho +Z của drone chỉ về tâm Trái Đất, nên tia phải
         loe ra dọc +Z. ConeGeometry có đỉnh ở +Y: quay **+90°** quanh X thì +Y → +Z,
         tức đỉnh ở phía mặt đất và đáy ở phía drone… nên phải dùng −90° cho đỉnh về
         phía drone. ⚠️ Đo trên ảnh chụp: −90° cho ra tia chiếu NGƯỢC LÊN trời, nên
         chiều đúng là **+90°**. Dấu của phép quay này không suy được từ mã, phải
         nhìn ảnh. */
      const h = Math.max(0.1, drone.position.length() - R);
      beam.scale.set(1, h, 1);
      beam.rotation.set(Math.PI / 2, 0, 0);
      beam.position.set(0, 0, h / 2);     // giữa đoạn từ drone tới mặt đất
      await tween(1100, k => {
        beam.material.opacity = Math.sin(k * Math.PI) * 0.8;
      }, () => { beam.material.opacity = 0; });
      ripple(drone.position.clone().setLength(R), 0xc084fc);
      await tween(700, k => {
        drone.position.lerpVectors(target, from, k);
      }, () => { drone.visible = false; });
      return true;
    },

    /** MÀNG KHÍ QUYỂN BẢO BỌC — kết thúc nhiệm vụ 5. */
    shield(ms = 1600) {
      return tween(ms, k => {
        shieldU.strength.value = 0.75 * k;      // 1,15 thì cháy trắng thành vành đặc
        atmoU.strength.value = 0.72 + 0.28 * Math.sin(k * Math.PI);
      });
    },
    get shieldOn() { return shieldU.strength.value > 0.1; },

    dispose() {
      world.stop();
      window.removeEventListener('resize', onResize);
      canvas.removeEventListener('pointerdown', onDragDown);
      canvas.removeEventListener('pointermove', onDragMove);
      canvas.removeEventListener('pointerup', onDragUp);
      canvas.removeEventListener('pointercancel', onDragUp);
      canvas.removeEventListener('pointerdown', onPointerDown);
      controls.dispose();
      scene.traverse(o => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) {
          for (const k of ['map', 'emissiveMap']) if (o.material[k]) o.material[k].dispose();
          o.material.dispose();
        }
      });
      renderer.dispose();
    }
  };

  resize();
  return world;
}
