class AssistantAgent:
    """Conversational helper that routes user queries to appropriate agents.
    This is a rule-based assistant for demo purposes.
    """
    def __init__(self, road_risk_agent, hazard_agent, route_agent, weather_agent, authority_agent):
        self.risk_agent = road_risk_agent
        self.hazard_agent = hazard_agent
        self.route_agent = route_agent
        self.weather_agent = weather_agent
        self.authority_agent = authority_agent

    def handle_query(self, query):
        q = query.lower()
        if 'dangerous' in q or 'risk' in q:
            return 'You can select a road segment on the risk map to see its risk score, category, and contributing factors.'
        if 'report' in q and 'pothole' in q:
            return 'Use the Hazard Reporting form to submit a pothole report. Include location, description, and an optional image.'
        if 'heavy rain' in q or 'rain' in q:
            return 'During heavy rain, reduce speed, avoid standing water, and follow local advisories. The Emergency & Weather panel also shows weather-related risks.'
        return 'I can help with road risk explanations, recent hazards, and reporting steps. Try: "Why is segment seg_3 high risk?"'

    def explain_segment_by_id(self, segment_id):
        df = self.risk_agent.load_data()
        row = df[df['segment_id']==segment_id]
        if row.empty:
            return f'Segment {segment_id} not found in dataset.'
        row = row.iloc[0].to_dict()
        pred, score = self.risk_agent.predict_segment_risk(row)
        explanation = self.risk_agent.explain_segment(row)
        return {'segment_id':segment_id, 'predicted_risk':pred, 'score':score, 'explanation':explanation}
