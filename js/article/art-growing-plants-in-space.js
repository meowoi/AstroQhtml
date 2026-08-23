/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www.nasa.gov/exploration-research-and-technology/growing-plants-in-space/
          (kiem 200 ngay 14/08/2026)
   Trich nguyen van:
     · "Veggie has successfully grown a variety of plants, including three types
        of lettuce, Chinese cabbage, mizuna mustard, red Russian kale and zinnia
        flowers."
     · Veggie "about the size of a carry-on piece of luggage and typically holds
        six plants. Each plant grows in a 'pillow' filled with a clay-based
        growth media and fertilizer."
     · "the roots would either drown in water or be engulfed by air because of
        the way fluids in space tend to form bubbles."
     · "Once, the zinnias in Veggie got a little overwatered, and there was a
        lack of air flow. A fungus started growing on the plants, and some died."

   ⚠️ SU CO HOA KEM LA PHAN DANG GIU NHAT, dung cat cho gon: no cho tre thay
      mot that bai THAT trong khoa hoc, va no giai thich vi sao "goi trong cay"
      lai kho — chu khong phai mot danh sach thanh tuu. */
export default {
  ord: 6040,
  id: "art-growing-plants-in-space",
  src: "NASA",
  cat: "life",
  em: "🌱",
  c: ["#a8f07a", "#4aa03c", "#132a10"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/exploration-research-and-technology/growing-plants-in-space/",
  title: { vi: "Trồng rau trên trạm vũ trụ khó ở chỗ tưới nước",
          en: "The hard part of gardening in space is watering" },
  body: {
    vi: ["Trên Trạm Vũ trụ Quốc tế có một khu vườn tên là Veggie. Nó chỉ to cỡ một chiếc vali xách tay và thường trồng được sáu cây một lúc.",
         "Veggie đã trồng thành công ba loại xà lách, cải thảo, cải mizuna, cải xoăn đỏ Nga và cả hoa cúc zinnia. Mỗi cây mọc trong một cái \"gối\" chứa giá thể gốc đất sét trộn phân bón.",
         "Chỗ khó nhất không phải ánh sáng mà là NƯỚC. Trong không gian, chất lỏng có xu hướng tụ lại thành bong bóng, nên rễ cây có thể chết đuối trong nước hoặc ngược lại bị bọc kín trong không khí — hai kiểu chết hoàn toàn trái ngược nhau, gây ra bởi cùng một nguyên nhân."],
    en: ["On the International Space Station there is a garden called Veggie. It is only about the size of a carry-on suitcase and typically holds six plants at a time.",
         "Veggie has successfully grown three types of lettuce, Chinese cabbage, mizuna mustard, red Russian kale, and even zinnia flowers. Each plant grows in a \"pillow\" filled with clay-based growth media and fertilizer.",
         "The hardest part is not light — it is WATER. In space, fluids tend to pull together into bubbles, so roots can either drown in water or get completely engulfed in air — two opposite ways to die, caused by the same thing."]
  },
  more: {
    vi: ["Có một lần cây cúc zinnia trong Veggie bị tưới hơi quá tay, cộng thêm luồng không khí lưu thông kém. Nấm bắt đầu mọc trên cây, và một số cây chết.",
         "Đáng chú ý là chuyện đó được ghi lại và kể ra, chứ không giấu đi. Một thí nghiệm hỏng vẫn là dữ liệu: nó chỉ đúng vào hai thứ mà một khu vườn trên mặt đất gần như không bao giờ phải lo — nước không tự chảy xuống, và không khí không tự đối lưu. Trên Trái Đất, không khí ấm nhẹ hơn nên tự bốc lên và kéo theo một luồng gió quanh lá; trong vi trọng lực thì \"nhẹ hơn\" không còn nghĩa gì, nên không khí đứng yên quanh cây nếu không có quạt.",
         "Vì sao NASA vẫn cố trồng? Vì thức ăn đóng gói mất dần dinh dưỡng theo thời gian, nên với những chuyến đi thật dài thì rau tươi không phải món xa xỉ mà là một phần của việc giữ cho người bay khoẻ mạnh. Và còn một lý do nữa ít ai nghĩ tới: một mảng xanh sống động có tác dụng tinh thần đối với người sống nhiều tháng trong một cái hộp kim loại."],
    en: ["Once the zinnias in Veggie got a little overwatered, and there was a lack of air flow. A fungus started growing on the plants, and some of them died.",
         "What is notable is that this was recorded and told, not hidden. A failed experiment is still data: it points at exactly the two things an Earth garden almost never worries about — water does not flow downward on its own, and air does not circulate on its own. On Earth warm air is lighter so it rises and drags a breeze past the leaves; in microgravity \"lighter\" stops meaning anything, so air just sits around the plant unless a fan moves it.",
         "Why does NASA keep trying? Because prepackaged food loses nutrients over time, so on really long trips fresh produce is not a luxury but part of keeping the crew healthy. And there is a reason fewer people think of: a living patch of green does something for the mind of someone living for months inside a metal box."]
  },
  term: { who: "byte",
          word: { vi: "Giá thể",
                  en: "Growth media" },
          text: { vi: "thứ thay cho đất để giữ rễ cây và giữ nước. Trong Veggie nó làm từ đất sét — đất thường sẽ bay lả tả khắp trạm ngay khi ai đó mở nắp. 🤖",
                  en: "The stuff that replaces soil to hold roots and water. In Veggie it is clay-based — ordinary loose soil would drift all over the station the moment someone opened the lid. 🤖" } },
  /* Noi voi kho cau hoi: bai day dung co che: chat long tu thanh bong bong nen re co the chet duoi HOAC bi boc kin trong khong khi. (Khong noi cau nao ve anh sang: bai noi ro cho kho KHONG phai anh sang.) */
  terms: ["plants-water-in-space"]
};
