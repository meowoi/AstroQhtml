/* js/quiz-sources.js — BANG NGUON CUA NGAN HANG CAU HOI. Nguon su that, SUA BANG TAY.

   ⚠️⚠️ VI SAO TON TAI FILE NAY (tach 09/08/2026):
     Truoc do bang `S` chi nam trong `js/quiz-index.js` — mot file SINH RA — va
     `split_quiz_bank.py` lay lai TEN KHOA bang cach doc `js/quiz-questions.js`.
     Nhung file mot-bank do da bi XOA ngay 07/08/2026 khi chia ngan hang, nen tu
     hom ay bo sinh muc luc **NEM FileNotFoundError va khong con chay duoc**, tuc
     KHONG AI THEM DUOC MOT CAU HOI NAO. Loi im lang suot 2 ngay: khong ai chay
     script vi khong ai them cau.
     Nay ban nguon la file NAY, va muc luc chi NHUNG lai nhung khoa co cau dung.

   ⚠️ `src` trong `js/quiz/<khoa>.js` la KHOA tro vao day, KHONG phai URL — 870 cau
      viet URL thang la ~870 ban sao cua ~40 dia chi, va ngay NASA doi mot duong dan
      thi phai sua hang tram file.
   ⚠️ File nay KHONG duoc trang nao nap: bo sinh doc no roi nhung bang S vao muc luc.
   ⚠️ Moi URL phai tra 200 o ngay them. Hai khoa KHONG duoc tro cung mot URL (bo sinh
      suy nguoc khoa tu URL o che do --from-old nen se dung lai).
*/
window.AstroQQuizSources = {
  nasaWhatIsAi:           { name: "NASA — What is AI? (Grades 5-8)", url: "https://www.nasa.gov/learning-resources/what-is-ai-grades-5-8/" },
  aiHubble:               { name: "NASA Science — AI and Hubble Science", url: "https://science.nasa.gov/mission/hubble/science/ai-hubble-science/" },
  mitAlgorithms:          { name: "MIT Media Lab — AI + Ethics for Middle School", url: "https://www.media.mit.edu/projects/ai-ethics-for-middle-school/overview/" },
  astrobee:               { name: "NASA — Astrobee", url: "https://www.nasa.gov/astrobee/" },
  aster:          { name: "NASA Science — Asteroid Facts", url: "https://science.nasa.gov/solar-system/asteroids/facts/" },
  bh:           { name: "NASA Science — Black Holes", url: "https://science.nasa.gov/universe/black-holes/" },
  comet:          { name: "NASA Science — Comet Facts", url: "https://science.nasa.gov/solar-system/comets/facts/" },
  cosmos:         { name: "NASA Science — Cosmic History", url: "https://science.nasa.gov/universe/overview/" },
  dwarf:          { name: "NASA Science — Pluto & Dwarf Planets", url: "https://science.nasa.gov/dwarf-planets/" },
  exo:          { name: "NASA Science — Exoplanets", url: "https://science.nasa.gov/exoplanets/" },
  exploratoriumCup:     { name: "Exploratorium — Eclipse in a Cup", url: "https://www.exploratorium.edu/eclipse/snacks/eclipse-in-a-cup" },
  exploratoriumEclipse:   { name: "Exploratorium — What Causes a Solar Eclipse?", url: "https://www.exploratorium.edu/eclipse/what-is-a-solar-eclipse" },
  ganym:          { name: "NASA Science — Ganymede", url: "https://science.nasa.gov/jupiter/moons/ganymede/" },
  grav:           { name: "NASA Space Place — What Is Gravity?", url: "https://spaceplace.nasa.gov/what-is-gravity/en/" },
  lcoStarColors:      { name: "Las Cumbres Observatory — Magnitude and Color", url: "https://lco.global/spacebook/distance/magnitude-and-color/" },
  meteor:         { name: "NASA Science — Meteors & Meteorites", url: "https://science.nasa.gov/solar-system/meteors-meteorites/facts/" },
  moon:           { name: "NASA Science — Moons", url: "https://science.nasa.gov/solar-system/moons/" },
  nasaEarthFacts:     { name: "NASA Science — Facts About Earth", url: "https://science.nasa.gov/earth/facts/" },
  nasaEclipseGeometry:  { name: "NASA Science — Why Do Eclipses Happen?", url: "https://science.nasa.gov/eclipses/geometry/" },
  nasaEclipseSafety:    { name: "NASA Science — Eclipse Viewing Safety", url: "https://science.nasa.gov/eclipses/safety/" },
  nasaEclipseTypes:     { name: "NASA Science — Types of Solar Eclipses", url: "https://science.nasa.gov/eclipses/types/" },
  nasaEclipsesMain:     { name: "NASA Science — Eclipses Overview", url: "https://science.nasa.gov/eclipses/" },
  nasaGeneralAtmosphere:  { name: "NASA Science — What Is Earth's Atmosphere?", url: "https://www.nasa.gov/general/what-is-earths-atmosphere/" },
  nasaMoonEclipses:     { name: "NASA Science — Eclipses and the Moon", url: "https://science.nasa.gov/moon/eclipses/" },
  nasaSpaceplaceEclipses: { name: "NASA Space Place — Lunar and Solar Eclipses", url: "https://spaceplace.nasa.gov/eclipses/" },
  nasaSpaceplaceMagic:  { name: "NASA Space Place — Explore the Electromagnetic Spectrum", url: "https://spaceplace.nasa.gov/magic-windows/" },
  nasaSpaceplaceMeso:   { name: "NASA Space Place — Mesosphere", url: "https://spaceplace.nasa.gov/mesosphere/" },
  nasaSpaceplaceStrato:   { name: "NASA Space Place — Stratosphere", url: "https://spaceplace.nasa.gov/stratosphere/" },
  nasaSpaceplaceTropo:  { name: "NASA Space Place — Troposphere", url: "https://spaceplace.nasa.gov/troposphere/" },
  nasaStarTypes:      { name: "NASA Science — Star Types", url: "https://science.nasa.gov/universe/stars/types/" },
  nasaSunCorona:      { name: "NASA Space Place — What Is the Sun's Corona?", url: "https://spaceplace.nasa.gov/sun-corona/en/" },
  planet:         { name: "NASA Science — About the Planets", url: "https://science.nasa.gov/solar-system/planets/" },
  star:           { name: "NASA Science — Stars", url: "https://science.nasa.gov/universe/stars/" },
  ucarOzoneLayer:     { name: "UCAR — The Ozone Layer", url: "https://scied.ucar.edu/learning-zone/atmosphere/ozone-layer" },
  ucarStratosphere:     { name: "UCAR — The Stratosphere", url: "https://scied.ucar.edu/learning-zone/atmosphere/stratosphere" },
  ucarTroposphere:    { name: "UCAR — The Troposphere", url: "https://scied.ucar.edu/learning-zone/atmosphere/troposphere" }
};
