# Pipeline Health Checker

**Automated risk detection for GTM teams** - A demonstration of how to build scalable processes that create leverage during hypergrowth.

## Problem Statement

Leadership needs a way to quickly understand pipeline health - identifying stalled deals, deals that need intervention, deals with poor salesforce hygiene, and tracking overall velocity.
This is a repeatable process that should be automated, so leadership can quickly see what's going well, what's going poorly, and take action.

## Solution

An automated Pipeline Health Checker that:
1. **Analyzes** every open opportunity against stage-specific benchmarks
2. **Scores** risk on a standardized 0-10 scale based on 5 key signals
3. **Flags** deals requiring immediate intervention
4. **Visualizes** results in an interactive HTML dashboard with expandable deal details


## How It Works

### Risk Scoring Methodology

Each deal is scored on a **standardized 0-2 point scale** across 5 dimensions:

| Signal | Scoring Logic | Points |
|--------|---------------|--------|
| **Time in Stage** | Within benchmark (0) / 1-2x over (1) / 2x+ over (2) | 0-2 pts |
| **Activity Gap** | ≤7 days (0) / 8-14 days (1) / 15+ days (2) | 0-2 pts |
| **Missing Fields** | None (0) / 1 field (1) / 2+ fields (2) | 0-2 pts |
| **Close Date Risk** | 30+ days (0) / 7-29 days (1) / <7 or past due (2) | 0-2 pts |
| **Competitor Threat** | None (0) / OpenAI or Google (2) | 0 or 2 pts |

**Overall Risk Score** = Sum of signals (max 10 points)

- **0-3** = Healthy (green)
- **4-6** = At Risk (yellow)
- **7-10** = High Risk (red)

### Stage-Specific Requirements

The system checks for missing critical fields based on deal stage:

- **Solution Mapping+**: Must have Economic Buyer identified
- **Technical Evaluation+**: Must have Economic Buyer + Technical Champion
- **EB Sign Off+**: Must have Economic Buyer + Technical Champion + Security Review "Complete"
- **Contract Negotiation**: Must have Economic Buyer + Technical Champion + Security Review "Complete"

### Stage Benchmarks

Each stage has expected duration ranges:

- **Qualification**: 7-14 days
- **Solution Mapping**: 14-21 days
- **Technical Evaluation**: 21-35 days
- **EB Sign Off**: 10-21 days
- **Contract Negotiation**: 14-28 days


## Quick Start

### Run the Analysis

```bash
# Run complete SQL analysis
duckdb :memory: < sql/final_analysis_full.sql
```

Output:
- Pipeline overview stats
- Risk breakdown by level
- Top 10 at-risk deals
- Exports `data/dashboard_data.json`

### Generate Dashboard

```bash
# Setup (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Generate interactive HTML dashboard
python scripts/generate_html_dashboard.py
```

Then open `pipeline_dashboard.html` in your browser to view the interactive dashboard.

This can be recreated with any salesforce_opportunity dataset and customized benchmarks

