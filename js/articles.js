/* ==========================================================
   js/articles.js — BÀI ĐỌC, CHỖ DUY NHẤT KHAI BÁO.

   Gộp 05/08/2026 từ HAI mảng `ARTICLES` riêng ở `learn.html` (4 bài) và
   `library.html` (8 bài). Ba bài trùng chủ đề nên tổng còn **9**.

   ⚠️⚠️ ĐÂY KHÔNG PHẢI DỌN DẸP — HAI MẢNG ĐÓ ĐANG GÂY HAI LỖI THẬT:

   ① **Đọc một bài ở trang này thì trang kia vẫn báo chưa đọc.** Cả hai trang cùng ghi
      vào `localStorage["astroq-read"]` theo **id**, mà cùng một bài lại mang hai id
      (`gaia` ↔ `lib-gaia` · `eht` ↔ `lib-blackhole` · `exo-ai` ↔ `lib-exoplanet`).
      Trẻ đọc Gaia ở Trạm Tri Thức, sang Góc Khám Phá vẫn thấy nó nằm ở khối "chưa đọc".

   ② **Bộ đếm `lessonsRead` trên server đếm hai lần cho cùng một nội dung.** Cả hai
      trang gọi `AstroQProgress.lesson(curArt.id)`; server chống đếm trùng bằng bản ghi
      `READ#<id>` — nhưng hai id khác nhau thì nó không có cách nào biết đó là một bài.
      Tức huy hiệu đọc sách mở được bằng cách đọc **cùng một bài ở hai chỗ**.

   ⇒ Vì thế `OLD_ID` ở dưới là **BẮT BUỘC, không phải phần thêm cho đẹp**: trẻ đã đọc
     `gaia` từ trước vẫn phải được tính là đã đọc `lib-gaia`. Bỏ nó đi là xoá lịch sử
     đọc của những đứa trẻ đã dùng app.

   ⚠️ Khi số bài vượt ~30 thì cân nhắc chuyển sang một file JSON tải bằng `fetch` —
      nhưng **đo trước rồi hãy đổi**, đừng đoán. Hiện 9 bài nên một file JS khai báo
      thẳng là đúng khuôn của `js/planets.js` · `js/badges.js` · `js/constellations.js`.

   Hình dạng một bài (lấy theo `library.html` vì nó đầy đủ hơn):
     id · src · cat · em · c[3] · img · credit · url · title{vi,en} · body{vi,en}[]
   `img`/`credit` được phép `null` — cả hai trang đều đã có nhánh không ảnh.
   ========================================================== */
(function () {
  "use strict";

  var IMG = "https://images-assets.nasa.gov/image/";

  var ARTICLES = [
    { id:"jwst", src:"NASA", cat:"astronomy", em:"🔭", c:["#8ee0ff","#2f8fd6","#0e2a5e"], url:"https://science.nasa.gov/mission/webb/",
      img:null, credit:null,
      title:{vi:"Kính thiên văn James Webb hé lộ những thiên hà cổ đại", en:"James Webb Telescope reveals ancient galaxies"},
      body:{
        vi:["Kính thiên văn James Webb (JWST) quan sát bằng tia hồng ngoại, giúp nhìn xuyên qua các đám bụi vũ trụ để thấy ánh sáng từ những thiên hà hình thành chỉ vài trăm triệu năm sau Vụ Nổ Lớn.",
            "Nhờ tấm gương vàng khổng lồ rộng 6,5 m, Webb thu được ánh sáng cực mờ đã du hành hơn 13 tỉ năm tới Trái Đất — như một cỗ máy thời gian nhìn về quá khứ của vũ trụ."],
        en:["The James Webb Space Telescope (JWST) observes in infrared, seeing through cosmic dust to capture light from galaxies that formed just a few hundred million years after the Big Bang.",
            "With its giant 6.5 m gold mirror, Webb collects extremely faint light that has travelled over 13 billion years to reach us — a time machine peering into the early universe."] } },
    { id:"lib-nebula", src:"NASA", cat:"astronomy", em:"🌌", c:["#8ee0ff","#2f6fd0","#0e2a5e"],
      img:IMG+"PIA25433/PIA25433~large.jpg", credit:"NASA / JPL-Caltech", url:"https://science.nasa.gov/mission/webb/",
      title:{vi:"Tinh vân Đại Bàng — vườn ươm của các ngôi sao",en:"The Eagle Nebula — a nursery of stars"},
      body:{vi:["Trong vũ trụ có những đám mây khí và bụi khổng lồ gọi là <b>tinh vân</b>. Bên trong chúng, khí co lại và nóng dần lên cho tới khi bùng cháy thành những ngôi sao mới.",
                "Tinh vân Đại Bàng nổi tiếng với 'Những Cột Trụ Sáng Tạo' — các cột khí cao hàng nghìn tỉ km, nơi hàng loạt ngôi sao đang chào đời."],
            en:["Space has giant clouds of gas and dust called <b>nebulae</b>. Inside them, gas squeezes together and heats up until it lights up as new stars.",
                "The Eagle Nebula is famous for the 'Pillars of Creation' — towers of gas trillions of km tall where many stars are being born."]},
      term:{who:"comet", word:{vi:"Tinh vân",en:"Nebula"}, text:{vi:"<b>Tinh vân</b> là 'đám mây' khổng lồ bằng khí và bụi trong vũ trụ — chính là nơi các ngôi sao ra đời đó! 🐱",en:"A <b>nebula</b> is a giant 'cloud' of gas and dust in space — it's where stars are born! 🐱"}} },
    { id:"lib-andromeda", src:"NASA", cat:"astronomy", em:"🌀", c:["#c6d8ff","#5a78c8","#20305e"],
      img:IMG+"PIA04921/PIA04921~large.jpg", credit:"NASA / JPL-Caltech", url:"https://science.nasa.gov/",
      title:{vi:"Thiên hà Tiên Nữ — người hàng xóm khổng lồ",en:"The Andromeda Galaxy — our giant neighbour"},
      body:{vi:["<b>Thiên hà</b> là một tập hợp khổng lồ gồm hàng trăm tỉ ngôi sao. Trái Đất của chúng ta nằm trong thiên hà Dải Ngân Hà.",
                "Tiên Nữ (Andromeda) là thiên hà lớn gần chúng ta nhất, cách khoảng 2,5 triệu năm ánh sáng — và đang tiến lại gần Dải Ngân Hà!"],
            en:["A <b>galaxy</b> is a huge collection of hundreds of billions of stars. Our Earth lives in the Milky Way galaxy.",
                "Andromeda is the nearest big galaxy to us, about 2.5 million light-years away — and it's slowly heading toward the Milky Way!"]},
      term:{who:"byte", word:{vi:"Năm ánh sáng",en:"Light-year"}, text:{vi:"<b>Năm ánh sáng</b> là quãng đường ánh sáng đi trong 1 năm — cực kỳ xa nhé! 🤖",en:"A <b>light-year</b> is how far light travels in one year — incredibly far! 🤖"}} },
    { id:"lib-mars", src:"NASA", cat:"robot", em:"🔴", c:["#ffcaa8","#d1642f","#5e2410"],
      img:IMG+"PIA21496/PIA21496~medium.jpg", credit:"NASA / JPL-Caltech", url:"https://mars.nasa.gov/",
      title:{vi:"Robot Perseverance khám phá Sao Hỏa",en:"Perseverance rover exploring Mars"},
      body:{vi:["<b>Xe tự hành</b> (rover) là robot 6 bánh do NASA gửi lên Sao Hỏa. Nó tự lái, chụp ảnh và thu thập mẫu đá.",
                "Perseverance đang tìm dấu vết của sự sống cổ đại và thử tạo khí oxy từ bầu khí quyển Sao Hỏa để giúp con người sau này."],
            en:["A <b>rover</b> is a six-wheeled robot NASA sends to Mars. It drives itself, takes photos and collects rock samples.",
                "Perseverance is looking for signs of ancient life and even makes oxygen from Mars' air to help future explorers."]},
      term:{who:"byte", word:{vi:"Xe tự hành",en:"Rover"}, text:{vi:"<b>Rover</b> là robot biết tự lái trên hành tinh khác — giống anh em họ của tớ! 🤖",en:"A <b>rover</b> is a robot that drives itself on another planet — like my cousin! 🤖"}} },
    { id:"lib-blackhole", src:"NASA", cat:"quantum", em:"🕳️", c:["#ffe1a8","#f2a53c","#3a2410"],
      img:IMG+"PIA23122/PIA23122~medium.jpg", credit:"NASA / JPL-Caltech", url:"https://science.nasa.gov/universe/black-holes/",
      title:{vi:"Hố đen khổng lồ ở thiên hà M87",en:"The giant black hole in galaxy M87"},
      body:{vi:["<b>Hố đen</b> là nơi có lực hấp dẫn mạnh đến mức ngay cả ánh sáng cũng không thoát ra được.",
                "Ở trung tâm thiên hà M87 có một hố đen nặng gấp hàng tỉ lần Mặt Trời. Năm 2019, con người lần đầu chụp được 'bóng' của nó."],
            en:["A <b>black hole</b> is a place where gravity is so strong that not even light can escape.",
                "At the center of galaxy M87 sits a black hole billions of times heavier than the Sun. In 2019 humans first photographed its 'shadow'."]},
      term:{who:"comet", word:{vi:"Hấp dẫn",en:"Gravity"}, text:{vi:"<b>Hấp dẫn</b> là lực kéo mọi vật lại gần nhau — hố đen kéo mạnh đến mức giữ luôn cả ánh sáng! 🐱",en:"<b>Gravity</b> is the pull that draws things together — a black hole pulls so hard it even traps light! 🐱"}} },
    { id:"lib-exoplanet", src:"AI & Tech", cat:"ai", em:"🪐", c:["#e6c6ff","#a06be0","#3a1f6e"],
      img:IMG+"PIA22082/PIA22082~orig.jpg", credit:"NASA / JPL-Caltech", url:"https://science.nasa.gov/exoplanets/",
      title:{vi:"AI giúp tìm hành tinh ngoài Hệ Mặt Trời",en:"AI helps find planets beyond the Solar System"},
      body:{vi:["<b>Ngoại hành tinh</b> là những hành tinh quay quanh một ngôi sao khác, không phải Mặt Trời của chúng ta.",
                "Máy tính dùng <b>trí tuệ nhân tạo</b> để soi hàng triệu ngôi sao, nhận ra lúc ánh sáng chớp mờ đi — dấu hiệu có hành tinh đi ngang qua."],
            en:["<b>Exoplanets</b> are planets orbiting other stars, not our Sun.",
                "Computers use <b>artificial intelligence</b> to scan millions of stars and spot tiny dips in brightness — a sign a planet passed in front."]},
      term:{who:"byte", word:{vi:"Trí tuệ nhân tạo",en:"Artificial Intelligence"}, text:{vi:"<b>AI</b> giúp máy tính học từ ví dụ để tự nhận ra quy luật — như cách tớ học vậy! 🤖",en:"<b>AI</b> lets computers learn from examples to spot patterns by themselves — just like me! 🤖"}} },
    { id:"lib-saturn", src:"NASA", cat:"astronomy", em:"🪐", c:["#ffe6b0","#d9a441","#5e3f14"],
      img:IMG+"PIA22766/PIA22766~orig.jpg", credit:"NASA / JPL-Caltech", url:"https://science.nasa.gov/saturn/",
      title:{vi:"Tàu Cassini và vành đai Sao Thổ",en:"Cassini and Saturn's rings"},
      body:{vi:["Sao Thổ nổi tiếng với những <b>vành đai</b> tuyệt đẹp làm từ hàng tỉ mảnh băng và đá, từ nhỏ như hạt cát đến to như ngôi nhà.",
                "Tàu Cassini đã bay quanh Sao Thổ suốt 13 năm, gửi về vô số hình ảnh và khám phá về hành tinh này cùng các mặt trăng của nó."],
            en:["Saturn is famous for its beautiful <b>rings</b> made of billions of pieces of ice and rock, from grains of sand to house-sized chunks.",
                "The Cassini spacecraft orbited Saturn for 13 years, sending back countless images and discoveries about the planet and its moons."]},
      term:{who:"comet", word:{vi:"Vành đai",en:"Rings"}, text:{vi:"<b>Vành đai</b> Sao Thổ không phải một khối liền — nó là hàng tỉ viên băng bay quanh cùng nhau! 🐱",en:"Saturn's <b>rings</b> aren't solid — they're billions of ice chunks orbiting together! 🐱"}} },
    { id:"lib-gaia", src:"ESA", cat:"astronomy", em:"🛰️", c:["#b6f5cf","#3fd6a0","#12503a"],
      img:"", credit:"ESA / Gaia / DPAC", url:"https://www.esa.int/Science_Exploration/Space_Science/Gaia",
      title:{vi:"Tàu Gaia của ESA vẽ bản đồ 3D Ngân Hà",en:"ESA's Gaia maps the Milky Way in 3D"},
      body:{vi:["<b>ESA</b> là Cơ quan Vũ trụ châu Âu. Tàu Gaia của họ đo vị trí và chuyển động của gần 2 tỉ ngôi sao.",
                "Nhờ đó, các nhà khoa học dựng nên tấm <b>bản đồ sao</b> ba chiều chi tiết nhất về thiên hà của chúng ta."],
            en:["<b>ESA</b> is the European Space Agency. Its Gaia spacecraft measures the position and motion of nearly 2 billion stars.",
                "From this, scientists build the most detailed 3D <b>star map</b> of our galaxy ever made."]},
      term:{who:"byte", word:{vi:"Bản đồ sao",en:"Star map"}, text:{vi:"<b>Bản đồ sao</b> cho biết mỗi ngôi sao ở đâu và đi hướng nào — như bản đồ đường phố nhưng cho cả thiên hà! 🤖",en:"A <b>star map</b> shows where each star is and where it's heading — like a street map for the whole galaxy! 🤖"}} },
    { id:"lib-qubit", src:"AI & Tech", cat:"quantum", em:"⚛️", c:["#c6ffe6","#4ade80","#155e40"],
      img:"", credit:"MIT / IBM Research", url:"https://www.ibm.com/quantum",
      title:{vi:"Máy tính lượng tử là gì?",en:"What is a quantum computer?"},
      body:{vi:["Máy tính thường dùng các bit chỉ mang giá trị 0 hoặc 1. Máy tính lượng tử dùng <b>qubit</b>, có thể mang cả 0 và 1 cùng lúc.",
                "Nhờ vậy, máy tính lượng tử có thể thử rất nhiều lời giải một lúc, giúp giải những bài toán mà máy tính thường mất hàng nghìn năm."],
            en:["Normal computers use bits that are only 0 or 1. Quantum computers use <b>qubits</b>, which can be both 0 and 1 at the same time.",
                "This lets quantum computers try many answers at once, solving problems that would take normal computers thousands of years."]},
      term:{who:"byte", word:{vi:"Qubit",en:"Qubit"}, text:{vi:"<b>Qubit</b> giống một đồng xu đang xoay tít — vừa là mặt ngửa vừa là mặt sấp cho tới khi bạn nhìn! 🤖",en:"A <b>qubit</b> is like a spinning coin — both heads and tails until you look! 🤖"}} },

    /* ═══════ ĐỢT 1 · 06/08/2026 · 5 bai doc ═══════
       ⚠️ `img: null` ca 5, co y — dung doan duong dan anh NASA theo mau:
          da do, `~large` KHONG ton tai voi moi anh. Tha khong anh con hon
          mot o anh vo truoc mat tre. `credit` phai null theo `img`.
       ⚠️ `terms` noi bai doc sang bank — `AstroQQuestions.byTerms()`. */
{
    id: "art-atmosphere-shield", src: "NASA", cat: "astronomy", em: "🌍",
    c: ["#8ee0ff", "#2f6fd0", "#0e2a5e"],
    url: "https://www.nasa.gov/general/what-is-earths-atmosphere/",
    img: null, credit: null,
    title: { vi: "Lá chắn khí quyển của Trái Đất",
             en: "Earth's atmospheric shield" },
    body: {
      vi: ["Nhìn Trái Đất từ vũ trụ, bạn sẽ thấy một dải khí mỏng màu xanh ôm lấy hành tinh. Đó là bầu khí quyển — lớp áo giữ cho sự sống an toàn giữa khoảng không lạnh lẽo.",
           "Khí quyển không phải một loại khí duy nhất. Khoảng 78% là nitơ, khoảng 21% là oxy mà con người và muôn loài hít thở mỗi ngày. Phần 1% còn lại gồm hơi nước cùng vài chất khí khác, ít thôi nhưng góp phần giữ nhiệt cho hành tinh.",
           "Bầu khí quyển xếp thành nhiều tầng chồng lên nhau. Tầng đối lưu sát mặt đất là nơi sinh ra mây, mưa và gió — vì gần như toàn bộ hơi nước đều nằm ở đó. Ngay phía trên là tầng bình lưu, nơi có lớp ôzôn hoạt động như một cặp kính râm khổng lồ chắn tia cực tím.",
           "Lên cao hơn nữa là tầng trung lưu. Mỗi vệt sao băng bạn thấy trên trời đêm chính là một mảnh đá vũ trụ đang cháy rụi ở đó, vì ma sát với các phân tử khí. Nhờ lớp áo ấy mà bề mặt Trái Đất không chi chít hố va chạm như Mặt Trăng."],
      en: ["Seen from space, Earth is wrapped in a thin blue band of gas. That is the atmosphere — the coat that keeps life safe in the cold emptiness around us.",
           "It is not one single gas. About 78% is nitrogen and about 21% is oxygen, the part that people and animals breathe every day. The last 1% is water vapour and a few other gases: a small share, but enough to help hold the planet's warmth.",
           "The atmosphere is stacked in layers. The troposphere, right at ground level, is where clouds, rain and wind are born — because nearly all the water vapour sits there. Just above it lies the stratosphere, home to the ozone layer, which works like a giant pair of sunglasses against ultraviolet rays.",
           "Higher still is the mesosphere. Every shooting star you spot at night is a piece of space rock burning up there, heated by friction with gas molecules. Thanks to that coat, Earth's surface is not pockmarked with craters the way the Moon is."]
    },
    term: { who: "comet", word: { vi: "Tầng đối lưu", en: "Troposphere" },
            text: { vi: "<b>Tầng đối lưu</b> là tầng khí quyển sát mặt đất — nơi có mây, mưa và gió. Bạn đang đứng trong nó ngay lúc này đấy! ☄️",
                    en: "The <b>troposphere</b> is the atmospheric layer closest to the ground — home to clouds, rain and wind. You are standing in it right now! ☄️" } },
    terms: ["atmo-comp-nitrogen", "atmo-tropo-weather", "atmo-strato-ozone", "atmo-meso-meteors"]
  },
  {
    id: "art-star-colors-temperature", src: "NASA", cat: "astronomy", em: "⭐",
    c: ["#ffd166", "#f77f00", "#d62828"],
    url: "https://science.nasa.gov/universe/stars/types/",
    img: null, credit: null,
    title: { vi: "Cầu vồng nhiệt độ của các vì sao",
             en: "The temperature rainbow of the stars" },
    body: {
      vi: ["Ngước nhìn trời đêm quang mây, bạn dễ nghĩ mọi ngôi sao đều trắng như nhau. Nhưng nhìn qua ống nhòm hay kính thiên văn, cả một dải màu hiện ra: xanh dương, trắng, vàng, cam, đỏ.",
           "Màu ấy không phải để trang trí. Nó chính là nhiệt độ bề mặt của ngôi sao. Và ở đây quy luật ngược hẳn với trực giác: sao xanh dương mới là sao nóng nhất, sao vàng như Mặt Trời ở mức trung bình, còn sao đỏ là nguội nhất.",
           "Hãy nhớ tới thanh sắt trong lò rèn. Mới nóng nó ửng đỏ, nóng hơn chuyển vàng, và nóng nhất thì trắng chói. Các vì sao chạy đúng thang màu đó — chỉ khác là chúng ở cách ta hàng nghìn năm ánh sáng.",
           "Chính vì vậy các nhà thiên văn đo được nhiệt độ một ngôi sao mà chưa từng tới gần nó. Họ chỉ cần đọc màu ánh sáng nó gửi tới. Một chùm ánh sáng đi hàng nghìn năm để tới mắt bạn, và nó vẫn mang theo tin tức về nơi nó xuất phát."],
      en: ["Look up on a clear night and every star seems the same shade of white. Put binoculars or a telescope in front of your eye, though, and a whole range appears: blue, white, yellow, orange, red.",
           "That colour is not decoration. It is the star's surface temperature. And the rule runs opposite to instinct: blue stars are the hottest, yellow stars like our Sun sit in the middle, and red stars are the coolest of all.",
           "Think of an iron bar in a blacksmith's forge. It glows dull red at first, turns yellow as it heats, and blazes white when it is hottest. Stars follow that very same scale — except they sit thousands of light-years away.",
           "This is how astronomers measure a star's temperature without ever going near it. They simply read the colour of the light it sends. A beam that travelled for thousands of years to reach your eye still carries news of where it began."]
    },
    term: { who: "byte", word: { vi: "Sao lùn đỏ", en: "Red dwarf" },
            text: { vi: "<b>Sao lùn đỏ</b> là loại sao nhỏ nhất và nguội nhất trong dải sao chính. Chúng đông nhất thiên hà, nhưng mờ tới mức mắt thường không thấy được. 🤖",
                    en: "A <b>red dwarf</b> is the smallest and coolest kind of main sequence star. They are the most common stars in the galaxy — yet too faint for the naked eye. 🤖" } },
    terms: ["star-color-temp-determine", "star-blue-hotter-red", "star-red-dwarf-coolest", "star-color-spectrum-order"]
  },
  {
    id: "art-solar-eclipse-dance", src: "NASA", cat: "astronomy", em: "☀️",
    c: ["#ff9f1c", "#ffbf69", "#2ec4b6"],
    url: "https://science.nasa.gov/eclipses/types/",
    img: null, credit: null,
    title: { vi: "Điệu nhảy bóng tối của nhật thực",
             en: "The shadow dance of a solar eclipse" },
    body: {
      vi: ["Nhật thực xảy ra khi Mặt Trăng đi vào đúng giữa Mặt Trời và Trái Đất, chắn ngang dòng ánh sáng và thả bóng của nó xuống hành tinh chúng ta.",
           "Điều kỳ lạ là nó xảy ra được. Mặt Trời rộng gấp 400 lần Mặt Trăng — nhưng cũng ở xa hơn đúng 400 lần. Hai con số triệt tiêu nhau, nên nhìn từ Trái Đất hai đĩa vừa khít. Không hành tinh nào khác trong hệ Mặt Trời có một vệ tinh đúng cỡ như vậy.",
           "Bóng Mặt Trăng có hai vùng. Vùng nửa tối rộng bên ngoài chạm tới Trái Đất trước, và ở đó Mặt Trời chỉ bị khuyết một góc, trông như lưỡi liềm. Đến đỉnh điểm, vùng bóng tối hẹp ở tâm mới quét qua — chỉ những ai đứng trong dải hẹp ấy mới thấy nhật thực toàn phần.",
           "Vài phút đó, ban ngày hoá hoàng hôn và vành nhật hoa trắng bạc của Mặt Trời hiện ra. ⛔ Nhưng nhớ kỹ: chỉ trong đúng khoảnh khắc Mặt Trời bị che kín hoàn toàn mới được nhìn bằng mắt thường. Chỉ cần một sợi ánh sáng ló ra, phải đeo kính lọc chuyên dụng ngay lập tức."],
      en: ["A solar eclipse happens when the Moon slides directly between the Sun and Earth, blocking the light and dropping its shadow onto our planet.",
           "The strange part is that it works at all. The Sun is 400 times wider than the Moon — and also sits 400 times farther away. The two numbers cancel out, so from Earth the discs look the same size. No other planet in the solar system has a moon that fits so exactly.",
           "The Moon's shadow comes in two parts. The wide, faint penumbra reaches Earth first, and there the Sun looks bitten into, like a crescent. Only at the peak does the narrow, dark umbra sweep past — and only people inside that thin track see a total eclipse.",
           "For those few minutes, daylight fades to dusk and the Sun's silver corona appears. ⛔ But remember: only during the moment the Sun is completely covered is it safe to look with bare eyes. The instant a sliver of light returns, proper solar filters go straight back on."]
    },
    term: { who: "comet", word: { vi: "Vành nhật hoa", en: "Corona" },
            text: { vi: "<b>Vành nhật hoa</b> là lớp khí ngoài cùng của Mặt Trời. Ngày thường nó bị ánh sáng bề mặt lấn át; chỉ khi nhật thực toàn phần nó mới hiện ra. ☄️",
                    en: "The <b>corona</b> is the Sun's outermost layer of gas. Normally the surface glare drowns it out — only during a total eclipse does it appear. ☄️" } },
    terms: ["eclipse-definition-moon-between", "eclipse-coincidence-size-distance-ratio", "eclipse-shadow-umbra-penumbra", "eclipse-safety-totality-viewing"]
  },
  {
    id: "art-blood-moon-lunar-eclipse", src: "NASA", cat: "astronomy", em: "🌕",
    c: ["#e63946", "#f1faee", "#1d3557"],
    url: "https://science.nasa.gov/moon/eclipses/",
    img: null, credit: null,
    title: { vi: "Vì sao Mặt Trăng hoá đỏ trong nguyệt thực",
             en: "Why the Moon turns red in an eclipse" },
    body: {
      vi: ["Nhật thực diễn ra ban ngày; nguyệt thực thì thuộc về ban đêm, và chỉ vào những đêm Trăng tròn. Khi đó Trái Đất nằm chính giữa Mặt Trời và Mặt Trăng, chắn không cho ánh sáng chiếu thẳng tới bề mặt Trăng.",
           "Nhưng Mặt Trăng không tối đen đi. Nó chuyển sang một sắc đỏ cam trầm, đến mức người ta gọi là Trăng Máu. Thủ phạm không nằm ở Mặt Trăng — mà ở bầu khí quyển của chính chúng ta.",
           "Ánh sáng Mặt Trời đi vòng qua rìa Trái Đất phải xuyên qua một lớp khí quyển rất dày. Lớp khí ấy tán xạ mất phần xanh và tím vì chúng có bước sóng ngắn, chỉ để lọt phần đỏ và cam bước sóng dài. Chính phần đỏ đó bẻ cong và rọi lên đĩa Trăng.",
           "Nếu hôm đó khí quyển nhiều bụi hoặc nhiều mây, Mặt Trăng sẽ đỏ đậm hơn. Và có một cách nghĩ rất đẹp về ánh đỏ ấy: đó là toàn bộ bình minh và hoàng hôn đang diễn ra khắp Trái Đất, cùng lúc chiếu lên một mặt trăng. Khác với nhật thực chỉ nhìn được trên một dải hẹp, cảnh này ai ở nửa cầu ban đêm cũng ngắm được."],
      en: ["Solar eclipses belong to the daytime; lunar eclipses belong to the night, and only to nights with a full moon. Earth moves directly between the Sun and the Moon, cutting off the light that would otherwise fall on the lunar surface.",
           "Yet the Moon does not go black. It shifts to a deep orange-red — deep enough that people call it a Blood Moon. The cause is not on the Moon at all. It is in our own atmosphere.",
           "Sunlight bending around the edge of Earth has to pass through a thick slice of air. That air scatters the blue and violet away, because their wavelengths are short, and lets the longer red and orange through. It is that red light which bends onward and lands on the Moon.",
           "If the atmosphere carries a lot of dust or cloud that night, the Moon turns a deeper red. And there is a lovely way to think about that glow: it is every sunrise and every sunset happening on Earth at once, all projected onto a single moon. Unlike a solar eclipse with its narrow track, anyone on the night side of the planet can watch."]
    },
    term: { who: "byte", word: { vi: "Bóng tối (umbra)", en: "Umbra" },
            text: { vi: "<b>Umbra</b> là vùng bóng tối đậm nhất. Mặt Trăng đi trọn vào đó thì có nguyệt thực toàn phần — và đó là lúc nó hoá đỏ. 🤖",
                    en: "The <b>umbra</b> is the darkest core of a shadow. When the Moon moves fully inside it we get a total lunar eclipse — and that is when it turns red. 🤖" } },
    terms: ["lunar-definition-earth-shadow", "lunar-phase-full-moon", "lunar-rayleigh-scattering-red-light", "lunar-sunrises-sunsets-projected"]
  },
  {
    id: "art-light-and-shadow-space", src: "NASA", cat: "astronomy", em: "🌌",
    c: ["#4a0e17", "#003049", "#fdf0d5"],
    url: "https://spaceplace.nasa.gov/eclipses/",
    img: null, credit: null,
    title: { vi: "Ánh sáng và bóng tối — hai thứ vũ trụ dạy ta",
             en: "Light and shadow — two lessons from space" },
    body: {
      vi: ["Ánh sáng Mặt Trời nhìn bằng mắt thường có màu trắng. Nhưng cho nó đi qua một lăng kính thuỷ tinh, nó tách ra thành cả dải cầu vồng — vì thứ ta gọi là màu trắng thật ra là nhiều bước sóng trộn lẫn.",
           "Trong dải nhìn thấy được, đỏ có bước sóng dài nhất còn tím có bước sóng ngắn nhất. Hai đầu ấy giải thích rất nhiều thứ: vì sao sao xanh nóng hơn sao đỏ, và vì sao Mặt Trăng hoá đỏ trong nguyệt thực chứ không hoá xanh.",
           "Còn bóng tối thì kể một câu chuyện khác. Trái Đất và Mặt Trăng cứ chuyển động theo chu kỳ, và thỉnh thoảng ba thiên thể xếp thẳng hàng — thế là có nhật thực hoặc nguyệt thực.",
           "Có một mẹo nhỏ để không bao giờ nhầm hai hiện tượng: tên gọi đã nói cho bạn biết thiên thể nào bị tối đi. Nhật thực thì Mặt Trời tối. Nguyệt thực thì Mặt Trăng tối. Chỉ vậy thôi."],
      en: ["Sunlight looks white to our eyes. Send it through a glass prism, though, and it fans out into a full rainbow — because what we call white is really many wavelengths mixed together.",
           "Across the visible range, red has the longest wavelength and violet the shortest. Those two ends explain a surprising amount: why blue stars burn hotter than red ones, and why the Moon turns red rather than blue during an eclipse.",
           "Shadow tells a different story. Earth and the Moon keep to their steady orbits, and every so often all three bodies line up — and we get a solar or a lunar eclipse.",
           "There is a small trick for never mixing the two up: the name tells you which body goes dark. In a solar eclipse, the Sun goes dark. In a lunar eclipse, the Moon goes dark. That is the whole rule."]
    },
    term: { who: "comet", word: { vi: "Bước sóng", en: "Wavelength" },
            text: { vi: "<b>Bước sóng</b> là khoảng cách giữa hai đỉnh sóng ánh sáng. Sóng dài cho màu đỏ, sóng ngắn cho màu tím — cả cầu vồng nằm ở giữa. ☄️",
                    en: "<b>Wavelength</b> is the distance between two crests of a light wave. Long waves look red, short waves look violet — the whole rainbow sits in between. ☄️" } },
    terms: ["star-prism-wavelengths", "star-visible-wavelength-range", "lunar-difference-name-darker", "eclipse-phase-new-moon"]
  }
  ];

  /* Bài cũ ↔ bài đã gộp. Chỉ dùng để ĐỌC LẠI lịch sử; bài mới không thêm vào đây. */
  var OLD_ID = { "gaia": "lib-gaia", "eht": "lib-blackhole", "exo-ai": "lib-exoplanet" };

  /* ───────── Trạng thái đã đọc — DÙNG CHUNG cho cả hai trang ─────────
     ⚠️ Trước đây ba hàm này được chép y hệt ở cả `learn.html` và `library.html`.
        Chúng phải giống nhau từng chữ, không thì lỗi ① ở trên quay lại — nên chúng
        thuộc về đây, không thuộc về từng trang. */
  var READ_KEY = "astroq-read";

  function readSet() {
    try { return JSON.parse(localStorage.getItem(READ_KEY) || "[]"); } catch (e) { return []; }
  }
  function isRead(id) {
    var s = readSet();
    if (s.indexOf(id) >= 0) return true;
    /* Bài này có phải bản gộp của một id cũ không? */
    for (var old in OLD_ID) {
      if (OLD_ID[old] === id && s.indexOf(old) >= 0) return true;
    }
    return false;
  }
  function markRead(id) {
    var s = readSet();
    if (s.indexOf(id) < 0) {
      s.push(id);
      try { localStorage.setItem(READ_KEY, JSON.stringify(s)); } catch (e) {}
    }
  }

  /* ───────── Chọn bài nổi bật — DÙNG CHUNG ─────────
     Ưu tiên bài CHƯA ĐỌC (giữ thứ tự khai báo), thiếu thì lấy thêm bài đã đọc cho đủ n
     — nên con số n không bao giờ hụt kể cả khi trẻ đã đọc hết.
     ⚠️ Chỗ gọi phải tính MỘT LẦN lúc mở trang. Tính lại sau mỗi lần đánh dấu đã đọc thì
        bài vừa đọc biến khỏi khối nổi bật ngay dưới tay trẻ và cả khối nhảy chỗ. */
  function featured(n) {
    var unread = [], seen = [];
    for (var i = 0; i < ARTICLES.length; i++) {
      (isRead(ARTICLES[i].id) ? seen : unread).push(ARTICLES[i]);
    }
    return unread.concat(seen).slice(0, Math.min(n, ARTICLES.length));
  }

  window.AstroQArticles = {
    all: function () { return ARTICLES.slice(); },
    featured: featured,
    byId: function (id) {
      for (var i = 0; i < ARTICLES.length; i++) if (ARTICLES[i].id === id) return ARTICLES[i];
      return null;
    },
    readSet: readSet,
    isRead: isRead,
    markRead: markRead,
    READ_KEY: READ_KEY
  };
})();
