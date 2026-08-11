/* MOT BAI DOC. Khoa bai = TEN FILE. Day la NGUON SU THAT — muc luc
   `js/articles-index.js` sinh ra tu day, va luat noi dung ghi o do. */
export default {
  ord: 3070,
  id: "art-ai-tags-nasa-data",
  src: "NASA",
  cat: "ai",
  em: "🔎",
  c: ["#d4f0e8", "#4aa890", "#123a30"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/science-research/artificial-intelligence-metadata-tagging/",
  title: { vi: "Tìm một tập dữ liệu trong kho của NASA: việc AI đang giúp",
          en: "Finding one dataset in NASA's archive: a job AI now helps with" },
  body: {
    vi: ["Có một vấn đề nghe rất buồn tẻ nhưng lại chặn đứng công việc khoa học thật: dữ liệu có đó mà không ai tìm ra. NASA mô tả tình cảnh ấy bằng một hình ảnh rất dễ hình dung: không có một ngôn ngữ chung để mô tả dữ liệu thì việc tìm ra tập dữ liệu khoa học Trái Đất phù hợp sẽ giống như đi tìm một cái kim trong đống cỏ khô, mà lại bị bịt mắt.",
           "Ngôn ngữ chung ở đây nghĩa là từ khoá. Mỗi tập dữ liệu cần được dán nhãn bằng những từ khoá chuẩn, để người sau gõ đúng từ đó là tìm ra. Vấn đề là việc dán nhãn phải làm bằng tay, cho từng tập dữ liệu một, và số tập dữ liệu thì rất lớn. Đây đúng là loại việc mà con người làm được nhưng làm mãi không hết.",
           "Nên NASA huấn luyện một mô hình AI để đề xuất từ khoá. NASA viết: bằng cách tự động đề xuất những từ khoá chính xác và đã được chuẩn hoá, mô hình giảm bớt gánh nặng cho những người biên mục trong khi vẫn giữ chất lượng dữ liệu mô tả ở mức cao. Hãy chú ý cách nói này — giảm gánh nặng cho người biên mục, không phải thay thế họ.",
           "Và bản mới học được nhiều hơn hẳn bản cũ. NASA cho biết bản mới nay xét tới hơn 3.200 từ khoá, tăng từ khoảng 430 ở bản trước. Bản cũ chỉ được huấn luyện trên 2.000 bản ghi mô tả, còn bản mới có cả một kho phong phú hơn nhiều với hơn 43.000 bản ghi. Đây là một ví dụ rất rõ về nguyên tắc của học máy: cho nó xem càng nhiều ví dụ đúng, nó càng đề xuất giỏi. Dữ liệu không phải thứ phụ — dữ liệu chính là bài học."],
    en: ["Here is a problem that sounds dull but genuinely blocks real science: the data exists, and nobody can find it. NASA describes the situation with a picture that is easy to grasp: without a common language for describing data, finding relevant Earth science datasets would be like trying to locate a needle in a haystack, blindfolded.",
           "A common language here means keywords. Each dataset needs labelling with standard keywords, so that someone later can type those words and find it. The catch is that the labelling has to be done by hand, one dataset at a time, and the number of datasets is enormous. This is exactly the kind of work people can do but can never finish.",
           "So NASA trained an AI model to suggest keywords. NASA writes: by automatically recommending precise, standardized keywords, the model reduces the burden on human curators while ensuring metadata quality remains high. Notice the wording — it reduces the burden on the curators, rather than replacing them.",
           "And the newer version learned far more than the old one. NASA reports that the new version now considers more than 3,200 keywords, up from about 430 in its earlier iteration. The older model was trained on only 2,000 metadata records, while the new one had access to a much richer dataset of more than 43,000 records. This is a very clear illustration of how machine learning works: show it more good examples and it suggests better. The data is not a side detail — the data is the lesson."]
  },
  term: { who: "byte",
           word: { vi: "Dữ liệu mô tả",
                   en: "Metadata" },
           text: { vi: "thông tin nói về dữ liệu — ai đo, đo ở đâu, đo cái gì. Không có nó thì tập dữ liệu vẫn tồn tại mà không ai tìm thấy. 🤖",
                   en: "information about data — who measured it, where, and what. Without it a dataset still exists, but nobody can find it. 🤖" } },
  terms: []
};
