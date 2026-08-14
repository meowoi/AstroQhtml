/* MOT BAI DOC. Khoa bai = TEN FILE.

   NGUON: https://science.nasa.gov/resource/autonomous-hazard-checks-leave-patterned-rover-tracks-on-mars-stereo/
          (kiem 200 ngay 14/08/2026)
   Trich nguyen van:
     · "In autonav mode, the rover pauses periodically during a drive, uses its
        stereo navigation camera to view the route in the intended drive
        direction, analyzes the images for potential hazards in the route, and
        makes a decision about that analysis."
     · "the backward autonav technique includes turning the rover 17.5 degrees
        away from the drive direction just before taking the navigation camera
        images."
     · "This little maneuver -- repeated every 1.2 meters -- is what created the
        dance-step pattern in the foreground portion of the rover tracks in this
        image."

   ⚠️⚠️ RANH GIOI PHAI GIU: trang NASA mo ta MOT THAO TAC DUOC LAP LAI va cai
      hoa van no de lai. Trang **KHONG** dung chu "vong lap", khong noi gi ve cau
      truc lap trinh. Nen THAN BAI chi ke dung thu NASA quan sat duoc; phan
      `more` moi giai thich khai niem VONG LAP, va no phai doc ra la loi giai
      thich cua astroQ chu khong phai loi cua NASA. Dat mot thuat ngu lap trinh
      vao mieng NASA la dung lop loi da mac ba lan (Nam Cuc "chau luc cao nhat" ·
      ba tieu chi IAU · CHNOPS).

   ⚠️ BAI NAY GO MOT MON NO DA GHI TU 25/07/2026: khoa quiz `loop` khai trong
      bank ma **khong bai doc nao day vong lap**, nen no chua bao gio duoc rut ra
      hoi mot cach tu te. Cau hoi do la: "Byte can nhat 3 tinh the giong nhau.
      Nen dung cau truc nao?" — nen phan `more` PHAI day dung y do (lam di lam
      lai cung mot viec), khong duoc chi noi chung chung ve su lap lai. */
export default {
  ord: 4006,
  id: "art-loop-you-can-see-on-mars",
  src: "NASA",
  cat: "it",
  em: "🔁",
  c: ["#ffd08a", "#d1762f", "#3a1c0c"],
  img: null,
  credit: null,
  url: "https://science.nasa.gov/resource/autonomous-hazard-checks-leave-patterned-rover-tracks-on-mars-stereo/",
  title: { vi: "Vết bánh xe trên Sao Hoả có hoa văn, và đó là dấu của một vòng lặp",
          en: "The rover's tracks on Mars have a pattern — and it is the mark of a loop" },
  body: {
    vi: ["Có một bức ảnh chụp vết bánh xe của rover trên Sao Hoả, và vết đó không thẳng đều. Nó có hoa văn lặp đi lặp lại, đều đặn như dấu chân của một điệu nhảy.",
         "Hoa văn đó không phải trang trí. Nó là dấu vết của việc rover tự lái. Ở chế độ tự dẫn đường, rover dừng lại theo chu kỳ trong lúc đi: nó dùng camera dẫn đường để nhìn con đường phía trước, phân tích ảnh xem có chướng ngại không, rồi ra quyết định dựa trên phân tích đó.",
         "Kiểu lái lùi còn thêm một bước nữa: xoay rover đi 17,5 độ khỏi hướng đang chạy, ngay trước khi chụp ảnh. Chính thao tác nhỏ ấy — lặp lại sau mỗi 1,2 mét — đã tạo ra hoa văn trên vết bánh xe.",
         "Nói cách khác: mỗi 1,2 mét, con robot làm lại đúng một chuỗi việc giống hệt nhau. Và vì nó làm trên đất, ta nhìn thấy được từng lượt lặp."],
    en: ["There is a photo of the rover's tracks on Mars, and the tracks are not evenly straight. They carry a repeating pattern, as regular as the footprints of a dance.",
         "That pattern is not decoration. It is the trace of the rover driving itself. In autonav mode the rover pauses periodically during a drive: it uses its stereo navigation camera to view the route ahead, analyzes the images for possible hazards, and makes a decision based on that analysis.",
         "The backward-driving technique adds one more step: turning the rover 17.5 degrees away from the drive direction, just before taking the camera images. That little manoeuvre — repeated every 1.2 metres — is what created the dance-step pattern in the tracks.",
         "Put another way: every 1.2 metres, the robot redoes exactly the same sequence of jobs. And because it does it in the dirt, we get to see each turn of the repetition."]
  },
  more: {
    vi: ["Trong lập trình, chuỗi việc làm-đi-làm-lại như thế có một cái tên: VÒNG LẶP. Bạn không viết cùng một lệnh hàng nghìn lần cho một chuyến đi dài hàng nghìn mét — bạn viết nó MỘT lần, rồi bảo máy lặp lại.",
         "Thử nghĩ về một việc nhỏ hơn: Byte cần nhặt 3 tinh thể giống nhau. Bạn có thể viết ba lệnh \"nhặt tinh thể\" nối nhau, và nó chạy đúng. Nhưng nếu đổi thành 30 tinh thể thì bạn phải gõ lại 30 lần; đổi thành 300 thì hết cách. Một vòng lặp thì chỉ cần đổi đúng một con số.",
         "Đó là chỗ vòng lặp thật sự đáng giá: nó tách phần VIỆC ra khỏi phần SỐ LẦN. Việc chỉ mô tả một lần, còn số lần thì đổi tuỳ hoàn cảnh — và người viết chương trình không phải viết lại gì cả.",
         "⚠️ Một chỗ đáng nói cho rõ: trang của NASA mô tả cái thao tác được lặp lại và cái hoa văn nó để lại; chữ \"vòng lặp\" là cách astroQ gọi tên khái niệm đó cho bạn dễ hình dung, không phải chữ NASA dùng trong trang ấy."],
    en: ["In programming, a sequence of work done over and over like that has a name: a LOOP. You do not write the same command a thousand times for a drive that is a thousand metres long — you write it ONCE and tell the machine to repeat it.",
         "Think about something smaller: Byte needs to pick up 3 identical crystals. You could write three \"pick up crystal\" commands in a row, and it would work. But change it to 30 crystals and you have to type it 30 times; change it to 300 and you are stuck. With a loop you only change one number.",
         "That is where a loop really earns its keep: it separates the WORK from the NUMBER OF TIMES. The work is described once, while the count changes with the situation — and the person writing the program rewrites nothing.",
         "⚠️ One thing worth stating clearly: the NASA page describes the repeated manoeuvre and the pattern it leaves; the word \"loop\" is how astroQ names that idea for you, not a word NASA uses on that page."]
  },
  terms: ["loop"],
  term: { who: "byte",
          word: { vi: "Vòng lặp",
                  en: "Loop" },
          text: { vi: "cấu trúc bảo máy làm lại cùng một việc nhiều lần. Viết một lần, chạy bao nhiêu lần cũng được — đổi số lần thì sửa đúng một con số. 🤖",
                  en: "The structure that tells a machine to redo the same work many times. Write it once, run it any number of times — change the count and you edit exactly one number. 🤖" } }
};
