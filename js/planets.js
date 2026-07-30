/* ============================================================
   planets.js — 8 hành tinh của Hệ Mặt Trời, tên song ngữ + màu.

   `id` PHẢI khớp `PLANET_DATA[].id` trong explorer.html, vì đó là chỗ ghi nhận
   "đã ghé hành tinh nào" (`AstroQProgress.planet(id)`) và cũng là chỗ hai trang
   profile.html / achievements.html đọc ra để vẽ hành trình khám phá. Lệch id là
   ghé một hành tinh mà hồ sơ không thấy.

   Dùng chung bởi profile.html và achievements.html:
     <script src="js/planets.js"></script>
     AstroQPlanets.all()  ·  AstroQPlanets.name(id, lang)
   ============================================================ */
(function (global) {
  "use strict";

  var PLANETS = [
    { id:"mercury", vi:"Sao Thuỷ", en:"Mercury", c:"#b9b0a3", c2:"#6e6559" },
    { id:"venus",   vi:"Sao Kim",  en:"Venus",   c:"#f0cf8e", c2:"#b9884a" },
    { id:"earth",   vi:"Trái Đất", en:"Earth",   c:"#2f74d6", c2:"#3f9d5a" },
    { id:"mars",    vi:"Sao Hoả",  en:"Mars",    c:"#d6603a", c2:"#7a3320" },
    { id:"jupiter", vi:"Sao Mộc",  en:"Jupiter", c:"#e8d0a8", c2:"#b07a4e" },
    { id:"saturn",  vi:"Sao Thổ",  en:"Saturn",  c:"#ece0b0", c2:"#c9a86a" },
    { id:"uranus",  vi:"Sao Thiên Vương", en:"Uranus",  c:"#6fe0e0", c2:"#3fb6c9" },
    { id:"neptune", vi:"Sao Hải Vương",   en:"Neptune", c:"#3b6fe0", c2:"#2340a8" }
  ];

  global.AstroQPlanets = {
    all: function () { return PLANETS.slice(); },
    count: PLANETS.length,
    name: function (id, lang) {
      for (var i = 0; i < PLANETS.length; i++) {
        if (PLANETS[i].id === id) return lang === "en" ? PLANETS[i].en : PLANETS[i].vi;
      }
      return id;   // hành tinh lạ (dữ liệu cũ) → hiện chính id, không vỡ trang
    }
  };
})(window);
