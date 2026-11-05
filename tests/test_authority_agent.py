from agents.authority_agent import AuthorityAgent
from agents.hazard_agent import HazardAgent
from agents.road_risk_agent import RoadRiskAgent


def test_prioritization_and_suggest_action(tmp_path):
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    # submit a critical waterlogging
    rid, sev = h.submit_report('Waterlogging','Flooded road',28.705,77.105)
    r = RoadRiskAgent()
    r.load_data()
    r.train_model(save=False)
    segments = r.get_all_segments_with_risk()
    auth = AuthorityAgent(segments, h)
    ranked = auth.prioritize_reports()
    assert isinstance(ranked, list)
    # check suggest_action
    action = auth.suggest_action(h.get_report(rid))
    assert isinstance(action, str)
