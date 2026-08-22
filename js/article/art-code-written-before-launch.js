/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://www.jpl.nasa.gov/edu/resources/project/code-a-mars-landing/
   Trich nguyen van:
     · "Because of the enormous distance between Earth and Mars, we can't control
        the spacecraft in real-time like one would in a video game."
     · "It takes a signal around seven minutes to be sent from Earth to Mars and
        another seven minutes to come back"
     · "Entry, descent, and landing, or EDL, is the series of events that occurs
        from the time a spacecraft encounters the top of the Martian atmosphere
        until it safely touches down on the surface."
     · "hundreds of thousands of lines of code, providing instructions for each of
        the maneuvers it will need to perform to land safely"

   ⚠️ TRANG NAY **KHONG** NOI GI VE VONG LAP hay cau truc dieu kien — da hoi thang
      va nhan duoc cau tra loi ro rang. Bai ve vong lap la mot bai RIENG voi mot
      nguon RIENG (`art-loop-you-can-see-on-mars`). Dung gop hai bai lam mot roi
      dan chung mot URL.

   ⚠️⚠️ URL NAY TRA 403 VOI curl TRAN VA VOI CHROMIUM HEADLESS, nhung 200 voi
      curl kem User-Agent that (do 14/08/2026). Do la bo loc bot cua CloudFront
      truoc jpl.nasa.gov, KHONG PHAI trang chet — tre bam vao bang trinh duyet
      that thi mo duoc binh thuong. Ghi lai o day de lan sau ai do chay mot bo
      kiem URL tu dong thi khong bao "nguon chet" oan roi di thay mot nguon tot. */
export default {
  ord: 4002,
  id: "art-code-written-before-launch",
  src: "NASA",
  cat: "it",
  em: "📜",
  c: ["#8ee0ff", "#3f7fd6", "#0d1f4a"],
  img: null,
  credit: null,
  url: "https://www.jpl.nasa.gov/edu/resources/project/code-a-mars-landing/",
  title: { vi: "Không ai cầm tay lái khi tàu hạ cánh xuống Sao Hoả",
          en: "Nobody is at the wheel when a spacecraft lands on Mars" },
  body: {
    vi: ["Hạ cánh xuống Sao Hoả là chuỗi việc từ lúc tàu chạm mép khí quyển cho tới lúc nó đặt xuống mặt đất an toàn — NASA gọi tắt là EDL. Cả chuỗi đó chỉ kéo dài vài phút.",
         "Vấn đề là khoảng cách. Một tín hiệu đi từ Trái Đất tới Sao Hoả mất khoảng bảy phút, rồi bảy phút nữa để quay về. Nên như NASA nói thẳng: không thể điều khiển con tàu theo thời gian thực như khi chơi điện tử.",
         "Bảy phút là quá muộn cho một cú hạ cánh chỉ kéo dài vài phút. Lệnh của bạn sẽ tới nơi khi mọi chuyện đã xong xuôi — theo hướng này hay hướng kia.",
         "Vậy nên con tàu phải tự làm, dựa vào thứ đã được nạp sẵn vào máy tính của nó: hàng trăm nghìn dòng lệnh, mô tả từng thao tác nó cần thực hiện để hạ cánh an toàn. Lập trình, ở đây, nghĩa là viết trước mọi câu trả lời cho những câu hỏi chưa xảy ra."],
    en: ["Landing on Mars is the series of events from the moment a spacecraft meets the top of the atmosphere until it safely touches down — NASA calls it EDL for short. The whole thing lasts only a few minutes.",
         "The problem is distance. A signal takes around seven minutes to travel from Earth to Mars, and another seven minutes to come back. So, as NASA puts it plainly: we can't control the spacecraft in real time the way you would in a video game.",
         "Seven minutes is far too late for a landing that lasts a few minutes. Your command would arrive after everything is already over — one way or the other.",
         "So the spacecraft has to do it itself, using what was loaded into its computer beforehand: hundreds of thousands of lines of code, giving instructions for each manoeuvre it needs to land safely. Programming, here, means writing every answer in advance for questions that have not happened yet."]
  },
  more: {
    vi: ["Điều đó đổi hẳn nghĩa của việc lập trình. Khi bạn viết một chương trình trên máy tính ở nhà, chạy sai thì sửa rồi chạy lại — vòng đó mất vài giây. Với một cú hạ cánh trên Sao Hoả thì không có lần chạy lại nào cả.",
         "Nên phần lớn công việc không nằm ở lúc gõ lệnh, mà ở lúc NGHĨ RA hết những chuyện có thể xảy ra: nếu gió mạnh hơn dự tính thì sao, nếu một cảm biến trả về con số vô lý thì sao, nếu mặt đất tới sớm hơn tính toán thì sao. Mỗi câu \"nếu\" như vậy phải có một câu trả lời nằm sẵn trong mã.",
         "Đó cũng là lý do một chương trình cho tàu vũ trụ dài tới hàng trăm nghìn dòng, trong khi việc nó làm — hạ cánh — nghe chỉ như một động tác. Phần lớn số dòng đó không dành cho trường hợp mọi thứ suôn sẻ. Chúng dành cho những trường hợp còn lại."],
    en: ["That changes what programming even means. When you write a program on a computer at home and it goes wrong, you fix it and run it again — that loop takes seconds. For a landing on Mars there is no second run.",
         "So most of the work is not in typing the commands, but in THINKING UP everything that could happen: what if the wind is stronger than predicted, what if a sensor returns a nonsense number, what if the ground arrives sooner than calculated. Every one of those \"what ifs\" needs an answer already sitting in the code.",
         "That is also why a spacecraft program runs to hundreds of thousands of lines while the thing it does — land — sounds like a single action. Most of those lines are not for the case where everything goes smoothly. They are for all the other cases."]
  },
  term: { who: "byte",
          word: { vi: "Tự chủ",
                  en: "Autonomous" },
          text: { vi: "máy tự quyết định theo chương trình đã nạp, không chờ người ra lệnh. Không phải vì nó thông minh hơn người — mà vì người ở quá xa để kịp trả lời. 🤖",
                  en: "The machine decides for itself from the program already loaded, without waiting for a human. Not because it is smarter than us — but because we are too far away to answer in time. 🤖" } },
  /* Noi voi kho cau hoi: bai day rang tau tu chay theo hang tram nghin dong lenh NAP SAN, mo ta tung buoc theo thu tu — vi bay phut tre tin hieu la qua muon de dieu khien. */
  terms: ["sequence"]
};
