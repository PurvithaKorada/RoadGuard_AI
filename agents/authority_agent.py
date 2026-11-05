class AuthorityAgent:
    """Processes reports and prioritizes maintenance actions.
    Uses report severity, proximity to high-risk segments, and report age to rank items.
    """
    def __init__(self, segments_df, hazard_agent):
        self.segments = segments_df
        self.hazard_agent = hazard_agent

    def prioritize_reports(self):
        reports = self.hazard_agent.list_reports()
        ranked = []
        # naive scoring: severity weight + proximity to critical/high segments
        sev_weight = {'critical':5,'high':3,'moderate':1,'low':0}
        for r in reports:
            score = sev_weight.get(r['severity'],1)
            # add proximity score: if near a critical/high segment, boost
            for _, s in self.segments.iterrows():
                if abs(s['latitude'] - r['latitude']) < 0.005 and abs(s['longitude'] - r['longitude']) < 0.005:
                    if s['predicted_risk']=='critical':
                        score += 5
                    elif s['predicted_risk']=='high':
                        score += 3
            ranked.append({'report':r, 'priority_score':score})
        ranked_sorted = sorted(ranked, key=lambda x: x['priority_score'], reverse=True)
        return ranked_sorted

    def suggest_action(self, report):
        # Simple mapping
        r = report
        if r['severity']=='critical':
            return 'Immediate site inspection and temporary traffic control. Arrange emergency drainage if waterlogging.'
        if r['severity']=='high':
            return 'Schedule repair within 7 days. Place warning signage.'
        if r['severity']=='moderate':
            return 'Monitor and include in routine maintenance.'
        return 'Monitor'
