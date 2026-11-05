import streamlit as st
import os
import uuid
import html as html_lib
import pandas as pd
import folium
import plotly.express as px

from streamlit.components.v1 import html
from agents import (
    RoadRiskAgent,
    HazardAgent,
    RouteAgent,
    WeatherAgent,
    AuthorityAgent,
    AssistantAgent
)

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="RoadGuard AI",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #08111f, #101d30);
    color: #e2f3ff;
}

[data-testid="stSidebar"] {
    background-color: #0b1728;
    border-right: 1px solid #1d3850;
}

[data-testid="stSidebar"] * {
    color: #d8efff;
}

h1, h2, h3 {
    color: #64d8ff !important;
}

p, label {
    color: #d1e5f5;
}

.stButton > button {
    background: linear-gradient(90deg, #05668d, #0284a8);
    color: white;
    border: none;
    border-radius: 9px;
    padding: 9px 18px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    background: #00a6c7;
    color: white;
    border: none;
}

div[data-testid="stMetric"] {
    background-color: #12243a;
    border: 1px solid #21435e;
    padding: 17px;
    border-radius: 12px;
}

div[data-testid="stMetricValue"] {
    color: #64d8ff;
}

.card {
    background: #12243a;
    border: 1px solid #21435e;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
}

.small-text {
    color: #91a9bd;
    font-size: 13px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #21435e;
    border-radius: 10px;
}

hr {
    border-color: #25445e;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# FOLDER SETUP
# =====================================================

os.makedirs("models", exist_ok=True)
os.makedirs("uploads", exist_ok=True)


# =====================================================
# MAP BASEMAPS (no API key required)
# =====================================================

BASEMAPS = {
    "Dark (Esri)": {
        "tiles": (
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        ),
        "attr": "Tiles © Esri — Esri, DeLorme, NAVTEQ"
    },
    "Light (Esri)": {
        "tiles": (
            "https://server.arcgisonline.com/ArcGIS/rest/services/"
            "Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        ),
        "attr": "Tiles © Esri — Esri, DeLorme, NAVTEQ"
    },
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None
    }
}


# =====================================================
# INITIALIZE AGENTS
# Keep instances in session state
# =====================================================

try:

    if "road_agent" not in st.session_state:

        st.session_state.road_agent = RoadRiskAgent()

    if "hazard_agent" not in st.session_state:

        st.session_state.hazard_agent = HazardAgent()

    if "weather_agent" not in st.session_state:

        st.session_state.weather_agent = WeatherAgent()

    road_agent = st.session_state.road_agent
    hazard_agent = st.session_state.hazard_agent
    weather_agent = st.session_state.weather_agent

    # Load or train model

    if "model_initialized" not in st.session_state:

        with st.spinner("Initializing Road Risk Prediction Model..."):

            model_loaded = road_agent.load_model()

            if not model_loaded:

                report, cm = road_agent.train_model(save=True)

                st.session_state.model_initialized = True

                st.toast("Demo risk model trained successfully!")

            else:

                st.session_state.model_initialized = True

    # Get road segments

    segments = road_agent.get_all_segments_with_risk()

    if segments is None or segments.empty:

        st.error("No road segment data available.")
        st.stop()

    # Initialize remaining agents

    route_agent = RouteAgent(segments)

    authority_agent = AuthorityAgent(
        segments,
        hazard_agent
    )

    assistant_agent = AssistantAgent(
        road_agent,
        hazard_agent,
        route_agent,
        weather_agent,
        authority_agent
    )

except Exception as e:

    st.error(f"Agent initialization failed: {e}")
    st.info("Check your agents.py file and model configuration.")
    st.stop()


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def risk_color(category):

    colors = {
        "low": "#16a34a",
        "moderate": "#eab308",
        "high": "#f97316",
        "critical": "#dc2626"
    }

    return colors.get(str(category).lower(), "#64748b")


def safe_value(value, default="N/A"):

    if pd.isna(value):
        return default

    return value


def get_reports():

    try:
        return hazard_agent.list_reports() or []

    except Exception:
        return []


def show_section(title, description=None):

    st.markdown(f"## {title}")

    if description:
        st.caption(description)


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

st.sidebar.markdown("""
# 🚦 ROADGUARD AI

### Intelligent Road Safety System

---
""")

mode = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Risk Map",
        "Report Hazard",
        "Route Safety",
        "Authority Dashboard",
        "Assistant"
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("### 🤖 AI AGENTS")

agents_list = [
    "Road Risk Agent",
    "Hazard Detection Agent",
    "Route Optimization Agent",
    "Weather Agent",
    "Authority Agent",
    "Assistant Agent"
]

for agent_name in agents_list:

    st.sidebar.markdown(f"🟢 {agent_name}")

st.sidebar.markdown("---")

st.sidebar.caption(
    "RoadGuard AI | Multi-Agent Road Safety Platform"
)


# =====================================================
# OVERVIEW DASHBOARD
# =====================================================

if mode == "Overview":

    st.title("🚦 ROADGUARD AI")

    st.subheader(
        "See the Risk. Understand the Danger. Prevent the Next Accident."
    )

    st.markdown(
        "An intelligent multi-agent system for road risk prediction, "
        "hazard reporting and safer route recommendations."
    )

    reports = get_reports()

    total_segments = len(segments)

    high_risk = len(
        segments[
            segments["predicted_risk"].astype(str).str.lower().isin(
                ["high", "critical"]
            )
        ]
    )

    total_reports = len(reports)

    critical_reports = len([
        r for r in reports
        if str(r.get("severity", "")).lower() == "critical"
        and str(r.get("status", "")).lower() == "submitted"
    ])

    # KPI CARDS

    st.markdown("### 📊 System Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Road Segments",
        total_segments,
        help="Total analyzed road segments"
    )

    c2.metric(
        "High Risk Segments",
        high_risk
    )

    c3.metric(
        "Hazard Reports",
        total_reports
    )

    c4.metric(
        "Critical Pending",
        critical_reports
    )

    st.markdown("---")

    # CHARTS

    col1, col2 = st.columns([1.3, 1])

    with col1:

        show_section(
            "📈 Road Risk Distribution",
            "Distribution of predicted risk categories"
        )

        risk_counts = (
            segments["predicted_risk"]
            .value_counts()
            .rename_axis("Risk Category")
            .reset_index(name="Count")
        )

        fig = px.pie(
            risk_counts,
            names="Risk Category",
            values="Count",
            hole=0.55,
            color="Risk Category",
            color_discrete_map={
                "low": "#16a34a",
                "moderate": "#eab308",
                "high": "#f97316",
                "critical": "#dc2626"
            }
        )

        fig.update_layout(
            paper_bgcolor="#12243a",
            plot_bgcolor="#12243a",
            font_color="white",
            legend_title="Risk Level"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        show_section(
            "⚠️ Risk Category Summary"
        )

        for category in ["low", "moderate", "high", "critical"]:

            count = len(
                segments[
                    segments["predicted_risk"].astype(str).str.lower()
                    == category
                ]
            )

            st.markdown(
                f"""
                <div class="card">
                    <span style="color:{risk_color(category)};
                    font-weight:bold;">
                    ● {category.upper()}
                    </span>
                    <h2>{count}</h2>
                    <span class="small-text">Road segments</span>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("---")

    # RECENT REPORTS

    show_section(
        "📋 Recent Hazard Reports",
        "Latest reported road hazards"
    )

    if reports:

        df = pd.DataFrame(reports)

        if "created_at" in df.columns:

            df = df.sort_values(
                "created_at",
                ascending=False
            )

        display_columns = [
            c for c in [
                "id",
                "hazard_type",
                "severity",
                "status",
                "created_at"
            ]
            if c in df.columns
        ]

        st.dataframe(
            df[display_columns].head(8),
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info("No hazard reports submitted yet.")

    st.caption(
        "Predictions use demo data and should not be treated "
        "as verified real-world road safety assessments."
    )


# =====================================================
# INTERACTIVE RISK MAP
# =====================================================

elif mode == "Risk Map":

    st.title("🗺️ Interactive Road Risk Map")

    st.write(
        "Explore road segments and identify their predicted risk levels."
    )

    required = [
        "latitude",
        "longitude",
        "segment_id",
        "predicted_risk",
        "risk_score"
    ]

    missing = [c for c in required if c not in segments.columns]

    if missing:

        st.error(f"Missing map columns: {missing}")
        st.stop()

    map_col1, map_col2 = st.columns([4, 1])

    with map_col2:

        selected_risks = st.multiselect(
            "Filter risk categories",
            ["low", "moderate", "high", "critical"],
            default=["low", "moderate", "high", "critical"]
        )

        basemap_choice = st.selectbox(
            "Basemap",
            list(BASEMAPS.keys()),
            index=0
        )

    map_segments = segments[
        segments["predicted_risk"].astype(str).str.lower().isin(
            selected_risks
        )
    ]

    with map_col1:

        st.markdown("### Road Segment Map")

        if map_segments.empty:

            st.warning("No segments match the selected filters.")

        else:

            center_lat = map_segments["latitude"].mean()
            center_lon = map_segments["longitude"].mean()

            basemap = BASEMAPS[basemap_choice]

            map_kwargs = dict(
                location=[center_lat, center_lon],
                zoom_start=13,
                tiles=basemap["tiles"],
                control_scale=True
            )

            if basemap["attr"]:
                map_kwargs["attr"] = basemap["attr"]

            m = folium.Map(**map_kwargs)

            for _, r in map_segments.iterrows():

                category = str(r["predicted_risk"]).lower()

                popup_text = f"""
                <b>{html_lib.escape(str(r['segment_id']))}</b><br>
                Risk: {html_lib.escape(category)}<br>
                Score: {r['risk_score']}<br>
                Accidents: {r.get('num_accidents', 'N/A')}
                """

                popup = folium.Popup(
                    popup_text,
                    max_width=300
                )

                folium.CircleMarker(
                    location=[
                        r["latitude"],
                        r["longitude"]
                    ],
                    radius=9,
                    color=risk_color(category),
                    fill=True,
                    fill_color=risk_color(category),
                    fill_opacity=0.85,
                    popup=popup,
                    tooltip=str(r["segment_id"])
                ).add_to(m)

            # Render the full map page (not the padded preview iframe)
            # so it fills the available width without cropping.
            html(
                m.get_root().render(),
                height=550,
                scrolling=False
            )

    st.markdown("### 🎨 Map Legend")

    legend_cols = st.columns(4)

    for col, category in zip(
        legend_cols,
        ["low", "moderate", "high", "critical"]
    ):

        col.markdown(
            f"""
            <div style="background:#12243a;
            padding:12px;border-radius:10px;">
            <span style="color:{risk_color(category)};">
            ● {category.upper()}
            </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    show_section("🔍 Road Segment Analysis")

    seg_options = segments["segment_id"].tolist()

    seg_id = st.selectbox(
        "Choose a road segment",
        seg_options
    )

    if seg_id:

        row = segments[
            segments["segment_id"] == seg_id
        ].iloc[0].to_dict()

        try:

            pred, score = road_agent.predict_segment_risk(row)

            st.markdown("#### Prediction Results")

            c1, c2, c3 = st.columns(3)

            c1.metric("Segment ID", str(seg_id))

            c2.metric("Predicted Risk", str(pred).upper())

            c3.metric("Risk Score", f"{float(score):.3f}")

            st.markdown("#### 🧠 Risk Explanation")

            explanation = road_agent.explain_segment(row)

            if explanation:

                exp_df = pd.DataFrame(explanation)

                st.dataframe(
                    exp_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:

                st.info("No explanation available.")

        except Exception as e:

            st.warning(f"Could not generate explanation: {e}")

        # Nearby reports

        st.markdown("#### 📍 Nearby Hazard Reports")

        nearby = []

        for rpt in get_reports():

            try:

                if (
                    abs(float(rpt["latitude"]) - float(row["latitude"])) < 0.01
                    and
                    abs(float(rpt["longitude"]) - float(row["longitude"])) < 0.01
                ):

                    nearby.append(rpt)

            except (KeyError, TypeError, ValueError):
                continue

        if nearby:

            st.dataframe(
                pd.DataFrame(nearby),
                use_container_width=True
            )

        else:

            st.info("No nearby hazard reports found.")


# =====================================================
# HAZARD REPORTING
# =====================================================

elif mode == "Report Hazard":

    st.title("🚧 Report a Road Hazard")

    st.write(
        "Help improve road safety by reporting potholes, "
        "waterlogging, damaged roads and other hazards."
    )

    with st.form("report_form", clear_on_submit=True):

        st.markdown("### Hazard Information")

        htype = st.selectbox(
            "Hazard Type",
            [
                "Pothole",
                "Waterlogging",
                "Poor lighting",
                "Debris/Obstacle",
                "Damaged road",
                "Accident-prone area",
                "Other"
            ]
        )

        desc = st.text_area(
            "Description",
            placeholder=(
                "Describe the hazard, its size, "
                "severity and nearby landmarks..."
            )
        )

        st.markdown("### 📍 Location Details")

        c1, c2 = st.columns(2)

        with c1:

            lat = st.number_input(
                "Latitude",
                min_value=-90.0,
                max_value=90.0,
                value=17.3850,
                format="%.6f"
            )

        with c2:

            lon = st.number_input(
                "Longitude",
                min_value=-180.0,
                max_value=180.0,
                value=78.4867,
                format="%.6f"
            )

        st.caption(
            "Default coordinates point to Hyderabad. "
            "Change them to the actual hazard location."
        )

        st.markdown("### 📸 Upload Hazard Image")

        img = st.file_uploader(
            "Upload an optional road hazard photograph",
            type=["jpg", "jpeg", "png"]
        )

        submitted = st.form_submit_button(
            "🚨 Submit Hazard Report",
            use_container_width=True
        )

        if submitted:

            if not desc.strip():

                st.error("Please provide a hazard description.")

            else:

                try:

                    img_path = None

                    if img is not None:

                        extension = os.path.splitext(img.name)[1].lower()

                        unique_name = (
                            f"{uuid.uuid4().hex}{extension}"
                        )

                        img_path = os.path.join(
                            "uploads",
                            unique_name
                        )

                        with open(img_path, "wb") as f:

                            f.write(img.getbuffer())

                    rid, severity = hazard_agent.submit_report(
                        htype,
                        desc,
                        lat,
                        lon,
                        image_path=img_path
                    )

                    st.success(
                        f"Report submitted successfully! "
                        f"Report ID: {rid}"
                    )

                    st.metric(
                        "Estimated Severity",
                        str(severity).upper()
                    )

                    st.info(
                        "Your report has been submitted "
                        "to the authority review queue."
                    )

                    st.caption(
                        "Uploaded images are stored for review. "
                        "They are not automatically analyzed in this demo."
                    )

                except Exception as e:

                    st.error(f"Report submission failed: {e}")


# =====================================================
# SMART ROUTE SAFETY
# =====================================================

elif mode == "Route Safety":

    st.title("🛣️ Smart Route Safety")

    st.write(
        "Compare simulated route options using predicted "
        "road risks and available hazard reports."
    )

    seg_options = segments["segment_id"].tolist()

    if len(seg_options) < 2:

        st.warning("At least two road segments are required.")
        st.stop()

    c1, c2 = st.columns(2)

    with c1:

        start = st.selectbox(
            "📍 Starting Segment",
            seg_options,
            key="route_start"
        )

    with c2:

        end_options = [
            s for s in seg_options
            if s != start
        ]

        end = st.selectbox(
            "🏁 Destination Segment",
            end_options,
            key="route_end"
        )

    st.markdown("---")

    if st.button(
        "🔍 Evaluate Safe Routes",
        use_container_width=True
    ):

        try:

            # Select a low-risk intermediate segment
            # that is different from the start and end.

            low_seg = segments[
                segments["predicted_risk"].astype(str).str.lower()
                == "low"
            ]

            low_seg = low_seg[
                ~low_seg["segment_id"].isin([start, end])
            ]

            if not low_seg.empty:

                mid = low_seg.iloc[0]["segment_id"]

                candidates = [
                    ("Direct Route", [start, end]),
                    ("Alternate Route", [start, mid, end])
                ]

            else:

                candidates = [
                    ("Direct Route", [start, end])
                ]

            results = route_agent.recommend_safer_route(
                candidates
            )

            if not results:

                st.warning("No route results were returned.")

            else:

                # Lower score is assumed to mean safer,
                # as specified by the existing route agent.

                valid_results = [
                    r for r in results
                    if r.get("segments")
                ]

                if not valid_results:

                    st.warning("No valid route segments returned.")

                else:

                    chosen = min(
                        valid_results,
                        key=lambda r: float(r["score"])
                    )

                    st.session_state.route_results = results
                    st.session_state.chosen_route = chosen

        except Exception as e:

            st.error(f"Route evaluation failed: {e}")

    # Display stored route results

    if "route_results" in st.session_state:

        results = st.session_state.route_results

        chosen = st.session_state.chosen_route

        st.markdown("### 📊 Route Comparison")

        st.caption(
            "Lower safety score indicates a safer route "
            "according to the existing route agent."
        )

        for r in results:

            with st.container(border=True):

                st.markdown(
                    f"#### {r['route']}"
                )

                st.metric(
                    "Safety Score",
                    f"{float(r['score']):.3f}"
                )

                if r.get("route") == chosen.get("route"):

                    st.success("Recommended route based on the model score.")

                if r.get("segments"):

                    st.dataframe(
                        pd.DataFrame(r["segments"]),
                        use_container_width=True,
                        hide_index=True
                    )

        # Hazards along recommended route

        st.markdown("### ⚠️ Hazards Along Recommended Route")

        route_ids = [
            s["segment_id"]
            for s in chosen.get("segments", [])
        ]

        hazards = route_agent.highlight_hazards_along_route(
            route_ids,
            get_reports()
        )

        if hazards:

            st.dataframe(
                pd.DataFrame(hazards),
                use_container_width=True,
                hide_index=True
            )

        else:

            st.success(
                "No matching reported hazards detected "
                "along the selected route."
            )

        st.warning(
            "These routes are simulated using available segment data. "
            "They are not verified navigable roads or real-time directions."
        )


# =====================================================
# AUTHORITY DASHBOARD
# =====================================================

elif mode == "Authority Dashboard":

    st.title("🏛️ Authority Dashboard")

    st.write(
        "Review, prioritize and manage submitted road hazard reports."
    )

    reports = get_reports()

    # Report statistics

    total = len(reports)

    submitted = len([
        r for r in reports
        if r.get("status") == "Submitted"
    ])

    under_review = len([
        r for r in reports
        if r.get("status") == "Under Review"
    ])

    resolved = len([
        r for r in reports
        if r.get("status") == "Resolved"
    ])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Reports", total)

    c2.metric("New Reports", submitted)

    c3.metric("Under Review", under_review)

    c4.metric("Resolved", resolved)

    st.markdown("---")

    show_section("📋 Report Management")

    if reports:

        try:

            prioritized = authority_agent.prioritize_reports()

        except Exception as e:

            st.error(f"Could not prioritize reports: {e}")
            prioritized = []

        if prioritized:

            for item in prioritized:

                r = item["report"]

                with st.container(border=True):

                    st.markdown(
                        f"### 🚨 Report {r.get('id', 'N/A')}"
                    )

                    col1, col2, col3 = st.columns(3)

                    col1.metric(
                        "Severity",
                        str(r.get("severity", "N/A")).upper()
                    )

                    col2.metric(
                        "Priority Score",
                        str(item.get("priority_score", "N/A"))
                    )

                    col3.metric(
                        "Status",
                        str(r.get("status", "N/A"))
                    )

                    st.write(
                        f"**Hazard:** {r.get('hazard_type', 'N/A')}"
                    )

                    st.write(
                        f"**Description:** {r.get('description', 'N/A')}"
                    )

                    st.write(
                        f"**Location:** "
                        f"{r.get('latitude', 'N/A')}, "
                        f"{r.get('longitude', 'N/A')}"
                    )

                    image_path = r.get("image_path")

                    if image_path and os.path.isfile(image_path):

                        st.image(
                            image_path,
                            caption="Submitted hazard photograph",
                            width=350
                        )

                    st.markdown("#### Suggested Action")

                    try:

                        suggestion = authority_agent.suggest_action(r)

                        st.info(suggestion)

                    except Exception:

                        st.info("Manual inspection recommended.")

                    st.markdown("#### Update Report Status")

                    b1, b2, b3 = st.columns(3)

                    with b1:

                        if st.button(
                            "🔎 Under Review",
                            key=f"review_{r.get('id')}"
                        ):

                            hazard_agent.update_status(
                                r["id"],
                                "Under Review"
                            )

                            st.rerun()

                    with b2:

                        if st.button(
                            "⭐ Prioritize",
                            key=f"priority_{r.get('id')}"
                        ):

                            hazard_agent.update_status(
                                r["id"],
                                "Prioritized"
                            )

                            st.rerun()

                    with b3:

                        if st.button(
                            "✅ Resolve",
                            key=f"resolve_{r.get('id')}"
                        ):

                            hazard_agent.update_status(
                                r["id"],
                                "Resolved"
                            )

                            st.rerun()

        else:

            st.info("No reports available for prioritization.")

    else:

        st.success("No hazard reports have been submitted yet.")


# =====================================================
# AI ROAD SAFETY ASSISTANT
# =====================================================

elif mode == "Assistant":

    st.title("🤖 Road Safety AI Assistant")

    st.write(
        "Ask questions about road risks, hazard reports, "
        "road segments and safety precautions."
    )

    st.markdown(
        """
        <div class="card">
        <h3>How can I help?</h3>
        <p>Ask me about:</p>
        <ul>
        <li>Road segment risk predictions</li>
        <li>Hazard reporting procedures</li>
        <li>Road safety precautions</li>
        <li>Safer route recommendations</li>
        <li>Road risk explanations</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
    )

    # QUESTION ASSISTANT

    st.markdown("### 💬 Ask a Question")

    q = st.text_input(
        "Your question",
        placeholder="Example: Which road segments have high risk?"
    )

    if st.button("Ask AI Assistant"):

        if not q.strip():

            st.warning("Please enter a question.")

        else:

            with st.spinner("AI agents are analyzing your question..."):

                try:

                    response = assistant_agent.handle_query(q)

                    st.markdown("### 🧠 Assistant Response")

                    st.write(response)

                except Exception as e:

                    st.error(f"Assistant error: {e}")

    st.markdown("---")

    # SEGMENT EXPLANATION

    st.markdown("### 🔍 Explain a Road Segment")

    seg_q = st.selectbox(
        "Select Segment ID",
        segments["segment_id"].tolist()
    )

    if st.button("Explain Segment"):

        with st.spinner("Analyzing segment..."):

            try:

                output = assistant_agent.explain_segment_by_id(
                    str(seg_q)
                )

                st.markdown("### Segment Analysis")

                st.json(output)

            except Exception as e:

                st.error(f"Segment explanation failed: {e}")

    st.markdown("---")

    # QUICK STATISTICS

    st.markdown("### 📊 Current Road Network")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Analyzed Segments",
        len(segments)
    )

    c2.metric(
        "High Risk Segments",
        len(
            segments[
                segments["predicted_risk"].astype(str).str.lower()
                .isin(["high", "critical"])
            ]
        )
    )

    c3.metric(
        "Reported Hazards",
        len(get_reports())
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center;padding:15px;">

    <h3>🚦 ROADGUARD AI</h3>

    <p style="color:#64d8ff;">
    See the Risk. Understand the Danger. Prevent the Next Accident.
    </p>

    <p style="color:#91a9bd;font-size:12px;">
    Multi-Agent AI Road Safety Decision Support System
    <br>
    Demo application | Synthetic data | Model predictions
    <br>
    Not intended for real-world safety-critical decisions.
    </p>

    </div>
    """,
    unsafe_allow_html=True
)