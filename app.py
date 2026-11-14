import os
import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Cloud Cost Analyzer",
    page_icon="☁️",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USAGE_FILE = os.path.join(BASE_DIR, "data", "cloud_usage.csv")
DAILY_FILE = os.path.join(BASE_DIR, "data", "daily_costs.csv")

SUGGESTIONS = {
    "ec2": "Consider rightsizing the instance.",
    "database": "Review database capacity.",
    "storage": "Review unused storage."
}

DEFAULT_SUGGESTION = "Review resource utilization."


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>

.stApp {
    background:
    radial-gradient(circle at top left, #25205a, transparent 40%),
    #0B1020;
    color: #E8ECF8;
}

h1, h2, h3 {
    color: #E8ECF8 !important;
}

p, label {
    color: #B8C2DF;
}

.hero {
    background: linear-gradient(
        120deg,
        #4F46E5,
        #7C3AED,
        #06B6D4
    );
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: 0 10px 35px rgba(79,70,229,0.3);
}

.hero h1 {
    color: white !important;
    font-size: 34px;
}

.hero p {
    color: white !important;
    font-size: 16px;
}

div[data-testid="stMetric"] {
    background: #171D35;
    border: 1px solid #343D65;
    padding: 22px;
    border-radius: 16px;
    box-shadow: 0 5px 18px rgba(0,0,0,0.2);
}

div[data-testid="stMetric"] label {
    color: #9DAAD0 !important;
}

div[data-testid="stMetricValue"] {
    color: #22D3EE !important;
    font-weight: bold;
}

section[data-testid="stSidebar"] {
    background: #111832;
}

button[data-baseweb="tab"] {
    background: #171D35;
    border-radius: 10px;
    color: white;
    padding: 12px;
}

div[data-testid="stDataFrame"] {
    border: 1px solid #343D65;
    border-radius: 12px;
}

.stDownloadButton button {
    background: linear-gradient(120deg, #4F46E5, #7C3AED);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 20px;
}

.stDownloadButton button:hover {
    background: #06B6D4;
    color: white;
}

hr {
    border-color: #343D65;
}

</style>
""", unsafe_allow_html=True)


# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>☁️ Cloud Cost Analyzer</h1>
    <p>
        Track cloud spending, identify idle resources
        and optimize your cloud costs.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------------- DATA LOADING ----------------

@st.cache_data
def load_usage(path):

    df = pd.read_csv(path)

    required = [
        "resource_id",
        "service",
        "region",
        "cost",
        "utilization"
    ]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing columns: {', '.join(sorted(missing))}"
        )

    df["cost"] = pd.to_numeric(
        df["cost"].astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    )

    df["utilization"] = pd.to_numeric(
        df["utilization"].astype(str).str.replace("%", "", regex=False),
        errors="coerce"
    )

    df = df.dropna(subset=["cost"])

    return df


@st.cache_data
def load_daily(path):

    daily = pd.read_csv(path)

    daily["date"] = pd.to_datetime(
        daily["date"],
        errors="coerce"
    )

    daily["total_cost"] = pd.to_numeric(
        daily["total_cost"],
        errors="coerce"
    )

    return daily.dropna(
        subset=["date", "total_cost"]
    ).sort_values("date")


uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Cloud Usage CSV",
    type=["csv"]
)

try:
    if uploaded_file is not None:
        df = load_usage(uploaded_file)
        st.sidebar.success("CSV uploaded successfully!")
    else:
        df = load_usage(USAGE_FILE)

except FileNotFoundError:
    st.error("Cloud usage CSV file not found!")
    st.stop()

except ValueError as error:
    st.error(str(error))
    st.stop()


# ---------------- SIDEBAR FILTERS ----------------

st.sidebar.title("⚙️ Dashboard Settings")

st.sidebar.markdown("### 🔍 Filters")

services = sorted(df["service"].dropna().unique())

selected_services = st.sidebar.multiselect(
    "Select Services",
    services,
    default=services
)

regions = sorted(df["region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    regions,
    default=regions
)

st.sidebar.markdown("---")

idle_threshold = st.sidebar.slider(
    "Idle Utilization Threshold",
    0, 100, 20
)

top_n = st.sidebar.slider(
    "Top Expensive Resources",
    3, 10, 5
)

window = st.sidebar.slider(
    "Anomaly Window",
    2, 5, 3
)

anomaly_threshold = st.sidebar.slider(
    "Anomaly Threshold (%)",
    10, 200, 50
)


# ---------------- FILTER DATA ----------------

filtered = df[
    df["service"].isin(selected_services)
    & df["region"].isin(selected_regions)
].copy()

if filtered.empty:
    st.warning("No data available for selected filters.")
    st.stop()


# ---------------- CALCULATIONS ----------------

total_cost = filtered["cost"].sum()

total_resources = len(filtered)

average_cost = filtered["cost"].mean()

idle_df = filtered[
    filtered["utilization"] <= idle_threshold
].copy()

idle_cost = idle_df["cost"].sum()


# ---------------- KPI CARDS ----------------

st.markdown("## 📊 Cloud Cost Overview")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Resources", total_resources)

c2.metric("Total Cost", f"₹{total_cost:,.0f}")

c3.metric("Average Cost", f"₹{average_cost:,.0f}")

c4.metric("Idle Resources", len(idle_df))

c5.metric("Idle Cost", f"₹{idle_cost:,.0f}")

st.divider()


# ---------------- DASHBOARD TABS ----------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "💰 Top Expensive",
    "😴 Idle Resources",
    "🚨 Anomalies",
    "💡 Recommendations",
    "📋 Data"
])


# ---------------- OVERVIEW ----------------

with tab1:

    left, right = st.columns(2)

    with left:

        st.subheader("Service-wise Cost")

        service_cost = (
            filtered.groupby("service")["cost"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(service_cost)

    with right:

        st.subheader("Region-wise Cost")

        region_cost = (
            filtered.groupby("region")["cost"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(region_cost)

    st.subheader("Cost vs Utilization")

    scatter_df = filtered.dropna(
        subset=["utilization"]
    )

    st.scatter_chart(
        scatter_df,
        x="utilization",
        y="cost",
        color="service"
    )


# ---------------- TOP EXPENSIVE ----------------

with tab2:

    st.subheader("💰 Most Expensive Resources")

    top_resources = filtered.nlargest(
        top_n,
        "cost"
    ).sort_values(
        by="cost",
        ascending=False
    )

    st.bar_chart(
        top_resources.set_index("resource_id")["cost"],
        horizontal=True
    )

    st.dataframe(
        top_resources,
        width="stretch",
        hide_index=True
    )

    st.success("Top Expensive Resources Analysis Completed!")


# ---------------- IDLE RESOURCES ----------------

with tab3:

    st.subheader("😴 Idle Resource Detection")

    st.caption(
        f"Resources having utilization below or equal to {idle_threshold}%"
    )

    if idle_df.empty:

        st.success("No idle resources found!")

    else:

        idle_display = idle_df.sort_values(
            "cost",
            ascending=False
        )

        styled_idle = (
            idle_display.style
            .set_properties(**{
                "background-color": "#171f35",
                "color": "#ffffff",
                "border-color": "#334155"
            })
            .set_table_styles([
                {
                    "selector": "th",
                    "props": [
                        ("background-color", "#263451"),
                        ("color", "#ffffff"),
                        ("font-weight", "bold")
                    ]
                }
            ])
        )

        st.dataframe(
            styled_idle,
            width="stretch",
            hide_index=True
        )

        st.download_button(
            "⬇️ Download Idle Resources",
            idle_df.to_csv(index=False).encode("utf-8"),
            "idle_resources.csv",
            "text/csv"
        )


# ---------------- ANOMALY DETECTION ----------------

with tab4:

    st.subheader("🚨 Daily Cost Anomaly Detection")

    try:

        daily = load_daily(DAILY_FILE)

        daily["previous_avg"] = (
            daily["total_cost"]
            .rolling(window)
            .mean()
            .shift(1)
        )

        daily["increase_%"] = (
            (
                daily["total_cost"] - daily["previous_avg"]
            ) / daily["previous_avg"]
        ) * 100

        st.line_chart(
            daily.set_index("date")[["total_cost", "previous_avg"]]
        )

        anomalies = daily[
            daily["increase_%"] > anomaly_threshold
        ].dropna(
            subset=["increase_%"]
        )

        if anomalies.empty:

            st.success("No cost anomalies detected.")

        else:

            st.error(
                f"{len(anomalies)} cost anomaly detected!"
            )

            st.dataframe(
                anomalies[
                    [
                        "date",
                        "total_cost",
                        "previous_avg",
                        "increase_%"
                    ]
                ].round({
                    "total_cost": 2,
                    "previous_avg": 2,
                    "increase_%": 2
                }),
                width="stretch",
                hide_index=True
            )

            st.download_button(
                "⬇️ Download Anomalies",
                anomalies.to_csv(index=False).encode("utf-8"),
                "cost_anomalies.csv",
                "text/csv"
            )

    except FileNotFoundError:

        st.warning("Daily cost CSV file not found.")


# ---------------- RECOMMENDATIONS ----------------

with tab5:

    st.subheader("💡 Optimization Recommendations")

    if idle_df.empty:

        st.success("No optimization recommendations available.")

    else:

        recommendations = idle_df.copy()

        recommendations["recommendation"] = (
            recommendations["service"]
            .str.lower()
            .map(SUGGESTIONS)
            .fillna(DEFAULT_SUGGESTION)
        )

        recommendations = recommendations.sort_values(
            "cost",
            ascending=False
        )

        for _, row in recommendations.iterrows():

            st.markdown(
                f"""
                <div style="
                    background:#171D35;
                    border-left:5px solid #F59E0B;
                    padding:18px;
                    border-radius:12px;
                    margin-bottom:12px;
                ">
                    <h4 style="color:#22D3EE;">
                        {row['resource_id']}
                    </h4>
                    <p>Service: {row['service']}</p>
                    <p>Cost: ₹{row['cost']:,.2f}</p>
                    <p>Utilization: {row['utilization']}%</p>
                    <b style="color:#F59E0B;">
                        {row['recommendation']}
                    </b>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.download_button(
            "⬇️ Download Recommendations",
            recommendations.to_csv(index=False).encode("utf-8"),
            "recommendations.csv",
            "text/csv"
        )


# ---------------- RAW DATA ----------------

with tab6:

    st.subheader("📋 Complete Cloud Resource Data")

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True
    )

    st.download_button(
        "⬇️ Download CSV Data",
        filtered.to_csv(index=False).encode("utf-8"),
        "cloud_usage_filtered.csv",
        "text/csv"
    )


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <center style="color:#93A0C0;">
        ☁️ Cloud Cost Analyzer |
        MCA Mini Project 2026-27
        <br>
        Built using Python, DSA and Streamlit
    </center>
    """,
    unsafe_allow_html=True
)
