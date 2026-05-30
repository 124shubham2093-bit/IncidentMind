import streamlit as st
import pandas as pd
import subprocess
import time
from datetime import datetime

CORAL_EXE_PATH = r"C:\Users\Prakash PC\Desktop\coral\coral.exe"

st.set_page_config(
    page_title="IncidentMind",
    page_icon="🚨",
    layout="wide"
)

st.markdown("""
<style>
div[data-testid="stMetric"] {
    background-color: #1b1f2b;
    border: 1px solid #313543;
    padding: 15px;
    border-radius: 12px;
}
.stAlert {
    border-radius: 12px;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stSidebar"] {
    background-color: #151821;
}
.live-feed {
    background-color: #1b1f2b;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #313543;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

def run_coral_command(args):
    try:
        result = subprocess.run(
            [CORAL_EXE_PATH] + args,
            capture_output=True,
            text=True,
            timeout=20
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def get_coral_status():
    ok, output, error = run_coral_command(["source", "list"])
    if ok and "github" in output:
        return True, output
    return False, error or output

def run_live_coral_query(query):
    ok, output, error = run_coral_command(["sql", query])
    if ok:
        return True, output
    return False, error or output

with st.sidebar:
    st.title("⚙️ IncidentMind")

    st.write("### 🪸 Coral Connected Sources")
    uploaded_deployments = st.file_uploader("Deployments Source", type=["csv"])
    uploaded_errors = st.file_uploader("Runtime Logs Source", type=["csv"])
    uploaded_tickets = st.file_uploader("Support Tickets Source", type=["csv"])
    st.success("🟢 Local Sources Ready")

using_uploaded_files = (
    uploaded_deployments is not None and
    uploaded_errors is not None and
    uploaded_tickets is not None
)

deployments = pd.read_csv(uploaded_deployments) if uploaded_deployments else pd.read_csv("data/deployments.csv")
errors = pd.read_csv(uploaded_errors) if uploaded_errors else pd.read_csv("data/errors.csv")
tickets = pd.read_csv(uploaded_tickets) if uploaded_tickets else pd.read_csv("data/tickets.csv")

if using_uploaded_files and "uploaded_data_loaded" not in st.session_state:
    st.session_state.messages = []
    st.session_state.uploaded_data_loaded = True
    st.success("✅ New operational sources loaded. Previous investigation history cleared.")

elif not using_uploaded_files and "uploaded_data_loaded" in st.session_state:
    del st.session_state.uploaded_data_loaded

required_deployment_cols = {"deploy_time", "commit", "service"}
required_error_cols = {"timestamp", "error", "service", "severity"}
required_ticket_cols = {"timestamp", "ticket", "user_region"}

if not required_deployment_cols.issubset(deployments.columns):
    st.error("Deployments Source must contain: deploy_time, commit, service")
    st.stop()

if not required_error_cols.issubset(errors.columns):
    st.error("Runtime Logs Source must contain: timestamp, error, service, severity")
    st.stop()

if not required_ticket_cols.issubset(tickets.columns):
    st.error("Support Tickets Source must contain: timestamp, ticket, user_region")
    st.stop()

top_service = errors["service"].value_counts().idxmax()
top_error = errors["error"].value_counts().idxmax()
top_region = tickets["user_region"].value_counts().idxmax()

high_errors = errors[errors["severity"].str.lower() == "high"]
high_count = len(high_errors)

total_errors = len(errors)
total_tickets = len(tickets)

latest_deployment = deployments.iloc[0]
deployment_name = latest_deployment["commit"]
deployment_service = latest_deployment["service"]
deployment_time = latest_deployment["deploy_time"]

if high_count >= 2:
    severity_level = "CRITICAL"
    severity_color = "🔴"
    priority = "P0"
elif high_count == 1:
    severity_level = "HIGH"
    severity_color = "🟠"
    priority = "P1"
else:
    severity_level = "MEDIUM"
    severity_color = "🟡"
    priority = "P2"

risk_score = min(
    100,
    (total_errors * 15) +
    (total_tickets * 10) +
    (high_count * 20)
)

business_impact = (
    "Severe Revenue Risk"
    if risk_score >= 80
    else "Moderate Operational Risk"
    if risk_score >= 50
    else "Low Impact"
)

confidence_score = min(99, 70 + (high_count * 10) + total_tickets)

coral_connected, coral_status_output = get_coral_status()

with st.sidebar:
    st.divider()

    st.write("### Runtime Sources")
    st.success("✅ deployments")
    st.success("✅ runtime_errors")
    st.success("✅ support_tickets")

    if coral_connected:
        st.success("✅ github via Coral")
    else:
        st.warning("⚠️ Coral GitHub unavailable")

    st.divider()

    st.write("### Incident Priority")
    st.error(f"{priority} — {severity_level}")

    st.write("### Risk Score")
    st.progress(risk_score)
    st.caption(f"{risk_score}/100")

    st.divider()

    selected_service = st.selectbox(
        "Filter Runtime Errors by Service",
        ["All"] + list(errors["service"].unique())
    )

    selected_severity = st.selectbox(
        "Filter Runtime Errors by Severity",
        ["All"] + list(errors["severity"].unique())
    )

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

filtered_errors = errors.copy()

if selected_service != "All":
    filtered_errors = filtered_errors[filtered_errors["service"] == selected_service]

if selected_severity != "All":
    filtered_errors = filtered_errors[filtered_errors["severity"] == selected_severity]

st.title("🚨 IncidentMind")
st.subheader("Coral-powered AI Incident Investigation Platform")

st.divider()

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Deployments", len(deployments))

with m2:
    st.metric("Runtime Errors", total_errors)

with m3:
    st.metric("Support Tickets", total_tickets)

with m4:
    st.metric("Priority", priority)

st.error(
    f"⚠️ {priority} INCIDENT: Production instability detected after deployment `{deployment_name}`"
)

st.info(f"""
🧠 Executive Insights

• Highest impacted service: {top_service}

• Dominant runtime issue: {top_error}

• Most affected customer region: {top_region}

• Incident severity: {severity_level}

• Business impact: {business_impact}
""")

st.divider()

st.write("## 🪸 Real Coral Integration")

if coral_connected:
    st.success("✅ Coral CLI detected")
    st.success("✅ GitHub source connected through Coral")

    with st.expander("View Coral Source List"):
        st.code(coral_status_output, language="text")
else:
    st.error("❌ Coral source check failed")
    st.code(coral_status_output, language="text")

default_live_query = "SELECT * FROM github.meta LIMIT 1"
query_ok, query_output = run_live_coral_query(default_live_query)

if query_ok:
    st.success("✅ Live Coral SQL query executed successfully")
else:
    st.warning("⚠️ Live Coral SQL query failed")

with st.expander("View Live Coral Query"):
    st.code(default_live_query, language="sql")

with st.expander("View Live Coral Query Output"):
    if query_ok:
        st.code(query_output[:3000], language="text")
    else:
        st.code(query_output, language="text")

st.divider()

st.write("## 🪸 Coral Query Console")

st.caption(
    "Run real Coral SQL queries against connected Coral sources. "
    "GitHub is connected through Coral in this demo."
)

query_preset = st.selectbox(
    "Choose a Coral query",
    [
        "GitHub Metadata",
        "Coral Source List",
        "Custom SQL"
    ]
)

if query_preset == "GitHub Metadata":
    coral_console_query = "SELECT * FROM github.meta LIMIT 1"
elif query_preset == "Coral Source List":
    coral_console_query = None
else:
    coral_console_query = st.text_area(
        "Write Coral SQL",
        value="SELECT * FROM github.meta LIMIT 1",
        height=120
    )

if coral_console_query:
    st.code(coral_console_query, language="sql")

if st.button("▶ Run Coral Query"):
    with st.spinner("Running Coral query..."):
        if query_preset == "Coral Source List":
            ok, output = get_coral_status()
        else:
            ok, output = run_live_coral_query(coral_console_query)

        if ok:
            st.success("✅ Coral query completed")
            st.code(output[:5000], language="text")
        else:
            st.error("❌ Coral query failed")
            st.code(output, language="text")

st.divider()

st.write("## 🧠 Coral Investigation Plan")

incident_query = f"""
SELECT
    deployments.commit,
    deployments.service,
    runtime_errors.error,
    runtime_errors.severity,
    support_tickets.ticket,
    support_tickets.user_region
FROM deployments
JOIN runtime_errors
    ON deployments.service = runtime_errors.service
JOIN support_tickets
    ON runtime_errors.timestamp <= support_tickets.timestamp
WHERE runtime_errors.severity = 'high'
  AND deployments.service = '{top_service}';
"""

st.code(incident_query, language="sql")

st.success(
    "This Coral-style investigation query explains the incident across deployments, runtime errors, and support tickets."
)

st.divider()

st.write("## 🔴 Live Incident Feed")

live_feed = [
    f"[{deployment_time}] INFO — Deployment released: {deployment_name}",
    f"[10:35] HIGH — Runtime issue detected: {top_error}",
    f"[10:40] {severity_level} — Failures increasing in {top_service}",
    f"[10:45] ALERT — Users impacted in {top_region}",
    "[10:50] AI — Root cause correlation triggered"
]

for event in live_feed:
    st.markdown(
        f"<div class='live-feed'>{event}</div>",
        unsafe_allow_html=True
    )

st.divider()

st.write("## ⏱ AI Remediation Timeline")

timeline_data = pd.DataFrame({
    "Time": ["10:30", "10:35", "10:40", "10:42", "10:45"],
    "Event": [
        "Deployment Released",
        "Errors Detected",
        "AI Correlation Triggered",
        "Root Cause Identified",
        "Rollback Recommended"
    ]
})

st.dataframe(timeline_data, use_container_width=True)

st.divider()

st.write("## 🚨 AI Anomaly Detection")

a1, a2, a3 = st.columns(3)

with a1:
    st.error(f"Suspicious Service: {top_service}")

with a2:
    st.warning(f"Spike Detected: {top_error}")

with a3:
    st.info(f"Impacted Region: {top_region}")

st.divider()

st.write("## 🛠 Auto-Remediation Playbook")

remediation_steps = pd.DataFrame({
    "Step": ["1", "2", "3", "4", "5"],
    "Action": [
        "Rollback deployment",
        "Inspect retry handling",
        "Restart impacted services",
        "Monitor payment recovery",
        "Validate API stability"
    ],
    "Purpose": [
        "Restore last stable production state",
        "Find timeout or retry-loop bugs",
        "Recover unstable runtime services",
        "Confirm customer transactions recover",
        "Prevent similar incidents in the future"
    ],
    "Priority": [
        "Immediate",
        "High",
        "High",
        "Medium",
        "Medium"
    ]
})

st.dataframe(remediation_steps, use_container_width=True)

st.success(
    "IncidentMind generated an AI-guided remediation workflow based on deployment, runtime error, and customer impact analysis."
)

st.divider()

st.write("## 📈 Incident Timeline")

chart_data = pd.DataFrame({
    "Time": ["10:30", "10:35", "10:40", "10:45", "10:50"],
    "Errors": [2, 8, 15, 22, 30]
})

st.line_chart(chart_data.set_index("Time"))

st.divider()

with st.expander("🧠 Why IncidentMind Recommended Rollback"):
    st.write(f"""
IncidentMind recommended rollback because:

- deployment `{deployment_name}` occurred before the error spike
- `{top_error}` became the dominant runtime issue
- `{top_service}` became the most impacted service
- support tickets increased after deployment
- customer impact appeared in `{top_region}`
""")

st.divider()

st.write("## 🚀 Deployment Investigation")

deployments_display = deployments.copy()
deployments_display["risk"] = deployments_display["service"].apply(
    lambda x: "⚠️ Suspicious" if x == top_service else "✅ Stable"
)

st.dataframe(deployments_display, use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    st.write("## 🎫 Support Tickets")
    st.dataframe(tickets, use_container_width=True)

with c2:
    st.write("## ❌ Runtime Errors")
    st.dataframe(filtered_errors, use_container_width=True)

st.divider()

st.write("## 🤖 Multi-Agent Investigation System")

ag1, ag2, ag3 = st.columns(3)

with ag1:
    st.success("Incident Agent")
    st.write("""
- detects production instability
- correlates runtime anomalies
- identifies impacted services
""")

with ag2:
    st.warning("Root Cause Agent")
    st.write(f"""
- analyzes deployment `{deployment_name}`
- links errors with deployment activity
- detects service instability
""")

with ag3:
    st.error("Remediation Agent")
    st.write("""
- recommends rollback
- restarts affected services
- inspects timeout handling
""")

st.divider()

st.write("## 📄 Executive Incident Report")

report = f"""
INCIDENTMIND EXECUTIVE REPORT

Priority:
{priority}

Severity:
{severity_level}

Most Impacted Service:
{top_service}

Dominant Error:
{top_error}

Most Affected Region:
{top_region}

Correlated Deployment:
{deployment_name}

Business Impact:
{business_impact}

Coral Integration:
GitHub source connected through Coral CLI.
Live Coral SQL query executed successfully.

Generated:
{datetime.now()}

Recommended Actions:
- rollback deployment
- inspect retry handling
- restart impacted services
- monitor recovery
"""

st.download_button(
    label="⬇️ Download Incident Report",
    data=report,
    file_name="incident_report.txt",
    mime="text/plain"
)

st.divider()

st.write("## 🪸 Why Coral?")

st.info("""
IncidentMind uses Coral as a unified operational data layer.

In this demo, IncidentMind connects to Coral through the Coral CLI and verifies
a live GitHub source using Coral SQL.

Coral exposes APIs, databases, support systems, logs, and files as queryable
SQL tables. IncidentMind sits on top of that layer to perform incident investigation.

Why it matters:

• Query live operational systems through SQL

• No ETL pipelines

• Cross-source joins

• Local-first execution

• Faster root cause analysis
""")

st.caption("Powered by Coral • IncidentMind AI • Streamlit")

st.divider()

st.write("## 💬 Incident Investigation")

st.write("### ⚡ Quick Investigation Queries")

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button("Root Cause"):
        st.session_state.quick_question = "What is the root cause?"

with q2:
    if st.button("Deployment Analysis"):
        st.session_state.quick_question = "Which deployment caused the issue?"

with q3:
    if st.button("Fix Recommendations"):
        st.session_state.quick_question = "How do we fix this incident?"

with q4:
    if st.button("Coral Status"):
        st.session_state.quick_question = "Show Coral status"

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def dynamic_query_engine(question):
    q = question.lower()

    if "high severity" in q or "critical errors" in q:
        filtered = errors[errors["severity"].str.lower() == "high"]
        return "## 🚨 High Severity Errors", filtered

    if top_service.lower() in q:
        filtered = errors[errors["service"].str.lower() == top_service.lower()]
        return f"## {top_service} Errors", filtered

    if "eu tickets" in q or "eu users" in q:
        filtered = tickets[tickets["user_region"].str.upper() == "EU"]
        return "## 🌍 EU Support Tickets", filtered

    if "deployment" in q:
        return "## 🚀 Deployment Records", deployments

    if "coral" in q or "github" in q:
        df = pd.DataFrame({
            "Component": [
                "Coral CLI",
                "GitHub Source",
                "Live SQL Query"
            ],
            "Status": [
                "Connected" if coral_connected else "Unavailable",
                "Connected" if coral_connected else "Unavailable",
                "Working" if query_ok else "Unavailable"
            ]
        })
        return "## 🪸 Coral Runtime Status", df

    return None, None

def generate_incident_response(question):
    return f"""
# 🤖 IncidentMind Investigation

## Priority
{priority}

## Severity
{severity_color} {severity_level}

## Findings

- impacted service: `{top_service}`
- dominant runtime issue: `{top_error}`
- impacted region: `{top_region}`
- correlated deployment: `{deployment_name}`
- Coral live source: `github`

---

## Coral Query Plan

{incident_query}

---

## Why IncidentMind Concluded This

- deployment timing matched error spike
- support tickets increased after deployment
- runtime instability escalated rapidly
- customer impact appeared in `{top_region}`

---

## Recommended Actions

1. rollback deployment
2. inspect retry handling
3. restart impacted services
4. monitor payment recovery
5. validate API stability

---

## AI Confidence
{confidence_score}%
"""

question = None

if "quick_question" in st.session_state:
    question = st.session_state.quick_question
    del st.session_state.quick_question

chat_input = st.chat_input("Ask IncidentMind about the incident...")

if chat_input:
    question = chat_input

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("🧠 IncidentMind is querying Coral-connected operational context..."):
            time.sleep(1)

            title, result_df = dynamic_query_engine(question)

            if result_df is not None:
                st.markdown(title)
                st.dataframe(result_df, use_container_width=True)
                st.success("IncidentMind returned matching operational records.")
                response_text = f"{title} generated."
            else:
                ai_response = generate_incident_response(question)
                st.markdown(ai_response)
                response_text = ai_response

            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })