/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/big-idea-3-2-intermediate-level-guiding-question/
          (kiem 200 · 14/08/2026)
   Trich nguyen van:
     · "Solar panels, most commonly made out of silicon"
     · pin quang dien la "a device that converts light energy into electrical energy"
     · "The dark silicon absorbs the photons, or particles from light, which the PV
        cells convert into electricity"
     · "Buildings with solar panels can store the energy in batteries for when it is
        nighttime or when it is cloudy"
     · "Instead of batteries, which can be expensive, many households will connect
        to the electrical grid"

   ⚠️ CON SO VE TRAM VU TRU (hon 20 kilowatt · tang 30% cong suat · tam pin chinh)
      KHONG nam o trang nay — no o
      `nasa.gov/international-space-station/international-space-station-assembly-elements/`.
      Neu muon dua vao bai thi phai dan THEM URL do; ban hien tai CO Y khong dung
      con so ay de bai chi mang dung mot nguon. Dung nho mot con so tu trang khac
      roi de nguyen mot URL — do la lop loi da mac bon lan (Nam Cuc · IAU · CHNOPS
      · "170 km").

   ⚠️ Mat xich nay noi ANH SANG voi DIEN trong chuoi vat ly, va bai anh sang
      (`art-light-and-shadow-space`) da co san — dung viet lai noi dung bai do. */
export default {
  ord: 8070,
  id: "art-sunlight-into-electricity",
  src: "NASA",
  cat: "physics",
  em: "⚡",
  c: ["#a8d8ff", "#3f86c9", "#0d1f38"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/big-idea-3-2-intermediate-level-guiding-question/",
  title: { vi: "Ánh sáng biến thành điện ở đâu? Ngay trong một tấm silic đen",
          en: "Where does light turn into electricity? Inside a black slab of silicon" },
  body: {
    vi: ["Một tấm pin mặt trời không có bộ phận nào chuyển động. Không bánh răng, không tuabin, không tiếng động. Vậy mà nó tạo ra điện.",
         "Tấm pin thường được làm từ silic, và nó gồm nhiều ô nhỏ gọi là pin quang điện — mỗi ô là một thiết bị biến năng lượng ánh sáng thành năng lượng điện.",
         "Cách nó làm: lớp silic sẫm màu hấp thụ các photon — tức các hạt của ánh sáng — và các ô quang điện biến chúng thành điện.",
         "Còn ban đêm, hoặc khi trời nhiều mây? Những toà nhà có pin mặt trời có thể trữ năng lượng trong ắc quy. Ắc quy thì đắt, nên thay vì vậy nhiều gia đình chọn nối vào lưới điện."],
    en: ["A solar panel has no moving parts. No gears, no turbine, no noise. And yet it makes electricity.",
         "Panels are most commonly made out of silicon, and each holds many small units called photovoltaic cells — each one a device that converts light energy into electrical energy.",
         "How it does it: the dark silicon absorbs the photons, the particles of light, and the PV cells convert them into electricity.",
         "And at night, or when it is cloudy? Buildings with solar panels can store the energy in batteries. Batteries can be expensive, so instead of them many households will connect to the electrical grid."]
  },
  more: {
    vi: ["Chỗ đáng nghĩ nhất của bài này nằm ở chữ **hạt**.",
         "Ta quen hình dung ánh sáng như một dòng chảy liên tục, giống nước từ vòi. Nhưng NASA gọi photon là *particles from light* — HẠT của ánh sáng. Một tấm pin mặt trời không tắm trong ánh sáng như tắm trong nước; nó **bị bắn trúng bởi từng hạt một**, và mỗi hạt trúng đích thì góp một phần vào dòng điện.",
         "Nghĩ theo cách đó thì hai chuyện thường ngày bỗng có lý. Vì sao trời râm thì pin yếu đi mà không tắt hẳn? Vì số hạt tới ít đi chứ không phải hết. Vì sao tấm pin lại có màu ĐEN? Vì màu đen nghĩa là hấp thụ chứ không phản xạ — mỗi hạt bị hắt ngược ra là một hạt không sinh được điện.",
         "Đây cũng là mắt xích nối hai bài trong chính nhánh Vật lý này: bài về ánh sáng nói ánh sáng là gì, còn bài này nói nó biến thành thứ khác ở đâu. Và ngoài không gian thì mắt xích ấy là chuyện sống còn — không có dây điện nào kéo lên tới quỹ đạo cả.",
         "⚠️ Phần suy luận về màu đen và về trời râm là cách astroQ giải thích; trang NASA nêu rằng silic sẫm màu hấp thụ photon, chứ không rút ra hai kết luận này."],
    en: ["The most interesting part of this article sits in one word: **particles**.",
         "We are used to imagining light as a continuous flow, like water from a tap. But NASA calls photons *particles from light*. A solar panel does not bathe in light the way you bathe in water; it is **struck by one particle at a time**, and each particle that lands contributes a share of the current.",
         "Thought of that way, two everyday things suddenly make sense. Why does a panel weaken on an overcast day without switching off? Because fewer particles arrive, not none. And why is a panel BLACK? Because black means absorbing rather than reflecting — every particle bounced away is one that generates no electricity.",
         "This is also the link between two articles in this very Physics branch: the one about light says what light is, and this one says where it turns into something else. Out in space that link is a matter of survival — no power cable reaches orbit.",
         "⚠️ The reasoning about the black colour and about overcast days is astroQ's explanation; the NASA page states that dark silicon absorbs photons without drawing these two conclusions."]
  },
  term: { who: "comet",
          word: { vi: "Photon",
                  en: "Photon" },
          text: { vi: "hạt của ánh sáng. Ánh sáng vừa cư xử như sóng vừa như một dòng hạt — và đúng cái nửa \"hạt\" ấy mới là thứ làm cho tấm pin mặt trời chạy được. ☄️",
                  en: "A particle of light. Light behaves both as a wave and as a stream of particles — and it is exactly that \"particle\" half that makes a solar panel work. ☄️" } },
  /* Noi voi kho cau hoi: bai day dung cho hap thu: lop silic sam mau hut cac photon roi o quang dien bien chung thanh dien. */
  terms: ["solar-cell-absorbs-photons"]
};
