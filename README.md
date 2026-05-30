# 🚨 IncidentMind

AI-powered incident investigation platform built with Coral.

## Overview

IncidentMind helps engineering teams rapidly identify, investigate, and remediate production incidents by correlating:

- Deployments
- Runtime Error Logs
- Support Tickets
- Monitoring Signals

Using Coral as a unified operational data layer, IncidentMind performs cross-source analysis without requiring ETL pipelines or data warehouses.

---

## Problem

When production incidents occur, engineers often need to manually investigate multiple systems:

- Deployment history
- Application logs
- Customer support tickets
- Monitoring dashboards

This process is slow and delays incident resolution.

---

## Solution

IncidentMind uses Coral to unify operational datasets and provide AI-assisted incident investigation.

The platform:

- Detects anomalies
- Identifies impacted services
- Correlates deployments with failures
- Prioritizes incidents
- Generates remediation recommendations
- Produces executive reports

---

## Features

### 🤖 AI Incident Investigation
- Root cause analysis
- Deployment correlation
- Incident severity classification
- Confidence scoring

### 🚨 Anomaly Detection
- Suspicious service detection
- Runtime error spike identification
- Regional impact analysis

### 📊 Operational Dashboard
- Live incident feed
- Incident timeline
- Risk scoring
- Executive insights

### 🪸 Coral Integration
- Unified SQL-style access
- Cross-source investigation
- No ETL pipelines
- Local-first architecture

### 📄 Reporting
- Executive incident reports
- Downloadable summaries

---

## Architecture

Deployments + Runtime Errors + Support Tickets

↓

Coral Query Layer

↓

IncidentMind AI Engine

↓

Root Cause Analysis

↓

Remediation Recommendations

↓

Executive Reporting

---

## Example Investigation Workflow

1. Deployment is released.
2. Runtime errors begin increasing.
3. Customer tickets spike.
4. Coral correlates datasets.
5. IncidentMind identifies probable root cause.
6. Engineers receive remediation guidance.

---

## Tech Stack

- Python
- Streamlit
- Pandas
- Coral
- SQL-style Data Investigation

---

## Why Coral?

Coral allows operational systems to be queried as connected tables.

Instead of building ETL pipelines and maintaining data warehouses, IncidentMind can investigate incidents across multiple sources through a unified query layer.

Benefits:

- No ETL
- Cross-source joins
- Local-first
- Faster investigations
- Reduced engineering complexity

---

## Future Improvements

- Live production integrations
- Real-time alert streaming
- LLM-powered reasoning
- Automated remediation workflows
- Multi-agent incident response

---

## Team

Built for the Coral Hackathon.
