/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www.nasa.gov/international-space-station/international-space-station-assembly-elements/
          (kiem 200 · 14/08/2026 — doc bang `curl`)

   Trich nguyen van:
     · "The roll-out solar arrays augment the International Space Station's eight
        main solar arrays. They produce more than 20 kilowatts of electricity and
        enable a 30% increase in power production over the station's current
        arrays."
     · "NASA spacewalker Stephen Bowen works to release a stowed roll-out solar
        array before installing it on the 1A power channel of the International
        Space Station's starboard truss structure."
     · "Spacewalkers Thomas Pesquet of ESA (European Space Agency) and Akihiko
        Hoshide of JAXA (Japan Aerospace Exploration Agency) set up the 4A channel
        on the International Space Station's P4 (Port) truss segment for the
        installation of an roll-out solar array."

   ⚠️ CHU **AUGMENT** LA CHOT CHAN CUA CA BAI — tam pin moi **THEM VAO** tam pin
      cu chu KHONG thay the. Dich thanh "thay the" la noi sai han cach he thong
      duoc nang cap, va lam hong luon phan `more`.

   ⚠️ "Hon 20 kilowatt" va "tang 30%" la HAI con so KHAC NHAU cua cung mot cau —
      20 kW la thu tam pin MOI sinh ra, 30% la muc tang so voi bo cu. Dung gop
      thanh mot y.

   ⚠️ TRANG **KHONG** NOI ISS can bao nhieu kilowatt tong cong, cung khong noi
      tam pin cu sinh ra bao nhieu. Dung suy nguoc tu 30% ra con so do roi viet
      nhu the trang co noi — do dung la lop loi da mac bon lan (CHNOPS · "170 km"
      · Nam Cuc · IAU).

   ⚠️ Phan ve khung gian (truss) o trang nay chi xuat hien trong CHU THICH ANH
      ("starboard truss structure" · "P4 (Port) truss segment"). Du de noi rang
      tam pin duoc gan len khung, KHONG du de viet mot doan rieng ve khung gian. */
export default {
  ord: 9020,
  id: "art-rollout-solar-arrays",
  src: "NASA",
  cat: "engineering",
  em: "🔌",
  c: ["#c0a4ff", "#6b4fd0", "#150f33"],
  img: null,
  credit: null,
  url: "https://www.nasa.gov/international-space-station/international-space-station-assembly-elements/",
  title: { vi: "Nâng cấp nhà máy điện của một con tàu không thể mang về xưởng",
          en: "Upgrading the power plant of a machine you can never bring home" },
  body: {
    vi: ["Trạm Vũ trụ Quốc tế chạy bằng điện mặt trời. Nó có **tám tấm pin chính**, và chúng đã ở trên đó rất lâu rồi.",
         "Trên Trái Đất, pin cũ thì tháo ra thay cái mới. Ngoài quỹ đạo thì không có xưởng nào để kéo con tàu về, cũng không có ai lên thay giúp.",
         "Cách NASA làm: một loại tấm pin **cuộn lại được**. Chúng được phóng lên ở dạng cuộn tròn, rồi phi hành gia **ra ngoài tàu** mở khoá và lắp vào đúng chỗ trên khung giàn — có lần trên khung bên phải, có lần trên khung bên trái, mỗi lần một kênh điện khác nhau.",
         "Và điểm quan trọng nhất nằm ở một chữ: những tấm pin cuộn ấy **THÊM VÀO** tám tấm pin chính, chứ không thay thế chúng. Chúng sinh ra **hơn 20 kilowatt điện** và giúp trạm tăng **30% sản lượng điện** so với bộ pin đang có."],
    en: ["The International Space Station runs on solar power. It has **eight main solar arrays**, and they have been up there a very long time.",
         "On Earth, when panels get old you take them out and put new ones in. In orbit there is no workshop to tow the station back to, and nobody comes up to swap them for you.",
         "NASA's answer: a kind of solar array that **rolls up**. They launch stowed as a roll, then astronauts go **outside the station** to release them and install them on the truss structure — once on the starboard side, once on the port side, each on a different power channel.",
         "And the most important part sits in a single word: those roll-out arrays **AUGMENT** the eight main arrays rather than replacing them. They produce **more than 20 kilowatts of electricity** and enable a **30% increase in power production** over the station's current arrays."]
  },
  more: {
    vi: ["Vì sao lại **thêm vào** chứ không **thay thế**? Nghĩ kỹ thì đó là một lựa chọn kỹ thuật rất đắt giá.",
         "Muốn thay thì phải **tháo cái cũ ra trước**. Mà tháo xong là trong khoảng thời gian đó trạm chạy bằng ít điện hơn — trên một con tàu mà máy lọc nước, máy lọc không khí và máy sinh oxy đều cần điện, một quãng thiếu điện không phải chuyện đùa. Thêm vào thì **không có khoảnh khắc nào yếu đi cả**: tấm cũ vẫn chạy trong suốt lúc lắp tấm mới.",
         "Cái giá phải trả là tấm mới **không được che mất tấm cũ**. Đây là lý do chúng nhỏ hơn và nằm chồng lên một phần: chúng phải chừa lại nắng cho những tấm mà chúng đang tới giúp.",
         "Chỗ này nói lên một điều chung về việc sửa chữa những cỗ máy không dừng lại được. Bạn không có nút tắt, không có \"để mai làm lại\". Nên câu hỏi của kỹ sư không phải *\"cách nào tốt nhất\"* mà là *\"cách nào không bao giờ để hệ thống rơi xuống dưới mức sống được\"* — dù cách đó cồng kềnh hơn.",
         "Điều đó cũng đúng với cỗ máy giữ mạng sống ở bài bên cạnh: cả hai đều là kỹ thuật của những nơi **không có đường lui**.",
         "⚠️ Lập luận về việc không được để trạm yếu điện, và chuyện tấm mới phải chừa nắng cho tấm cũ, là cách astroQ giải thích; trang NASA nêu rằng tấm pin mới THÊM VÀO bộ cũ chứ không nói theo lối này."],
    en: ["Why **augment** instead of **replace**? Think it through and it turns out to be an expensive engineering choice, made on purpose.",
         "To replace, you must **take the old one off first**. And for as long as that lasts, the station runs on less power — on a craft where the water processor, the air system and the oxygen generator all need electricity, a stretch of low power is not a small thing. Adding instead means **there is never a weaker moment**: the old arrays keep working the whole time the new ones go in.",
         "The price is that the new arrays **must not shade the old ones**. That is why they are smaller and only partly overlap: they have to leave sunlight for the very panels they came to help.",
         "There is a general lesson here about repairing machines that cannot stop. You have no off switch and no \"let's try again tomorrow\". So the engineer's question is not *\"which way is best\"* but *\"which way never lets the system drop below survivable\"* — even when that way is clumsier.",
         "The same is true of the life-support machine in the article next door: both are engineering for places with **no way back**.",
         "⚠️ The reasoning about never letting the station lose power, and about leaving sunlight for the old arrays, is astroQ's explanation; the NASA page states that the new arrays augment the existing ones without putting it this way."]
  },
  term: { who: "byte",
          word: { vi: "Kilowatt",
                  en: "Kilowatt" },
          text: { vi: "đơn vị đo công suất điện — tức là *bao nhiêu điện mỗi giây*, chứ không phải tổng cộng bao nhiêu. Hơn 20 kilowatt nghĩa là dòng điện đó chảy liên tục chừng nào còn nắng. 🤖",
                  en: "A unit of electrical power — *how much electricity per second*, not how much in total. More than 20 kilowatts means that flow keeps going for as long as the sunlight lasts. 🤖" } },
  /* Noi voi kho cau hoi: bai day dung diem quan trong nhat cua no: tam pin cuon THEM VAO tam tam chinh chu khong thay the chung. */
  terms: ["rollout-arrays-augment"]
};
