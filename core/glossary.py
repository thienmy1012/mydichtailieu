# -*- coding: utf-8 -*-
"""
glossary.py
Thuật ngữ chuẩn cho tài liệu guideline dược phẩm quốc tế (ICH, WHO, FDA, EMA...).
Dùng để "ghim" thuật ngữ trong prompt dịch, đảm bảo nhất quán xuyên suốt tài liệu.
Người dùng có thể chỉnh sửa file này để bổ sung/thay đổi thuật ngữ theo nhu cầu.
"""

PHARMA_GLOSSARY = {
    "Active Pharmaceutical Ingredient (API)": "Dược chất / Nguyên liệu làm thuốc (API)",
    "Good Manufacturing Practice (GMP)": "Thực hành sản xuất tốt (GMP)",
    "Good Clinical Practice (GCP)": "Thực hành lâm sàng tốt (GCP)",
    "Good Laboratory Practice (GLP)": "Thực hành phòng thí nghiệm tốt (GLP)",
    "Good Distribution Practice (GDP)": "Thực hành phân phối tốt (GDP)",
    "Quality Assurance (QA)": "Đảm bảo chất lượng (QA)",
    "Quality Control (QC)": "Kiểm tra chất lượng (QC)",
    "Quality Unit": "Đơn vị chất lượng",
    "Standard Operating Procedure (SOP)": "Quy trình thao tác chuẩn (SOP)",
    "Batch Record": "Hồ sơ lô",
    "Batch Number / Lot Number": "Số lô",
    "Validation": "Thẩm định / Xác nhận giá trị sử dụng",
    "Qualification": "Đánh giá (thiết bị/hệ thống)",
    "Deviation": "Sai lệch",
    "Corrective and Preventive Action (CAPA)": "Hành động khắc phục và phòng ngừa (CAPA)",
    "Change Control": "Kiểm soát thay đổi",
    "Out of Specification (OOS)": "Ngoài giới hạn tiêu chuẩn (OOS)",
    "Stability Study": "Nghiên cứu độ ổn định",
    "Shelf Life": "Hạn sử dụng / Tuổi thọ",
    "Excipient": "Tá dược",
    "Dosage Form": "Dạng bào chế",
    "Marketing Authorization / Registration Dossier": "Hồ sơ đăng ký lưu hành",
    "Common Technical Document (CTD)": "Hồ sơ kỹ thuật chung (CTD)",
    "Pharmacovigilance": "Cảnh giác dược",
    "Adverse Event (AE)": "Biến cố bất lợi (AE)",
    "Adverse Drug Reaction (ADR)": "Phản ứng có hại của thuốc (ADR)",
    "Clinical Trial": "Thử nghiệm lâm sàng",
    "Investigational Product": "Sản phẩm nghiên cứu",
    "Sponsor": "Nhà tài trợ (thử nghiệm lâm sàng)",
    "Institutional Review Board (IRB) / Ethics Committee": "Hội đồng đạo đức",
    "Informed Consent": "Chấp thuận tham gia nghiên cứu (sau khi được thông báo)",
    "Biological Product / Biologics": "Sản phẩm sinh học",
    "Sterility": "Vô trùng / Tính vô khuẩn",
    "Contamination": "Nhiễm / Tạp nhiễm",
    "Cross-contamination": "Nhiễm chéo",
    "Traceability": "Khả năng truy xuất nguồn gốc",
    "Labelling": "Ghi nhãn / Nhãn",
    "Packaging": "Đóng gói / Bao bì",
    "Recall": "Thu hồi (sản phẩm)",
    "Audit": "Đánh giá nội bộ / Kiểm tra (audit)",
    "Inspection": "Thanh tra / Kiểm tra",
    "Regulatory Authority": "Cơ quan quản lý",
    "Manufacturer": "Nhà sản xuất",
    "Supplier": "Nhà cung cấp",
    "Specification": "Tiêu chuẩn chất lượng",
    "Impurity": "Tạp chất",
    "Reference Standard": "Chất chuẩn đối chiếu",
    "Retention Sample": "Mẫu lưu",
    "Master Production Record": "Hồ sơ sản xuất gốc",
    "Risk Assessment": "Đánh giá rủi ro",
    "Risk Management": "Quản lý rủi ro",
}


def glossary_as_prompt_block() -> str:
    lines = ["THUẬT NGỮ CHUẨN (phải dùng nhất quán trong toàn bộ tài liệu):"]
    for en, vi in PHARMA_GLOSSARY.items():
        lines.append(f'- "{en}" -> "{vi}"')
    return "\n".join(lines)
