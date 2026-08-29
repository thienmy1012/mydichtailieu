# -*- coding: utf-8 -*-
"""
cli.py
Dich 1 file PDF hoac ca thu muc PDF sang Word song ngu, tu dong lenh (khong can mo web).
MIEN PHI - khong can API key.

Vi du:
    python cli.py document.pdf
    python cli.py ./ho_so_input/ --output-dir ./ho_so_output/
"""
import argparse
import os
import sys
import time

from core.pipeline import translate_pdf_to_bilingual_docx


def process_one(pdf_path: str, output_dir: str):
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    out_path = os.path.join(output_dir, f"{base}_song_ngu.docx")
    print(f"\n=== Đang xử lý: {pdf_path} ===")
    start = time.time()

    def progress_cb(stage, current, total):
        if stage == "extract":
            print("  [1/3] Trích xuất cấu trúc PDF...")
        elif stage == "translate":
            print(f"  [2/3] Đang dịch đoạn {current}/{total}...", end="\r")
        elif stage == "build":
            print("\n  [3/3] Xuất file Word song ngữ...")

    try:
        translate_pdf_to_bilingual_docx(
            pdf_path=pdf_path,
            output_path=out_path,
            progress_cb=progress_cb,
        )
        print(f"  ✅ Xong ({time.time() - start:.0f}s) → {out_path}")
    except Exception as e:
        print(f"  ❌ Lỗi khi xử lý {pdf_path}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Dịch PDF tiếng Anh → Word song ngữ Anh-Việt (miễn phí)")
    parser.add_argument("input", help="File PDF hoặc thư mục chứa nhiều file PDF")
    parser.add_argument("--output-dir", default="./output", help="Thư mục lưu file kết quả (mặc định: ./output)")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if os.path.isdir(args.input):
        pdf_files = [os.path.join(args.input, f) for f in sorted(os.listdir(args.input)) if f.lower().endswith(".pdf")]
        if not pdf_files:
            print(f"Không tìm thấy file PDF nào trong {args.input}")
            sys.exit(1)
        print(f"Tìm thấy {len(pdf_files)} file PDF. Bắt đầu dịch lần lượt...")
        for p in pdf_files:
            process_one(p, args.output_dir)
    else:
        process_one(args.input, args.output_dir)

    print("\n🎉 Hoàn tất toàn bộ.")


if __name__ == "__main__":
    main()
