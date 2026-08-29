# -*- coding: utf-8 -*-
"""
app.py
Giao dien web don gian (Streamlit) de dich PDF -> Word song ngu Anh-Viet.
HOAN TOAN MIEN PHI - khong can API key, khong can dang ky tai khoan nao.

Chay:
    streamlit run app.py

Se mo trinh duyet tai http://localhost:8501
"""
import os
import tempfile
import time

import streamlit as st

from core.pipeline import translate_pdf_to_bilingual_docx

st.set_page_config(page_title="Dịch PDF song ngữ Anh–Việt (Miễn phí)", page_icon="📄", layout="centered")

st.title("📄 Công cụ dịch PDF → Word song ngữ Anh–Việt")
st.caption("Miễn phí 100% — không cần API key, không cần đăng ký tài khoản. "
           "Tối ưu cho tài liệu guideline dược phẩm quốc tế (ICH / WHO / FDA / EMA...)")

st.warning(
    "⚠️ **Lưu ý về chất lượng**: Công cụ dùng dịch máy miễn phí (Google Translate). "
    "Với câu dài, phức tạp hoặc thuật ngữ chuyên ngành, bản dịch có thể chưa tự nhiên hoặc "
    "cần chỉnh sửa lại. Đoạn nào máy không dịch được sẽ giữ nguyên tiếng Anh kèm ghi chú "
    "**\"[MÁY DỊCH — cần kiểm tra lại]\"** để bạn dễ rà soát.",
    icon="⚠️",
)

with st.sidebar:
    st.header("ℹ️ Thông tin")
    st.caption(
        "Công cụ chạy hoàn toàn miễn phí, dùng dịch vụ dịch công khai của Google. "
        "Không cần API key, không cần tài khoản, không giới hạn số lượt dùng."
    )
    st.markdown("---")
    st.caption(
        "💡 Nếu dịch tài liệu dài, quá trình có thể mất vài phút vì dịch từng đoạn một "
        "để đảm bảo không bị giới hạn tốc độ từ dịch vụ miễn phí."
    )

uploaded_file = st.file_uploader("Chọn file PDF tiếng Anh cần dịch", type=["pdf"])

enable_ocr = st.checkbox(
    "🔎 Nhận diện chữ trong hình ảnh / trang scan (OCR) và dịch luôn phần đó",
    value=True,
    help="Bật tính năng này nếu file PDF có chứa ảnh chụp/scan văn bản (không phải chữ dạng text "
         "thật). Công cụ sẽ tự nhận diện chữ trong ảnh bằng Tesseract OCR, giữ nguyên ảnh gốc và "
         "thêm phần chữ nhận diện + bản dịch ngay bên dưới. Có thể làm quá trình xử lý chậm hơn "
         "một chút với tài liệu nhiều ảnh.",
)

start_btn = st.button("🚀 Bắt đầu dịch", type="primary", use_container_width=True, disabled=uploaded_file is None)

if start_btn:
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        out_name = os.path.splitext(uploaded_file.name)[0] + "_song_ngu.docx"
        out_path = os.path.join(tmpdir, out_name)

        status = st.empty()
        progress_bar = st.progress(0.0)
        start_time = time.time()

        def progress_cb(stage, current, total):
            if stage == "extract":
                status.info("📑 Đang trích xuất cấu trúc tài liệu từ PDF...")
                progress_bar.progress(0.05)
            elif stage == "translate":
                pct = 0.1 + 0.85 * (current / max(total, 1))
                elapsed = time.time() - start_time
                status.info(f"🌐 Đang dịch — đoạn {current}/{total} (đã chạy {elapsed:.0f}s)...")
                progress_bar.progress(min(pct, 0.95))
            elif stage == "build":
                status.info("📝 Đang xuất file Word song ngữ...")
                progress_bar.progress(0.97)

        try:
            translate_pdf_to_bilingual_docx(
                pdf_path=pdf_path,
                output_path=out_path,
                progress_cb=progress_cb,
                enable_ocr=enable_ocr,
            )
            progress_bar.progress(1.0)
            status.success(f"✅ Hoàn tất trong {time.time() - start_time:.0f} giây!")

            with open(out_path, "rb") as f:
                data = f.read()

            st.download_button(
                label="⬇️ Tải file Word song ngữ",
                data=data,
                file_name=out_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
            st.info(
                "ℹ️ Bản dịch tiếng Việt hiển thị **in nghiêng, màu xanh đậm** ngay dưới mỗi đoạn "
                "tiếng Anh để dễ phân biệt. Vì là dịch máy miễn phí, bạn nên **đọc lại và chỉnh sửa** "
                "trước khi dùng chính thức, đặc biệt các đoạn có ghi chú \"cần kiểm tra lại\"."
            )
        except Exception as e:
            status.error(f"❌ Lỗi: {e}")
            st.exception(e)

st.markdown("---")
with st.expander("📋 Lưu ý khi sử dụng"):
    st.markdown(
        """
- Đây là **dịch máy** (Google Translate miễn phí) — không "hiểu" ngữ cảnh sâu như AI cao cấp,
  nên câu dài/phức tạp hoặc đoạn có nhiều ý lồng nhau có thể dịch chưa tự nhiên. Hãy đọc lại
  trước khi dùng cho mục đích chính thức (nộp hồ sơ, xuất bản...).
- Thuật ngữ dược/quy chế phổ biến (GMP, API, CAPA, OOS, pharmacovigilance...) được tự động
  sửa lại theo bộ thuật ngữ chuẩn trong `core/glossary.py` nếu máy dịch bỏ sót — bạn có thể
  chỉnh sửa file này để bổ sung thêm.
- Bảng biểu được tái tạo thành bảng Word thật; nếu PDF gốc dùng bảng không viền/không kẻ,
  công cụ có thể nhận nhầm thành đoạn văn thường — kiểm tra lại phần này sau khi dịch.
- Hình ảnh trong PDF được giữ nguyên. Nếu bật tùy chọn OCR, chữ trong ảnh/trang scan sẽ được
  tự động nhận diện (Tesseract OCR, mặc định ngôn ngữ tiếng Anh) và dịch, hiển thị ngay dưới ảnh
  gốc. OCR không phải lúc nào cũng chính xác 100% — với ảnh mờ, chữ viết tay, hoặc font lạ, kết
  quả nhận diện có thể sai sót; hãy đối chiếu lại với ảnh gốc trước khi dùng chính thức.
- Nếu dịch vụ Google Translate tạm thời giới hạn tốc độ (do dùng nhiều cùng lúc), công cụ sẽ
  tự động chờ và thử lại — tài liệu dài có thể mất vài phút, cứ để tab mở, đừng đóng giữa chừng.
        """
    )
