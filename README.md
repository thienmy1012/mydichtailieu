# Công cụ dịch PDF → Word song ngữ Anh–Việt (100% miễn phí, chuyên guideline dược phẩm)

Công cụ chạy **độc lập**, dùng lại bao nhiêu tài liệu tùy thích, **hoàn toàn miễn phí — không
cần API key, không cần đăng ký tài khoản, không cần thẻ tín dụng ở bất kỳ đâu.**

## Tính năng

- Trích xuất PDF giữ cấu trúc: tiêu đề (nhiều cấp), đoạn văn, danh sách, bảng biểu, hình ảnh, số trang.
- Dịch miễn phí bằng Google Translate (không cần API key).
- Tự động sửa lại các thuật ngữ dược/quy chế quốc tế (GMP, API, CTD, pharmacovigilance...)
  theo bộ thuật ngữ chuẩn nếu máy dịch bỏ sót — xem `core/glossary.py`.
- Đoạn nào dịch máy thất bại sẽ giữ nguyên tiếng Anh + ghi chú `[MÁY DỊCH — cần kiểm tra lại]`
  để bạn dễ rà soát, thay vì bịa nội dung.
- Xuất file Word (.docx): tiếng Anh gốc giữ nguyên định dạng (đậm/nghiêng/tiêu đề), bản dịch
  tiếng Việt in nghiêng màu xanh đậm ngay bên dưới. Bảng biểu là bảng Word thật. Font
  Times New Roman hỗ trợ đầy đủ dấu tiếng Việt.
- Hai cách dùng: giao diện web (kéo-thả file) hoặc dòng lệnh (dịch hàng loạt).
- **Dùng được trên cả điện thoại và máy tính** khi deploy lên Streamlit Cloud (miễn phí) —
  xem hướng dẫn chi tiết trong `HUONG_DAN_DEPLOY.md`.

## ⚠️ Lưu ý quan trọng về chất lượng dịch

Vì hoàn toàn miễn phí, công cụ dùng **dịch máy** (Google Translate) thay vì AI cao cấp như
Claude/ChatGPT. Điều này có nghĩa:

- Câu ngắn, đơn giản → dịch khá tốt.
- Câu dài, phức tạp, nhiều mệnh đề lồng nhau → có thể dịch cứng, thiếu tự nhiên, hoặc đôi khi
  sai ý — **bạn nên đọc lại và chỉnh sửa trước khi dùng cho mục đích chính thức** (nộp hồ sơ
  cơ quan quản lý, xuất bản, hợp đồng...).
- Đây không phải bản dịch có "hiểu ngữ cảnh" xuyên suốt tài liệu như AI — mỗi đoạn được dịch
  riêng lẻ.
- Bộ thuật ngữ dược (glossary) giúp sửa các từ viết tắt/thuật ngữ chuyên ngành bị bỏ sót, nhưng
  không thể sửa hết mọi lỗi ngữ pháp/văn phong.

Nếu tài liệu cực kỳ quan trọng (nộp cơ quan quản lý, có giá trị pháp lý), nên coi bản dịch này
là **bản nháp để tăng tốc độ đọc hiểu**, và nhờ người biết chuyên môn rà soát lại trước khi
dùng chính thức.

## 1. Cài đặt (chỉ làm 1 lần, nếu chạy trên máy tính)

Yêu cầu: Python 3.9+ đã cài trên máy.

```bash
cd pdf-bilingual-translator
pip install -r requirements.txt
```

## 2. Cách dùng

### A. Giao diện web (khuyến nghị)

```bash
streamlit run app.py
```

Trình duyệt tự mở `http://localhost:8501`. Upload PDF → bấm **Bắt đầu dịch** → tải file Word.

Muốn dùng được **trên cả điện thoại**, xem hướng dẫn deploy miễn phí lên mạng trong file
`HUONG_DAN_DEPLOY.md` đi kèm.

### B. Dòng lệnh (phù hợp dịch hàng loạt)

Dịch 1 file:
```bash
python cli.py document.pdf --output-dir ./output
```

Dịch cả thư mục (nhiều PDF cùng lúc):
```bash
python cli.py ./thu_muc_pdf_dau_vao/ --output-dir ./thu_muc_ket_qua/
```

## 3. Tùy chỉnh

- **Thuật ngữ chuyên ngành**: chỉnh sửa `core/glossary.py` — thêm/sửa cặp thuật ngữ
  Anh–Việt để công cụ tự động sửa lại khi máy dịch bỏ sót. Mặc định đã có sẵn ~45 thuật
  ngữ dược/quy chế phổ biến (GMP, GCP, CAPA, OOS, pharmacovigilance...).
- **Màu/kiểu chữ bản dịch**: chỉnh các hằng số `VI_TRANSLATION_COLOR`, `BODY_SIZE`,
  `FONT_NAME` trong `core/docx_builder.py`.

## 4. Giới hạn cần biết

- **Bảng không có đường kẻ rõ ràng**: một số PDF trình bày bảng bằng cách canh cột (không
  vẽ viền) — công cụ có thể không nhận diện được đó là bảng và sẽ trích xuất thành các đoạn
  văn bản rời. Bạn nên kiểm tra lại phần này sau khi dịch.
- **PDF dạng ảnh scan** (không có lớp văn bản): công cụ hiện trích xuất văn bản trực tiếp từ
  PDF, chưa tích hợp OCR. Nếu PDF của bạn là bản scan, cần OCR trước (ví dụ bằng Adobe Acrobat
  hoặc `ocrmypdf`) rồi mới đưa vào công cụ.
- **Chữ trong hình ảnh không được dịch** (đúng theo yêu cầu) — hình được giữ nguyên.
- **Dịch vụ dịch miễn phí có thể bị giới hạn tốc độ** nếu dịch quá nhiều/quá nhanh — công cụ
  tự động chờ và thử lại, nhưng tài liệu rất dài có thể mất nhiều phút hơn.

## 5. Cấu trúc thư mục

```
pdf-bilingual-translator/
├── app.py                  # Giao diện web (Streamlit)
├── cli.py                  # Công cụ dòng lệnh
├── core/
│   ├── extract.py          # Bước 1: trích xuất cấu trúc PDF
│   ├── translate.py        # Bước 2: dịch miễn phí + sửa thuật ngữ
│   ├── docx_builder.py     # Bước 3+4: ghép song ngữ, xuất .docx
│   ├── glossary.py         # Thuật ngữ chuẩn (chỉnh sửa được)
│   └── pipeline.py         # Nối 3 bước lại với nhau
├── requirements.txt
├── README.md
└── HUONG_DAN_DEPLOY.md     # Hướng dẫn dùng trên điện thoại + máy tính (miễn phí)
```
