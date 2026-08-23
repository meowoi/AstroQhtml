/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "moxie-oxygen-from-mars-air",
  topic: { vi: "ROBOT TRÊN SAO HOẢ",
           en: "ROVERS ON MARS" },
  q: { vi: "Thiết bị MOXIE lấy nguyên liệu ở đâu để tạo ra oxy trên Sao Hoả?",
       en: "Where does the MOXIE device get the raw material to make oxygen on Mars?" },
  opts: [
    { vi: "Từ các bình khí chở sẵn từ Trái Đất",
        en: "From gas tanks carried all the way from Earth" },
    { vi: "Từ khí cacbonic có trong bầu khí quyển Sao Hoả",
        en: "From carbon dioxide in the Martian atmosphere" },
    { vi: "Từ ánh sáng Mặt Trời",
        en: "From sunlight" },
    { vi: "Từ chính pin của con robot",
        en: "From the rover's own battery" }
  ],
  a: 1,
  ok: { vi: "Đúng rồi! NASA ghi MOXIE tạo oxy <b>từ khí cacbonic trong bầu khí quyển Sao Hoả</b> — thứ có sẵn ngay tại đó, để người sau này có cái mà thở và làm nhiên liệu tên lửa.",
        en: "Right! NASA says MOXIE produces oxygen <b>from carbon dioxide in the Martian atmosphere</b> - something already there, so future explorers can fill their lungs and fuel rockets." },
  no: { vi: "Chưa đúng! Nếu phải chở bình khí từ Trái Đất thì đã chẳng cần MOXIE. Nó lấy <b>khí cacbonic trong bầu khí quyển Sao Hoả</b> rồi tách oxy ra.",
        en: "Not quite! If you had to ship tanks from Earth you would not need MOXIE at all. It takes <b>carbon dioxide from the Martian atmosphere</b> and splits the oxygen out." },
  hint: { vi: "Cả cái hay của MOXIE là nó dùng thứ có sẵn tại chỗ. Bầu khí quyển Sao Hoả chủ yếu là khí gì?",
          en: "The whole point of MOXIE is using what is already there. What gas makes up most of the Martian atmosphere?" },
  /* lv2, khong phai lv3: thang chot 19/08 dat lv3 cho cau GIAI THICH MOT CO CHE.
     Cau nay hoi NGUYEN LIEU DAU VAO lay o dau — tra loi bang cach nho dung mot
     chat lieu, tuc lv2. So voi `oxygen-from-electrolysis` (lv3): cau do hoi oxy
     duoc LAM RA bang cach nao (dien phan nuoc) — do moi la co che. */
  lv: 2,
  src: "perseverance",
  srcQuote: "MOXIE device successfully produces oxygen from carbon dioxide in the Martian atmosphere - technology for future explorers to fill lungs and fuel rockets.",
  srcChecked: "2026-08-22"
};
