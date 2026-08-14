/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/asset/hubble/stellar-parallax/ (kiem 200 · 14/08/2026)
   Trich nguyen van — DUNG BA CAU NAY, trang khong noi gi hon:
     · "This requires viewing the star on two occasions, when Earth is at opposite
        sides of the Sun."
     · "The Hubble Space Telescope can then precisely measure the very small
        angular displacement of the star between observations."
     · "When the offset value is combined using geometry with the value for
        Earth's orbital diameter, a precise distance can be calculated."
     · "Land surveyors commonly use this triangulation technique."

   ⚠️ PHEP VI NGON TAY / NHAM MOT MAT **KHONG CO TREN TRANG NAY** — bo tra cuu
      lay no tu mot trang khac. No la mot cach day, khong phai mot phat bieu can
      nguon, nen duoc phep dung — nhung phai nam o `more` va doc ra la loi cua
      astroQ. Cung ranh gioi da giu o `art-loop-you-can-see-on-mars`.
   ⚠️ Trang KHONG noi khoang cach sau THANG. No noi "hai lan quan sat khi Trai Dat
      o hai phia doi dien cua Mat Troi" — viet dung nhu vay. */
export default {
  ord: 7030,
  id: "art-measuring-stars-with-angles",
  src: "NASA",
  cat: "math",
  em: "📡",
  c: ["#ffd9a0", "#c98a3a", "#33240c"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/asset/hubble/stellar-parallax/",
  title: { vi: "Đo khoảng cách tới một ngôi sao mà không cần tới gần nó",
          en: "Measuring the distance to a star without going near it" },
  body: {
    vi: ["Không ai kéo được một cái thước dây tới ngôi sao. Vậy mà ta biết chúng cách bao xa — và cách làm chỉ cần một thứ: một GÓC.",
         "Muốn đo, phải quan sát ngôi sao đó hai lần, vào hai thời điểm khi Trái Đất nằm ở hai phía đối diện của Mặt Trời. Giữa hai lần ấy, ngôi sao có vẻ nhích đi một chút so với nền trời phía sau.",
         "Kính Hubble đo được rất chính xác cái độ dịch góc tí xíu đó. Rồi khi ghép con số ấy với đường kính quỹ đạo Trái Đất bằng hình học, ta tính ra được một khoảng cách chính xác.",
         "Cách này không lạ chút nào: chính những người đo đạc đất đai vẫn dùng kỹ thuật tam giác đó hằng ngày. Chỉ khác là tam giác của các nhà thiên văn có một cạnh dài bằng cả quỹ đạo Trái Đất."],
    en: ["Nobody can stretch a tape measure to a star. Yet we know how far away they are — and the method needs only one thing: an ANGLE.",
         "To measure it, you must view the star on two occasions, when Earth is at opposite sides of the Sun. Between those two views, the star appears to shift a little against the background sky.",
         "The Hubble Space Telescope can precisely measure that very small angular displacement. Then, when that offset is combined using geometry with the value for Earth's orbital diameter, a precise distance can be calculated.",
         "The method is nothing exotic: land surveyors commonly use this same triangulation technique. The only difference is that an astronomer's triangle has one side as long as Earth's whole orbit."]
  },
  more: {
    vi: ["Bạn thử được ngay bây giờ, không cần kính thiên văn nào. Giơ một ngón tay ra trước mặt, nhắm mắt trái rồi đổi sang nhắm mắt phải. Ngón tay như nhảy sang bên so với thứ ở xa phía sau — dù nó chẳng hề nhúc nhích.",
         "Cái \"nhảy\" đó là một góc, và nó phụ thuộc vào hai thứ: khoảng cách giữa hai mắt bạn, và ngón tay ở gần hay xa. Đưa ngón tay ra xa hơn, cú nhảy nhỏ đi. Càng xa thì góc càng nhỏ.",
         "Các nhà thiên văn làm đúng như vậy, chỉ thay hai con mắt bằng hai VỊ TRÍ của Trái Đất ở hai phía đối diện của Mặt Trời — một cặp \"mắt\" cách nhau bằng cả đường kính quỹ đạo. Cần cặp mắt to đến thế vì các ngôi sao ở quá xa: với chúng, cú nhảy nhỏ tới mức mắt thường không thấy nổi, phải có kính như Hubble mới đo được.",
         "Và đây là chỗ toán học trở nên đáng nể: bạn không cần đi tới chỗ một vật để biết nó cách bao xa. Chỉ cần đo được một góc và biết được chiều dài của cạnh mình đang đứng, hình học sẽ trả nốt phần còn lại.",
         "⚠️ Phép ví ngón tay và con mắt là cách astroQ giải thích cho dễ hình dung; trang của NASA nói về phép đo bằng Hubble và hình học, không dùng phép ví này."],
    en: ["You can try it right now, with no telescope at all. Hold up one finger in front of you, close your left eye, then swap to closing your right. The finger seems to jump sideways against whatever is far behind it — even though it never moved.",
         "That \"jump\" is an angle, and it depends on two things: the gap between your two eyes, and whether the finger is near or far. Move the finger further away and the jump gets smaller. The further, the smaller the angle.",
         "Astronomers do exactly this, only swapping two eyes for two POSITIONS of Earth at opposite sides of the Sun — a pair of \"eyes\" separated by an entire orbital diameter. They need eyes that far apart because stars are so distant: for them the jump is far too small for a human eye, and it takes a telescope like Hubble to measure it.",
         "And here is where the maths becomes impressive: you do not have to travel to a thing to know how far away it is. Measure one angle, know the length of the side you are standing on, and geometry supplies the rest.",
         "⚠️ The finger-and-eye comparison is astroQ's way of explaining it; the NASA page talks about the Hubble measurement and the geometry, and does not use this analogy."]
  },
  term: { who: "byte",
          word: { vi: "Thị sai",
                  en: "Parallax" },
          text: { vi: "hiện tượng một vật như dịch đi khi bạn nhìn nó từ hai chỗ khác nhau. Vật càng xa thì dịch càng ít — nên chính độ dịch ấy cho biết nó xa bao nhiêu. 🤖",
                  en: "The way an object seems to shift when you look at it from two different places. The further it is, the less it shifts — so that very shift tells you how far away it is. 🤖" } }
};
