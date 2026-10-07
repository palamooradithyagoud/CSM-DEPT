"""
Institutional PDF Report Generator using ReportLab.
Produces professional, institutional academic reports with dynamic headers, footers, page numbering,
and formatted data tables for Department, Section, Student, Subject, and Insights reports.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp total page count in the footer.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 810, "Department of Computer Science & Engineering — Academic Management")
            self.setStrokeColor(colors.HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)

        # Running Footer (on all pages)
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(40, 36, 555, 36)

        footer_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 24, footer_text)
        confidential_notice = "CONFIDENTIAL — Authorized College HOD / Academic Administration Use Only"
        self.drawString(40, 24, confidential_notice)
        self.restoreState()


class PDFReportGenerator:
    """Institutional PDF generation engine using ReportLab."""

    @classmethod
    def _get_styles(cls):
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12,
        )
        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#1E293B"),
        )
        body_bold = ParagraphStyle(
            "DocBodyBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A"),
        )
        table_cell = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#1E293B"),
        )
        table_cell_bold = ParagraphStyle(
            "TableCellBold",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0F172A"),
        )
        table_header = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.white,
            alignment=1, # Center
        )
        meta_label = ParagraphStyle(
            "MetaLabel",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#475569"),
        )
        meta_val = ParagraphStyle(
            "MetaVal",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#0F172A"),
        )

        return {
            "title": title_style,
            "subtitle": subtitle_style,
            "section": section_heading,
            "body": body_style,
            "body_bold": body_bold,
            "cell": table_cell,
            "cell_bold": table_cell_bold,
            "header": table_header,
            "meta_label": meta_label,
            "meta_val": meta_val,
        }

    @classmethod
    def _create_doc(cls):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=45,
        )
        return buf, doc

    @classmethod
    def _build_header_elements(cls, title, subtitle_meta, styles):
        elements = []
        elements.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", styles["meta_label"]))
        elements.append(Paragraph(title, styles["title"]))
        
        # Meta row
        now_str = datetime.utcnow().strftime("%d %B %Y, %H:%M UTC")
        meta_text = f"Generated: {now_str} &nbsp;|&nbsp; {subtitle_meta}"
        elements.append(Paragraph(meta_text, styles["subtitle"]))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=10))
        return elements

    @classmethod
    def generate_department_pdf(cls, data):
        buf, doc = cls._create_doc()
        styles = cls._get_styles()
        elements = []

        sub_meta = f"Batch: {data.get('batchName', 'All')} &nbsp;|&nbsp; Semester: {data.get('semesterName', 'All')}"
        elements.extend(cls._build_header_elements("Comprehensive Department Academic Report", sub_meta, styles))

        # 1. KPI Metric Grid
        elements.append(Paragraph("Executive Academic Overview", styles["section"]))
        kpis = data.get("kpis", {})
        kpi_table_data = [
            [
                Paragraph("Total Students", styles["meta_label"]),
                Paragraph(str(kpis.get("totalStudents", 0)), styles["body_bold"]),
                Paragraph("Average SGPA", styles["meta_label"]),
                Paragraph(str(kpis.get("averageSGPA") or "N/A"), styles["body_bold"]),
            ],
            [
                Paragraph("Average CGPA", styles["meta_label"]),
                Paragraph(str(kpis.get("averageCGPA") or "N/A"), styles["body_bold"]),
                Paragraph("Average Attendance", styles["meta_label"]),
                Paragraph(f"{kpis.get('averageAttendance')}%" if kpis.get("averageAttendance") is not None else "N/A", styles["body_bold"]),
            ],
            [
                Paragraph("Pass Percentage", styles["meta_label"]),
                Paragraph(f"{kpis.get('passPercentage')}%" if kpis.get("passPercentage") is not None else "N/A", styles["body_bold"]),
                Paragraph("Students Flagged", styles["meta_label"]),
                Paragraph(str(data.get("flaggedStudentsCount", 0)), styles["body_bold"]),
            ]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[120, 135, 130, 135])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # 2. Subject Performance Table
        elements.append(Paragraph("Subject-Wise Performance Breakdown", styles["section"]))
        subjects = data.get("subjects", [])
        if subjects:
            sub_headers = ["Code", "Subject Name", "Avg Marks", "Pass %", "Failures", "Evaluated"]
            sub_rows = [[Paragraph(h, styles["header"]) for h in sub_headers]]
            for s in subjects:
                pass_str = f"{s.get('passPercentage')}%" if s.get('passPercentage') is not None else "N/A"
                sub_rows.append([
                    Paragraph(s.get("code", ""), styles["cell_bold"]),
                    Paragraph(s.get("name", ""), styles["cell"]),
                    Paragraph(str(s.get("averageMarks") or "N/A"), styles["cell"]),
                    Paragraph(pass_str, styles["cell"]),
                    Paragraph(str(s.get("failureCount", 0)), styles["cell"]),
                    Paragraph(str(s.get("evaluatedStudents", 0)), styles["cell"]),
                ])
            sub_tbl = Table(sub_rows, colWidths=[65, 205, 60, 60, 60, 70])
            sub_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(sub_tbl)
        else:
            elements.append(Paragraph("No subject performance data available for this selection.", styles["body"]))
        elements.append(Spacer(1, 12))

        # 3. Section Comparison Table
        elements.append(Paragraph("Section Comparative Summary", styles["section"]))
        sections = data.get("sections", [])
        if sections:
            sec_headers = ["Section", "Student Count", "Avg SGPA", "Avg Attendance", "Pass Rate"]
            sec_rows = [[Paragraph(h, styles["header"]) for h in sec_headers]]
            for sec in sections:
                att_str = f"{sec.get('averageAttendance')}%" if sec.get('averageAttendance') is not None else "N/A"
                pr_str = f"{sec.get('passPercentage')}%" if sec.get('passPercentage') is not None else "N/A"
                sec_rows.append([
                    Paragraph(f"Section {sec.get('sectionName', '')}", styles["cell_bold"]),
                    Paragraph(str(sec.get("studentCount", 0)), styles["cell"]),
                    Paragraph(str(sec.get("averageSGPA") or "N/A"), styles["cell"]),
                    Paragraph(att_str, styles["cell"]),
                    Paragraph(pr_str, styles["cell"]),
                ])
            sec_tbl = Table(sec_rows, colWidths=[110, 100, 100, 105, 105])
            sec_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(sec_tbl)
        else:
            elements.append(Paragraph("No section comparative records available.", styles["body"]))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_section_pdf(cls, data):
        buf, doc = cls._create_doc()
        styles = cls._get_styles()
        elements = []

        sub_meta = f"Section: {data.get('sectionName')} &nbsp;|&nbsp; Batch: {data.get('batchName')} &nbsp;|&nbsp; Semester: {data.get('semesterName')}"
        elements.extend(cls._build_header_elements(f"Section {data.get('sectionName')} Performance Report", sub_meta, styles))

        # KPIs
        elements.append(Paragraph("Section Overview Metrics", styles["section"]))
        kpi_table_data = [
            [
                Paragraph("Student Count", styles["meta_label"]),
                Paragraph(str(data.get("studentCount", 0)), styles["body_bold"]),
                Paragraph("Average SGPA", styles["meta_label"]),
                Paragraph(str(data.get("averageSGPA") or "N/A"), styles["body_bold"]),
            ],
            [
                Paragraph("Average Attendance", styles["meta_label"]),
                Paragraph(f"{data.get('averageAttendance')}%" if data.get("averageAttendance") is not None else "N/A", styles["body_bold"]),
                Paragraph("Pass Rate", styles["meta_label"]),
                Paragraph(f"{data.get('passPercentage')}%" if data.get("passPercentage") is not None else "N/A", styles["body_bold"]),
            ]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[120, 140, 120, 140])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # Subject table
        elements.append(Paragraph("Subject-Wise Results in Section", styles["section"]))
        subjects = data.get("subjects", [])
        if subjects:
            sub_headers = ["Code", "Subject Name", "Avg Marks", "Pass %", "Failures"]
            sub_rows = [[Paragraph(h, styles["header"]) for h in sub_headers]]
            for s in subjects:
                pr_str = f"{s.get('passPercentage')}%" if s.get('passPercentage') is not None else "N/A"
                sub_rows.append([
                    Paragraph(s.get("code", ""), styles["cell_bold"]),
                    Paragraph(s.get("name", ""), styles["cell"]),
                    Paragraph(str(s.get("averageMarks") or "N/A"), styles["cell"]),
                    Paragraph(pr_str, styles["cell"]),
                    Paragraph(str(s.get("failureCount", 0)), styles["cell"]),
                ])
            sub_tbl = Table(sub_rows, colWidths=[70, 240, 70, 70, 70])
            sub_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(sub_tbl)
        elements.append(Spacer(1, 12))

        # Flagged students
        flagged = data.get("flaggedStudents", [])
        if flagged:
            elements.append(Paragraph(f"Students Requiring Academic Attention ({len(flagged)})", styles["section"]))
            st_headers = ["Roll Number", "Student Name", "Severity", "Primary Reason", "Att %", "SGPA"]
            st_rows = [[Paragraph(h, styles["header"]) for h in st_headers]]
            for st in flagged:
                att_s = f"{st.get('attendance')}%" if st.get('attendance') is not None else "N/A"
                st_rows.append([
                    Paragraph(st.get("rollNumber", ""), styles["cell_bold"]),
                    Paragraph(st.get("name", ""), styles["cell"]),
                    Paragraph(st.get("severity", ""), styles["cell_bold"]),
                    Paragraph(st.get("primaryReason", ""), styles["cell"]),
                    Paragraph(att_s, styles["cell"]),
                    Paragraph(str(st.get("sgpa") or "N/A"), styles["cell"]),
                ])
            st_tbl = Table(st_rows, colWidths=[80, 130, 60, 160, 45, 45])
            st_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(st_tbl)

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_student_pdf(cls, data):
        buf, doc = cls._create_doc()
        styles = cls._get_styles()
        elements = []

        sub_meta = f"Roll No: {data.get('rollNumber')} &nbsp;|&nbsp; Section: {data.get('sectionName')} &nbsp;|&nbsp; Batch: {data.get('batchName')}"
        elements.extend(cls._build_header_elements(f"Student Academic Dossier — {data.get('name')}", sub_meta, styles))

        # Academic standing summary
        elements.append(Paragraph("Academic Standing & Performance Summary", styles["section"]))
        meta_table_data = [
            [
                Paragraph("Student Name", styles["meta_label"]),
                Paragraph(data.get("name", ""), styles["body_bold"]),
                Paragraph("Roll Number", styles["meta_label"]),
                Paragraph(data.get("rollNumber", ""), styles["body_bold"]),
            ],
            [
                Paragraph("Cohort Batch", styles["meta_label"]),
                Paragraph(data.get("batchName", ""), styles["body"]),
                Paragraph("Current Section", styles["meta_label"]),
                Paragraph(data.get("sectionName", ""), styles["body"]),
            ],
            [
                Paragraph("Latest SGPA", styles["meta_label"]),
                Paragraph(str(data.get("sgpa") or "N/A"), styles["body_bold"]),
                Paragraph("Overall CGPA", styles["meta_label"]),
                Paragraph(str(data.get("cgpa") or "N/A"), styles["body_bold"]),
            ],
            [
                Paragraph("Average Attendance", styles["meta_label"]),
                Paragraph(f"{data.get('attendancePercentage')}%" if data.get("attendancePercentage") is not None else "N/A", styles["body_bold"]),
                Paragraph("Performance Trend", styles["meta_label"]),
                Paragraph(data.get("trend", "STABLE"), styles["body"]),
            ]
        ]
        meta_tbl = Table(meta_table_data, colWidths=[120, 140, 120, 140])
        meta_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(meta_tbl)
        elements.append(Spacer(1, 10))

        # Subject-wise results
        elements.append(Paragraph("Coursework Results & Subject-Wise Attendance", styles["section"]))
        subjects = data.get("subjects", [])
        if subjects:
            sub_headers = ["Code", "Subject Name", "Credits", "Attendance", "Total Marks", "Grade", "Status"]
            sub_rows = [[Paragraph(h, styles["header"]) for h in sub_headers]]
            for s in subjects:
                att_str = f"{s.get('attendance')}%" if s.get('attendance') is not None else "N/A"
                sub_rows.append([
                    Paragraph(s.get("code", ""), styles["cell_bold"]),
                    Paragraph(s.get("name", ""), styles["cell"]),
                    Paragraph(str(s.get("credits", "")), styles["cell"]),
                    Paragraph(att_str, styles["cell"]),
                    Paragraph(str(s.get("totalMarks") or "N/A"), styles["cell"]),
                    Paragraph(s.get("grade") or "N/A", styles["cell_bold"]),
                    Paragraph(s.get("resultStatus", ""), styles["cell"]),
                ])
            sub_tbl = Table(sub_rows, colWidths=[65, 175, 45, 65, 60, 50, 60])
            sub_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(sub_tbl)
        elements.append(Spacer(1, 10))

        # Trajectory
        trajectory = data.get("trajectory", [])
        if trajectory:
            elements.append(Paragraph("Semester-Wise Academic Trajectory", styles["section"]))
            traj_headers = ["Semester", "SGPA", "CGPA", "Credits Earned"]
            traj_rows = [[Paragraph(h, styles["header"]) for h in traj_headers]]
            for t in trajectory:
                traj_rows.append([
                    Paragraph(t.get("semesterName", ""), styles["cell_bold"]),
                    Paragraph(str(t.get("sgpa") or "N/A"), styles["cell"]),
                    Paragraph(str(t.get("cgpa") or "N/A"), styles["cell"]),
                    Paragraph(str(t.get("credits") or "N/A"), styles["cell"]),
                ])
            traj_tbl = Table(traj_rows, colWidths=[180, 110, 110, 120])
            traj_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(traj_tbl)
        elements.append(Spacer(1, 10))

        # Attention signals & recommendations
        issues = data.get("issues", [])
        if issues:
            elements.append(Paragraph("Identified Academic Attention Signals", styles["section"]))
            for iss in issues:
                iss_box = [
                    [Paragraph(f"[{iss.get('severity')}] {iss.get('title')}", styles["body_bold"])],
                    [Paragraph(iss.get("reason", ""), styles["body"])],
                ]
                ib_tbl = Table(iss_box, colWidths=[520])
                ib_tbl.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2") if iss.get("severity") in ["CRITICAL", "HIGH"] else colors.HexColor("#F8FAFC")),
                    ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCA5A5") if iss.get("severity") in ["CRITICAL", "HIGH"] else colors.HexColor("#CBD5E1")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                elements.append(ib_tbl)
                elements.append(Spacer(1, 4))

        recs = data.get("recommendations", [])
        if recs:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph("Actionable Pedagogical Recommendations", styles["section"]))
            for rec in recs:
                elements.append(Paragraph(f"• <b>{rec.get('action')}</b>: {rec.get('justification')}", styles["body"]))
                elements.append(Spacer(1, 3))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_subject_pdf(cls, data):
        buf, doc = cls._create_doc()
        styles = cls._get_styles()
        elements = []

        sub_meta = f"Code: {data.get('code')} &nbsp;|&nbsp; Credits: {data.get('credits')} &nbsp;|&nbsp; Type: {data.get('subjectType')}"
        elements.extend(cls._build_header_elements(f"Subject Performance Report — {data.get('name')}", sub_meta, styles))

        elements.append(Paragraph("Course Performance Indicators", styles["section"]))
        pr_str = f"{data.get('passPercentage')}%" if data.get("passPercentage") is not None else "N/A"
        att_str = f"{data.get('averageAttendance')}%" if data.get("averageAttendance") is not None else "N/A"
        kpi_table_data = [
            [
                Paragraph("Evaluated Students", styles["meta_label"]),
                Paragraph(str(data.get("studentCount", 0)), styles["body_bold"]),
                Paragraph("Pass Rate", styles["meta_label"]),
                Paragraph(pr_str, styles["body_bold"]),
            ],
            [
                Paragraph("Average Marks", styles["meta_label"]),
                Paragraph(str(data.get("averageMarks") or "N/A"), styles["body_bold"]),
                Paragraph("Total Failures", styles["meta_label"]),
                Paragraph(str(data.get("failureCount", 0)), styles["body_bold"]),
            ],
            [
                Paragraph("Highest Marks", styles["meta_label"]),
                Paragraph(str(data.get("highestMarks") or "N/A"), styles["body"]),
                Paragraph("Lowest Marks", styles["meta_label"]),
                Paragraph(str(data.get("lowestMarks") or "N/A"), styles["body"]),
            ],
            [
                Paragraph("Average Attendance", styles["meta_label"]),
                Paragraph(att_str, styles["body_bold"]),
                Paragraph("Curricular Type", styles["meta_label"]),
                Paragraph(data.get("subjectType", "THEORY"), styles["body"]),
            ]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[120, 140, 120, 140])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # Section-wise breakdown
        sections = data.get("sections", [])
        if sections:
            elements.append(Paragraph("Section-Wise Course Distribution", styles["section"]))
            sec_headers = ["Section", "Student Count", "Avg Marks", "Pass Rate", "Failures"]
            sec_rows = [[Paragraph(h, styles["header"]) for h in sec_headers]]
            for sec in sections:
                p_rate = f"{sec.get('passPercentage')}%" if sec.get('passPercentage') is not None else "N/A"
                sec_rows.append([
                    Paragraph(f"Section {sec.get('sectionName', '')}", styles["cell_bold"]),
                    Paragraph(str(sec.get("studentCount", 0)), styles["cell"]),
                    Paragraph(str(sec.get("averageMarks") or "N/A"), styles["cell"]),
                    Paragraph(p_rate, styles["cell"]),
                    Paragraph(str(sec.get("failureCount", 0)), styles["cell"]),
                ])
            sec_tbl = Table(sec_rows, colWidths=[110, 100, 105, 105, 100])
            sec_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(sec_tbl)

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def generate_insights_pdf(cls, data):
        buf, doc = cls._create_doc()
        styles = cls._get_styles()
        elements = []

        sub_meta = f"Academic Context: {data.get('semesterName', 'All Semesters')}"
        elements.extend(cls._build_header_elements("Academic Insights & Student Watchlist Report", sub_meta, styles))

        # Summary KPIs
        elements.append(Paragraph("Problem Identification Overview", styles["section"]))
        summary = data.get("summary", {})
        kpi_table_data = [
            [
                Paragraph("Students Requiring Attention", styles["meta_label"]),
                Paragraph(str(summary.get("studentsRequiringAttention", 0)), styles["body_bold"]),
                Paragraph("Critical Issues", styles["meta_label"]),
                Paragraph(str(summary.get("criticalIssues", 0)), styles["body_bold"]),
            ],
            [
                Paragraph("High Priority Issues", styles["meta_label"]),
                Paragraph(str(summary.get("highPriorityIssues", 0)), styles["body_bold"]),
                Paragraph("Medium Priority Issues", styles["meta_label"]),
                Paragraph(str(summary.get("mediumPriorityIssues", 0)), styles["body_bold"]),
            ],
            [
                Paragraph("Flagged Subjects", styles["meta_label"]),
                Paragraph(str(summary.get("subjectsRequiringAttention", 0)), styles["body_bold"]),
                Paragraph("Flagged Sections", styles["meta_label"]),
                Paragraph(str(summary.get("sectionsRequiringAttention", 0)), styles["body_bold"]),
            ]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[140, 120, 140, 120])
        kpi_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))

        # Watchlist
        elements.append(Paragraph("Student Diagnostic Watchlist", styles["section"]))
        watchlist = data.get("watchlist", [])
        if watchlist:
            headers = ["Roll Number", "Student Name", "Sec", "Severity", "Primary Reason", "Att %", "SGPA"]
            rows = [[Paragraph(h, styles["header"]) for h in headers]]
            for st in watchlist:
                att_s = f"{st.get('attendance')}%" if st.get('attendance') is not None else "N/A"
                rows.append([
                    Paragraph(st.get("rollNumber", ""), styles["cell_bold"]),
                    Paragraph(st.get("name", ""), styles["cell"]),
                    Paragraph(st.get("sectionName", ""), styles["cell"]),
                    Paragraph(st.get("severity", ""), styles["cell_bold"]),
                    Paragraph(st.get("primaryReason", ""), styles["cell"]),
                    Paragraph(att_s, styles["cell"]),
                    Paragraph(str(st.get("sgpa") or "N/A"), styles["cell"]),
                ])
            w_tbl = Table(rows, colWidths=[75, 120, 30, 55, 150, 45, 45])
            w_tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            elements.append(w_tbl)
        else:
            elements.append(Paragraph("No students requiring immediate academic attention for this selection.", styles["body"]))

        doc.build(elements, canvasmaker=NumberedCanvas)
        buf.seek(0)
        return buf.getvalue()
