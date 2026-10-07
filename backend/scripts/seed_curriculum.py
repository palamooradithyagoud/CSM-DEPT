"""
Populate complete 4-year curriculum:
Ensures each Academic Year has 2 distinct Semesters with DIFFERENT subjects.
Also ensures Sections A, B, C exist for all Semesters 1 through 8.
"""

import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, base_dir)

from app import create_app
from app.extensions import db
from app.models.academic import Batch, AcademicYear, Semester, Section, Subject

CURRICULUM_SEMESTERS = {
    1: [
        {"code": "A9001", "name": "Matrices and Calculus", "short_name": "MAC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9501", "name": "Programming for Problem Solving", "short_name": "PPS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9502", "name": "Programming for Problem Solving Lab", "short_name": "PPSL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9302", "name": "Engineering Workshop", "short_name": "EW", "credits": 2.5, "subject_type": "LAB"},
        {"code": "A9021", "name": "Critical Thinking & Design Thinking", "short_name": "CCDT", "credits": 2.0, "subject_type": "THEORY"},
        {"code": "A9007", "name": "Engineering Physics", "short_name": "EP", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9008", "name": "Engineering Physics Lab", "short_name": "EPL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9204", "name": "Basic Electrical Engineering", "short_name": "BEE", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9801", "name": "Foundations of Data Science", "short_name": "FDS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9205", "name": "Basic Electrical Engineering Lab", "short_name": "BEEL", "credits": 1.5, "subject_type": "LAB"},
    ],
    2: [
        {"code": "A9003", "name": "Linear Algebra and Advanced Calculus", "short_name": "LAAC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9004", "name": "Applied Chemistry", "short_name": "AC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9005", "name": "Applied Chemistry Lab", "short_name": "ACL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9505", "name": "Python Programming for Problem Solving", "short_name": "PPPS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9506", "name": "Python Programming Lab", "short_name": "PYLAB", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9013", "name": "English for Skill Enhancement", "short_name": "ESE", "credits": 2.0, "subject_type": "THEORY"},
        {"code": "A9014", "name": "English Language & Communication Skills Lab", "short_name": "ELCS", "credits": 1.0, "subject_type": "LAB"},
        {"code": "A9206", "name": "Electronic Devices and Circuits", "short_name": "EDC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9207", "name": "Electronic Devices and Circuits Lab", "short_name": "EDCL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9023", "name": "Environmental Science and Ecology", "short_name": "EVS", "credits": 2.0, "subject_type": "THEORY"},
    ],
    3: [
        {"code": "A9002", "name": "Ordinary Differential Equations and Calculus of Variations", "short_name": "ODECV", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9009", "name": "Engineering Chemistry", "short_name": "EC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9011", "name": "Engineering Science Elective", "short_name": "ESE", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9503", "name": "Data Structures using C++", "short_name": "DS", "credits": 4.0, "subject_type": "THEORY"},
        {"code": "A9402", "name": "Digital Electronics", "short_name": "DE", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9010", "name": "Engineering Chemistry Lab", "short_name": "ECL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9012", "name": "Engineering Science Elective Lab", "short_name": "ESEL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9504", "name": "Data Structures Lab", "short_name": "DSL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9304", "name": "Computer Aided Engineering Graphics", "short_name": "CAEG", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9022", "name": "Professional Development & Design", "short_name": "PDD", "credits": 2.0, "subject_type": "THEORY"},
    ],
    4: [
        {"code": "A9006", "name": "Discrete Mathematics and Graph Theory", "short_name": "DMGT", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9507", "name": "Database Management Systems", "short_name": "DBMS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9508", "name": "Database Management Systems Lab", "short_name": "DBMSL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9509", "name": "Operating Systems", "short_name": "OS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9510", "name": "Operating Systems Lab", "short_name": "OSL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9511", "name": "Computer Organization and Architecture", "short_name": "COA", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9512", "name": "Object-Oriented Programming through Java", "short_name": "JAVA", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9513", "name": "Java Programming Lab", "short_name": "JAVAL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9514", "name": "Design and Analysis of Algorithms", "short_name": "DAA", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9024", "name": "Constitution of India", "short_name": "COI", "credits": 2.0, "subject_type": "THEORY"},
    ],
    5: [
        {"code": "A9515", "name": "Computer Networks", "short_name": "CN", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9516", "name": "Formal Languages and Automata Theory", "short_name": "FLAT", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9802", "name": "Machine Learning", "short_name": "ML", "credits": 4.0, "subject_type": "THEORY"},
        {"code": "A9803", "name": "Machine Learning Lab", "short_name": "MLL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9517", "name": "Software Engineering", "short_name": "SE", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9518", "name": "Web Technologies", "short_name": "WT", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9519", "name": "Web Technologies Lab", "short_name": "WTL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9520", "name": "Computer Networks Lab", "short_name": "CNL", "credits": 1.5, "subject_type": "LAB"},
    ],
    6: [
        {"code": "A9804", "name": "Artificial Intelligence", "short_name": "AI", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9805", "name": "Artificial Intelligence Lab", "short_name": "AIL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9521", "name": "Compiler Design", "short_name": "CD", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9806", "name": "Deep Learning and Neural Networks", "short_name": "DL", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9807", "name": "Deep Learning Lab", "short_name": "DLL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9522", "name": "Cloud Computing and Distributed Systems", "short_name": "CC", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9025", "name": "Intellectual Property Rights and Cyber Law", "short_name": "IPR", "credits": 2.0, "subject_type": "THEORY"},
        {"code": "A9523", "name": "Industry Oriented Mini Project", "short_name": "MP", "credits": 2.0, "subject_type": "LAB"},
    ],
    7: [
        {"code": "A9524", "name": "Cryptography and Network Security", "short_name": "CNS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9808", "name": "Natural Language Processing", "short_name": "NLP", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9809", "name": "Big Data Analytics and Processing", "short_name": "BDA", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9525", "name": "Network Security Lab", "short_name": "NSL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9810", "name": "Big Data Analytics Lab", "short_name": "BDAL", "credits": 1.5, "subject_type": "LAB"},
        {"code": "A9526", "name": "Professional Elective - DevOps and Agile Engineering", "short_name": "DEVOPS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9527", "name": "Major Project Stage - I", "short_name": "PROJ1", "credits": 3.0, "subject_type": "LAB"},
    ],
    8: [
        {"code": "A9811", "name": "Deep Reinforcement Learning", "short_name": "DRL", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9812", "name": "Autonomous Intelligent Systems & Robotics", "short_name": "AIS", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9026", "name": "Management Fundamentals & Entrepreneurship", "short_name": "MFE", "credits": 3.0, "subject_type": "THEORY"},
        {"code": "A9528", "name": "Major Project Stage - II / Capstone Internship", "short_name": "PROJ2", "credits": 10.0, "subject_type": "LAB"},
    ],
}


def seed_all_semesters_and_subjects():
    app = create_app("development")
    with app.app_context():
        batch = Batch.query.filter_by(name="2025-2029").first()
        if not batch:
            print("[ERROR] Batch 2025-2029 not found. Run seed.py first.")
            return

        total_subjects_added = 0
        total_sections_added = 0

        for sem in Semester.query.all():
            sem_num = sem.semester_number

            # 1. Ensure Sections A, B, C exist
            for sec_letter in ["A", "B", "C"]:
                existing_sec = Section.query.filter_by(semester_id=sem.id, name=sec_letter).first()
                if not existing_sec:
                    sec = Section(
                        semester_id=sem.id,
                        name=sec_letter,
                        room_number=f"Room-{sec_letter}-30{sem_num}",
                    )
                    db.session.add(sec)
                    total_sections_added += 1

            # 2. Add distinct curriculum subjects
            subjects_list = CURRICULUM_SEMESTERS.get(sem_num, [])
            for sub_data in subjects_list:
                existing_sub = Subject.query.filter_by(semester_id=sem.id, code=sub_data["code"]).first()
                if not existing_sub:
                    sub = Subject(semester_id=sem.id, **sub_data)
                    db.session.add(sub)
                    total_subjects_added += 1

        db.session.commit()
        print(f"[SUCCESS] Added {total_sections_added} missing Sections and {total_subjects_added} distinct Subjects across all semesters!")

        # Print summary
        for sem in Semester.query.order_by(Semester.semester_number).all():
            subs = Subject.query.filter_by(semester_id=sem.id).all()
            secs = Section.query.filter_by(semester_id=sem.id).all()
            ay = sem.academic_year
            print(f"  • {ay.name} -> {sem.name}: {len(subs)} distinct subjects, {len(secs)} sections (A, B, C)")


if __name__ == "__main__":
    seed_all_semesters_and_subjects()
