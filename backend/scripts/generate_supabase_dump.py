import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'student_management.db')
output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'supabase_seed_data.sql')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tables = [
    'users',
    'department_info',
    'faculty_members',
    'department_events',
    'student_achievements',
    'announcements',
    'batches',
    'academic_years',
    'semesters',
    'sections',
    'subjects',
    'students',
    'attendance_records',
    'assessment_records',
    'semester_results',
    'student_semester_summaries',
    'upload_history'
]

with open(output_path, 'w', encoding='utf-8') as f:
    f.write('-- ============================================================================\n')
    f.write('-- SUPABASE INITIAL DATA SEED SCRIPT\n')
    f.write('-- College of Engineering & Technology | Department of Computer Science\n')
    f.write('-- Project Ref: wehwepjchdclhwsaxadg\n')
    f.write('-- ============================================================================\n\n')
    f.write('BEGIN;\n\n')

    total_records = 0
    for tbl in tables:
        cursor.execute(f"PRAGMA table_info({tbl})")
        cols = [info[1] for info in cursor.fetchall()]
        col_names = ', '.join([f'"{c}"' for c in cols])

        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()
        f.write(f'-- Table: {tbl} ({len(rows)} records)\n')
        total_records += len(rows)

        for row in rows:
            vals = []
            for val in row:
                if val is None:
                    vals.append('NULL')
                elif isinstance(val, (int, float)):
                    vals.append(str(val))
                elif isinstance(val, bool):
                    vals.append('TRUE' if val else 'FALSE')
                else:
                    escaped = str(val).replace("'", "''")
                    vals.append(f"'{escaped}'")
            val_str = ', '.join(vals)
            f.write(f"INSERT INTO {tbl} ({col_names}) VALUES ({val_str}) ON CONFLICT DO NOTHING;\n")
        f.write('\n')

    f.write('COMMIT;\n')

print(f"Successfully generated {output_path} with {total_records} records.")
