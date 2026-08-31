# Log Anomaly Detection & Monitoring System

A portfolio-ready Python project that parses distributed application logs, normalizes noisy fields, learns normal log-message patterns with **TF-IDF + Isolation Forest**, and exposes an interactive **Streamlit** monitoring dashboard.

## Features

- Regex-based parsing for semi-structured distributed logs
- Normalization of IPs, UUIDs, emails, IDs and other high-cardinality fields
- TF-IDF text features + numeric telemetry (status code, latency, message length, error signals)
- Unsupervised anomaly detection with Isolation Forest
- Interactive Streamlit + Plotly dashboard
- Anomaly timeline, service distribution, log-level distribution and risk scores
- Alert simulation for selected anomalies
- Synthetic log generator with injected incidents
- Unit tests

## Architecture

```text
Raw distributed logs
        |
        v
  Log Parser
        |
        v
  Normalizer
        |
        +----------------------+
        |                      |
        v                      v
   TF-IDF text          Numeric telemetry
        |                      |
        +----------+-----------+
                   v
          Feature Matrix
                   |
                   v
          Isolation Forest
                   |
                   v
       Anomaly score + label
                   |
                   v
      Streamlit Monitoring UI
```

## Quick start

```bash
git clone <your-repository-url>
cd log-anomaly-detection

python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Generate fresh logs

```bash
python generate_logs.py --rows 1500 --output data/sample_logs.log
```

The generator injects authentication failures, database latency spikes, HTTP 5xx responses, connection errors and unusual request patterns.

## Run tests

```bash
pytest -q
```

## Resume bullet

> **Log Anomaly Detection & Monitoring System** — Built an unsupervised monitoring pipeline for distributed logs using regex-based parsing, field normalization, TF-IDF feature extraction and Isolation Forest; developed a Streamlit/Plotly dashboard for anomaly scoring, service-level analysis and alert simulation.

## Tech stack

**Python · Pandas · Scikit-learn · TF-IDF · Isolation Forest · Streamlit · Plotly**

## Project structure

```text
log-anomaly-detection/
├── app.py
├── generate_logs.py
├── requirements.txt
├── README.md
├── LICENSE
├── data/
│   └── sample_logs.log
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── features.py
│   ├── model.py
│   └── pipeline.py
└── tests/
    └── test_parser.py
```
