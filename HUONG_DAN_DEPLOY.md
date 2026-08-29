# Hướng dẫn đưa công cụ lên mạng để dùng trên cả điện thoại và máy tính (100% MIỄN PHÍ)

Làm theo đúng thứ tự bên dưới. **Không cần nạp tiền ở bất kỳ đâu, không cần thẻ tín dụng,
không cần API key.** Chỉ cần 1 tài khoản GitHub và 1 tài khoản Streamlit Cloud, cả hai đều
đăng ký miễn phí bằng email.

Sau khi xong, bạn sẽ có **1 đường link** (ví dụ: `https://ten-ban-dat.streamlit.app`) —
mở link đó trên điện thoại hoặc máy tính đều dùng được, giống như một trang web.

---

## Bước 1 — Tạo tài khoản GitHub (nơi lưu code của công cụ)

1. Vào **https://github.com** → bấm **Sign up** → đăng ký bằng email (miễn phí, không cần thẻ).
2. Xác thực email theo hướng dẫn.

---

## Bước 2 — Tải code công cụ lên GitHub (không cần biết lệnh git)

1. Đăng nhập GitHub xong, bấm dấu **+** ở góc trên bên phải → chọn **New repository**.
2. Đặt tên, ví dụ: `dich-pdf-song-ngu` → để chế độ **Public** → bấm **Create repository**.
3. Ở trang repo vừa tạo, bấm **"uploading an existing file"** (hoặc **Add file → Upload files**).
4. Giải nén file `pdf-bilingual-translator.zip` (mình đã gửi ở tin nhắn trước) ra một thư mục
   trên máy tính.
5. **Kéo-thả toàn bộ nội dung bên trong** thư mục `pdf-bilingual-translator` (không phải kéo cả
   thư mục ngoài cùng — kéo các file/thư mục con: `app.py`, `cli.py`, `core/`, `requirements.txt`,
   `README.md`...) vào ô upload trên GitHub.
6. Cuộn xuống dưới, bấm **Commit changes** (giữ nguyên các tùy chọn mặc định).

---

## Bước 3 — Deploy lên Streamlit Community Cloud (biến code thành 1 trang web, miễn phí)

1. Vào **https://share.streamlit.io**
2. Bấm **Sign in with GitHub** → cho phép Streamlit truy cập tài khoản GitHub của bạn (miễn phí,
   không yêu cầu thẻ ở bất kỳ bước nào).
3. Bấm **Create app** (hoặc **New app**).
4. Điền:
   - **Repository**: chọn `dich-pdf-song-ngu` (repo bạn vừa tạo ở Bước 2).
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (tùy chọn): đặt tên link dễ nhớ, ví dụ `dich-pdf-duoc` → link sẽ là
     `https://dich-pdf-duoc.streamlit.app`
5. Bấm **Deploy**. Chờ khoảng 1-3 phút để hệ thống cài đặt tự động (bạn sẽ thấy log chạy trên
   màn hình).
6. Khi thấy giao diện công cụ hiện ra (ô upload PDF, nút "Bắt đầu dịch"...) — **xong, không cần
   cấu hình gì thêm** (không có ô nhập API key vì công cụ đã dùng dịch vụ dịch miễn phí sẵn có).

---

## Bước 4 — Dùng công cụ trên điện thoại và máy tính

- **Trên máy tính**: mở trình duyệt (Chrome/Edge/Safari) → vào link
  `https://ten-ban-dat.streamlit.app`
- **Trên điện thoại**: mở trình duyệt điện thoại → dán y hệt link đó → upload PDF từ bộ nhớ
  điện thoại hoặc từ Google Drive/iCloud tải về máy trước.
- Có thể **lưu link này thành icon trên màn hình chính điện thoại** để mở nhanh như 1 app:
  - iPhone (Safari): bấm nút Chia sẻ → **Thêm vào MH chính**.
  - Android (Chrome): bấm menu 3 chấm → **Thêm vào màn hình chính**.

---

## Sau này muốn cập nhật/sửa công cụ thì sao?

Chỉ cần vào lại repo trên GitHub → sửa/thay file → **Commit changes**. Streamlit Cloud sẽ
**tự động deploy lại** trong vài phút, không cần làm lại từ đầu.

---

## Một vài lưu ý quan trọng

- **Chất lượng dịch**: công cụ dùng dịch máy miễn phí (Google Translate không chính thức qua
  thư viện mã nguồn mở), **không thông minh bằng AI cao cấp** (như Claude/ChatGPT) — câu dài,
  phức tạp hoặc thuật ngữ chuyên ngành đặc thù có thể dịch chưa mượt, cần bạn đọc lại và chỉnh
  sửa trước khi dùng chính thức (nộp hồ sơ, xuất bản...). Đoạn máy không dịch được sẽ giữ
  nguyên tiếng Anh kèm ghi chú để bạn dễ nhận biết.
- **Tốc độ**: vì gọi dịch vụ dịch miễn phí (có giới hạn tốc độ), tài liệu dài có thể mất vài
  phút — cứ để tab mở, đừng đóng giữa chừng.
- **App "ngủ"**: gói miễn phí của Streamlit Cloud cho phép app "ngủ" nếu không ai dùng trong vài
  ngày — chỉ cần bấm vào link, chờ ~30 giây để app "thức dậy" lại là dùng bình thường.
- **Không mất phí ở bất kỳ đâu** trong toàn bộ quy trình này — GitHub free, Streamlit Cloud
  free, dịch vụ dịch free.

---

## Nếu bạn chỉ muốn dùng trên 1 máy tính, không cần deploy lên mạng

Vẫn có cách đơn giản hơn nhưng **chỉ dùng được trên đúng máy tính đó**:

```bash
cd pdf-bilingual-translator
pip install -r requirements.txt
streamlit run app.py
```

Xem thêm chi tiết trong `README.md` đi kèm.
