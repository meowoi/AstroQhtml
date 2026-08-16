/* ============================================================
   specimens.js — TÊN + PHÂN LOẠI + LỜI LINH VẬT + FUN FACT của mẫu vật, song ngữ.

   PHÂN CÔNG RÕ RÀNG, đọc trước khi thêm mẫu vật mới (giống js/badges.js):
     · SERVER (AstroqSV/Services/Specimens.cs) giữ **điều kiện mở khoá**
       (`metric`, `goal`), nhóm, độ hiếm, và là nơi DUY NHẤT quyết mẫu nào đã
       thu thập. Không có route "thu thập mẫu vật" — trạng thái SUY RA từ bộ đếm
       tiến độ, nên gọi API kiểu nào cũng không thêm được mẫu.
     · FILE NÀY chỉ giữ phần **hiển thị**: tên, phân loại khoa học, emoji, lời
       thoại linh vật, fun fact, link nguồn.

   THÊM MẪU VẬT MỚI: thêm dòng vào `Specimens.All` ở server, rồi thêm khoá cùng id
   vào đây. Thiếu ở đây thì trang vẫn chạy và hiện chính id — không vỡ.

   ⚠️ NỘI DUNG KHOA HỌC CHƯA QUA RÀ SOÁT CHUYÊN MÔN. Các câu `fact` được viết ở
   dạng định tính (tránh con số cụ thể) và mọi URL trong `src` đã kiểm trả 200
   ngày 29/07/2026, nhưng **cần giáo viên rà lại trước khi phát hành**, đúng như
   ghi chú đã dùng cho learningdata/.

     <script src="js/specimens.js"></script>
     AstroQSpecimens.name("amazon-leaf", "vi")   → "Lá Cây Rừng Amazon"
   ============================================================ */
(function (global) {
  "use strict";

  /* ic = emoji hiện trong khoang ngủ đông · cls = phân loại khoa học
     m  = { who:"comet"|"byte", vi, en } lời linh vật đọc trong màn soi chi tiết
     f  = fun fact · src = { label, url } nguồn tham chiếu (URL đã kiểm 200) */
  var S = {
    /* ───────────── 🌊 Thuỷ quyển ───────────── */
    "ancient-seawater": {
      ic: "💧", cls: "Aqua marina · dung dịch muối khoáng",
      vi: { n: "Nước Biển Cổ Đại" }, en: { n: "Ancient Seawater" },
      m: { who: "comet",
           vi: "Tớ hút mẫu này ở vùng biển sâu, chỗ ánh nắng gần như không xuống tới! Lắc nhẹ thôi nhé — muối khoáng bên trong vẫn đang lơ lửng đó.",
           en: "I siphoned this from deep water, where sunlight barely reaches! Shake it gently — the minerals inside are still floating." },
      f: { vi: "Nước biển mặn vì mưa và sông suối mang muối khoáng từ đá trên đất liền ra biển, tích tụ suốt hàng triệu năm.",
           en: "Seawater is salty because rain and rivers carry minerals from land rocks into the ocean, building up over millions of years." },
      src: { label: "NOAA Ocean Service", url: "https://oceanservice.noaa.gov/facts/whyoceansalty.html" }
    },
    "coral-fragment": {
      ic: "🪸", cls: "Scleractinia · bộ xương đá vôi (CaCO₃)",
      vi: { n: "Mảnh San Hô" }, en: { n: "Coral Fragment" },
      m: { who: "byte",
           vi: "Cảm biến của tớ báo: cái này không phải đá! Nó là bộ xương do hàng triệu sinh vật tí hon cùng nhau xây nên.",
           en: "My sensors say: this isn't a rock! It's a skeleton that millions of tiny animals built together." },
      f: { vi: "Rạn san hô do những sinh vật rất nhỏ xây bằng đá vôi, và chúng cần nước biển ấm, trong để sống được.",
           en: "Coral reefs are built from limestone by very small animals, and they need warm, clear seawater to survive." },
      src: { label: "NOAA Ocean Service", url: "https://oceanservice.noaa.gov/facts/coral_reef.html" }
    },
    "polar-ice-core": {
      ic: "🧊", cls: "Ice core · băng xếp lớp theo năm",
      vi: { n: "Cột Băng Vùng Cực" }, en: { n: "Polar Ice Core" },
      m: { who: "comet",
           vi: "Cột băng này là một quyển sách! Mỗi lớp là một năm, nên đọc từ trên xuống là biết thời tiết ngày xưa thế nào.",
           en: "This ice column is a book! Each layer is one year, so reading top to bottom tells you the weather of the past." },
      f: { vi: "Băng ở hai cực xếp thành từng lớp theo năm, nên khoan lấy một cột băng là đọc được khí hậu của quá khứ.",
           en: "Polar ice builds up in yearly layers, so drilling out a core lets scientists read the climate of the past." },
      src: { label: "NASA Climate", url: "https://climate.nasa.gov/" }
    },
    "mars-red-ice": {
      ic: "💎", cls: "Băng H₂O + bụi oxit sắt · vùng cực Sao Hoả",
      vi: { n: "Tinh Thể Băng Đỏ" }, en: { n: "Red Ice Crystal" },
      m: { who: "comet",
           vi: "Mẫu vật hạng quý! Khoang lạnh phải giữ thật thấp mới không tan. Màu đỏ là bụi Sao Hoả lẫn vào trong băng đó.",
           en: "A prized sample! The cold pod has to stay very low or it melts. The red tint is Martian dust mixed into the ice." },
      f: { vi: "Sao Hoả có mũ băng ở hai cực, và màu đỏ của hành tinh đến từ bụi giàu oxit sắt — cùng loại chất tạo nên gỉ sắt.",
           en: "Mars has polar ice caps, and the planet's red colour comes from dust rich in iron oxide — the same stuff as rust." },
      src: { label: "NASA — Mars", url: "https://science.nasa.gov/mars/" }
    },
    "europa-brine": {
      ic: "🌊", cls: "Nước mặn dưới lớp vỏ băng · Europa",
      vi: { n: "Nước Mặn Dưới Băng Europa" }, en: { n: "Europan Under-Ice Brine" },
      m: { who: "byte",
           vi: "Hạng truyền thuyết! Drone phải khoan qua lớp vỏ băng rất dày mới lấy được. Đây có thể là nước của một đại dương ngầm.",
           en: "Legendary tier! The drone had to drill through a very thick ice shell. This may be water from a hidden ocean." },
      f: { vi: "Europa là một mặt trăng của Sao Mộc; bên dưới lớp vỏ băng của nó được cho là có một đại dương nước mặn.",
           en: "Europa is one of Jupiter's moons; beneath its icy shell scientists believe there is a salty ocean." },
      src: { label: "NASA — Europa", url: "https://science.nasa.gov/jupiter/moons/europa/" }
    },

    /* ───────────── 🌿 Sinh quyển ───────────── */
    "amazon-leaf": {
      ic: "🌿", cls: "Folium tropicale · thực vật hạt kín",
      vi: { n: "Lá Cây Rừng Amazon" }, en: { n: "Amazon Rainforest Leaf" },
      m: { who: "byte",
           vi: "Chiếc lá này là một nhà máy tí hon: nó lấy ánh sáng với khí CO₂ rồi nhả ra khí oxy — đúng thứ phi hành gia cần!",
           en: "This leaf is a tiny factory: it takes light and CO₂ and gives out oxygen — exactly what an astronaut needs!" },
      f: { vi: "Lá cây quang hợp: dùng năng lượng ánh sáng để biến nước và khí CO₂ thành đường, đồng thời thải ra khí oxy.",
           en: "Leaves photosynthesise: they use light energy to turn water and CO₂ into sugar, releasing oxygen as they go." },
      src: { label: "NASA Earth Observatory", url: "https://earthobservatory.nasa.gov/" }
    },
    "penguin-feather": {
      ic: "🪶", cls: "Pluma · Aptenodytes forsteri",
      vi: { n: "Lông Chim Cánh Cụt" }, en: { n: "Penguin Feather" },
      m: { who: "comet",
           vi: "Ở Nam Cực lạnh tới mức tớ phải bật lò sưởi trong drone! Bộ lông xếp lớp dày như áo phao giúp chim cánh cụt giữ ấm.",
           en: "Antarctica is so cold I had to switch on the drone's heater! Layered feathers keep penguins warm like a padded coat." },
      f: { vi: "Chim cánh cụt hoàng đế sống ở Nam Cực và có lớp lông xếp rất dày, giúp chặn gió lạnh và giữ nhiệt cho cơ thể.",
           en: "Emperor penguins live in Antarctica and have very densely layered feathers that block cold wind and hold in body heat." },
      src: { label: "NASA — Earth", url: "https://science.nasa.gov/earth/" }
    },
    "tardigrade-sample": {
      ic: "🐛", cls: "Tardigrada · động vật tám chân hiển vi",
      vi: { n: "Bọ Gấu Nước" }, en: { n: "Water Bear (Tardigrade)" },
      m: { who: "byte",
           vi: "Bé xíu mà gan cực! Tớ để mẫu này trong khoang chân không suốt một ngày, mở ra nó vẫn bò tung tăng.",
           en: "Tiny but incredibly tough! I left this in the vacuum pod for a whole day and it was still crawling around." },
      f: { vi: "Bọ gấu nước là sinh vật tí hon chịu được điều kiện rất khắc nghiệt; trong một số thí nghiệm, chúng còn sống sót khi được đưa ra ngoài không gian.",
           en: "Tardigrades are microscopic animals that endure extreme conditions; in some experiments they survived exposure to space." },
      src: { label: "NASA Biological & Physical Sciences", url: "https://science.nasa.gov/biological-physical/" }
    },
    "deep-sea-bacteria": {
      ic: "🦠", cls: "Vi khuẩn hoá dưỡng · miệng phun thuỷ nhiệt",
      vi: { n: "Vi Khuẩn Đáy Biển Sâu" }, en: { n: "Deep-Sea Bacteria" },
      m: { who: "comet",
           vi: "Chỗ này tối đen, không một tia nắng, mà vẫn có sinh vật sống! Chúng ăn chất khoáng phun ra từ đáy biển.",
           en: "It's pitch dark down here, not a ray of sunlight, yet living things thrive! They feed on minerals venting from the seafloor." },
      f: { vi: "Ở đáy biển sâu không có ánh nắng, một số vi khuẩn sống bằng năng lượng lấy từ chất khoáng phun ra ở miệng phun thuỷ nhiệt.",
           en: "In the sunless deep sea, some bacteria live on energy taken from minerals pouring out of hydrothermal vents." },
      src: { label: "NASA Biological & Physical Sciences", url: "https://science.nasa.gov/biological-physical/" }
    },

    /* ───────────── 🪨 Địa quyển ───────────── */
    "himalaya-crystal": {
      ic: "🪨", cls: "Quartz (SiO₂) · hệ tinh thể sáu phương",
      vi: { n: "Tinh Thể Núi Đá" }, en: { n: "Mountain Rock Crystal" },
      m: { who: "byte",
           vi: "Cứng thật! Tớ phải đổi sang mũi khoan cứng nhất. Các mặt phẳng bóng loáng này không ai mài đâu — tinh thể tự lớn thành hình.",
           en: "So hard! I had to swap in my toughest drill bit. Nobody polished these flat faces — the crystal grew into that shape." },
      f: { vi: "Dãy Himalaya hình thành khi hai mảng lục địa đâm vào nhau, và các phép đo cho thấy nó vẫn đang được đẩy cao thêm.",
           en: "The Himalayas formed where two continental plates collided, and measurements show they are still being pushed higher." },
      src: { label: "NASA Earth Observatory", url: "https://earthobservatory.nasa.gov/" }
    },
    "volcano-obsidian": {
      ic: "🌑", cls: "Obsidian · thuỷ tinh núi lửa",
      vi: { n: "Đá Thuỷ Tinh Núi Lửa" }, en: { n: "Volcanic Obsidian" },
      m: { who: "comet",
           vi: "Nhẵn như gương mà lại là đá! Vì dung nham nguội quá nhanh nên không kịp mọc thành tinh thể.",
           en: "Smooth as a mirror, yet it's rock! The lava cooled so fast it never had time to grow crystals." },
      f: { vi: "Obsidian là dung nham nguội đi cực nhanh nên không kịp tạo tinh thể — vì thế bề mặt nó nhẵn như thuỷ tinh.",
           en: "Obsidian is lava that cooled extremely fast, so no crystals could form — which is why it looks like glass." },
      src: { label: "NASA Earth Observatory", url: "https://earthobservatory.nasa.gov/" }
    },
    "ancient-lava-rock": {
      ic: "🪨", cls: "Basalt · đá phun trào nguội từ dung nham",
      vi: { n: "Nham Thạch Cổ Đại" }, en: { n: "Ancient Lava Rock" },
      m: { who: "comet",
           vi: "Bạn vừa xem Trái Đất thời còn là quả cầu dung nham, và đây là một mảnh của thời đó! Nó cứng như đá, nhưng ngày xưa từng chảy đỏ rực.",
           en: "You just watched Earth back when it was a ball of magma — and this is a piece of that time! It's solid stone now, but it once flowed red-hot." },
      f: { vi: "Trái Đất hình thành khoảng 4,5 tỷ năm trước và bề mặt thời đầu gần như nóng chảy; đá phun trào là loại đá sinh ra khi dung nham nguội lại.",
           en: "Earth formed about 4.5 billion years ago with a largely molten early surface; volcanic rock is what forms when lava cools down." },
      src: { label: "NASA Science — Facts About Earth", url: "https://science.nasa.gov/earth/facts/" }
    },
    "desert-sand": {
      ic: "🏜️", cls: "Cát thạch anh · hạt mài mòn do gió",
      vi: { n: "Cát Sa Mạc Sahara" }, en: { n: "Sahara Desert Sand" },
      m: { who: "byte",
           vi: "Mấy hạt cát này đi xa hơn cả tớ! Gió bốc chúng lên rồi thổi qua tận bên kia đại dương.",
           en: "These grains travel farther than I do! Wind lifts them up and carries them clear across an ocean." },
      f: { vi: "Bụi từ sa mạc Sahara bay qua cả Đại Tây Dương, và các vệ tinh theo dõi được đường đi của những đám bụi đó.",
           en: "Dust from the Sahara crosses the entire Atlantic Ocean, and satellites can track where those dust clouds travel." },
      src: { label: "NASA Earth Observatory", url: "https://earthobservatory.nasa.gov/" }
    },
    "lunar-regolith": {
      ic: "🌕", cls: "Lunar regolith · mảnh vụn thuỷ tinh & silicat",
      vi: { n: "Bụi Mịn Mặt Trăng" }, en: { n: "Lunar Fine Dust" },
      m: { who: "byte",
           vi: "Bụi này sắc như dao và bám dính khủng khiếp — nó làm xước cả kính bảo hộ của tớ. Đừng mở nắp khoang nhé!",
           en: "This dust is razor-sharp and clings to everything — it even scratched my visor. Don't open the pod!" },
      f: { vi: "Bề mặt Mặt Trăng phủ một lớp bụi đá vụn gọi là regolith, do thiên thạch va đập nghiền nhỏ suốt hàng tỉ năm.",
           en: "The Moon's surface is covered by a layer of crushed rock called regolith, ground down by impacts over billions of years." },
      src: { label: "NASA — Moon", url: "https://science.nasa.gov/moon/" }
    },
    "mercury-slate": {
      ic: "⚪", cls: "Đá silicat · vỏ Sao Thuỷ",
      vi: { n: "Phiến Đá Sao Thuỷ" }, en: { n: "Mercurian Slate" },
      m: { who: "comet",
           vi: "Lấy mẫu này khó nhất đấy! Ban ngày ở đó nóng kinh khủng, ban đêm lại lạnh buốt — drone phải đợi lúc chuyển giao.",
           en: "This was the trickiest pickup! Daytime is scorching, night is freezing — the drone had to wait for the changeover." },
      f: { vi: "Sao Thuỷ ở gần Mặt Trời nhất và gần như không có khí quyển, nên ban ngày rất nóng còn ban đêm rất lạnh.",
           en: "Mercury is closest to the Sun and has almost no atmosphere, so its days are very hot and its nights very cold." },
      src: { label: "NASA — Mercury", url: "https://science.nasa.gov/mercury/" }
    },
    "venus-basalt": {
      ic: "🟠", cls: "Basalt · đá núi lửa Sao Kim",
      vi: { n: "Đá Bazan Sao Kim" }, en: { n: "Venusian Basalt" },
      m: { who: "byte",
           vi: "Drone của tớ chỉ trụ được vài phút ở dưới đó! Khí quyển Sao Kim vừa dày vừa nóng như cái lò.",
           en: "My drone lasted only a few minutes down there! Venus's atmosphere is thick and hot like an oven." },
      f: { vi: "Sao Kim có khí quyển rất dày khiến nhiệt bị giữ lại, nên nó là hành tinh nóng nhất trong Hệ Mặt Trời.",
           en: "Venus has a very thick atmosphere that traps heat, making it the hottest planet in the Solar System." },
      src: { label: "NASA — Venus", url: "https://science.nasa.gov/venus/" }
    },

    /* ───────────── 🌌 Cổ vật vũ trụ ───────────── */
    "iron-meteorite": {
      ic: "☄️", cls: "Thiên thạch sắt · hợp kim sắt–niken",
      vi: { n: "Thiên Thạch Sắt" }, en: { n: "Iron Meteorite" },
      m: { who: "comet",
           vi: "Nặng trịch! Mẩu kim loại này từng là phần lõi của một vật thể lớn hơn nhiều, thời Hệ Mặt Trời còn non.",
           en: "So heavy! This lump of metal was once the core of a much bigger body, back when the Solar System was young." },
      f: { vi: "Thiên thạch sắt là mảnh vỡ từ phần lõi kim loại của những vật thể lớn hình thành thời Hệ Mặt Trời còn non.",
           en: "Iron meteorites are fragments from the metal cores of large bodies that formed when the Solar System was young." },
      src: { label: "NASA — Meteors & Meteorites", url: "https://science.nasa.gov/solar-system/meteors-meteorites/" }
    },
    "saturn-ring-ice": {
      ic: "🪐", cls: "Băng nước · hạt vành đai Sao Thổ",
      vi: { n: "Băng Vành Đai Sao Thổ" }, en: { n: "Saturn Ring Ice" },
      m: { who: "byte",
           vi: "Vành đai nhìn từ xa như một cái đĩa liền, nhưng bay vào giữa thì hoá ra là vô số mảnh băng đang bay quanh.",
           en: "From afar the rings look like one solid disc, but fly inside and they're countless ice chunks orbiting along." },
      f: { vi: "Vành đai Sao Thổ phần lớn là những mảnh băng nước, kích thước từ hạt bụi cho tới tảng lớn.",
           en: "Saturn's rings are mostly chunks of water ice, ranging in size from dust grains to large boulders." },
      src: { label: "NASA — Saturn", url: "https://science.nasa.gov/saturn/" }
    },
    "uranus-frost": {
      ic: "🔵", cls: "Sương metan · khí quyển Sao Thiên Vương",
      vi: { n: "Sương Metan Xanh" }, en: { n: "Blue Methane Frost" },
      m: { who: "comet",
           vi: "Cả hành tinh xanh lơ như viên bi! Là do khí metan trong khí quyển hút mất ánh sáng đỏ đó.",
           en: "The whole planet is pale blue like a marble! That's methane in the atmosphere soaking up red light." },
      f: { vi: "Sao Thiên Vương có màu xanh lục-lam vì khí metan trong khí quyển hấp thụ phần ánh sáng đỏ.",
           en: "Uranus looks blue-green because methane in its atmosphere absorbs the red part of sunlight." },
      src: { label: "NASA — Uranus", url: "https://science.nasa.gov/uranus/" }
    },
    "neptune-diamond-dust": {
      ic: "💠", cls: "Carbon nén áp suất cao · lòng Sao Hải Vương",
      vi: { n: "Bụi Kim Cương Sao Hải Vương" }, en: { n: "Neptunian Diamond Dust" },
      m: { who: "byte",
           vi: "Hạng truyền thuyết, và cũng là mẫu khó lấy nhất! Sâu trong lòng hành tinh, áp suất lớn tới mức có thể ép carbon thành kim cương.",
           en: "Legendary tier, and the hardest to fetch! Deep inside the planet, pressure can be great enough to squeeze carbon into diamond." },
      f: { vi: "Trong lòng Sao Hải Vương áp suất cực lớn; các thí nghiệm cho thấy điều kiện như vậy có thể ép carbon thành kim cương.",
           en: "Deep inside Neptune the pressure is immense; experiments suggest such conditions can squeeze carbon into diamond." },
      src: { label: "NASA — Neptune", url: "https://science.nasa.gov/neptune/" }
    },
    "orion-stardust": {
      ic: "✨", cls: "Bụi & khí giữa các sao · tinh vân Lạp Hộ",
      vi: { n: "Bụi Sao Tinh Vân Lạp Hộ" }, en: { n: "Orion Nebula Stardust" },
      m: { who: "comet",
           vi: "Đây là nguyên liệu làm ra các ngôi sao! Trong tinh vân, bụi với khí đang từ từ co lại để thành sao mới.",
           en: "This is the raw material stars are made of! Inside a nebula, dust and gas slowly pull together into new stars." },
      f: { vi: "Tinh vân Lạp Hộ là một vùng đang sinh sao — nơi bụi và khí co lại để hình thành những ngôi sao mới.",
           en: "The Orion Nebula is a star-forming region — a place where dust and gas collapse to build brand-new stars." },
      src: { label: "NASA — James Webb Space Telescope", url: "https://science.nasa.gov/mission/webb/" }
    }
  };

  /* Nhóm — khoá phải khớp `Category` trong Specimens.All ở server. */
  var CATS = {
    hydro:  { ic: "🌊", vi: "Thuỷ quyển",     en: "Hydrosphere",
              subVi: "Mẫu nước & chất lỏng", subEn: "Water & liquid samples" },
    bio:    { ic: "🌿", vi: "Sinh quyển",     en: "Biosphere",
              subVi: "Mẫu sinh vật & thực vật", subEn: "Life & plant samples" },
    litho:  { ic: "🪨", vi: "Địa quyển",      en: "Lithosphere",
              subVi: "Mẫu đá & khoáng vật",  subEn: "Rock & mineral samples" },
    cosmic: { ic: "🌌", vi: "Cổ vật vũ trụ",  en: "Cosmic Artifacts",
              subVi: "Vật thể ngoài hành tinh", subEn: "Objects beyond the planets" }
  };

  /* Nơi lấy mẫu — khoá phải khớp `Origin` trong Specimens.All ở server. */
  var ORIGINS = {
    "earth-ocean":    { ic: "🌍", vi: "Trái Đất (Đại Dương)",     en: "Earth (Ocean)" },
    "earth-reef":     { ic: "🌍", vi: "Trái Đất (Rạn San Hô)",    en: "Earth (Coral Reef)" },
    "earth-pole":     { ic: "🌍", vi: "Trái Đất (Nam Cực)",       en: "Earth (Antarctica)" },
    "earth-forest":   { ic: "🌍", vi: "Trái Đất (Rừng Amazon)",   en: "Earth (Amazon Rainforest)" },
    "earth-spring":   { ic: "🌍", vi: "Trái Đất (Suối Nước Nóng)", en: "Earth (Hot Spring)" },
    "earth-abyss":    { ic: "🌍", vi: "Trái Đất (Đáy Biển Sâu)",  en: "Earth (Deep Sea)" },
    "earth-himalaya": { ic: "🌍", vi: "Trái Đất (Dãy Himalaya)",  en: "Earth (Himalayas)" },
    "earth-volcano":  { ic: "🌍", vi: "Trái Đất (Miệng Núi Lửa)", en: "Earth (Volcano)" },
    "earth-desert":   { ic: "🌍", vi: "Trái Đất (Sa Mạc Sahara)", en: "Earth (Sahara Desert)" },
    "moon":           { ic: "🌕", vi: "Mặt Trăng",                en: "The Moon" },
    "mercury":        { ic: "⚪", vi: "Sao Thuỷ",                 en: "Mercury" },
    "venus":          { ic: "🟠", vi: "Sao Kim",                  en: "Venus" },
    "mars":           { ic: "🔴", vi: "Sao Hoả",                  en: "Mars" },
    "jupiter":        { ic: "🟤", vi: "Sao Mộc (Mặt trăng Europa)", en: "Jupiter (moon Europa)" },
    "saturn":         { ic: "🪐", vi: "Sao Thổ (Vành Đai)",       en: "Saturn (Rings)" },
    "uranus":         { ic: "🔵", vi: "Sao Thiên Vương",          en: "Uranus" },
    "neptune":        { ic: "🔷", vi: "Sao Hải Vương",            en: "Neptune" },
    "belt":           { ic: "☄️", vi: "Vành Đai Thiên Thạch",     en: "Asteroid Belt" },
    "orion":          { ic: "🌌", vi: "Tinh Vân Lạp Hộ",          en: "Orion Nebula" }
  };

  var RARITY = {
    common:    { vi: "Phổ thông",   en: "Common",    tag: "Common" },
    rare:      { vi: "Quý",         en: "Rare",      tag: "✦ Rare" },
    legendary: { vi: "Truyền thuyết", en: "Legendary", tag: "★ Legendary" }
  };

  var MASCOT = {
    comet: { ic: "☄️", name: "Comet" },
    byte:  { ic: "🤖", name: "Byte" }
  };

  /* ─────────── Câu nhắc mở khoá, ghép từ `metric` + `goal` của SERVER ───────────
     Cố ý KHÔNG lưu câu này ở server: mốc thì chỉ khai báo một chỗ (server), còn
     cách diễn đạt thì phải dịch VI/EN nên thuộc về client. Đổi mốc ở server thì
     câu nhắc tự đúng theo, không phải sửa file này.

     ⚠️ KHÔNG dùng câu kiểu "Mở khoá tại Mission 02" — nhiệm vụ ĐÓ chưa tồn tại,
     viết thế là hứa với trẻ một thứ không có. Nhiệm Vụ 01 thì được nhắc thẳng vì
     `mission-earth.html` có thật; khoá `mission:earth:<step>` dưới đây khớp đúng id
     bước trong `AstroqSV/Services/Missions.cs`.

     `hint()` tra `d[metric]` trước khi lùi về `d["_"]`, nên chỉ cần THÊM KHOÁ vào
     hai từ điển là xong — không phải sửa hàm. */
  var HINT = {
    vi: {
      "planet":        "Bay tới {name} trong Bản Đồ Thiên Hà",
      "const":         "Ghép xong chòm sao {name} ở Khu Huấn Luyện",
      "planets":       "Ghé thăm {n} hành tinh trong Bản Đồ Thiên Hà",
      "lessonsRead":   "Đọc xong {n} bài ở Trạm Tri Thức",
      "quizTaken":     "Hoàn thành {n} lượt Quiz",
      "quizCorrect":   "Trả lời đúng {n} câu hỏi Quiz",
      "quizPerfect":   "Trả lời đúng toàn bộ một lượt Quiz",
      "gamesPlayed":   "Chơi {n} lượt ở Khu Huấn Luyện",
      "meteorsEarned": "Thu được {n} Thiên thạch tím",
      "flightSeconds": "Bay tổng cộng {n} giây",
      "level":         "Đạt cấp {n}",
      "best:dodge":         "Đạt {n} điểm ở Né Thiên Thạch",
      "best:defender":      "Đạt {n} điểm ở Space Defender",
      "best:constellation": "Ghép xong một chòm sao ở Khu Huấn Luyện",
      "mission:earth":          "Hoàn thành Nhiệm Vụ 01: Hành Tinh Xanh",
      "mission:earth:timeline": "Xem hết mốc thời gian 4,5 tỷ năm ở Nhiệm Vụ 01",
      "_": "Tiếp tục khám phá để mở khoá"
    },
    en: {
      "planet":        "Fly to {name} in the Galaxy Map",
      "const":         "Complete the {name} constellation in the Training Simulator",
      "planets":       "Visit {n} planets in the Galaxy Map",
      "lessonsRead":   "Finish reading {n} articles at the Knowledge Station",
      "quizTaken":     "Complete {n} quiz runs",
      "quizCorrect":   "Answer {n} quiz questions correctly",
      "quizPerfect":   "Get every question right in one quiz",
      "gamesPlayed":   "Play {n} runs in the Training Simulator",
      "meteorsEarned": "Collect {n} Purple Meteors",
      "flightSeconds": "Fly for {n} seconds in total",
      "level":         "Reach level {n}",
      "best:dodge":         "Score {n} in Asteroid Dodge",
      "best:defender":      "Score {n} in Space Defender",
      "best:constellation": "Complete one constellation in the Training Simulator",
      "mission:earth":          "Complete Mission 01: The Blue Planet",
      "mission:earth:timeline": "Walk through the whole 4.5-billion-year timeline in Mission 01",
      "_": "Keep exploring to unlock"
    }
  };

  function dict(lang) { return HINT[lang === "en" ? "en" : "vi"]; }

  function pick(id, lang) {
    var s = S[id];
    if (!s) return null;
    return (lang === "en" ? s.en : s.vi) || s.vi;
  }
  function bi(obj, lang) {
    if (!obj) return "";
    return (lang === "en" ? obj.en : obj.vi) || obj.vi || "";
  }

  /* ─────────────────── MÓC TREO TRÊN VÁCH KHOANG LÁI ───────────────────
     Chỗ DUY NHẤT ở client khai danh sách móc — `dashboard.html` (vẽ ra buồng lái)
     và `specimen-vault.html` (cho trẻ chọn) đều đọc ở đây. Khai hai bản là hai nơi
     nói hai bộ móc, mà server chỉ nhận một bộ.

     ⚠️ PHẢI KHỚP `Specimens.Hooks` Ở SERVER — server mới là bên quyết định giá trị
        nào ghi được vào DB. `check_pages.py` mục [11] đối chiếu hai bên; lệch thì
        trẻ chọn được một móc rồi nhận lỗi đỏ, hoặc ngược lại.
     ⚠️ THỨ TỰ TRONG MẢNG LÀ THỨ TỰ TỪ TRÊN XUỐNG của mỗi vách — `css/dashboard.css`
        xếp chúng bằng flex theo đúng thứ tự này, không gán toạ độ cho từng móc.
        Đảo thứ tự ở đây là đảo chỗ treo của mọi mẫu vật đã lưu. */
  var HOOKS = ["L1", "L2", "L3", "L4", "L5", "R1", "R2", "R3", "R4", "R5"];
  var WALL_NAME = {
    L: { vi: "Vách trái", en: "Left wall" },
    R: { vi: "Vách phải", en: "Right wall" }
  };

  global.AstroQSpecimens = {
    /** Mẫu vật server có mà đây chưa có tên → trả chính id (trang không vỡ). */
    name: function (id, lang) { var d = pick(id, lang); return d ? d.n : id; },

    /** Danh sách móc, thứ tự trên→dưới của vách trái rồi vách phải. */
    hooks: function () { return HOOKS.slice(); },
    /** Móc của một vách: "L" hoặc "R". */
    hooksOf: function (wall) {
      return HOOKS.filter(function (h) { return h.charAt(0) === wall; });
    },
    isHook: function (h) { return HOOKS.indexOf(h) !== -1; },
    /** "L" → "Vách trái". Nhận cả "L2" (lấy chữ đầu) cho tiện chỗ gọi. */
    wallName: function (w, lang) {
      var x = WALL_NAME[String(w || "").charAt(0)];
      return x ? (lang === "en" ? x.en : x.vi) : String(w || "");
    },
    /** "L2" → "Vách trái · Móc 2" — dùng cho `aria-label`, không vẽ ra mặt tranh. */
    hookName: function (h, lang) {
      if (!WALL_NAME[String(h || "").charAt(0)]) return String(h || "");
      return this.wallName(h, lang) + " · " +
             (lang === "en" ? "Hook " : "Móc ") + String(h).slice(1);
    },
    icon: function (id) { return (S[id] && S[id].ic) || "🧪"; },
    classification: function (id) { return (S[id] && S[id].cls) || ""; },
    fact: function (id, lang) { return S[id] ? bi(S[id].f, lang) : ""; },
    source: function (id) { return (S[id] && S[id].src) || null; },

    /** → { ic, name, line } — lời linh vật đọc trong màn soi chi tiết. */
    mascot: function (id, lang) {
      var s = S[id];
      if (!s || !s.m) return null;
      var who = MASCOT[s.m.who] || MASCOT.byte;
      return { ic: who.ic, name: who.name, line: bi(s.m, lang) };
    },

    cats: CATS,
    catName: function (k, lang) { var c = CATS[k]; return c ? bi(c, lang) : k; },
    catIcon: function (k) { return (CATS[k] && CATS[k].ic) || "🧪"; },
    catSub: function (k, lang) {
      var c = CATS[k];
      if (!c) return "";
      return (lang === "en" ? c.subEn : c.subVi) || c.subVi || "";
    },

    originName: function (k, lang) { var o = ORIGINS[k]; return o ? bi(o, lang) : k; },
    originIcon: function (k) { return (ORIGINS[k] && ORIGINS[k].ic) || "🛰️"; },

    rarityName: function (r, lang) { var x = RARITY[r]; return x ? bi(x, lang) : r; },
    rarityTag: function (r) { return (RARITY[r] && RARITY[r].tag) || r; },

    /**
     * Câu nhắc mở khoá, ghép từ `metric` + `goal` mà SERVER trả về.
     * Dạng `planet:<id>` / `const:<id>` cần tên hành tinh & chòm sao — lấy ở
     * js/planets.js và js/constellations.js (chỗ duy nhất khai báo chúng).
     */
    hint: function (metric, goal, lang) {
      var d = dict(lang);
      metric = String(metric || "");

      if (metric.indexOf("planet:") === 0) {
        var pid = metric.slice(7);
        var pn = global.AstroQPlanets ? AstroQPlanets.name(pid, lang) : pid;
        return d["planet"].replace("{name}", pn);
      }
      if (metric.indexOf("const:") === 0) {
        var cid = metric.slice(6);
        var cn = global.AstroQConsts ? AstroQConsts.name(cid, lang) : cid;
        return d["const"].replace("{name}", cn);
      }
      var tpl = d[metric] || d["_"];
      return tpl.replace("{n}", goal);
    },

    /** Có nội dung cho id này chưa — script kiểm thử dùng để soi thiếu/thừa. */
    has: function (id) { return Object.prototype.hasOwnProperty.call(S, id); },
    ids: function () { return Object.keys(S); }
  };
})(window);
