/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-thrust/
          (kiem 200 · 14/08/2026 — doc bang `curl`, xem ghi chu o
           art-four-forces-tug-of-war.js)

   Trich nguyen van:
     · "In a rocket engine, stored fuel and stored oxidizer are ignited in a
        combustion chamber. The combustion produces great amounts of exhaust gas
        at high temperatures and pressure."
     · "The amount of thrust produced by the rocket depends on the mass flow rate
        through the engine, the exit velocity of the exhaust, and the pressure at
        the nozzle exit."
     · "Since the oxidizer is carried onboard the rocket, rockets can generate
        thrust in a vacuum where there is no oxygen."
     · "Notice that there is no free stream mass times free stream velocity term
        in the thrust equation because no external air is brought on board."

   ⚠️ CAU THU BA LA CHOT CHAN CUA CA BAI — no bac thang quan niem sai pho bien
      nhat ve ten lua ("ten lua day vao khong khi"). Dung bo no di cho gon.

   ⚠️ BAI NAY PHU HAI MAT XICH CUA CHUOI VAT LY (nang luong + vat ly khong gian /
      chan khong) — co y, va ly do ghi o docs/decisions/010: chuoi khong bat buoc
      moi mat xich mot bai khi mot trang nguon noi ca hai dieu do. */
export default {
  ord: 8040,
  id: "art-rockets-work-in-vacuum",
  src: "NASA",
  cat: "physics",
  em: "🚀",
  c: ["#8fd4ff", "#3a8fd6", "#0c2140"],
  img: null,
  credit: null,
  url: "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-thrust/",
  title: { vi: "Tên lửa không đẩy vào không khí — nên nó bay được trong chân không",
          en: "A rocket does not push against the air — so it works in a vacuum" },
  body: {
    vi: ["Gần như ai cũng hình dung tên lửa đẩy vào không khí phía dưới để bay lên, giống như bơi thì đẩy vào nước. Nếu vậy thì ra ngoài không gian — nơi không còn không khí — nó phải chịu chết.",
         "Nhưng tên lửa bay tốt ngoài đó. Vì cách nó hoạt động khác hẳn.",
         "Trong một động cơ tên lửa, nhiên liệu và chất oxy hoá được chứa sẵn trên tàu rồi đốt cháy trong buồng đốt. Sự cháy sinh ra một lượng lớn khí thải ở nhiệt độ và áp suất rất cao. Lực đẩy sinh ra phụ thuộc vào lưu lượng khối lượng qua động cơ, vận tốc khí thoát ra, và áp suất ở miệng loa phụt.",
         "Chú ý hai chữ **chứa sẵn**. Vì chất oxy hoá được mang theo trên tàu, tên lửa sinh được lực đẩy **trong chân không, nơi không có oxy**. Trong phương trình lực đẩy thậm chí không có số hạng nào cho không khí bên ngoài — bởi không có không khí nào được lấy vào."],
    en: ["Almost everyone pictures a rocket pushing against the air beneath it to rise, the way you push against water to swim. If that were true, then out in space — where there is no air — it would be helpless.",
         "But rockets work perfectly well out there. Because they work in a completely different way.",
         "In a rocket engine, stored fuel and stored oxidizer are ignited in a combustion chamber. The combustion produces great amounts of exhaust gas at high temperatures and pressure. The thrust produced depends on the mass flow rate through the engine, the exit velocity of the exhaust, and the pressure at the nozzle exit.",
         "Note the word **stored**. Since the oxidizer is carried onboard, a rocket can generate thrust **in a vacuum, where there is no oxygen**. The thrust equation does not even contain a term for outside air — because no external air is brought on board."]
  },
  more: {
    vi: ["Vì sao lại phải mang theo cả chất oxy hoá? Vì cháy không phải chuyện của riêng nhiên liệu.",
         "Muốn cháy thì cần hai thứ: chất đốt và một chất cung cấp oxy. Một cây nến trong phòng lấy oxy từ không khí quanh nó — úp cái cốc lên là nó tắt, không phải vì hết sáp mà vì hết oxy. Ngoài không gian thì không có cái không khí ấy. Nên tên lửa mang theo cả hai nửa của đám cháy.",
         "Đó cũng là lý do tên lửa to đến vậy mà phần lớn thân chỉ là bình chứa: một phần đựng nhiên liệu, một phần đựng chất oxy hoá. Máy bay phản lực thì không cần bình thứ hai — nó hút oxy từ không khí, và chính vì thế nó **không bay ra ngoài khí quyển được**.",
         "Còn cái đẩy tên lửa đi là gì, nếu không phải không khí? Là chính dòng khí phụt ra. Tên lửa đẩy luồng khí về phía sau, và luồng khí đẩy tên lửa về phía trước — đúng định luật thứ ba của Newton ở bài bên cạnh. Cặp lực ấy xảy ra **giữa con tàu và chính khí của nó**, nên nó không cần mượn thứ gì bên ngoài.",
         "⚠️ Ví dụ cây nến, chuyện bình chứa và so sánh với máy bay phản lực là cách astroQ giải thích; trang NASA nói về buồng đốt, lực đẩy và chân không chứ không kể những ví dụ này."],
    en: ["Why carry an oxidizer at all? Because burning is not the fuel's business alone.",
         "To burn you need two things: something to burn, and something to supply oxygen. A candle in a room takes oxygen from the surrounding air — put a glass over it and it goes out, not for lack of wax but for lack of oxygen. In space there is no such air. So a rocket carries both halves of the fire with it.",
         "That is also why rockets are so large while most of the body is just tanks: one part holds fuel, another holds oxidizer. A jet aircraft needs no second tank — it draws oxygen from the air, and that is exactly why it **cannot fly beyond the atmosphere**.",
         "So what pushes the rocket, if not the air? The exhaust stream itself. The rocket pushes the gas backwards and the gas pushes the rocket forwards — Newton's third law, from the article next door. That pair of forces happens **between the craft and its own gas**, so it needs to borrow nothing from outside.",
         "⚠️ The candle example, the tank comparison and the jet-aircraft contrast are astroQ's explanation; the NASA page discusses the combustion chamber, thrust and vacuum without telling these stories."]
  },
  term: { who: "byte",
          word: { vi: "Chất oxy hoá",
                  en: "Oxidizer" },
          text: { vi: "thứ cung cấp oxy cho đám cháy. Tên lửa mang nó theo trong bình riêng — đó chính là lý do nó cháy được ở nơi không có một phân tử không khí nào. 🤖",
                  en: "The stuff that supplies oxygen to a fire. A rocket carries it in its own tank — which is precisely why it can burn where there is not a single molecule of air. 🤖" } },
  /* Noi voi kho cau hoi: bai day dung ly do: chat oxy hoa duoc mang san tren tau nen ten lua sinh luc day duoc trong chan khong. */
  terms: ["rocket-thrust-in-vacuum"]
};
