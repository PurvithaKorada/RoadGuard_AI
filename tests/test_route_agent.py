import pytest
from agents.road_risk_agent import RoadRiskAgent
from agents.route_agent import RouteAgent
from agents.hazard_agent import HazardAgent


def test_route_estimation_and_recommendation(tmp_path):
    r = RoadRiskAgent()
    df = r.load_data()
    r.train_model(save=False)
    segments = r.get_all_segments_with_risk()
    ra = RouteAgent(segments)
    # create candidate routes
    all_segs = list(segments['segment_id'])
    if len(all_segs) < 3:
        pytest.skip('Not enough segments for route tests')
    candidates = [('A',[all_segs[0], all_segs[1]]), ('B',[all_segs[0], all_segs[2]])]
    res = ra.recommend_safer_route(candidates)
    assert isinstance(res, list)
    assert all('route' in r for r in res)


def test_highlight_hazards(tmp_path):
    # use hazard agent db in tmp
    db_path = tmp_path / 'reports.db'
    h = HazardAgent(db_path=str(db_path))
    rid, sev = h.submit_report('Pothole','Near seg_1',28.7041,77.1025)
    r = RoadRiskAgent()
    segments = r.load_data()
    ra = RouteAgent(segments)
    reports = h.list_reports()
    hazards = ra.highlight_hazards_along_route(['seg_1'], reports)
    assert isinstance(hazards, list)
    # since same coords, expect at least one hazard
    assert len(hazards) >= 1
