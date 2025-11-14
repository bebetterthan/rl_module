#!/usr/bin/env python3
"""
Generate NEW test set for V13 vs V16 evaluation

Action 1.2: Create 25 unseen scenarios to test generalization
"""
import json
import random
from pathlib import Path
from datetime import datetime

def generate_test_scenario(scenario_id: int, scenario_type: str) -> dict:
    """Generate a single test scenario"""
    
    # Define scenario templates
    templates = {
        "web_only": {
            "ports": [80, 443, 8080, 3000, 8443],
            "subdomains": random.randint(15, 25),
            "endpoints": random.randint(12, 20),
            "nmap_value": "skip",  # Low nmap value
            "base_reward": 1500
        },
        "infrastructure": {
            "ports": [22, 3306, 5432, 6379, 27017, 1433],
            "subdomains": random.randint(5, 12),
            "endpoints": random.randint(3, 8),
            "nmap_value": "service",  # High nmap value
            "base_reward": 4000
        },
        "hybrid": {
            "ports": [80, 443, 22, 3306, 8080],
            "subdomains": random.randint(10, 18),
            "endpoints": random.randint(8, 15),
            "nmap_value": "quick",  # Medium nmap value
            "base_reward": 2500
        },
        "edge_case": {
            "ports": random.sample(range(4000, 10000), random.randint(5, 10)),
            "subdomains": random.randint(8, 20),
            "endpoints": random.randint(5, 15),
            "nmap_value": random.choice(["quick", "service", "skip"]),
            "base_reward": random.randint(2000, 5000)
        }
    }
    
    template = templates[scenario_type]
    
    # Generate unique ports
    ports = random.sample(template["ports"], min(4, len(template["ports"])))
    
    # Calculate rewards
    subfinder_reward = template["subdomains"] * 10
    httpx_reward = template["endpoints"] * 20
    
    nmap_multiplier = {
        "skip": 0.1,
        "quick": 0.5,
        "service": 1.0,
        "thorough": 1.2,
        "full": 1.5
    }
    
    nmap_reward = int(len(ports) * 100 * nmap_multiplier[template["nmap_value"]])
    
    skip_reward = subfinder_reward + httpx_reward + 50  # Small completion bonus
    nmap_best_reward = subfinder_reward + httpx_reward + nmap_reward
    
    # Create scenario
    scenario = {
        "id": f"test_{scenario_type}_{scenario_id}",
        "name": f"Test {scenario_type.replace('_', ' ').title()} {scenario_id}",
        "description": f"Test scenario for {scenario_type} evaluation",
        "target": f"test{scenario_id}.example.com",
        "complexity": "medium",
        "scenario_type": scenario_type,
        "metadata": {
            "total_subdomains": template["subdomains"],
            "live_endpoints": template["endpoints"],
            "open_ports": len(ports),
            "critical_services": 1 if scenario_type == "infrastructure" else 0,
            "port_list": sorted(ports),
            "technologies": ["Test", "Service"],
            "expected_strategy": template["nmap_value"]
        },
        "tool_results": {
            "subfinder": {
                "subdomains_found": template["subdomains"],
                "reward": subfinder_reward,
                "time_cost": 5
            },
            "httpx": {
                "live_endpoints": template["endpoints"],
                "status_codes": {"200": template["endpoints"]},
                "reward": httpx_reward,
                "time_cost": 10
            },
            "nmap": {
                "open_ports": len(ports),
                "services_identified": len(ports) if scenario_type != "web_only" else 0,
                "vulnerabilities": 1 if scenario_type == "infrastructure" else 0,
                "reward": nmap_reward,
                "time_cost": 30
            }
        },
        "optimal_action_sequence": {
            "actions": [2, 5, 8 if template["nmap_value"] != "skip" else 9],
            "expected_reward": nmap_best_reward if template["nmap_value"] != "skip" else skip_reward,
            "explanation": f"Best: {'Use nmap' if template['nmap_value'] != 'skip' else 'Skip nmap'}",
            "nmap_mode": template["nmap_value"],
            "reason": f"Test scenario - {template['nmap_value']} strategy"
        },
        "rewards": {
            "optimal": nmap_best_reward if template["nmap_value"] != "skip" else skip_reward,
            "suboptimal": skip_reward if template["nmap_value"] != "skip" else nmap_best_reward
        },
        "baseline_skip_reward": skip_reward,
        "baseline_nmap_reward": nmap_best_reward
    }
    
    return scenario

def generate_test_set(num_scenarios: int = 25) -> dict:
    """Generate complete test set"""
    
    # Distribution: 8 web, 10 infrastructure, 5 hybrid, 2 edge
    distribution = (
        ["web_only"] * 8 +
        ["infrastructure"] * 10 +
        ["hybrid"] * 5 +
        ["edge_case"] * 2
    )
    
    random.shuffle(distribution)
    
    scenarios = []
    for idx, scenario_type in enumerate(distribution[:num_scenarios], 1):
        scenario = generate_test_scenario(idx, scenario_type)
        scenarios.append(scenario)
    
    test_set = {
        "version": "1.0_test",
        "generated_at": datetime.now().isoformat(),
        "total_scenarios": len(scenarios),
        "purpose": "Evaluation set for V13 vs V16 generalization test",
        "note": "These scenarios were NOT seen during training",
        "scenarios": scenarios
    }
    
    return test_set

if __name__ == "__main__":
    print("\n🎯 ACTION 1.2: GENERATE TEST SET")
    print("="*80)
    print()
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate test set
    print("Generating 25 new test scenarios...")
    test_set = generate_test_set(25)
    
    # Save to file
    output_path = Path("../data/phase1b_evaluation_test.json")
    with open(output_path, 'w') as f:
        json.dump(test_set, f, indent=2)
    
    print(f"✅ Test set saved to: {output_path}")
    print()
    
    # Statistics
    scenario_types = {}
    for scenario in test_set["scenarios"]:
        stype = scenario["scenario_type"]
        scenario_types[stype] = scenario_types.get(stype, 0) + 1
    
    print("="*80)
    print("TEST SET STATISTICS:")
    print("="*80)
    print(f"  Total scenarios: {test_set['total_scenarios']}")
    print(f"\n  Distribution:")
    for stype, count in sorted(scenario_types.items()):
        print(f"    {stype:20s}: {count:2d} scenarios")
    
    print()
    print("="*80)
    print("✅ TEST SET READY!")
    print("="*80)
    print()
    print("Next: Run evaluate_on_test_set.py to test V13 and V16")
    print()
