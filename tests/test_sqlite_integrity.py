import sqlite3
from agents.hazard_agent import HazardAgent


def test_db_file_creation(tmp_path):
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    # DB file should exist
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reports'")
    row = c.fetchone()
    conn.close()
    assert row is not None


def test_report_storage_and_query(tmp_path):
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    rid, sev = h.submit_report('Pothole','Test',28.7,77.1)
    rep = h.get_report(rid)
    assert rep['id'] == rid
    reps = h.list_reports()
    assert any(r['id']==rid for r in reps)
