# Phân vai ChatGPT / Gemini — AstroQ

> File này dành cho **chủ dự án**, không dán vào model nào.
> Cái dán vào model là `docs/BRIEFING.md` + phần "Đề bài" tương ứng ở cuối file này.

---

## Nguyên tắc tách vai

Không tách theo *"model nào giỏi hơn"* — điều đó không kiểm chứng được và đổi liên tục.
Tách theo **bản chất công việc**, vì đó là thứ ổn định:

| | Lane A — **ChatGPT** | Lane B — **Gemini** |
|---|---|---|
| Vai | **Người sáng tác** | **Người tra nguồn & kiểm chứng** |
| Bản chất việc | Bịa ra cái chưa có | Xác minh cái đã có là đúng |
| Đầu ra đúng khi | Trẻ thấy vui, muốn chơi tiếp | Mọi câu đều dẫn được về nguồn thật |
| Sai kiểu gì | Nhàm, khó hiểu, lạc tuổi | Sai khoa học, nguồn chết, dịch sai |
| Không được làm | Khẳng định số liệu khoa học | Sửa giọng văn dành cho trẻ |

Hai lane **chạy song song, độc lập**, chỉ có **một điểm giao duy nhất**: khi Lane A tạo ra
nội dung có khẳng định khoa học thì đưa sang Lane B kiểm. Một hop, không ping-pong.

*[Suy luận]* Cách chia này cũng khớp với mẫu hình thường thấy — ChatGPT mạnh về viết sáng tạo
và giữ giọng nhân vật, Gemini gắn với hệ tìm kiếm của Google nên thuận cho việc tra và dẫn nguồn.
Nhưng **kể cả nếu điều đó sai**, cách chia vẫn hiệu quả, vì hai vai là hai công việc thật sự
khác nhau chứ không phải hai cách nói về cùng một việc.

> **Cách tự kiểm trong 15 phút:** giao chéo một đề bài nhỏ cho cả hai (ví dụ "viết 5 câu quiz về
> Sao Hoả cho trẻ, có dẫn nguồn NASA"), so kết quả, rồi hoán vai nếu thấy ngược với dự đoán ở đây.
> Đừng tin bảng trên hơn kết quả thật của chính bạn.

---

## Lane A — ChatGPT: sáng tác

**Sở hữu trọn vẹn (không ai khác đụng vào):**

1. **Bộ khuôn tương tác** — 6–8 khuôn dùng lại được để dựng nhiệm vụ bằng dữ liệu.
   Đây là việc chặn đường mọi thứ khác, làm trước.
2. **Cấu trúc quest mỗi World** — bao nhiêu chủ đề, nhịp lên cấp, cách mở khoá.
3. **Lời thoại Comet & Byte** — giọng nhân vật, lời khen, lời an ủi khi trả lời sai.
4. **Chữ hiển thị cho trẻ** — tên nhiệm vụ, mô tả, thông báo, chữ trên nút.
5. **Concept 2 khu chưa có trang** — Phòng Nghiên Cứu (MOD-05) và Thư Viện Thiên Văn (MOD-06)
   hiện là hai ô trống, chưa ai biết chúng nên là gì.
6. **Chống nhàm** — cùng bộ khuôn dùng cho 9 hành tinh thì làm sao hành tinh thứ 5 vẫn thấy mới.

**Cấm:**
- Khẳng định bất kỳ số liệu khoa học nào. Cần số thì viết `[CẦN KIỂM: …]` để Lane B điền.
- Ước lượng công sức thực hiện — không đọc được mã nguồn thì không ước lượng được.
- Soạn câu hỏi quiz (đó là Lane B).

---

## Lane B — Gemini: tra nguồn & kiểm chứng

**Sở hữu trọn vẹn:**

1. **Ngân hàng câu hỏi quiz** — hiện chỉ có 35 câu cho cả app. Mỗi câu cần: câu hỏi, 4 đáp án,
   lời giải thích khi đúng, gợi ý khi sai, **và một URL nguồn NASA/ESA/NOAA còn sống**.
   Đây là nút thắt lớn nhất của dự án.
2. **Kho dữ liệu học `learningdata/`** — hiện gần như trống. Cần nội dung theo từng hành tinh.
3. **Kiểm chứng khoa học** cho mọi thứ Lane A viết ra — điểm giao duy nhất giữa hai lane.
4. **Kiểm URL còn sống thật** (mọi nguồn trong dự án đều đã được kiểm 200 trước khi dùng).
5. **Chất lượng bản tiếng Anh** — dự án song ngữ, bản EN không được là bản dịch máy.
6. **Kiểm độ khó theo lứa tuổi** — câu nào quá khó, thuật ngữ nào chưa giải thích.

**Cấm:**
- Sửa giọng văn dành cho trẻ, đổi lời thoại Comet/Byte — đó là Lane A.
- Thiết kế cơ chế chơi.
- Nói "chỗ này sửa nhẹ thôi".

---

## Vì sao không cho hai bên bàn chung

Hai model đều **không đọc được mã nguồn**, đều có thiên lệch trả lời nghe-cho-hay. Cho bàn chung
một đề thì chúng hội tụ về đồng thuận rỗng, mà bạn tốn gấp đôi thời gian đọc.

Chia thành hai lane thì mỗi vòng bạn nhận **hai kết quả khác nhau, cùng dùng được**, thay vì
hai phiên bản của một câu trả lời.

Khi nào *muốn* cho đối kháng thì làm có chủ đích: đưa đề xuất của Lane A cho Lane B với đề bài
*"tìm lý do cái này hỏng"* — nhưng đó là kiểm chứng, không phải bàn chung.

---

# Đề bài dán thẳng — vòng 1

Cả hai đề bài dưới đây đều phải **dán kèm toàn bộ `docs/BRIEFING.md` phía trước**.

---

## 📋 Dán cho ChatGPT

```
Bạn phụ trách phần SÁNG TÁC của dự án AstroQ. Một model khác (Gemini) phụ trách kiểm chứng
khoa học và tra nguồn — nên bạn KHÔNG cần khẳng định số liệu khoa học nào. Chỗ nào cần một
con số hay một dữ kiện thiên văn, hãy viết [CẦN KIỂM: mô tả điều cần tra] và đi tiếp.

NHIỆM VỤ VÒNG 1 — Bộ khuôn tương tác.

Hiện mỗi bước nhiệm vụ của AstroQ được viết tay riêng, tốn ~410 dòng mã. Không thể nhân
cách đó ra 9 hành tinh. Cần một bộ khuôn dùng lại được, để mỗi nhiệm vụ chỉ còn là một
mẩu dữ liệu JSON.

Hãy đề xuất 6–8 khuôn tương tác. Với MỖI khuôn:
1. Tên khuôn (Việt + Anh)
2. Cách chơi, mô tả trong 3–4 câu, đủ rõ để một lập trình viên hình dung được màn hình
3. Loại kiến thức nó dạy TỐT NHẤT, và loại kiến thức nó dạy DỞ
4. Cấu trúc JSON tối thiểu để tạo một nhiệm vụ bằng khuôn đó (viết ra ví dụ thật)
5. Một ví dụ nhiệm vụ cụ thể dùng khuôn đó, cho bất kỳ hành tinh nào

RÀNG BUỘC:
- Chỉ HTML/CSS/JS thuần, không framework. Khuôn phải chạy được trên điện thoại, chạm bằng ngón tay.
- Phải tôn trọng prefers-reduced-motion.
- 8 bước của nhiệm vụ Trái Đất hiện có (quét điểm nóng · sắp thứ tự mốc thời gian ·
  kéo-thả phân loại · thu thập thẻ · giải đố ghép) PHẢI diễn đạt lại được bằng bộ khuôn của bạn
  — nếu không thì nhiệm vụ đang chạy sẽ phải viết lại từ đầu. Hãy chỉ rõ bước nào ánh xạ vào khuôn nào.

Sau đó trả lời thêm: cùng một bộ khuôn dùng cho 9 hành tinh thì làm cách nào để tới hành tinh
thứ 5 trẻ vẫn thấy mới? Cho 3 cơ chế cụ thể, không nói chung chung.

Trả lời theo khuôn ở docs/proposals/_TEMPLATE.md.
```

---

## 📋 Dán cho Gemini

```
Bạn phụ trách phần NỘI DUNG KHOA HỌC VÀ NGUỒN của dự án AstroQ. Một model khác (ChatGPT)
phụ trách cơ chế chơi và lời thoại nhân vật — nên bạn KHÔNG cần đề xuất cách chơi, và
KHÔNG sửa giọng văn dành cho trẻ.

NHIỆM VỤ VÒNG 1 — Ngân hàng câu hỏi quiz cho Mặt Trăng.

AstroQ hiện chỉ có 35 câu quiz cho toàn bộ ứng dụng. Đây là nút thắt lớn nhất. Nhiệm vụ
"Mặt Trăng" là nhiệm vụ tiếp theo sẽ làm, nên bắt đầu từ đó.

Hãy soạn 25 câu hỏi về Mặt Trăng cho trẻ em, chia 3 mức: dễ (10 câu) · vừa (10) · khó (5).

Với MỖI câu, cho đủ:
- Câu hỏi (tiếng Việt + tiếng Anh)
- 4 đáp án (Việt + Anh), chỉ một đáp án đúng
- Lời giải thích khi trả lời ĐÚNG — 1–2 câu, giải thích VÌ SAO, không chỉ khen (Việt + Anh)
- Gợi ý khi trả lời SAI — dẫn dắt tới đáp án, KHÔNG nói thẳng đáp án (Việt + Anh)
- Một URL nguồn NASA / ESA / NOAA. Hãy TRA THẬT và chỉ đưa URL bạn xác nhận đang sống.
  Không chắc URL còn sống thì ghi rõ "chưa xác minh được" thay vì đoán.

YÊU CẦU CHẤT LƯỢNG:
- Bản tiếng Anh phải là tiếng Anh viết cho trẻ em bản ngữ, không phải bản dịch từ tiếng Việt.
- Thuật ngữ khoa học nào dùng trong câu hỏi thì phải được giải thích ngay trong lời giải thích.
- Đáp án sai phải hợp lý (là hiểu lầm phổ biến), không phải đáp án ngớ ngẩn để loại trừ.
- Tránh câu hỏi mẹo. Mục tiêu là dạy, không phải bẫy.

Trả về dạng bảng hoặc JSON, mỗi câu một khối, để dễ chuyển vào mã nguồn.

Sau đó trả lời thêm: trong 25 câu bạn vừa viết, câu nào bạn KÉM chắc chắn nhất về mặt
khoa học, và vì sao?
```

---

## Quy trình mỗi vòng

Khi có kết quả một vòng:

1. Lưu vào `docs/proposals/YYYY-MM-DD-<tên>.md`, ghi rõ model nào viết
2. Bảo Claude đọc — đối chiếu mã nguồn, ước lượng chi phí, chỉ chỗ giả định sai
3. Chủ dự án chốt → ghi vào `docs/decisions/`
4. Giao vòng tiếp, vẫn giữ đúng hai lane

Điểm giao duy nhất được phép: khi bộ khuôn của ChatGPT có chỗ `[CẦN KIỂM: …]`, gom hết lại
gửi Gemini một lượt. **Một lượt, không hỏi lẻ từng cái** — chi phí thật của mô hình ba model
là thời gian copy-paste của bạn.

---

# Đề bài dán thẳng — vòng 2

Cả hai đều là **làm lại có mục tiêu**, không phải làm mới. Kết quả rà vòng 1 đầy đủ ở
`docs/proposals/2026-07-31-review-vong-1.md`.

Vòng này **không cần dán lại `BRIEFING.md`** nếu bạn tiếp tục trong cùng cuộc trò chuyện cũ.
Mở chat mới thì vẫn phải dán.

---

## 📋 Dán cho ChatGPT — vòng 2

```
Đề xuất 8 khuôn của bạn đã được đối chiếu với mã nguồn thật. Hướng đúng, nhưng có ba
phát hiện làm thay đổi bài toán, và một chỗ phải thu hẹp.

=== ĐÃ KIỂM BẰNG MÃ NGUỒN — dùng thay cho các giả định của bạn ===

1. SỔ ĐĂNG KÝ BƯỚC ĐÃ TỒN TẠI. mission-earth.html đã có sẵn
   `const steps = { scan:{}, timeline:{}, sun:{}, energy:{}, rotation:{}, life:{}, eco:{}, core:{} }`
   chạy bằng mảng STEP_IDS + biến stepIdx. Khung điều phối không phải dựng mới, chỉ phải
   rút ra khỏi file HTML. Bạn KHÔNG cần thiết kế lại trình điều phối.

2. TOẠ ĐỘ ĐÃ ĐỘC LẬP ENGINE. Các điểm trên hành tinh dùng lat/lon địa lý thật, không phải
   pixel. Đã có sẵn cờ SCENE = '2d' | '3d'. Nghĩa là một khuôn dạng quét/chạm-điểm dùng
   được cho cả cảnh 2D lẫn 3D mà không đổi dữ liệu.

3. SERVER KHÔNG KIỂM ĐÁP ÁN. Client chỉ gửi {mission, step, opId}; server tra bảng thưởng
   theo id bước, không hề biết người chơi trả lời đúng hay sai. Vậy nên câu hỏi của bạn về
   successRules đã có trả lời: client VỐN ĐÃ là bên duy nhất quyết định bước nào xong.
   Đưa luật hoàn thành vào JSON không làm yếu thêm gì. Đừng thiết kế cơ chế chống gian lận
   ở client — nó không mua được gì.

4. HAI KHOẢN NỢ, phải tính vào mọi phương án:
   - KHÔNG có component hội thoại Comet/Byte dùng chung. CSS linh vật đang lặp ở 5 file.
   - KHÔNG có lối chơi bằng bàn phím ở bất kỳ đâu. Cả mission-earth.html chỉ có 1 handler
     keydown, và nó dùng để mở khoá âm thanh. Mọi phương án thay cho kéo-thả là việc mới
     hoàn toàn, không có gì để dựa.

5. Trả lời nốt các câu bạn hỏi: 9 World = 8 hành tinh + Mặt Trăng (Mặt Trăng CHƯA có trong
   dữ liệu hành tinh, sẽ phải tách world-id khỏi planet-id) · mỗi bước chỉ tính thưởng một
   lần, chống gửi trùng bằng opId · nhiệm vụ KHÔNG trừ Thiên thạch tím · song ngữ là {vi, en}
   lồng trong từng trường · nội dung nhiệm vụ phát hành dạng file tĩnh là đủ, không cần
   endpoint mới · trộn thứ tự thẻ ở client là được.

=== VIỆC CẦN LÀM ===

A. THU XUỐNG CÒN 4 KHUÔN.
   Bạn ước 36 bước cho 9 điểm đến. 36 chia 8 khuôn = 4,5 bước mỗi khuôn — dựng 8 cỗ máy để
   chạy 36 lượt là lỗ. Hãy chọn đúng 4 khuôn có độ phủ cao nhất và giải thích vì sao chọn
   4 cái đó.
   Ba khuôn sau ĐỂ LẠI ĐỢT SAU, không cần bàn thêm: branching_field_log (tốn lời thoại
   gấp bội), mission_resource_balance (successRules thành bộ máy luật thu nhỏ mà không mua
   được gì, xem điểm 3), relationship_map (nối dây là dạng khó làm bàn phím nhất, mà ta
   không có hạ tầng nào — xem điểm 4).

B. VỚI MỖI KHUÔN TRONG 4 KHUÔN, mô tả LỐI CHƠI BẰNG BÀN PHÍM tương đương.
   Không phải "thêm aria-label", mà là: nhấn phím nào, thứ tự focus ra sao, người chơi biết
   mình đang chọn gì bằng cách nào, xác nhận bằng phím gì. Đây là phần mới hoàn toàn nên
   phải cụ thể.

C. ÁNH XẠ ĐỦ 8 BƯỚC TRÁI ĐẤT vào 4 khuôn đó:
   scan · timeline · sun · energy · rotation · life · eco · core
   Bước nào không ánh xạ được thì NÓI THẲNG là không, đừng cố nhét. Nhiệm vụ Trái Đất SẼ
   được chuyển sang bộ khuôn mới — đó chính là phép thử xem bộ khuôn có đủ dùng hay không,
   nên đừng đề xuất giữ nguyên nó.

D. Với 4 khuôn đã chọn, ước lượng lại mục 7 (cần bao nhiêu nội dung mới) cho ĐÚNG MỘT World
   là Mặt Trăng, không phải cho cả 9. Ta cần một con số đo được trước khi nhân lên.

Vẫn theo khuôn ở docs/proposals/_TEMPLATE.md. Vẫn KHÔNG khẳng định dữ kiện khoa học nào —
dùng [CẦN KIỂM: …].
```

---

## 📋 Dán cho Gemini — vòng 2

```
Bộ 25 câu quiz Mặt Trăng của bạn đã được đối chiếu. Nội dung khoa học ĐÚNG cả 18 câu đọc
được, giải thích tốt, tiếng Anh tự nhiên. Nhưng có ba lỗi phải sửa trước khi dùng được,
và một lỗi trong số đó nằm đúng phần bạn được giao.

=== LỖI 1 — NGUỒN THAM CHIẾU: 11/12 URL kiểm được đều hỏng ===

Đã curl từng URL. Kết quả:
- 9 URL trỏ moon.nasa.gov: TOÀN BỘ tên miền này đã bị NASA gộp. Mọi đường dẫn cụ thể đều
  301 về một trang chung science.nasa.gov/moon/ — tức là nguồn KHÔNG CÒN trỏ tới dữ kiện
  mà nó chống lưng.
- science.nasa.gov/eclipses/lunar-eclipses/ → 404
- www.nasa.gov/topics/moon-to-mars/water-on-the-moon → 404
- scijinks.gov/tides/ → không kết nối được

Bạn viết "tất cả đường dẫn đều dẫn tới domain chính thức của NASA". Đúng, nhưng đó không
phải điều được yêu cầu — yêu cầu là URL đã tra và xác nhận CÒN SỐNG, tới đúng trang chứa
dữ kiện.

Chín URL sau đã được kiểm trả 200, dùng được:
  https://science.nasa.gov/moon/facts/
  https://science.nasa.gov/moon/moon-phases/
  https://science.nasa.gov/moon/tidal-locking/
  https://science.nasa.gov/moon/formation/
  https://science.nasa.gov/moon/top-moon-questions/
  https://science.nasa.gov/eclipses/
  https://www.nasa.gov/humans-in-space/artemis/
  https://www.nasa.gov/specials/apollo50th/missions.html
  https://oceanservice.noaa.gov/facts/moon-tide.html   (thuỷ triều — NOAA)

YÊU CẦU: mỗi câu phải ghi kèm MÃ HTTP bạn nhận được khi tra URL đó. Không tra được thì
ghi "chưa xác minh được" và dùng một trong chín URL trên.

=== LỖI 2 — ĐÁP ÁN ĐÚNG DỒN HẾT VÀO B ===

Đếm 18 câu đọc được:  A = 1 câu · B = 15 câu · C = 2 câu · D = 0 câu.

83% đáp án đúng nằm ở vị trí B, không câu nào ở D. Dự án có luật rải đều A/B/C/D, ghi ngay
đầu file ngân hàng câu hỏi, kèm lý do: trẻ học "cứ chọn B" thì bài kiểm tra mất tác dụng.
Bộ câu hỏi hiện có rải 8/6/6/5.

YÊU CẦU: rải lại cho gần đều (khoảng 6/6/6/7 trên 25 câu), và ghi KÈM BẢNG PHÂN BỐ A/B/C/D
ở cuối để tự kiểm.

=== LỖI 3 — SAI SCHEMA ===

Dùng ĐÚNG cấu trúc dưới đây. Đây là một câu thật đang chạy trong dự án, chép nguyên dạng:

    {
      term: "planet",
      topic: { vi: "HÀNH TINH", en: "PLANET" },
      q: { vi: "...", en: "..." },
      opts: [
        { vi: "...", en: "..." },
        { vi: "...", en: "..." },
        { vi: "...", en: "..." },
        { vi: "...", en: "..." }
      ],
      a: 0,
      ok:   { vi: "Chuẩn! ...", en: "Exactly! ..." },
      no:   { vi: "Chưa đúng! ...", en: "Not quite! ..." },
      hint: { vi: "...", en: "..." },
      src:  { name: "NASA Science — ...", url: "https://..." }
    }

Bốn điểm khác với bản bạn gửi:
- `a` là MỘT chỉ số duy nhất (0..3), nằm NGOÀI vi/en. Bản của bạn lặp `correct` trong cả hai
  ngôn ngữ — sửa một bên quên bên kia thì bản tiếng Anh chấm sai mà không ai phát hiện.
- `term` là khoá bắt buộc, dùng để mỗi lượt chơi không hỏi trùng thuật ngữ. Bản của bạn thiếu.
  Mỗi câu một `term` riêng, đặt theo khái niệm (ví dụ "moon-gravity", "moon-maria").
- `no` là lời nói khi trả lời SAI — bản của bạn thiếu hẳn. Nó phải giải thích vì sao lựa chọn
  đó chưa đúng, rồi dẫn tới đáp án; không phải chỉ nói "sai rồi".
- `topic` phải song ngữ (nó hiện trên badge cho trẻ đọc), không phải chuỗi tiếng Anh.
  `src` cần cả `name` hiển thị lẫn `url`.
Cho phép dùng thẻ <b> trong ok/no/hint để nhấn mạnh, như ví dụ trên.

=== VIỆC CẦN LÀM ===

Gửi lại ĐỦ 25 CÂU (lần trước bản dán bị cắt ở câu 18), theo đúng schema trên, nguồn đã sửa,
đáp án đã rải lại, kèm bảng phân bố A/B/C/D.

Hai điều nhỏ: bỏ đánh số lệch ở id (lần trước có "quiz_moon_0010" thừa một số 0), và ĐỪNG
tự giả định độ tuổi — tài liệu dự án chưa chốt, đề bài đã dặn điều này. Câu nêu -246°C ở hố
cực cần một nguồn riêng, con số đó không nằm trong trang facts chung.

Cuối cùng, như lần trước: trong 25 câu, câu nào bạn kém chắc chắn nhất về khoa học, vì sao?
```
