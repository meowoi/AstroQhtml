/* Mot CAU HOI cua Dau Truong Kien Thuc. Khoa cau = TEN FILE.
   Luat + bang nguon S (`src` la KHOA, khong phai URL): js/quiz-index.js */
export default {
  term: "sequence",
  topic: { vi: "THUẬT TOÁN",
           en: "ALGORITHMS" },
  q: { vi: "Để tới đích: tiến 2 ô rồi rẽ phải. Trình tự lệnh đúng là?",
       en: "To reach the goal: go 2 tiles then turn right. Correct order?" },
  opts: [
    { vi: "MoveForward(2) → TurnRight()",
      en: "MoveForward(2) → TurnRight()" },
    { vi: "TurnRight() → MoveForward(2)",
      en: "TurnRight() → MoveForward(2)" },
    { vi: "TurnRight() → TurnLeft()",
      en: "TurnRight() → TurnLeft()" },
    { vi: "Stop() → MoveForward(2)",
      en: "Stop() → MoveForward(2)" }
  ],
  a: 0,
  ok: { vi: "Hoàn hảo! Máy tính chạy lệnh <b>theo thứ tự từ trên xuống</b> — tiến trước, rẽ sau.",
        en: "Perfect! Computers run commands <b>in order, top to bottom</b> — move first, then turn." },
  no: { vi: "Chưa đúng! Đề yêu cầu <b>tiến trước, rẽ phải sau</b> — đúng thứ tự nhé.",
        en: "Not quite! It says <b>move first, then turn right</b> — order matters." },
  hint: { vi: "Thứ tự rất quan trọng: việc nào làm <b>trước</b>?",
          en: "Order matters: which step comes <b>first</b>?" }
};
