/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3080,
  id: "art-ai-predicts-solar-flares",
  src: "NASA",
  cat: "ai",
  em: "🌞",
  c: ["#fff0c8", "#e8a030", "#4a2a08"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/science-research/artificial-intelligence-model-heliophysics/",
  title: { vi: "AI học chín năm nhìn Mặt Trời để đoán trước cơn bão",
          en: "AI that watched the Sun for nine years to see storms coming" },
  body: {
    vi: ["Mặt Trời không hề yên tĩnh. Nó phun ra những đợt bùng sáng và những khối vật chất khổng lồ, và những thứ đó tới được Trái Đất. NASA nói rõ chúng gây ra chuyện gì: bão Mặt Trời gây rủi ro đáng kể cho một xã hội phụ thuộc vào công nghệ. Những sự kiện Mặt Trời mạnh làm tầng điện li của Trái Đất bị nạp năng lượng, dẫn tới sai số GPS lớn hoặc mất hoàn toàn tín hiệu liên lạc vệ tinh.",
           "Chưa hết. NASA viết tiếp rằng chúng cũng gây rủi ro cho lưới điện, vì những dòng điện cảm ứng do từ trường sinh ra từ các vụ phun trào vành nhật hoa có thể làm quá tải máy biến áp và gây mất điện trên diện rộng. Nghĩa là một chuyện xảy ra trên Mặt Trời có thể làm tắt đèn ở nhà bạn — và đó là lý do người ta rất muốn biết trước.",
           "Nên NASA làm một mô hình AI tên là Surya. NASA mô tả đó là một mô hình trí tuệ nhân tạo được huấn luyện trên 9 năm quan sát từ Đài quan sát Động lực học Mặt Trời của NASA. Chín năm ảnh Mặt Trời, chụp liên tục — nhiều hơn hẳn số ảnh một người có thể xem hết trong cả đời làm việc. Đó chính là loại nguyên liệu mà học máy cần.",
           "Nó làm được gì? NASA cho biết Surya có thể tạo ra những dự đoán dạng hình ảnh về các đợt bùng sáng Mặt Trời trước hai giờ. Hai giờ nghe ngắn, nhưng hãy nghĩ theo cách này: hai giờ là khoảng thời gian đủ để người vận hành vệ tinh và người vận hành lưới điện làm một việc gì đó, thay vì chỉ biết chuyện sau khi nó đã xảy ra. Rất nhiều giá trị của việc dự báo không nằm ở chỗ đoán được xa, mà ở chỗ đoán kịp."],
    en: ["The Sun is not quiet. It throws out flares and huge blobs of material, and those things reach Earth. NASA is explicit about what they do: solar storms pose significant risks to our technology-dependent society. Powerful solar events energize Earth's ionosphere, resulting in substantial GPS errors or complete signal loss to satellite communications.",
           "There is more. NASA goes on to say they also pose risks to power grids, as geomagnetically induced currents from coronal mass ejections can overload transformers and trigger widespread outages. So something happening on the Sun can switch off the lights in your house — which is exactly why people would very much like some warning.",
           "So NASA built an AI model called Surya. NASA describes it as an artificial intelligence model trained on 9 years of observations from NASA's Solar Dynamics Observatory. Nine years of images of the Sun, taken continuously — far more pictures than one person could look through in an entire working life. That is precisely the kind of raw material machine learning needs.",
           "What can it do? NASA says Surya can generate visual predictions of solar flares two hours into the future. Two hours sounds short, but think of it this way: two hours is long enough for satellite operators and grid operators to actually do something, rather than only finding out afterwards. Much of the value of a forecast lies not in seeing far ahead, but in seeing in time."]
  },
  term: { who: "byte",
           word: { vi: "Thời tiết không gian",
                   en: "Space weather" },
           text: { vi: "những gì Mặt Trời gửi tới Trái Đất — bùng sáng, hạt tích điện, từ trường. Nó không làm mưa, nhưng làm hỏng vệ tinh và lưới điện. 🤖",
                   en: "what the Sun sends our way — flares, charged particles, magnetic fields. It brings no rain, but it can knock out satellites and power grids. 🤖" } },
  terms: ["ai-surya-two-hours"]
};
