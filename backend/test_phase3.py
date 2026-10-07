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
    SemesterResult,
    StudentSemesterSummary,
)
from app.analytics.service import AnalyticsService
from app.analytics.correlation import AnalyticsCorrelation


class Phase3AnalyticsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

            # 1. Create HOD User & Regular Student User
            cls.hod = User(
                email="hod.analytics@dept.edu",
                full_name="Dr. Analytics HOD",
                role="HOD",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.hod.set_password("HodPass@123")
            db.session.add(cls.hod)

            cls.student_user = User(
                email="student.test@dept.edu",
                full_name="Student Test",
                role="STUDENT",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.student_user.set_password("StudentPass@123")
            db.session.add(cls.student_user)

            # 2. Create Batch 2025-2029
            cls.batch = Batch(
                name="2025-2029",
                start_year=2025,
                end_year=2029,
                is_active=True,
            )
            db.session.add(cls.batch)
            db.session.flush()

            # 3. Create Academic Year 1 & 2
            cls.ay1 = AcademicYear(batch_id=cls.batch.id, year_number=1, name="1st Year")
            cls.ay2 = AcademicYear(batch_id=cls.batch.id, year_number=2, name="2nd Year", is_current=True)
            db.session.add_all([cls.ay1, cls.ay2])
            db.session.flush()

            # 4. Create Semesters: Sem 1, Sem 2, Sem 3
            cls.sem1 = Semester(academic_year_id=cls.ay1.id, semester_number=1, name="Semester 1")
            cls.sem2 = Semester(academic_year_id=cls.ay1.id, semester_number=2, name="Semester 2")
            cls.sem3 = Semester(academic_year_id=cls.ay2.id, semester_number=3, name="Semester 3", is_current=True)
            cls.sem4 = Semester(academic_year_id=cls.ay2.id, semester_number=4, name="Semester 4")  # Empty for availability tests
            db.session.add_all([cls.sem1, cls.sem2, cls.sem3, cls.sem4])
            db.session.flush()

            # 5. Create Sections for Sem 3: Section A, Section B
            cls.sec_a = Section(semester_id=cls.sem3.id, name="A", room_number="301")
            cls.sec_b = Section(semester_id=cls.sem3.id, name="B", room_number="302")
            db.session.add_all([cls.sec_a, cls.sec_b])
            db.session.flush()

            # 6. Create Subjects for Sem 3
            cls.sub_ds = Subject(semester_id=cls.sem3.id, code="A9503", name="Data Structures", credits=4.0)
            cls.sub_ec = Subject(semester_id=cls.sem3.id, code="A9009", name="Engineering Chemistry", credits=3.0)
            db.session.add_all([cls.sub_ds, cls.sub_ec])
            db.session.flush()

            # 7. Create Controlled Fixture Students:
            # Student A, B, C (Controlled semester comparison fixture):
            # Student A: Sem 1 = 7.5, Sem 2 = 8.2 => +0.7 IMPROVED
            # Student B: Sem 1 = 8.4, Sem 2 = 8.1 => -0.3 DECLINED
            # Student C: Sem 1 = 7.9, Sem 2 = 7.9 => 0.0 STABLE
            # Plus Students D, E, F to test correlation & section comparison
            cls.stu_a = Student(roll_number="25A001", name="Student Alpha", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            cls.stu_b = Student(roll_number="25A002", name="Student Beta", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            cls.stu_c = Student(roll_number="25A003", name="Student Gamma", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            cls.stu_d = Student(roll_number="25A004", name="Student Delta", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            cls.stu_e = Student(roll_number="25A005", name="Student Epsilon", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            cls.stu_f = Student(roll_number="25A006", name="Student Zeta", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            db.session.add_all([cls.stu_a, cls.stu_b, cls.stu_c, cls.stu_d, cls.stu_e, cls.stu_f])
            db.session.flush()

            # Controlled summaries for Sem 1 & Sem 2:
            db.session.add_all([
                StudentSemesterSummary(student_id=cls.stu_a.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=7.5, cgpa=7.5),
                StudentSemesterSummary(student_id=cls.stu_a.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=8.2, cgpa=7.85),
                StudentSemesterSummary(student_id=cls.stu_b.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=8.4, cgpa=8.4),
                StudentSemesterSummary(student_id=cls.stu_b.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=8.1, cgpa=8.25),
                StudentSemesterSummary(student_id=cls.stu_c.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=7.9, cgpa=7.9),
                StudentSemesterSummary(student_id=cls.stu_c.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=7.9, cgpa=7.9),
            ])

            # Summaries for Sem 3:
            db.session.add_all([
                StudentSemesterSummary(student_id=cls.stu_a.id, semester_id=cls.sem3.id, section_id=cls.sec_a.id, sgpa=8.5, cgpa=8.07),
                StudentSemesterSummary(student_id=cls.stu_b.id, semester_id=cls.sem3.id, section_id=cls.sec_a.id, sgpa=8.0, cgpa=8.17),
                StudentSemesterSummary(student_id=cls.stu_c.id, semester_id=cls.sem3.id, section_id=cls.sec_a.id, sgpa=7.5, cgpa=7.77),
                StudentSemesterSummary(student_id=cls.stu_d.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, sgpa=9.0, cgpa=9.0),
                StudentSemesterSummary(student_id=cls.stu_e.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, sgpa=8.8, cgpa=8.8),
                StudentSemesterSummary(student_id=cls.stu_f.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, sgpa=6.2, cgpa=6.2),
            ])

            # Attendance records for Sem 3 in Data Structures (sub_ds) - 6 samples for correlation testing:
            # High attendance -> high marks correlation pairing
            attendance_fixtures = [
                (cls.stu_a, 92.0, 88.0, "A+", 9.0, cls.sec_a.id),
                (cls.stu_b, 85.0, 78.0, "A", 8.0, cls.sec_a.id),
                (cls.stu_c, 74.0, 68.0, "B+", 7.0, cls.sec_a.id),
                (cls.stu_d, 96.0, 94.0, "O", 10.0, cls.sec_b.id),
                (cls.stu_e, 90.0, 86.0, "A+", 9.0, cls.sec_b.id),
                (cls.stu_f, 62.0, 48.0, "F", 0.0, cls.sec_b.id),  # 1 fail in Section B
            ]
            for stu, att_pct, marks, grade, gp, sec_id in attendance_fixtures:
                db.session.add(AttendanceRecord(
                    student_id=stu.id,
                    section_id=sec_id,
                    subject_id=cls.sub_ds.id,
                    semester_id=cls.sem3.id,
                    percentage=att_pct,
                    classes_attended=int(att_pct * 0.6),
                    total_classes=60,
                ))
                db.session.add(SemesterResult(
                    student_id=stu.id,
                    section_id=sec_id,
                    subject_id=cls.sub_ds.id,
                    semester_id=cls.sem3.id,
                    total_marks=marks,
                    grade=grade,
                    grade_point=gp,
                    result_status="FAILED" if grade == "F" else "PASSED",
                ))

            db.session.commit()

            cls.batch_id = cls.batch.id
            cls.sem1_id = cls.sem1.id
            cls.sem2_id = cls.sem2.id
            cls.sem3_id = cls.sem3.id
            cls.sem4_id = cls.sem4.id
            cls.sec_a_id = cls.sec_a.id
            cls.sec_b_id = cls.sec_b.id
            cls.stu_a_id = cls.stu_a.id
            cls.sub_ec_id = cls.sub_ec.id


    def setUp(self):
        # Login as HOD
        resp = self.client.post("/api/v1/auth/login", json={"email": "hod.analytics@dept.edu", "password": "HodPass@123"})
        self.assertEqual(resp.status_code, 200)
        self.hod_token = resp.get_json()["data"]["accessToken"]
        self.auth_headers = {"Authorization": f"Bearer {self.hod_token}"}

    def test_01_security_unauthenticated_and_rbac(self):
        """Verify unauthenticated requests return 401 and non-HOD return 403."""
        # Unauthenticated
        resp = self.client.get("/api/v1/analytics/overview")
        self.assertEqual(resp.status_code, 401)

        # Non-HOD user login
        stud_login = self.client.post("/api/v1/auth/login", json={"email": "student.test@dept.edu", "password": "StudentPass@123"})
        self.assertEqual(stud_login.status_code, 200)
        stud_token = stud_login.get_json()["data"]["accessToken"]
        stud_headers = {"Authorization": f"Bearer {stud_token}"}

        resp_forbidden = self.client.get("/api/v1/analytics/overview", headers=stud_headers)
        self.assertEqual(resp_forbidden.status_code, 403)

    def test_02_overview_kpis_calculation(self):
        """Verify overview calculation: Avg SGPA, Avg Attendance, Pass % from verified database records."""
        resp = self.client.get(f"/api/v1/analytics/overview?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]

        # SGPA values in Sem 3: 8.5, 8.0, 7.5, 9.0, 8.8, 6.2 => sum = 48.0 / 6 = 8.00
        self.assertEqual(data["metrics"]["averageSGPA"], 8.0)
        self.assertEqual(data["metrics"]["studentsWithResults"], 6)

        # Attendance values: 92, 85, 74, 96, 90, 62 => sum = 499 / 6 = 83.17%
        self.assertEqual(data["metrics"]["averageAttendance"], 83.17)

        # 5 passed, 1 failed (stu_f has F) => pass % = (5/6)*100 = 83.33%
        self.assertEqual(data["metrics"]["passPercentage"], 83.33)
        self.assertEqual(data["metrics"]["totalPassedStudents"], 5)
        self.assertEqual(data["metrics"]["totalFailedStudents"], 1)

    def test_03_section_comparison(self):
        """Verify cross-section comparison across Section A and Section B."""
        resp = self.client.get(f"/api/v1/analytics/sections?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        sections = resp.get_json()["data"]["sections"]
        self.assertEqual(len(sections), 2)

        sec_a = next(s for s in sections if s["sectionName"] == "A")
        sec_b = next(s for s in sections if s["sectionName"] == "B")

        # Sec A: 3 students, all passed (8.5, 8.0, 7.5 => avg 8.0), avg att = (92+85+74)/3 = 83.67
        self.assertEqual(sec_a["totalStudents"], 3)
        self.assertEqual(sec_a["averageSGPA"], 8.0)
        self.assertEqual(sec_a["averageAttendance"], 83.67)
        self.assertEqual(sec_a["passPercentage"], 100.0)

        # Sec B: 3 students, 1 failed (stu_f F) => pass % = (2/3)*100 = 66.67%
        self.assertEqual(sec_b["totalStudents"], 3)
        self.assertEqual(sec_b["passPercentage"], 66.67)

    def test_04_controlled_semester_comparison(self):
        """
        Verify deterministic semester comparison classification matching user specification:
        Student A: Sem 1 = 7.5, Sem 2 = 8.2 => +0.7 IMPROVED
        Student B: Sem 1 = 8.4, Sem 2 = 8.1 => -0.3 DECLINED
        Student C: Sem 1 = 7.9, Sem 2 = 7.9 => 0.0 STABLE
        """
        resp = self.client.get(
            f"/api/v1/analytics/semester-comparison?batch_id={self.batch_id}&sem1_id={self.sem1_id}&sem2_id={self.sem2_id}&tolerance=0.10",
            headers=self.auth_headers
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]

        summary = data["summary"]
        self.assertEqual(summary["studentsCompared"], 3)
        self.assertEqual(summary["improvedCount"], 1)
        self.assertEqual(summary["declinedCount"], 1)
        self.assertEqual(summary["stableCount"], 1)

        students = {s["rollNumber"]: s for s in data["students"]}
        # Student A (25A001)
        self.assertEqual(students["25A001"]["change"], 0.7)
        self.assertEqual(students["25A001"]["status"], "IMPROVED")

        # Student B (25A002)
        self.assertEqual(students["25A002"]["change"], -0.3)
        self.assertEqual(students["25A002"]["status"], "DECLINED")

        # Student C (25A003)
        self.assertEqual(students["25A003"]["change"], 0.0)
        self.assertEqual(students["25A003"]["status"], "STABLE")

    def test_05_subject_analytics(self):
        """Verify subject-level performance metrics: avg marks, highest, lowest, pass %."""
        resp = self.client.get(f"/api/v1/analytics/subjects?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        subjects = resp.get_json()["data"]["subjects"]

        ds = next(s for s in subjects if s["code"] == "A9503")
        # Marks: 88, 78, 68, 94, 86, 48 => avg = 462 / 6 = 77.0
        self.assertEqual(ds["averageMarks"], 77.0)
        self.assertEqual(ds["highestMarks"], 94.0)
        self.assertEqual(ds["lowestMarks"], 48.0)
        self.assertEqual(ds["passCount"], 5)
        self.assertEqual(ds["failCount"], 1)
        self.assertEqual(ds["passPercentage"], 83.33)

    def test_06_grade_distribution(self):
        """Verify grade distribution only returns existing recorded grades."""
        resp = self.client.get(f"/api/v1/analytics/grades?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertTrue(data["available"])

        grades = {g["grade"]: g["count"] for g in data["distribution"]}
        # Grades recorded: O:1, A+:2, A:1, B+:1, F:1
        self.assertEqual(grades.get("O"), 1)
        self.assertEqual(grades.get("A+"), 2)
        self.assertEqual(grades.get("A"), 1)
        self.assertEqual(grades.get("B+"), 1)
        self.assertEqual(grades.get("F"), 1)
        # Grade 'C' should NOT be in distribution since no student received it
        self.assertNotIn("C", grades)

    def test_07_student_analytics_and_trajectory(self):
        """Verify student analytical profile and chronological trajectory."""
        resp = self.client.get(f"/api/v1/analytics/student/{self.stu_a_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]

        self.assertEqual(data["student"]["rollNumber"], "25A001")
        self.assertEqual(data["summary"]["latestSGPA"], 8.5)
        self.assertEqual(data["summary"]["currentCGPA"], 8.07)
        self.assertIn("Improving", data["summary"]["performanceTrend"])

        # Trajectory has 3 semesters (Sem 1, Sem 2, Sem 3)
        self.assertEqual(len(data["trajectory"]), 3)
        self.assertEqual(data["trajectory"][0]["semesterNumber"], 1)
        self.assertEqual(data["trajectory"][1]["semesterNumber"], 2)
        self.assertEqual(data["trajectory"][2]["semesterNumber"], 3)

    def test_08_attendance_performance_correlation(self):
        """Verify Pearson correlation between attendance % and marks."""
        resp = self.client.get(f"/api/v1/analytics/attendance-performance?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]

        self.assertEqual(data["status"], "SUCCESS")
        self.assertEqual(data["sampleSize"], 6)
        self.assertGreater(data["correlation"], 0.8)  # Strong positive correlation fixture
        self.assertIn("positive association", data["interpretation"].lower())
        self.assertIn("Association between attendance and academic performance", data["terminology"])
        self.assertIsNotNone(data["trendline"])

    def test_09_correlation_insufficient_sample_safety(self):
        """Verify sample size < 5 safely returns INSUFFICIENT_DATA without crashing."""
        # Query with subject that has 0 records
        resp = self.client.get(
            f"/api/v1/analytics/attendance-performance?semester_id={self.sem3_id}&subject_id={self.sub_ec_id}",
            headers=self.auth_headers
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertEqual(data["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(data["correlation"])

    def test_10_missing_data_safety(self):
        """Verify querying an empty semester (Semester 4) clearly reports NOT_AVAILABLE instead of 0 or crashing."""
        resp = self.client.get(f"/api/v1/analytics/overview?semester_id={self.sem4_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertEqual(data["dataAvailability"]["results"], "NOT_AVAILABLE")
        self.assertEqual(data["dataAvailability"]["attendance"], "NOT_AVAILABLE")
        self.assertIsNone(data["metrics"]["averageSGPA"])
        self.assertIsNone(data["metrics"]["averageAttendance"])
        self.assertIsNone(data["metrics"]["passPercentage"])

    def test_11_rbac_protection(self):
        """Verify unauthenticated requests return 401 and regular students return 403."""
        # Unauthenticated
        resp_unauth = self.client.get(f"/api/v1/analytics/overview?semester_id={self.sem3_id}")
        self.assertEqual(resp_unauth.status_code, 401)

        # Authenticated as regular student (non-HOD/Admin)
        resp_login = self.client.post("/api/v1/auth/login", json={
            "email": "student.test@dept.edu",
            "password": "StudentPass@123"
        })
        self.assertEqual(resp_login.status_code, 200)
        student_token = resp_login.get_json()["data"]["accessToken"]
        student_headers = {"Authorization": f"Bearer {student_token}"}

        resp_forbidden = self.client.get(f"/api/v1/analytics/overview?semester_id={self.sem3_id}", headers=student_headers)
        self.assertEqual(resp_forbidden.status_code, 403)

    def test_12_constant_value_correlation(self):
        """Verify that zero variance (all identical attendance or marks values) is handled safely."""
        # Test correlation engine directly with constant marks
        constant_pairs = [(80.0, 75.0), (85.0, 75.0), (90.0, 75.0), (95.0, 75.0), (70.0, 75.0)]
        result = AnalyticsCorrelation.calculate_correlation(constant_pairs)
        self.assertEqual(result["status"], "UNDEFINED_VARIATION")
        self.assertIsNone(result["correlation"])
        self.assertIn("cannot be determined", result["interpretation"].lower())

    def test_13_invalid_filter_combinations(self):
        """Verify invalid or mismatched filter combinations do not crash and return empty/not-available results."""
        resp = self.client.get("/api/v1/analytics/overview?semester_id=non-existent-uuid-1234", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertEqual(data["dataAvailability"]["results"], "NOT_AVAILABLE")
        self.assertEqual(data["dataAvailability"]["attendance"], "NOT_AVAILABLE")
    def test_14_leaderboard_endpoint(self):
        """Verify Leaderboard API returns ranked students mapped across semesters with podium."""
        resp = self.client.get(f"/api/v1/analytics/leaderboard?batch_id={self.batch_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("cohort", data)
        self.assertIn("summary", data)
        self.assertIn("rankings", data)
        self.assertIn("podium", data)
        self.assertIn("topImprovers", data)
        self.assertGreater(data["summary"]["totalStudents"], 0)


if __name__ == "__main__":
    unittest.main()
