/* Nguyen mau: bo phan loai THAT, vanilla JS, khong thu vien, khong build step.
   Mo hinh = k-NN (k lang gieng gan nhat) tren 4 dac trung NHIN THAY DUOC.

   ⚠️⚠️ VI SAO k-NN CHU KHONG PHAI NEAREST-CENTROID — do duoc, khong phai so thich.
      Ban dau toi dung trong tam moi lop (goi la nearest centroid). No CHAY, no
      nhe hon, va no VAN cho ra cu twist "du lieu lech -> doan sai". Nhung phep
      thu tiep theo lam no do: them du lieu DA DANG vao thi Byte VAN doan sai —
      vi lay trung binh chinh la XOA MAT su da dang vua them.
      Tuc la nua sau cua bai hoc ("them du lieu da dang thi AI khá lên") KHONG
      TAI HIEN DUOC. Mot game day machine learning ma buoc sua khong co tac dung
      thi no day sai, va tre se hoc duoc dieu nguoc lai.
      k-NN thi moi mau tre them vao la MOT LANG GIENG THAT — sua duoc ngay.
      Va no dung ve su pham hon: "Byte NHO nhung mau ban da day, roi tim mau
      giong nhat", dung thu mot dua 8 tuoi hinh dung duoc. */

var FEAT = ["xam", "tron", "sang", "dai"];   // do xam TB · do tron · do sang · ti le dai/rong
var K = 3;

/* "Huan luyen" cua k-NN = NHO LAI. Co y de nguyen mot ham cho ro y: buoc
   TRAIN trong game la mot man hinh that (thanh tien trinh), khong phai o day. */
function train(samples) { return { data: samples.slice(), k: K }; }

function dist(a, b) {
  var s = 0;
  for (var i = 0; i < a.length; i++) s += (a[i] - b[i]) * (a[i] - b[i]);
  return Math.sqrt(s);
}

function predict(model, f) {
  var near = model.data.map(function (s) { return { label: s.label, d: dist(s.f, f), f: s.f }; })
                       .sort(function (a, b) { return a.d - b.d; })
                       .slice(0, Math.min(model.k, model.data.length));
  var vote = {};
  near.forEach(function (p) { vote[p.label] = (vote[p.label] || 0) + 1; });
  var best = Object.keys(vote).sort(function (a, b) { return vote[b] - vote[a]; })[0];
  /* "Do chac chan" = ti le phieu. KHONG phai xac suat, va man hinh phai noi ro
     dieu do — day la mot bai hoc chu khong phai con so trang tri. */
  var conf = vote[best] / near.length;
  /* ── Khung nhin XAI: VI SAO Byte chon lop nay ──────────────────────────
     Day la thu "Break Byte" song bang. Khong co no thi tre pha duoc AI ma
     khong biet minh vua pha bang cach nao — tuc mat han phan bai hoc.

     ⚠️⚠️ DO SUC PHAN BIET, KHONG DO DO GIONG. Ban dau toi lay "dac trung nao
        gan lang gieng nhat" — va no NOI DOI, do duoc ngay o phep thu dau:
        moi mau trong bo deu co ti le dai/rong = 1.0, nen dac trung do luon
        "gan nhat" va may khai no la ly do, trong khi no khong phan biet duoc
        gi ca. Mot dac trung HANG SO trong ra la quan trong nhat — dung loai
        loi im lang de day tre mot dieu sai.
        Luat dung: so khoang cach theo TUNG TRUC toi lop THANG voi lop THUA.
        Truc nao co loi the lon nhat cho lop thang, truc do moi la ly do that. */
  var win = near[0].label;
  var lose = null;
  for (var j = 0; j < model.data.length && !lose; j++)
    if (model.data[j].label !== win) lose = model.data[j].label;
  function nearestOf(lab, i) {
    var m = Infinity;
    model.data.forEach(function (s) {
      if (s.label === lab) m = Math.min(m, Math.abs(s.f[i] - f[i]));
    });
    return m;
  }
  var why = FEAT[0], bestEdge = -Infinity;
  if (lose) FEAT.forEach(function (name, i) {
    var edge = nearestOf(lose, i) - nearestOf(win, i);   // >0 = truc nay keo ve lop thang
    if (edge > bestEdge) { bestEdge = edge; why = name; }
  });
  return { label: best, conf: conf, why: why, near: near };
}

module.exports = { train: train, predict: predict, FEAT: FEAT };
