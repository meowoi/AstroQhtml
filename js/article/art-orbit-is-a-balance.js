/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www.nasa.gov/learning-resources/for-kids-and-students/what-is-an-orbit-grades-5-8/
          (kiem 200 · 14/08/2026 — ban NASA viet cho lop 5-8, dung do tuoi)
   Trich nguyen van:
     · "An orbit is a regular, repeating path that one object in space takes
        around another one."
     · "All orbits are elliptical, which means they are an ellipse, similar to an
        oval."
     · "An object's momentum and the force of gravity have to be balanced for an
        orbit to happen."
     · "When these forces are balanced, the object is always falling toward the
        planet, but because it's moving sideways fast enough, it never hits the
        planet."

   ⚠️ BAI NAY LA MAT XICH CUOI CUA CHUOI TOAN (do luong → ty le → toa do → goc →
      van toc → khoang cach → QUY DAO), va no CO Y noi lai y "roi vong quanh" da
      co o `art-microgravity-is-falling` (nhanh LIFE SCIENCE). Khong phai trung
      lap: bai kia hoi "vi sao phi hanh gia troi", bai nay hoi "cai duong di do co
      HINH gi va vi sao no on dinh". Mot ben la cam giac, mot ben la hinh hoc.
   ⚠️ Trang KHONG neu mot con so nao (khong toc do, khong ban kinh). Dung muon so
      lieu tu bai khac roi dan URL nay. */
export default {
  ord: 7040,
  id: "art-orbit-is-a-balance",
  src: "NASA",
  cat: "math",
  em: "🛰️",
  c: ["#ffe3a8", "#c9922f", "#332608"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/learning-resources/for-kids-and-students/what-is-an-orbit-grades-5-8/",
  title: { vi: "Quỹ đạo không phải hình tròn, và nó là một thế cân bằng",
          en: "An orbit is not a circle, and it is a balance" },
  body: {
    vi: ["Quỹ đạo là đường đi đều đặn, lặp lại, mà một vật trong không gian vạch ra quanh một vật khác. Vẽ trong sách giáo khoa thì nó hay là một vòng tròn — nhưng đó là hình vẽ cho gọn.",
         "NASA nói rõ: mọi quỹ đạo đều là hình ELIP, tức một hình bầu dục. Vòng tròn hoàn hảo chỉ là một trường hợp riêng mà thực tế gần như không rơi vào.",
         "Vậy điều gì giữ cho một vật ở nguyên trên đường ấy? Một thế cân bằng giữa hai thứ: đà của chính nó, và lực hấp dẫn kéo nó lại. Muốn có quỹ đạo thì hai thứ đó phải cân nhau.",
         "Và khi chúng cân nhau thì chuyện xảy ra là điều này: vật luôn luôn đang RƠI về phía hành tinh — nhưng vì nó đang đi ngang đủ nhanh, nên nó không bao giờ chạm tới."],
    en: ["An orbit is a regular, repeating path that one object in space takes around another one. Drawn in a textbook it is usually a circle — but that is a drawing made for convenience.",
         "NASA says it plainly: all orbits are elliptical, meaning an ellipse, similar to an oval. A perfect circle is only a special case that reality almost never lands on.",
         "So what keeps an object on that path? A balance between two things: its own momentum, and the force of gravity pulling it back. For an orbit to happen, those two have to be balanced.",
         "And when they are balanced, here is what happens: the object is always FALLING toward the planet — but because it is moving sideways fast enough, it never hits it."]
  },
  more: {
    vi: ["Hai chữ \"cân bằng\" ở đây đáng dừng lại, vì nó không giống thế cân bằng của một cái cân đứng yên.",
         "Ở đây không có gì đứng yên cả. Lực hấp dẫn không hề bị triệt tiêu — nó vẫn kéo, kéo suốt, và vật vẫn luôn rơi. Thứ được cân bằng là giữa việc RƠI XUỐNG và việc ĐI NGANG: rơi xuống bao nhiêu thì mặt đất cũng cong đi bấy nhiêu, nên khoảng cách giữ nguyên.",
         "Nghĩ theo cách đó thì hình elip thôi lạ. Nếu đà và lực hấp dẫn không cân nhau hoàn hảo ở mọi điểm — mà chúng gần như không bao giờ cân hoàn hảo — thì vật sẽ khi gần hơn khi xa hơn một chút trong mỗi vòng. Vẽ cái đường ấy ra, bạn được một hình bầu dục chứ không phải vòng tròn.",
         "Và đây là chỗ mắt xích này nối lại cả chuỗi: để biết một vật có ở lại quỹ đạo hay không, người ta phải đo được **vận tốc** của nó, **khoảng cách** tới hành tinh, và **góc** mà nó đang bay. Ba đại lượng — đúng ba thứ mà nhánh toán này đã đi qua. Quỹ đạo không phải một chủ đề mới; nó là chỗ những thứ kia gặp nhau.",
         "⚠️ Phần giải thích vì sao đường đi thành hình bầu dục là cách astroQ diễn đạt lại; trang NASA cho lớp 5–8 nêu hai điều — quỹ đạo là elip, và đà phải cân với lực hấp dẫn — chứ không trình bày lập luận này."],
    en: ["The word \"balance\" here is worth pausing on, because it is not like the balance of a still weighing scale.",
         "Nothing here is still. Gravity is not cancelled out — it keeps pulling, all the time, and the object keeps falling. What is balanced is FALLING DOWN against MOVING SIDEWAYS: it falls by just as much as the ground curves away, so the distance stays the same.",
         "Thought of that way, the ellipse stops being strange. If momentum and gravity are not perfectly matched at every point — and they almost never are — then the object comes a little closer and drifts a little further on each lap. Trace that path and you get an oval, not a circle.",
         "And here is where this link ties the whole chain together: to know whether something will stay in orbit, you must measure its **speed**, its **distance** from the planet, and the **angle** it is travelling at. Three quantities — exactly the three this maths branch has walked through. An orbit is not a new topic; it is where those others meet.",
         "⚠️ The explanation of why the path becomes an oval is astroQ's own wording; the NASA page for grades 5-8 states two things — that orbits are ellipses, and that momentum must balance gravity — without laying out this argument."]
  },
  term: { who: "comet",
          word: { vi: "Elip",
                  en: "Ellipse" },
          text: { vi: "hình bầu dục khép kín. Vòng tròn là một elip đặc biệt, khi nó \"tròn đều\" ở mọi phía — nên nói mọi quỹ đạo là elip thì vẫn đúng cả với những quỹ đạo trông như tròn. ☄️",
                  en: "A closed oval. A circle is a special ellipse, the one that is equally round all the way around — so saying every orbit is an ellipse stays true even for the ones that look circular. ☄️" } }
};
