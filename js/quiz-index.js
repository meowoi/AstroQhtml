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
     LV     do kho 1/2/3. 0/126 cau chua khai.
            DUOC DOC THAT TU 19/08/2026 ("vai ②" — do kho tu dieu chinh):
              server  Services/Adapt.cs tinh `progress.quizLv` tu ti le tra loi dung
                      (KHONG tu `xp`/`level`: `level` do THOI GIAN CHOI).
              cau noi js/progress.js ghi cache `astroq-quiz-lv` co dong dau uid —
                      `quiz.html` CO Y khong nap SDK Firebase nen khong co token,
                      dung khuon `astroq-route-gate`/`astroq-training`.
              dung   `pickKeys(n, lv)` duoi day.
            ⚠️ `lv` NAM O FILE CAU (`js/quiz/*.js`) moi la nguon su that; bang LV
               nay SINH RA. Dung go tay vao js/quiz-index.js.
            ⚠️ Cap do doi CAU NAO TRONG THE, KHONG doi THE NAO duoc vao — xem
               chu thich `pickKeys`.

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
    aiHubble:               { name: "NASA Science — AI and Hubble Science", url: "https://science.nasa.gov/mission/hubble/science/ai-hubble-science/" },
    aster:                  { name: "NASA Science — Asteroid Facts", url: "https://science.nasa.gov/solar-system/asteroids/facts/" },
    astrobee:               { name: "NASA — Astrobee", url: "https://www.nasa.gov/astrobee/" },
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
    mitAlgorithms:          { name: "MIT Media Lab — AI + Ethics for Middle School", url: "https://www.media.mit.edu/projects/ai-ethics-for-middle-school/overview/" },
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
    nasaWhatIsAi:           { name: "NASA — What is AI? (Grades 5-8)", url: "https://www.nasa.gov/learning-resources/what-is-ai-grades-5-8/" },
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
      q: ["star", "star-fusion", "star-mass-life"] },
    { c: "term_planet",
      t: { vi: "HÀNH TINH",
           en: "PLANET" },
      q: ["planet", "planet-count", "planet-ice-giants"] },
    { c: "term_dwarf_planet",
      t: { vi: "HÀNH TINH LÙN",
           en: "DWARF PLANET" },
      q: ["dwarf", "dwarf-ceres", "dwarf-pluto"] },
    { c: "term_moon",
      t: { vi: "VỆ TINH TỰ NHIÊN",
           en: "NATURAL SATELLITE" },
      q: ["moon", "moon-largest", "moon-most-not-planets"] },
    { c: "term_asteroid",
      t: { vi: "TIỂU HÀNH TINH",
           en: "ASTEROID" },
      q: ["asteroid-belt", "asteroid-what", "asteroid-jupiter-stopped"] },
    { c: "term_comet",
      t: { vi: "SAO CHỔI",
           en: "COMET" },
      q: ["comet-what", "comet-tail", "comet-two-tails"] },
    { c: "term_meteoroid",
      t: { vi: "THIÊN THẠCH NHỎ",
           en: "METEOROID" },
      q: ["meteoroid", "meteoroid-chain", "meteoroid-daily-mass"] },
    { c: "term_meteor",
      t: { vi: "SAO BĂNG",
           en: "METEOR" },
      q: ["meteor", "meteor-fireball", "meteor-where"] },
    { c: "term_meteorite",
      t: { vi: "THIÊN THẠCH",
           en: "METEORITE" },
      q: ["meteorite", "meteorite-survive", "meteorite-name"] },
    { c: "term_exoplanet",
      t: { vi: "NGOẠI HÀNH TINH",
           en: "EXOPLANET" },
      q: ["exoplanet", "exoplanet-transit", "exo-rogue"] },
    { c: "term_black_hole",
      t: { vi: "LỖ ĐEN",
           en: "BLACK HOLE" },
      q: ["black-hole", "black-hole-light", "bh-horizon-boundary", "bh-not-hole"] },
    { c: "term_gravity",
      t: { vi: "LỰC HẤP DẪN",
           en: "GRAVITY" },
      q: ["gravity", "gravity-distance", "grav-two-rules"] },
    { c: "term_nebula",
      t: { vi: "TINH VÂN",
           en: "NEBULA" },
      q: ["nebula", "nebula-gas", "nebula-planetary"] },
    { c: "term_supernova",
      t: { vi: "SIÊU TÂN TINH",
           en: "SUPERNOVA" },
      q: ["supernova", "supernova-elements", "supernova-what"] },
    { c: "term_cmb",
      t: { vi: "BỨC XẠ NỀN VŨ TRỤ",
           en: "COSMIC MICROWAVE BACKGROUND" },
      q: ["cmb", "cmb-when", "cmb-oldest-light"] },
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
      q: ["lunar-definition-earth-shadow", "lunar-phase-full-moon", "lunar-earth-between-sun-moon", "lunar-umbra-inner-shadow", "lunar-rayleigh-scattering-red-light", "lunar-atmosphere-dust-redder", "lunar-partial-imperfect-alignment", "lunar-penumbral-faint-outer-shadow", "lunar-red-filtered-atmosphere", "lunar-sunrises-sunsets-projected", "lunar-difference-name-darker", "lunar-shadow-huge-earth", "lunar-night-side-visibility"] },
    { c: "term_ai",
      t: { vi: "TRÍ TUỆ NHÂN TẠO",
           en: "ARTIFICIAL INTELLIGENCE" },
      q: ["ai-what-is", "ai-can-do-what", "ai-why-fast"] },
    { c: "term_machine_learning",
      t: { vi: "HỌC MÁY",
           en: "MACHINE LEARNING" },
      q: ["ml-learns-from-data", "ml-humans-still-check", "ml-trained-by-hubble"] },
    { c: "term_algorithm",
      t: { vi: "THUẬT TOÁN",
           en: "ALGORITHMS" },
      q: ["algorithm-is-an-opinion", "algorithm", "sequence", "loop", "condition"] },
    { c: "term_sensor",
      t: { vi: "CẢM BIẾN",
           en: "SENSORS" },
      q: ["sensor", "sensor-robot-sees", "sensor-why-autonomous", "sensor-fans-move"] }
  ];

  /* ── DO KHO. Chi khai cho cau DA co `lv`. Xem canh bao dau file. */
  var LV = {
    "ai-can-do-what": 2, "ai-what-is": 1, "ai-why-fast": 3, "algorithm": 2,
    "algorithm-is-an-opinion": 3, "asteroid-belt": 2, "asteroid-jupiter-stopped": 3,
    "asteroid-what": 1, "atmo-comp-nitrogen": 1, "atmo-comp-ratio": 1, "atmo-exo-end": 3,
    "atmo-exo-outermost": 1, "atmo-meso-friction": 2, "atmo-meso-location": 2,
    "atmo-meso-meteors": 1, "atmo-shield-meteoroids": 2, "atmo-shield-radiation": 3,
    "atmo-strato-location": 3, "atmo-strato-ozone": 1, "atmo-strato-uv": 2,
    "atmo-thermo-aurora": 3, "atmo-thermo-iss": 2, "atmo-thermo-location": 2,
    "atmo-tropo-density": 3, "atmo-tropo-lowest": 1, "atmo-tropo-mass": 2,
    "atmo-tropo-watervapor": 2, "atmo-tropo-weather": 1, "bh-horizon-boundary": 3,
    "bh-not-hole": 1, "black-hole": 2, "black-hole-light": 2, "cmb": 1, "cmb-oldest-light": 2,
    "cmb-when": 3, "comet-tail": 3, "comet-two-tails": 2, "comet-what": 1, "condition": 1,
    "dwarf": 3, "dwarf-ceres": 2, "dwarf-pluto": 1, "eclipse-annular-farthest-ring": 1,
    "eclipse-coincidence-size-distance-ratio": 3, "eclipse-corona-outermost-atmosphere": 1,
    "eclipse-corona-visible-totality": 2, "eclipse-definition-moon-between": 1,
    "eclipse-hybrid-annular-total": 2, "eclipse-moon-shadows-umbra-penumbra": 3,
    "eclipse-partial-crescent-shape": 1, "eclipse-penumbra-partially-blocked": 2,
    "eclipse-phase-new-moon": 3, "eclipse-safety-glasses-reappear": 2,
    "eclipse-safety-totality-viewing": 2, "eclipse-shadow-umbra-penumbra": 1,
    "eclipse-umbra-total-blocked": 2, "exo-rogue": 3, "exoplanet": 1, "exoplanet-transit": 2,
    "grav-two-rules": 3, "gravity": 1, "gravity-distance": 2, "loop": 2,
    "lunar-atmosphere-dust-redder": 2, "lunar-definition-earth-shadow": 1,
    "lunar-difference-name-darker": 3, "lunar-earth-between-sun-moon": 1,
    "lunar-night-side-visibility": 3, "lunar-partial-imperfect-alignment": 2,
    "lunar-penumbral-faint-outer-shadow": 2, "lunar-phase-full-moon": 1,
    "lunar-rayleigh-scattering-red-light": 2, "lunar-red-filtered-atmosphere": 2,
    "lunar-shadow-huge-earth": 3, "lunar-sunrises-sunsets-projected": 3,
    "lunar-umbra-inner-shadow": 1, "meteor": 2, "meteor-fireball": 3, "meteor-where": 1,
    "meteorite": 2, "meteorite-name": 1, "meteorite-survive": 3, "meteoroid": 1,
    "meteoroid-chain": 3, "meteoroid-daily-mass": 2, "ml-humans-still-check": 3,
    "ml-learns-from-data": 2, "ml-trained-by-hubble": 1, "moon": 1, "moon-largest": 2,
    "moon-most-not-planets": 3, "nebula": 1, "nebula-gas": 3, "nebula-planetary": 2,
    "planet": 3, "planet-count": 1, "planet-ice-giants": 2, "sensor": 1, "sensor-fans-move": 2,
    "sensor-robot-sees": 1, "sensor-why-autonomous": 3, "sequence": 1, "star": 1,
    "star-arcturus-red-giant": 2, "star-betelgeuse-red-giant": 2, "star-blue-hotter-red": 1,
    "star-closest-main-sequence": 2, "star-color-spectrum-order": 1,
    "star-color-temp-determine": 1, "star-coolest-star-temperature": 3, "star-fusion": 2,
    "star-mass-life": 3, "star-prism-wavelengths": 2, "star-properties-range": 2,
    "star-proxima-red-dwarf": 1, "star-red-dwarf-coolest": 1, "star-red-dwarf-faint": 3,
    "star-red-dwarf-longevity": 3, "star-red-giant-expansion": 2, "star-sirius-brightest": 1,
    "star-sun-age-main-sequence": 1, "star-surface-temp-color": 3,
    "star-visible-wavelength-range": 2, "supernova": 2, "supernova-elements": 3,
    "supernova-what": 1
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

  /* Sap mot danh sach khoa theo KHOANG CACH den cap `lv`, tron trong cung khoang
     cach. Cau chua khai `lv` xuong cuoi (khoang cach 9) chu khong bi loai — loai
     thi mot cau moi chua kip khai do kho se im lang mat khoi moi luot.

     ⚠️ DAY LA DUONG LUI BAT BUOC, KHONG PHAI PHONG XA. Do duoc tren bank
        19/08/2026: `term_black_hole` co CA HAI cau o cap 2, `term_meteor` va
        `term_meteorite` la {2,3}. Loc thang `lv === 1` thi ba the nay bien mat
        khoi moi luot cua tre moi — do kho tu dieu chinh lai di THU HEP kien thuc.
        Nen chi sap thu tu, khong bao gio loai. */
  function nearest(ks, lv) {
    var byd = {}, ds = [], out = [], i;
    for (i = 0; i < ks.length; i++) {
      var d = (LV[ks[i]] == null) ? 9 : Math.abs(LV[ks[i]] - lv);
      if (!byd[d]) { byd[d] = []; ds.push(d); }
      byd[d].push(ks[i]);
    }
    ds.sort(function (a, b) { return a - b; });
    for (i = 0; i < ds.length; i++) out = out.concat(shuffled(byd[ds[i]]));
    return out;
  }

  /* Chon n khoa cho mot luot. CHONG TRUNG THEO THE (xem canh bao dau file):
     rut nhom truoc, moi nhom mot cau. Het nhom moi lay bu cau thu hai.

     `lv` (1..3, bo trong = khong quan tam) la CAP DO SERVER TINH cho tre —
     Services/Adapt.cs. No quyet dinh CHON CAU NAO TRONG MOI THE, khong quyet dinh
     the nao duoc vao: moi the vao mot cau nhu cu, chi la cau gan cap `lv` nhat.
     Nho vay so the moi luot khong doi theo cap do, va khong the co cap nao ra
     luot rong (`check_quiz_split.py` canh dieu nay). */
  function pickKeys(n, lv) {
    var gs = shuffled(G), out = [], spare = [], i;
    for (i = 0; i < gs.length && out.length < n; i++) {
      var ks = lv ? nearest(gs[i].q, lv) : shuffled(gs[i].q);
      out.push(ks[0]);
      for (var j = 1; j < ks.length; j++) spare.push(ks[j]);
    }
    spare = lv ? nearest(spare, lv) : shuffled(spare);
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
  function round(n, lv) {
    var keys = pickKeys(n, lv);
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
    nearest: nearest,   /* xuat de check_quiz_split.py do duoc luat chon theo cap */
    load: load, round: round, byTerms: byTerms
  };
})();
