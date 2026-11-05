import sqlite3
import uuid
import os
from datetime import datetime

DB_PATH = 'db/reports.db'

class HazardAgent:
    """Handles hazard report submission and basic categorization.
    This agent stores reports in a simple SQLite DB and assigns severity based on rules.
    Image analysis is not implemented in this demo.
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            created_at TEXT,
            hazard_type TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            severity TEXT,
            status TEXT,
            needs_verification INTEGER,
            image_path TEXT
        )
        ''')
        conn.commit()
        conn.close()

    def submit_report(self, hazard_type, description, lat, lon, image_path=None):
        rid = str(uuid.uuid4())[:8]
        created = datetime.utcnow().isoformat()
        severity = self._estimate_severity(hazard_type, description)
        needs_ver = 1 if severity in ('critical','high') else 0
        status = 'Submitted'
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('INSERT INTO reports VALUES (?,?,?,?,?,?,?,?,?,?)', (rid, created, hazard_type, description, lat, lon, severity, status, needs_ver, image_path))
        conn.commit()
        conn.close()
        return rid, severity

    def _estimate_severity(self, hazard_type, description):
        # Rule-based severity estimation
        h = hazard_type.lower()
        desc = (description or '').lower()
        if 'pothole' in h or 'pothole' in desc:
            return 'high'
        if 'water' in h or 'flood' in h or 'water' in desc:
            return 'critical'
        if 'lighting' in h or 'light' in desc:
            return 'moderate'
        if 'debris' in h or 'obstacle' in h:
            return 'high'
        return 'moderate'

    def list_reports(self, status=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        if status:
            c.execute('SELECT * FROM reports WHERE status=?', (status,))
        else:
            c.execute('SELECT * FROM reports')
        rows = c.fetchall()
        conn.close()
        keys = ['id','created_at','hazard_type','description','latitude','longitude','severity','status','needs_verification','image_path']
        return [dict(zip(keys,row)) for row in rows]

    def get_report(self, report_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT * FROM reports WHERE id=?', (report_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return None
        keys = ['id','created_at','hazard_type','description','latitude','longitude','severity','status','needs_verification','image_path']
        return dict(zip(keys,row))

    def update_status(self, report_id, status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('UPDATE reports SET status=? WHERE id=?', (status, report_id))
        conn.commit()
        conn.close()
        return True
