import os
import pytest
from agents.road_risk_agent import RoadRiskAgent


def test_load_data_and_preprocess():
    r = RoadRiskAgent()
    df = r.load_data()
    assert not df.empty
    X, y, d = r.preprocess(df)
    assert 'risk_label' in d.columns
    assert set(y.unique()).issubset({'low','moderate','high','critical'})


def test_train_and_predict(tmp_path):
    # ensure model saved to tmp path
    model_path = tmp_path / 'test_model.pkl'
    r = RoadRiskAgent(model_path=str(model_path))
    r.load_data()
    report, cm = r.train_model(save=True)
    assert r.model is not None
    # pick a row and predict
    row = r.df.iloc[0].to_dict()
    pred, score = r.predict_segment_risk(row)
    assert pred in ['low','moderate','high','critical']
    assert 0.0 <= score <= 1.0


def test_explain_segment():
    r = RoadRiskAgent()
    r.load_data()
    r.train_model(save=False)
    row = r.df.iloc[0].to_dict()
    expl = r.explain_segment(row)
    assert isinstance(expl, list)
    assert len(expl) > 0
