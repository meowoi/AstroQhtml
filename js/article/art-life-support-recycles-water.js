/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www.nasa.gov/reference/environmental-control-and-life-support-systems-eclss/
          (kiem 200 · 14/08/2026 — doc bang `curl`)

   Trich nguyen van:
     · "ECLSS is a life support system that provides or controls atmospheric
        pressure, fire detection and suppression, oxygen levels, proper
        ventilation, waste management and water supply."
     · "ECLSS includes three key components — the Water Recovery System, the Air
        Revitalization System and the Oxygen Generation System."
     · "The Water Recovery System provides clean water by reclaiming wastewater
        (including water from crew members' urine), cabin humidity condensate,
        and water from the hydration system inside crew members' Extra Vehicular
        Activity suits."
     · "The water processor sends the water through a series of multi-filtration
        beds and a catalytic oxidizer for purification."
     · "The Air Revitalization System is dedicated to cleaning the circulating
        cabin air … removing trace contaminants produced by electronics, plastics
        and human off-gassing, including carbon dioxide exhaled by the crew during
        normal respiration."
     · "The oxygen generation assembly is composed of the cell stack, which
        electrolyzes, or breaks apart, water"

   ⚠️⚠️ HAI CHI TIET **CO Y BI LOAI** KHOI BAI: con so "khoang 90% nuoc duoc tai
      che" va "lo Sabatier". Ca hai den tu BAN TOM TAT cua bo tra cuu, toi
      **khong tu doc thay chung tren trang nay**. `docs/proposals/2026-08-14-…`
      muc 2 co nhac chung — do la cho GHI HO SO, khong phai giay phep trich.
      Do dung la lop loi da mac bon lan (CHNOPS · "170 km" · Nam Cuc · IAU).
      Muon dung thi phai mo trang doc lai va thay tan mat, hoac dan them URL khac.

   ⚠️ BAI NAY NOI THANG SANG NHANH LIFE SCIENCE (`art-what-life-needs`) — bai do
      noi su song CAN gi, bai nay noi con nguoi DUNG MAY gi de tu lam ra nhung
      thu ay. Dung viet lai noi dung bai kia o day. */
export default {
  ord: 9060,
  id: "art-life-support-recycles-water",
  src: "NASA",
  cat: "engineering",
  em: "💧",
  c: ["#c0a4ff", "#6b4fd0", "#150f33"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/reference/environmental-control-and-life-support-systems-eclss/",
  title: { vi: "Cỗ máy giữ mạng sống: nước uống hôm nay từng là nước tiểu hôm qua",
          en: "The machine that keeps you alive: today's drinking water was yesterday's urine" },
  body: {
    vi: ["Trên Trạm Vũ trụ Quốc tế có một hệ thống tên là ECLSS. Nó lo những việc mà ở Trái Đất chẳng ai phải nghĩ tới: áp suất không khí, phát hiện và dập cháy, lượng oxy, thông gió, xử lý chất thải, và nước. ECLSS gồm ba bộ phận chính: **hệ thu hồi nước**, **hệ làm mới không khí**, và **hệ sinh oxy**.",
         "Hệ thu hồi nước làm ra nước sạch bằng cách tái chế nước thải — trong đó có nước tiểu của phi hành đoàn, hơi ẩm ngưng tụ trong cabin, và nước từ hệ thống uống nước bên trong bộ đồ đi ra ngoài tàu. Bộ xử lý cho nước đi qua một loạt tầng lọc rồi qua một bộ oxy hoá xúc tác để làm sạch.",
         "Hệ làm mới không khí thì lo phần khí đang lưu thông trong cabin: nó gỡ đi những chất bẩn vi lượng do đồ điện tử, nhựa và chính cơ thể người thải ra — kể cả khí carbonic mà phi hành đoàn thở ra suốt ngày đêm.",
         "Còn oxy đến từ đâu? Từ nước. Bộ sinh oxy có một chồng pin điện phân — nó **tách nước ra**, và một trong hai mảnh tách được chính là oxy để thở."],
    en: ["Aboard the International Space Station there is a system called ECLSS. It handles the things nobody on Earth ever has to think about: atmospheric pressure, fire detection and suppression, oxygen levels, ventilation, waste management and water supply. ECLSS has three key components: the **Water Recovery System**, the **Air Revitalization System** and the **Oxygen Generation System**.",
         "The Water Recovery System provides clean water by reclaiming wastewater — including water from crew members' urine, cabin humidity condensate, and water from the hydration system inside their spacewalking suits. The water processor sends it through a series of multi-filtration beds and a catalytic oxidizer for purification.",
         "The Air Revitalization System takes care of the air circulating through the cabin: it removes trace contaminants produced by electronics, plastics and human off-gassing — including the carbon dioxide the crew exhales during normal breathing, all day and all night.",
         "And where does the oxygen come from? From water. The oxygen generation assembly contains a cell stack that **electrolyzes, or breaks apart, water** — and one of the two pieces it breaks into is the oxygen you breathe."]
  },
  more: {
    vi: ["Đọc xong dễ dừng lại ở chỗ \"eo ơi, nước tiểu\". Nhưng chỗ đáng nghĩ nằm ở một chữ khác: **VÒNG**.",
         "Ở Trái Đất, mọi thứ ta dùng đều đi theo ĐƯỜNG THẲNG: nước từ vòi chảy vào, dùng xong chảy ra cống, và ta không bao giờ gặp lại nó nữa. Cách sống ấy chỉ chạy được khi có một hành tinh khổng lồ ở đầu này để lấy vào và ở đầu kia để đổ ra.",
         "Trên trạm thì không có hai đầu ấy. Không có vòi nào ngoài kia, không có cống nào cả. Nên các kỹ sư phải **bẻ cong đường thẳng thành vòng tròn**: đầu ra phải nối lại vào đầu vào. Chú ý ba hệ ở trên nối với nhau khéo thế nào — hơi ẩm phi hành đoàn thở ra được hứng lại thành nước, nước lại bị tách ra để lấy oxy, oxy lại được thở. Cùng một mớ vật chất, đi vòng mãi.",
         "Nghĩ kỹ thì Trái Đất cũng đang làm đúng như vậy, chỉ là ở cỡ khổng lồ và chậm đến mức ta không thấy. Nước trong cốc của bạn đã từng ở trong một đám mây, một dòng sông, và trong cơ thể của vô số sinh vật trước bạn. Trạm vũ trụ chỉ là một Trái Đất **thu nhỏ đến mức nhìn thấy được cái vòng ấy** — nhỏ tới mức nếu vòng đứt thì người trên đó biết ngay trong vài giờ.",
         "Đó cũng là lý do một cỗ máy lọc nước lại là **kỹ thuật khó nhất trên trạm**, chứ không phải động cơ hay máy tính. Động cơ hỏng thì con tàu đứng yên; ECLSS hỏng thì không còn ai để sửa nó.",
         "⚠️ Phép so đường thẳng — vòng tròn, ví dụ nước trong cốc và câu \"kỹ thuật khó nhất trên trạm\" là cách astroQ giải thích; trang NASA mô tả ba hệ thống chứ không rút ra những kết luận này."],
    en: ["It is easy to stop at \"ugh, urine\". But the part worth thinking about sits in another word: **LOOP**.",
         "On Earth everything we use travels in a STRAIGHT LINE: water arrives from a tap, and once used it goes down a drain and we never meet it again. That way of living only works while there is an enormous planet at one end to draw from and at the other end to pour into.",
         "The station has neither end. There is no tap out there and no drain. So the engineers had to **bend the straight line into a circle**: the output has to be plumbed back into the input. Notice how neatly the three systems above interlock — the moisture the crew breathes out is caught as water, the water is split to yield oxygen, and the oxygen is breathed again. The same handful of matter, going round and round.",
         "Think it through and Earth is doing exactly the same thing, only on a colossal scale and so slowly that we never notice. The water in your glass has been inside a cloud, a river, and countless living bodies before you. A space station is simply an Earth **shrunk until the loop becomes visible** — small enough that if the loop ever breaks, the people inside know within hours.",
         "That is also why a water-purifying machine is **the hardest engineering on the station**, not the engines or the computers. If an engine fails, the craft stops moving; if ECLSS fails, there is nobody left to repair it.",
         "⚠️ The straight-line-versus-circle comparison, the glass of water example and the \"hardest engineering on the station\" claim are astroQ's explanation; the NASA page describes the three systems without drawing these conclusions."]
  },
  term: { who: "comet",
          word: { vi: "Điện phân",
                  en: "Electrolysis" },
          text: { vi: "dùng dòng điện để tách một chất ra thành các phần của nó. Trên trạm, người ta điện phân nước — và một trong hai mảnh tách ra là oxy để thở. ☄️",
                  en: "Using an electric current to break a substance apart into its pieces. On the station they electrolyze water — and one of the two pieces that comes out is breathable oxygen. ☄️" } }
};
