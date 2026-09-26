import sqlite3

con = sqlite3.connect('civic_ai.db')
cur = con.cursor()

# 1. Update requirements table
cols = [c[1] for c in cur.execute('PRAGMA table_info(requirements)').fetchall()]

columns_to_add = [
    ('source_type', 'VARCHAR DEFAULT "seed"'),
    ('document_id', 'VARCHAR'),
    ('source_document', 'VARCHAR'),
    ('source_page', 'INTEGER'),
    ('source_section', 'VARCHAR'),
    ('source_location', 'VARCHAR'),
    ('source_traceability_json', 'TEXT DEFAULT "{}"')
]

for col_name, col_type in columns_to_add:
    if col_name not in cols:
        cur.execute(f'ALTER TABLE requirements ADD COLUMN {col_name} {col_type}')
        print(f"Added {col_name} to requirements table")

# 2. Ensure existing rows have source_type = 'seed'
cur.execute("UPDATE requirements SET source_type = 'seed' WHERE source_type IS NULL")

# 3. Create requirement_documents table if not exists
cur.execute('''
CREATE TABLE IF NOT EXISTS requirement_documents (
    id VARCHAR PRIMARY KEY,
    original_filename VARCHAR NOT NULL,
    sanitized_filename VARCHAR NOT NULL,
    file_type VARCHAR NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    upload_timestamp DATETIME,
    extraction_status VARCHAR,
    extraction_error TEXT,
    imported_requirement_count INTEGER DEFAULT 0,
    duplicate_count INTEGER DEFAULT 0,
    specification_gap_count INTEGER DEFAULT 0,
    processing_status VARCHAR,
    created_at DATETIME
)
''')

con.commit()
con.close()
print("civic_ai.db schema successfully migrated.")
