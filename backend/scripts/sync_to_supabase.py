"""
Sync Local Database to Supabase
Transfers all local SQLite data to Supabase PostgreSQL over REST API using service role key.
Tables must first be created by running `supabase_schema.sql` in the Supabase SQL Editor.
"""

import os
import sqlite3
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(backend_dir, '.env'))

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://wehwepjchdclhwsaxadg.supabase.co")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SERVICE_KEY:
    print("Error: SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

db_path = os.path.join(backend_dir, 'student_management.db')
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Dependency order for relational integrity
TABLES = [
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

def post_batch(table_name, records):
    if not records:
        return True
    
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=ignore-duplicates,return=minimal"
    }
    
    # Send in chunks of 200
    chunk_size = 200
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        body = json.dumps(chunk).encode('utf-8')
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        
        try:
            with urllib.request.urlopen(req) as resp:
                pass
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"  [ERROR] Table {table_name} batch {i//chunk_size + 1}: HTTP {e.code} - {err_body}")
            return False
        except Exception as e:
            print(f"  [ERROR] Table {table_name}: {e}")
            return False
            
    return True

def sync():
    print(f"Connecting to Supabase at: {SUPABASE_URL}")
    print("Beginning sync of 17 tables from SQLite to Supabase...")
    
    total_synced = 0
    for tbl in TABLES:
        cursor.execute(f"SELECT * FROM {tbl}")
        rows = cursor.fetchall()
        dict_rows = [dict(row) for row in rows]
        
        # Clean up boolean values and nulls if needed
        for r in dict_rows:
            for k, v in list(r.items()):
                if isinstance(v, int) and k.startswith(('is_', 'has_')):
                    r[k] = bool(v)
                    
        print(f"Syncing table: {tbl} ({len(dict_rows)} records)...", end=" ")
        success = post_batch(tbl, dict_rows)
        if success:
            print("[OK]")
            total_synced += len(dict_rows)
        else:
            print("[FAILED - Ensure supabase_schema.sql was run in Supabase SQL Editor]")
            
    print(f"\nSync complete: {total_synced} total records processed.")

if __name__ == '__main__':
    sync()
