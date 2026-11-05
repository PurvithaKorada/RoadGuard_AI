import importlib
import sys
import types
import pandas as pd


def test_app_import_monkeypatched(monkeypatch):
    # Import the road_risk_agent module and monkeypatch methods to avoid training during import
    import agents.road_risk_agent as rmod
    # Patch load_model to return True so app won't retrain
    monkeypatch.setattr(rmod.RoadRiskAgent, 'load_model', lambda self: True)
    # Patch get_all_segments_with_risk to return a minimal dataframe
    df = pd.DataFrame([{
        'segment_id':'seg_test','latitude':28.7,'longitude':77.1,'predicted_risk':'low','risk_score':0.9,
        'num_accidents':0,'num_fatal_accidents':0,'num_injuries':0,'length_km':1.0,'avg_speed_kmph':40,'num_potholes':0,'night_lighting_score':5,'road_type':'urban','road_type_enc':0,'num_lanes':2
    }])
    monkeypatch.setattr(rmod.RoadRiskAgent, 'get_all_segments_with_risk', lambda self: df)

    # Also patch HazardAgent to use in-memory DB to avoid file writes
    import agents.hazard_agent as hmod
    monkeypatch.setattr(hmod.HazardAgent, '__init__', lambda self, db_path='db/reports.db': None)
    # Provide minimal methods used by app
    monkeypatch.setattr(hmod.HazardAgent, 'list_reports', lambda self, status=None: [])
    monkeypatch.setattr(hmod.HazardAgent, 'submit_report', lambda self, *a, **k: ('r1','moderate'))
    monkeypatch.setattr(hmod.HazardAgent, 'get_report', lambda self, rid: None)
    monkeypatch.setattr(hmod.HazardAgent, 'update_status', lambda self, *a, **k: True)

    # Now import app
    try:
        import app
    except Exception as e:
        raise AssertionError(f'Importing app failed: {e}')
    # basic checks
    assert hasattr(app, 'road_agent')
    assert hasattr(app, 'hazard_agent')
    assert hasattr(app, 'route_agent')
    assert hasattr(app, 'authority_agent')
    assert hasattr(app, 'assistant_agent')
