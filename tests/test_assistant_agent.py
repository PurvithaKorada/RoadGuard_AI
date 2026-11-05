from agents.assistant_agent import AssistantAgent
from agents.road_risk_agent import RoadRiskAgent
from agents.hazard_agent import HazardAgent
from agents.route_agent import RouteAgent
from agents.weather_agent import WeatherAgent
from agents.authority_agent import AuthorityAgent


def test_assistant_responses(tmp_path):
    r = RoadRiskAgent()
    r.load_data()
    r.train_model(save=False)
    segments = r.get_all_segments_with_risk()
    h = HazardAgent(db_path=str(tmp_path / 'reports.db'))
    ra = RouteAgent(segments)
    w = WeatherAgent()
    auth = AuthorityAgent(segments, h)
    assist = AssistantAgent(r, h, ra, w, auth)
    resp = assist.handle_query('Which road is dangerous?')
    assert isinstance(resp, str)
    # explain segment
    out = assist.explain_segment_by_id('seg_3')
    assert 'segment_id' in out or 'not found' in out
