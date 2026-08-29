# -*- coding: utf-8 -*-
"""
translate.py
Dich MIEN PHI, KHONG can API key, KHONG can dang ky tai khoan nao.

Co che:
- Dung Google Translate (qua thu vien mo nguon mo `deep-translator`, goi toi endpoint dich
  cong khai cua Google) - hoan toan mien phi, khong gioi han cung, nhung co the bi Google
  tam thoi gioi han toc do (rate limit) neu goi qua nhanh/qua nhieu -> code tu dong cho va
  thu lai.
- Sau khi dich xong tung doan, ap dung "hau xu ly thuat ngu" (glossary post-processing):
  neu ban goc co chua thuat ngu/viet tat chuan trong core/glossary.py ma ban dich con sot
  lai nguyen tieng Anh (may dich khong dich duoc thuat ngu chuyen nganh), tu dong thay bang
  cum tu tieng Viet chuan de dam bao nhat quan thuat ngu duoc pham.

LUU Y VE CHAT LUONG: day la dich may thuan tuy (khong co "hieu ngu canh" nhu dich bang LLM),
nen voi cau dai/phuc tap hoac doan van nhieu y, ban dich co the cung, thieu tu nhien, hoac
doi cho o mot so truong hop. Nguoi dung nen ra soat lai truoc khi dung chinh thuc, dac biet
voi noi dung phap ly/ky thuat quan trong.
"""
import re
import time
from dataclasses import dataclass
from typing import List, Dict, Optional, Callable

from .extract import Block
from .glossary import PHARMA_GLOSSARY

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

MAX_CHARS_PER_CALL = 4500  # gioi han an toan cho 1 lan goi Google Translate free
UNCERTAIN_MARK = " [MÁY DỊCH — cần kiểm tra lại]"


@dataclass
class TranslatableUnit:
    uid: int
    source_text: str
    translated_text: Optional[str] = None


def _split_long_text(text: str, max_chars: int = MAX_CHARS_PER_CALL) -> List[str]:
    """Cat van ban dai thanh nhieu doan nho hon gioi han ky tu, uu tien cat o dau cau."""
    if len(text) <= max_chars:
        return [text]
    parts = []
    remaining = text
    while len(remaining) > max_chars:
        cut = remaining.rfind(". ", 0, max_chars)
        if cut == -1:
            cut = max_chars
        else:
            cut += 1
        parts.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def _apply_glossary_postprocess(source_text: str, translated_text: str) -> str:
    """Neu nguon co thuat ngu chuan va ban dich con sot nguyen tieng Anh, thay bang cum tu VI chuan."""
    result = translated_text
    for en_term, vi_term in PHARMA_GLOSSARY.items():
        # lay phan "loi" cua thuat ngu (bo phan trong ngoac neu co), vi du
        # "Active Pharmaceutical Ingredient (API)" -> can kiem tra ca cum day du lan tu viet tat "API"
        candidates = [en_term]
        m = re.search(r"\(([^)]+)\)\s*$", en_term)
        if m:
            candidates.append(m.group(1))  # phan viet tat, vd "API"
            candidates.append(en_term[:m.start()].strip())  # phan day du, vd "Active Pharmaceutical Ingredient"

        if not any(c.lower() in source_text.lower() for c in candidates):
            continue

        for c in candidates:
            if len(c) < 2:
                continue
            pattern = re.compile(r"(?<![A-Za-zÀ-ỹ])" + re.escape(c) + r"(?![A-Za-zÀ-ỹ])", re.IGNORECASE)
            if pattern.search(result):
                result = pattern.sub(vi_term, result, count=1)
                break
    return result


class FreeTranslator:
    """Dich mien phi bang Google Translate (khong can API key)."""

    def __init__(self, source_lang: str = "en", target_lang: str = "vi",
                 max_retries: int = 4, base_delay: float = 2.0):
        if GoogleTranslator is None:
            raise RuntimeError(
                "Chưa cài package 'deep-translator'. Chạy: pip install deep-translator"
            )
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.max_retries = max_retries
        self.base_delay = base_delay
        self._client = GoogleTranslator(source=source_lang, target=target_lang)

    def _translate_one(self, text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        parts = _split_long_text(text)
        translated_parts = []
        for part in parts:
            translated_parts.append(self._translate_with_retry(part))
            time.sleep(0.15)  # giai tan toc do goi, tranh bi Google gioi han
        return " ".join(translated_parts)

    def _translate_with_retry(self, text: str) -> str:
        last_err = None
        for attempt in range(self.max_retries):
            try:
                result = self._client.translate(text)
                if result:
                    return result
                last_err = RuntimeError("Kết quả dịch rỗng")
            except Exception as e:
                last_err = e
            delay = self.base_delay * (2 ** attempt)
            time.sleep(delay)
        return text + UNCERTAIN_MARK  # khong dich duoc -> giu nguyen goc + danh dau de nguoi dung tu dich

    def translate_units(self, units: List[TranslatableUnit], progress_cb: Optional[Callable] = None) -> None:
        total = len(units)
        for i, u in enumerate(units):
            raw = self._translate_one(u.source_text)
            u.translated_text = _apply_glossary_postprocess(u.source_text, raw)
            if progress_cb:
                progress_cb(i + 1, total)


def blocks_to_units(blocks: List[Block]):
    """
    Chuyen danh sach Block thanh danh sach TranslatableUnit de dich.
    Bang duoc "phang hoa": moi o (cell) la 1 unit rieng, gan voi (block_index, row, col).
    Tra ve (units, uid_map) trong do uid_map[uid] = (block_index, row_or_None, col_or_None)
    """
    units = []
    uid_map = {}
    uid_counter = 0

    for bi, b in enumerate(blocks):
        if b.type in ("heading", "paragraph", "list_item"):
            txt = b.text.strip()
            if not txt:
                continue
            units.append(TranslatableUnit(uid=uid_counter, source_text=txt))
            uid_map[uid_counter] = (bi, None, None)
            uid_counter += 1
        elif b.type == "table" and b.table_rows:
            for ri, row in enumerate(b.table_rows):
                for ci, cell in enumerate(row):
                    cell_txt = (cell or "").strip()
                    if not cell_txt:
                        continue
                    units.append(TranslatableUnit(uid=uid_counter, source_text=cell_txt))
                    uid_map[uid_counter] = (bi, ri, ci)
                    uid_counter += 1
    return units, uid_map


def apply_translations(blocks: List[Block], units: List[TranslatableUnit], uid_map: Dict[int, tuple]) -> None:
    """Ghi ket qua dich tro lai vao cac Block (in-place)."""
    for u in units:
        bi, ri, ci = uid_map[u.uid]
        b = blocks[bi]
        if ri is None:
            b.translated_text = u.translated_text or ""
        else:
            if b.translated_table_rows is None:
                b.translated_table_rows = [[""] * len(row) for row in b.table_rows]
            b.translated_table_rows[ri][ci] = u.translated_text or ""
