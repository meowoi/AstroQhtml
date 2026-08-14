/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/
          (kiem 200 · 14/08/2026 — doc bang `curl`, xem ghi chu o
           art-four-forces-tug-of-war.js va docs/proposals/2026-08-14-… muc 4)

   Trich nguyen van:
     · "An object at rest remains at rest, and an object in motion remains in
        motion at constant speed and in a straight line unless acted on by an
        unbalanced force."
     · "This tendency to resist changes in a state of motion is inertia."
     · "The acceleration of an object depends on the mass of the object and the
        amount of force applied."
     · "Whenever one object exerts a force on another object, the second object
        exerts an equal and opposite on the first."
     · "In 1686, he presented his three laws of motion in the 'Principia
        Mathematica Philosophiae Naturalis.'"
     · "Newton's laws together with Kepler's Laws explained why planets move in
        elliptical orbits rather than in circles."

   ⚠️⚠️ CAU DINH LUAT 3 TREN TRANG NASA **THIEU CHU "force"** — nguyen van la
      "exerts an equal and opposite on the first". Khi dich thi dich cho DUNG NGHIA
      (tre phai hieu duoc), nhung TUYET DOI KHONG "sua ho" roi van de trong ngoac
      kep nhu mot trich dan — sua xong thi no khong con la trich dan nua. O day bai
      viet dien dat lai bang loi cua minh chu khong trich nguyen van cau do.

   ⚠️ CAU CUOI (Newton + Kepler giai thich quy dao elip) NOI THANG SANG
      `art-orbit-is-a-balance` cua nhanh MATHEMATICS — co y, va no la cho hai nhanh
      gap nhau. Dung viet lai noi dung bai kia o day. */
export default {
  ord: 8030,
  id: "art-newtons-three-laws",
  src: "NASA",
  cat: "physics",
  em: "🍎",
  c: ["#9fc2ff", "#4a72d6", "#0e1f42"],
  img: null,
  credit: null,
  url: "https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/newtons-laws-of-motion/",
  title: { vi: "Ba câu của Newton, và câu đầu tiên là câu khó tin nhất",
          en: "Newton's three sentences — and the first is the hardest to believe" },
  body: {
    vi: ["Năm 1686, Isaac Newton trình bày ba định luật chuyển động của ông trong cuốn *Principia*. Ba câu, và chúng vẫn là nền của vật lý hiện đại.",
         "**Câu thứ nhất:** một vật đang đứng yên thì vẫn đứng yên, một vật đang chuyển động thì vẫn chuyển động với tốc độ không đổi theo đường thẳng — trừ khi có một lực không cân bằng tác dụng lên nó. Xu hướng chống lại việc đổi trạng thái chuyển động ấy gọi là QUÁN TÍNH.",
         "**Câu thứ hai:** gia tốc của một vật phụ thuộc vào khối lượng của vật và độ lớn của lực tác dụng.",
         "**Câu thứ ba:** hễ một vật tác dụng lực lên vật khác, thì vật thứ hai cũng tác dụng lại một lực bằng về độ lớn và ngược chiều."],
    en: ["In 1686 Isaac Newton presented his three laws of motion in the *Principia*. Three sentences — and they are still the basis of modern physics.",
         "**The first:** an object at rest remains at rest, and an object in motion remains in motion at constant speed and in a straight line, unless acted on by an unbalanced force. That tendency to resist changes in a state of motion is called INERTIA.",
         "**The second:** the acceleration of an object depends on the mass of the object and the amount of force applied.",
         "**The third:** whenever one object exerts a force on another object, the second object exerts an equal and opposite force back on the first."]
  },
  more: {
    vi: ["Câu thứ nhất là câu khó tin nhất, và đáng dừng lại ở đó.",
         "Nó nói rằng một vật đang chuyển động sẽ CỨ THẾ chuyển động mãi mãi. Nhưng ai đẩy một quyển sách trên bàn cũng thấy nó dừng lại. Vậy Newton sai à?",
         "Không. Quyển sách dừng vì có lực tác dụng lên nó — ma sát. Trên Trái Đất, ma sát và sức cản không khí có mặt ở khắp nơi, nên ta lớn lên với một cảm giác SAI: rằng vật phải được đẩy liên tục mới chuyển động được. Đó là cảm giác mà loài người tin suốt gần hai nghìn năm trước Newton.",
         "Chỗ dễ thấy điều ngược lại nhất chính là không gian. Ở đó gần như không có gì cản, nên một con tàu tắt hẳn động cơ vẫn bay tiếp — không phải vì nó còn nhiên liệu, mà vì **không có gì bảo nó dừng**. Tàu Voyager rời hệ Mặt Trời với động cơ đã tắt từ lâu.",
         "Và ba câu này còn với xa hơn chuyển động của một quyển sách: cùng với các định luật của Kepler, chúng giải thích vì sao các hành tinh đi theo quỹ đạo hình elip chứ không phải hình tròn — đúng thứ mà nhánh Toán & đo lường đã đi qua ở bài về quỹ đạo.",
         "⚠️ Ví dụ quyển sách, ví dụ Voyager và câu về \"gần hai nghìn năm\" là cách astroQ giải thích; trang NASA phát biểu ba định luật và nêu mối liên hệ với Kepler, không kể những ví dụ này."],
    en: ["The first law is the hardest to believe, and it is worth stopping there.",
         "It says an object in motion will KEEP moving forever. But push a book across a table and it stops. So was Newton wrong?",
         "No. The book stops because a force acts on it — friction. On Earth, friction and air resistance are everywhere, so we grow up with a FALSE feeling: that a thing must be pushed continuously to keep moving. That is the feeling humanity believed for nearly two thousand years before Newton.",
         "The easiest place to see the opposite is space. There is almost nothing to resist there, so a spacecraft with its engines fully off keeps travelling — not because it still has fuel, but because **nothing tells it to stop**. Voyager left the Solar System with its engines long since silent.",
         "And these three sentences reach further than a sliding book: together with Kepler's laws they explained why planets move in elliptical orbits rather than circles — exactly what the Maths & measuring branch walked through in its article on orbits.",
         "⚠️ The book example, the Voyager example and the \"nearly two thousand years\" remark are astroQ's explanation; the NASA page states the three laws and notes the link to Kepler without telling these stories."]
  },
  term: { who: "comet",
          word: { vi: "Quán tính",
                  en: "Inertia" },
          text: { vi: "xu hướng của một vật chống lại việc bị đổi trạng thái chuyển động. Vật càng nặng thì càng khó đẩy cho đi — và cũng càng khó bắt cho dừng. ☄️",
                  en: "An object's tendency to resist any change to its state of motion. The heavier it is, the harder it is to get moving — and just as hard to stop. ☄️" } }
};
