ROADGUARD AI

From Accident Hotspots to Accident Prevention

Overview

RoadGuard AI is an explainable, multi-agent road safety intelligence platform built as a Streamlit application. It demonstrates a functional MVP that identifies risky road segments, processes hazard reports, recommends safer routes, and helps authorities prioritize maintenance. The demo uses a small, clearly-labeled synthetic dataset for demonstration.

Important: The included dataset is synthetic/demo data for presentation purposes only. Do not treat any outputs as live or authoritative road-safety information.

Features

- Multi-agent architecture: Road Risk Intelligence Agent, Hazard Detection Agent, Smart Route Safety Agent, Emergency & Weather Agent, Authority Action Agent, Road Safety Assistant.
- Interactive map with risk-colored road segments (Folium) and a risk dashboard (Plotly).
- Hazard reporting form with image upload (image processing disabled for demo — images are stored only).
- Simple RandomForest risk classifier trained on a synthetic dataset with explainability via feature importances.
- SQLite store for hazard reports and their lifecycle (Submitted, Under Review, Prioritized, Resolved).

Installation

1. Create a Python 3.9+ virtual environment.

2. Install dependencies:

pip install -r requirements.txt

3. Run the Streamlit app:

streamlit run app.py

Project structure

- app.py                # Streamlit main app
- agents/               # Agent modules
  - __init__.py
  - road_risk_agent.py
  - hazard_agent.py
  - route_agent.py
  - weather_agent.py
  - authority_agent.py
  - assistant_agent.py
- models/               # Model training and utils
  - train_model.py
  - model_utils.py
  - risk_model.pkl      # created when training runs
- data/
  - sample_accidents.csv
- db/
  - reports.db          # created at runtime
- requirements.txt

Notes for judges

- The system demonstrates agent coordination: when a hazard report is submitted it updates the authority queue and influences route recommendations and risk explanations.
- The app is fully modular; models and agents can be swapped for production-grade components.
- All risk outputs are "decision-support" only. The app explicitly warns users that these are not guarantees of safety.

Next steps (if you continue development)

- Replace synthetic dataset with verified accident and road datasets (MoRTH, state open data).
- Add a proper image-analysis model for hazard photos.
- Integrate a geocoding / routing API for real route geometries and live traffic.
- Add SHAP explainability visualizations for model explanations.

License: MIT
