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
from app.insights.rules import InsightRules, DEFAULT_INSIGHT_THRESHOLDS
from app.insights.severity import SeverityLevel, InsightSeverityClassifier
from app.insights.detectors import AcademicDetectors
from app.insights.service import InsightsService
from app.insights.recommendations import RecommendationEngine


class Phase4InsightsTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        cls.client = cls.app.test_client()

        with cls.app.app_context():
            db.create_all()

            # 1. Users: HOD and Regular Student
            cls.hod = User(
                email="hod.insights@dept.edu",
                full_name="Dr. Insights HOD",
                role="HOD",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.hod.set_password("HodPass@123")
            db.session.add(cls.hod)

            cls.student_user = User(
                email="student.regular@dept.edu",
                full_name="Regular Student",
                role="STUDENT",
                department="Computer Science & Engineering",
                is_active=True,
            )
            cls.student_user.set_password("StudentPass@123")
            db.session.add(cls.student_user)

            # 2. Academic Hierarchy: Batch 2025-2029
            cls.batch = Batch(name="2025-2029", start_year=2025, end_year=2029, is_active=True)
            db.session.add(cls.batch)
            db.session.flush()

            cls.ay1 = AcademicYear(batch_id=cls.batch.id, year_number=1, name="1st Year")
            cls.ay2 = AcademicYear(batch_id=cls.batch.id, year_number=2, name="2nd Year", is_current=True)
            db.session.add_all([cls.ay1, cls.ay2])
            db.session.flush()

            cls.sem1 = Semester(academic_year_id=cls.ay1.id, semester_number=1, name="Semester 1")
            cls.sem2 = Semester(academic_year_id=cls.ay1.id, semester_number=2, name="Semester 2")
            cls.sem3 = Semester(academic_year_id=cls.ay2.id, semester_number=3, name="Semester 3", is_current=True)
            cls.sem4 = Semester(academic_year_id=cls.ay2.id, semester_number=4, name="Semester 4")  # empty
            db.session.add_all([cls.sem1, cls.sem2, cls.sem3, cls.sem4])
            db.session.flush()

            cls.sec_a = Section(semester_id=cls.sem3.id, name="A")
            cls.sec_b = Section(semester_id=cls.sem3.id, name="B")
            db.session.add_all([cls.sec_a, cls.sec_b])
            db.session.flush()

            # 3. Subjects
            cls.sub_ds = Subject(semester_id=cls.sem3.id, code="CS301", name="Data Structures", credits=4.0)
            cls.sub_algo = Subject(semester_id=cls.sem3.id, code="CS302", name="Algorithms", credits=4.0)
            cls.sub_dbms = Subject(semester_id=cls.sem3.id, code="CS303", name="Database Systems", credits=3.0)
            db.session.add_all([cls.sub_ds, cls.sub_algo, cls.sub_dbms])
            db.session.flush()

            # 4. Controlled Test Students
            # S1: Low Attendance (62.0%)
            cls.stu_low_att = Student(roll_number="25INS01", name="Low Attendance Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            # S2: Normal Attendance (88.0%) & Good SGPA
            cls.stu_norm = Student(roll_number="25INS02", name="Normal Model Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            # S3: Significant SGPA Decline (Sem 1: 8.5 -> Sem 2: 7.2, delta -1.3)
            cls.stu_decline = Student(roll_number="25INS03", name="Decline Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            # S4: Stable SGPA (Sem 1: 8.0 -> Sem 2: 8.04, delta +0.04)
            cls.stu_stable = Student(roll_number="25INS04", name="Stable Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            # S5: Improved SGPA (Sem 1: 7.0 -> Sem 2: 8.2, delta +1.2)
            cls.stu_improved = Student(roll_number="25INS05", name="Improved Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)
            # S6: Consecutive Decline (Sem 1: 8.8 -> Sem 2: 8.0 -> Sem 3: 7.1)
            cls.stu_consec = Student(roll_number="25INS06", name="Consecutive Drop Stu", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            # S7: Failed Subjects (Failed CS301 and CS302 in Sem 3)
            cls.stu_failed = Student(roll_number="25INS07", name="Backlog Stu", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            # S8: Repeated Failure (Failed CS301 in Sem 2 and again in Sem 3)
            cls.stu_repeated = Student(roll_number="25INS08", name="Repeated Backlog Stu", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            # S9: Combined Attendance + Performance (Att: 58%, Marks: 38 in CS301)
            cls.stu_combined = Student(roll_number="25INS09", name="Combined Deficit Stu", batch_id=cls.batch.id, current_section_id=cls.sec_b.id)
            # S10: Empty Data (No results, no attendance)
            cls.stu_empty = Student(roll_number="25INS10", name="Empty Profile Stu", batch_id=cls.batch.id, current_section_id=cls.sec_a.id)

            db.session.add_all([
                cls.stu_low_att, cls.stu_norm, cls.stu_decline, cls.stu_stable,
                cls.stu_improved, cls.stu_consec, cls.stu_failed, cls.stu_repeated,
                cls.stu_combined, cls.stu_empty
            ])
            db.session.flush()

            # --- Attendance Records ---
            # S1: Low Attendance (62%) in CS301
            db.session.add(AttendanceRecord(
                student_id=cls.stu_low_att.id, semester_id=cls.sem3.id, section_id=cls.sec_a.id,
                subject_id=cls.sub_ds.id, percentage=62.0, classes_attended=31, total_classes=50
            ))
            # S2: Normal Attendance (88%)
            db.session.add(AttendanceRecord(
                student_id=cls.stu_norm.id, semester_id=cls.sem3.id, section_id=cls.sec_a.id,
                subject_id=cls.sub_ds.id, percentage=88.0, classes_attended=44, total_classes=50
            ))
            # S9: Combined (58%) in CS301
            db.session.add(AttendanceRecord(
                student_id=cls.stu_combined.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id,
                subject_id=cls.sub_ds.id, percentage=58.0, classes_attended=29, total_classes=50
            ))

            # --- Semester Summaries for Decline Tests ---
            # S3: Sem 1: 8.5 -> Sem 2: 7.2 (Delta -1.3)
            db.session.add(StudentSemesterSummary(student_id=cls.stu_decline.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=8.5, is_official=True))
            db.session.add(StudentSemesterSummary(student_id=cls.stu_decline.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=7.2, is_official=True))

            # S4: Sem 1: 8.0 -> Sem 2: 8.04 (Stable)
            db.session.add(StudentSemesterSummary(student_id=cls.stu_stable.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=8.0, is_official=True))
            db.session.add(StudentSemesterSummary(student_id=cls.stu_stable.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=8.04, is_official=True))

            # S5: Sem 1: 7.0 -> Sem 2: 8.2 (Improved)
            db.session.add(StudentSemesterSummary(student_id=cls.stu_improved.id, semester_id=cls.sem1.id, section_id=cls.sec_a.id, sgpa=7.0, is_official=True))
            db.session.add(StudentSemesterSummary(student_id=cls.stu_improved.id, semester_id=cls.sem2.id, section_id=cls.sec_a.id, sgpa=8.2, is_official=True))

            # S6: Consecutive Decline (Sem 1: 8.8 -> Sem 2: 8.0 -> Sem 3: 7.1)
            db.session.add(StudentSemesterSummary(student_id=cls.stu_consec.id, semester_id=cls.sem1.id, section_id=cls.sec_b.id, sgpa=8.8, is_official=True))
            db.session.add(StudentSemesterSummary(student_id=cls.stu_consec.id, semester_id=cls.sem2.id, section_id=cls.sec_b.id, sgpa=8.0, is_official=True))
            db.session.add(StudentSemesterSummary(student_id=cls.stu_consec.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, sgpa=7.1, is_official=True))

            # --- Semester Results for Failure Tests ---
            # S7: Failed CS301 and CS302 in Sem 3
            db.session.add(SemesterResult(student_id=cls.stu_failed.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, subject_id=cls.sub_ds.id, total_marks=38.0, grade="F", result_status="FAILED"))
            db.session.add(SemesterResult(student_id=cls.stu_failed.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, subject_id=cls.sub_algo.id, total_marks=32.0, grade="F", result_status="FAILED"))

            # S8: Repeated Failure (CS301 in Sem 2 and Sem 3)
            db.session.add(SemesterResult(student_id=cls.stu_repeated.id, semester_id=cls.sem2.id, section_id=cls.sec_b.id, subject_id=cls.sub_ds.id, total_marks=35.0, grade="F", result_status="FAILED"))
            db.session.add(SemesterResult(student_id=cls.stu_repeated.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, subject_id=cls.sub_ds.id, total_marks=40.0, grade="F", result_status="FAILED"))

            # S9: Combined Deficit in CS301 (Marks: 38, Grade: F)
            db.session.add(SemesterResult(student_id=cls.stu_combined.id, semester_id=cls.sem3.id, section_id=cls.sec_b.id, subject_id=cls.sub_ds.id, total_marks=38.0, grade="F", result_status="FAILED"))

            db.session.commit()

            # Store IDs as primitives to avoid DetachedInstanceError
            cls.batch_id = cls.batch.id
            cls.sem1_id = cls.sem1.id
            cls.sem2_id = cls.sem2.id
            cls.sem3_id = cls.sem3.id
            cls.sem4_id = cls.sem4.id
            cls.sec_a_id = cls.sec_a.id
            cls.sec_b_id = cls.sec_b.id
            cls.stu_low_att_id = cls.stu_low_att.id
            cls.stu_norm_id = cls.stu_norm.id
            cls.stu_decline_id = cls.stu_decline.id
            cls.stu_stable_id = cls.stu_stable.id
            cls.stu_improved_id = cls.stu_improved.id
            cls.stu_consec_id = cls.stu_consec.id
            cls.stu_failed_id = cls.stu_failed.id
            cls.stu_repeated_id = cls.stu_repeated.id
            cls.stu_combined_id = cls.stu_combined.id
            cls.stu_empty_id = cls.stu_empty.id

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Obtain HOD auth token
        resp = self.client.post("/api/v1/auth/login", json={"email": "hod.insights@dept.edu", "password": "HodPass@123"})
        self.assertEqual(resp.status_code, 200)
        self.hod_token = resp.get_json()["data"]["accessToken"]
        self.auth_headers = {"Authorization": f"Bearer {self.hod_token}"}

    def tearDown(self):
        self.app_context.pop()

    # 1. Low Attendance Detection
    def test_01_low_attendance_detection(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_low_att_id, self.sem3_id)
        self.assertTrue(detected["requires_attention"])
        att_signals = [s for s in detected["signals"] if s["category"] == "LOW_ATTENDANCE"]
        self.assertEqual(len(att_signals), 1)
        self.assertEqual(att_signals[0]["evidence"]["current_attendance"], 62.0)
        self.assertIn("62.0%", att_signals[0]["reason"])

    # 2. Normal Attendance Does Not Trigger Warning
    def test_02_normal_attendance_no_warning(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_norm_id, self.sem3_id)
        att_signals = [s for s in detected["signals"] if s["category"] == "LOW_ATTENDANCE"]
        self.assertEqual(len(att_signals), 0)

    # 3. SGPA Decline Detection
    def test_03_sgpa_decline_detection(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_decline_id, self.sem2_id)
        self.assertTrue(detected["requires_attention"])
        decline_signals = [s for s in detected["signals"] if s["category"] == "SGPA_DECLINE"]
        self.assertEqual(len(decline_signals), 1)
        self.assertEqual(decline_signals[0]["evidence"]["delta"], -1.3)

    # 4. Stable SGPA Does Not Trigger Decline
    def test_04_stable_sgpa_no_decline(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_stable_id, self.sem2_id)
        decline_signals = [s for s in detected["signals"] if s["category"] == "SGPA_DECLINE"]
        self.assertEqual(len(decline_signals), 0)

    # 5. SGPA Improvement Does Not Trigger Decline
    def test_05_improved_sgpa_no_decline(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_improved_id, self.sem2_id)
        decline_signals = [s for s in detected["signals"] if s["category"] == "SGPA_DECLINE"]
        self.assertEqual(len(decline_signals), 0)

    # 6. Consecutive SGPA Decline Detection
    def test_06_consecutive_decline_detection(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_consec_id, self.sem3_id)
        consec_signals = [s for s in detected["signals"] if s["category"] == "CONSECUTIVE_DECLINE"]
        self.assertEqual(len(consec_signals), 1)
        self.assertEqual(consec_signals[0]["severity"], SeverityLevel.CRITICAL)

    # 7. Failed Subject Detection
    def test_07_failed_subject_detection(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_failed_id, self.sem3_id)
        fail_signals = [s for s in detected["signals"] if s["category"] == "FAILED_SUBJECTS"]
        self.assertEqual(len(fail_signals), 1)
        self.assertEqual(fail_signals[0]["evidence"]["failed_count"], 2)

    # 8. Repeated Failure Detection Across Semesters
    def test_08_repeated_failure_detection(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_repeated_id, self.sem3_id)
        repeated_signals = [s for s in detected["signals"] if s["category"] == "REPEATED_FAILURE"]
        self.assertEqual(len(repeated_signals), 1)
        self.assertEqual(repeated_signals[0]["severity"], SeverityLevel.CRITICAL)

    # 9. Attendance + Performance Combined Signal
    def test_09_combined_attendance_performance_signal(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_combined_id, self.sem3_id)
        comb_signals = [s for s in detected["signals"] if s["category"] == "COMBINED_ATTENDANCE_PERFORMANCE"]
        self.assertEqual(len(comb_signals), 1)
        self.assertIn("associated with lower performance", comb_signals[0]["reason"].lower())

    # 10. Missing Data Safety (Zero False Positives)
    def test_10_missing_data_safety_no_false_positives(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_empty_id, self.sem4_id)
        self.assertFalse(detected["requires_attention"])
        self.assertEqual(len(detected["signals"]), 0)
        self.assertEqual(detected["overall_severity"], SeverityLevel.INFO)

    # 11. Grounded Recommendations Generation
    def test_11_recommendation_generation(self):
        detected = AcademicDetectors.detect_student_problems(self.stu_failed_id, self.sem3_id)
        recommends = detected["recommendations"]
        self.assertGreater(len(recommends), 0)
        action_types = [r["action_type"] for r in recommends]
        self.assertIn("REMEDIAL_ENROLLMENT", action_types)

    # 12. Centralized Threshold Configuration
    def test_12_threshold_configuration(self):
        original = InsightRules.get("low_attendance_threshold")
        InsightRules.update({"low_attendance_threshold": 80.0})
        self.assertEqual(InsightRules.get("low_attendance_threshold"), 80.0)
        # Reset to default
        InsightRules.reset_defaults()
        self.assertEqual(InsightRules.get("low_attendance_threshold"), original)

    # 13. API RBAC Security: 401 Unauthenticated
    def test_13_rbac_unauthenticated_returns_401(self):
        resp = self.client.get("/api/v1/insights/overview")
        self.assertEqual(resp.status_code, 401)

    # 14. API RBAC Security: 403 Non-HOD/Student Role
    def test_14_rbac_student_returns_403(self):
        login_resp = self.client.post("/api/v1/auth/login", json={"email": "student.regular@dept.edu", "password": "StudentPass@123"})
        self.assertEqual(login_resp.status_code, 200)
        stud_token = login_resp.get_json()["data"]["accessToken"]
        stud_headers = {"Authorization": f"Bearer {stud_token}"}

        resp = self.client.get("/api/v1/insights/overview", headers=stud_headers)
        self.assertEqual(resp.status_code, 403)

    # 15. HOD Insights Overview Endpoint
    def test_15_insights_overview_endpoint(self):
        resp = self.client.get(f"/api/v1/insights/overview?batch_id={self.batch_id}&semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        summary = data["summary"]
        self.assertGreater(summary["totalCohortStudents"], 0)
        self.assertGreater(summary["studentsRequiringAttention"], 0)
        self.assertIn("priorityInsights", data)

    # 16. Student Watchlist Endpoint with Filtering
    def test_16_student_watchlist_endpoint(self):
        resp = self.client.get(f"/api/v1/insights/students?batch_id={self.batch_id}&semester_id={self.sem3_id}&severity=CRITICAL", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertTrue(all(item["severity"] == "CRITICAL" for item in data["data"]))

    # 17. Single Student Detailed Insights Endpoint
    def test_17_single_student_insights_endpoint(self):
        resp = self.client.get(f"/api/v1/insights/students/{self.stu_decline_id}?semester_id={self.sem2_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertEqual(data["roll_number"], "25INS03")
        self.assertTrue(len(data["signals"]) > 0)

    # 18. Subject Insights Endpoint
    def test_18_subject_insights_endpoint(self):
        resp = self.client.get(f"/api/v1/insights/subjects?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("subjects", data)

    # 19. Section Insights Endpoint
    def test_19_section_insights_endpoint(self):
        resp = self.client.get(f"/api/v1/insights/sections?semester_id={self.sem3_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()["data"]
        self.assertIn("sections", data)

    # 20. Config API Endpoint (GET & POST)
    def test_20_config_api_endpoint(self):
        resp_get = self.client.get("/api/v1/insights/config", headers=self.auth_headers)
        self.assertEqual(resp_get.status_code, 200)
        self.assertIn("thresholds", resp_get.get_json()["data"])

        resp_post = self.client.post("/api/v1/insights/config", json={"low_attendance_threshold": 76.0}, headers=self.auth_headers)
        self.assertEqual(resp_post.status_code, 200)
        self.assertEqual(resp_post.get_json()["data"]["thresholds"]["low_attendance_threshold"], 76.0)
        InsightRules.reset_defaults()


if __name__ == "__main__":
    unittest.main()
