import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "civic_ai.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

columns = [row[1] for row in cursor.execute("PRAGMA table_info(test_cases)").fetchall()]
new_cols = [
    ("generation_provider", "TEXT"),
    ("generation_model", "TEXT"),
    ("generation_status", "TEXT DEFAULT 'GENERATED'"),
    ("validation_status", "TEXT DEFAULT 'VALID'"),
    ("validation_findings_json", "TEXT DEFAULT '[]'"),
    ("traceability_json", "TEXT DEFAULT '{}'"),
    ("generation_context_json", "TEXT DEFAULT '{}'")
]

for col_name, col_type in new_cols:
    if col_name not in columns:
        cursor.execute(f"ALTER TABLE test_cases ADD COLUMN {col_name} {col_type}")
        print(f"Added column {col_name} to test_cases")

cursor.execute("""
CREATE TABLE IF NOT EXISTS test_generation_runs (
    id TEXT PRIMARY KEY,
    provider TEXT NOT NULL DEFAULT 'mock',
    model TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    requested_requirement_count INTEGER DEFAULT 0,
    generated_test_count INTEGER DEFAULT 0,
    validation_status TEXT DEFAULT 'VALID',
    error_message TEXT,
    requirement_ids_json TEXT DEFAULT '[]',
    generated_test_ids_json TEXT DEFAULT '[]'
)
""")

conn.commit()
conn.close()
print("Phase 3 database migration completed successfully!")
