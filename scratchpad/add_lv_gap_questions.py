# -*- coding: utf-8 -*-
"""add_lv_gap_questions.py — 20 CAU MOI, dung vao 20 CHO THIEU do `gap_lv.py` chi ra.

VI SAO CHON DUNG 20 CAU NAY (chot 19/08/2026):
  Tu khi `pickKeys(n, lv)` doc `lv` ("vai (2)"), mot the thieu mot cap la mot the
  ma o cap do dua tre phai nhan cau KHONG dung suc minh (duong lui `nearest()` lay
  cau gan cap nhat). Do duoc: 20 cho thieu tren 18/23 the. Nen "tra no noi dung"
  o luot nay KHONG phai rai deu cho du so, ma la LAP KIN dung 20 cho ay — sau luot
  nay moi the deu co du ca ba cap va duong lui thanh du phong that su.

MOI CAU DEU CO NGUON THAT:
  `src` tro vao bang S san co (khong them nguon moi — 13 trang nay da nam trong S),
  `srcQuote` la cau NGUYEN VAN doc tu trang goc ngay 19/08/2026, `srcChecked` la
  ngay do. `check_srcquote.py` doi chieu lai voi trang song nen mot chu thua/thieu
  la bao hong.
  ⚠️ Da mo TUNG trang trong 13 trang de lay cau dan, khong lay tu ky uc. Ba cho
     trang KHONG noi dieu toi can (cach ve tinh hinh thanh; vi sao ngoai hanh tinh
     kho thay truc tiep; gioi han cua AI) thi KHONG viet cau hoi ve dieu do.

TIEU CHI CAP DO (giu y nguyen `setlv.py` da dung cho 106 cau truoc):
  lv1 nhan biet — cau tra loi nam ngay trong mot cau cua trang nguon
  lv2 phan biet hai khai niem gan nhau, hoac nho mot ten/con so/vi tri cu the
  lv3 giai thich co che, hoac dinh nghia bang loai tru

⚠️ CHAY MOT LAN. Script tu dung neu file da ton tai (khong ghi de cau da co).
⚠️ Sau khi chay: `python scratchpad/split_quiz_bank.py` de sinh lai muc luc.
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKED = "2026-08-19"

TOPIC = {
    "term_star": ("NGÔI SAO", "STAR"),
    "term_planet": ("HÀNH TINH", "PLANET"),
    "term_dwarf_planet": ("HÀNH TINH LÙN", "DWARF PLANET"),
    "term_moon": ("VỆ TINH TỰ NHIÊN", "NATURAL SATELLITE"),
    "term_asteroid": ("TIỂU HÀNH TINH", "ASTEROID"),
    "term_comet": ("SAO CHỔI", "COMET"),
    "term_meteoroid": ("THIÊN THẠCH NHỎ", "METEOROID"),
    "term_meteor": ("SAO BĂNG", "METEOR"),
    "term_meteorite": ("THIÊN THẠCH", "METEORITE"),
    "term_exoplanet": ("NGOẠI HÀNH TINH", "EXOPLANET"),
    "term_black_hole": ("LỖ ĐEN", "BLACK HOLE"),
    "term_gravity": ("LỰC HẤP DẪN", "GRAVITY"),
    "term_nebula": ("TINH VÂN", "NEBULA"),
    "term_supernova": ("SIÊU TÂN TINH", "SUPERNOVA"),
    "term_cmb": ("BỨC XẠ NỀN VŨ TRỤ", "COSMIC MICROWAVE BACKGROUND"),
    "term_ai": ("TRÍ TUỆ NHÂN TẠO", "ARTIFICIAL INTELLIGENCE"),
    "term_machine_learning": ("HỌC MÁY", "MACHINE LEARNING"),
    "term_sensor": ("CẢM BIẾN", "SENSORS"),
}

Q = [
 # ═══════════════════════════ 8 cho thieu CAP 3 ═══════════════════════════
 dict(key="star-mass-life", card="term_star", lv=3, src="star", a=1,
  q=("Hai ngôi sao cùng sinh ra một lúc, nhưng một ngôi nặng gấp nhiều lần ngôi kia. Ngôi NẶNG hơn sẽ sống lâu hơn hay ngắn hơn?",
     "Two stars are born at the same time, but one is many times heavier than the other. Will the HEAVIER one live longer or shorter?"),
  opts=[("Lâu hơn, vì nó có nhiều nhiên liệu hơn", "Longer, because it has more fuel"),
        ("Ngắn hơn, vì nó đốt nhiên liệu nhanh hơn rất nhiều", "Shorter, because it burns through its fuel far faster"),
        ("Bằng nhau — khối lượng không liên quan", "The same — mass has nothing to do with it"),
        ("Lâu hơn, vì nó nóng hơn", "Longer, because it is hotter")],
  ok=("Đúng rồi! Khối lượng quyết định ngôi sao <b>đốt hết nhiên liệu nhanh cỡ nào</b>. Sao nhẹ cháy <b>lâu hơn, mờ hơn và mát hơn</b>; sao rất nặng thì sáng chói nhưng tiêu hết nhiên liệu rất nhanh — nhiều nhiên liệu mà đốt quá nhanh thì vẫn hết sớm.",
      "Right! Mass decides <b>how fast a star runs through its fuel</b>. Low-mass stars burn <b>longer, dimmer and cooler</b>; very massive stars blaze bright but use up their supply fast — plenty of fuel burned far too quickly still runs out sooner."),
  no=("Chưa đúng! Sao nặng <b>có</b> nhiều nhiên liệu hơn thật, nhưng nó phải đốt nhanh hơn nhiều để không sụp xuống dưới sức nặng của chính mình. NASA cho biết sao nhẹ cháy <b>lâu hơn, mờ hơn, mát hơn</b>.",
      "Not quite! A massive star <b>does</b> have more fuel, but it must burn it far faster to keep from collapsing under its own weight. NASA says lower-mass stars burn <b>longer, dimmer and cooler</b>."),
  hint=("Nhiều nhiên liệu nhưng đốt cực nhanh — nghĩ tới cây nến to bị thắp <b>hai đầu</b>.",
        "Lots of fuel but burning very fast — think of a big candle lit at <b>both ends</b>."),
  quote="A star's gas provides its fuel, and its mass determines how rapidly it runs through its supply, with lower-mass stars burning longer, dimmer, and cooler than very massive stars."),

 dict(key="moon-most-not-planets", card="term_moon", lv=3, src="moon", a=1,
  q=("NASA đếm được 421 vệ tinh quay quanh các hành tinh, và hơn 470 vệ tinh quay quanh hành tinh lùn, tiểu hành tinh và các vật thể ngoài Sao Hải Vương. Vậy điều nào đúng?",
     "NASA counts 421 moons orbiting planets, and more than 470 moons orbiting dwarf planets, asteroids and trans-Neptunian objects. So which statement is true?"),
  opts=[("Phần lớn vệ tinh quay quanh các hành tinh", "Most moons orbit planets"),
        ("Phần lớn vệ tinh KHÔNG quay quanh hành tinh nào", "Most moons do NOT orbit a planet"),
        ("Chỉ hành tinh mới có vệ tinh", "Only planets can have moons"),
        ("Hai con số đó bằng nhau", "The two counts are equal")],
  ok=("Đúng! Hơn 470 nhiều hơn 421, nên <b>quá nửa số vệ tinh đã xác nhận lại quay quanh những thứ không phải hành tinh</b> — hành tinh lùn, tiểu hành tinh và các vật thể ngoài Sao Hải Vương. Có vệ tinh không phải đặc quyền của hành tinh.",
      "Yes! More than 470 beats 421, so <b>over half of all confirmed moons orbit things that are not planets</b> — dwarf planets, asteroids and trans-Neptunian objects. Having moons is not a planets-only privilege."),
  no=("Chưa đúng! Cứ so hai con số: 421 quay quanh hành tinh, <b>hơn 470</b> quay quanh các vật thể khác — vậy phần lớn vệ tinh <b>không</b> thuộc về hành tinh nào.",
      "Not quite! Just compare: 421 orbit planets, <b>more than 470</b> orbit other bodies — so most moons <b>don't</b> belong to a planet."),
  hint=("Đọc kỹ hai con số trong câu hỏi rồi xem bên nào lớn hơn.",
        "Read the two numbers in the question, then see which is bigger."),
  quote="Of those, 421 moons are orbiting planets (including Pluto). More than 470 moons are orbiting other dwarf planets, asteroids and trans-Neptunian objects (TNOs)."),

 dict(key="asteroid-jupiter-stopped", card="term_asteroid", lv=3, src="aster", a=1,
  q=("Vì sao đám vật thể ở vành đai tiểu hành tinh không gộp lại thành một hành tinh?",
     "Why did the bodies in the asteroid belt never come together into a planet?"),
  opts=[("Vì chỗ đó quá lạnh để đá dính được vào nhau", "Because it is too cold there for rock to stick together"),
        ("Vì lực hấp dẫn của Sao Mộc vừa hình thành đã chặn lại", "Because the gravity of newly formed Jupiter put a stop to it"),
        ("Vì tổng khối lượng ở đó lớn quá", "Because there is far too much total mass there"),
        ("Vì Mặt Trời hút hết vật chất về phía mình", "Because the Sun pulled all the material inward")],
  ok=("Chính xác! NASA cho biết ngay thời kỳ đầu của hệ Mặt Trời, <b>lực hấp dẫn của Sao Mộc vừa hình thành đã chấm dứt việc tạo hành tinh ở vùng đó</b>, đồng thời làm các vật thể nhỏ va vào nhau và vỡ ra thành những tiểu hành tinh ta thấy hôm nay.",
      "Exactly! NASA says that early in the solar system's history, <b>the gravity of newly formed Jupiter brought an end to planet formation in that region</b> and made the small bodies collide, fragmenting them into the asteroids we see today."),
  no=("Chưa đúng! Nguyên nhân là <b>lực hấp dẫn của Sao Mộc</b>. Ngược lại, tổng khối lượng ở vành đai rất NHỎ — cộng hết tiểu hành tinh lại vẫn nhẹ hơn Mặt Trăng của Trái Đất.",
      "Not quite! The cause is <b>Jupiter's gravity</b>. In fact the belt's total mass is tiny — all the asteroids combined weigh less than Earth's Moon."),
  hint=("Hành tinh lớn nhất hệ Mặt Trời nằm ngay sát vành đai ấy.",
        "The largest planet in the solar system sits right next to that belt."),
  quote="Early in the history of the solar system, the gravity of newly formed Jupiter brought an end to the formation of planetary bodies in this region and caused the small bodies to collide with one another, fragmenting them into the asteroids we observe today."),

 dict(key="exo-rogue", card="term_exoplanet", lv=3, src="exo", a=1,
  q=("Hầu hết ngoại hành tinh đều quay quanh một ngôi sao. Nhưng có loại không thuộc về ngôi sao nào cả — NASA gọi chúng là gì?",
     "Most exoplanets orbit a star. But some belong to no star at all — what does NASA call those?"),
  opts=[("Hành tinh lùn", "Dwarf planets"),
        ("Hành tinh lang thang (rogue planet)", "Rogue planets"),
        ("Sao chổi khổng lồ", "Giant comets"),
        ("Chúng không được coi là ngoại hành tinh", "They don't count as exoplanets")],
  ok=("Đúng! NASA gọi chúng là <b>rogue planet — hành tinh lang thang</b>: bay tự do, <b>không bị ràng vào ngôi sao nào</b>. Và chúng <b>vẫn</b> được tính là ngoại hành tinh, vì định nghĩa chỉ đòi “ở ngoài hệ Mặt Trời của chúng ta”.",
      "Yes! NASA calls them <b>rogue planets</b>: free-floating and <b>untethered to any star</b>. They still <b>do</b> count as exoplanets, because the definition only asks that they lie beyond our solar system."),
  no=("Chưa đúng! Chúng là <b>hành tinh lang thang (rogue planet)</b>. Điểm hay là chúng vẫn được coi là ngoại hành tinh — định nghĩa của NASA là “bất kỳ hành tinh nào ở ngoài hệ Mặt Trời”, không đòi phải có sao chủ.",
      "Not quite! They are <b>rogue planets</b>. The neat part: they still count as exoplanets — NASA's definition is “any planet beyond our solar system”, with no host star required."),
  hint=("Một từ tiếng Anh chỉ kẻ đi lang thang, không theo ai.",
        "An English word for a wanderer who follows nobody."),
  quote="An exoplanet is any planet beyond our solar system. Most of them orbit other stars, but some free-floating exoplanets, called rogue planets, are untethered to any star."),

 dict(key="bh-horizon-boundary", card="term_black_hole", lv=3, src="bh", a=1,
  q=("Chân trời sự kiện KHÔNG phải một bề mặt rắn như mặt đất của Trái Đất hay bề mặt Mặt Trời. Vậy nó là gì?",
     "The event horizon is NOT a solid surface like Earth's or the Sun's. So what is it?"),
  opts=[("Một lớp vỏ đá bao quanh lỗ đen", "A rocky shell around the black hole"),
        ("Một đường biên chứa toàn bộ vật chất làm nên lỗ đen", "A boundary that contains all the matter making up the black hole"),
        ("Một luồng khí nóng đang xoáy", "A swirling jet of hot gas"),
        ("Chỗ để hướng kính viễn vọng vào quan sát", "The spot telescopes are aimed at")],
  ok=("Chính xác! NASA nói chân trời sự kiện <b>không phải một bề mặt</b> — nó là <b>một đường biên chứa toàn bộ vật chất làm nên lỗ đen</b>. Vượt qua đường biên ấy thì không gì, kể cả ánh sáng, quay ra được nữa.",
      "Exactly! NASA says the event horizon <b>isn't a surface</b> — it is <b>a boundary that contains all the matter that makes up the black hole</b>. Past that line nothing, not even light, gets back out."),
  no=("Chưa đúng! Đó không phải vật rắn nào cả: chân trời sự kiện là <b>một đường biên</b> — ranh giới bao lấy toàn bộ vật chất của lỗ đen, cũng là chỗ ánh sáng không thoát ra được.",
      "Not quite! It isn't a solid thing at all: the event horizon is <b>a boundary</b> — the line enclosing all the black hole's matter, and the line light cannot cross outward."),
  hint=("Nó là một ranh giới, không phải một thứ ta có thể đứng lên.",
        "It's a line, not something you could stand on."),
  quote="The event horizon isn't a surface like Earth's or even the Sun's. It's a boundary that contains all the matter that makes up the black hole."),

 dict(key="grav-two-rules", card="term_gravity", lv=3, src="grav", a=2,
  q=("NASA nêu hai quy tắc: vật có khối lượng lớn hơn thì hấp dẫn mạnh hơn, và hấp dẫn yếu đi khi ở xa. Vậy lực hấp dẫn mà một vật cảm nhận được phụ thuộc vào điều gì?",
     "NASA gives two rules: objects with more mass have more gravity, and gravity gets weaker with distance. So what does the gravity an object feels depend on?"),
  opts=[("Chỉ khối lượng", "Mass only"),
        ("Chỉ khoảng cách", "Distance only"),
        ("Cả khối lượng lẫn khoảng cách", "Both mass and distance"),
        ("Không phụ thuộc gì — ở đâu hấp dẫn cũng như nhau", "Neither — gravity is the same everywhere")],
  ok=("Đúng! <b>Cả hai</b> đều tính. Mặt Trời nặng hơn Trái Đất cực nhiều nhưng ở rất xa; Trái Đất nhẹ hơn nhiều nhưng ở ngay dưới chân ta — nên chính Trái Đất mới là thứ giữ ta đứng trên mặt đất.",
      "Yes! <b>Both</b> count. The Sun is vastly heavier than Earth but very far away; Earth is far lighter but right under your feet — which is why Earth is what keeps you on the ground."),
  no=("Chưa đúng! Phải tính <b>cả hai</b>: khối lượng càng lớn thì hấp dẫn càng mạnh, <b>và</b> càng ra xa thì hấp dẫn càng yếu. Bỏ một trong hai là trả lời sai ngay câu “vì sao ta không bị Mặt Trời hút bay đi”.",
      "Not quite! You need <b>both</b>: more mass means more gravity, <b>and</b> gravity weakens with distance. Drop either one and you can't answer “why doesn't the Sun pull us away”."),
  hint=("Hai quy tắc, không phải một — cả hai được nhắc trong cùng một đoạn.",
        "Two rules, not one — both appear in the same passage."),
  quote="Objects with more mass have more gravity. Gravity also gets weaker with distance."),

 dict(key="ai-why-fast", card="term_ai", lv=3, src="aiHubble", a=1,
  q=("Vì sao các nhà thiên văn để AI soi hàng chục nghìn ảnh Hubble thay vì tự xem từng ảnh?",
     "Why do astronomers let AI comb through tens of thousands of Hubble images instead of looking at each one themselves?"),
  opts=[("Vì AI thấy được những thứ mắt người không bao giờ thấy", "Because AI can see things human eyes never could"),
        ("Vì người sẽ mất vô số giờ, còn AI nhận ra mẫu rất nhanh", "Because people would need countless hours, while AI recognises patterns fast"),
        ("Vì AI không bao giờ sai", "Because AI never makes mistakes"),
        ("Vì ảnh Hubble quá mờ, người không xem được", "Because Hubble images are too blurry for people")],
  ok=("Đúng! NASA nói thẳng: <b>người sẽ phải mất vô số giờ</b> để soi hết dữ liệu của nhiều năm quan sát, còn <b>AI dùng nhận dạng mẫu để chỉ ra nhanh những phần đáng chú ý</b>. Lợi thế ở đây là <b>khối lượng và tốc độ</b>, chứ không phải AI thấy được điều con người không thấy.",
      "Yes! NASA puts it plainly: <b>it would take countless hours for individuals</b> to sort through years of observations, while <b>AI uses pattern recognition to swiftly identify key components</b>. The advantage is <b>volume and speed</b>, not seeing what humans cannot."),
  no=("Chưa đúng! Lý do là <b>khối lượng công việc</b>: hàng chục nghìn ảnh thì người soi hết sẽ mất vô số giờ. AI nhanh, nhưng nó <b>không</b> phải thứ không bao giờ sai — chính dự án đó vẫn cần hàng nghìn người tình nguyện cùng kiểm.",
      "Not quite! The reason is <b>sheer volume</b>: tens of thousands of images would take a person countless hours. AI is fast, but it is <b>not</b> infallible — that very project still needed thousands of volunteers checking alongside it."),
  hint=("Thử nhân xem: 30.000 ảnh, mỗi ảnh vài phút thì mất bao lâu?",
        "Do the multiplication: 30,000 images at a few minutes each is how long?"),
  quote="But while it would take countless hours for individuals to sort through information from years of observations, artificial intelligence (AI) programs can use pattern recognition to swiftly identify key components."),

 dict(key="sensor-why-autonomous", card="term_sensor", lv=3, src="astrobee", a=1,
  q=("Astrobee có thể làm việc TỰ ĐỘNG, không cần ai điều khiển từng động tác. Vì sao khi đó cảm biến lại càng quan trọng?",
     "Astrobee can work AUTONOMOUSLY, with nobody steering each move. Why do sensors matter even more then?"),
  opts=[("Vì cảm biến làm robot bay nhanh hơn", "Because sensors make the robot fly faster"),
        ("Vì không có người chỉ đường, robot phải tự nhận biết xung quanh mới đi được", "Because with nobody guiding it, the robot must sense its surroundings to move at all"),
        ("Vì cảm biến thay cho pin", "Because sensors take the place of the battery"),
        ("Vì phi hành gia thích tiếng cảm biến kêu", "Because the astronauts like the sound sensors make")],
  ok=("Chính xác! Astrobee <b>làm việc tự động HOẶC do người điều khiển từ xa</b>. Khi tự động thì không ai nói cho nó biết phía trước có gì, nên nó phải <b>tự “nhìn” bằng camera và cảm biến</b> để định hướng — cảm biến chính là cặp mắt của nó.",
      "Exactly! Astrobee works <b>autonomously or via remote control</b>. When it's on its own, nobody tells it what lies ahead, so it must <b>“see” for itself with cameras and sensors</b> — the sensors are its eyes."),
  no=("Chưa đúng! Cảm biến không phải để bay nhanh hay để thay pin. Khi <b>không có người điều khiển</b>, robot chỉ còn cách <b>tự nhận biết xung quanh</b> — và đó đúng là việc của cảm biến.",
      "Not quite! Sensors aren't for speed or for replacing the battery. With <b>nobody at the controls</b>, the robot's only option is to <b>sense its surroundings itself</b> — which is exactly a sensor's job."),
  hint=("Nếu bịt mắt bạn rồi bảo bạn tự đi trong một căn phòng lạ thì sao?",
        "What if someone blindfolded you and asked you to cross an unfamiliar room?"),
  quote="Working autonomously or via remote control by astronauts, flight controllers or researchers on the ground, the robots are designed to complete tasks"),

 # ═══════════════════════════ 6 cho thieu CAP 2 ═══════════════════════════
 dict(key="planet-ice-giants", card="term_planet", lv=2, src="planet", a=1,
  q=("Sao Mộc và Sao Thổ được gọi là hành tinh khí khổng lồ. Còn Sao Thiên Vương và Sao Hải Vương thì NASA gọi là gì?",
     "Jupiter and Saturn are called gas giants. So what does NASA call Uranus and Neptune?"),
  opts=[("Hành tinh đá", "Rocky planets"),
        ("Hành tinh băng khổng lồ", "Ice giants"),
        ("Hành tinh lùn", "Dwarf planets"),
        ("Cũng là hành tinh khí khổng lồ", "Gas giants as well")],
  ok=("Chính xác! <b>Sao Mộc và Sao Thổ là hành tinh khí khổng lồ; Sao Thiên Vương và Sao Hải Vương là hành tinh băng khổng lồ.</b> Cả bốn đều không có bề mặt rắn để đứng lên — chỉ là khí xoáy trên một lõi.",
      "Exactly! <b>Jupiter and Saturn are gas giants; Uranus and Neptune are ice giants.</b> None of the four has a hard surface to stand on — just swirling gases above a core."),
  no=("Chưa đúng! Bốn hành tinh ngoài đều khổng lồ và đều không có mặt đất rắn, nhưng NASA chia làm hai loại: <b>khí</b> (Sao Mộc, Sao Thổ) và <b>băng</b> (Sao Thiên Vương, Sao Hải Vương).",
      "Not quite! All four outer planets are giants without hard surfaces, but NASA splits them in two: <b>gas</b> (Jupiter, Saturn) and <b>ice</b> (Uranus, Neptune)."),
  hint=("Hai hành tinh xa nhất thì lạnh nhất — tên loại của chúng cũng lạnh.",
        "The two farthest planets are the coldest — and their group name is cold too."),
  quote="Jupiter and Saturn are gas giants. Uranus and Neptune are ice giants."),

 dict(key="comet-two-tails", card="term_comet", lv=2, src="comet", a=1,
  q=("Một sao chổi thực ra có mấy cái đuôi?",
     "How many tails does a comet actually have?"),
  opts=[("Một đuôi duy nhất", "Just one"),
        ("Hai đuôi: một đuôi bụi và một đuôi ion (khí)", "Two: a dust tail and an ion (gas) tail"),
        ("Ba đuôi", "Three"),
        ("Không có đuôi nào — đó chỉ là ảo giác", "None — the tail is an illusion")],
  ok=("Đúng! NASA nói sao chổi thực ra có <b>hai đuôi: một đuôi bụi và một đuôi ion (khí)</b>. Trong những bức ảnh đẹp, đôi khi ta thấy rõ hai vệt riêng hơi lệch nhau.",
      "Yes! NASA says comets actually have <b>two tails — a dust tail and an ion (gas) tail</b>. In good photographs you can sometimes make out two separate streaks at slightly different angles."),
  no=("Chưa đúng! Sao chổi có <b>hai</b> đuôi — <b>đuôi bụi</b> và <b>đuôi ion (khí)</b>.",
      "Not quite! A comet has <b>two</b> tails — a <b>dust tail</b> and an <b>ion (gas) tail</b>."),
  hint=("Bụi và khí bay theo hai kiểu khác nhau, nên chúng không nằm chồng lên nhau.",
        "Dust and gas get pushed in different ways, so they don't lie on top of each other."),
  quote="Comets actually have two tails – a dust tail and an ion (gas) tail."),

 dict(key="meteoroid-daily-mass", card="term_meteoroid", lv=2, src="meteor", a=1,
  q=("Các nhà khoa học ước tính mỗi NGÀY có khoảng bao nhiêu vật chất từ không gian rơi xuống Trái Đất?",
     "Scientists estimate roughly how much space material falls on Earth each DAY?"),
  opts=[("Khoảng 1 kg", "About 1 kilogram"),
        ("Khoảng 48,5 tấn (44.000 kg)", "About 48.5 tons (44,000 kilograms)"),
        ("Khoảng 5 triệu tấn", "About 5 million tons"),
        ("Gần như không có gì", "Almost nothing at all")],
  ok=("Đúng! NASA ước tính khoảng <b>48,5 tấn (44.000 kg)</b> vật chất từ không gian rơi xuống Trái Đất <b>mỗi ngày</b> — phần lớn là hạt bụi cháy hết trên cao nên ta không hề hay biết.",
      "Yes! NASA estimates about <b>48.5 tons (44,000 kilograms)</b> of meteoritic material falls on Earth <b>every day</b> — mostly dust grains that burn up high above us, unnoticed."),
  no=("Chưa đúng! Con số NASA đưa ra là khoảng <b>48,5 tấn mỗi ngày</b>. Nghe nhiều, nhưng gần hết là bụi mịn tan trong khí quyển.",
      "Not quite! NASA's figure is about <b>48.5 tons per day</b>. It sounds like a lot, but nearly all of it is fine dust that burns up in the atmosphere."),
  hint=("Nặng hơn một con voi, nhẹ hơn một toà nhà — và là mỗi ngày.",
        "Heavier than an elephant, lighter than a building — and that's per day."),
  quote="Scientists estimate that about 48.5 tons (44,000 kilograms) of meteoritic material falls on Earth each day."),

 dict(key="nebula-planetary", card="term_nebula", lv=2, src="star", a=0,
  q=("“Tinh vân hành tinh” (planetary nebula) thực ra là gì?",
     "What is a “planetary nebula” actually?"),
  opts=[("Đám mây khí bụi do một ngôi sao già thổi các lớp ngoài của mình bay ra", "The cloud of gas and dust an aging star blows off from its outer layers"),
        ("Một đám mây đang tạo ra các hành tinh mới", "A cloud that is making new planets"),
        ("Vành đai bụi quanh một hành tinh", "A dust ring around a planet"),
        ("Một hành tinh lớn bị bao trong sương mù", "A large planet wrapped in fog")],
  ok=("Đúng — và đây là cái tên gây hiểu lầm bậc nhất trong thiên văn! NASA cho biết cuối đời một ngôi sao, <b>toàn bộ các lớp ngoài của nó bay đi, tạo thành một đám mây khí bụi đang giãn ra gọi là tinh vân hành tinh</b>. Nó <b>chẳng liên quan gì tới hành tinh</b> — chỉ vì qua kính thời xưa nó trông tròn như một hành tinh.",
      "Yes — and it's astronomy's most misleading name! NASA says that at the end of a star's life <b>all its outer layers blow away, creating an expanding cloud of dust and gas called a planetary nebula</b>. It has <b>nothing to do with planets</b> — early telescopes just made it look round like one."),
  no=("Chưa đúng! Cái tên rất dễ lừa: tinh vân hành tinh <b>không tạo ra hành tinh nào</b>. Đó là <b>các lớp ngoài mà một ngôi sao sắp tàn thổi bay ra</b>.",
      "Not quite! The name is a trap: a planetary nebula <b>makes no planets</b>. It is <b>the outer layers a dying star has blown away</b>."),
  hint=("Đừng tin cái tên — hãy hỏi ngôi sao đang ở giai đoạn nào của đời mình.",
        "Don't trust the name — ask what stage of life the star is in."),
  quote="Eventually, all the star's outer layers blow away, creating an expanding cloud of dust and gas called a planetary nebula."),

 dict(key="cmb-oldest-light", card="term_cmb", lv=2, src="cosmos", a=0,
  q=("Bức xạ nền vũ trụ giữ “kỷ lục” gì trong mọi thứ ta quan sát được?",
     "What “record” does the cosmic microwave background hold among everything we can observe?"),
  opts=[("Là ánh sáng CỔ NHẤT ta quan sát được", "It is the OLDEST light we can observe"),
        ("Là ánh sáng sáng nhất trên trời", "It is the brightest light in the sky"),
        ("Là ánh sáng gần Trái Đất nhất", "It is the closest light to Earth"),
        ("Là ánh sáng nóng nhất từng đo được", "It is the hottest light ever measured")],
  ok=("Đúng! NASA nói bức xạ nền vũ trụ là <b>ánh sáng cổ nhất mà ta quan sát được trong vũ trụ</b> — thứ ánh sáng ấy lên đường từ khi vũ trụ còn rất trẻ, và đến nay vẫn còn dò được.",
      "Yes! NASA says the cosmic microwave background is <b>the oldest light we can observe in the universe</b> — light that set out when the universe was very young, and is still detectable today."),
  no=("Chưa đúng! Nó không phải sáng nhất hay nóng nhất, mà là <b>cổ nhất</b>: ánh sáng xưa nhất ta quan sát được trong vũ trụ.",
      "Not quite! It isn't the brightest or hottest — it is the <b>oldest</b>: the most ancient light we can observe in the universe."),
  hint=("Nghĩ về TUỔI của ánh sáng, không phải độ sáng của nó.",
        "Think about the light's AGE, not its brightness."),
  quote="This glow, still detectable today, is called the cosmic microwave background. It is the oldest light we can observe in the universe."),

 dict(key="sensor-fans-move", card="term_sensor", lv=2, src="astrobee", a=1,
  q=("Robot Astrobee dùng quạt điện để làm gì?",
     "What do Astrobee robots use their electric fans for?"),
  opts=[("Để “nhìn” xung quanh", "To “see” their surroundings"),
        ("Để bay đi trong môi trường vi trọng lực của trạm", "To fly through the station's microgravity"),
        ("Để làm mát cho các phi hành gia", "To cool the astronauts down"),
        ("Để gửi tín hiệu về Trái Đất", "To send signals back to Earth")],
  ok=("Đúng! Astrobee <b>dùng quạt điện làm hệ đẩy để bay tự do trong môi trường vi trọng lực</b> của trạm. Còn việc “nhìn” và định hướng là phần của <b>camera và cảm biến</b> — hai bộ phận, hai việc khác nhau.",
      "Yes! Astrobee <b>uses electric fans as a propulsion system to fly freely through the station's microgravity</b>. “Seeing” and navigating is the job of its <b>cameras and sensors</b> — different parts, different jobs."),
  no=("Chưa đúng! Quạt điện là để <b>di chuyển</b>. Để “nhìn” và tìm đường thì Astrobee dùng <b>camera và cảm biến</b>.",
      "Not quite! The fans are for <b>moving</b>. For “seeing” and finding its way, Astrobee uses <b>cameras and sensors</b>."),
  hint=("Trong không gian không có mặt đất để đạp chân — muốn đi thì phải đẩy không khí.",
        "In space there's no floor to push off — to move, you push air."),
  quote="The robots use electric fans as a propulsion system that allows them to fly freely through the microgravity environment of the station."),

 # ═══════════════════════════ 6 cho thieu CAP 1 ═══════════════════════════
 dict(key="dwarf-pluto", card="term_dwarf_planet", lv=1, src="dwarf", a=1,
  q=("Sao Diêm Vương (Pluto) hiện được xếp vào nhóm nào?",
     "What group is Pluto classified in today?"),
  opts=[("Hành tinh", "A planet"),
        ("Hành tinh lùn", "A dwarf planet"),
        ("Vệ tinh của Sao Hải Vương", "A moon of Neptune"),
        ("Sao chổi", "A comet")],
  ok=("Đúng! Pluto là một trong <b>năm hành tinh lùn</b> mà IAU đã công nhận. Tính từ Mặt Trời ra, năm cái đó là <b>Ceres, Pluto, Haumea, Makemake và Eris</b>.",
      "Yes! Pluto is one of the <b>five dwarf planets</b> the IAU recognises. In order of distance from the Sun they are <b>Ceres, Pluto, Haumea, Makemake and Eris</b>."),
  no=("Chưa đúng! Pluto là <b>hành tinh lùn</b>, cùng nhóm với Ceres, Haumea, Makemake và Eris.",
      "Not quite! Pluto is a <b>dwarf planet</b>, in the same group as Ceres, Haumea, Makemake and Eris."),
  hint=("Nó gần thành hành tinh — chỉ thiếu đúng một bước.",
        "It almost qualifies as a planet — it just misses one step."),
  quote="In order of distance from the Sun they are: Ceres, Pluto, Haumea, Makemake, and Eris."),

 dict(key="meteor-where", card="term_meteor", lv=1, src="meteor", a=1,
  q=("Hiện tượng meteor (sao băng) xảy ra ở đâu?",
     "Where does a meteor happen?"),
  opts=[("Ngoài không gian, giữa các hành tinh", "Out in space, between the planets"),
        ("Trong khí quyển", "In the atmosphere"),
        ("Trên mặt đất", "On the ground"),
        ("Trong lõi Mặt Trời", "Inside the Sun's core")],
  ok=("Đúng! Chỉ khi hòn đá không gian <b>lao vào khí quyển</b> và cháy lên thì nó mới được gọi là <b>meteor</b>. Lúc còn bay ngoài không gian nó là <b>meteoroid</b>.",
      "Yes! Only when a space rock <b>enters the atmosphere</b> and burns up is it called a <b>meteor</b>. While still out in space it is a <b>meteoroid</b>."),
  no=("Chưa đúng! Meteor là chuyện xảy ra <b>trong khí quyển</b> — đó chính là lúc hòn đá cháy sáng thành một vệt.",
      "Not quite! A meteor happens <b>in the atmosphere</b> — that's the moment the rock burns into a streak of light."),
  hint=("Ta ngắm sao băng từ mặt đất bằng mắt thường, nên nó phải cháy ở tầng khí ngay trên đầu ta.",
        "We watch meteors from the ground with the naked eye, so they must burn in the air above us."),
  quote="When meteoroids enter Earth's atmosphere, or that of another planet, at high speed and burn up, they're called meteors."),

 dict(key="meteorite-name", card="term_meteorite", lv=1, src="meteor", a=2,
  q=("Một hòn đá từ không gian đã rơi xuống và đang nằm trên mặt đất thì gọi là gì?",
     "What do we call a space rock that has landed and is lying on the ground?"),
  opts=[("Meteoroid", "A meteoroid"),
        ("Meteor", "A meteor"),
        ("Meteorite (thiên thạch)", "A meteorite"),
        ("Tiểu hành tinh", "An asteroid")],
  ok=("Chính xác! Hòn đá <b>đi hết được khí quyển và tới mặt đất</b> thì mang tên <b>meteorite</b> — đây là loại duy nhất trong ba loại mà con người có thể <b>cầm lên tay</b>.",
      "Exactly! A rock that <b>survives the atmosphere and hits the ground</b> is a <b>meteorite</b> — the only one of the three you can actually <b>hold in your hand</b>."),
  no=("Chưa đúng! Ngoài không gian nó là <b>meteoroid</b>, đang cháy trên trời là <b>meteor</b>, còn nằm trên mặt đất là <b>meteorite</b>.",
      "Not quite! In space it's a <b>meteoroid</b>, burning in the sky it's a <b>meteor</b>, and on the ground it's a <b>meteorite</b>."),
  hint=("Chỉ một trong ba cái tên đó chỉ hòn đá đã hạ cánh.",
        "Only one of the three names belongs to a rock that has landed."),
  quote="When a meteoroid survives its trip through the atmosphere and hits the ground, it's called a meteorite."),

 dict(key="bh-not-hole", card="term_black_hole", lv=1, src="bh", a=1,
  q=("Cái tên “lỗ đen” dễ làm ta tưởng đó là một cái lỗ rỗng. Theo NASA, lỗ đen thực ra là gì?",
     "The name “black hole” makes it sound like an empty hole. According to NASA, what is a black hole really?"),
  opts=[("Một cái lỗ rỗng trong không gian", "An empty hole in space"),
        ("Một khối vật chất khổng lồ bị dồn vào một khoảng cực nhỏ", "A huge concentration of matter packed into a very tiny space"),
        ("Một ngôi sao rất tối", "A very dark star"),
        ("Một đám mây bụi dày", "A thick cloud of dust")],
  ok=("Đúng! NASA nói rõ: lỗ đen <b>không thật sự là cái lỗ nào cả</b> — chúng là <b>những khối vật chất khổng lồ bị dồn vào khoảng không gian cực nhỏ</b>. Chính vì thế chúng đặc đến mức ánh sáng cũng không thoát ra.",
      "Yes! NASA is explicit: black holes <b>aren't really holes</b> — they are <b>huge concentrations of matter packed into very tiny spaces</b>. That's why they're dense enough that not even light escapes."),
  no=("Chưa đúng! Lỗ đen <b>không rỗng</b>. Đó là <b>rất nhiều vật chất nhồi vào một chỗ rất bé</b> — đặc đến mức không gì thoát ra được.",
      "Not quite! A black hole is <b>not empty</b>. It is <b>a great deal of matter squeezed into a very small space</b> — so dense nothing gets out."),
  hint=("Ngược hẳn với “rỗng” — hãy nghĩ tới “chật kín”.",
        "The opposite of “empty” — think “packed full”."),
  quote="These objects aren't really holes. They're huge concentrations of matter packed into very tiny spaces."),

 dict(key="supernova-what", card="term_supernova", lv=1, src="star", a=1,
  q=("Siêu tân tinh (supernova) là gì?",
     "What is a supernova?"),
  opts=[("Một ngôi sao vừa mới sinh ra", "A brand-new star that has just been born"),
        ("Một vụ nổ khổng lồ", "A huge explosion"),
        ("Một hành tinh rất sáng", "A very bright planet"),
        ("Một loại kính viễn vọng", "A kind of telescope")],
  ok=("Đúng! NASA gọi kết cục ấy đúng bằng một câu: <b>một vụ nổ khổng lồ gọi là siêu tân tinh</b>. Cái tên nghe như “ngôi sao mới”, nhưng thực ra đó là lúc một ngôi sao lớn kết thúc.",
      "Yes! NASA names it in one line: <b>a huge explosion called a supernova</b>. The name sounds like “new star”, but it marks the end of a massive one."),
  no=("Chưa đúng! Siêu tân tinh là <b>một vụ nổ khổng lồ</b> — tên nghe như “ngôi sao mới”, nhưng nó là dấu chấm hết của một ngôi sao lớn.",
      "Not quite! A supernova is <b>a huge explosion</b> — the name sounds like “new star”, but it is a massive star's final moment."),
  hint=("Chuyện xảy ra khi một ngôi sao rất nặng cạn nhiên liệu.",
        "It's what happens when a very massive star runs out of fuel."),
  quote="The result is a huge explosion called a supernova."),

 dict(key="ml-trained-by-hubble", card="term_machine_learning", lv=1, src="aiHubble", a=0,
  q=("Để AI biết nhận ra hình dạng các thiên hà, người ta đã cho nó học từ cái gì?",
     "To teach an AI to recognise galaxy shapes, what was it trained on?"),
  opts=[("Ảnh hàng nghìn thiên hà do Hubble quan sát", "Hubble observations of thousands of galaxies"),
        ("Sách giáo khoa thiên văn", "Astronomy textbooks"),
        ("Bản đồ Trái Đất", "Maps of Earth"),
        ("Không cần học gì — AI tự biết", "Nothing — the AI just knows")],
  ok=("Đúng! <b>Ảnh hàng nghìn thiên hà của Hubble đã được dùng để huấn luyện các chương trình AI</b> nhận ra cấu trúc và hình dạng thiên hà — có lúc xét đến từng điểm ảnh. Học máy luôn cần <b>ví dụ</b> để học.",
      "Yes! <b>Hubble observations of thousands of galaxies helped train AI programs</b> to identify galaxy structures and forms — sometimes pixel by pixel. Machine learning always needs <b>examples</b>."),
  no=("Chưa đúng! Học máy không tự biết gì: nó học từ <b>ví dụ</b>. Ở đây ví dụ chính là <b>ảnh hàng nghìn thiên hà do Hubble quan sát</b>.",
      "Not quite! Machine learning knows nothing on its own: it learns from <b>examples</b>. Here the examples were <b>Hubble observations of thousands of galaxies</b>."),
  hint=("Muốn dạy ai nhận ra một thứ, ta phải cho họ xem thật nhiều thứ đó.",
        "To teach anyone to recognise something, you show them a great many of it."),
  quote="Hubble observations of thousands of galaxies helped train AI programs to identify galaxy structures and forms – sometimes on a pixel-by-pixel basis."),
]

HEAD = ("/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.\n"
        "   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */\n")


def esc(t):
    return t.replace("\\", "\\\\").replace('"', '\\"')


def build(d):
    tv, te = TOPIC[d["card"]]
    L = [HEAD, "export default {\n"]
    L.append('  term: "%s",\n' % d["key"])
    L.append('  topic: { vi: "%s",\n           en: "%s" },\n' % (esc(tv), esc(te)))
    L.append('  q: { vi: "%s",\n       en: "%s" },\n' % (esc(d["q"][0]), esc(d["q"][1])))
    L.append("  opts: [\n")
    for i, (ov, oe) in enumerate(d["opts"]):
        L.append('    { vi: "%s",\n      en: "%s" }%s\n'
                 % (esc(ov), esc(oe), "," if i < len(d["opts"]) - 1 else ""))
    L.append("  ],\n")
    L.append("  a: %d,\n" % d["a"])
    for f in ("ok", "no", "hint"):
        pad = " " * (len(f) + 8)
        L.append('  %s: { vi: "%s",\n%sen: "%s" },\n'
                 % (f, esc(d[f][0]), pad, esc(d[f][1])))
    L.append("  lv: %d,\n" % d["lv"])
    L.append('  src: "%s",\n' % d["src"])
    L.append('  srcQuote: "%s",\n' % esc(d["quote"]))
    L.append('  srcChecked: "%s"\n' % CHECKED)
    L.append("};\n")
    return "".join(L)


keys = [d["key"] for d in Q]
if len(set(keys)) != len(keys):
    sys.exit("khoa trung trong danh sach")

for d in Q:
    p = os.path.join(ROOT, "js", "quiz", d["key"] + ".js")
    if os.path.exists(p):
        sys.exit("%s DA TON TAI — dung ghi de mot cau da co" % d["key"])
    io.open(p, "w", encoding="utf-8", newline="").write(build(d))

print("da viet %d file cau moi" % len(Q))

# ── Noi khoa moi vao THE tuong ung o js/codex-terms.js ──
# ⚠️ PHAI LAM, khong thi cau moi thanh "cau le chua the nao nhan": `split_quiz_bank`
#    dua vao `q: [...]` cua tung the de dung bang G, va So Tay dua vao dung bang do
#    de biet tra loi dung cau nao thi mo the nao.
# ⚠️ `isDecoded` la phep HOAC (dung MOT cau la mo the) — da doc lai js/codex-terms.js
#    truoc khi them, nen them cau thu ba KHONG the khoa lai the mot dua tre da mo.
cp = os.path.join(ROOT, "js", "codex-terms.js")
cs = io.open(cp, encoding="utf-8").read()
add = {}
for d in Q:
    add.setdefault(d["card"], []).append(d["key"])
for card, ks in add.items():
    m = 'id: "%s"' % card
    i = cs.index(m)
    j = cs.index("q: [", i)
    k = cs.index("]", j)
    old = cs[j:k + 1]
    inner = old[4:-1].rstrip()
    new = "q: [" + inner + ", " + ", ".join('"%s"' % x for x in ks) + "]"
    cs = cs[:j] + new + cs[k + 1:]
io.open(cp, "w", encoding="utf-8", newline="").write(cs)
print("da noi %d khoa vao %d the o js/codex-terms.js" % (len(Q), len(add)))
