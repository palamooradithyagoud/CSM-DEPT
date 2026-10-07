import io
import os
import unittest
from app import create_app
from app.extensions import db
from app.models.user import User
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
    UploadHistory,
)
from app.services.ingestion_service import IngestionService, TEMP_UPLOAD_CACHE


class Phase2AcademicTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

            # Create test HOD
            cls.hod = User(
                email="hod.test@dept.edu",
                full_name="Dr. Test HOD",
                role="HOD",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.hod.set_password("TestPass@123")
            db.session.add(cls.hod)

            # Create test Batch
            cls.batch = Batch(
                name="2025-2029",
                start_year=2025,
                end_year=2029,
                is_active=True,
            )
            db.session.add(cls.batch)
            db.session.flush()

            cls.ay2 = AcademicYear(
                batch_id=cls.batch.id,
                year_number=2,
                name="2nd Year",
                calendar_year="2026-2027",
                is_current=True,
            )
            db.session.add(cls.ay2)
            db.session.flush()

            cls.sem3 = Semester(
                academic_year_id=cls.ay2.id,
                semester_number=3,
                name="Semester 3",
                is_current=True,
            )
            db.session.add(cls.sem3)
            db.session.flush()

            cls.sec_a = Section(
                semester_id=cls.sem3.id,
                name="A",
                room_number="Room-A-303",
            )
            cls.sec_b = Section(
                semester_id=cls.sem3.id,
                name="B",
                room_number="Room-B-303",
            )
            db.session.add_all([cls.sec_a, cls.sec_b])
            db.session.flush()

            cls.subj_ds = Subject(
                semester_id=cls.sem3.id,
                code="A9503",
                name="Data Structures using C++",
                short_name="DS",
                credits=4.0,
                subject_type="THEORY",
                is_active=True,
            )
            cls.subj_ec = Subject(
                semester_id=cls.sem3.id,
                code="A9009",
                name="Engineering Chemistry",
                short_name="EC",
                credits=3.0,
                subject_type="THEORY",
                is_active=True,
            )
            db.session.add_all([cls.subj_ds, cls.subj_ec])
            db.session.flush()

            # Add two test students
            cls.stu_1 = Student(
                roll_number="25881A6601",
                name="Student Alpha",
                batch_id=cls.batch.id,
                current_section_id=cls.sec_a.id,
                is_active=True,
            )
            cls.stu_2 = Student(
                roll_number="25881A6666",
                name="Student Beta",
                batch_id=cls.batch.id,
                current_section_id=cls.sec_b.id,
                is_active=True,
            )
            db.session.add_all([cls.stu_1, cls.stu_2])
            db.session.commit()

            # Store IDs for tests
            cls.batch_id = cls.batch.id
            cls.ay_id = cls.ay2.id
            cls.sem_id = cls.sem3.id
            cls.sec_a_id = cls.sec_a.id
            cls.sec_b_id = cls.sec_b.id
            cls.subj_ds_id = cls.subj_ds.id
            cls.stu_1_id = cls.stu_1.id

    def setUp(self):
        # Obtain auth token for HOD
        resp = self.client.post(
            "/api/v1/auth/login",
            json={"email": "hod.test@dept.edu", "password": "TestPass@123"},
        )
        self.assertEqual(resp.status_code, 200)
        self.hod_token = resp.get_json()["data"]["accessToken"]
        self.auth_headers = {"Authorization": f"Bearer {self.hod_token}"}

    def test_01_security_unauthenticated_blocked(self):
        """Verify unauthenticated requests to academic endpoints are strictly rejected with 401."""
        endpoints = [
            "/api/v1/batches",
            "/api/v1/students",
            "/api/v1/subjects",
            "/api/v1/academic-data/availability",
            "/api/v1/uploads/history",
        ]
        for ep in endpoints:
            resp = self.client.get(ep)
            self.assertEqual(resp.status_code, 401, f"Expected 401 for {ep}")

    def test_02_hierarchy_traversal(self):
        """Verify navigation through Batch -> Academic Year -> Semester -> Section."""
        resp = self.client.get("/api/v1/batches", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertGreaterEqual(len(data), 1)

        resp_ay = self.client.get(f"/api/v1/academic-years?batch_id={self.batch_id}", headers=self.auth_headers)
        self.assertEqual(resp_ay.status_code, 200)
        ay_data = resp_ay.get_json()["data"]
        self.assertEqual(ay_data[0]["yearNumber"], 2)

        resp_sem = self.client.get(f"/api/v1/semesters?academic_year_id={self.ay_id}", headers=self.auth_headers)
        self.assertEqual(resp_sem.status_code, 200)
        sem_data = resp_sem.get_json()["data"]
        self.assertEqual(sem_data[0]["semesterNumber"], 3)

        resp_sec = self.client.get(f"/api/v1/sections?semester_id={self.sem_id}", headers=self.auth_headers)
        self.assertEqual(resp_sec.status_code, 200)
        sec_names = [s["name"] for s in resp_sec.get_json()["data"]]
        self.assertIn("A", sec_names)
        self.assertIn("B", sec_names)

    def test_03_student_search_and_filter(self):
        """Verify student search by roll number/name and section filter."""
        resp = self.client.get(f"/api/v1/students?search=Alpha", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        res = resp.get_json()
        self.assertEqual(res["total"], 1)
        self.assertEqual(res["data"][0]["rollNumber"], "25881A6601")

        # Filter by Section B
        resp_b = self.client.get(f"/api/v1/students?section_id={self.sec_b_id}", headers=self.auth_headers)
        self.assertEqual(resp_b.status_code, 200)
        rolls = [s["rollNumber"] for s in resp_b.get_json()["data"]]
        self.assertIn("25881A6666", rolls)
        self.assertNotIn("25881A6601", rolls)

    def test_04_student_detail_profile(self):
        """Verify student profile loads without crashing and accurately returns verified records."""
        resp = self.client.get(f"/api/v1/students/{self.stu_1_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        profile = resp.get_json()["data"]
        self.assertEqual(profile["rollNumber"], "25881A6601")
        self.assertIn("attendanceRecords", profile)
        self.assertIn("assessmentRecords", profile)
        self.assertIn("semesterResults", profile)

    def test_05_upload_validation_valid_csv(self):
        """Verify CSV upload validation passes for valid tabular attendance data."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6601,Student Alpha,A9503,88.5\n"
        )
        data = {
            "batchId": self.batch_id,
            "academicYearId": self.ay_id,
            "semesterId": self.sem_id,
            "sectionId": self.sec_a_id,
            "dataType": "ATTENDANCE",
            "file": (io.BytesIO(csv_content.encode("utf-8")), "valid_test.csv"),
        }
        resp = self.client.post(
            "/api/v1/uploads/validate",
            data=data,
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertTrue(body["success"])
        self.assertEqual(body["summary"]["validRows"], 1)
        self.assertEqual(body["summary"]["invalidRows"], 0)
        self.assertIn("fileToken", body)

    def test_06_upload_validation_rejects_wrong_section(self):
        """Verify validation rejects row if student belongs to Section B but uploaded to Section A."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6666,Student Beta,A9503,90.0\n"  # 25881A6666 is registered in Section B
        )
        data = {
            "batchId": self.batch_id,
            "academicYearId": self.ay_id,
            "semesterId": self.sem_id,
            "sectionId": self.sec_a_id,  # Target is Section A
            "dataType": "ATTENDANCE",
            "file": (io.BytesIO(csv_content.encode("utf-8")), "wrong_section.csv"),
        }
        resp = self.client.post(
            "/api/v1/uploads/validate",
            data=data,
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["summary"]["invalidRows"], 1)
        self.assertTrue(any("belongs to Section" in err for err in body["errors"]))

    def test_07_upload_validation_rejects_invalid_percentage(self):
        """Verify validation rejects attendance > 100."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6601,Student Alpha,A9503,145.0\n"
        )
        data = {
            "batchId": self.batch_id,
            "academicYearId": self.ay_id,
            "semesterId": self.sem_id,
            "sectionId": self.sec_a_id,
            "dataType": "ATTENDANCE",
            "file": (io.BytesIO(csv_content.encode("utf-8")), "invalid_pct.csv"),
        }
        resp = self.client.post(
            "/api/v1/uploads/validate",
            data=data,
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["summary"]["invalidRows"], 1)
        self.assertTrue(any("out of valid bounds" in err for err in body["errors"]))

    def test_08_upload_validation_rejects_unconfigured_subject(self):
        """Verify validation rejects subject typo or subject not belonging to semester."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6601,Student Alpha,NOT_A_SUBJECT,80.0\n"
        )
        data = {
            "batchId": self.batch_id,
            "academicYearId": self.ay_id,
            "semesterId": self.sem_id,
            "sectionId": self.sec_a_id,
            "dataType": "ATTENDANCE",
            "file": (io.BytesIO(csv_content.encode("utf-8")), "invalid_subj.csv"),
        }
        resp = self.client.post(
            "/api/v1/uploads/validate",
            data=data,
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.get_json()
        self.assertEqual(body["summary"]["invalidRows"], 1)
        self.assertTrue(any("not configured" in err for err in body["errors"]))

    def test_09_transactional_confirm_and_history(self):
        """Verify confirmation imports records atomically, creates audit history, and updates availability."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6601,Student Alpha,A9503,85.0\n"
        )
        val_resp = self.client.post(
            "/api/v1/uploads/validate",
            data={
                "batchId": self.batch_id,
                "academicYearId": self.ay_id,
                "semesterId": self.sem_id,
                "sectionId": self.sec_a_id,
                "dataType": "ATTENDANCE",
                "file": (io.BytesIO(csv_content.encode("utf-8")), "import_test.csv"),
            },
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        file_token = val_resp.get_json()["fileToken"]

        # Confirm import
        conf_resp = self.client.post(
            "/api/v1/uploads/confirm",
            json={"fileToken": file_token, "duplicateStrategy": "SKIP"},
            headers=self.auth_headers,
        )
        self.assertEqual(conf_resp.status_code, 200)
        self.assertTrue(conf_resp.get_json()["success"])

        # Check database record
        with self.app.app_context():
            rec = AttendanceRecord.query.filter_by(
                student_id=self.stu_1_id, semester_id=self.sem_id, subject_id=self.subj_ds_id
            ).first()
            self.assertIsNotNone(rec)
            self.assertEqual(rec.percentage, 85.0)

        # Check Upload History
        hist_resp = self.client.get("/api/v1/uploads/history", headers=self.auth_headers)
        self.assertEqual(hist_resp.status_code, 200)
        hist_data = hist_resp.get_json()["data"]
        self.assertGreaterEqual(len(hist_data), 1)
        self.assertEqual(hist_data[0]["status"], "IMPORTED")

        # Check Data Availability
        avail_resp = self.client.get(
            f"/api/v1/academic-data/availability?semester_id={self.sem_id}&section_id={self.sec_a_id}",
            headers=self.auth_headers,
        )
        self.assertEqual(avail_resp.status_code, 200)
        avail = avail_resp.get_json()["data"]
        self.assertTrue(avail["attendance"]["available"])
        self.assertEqual(avail["attendance"]["recordCount"], 1)

    def test_10_duplicate_prevention_and_replace_strategy(self):
        """Verify duplicate detection and transactional replace behavior."""
        csv_content = (
            "Roll Number,Student Name,Subject Code,Attendance %\n"
            "25881A6601,Student Alpha,A9503,96.5\n"  # Update to 96.5%
        )
        val_resp = self.client.post(
            "/api/v1/uploads/validate",
            data={
                "batchId": self.batch_id,
                "academicYearId": self.ay_id,
                "semesterId": self.sem_id,
                "sectionId": self.sec_a_id,
                "dataType": "ATTENDANCE",
                "file": (io.BytesIO(csv_content.encode("utf-8")), "dup_test.csv"),
            },
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        body = val_resp.get_json()
        self.assertEqual(body["summary"]["duplicatesCount"], 1)

        file_token = body["fileToken"]
        # Confirm with REPLACE
        conf_resp = self.client.post(
            "/api/v1/uploads/confirm",
            json={"fileToken": file_token, "duplicateStrategy": "REPLACE"},
            headers=self.auth_headers,
        )
        self.assertEqual(conf_resp.status_code, 200)

        # Check updated percentage
        with self.app.app_context():
            rec = AttendanceRecord.query.filter_by(
                student_id=self.stu_1_id, semester_id=self.sem_id, subject_id=self.subj_ds_id
            ).first()
            self.assertEqual(rec.percentage, 96.5)

    def test_11_mid_and_results_upload(self):
        """Verify Mid assessments and Semester Results handling without fake data."""
        # Mid assessment
        csv_mid = (
            "Roll Number,Student Name,Subject Code,Marks Obtained,Max Marks\n"
            "25881A6601,Student Alpha,A9503,27,30\n"
        )
        val_mid = self.client.post(
            "/api/v1/uploads/validate",
            data={
                "batchId": self.batch_id,
                "academicYearId": self.ay_id,
                "semesterId": self.sem_id,
                "sectionId": self.sec_a_id,
                "dataType": "MID_1",
                "file": (io.BytesIO(csv_mid.encode("utf-8")), "mid1.csv"),
            },
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        tok_mid = val_mid.get_json()["fileToken"]
        self.client.post(
            "/api/v1/uploads/confirm",
            json={"fileToken": tok_mid, "duplicateStrategy": "SKIP"},
            headers=self.auth_headers,
        )

        # Semester Result
        csv_res = (
            "Roll Number,Student Name,Subject Code,Internal,External,Total,Grade,Grade Point,SGPA\n"
            "25881A6601,Student Alpha,A9503,28,65,93,A+,9.0,8.75\n"
        )
        val_res = self.client.post(
            "/api/v1/uploads/validate",
            data={
                "batchId": self.batch_id,
                "academicYearId": self.ay_id,
                "semesterId": self.sem_id,
                "sectionId": self.sec_a_id,
                "dataType": "SEMESTER_RESULT",
                "file": (io.BytesIO(csv_res.encode("utf-8")), "results.csv"),
            },
            content_type="multipart/form-data",
            headers=self.auth_headers,
        )
        tok_res = val_res.get_json()["fileToken"]
        self.client.post(
            "/api/v1/uploads/confirm",
            json={"fileToken": tok_res, "duplicateStrategy": "SKIP"},
            headers=self.auth_headers,
        )

        with self.app.app_context():
            mid_rec = AssessmentRecord.query.filter_by(
                student_id=self.stu_1_id, assessment_type="MID_1"
            ).first()
            self.assertIsNotNone(mid_rec)
            self.assertEqual(mid_rec.marks_obtained, 27.0)

            res_rec = SemesterResult.query.filter_by(student_id=self.stu_1_id).first()
            self.assertIsNotNone(res_rec)
            self.assertEqual(res_rec.grade, "A+")
            self.assertEqual(res_rec.grade_point, 9.0)


if __name__ == "__main__":
    unittest.main()
