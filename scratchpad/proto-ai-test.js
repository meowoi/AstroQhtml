/* proto-ai-test.js — PHEP THU CHO NGUYEN MAU, chay bang: node scratchpad/proto-ai-test.js
   Do dung MOT dieu: cu twist su pham cua "Train Byte" co TAI HIEN DUOC bang co hoc
   khong. Bo du lieu LECH phai lam Byte doan SAI; them du lieu DA DANG phai sua duoc.
   Neu phep [3] do thi mo hinh sai — xem chu thich (1) trong proto-ai-classifier.js.
   Boi canh day du: docs/proposals/2026-08-29-review-ai-lab.md muc 5. */
var M = require("./proto-ai-classifier.js");
// dac trung: [xam, tron, sang, dai]  — moi so trong 0..1
// KICH BAN A — bo du lieu LECH: moi thien thach deu XAM, moi ve tinh deu SANG.
var lech = [
  {f:[0.30,0.70,0.28,1.0], label:"thienthach"},
  {f:[0.28,0.66,0.30,1.0], label:"thienthach"},
  {f:[0.33,0.72,0.26,1.0], label:"thienthach"},
  {f:[0.31,0.68,0.31,1.0], label:"thienthach"},
  {f:[0.88,0.20,0.90,1.0], label:"vetinh"},
  {f:[0.85,0.24,0.87,1.0], label:"vetinh"},
  {f:[0.90,0.18,0.92,1.0], label:"vetinh"},
  {f:[0.86,0.22,0.89,1.0], label:"vetinh"}
];
// KICH BAN B — bo du lieu DA DANG: them thien thach DO/SANG va ve tinh toi.
var dadang = lech.concat([
  {f:[0.78,0.71,0.80,1.0], label:"thienthach"},   // thien thach do, sang
  {f:[0.70,0.69,0.75,1.0], label:"thienthach"},
  {f:[0.35,0.19,0.33,1.0], label:"vetinh"},       // ve tinh trong bong toi
  {f:[0.40,0.21,0.38,1.0], label:"vetinh"}
]);

// Bai kiem: mot THIEN THACH mau DO (sang) — Byte chua tung thay.
var thienThachDo = [0.82,0.70,0.84,1.0];

function show(ten, model) {
  var r = M.predict(model, thienThachDo);
  console.log("  " + ten.padEnd(22) + " -> " + r.label.padEnd(11) +
              " chac " + Math.round(r.conf*100) + "%   nhin vao: " + r.why);
  return r;
}
console.log("Vat thu: THIEN THACH mau DO (sang). Dap an dung = thienthach\n");
var a = show("day bang du lieu LECH", M.train(lech));
var b = show("day bang du lieu DA DANG", M.train(dadang));

console.log("\n=== Phep kiem ===");
function chk(t, ok){ console.log((ok?"  [OK]   ":"  [HONG] ") + t); return ok; }
var n = 0, bad = 0;
[ chk("du lieu lech -> Byte doan SAI (dung nhu bai hoc)", a.label === "vetinh"),
  chk("va no giai thich duoc: quyet dinh boi MAU/SANG", a.why === "xam" || a.why === "sang"),
  chk("du lieu da dang -> Byte doan DUNG", b.label === "thienthach"),
  chk("cu twist tai hien duoc, khong phai ke chuyen", a.label !== b.label)
].forEach(function(ok){ n++; if(!ok) bad++; });
console.log("\n" + (n-bad) + "/" + n + " dat");
process.exit(bad ? 1 : 0);
