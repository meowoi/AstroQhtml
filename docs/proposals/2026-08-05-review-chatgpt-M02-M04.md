# RÀ SOÁT M-02 → M-04 — gửi ChatGPT trước khi viết M-05, M-06

> Ngày 05/08/2026 · Đã đối chiếu từng bảng với mã nguồn và với `docs/decisions/`.

Ba nhiệm vụ đứng vững về chủ đề: **không cái nào trùng M-01**, câu hỏi lớn của M-04
(*"nếu không nhìn thấy chúng, làm sao biết đại dương luôn chuyển động?"*) là câu hay nhất
trong cả bốn vòng. Ngân sách khuôn **không nhiệm vụ nào vượt 2 lần** — đã cộng lại từng
bảng chi tiết. Asset: **0 ảnh mới cho cả ba**, đúng như đã chốt.

Ba việc phải sửa.

---

## ① LỖI CỘNG — dòng M-02, lần thứ hai

| | K1 | K2 | K3 | K4 | K5 | K6 | tổng |
|---|---|---|---|---|---|---|---|
| Mục 0 đang ghi | 1 | 1 | 0 | **1** | 2 | 0 | **5** |
| Bảng chi tiết + dòng "Khuôn đã tiêu" | 1 | 1 | 0 | **2** | 2 | 0 | **6** |

Chặng 4 và chặng 6 của M-02 đều là khuôn 4. M-03 và M-04 thì khớp chính xác.

⇒ **Phép thử một giây, dùng cho mọi dòng từ nay:** *tổng một dòng Mục 0 phải bằng đúng số
chặng của nhiệm vụ đó.* Dòng M-02 cộng ra 5 trong khi nhiệm vụ có 6 chặng — sai lộ ra ngay
mà không cần đọc lại bảng chi tiết. Cả hai lần dòng M-02 sai đều bị bắt bằng đúng phép này.

---

## ② KHUÔN 5 ĐANG BỊ DÙNG LÀM KHUÔN 3 — 4 trong 6 lần

Đây là việc quan trọng nhất, và nó chính là lối thoát sai mà đề bài đã gọi tên:
⛔ *"dùng khuôn đã đầy rồi biện minh bằng cách trình bày khác"*.

**Khuôn 5 (`buildXsec`) không phải "một câu hỏi có cột minh hoạ".** Định nghĩa của nó
trong dự án: *đoán vị trí một nơi trên một **thang có thứ tự**; mỗi lượt để lại một chip
trên cột, và **cái cột dựng dần lên mới là thứ mang bài học**.* Ở M-01 bước ④, xếp xong
bốn nấc thì chính cái cột **là bằng chứng** cho tiêu đề bước *"Sự sống ở khắp nơi"*.
Hồ sơ dự án ghi thẳng: **nó KHÔNG phải câu đố 4 lựa chọn trá hình** — câu đố hỏi xong là
vứt câu hỏi đi, còn ở đây cột phải ở lại.

### Phép thử

> **Bốn lựa chọn có xếp được thành một thang theo thứ tự không?**
> Có → khuôn 5. Không → đó là khuôn 3, và khuôn 3 có trần 2 lần/nhiệm vụ.

Soi lại 6 lần dùng:

| Chặng | Lựa chọn | Có thang? | Thực chất |
|---|---|---|---|
| M-02 ① | biển · mây · sông · hồ | ✗ không có thứ tự | **khuôn 3** |
| M-02 ⑤ | giai đoạn tiếp theo | ✗ | **khuôn 3** |
| M-03 ① | thời điểm trong năm | ✗ mùa là **vòng**, không phải thang | **khuôn 3** |
| M-03 ⑤ | ghép cặp mùa hai bán cầu | ✗ đây là **ghép cặp** | **khuôn 4** |
| M-04 ① | vùng biển chảy mạnh hơn | ✓ **tốc độ là thang** | khuôn 5 ✓ |

⇒ M-02 thực chất đang là `K3 ×2` (chưa khai), M-03 là `K3 ×2 + K4 ×2`.

### Sửa — và hai chỗ có thang THẬT đang bị bỏ lỡ

**M-02 có sẵn một thang, rất đẹp: ĐỘ CAO.** Mây (cao nhất) → mưa đang rơi → sông trên
mặt đất → biển (thấp nhất). Đổi chặng ① thành *"giọt nước đang ở nấc nào của cột độ cao"*
thì nó thành khuôn 5 **thật**, và cái cột dựng dần lên biến vòng tuần hoàn nước thành một
**hành trình đi lên rồi rơi xuống nhìn thấy được** — đúng thứ tiêu đề nhiệm vụ hứa. Đây là
cùng hình dạng với bước ④ của M-01, nên **dùng lại được `buildXsec` không phải viết mới**.

**M-03 cũng có một thang, và nó chính là cơ chế của mùa: ĐỘ DÀI NGÀY.** Ngày rất dài →
dài → ngắn → rất ngắn. Đoán "ở đây ngày dài hay ngắn" xếp lên thang 4 nấc thì cột dựng
lên **chính là lời giải thích mùa**, không phải một câu đố về mùa. Còn chặng ⑤ (ghép cặp
Bắc–Nam) thì khai đúng là **khuôn 4**.

⇒ Không phải cắt bớt tương tác — là **gọi đúng tên** rồi khai lại ngân sách cho đúng.

---

## ③ CHẶNG CUỐI LÀ CHỖ CHỐT, KHÔNG PHẢI BÀI KIỂM TRA THỨ SÁU

Cả ba nhiệm vụ đang kết bằng thêm một bài tập nữa:

- M-02 ⑥ *"ghép các trạng thái còn thiếu vào đúng vị trí"* (khuôn 4)
- M-03 ⑥ *"kéo các thẻ mùa vào đúng bán cầu"* (khuôn 4)
- M-04 ⑥ *"ghép các đoạn dòng biển còn thiếu"* (khuôn 4)

Dự án có luật ngược lại, và **đang canh bằng phép kiểm tự động** cho bước ⑦ của M-01:
*bước cuối phải có **0 lựa chọn**.* Lý do ghi trong hồ sơ: **nó nằm ngay trước màn
thưởng — bắt trả lời đúng mới cho qua là dựng một cửa chặn ở đúng chỗ trẻ tưởng mình đã
xong.** Lý do đó áp cho mọi nhiệm vụ, không riêng M-01.

Bước ⑦ của M-01 làm thế này: **ba dòng có dấu ✓** nhắc lại ba thứ trẻ vừa tự khám phá ở
các chặng trước, **một** nút đóng dấu, và một câu chốt mạnh (*"phải có đủ cả ba cùng một
lúc"*). Không có lựa chọn nào.

⇒ Viết lại chặng ⑥ của cả ba theo khuôn đó. Nó **rẻ hơn** (không tiêu suất khuôn nào) và
trả lại mỗi nhiệm vụ **một suất khuôn 4** đang bị tiêu cho việc kiểm tra lại.

### Kèm theo, M-02 đang dạy thứ tự HAI LẦN

Chặng ③ *"mở đúng thứ tự các giai đoạn"* → kết quả *"đường đi được nối thành vòng kín"*.
Chặng ⑥ *"ghép trạng thái còn thiếu"* → kết quả *"toàn bộ vòng tuần hoàn sáng hoàn chỉnh"*.
Hai chặng, một bài học, và **chặng ③ đã đóng vòng rồi**. Sáu chặng nhưng chỉ có năm bài
học. Sửa chặng ⑥ theo mục ③ ở trên là hết trùng.

---

## ④ VIỆC TIẾP THEO

1. Sửa Mục 0 dòng M-02, và **cộng lại từng dòng theo phép thử ở mục ①**.
2. Khai lại khuôn cho 4 chặng ở mục ②; đổi M-02 ① sang **thang độ cao** và M-03 ① sang
   **thang độ dài ngày** để chúng thành khuôn 5 thật.
3. Viết lại chặng ⑥ của cả ba thành **chốt, không kiểm tra**.
4. Rồi mới viết **M-05 và M-06** như bạn đã định — và áp luôn ba luật trên cho chúng.

Không cần viết lại phần chủ đề, câu hỏi lớn, asset hay cảnh — những phần đó đã đúng.
