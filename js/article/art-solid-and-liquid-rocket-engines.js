/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/model-solid-rocket-engine/
          (kiem 200 · 14/08/2026 — doc bang `curl`; may chu NASA nay phuc vu THIEU
           CHUNG CHI TRUNG GIAN nen WebFetch tu choi, xem ghi chu o
           art-four-forces-tug-of-war.js)

   Trich nguyen van:
     · "There are two main categories of rocket engines: liquid rockets and solid
        rockets. In a liquid rocket, the fuel and the source of oxygen (oxidizer)
        necessary for combustion are stored separately and pumped into the
        combustion chamber of the nozzle"
     · "Some type of igniter is used to initiate the burning of a solid rocket
        motor at the end of the propellant facing the nozzle. As the propellant
        burns, hot exhaust gas is produced which is used to propel the rocket,
        and a 'flame front' is produced"
     · "The engine casing is a cylinder made of heavy cardboard which contains
        the nozzle, propellants, and other explosive charges. At the right side
        of the engine is the nozzle, a relatively simple device used to
        accelerate hot gases and produce thrust"
     · "When the flame front reaches the far left of the propellant, thrust goes
        to zero, and a delay charge" [bat dau chay]
     · "When the delay charge is completely burned through, the ejection charge
        … is ignited. This produces a small explosion which ejects hot gas out
        the front of the engine through the engine mount, ejects the nose cone,
        and deploys the par[achute]"
     · "Flying model rockets is a relatively safe and inexpensive way for students
        to learn the basics of forces and the response of vehicles to external
        forces."
     · "Note: Never disturb, cut, or modify a real model rocket engine. The
        propellant can ignite at any time if there is a source of heat."

   ⚠️⚠️ CAU CANH BAO AN TOAN PHAI GIU TRONG THAN BAI, KHONG DUOC BO CHO GON.
      Day la mon do tre CO THE cam trong tay ngoai doi that — khac han moi bai
      khac cua kho (khong ai cham duoc vao ISS hay Sao Hoa). Trang NASA dat no o
      cuoi bai, astroQ cung vay.

   ⚠️⚠️ BAI NAY **KHONG DUOC LAP** `art-rockets-work-in-vacuum`. Trang
      `liquid-rocket-engine/` cua cung bo Beginner's Guide noi **gan y het** bai
      chan khong (phuong trinh luc day · "rockets can generate thrust in a
      vacuum") nen da BI LOAI. Trang duoc chon o day khac han: no noi ve
      **HAI LOAI dong co** va ve **chuoi thoi gian nam trong khoi thuoc phong**.
      Truoc khi them mot bai dong co nua, doc ky ca hai trang de khong lap doan.

   ⚠️ CON SO "khong tat duoc / khong dieu chinh duoc luc day" cua dong co ran
      DEN TU BAN TOM TAT cua bo tra cuu, **khong nam tren trang nay** — co y
      KHONG dua vao bai. Muon dung thi phai mo mot trang khac va dan them URL.
      Do dung la lop loi da mac bon lan (CHNOPS · "170 km" · Nam Cuc · IAU). */
export default {
  ord: 9050,
  id: "art-solid-and-liquid-rocket-engines",
  src: "NASA",
  cat: "engineering",
  em: "🧨",
  c: ["#c0a4ff", "#6b4fd0", "#150f33"],
  img: null,
  credit: null,
  url: "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/model-solid-rocket-engine/",
  title: { vi: "Có hai loại động cơ tên lửa, và loại thứ hai không có nút tắt",
          en: "There are two kinds of rocket engine — and one of them has no off switch" },
  body: {
    vi: ["NASA chia động cơ tên lửa thành **hai loại chính**: động cơ lỏng và động cơ rắn. Ở động cơ **lỏng**, nhiên liệu và nguồn cung cấp oxy được chứa **riêng** rồi **bơm** vào buồng đốt — hai thứ chỉ gặp nhau đúng lúc cần cháy.",
         "Ở động cơ **rắn** thì ngược lại: cả hai đã trộn sẵn thành một khối thuốc phóng nằm im trong vỏ. Một bộ mồi đốt cháy phần thuốc phóng ở đầu sát loa phụt, và khi thuốc phóng cháy thì sinh ra khí nóng đẩy tên lửa đi — cùng với một thứ gọi là **mặt lửa** lan dần vào trong.",
         "Hãy xem một động cơ tên lửa mô hình. Vỏ động cơ chỉ là một ống bìa cứng dày, bên trong chứa loa phụt, thuốc phóng và **các liều nổ khác**. Khi mặt lửa cháy tới đầu kia của thuốc phóng, **lực đẩy về không** — và một **liều trễ** bắt đầu cháy. Cháy hết liều trễ thì tới **liều đẩy**: một tiếng nổ nhỏ thổi khí nóng ra phía trước, bật mũi tên lửa ra và bung dù.",
         "⚠️ NASA ghi rõ: **đừng bao giờ tháo, cắt hay sửa một động cơ tên lửa mô hình thật.** Thuốc phóng có thể bắt lửa bất cứ lúc nào nếu gặp nguồn nhiệt."],
    en: ["NASA sorts rocket engines into **two main categories**: liquid rockets and solid rockets. In a **liquid** rocket, the fuel and the source of oxygen are stored **separately** and **pumped** into the combustion chamber — the two only meet at the moment they are meant to burn.",
         "A **solid** rocket is the opposite: both are already mixed into one block of propellant sitting quietly inside the casing. An igniter starts the burn at the end of the propellant facing the nozzle, and as the propellant burns it produces hot exhaust gas that propels the rocket — along with something called a **flame front** travelling inward.",
         "Look inside a model rocket engine. The casing is just a cylinder of heavy cardboard holding the nozzle, the propellant and **other explosive charges**. When the flame front reaches the far end of the propellant, **thrust goes to zero** — and a **delay charge** begins to burn. Once that is burned through, the **ejection charge** fires: a small explosion pushes hot gas out the front of the engine, throws off the nose cone and deploys the parachute.",
         "⚠️ NASA says it plainly: **never disturb, cut or modify a real model rocket engine.** The propellant can ignite at any time if there is a source of heat."]
  },
  more: {
    vi: ["Chỗ đáng nghĩ nhất của bài này: **một khối thuốc phóng cũng là một cái đồng hồ.**",
         "Đọc lại thứ tự đi — đẩy lên, rồi im lặng một lúc, rồi bung dù. Ba việc, đúng thứ tự, đúng khoảng cách thời gian. Nhưng trong ống bìa cứng ấy **không có một mạch điện nào**, không có bộ đếm giờ, không có cảm biến. Vậy cái gì bấm giờ?",
         "Chính **hình dạng** của các khối thuốc. Mặt lửa cháy với tốc độ khá đều, nên **độ dày của liều trễ CHÍNH LÀ số giây phải chờ**. Muốn dù bung muộn hơn hai giây thì làm liều trễ dày hơn. Người kỹ sư ở đây không lập trình bằng chữ — họ lập trình bằng **bề dày**.",
         "Và đó cũng là chỗ hai loại động cơ khác nhau nhất. Động cơ lỏng có hai bình riêng và một cái bơm, nên **con người còn quyết định được** khi nào bơm và bơm bao nhiêu. Động cơ rắn thì mọi quyết định đã **đóng cứng vào vật chất** từ lúc chế tạo — mồi lửa xong là câu chuyện tự chạy tới hết.",
         "Nghĩ theo cách đó thì bạn hiểu vì sao NASA phải viết câu cảnh báo kia. Một ống bìa cứng trông vô hại, nhưng bên trong nó là một chuỗi việc đã được nạp sẵn và chỉ chờ đủ nóng để bắt đầu.",
         "⚠️ Cách gọi \"khối thuốc phóng là một cái đồng hồ\" và lập luận về bề dày liều trễ là cách astroQ giải thích; trang NASA mô tả các bộ phận và thứ tự cháy chứ không nói theo lối này."],
    en: ["The most interesting idea here: **a block of propellant is also a clock.**",
         "Read the order again — push, then a silence, then the parachute. Three things, in the right order, spaced the right way apart. Yet inside that cardboard tube there is **no circuit**, no timer chip, no sensor. So what keeps time?",
         "The **shape** of the charges does. The flame front burns at a fairly steady rate, so **the thickness of the delay charge IS the number of seconds to wait**. Want the parachute two seconds later? Make that charge thicker. The engineer here does not program with words — they program with **thickness**.",
         "That is also where the two kinds of engine differ most. A liquid rocket has two separate tanks and a pump, so **people can still decide** when to pump and how much. In a solid rocket every decision was **frozen into matter** at the factory — once it is lit, the story runs to the end on its own.",
         "Think of it that way and you see why NASA had to write that warning. A cardboard tube looks harmless, but inside it is a sequence already loaded, waiting only for enough heat to begin.",
         "⚠️ Calling the propellant \"a clock\" and the reasoning about the delay charge's thickness are astroQ's explanation; the NASA page describes the parts and the burning order without putting it this way."]
  },
  term: { who: "byte",
          word: { vi: "Mặt lửa",
                  en: "Flame front" },
          text: { vi: "ranh giới đang cháy chạy dần vào trong khối thuốc phóng. Nó đi tới đâu thì phần đó cháy — nên vị trí của nó chính là \"kim đồng hồ\" của cả động cơ. 🤖",
                  en: "The burning boundary that travels inward through the propellant. Whatever it reaches, burns — so its position is the \"clock hand\" of the whole engine. 🤖" } },
  /* Noi voi kho cau hoi: bai day ca hai: dong co ran tron san thuoc phong thanh mot khoi, va muon dung thi phai pha vo. (Cau hoi ve viec DUNG, khong phai ve viec dieu chinh luc day — trang nguon khong noi gi ve viec dieu chinh.) */
  terms: ["solid-engine-propellant-mixed", "solid-engine-cannot-be-stopped"]
};
