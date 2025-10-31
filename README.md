# Pipeline Health Checker

**Automated risk detection for GTM teams** - A demonstration of how Claude Code creates leverage by building scalable processes.

## Problem Statement

Leadership needs a way to quickly understand pipeline health - identifying stalled deals, deals that need intervention, deals with poor salesforce hygiene, and tracking overall velocity.
This is a repeatable process that should be automated, so leadership can quickly see what's going well, what's going poorly, and take action.

## Solution

An automated Pipeline Health Checker that:
1. **Analyzes** every open opportunity against stage-specific benchmarks
2. **Scores** risk on a 1-10 scale based on multiple signals
3. **Alerts** managers to deals requiring intervention
4. **Exports** structured data for Slack/email integration


## Results

From a fake Salesforce opportunity dataset of 45 open deals ($12.9M pipeline):

```
⚠️  RISK BREAKDOWN

┌────────────┬────────────┬─────────────┬──────────────┬──────────┐
│ risk_level │ deal_count │ total_value │ pct_pipeline │ avg_risk │
├────────────┼────────────┼─────────────┼──────────────┼──────────┤
│ high_risk  │ 11         │ $3.2M       │ 24.3%        │ 8.8/10   │
│ at_risk    │ 4          │ $1.3M       │ 10.0%        │ 5.0/10   │
│ healthy    │ 30         │ $8.5M       │ 65.8%        │ 1.3/10   │
└────────────┴────────────┴─────────────┴──────────────┴──────────┘
```

**Key Insight**: 15 deals ($4.5M or 34% of pipeline) need immediate attention.

## How It Works

### Risk Scoring Methodology

Each deal is scored across 6 dimensions:

| Signal | Scoring Logic | Weight |
|--------|---------------|--------|
| **Time in Stage** | Days vs. benchmark (e.g., Technical Evaluation: 21-35 days) | 0-10 pts |
| **Activity Gap** | Days since last activity (5d = healthy, 15d+ = stalled) | 0-9 pts |
| **Missing Fields** | Stage-specific requirements (Economic Buyer, Security Review) | 3 pts each |
| **Close Date Risk** | Past due (+5), Closing within 14 days (+2) | 0-5 pts |
| **Next Steps Quality** | Blank (+3), Vague (+2), Specific (0) | 0-3 pts |
| **Competitor Threat** | Active competitor identified | 1-2 pts |

**Overall Risk Score** = Sum of signals (capped at 10)

- **0-3.5** = Healthy (green)
- **3.5-7.0** = At Risk (yellow)
- **7.0-10.0** = High Risk (red)

### Stage-Specific Requirements

- **Solution Mapping+**: Must have Economic Buyer identified
- **Technical Evaluation+**: Must have Technical Champion identified
- **EB Sign Off+**: Security Review must be "Complete"
- **All Stages**: Must have specific Next Steps defined

## Files

```
pipeline-risk-alerting/
├── generate_salesforce_data.py  # Generates synthetic test data
├── salesforce_opportunities.csv # 50 deals (45 open, 5 closed)
│
├── analysis.sql                 # Complete analysis (run with DuckDB)
├── schema.sql                   # Database schema
├── setup.sql                    # Reference data (benchmarks, requirements)
├── risk_analysis.sql            # Core risk scoring query
├── dashboard_queries.sql        # Manager-level insights
│
├── run_analysis.py              # Python orchestrator (optional, requires venv)
├── requirements.txt             # Python dependencies
│
├── deal_alerts.json             # Generated alerts (15 deals)
└── README.md                    # This file
```

## Quick Start

### Option 1: DuckDB CLI (Fastest)

```bash
# Run complete analysis
duckdb :memory: < analysis.sql
```

Output:
- Pipeline overview
- Risk breakdown
- Top 10 at-risk deals
- Exports `deal_alerts.json`

### Option 2: Python (Pretty Output)

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install duckdb rich pandas

# Run
python run_analysis.py
```

## Sample Outputs

### High-Risk Deal Example

```json
{
  "id": "006fdb1mF7Z4lCDrK9",
  "name": "InsureTech - Enterprise AI",
  "account_name": "InsureTech",
  "owner_name": "Christopher Lee",
  "stage_name": "Technical Evaluation",
  "amount": 585000.0,
  "risk_score": 10.0,
  "risk_level": "high_risk",
  "days_in_stage": 83,
  "days_since_activity": 21,
  "days_to_close": -7,
  "next_step": "Follow up - no response to last 2 emails",
  "competitor": "Google Vertex AI"
}
```

**Why High Risk?**
- Stuck in stage for 83 days (benchmark: 35 days max) = +10 pts
- No activity in 21 days = +9 pts
- Close date passed 7 days ago = +5 pts
- Vague next steps = +2 pts
- Active competitor = +2 pts
- **Total: Capped at 10.0**

**Recommended Actions:**
1. [URGENT] Re-engage immediately - no activity in 21 days
2. Develop competitive strategy against Google Vertex AI
3. Update close date and verify deal status
4. Review deal progression - stuck in Technical Evaluation

## Business Impact

### Time Savings
- **Before**: Manager manually reviews 50 deals = 2-3 hours/week
- **After**: Automated analysis + review top 15 alerts = 30 minutes/week
- **Savings**: 2.5 hours/week per manager

### Revenue Protection
- Identifies $4.5M (34%) of pipeline at risk
- Enables proactive intervention before deals are lost
- Quantifies risk across team (rep performance view)

### Scalability
This same system works for:
- 50 deals (demo) → seconds to run
- 5,000 deals (enterprise) → still seconds (DuckDB optimized for analytics)
- Integration with Salesforce via SOQL → same SQL logic
- Daily automated runs → Slack alerts for high-risk deals

## Production Roadmap

To deploy this in a real GTM organization:

1. **Data Integration**
   - Connect to Salesforce via API (not CSV export)
   - Use dbt for SQL transformations
   - Store in Snowflake/BigQuery

2. **Automation**
   - Daily cron job to run analysis
   - Slack alerts for high-risk deals
   - Email digest for managers

3. **Dashboards**
   - Tableau/Looker/Mode Analytics
   - SQL queries copy-paste ready
   - Interactive filters (rep, stage, risk level)

4. **Customization**
   - Adjust benchmarks by segment/region
   - Custom scoring weights
   - Additional risk signals (budget approval, legal review)

## Why This Demonstrates GTM Leverage

This project shows the principle of **"Build once, scale infinitely"**:

1. **Replicable Process**: Same analysis works for any sales team
2. **Force Multiplication**: One engineer → saves 10 managers 2.5 hrs/week each
3. **Data-Driven Culture**: Shifts from "gut feel" to quantified risk
4. **Scalable Infrastructure**: SQL-based = works in any BI tool
5. **Measurable Impact**: Track time saved, revenue protected, win rate improvement

Most importantly: **This took ~3 hours to build, demonstrates years of GTM ops experience**.

## Contact

Built by Kelsey for Anthropic Head of GTM Strategy application.

**Approach**: Use Claude Code to build scalable processes that create leverage for hypergrowth teams.
