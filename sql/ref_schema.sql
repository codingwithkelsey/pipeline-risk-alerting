-- Schema for Pipeline Health Checker
-- DuckDB optimized for analytical queries

-- Stage benchmark reference table
CREATE TABLE IF NOT EXISTS stage_benchmarks (
    stage_name VARCHAR PRIMARY KEY,
    min_days INTEGER,
    max_days INTEGER,
    sequence_order INTEGER
);

-- Stage field requirements reference table
CREATE TABLE IF NOT EXISTS stage_requirements (
    stage_name VARCHAR,
    required_field VARCHAR,
    required_value VARCHAR,  -- NULL means just needs to be populated
    severity VARCHAR,  -- 'critical' or 'warning'
    PRIMARY KEY (stage_name, required_field)
);

-- Risk scoring rules configuration
CREATE TABLE IF NOT EXISTS risk_rules (
    rule_id VARCHAR PRIMARY KEY,
    rule_type VARCHAR,  -- 'time_in_stage', 'activity_gap', 'missing_field', etc.
    threshold_low DECIMAL(3,1),
    threshold_med DECIMAL(3,1),
    threshold_high DECIMAL(3,1),
    score_low DECIMAL(3,1),
    score_med DECIMAL(3,1),
    score_high DECIMAL(3,1),
    message_template VARCHAR,
    action_template VARCHAR
);
