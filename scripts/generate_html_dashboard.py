#!/usr/bin/env python3
"""
Pipeline health risk analysis 
"""

import pandas as pd
import json
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Stoplight color palette
COLORS = {
    'primary': '#2c5aa0',
    'background': '#f6f8fa',
    'tile_bg': '#ffffff',
    'text': '#3e3f40',
    'tile_title': '#3a4245',
    'border': '#e8eaed',
    'healthy': '#28a745',    # Green
    'at_risk': '#ffc107',    # Yellow/Amber
    'high_risk': '#dc3545',  # Red
}

# Load data
with open(PROJECT_ROOT / 'data' / 'dashboard_data.json', 'r') as f:
    alerts = json.load(f)

df = pd.read_csv(PROJECT_ROOT / 'data' / 'salesforce_opportunities.csv')
df_open = df[~df['StageName'].isin(['Closed Won', 'Closed Lost'])].copy()

# Add risk data
alert_ids = {alert['id']: alert for alert in alerts}
df_open['risk_level'] = df_open['Id'].apply(
    lambda x: alert_ids[x]['risk_level'] if x in alert_ids else 'healthy'
)
df_open['risk_score'] = df_open['Id'].apply(
    lambda x: alert_ids[x]['risk_score'] if x in alert_ids else 0
)

# Calculate metrics
total_deals = len(df_open)
total_pipeline = df_open['Amount'].sum()
risk_counts = df_open['risk_level'].value_counts()
risk_values = df_open.groupby('risk_level')['Amount'].sum()

at_risk_value = risk_values.get('at_risk', 0) + risk_values.get('high_risk', 0)
at_risk_count = risk_counts.get('at_risk', 0) + risk_counts.get('high_risk', 0)
at_risk_pct = (at_risk_value / total_pipeline * 100)
avg_risk_at_risk = df_open[df_open['risk_score'] > 0]['risk_score'].mean()

# Sort alerts and enrich with risk factors and actions
top_alerts = sorted(alerts, key=lambda x: (-x['risk_score'], -x['amount']))[:10]

# Function to generate risk factors and actions
def get_risk_factors(alert):
    factors = []
    if alert['days_in_stage'] > 35:
        factors.append(f"Stuck in stage for {alert['days_in_stage']} days")
    if alert['days_since_activity'] > 10:
        factors.append(f"No activity in {alert['days_since_activity']} days")
    if alert['days_to_close'] < 0:
        factors.append(f"Close date passed {abs(alert['days_to_close'])} days ago")
    elif alert['days_to_close'] <= 14:
        factors.append(f"Closing in {alert['days_to_close']} days")
    if alert.get('missing_field_list'):
        factors.append(f"Missing: {alert['missing_field_list']}")
    if alert.get('competitor') and alert['competitor'] != 'None identified':
        factors.append(f"Competing with {alert['competitor']}")
    return factors

def get_recommended_actions(alert):
    actions = []

    # Activity-based actions
    if alert['days_since_activity'] > 15:
        actions.append("Re-engage immediately - deal may be stalled")
    elif alert['days_since_activity'] > 10:
        actions.append("Schedule follow-up call this week")

    # Stage velocity actions
    if alert['days_in_stage'] > 50:
        actions.append("Review deal progression with manager")

    # Missing fields actions
    if alert.get('missing_field_list'):
        fields = alert['missing_field_list']
        if 'economic_buyer' in fields:
            actions.append("Identify and engage economic buyer")
        if 'technical_champion' in fields:
            actions.append("Secure technical champion sponsor")
        if 'security_review' in fields:
            actions.append("Initiate security review process")

    # Close date actions
    if alert['days_to_close'] < 0:
        actions.append("Update close date and verify deal status")
    elif alert['days_to_close'] <= 14:
        actions.append("Verify all requirements met for close")

    # Competitor actions
    if alert.get('competitor') and alert['competitor'] not in ['None identified', None]:
        actions.append(f"Develop competitive strategy vs {alert['competitor']}")

    # Default action if nothing specific
    if not actions:
        actions.append("Review deal status with account executive")

    return actions[:3]  # Limit to top 3 actions

# Enrich alerts
for alert in top_alerts:
    alert['risk_factors'] = get_risk_factors(alert)
    alert['recommended_actions'] = get_recommended_actions(alert)

# Rep performance
rep_risk = df_open.groupby('Owner.Name')['risk_score'].mean().sort_values(ascending=False).head(8)

# Generate HTML
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pipeline Health Checker - Executive Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: {COLORS['background']};
            color: {COLORS['text']};
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            background: {COLORS['background']};
            padding: 20px 0;
            margin-bottom: 30px;
        }}

        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['tile_title']};
            margin-bottom: 5px;
        }}

        .header p {{
            font-size: 13px;
            color: {COLORS['text']};
            font-style: italic;
        }}

        /* Tiles */
        .tile {{
            background: {COLORS['tile_bg']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            transition: box-shadow 0.2s;
        }}

        .tile:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}

        .tile-title {{
            font-size: 13px;
            font-weight: 600;
            color: {COLORS['tile_title']};
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .tile-subtitle {{
            font-size: 11px;
            color: {COLORS['text']};
            opacity: 0.7;
            margin-bottom: 16px;
        }}

        /* Grid Layout */
        .grid {{
            display: grid;
            gap: 20px;
            margin-bottom: 20px;
        }}

        .grid-3 {{
            grid-template-columns: repeat(3, 1fr);
        }}

        .grid-2 {{
            grid-template-columns: repeat(2, 1fr);
        }}

        /* Metric Cards */
        .metric {{
            text-align: center;
            padding: 20px;
        }}

        .metric-value {{
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .metric-label {{
            font-size: 14px;
            font-weight: 500;
            color: {COLORS['text']};
            margin-bottom: 8px;
        }}

        .metric-detail {{
            font-size: 12px;
            color: {COLORS['text']};
            opacity: 0.7;
        }}

        .metric-primary {{ color: {COLORS['primary']}; }}
        .metric-danger {{ color: {COLORS['high_risk']}; }}
        .metric-warning {{ color: {COLORS['at_risk']}; }}

        /* Table */
        table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }}

        thead {{
            background: {COLORS['background']};
        }}

        th {{
            text-align: left;
            padding: 12px 16px;
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['tile_title']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border-bottom: 2px solid {COLORS['border']};
        }}

        td {{
            padding: 14px 16px;
            font-size: 13px;
            border-bottom: 1px solid {COLORS['border']};
        }}

        tbody tr:hover {{
            background: {COLORS['background']};
        }}

        tbody tr:nth-child(even) {{
            background: #fafbfc;
        }}

        .expandable-row {{
            cursor: pointer;
            transition: background 0.2s;
        }}

        .expandable-row:hover {{
            background: #e8f4fd !important;
        }}

        .detail-row {{
            display: none;
            background: #f8f9fa !important;
        }}

        .detail-row.show {{
            display: table-row;
        }}

        .detail-content {{
            padding: 20px;
            border-left: 3px solid {COLORS['primary']};
        }}

        .detail-section {{
            margin-bottom: 16px;
        }}

        .detail-section-title {{
            font-size: 12px;
            font-weight: 600;
            color: {COLORS['tile_title']};
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .detail-list {{
            list-style: none;
            padding-left: 0;
        }}

        .detail-list li {{
            padding: 6px 0;
            font-size: 13px;
            color: {COLORS['text']};
            line-height: 1.5;
        }}

        .risk-factor {{
            color: {COLORS['high_risk']};
        }}

        .action-item {{
            color: {COLORS['primary']};
            font-weight: 500;
        }}

        .expand-icon {{
            display: inline-block;
            margin-right: 8px;
            transition: transform 0.2s;
            font-size: 10px;
            color: {COLORS['text']};
            opacity: 0.5;
        }}

        .expandable-row.expanded .expand-icon {{
            transform: rotate(90deg);
        }}

        .risk-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            color: white;
            text-align: center;
            min-width: 40px;
        }}

        .risk-high {{ background: {COLORS['high_risk']}; }}
        .risk-medium {{ background: {COLORS['at_risk']}; }}
        .risk-low {{ background: {COLORS['healthy']}; }}

        /* Chart Containers */
        .chart-container {{
            padding: 20px;
            min-height: 300px;
        }}

        .bar {{
            height: 32px;
            margin: 8px 0;
            background: #e9ecef;
            border-radius: 4px;
            position: relative;
            overflow: hidden;
        }}

        .bar-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            padding: 0 12px;
            color: white;
            font-weight: 600;
            font-size: 13px;
            border-radius: 4px;
            transition: width 0.5s ease;
        }}

        .bar-label {{
            display: flex;
            justify-content: space-between;
            font-size: 13px;
            margin-bottom: 4px;
            color: {COLORS['text']};
        }}

        .bar-label-name {{
            font-weight: 500;
        }}

        .bar-label-value {{
            font-weight: 600;
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 30px 0;
            font-size: 12px;
            color: {COLORS['text']};
            opacity: 0.6;
        }}

        @media print {{
            .footer {{
                display: none;
            }}
        }}

        /* Donut Chart */
        .donut-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            padding: 20px;
        }}

        .donut-chart {{
            position: relative;
            width: 220px;
            height: 220px;
            margin: 20px auto;
        }}

        .donut-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        }}

        .donut-center-value {{
            font-size: 36px;
            font-weight: 700;
            color: {COLORS['text']};
        }}

        .donut-center-label {{
            font-size: 13px;
            color: {COLORS['text']};
            opacity: 0.7;
        }}

        .legend {{
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: 16px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
        }}

        .legend-color {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
        }}

        @media (max-width: 768px) {{
            .grid-3, .grid-2 {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div>
                <h1>Pipeline Health Checker</h1>
                <p>Automated Risk Detection Analysis • Powered by SQL + DuckDB</p>
            </div>
        </div>

        <!-- Key Metrics -->
        <div class="grid grid-3">
            <div class="tile metric">
                <div class="metric-value metric-primary">${total_pipeline/1e6:.1f}M</div>
                <div class="metric-label">Total Pipeline</div>
                <div class="metric-detail">{total_deals} Open Deals</div>
            </div>

            <div class="tile metric">
                <div class="metric-value metric-danger">${at_risk_value/1e6:.1f}M</div>
                <div class="metric-label">Pipeline at Risk</div>
                <div class="metric-detail">{at_risk_count} Deals • {at_risk_pct:.0f}% of Pipeline</div>
            </div>

            <div class="tile metric">
                <div class="metric-value metric-warning">{avg_risk_at_risk:.1f}</div>
                <div class="metric-label">Avg Risk Score (At-Risk Deals)</div>
                <div class="metric-detail">Overall Avg: {df_open['risk_score'].mean():.1f} / 10</div>
            </div>
        </div>

        <!-- Charts Row -->
        <div class="grid grid-3">
            <!-- Deal Distribution Donut -->
            <div class="tile">
                <div class="tile-title">Deal Distribution</div>
                <div class="tile-subtitle">By Risk Level</div>
                <div class="donut-container">
                    <svg class="donut-chart" viewBox="0 0 200 200">
                        <circle cx="100" cy="100" r="80" fill="none"
                                stroke="{COLORS['healthy']}" stroke-width="40"
                                stroke-dasharray="{risk_counts.get('healthy', 0)/total_deals*502.4} 502.4"
                                transform="rotate(-90 100 100)"/>
                        <circle cx="100" cy="100" r="80" fill="none"
                                stroke="{COLORS['at_risk']}" stroke-width="40"
                                stroke-dasharray="{risk_counts.get('at_risk', 0)/total_deals*502.4} 502.4"
                                stroke-dashoffset="{-risk_counts.get('healthy', 0)/total_deals*502.4}"
                                transform="rotate(-90 100 100)"/>
                        <circle cx="100" cy="100" r="80" fill="none"
                                stroke="{COLORS['high_risk']}" stroke-width="40"
                                stroke-dasharray="{risk_counts.get('high_risk', 0)/total_deals*502.4} 502.4"
                                stroke-dashoffset="{-(risk_counts.get('healthy', 0) + risk_counts.get('at_risk', 0))/total_deals*502.4}"
                                transform="rotate(-90 100 100)"/>
                    </svg>
                    <div class="donut-center">
                        <div class="donut-center-value">{total_deals}</div>
                        <div class="donut-center-label">Deals</div>
                    </div>
                    <div class="legend">
                        <div class="legend-item">
                            <div class="legend-color" style="background: {COLORS['healthy']}"></div>
                            <span>Healthy: {risk_counts.get('healthy', 0)} ({risk_counts.get('healthy', 0)/total_deals*100:.0f}%)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: {COLORS['at_risk']}"></div>
                            <span>At Risk: {risk_counts.get('at_risk', 0)} ({risk_counts.get('at_risk', 0)/total_deals*100:.0f}%)</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color" style="background: {COLORS['high_risk']}"></div>
                            <span>High Risk: {risk_counts.get('high_risk', 0)} ({risk_counts.get('high_risk', 0)/total_deals*100:.0f}%)</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Pipeline Value -->
            <div class="tile">
                <div class="tile-title">Pipeline Value</div>
                <div class="tile-subtitle">By Risk Level ($M)</div>
                <div class="chart-container">
"""

# Add pipeline value bars
for risk_level in ['high_risk', 'at_risk', 'healthy']:
    value = risk_values.get(risk_level, 0) / 1e6
    max_value = risk_values.max() / 1e6
    percentage = (value / max_value * 100) if max_value > 0 else 0

    html += f"""
                    <div style="margin-bottom: 20px;">
                        <div class="bar-label">
                            <span class="bar-label-name">{risk_level.replace('_', ' ').title()}</span>
                            <span class="bar-label-value">${value:.1f}M</span>
                        </div>
                        <div class="bar">
                            <div class="bar-fill" style="width: {percentage}%; background: {COLORS[risk_level]}">
                            </div>
                        </div>
                    </div>
"""

html += """
                </div>
            </div>

            <!-- Rep Performance -->
            <div class="tile">
                <div class="tile-title">Rep Performance</div>
                <div class="tile-subtitle">Average Risk Score</div>
                <div class="chart-container">
"""

# Add rep performance bars
max_score = 10
for owner, score in rep_risk.items():
    percentage = (score / max_score * 100)
    if score >= 5:
        color = COLORS['high_risk']
    elif score >= 3.5:
        color = COLORS['at_risk']
    else:
        color = COLORS['healthy']

    html += f"""
                    <div style="margin-bottom: 16px;">
                        <div class="bar-label">
                            <span class="bar-label-name">{owner}</span>
                            <span class="bar-label-value">{score:.1f}</span>
                        </div>
                        <div class="bar">
                            <div class="bar-fill" style="width: {percentage}%; background: {color}">
                            </div>
                        </div>
                    </div>
"""

html += """
                </div>
            </div>
        </div>

        <!-- At-Risk Deals Table -->
        <div class="tile">
            <div class="tile-title">Top At-Risk Deals Requiring Immediate Attention</div>
            <div class="tile-subtitle">"""

html += f"{len(alerts)} deals flagged"

html += """</div>
            <table>
                <thead>
                    <tr>
                        <th>Account</th>
                        <th>Stage</th>
                        <th>Amount</th>
                        <th>Risk</th>
                        <th>In Stage</th>
                        <th>Last Activity</th>
                        <th>Owner</th>
                    </tr>
                </thead>
                <tbody>
"""

# Add table rows with expandable details
for idx, alert in enumerate(top_alerts):
    risk_class = 'risk-high' if alert['risk_level'] == 'high_risk' else 'risk-medium'

    # Main row
    html += f"""
                    <tr class="expandable-row" onclick="toggleRow({idx})">
                        <td><span class="expand-icon">▶</span><strong>{alert['account_name']}</strong></td>
                        <td>{alert['stage_name']}</td>
                        <td>${alert['amount']/1000:.0f}K</td>
                        <td><span class="risk-badge {risk_class}">{alert['risk_score']:.1f}</span></td>
                        <td>{alert['days_in_stage']}d</td>
                        <td>{alert['days_since_activity']}d ago</td>
                        <td>{alert['owner_name']}</td>
                    </tr>
"""

    # Detail row
    html += f"""
                    <tr class="detail-row" id="detail-{idx}">
                        <td colspan="7">
                            <div class="detail-content">
                                <div class="detail-section">
                                    <div class="detail-section-title">Risk Factors</div>
                                    <ul class="detail-list">
"""

    if alert['risk_factors']:
        for factor in alert['risk_factors']:
            html += f"""
                                        <li class="risk-factor">{factor}</li>
"""
    else:
        html += """
                                        <li class="risk-factor">Standard risk monitoring</li>
"""

    html += """
                                    </ul>
                                </div>
                                <div class="detail-section">
                                    <div class="detail-section-title">Recommended Actions</div>
                                    <ul class="detail-list">
"""

    for action in alert['recommended_actions']:
        html += f"""
                                        <li class="action-item">• {action}</li>
"""

    html += """
                                    </ul>
                                </div>
                            </div>
                        </td>
                    </tr>
"""

html += """
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div class="footer">
            SQL-Based Risk Analysis • Data as of Oct 30, 2025
        </div>
    </div>

    <script>
        // Toggle expandable row details
        function toggleRow(index) {
            const detailRow = document.getElementById('detail-' + index);
            const expandRow = event.currentTarget;

            if (detailRow.classList.contains('show')) {
                detailRow.classList.remove('show');
                expandRow.classList.remove('expanded');
            } else {
                detailRow.classList.add('show');
                expandRow.classList.add('expanded');
            }
        }

        // Add smooth scroll animation on load
        document.addEventListener('DOMContentLoaded', function() {
            const bars = document.querySelectorAll('.bar-fill');
            bars.forEach((bar, index) => {
                setTimeout(() => {
                    bar.style.transition = 'width 0.8s ease-out';
                }, index * 100);
            });
        });
    </script>
</body>
</html>
"""

# Save HTML file to project root
output_file = PROJECT_ROOT / 'pipeline_dashboard.html'
with open(output_file, 'w') as f:
    f.write(html)

print(f"\n✅ Interactive HTML dashboard saved to: {output_file}")
print(f"   Open in browser to view interactive dashboard")
print(f"   Looker-style design with responsive layout")
print(f"\n   Ready to share via email or presentation!")
