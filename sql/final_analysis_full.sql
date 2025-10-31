-- Pipeline Health Checker - Complete Analysis
-- CLI command = duckdb :memory: < analysis.sql

.mode box
.headers on

-- Setup reference tables
CREATE TABLE stage_benchmarks (
    stage_name VARCHAR PRIMARY KEY,
    min_days INTEGER,
    max_days INTEGER,
    sequence_order INTEGER
);

INSERT INTO stage_benchmarks VALUES
    ('Qualification', 7, 14, 1),
    ('Solution Mapping', 14, 21, 2),
    ('Technical Evaluation', 21, 35, 3),
    ('EB Sign Off', 10, 21, 4),
    ('Contract Negotiation', 14, 28, 5);

CREATE TABLE stage_requirements (
    stage_name VARCHAR,
    required_field VARCHAR,
    required_value VARCHAR,
    severity VARCHAR,
    PRIMARY KEY (stage_name, required_field)
);

INSERT INTO stage_requirements VALUES
    ('Solution Mapping', 'economic_buyer', NULL, 'critical'),
    ('Technical Evaluation', 'economic_buyer', NULL, 'critical'),
    ('EB Sign Off', 'economic_buyer', NULL, 'critical'),
    ('Contract Negotiation', 'economic_buyer', NULL, 'critical'),
    ('Technical Evaluation', 'technical_champion', NULL, 'critical'),
    ('EB Sign Off', 'technical_champion', NULL, 'critical'),
    ('Contract Negotiation', 'technical_champion', NULL, 'critical'),
    ('EB Sign Off', 'security_review_status', 'Complete', 'critical'),
    ('Contract Negotiation', 'security_review_status', 'Complete', 'critical'),
    ('EB Sign Off', 'next_step', NULL, 'critical'),
    ('Contract Negotiation', 'next_step', NULL, 'critical');

-- Main risk analysis view
.print ''
.print '═══════════════════════════════════════════════════════════════════════════════'
.print '  PIPELINE HEALTH CHECKER - Analysis Results'
.print '═══════════════════════════════════════════════════════════════════════════════'
.print ''

CREATE OR REPLACE VIEW risk_analysis AS
WITH

opportunities AS (
    SELECT
        "Id" as id,
        "Name" as name,
        "Account.Name" as account_name,
        "Owner.Name" as owner_name,
        CAST("Amount" AS DECIMAL(12,2)) as amount,
        "StageName" as stage_name,
        CAST("Probability" AS INTEGER) as probability,
        CAST("CloseDate" AS DATE) as close_date,
        CAST("LastActivityDate" AS DATE) as last_activity_date,
        CAST("LastStageChangeDate" AS DATE) as last_stage_change_date,
        "NextStep" as next_step,
        "Economic_Buyer__c" as economic_buyer,
        "Technical_Champion__c" as technical_champion,
        "Security_Review_Status__c" as security_review_status,
        "Competitor__c" as competitor
    FROM read_csv_auto('data/salesforce_opportunities.csv')
    WHERE "StageName" NOT IN ('Closed Won', 'Closed Lost')
),

current_date AS (
    SELECT DATE '2025-10-30' as analysis_date
),

time_in_stage AS (
    SELECT
        o.id,
        o.stage_name,
        DATE_DIFF('day', o.last_stage_change_date, c.analysis_date) AS days_in_stage,
        b.max_days AS benchmark_max,
        CASE
            WHEN DATE_DIFF('day', o.last_stage_change_date, c.analysis_date) <= b.max_days THEN 0
            WHEN DATE_DIFF('day', o.last_stage_change_date, c.analysis_date) <= b.max_days * 2.0 THEN 1
            ELSE 2
        END AS time_in_stage_score
    FROM opportunities o
    CROSS JOIN current_date c
    LEFT JOIN stage_benchmarks b ON o.stage_name = b.stage_name
),

activity_gaps AS (
    SELECT
        o.id,
        DATE_DIFF('day', o.last_activity_date, c.analysis_date) AS days_since_activity,
        CASE
            WHEN DATE_DIFF('day', o.last_activity_date, c.analysis_date) <= 7 THEN 0
            WHEN DATE_DIFF('day', o.last_activity_date, c.analysis_date) <= 14 THEN 1
            ELSE 2
        END AS activity_gap_score
    FROM opportunities o
    CROSS JOIN current_date c
),

missing_fields AS (
    SELECT
        o.id,
        CASE
            WHEN COUNT(*) = 0 THEN 0
            WHEN COUNT(*) = 1 THEN 1
            ELSE 2
        END AS missing_fields_score,
        STRING_AGG(sr.required_field, ', ') AS missing_field_list
    FROM opportunities o
    INNER JOIN stage_requirements sr ON o.stage_name = sr.stage_name
    WHERE sr.severity = 'critical'
      AND (
          (sr.required_field = 'economic_buyer' AND (o.economic_buyer IS NULL OR o.economic_buyer = ''))
          OR (sr.required_field = 'technical_champion' AND (o.technical_champion IS NULL OR o.technical_champion = ''))
          OR (sr.required_field = 'security_review_status' AND sr.required_value = 'Complete' AND o.security_review_status != 'Complete')
          OR (sr.required_field = 'next_step' AND (o.next_step IS NULL OR o.next_step = ''))
      )
    GROUP BY o.id
),

close_date_risk AS (
    SELECT
        o.id,
        DATE_DIFF('day', c.analysis_date, o.close_date) AS days_to_close,
        CASE
            WHEN DATE_DIFF('day', c.analysis_date, o.close_date) < 7 OR DATE_DIFF('day', c.analysis_date, o.close_date) < 0 THEN 2
            WHEN DATE_DIFF('day', c.analysis_date, o.close_date) <= 29 THEN 1
            ELSE 0
        END AS close_date_score
    FROM opportunities o
    CROSS JOIN current_date c
),

competitor_threat AS (
    SELECT
        id,
        CASE
            WHEN competitor IN ('OpenAI', 'Google Vertex AI') THEN 2
            ELSE 0
        END AS competitor_score
    FROM opportunities
)

SELECT
    o.id,
    o.name,
    o.account_name,
    o.owner_name,
    o.stage_name,
    o.amount,
    o.close_date,

    COALESCE(t.time_in_stage_score, 0) AS time_in_stage_score,
    COALESCE(a.activity_gap_score, 0) AS activity_gap_score,
    COALESCE(m.missing_fields_score, 0) AS missing_fields_score,
    COALESCE(c.close_date_score, 0) AS close_date_score,
    COALESCE(ct.competitor_score, 0) AS competitor_score,

    LEAST(
        COALESCE(t.time_in_stage_score, 0) +
        COALESCE(a.activity_gap_score, 0) +
        COALESCE(m.missing_fields_score, 0) +
        COALESCE(c.close_date_score, 0) +
        COALESCE(ct.competitor_score, 0),
        10.0
    ) AS overall_risk_score,

    CASE
        WHEN LEAST(
            COALESCE(t.time_in_stage_score, 0) +
            COALESCE(a.activity_gap_score, 0) +
            COALESCE(m.missing_fields_score, 0) +
            COALESCE(c.close_date_score, 0) +
            COALESCE(ct.competitor_score, 0),
            10.0
        ) <= 3 THEN 'healthy'
        WHEN LEAST(
            COALESCE(t.time_in_stage_score, 0) +
            COALESCE(a.activity_gap_score, 0) +
            COALESCE(m.missing_fields_score, 0) +
            COALESCE(c.close_date_score, 0) +
            COALESCE(ct.competitor_score, 0),
            10.0
        ) <= 6 THEN 'at_risk'
        ELSE 'high_risk'
    END AS risk_level,

    t.days_in_stage,
    t.benchmark_max,
    a.days_since_activity,
    m.missing_field_list,
    c.days_to_close,
    o.next_step,
    o.competitor

FROM opportunities o
LEFT JOIN time_in_stage t ON o.id = t.id
LEFT JOIN activity_gaps a ON o.id = a.id
LEFT JOIN missing_fields m ON o.id = m.id
LEFT JOIN close_date_risk c ON o.id = c.id
LEFT JOIN competitor_threat ct ON o.id = ct.id
ORDER BY overall_risk_score DESC, amount DESC;

-- Display results
.print '📊 PIPELINE OVERVIEW'
.print ''

SELECT
    COUNT(*) AS total_deals,
    '$' || ROUND(SUM(amount) / 1000000.0, 1) || 'M' AS total_pipeline_value,
    ROUND(AVG(overall_risk_score), 1) AS avg_risk_score
FROM risk_analysis;

.print ''
.print '⚠️  RISK BREAKDOWN'
.print ''

SELECT
    risk_level,
    COUNT(*) AS deal_count,
    '$' || ROUND(SUM(amount) / 1000000.0, 1) || 'M' AS total_value,
    ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM risk_analysis), 1) AS pct_pipeline,
    ROUND(AVG(overall_risk_score), 1) AS avg_risk
FROM risk_analysis
GROUP BY risk_level
ORDER BY
    CASE risk_level
        WHEN 'high_risk' THEN 1
        WHEN 'at_risk' THEN 2
        ELSE 3
    END;

.print ''
.print '🚨 TOP 10 AT-RISK DEALS'
.print ''

SELECT
    account_name,
    stage_name,
    '$' || CAST(CAST(amount AS INTEGER) AS VARCHAR) AS amount,
    ROUND(overall_risk_score, 1) AS risk_score,
    days_in_stage,
    days_since_activity || 'd ago' as last_activity,
    owner_name
FROM risk_analysis
WHERE risk_level IN ('at_risk', 'high_risk')
ORDER BY overall_risk_score DESC, amount DESC
LIMIT 10;

-- Export to JSON
.print ''
.print 'Exporting dashboard data to dashboard_data.json...'

COPY (
    SELECT
        id,
        name,
        account_name,
        owner_name,
        stage_name,
        amount,
        ROUND(overall_risk_score, 1) as risk_score,
        risk_level,
        days_in_stage,
        days_since_activity,
        days_to_close,
        missing_field_list,
        next_step,
        competitor
    FROM risk_analysis
    WHERE risk_level IN ('at_risk', 'high_risk')
    ORDER BY overall_risk_score DESC
) TO 'data/dashboard_data.json' (FORMAT JSON, ARRAY true);

.print ''
.print '✅ Analysis complete! Generated alerts for ' || (SELECT COUNT(*) FROM risk_analysis WHERE risk_level IN ('at_risk', 'high_risk')) || ' deals.'
.print ''
