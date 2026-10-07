"""
CSV Export Generator for Academic Reports.
Generates clean, well-structured CSV bytes for Department, Section, Student, Subject, and Insights reports.
"""

import io
import csv
from datetime import datetime


class CSVReportGenerator:
    """Generates standard UTF-8 CSV exports for academic reports."""

    @staticmethod
    def _create_writer():
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        return output, writer

    @classmethod
    def generate_department_csv(cls, data):
        output, writer = cls._create_writer()

        # Metadata Header
        writer.writerow(["INSTITUTION", "Department of Computer Science & Engineering"])
        writer.writerow(["REPORT", "Department Comprehensive Academic Report"])
        writer.writerow(["GENERATED AT", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow(["BATCH", data.get("batchName", "All Batches")])
        writer.writerow(["SEMESTER", data.get("semesterName", "All Semesters")])
        writer.writerow([])

        # Summary KPIs
        writer.writerow(["--- SUMMARY METRICS ---"])
        writer.writerow(["Metric", "Value"])
        kpis = data.get("kpis", {})
        writer.writerow(["Total Enrolled Students", kpis.get("totalStudents", 0)])
        writer.writerow(["Average SGPA", kpis.get("averageSGPA", "N/A")])
        writer.writerow(["Average CGPA", kpis.get("averageCGPA", "N/A")])
        writer.writerow(["Average Attendance (%)", f"{kpis.get('averageAttendance', 'N/A')}%" if kpis.get('averageAttendance') is not None else "N/A"])
        writer.writerow(["Overall Pass Rate (%)", f"{kpis.get('passPercentage', 'N/A')}%" if kpis.get('passPercentage') is not None else "N/A"])
        writer.writerow(["Students Requiring Attention", data.get("flaggedStudentsCount", 0)])
        writer.writerow([])

        # Subject Breakdown
        writer.writerow(["--- SUBJECT PERFORMANCE BREAKDOWN ---"])
        writer.writerow(["Subject Code", "Subject Name", "Average Marks", "Pass Rate (%)", "Failed Students", "Total Evaluated"])
        for sub in data.get("subjects", []):
            writer.writerow([
                sub.get("code", ""),
                sub.get("name", ""),
                sub.get("averageMarks", "N/A"),
                f"{sub.get('passPercentage', 'N/A')}%" if sub.get('passPercentage') is not None else "N/A",
                sub.get("failureCount", 0),
                sub.get("evaluatedStudents", 0)
            ])
        writer.writerow([])

        # Section Comparison
        writer.writerow(["--- SECTION COMPARISON ---"])
        writer.writerow(["Section", "Student Count", "Average SGPA", "Average Attendance (%)", "Pass Rate (%)"])
        for sec in data.get("sections", []):
            writer.writerow([
                sec.get("sectionName", ""),
                sec.get("studentCount", 0),
                sec.get("averageSGPA", "N/A"),
                f"{sec.get('averageAttendance', 'N/A')}%" if sec.get('averageAttendance') is not None else "N/A",
                f"{sec.get('passPercentage', 'N/A')}%" if sec.get('passPercentage') is not None else "N/A"
            ])
        writer.writerow([])

        # Grade Distribution
        writer.writerow(["--- GRADE DISTRIBUTION ---"])
        writer.writerow(["Grade", "Count", "Percentage (%)"])
        for gr in data.get("gradeDistribution", []):
            writer.writerow([
                gr.get("grade", ""),
                gr.get("count", 0),
                f"{gr.get('percentage', 0)}%"
            ])

        return output.getvalue().encode("utf-8-sig")

    @classmethod
    def generate_section_csv(cls, data):
        output, writer = cls._create_writer()

        writer.writerow(["INSTITUTION", "Department of Computer Science & Engineering"])
        writer.writerow(["REPORT", f"Section {data.get('sectionName', '')} Performance Report"])
        writer.writerow(["SEMESTER", data.get("semesterName", "")])
        writer.writerow(["BATCH", data.get("batchName", "")])
        writer.writerow(["GENERATED AT", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])

        writer.writerow(["--- SECTION METRICS ---"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Students", data.get("studentCount", 0)])
        writer.writerow(["Average SGPA", data.get("averageSGPA", "N/A")])
        writer.writerow(["Average Attendance (%)", f"{data.get('averageAttendance', 'N/A')}%" if data.get('averageAttendance') is not None else "N/A"])
        writer.writerow(["Pass Rate (%)", f"{data.get('passPercentage', 'N/A')}%" if data.get('passPercentage') is not None else "N/A"])
        writer.writerow(["Flagged Students", data.get("flaggedStudentsCount", 0)])
        writer.writerow([])

        writer.writerow(["--- SUBJECT-WISE RESULTS ---"])
        writer.writerow(["Subject Code", "Subject Name", "Average Marks", "Pass Rate (%)", "Failures", "Total Evaluated"])
        for sub in data.get("subjects", []):
            writer.writerow([
                sub.get("code", ""),
                sub.get("name", ""),
                sub.get("averageMarks", "N/A"),
                f"{sub.get('passPercentage', 'N/A')}%" if sub.get('passPercentage') is not None else "N/A",
                sub.get("failureCount", 0),
                sub.get("evaluatedStudents", 0)
            ])
        writer.writerow([])

        writer.writerow(["--- STUDENTS REQUIRING ATTENTION ---"])
        writer.writerow(["Roll Number", "Student Name", "Severity", "Primary Reason", "Attendance (%)", "SGPA"])
        for st in data.get("flaggedStudents", []):
            writer.writerow([
                st.get("rollNumber", ""),
                st.get("name", ""),
                st.get("severity", ""),
                st.get("primaryReason", ""),
                f"{st.get('attendance', 'N/A')}%" if st.get('attendance') is not None else "N/A",
                st.get("sgpa", "N/A")
            ])

        return output.getvalue().encode("utf-8-sig")

    @classmethod
    def generate_student_csv(cls, data):
        output, writer = cls._create_writer()

        writer.writerow(["INSTITUTION", "Department of Computer Science & Engineering"])
        writer.writerow(["REPORT", "Individual Student Academic Dossier"])
        writer.writerow(["STUDENT NAME", data.get("name", "")])
        writer.writerow(["ROLL NUMBER", data.get("rollNumber", "")])
        writer.writerow(["BATCH", data.get("batchName", "")])
        writer.writerow(["SECTION", data.get("sectionName", "")])
        writer.writerow(["SEMESTER", data.get("semesterName", "")])
        writer.writerow(["LATEST SGPA", data.get("sgpa", "N/A")])
        writer.writerow(["OVERALL CGPA", data.get("cgpa", "N/A")])
        writer.writerow(["AVERAGE ATTENDANCE", f"{data.get('attendancePercentage', 'N/A')}%" if data.get('attendancePercentage') is not None else "N/A"])
        writer.writerow(["GENERATED AT", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])

        writer.writerow(["--- SUBJECT-WISE PERFORMANCE & ATTENDANCE ---"])
        writer.writerow(["Subject Code", "Subject Name", "Credits", "Attendance (%)", "Internal Marks", "External Marks", "Total Marks", "Grade", "Result Status"])
        for sub in data.get("subjects", []):
            writer.writerow([
                sub.get("code", ""),
                sub.get("name", ""),
                sub.get("credits", ""),
                f"{sub.get('attendance', 'N/A')}%" if sub.get('attendance') is not None else "N/A",
                sub.get("internalMarks", "N/A"),
                sub.get("externalMarks", "N/A"),
                sub.get("totalMarks", "N/A"),
                sub.get("grade", "N/A"),
                sub.get("resultStatus", "N/A")
            ])
        writer.writerow([])

        writer.writerow(["--- SEMESTER TRAJECTORY ---"])
        writer.writerow(["Semester", "SGPA", "CGPA", "Credits Earned"])
        for sem in data.get("trajectory", []):
            writer.writerow([
                sem.get("semesterName", ""),
                sem.get("sgpa", "N/A"),
                sem.get("cgpa", "N/A"),
                sem.get("credits", "N/A")
            ])
        writer.writerow([])

        if data.get("issues"):
            writer.writerow(["--- ACADEMIC ATTENTION SIGNALS ---"])
            writer.writerow(["Severity", "Category", "Title", "Reason"])
            for iss in data.get("issues", []):
                writer.writerow([
                    iss.get("severity", ""),
                    iss.get("category", ""),
                    iss.get("title", ""),
                    iss.get("reason", "")
                ])
            writer.writerow([])

        if data.get("recommendations"):
            writer.writerow(["--- GROUNDED RECOMMENDATIONS ---"])
            writer.writerow(["Action", "Context / Justification"])
            for rec in data.get("recommendations", []):
                writer.writerow([
                    rec.get("action", ""),
                    rec.get("justification", "")
                ])

        return output.getvalue().encode("utf-8-sig")

    @classmethod
    def generate_subject_csv(cls, data):
        output, writer = cls._create_writer()

        writer.writerow(["INSTITUTION", "Department of Computer Science & Engineering"])
        writer.writerow(["REPORT", "Subject Performance Diagnostic Report"])
        writer.writerow(["SUBJECT CODE", data.get("code", "")])
        writer.writerow(["SUBJECT NAME", data.get("name", "")])
        writer.writerow(["CREDITS", data.get("credits", "")])
        writer.writerow(["SUBJECT TYPE", data.get("subjectType", "")])
        writer.writerow(["SEMESTER", data.get("semesterName", "")])
        writer.writerow(["GENERATED AT", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])

        writer.writerow(["--- SUBJECT METRICS ---"])
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Evaluated Students", data.get("studentCount", 0)])
        writer.writerow(["Average Marks", data.get("averageMarks", "N/A")])
        writer.writerow(["Highest Marks", data.get("highestMarks", "N/A")])
        writer.writerow(["Lowest Marks", data.get("lowestMarks", "N/A")])
        writer.writerow(["Pass Rate (%)", f"{data.get('passPercentage', 'N/A')}%" if data.get('passPercentage') is not None else "N/A"])
        writer.writerow(["Total Failed", data.get("failureCount", 0)])
        writer.writerow(["Average Attendance (%)", f"{data.get('averageAttendance', 'N/A')}%" if data.get('averageAttendance') is not None else "N/A"])
        writer.writerow([])

        writer.writerow(["--- SECTION-WISE BREAKDOWN ---"])
        writer.writerow(["Section", "Students", "Average Marks", "Pass Rate (%)", "Failures"])
        for sec in data.get("sections", []):
            writer.writerow([
                sec.get("sectionName", ""),
                sec.get("studentCount", 0),
                sec.get("averageMarks", "N/A"),
                f"{sec.get('passPercentage', 'N/A')}%" if sec.get('passPercentage') is not None else "N/A",
                sec.get("failureCount", 0)
            ])

        return output.getvalue().encode("utf-8-sig")

    @classmethod
    def generate_insights_csv(cls, data):
        output, writer = cls._create_writer()

        writer.writerow(["INSTITUTION", "Department of Computer Science & Engineering"])
        writer.writerow(["REPORT", "Academic Insights & Student Watchlist Report"])
        writer.writerow(["SEMESTER", data.get("semesterName", "All Semesters")])
        writer.writerow(["GENERATED AT", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")])
        writer.writerow([])

        writer.writerow(["--- SUMMARY METRICS ---"])
        summary = data.get("summary", {})
        writer.writerow(["Metric", "Count"])
        writer.writerow(["Students Requiring Attention", summary.get("studentsRequiringAttention", 0)])
        writer.writerow(["Critical Severity Issues", summary.get("criticalIssues", 0)])
        writer.writerow(["High Severity Issues", summary.get("highPriorityIssues", 0)])
        writer.writerow(["Medium Severity Issues", summary.get("mediumPriorityIssues", 0)])
        writer.writerow(["Subjects Requiring Attention", summary.get("subjectsRequiringAttention", 0)])
        writer.writerow(["Sections Requiring Attention", summary.get("sectionsRequiringAttention", 0)])
        writer.writerow([])

        writer.writerow(["--- STUDENT WATCHLIST ---"])
        writer.writerow(["Roll Number", "Student Name", "Section", "Severity", "Primary Reason", "Attendance (%)", "SGPA", "Failed Subjects", "Recommendations"])
        for st in data.get("watchlist", []):
            recs_text = "; ".join([r.get("action", "") for r in st.get("recommendations", [])])
            failed_text = ", ".join(st.get("failedSubjectCodes", []))
            writer.writerow([
                st.get("rollNumber", ""),
                st.get("name", ""),
                st.get("sectionName", ""),
                st.get("severity", ""),
                st.get("primaryReason", ""),
                f"{st.get('attendance', 'N/A')}%" if st.get('attendance') is not None else "N/A",
                st.get("sgpa", "N/A"),
                failed_text,
                recs_text
            ])

        return output.getvalue().encode("utf-8-sig")
