# -*- coding: utf-8 -*-
"""
pipeline.py
Ghep 3 buoc: trich xuat PDF -> dich (MIEN PHI, khong can API key) -> xuat docx song ngu.
Day la ham duoc app.py (giao dien Streamlit) va cli.py goi toi.
"""
import os
from typing import Callable, Optional

from .extract import extract_pdf_structure
from .translate import FreeTranslator, blocks_to_units, apply_translations
from .docx_builder import build_bilingual_docx


def translate_pdf_to_bilingual_docx(
    pdf_path: str,
    output_path: str,
    progress_cb: Optional[Callable[[str, int, int], None]] = None,
    enable_ocr: bool = True,
) -> str:
    """
    progress_cb(stage: str, current: int, total: int) -> None
      stage in {"extract", "translate", "build"}
    enable_ocr: True (mac dinh) -> tu dong nhan dien chu trong anh/trang scan bang Tesseract OCR
      va dich luon phan chu do.
    """
    if progress_cb:
        progress_cb("extract", 0, 1)
    blocks = extract_pdf_structure(pdf_path, enable_ocr=enable_ocr)
    if progress_cb:
        progress_cb("extract", 1, 1)

    units, uid_map = blocks_to_units(blocks)

    translator = FreeTranslator(source_lang="en", target_lang="vi")

    def _t_progress(done, total):
        if progress_cb:
            progress_cb("translate", done, total)

    translator.translate_units(units, progress_cb=_t_progress)
    apply_translations(blocks, units, uid_map)

    if progress_cb:
        progress_cb("build", 0, 1)
    title = os.path.splitext(os.path.basename(pdf_path))[0]
    build_bilingual_docx(blocks, output_path, title=title)
    if progress_cb:
        progress_cb("build", 1, 1)

    return output_path
