class WeatherAgent:
    """Analyzes provided weather inputs to detect weather-related road risks.
    For demo, accepts a simple weather dict and returns risk notes.
    """
    def __init__(self):
        pass

    def analyze_weather(self, weather):
        # weather: dict with keys like 'precip_mm', 'visibility_km', 'wind_kmph', 'condition'
        notes = []
        risk_level = 'low'
        if weather.get('precip_mm',0) > 10:
            notes.append('Heavy precipitation recorded — risk of waterlogging and reduced traction')
            risk_level = 'high'
        if weather.get('visibility_km',10) < 2:
            notes.append('Low visibility — increased collision risk')
            risk_level = 'high'
        if weather.get('condition','').lower() in ('thunderstorm','storm'):
            notes.append('Severe weather reported — avoid travel if possible')
            risk_level = 'critical'
        if not notes:
            notes.append('No significant weather-related risks detected')
        return {'risk_level':risk_level, 'notes':notes}
