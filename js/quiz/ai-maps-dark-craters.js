/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "ai-maps-dark-craters",
  topic: { vi: "AI VÀ HỐ TỐI MẶT TRĂNG",
           en: "AI AND THE MOON'S DARK CRATERS" },
  q: { vi: "Với các nhiệm vụ tới Mặt Trăng, NASA nói AI dùng ảnh vệ tinh để làm gì?",
       en: "For missions to the Moon, what does NASA say AI uses satellite imagery to do?" },
  opts: [
    { vi: "Chiếu sáng vào đáy những hố tối",
      en: "Shine light into the bottom of dark craters" },
    { vi: "Đếm số hố trên toàn bộ bề mặt",
      en: "Count every crater on the whole surface" },
    { vi: "Chọn ngày phóng có thời tiết tốt nhất",
      en: "Pick the launch day with the best weather" },
    { vi: "Dựng bản đồ ba chiều chi tiết của những hố tối",
      en: "Create detailed 3D maps of dark craters" }
  ],
  a: 3,
  ok: { vi: "Đúng! NASA viết: <b>AI có thể dùng ảnh vệ tinh để dựng những bản đồ 3D chi tiết của các hố tối</b>. Máy lấy những mảnh thông tin mờ nhạt trong <b>rất nhiều tấm ảnh</b> rồi ghép lại thành hình khối — thứ mắt người nhìn từng tấm một thì không dựng ra được.",
       en: "Yes! NASA writes: <b>AI can use satellite imagery to create detailed 3D maps of dark craters</b>. The machine takes faint scraps of information from <b>many images</b> and builds them into shape — something a person looking at one image at a time cannot do." },
  no: { vi: "Chưa đúng! AI <b>không chiếu sáng gì cả</b> — nó ghép thông tin từ nhiều tấm ảnh thành <b>bản đồ ba chiều</b> của những cái hố mà ánh sáng Mặt Trời chưa bao giờ chiếu tới đáy.",
       en: "Not quite! AI <b>does not light anything up</b> — it stitches information from many images into a <b>three-dimensional map</b> of craters whose floors sunlight has never reached." },
  hint: { vi: "Muốn đưa tàu xuống đó thì cần biết bên trong nó có hình khối thế nào.",
         en: "To land there you need to know the shape of what is inside." },
  lv: 2,
  src: "nasaWhatIsAi",
  srcQuote: "For missions to the Moon, AI can use satellite imagery to create detailed 3D maps of dark craters.",
  srcChecked: "2026-08-23"
};
