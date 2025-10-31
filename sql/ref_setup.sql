-- Reference data setup for Pipeline Health Checker

-- Insert stage benchmarks (from generate_salesforce_data.py)
INSERT INTO stage_benchmarks VALUES
    ('Qualification', 7, 14, 1),
    ('Solution Mapping', 14, 21, 2),
    ('Technical Evaluation', 21, 35, 3),
    ('EB Sign Off', 10, 21, 4),
    ('Contract Negotiation', 14, 28, 5);

-- Insert stage-specific field requirements
INSERT INTO stage_requirements VALUES
    -- Solution Mapping onwards needs Economic Buyer
    ('Solution Mapping', 'economic_buyer', NULL, 'critical'),
    ('Technical Evaluation', 'economic_buyer', NULL, 'critical'),
    ('EB Sign Off', 'economic_buyer', NULL, 'critical'),
    ('Contract Negotiation', 'economic_buyer', NULL, 'critical'),

    -- Technical Evaluation onwards needs Technical Champion
    ('Technical Evaluation', 'technical_champion', NULL, 'critical'),
    ('EB Sign Off', 'technical_champion', NULL, 'critical'),
    ('Contract Negotiation', 'technical_champion', NULL, 'critical'),

    -- EB Sign Off onwards needs Security Complete
    ('EB Sign Off', 'security_review_status', 'Complete', 'critical'),
    ('Contract Negotiation', 'security_review_status', 'Complete', 'critical'),

    -- All stages need Next Step (warning level for early stages, critical for later)
    ('Qualification', 'next_step', NULL, 'warning'),
    ('Solution Mapping', 'next_step', NULL, 'warning'),
    ('Technical Evaluation', 'next_step', NULL, 'warning'),
    ('EB Sign Off', 'next_step', NULL, 'critical'),
    ('Contract Negotiation', 'next_step', NULL, 'critical');

-- Insert risk scoring rules
INSERT INTO risk_rules VALUES
    ('time_in_stage', 'time_in_stage', 1.0, 1.5, 2.0, 0, 4, 8,
     'Stuck in {stage} for {days} days (benchmark: {benchmark_max} days max)',
     'Review deal progression - this deal has been in {stage} for {pct_over_benchmark}% of benchmark time'),

    ('activity_gap', 'activity_gap', 5, 10, 15, 0, 3, 7,
     'No activity in {days} days',
     'Re-engage immediately - {days} days without activity suggests deal may be stalled'),

    ('close_date_past', 'close_date', -999, 0, 999, 5, 0, 0,
     'Close date has passed',
     'Update close date and verify deal status - this may be a lost opportunity'),

    ('close_date_soon', 'close_date', 0, 14, 999, 2, 0, 0,
     'Closing in {days} days',
     'Verify all requirements are met - deal closes in {days} days'),

    ('competitor', 'competitor', 0, 1, 2, 0, 1, 2,
     'Active competitor: {competitor}',
     'Develop competitive strategy against {competitor}');
