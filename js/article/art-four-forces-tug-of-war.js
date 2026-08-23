/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/four-rocket-forces/
          (kiem 200 · 14/08/2026)

   ⚠️⚠️ DOC TRANG NAY BANG `curl`, KHONG PHAI `WebFetch`. May chu do phuc vu THIEU
      CHUNG CHI TRUNG GIAN nen WebFetch tu choi ("unable to verify the first
      certificate") trong khi curl vao binh thuong. Ngay 14/08/2026 toi da mot lan
      ket luan SAI rang nguon nay chet chi vi mot cong cu khong mo duoc. Cach doc:
        curl -s -L -A "<User-Agent that>" "<url>" | <boc the HTML>
      Ghi o docs/proposals/2026-08-14-nguon-cho-physics-engineering.md muc 4.

   Trich nguyen van:
     · "In flight, a rocket is subjected to four forces; weight, thrust, and the
        aerodynamic forces, lift and drag."
     · "Forces are vector quantities having both a magnitude and a direction. When
        describing the action of forces, one must account for both the magnitude
        and the direction."
     · "In flight, the magnitude, and sometimes the direction, of the four forces
        is constantly changing. The response of the rocket depends on the relative
        magnitude and direction of the forces, much like the motion of the rope in
        a 'tug-of-war' contest."
     · "While most airplanes have a high lift to drag ratio, the drag of a rocket
        is usually much greater than the lift."

   ⚠️ Phep vi KEO CO la CUA CHINH TRANG NASA (khong phai cua astroQ) — nen o day
      duoc phep dat trong than bai. Khac han phep vi ngon tay o bai thi sai, vi cai
      do trang khong co. Doc ky khac biet truoc khi them mot phep vi nao nua. */
export default {
  ord: 8010,
  id: "art-four-forces-tug-of-war",
  src: "NASA",
  cat: "physics",
  em: "🪢",
  c: ["#7fb0ff", "#3a63c9", "#0d1a3a"],
  img: null,
  credit: null,
  url: "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/four-rocket-forces/",
  title: { vi: "Một cuộc kéo co bốn phía quyết định tên lửa bay hay rơi",
          en: "A four-way tug-of-war decides whether a rocket flies" },
  body: {
    vi: ["Khi đang bay, một tên lửa chịu bốn lực: trọng lượng, lực đẩy, và hai lực khí động là lực nâng và lực cản.",
         "Lực không phải một con số đơn thuần. NASA gọi nó là đại lượng vectơ — nó có ĐỘ LỚN và có HƯỚNG, và khi nói về tác dụng của lực thì phải kể cả hai. Một lực 100 đơn vị hướng lên và một lực 100 đơn vị hướng xuống là hai chuyện hoàn toàn khác nhau.",
         "Trong lúc bay, độ lớn — và đôi khi cả hướng — của bốn lực ấy thay đổi liên tục. Con tàu phản ứng ra sao là tuỳ vào tương quan giữa chúng, và chính NASA ví nó với chuyển động của sợi dây trong một cuộc KÉO CO.",
         "Phép ví đó đắt hơn nó thoạt nghe. Sợi dây không đứng yên vì hai bên ngừng kéo — nó đứng yên vì hai bên kéo BẰNG NHAU. Một tên lửa treo lơ lửng giữa trời cũng vậy: không phải vì hết lực, mà vì các lực đang hoà nhau."],
    en: ["In flight, a rocket is subjected to four forces: weight, thrust, and the aerodynamic forces, lift and drag.",
         "A force is not just a number. NASA calls it a vector quantity — it has a MAGNITUDE and a DIRECTION, and when describing what a force does you must account for both. A force of 100 units pushing up and one of 100 units pushing down are completely different things.",
         "During flight the magnitude — and sometimes the direction — of those four forces is constantly changing. How the rocket responds depends on their relative sizes and directions, and NASA itself compares it to the motion of the rope in a TUG-OF-WAR contest.",
         "That comparison is worth more than it first sounds. The rope is not still because both sides stopped pulling — it is still because both sides pull EQUALLY. A rocket hanging steady in the air is the same: not out of forces, but with its forces cancelling."]
  },
  more: {
    vi: ["Có một chỗ khác nhau giữa tên lửa và máy bay mà chính trang NASA nêu, và nó nói lên rất nhiều về việc thiết kế.",
         "Ở máy bay, lực NÂNG là thứ dùng để thắng trọng lượng — đôi cánh giữ nó trên trời. Ở tên lửa thì không: chính LỰC ĐẨY mới là thứ chống lại trọng lượng. Trên nhiều tên lửa, lực nâng chỉ dùng để giữ thăng bằng và điều khiển hướng.",
         "Kéo theo đó là một con số đảo ngược: phần lớn máy bay có tỉ số lực nâng trên lực cản CAO, còn ở tên lửa thì lực cản thường LỚN HƠN NHIỀU so với lực nâng.",
         "Nghĩ kỹ thì đó chính là lý do hai thứ trông khác nhau đến vậy. Máy bay có cánh rộng vì nó sống bằng lực nâng; tên lửa thì thon dài như một mũi tên vì với nó, cánh chỉ là thứ làm tăng lực cản. Hình dáng của một cỗ máy là câu trả lời cho câu hỏi: nó đang phải thắng lực nào?",
         "⚠️ Đoạn suy luận cuối (vì sao hai thứ trông khác nhau) là cách astroQ diễn đạt lại; trang NASA nêu bốn khác biệt kỹ thuật chứ không rút ra kết luận này."],
    en: ["There is a difference between rockets and aeroplanes that the NASA page itself raises, and it says a lot about design.",
         "On an aeroplane, LIFT is what overcomes weight — the wings hold it up. Not so on a rocket: there, THRUST is what opposes weight. On many rockets, lift is only used to stabilise and steer.",
         "That brings a reversed figure with it: most aeroplanes have a high lift-to-drag ratio, while on a rocket the drag is usually much greater than the lift.",
         "Think it through and that is exactly why the two look so different. An aeroplane has broad wings because it lives on lift; a rocket is slim as an arrow because for it, wings are mostly a way to add drag. The shape of a machine is an answer to the question: which force is it fighting?",
         "⚠️ That last piece of reasoning (why the two look different) is astroQ's own wording; the NASA page lists four technical differences without drawing this conclusion."]
  },
  term: { who: "byte",
          word: { vi: "Vectơ",
                  en: "Vector" },
          text: { vi: "một đại lượng có cả độ lớn lẫn hướng. Vận tốc, lực, gia tốc đều là vectơ — nên nói \"lực 100\" mà không nói hướng thì mới nói được một nửa. 🤖",
                  en: "A quantity with both a size and a direction. Velocity, force and acceleration are all vectors — so saying \"a force of 100\" without a direction is only half the story. 🤖" } },
  /* Noi voi kho cau hoi: bai day ca hai: bon luc (trong luong, luc day, luc nang, luc can), va luc la dai luong vecto co ca do lon lan huong. */
  terms: ["four-forces-on-a-rocket", "force-is-a-vector"]
};
