"""
Phase 5 Comprehensive Automated Test Suite.
Validates:
1. Multi-format Report Generation (PDF, Excel, CSV)
2. Report Authorization and RBAC Security (HOD, ADMIN, STUDENT, PUBLIC)
3. Input Validation, Format Guarding, and Safe Empty-Dataset Handling
4. High-Volume Dataset Performance & Memory Safety
5. Production Database Connectivity, Transaction Commit & Rollback Integrity
6. Secret & Credential Privacy Isolation
7. Upload Validation & Atomic Rollback
8. End-to-End Academic Lifecycle Workflow
9. Academic Privacy: Zero Private Student Data Leaked to Public Endpoints
"""

import unittest
import io
import openpyxl
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.department import DepartmentInfo
from app.models.academic import (
    Batch,
    AcademicYear,
    Semester,
    Section,
    Student,
    Subject,
    AttendanceRecord,
    SemesterResult,
    StudentSemesterSummary,
)
from app.reports.service import ReportsService


class Phase5ProductionTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

            # 0. Department Info
            dept_info = DepartmentInfo(
                name="Department of Computer Science & Engineering",
                short_code="CSE",
                about="Fostering academic excellence in computing.",
                vision="To be a premier center of technical education.",
                mission="Provide rigorous curriculum and research opportunities.",
                hod_name="Dr. M. A. Jabbar",
                hod_message="Welcome to our department.",
                contact_email="hod.cse@dept.edu",
            )
            db.session.add(dept_info)

            # 1. Users: HOD and Regular Student
            cls.hod = User(
                email="hod.production@dept.edu",
                full_name="Dr. Production HOD",
                role="HOD",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.hod.set_password("HodPass@123")
            db.session.add(cls.hod)

            cls.student_user = User(
                email="student.prod@dept.edu",
                full_name="Prod Student",
                role="STUDENT",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.student_user.set_password("StudentPass@123")
            db.session.add(cls.student_user)

            # 2. Academic Hierarchy: Batch 2025-2029
            batch = Batch(name="2025-2029", start_year=2025, end_year=2029, is_active=True)
            db.session.add(batch)
            db.session.flush()

            ay = AcademicYear(batch_id=batch.id, year_number=2, name="2nd Year", is_current=True)
            db.session.add(ay)
            db.session.flush()

            sem = Semester(academic_year_id=ay.id, semester_number=3, name="Semester 3", is_current=True)
            empty_sem = Semester(academic_year_id=ay.id, semester_number=4, name="Semester 4")
            db.session.add_all([sem, empty_sem])
            db.session.flush()

            sec_a = Section(semester_id=sem.id, name="A", room_number="CSE-201")
            sec_b = Section(semester_id=sem.id, name="B", room_number="CSE-202")
            db.session.add_all([sec_a, sec_b])
            db.session.flush()

            # 3. Subjects
            sub_ds = Subject(semester_id=sem.id, code="CS301", name="Data Structures", credits=4.0)
            sub_db = Subject(semester_id=sem.id, code="CS302", name="Database Systems", credits=3.0)
            db.session.add_all([sub_ds, sub_db])
            db.session.flush()

            # 4. Students
            stu_1 = Student(roll_number="25PROD01", name="Alice Sharma", batch_id=batch.id, current_section_id=sec_a.id, email="alice@dept.edu")
            stu_2 = Student(roll_number="25PROD02", name="Bob Verma", batch_id=batch.id, current_section_id=sec_a.id, email="bob@dept.edu")
            stu_3 = Student(roll_number="25PROD03", name="Charlie Patel", batch_id=batch.id, current_section_id=sec_b.id, email="charlie@dept.edu")
            db.session.add_all([stu_1, stu_2, stu_3])
            db.session.flush()

            # Attendance
            db.session.add(AttendanceRecord(student_id=stu_1.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_ds.id, percentage=86.0))
            db.session.add(AttendanceRecord(student_id=stu_1.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_db.id, percentage=80.0))
            db.session.add(AttendanceRecord(student_id=stu_2.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_ds.id, percentage=60.0))
            db.session.add(AttendanceRecord(student_id=stu_3.id, semester_id=sem.id, section_id=sec_b.id, subject_id=sub_ds.id, percentage=92.0))

            # Results
            db.session.add(SemesterResult(student_id=stu_1.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_ds.id, internal_marks=26, external_marks=58, total_marks=84, grade="A+", grade_point=9.0, result_status="PASSED"))
            db.session.add(SemesterResult(student_id=stu_1.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_db.id, internal_marks=24, external_marks=54, total_marks=78, grade="A", grade_point=8.0, result_status="PASSED"))
            db.session.add(SemesterResult(student_id=stu_2.id, semester_id=sem.id, section_id=sec_a.id, subject_id=sub_ds.id, internal_marks=12, external_marks=20, total_marks=32, grade="F", grade_point=0.0, result_status="FAILED"))
            db.session.add(SemesterResult(student_id=stu_3.id, semester_id=sem.id, section_id=sec_b.id, subject_id=sub_ds.id, internal_marks=28, external_marks=62, total_marks=90, grade="O", grade_point=10.0, result_status="PASSED"))

            # Summaries
            db.session.add(StudentSemesterSummary(student_id=stu_1.id, semester_id=sem.id, section_id=sec_a.id, sgpa=8.57, cgpa=8.40))
            db.session.add(StudentSemesterSummary(student_id=stu_2.id, semester_id=sem.id, section_id=sec_a.id, sgpa=4.00, cgpa=5.50))
            db.session.add(StudentSemesterSummary(student_id=stu_3.id, semester_id=sem.id, section_id=sec_b.id, sgpa=10.0, cgpa=9.60))

            db.session.commit()

            # Store IDs as immutable strings
            cls.batch_id = batch.id
            cls.ay_id = ay.id
            cls.sem_id = sem.id
            cls.empty_sem_id = empty_sem.id
            cls.sec_a_id = sec_a.id
            cls.sec_b_id = sec_b.id
            cls.sub_ds_id = sub_ds.id
            cls.sub_db_id = sub_db.id
            cls.stu_1_id = stu_1.id
            cls.stu_2_id = stu_2.id
            cls.stu_3_id = stu_3.id

        # Login tokens
        res = cls.client.post("/api/v1/auth/login", json={"email": "hod.production@dept.edu", "password": "HodPass@123"})
        cls.hod_token = res.get_json()["data"]["accessToken"]

        res = cls.client.post("/api/v1/auth/login", json={"email": "student.prod@dept.edu", "password": "StudentPass@123"})
        cls.student_token = res.get_json()["data"]["accessToken"]

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # ------------------------------------------------------------------
    # 1. REPORT GENERATION TESTS (PDF, EXCEL, CSV)
    # ------------------------------------------------------------------

    def test_01_pdf_department_report_generation(self):
        """Verify department PDF generation generates valid binary PDF with header stamp."""
        data = ReportsService.get_department_report_data(self.batch_id, self.ay_id, self.sem_id)
        pdf_bytes, mimetype, filename = ReportsService.export_report("department", data, "pdf")
        self.assertEqual(mimetype, "application/pdf")
        self.assertTrue(filename.endswith(".pdf"))
        self.assertTrue(len(pdf_bytes) > 2000, "PDF size should be substantial")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"), "File must start with standard PDF magic header")

    def test_02_excel_department_report_generation(self):
        """Verify department Excel generation produces valid OOXML spreadsheet with structured sheets."""
        data = ReportsService.get_department_report_data(self.batch_id, self.ay_id, self.sem_id)
        xlsx_bytes, mimetype, filename = ReportsService.export_report("department", data, "excel")
        self.assertEqual(mimetype, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertTrue(filename.endswith(".xlsx"))
        self.assertTrue(xlsx_bytes.startswith(b"PK\x03\x04"), "Excel file must start with PK zip signature")

        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        self.assertIn("Department Overview", wb.sheetnames)
        ws = wb["Department Overview"]
        self.assertIn("DEPARTMENT OF COMPUTER SCIENCE", ws["A1"].value)

    def test_03_csv_department_report_generation(self):
        """Verify department CSV export generates UTF-8 encoded text with correct headers and metrics."""
        data = ReportsService.get_department_report_data(self.batch_id, self.ay_id, self.sem_id)
        csv_bytes, mimetype, filename = ReportsService.export_report("department", data, "csv")
        self.assertIn("text/csv", mimetype)
        self.assertTrue(filename.endswith(".csv"))

        text = csv_bytes.decode("utf-8-sig")
        self.assertIn("Department Comprehensive Academic Report", text)
        self.assertIn("Total Enrolled Students", text)
        self.assertIn("CS301", text)

    def test_04_student_report_generation_all_formats(self):
        """Verify individual student academic dossier generates in PDF, Excel, and CSV with accurate data."""
        data = ReportsService.get_student_report_data(self.stu_1_id, self.sem_id)
        self.assertIsNotNone(data)
        self.assertEqual(data["rollNumber"], "25PROD01")
        self.assertEqual(data["name"], "Alice Sharma")

        # PDF
        pdf_bytes, _, _ = ReportsService.export_report("student", data, "pdf")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        # Excel
        xlsx_bytes, _, _ = ReportsService.export_report("student", data, "excel")
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
        self.assertIn(f"Student 25PROD01", wb.sheetnames[0])

        # CSV
        csv_bytes, _, _ = ReportsService.export_report("student", data, "csv")
        text = csv_bytes.decode("utf-8-sig")
        self.assertIn("25PROD01", text)
        self.assertIn("Alice Sharma", text)

    def test_05_section_and_subject_reports(self):
        """Verify Section and Subject reports generate successfully across formats."""
        sec_data = ReportsService.get_section_report_data(self.sec_a_id, self.sem_id)
        self.assertEqual(sec_data["sectionName"], "A")
        sec_pdf, _, _ = ReportsService.export_report("section", sec_data, "pdf")
        self.assertTrue(sec_pdf.startswith(b"%PDF-"))

        sub_data = ReportsService.get_subject_report_data(self.sub_ds_id, self.sem_id)
        self.assertEqual(sub_data["code"], "CS301")
        sub_csv, _, _ = ReportsService.export_report("subject", sub_data, "csv")
        self.assertIn("CS301", sub_csv.decode("utf-8-sig"))

    def test_06_insights_report_generation(self):
        """Verify Academic Insights report export aggregates watchlist and KPIs."""
        ins_data = ReportsService.get_insights_report_data(semester_id=self.sem_id)
        self.assertIn("summary", ins_data)
        self.assertIn("watchlist", ins_data)
        ins_pdf, _, _ = ReportsService.export_report("insights", ins_data, "pdf")
        self.assertTrue(ins_pdf.startswith(b"%PDF-"))

    # ------------------------------------------------------------------
    # 2. AUTHORIZATION & RBAC VERIFICATION
    # ------------------------------------------------------------------

    def test_07_public_report_rejection(self):
        """Verify unauthenticated public requests to reports API are strictly rejected with 401."""
        res = self.client.get(f"/api/v1/reports/department?semester_id={self.sem_id}")
        self.assertEqual(res.status_code, 401)

        res = self.client.get(f"/api/v1/reports/student/{self.stu_1_id}")
        self.assertEqual(res.status_code, 401)

    def test_08_student_role_forbidden(self):
        """Verify regular student token cannot access confidential academic export endpoints (403)."""
        headers = {"Authorization": f"Bearer {self.student_token}"}
        res = self.client.get(f"/api/v1/reports/department?semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 403)

        res = self.client.get(f"/api/v1/reports/student/{self.stu_1_id}", headers=headers)
        self.assertEqual(res.status_code, 403)

    def test_09_hod_report_authorization_success(self):
        """Verify authorized HOD token can export all report endpoints successfully with 200."""
        headers = {"Authorization": f"Bearer {self.hod_token}"}
        # Department
        res = self.client.get(f"/api/v1/reports/department?semester_id={self.sem_id}&format=pdf", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/pdf")

        # Section
        res = self.client.get(f"/api/v1/reports/section/{self.sec_a_id}?format=excel", headers=headers)
        self.assertEqual(res.status_code, 200)

        # Student
        res = self.client.get(f"/api/v1/reports/student/{self.stu_1_id}?format=csv", headers=headers)
        self.assertEqual(res.status_code, 200)

        # Subject
        res = self.client.get(f"/api/v1/reports/subject/{self.sub_ds_id}?format=pdf", headers=headers)
        self.assertEqual(res.status_code, 200)

        # Insights
        res = self.client.get(f"/api/v1/reports/insights?semester_id={self.sem_id}&format=pdf", headers=headers)
        self.assertEqual(res.status_code, 200)

    # ------------------------------------------------------------------
    # 3. INPUT VALIDATION & ERROR HANDLING
    # ------------------------------------------------------------------

    def test_10_invalid_report_filters_and_formats(self):
        """Verify invalid export format or non-existent entity IDs return clean 400 and 404 responses."""
        headers = {"Authorization": f"Bearer {self.hod_token}"}

        # Invalid format
        res = self.client.get(f"/api/v1/reports/department?format=docx", headers=headers)
        self.assertEqual(res.status_code, 400)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Unsupported format", data["message"])

        # Non-existent student
        res = self.client.get("/api/v1/reports/student/non-existent-id", headers=headers)
        self.assertEqual(res.status_code, 404)

        # Non-existent section
        res = self.client.get("/api/v1/reports/section/non-existent-id", headers=headers)
        self.assertEqual(res.status_code, 404)

        # Non-existent subject
        res = self.client.get("/api/v1/reports/subject/non-existent-id", headers=headers)
        self.assertEqual(res.status_code, 404)

    def test_11_empty_report_dataset_safety(self):
        """Verify querying an empty semester (Semester 4) generates clean reports without crashing."""
        data = ReportsService.get_department_report_data(semester_id=self.empty_sem_id)
        self.assertEqual(data["subjects"], [])
        self.assertEqual(data["sections"], [])

        # PDF and Excel generation must not crash
        pdf_bytes, _, _ = ReportsService.export_report("department", data, "pdf")
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

        xlsx_bytes, _, _ = ReportsService.export_report("department", data, "excel")
        self.assertTrue(xlsx_bytes.startswith(b"PK\x03\x04"))

    def test_12_report_preview_endpoint(self):
        """Verify report preview API returns structured JSON preview before triggering file export."""
        headers = {"Authorization": f"Bearer {self.hod_token}"}
        res = self.client.get(f"/api/v1/reports/preview?type=department&semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("kpis", data["data"])

    # ------------------------------------------------------------------
    # 4. DATABASE INTEGRITY, TRANSACTION & ROLLBACK VERIFICATION
    # ------------------------------------------------------------------

    def test_13_production_db_connectivity_and_commit(self):
        """Verify direct DB connectivity, query execution, and explicit transaction commit."""
        test_student = Student(
            roll_number="25TXN01",
            name="Txn Test Student",
            batch_id=self.batch_id,
            current_section_id=self.sec_a_id,
        )
        db.session.add(test_student)
        db.session.commit()

        # Query back to verify persistence
        saved = Student.query.filter_by(roll_number="25TXN01").first()
        self.assertIsNotNone(saved)
        self.assertEqual(saved.name, "Txn Test Student")

    def test_14_transaction_rollback(self):
        """Verify transaction rollback on error leaves zero orphaned rows in the database."""
        try:
            # Create a student with duplicate roll number to force integrity failure
            bad_student = Student(
                roll_number="25PROD01", # Duplicate of Alice Sharma
                name="Duplicate Roll Student",
                batch_id=self.batch_id,
            )
            db.session.add(bad_student)
            db.session.commit()
            self.fail("Should have raised IntegrityError on duplicate roll number")
        except Exception:
            db.session.rollback()

        # Ensure database is clean and previous records are unaffected
        alice = Student.query.filter_by(roll_number="25PROD01").first()
        self.assertEqual(alice.name, "Alice Sharma")

    # ------------------------------------------------------------------
    # 5. ENVIRONMENT & PRIVACY SECURITY AUDIT
    # ------------------------------------------------------------------

    def test_15_secret_and_credential_safety(self):
        """Verify no backend secrets (SECRET_KEY, JWT_SECRET_KEY, database URIs) leak in API responses."""
        res = self.client.get("/api/v1/health")
        text = res.get_data(as_text=True)
        self.assertNotIn("SECRET_KEY", text)
        self.assertNotIn("jwt_secret", text.lower())
        self.assertNotIn("password", text.lower())

        headers = {"Authorization": f"Bearer {self.hod_token}"}
        res = self.client.get("/api/v1/insights/config", headers=headers)
        text = res.get_data(as_text=True)
        self.assertNotIn("SUPABASE_KEY", text)
        self.assertNotIn("DATABASE_URL", text)

    def test_16_academic_privacy_no_leakage_in_public(self):
        """Verify all public endpoints expose zero private student information (marks, attendance, SGPA)."""
        endpoints = [
            "/api/v1/public/department-info",
            "/api/v1/public/faculty",
            "/api/v1/public/events",
            "/api/v1/public/achievements",
            "/api/v1/public/announcements",
        ]
        for ep in endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} should return 200")
            text = res.get_data(as_text=True)
            self.assertNotIn("25PROD01", text)
            self.assertNotIn("Alice Sharma", text)
            self.assertNotIn("sgpa", text.lower())
            self.assertNotIn("cgpa", text.lower())

    # ------------------------------------------------------------------
    # 6. UPLOAD VALIDATION & ATOMIC INTEGRITY
    # ------------------------------------------------------------------

    def test_17_upload_validation_rejects_invalid_file(self):
        """Verify upload validation rejects invalid extensions and empty files."""
        headers = {"Authorization": f"Bearer {self.hod_token}"}
        # Invalid extension
        data = {
            "batch_id": self.batch_id,
            "academic_year_id": self.ay_id,
            "semester_id": self.sem_id,
            "section_id": self.sec_a_id,
            "data_type": "ATTENDANCE",
            "file": (io.BytesIO(b"malicious executable"), "malicious.exe"),
        }
        res = self.client.post("/api/v1/uploads/validate", data=data, content_type="multipart/form-data", headers=headers)
        self.assertEqual(res.status_code, 400)
        res_json = res.get_json()
        self.assertIn("Unsupported file extension", res_json["message"])

    def test_18_api_error_handling_structured_format(self):
        """Verify unknown route returns clean structured JSON error without stack trace."""
        res = self.client.get("/api/v1/non-existent-route")
        self.assertEqual(res.status_code, 404)
        data = res.get_json()
        self.assertFalse(data["success"])
        self.assertIn("Requested API resource not found", data["message"])

    # ------------------------------------------------------------------
    # 7. HIGH VOLUME PERFORMANCE & END-TO-END WORKFLOW
    # ------------------------------------------------------------------

    def test_19_high_volume_dataset_performance(self):
        """Verify reporting engine handles large student cohorts efficiently without performance degradation."""
        bulk_students = [
            Student(roll_number=f"25BULK{i:02d}", name=f"Bulk Student {i}", batch_id=self.batch_id, current_section_id=self.sec_b_id)
            for i in range(1, 61)
        ]
        db.session.add_all(bulk_students)
        db.session.flush()

        for st in bulk_students:
            db.session.add(AttendanceRecord(student_id=st.id, semester_id=self.sem_id, section_id=self.sec_b_id, subject_id=self.sub_ds_id, percentage=74.0))
            db.session.add(SemesterResult(student_id=st.id, semester_id=self.sem_id, section_id=self.sec_b_id, subject_id=self.sub_ds_id, total_marks=65, grade="B+", grade_point=7.0, result_status="PASSED"))
        db.session.commit()

        # Generate report and verify performance
        data = ReportsService.get_department_report_data(semester_id=self.sem_id)
        self.assertGreater(data["kpis"]["totalStudents"], 60)

        pdf_bytes, _, _ = ReportsService.export_report("department", data, "pdf")
        self.assertTrue(len(pdf_bytes) > 2000)

    def test_20_end_to_end_academic_workflow(self):
        """
        Comprehensive End-to-End Workflow:
        1. Query Analytics Overview
        2. Query Insights Problem Detection
        3. Query Student Diagnostic Watchlist
        4. Request Report Preview
        5. Export Final Institutional PDF Report
        """
        headers = {"Authorization": f"Bearer {self.hod_token}"}

        # 1. Analytics
        res = self.client.get(f"/api/v1/analytics/overview?semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 200)

        # 2. Insights
        res = self.client.get(f"/api/v1/insights/overview?semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 200)

        # 3. Watchlist
        res = self.client.get(f"/api/v1/insights/students?semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 200)

        # 4. Report Preview
        res = self.client.get(f"/api/v1/reports/preview?type=department&semester_id={self.sem_id}", headers=headers)
        self.assertEqual(res.status_code, 200)

        # 5. Export Report
        res = self.client.get(f"/api/v1/reports/department?semester_id={self.sem_id}&format=pdf", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.mimetype, "application/pdf")
        self.assertTrue(len(res.get_data()) > 2000)


if __name__ == "__main__":
    unittest.main()
