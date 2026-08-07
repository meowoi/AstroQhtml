/* js/quiz-index.js — MUC LUC NGAN HANG CAU HOI + BANG NGUON + BO NAP.

   ⚠️⚠️ FILE NAY SINH RA BANG SCRIPT — DUNG SUA BANG TAY.
        Nguon su that la `js/quiz/<khoa-cau>.js` (mot cau moi file). Them cau =
        them file roi chay:  python scratchpad/split_quiz_bank.py

   VI SAO KHONG CON MOT FILE BANK: do 07/08/2026 — `js/quiz-questions.js` la
   43,6 KB gzip cho 100 cau, tuc 51% duong tai cua quiz.html, ma mot luot chi
   dung 5 cau. Dot 2 (+270 cau) se day bank len ~161 KB gzip [Suy luan]. Nay
   trang tai MUC LUC (nho) roi tai dung 5 file cau — con so nay khong tang khi
   bank lon len toi 1.000 cau.

   BA THU TRONG FILE NAY
     S      bang nguon dung chung. Cau hoi tro vao day bang KHOA (`src: "star"`),
            khong viet URL — 870 cau viet URL thang la ~870 ban sao cua ~40 dia chi.
     G      cac NHOM. Mot nhom = mot THE So Tay (`js/codex-terms.js`), hoac mot
            cau le chua the nao nhan. `t` = topic hien o badge [ CHU DE · CAU n/m ].
     LV     do kho 1/2/3, chi khai cho cau DA co. 35/100 cau chua khai —
            ⚠️ HIEN CHUA AI DOC `lv`. Chu du an chot 07/08/2026: GIU truong nay,
            cho duong "server tinh cap do roi client rut de theo cap do". Muon noi
            day thi quiz.html can doc duoc cap do cua tre, ma trang do CO Y khong
            nap SDK Firebase (233 KB) nen khong co token — phai them mot cache do
            dashboard ghi, dung khuon `astroq-route-gate`. Dung noi lai ma chua lam
            cai cache do; va dung xoa `lv` — de bai Dot 2-5 van yeu cau Gemini khai.

   ⚠️ `pickKeys()` CHONG TRUNG THEO THE, KHONG THEO `term` — sua 07/08/2026.
      Ban cu loc bang `pool[i].term`, nhung `term` la khoa cua CAU (moi cau mot
      khoa rieng: `star`, `star-fusion`), nen phep loc do CHUA BAO GIO chan duoc
      gi: do duoc 100/100 khoa la duy nhat. Y dinh ghi trong chu thich cu ("mot
      luot 5 cau co the hoi Sao choi hai lan") chi thanh that khi loc theo THE.
      Sau Dot 2 no moi that su quan trong: 15 the len ~20 cau/the, khong loc thi
      mot luot 5 cau co the toan la cau ve nhat thuc. */

window.AstroQQuestions = (function () {
  "use strict";

  /* ── BANG NGUON. Chi giu nguon CO CAU DANG DUNG; them nguon moi thi
     them vao file cau roi chay lai script, dung sua o day. */
  var S = {
    aster:                  { name: "NASA Science — Asteroid Facts", url: "https://science.nasa.gov/solar-system/asteroids/facts/" },
    bh:                     { name: "NASA Science — Black Holes", url: "https://science.nasa.gov/universe/black-holes/" },
    comet:                  { name: "NASA Science — Comet Facts", url: "https://science.nasa.gov/solar-system/comets/facts/" },
    cosmos:                 { name: "NASA Science — Cosmic History", url: "https://science.nasa.gov/universe/overview/" },
    dwarf:                  { name: "NASA Science — Pluto & Dwarf Planets", url: "https://science.nasa.gov/dwarf-planets/" },
    exo:                    { name: "NASA Science — Exoplanets", url: "https://science.nasa.gov/exoplanets/" },
    exploratoriumCup:       { name: "Exploratorium — Eclipse in a Cup", url: "https://www.exploratorium.edu/eclipse/snacks/eclipse-in-a-cup" },
    exploratoriumEclipse:   { name: "Exploratorium — What Causes a Solar Eclipse?", url: "https://www.exploratorium.edu/eclipse/what-is-a-solar-eclipse" },
    ganym:                  { name: "NASA Science — Ganymede", url: "https://science.nasa.gov/jupiter/moons/ganymede/" },
    grav:                   { name: "NASA Space Place — What Is Gravity?", url: "https://spaceplace.nasa.gov/what-is-gravity/en/" },
    lcoStarColors:          { name: "Las Cumbres Observatory — Magnitude and Color", url: "https://lco.global/spacebook/distance/magnitude-and-color/" },
    meteor:                 { name: "NASA Science — Meteors & Meteorites", url: "https://science.nasa.gov/solar-system/meteors-meteorites/facts/" },
    moon:                   { name: "NASA Science — Moons", url: "https://science.nasa.gov/solar-system/moons/" },
    nasaEarthFacts:         { name: "NASA Science — Facts About Earth", url: "https://science.nasa.gov/earth/facts/" },
    nasaEclipseGeometry:    { name: "NASA Science — Why Do Eclipses Happen?", url: "https://science.nasa.gov/eclipses/geometry/" },
    nasaEclipseSafety:      { name: "NASA Science — Eclipse Viewing Safety", url: "https://science.nasa.gov/eclipses/safety/" },
    nasaEclipseTypes:       { name: "NASA Science — Types of Solar Eclipses", url: "https://science.nasa.gov/eclipses/types/" },
    nasaEclipsesMain:       { name: "NASA Science — Eclipses Overview", url: "https://science.nasa.gov/eclipses/" },
    nasaGeneralAtmosphere:  { name: "NASA Science — What Is Earth's Atmosphere?", url: "https://www.nasa.gov/general/what-is-earths-atmosphere/" },
    nasaMoonEclipses:       { name: "NASA Science — Eclipses and the Moon", url: "https://science.nasa.gov/moon/eclipses/" },
    nasaSpaceplaceEclipses: { name: "NASA Space Place — Lunar and Solar Eclipses", url: "https://spaceplace.nasa.gov/eclipses/" },
    nasaSpaceplaceMagic:    { name: "NASA Space Place — Explore the Electromagnetic Spectrum", url: "https://spaceplace.nasa.gov/magic-windows/" },
    nasaSpaceplaceMeso:     { name: "NASA Space Place — Mesosphere", url: "https://spaceplace.nasa.gov/mesosphere/" },
    nasaSpaceplaceStrato:   { name: "NASA Space Place — Stratosphere", url: "https://spaceplace.nasa.gov/stratosphere/" },
    nasaSpaceplaceTropo:    { name: "NASA Space Place — Troposphere", url: "https://spaceplace.nasa.gov/troposphere/" },
    nasaStarTypes:          { name: "NASA Science — Star Types", url: "https://science.nasa.gov/universe/stars/types/" },
    nasaSunCorona:          { name: "NASA Space Place — What Is the Sun's Corona?", url: "https://spaceplace.nasa.gov/sun-corona/en/" },
    planet:                 { name: "NASA Science — About the Planets", url: "https://science.nasa.gov/solar-system/planets/" },
    star:                   { name: "NASA Science — Stars", url: "https://science.nasa.gov/universe/stars/" },
    ucarOzoneLayer:         { name: "UCAR — The Ozone Layer", url: "https://scied.ucar.edu/learning-zone/atmosphere/ozone-layer" },
    ucarStratosphere:       { name: "UCAR — The Stratosphere", url: "https://scied.ucar.edu/learning-zone/atmosphere/stratosphere" },
    ucarTroposphere:        { name: "UCAR — The Troposphere", url: "https://scied.ucar.edu/learning-zone/atmosphere/troposphere" }
  };

  /* ── NHOM = MOT THE So Tay. `c` = id the (null = chua the nao nhan),
     `t` = topic, `q` = cac khoa cau (chinh la ten file trong js/quiz/). */
  var G = [
    { c: "term_star",
      t: { vi: "NGÔI SAO",
           en: "STAR" },
      q: ["star", "star-fusion"] },
    { c: "term_planet",
      t: { vi: "HÀNH TINH",
           en: "PLANET" },
      q: ["planet", "planet-count"] },
    { c: "term_dwarf_planet",
      t: { vi: "HÀNH TINH LÙN",
           en: "DWARF PLANET" },
      q: ["dwarf", "dwarf-ceres"] },
    { c: "term_moon",
      t: { vi: "VỆ TINH TỰ NHIÊN",
           en: "NATURAL SATELLITE" },
      q: ["moon", "moon-largest"] },
    { c: "term_asteroid",
      t: { vi: "TIỂU HÀNH TINH",
           en: "ASTEROID" },
      q: ["asteroid-belt", "asteroid-what"] },
    { c: "term_comet",
      t: { vi: "SAO CHỔI",
           en: "COMET" },
      q: ["comet-what", "comet-tail"] },
    { c: "term_meteoroid",
      t: { vi: "THIÊN THẠCH NHỎ",
           en: "METEOROID" },
      q: ["meteoroid", "meteoroid-chain"] },
    { c: "term_meteor",
      t: { vi: "SAO BĂNG",
           en: "METEOR" },
      q: ["meteor", "meteor-fireball"] },
    { c: "term_meteorite",
      t: { vi: "THIÊN THẠCH",
           en: "METEORITE" },
      q: ["meteorite", "meteorite-survive"] },
    { c: "term_exoplanet",
      t: { vi: "NGOẠI HÀNH TINH",
           en: "EXOPLANET" },
      q: ["exoplanet", "exoplanet-transit"] },
    { c: "term_black_hole",
      t: { vi: "LỖ ĐEN",
           en: "BLACK HOLE" },
      q: ["black-hole", "black-hole-light"] },
    { c: "term_gravity",
      t: { vi: "LỰC HẤP DẪN",
           en: "GRAVITY" },
      q: ["gravity", "gravity-distance"] },
    { c: "term_nebula",
      t: { vi: "TINH VÂN",
           en: "NEBULA" },
      q: ["nebula", "nebula-gas"] },
    { c: "term_supernova",
      t: { vi: "SIÊU TÂN TINH",
           en: "SUPERNOVA" },
      q: ["supernova", "supernova-elements"] },
    { c: "term_cmb",
      t: { vi: "BỨC XẠ NỀN VŨ TRỤ",
           en: "COSMIC MICROWAVE BACKGROUND" },
      q: ["cmb", "cmb-when"] },
    { c: null,
      t: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
      q: ["algorithm"] },
    { c: null,
      t: { vi: "VÒNG LẶP",
           en: "LOOPS" },
      q: ["loop"] },
    { c: null,
      t: { vi: "ĐIỀU KIỆN",
           en: "CONDITIONS" },
      q: ["condition"] },
    { c: null,
      t: { vi: "CẢM BIẾN",
           en: "SENSORS" },
      q: ["sensor"] },
    { c: null,
      t: { vi: "TRÌNH TỰ",
           en: "SEQUENCING" },
      q: ["sequence"] },
    { c: "term_earth_atmosphere",
      t: { vi: "Trái Đất & Khí Quyển",
           en: "Earth & Atmosphere" },
      q: ["atmo-comp-nitrogen", "atmo-comp-ratio", "atmo-tropo-lowest", "atmo-tropo-weather", "atmo-tropo-mass", "atmo-tropo-watervapor", "atmo-tropo-density", "atmo-strato-ozone", "atmo-strato-uv", "atmo-strato-location", "atmo-meso-location", "atmo-meso-meteors", "atmo-meso-friction", "atmo-thermo-location", "atmo-thermo-iss", "atmo-thermo-aurora", "atmo-exo-outermost", "atmo-exo-end", "atmo-shield-meteoroids", "atmo-shield-radiation"] },
    { c: "term_star_colour",
      t: { vi: "Thiên Văn",
           en: "Astronomy" },
      q: ["star-color-temp-determine", "star-blue-hotter-red", "star-color-spectrum-order", "star-surface-temp-color", "star-red-dwarf-coolest", "star-coolest-star-temperature", "star-sun-age-main-sequence", "star-sirius-brightest", "star-proxima-red-dwarf", "star-closest-main-sequence", "star-arcturus-red-giant", "star-betelgeuse-red-giant", "star-red-giant-expansion", "star-properties-range", "star-red-dwarf-faint", "star-red-dwarf-longevity", "star-prism-wavelengths", "star-visible-wavelength-range"] },
    { c: "term_solar_eclipse",
      t: { vi: "Thiên Văn",
           en: "Astronomy" },
      q: ["eclipse-definition-moon-between", "eclipse-annular-farthest-ring", "eclipse-partial-crescent-shape", "eclipse-hybrid-annular-total", "eclipse-shadow-umbra-penumbra", "eclipse-umbra-total-blocked", "eclipse-penumbra-partially-blocked", "eclipse-corona-outermost-atmosphere", "eclipse-corona-visible-totality", "eclipse-safety-totality-viewing", "eclipse-safety-glasses-reappear", "eclipse-coincidence-size-distance-ratio", "eclipse-moon-shadows-umbra-penumbra", "eclipse-phase-new-moon"] },
    { c: "term_lunar_eclipse",
      t: { vi: "Thiên Văn",
           en: "Astronomy" },
      q: ["lunar-definition-earth-shadow", "lunar-phase-full-moon", "lunar-earth-between-sun-moon", "lunar-umbra-inner-shadow", "lunar-rayleigh-scattering-red-light", "lunar-atmosphere-dust-redder", "lunar-partial-imperfect-alignment", "lunar-penumbral-faint-outer-shadow", "lunar-red-filtered-atmosphere", "lunar-sunrises-sunsets-projected", "lunar-difference-name-darker", "lunar-shadow-huge-earth", "lunar-night-side-visibility"] }
  ];

  /* ── DO KHO. Chi khai cho cau DA co `lv`. Xem canh bao dau file. */
  var LV = {
    "atmo-comp-nitrogen": 1, "atmo-comp-ratio": 1, "atmo-tropo-lowest": 1,
    "atmo-tropo-weather": 1, "atmo-tropo-mass": 2, "atmo-tropo-watervapor": 2,
    "atmo-tropo-density": 3, "atmo-strato-ozone": 1, "atmo-strato-uv": 2,
    "atmo-strato-location": 3, "atmo-meso-location": 2, "atmo-meso-meteors": 1,
    "atmo-meso-friction": 2, "atmo-thermo-location": 2, "atmo-thermo-iss": 2,
    "atmo-thermo-aurora": 3, "atmo-exo-outermost": 1, "atmo-exo-end": 3,
    "atmo-shield-meteoroids": 2, "atmo-shield-radiation": 3, "star-color-temp-determine": 1,
    "star-blue-hotter-red": 1, "star-color-spectrum-order": 1, "star-surface-temp-color": 3,
    "star-red-dwarf-coolest": 1, "star-coolest-star-temperature": 3,
    "star-sun-age-main-sequence": 1, "star-sirius-brightest": 1, "star-proxima-red-dwarf": 1,
    "star-closest-main-sequence": 2, "star-arcturus-red-giant": 2,
    "star-betelgeuse-red-giant": 2, "star-red-giant-expansion": 2, "star-properties-range": 2,
    "star-red-dwarf-faint": 3, "star-red-dwarf-longevity": 3, "star-prism-wavelengths": 2,
    "star-visible-wavelength-range": 2, "eclipse-definition-moon-between": 1,
    "eclipse-annular-farthest-ring": 1, "eclipse-partial-crescent-shape": 1,
    "eclipse-hybrid-annular-total": 2, "eclipse-shadow-umbra-penumbra": 1,
    "eclipse-umbra-total-blocked": 2, "eclipse-penumbra-partially-blocked": 2,
    "eclipse-corona-outermost-atmosphere": 1, "eclipse-corona-visible-totality": 2,
    "eclipse-safety-totality-viewing": 2, "eclipse-safety-glasses-reappear": 2,
    "eclipse-coincidence-size-distance-ratio": 3, "eclipse-moon-shadows-umbra-penumbra": 3,
    "eclipse-phase-new-moon": 3, "lunar-definition-earth-shadow": 1, "lunar-phase-full-moon": 1,
    "lunar-earth-between-sun-moon": 1, "lunar-umbra-inner-shadow": 1,
    "lunar-rayleigh-scattering-red-light": 2, "lunar-atmosphere-dust-redder": 2,
    "lunar-partial-imperfect-alignment": 2, "lunar-penumbral-faint-outer-shadow": 2,
    "lunar-red-filtered-atmosphere": 2, "lunar-sunrises-sunsets-projected": 3,
    "lunar-difference-name-darker": 3, "lunar-shadow-huge-earth": 3,
    "lunar-night-side-visibility": 3
  };

  /* Tron mot BAN SAO — tron tai cho thi luot sau thu tu G/LV da bi doi, va moi
     phep kiem dua vao thu tu khai bao se hong mot cach kho hieu. */
  function shuffled(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var r = Math.floor(Math.random() * (i + 1));
      var t = a[i]; a[i] = a[r]; a[r] = t;
    }
    return a;
  }

  /* Nhom cua mot khoa cau (de gan `topic` sau khi tai). */
  var GOF = {};
  G.forEach(function (g) { g.q.forEach(function (k) { GOF[k] = g; }); });

  function terms() { return Object.keys(GOF); }
  function has(k) { return !!GOF[k]; }

  /* Chon n khoa cho mot luot. CHONG TRUNG THEO THE (xem canh bao dau file):
     rut nhom truoc, moi nhom mot cau. Het nhom moi lay bu cau thu hai. */
  function pickKeys(n) {
    var gs = shuffled(G), out = [], spare = [], i;
    for (i = 0; i < gs.length && out.length < n; i++) {
      var ks = shuffled(gs[i].q);
      out.push(ks[0]);
      for (var j = 1; j < ks.length; j++) spare.push(ks[j]);
    }
    spare = shuffled(spare);
    for (i = 0; out.length < n && i < spare.length; i++) out.push(spare[i]);
    return out.slice(0, n);
  }

  /* Loc khoa theo danh sach (duong vao `quiz.html?terms=a,b,c` tu bai doc). */
  function keysOfTerms(list) {
    if (!list || !list.length) return [];
    return list.filter(has);
  }

  /* Bu cho du n khoa, khong trung khoa da co va uu tien the khac. */
  function fill(keys, n) {
    var have = {}, out = keys.slice();
    out.forEach(function (k) { have[k] = 1; });
    var usedG = {};
    out.forEach(function (k) { if (GOF[k]) usedG[GOF[k].c || k] = 1; });
    var pool = shuffled(G), i, j;
    for (i = 0; i < pool.length && out.length < n; i++) {
      var g = pool[i], gid = g.c || g.q[0];
      if (usedG[gid]) continue;
      var ks = shuffled(g.q);
      for (j = 0; j < ks.length; j++) {
        if (!have[ks[j]]) { have[ks[j]] = 1; usedG[gid] = 1; out.push(ks[j]); break; }
      }
    }
    for (i = 0; i < pool.length && out.length < n; i++) {   /* het the moi trung the */
      var kk = shuffled(pool[i].q);
      for (j = 0; j < kk.length && out.length < n; j++) {
        if (!have[kk[j]]) { have[kk[j]] = 1; out.push(kk[j]); }
      }
    }
    return out.slice(0, n);
  }

  /* Gan lai phan khai o MUC LUC (topic, lv) va doi `src` tu KHOA sang object.
     Nho vay quiz.html nhan duoc cau co hinh dang y NHU bank mot-file cu. */
  function hydrate(k, raw) {
    if (!raw) return null;
    var q = {}, p;
    for (p in raw) if (Object.prototype.hasOwnProperty.call(raw, p)) q[p] = raw[p];
    q.term = k;
    var g = GOF[k];
    if (g && !q.topic) q.topic = g.t;
    if (LV[k] != null && q.lv == null) q.lv = LV[k];
    if (typeof q.src === "string") q.src = S[q.src] || null;
    return q;
  }

  /* Tai dung nhung cau duoc yeu cau. MOT FILE HONG KHONG DUOC GIET CA LUOT:
     `import()` co `.catch` rieng tung file, cau hong tra `null` roi bi loc ra —
     quiz.html se thay it cau hon chu khong thay mot trang trang. */
  function load(keys) {
    return Promise.all(keys.map(function (k) {
      return import("./quiz/" + k + ".js")
        .then(function (m) { return hydrate(k, m["default"]); })
        .catch(function (e) {
          if (window.console) console.warn("[quiz] khong tai duoc cau " + k, e);
          return null;
        });
    })).then(function (a) {
      return a.filter(function (x) { return !!x; });
    });
  }

  /* Mot luot binh thuong: rut n khoa roi tai. Neu co file hong thi bu them
     mot lan cho du n — de tre khong bi mot luot ngan hon vi loi mang. */
  function round(n) {
    var keys = pickKeys(n);
    return load(keys).then(function (qs) {
      if (qs.length >= n) return qs;
      var more = fill(qs.map(function (q) { return q.term; }), n)
                   .filter(function (k) {
                     return keys.indexOf(k) < 0;
                   });
      if (!more.length) return qs;
      return load(more).then(function (extra) {
        return qs.concat(extra).slice(0, n);
      });
    });
  }

  /* Duong vao tu bai doc: uu tien dung cac khoa duoc yeu cau, bu cho du n. */
  function byTerms(list, n) {
    var keys = shuffled(keysOfTerms(list)).slice(0, n);
    if (!keys.length) return Promise.resolve([]);
    if (keys.length < n) keys = fill(keys, n);
    return load(keys);
  }

  return {
    S: S, G: G, LV: LV,
    terms: terms, has: has, groupOf: function (k) { return GOF[k] || null; },
    shuffled: shuffled, pickKeys: pickKeys, keysOfTerms: keysOfTerms, fill: fill,
    load: load, round: round, byTerms: byTerms
  };
})();
