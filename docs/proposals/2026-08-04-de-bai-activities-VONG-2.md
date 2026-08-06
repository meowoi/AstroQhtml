# Đề bài VÒNG 2 gửi ChatGPT — hệ thống Activities

**Ngày:** 2026-08-04 · **Người soạn:** Claude (sau khi đối chiếu vòng 1 với mã nguồn)
**Vòng 1:** `2026-08-03` — bản rà đầy đủ ở `2026-08-04-review-activities-tong-quat.md`

> **Cách dùng:** dán TOÀN BỘ phần trong khung dưới đây vào ChatGPT. Bản này **tự đứng được**,
> không cần dán lại `docs/BRIEFING.md` hay đề xuất vòng 1.
>
> Khác vòng 1 ở bốn chỗ: ① mọi giả định sai được **thay bằng số đo**, không tranh luận ·
> ② ngân sách khuôn và ngân sách nội dung ghi thành **bảng có số chỗ trống** · ③ hai lối thoát
> sai đã đặt tên sẵn · ④ **"giữ nguyên ở tầm toàn app" là câu trả lời hợp lệ** cho việc A.

---

```
Đây là VÒNG 2. Đề xuất Activities của bạn đã được đối chiếu với mã nguồn thật.

Hướng ĐÚNG — dự án đã chốt đúng nguyên tắc đó từ 31/07 (bộ khuôn dùng chung, nhiệm vụ
chỉ còn là dữ liệu). Bản của bạn bị chặn ở hai chỗ đếm được: ba giả định nền không đúng
với mã đang chạy, và ngân sách nội dung vượt xa thứ dự án sản xuất được.

Bản này nói thẳng các con số ra để bạn thiết kế trong khuôn đó ngay từ đầu.

Hãy trả lời theo đúng khuôn ở cuối. Mục nào không đủ thông tin để điền thì ghi
"không đủ thông tin" thay vì đoán — phần này sẽ được đối chiếu với mã nguồn.

════════════════════════════════════════════════════════════════════════
PHẦN 1 — ĐÃ KIỂM BẰNG MÃ NGUỒN. DÙNG THAY CHO CÁC GIẢ ĐỊNH CỦA BẠN.
════════════════════════════════════════════════════════════════════════

① KHÔNG CÓ MÀN HÌNH RIÊNG CHO TỪNG HÀNH TINH.
   Toàn dự án có ĐÚNG MỘT trang nhiệm vụ (Trái Đất) và ĐÚNG MỘT trang bản đồ 3D dùng
   chung cho 22 điểm đến. Không có template nào để nhân bản. Bạn giả định ngược lại.

② KHÔNG CÓ ĐƯỜNG NẠP DỮ LIỆU NÀO. Đếm được: 0 lời gọi tải một file JSON trong toàn bộ
   client. Nội dung nhiệm vụ Trái Đất nằm thẳng trong trang — riêng phần chữ song ngữ
   đã là 408 khoá viết tay. Thư mục dữ liệu học có tồn tại nhưng CHƯA TRANG NÀO ĐỌC NÓ.
   ⇒ Câu "chỉ thay dữ liệu, không thay gameplay" hiện chưa có nghĩa: chưa có chỗ nào
     để thay dữ liệu vào.

③ TRÌNH ĐIỀU PHỐI BƯỚC ĐÃ CÓ, NHƯNG NÓ CHỈ BIẾT MỘT HÌNH DẠNG.
   Hình dạng đó là: một nhiệm vụ = một DÃY BƯỚC TUYẾN TÍNH, và MỖI BƯỚC TÍNH ĐÚNG MỘT
   LẦN VĨNH VIỄN (cơ sở dữ liệu ghi có điều kiện, xong rồi là không ghi lại được).
   ⇒ Đây là điều quan trọng nhất cho đề xuất của bạn: cấu trúc hiện tại TỪ CHỐI TẬN GỐC
     mọi hoạt động lặp lại được. "Nhiệm vụ ngày" không phải nội dung mới — nó là một
     HÌNH DẠNG DỮ LIỆU MỚI.

④ MÁY CHỦ KHÔNG CÓ KHÁI NIỆM NGÀY. Không có ranh giới ngày, không có múi giờ, không có
   bảng sự kiện, không có đường phát hành nội dung theo mùa. Mọi mốc thời gian trong mã
   chỉ là dấu thời gian ghi lại việc đã xảy ra.
   Trang web là TĨNH: "ra một sự kiện" hiện tại nghĩa là phát hành lại cả trang.

⑤ NĂM TRONG TÁM NHÓM BẠN ĐỀ XUẤT ĐÃ TỒN TẠI — nhưng ở tầm TOÀN APP, không theo hành tinh:

   ┌──────────────────────┬──────────────────────────────────┬──────────────────┐
   │ Nhóm bạn đề xuất     │ Hiện có gì                       │ Đang ở tầm nào   │
   ├──────────────────────┼──────────────────────────────────┼──────────────────┤
   │ Main Missions        │ sảnh nhiệm vụ + nhiệm vụ Trái Đất│ THEO HÀNH TINH ✅│
   │ Knowledge            │ khu Tri Thức · 12 bài · 15 thuật │ toàn app         │
   │                      │ ngữ sổ tay                       │                  │
   │ Training             │ khu Huấn Luyện · 3 mini-game     │ toàn app         │
   │ Collections          │ 21 mẫu vật · 22 huy hiệu         │ toàn app         │
   │ Research Lab         │ MỘT Ô TRỐNG trên trang chủ tàu,  │ —                │
   │                      │ chưa có trang, chưa ai biết là gì│                  │
   │ Side Missions        │ chưa có                          │ —                │
   │ Daily Missions       │ chưa có                          │ —                │
   │ Events               │ chưa có                          │ —                │
   └──────────────────────┴──────────────────────────────────┴──────────────────┘

   ⇒ Đề xuất của bạn thực chất là HAI VIỆC rất khác nhau về giá, đang bị gộp làm một:
     (a) KÉO 3 khu đang dùng chung xuống thành per-planet — đây là tái cấu trúc điều
         hướng, và nó đụng vào điều kiện mở khoá của 22 huy hiệu + 21 mẫu vật (tất cả
         đang đếm theo bộ đếm TOÀN APP: số câu quiz đúng, số bài đã đọc, số hành tinh
         đã ghé…). Đổi tầm là phải tính lại toàn bộ chỗ đó.
     (b) DỰNG 3 hệ thống mới.
     Gộp hai việc làm cả hai trông rẻ hơn thực tế.

⑥ MÁY CHỦ KHÔNG KIỂM ĐÁP ÁN. Client chỉ gửi {nhiệm vụ, bước}; máy chủ tra bảng thưởng
   theo id bước, không hề biết trẻ trả lời đúng hay sai. Đừng thiết kế cơ chế chống gian
   lận ở client — nó không mua được gì.

⑦ LỘ TRÌNH ĐÃ CHỐT LÀ HAI ĐIỂM ĐẾN: Trái Đất → Mặt Trăng. Cổng mở điểm đến sau là
   70% số bước, làm tròn lên (hiện là 5/7 bước). Mặt Trăng CHƯA có nhiệm vụ nào.

════════════════════════════════════════════════════════════════════════
⚠️⚠️ PHẦN 2 — RÀNG BUỘC SỐ 1: NGÂN SÁCH KHUÔN. ĐÂY LÀ THỨ ĐÃ BÁC HAI VÒNG TRƯỚC.
════════════════════════════════════════════════════════════════════════

Dự án có 5 khuôn tương tác được đặt tên. Luật: **một nhiệm vụ không dùng cùng một khuôn
quá 2 LẦN.** Đây không phải hướng dẫn mềm — nó đã bác nguyên hai vòng đề xuất trước.

Đếm bằng công cụ trên mã nguồn thật, KHÔNG phải ước lượng:

┌─────────────────────────┬────────────────────────────┬────────────────────────┐
│ Khuôn                   │ Trạng thái CÀI ĐẶT         │ Dùng ở Trái Đất        │
├─────────────────────────┼────────────────────────────┼────────────────────────┤
│ profile_builder         │ ✅ ĐÃ tách thành file dùng │ 2/2 ⛔ ĐÃ ĐẦY          │
│ (thẻ → ô, kéo HOẶC bấm) │    chung, chơi được bàn phím│                        │
├─────────────────────────┼────────────────────────────┼────────────────────────┤
│ câu đố chọn đáp án      │ ⚠️ còn nằm TRONG trang     │ 2/2 ⛔ ĐÃ ĐẦY          │
│                         │    nhiệm vụ Trái Đất       │                        │
├─────────────────────────┼────────────────────────────┼────────────────────────┤
│ signal_scan             │ ⚠️ còn nằm TRONG trang     │ 2/2 ⛔ ĐÃ ĐẦY          │
│ (chạm dấu hiệu trên bản │    nhiệm vụ Trái Đất       │ (từng lên 3/2 và đó là │
│  đồ theo toạ độ thật)   │                            │  lý do một bước phải   │
│                         │                            │  đổi hẳn cơ chế)       │
├─────────────────────────┼────────────────────────────┼────────────────────────┤
│ sequence_reconstruction │ ⚠️ còn nằm TRONG trang     │ 1/2 ✅ CÒN 1 CHỖ       │
│ (sắp đúng thứ tự)       │    nhiệm vụ Trái Đất       │                        │
├─────────────────────────┼────────────────────────────┼────────────────────────┤
│ orientation_align       │ ❌ CHƯA TỪNG ĐƯỢC CÀI ĐẶT  │ 0 — bước cần nó đã bỏ  │
│ (ngắm/canh cho thẳng)   │                            │   hẳn                  │
└─────────────────────────┴────────────────────────────┴────────────────────────┘

⇒ Số khuôn THẬT SỰ dùng lại được ngay hôm nay: **1** (profile_builder).
  Ba khuôn nữa tồn tại dưới dạng mã viết dính vào Trái Đất, phải rút ra mới dùng lại được.
  Khuôn thứ năm chỉ là một cái tên trong tài liệu.

⇒ Bạn đề xuất 8 nhóm hoạt động. Mỗi nhóm cần một cảm giác chơi khác nhau, nếu không thì
  chúng không phải 8 nhóm mà là một nhóm gọi bằng 8 tên. Hãy tự đối chiếu con số này
  TRƯỚC KHI viết bất cứ thứ gì khác.

════════════════════════════════════════════════════════════════════════
⚠️⚠️ PHẦN 3 — RÀNG BUỘC SỐ 2: NGÂN SÁCH NỘI DUNG. ĐÂY LÀ THỨ ĐÃ BÁC VÒNG 1.
════════════════════════════════════════════════════════════════════════

Mục 7 của bạn đề nghị 215 mục nội dung cho RIÊNG Trái Đất. Đối chiếu:

┌──────────────────────────┬───────────────────┬─────────────────────────────┐
│ Loại                     │ Bạn đề nghị       │ TOÀN BỘ APP hiện có         │
│                          │ (riêng Trái Đất)  │ (sau nhiều tuần làm)        │
├──────────────────────────┼───────────────────┼─────────────────────────────┤
│ Nhiệm vụ chính           │ 8                 │ 7 bước (Trái Đất)           │
│ Nhiệm vụ phụ             │ 30                │ 0                           │
│ Nhiệm vụ ngày            │ 100               │ 0                           │
│ Sự kiện                  │ 8                 │ 0                           │
│ Module nghiên cứu        │ 4                 │ 0                           │
│ Bài tri thức             │ 20                │ 12 (có trùng chủ đề)        │
│ Bài huấn luyện           │ 15                │ 3 mini-game                 │
│ Mục sưu tập              │ 30                │ 21 mẫu vật                  │
│ (kèm theo) ngân hàng quiz│ —                 │ 35 câu ← nút thắt lớn nhất  │
├──────────────────────────┼───────────────────┼─────────────────────────────┤
│ TỔNG                     │ 215 mục           │ ~85 mục, CHO CẢ APP         │
└──────────────────────────┴───────────────────┴─────────────────────────────┘

Riêng "100 nhiệm vụ ngày" đã gấp gần BA LẦN toàn bộ ngân hàng quiz của cả dự án.
Và đó mới là hành tinh thứ nhất; nhân lên 9 điểm đến là ~1.900 mục.

⚠️ MỖI MỤC ĐẮT HƠN BẠN TƯỞNG. Một "mục" không phải một dòng. Bắt buộc:
   · Song ngữ {vi, en} ở TỪNG trường hiển thị — tên, mô tả, lời Comet, lời khen, lời an ủi
   · Mọi con số hay dữ kiện khoa học phải kèm URL nguồn NASA/ESA/NOAA ĐÃ KIỂM CÒN SỐNG
   · Không có nguồn thì phải viết ĐỊNH TÍNH, không được nêu con số
   ⇒ Một "nhiệm vụ ngày" tối thiểu là 6–10 trường chữ, không phải 1.

⇒ VÌ VẬY: từ vòng này, hãy đếm nội dung bằng **SỐ TRƯỜNG CHỮ PHẢI VIẾT**, không đếm bằng
  "số mục". Con số thứ hai giấu mất chi phí thật.

════════════════════════════════════════════════════════════════════════
VIỆC CẦN LÀM — bốn việc, làm đủ cả bốn
════════════════════════════════════════════════════════════════════════

A. CHỌN PHẠM VI, VÀ NÓI RÕ VÌ SAO.
   Ba khu Tri Thức · Huấn Luyện · Bộ Sưu Tập đang ở tầm TOÀN APP và đang chạy tốt.
   Có lý do nào đủ mạnh để kéo chúng xuống thành per-planet không?
   ⚠️ "GIỮ NGUYÊN Ở TẦM TOÀN APP" LÀ MỘT CÂU TRẢ LỜI HỢP LỆ, không bị coi là né việc.
   Nếu chọn kéo xuống thì phải trả lời được: trẻ được thêm điều gì mà hiện chưa có?
   Nếu chọn giữ nguyên thì hệ Activities chỉ còn phục vụ Main + Side + 3 nhóm mới —
   nói thẳng ra như vậy.

B. ÁNH XẠ TỪNG NHÓM BẠN GIỮ LẠI VÀO BỘ KHUÔN.
   Với mỗi nhóm: dùng khuôn nào · nhóm đó tiêu mấy chỗ trên 2 · nếu phải đề xuất khuôn
   MỚI thì nói rõ nó là gì, vì sao 4 khuôn cũ không làm được, và CHƠI BẰNG BÀN PHÍM thế
   nào (không phải "thêm nhãn trợ năng" — mà là: nhấn phím nào, thứ tự tiêu điểm ra sao,
   trẻ biết mình đang chọn gì bằng cách nào, xác nhận bằng phím gì).
   Nhóm nào KHÔNG cần cơ chế chơi thì nói thẳng là không có.

C. ƯỚC LƯỢNG LẠI NỘI DUNG CHO ĐÚNG MỘT ĐIỂM ĐẾN: MẶT TRĂNG.
   Không phải cho cả 9. Ta cần một con số đo được trước khi nhân lên.
   Đếm bằng SỐ TRƯỜNG CHỮ (xem phần 3), tách riêng: chữ hiển thị cho trẻ · lời thoại
   nhân vật · dữ kiện cần tra nguồn. Ghi rõ mục nào cần con số khoa học — những mục đó
   sẽ chuyển sang model khác tra nguồn, và đó là phần chậm nhất.

D. PHÒNG NGHIÊN CỨU (Research Lab) — ĐÂY LÀ Ô TRỐNG THẬT, VÀ LÀ VIỆC CỦA BẠN.
   Trang chủ con tàu có một ô mang tên này, trạng thái "sắp ra mắt", và CHƯA AI BIẾT
   NÓ NÊN LÀ GÌ. Không có mã nguồn nào để đối chiếu, không có ràng buộc cũ nào —
   nên đây là chỗ đề xuất của bạn có giá trị cao nhất.
   Hãy mô tả: trẻ vào đó làm gì · nó khác khu Tri Thức (đọc bài, làm quiz) ở chỗ nào ·
   một phiên chơi 2–3 phút diễn ra thế nào, kể theo từng nhịp · nó dùng khuôn nào trong
   bảng ngân sách · và nó cần bao nhiêu nội dung cho phiên bản đầu tiên.
   ⚠️ Nếu ý tưởng của bạn cần một khuôn mới thì cứ đề xuất, nhưng phải nói rõ là mới.

════════════════════════════════════════════════════════════════════════
ĐÃ BÁC RỒI — ĐỪNG ĐỀ XUẤT LẠI
════════════════════════════════════════════════════════════════════════

  · 215 mục nội dung cho một hành tinh. Xem bảng ở phần 3.
  · Nhiệm vụ ngày và Sự kiện ở phiên bản ĐẦU. Chúng đòi máy chủ có khái niệm ngày và
    một đường phát hành nội dung theo mùa — cả hai đều chưa tồn tại, và tài liệu quyết
    định của dự án đã xếp hai thứ này XUỐNG SAU CÙNG, kèm lý do: chúng chỉ có ý nghĩa
    khi đã đủ nội dung để đáng quay lại. Bạn đưa chúng lên đầu.
  · "Chỉ cần thay dữ liệu" — chưa có đường nạp dữ liệu nào (điểm ②).
  · Dùng một khuôn đã đầy rồi biện minh bằng "cách trình bày khác".   ← lỗi hai vòng trước
  · Gỡ bỏ tương tác để tránh trùng lặp (biến một hoạt động thành đoạn phim có nút).
  · Đổi id các bước đang chạy — id là khoá trong cơ sở dữ liệu người chơi.
  · Thiết kế cơ chế chống gian lận ở client (điểm ⑥).
  · Tự ước lượng công sức lập trình. Bạn không đọc được mã nguồn nên không ước lượng
    được; phần đó do bên khác làm.

════════════════════════════════════════════════════════════════════════
KHUÔN TRẢ LỜI — viết đúng dạng này
════════════════════════════════════════════════════════════════════════

# Đề xuất VÒNG 2: hệ thống Activities
**Người viết:** ChatGPT · **Ngày:** 2026-08-04

## 0. Phạm vi tôi chọn và khuôn tôi tiêu
<Bắt buộc, viết TRƯỚC MỌI THỨ KHÁC.
 · Việc A: tôi chọn kéo xuống per-planet / giữ nguyên toàn app — và vì sao.
 · Sau lựa chọn đó, hệ Activities gồm ĐÚNG những nhóm nào.
 · Bảng: mỗi nhóm dùng khuôn nào · tiêu mấy chỗ trên 2 · khuôn nào là MỚI.>

## 1. Vấn đề cần giải
<Một đoạn. Nói vấn đề, không nói giải pháp.>

## 2. Đề xuất
<Mô tả. Ngắn gọn, cụ thể.>

## 3. Từng nhóm hoạt động
<Với mỗi nhóm: trẻ làm gì · khuôn nào · chơi bằng bàn phím thế nào ·
 có cơ chế chơi hay không (nói thẳng nếu không).>

## 4. Phòng Nghiên Cứu — kịch bản một phiên 2–3 phút
<Kể theo trình tự trẻ trải nghiệm, từng nhịp một. Trẻ THẤY gì, LÀM gì,
 nhận lại gì sau mỗi thao tác. Đây là việc D.>

## 5. Nội dung cần cho MẶT TRĂNG — đếm bằng SỐ TRƯỜNG CHỮ
<Bảng. Tách: chữ hiển thị · lời thoại nhân vật · dữ kiện cần tra nguồn.
 Mục nào cần con số khoa học thì đánh dấu [CẦN KIỂM: …].>

## 6. Giả định tôi đang dựa vào
<Gạch đầu dòng. ĐÂY LÀ MỤC QUAN TRỌNG NHẤT — sẽ được đối chiếu với mã nguồn.
 Vòng 1 bạn có 3/7 giả định sai, và cả ba đều ở phần "cái gì đã tồn tại".>

## 7. Cái tôi KHÔNG chắc
<Thành thật. Chỗ nào bạn đoán thì nói là đoán.
 Vòng 1 mục này viết tốt và chính nó dẫn tới phần lớn phát hiện — giữ nguyên cách viết đó.>

## 8. Phương án nhỏ hơn nếu quá tốn
<Nếu phải cắt xuống 1/3 công sức thì giữ lại phần nào?
 ⚠️ Vòng 1 bạn cắt nhầm: bạn giữ lại đúng hai nhóm ĐẮT NHẤT (Nhiệm vụ ngày, Sự kiện)
 và bỏ đi hai nhóm rẻ nhất. Lần này cắt theo GIÁ, không cắt theo mức hấp dẫn.>
```

---

## Ghi chú cho Claude ở vòng sau

- **Đọc mục 0 trước tiên.** Nếu nó chọn "kéo xuống per-planet" mà không nói được trẻ được
  thêm gì, thì đó là câu trả lời chưa đủ — chi phí bên đó là 22 huy hiệu + 21 mẫu vật phải
  tính lại điều kiện mở khoá, cộng `docs/decisions/003`.
- **Kiểm mục 6 và mục 3.** Vòng 1 sai 3/7 giả định, tất cả đều ở phần *"cái gì đã tồn tại"* —
  nên vòng này phần 1 của đề bài đã ghi thẳng bảy điểm đó ra. Nếu mục 6 lại khai một giả định
  mâu thuẫn với phần 1 thì nghĩa là nó không đọc kỹ, không phải nó bất đồng.
- **Đếm lại khuôn bằng `grep`** nếu mục 0 khai sai: `grep -c "buildAsk(" mission-earth.html`
  và `grep -c "dragDrop(" mission-earth.html` (trừ 1 cho dòng định nghĩa hàm).
- **Việc D là phần đáng giá nhất của vòng này** — Phòng Nghiên Cứu không có mã nguồn để đối
  chiếu, tức không có gì bác được nó bằng số. Đổi lại, nó phải nằm trong ngân sách khuôn.
- Mọi câu `[CẦN KIỂM: …]` ở mục 5 gom **một lượt** gửi Gemini tra nguồn — điểm giao duy nhất
  giữa hai lane (`docs/PHAN-VAI.md`).
- Nếu vòng này ra kết quả dùng được, **`docs/decisions/001` đang mở** là chỗ ghi quyết định
  (bao nhiêu nhóm hoạt động · per-planet hay toàn app · Daily/Event xếp ở đâu).
