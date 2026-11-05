from geopy.distance import geodesic

class RouteAgent:
    """Provides simple route safety comparison using available segment risk data.
    In this demo, routes are simulated as lists of segment IDs; in production, integrate with a routing API.
    """
    def __init__(self, segments_df):
        self.segments = segments_df

    def estimate_route_safety(self, route_segment_ids):
        # Compute aggregate risk for a route based on segment risk scores
        segs = self.segments[self.segments['segment_id'].isin(route_segment_ids)]
        if segs.empty:
            return {'route_score':None, 'segments':[]}
        # map categories to numeric
        mapv = {'low':0, 'moderate':1, 'high':2, 'critical':3}
        segs['risk_num'] = segs['predicted_risk'].map(mapv)
        route_score = float(segs['risk_num'].mean())
        segment_list = segs[['segment_id','predicted_risk','risk_score','latitude','longitude']].to_dict(orient='records')
        return {'route_score':route_score, 'segments':segment_list}

    def recommend_safer_route(self, candidate_routes):
        # candidate_routes: list of (route_name, [segment_ids])
        results = []
        for name, segs in candidate_routes:
            est = self.estimate_route_safety(segs)
            results.append({'route':name, 'score':est['route_score'], 'segments':est['segments']})
        sorted_routes = sorted(results, key=lambda x: (x['score'] is None, x['score']))
        return sorted_routes

    def highlight_hazards_along_route(self, route_segment_ids, reports):
        # reports: list of report dicts with lat/lon; flag reports within 0.01 degrees (~1km) of any segment
        hazards = []
        segs = self.segments[self.segments['segment_id'].isin(route_segment_ids)]
        for r in reports:
            rpt_loc = (r['latitude'], r['longitude'])
            for _, s in segs.iterrows():
                s_loc = (s['latitude'], s['longitude'])
                dist = geodesic(rpt_loc, s_loc).meters
                if dist < 500: # within 500m
                    hazards.append({'report_id':r['id'], 'hazard_type':r['hazard_type'], 'distance_m':dist, 'severity':r['severity']})
                    break
        return hazards
