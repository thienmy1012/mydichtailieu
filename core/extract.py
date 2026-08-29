"""
extract.py
Trich xuat noi dung PDF thanh danh sach cac "block" co cau truc:
  - heading (voi level 1/2/3 dua tren kich thuoc font)
  - paragraph (van ban thuong, giu bold/italic o muc run)
  - list_item (danh sach danh so / gach dau dong)
  - table (danh sach hang/cot)
  - image (placeholder, khong dich chu trong anh)

Muc tieu: giu cau truc de sau nay ghep song ngu va xuat docx dung dinh dang.
"""
import io
import pymupdf as fitz
import re
import statistics
from dataclasses import dataclass, field
from typing import List, Optional

try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

# Ngon ngu OCR mac dinh: tai lieu chu yeu la tieng Anh.
# Neu tai lieu co ca tieng Viet trong anh, doi thanh "eng+vie"
# (yeu cau da cai goi ngon ngu tesseract-ocr-vie, xem packages.txt).
OCR_LANG = "eng"
# Nguong dien tich toi thieu (px) de coi mot vung anh la "dang OCR duoc"
# (tranh OCR cac icon/logo nho, lang phi thoi gian).
OCR_MIN_PIXELS = 40 * 40


@dataclass
class Run:
    text: str
    bold: bool = False
    italic: bool = False


@dataclass
class Block:
    type: str  # "heading" | "paragraph" | "list_item" | "table" | "image" | "page_break"
    runs: List[Run] = field(default_factory=list)
    level: int = 0  # heading level (1-3), or list indent level
    page: int = 1
    table_rows: Optional[List[List[str]]] = None  # for type == "table"
    list_marker: Optional[str] = None  # "1." / "-" / "a)" etc.
    translated_text: Optional[str] = None  # dien sau khi dich (paragraph/heading/list_item)
    translated_table_rows: Optional[List[List[str]]] = None  # dien sau khi dich (table)
    image_bytes: Optional[bytes] = None  # anh PNG da render (cho type == "image")
    image_width_in: float = 0.0
    image_height_in: float = 0.0

    @property
    def text(self) -> str:
        return "".join(r.text for r in self.runs)


LIST_MARKER_RE = re.compile(r"^\s*((\d{1,3}[.)])|([a-zA-Z][.)])|([\u2022\-\*]))\s+")


def _span_is_bold(span) -> bool:
    flags = span.get("flags", 0)
    font = span.get("font", "").lower()
    return bool(flags & 2**4) or "bold" in font


def _span_is_italic(span) -> bool:
    flags = span.get("flags", 0)
    font = span.get("font", "").lower()
    return bool(flags & 2**1) or "italic" in font or "oblique" in font


def _collect_body_font_size(doc) -> float:
    """Uoc luong kich thuoc font pho bien nhat (= than van ban) de suy ra heading."""
    sizes = []
    for page in doc:
        d = page.get_text("dict")
        for block in d.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    t = span.get("text", "").strip()
                    if t:
                        sizes.append(round(span["size"], 1))
    if not sizes:
        return 10.0
    return statistics.median(sizes)


def _heading_level(size: float, body_size: float) -> int:
    ratio = size / body_size if body_size else 1
    if ratio >= 1.45:
        return 1
    if ratio >= 1.25:
        return 2
    if ratio >= 1.1:
        return 3
    return 0


def _ocr_image_bytes(image_bytes: bytes) -> str:
    """
    Dung Tesseract OCR de nhan dien chu trong 1 anh (bytes PNG).
    Tra ve chuoi rong neu: chua cai Tesseract, anh qua nho, hoac khong tim thay chu nao.
    Loi khi OCR (anh hong, Tesseract thieu ngon ngu...) duoc bo qua am tham de khong
    lam gian doan qua trinh dich toan bo tai lieu.
    """
    if pytesseract is None or Image is None:
        return ""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.width * img.height < OCR_MIN_PIXELS:
            return ""
        text = pytesseract.image_to_string(img, lang=OCR_LANG)
        return text.strip()
    except Exception:
        return ""


def _split_ocr_paragraphs(text: str) -> List[str]:
    """Cat chuoi ket qua OCR thanh cac doan van dua theo dong trong (ngan cach doan)."""
    if not text:
        return []
    raw_paragraphs = re.split(r"\n\s*\n", text)
    paragraphs = []
    for p in raw_paragraphs:
        p_clean = " ".join(line.strip() for line in p.splitlines() if line.strip())
        # bo qua cac doan qua ngan (1-2 ky tu) - thuong la nhieu OCR (dau cham, ky hieu la)
        if len(p_clean) >= 3:
            paragraphs.append(p_clean)
    return paragraphs


def extract_tables_per_page(page):
    """Dung PyMuPDF table finder. Tra ve list cac (bbox, rows)."""
    tables = []
    try:
        finder = page.find_tables()
        for t in finder.tables:
            rows = t.extract()
            # extract() tra ve list[list[str|None]]
            clean_rows = [[(c or "").strip() for c in row] for row in rows]
            tables.append((t.bbox, clean_rows))
    except Exception:
        pass
    return tables


def _bbox_overlaps(bbox, y0, y1):
    tx0, ty0, tx1, ty1 = bbox
    return not (ty1 < y0 or ty0 > y1)


def extract_pdf_structure(pdf_path: str, enable_ocr: bool = True) -> List[Block]:
    """
    enable_ocr: neu True (mac dinh), moi vung anh trich xuat tu PDF (ke ca trang scan
    toan trang, vi PyMuPDF cung nhan dien do la 1 khoi anh) se duoc chay qua Tesseract OCR
    de nhan dien chu. Chu nhan dien duoc se them vao ngay sau anh do, duoi dang doan van
    binh thuong -> se duoc dich va hien trong file docx cung nhu moi doan van khac,
    trong khi anh goc van duoc giu nguyen phia tren de doi chieu.
    """
    doc = fitz.open(pdf_path)
    body_size = _collect_body_font_size(doc)
    blocks: List[Block] = []

    for page_index, page in enumerate(doc):
        page_num = page_index + 1
        tables = extract_tables_per_page(page)
        used_table_bboxes = []

        d = page.get_text("dict")
        page_blocks = d.get("blocks", [])
        # sort by vertical position to keep reading order
        page_blocks.sort(key=lambda b: (b.get("bbox", [0, 0, 0, 0])[1]))

        for pb in page_blocks:
            if pb.get("type") == 1:
                # image block: render vung bbox nay thanh PNG de nhung nguyen vao docx
                bbox = pb.get("bbox", [0, 0, 0, 0])
                img_block = Block(type="image", page=page_num)
                try:
                    clip = fitz.Rect(bbox)
                    if clip.width > 2 and clip.height > 2:
                        pix = page.get_pixmap(clip=clip, dpi=150)
                        img_block.image_bytes = pix.tobytes("png")
                        img_block.image_width_in = clip.width / 72.0
                        img_block.image_height_in = clip.height / 72.0
                except Exception:
                    pass
                blocks.append(img_block)

                # OCR: neu anh co chua chu (vi du trang scan, anh chup tai lieu...),
                # nhan dien chu va them thanh (cac) doan van ngay sau anh de dich binh thuong.
                if enable_ocr and img_block.image_bytes:
                    ocr_text = _ocr_image_bytes(img_block.image_bytes)
                    for para in _split_ocr_paragraphs(ocr_text):
                        blocks.append(Block(type="paragraph", runs=[Run(text=para)], page=page_num))
                continue

            bbox = pb.get("bbox", [0, 0, 0, 0])
            y0, y1 = bbox[1], bbox[3]

            # neu block nay nam trong vung cua 1 bang da phat hien -> bo qua (se xu ly rieng)
            inside_table = False
            for tbbox, rows in tables:
                if _bbox_overlaps(tbbox, y0, y1):
                    inside_table = True
                    if tbbox not in used_table_bboxes:
                        used_table_bboxes.append(tbbox)
                        blocks.append(Block(type="table", table_rows=rows, page=page_num))
                    break
            if inside_table:
                continue

            lines = pb.get("lines", [])
            if not lines:
                continue

            # gop cac line lai thanh 1 "paragraph" block dua tren khoang cach dong
            runs: List[Run] = []
            max_size = 0.0
            raw_text_parts = []
            for line in lines:
                for span in line.get("spans", []):
                    txt = span.get("text", "")
                    if not txt:
                        continue
                    raw_text_parts.append(txt)
                    runs.append(Run(
                        text=txt,
                        bold=_span_is_bold(span),
                        italic=_span_is_italic(span),
                    ))
                    max_size = max(max_size, span.get("size", body_size))
                runs.append(Run(text=" "))  # noi cac dong trong cung block bang khoang trang

            full_text = "".join(raw_text_parts).strip()
            if not full_text:
                continue

            level = _heading_level(max_size, body_size)
            list_match = LIST_MARKER_RE.match(full_text)

            if level > 0 and len(full_text) < 200:
                blocks.append(Block(type="heading", runs=runs, level=level, page=page_num))
            elif list_match:
                marker = list_match.group(0).strip()
                blocks.append(Block(type="list_item", runs=runs, list_marker=marker, page=page_num))
            else:
                blocks.append(Block(type="paragraph", runs=runs, page=page_num))

        blocks.append(Block(type="page_break", page=page_num))

    doc.close()
    return blocks


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "sample_pharma_guideline.pdf"
    result = extract_pdf_structure(path)
    for b in result:
        if b.type == "table":
            print(f"[TABLE p{b.page}] {b.table_rows}")
        elif b.type == "page_break":
            pass
        elif b.type == "image":
            print(f"[IMAGE p{b.page}]")
        else:
            print(f"[{b.type.upper()} L{b.level} p{b.page}] {b.text[:100]}")
