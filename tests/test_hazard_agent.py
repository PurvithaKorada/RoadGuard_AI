import os
import tempfile
from agents.hazard_agent import HazardAgent


def test_submit_and_retrieve_report(tmp_path):
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    rid, sev = h.submit_report('Pothole', 'Large pothole near junction', 28.70, 77.10, image_path=None)
    assert isinstance(rid, str)
    rep = h.get_report(rid)
    assert rep is not None
    assert rep['hazard_type'] == 'Pothole'
    assert rep['severity'] in ('low','moderate','high','critical')


def test_list_and_update_status(tmp_path):
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    rid, _ = h.submit_report('Waterlogging', 'Water on carriageway', 28.71, 77.11)
    reps = h.list_reports()
    assert any(r['id'] == rid for r in reps)
    # update status
    ok = h.update_status(rid, 'Under Review')
    assert ok
    r = h.get_report(rid)
    assert r['status'] == 'Under Review'
