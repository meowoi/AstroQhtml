/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do.

   NGUON: https://www.nasa.gov/hrp/bodyinspace/ (kiem 200 ngay 14/08/2026)
   Trich nguyen van dung de viet bai nay:
     · "weight-bearing bones lose on average 1% to 1.5% of mineral density
        per month during spaceflight"
     · "astronauts also lose muscle mass in microgravity faster than they
        would on Earth"
     · "fluids in the body shift upward to the head in microgravity, which
        may put pressure on the eyes"
   ⚠️ DUNG viet "xuong mat 1% moi thang" chung chung — trang noi ro la XUONG
      CHIU LUC (weight-bearing) va la con so TRUNG BINH. Bo hai chu do la
      bien mot phep do thanh mot lo^`i khang dinh rong hon trang noi. */
export default {
  ord: 6010,
  id: "art-body-in-space-changes",
  src: "NASA",
  cat: "life",
  em: "🧑‍🚀",
  c: ["#7ee07a", "#3f9e5c", "#0d2c22"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/hrp/bodyinspace/",
  title: { vi: "Cơ thể bạn sẽ đổi khác nếu sống trên trạm vũ trụ",
          en: "Your body changes if you live on a space station" },
  body: {
    vi: ["Cơ thể người lớn lên trong lực hấp dẫn của Trái Đất. Bỏ lực đó đi thì cơ thể lập tức đi tìm một cách sống mới — và nó đổi nhanh hơn bạn tưởng.",
         "Xương chịu lực (xương chân, xương hông — những xương ngày nào cũng phải đỡ sức nặng của bạn) mất trung bình 1% đến 1,5% mật độ khoáng mỗi tháng bay. Cơ bắp cũng teo đi nhanh hơn so với khi ở Trái Đất, vì gần như chẳng còn việc gì cho chúng làm.",
         "Chất lỏng trong người thì dồn ngược lên đầu. Mặt phi hành gia trông đầy đặn hơn, chân thì thon lại — và chính áp lực đó có thể đè lên mắt, nên thị lực là một trong những thứ NASA theo dõi kỹ nhất."],
    en: ["The human body grows up inside Earth's gravity. Take that pull away and the body immediately starts looking for a new way to work — and it changes faster than you would guess.",
         "Weight-bearing bones — the leg and hip bones that carry your weight every single day — lose on average 1% to 1.5% of their mineral density per month of spaceflight. Muscles shrink faster than they would on Earth too, because there is barely any work left for them to do.",
         "Body fluids shift upward toward the head. Astronauts' faces look puffier and their legs get thinner — and that same pressure can push on the eyes, which is why vision is one of the things NASA watches most closely."]
  },
  more: {
    vi: ["Vì sao xương lại phản ứng như vậy? Xương không phải một thanh đá chết. Nó là mô sống, liên tục được phá đi và xây lại, và tín hiệu nói cho nó biết \"cần xây dày tới đâu\" chính là SỨC NẶNG đè lên nó mỗi ngày. Bỏ sức nặng đi thì cơ thể đọc ra rằng chỗ đó không cần dày như thế nữa.",
         "Đó cũng là lý do phi hành gia trên trạm phải tập thể dục hằng ngày với những cỗ máy kéo họ ép xuống — không phải để cho khoẻ đẹp, mà để dựng lại cái tín hiệu mà vi trọng lực vừa lấy mất.",
         "Và đây là chỗ nó vòng về Trái Đất: cùng cơ chế đó giải thích vì sao người nằm liệt giường lâu ngày cũng mất mật độ xương. Nghiên cứu để giữ sức khoẻ cho phi hành gia vì thế giúp luôn cả bệnh nhân dưới mặt đất."],
    en: ["Why do bones react that way? Bone is not a dead stick of stone. It is living tissue, constantly torn down and rebuilt, and the signal telling it how thick to build is the WEIGHT pressing on it every day. Remove the weight and the body reads it as: this part no longer needs to be that thick.",
         "That is also why astronauts exercise daily on machines that pull them down against a load — not to look strong, but to rebuild the very signal that microgravity took away.",
         "And here is where it loops back to Earth: the same mechanism explains why people on long bed rest also lose bone density. Research meant to keep astronauts healthy ends up helping patients on the ground too."]
  },
  term: { who: "byte",
          word: { vi: "Xương chịu lực",
                  en: "Weight-bearing bone" },
          text: { vi: "những xương phải đỡ sức nặng cơ thể khi bạn đứng và đi — xương chân, xương hông. Chúng mất khoáng nhanh nhất trong không gian, vì chúng là những xương mất việc nhiều nhất. 🦴",
                  en: "The bones that carry your body weight when you stand and walk — legs and hips. They lose mineral fastest in space, because they are the ones that lose the most work to do. 🦴" } }
};
