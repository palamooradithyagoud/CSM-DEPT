import csv
import io
import json
import os
import re
import uuid
from datetime import datetime
import openpyxl
from app.extensions import db
from app.models.academic import (
    Batch,
    AcademicYear,
    Semester,
    Section,
    Student,
    Subject,
    AttendanceRecord,
    AssessmentRecord,
    SemesterResult,
    StudentSemesterSummary,
    UploadHistory,
)

TEMP_UPLOAD_CACHE = {}


class IngestionService:
    """
    Academic Data Ingestion & Validation Engine.
    Enforces strict hierarchy:
    DEPARTMENT -> BATCH -> ACADEMIC YEAR -> SEMESTER -> SECTION -> STUDENT -> SUBJECT -> DATA TYPE
    """

    SUPPORTED_DATA_TYPES = ["ATTENDANCE", "MID_1", "MID_2", "SEMESTER_RESULT"]

    KNOWN_SUBJECT_NAMES = {
        "MAC": "Matrices and Calculus",
        "PPS": "Programming for Problem Solving",
        "PPSL": "Programming for Problem Solving Lab",
        "PPS LAB": "Programming for Problem Solving Lab",
        "EW": "Engineering Workshop",
        "CCDT": "Critical Thinking & Design Thinking",
        "EP": "Engineering Physics",
        "EPL": "Engineering Physics Lab",
        "EP LAB": "Engineering Physics Lab",
        "BEE": "Basic Electrical Engineering",
        "BEEL": "Basic Electrical Engineering Lab",
        "BEE LAB": "Basic Electrical Engineering Lab",
        "FDS": "Foundations of Data Science",
        "LAAC": "Linear Algebra and Advanced Calculus",
        "AC": "Applied Chemistry",
        "ACL": "Applied Chemistry Lab",
        "PPPS": "Python Programming for Problem Solving",
        "PYLAB": "Python Programming Lab",
        "ESE": "Engineering Science Elective",
        "ESEL": "Engineering Science Elective Lab",
        "ELCS": "English Language & Communication Skills Lab",
        "ELCSL": "English Language & Communication Skills Lab",
        "EDC": "Electronic Devices and Circuits",
        "EDCL": "Electronic Devices and Circuits Lab",
        "EVS": "Environmental Science and Ecology",
        "ODECV": "Ordinary Differential Equations and Calculus of Variations",
        "ODEVC": "Ordinary Differential Equations and Vector Calculus",
        "EC": "Engineering Chemistry",
        "ECL": "Engineering Chemistry Lab",
        "DS": "Data Structures using C++",
        "DSL": "Data Structures Lab",
        "DE": "Digital Electronics",
        "CAEG": "Computer Aided Engineering Graphics",
        "PDD": "Professional Development & Design",
        "PDP": "Professional Development Program",
        "DMGT": "Discrete Mathematics and Graph Theory",
        "DBMS": "Database Management Systems",
        "DBMSL": "Database Management Systems Lab",
        "OS": "Operating Systems",
        "OSL": "Operating Systems Lab",
        "COA": "Computer Organization and Architecture",
        "JAVA": "Object-Oriented Programming through Java",
        "JAVAL": "Java Programming Lab",
        "DAA": "Design and Analysis of Algorithms",
        "COI": "Constitution of India",
        "CN": "Computer Networks",
        "CNL": "Computer Networks Lab",
        "FLAT": "Formal Languages and Automata Theory",
        "ML": "Machine Learning",
        "MLL": "Machine Learning Lab",
        "SE": "Software Engineering",
        "WT": "Web Technologies",
        "WTL": "Web Technologies Lab",
        "AI": "Artificial Intelligence",
        "AIL": "Artificial Intelligence Lab",
        "CD": "Compiler Design",
        "DL": "Deep Learning and Neural Networks",
        "DLL": "Deep Learning Lab",
        "CC": "Cloud Computing and Distributed Systems",
        "IPR": "Intellectual Property Rights and Cyber Law",
        "CNS": "Cryptography and Network Security",
        "NLP": "Natural Language Processing",
        "BDA": "Big Data Analytics and Processing",
    }

    @staticmethod
    def _clean_str(val):
        if val is None:
            return ""
        return str(val).strip()

    @classmethod
    def _extract_subject_info(cls, header_str):
        """
        Extracts (code, full_name, short_name, subject_type, credits) from header string.
        Supports:
          '( A9001 )  MAC' -> ('A9001', 'Matrices and Calculus', 'MAC', 'THEORY', 3.0)
          'A9001 (MAC)' -> ('A9001', 'Matrices and Calculus', 'MAC', 'THEORY', 3.0)
          'A9007\n(EP)' -> ('A9007', 'Engineering Physics', 'EP', 'THEORY', 3.0)
          'A9008 (EP Lab)' -> ('A9008', 'Engineering Physics Lab', 'EP Lab', 'LAB', 1.5)
          'A9002\nODECV' -> ('A9002', 'Ordinary Differential Equations...', 'ODECV', 'THEORY', 3.0)
        """
        if not header_str:
            return "", "", "", "THEORY", 3.0
        s = str(header_str).strip()
        code = ""
        name = ""

        # Pattern 1: ( CODE ) Name
        m = re.match(r"^\(\s*([A-Za-z0-9_-]+)\s*\)\s*(.*)", s)
        if m:
            code = m.group(1).upper()
            name = m.group(2).strip()
        else:
            # Pattern 2: CODE (Name)
            m = re.match(r"^([A-Za-z0-9_-]{3,})\s*(?:[\n\s]*\(\s*([^)]+)\s*\))?", s)
            if m and m.group(2):
                code = m.group(1).upper()
                name = m.group(2).strip()
            elif "\n" in s:
                parts = [p.strip() for p in s.split("\n") if p.strip()]
                if len(parts) >= 2 and re.match(r"^[A-Za-z0-9_-]{3,}$", parts[0]):
                    code = parts[0].upper()
                    name = parts[1].strip("() ")
            else:
                parts = s.split()
                if len(parts) >= 2 and re.match(r"^[A-Za-z0-9_-]{3,}$", parts[0]):
                    code = parts[0].upper()
                    name = " ".join(parts[1:]).strip("() ")
                else:
                    first_tok = re.match(r"^([A-Za-z0-9_-]+)", s)
                    if first_tok:
                        code = first_tok.group(1).upper()
                        name = code
                    else:
                        code = s.upper()
                        name = code

        short_name = name or code
        full_name = cls.KNOWN_SUBJECT_NAMES.get(short_name.upper(), cls.KNOWN_SUBJECT_NAMES.get(code, short_name))

        # Classify subject type and credits
        short_up = short_name.upper()
        is_lab = (
            "LAB" in short_up
            or "WORKSHOP" in short_up
            or "WORK SHOP" in short_up
            or (short_up.endswith("L") and len(short_up) <= 6 and short_up not in ["CCDL"])
            or "PRACTICAL" in full_name.upper()
        )
        subject_type = "LAB" if is_lab else "THEORY"
        credits = 1.5 if is_lab else (4.0 if ("DS" in short_up or "ML" in short_up) else 3.0)

        return code, full_name, short_name, subject_type, credits

    @classmethod
    def _extract_subject_code(cls, header_str):
        """
        Extracts subject code like 'A9002' from header string.
        """
        return cls._extract_subject_info(header_str)[0]

    @classmethod
    def parse_file_to_rows(cls, file_storage, filename):
        """
        Parses .xlsx or .csv into a raw matrix of rows (list of lists).
        """
        ext = os.path.splitext(filename)[1].lower()
        if ext not in [".xlsx", ".xls", ".csv"]:
            raise ValueError(f"Unsupported file extension '{ext}'. Only .xlsx and .csv files are supported.")

        content = file_storage.read()
        file_storage.seek(0)  # reset pointer

        rows = []
        if ext == ".xlsx":
            try:
                wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
                ws = wb.active
                for r in ws.iter_rows(values_only=True):
                    # Check if entire row is None
                    if any(cell is not None for cell in r):
                        rows.append([cell if cell is not None else "" for cell in r])
            except Exception as e:
                raise ValueError(f"Failed to parse Excel file: {str(e)}")
        elif ext == ".xls":
            try:
                import xlrd
                wb = xlrd.open_workbook(file_contents=content)
                ws = wb.sheet_by_index(0)
                for row_idx in range(ws.nrows):
                    r = [ws.cell_value(row_idx, col_idx) for col_idx in range(ws.ncols)]
                    if any(c != "" and c is not None for c in r):
                        rows.append([c if c is not None else "" for c in r])
            except Exception as e:
                raise ValueError(f"Failed to parse legacy Excel (.xls) file: {str(e)}")
        elif ext == ".csv":
            try:
                # Try UTF-8 then Latin-1
                try:
                    text = content.decode("utf-8-sig")
                except UnicodeDecodeError:
                    text = content.decode("latin-1")
                reader = csv.reader(io.StringIO(text))
                for r in reader:
                    if any(cell.strip() for cell in r):
                        rows.append(r)
            except Exception as e:
                raise ValueError(f"Failed to parse CSV file: {str(e)}")

        if not rows:
            raise ValueError("The uploaded file is empty.")

        return rows, content

    @classmethod
    def normalize_tabular_data(cls, raw_rows, data_type):
        """
        Converts either Standard Tabular format or College Matrix format
        into uniform normalized records:
        [{
            "roll_number": "...",
            "student_name": "...",
            "subject_code": "...",
            "section_name": "...",
            "row_idx": int,
            ... data specific fields
        }]
        """
        # Determine if it's a College Matrix Attendance sheet
        # Check rows 1 to 6 for patterns like '#', 'Section', 'Roll Number', 'ODECV' or 'GD', 'S', 'GP'
        is_attendance_matrix = False
        is_result_matrix = False
        header_row_idx = 0

        for idx, row in enumerate(raw_rows[:8]):
            row_str = " ".join([str(c) for c in row if c is not None]).lower()
            if "roll number" in row_str or "roll no" in row_str:
                header_row_idx = idx
                if any("\n" in str(c) for c in row if c) or any("odecv" in str(c).lower() for c in row if c):
                    is_attendance_matrix = True
                if idx > 0 and any("student info" in str(c).lower() for c in raw_rows[0]):
                    is_result_matrix = True
                break

        # Check for Result Matrix if first row had '( a9001 )' and second row had 'gd', 'gp'
        if not is_result_matrix and len(raw_rows) > 2:
            r1_str = " ".join([str(c) for c in raw_rows[0] if c]).lower()
            r2_str = " ".join([str(c) for c in raw_rows[1] if c]).lower()
            if "gd" in r2_str and "gp" in r2_str:
                is_result_matrix = True
                header_row_idx = 1

        if is_attendance_matrix and data_type == "ATTENDANCE":
            return cls._parse_attendance_matrix(raw_rows, header_row_idx)
        elif is_result_matrix and data_type == "SEMESTER_RESULT":
            return cls._parse_result_matrix(raw_rows, header_row_idx)
        else:
            return cls._parse_standard_tabular(raw_rows, data_type)

    @classmethod
    def _parse_attendance_matrix(cls, raw_rows, header_row_idx):
        """
        Parses College Attendance Matrix format:
        Row 4: #, Section, Roll Number, Name of the Student, A9002\nODECV, None, A9009\nEC, ...
        Row 6: None, None, None, None, C, A, C, A, ...
        Row 7+: Data rows
        """
        subject_row = raw_rows[header_row_idx]
        conducted_attended_row = raw_rows[header_row_idx + 2] if len(raw_rows) > header_row_idx + 2 else []

        # Find roll number col and name col
        roll_col = -1
        name_col = -1
        sec_col = -1
        for col_idx, val in enumerate(subject_row):
            v_low = str(val).lower().strip()
            if "roll" in v_low:
                roll_col = col_idx
            elif "name" in v_low:
                name_col = col_idx
            elif "section" in v_low or v_low == "sec":
                sec_col = col_idx

        if roll_col == -1:
            roll_col = 2  # default per observed sheet

        # Map column pairs for subjects: (subject_code, full_name, short_name, subject_type, credits, conducted_col, attended_col)
        subject_pairs = []
        c = roll_col + 2
        while c < len(subject_row):
            header_val = str(subject_row[c]).strip()
            if not header_val or header_val.lower() == "total" or "total" in header_val.lower():
                c += 1
                continue
            subj_code, full_name, short_name, subj_type, credits = cls._extract_subject_info(header_val)
            if subj_code:
                # Next col is usually attended
                cond_col = c
                att_col = c + 1
                subject_pairs.append((subj_code, full_name, short_name, subj_type, credits, cond_col, att_col))
                c += 2
            else:
                c += 1

        records = []
        start_data_row = header_row_idx + 3
        for r_idx in range(start_data_row, len(raw_rows)):
            row = raw_rows[r_idx]
            if len(row) <= roll_col:
                continue
            roll = cls._clean_str(row[roll_col]).upper()
            if not roll or roll.lower() in ["total", "average", "percentage", "passed"]:
                continue
            name = cls._clean_str(row[name_col]) if name_col != -1 and len(row) > name_col else ""
            sec = cls._clean_str(row[sec_col]).upper() if sec_col != -1 and len(row) > sec_col else ""

            for subj_code, full_name, short_name, subj_type, credits, cond_c, att_c in subject_pairs:
                cond_val = row[cond_c] if len(row) > cond_c else None
                att_val = row[att_c] if len(row) > att_c else None

                # Calculate percentage
                try:
                    c_num = float(cond_val) if cond_val is not None and str(cond_val).strip() != "" else 0
                    a_num = float(att_val) if att_val is not None and str(att_val).strip() != "" else 0
                    pct = round((a_num / c_num) * 100, 2) if c_num > 0 else 0.0
                except (ValueError, TypeError, ZeroDivisionError):
                    c_num, a_num, pct = 0, 0, 0.0

                records.append({
                    "row_idx": r_idx + 1,
                    "roll_number": roll,
                    "student_name": name,
                    "section_name": sec,
                    "subject_code": subj_code,
                    "subject_name": full_name,
                    "short_name": short_name,
                    "subject_type": subj_type,
                    "credits": credits,
                    "percentage": pct,
                    "classes_attended": int(a_num),
                    "total_classes": int(c_num),
                })

        return records

    @classmethod
    def _parse_result_matrix(cls, raw_rows, header_row_idx):
        """
        Parses College Result Matrix format (RESULT 1-1 style).
        Row 0: Student Info, ( A9001 ) MAC, ... FINAL RESULT
        Row 1: S.No., Student Name, Roll No, Sec, GD, S, GP, ... TCR, SGPA, Current CGPA
        Row 2+: Data
        """
        r0 = raw_rows[0]
        r1 = raw_rows[1]

        roll_col = -1
        name_col = -1
        sec_col = -1
        for col_idx, val in enumerate(r1):
            v_low = str(val).lower().strip()
            if "roll" in v_low:
                roll_col = col_idx
            elif "name" in v_low:
                name_col = col_idx
            elif "sec" in v_low:
                sec_col = col_idx

        # Find SGPA / CGPA columns
        sgpa_col = -1
        cgpa_col = -1
        for col_idx, val in enumerate(r1):
            v_low = str(val).lower().strip()
            if v_low == "sgpa":
                sgpa_col = col_idx
            elif "cgpa" in v_low and "last" not in v_low:
                cgpa_col = col_idx

        # Find subjects in Row 0
        subject_triplets = []  # (subj_code, full_name, short_name, subj_type, credits, gd_col, s_col, gp_col)
        c = 0
        while c < len(r0):
            val0 = r0[c]
            if val0 and "(" in str(val0) and ")" in str(val0):
                subj_code, full_name, short_name, subj_type, credits = cls._extract_subject_info(str(val0))
                gd_col = c
                s_col = c + 1
                gp_col = c + 2
                subject_triplets.append((subj_code, full_name, short_name, subj_type, credits, gd_col, s_col, gp_col))
                c += 3
            else:
                c += 1

        records = []
        for r_idx in range(2, len(raw_rows)):
            row = raw_rows[r_idx]
            if len(row) <= roll_col:
                continue
            roll = cls._clean_str(row[roll_col]).upper()
            if not roll or "total" in roll.lower() or "passed" in roll.lower():
                continue
            name = cls._clean_str(row[name_col]) if name_col != -1 and len(row) > name_col else ""
            sec = cls._clean_str(row[sec_col]).upper() if sec_col != -1 and len(row) > sec_col else ""

            sgpa_val = None
            if sgpa_col != -1 and len(row) > sgpa_col:
                try:
                    s_str = str(row[sgpa_col]).strip()
                    if s_str:
                        sgpa_val = float(s_str)
                except (ValueError, TypeError):
                    sgpa_val = None

            cgpa_val = None
            if cgpa_col != -1 and len(row) > cgpa_col:
                try:
                    c_str = str(row[cgpa_col]).strip()
                    if c_str:
                        cgpa_val = float(c_str)
                except (ValueError, TypeError):
                    cgpa_val = None

            for subj_code, full_name, short_name, subj_type, credits, gd_c, s_c, gp_c in subject_triplets:
                gd = cls._clean_str(row[gd_c]) if len(row) > gd_c else None
                s_stat = cls._clean_str(row[s_c]) if len(row) > s_c else None
                gp = None
                if len(row) > gp_c:
                    try:
                        gp_str = str(row[gp_c]).strip()
                        if gp_str:
                            gp = float(gp_str)
                    except (ValueError, TypeError):
                        gp = None

                status_norm = "PASSED" if s_stat and "p" in s_stat.lower() else ("FAILED" if s_stat and "f" in s_stat.lower() else "PASSED")

                records.append({
                    "row_idx": r_idx + 1,
                    "roll_number": roll,
                    "student_name": name,
                    "section_name": sec,
                    "subject_code": subj_code,
                    "subject_name": full_name,
                    "short_name": short_name,
                    "subject_type": subj_type,
                    "credits": credits,
                    "grade": gd,
                    "grade_point": gp,
                    "result_status": status_norm,
                    "sgpa": sgpa_val,
                    "cgpa": cgpa_val,
                })

        return records

    @classmethod
    def _parse_standard_tabular(cls, raw_rows, data_type):
        """
        Parses standard column-based row format.
        Columns might be:
        Roll Number | Student Name | Subject Code | Attendance %
        OR
        Roll Number | Subject Code | Marks Obtained | Max Marks
        OR
        Roll Number | Subject Code | Internal | External | Total | Grade | Grade Point
        """
        # Find header row
        header_row_idx = -1
        header_map = {}
        for idx, row in enumerate(raw_rows[:5]):
            raw_cleaned = []
            for c in row:
                if c is not None:
                    s = cls._clean_str(c).lower().replace(" ", "_").replace("-", "_")
                    s = re.sub(r"[^a-z0-9_]", "", s)
                    raw_cleaned.append(s)
            if any(k in raw_cleaned for k in ["roll_no", "roll_number", "rollno", "student_id", "htno", "roll"]):
                header_row_idx = idx
                for col_idx, col_name in enumerate(raw_cleaned):
                    if col_name:
                        header_map[col_name] = col_idx
                break

        if header_row_idx == -1:
            raise ValueError(
                "Unable to identify header row in file. Expected columns: 'Roll Number' or 'Roll No', along with 'Subject Code' and data values."
            )

        def get_col(candidates):
            for cand in candidates:
                cand_clean = cand.lower().replace(" ", "_").replace("-", "_")
                # Direct match
                if cand_clean in header_map:
                    return header_map[cand_clean]
                # Partial match in header keys
                for h_k, h_idx in header_map.items():
                    if cand_clean in h_k or h_k in cand_clean:
                        return h_idx
            return None


        roll_c = get_col(["roll_number", "roll_no", "rollno", "student_id", "htno"])
        name_c = get_col(["student_name", "name", "student"])
        sec_c = get_col(["section", "sec", "section_name"])
        subj_c = get_col(["subject_code", "subject", "sub_code", "course_code"])
        subj_name_c = get_col(["subject_name", "course_name", "sub_name", "title"])

        if roll_c is None:
            raise ValueError("Required column 'Roll Number' not found in file.")
        if subj_c is None:
            raise ValueError("Required column 'Subject Code' not found in file.")

        records = []
        for r_idx in range(header_row_idx + 1, len(raw_rows)):
            row = raw_rows[r_idx]
            if len(row) <= roll_c:
                continue
            roll = cls._clean_str(row[roll_c]).upper()
            if not roll:
                continue

            name = cls._clean_str(row[name_c]) if name_c is not None and len(row) > name_c else ""
            sec = cls._clean_str(row[sec_c]).upper() if sec_c is not None and len(row) > sec_c else ""
            raw_subj = cls._clean_str(row[subj_c]) if len(row) > subj_c else ""
            subj, full_name, short_name, subj_type, credits = cls._extract_subject_info(raw_subj)
            if subj_name_c is not None and len(row) > subj_name_c:
                custom_name = cls._clean_str(row[subj_name_c])
                if custom_name:
                    full_name = custom_name

            rec = {
                "row_idx": r_idx + 1,
                "roll_number": roll,
                "student_name": name,
                "section_name": sec,
                "subject_code": subj,
                "subject_name": full_name,
                "short_name": short_name,
                "subject_type": subj_type,
                "credits": credits,
            }

            if data_type == "ATTENDANCE":
                pct_c = get_col(["attendance", "percentage", "attendance_percentage", "pct", "att_%"])
                att_classes_c = get_col(["classes_attended", "attended", "present"])
                tot_classes_c = get_col(["total_classes", "conducted", "total"])

                pct_val = None
                if pct_c is not None and len(row) > pct_c:
                    val_str = cls._clean_str(row[pct_c]).replace("%", "")
                    try:
                        pct_val = float(val_str)
                    except ValueError:
                        pct_val = None

                c_att = None
                if att_classes_c is not None and len(row) > att_classes_c:
                    try:
                        c_att = int(float(row[att_classes_c]))
                    except (ValueError, TypeError):
                        pass

                c_tot = None
                if tot_classes_c is not None and len(row) > tot_classes_c:
                    try:
                        c_tot = int(float(row[tot_classes_c]))
                    except (ValueError, TypeError):
                        pass

                if pct_val is None and c_att is not None and c_tot and c_tot > 0:
                    pct_val = round((c_att / c_tot) * 100, 2)

                rec["percentage"] = pct_val
                rec["classes_attended"] = c_att
                rec["total_classes"] = c_tot

            elif data_type in ["MID_1", "MID_2"]:
                marks_c = get_col(["marks", "marks_obtained", "score", "mid_marks", "obtained"])
                max_c = get_col(["max_marks", "total_marks", "maximum", "out_of"])
                status_c = get_col(["status", "attendance_status"])

                marks_val = None
                status_val = "AVAILABLE"

                if marks_c is not None and len(row) > marks_c:
                    raw_m = cls._clean_str(row[marks_c])
                    if raw_m.upper() in ["NA", "N/A", "NOT AVAILABLE", "NOT_AVAILABLE"]:
                        status_val = "NOT_AVAILABLE"
                        marks_val = None
                    elif raw_m.upper() in ["AB", "ABSENT", "A"]:
                        status_val = "ABSENT"
                        marks_val = 0.0
                    else:
                        try:
                            marks_val = float(raw_m)
                        except ValueError:
                            marks_val = None
                else:
                    status_val = "NOT_AVAILABLE"

                max_m = 30.0
                if max_c is not None and len(row) > max_c:
                    try:
                        max_m = float(row[max_c])
                    except (ValueError, TypeError):
                        max_m = 30.0

                rec["marks_obtained"] = marks_val
                rec["max_marks"] = max_m
                rec["status"] = status_val

            elif data_type == "SEMESTER_RESULT":
                int_c = get_col(["internal", "internal_marks", "int"])
                ext_c = get_col(["external", "external_marks", "ext"])
                tot_c = get_col(["total", "total_marks", "marks"])
                gd_c = get_col(["grade", "gd"])
                gp_c = get_col(["grade_point", "gp", "points"])
                sgpa_c = get_col(["sgpa", "gpa"])
                cgpa_c = get_col(["cgpa"])

                def parse_num(col_idx):
                    if col_idx is not None and len(row) > col_idx:
                        s = cls._clean_str(row[col_idx])
                        if s:
                            try:
                                return float(s)
                            except ValueError:
                                return None
                    return None

                rec["internal_marks"] = parse_num(int_c)
                rec["external_marks"] = parse_num(ext_c)
                rec["total_marks"] = parse_num(tot_c)
                rec["grade"] = cls._clean_str(row[gd_c]) if gd_c is not None and len(row) > gd_c else None
                rec["grade_point"] = parse_num(gp_c)
                rec["sgpa"] = parse_num(sgpa_c)
                rec["cgpa"] = parse_num(cgpa_c)
                rec["result_status"] = "PASSED" if rec["grade"] != "F" else "FAILED"

            records.append(rec)

        return records

    @classmethod
    def validate_dataset(cls, records, batch_id, academic_year_id, semester_id, section_id, data_type):
        """
        Runs comprehensive validation across all parsed records:
        1. Academic context entity verification.
        2. Student verification & Section/Batch membership.
        3. Subject verification & Semester association.
        4. Range & format checks (e.g., Attendance 0-100, Marks <= Max Marks).
        5. Duplicate detection against current database state and within file.
        Returns: {
            "total_rows": int,
            "valid_rows": int,
            "invalid_rows": int,
            "duplicates_count": int,
            "errors": [...],
            "warnings": [...],
            "valid_records": [...],
            "preview_rows": [...]
        }
        """
        # 1. Fetch & Verify Academic Context
        batch = Batch.query.get(batch_id)
        if not batch:
            raise ValueError(f"Batch with ID '{batch_id}' not found.")

        academic_year = AcademicYear.query.filter_by(id=academic_year_id, batch_id=batch_id).first()
        if not academic_year:
            raise ValueError("Academic Year not found or does not belong to the selected Batch.")

        semester = Semester.query.filter_by(id=semester_id, academic_year_id=academic_year_id).first()
        if not semester:
            raise ValueError("Semester not found or does not belong to the selected Academic Year.")

        is_overall = (not section_id or str(section_id).strip().upper() in ["OVERALL", "ALL", "NONE", ""])

        if is_overall and data_type == "ATTENDANCE":
            raise ValueError("Attendance must be Section-Wise. Please select Section A, B, or C.")

        section = None
        if not is_overall:
            section = Section.query.filter_by(id=section_id, semester_id=semester_id).first()
            if not section:
                raise ValueError("Section not found or does not belong to the selected Semester.")

        # Cache all sections in this Semester
        semester_sections = Section.query.filter_by(semester_id=semester_id).all()
        sec_by_name = {s.name.upper(): s for s in semester_sections}
        sec_by_id = {s.id: s for s in semester_sections}

        # Cache Students in this Batch
        all_students = Student.query.filter_by(batch_id=batch_id).all()
        student_by_roll = {s.roll_number.upper(): s for s in all_students}

        # Cache Subjects in this Semester
        semester_subjects = Subject.query.filter_by(semester_id=semester_id, is_active=True).all()
        subject_by_code = {s.code.upper(): s for s in semester_subjects}
        # Also map short names for flexibility
        subject_by_short = {s.short_name.upper(): s for s in semester_subjects if s.short_name}

        # Track dynamically extracted subjects from uploaded file
        newly_extracted_subjects = {}

        # Cache Existing Database Records for Duplicate Check
        existing_keys = set()
        if data_type == "ATTENDANCE":
            records_db = AttendanceRecord.query.filter_by(semester_id=semester_id, section_id=section.id).all()
            for r in records_db:
                existing_keys.add((r.student_id, r.subject_id))
        elif data_type in ["MID_1", "MID_2"]:
            if is_overall:
                records_db = AssessmentRecord.query.filter_by(
                    semester_id=semester_id, assessment_type=data_type
                ).all()
            else:
                records_db = AssessmentRecord.query.filter_by(
                    semester_id=semester_id, section_id=section.id, assessment_type=data_type
                ).all()
            for r in records_db:
                existing_keys.add((r.student_id, r.subject_id))
        elif data_type == "SEMESTER_RESULT":
            if is_overall:
                records_db = SemesterResult.query.filter_by(semester_id=semester_id).all()
            else:
                records_db = SemesterResult.query.filter_by(semester_id=semester_id, section_id=section.id).all()
            for r in records_db:
                existing_keys.add((r.student_id, r.subject_id))

        errors = []
        warnings = []
        valid_records = []
        file_seen_keys = set()
        duplicates_count = 0

        for idx, rec in enumerate(records):
            row_num = rec.get("row_idx", idx + 1)
            roll = rec.get("roll_number", "").strip().upper()
            subj_code = rec.get("subject_code", "").strip().upper()
            file_sec = rec.get("section_name", "").strip().upper()

            row_errors = []

            # 2. Student & Section Check
            if not roll:
                row_errors.append(f"Row {row_num}: Missing Student Roll Number.")
                student = None
            elif roll not in student_by_roll:
                row_errors.append(
                    f"Row {row_num}: Student with Roll Number '{roll}' is not registered in Batch '{batch.name}'."
                )
                student = None
            else:
                student = student_by_roll[roll]
                if is_overall:
                    # In Overall Result upload, resolve the student's section automatically across A, B, C!
                    target_sec = None
                    if file_sec and file_sec in sec_by_name:
                        target_sec = sec_by_name[file_sec]
                    elif student.current_section_id and student.current_section_id in sec_by_id:
                        target_sec = sec_by_id[student.current_section_id]
                    elif student.current_section and student.current_section.name.upper() in sec_by_name:
                        target_sec = sec_by_name[student.current_section.name.upper()]
                    elif semester_sections:
                        target_sec = semester_sections[0]

                    rec["section_id"] = target_sec.id if target_sec else None
                    rec["section_name"] = target_sec.name if target_sec else (file_sec or "A")
                else:
                    # Section-wise consistency check (strictly enforced for Attendance)
                    if student.current_section_id and student.current_section and student.current_section.name != section.name:
                        row_errors.append(
                            f"Row {row_num}: Student '{roll}' belongs to Section '{student.current_section.name if student.current_section else 'Unknown'}', not the selected Section '{section.name}'. Silent cross-section movement is forbidden."
                        )
                    elif file_sec and file_sec != section.name.upper():
                        row_errors.append(
                            f"Row {row_num}: File specifies Section '{file_sec}', which contradicts the selected Section '{section.name}'."
                        )
                    rec["section_id"] = section.id
                    rec["section_name"] = section.name

            # 3. Subject Check (Extract directly from uploaded CSV/Excel)
            if not subj_code:
                row_errors.append(f"Row {row_num}: Missing Subject Code.")
                subject = None
            elif subj_code in subject_by_code:
                subject = subject_by_code[subj_code]
            elif subj_code in subject_by_short:
                subject = subject_by_short[subj_code]
            elif subj_code in newly_extracted_subjects:
                subj_data = newly_extracted_subjects[subj_code]
                class _ExtractedSubjProxyCached:
                    id = f"auto-{subj_code}"
                    code = subj_data["code"]
                    name = subj_data["name"]
                    short_name = subj_data["short_name"]
                    subject_type = subj_data["subject_type"]
                    credits = subj_data["credits"]
                subject = _ExtractedSubjProxyCached()
            else:
                # Validate subject code format to guard against non-subject typos
                is_valid_code_pattern = bool(
                    re.match(r"^[A-Za-z0-9]{3,8}$", subj_code)
                    and not subj_code.startswith("NOT_A_")
                    and "SUBJECT" not in subj_code
                )
                if not is_valid_code_pattern:
                    row_errors.append(
                        f"Row {row_num}: Subject '{subj_code}' is not configured for {semester.name}. Auto-creation is disallowed to prevent typos."
                    )
                    subject = None
                else:
                    s_name = rec.get("subject_name") or cls.KNOWN_SUBJECT_NAMES.get(subj_code, subj_code)
                    s_short = rec.get("short_name") or subj_code
                    s_type = rec.get("subject_type", "THEORY")
                    s_creds = rec.get("credits", 3.0)
                    newly_extracted_subjects[subj_code] = {
                        "code": subj_code,
                        "name": s_name,
                        "short_name": s_short,
                        "subject_type": s_type,
                        "credits": s_creds,
                    }
                    warnings.append(
                        f"Subject '{subj_code}' ({s_name}) extracted from file and will be automatically registered for {semester.name}."
                    )
                    class _ExtractedSubjProxyNew:
                        id = f"auto-{subj_code}"
                        code = subj_code
                        name = s_name
                        short_name = s_short
                        subject_type = s_type
                        credits = s_creds
                    subject = _ExtractedSubjProxyNew()

            # 4. Data Type Value Checks
            if data_type == "ATTENDANCE":
                pct = rec.get("percentage")
                if pct is None:
                    row_errors.append(f"Row {row_num}: Invalid or missing Attendance percentage.")
                elif not (0.0 <= pct <= 100.0):
                    row_errors.append(
                        f"Row {row_num}: Attendance percentage {pct}% is out of valid bounds (0.0 - 100.0%)."
                    )

            elif data_type in ["MID_1", "MID_2"]:
                status = rec.get("status", "AVAILABLE")
                marks = rec.get("marks_obtained")
                max_m = rec.get("max_marks", 30.0)

                if status == "AVAILABLE":
                    if marks is None:
                        row_errors.append(f"Row {row_num}: Missing marks for available assessment.")
                    elif marks < 0 or marks > max_m:
                        row_errors.append(
                            f"Row {row_num}: Marks obtained ({marks}) must be between 0 and maximum marks ({max_m})."
                        )

            elif data_type == "SEMESTER_RESULT":
                grade = rec.get("grade")
                gp = rec.get("grade_point")
                if grade is None and gp is None:
                    row_errors.append(f"Row {row_num}: Result record must contain at least Grade or Grade Point.")

            # 5. Duplicate Check
            is_dup = False
            if student and subject:
                key = (student.id, getattr(subject, "id", None) or f"auto-{subj_code}")
                if key in file_seen_keys:
                    row_errors.append(
                        f"Row {row_num}: Duplicate entry for Student '{roll}' and Subject '{subject.code}' found within the same uploaded file."
                    )
                file_seen_keys.add(key)

                if key in existing_keys:
                    is_dup = True
                    duplicates_count += 1
                    warnings.append(
                        f"Row {row_num}: Existing {data_type} record found in database for Student '{roll}' - {subject.code}. Duplicate resolution required upon confirmation."
                    )

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_records.append({
                    **rec,
                    "student_id": student.id,
                    "student_name": student.name,
                    "subject_id": getattr(subject, "id", None),
                    "subject_name": getattr(subject, "name", rec.get("subject_name", subj_code)),
                    "subject_code": subj_code,
                    "is_duplicate": is_dup,
                })

        total_rows = len(records)
        valid_rows = len(valid_records)
        invalid_rows = total_rows - valid_rows

        # Prepare paginated preview (first 50 rows)
        preview_rows = valid_records[:50]

        return {
            "total_rows": total_rows,
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "duplicates_count": duplicates_count,
            "errors": errors[:100],  # cap error report display
            "total_errors": len(errors),
            "warnings": warnings[:50],
            "valid_records": valid_records,
            "preview_rows": preview_rows,
            "extracted_subjects": list(newly_extracted_subjects.values()),
        }

    @classmethod
    def execute_transactional_import(
        cls,
        valid_records,
        batch_id,
        academic_year_id,
        semester_id,
        section_id,
        data_type,
        duplicate_strategy,
        uploaded_by,
        filename,
    ):
        """
        Executes atomic database transaction to import valid records.
        duplicate_strategy: 'CANCEL' | 'SKIP' | 'REPLACE'
        Atomicity Guarantee: All-or-nothing rollback on any database exception.
        """
        if duplicate_strategy == "CANCEL":
            has_dups = any(r.get("is_duplicate", False) for r in valid_records)
            if has_dups:
                raise ValueError("Import cancelled because duplicate records exist and 'Cancel' was selected.")

        imported_count = 0
        skipped_count = 0
        replaced_count = 0

        # Execute inside a transaction savepoint / block
        try:
            # 0. Ensure all subjects extracted from uploaded file are registered in DB
            existing_sem_subjects = {s.code.upper(): s for s in Subject.query.filter_by(semester_id=semester_id).all()}
            for s in Subject.query.filter_by(semester_id=semester_id).all():
                if s.short_name:
                    existing_sem_subjects[s.short_name.upper()] = s

            subject_id_map = {}
            for rec in valid_records:
                s_code = rec["subject_code"].upper()
                if s_code in subject_id_map:
                    rec["subject_id"] = subject_id_map[s_code]
                    continue

                if s_code in existing_sem_subjects:
                    subj_obj = existing_sem_subjects[s_code]
                else:
                    s_name = rec.get("subject_name") or cls.KNOWN_SUBJECT_NAMES.get(s_code, s_code)
                    s_short = rec.get("short_name") or s_code
                    s_type = rec.get("subject_type", "THEORY")
                    s_creds = rec.get("credits", 3.0)

                    subj_obj = Subject(
                        semester_id=semester_id,
                        code=s_code,
                        name=s_name,
                        short_name=s_short,
                        subject_type=s_type,
                        credits=s_creds,
                        is_active=True,
                    )
                    db.session.add(subj_obj)
                    db.session.flush()
                    existing_sem_subjects[s_code] = subj_obj

                subject_id_map[s_code] = subj_obj.id
                rec["subject_id"] = subj_obj.id

            # If strategy is REPLACE, gather student-subject pairs to replace
            if duplicate_strategy == "REPLACE":
                for rec in valid_records:
                    if rec.get("is_duplicate", False):
                        s_id = rec["student_id"]
                        sub_id = rec["subject_id"]
                        if data_type == "ATTENDANCE":
                            AttendanceRecord.query.filter_by(
                                student_id=s_id, semester_id=semester_id, subject_id=sub_id
                            ).delete()
                        elif data_type in ["MID_1", "MID_2"]:
                            AssessmentRecord.query.filter_by(
                                student_id=s_id, semester_id=semester_id, subject_id=sub_id, assessment_type=data_type
                            ).delete()
                        elif data_type == "SEMESTER_RESULT":
                            SemesterResult.query.filter_by(
                                student_id=s_id, semester_id=semester_id, subject_id=sub_id
                            ).delete()
                        replaced_count += 1

            is_overall = (not section_id or str(section_id).strip().upper() in ["OVERALL", "ALL", "NONE", ""])
            effective_section_id = None if is_overall else section_id

            for rec in valid_records:
                is_dup = rec.get("is_duplicate", False)
                if is_dup and duplicate_strategy == "SKIP":
                    skipped_count += 1
                    continue

                rec_sec_id = rec.get("section_id") or effective_section_id
                if not rec_sec_id:
                    stu_temp = Student.query.get(rec["student_id"])
                    rec_sec_id = stu_temp.current_section_id if stu_temp else None

                if data_type == "ATTENDANCE":
                    # If replacing, record was deleted above; create fresh
                    att = AttendanceRecord(
                        student_id=rec["student_id"],
                        section_id=rec_sec_id,
                        subject_id=rec["subject_id"],
                        semester_id=semester_id,
                        percentage=rec["percentage"],
                        classes_attended=rec.get("classes_attended"),
                        total_classes=rec.get("total_classes"),
                    )
                    db.session.add(att)
                    imported_count += 1

                elif data_type in ["MID_1", "MID_2"]:
                    asm = AssessmentRecord(
                        student_id=rec["student_id"],
                        section_id=rec_sec_id,
                        subject_id=rec["subject_id"],
                        semester_id=semester_id,
                        assessment_type=data_type,
                        marks_obtained=rec.get("marks_obtained"),
                        max_marks=rec.get("max_marks", 30.0),
                        status=rec.get("status", "AVAILABLE"),
                    )
                    db.session.add(asm)
                    imported_count += 1

                elif data_type == "SEMESTER_RESULT":
                    res = SemesterResult(
                        student_id=rec["student_id"],
                        section_id=rec_sec_id,
                        subject_id=rec["subject_id"],
                        semester_id=semester_id,
                        internal_marks=rec.get("internal_marks"),
                        external_marks=rec.get("external_marks"),
                        total_marks=rec.get("total_marks"),
                        grade=rec.get("grade"),
                        grade_point=rec.get("grade_point"),
                        result_status=rec.get("result_status", "PASSED"),
                    )
                    db.session.add(res)
                    imported_count += 1

                    # If SGPA/CGPA provided in result record, update or create StudentSemesterSummary
                    if rec.get("sgpa") is not None or rec.get("cgpa") is not None:
                        summary = StudentSemesterSummary.query.filter_by(
                            student_id=rec["student_id"], semester_id=semester_id
                        ).first()
                        if not summary:
                            summary = StudentSemesterSummary(
                                student_id=rec["student_id"],
                                semester_id=semester_id,
                                section_id=rec_sec_id,
                                sgpa=rec.get("sgpa"),
                                cgpa=rec.get("cgpa"),
                                is_official=True,
                            )
                            db.session.add(summary)
                        else:
                            if rec.get("sgpa") is not None:
                                summary.sgpa = rec.get("sgpa")
                            if rec.get("cgpa") is not None:
                                summary.cgpa = rec.get("cgpa")
                            if rec_sec_id:
                                summary.section_id = rec_sec_id

            # Record Upload History
            history = UploadHistory(
                filename=filename,
                uploaded_by=uploaded_by,
                batch_id=batch_id,
                academic_year_id=academic_year_id,
                semester_id=semester_id,
                section_id=effective_section_id,
                data_type=data_type,
                total_rows=len(valid_records) + skipped_count,
                valid_rows=imported_count + skipped_count,
                invalid_rows=0,
                duplicates_count=replaced_count + skipped_count,
                status="IMPORTED",
                details=json.dumps({
                    "strategy": duplicate_strategy,
                    "imported": imported_count,
                    "replaced": replaced_count,
                    "skipped": skipped_count,
                    "is_overall": is_overall,
                }),
            )
            db.session.add(history)

            # Atomic commit
            db.session.commit()

            return {
                "success": True,
                "imported_count": imported_count,
                "replaced_count": replaced_count,
                "skipped_count": skipped_count,
                "upload_id": history.id,
            }

        except Exception as e:
            db.session.rollback()
            # Log failed history attempt
            try:
                fail_history = UploadHistory(
                    filename=filename,
                    uploaded_by=uploaded_by,
                    batch_id=batch_id,
                    academic_year_id=academic_year_id,
                    semester_id=semester_id,
                    section_id=section_id,
                    data_type=data_type,
                    total_rows=len(valid_records),
                    valid_rows=0,
                    invalid_rows=len(valid_records),
                    duplicates_count=0,
                    status="FAILED",
                    details=f"Transaction rolled back due to error: {str(e)}",
                )
                db.session.add(fail_history)
                db.session.commit()
            except Exception:
                db.session.rollback()

            raise RuntimeError(f"Database import transaction failed and was completely rolled back: {str(e)}")
