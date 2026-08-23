/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/mission/mars-climate-orbiter/ (kiem 200 · 14/08/2026)
   Trich nguyen van — CHI CO HAI CAU NAY, va bai viet khong duoc di xa hon:
     · "Ground software used English units, while onboard software worked in
        metric. The discrepancy caused errors in trajectory calculations which
        sent the spacecraft too close to Mars."
     · "Last contact with the spacecraft was on Sept. 23, 1999, nine months after
        launch, and an investigation found that the spacecraft burned up in
        Mars' atmosphere."

   ⚠️⚠️ CON SO "170 km thap hon du tinh" CO TRONG BAN TOM TAT CUA BO TRA CUU
      nhung **KHONG CO TREN TRANG NAY** (no nam o bao cao cua ban dieu tra, mot
      tai lieu khac). DUNG dua vao bai roi dan URL nay. Day dung lop loi da mac
      ba lan (Nam Cuc "chau luc cao nhat" · ba tieu chi IAU · CHNOPS) — va lan
      nay no cam do hon vi con so nghe rat "chac".
   ⚠️ Trang cung KHONG noi doi nao dung don vi nao ngoai "ground software" va
      "onboard software". Dung gan trach nhiem cho mot nhom cu the. */
export default {
  ord: 7010,
  id: "art-units-lost-a-spacecraft",
  src: "NASA",
  cat: "math",
  em: "📏",
  c: ["#ffcf6b", "#d1892f", "#3a2a0c"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/mission/mars-climate-orbiter/",
  title: { vi: "Một con tàu mất vì hai bên dùng hai đơn vị khác nhau",
          en: "A spacecraft was lost because two sides used different units" },
  body: {
    vi: ["Năm 1999, tàu Mars Climate Orbiter bay chín tháng để tới Sao Hoả. Nó không bao giờ vào được quỹ đạo.",
         "Nguyên nhân không phải một con ốc lỏng hay một cú va chạm. Phần mềm dưới mặt đất dùng hệ đơn vị Anh, còn phần mềm trên tàu làm việc bằng hệ mét. Sự lệch nhau đó gây ra sai số trong việc tính đường bay, và đưa con tàu tới quá gần Sao Hoả.",
         "Liên lạc cuối cùng là ngày 23 tháng 9 năm 1999. Cuộc điều tra kết luận con tàu đã cháy trong khí quyển Sao Hoả.",
         "Cả hai bên đều tính đúng. Phép tính không sai một chỗ nào. Thứ sai là ở chỗ hai bên không nói cùng một thứ tiếng khi nói về những con số."],
    en: ["In 1999 the Mars Climate Orbiter flew for nine months to reach Mars. It never made it into orbit.",
         "The cause was not a loose bolt or a collision. Ground software used English units, while onboard software worked in metric. That discrepancy caused errors in the trajectory calculations, which sent the spacecraft too close to Mars.",
         "Last contact was on 23 September 1999. An investigation found that the spacecraft burned up in Mars' atmosphere.",
         "Both sides did their arithmetic correctly. Not a single calculation was wrong. What was wrong is that the two sides were not speaking the same language about their numbers."]
  },
  more: {
    vi: ["Câu chuyện này thường được kể như một chuyện cười về sự bất cẩn. Nó không phải vậy — và chỗ đáng học nằm đúng ở đó.",
         "Một con số trần trụi không mang đủ thông tin. \"5\" không nói được gì cả: 5 mét hay 5 dặm? 5 giây hay 5 giờ? Đơn vị không phải cái đuôi trang trí gắn sau con số — nó là NỬA CÒN LẠI của thông tin. Bỏ nó đi thì con số mất nghĩa, mà điều nguy hiểm là nó **trông vẫn như một con số dùng được**.",
         "Vì thế trong khoa học và kỹ thuật, mỗi đại lượng luôn đi kèm đơn vị, và người ta bỏ công ghi rõ đơn vị ở mọi chỗ dữ liệu đổi tay. Nghe thừa thãi — cho tới lúc nó không còn thừa.",
         "Có một thói quen nhỏ đáng mượn cho bài tập ở trường: viết đơn vị vào MỌI bước của phép tính, đừng chỉ viết ở kết quả cuối. Nếu đơn vị ở hai vế không khớp nhau thì bạn biết mình sai TRƯỚC khi ra đáp số — chứ không phải sau khi đã đi chín tháng đường."],
    en: ["This story is often told as a joke about carelessness. It is not — and that is exactly where the lesson sits.",
         "A bare number does not carry enough information. \"5\" says nothing on its own: 5 metres or 5 miles? 5 seconds or 5 hours? A unit is not decorative trim stuck on the end of a number — it is the OTHER HALF of the information. Drop it and the number loses its meaning, and the dangerous part is that it **still looks like a usable number**.",
         "That is why in science and engineering every quantity travels with its unit, and people take the trouble to state units everywhere data changes hands. It sounds like overkill — right up until it isn't.",
         "There is a small habit worth borrowing for schoolwork: write the units at EVERY step of a calculation, not just on the final answer. If the units on the two sides do not match, you know you are wrong BEFORE you reach a result — rather than after travelling for nine months."]
  },
  term: { who: "comet",
          word: { vi: "Đơn vị",
                  en: "Unit" },
          text: { vi: "thứ cho biết một con số đang đo cái gì và đo bằng thước nào. Hai người cùng viết \"5\" mà khác đơn vị thì họ đang nói về hai thứ khác nhau — dù trên giấy trông y hệt. ☄️",
                  en: "The thing that tells you what a number measures and on whose ruler. Two people can both write \"5\" and mean two different things — even though on paper it looks identical. ☄️" } },
  /* Noi voi kho cau hoi: bai day dung nguyen nhan: phan mem duoi mat dat dung he Anh, phan mem tren tau dung he met. (Khong hoi con so \"170 km\" — trang nguon KHONG co con so do.) */
  terms: ["units-lost-an-orbiter"]
};
