"""
Module Xuất File Word (.docx) Chuẩn Hành Chính cho Tập đoàn Kim Long Phát
Bao gồm:
- Option 1: Biên bản Cuộc họp Nội bộ Chuẩn Hành chính KLP
- Option 2: Biên bản Làm việc & Phân tích Đàm phán Đối tác (Hỗ trợ bản nội bộ mật & bản gửi đối tác)
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from app.config import settings

def set_cell_background(cell, fill_hex="F2F2F2"):
    """Đặt màu nền cho ô trong bảng docx"""
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Đặt padding cho ô trong bảng"""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="B0B0B0", sz="4", val="single"):
    """Thêm đường viền bảng chuyên nghiệp"""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        tblBorders = OxmlElement('w:tblBorders')
        for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            border = OxmlElement(f'w:{border_name}')
            border.set(qn('w:val'), val)
            border.set(qn('w:sz'), sz)
            border.set(qn('w:space'), '0')
            border.set(qn('w:color'), color)
            tblBorders.append(border)
        tblPr[0].append(tblBorders)

class DocxExporter:
    def __init__(self):
        self.output_dir = settings.OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def _set_default_font(self, doc):
        """Cấu hình font Times New Roman chuẩn hành chính"""
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Times New Roman'
        font.size = Pt(12)
        font.color.rgb = RGBColor(30, 30, 30)

    def export_option_1(self, meeting_info: Dict[str, Any], analysis: Dict[str, Any], transcripts: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Xuất Mẫu Biên bản Chuẩn - Option 1: Họp Nội Bộ Tập Đoàn Kim Long Phát
        """
        doc = docx.Document()
        self._set_default_font(doc)

        # Căn lề chuẩn văn bản: Top 2cm, Bottom 2cm, Left 2.5cm, Right 2cm
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(0.8)

        # 1. Header 2 bên: Thông tin công ty & Quốc hiệu tiêu ngữ
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False

        left_cell = header_table.cell(0, 0)
        right_cell = header_table.cell(0, 1)

        p_left = left_cell.paragraphs[0]
        p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p_left.add_run("CÔNG TY CỔ PHẦN TẬP ĐOÀN\nKIM LONG PHÁT\n")
        r1.bold = True
        r1.font.size = Pt(11)
        doc_num = meeting_info.get("doc_number", f"{datetime.now().strftime('%d%m')}/2026/BBH-KLP")
        r2 = p_left.add_run(f"Số: {doc_num}")
        r2.italic = True
        r2.font.size = Pt(10)

        p_right = right_cell.paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p_right.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n")
        r3.bold = True
        r3.font.size = Pt(11)
        today_str = datetime.now().strftime("ngày %d tháng %m năm %Y")
        r4 = p_right.add_run(f"TP. Hồ Chí Minh, {today_str}")
        r4.italic = True
        r4.font.size = Pt(10)

        doc.add_paragraph()  # khoảng cách

        # 2. Tiêu đề Biên bản
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_title = p_title.add_run("BIÊN BẢN CUỘC HỌP NỘI BỘ\n")
        r_title.bold = True
        r_title.font.size = Pt(14)
        
        meeting_title = analysis.get("meeting_title") or meeting_info.get("title", "Cuộc họp Giao ban Triển khai Kế hoạch Quý 4")
        r_sub = p_title.add_run(f"Về việc: {meeting_title}")
        r_sub.bold = True
        r_sub.italic = True
        r_sub.font.size = Pt(12)

        # 3. PHẦN I. THÔNG TIN CHUNG & THÀNH PHẦN THAM DỰ
        h1 = doc.add_paragraph()
        r_h1 = h1.add_run("I. THÔNG TIN CHUNG & THÀNH PHẦN THAM DỰ")
        r_h1.bold = True
        r_h1.font.size = Pt(12)

        info_table = doc.add_table(rows=5, cols=2)
        info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(info_table)

        participants_list = meeting_info.get("participants") or [
            "1. Ông Trần Văn Hùng - Phó Tổng Giám Đốc",
            "2. Ông Đặng Minh Trí - Trưởng Phòng Kinh Doanh",
            "3. Ông Phạm Đức Huy - Trưởng Phòng Kỹ Thuật",
            "4. Bà Nguyễn Mai Phương - Kế toán Trưởng"
        ]

        info_rows = [
            ("1. Thời gian & Hình thức:", f"Bắt đầu: {meeting_info.get('start_time', '09:00')} - Kết thúc: {meeting_info.get('end_time', datetime.now().strftime('%H:%M'))}, {datetime.now().strftime('%d/%m/%Y')} | Hình thức: {meeting_info.get('meeting_mode', 'Trực tiếp kết hợp Online Zoom')}"),
            ("2. Chủ trì cuộc họp:", meeting_info.get("chairperson", "Sếp Trực - TGĐ")),
            ("3. Thư ký cuộc họp:", meeting_info.get("secretary", "Bà Lê Thu Thảo - Thư ký Ban TGĐ")),
            ("4. Thành phần tham dự:", "\n".join(participants_list)),
            ("5. Vắng mặt (nếu có):", meeting_info.get("absentees", "Không có (Đầy đủ)"))
        ]

        for idx, (label, val) in enumerate(info_rows):
            c0 = info_table.cell(idx, 0)
            c1 = info_table.cell(idx, 1)
            c0.width = Inches(2.2)
            c1.width = Inches(4.5)
            set_cell_background(c0, "F5F7FA")
            set_cell_margins(c0)
            set_cell_margins(c1)
            p0 = c0.paragraphs[0]
            r = p0.add_run(label)
            r.bold = True
            p1 = c1.paragraphs[0]
            p1.add_run(val)

        doc.add_paragraph()

        # 4. PHẦN II. NỘI DUNG CHỈ ĐẠO & PHÂN TÍCH PHÁT BIỂU
        h2 = doc.add_paragraph()
        r_h2 = h2.add_run("II. NỘI DUNG CHỈ ĐẠO & PHÂN TÍCH PHÁT BIỂU CỦA CÁC BỘ PHẬN")
        r_h2.bold = True

        # 1. Tóm tắt mục tiêu
        doc.add_paragraph().add_run("1. Tóm tắt mục tiêu trọng tâm cuộc họp:").bold = True
        goals = analysis.get("summary_goals") or []
        if goals:
            for g in goals:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(g)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa ghi nhận mục tiêu cụ thể.")
            r.italic = True

        # 2. Ý kiến chỉ đạo của Chủ trì
        doc.add_paragraph().add_run("2. Ý kiến chỉ đạo của Chủ trì (Ban Lãnh Đạo):").bold = True
        directions = analysis.get("leader_directions") or []
        if directions:
            for d in directions:
                p = doc.add_paragraph(style='List Bullet')
                p.add_run(d)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa ghi nhận ý kiến chỉ đạo cụ thể.")
            r.italic = True

        # 3. Báo cáo & Thảo luận phòng ban
        doc.add_paragraph().add_run("3. Báo cáo & Thảo luận của các Phòng ban / Cá nhân:").bold = True
        dept_reports = analysis.get("department_reports") or []
        if dept_reports:
            for rep in dept_reports:
                p = doc.add_paragraph()
                r_spk = p.add_run(f"• {rep.get('speaker', '')}: ")
                r_spk.bold = True
                p.add_run(rep.get("content", ""))
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa ghi nhận báo cáo phòng ban phát sinh.")
            r.italic = True

        # Bảng Phân tích Thoại & Đánh giá mức độ đóng góp
        doc.add_paragraph().add_run("Bảng Phân tích Thoại & Đánh giá Mức độ Đóng góp:").bold = True
        speech_data = analysis.get("speech_analytics") or []

        sp_table = doc.add_table(rows=1, cols=5)
        sp_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(sp_table)

        sp_headers = ["Người tham gia", "Tỷ lệ (%)", "Luận điểm chính đã phát biểu", "Thái độ thảo luận", "Đánh giá đóng góp"]
        for i, h_text in enumerate(sp_headers):
            cell = sp_table.cell(0, i)
            set_cell_background(cell, "2B4C7E")
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(h_text)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

        if speech_data:
            for item in speech_data:
                row_cells = sp_table.add_row().cells
                row_cells[0].paragraphs[0].add_run(str(item.get("speaker", ""))).bold = True
                row_cells[1].paragraphs[0].add_run(f"{item.get('ratio_percent', 0)}%")
                row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[2].paragraphs[0].add_run(str(item.get("key_points", "")))
                row_cells[3].paragraphs[0].add_run(str(item.get("attitude", "")))
                row_cells[4].paragraphs[0].add_run(str(item.get("contribution_eval", "")))
                for c in row_cells:
                    set_cell_margins(c)
                    c.paragraphs[0].runs[0].font.size = Pt(10)
        else:
            row_cells = sp_table.add_row().cells
            row_cells[0].merge(row_cells[4])
            p_empty = row_cells[0].paragraphs[0]
            p_empty.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_emp = p_empty.add_run("Chưa có dữ liệu thống kê phát biểu.")
            r_emp.italic = True
            set_cell_margins(row_cells[0])

        doc.add_paragraph()

        # 5. PHẦN III. ĐÁNH GIÁ KẾT QUẢ CUỘC HỌP
        h3 = doc.add_paragraph()
        r_h3 = h3.add_run("III. ĐÁNH GIÁ KẾT QUẢ CUỘC HỌP")
        r_h3.bold = True

        p_agreed = doc.add_paragraph()
        p_agreed.add_run("✅ Các vấn đề ĐÃ THỐNG NHẤT & CHỐT phương án:").bold = True
        agreed_list = analysis.get("agreed_issues") or []
        if agreed_list:
            for a in agreed_list:
                doc.add_paragraph(style='List Bullet').add_run(a)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa có quyết định được chốt.")
            r.italic = True

        p_pending = doc.add_paragraph()
        p_pending.add_run("Các vấn đề CÒN TỒN ĐỌNG / CHƯA GIẢI QUYẾT:").bold = True
        pending_list = analysis.get("pending_issues") or []
        if pending_list:
            for pe in pending_list:
                doc.add_paragraph(style='List Bullet').add_run(pe)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Không có vấn đề vướng mắc tồn đọng.")
            r.italic = True

        # Bookmark nóng nếu có
        bookmarks = analysis.get("hot_bookmarks", [])
        if bookmarks:
            p_bm = doc.add_paragraph()
            p_bm.add_run("Các mốc Trọng tâm (Bookmark) được Thư ký ghi nhận:").bold = True
            for bm in bookmarks:
                doc.add_paragraph(style='List Bullet').add_run(f"[{bm.get('timestamp', '')}] {bm.get('speaker', '')}: \"{bm.get('content', '')}\"")

        doc.add_paragraph()

        # 6. PHẦN IV. BẢNG PHÂN CÔNG CÔNG VIỆC (ACTION ITEMS)
        h4 = doc.add_paragraph()
        r_h4 = h4.add_run("IV. BẢNG PHÂN CÔNG CÔNG VIỆC SAU CUỘC HỌP (ACTION ITEMS)")
        r_h4.bold = True

        act_table = doc.add_table(rows=1, cols=6)
        act_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(act_table)

        act_headers = ["STT", "Đầu việc cụ thể cần thực hiện", "Người phụ trách (PIC)", "Bộ phận phối hợp", "Thời hạn (Deadline)", "KPI / Kết quả đầu ra"]
        col_widths = [Inches(0.5), Inches(2.2), Inches(1.2), Inches(1.0), Inches(1.0), Inches(1.3)]
        
        for i, h_text in enumerate(act_headers):
            cell = act_table.cell(0, i)
            cell.width = col_widths[i]
            set_cell_background(cell, "2B4C7E")
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(h_text)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

        action_items = analysis.get("action_items") or []

        if action_items:
            for item in action_items:
                row_cells = act_table.add_row().cells
                row_cells[0].paragraphs[0].add_run(str(item.get("stt", "")))
                row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[1].paragraphs[0].add_run(str(item.get("task", "")))
                row_cells[2].paragraphs[0].add_run(str(item.get("pic", ""))).bold = True
                row_cells[3].paragraphs[0].add_run(str(item.get("coordinating_dept", "")))
                row_cells[4].paragraphs[0].add_run(str(item.get("deadline", "")))
                row_cells[5].paragraphs[0].add_run(str(item.get("kpi", "")))
                for idx, c in enumerate(row_cells):
                    c.width = col_widths[idx]
                    set_cell_margins(c)
                    if c.paragraphs[0].runs:
                        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        else:
            row_cells = act_table.add_row().cells
            row_cells[0].merge(row_cells[5])
            p_empty = row_cells[0].paragraphs[0]
            p_empty.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_emp = p_empty.add_run("Chưa có đầu việc phân công phát sinh trong cuộc họp.")
            r_emp.italic = True
            set_cell_margins(row_cells[0])

        doc.add_paragraph()
        doc.add_paragraph()

        # 7. CHỮ KÝ 2 BÊN
        sign_table = doc.add_table(rows=2, cols=2)
        sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        c_left = sign_table.cell(0, 0)
        c_right = sign_table.cell(0, 1)

        p_sign_left = c_left.paragraphs[0]
        p_sign_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sl = p_sign_left.add_run("THƯ KÝ CUỘC HỌP\n")
        r_sl.bold = True
        r_sl_sub = p_sign_left.add_run("(Ký và ghi rõ họ tên)")
        r_sl_sub.italic = True
        r_sl_sub.font.size = Pt(10)

        p_sign_right = c_right.paragraphs[0]
        p_sign_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sr = p_sign_right.add_run("CHỦ TRÌ CUỘC HỌP\n")
        r_sr.bold = True
        r_sr_sub = p_sign_right.add_run("(Ký và ghi rõ họ tên)")
        r_sr_sub.italic = True
        r_sr_sub.font.size = Pt(10)

        # Tên người ký ở hàng 2
        p_name_left = sign_table.cell(1, 0).paragraphs[0]
        p_name_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name_left.add_run(f"\n\n\n\n{meeting_info.get('secretary', 'Bà Lê Thu Thảo')}").bold = True

        p_name_right = sign_table.cell(1, 1).paragraphs[0]
        p_name_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_name_right.add_run(f"\n\n\n\n{meeting_info.get('chairperson', 'Bà Phan Thị Phát')}").bold = True

        # V. PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ BẢN GHI ÂM
        if transcripts and len(transcripts) > 0:
            doc.add_page_break()
            p_app_h = doc.add_paragraph()
            p_app_h.paragraph_format.space_before = Pt(12)
            p_app_h.paragraph_format.space_after = Pt(4)
            r_app_h = p_app_h.add_run("V. PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ BẢN GHI ÂM")
            r_app_h.bold = True
            r_app_h.font.size = Pt(12)
            r_app_h.font.color.rgb = RGBColor(21, 62, 117)

            p_app_desc = doc.add_paragraph()
            p_app_desc.paragraph_format.space_after = Pt(8)
            r_desc = p_app_desc.add_run("(Toàn bộ lời nói của các thành viên tham gia được bóc tách chi tiết theo tiến trình cuộc họp)")
            r_desc.italic = True
            r_desc.font.size = Pt(10)
            r_desc.font.color.rgb = RGBColor(100, 100, 100)

            t_table = doc.add_table(rows=1, cols=4)
            t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            t_table.autofit = False
            set_table_borders(t_table)

            col_widths = [Inches(0.5), Inches(1.1), Inches(2.2), Inches(3.3)]
            for i, w in enumerate(col_widths):
                t_table.columns[i].width = w

            hdr = t_table.rows[0].cells
            hdr_titles = ["STT", "Thời gian", "Người phát biểu", "Lời phát biểu nguyên văn"]
            for i, t in enumerate(hdr_titles):
                hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = hdr[i].paragraphs[0].add_run(t)
                r.bold = True
                r.font.size = Pt(10)
                set_cell_background(hdr[i], "153E75")
                r.font.color.rgb = RGBColor(255, 255, 255)
                set_cell_margins(hdr[i], top=80, bottom=80, left=80, right=80)

            for idx, tr in enumerate(transcripts, 1):
                row_cells = t_table.add_row().cells
                row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[0].paragraphs[0].add_run(f"{idx:02d}").font.size = Pt(9.5)

                row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[1].paragraphs[0].add_run(tr.get("timestamp", "00:00:00")).font.size = Pt(9.5)

                spk_run = row_cells[2].paragraphs[0].add_run(tr.get("speaker", "Người nói"))
                spk_run.bold = True
                spk_run.font.size = Pt(9.5)
                if tr.get("is_bookmark"):
                    spk_run.font.color.rgb = RGBColor(180, 83, 9)

                txt_p = row_cells[3].paragraphs[0]
                txt_run = txt_p.add_run(tr.get("text", ""))
                txt_run.font.size = Pt(9.5)
                if tr.get("note"):
                    p_note = row_cells[3].add_paragraph()
                    r_note = p_note.add_run(f"-> Ghi chú: {tr.get('note')}")
                    r_note.italic = True
                    r_note.font.size = Pt(8.5)
                    r_note.font.color.rgb = RGBColor(100, 100, 100)

                for c in row_cells:
                    set_cell_margins(c, top=60, bottom=60, left=80, right=80)

        filename = f"BBH_NoiBo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        file_path = os.path.join(self.output_dir, filename)
        doc.save(file_path)
        return file_path

    def export_option_2(self, meeting_info: Dict[str, Any], analysis: Dict[str, Any], include_internal_confidential: bool = True, transcripts: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Xuất Mẫu Biên bản Chuẩn - Option 2: Họp Đối Tác & Khách Hàng
        Hỗ trợ 2 chế độ:
        - include_internal_confidential = True: Bản Đầy Đủ Lưu Hành Nội Bộ KLP (có Phần B Mật)
        - include_internal_confidential = False: Bản Gửi Cho Đối Tác Xác Nhận (chỉ có Phần A + C)
        """
        doc = docx.Document()
        self._set_default_font(doc)

        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(0.8)

        # 1. Header
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        header_table.autofit = False

        left_cell = header_table.cell(0, 0)
        right_cell = header_table.cell(0, 1)

        p_left = left_cell.paragraphs[0]
        p_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p_left.add_run("CÔNG TY CỔ PHẦN TẬP ĐOÀN\nKIM LONG PHÁT\n")
        r1.bold = True
        r1.font.size = Pt(11)
        r2 = p_left.add_run("Văn phòng Ban Tổng Giám Đốc")
        r2.italic = True
        r2.font.size = Pt(10)

        p_right = right_cell.paragraphs[0]
        p_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r3 = p_right.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM\nĐộc lập - Tự do - Hạnh phúc\n")
        r3.bold = True
        r3.font.size = Pt(11)
        today_str = datetime.now().strftime("ngày %d tháng %m năm %Y")
        r4 = p_right.add_run(f"TP. Hồ Chí Minh, {today_str}")
        r4.italic = True
        r4.font.size = Pt(10)

        doc.add_paragraph()

        # 2. Tiêu đề
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc_type_text = "BIÊN BẢN LÀM VIỆC & PHÂN TÍCH ĐÀM PHÁN ĐỐI TÁC" if include_internal_confidential else "BIÊN BẢN LÀM VIỆC VỚI ĐỐI TÁC"
        r_title = p_title.add_run(f"{doc_type_text}\n")
        r_title.bold = True
        r_title.font.size = Pt(14)
        
        proj_name = analysis.get("project_title") or meeting_info.get("project_title", "Đàm phán Hợp đồng Cung cấp Thiết bị Lọc nước Ion Kiềm")
        partner_name = analysis.get("partner_name") or meeting_info.get("partner_name", "Công ty TNHH Đầu tư & Phát triển Tân Phát Đạt")
        r_sub = p_title.add_run(f"Dự án / Nội dung: {proj_name}\nĐối tác: {partner_name}")
        r_sub.bold = True
        r_sub.italic = True
        r_sub.font.size = Pt(11)

        if include_internal_confidential:
            p_conf = doc.add_paragraph()
            p_conf.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            r_cf = p_conf.add_run("[TÀI LIỆU MẬT - LƯU HÀNH NỘI BỘ TẬP ĐOÀN KIM LONG PHÁT]")
            r_cf.bold = True
            r_cf.font.color.rgb = RGBColor(180, 0, 0)
            r_cf.font.size = Pt(10)

        # PHẦN A. NỘI DUNG LÀM VIỆC CHUNG
        hA = doc.add_paragraph()
        r_hA = hA.add_run("PHẦN A. NỘI DUNG LÀM VIỆC CHUNG (DÙNG ĐỂ ĐỐI CHIẾU & LƯU HỒ SƠ)")
        r_hA.bold = True
        r_hA.font.color.rgb = RGBColor(20, 60, 120)

        # Bảng thông tin 2 bên
        party_table = doc.add_table(rows=2, cols=2)
        party_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(party_table)

        c_a = party_table.cell(0, 0)
        c_b = party_table.cell(0, 1)
        set_cell_background(c_a, "EBF3FB")
        set_cell_background(c_b, "EBF3FB")
        set_cell_margins(c_a)
        set_cell_margins(c_b)

        c_a.paragraphs[0].add_run("ĐẠI DIỆN TẬP ĐOÀN KIM LONG PHÁT (BÊN A)").bold = True
        c_b.paragraphs[0].add_run(f"ĐẠI DIỆN ĐỐI TÁC / KHÁCH HÀNG (BÊN B)").bold = True

        p_klp = party_table.cell(1, 0).paragraphs[0]
        klp_reps = meeting_info.get("klp_reps") or [
            "• Ông Trần Văn Hùng - Phó Tổng Giám Đốc",
            "• Ông Đặng Minh Trí - Trưởng Phòng Kinh Doanh",
            f"• Thư ký ghi nhận: {meeting_info.get('secretary', 'Bà Lê Thu Thảo')}"
        ]
        p_klp.add_run("\n".join(klp_reps))

        p_ptn = party_table.cell(1, 1).paragraphs[0]
        ptn_reps = meeting_info.get("partner_reps") or [
            f"• Tên Đơn vị: {partner_name}",
            "• Ông Vũ Đình Toàn - Giám Đốc Dự Án",
            "• Bà Hoàng Thị Nga - Trưởng Phòng Mua Sắm & Đấu Thầu"
        ]
        p_ptn.add_run("\n".join(ptn_reps))
        set_cell_margins(party_table.cell(1, 0))
        set_cell_margins(party_table.cell(1, 1))

        doc.add_paragraph()

        # Mục tiêu & Thời gian
        p_time = doc.add_paragraph()
        p_time.add_run(f"• Thời gian & Địa điểm: ").bold = True
        p_time.add_run(f"{meeting_info.get('time_location', '09:30 ngày ' + datetime.now().strftime('%d/%m/%Y') + ' tại Phòng họp VIP Tập đoàn Kim Long Phát')}\n")
        p_time.add_run(f"• Mục đích buổi làm việc: ").bold = True
        p_time.add_run(meeting_info.get("meeting_purpose", "Thương thảo hợp đồng cung cấp thiết bị lọc nước ion kiềm và chốt chính sách công nợ."))

        # 1. Nhu cầu đối tác
        doc.add_paragraph().add_run("1. Nhu cầu & Yêu cầu cốt lõi của Đối tác/Khách hàng (Customer Pain Points):").bold = True
        pains = analysis.get("customer_pain_points") or []
        if pains:
            for p_item in pains:
                doc.add_paragraph(style='List Bullet').add_run(p_item)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa ghi nhận nhu cầu cụ thể của đối tác.")
            r.italic = True

        # 2. Đề xuất Kim Long Phát
        doc.add_paragraph().add_run("2. Đề xuất & Giải pháp từ phía Tập đoàn Kim Long Phát:").bold = True
        proposals = analysis.get("klp_proposals") or []
        if proposals:
            for prop in proposals:
                doc.add_paragraph(style='List Bullet').add_run(prop)
        else:
            p = doc.add_paragraph()
            r = p.add_run("Chưa ghi nhận đề xuất giải pháp cụ thể.")
            r.italic = True

        # 3. Bảng Bóc tách Thông số Thương mại
        doc.add_paragraph().add_run("3. Bảng Bóc tách Thông số Thương mại, Báo giá & Điều khoản Hợp đồng:").bold = True
        comm_table = doc.add_table(rows=1, cols=4)
        comm_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(comm_table)

        comm_headers = ["Hạng mục thương thảo", "Đề xuất của Kim Long Phát", "Phản hồi / Yêu cầu của Đối tác", "Trạng thái chốt"]
        comm_widths = [Inches(1.8), Inches(2.2), Inches(2.0), Inches(1.2)]
        for i, h_text in enumerate(comm_headers):
            cell = comm_table.cell(0, i)
            cell.width = comm_widths[i]
            set_cell_background(cell, "2B4C7E")
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(h_text)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

        comm_data = analysis.get("commercial_terms") or []

        if comm_data:
            for item in comm_data:
                row_cells = comm_table.add_row().cells
                row_cells[0].paragraphs[0].add_run(str(item.get("term_name", ""))).bold = True
                row_cells[1].paragraphs[0].add_run(str(item.get("klp_offer", "")))
                row_cells[2].paragraphs[0].add_run(str(item.get("partner_demand", "")))
                r_st = row_cells[3].paragraphs[0].add_run(str(item.get("status", "")))
                r_st.bold = True
                row_cells[3].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                for idx, c in enumerate(row_cells):
                    c.width = comm_widths[idx]
                    set_cell_margins(c)
                    if c.paragraphs[0].runs:
                        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        else:
            row_cells = comm_table.add_row().cells
            row_cells[0].merge(row_cells[3])
            p_empty = row_cells[0].paragraphs[0]
            p_empty.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_emp = p_empty.add_run("Chưa có điều khoản thương mại phát sinh.")
            r_emp.italic = True
            set_cell_margins(row_cells[0])

        doc.add_paragraph()

        # PHẦN B. PHÂN TÍCH TÂM LÝ ĐÀM PHÁN & LƯU Ý MẬT (CHỈ XUẤT NẾU include_internal_confidential)
        if include_internal_confidential:
            hB = doc.add_paragraph()
            r_hB = hB.add_run("PHẦN B. PHÂN TÍCH TÂM LÝ ĐÀM PHÁN & LƯU Ý MẬT (CHỈ LƯU HÀNH NỘI BỘ KLP)")
            r_hB.bold = True
            r_hB.font.color.rgb = RGBColor(160, 20, 20)

            conf = analysis.get("confidential_internal", {})

            # Deal Score
            deal_score = conf.get("deal_score", 7.0)
            p_score = doc.add_paragraph()
            p_score.add_run(f"1. Đánh giá Mức độ Đồng thuận & Khả năng Chốt Hợp đồng (Deal Score): ").bold = True
            r_sc = p_score.add_run(f"{deal_score}/10")
            r_sc.bold = True
            r_sc.font.size = Pt(13)
            r_sc.font.color.rgb = RGBColor(0, 120, 50) if float(deal_score) >= 7 else RGBColor(180, 0, 0)
            
            p_score.add_run(f"\nNhận định chuyên môn: {conf.get('deal_score_explanation', 'Đang theo dõi diễn biến thương thảo thực tế.')}")

            # Buying signals
            doc.add_paragraph().add_run("2. Các tín hiệu đồng thuận & Động lực hợp tác (Buying Signals):").bold = True
            buying_sigs = conf.get("buying_signals") or []
            if buying_sigs:
                for sig in buying_sigs:
                    doc.add_paragraph(style='List Bullet').add_run(sig)
            else:
                p = doc.add_paragraph()
                r = p.add_run("Chưa ghi nhận tín hiệu mua hàng nổi bật.")
                r.italic = True

            # Objections & Red flags
            doc.add_paragraph().add_run("3. Các điểm nghẽn & Rủi ro cần cảnh giác (Red Flags):").bold = True
            red_flags = conf.get("objections_and_red_flags") or []
            if red_flags:
                for red in red_flags:
                    doc.add_paragraph(style='List Bullet').add_run(red)
            else:
                p = doc.add_paragraph()
                r = p.add_run("Không phát hiện rủi ro hay phản đối lớn.")
                r.italic = True

            # Phân tích thoại từng người
            doc.add_paragraph().add_run("4. Đánh giá quan điểm & Vai trò từng nhân sự phía Đối tác:").bold = True
            speakers_ana = conf.get("partner_speakers_analysis") or []
            if speakers_ana:
                for sp_a in speakers_ana:
                    p_sp = doc.add_paragraph(style='List Bullet')
                    p_sp.add_run(f"{sp_a.get('speaker', '')} [{sp_a.get('role_category', '')}]: ").bold = True
                    p_sp.add_run(sp_a.get("assessment", ""))
            else:
                p = doc.add_paragraph()
                r = p.add_run("Đang theo dõi quan điểm phát biểu của các đại biểu đối tác.")
                r.italic = True

            doc.add_paragraph()

        # PHẦN C. KẾ HOẠCH HÀNH ĐỘNG TIẾP THEO (FOLLOW-UP PLAN)
        hC = doc.add_paragraph()
        r_hC = hC.add_run("PHẦN C. KẾ HOẠCH HÀNH ĐỘNG TIẾP THEO (FOLLOW-UP PLAN)")
        r_hC.bold = True
        r_hC.font.color.rgb = RGBColor(20, 60, 120)

        fol_table = doc.add_table(rows=1, cols=5)
        fol_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(fol_table)

        fol_headers = ["Bên thực hiện", "Công việc đã cam kết trong cuộc họp", "Người phụ trách", "Thời hạn (Deadline)", "Ghi chú ưu tiên"]
        fol_widths = [Inches(1.2), Inches(2.6), Inches(1.3), Inches(1.1), Inches(1.0)]
        for i, h_text in enumerate(fol_headers):
            cell = fol_table.cell(0, i)
            cell.width = fol_widths[i]
            set_cell_background(cell, "2B4C7E")
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(h_text)
            run.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)

        follow_data = analysis.get("follow_up_plan") or []

        if follow_data:
            for item in follow_data:
                row_cells = fol_table.add_row().cells
                row_cells[0].paragraphs[0].add_run(str(item.get("party", ""))).bold = True
                row_cells[1].paragraphs[0].add_run(str(item.get("task", "")))
                row_cells[2].paragraphs[0].add_run(str(item.get("pic", "")))
                row_cells[3].paragraphs[0].add_run(str(item.get("deadline", "")))
                r_pr = row_cells[4].paragraphs[0].add_run(str(item.get("priority", "")))
                r_pr.italic = True
                row_cells[4].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                for idx, c in enumerate(row_cells):
                    c.width = fol_widths[idx]
                    set_cell_margins(c)
                    if c.paragraphs[0].runs:
                        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        else:
            row_cells = fol_table.add_row().cells
            row_cells[0].merge(row_cells[4])
            p_empty = row_cells[0].paragraphs[0]
            p_empty.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_emp = p_empty.add_run("Chưa có kế hoạch hành động tiếp theo.")
            r_emp.italic = True
            set_cell_margins(row_cells[0])

        doc.add_paragraph()
        doc.add_paragraph()

        # CHỮ KÝ XÁC NHẬN
        sign_table = doc.add_table(rows=2, cols=2)
        sign_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        c_left = sign_table.cell(0, 0)
        c_right = sign_table.cell(0, 1)

        p_sl = c_left.paragraphs[0]
        p_sl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sl.add_run("ĐẠI DIỆN TẬP ĐOÀN KIM LONG PHÁT\n").bold = True
        p_sl.add_run("(Ký và ghi rõ họ tên)").italic = True

        p_sr = c_right.paragraphs[0]
        p_sr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_sr.add_run("ĐẠI DIỆN ĐỐI TÁC / KHÁCH HÀNG\n").bold = True
        p_sr.add_run("(Ký và ghi rõ họ tên)").italic = True

        sign_table.cell(1, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        sign_table.cell(1, 0).paragraphs[0].add_run(f"\n\n\n\n{meeting_info.get('klp_signer', 'Ông Trần Văn Hùng - Phó Tổng Giám Đốc')}").bold = True

        sign_table.cell(1, 1).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        sign_table.cell(1, 1).paragraphs[0].add_run(f"\n\n\n\n{meeting_info.get('partner_signer', 'Ông Vũ Đình Toàn - Giám Đốc Dự Án')}").bold = True

        # PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ BẢN GHI ÂM
        if transcripts and len(transcripts) > 0:
            doc.add_page_break()
            p_app_h = doc.add_paragraph()
            p_app_h.paragraph_format.space_before = Pt(12)
            p_app_h.paragraph_format.space_after = Pt(4)
            r_app_h = p_app_h.add_run("PHỤ LỤC: BĂNG GHI CHỮ THOẠI NGUYÊN VĂN BÓC TÁCH TỪ BẢN GHI ÂM ĐÀM PHÁN")
            r_app_h.bold = True
            r_app_h.font.size = Pt(12)
            r_app_h.font.color.rgb = RGBColor(21, 62, 117)

            p_app_desc = doc.add_paragraph()
            p_app_desc.paragraph_format.space_after = Pt(8)
            r_desc = p_app_desc.add_run("(Văn bản bóc tách nguyên văn toàn bộ lời nói của hai bên theo tiến trình đàm phán)")
            r_desc.italic = True
            r_desc.font.size = Pt(10)
            r_desc.font.color.rgb = RGBColor(100, 100, 100)

            t_table = doc.add_table(rows=1, cols=4)
            t_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            t_table.autofit = False
            set_table_borders(t_table)

            col_widths = [Inches(0.5), Inches(1.1), Inches(2.2), Inches(3.3)]
            for i, w in enumerate(col_widths):
                t_table.columns[i].width = w

            hdr = t_table.rows[0].cells
            hdr_titles = ["STT", "Thời gian", "Người phát biểu", "Lời phát biểu nguyên văn"]
            for i, t in enumerate(hdr_titles):
                hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = hdr[i].paragraphs[0].add_run(t)
                r.bold = True
                r.font.size = Pt(10)
                set_cell_background(hdr[i], "153E75")
                r.font.color.rgb = RGBColor(255, 255, 255)
                set_cell_margins(hdr[i], top=80, bottom=80, left=80, right=80)

            for idx, tr in enumerate(transcripts, 1):
                row_cells = t_table.add_row().cells
                row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[0].paragraphs[0].add_run(f"{idx:02d}").font.size = Pt(9.5)

                row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[1].paragraphs[0].add_run(tr.get("timestamp", "00:00:00")).font.size = Pt(9.5)

                spk_run = row_cells[2].paragraphs[0].add_run(tr.get("speaker", "Người nói"))
                spk_run.bold = True
                spk_run.font.size = Pt(9.5)
                if tr.get("is_bookmark"):
                    spk_run.font.color.rgb = RGBColor(180, 83, 9)

                txt_p = row_cells[3].paragraphs[0]
                txt_run = txt_p.add_run(tr.get("text", ""))
                txt_run.font.size = Pt(9.5)
                if tr.get("note"):
                    p_note = row_cells[3].add_paragraph()
                    r_note = p_note.add_run(f"-> Ghi chú: {tr.get('note')}")
                    r_note.italic = True
                    r_note.font.size = Pt(8.5)
                    r_note.font.color.rgb = RGBColor(100, 100, 100)

                for c in row_cells:
                    set_cell_margins(c, top=60, bottom=60, left=80, right=80)

        prefix = "BBH_DoiTac_NoiBo" if include_internal_confidential else "BBH_DoiTac_XacNhan"
        filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        file_path = os.path.join(self.output_dir, filename)
        doc.save(file_path)
        return file_path

docx_exporter = DocxExporter()
