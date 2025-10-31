-- Ad hoc queries for analyzing pipeline risk


-- Overview: Total deals, pipeline value, weighted value, avg risk
SELECT
    COUNT(*) AS total_deals,
    '$' || ROUND(SUM(amount) / 1000000.0, 1) || 'M' AS total_pipeline_value,
    '$' || ROUND(SUM(amount * probability / 100.0) / 1000000.0, 1) || 'M' AS weighted_pipeline_value,
    ROUND(AVG(overall_risk_score), 1) AS avg_risk_score
FROM risk_analysis;


-- Overview: Distribution of deals and value by risk level
SELECT
    risk_level,
    COUNT(*) AS deal_count,
    '$' || ROUND(SUM(amount) / 1000000.0, 1) || 'M' AS total_value,
    ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM risk_analysis), 1) AS pct_of_pipeline,
    ROUND(AVG(overall_risk_score), 1) AS avg_risk_score
FROM risk_analysis
GROUP BY risk_level
ORDER BY
    CASE risk_level
        WHEN 'high_risk' THEN 1
        WHEN 'at_risk' THEN 2
        ELSE 3
    END;

-- Overview: Deals closing soon (≤14 days) with high risk scores
SELECT
    account_name,
    stage_name,
    '$' || FORMAT('{:,}', CAST(amount AS INTEGER)) AS amount,
    days_to_close,
    ROUND(overall_risk_score, 1) AS risk_score,
    owner_name,
    next_step
FROM risk_analysis
WHERE days_to_close <= 14 AND overall_risk_score >= 5.0
ORDER BY days_to_close ASC, overall_risk_score DESC;


-- Overview: Pipeline health by sales rep
SELECT
    owner_name,
    COUNT(*) AS total_deals,
    SUM(CASE WHEN risk_level = 'healthy' THEN 1 ELSE 0 END) AS healthy_deals,
    SUM(CASE WHEN risk_level = 'at_risk' THEN 1 ELSE 0 END) AS at_risk_deals,
    SUM(CASE WHEN risk_level = 'high_risk' THEN 1 ELSE 0 END) AS high_risk_deals,
    '$' || ROUND(SUM(amount) / 1000000.0, 1) || 'M' AS total_pipeline,
    ROUND(AVG(overall_risk_score), 1) AS avg_risk_score,
    '$' || ROUND(SUM(CASE WHEN risk_level IN ('at_risk', 'high_risk') THEN amount ELSE 0 END) / 1000000.0, 1) || 'M' AS at_risk_value
FROM risk_analysis
GROUP BY owner_name
ORDER BY avg_risk_score DESC;


-- Overview: Deal velocity and health by stage
SELECT
    r.stage_name,
    b.max_days AS benchmark_days,
    COUNT(*) AS deal_count,
    ROUND(AVG(r.days_in_stage), 0) AS avg_days_in_stage,
    ROUND(AVG(r.pct_of_benchmark), 0) AS pct_of_benchmark,
    SUM(CASE WHEN r.days_in_stage > b.max_days THEN 1 ELSE 0 END) AS deals_over_benchmark,
    '$' || ROUND(SUM(r.amount) / 1000000.0, 1) || 'M' AS stage_value,
    ROUND(AVG(r.overall_risk_score), 1) AS avg_risk_score
FROM risk_analysis r
LEFT JOIN stage_benchmarks b ON r.stage_name = b.stage_name
GROUP BY r.stage_name, b.max_days, b.sequence_order
ORDER BY b.sequence_order;


-- Overview: Which risk factors are most common across the pipeline
SELECT
    'Time in Stage' AS risk_driver,
    SUM(CASE WHEN time_in_stage_score > 0 THEN 1 ELSE 0 END) AS affected_deals,
    ROUND(AVG(CASE WHEN time_in_stage_score > 0 THEN time_in_stage_score END), 1) AS avg_score_when_present,
    ROUND(SUM(time_in_stage_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1) AS pct_of_total_risk
FROM risk_analysis
UNION ALL
SELECT
    'Activity Gap',
    SUM(CASE WHEN activity_gap_score > 0 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN activity_gap_score > 0 THEN activity_gap_score END), 1),
    ROUND(SUM(activity_gap_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1)
FROM risk_analysis
UNION ALL
SELECT
    'Missing Fields',
    SUM(CASE WHEN missing_fields_score > 0 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN missing_fields_score > 0 THEN missing_fields_score END), 1),
    ROUND(SUM(missing_fields_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1)
FROM risk_analysis
UNION ALL
SELECT
    'Close Date Risk',
    SUM(CASE WHEN close_date_score > 0 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN close_date_score > 0 THEN close_date_score END), 1),
    ROUND(SUM(close_date_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1)
FROM risk_analysis
UNION ALL
SELECT
    'Next Step Quality',
    SUM(CASE WHEN next_step_score > 0 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN next_step_score > 0 THEN next_step_score END), 1),
    ROUND(SUM(next_step_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1)
FROM risk_analysis
UNION ALL
SELECT
    'Competitor Threat',
    SUM(CASE WHEN competitor_score > 0 THEN 1 ELSE 0 END),
    ROUND(AVG(CASE WHEN competitor_score > 0 THEN competitor_score END), 1),
    ROUND(SUM(competitor_score) * 100.0 / (SELECT SUM(overall_risk_score) FROM risk_analysis WHERE overall_risk_score > 0), 1)
FROM risk_analysis
ORDER BY affected_deals DESC;


-- Overview: Highest priority deals requiring intervention

SELECT
    account_name,
    name AS opportunity_name,
    stage_name,
    '$' || FORMAT('{:,}', CAST(amount AS INTEGER)) AS amount,
    ROUND(overall_risk_score, 1) AS risk_score,
    days_in_stage,
    days_since_activity,
    owner_name,
    CASE
        WHEN time_in_stage_score > 0 THEN '⏱️  Stuck in stage'
        ELSE ''
    END || ' ' ||
    CASE
        WHEN activity_gap_score > 0 THEN '📵 Low activity'
        ELSE ''
    END || ' ' ||
    CASE
        WHEN missing_fields_score > 0 THEN '❌ Missing fields'
        ELSE ''
    END AS flags
FROM risk_analysis
WHERE risk_level IN ('at_risk', 'high_risk')
ORDER BY overall_risk_score DESC, amount DESC
LIMIT 10;
