/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/biological-physical/programs/space-biology/
          (kiem 200 ngay 14/08/2026)
   Trich nguyen van:
     · "The main objective of Space Biology research is to build a better
        understanding of how spaceflight affects living systems in spacecraft
        such as the International Space Station (ISS)."
     · nghien cuu "how plants, microbes, and animals adjust or adapt to living
        in space"
     · sinh vat mau: "rodents, both rats and mice, and a variety of invertebrate
        species, e.g., nematodes and insects."
     · cau hoi: "Do the effects of spaceflight level off over time, get worse, or
        get better?" · "Are the effects of spaceflight exposure permanent or do
        they decrease and/or vanish with time upon return?"
     · "How does gravity affect plant growth, development & metabolism…?"

   ⚠️ BAI NAY CO Y KHONG TRA LOI CAC CAU HOI DO — trang nguon cung khong tra loi.
      No la bai ve CACH DAT CAU HOI, tuc bai duy nhat cua nhanh nay noi ve phuong
      phap thay vi ve su that. Dung "lam giau" bang mot cau tra loi nghe hop ly. */
export default {
  ord: 6050,
  id: "art-space-biology-questions",
  src: "NASA",
  cat: "life",
  em: "🔬",
  c: ["#c9f07a", "#5aa03c", "#1a2a0e"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/biological-physical/programs/space-biology/",
  title: { vi: "Những câu hỏi mà ngành sinh học không gian chưa trả lời xong",
          en: "The questions space biology has not finished answering" },
  body: {
    vi: ["Sinh học không gian là ngành đi tìm hiểu chuyến bay vũ trụ ảnh hưởng thế nào tới các hệ sống bên trong tàu — chẳng hạn Trạm Vũ trụ Quốc tế.",
         "Nó không chỉ nghiên cứu con người. Nó xem cây cối, vi khuẩn và động vật điều chỉnh hoặc thích nghi ra sao khi sống trong không gian. Sinh vật thường được dùng gồm chuột cống và chuột nhắt, cùng nhiều loài không xương sống như giun tròn và côn trùng.",
         "Điều đáng chú ý nhất là NASA công bố thẳng những thứ họ CHƯA biết. Hai trong số đó: tác động của chuyến bay dài rồi sẽ chững lại, nặng thêm hay nhẹ đi? Và khi trở về Trái Đất thì những thay đổi đó là vĩnh viễn, hay giảm dần rồi biến mất?"],
    en: ["Space biology is the field studying how spaceflight affects living systems inside a spacecraft — for example the International Space Station.",
         "It does not only study humans. It looks at how plants, microbes and animals adjust or adapt to living in space. Common model organisms include rats and mice, plus many invertebrates such as nematodes and insects.",
         "The most striking part is that NASA publishes plainly what they do NOT yet know. Two of those: do the effects of spaceflight level off over time, get worse, or get better? And once back on Earth, are those changes permanent, or do they fade and vanish?"]
  },
  more: {
    vi: ["Vì sao lại dùng giun tròn và côn trùng chứ không chỉ dùng người? Vì chúng có vòng đời rất ngắn. Một chuyến bay vài tháng đủ để quan sát nhiều THẾ HỆ nối tiếp nhau — thứ mà với con người phải chờ cả trăm năm. Muốn biết một thay đổi có truyền sang đời sau hay không thì phải có đời sau để mà nhìn.",
         "Ngành này còn hỏi một câu ở tầng sâu hơn: cơ chế di truyền và phân tử nào bên trong tế bào bị ảnh hưởng khi trọng lực thay đổi? Và với thực vật: trọng lực ảnh hưởng thế nào tới việc cây lớn lên, phát triển và trao đổi chất — kể cả quang hợp và cách cây tự vệ?",
         "Hãy để ý cách những câu đó được viết. Chúng không hỏi \"có ảnh hưởng không\" mà hỏi \"ảnh hưởng NHƯ THẾ NÀO\", và chúng nêu sẵn cả ba khả năng (chững lại / nặng hơn / nhẹ đi) thay vì đoán trước một khả năng. Đó là cách một câu hỏi khoa học được đặt cho tử tế: nó chừa chỗ cho câu trả lời làm mình bất ngờ."],
    en: ["Why use nematodes and insects instead of only people? Because their life cycles are very short. A flight of a few months is enough to watch several GENERATIONS follow one another — something that would take a century with humans. To find out whether a change passes to the next generation, you need a next generation to look at.",
         "The field also asks a deeper-level question: which genetic and molecular mechanisms inside cells are influenced when gravity changes? And for plants: how does gravity affect growth, development and metabolism — including photosynthesis and how a plant defends itself?",
         "Notice how those are worded. They do not ask \"is there an effect\" but \"HOW does it act\", and they lay out all three possibilities (level off / get worse / get better) instead of guessing one in advance. That is what a properly posed scientific question looks like: it leaves room for the answer to surprise you."]
  },
  term: { who: "byte",
          word: { vi: "Sinh vật mẫu",
                  en: "Model organism" },
          text: { vi: "một loài được chọn để nghiên cứu vì nó dễ nuôi, lớn nhanh và ta đã hiểu rõ nó — nên thứ học được từ nó giúp hiểu cả những loài khó nghiên cứu hơn, kể cả chúng ta. 🤖",
                  en: "A species picked for study because it is easy to keep, grows fast and is already well understood — so what we learn from it helps explain harder species too, including us. 🤖" } },
  /* Noi voi kho cau hoi: bai day ca hai: NASA cong bo cau chua tra loi xong (vinh vien hay giam dan), va sinh vat thuong dung la chuot cung giun tron va con trung. */
  terms: ["space-biology-open-question", "model-organisms-space"]
};
