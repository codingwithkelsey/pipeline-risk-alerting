import csv
import random
from datetime import datetime, timedelta

# Set seed for reproducibility
random.seed(42)

# Configuration
STAGES = [
    ("Qualification", 10),
    ("Solution Mapping", 25),
    ("Technical Evaluation", 50),
    ("EB Sign Off", 75),
    ("Contract Negotiation", 90),
    ("Closed Won", 100),
    ("Closed Lost", 0)
]

STAGE_BENCHMARKS = {
    "Qualification": (7, 14),
    "Solution Mapping": (14, 21),
    "Technical Evaluation": (21, 35),
    "EB Sign Off": (10, 21),
    "Contract Negotiation": (14, 28)
}

COMPANY_NAMES = [
    "TechCorp", "DataSystems Inc", "CloudVentures", "FinanceFirst", "HealthTech Solutions",
    "RetailGiant", "ManufactureCo", "EduPlatform", "LogisticsHub", "MediaGroup",
    "BioTech Labs", "AutoInnovate", "EnergyFlow", "TravelBooking Co", "FoodService Systems",
    "RealEstate Pro", "InsureTech", "LegalEase", "MarketingAI", "CyberSecure",
    "ArchitectureStudio", "Construction Plus", "Hospitality Suite", "AgriTech", "PharmaCorp",
    "Telecommunications Inc", "Gaming Studios", "Fashion Retail", "Sports Analytics", "Music Streaming",
    "Publishing House", "Chemical Industries", "Aerospace Systems", "Maritime Logistics", "Mining Corp",
    "Utilities Management", "Government Services", "Non-Profit Org", "Consulting Group", "Research Institute",
    "E-commerce Platform", "Social Network Inc", "AdTech Solutions", "Payment Processor", "Supply Chain Co",
    "HR Software", "CRM Vendor", "Analytics Platform", "Security Services", "Cloud Storage Inc"
]

SALES_REPS = [
    "Sarah Chen", "Michael Rodriguez", "Emily Watson", "James Kim", "Lisa Anderson",
    "David Park", "Jennifer Martinez", "Robert Taylor", "Amanda Singh", "Christopher Lee"
]

USE_CASES = [
    "Customer support automation",
    "Content generation and marketing",
    "Code review and development assistance",
    "Research and analysis",
    "Document processing and summarization",
    "Sales enablement and prospecting",
    "Legal document review",
    "Technical documentation",
    "Data analysis and insights",
    "Internal knowledge management"
]

COMPETITORS = ["OpenAI", "Google Vertex AI", "Azure OpenAI", "Cohere", "None identified"]

SECURITY_STATUSES = ["Not Started", "In Progress", "Complete"]

LOSS_REASONS = [
    "Chose Competitor - OpenAI",
    "Budget/Timing",
    "No Decision Made",
    "Chose Competitor - Google"
]

def generate_opportunity_id():
    """Generate a realistic Salesforce ID (18 characters)"""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "006" + "".join(random.choices(chars, k=15))

def random_date_in_range(start_date, end_date):
    """Generate a random date between start and end"""
    time_between = end_date - start_date
    random_days = random.randint(0, time_between.days)
    return start_date + timedelta(days=random_days)

def generate_healthy_deal(idx, company_name, current_date):
    """Generate a healthy deal with good hygiene"""
    stage_idx = random.randint(0, 4)  # Qualification through Contract Negotiation
    stage_name, probability = STAGES[stage_idx]
    
    # Created date: 30-120 days ago
    created_date = current_date - timedelta(days=random.randint(30, 120))
    
    # Calculate time in current stage (within benchmark)
    min_days, max_days = STAGE_BENCHMARKS[stage_name]
    days_in_stage = random.randint(min_days, max_days)
    last_stage_change = current_date - timedelta(days=days_in_stage)
    
    # Last activity: 2-5 days ago (active)
    last_activity = current_date - timedelta(days=random.randint(2, 5))
    
    # Close date: reasonable future date (30-90 days out)
    close_date = current_date + timedelta(days=random.randint(30, 90))
    
    # Amount: $50K-$500K
    amount = random.randint(50, 500) * 1000
    
    # All stakeholders identified appropriately
    tech_champion = "John Smith (CTO)" if stage_idx >= 2 else ""  # From Technical Eval onwards
    economic_buyer = "Jane Doe (VP Ops)" if stage_idx >= 1 else ""  # From Solution Mapping onwards
    
    # Security review status appropriate to stage
    if stage_idx < 2:
        security_status = "Not Started"
    elif stage_idx == 2:
        security_status = random.choice(["In Progress", "Complete"])
    else:
        security_status = "Complete"
    
    # Specific next steps
    next_steps = [
        "Schedule discovery call with security team",
        "Demo custom use case on Friday 11/8",
        "Share ROI analysis with finance stakeholder",
        "Technical deep-dive session scheduled for next week",
        "Review MSA terms with legal",
        "Present to executive committee on 11/12"
    ]
    
    competitor = random.choice(["None identified", "OpenAI", "Google Vertex AI"])
    
    return {
        "Id": generate_opportunity_id(),
        "Name": f"{company_name} - Enterprise AI",
        "Account.Name": company_name,
        "Owner.Name": random.choice(SALES_REPS),
        "Amount": amount,
        "Type": "New Business",
        "StageName": stage_name,
        "Probability": probability,
        "CloseDate": close_date.strftime("%Y-%m-%d"),
        "CreatedDate": created_date.strftime("%Y-%m-%d"),
        "LastActivityDate": last_activity.strftime("%Y-%m-%d"),
        "LastStageChangeDate": last_stage_change.strftime("%Y-%m-%d"),
        "NextStep": random.choice(next_steps),
        "Economic_Buyer__c": economic_buyer,
        "Technical_Champion__c": tech_champion,
        "Security_Review_Status__c": security_status,
        "Competitor__c": competitor,
        "Use_Case__c": random.choice(USE_CASES),
        "Description": f"Evaluating Claude for {random.choice(USE_CASES).lower()}. Strong engagement from technical team.",
        "Loss_Reason__c": ""
    }

def generate_medium_risk_deal(idx, company_name, current_date):
    """Generate a medium-risk deal with 1-2 yellow flags"""
    stage_idx = random.randint(1, 4)  # Solution Mapping through Contract Negotiation
    stage_name, probability = STAGES[stage_idx]
    
    created_date = current_date - timedelta(days=random.randint(40, 150))
    
    # Pick 1-2 risk factors
    risk_factors = random.sample([
        "slow_velocity",
        "missing_stakeholder",
        "activity_gap",
        "vague_next_steps",
        "close_date_push"
    ], k=random.randint(1, 2))
    
    # Time in stage: 1.5x benchmark if slow_velocity
    min_days, max_days = STAGE_BENCHMARKS[stage_name]
    if "slow_velocity" in risk_factors:
        days_in_stage = int(max_days * 1.5)
    else:
        days_in_stage = random.randint(min_days, max_days)
    
    last_stage_change = current_date - timedelta(days=days_in_stage)
    
    # Activity gap: 7-10 days if activity_gap
    if "activity_gap" in risk_factors:
        last_activity = current_date - timedelta(days=random.randint(7, 10))
    else:
        last_activity = current_date - timedelta(days=random.randint(3, 6))
    
    # Close date
    if "close_date_push" in risk_factors:
        close_date = current_date + timedelta(days=random.randint(15, 40))
    else:
        close_date = current_date + timedelta(days=random.randint(30, 75))
    
    amount = random.randint(75, 400) * 1000
    
    # Missing stakeholder in early stages is acceptable
    if "missing_stakeholder" in risk_factors and stage_idx <= 2:
        tech_champion = ""
        economic_buyer = "Jane Doe (VP Ops)" if stage_idx >= 1 else ""
    elif stage_idx >= 2:
        tech_champion = "John Smith (CTO)"
        economic_buyer = "Jane Doe (VP Ops)" if stage_idx >= 1 else ""
    else:
        tech_champion = ""
        economic_buyer = ""
    

    if stage_idx < 2:
        security_status = "Not Started"
    elif stage_idx == 2:
        security_status = "In Progress"
    else:
        security_status = random.choice(["In Progress", "Complete"])
    

    if "vague_next_steps" in risk_factors:
        next_step = random.choice(["Follow up with team", "Waiting on customer", "Check in next week"])
    else:
        next_step = "Schedule follow-up call to discuss technical requirements"
    
    competitor = random.choice(["None identified", "OpenAI", "Azure OpenAI"])
    
    return {
        "Id": generate_opportunity_id(),
        "Name": f"{company_name} - Enterprise AI",
        "Account.Name": company_name,
        "Owner.Name": random.choice(SALES_REPS),
        "Amount": amount,
        "Type": random.choice(["New Business", "Upsell"]),
        "StageName": stage_name,
        "Probability": probability,
        "CloseDate": close_date.strftime("%Y-%m-%d"),
        "CreatedDate": created_date.strftime("%Y-%m-%d"),
        "LastActivityDate": last_activity.strftime("%Y-%m-%d"),
        "LastStageChangeDate": last_stage_change.strftime("%Y-%m-%d"),
        "NextStep": next_step,
        "Economic_Buyer__c": economic_buyer,
        "Technical_Champion__c": tech_champion,
        "Security_Review_Status__c": security_status,
        "Competitor__c": competitor,
        "Use_Case__c": random.choice(USE_CASES),
        "Description": f"Evaluating for {random.choice(USE_CASES).lower()}. Some delays in getting stakeholder alignment.",
        "Loss_Reason__c": ""
    }

def generate_high_risk_deal(idx, company_name, current_date):
    """Generate a high-risk deal with multiple red flags"""
    stage_idx = random.randint(2, 4)  # Technical Evaluation through Contract Negotiation
    stage_name, probability = STAGES[stage_idx]
    
    created_date = current_date - timedelta(days=random.randint(60, 180))
    
    # Multiple risk factors (3-4)
    risk_factors = random.sample([
        "no_activity",
        "missing_eb",
        "stuck_in_stage",
        "security_not_started",
        "competitor_threat",
        "multiple_pushes",
        "no_next_steps"
    ], k=random.randint(3, 4))
    
    # Time in stage: 2x+ benchmark
    min_days, max_days = STAGE_BENCHMARKS[stage_name]
    days_in_stage = int(max_days * random.uniform(2.0, 3.0))
    last_stage_change = current_date - timedelta(days=days_in_stage)
    
    # No activity in 15+ days
    if "no_activity" in risk_factors:
        last_activity = current_date - timedelta(days=random.randint(15, 30))
    else:
        last_activity = current_date - timedelta(days=random.randint(11, 14))
    
    # Close date issues
    if "multiple_pushes" in risk_factors:
        # Close date already passed or very soon
        close_date = current_date + timedelta(days=random.randint(-10, 10))
    else:
        close_date = current_date + timedelta(days=random.randint(10, 30))
    
    amount = random.randint(100, 600) * 1000
    
    # Missing economic buyer in later stages is a red flag
    if "missing_eb" in risk_factors:
        economic_buyer = ""
    else:
        economic_buyer = "Jane Doe (VP Ops)"
    
    tech_champion = "John Smith (CTO)" if stage_idx >= 2 else ""
    
    # Security review not started despite being in later stages
    if "security_not_started" in risk_factors:
        security_status = "Not Started"
    else:
        security_status = "In Progress"
    
    # Next steps blank or stale
    if "no_next_steps" in risk_factors:
        next_step = ""
    else:
        next_step = "Follow up - no response to last 2 emails"
    
    # Competitor threat without counter-strategy
    if "competitor_threat" in risk_factors:
        competitor = random.choice(["OpenAI", "Google Vertex AI", "Azure OpenAI"])
        description = f"Evaluating for {random.choice(USE_CASES).lower()}. Customer mentioned they're also looking at {competitor}. Champion has gone quiet."
    else:
        competitor = "None identified"
        description = f"Evaluating for {random.choice(USE_CASES).lower()}. Deal has stalled - multiple attempts to re-engage."
    
    return {
        "Id": generate_opportunity_id(),
        "Name": f"{company_name} - Enterprise AI",
        "Account.Name": company_name,
        "Owner.Name": random.choice(SALES_REPS),
        "Amount": amount,
        "Type": "New Business",
        "StageName": stage_name,
        "Probability": probability,
        "CloseDate": close_date.strftime("%Y-%m-%d"),
        "CreatedDate": created_date.strftime("%Y-%m-%d"),
        "LastActivityDate": last_activity.strftime("%Y-%m-%d"),
        "LastStageChangeDate": last_stage_change.strftime("%Y-%m-%d"),
        "NextStep": next_step,
        "Economic_Buyer__c": economic_buyer,
        "Technical_Champion__c": tech_champion,
        "Security_Review_Status__c": security_status,
        "Competitor__c": competitor,
        "Use_Case__c": random.choice(USE_CASES),
        "Description": description,
        "Loss_Reason__c": ""
    }

def generate_closed_deal(idx, company_name, current_date, is_won):
    """Generate a closed deal (won or lost)"""
    if is_won:
        stage_name, probability = STAGES[5]  # Closed Won
    else:
        stage_name, probability = STAGES[6]  # Closed Lost
    
    # Closed 10-60 days ago
    closed_date = current_date - timedelta(days=random.randint(10, 60))
    created_date = closed_date - timedelta(days=random.randint(60, 120))
    
    last_stage_change = closed_date
    last_activity = closed_date
    
    amount = random.randint(80, 450) * 1000
    
    if is_won:
        # Clean won deals have all the right characteristics
        tech_champion = "John Smith (CTO)"
        economic_buyer = "Jane Doe (VP Ops)"
        security_status = "Complete"
        next_step = "Onboarding scheduled"
        description = f"Successfully closed! Moving to implementation phase. Use case: {random.choice(USE_CASES).lower()}"
        loss_reason = ""
        competitor = random.choice(["None identified", "OpenAI"])
    else:
        # Lost deals show why they lost
        tech_champion = "John Smith (CTO)"
        economic_buyer = "Jane Doe (VP Ops)" if random.random() > 0.3 else ""
        security_status = random.choice(["In Progress", "Complete", "Not Started"])
        next_step = ""
        loss_reason = random.choice(LOSS_REASONS)
        competitor = "OpenAI" if "OpenAI" in loss_reason else random.choice(["Google Vertex AI", "Azure OpenAI"])
        description = f"Lost to competitor. Reason: {loss_reason}. They prioritized price/existing relationship."
    
    return {
        "Id": generate_opportunity_id(),
        "Name": f"{company_name} - Enterprise AI",
        "Account.Name": company_name,
        "Owner.Name": random.choice(SALES_REPS),
        "Amount": amount,
        "Type": "New Business",
        "StageName": stage_name,
        "Probability": probability,
        "CloseDate": closed_date.strftime("%Y-%m-%d"),
        "CreatedDate": created_date.strftime("%Y-%m-%d"),
        "LastActivityDate": last_activity.strftime("%Y-%m-%d"),
        "LastStageChangeDate": last_stage_change.strftime("%Y-%m-%d"),
        "NextStep": next_step,
        "Economic_Buyer__c": economic_buyer,
        "Technical_Champion__c": tech_champion,
        "Security_Review_Status__c": security_status,
        "Competitor__c": competitor,
        "Use_Case__c": random.choice(USE_CASES),
        "Description": description,
        "Loss_Reason__c": loss_reason
    }

def main():
    current_date = datetime(2025, 10, 30)
    opportunities = []
    
    # Shuffle company names
    companies = random.sample(COMPANY_NAMES, 50)
    
    idx = 0
    
    # Generate 30 healthy deals
    print("Generating 30 healthy deals...")
    for i in range(30):
        opp = generate_healthy_deal(idx, companies[idx], current_date)
        opportunities.append(opp)
        idx += 1
    
    # Generate 10 medium-risk deals
    print("Generating 10 medium-risk deals...")
    for i in range(10):
        opp = generate_medium_risk_deal(idx, companies[idx], current_date)
        opportunities.append(opp)
        idx += 1
    
    # Generate 5 high-risk deals
    print("Generating 5 high-risk deals...")
    for i in range(5):
        opp = generate_high_risk_deal(idx, companies[idx], current_date)
        opportunities.append(opp)
        idx += 1
    
    # Generate 5 closed deals (3 won, 2 lost)
    print("Generating 5 closed deals...")
    for i in range(3):
        opp = generate_closed_deal(idx, companies[idx], current_date, is_won=True)
        opportunities.append(opp)
        idx += 1
    
    for i in range(2):
        opp = generate_closed_deal(idx, companies[idx], current_date, is_won=False)
        opportunities.append(opp)
        idx += 1
    
    # Write to CSV
    fieldnames = [
        "Id", "Name", "Account.Name", "Owner.Name", "Amount", "Type", 
        "StageName", "Probability", "CloseDate", "CreatedDate", 
        "LastActivityDate", "LastStageChangeDate", "NextStep", 
        "Economic_Buyer__c", "Technical_Champion__c", "Security_Review_Status__c",
        "Competitor__c", "Use_Case__c", "Description", "Loss_Reason__c"
    ]
    
    output_file = "/home/claude/salesforce_opportunities.csv"
    
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(opportunities)
    
    print(f"\n✅ Generated {len(opportunities)} opportunities")
    print(f"📊 Breakdown:")
    print(f"   - 30 healthy deals")
    print(f"   - 10 medium-risk deals")
    print(f"   - 5 high-risk deals")
    print(f"   - 3 closed won deals")
    print(f"   - 2 closed lost deals")
    print(f"\n💾 Saved to: {output_file}")

if __name__ == "__main__":
    main()
