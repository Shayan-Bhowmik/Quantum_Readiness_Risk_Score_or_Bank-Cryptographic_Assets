import csv
import random
from datetime import datetime, timezone
from faker import Faker

fake = Faker()
Faker.seed(42)
random.seed(42)

# Configurable options matching banking domain
SYSTEM_CATEGORIES = ["Card Network", "SWIFT", "Internal PKI"]

ALGORITHM_CONFIGS = [
    {"algorithm": "RSA", "key_size_bits": 1024, "recommended_pqc": "CRYSTALS-Dilithium", "base_years": 3.0},
    {"algorithm": "RSA", "key_size_bits": 2048, "recommended_pqc": "CRYSTALS-Dilithium", "base_years": 7.0},
    {"algorithm": "RSA", "key_size_bits": 4096, "recommended_pqc": "CRYSTALS-Dilithium", "base_years": 12.0},
    {"algorithm": "ECC", "key_size_bits": 256, "recommended_pqc": "CRYSTALS-Kyber", "base_years": 5.0},
    {"algorithm": "ECC", "key_size_bits": 384, "recommended_pqc": "CRYSTALS-Kyber", "base_years": 9.0},
]

DATA_SENSITIVITIES = ["Low", "Medium", "High", "Critical"]

ASSET_PREFIXES = {
    "Card Network": ["EMV Key", "POS Terminal Master Key", "PIN Verification Key", "Payment Gateway TLS", "CVV Gen Key"],
    "SWIFT": ["BKE Authentication Key", "RMA Exchange Cert", "SWIFT Alliance Gateway TLS", "Financial Messaging Signing Key", "HSM Root Key"],
    "Internal PKI": ["Domain Controller Root CA", "Staff Smartcard Issuing CA", "Internal API Mutual TLS", "VPN Gateway Cert", "Database Column Encryption Key"]
}

def generate_sample_assets(num_records=50, output_path="data/sample_assets.csv"):
    rows = []
    now_iso = datetime.now(timezone.utc).isoformat()
    
    for asset_id in range(1, num_records + 1):
        category = random.choice(SYSTEM_CATEGORIES)
        algo_choice = random.choice(ALGORITHM_CONFIGS)
        sensitivity = random.choice(DATA_SENSITIVITIES)
        
        prefix = random.choice(ASSET_PREFIXES[category])
        asset_name = f"{prefix} - {fake.city()} Node {random.randint(1, 99)}"
        
        # Realistic variability
        years_to_break = round(max(1.0, algo_choice["base_years"] + random.uniform(-1.5, 1.5)), 1)
        migration_cost_score = round(random.uniform(1.0, 10.0), 1)
        
        # Risk score formula approximation (0 to 100):
        # Higher sensitivity & lower years_to_break = higher risk
        sensitivity_weight = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}[sensitivity]
        time_urgency = max(0.1, 15.0 - years_to_break)
        raw_risk = (sensitivity_weight * 15.0) + (time_urgency * 2.5) + (migration_cost_score * 1.5)
        risk_score = round(min(100.0, max(0.0, raw_risk)), 1)
        
        # Phase assignment based on risk score
        if risk_score >= 75.0:
            migration_phase = "Phase 1"
        elif risk_score >= 50.0:
            migration_phase = "Phase 2"
        else:
            migration_phase = "Phase 3"
            
        rows.append({
            "asset_id": asset_id,
            "asset_name": asset_name,
            "system_category": category,
            "algorithm": algo_choice["algorithm"],
            "key_size_bits": algo_choice["key_size_bits"],
            "data_sensitivity": sensitivity,
            "estimated_years_to_break": years_to_break,
            "migration_cost_score": migration_cost_score,
            "risk_score": risk_score,
            "migration_phase": migration_phase,
            "recommended_pqc_algorithm": algo_choice["recommended_pqc"],
            "created_at": now_iso,
            "updated_at": now_iso
        })
        
    fieldnames = [
        "asset_id", "asset_name", "system_category", "algorithm",
        "key_size_bits", "data_sensitivity", "estimated_years_to_break",
        "migration_cost_score", "risk_score", "migration_phase",
        "recommended_pqc_algorithm", "created_at", "updated_at"
    ]
    
    with open(output_path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
        
    print(f"Successfully generated {num_records} synthetic crypto assets into {output_path}")

if __name__ == "__main__":
    generate_sample_assets(50, "data/sample_assets.csv")
