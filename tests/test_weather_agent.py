from agents.weather_agent import WeatherAgent


def test_weather_analysis():
    w = WeatherAgent()
    out = w.analyze_weather({'precip_mm': 0, 'visibility_km': 10, 'condition':'clear'})
    assert out['risk_level'] in ('low','high','critical')
    out2 = w.analyze_weather({'precip_mm':20, 'visibility_km':1, 'condition':'rain'})
    assert out2['risk_level'] in ('high','critical')
