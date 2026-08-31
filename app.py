"""Streamlit dashboard for Log Anomaly Detection & Monitoring."""
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from src.pipeline import LogAnomalyPipeline

st.set_page_config(page_title="Log Anomaly Monitor", page_icon="🔎", layout="wide")
st.title("🔎 Log Anomaly Detection & Monitoring")
st.caption("TF-IDF + Isolation Forest for distributed application logs")

with st.sidebar:
    st.header("Configuration")
    contamination = st.slider(
        "Expected anomaly rate", 0.01, 0.20, 0.05, 0.01,
        help="Approximate proportion of logs expected to be anomalous."
    )
    source = st.radio("Log source", ["Included sample", "Upload log file"])
    uploaded = st.file_uploader("Upload .log/.txt", type=["log", "txt"]) if source == "Upload log file" else None
    st.divider()
    st.markdown("**Model:** Isolation Forest")
    st.markdown("**Text features:** TF-IDF 1–2 grams")
    st.markdown("**Dashboard:** Streamlit + Plotly")

if uploaded:
    log_text = uploaded.getvalue().decode("utf-8", errors="replace")
else:
    log_text = (Path(__file__).parent / "data" / "sample_logs.log").read_text(encoding="utf-8")

try:
    with st.spinner("Parsing logs and detecting anomalies..."):
        results = LogAnomalyPipeline(contamination=contamination).fit_text(log_text)
except Exception as exc:
    st.error(f"Could not process the log file: {exc}")
    st.stop()

anomalies = results[results["is_anomaly"]].copy()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total logs", f"{len(results):,}")
c2.metric("Anomalies", f"{len(anomalies):,}")
c3.metric("Anomaly rate", f"{len(anomalies) / len(results) * 100:.1f}%")
c4.metric("Services", f"{results['service'].nunique():,}")

st.subheader("Monitoring overview")
left, right = st.columns(2)
with left:
    timeline = results.assign(window=results["timestamp"].dt.floor("5min")).groupby("window", dropna=False)["is_anomaly"].sum().reset_index(name="anomalies")
    st.plotly_chart(px.line(timeline, x="window", y="anomalies", markers=True, title="Anomalies over time"), use_container_width=True)
with right:
    service_counts = anomalies["service"].value_counts().reset_index()
    service_counts.columns = ["service", "anomalies"]
    st.plotly_chart(px.bar(service_counts, x="service", y="anomalies", title="Anomalies by service"), use_container_width=True)

left, right = st.columns(2)
with left:
    level_counts = results["level"].value_counts().reset_index()
    level_counts.columns = ["level", "logs"]
    st.plotly_chart(px.bar(level_counts, x="level", y="logs", title="Log levels"), use_container_width=True)
with right:
    st.plotly_chart(px.histogram(results, x="anomaly_score", nbins=25, title="Anomaly score distribution"), use_container_width=True)

st.subheader("🚨 Highest-risk events")
display_cols = ["timestamp", "service", "level", "anomaly_score", "severity", "status_code", "response_ms", "message"]
st.dataframe(anomalies[display_cols].head(25), use_container_width=True, hide_index=True)

st.subheader("Alert simulation")
if anomalies.empty:
    st.success("No anomalies detected at the current contamination setting.")
else:
    selected = st.selectbox(
        "Select an anomaly to simulate an alert",
        anomalies.index,
        format_func=lambda i: f"{results.loc[i, 'service']} · {results.loc[i, 'level']} · score {results.loc[i, 'anomaly_score']}"
    )
    event = results.loc[selected]
    if st.button("Trigger alert"):
        st.warning(
            f"ALERT — {event['severity']} anomaly in `{event['service']}` | "
            f"score={event['anomaly_score']} | status={event['status_code']} | {event['message']}"
        )

with st.expander("How the detector works"):
    st.markdown("""
1. **Parse:** extract timestamp, level, service and telemetry from each line.
2. **Normalize:** mask volatile identifiers such as IPs, UUIDs and numeric IDs.
3. **Vectorize:** convert normalized messages into TF-IDF features.
4. **Enrich:** add status code, response latency, message length and error-keyword signals.
5. **Detect:** Isolation Forest isolates unusual combinations without requiring labelled incidents.
6. **Explain:** rank events by anomaly risk and visualize where incidents cluster.
""")
