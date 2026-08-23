/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/exoplanets/what-is-a-light-year/ (kiem 200 · 14/08/2026)
   Trich nguyen van:
     · "Light-year is the distance light travels in one year."
     · "5.88 trillion miles (9.46 trillion kilometers) per year."
     · "A little more than four light-years away, or 24 trillion miles."
     · "Keep going to Proxima Centauri, our nearest neighboring star, and plan on
        arriving in 4.25 years at light speed."
     · "Earth is about eight light minutes from the Sun."
     · "If an airline offered a flight there by jet, it would take 5 million years."

   ⚠️ TRANG NAY CHO CA HAI HE DON VI (dam VA ki-lo-met) cho con so 9,46 nghin ti,
      nen duoc phep dung km. Nhung con so 24 nghin ti thi trang **CHI CHO DAM** —
      viet "24 nghin ti dam" va noi ro do la don vi NASA dung, dung tu quy sang km.
      Cung luat da ap cho Canadarm2 (foot/pound) va toc do 17.500 dam/gio.

   ⚠️ MAT XICH "TY LE" CUA CHUOI TOAN NAM O PHAN `more` CUA CHINH BAI NAY, co y:
      8 phut anh sang so voi 4,25 nam anh sang la mot bai hoc ve TY LE dep hon bat
      cu vi du bia nao, va no dung so lieu da co nguon o than bai. Xem docs/decisions/010. */
export default {
  ord: 7020,
  id: "art-light-year-is-a-distance",
  src: "NASA",
  cat: "math",
  em: "📐",
  c: ["#ffe08a", "#d1a02f", "#3a2f0c"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/exoplanets/what-is-a-light-year/",
  title: { vi: "Năm ánh sáng là một khoảng cách, không phải một khoảng thời gian",
          en: "A light-year is a distance, not a length of time" },
  body: {
    vi: ["Cái tên đánh lừa gần như mọi người lần đầu nghe. Có chữ \"năm\" trong đó, nên ai cũng tưởng nó đo thời gian. Không phải: năm ánh sáng là QUÃNG ĐƯỜNG mà ánh sáng đi được trong một năm.",
         "Quãng đường đó là 9,46 nghìn tỉ ki-lô-mét. Viết ra thì chỉ là một dãy số; điều đáng nghĩ là nó dùng để làm gì.",
         "Vũ trụ quá rộng để đo bằng ki-lô-mét — cũng như bạn không đo quãng đường từ nhà tới trường bằng mi-li-mét. Nên các nhà thiên văn đổi sang một cái thước dài hơn, và cái thước đó chính là quãng đường ánh sáng đi trong một năm.",
         "Với thước ấy: Trái Đất cách Mặt Trời khoảng tám phút ánh sáng. Còn ngôi sao gần chúng ta nhất, Proxima Centauri, thì hơn bốn năm ánh sáng một chút — tức 24 nghìn tỉ dặm (đơn vị NASA dùng cho con số này). Đi bằng máy bay phản lực thì mất 5 triệu năm."],
    en: ["The name fools almost everyone the first time. It has the word \"year\" in it, so people assume it measures time. It does not: a light-year is the DISTANCE light travels in one year.",
         "That distance is 9.46 trillion kilometres. Written out it is just a row of digits; what matters is what it is for.",
         "The universe is too big to measure in kilometres — just as you would not measure your walk to school in millimetres. So astronomers switched to a longer ruler, and that ruler is how far light gets in a year.",
         "With that ruler: Earth is about eight light-minutes from the Sun. And the nearest star to us, Proxima Centauri, is a little more than four light-years away — 24 trillion miles (NASA's unit for this figure). By jet, the trip would take 5 million years."]
  },
  more: {
    vi: ["Hai con số ở cuối bài đứng cạnh nhau mới nói ra điều đáng nói nhất, và đó là một bài học về TỈ LỆ.",
         "Mặt Trời cách ta tám PHÚT ánh sáng. Ngôi sao gần nhất cách ta hơn bốn NĂM ánh sáng. Một năm có khoảng 525.600 phút, nên bốn năm ánh sáng dài hơn tám phút ánh sáng khoảng hai trăm sáu mươi nghìn lần.",
         "Hãy thử đặt nó vào một tỉ lệ mà tay bạn cầm được: nếu khoảng cách Trái Đất–Mặt Trời co lại vừa đúng một bước chân của bạn, thì ngôi sao gần nhất sẽ nằm cách đó khoảng hai trăm sáu mươi ki-lô-mét — vẫn là ngôi sao GẦN NHẤT, trong một thiên hà có hàng trăm tỉ ngôi sao.",
         "Đó là việc mà tỉ lệ làm được còn con số trần thì không: \"9,46 nghìn tỉ\" không gợi lên gì trong đầu ai cả, nhưng \"một bước chân so với hai trăm sáu mươi ki-lô-mét\" thì hình dung được ngay. Khi một con số lớn tới mức mất nghĩa, hãy đổi nó thành một tỉ lệ giữa hai thứ bạn đã biết.",
         "⚠️ Con số hai trăm sáu mươi nghìn lần và hai trăm sáu mươi ki-lô-mét là phép chia của astroQ từ chính hai số liệu NASA nêu ở thân bài, không phải con số NASA viết ra trong trang ấy."],
    en: ["The two figures at the end of the article only say the important thing when you put them side by side — and that is a lesson about RATIO.",
         "The Sun is eight light-MINUTES away. The nearest star is more than four light-YEARS away. A year holds about 525,600 minutes, so four light-years is roughly two hundred and sixty thousand times further than eight light-minutes.",
         "Try putting that into a scale your hands can hold: if the Earth–Sun distance shrank to exactly one of your paces, the nearest star would sit about two hundred and sixty kilometres away — and that is still the NEAREST star, in a galaxy holding hundreds of billions of them.",
         "That is what a ratio does and a bare number cannot: \"9.46 trillion\" brings nothing to mind, but \"one pace versus two hundred and sixty kilometres\" lands immediately. When a number grows so large it stops meaning anything, turn it into a ratio between two things you already know.",
         "⚠️ The figures of two hundred and sixty thousand times and two hundred and sixty kilometres are astroQ's own division from the two NASA numbers quoted above, not figures NASA wrote on that page."]
  },
  term: { who: "comet",
          word: { vi: "Tỉ lệ",
                  en: "Ratio" },
          text: { vi: "phép so hai đại lượng với nhau thay vì đọc từng con số riêng lẻ. Nó là cách duy nhất làm cho những con số quá lớn hoặc quá nhỏ trở lại có nghĩa với đầu người. ☄️",
                  en: "Comparing two quantities against each other instead of reading each number alone. It is the only way to make numbers that are far too big or too small mean something to a human brain again. ☄️" } },
  /* Noi voi kho cau hoi: bai day ca hai: nam anh sang la QUANG DUONG chu khong phai thoi gian, va Trai Dat cach Mat Troi khoang tam phut anh sang. */
  terms: ["light-year-is-distance", "earth-eight-light-minutes"]
};
