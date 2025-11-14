#!/usr/bin/env python3
"""
Task 1.1: Analyze Current 20 Scenarios
Understand patterns, gaps, and over-representations to design 80-scenario expansion
"""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd

def analyze_scenarios(scenarios_path: str):
    """Comprehensive analysis of current scenario set"""
    
    # Load scenarios
    with open(scenarios_path, 'r') as f:
        data = json.load(f)
        scenarios = data['scenarios']
    
    print("\n" + "="*80)
    print("TASK 1.1: CURRENT SCENARIO ANALYSIS (20 Scenarios)")
    print("="*80)
    print()
    
    # === DIMENSION 1: Target Size Distribution ===
    print("DIMENSION 1: TARGET SIZE DISTRIBUTION")
    print("-" * 80)
    
    subdomain_counts = []
    for s in scenarios:
        count = s['metadata']['total_subdomains']
        subdomain_counts.append((s['id'], count))
    
    small = [(sid, c) for sid, c in subdomain_counts if 3 <= c <= 7]
    medium = [(sid, c) for sid, c in subdomain_counts if 8 <= c <= 15]
    large = [(sid, c) for sid, c in subdomain_counts if 16 <= c <= 25]
    
    print(f"Small (3-7 subdomains):   {len(small):2d} scenarios ({len(small)/len(scenarios)*100:5.1f}%)")
    print(f"Medium (8-15 subdomains): {len(medium):2d} scenarios ({len(medium)/len(scenarios)*100:5.1f}%)")
    print(f"Large (16-25 subdomains): {len(large):2d} scenarios ({len(large)/len(scenarios)*100:5.1f}%)")
    print()
    print("TARGET for 80 scenarios: 31% small, 44% medium, 25% large")
    print("CURRENT balance:", "✅ Good" if len(medium) >= len(small) and len(medium) >= len(large) else "⚠️ Imbalanced")
    print()
    
    # === DIMENSION 2: Scenario Type Distribution ===
    print("DIMENSION 2: SCENARIO TYPE DISTRIBUTION")
    print("-" * 80)
    
    type_counts = Counter([s['scenario_type'] for s in scenarios])
    
    # Categorize into main types
    web_only = sum(v for k, v in type_counts.items() if 'web' in k.lower() and 'infra' not in k.lower())
    infrastructure = sum(v for k, v in type_counts.items() if 'infra' in k.lower() or 'database' in k.lower() or 'ssh' in k.lower())
    hybrid = sum(v for k, v in type_counts.items() if any(x in k.lower() for x in ['hybrid', 'full', 'mixed']))
    edge = len(scenarios) - web_only - infrastructure - hybrid
    
    for stype, count in sorted(type_counts.items()):
        print(f"  {stype:25s}: {count:2d} scenarios")
    
    print()
    print(f"CATEGORIZATION:")
    print(f"  Web-only:        {web_only:2d} scenarios ({web_only/len(scenarios)*100:5.1f}%)")
    print(f"  Infrastructure:  {infrastructure:2d} scenarios ({infrastructure/len(scenarios)*100:5.1f}%)")
    print(f"  Hybrid:          {hybrid:2d} scenarios ({hybrid/len(scenarios)*100:5.1f}%)")
    print(f"  Edge cases:      {edge:2d} scenarios ({edge/len(scenarios)*100:5.1f}%)")
    print()
    print("TARGET for 80 scenarios: 37% web, 31% infra, 25% hybrid, 7% edge")
    print("CURRENT balance:", "✅ Reasonable" if 0.3 <= web_only/len(scenarios) <= 0.5 else "⚠️ Imbalanced")
    print()
    
    # === DIMENSION 3: Port Pattern Analysis ===
    print("DIMENSION 3: PORT PATTERN ANALYSIS")
    print("-" * 80)
    
    port_patterns = []
    port_pattern_counts = Counter()
    
    for s in scenarios:
        ports = tuple(sorted(s['metadata']['port_list']))
        port_patterns.append((s['id'], ports))
        port_pattern_counts[ports] += 1
    
    print(f"Total scenarios: {len(port_patterns)}")
    print(f"Unique port patterns: {len(port_pattern_counts)}")
    print()
    
    # Find duplicates
    duplicates = [(ports, count) for ports, count in port_pattern_counts.items() if count > 1]
    
    if duplicates:
        print("⚠️  DUPLICATE PORT PATTERNS FOUND:")
        for ports, count in sorted(duplicates, key=lambda x: x[1], reverse=True):
            print(f"  {str(ports):40s}: {count} scenarios (REMOVE DUPLICATES!)")
        print()
    else:
        print("✅ All port patterns are UNIQUE (excellent!)")
        print()
    
    print("Sample port patterns:")
    for sid, ports in port_patterns[:10]:
        print(f"  {sid:30s}: {ports}")
    print()
    print("TARGET for 80 scenarios: 80 UNIQUE patterns (one per scenario)")
    print("CURRENT status:", f"{len(port_pattern_counts)} unique / {len(scenarios)} total")
    print()
    
    # === DIMENSION 4: Technology Stack Variety ===
    print("DIMENSION 4: TECHNOLOGY STACK VARIETY")
    print("-" * 80)
    
    all_technologies = []
    for s in scenarios:
        techs = s['metadata'].get('technologies', [])
        all_technologies.extend(techs)
    
    tech_counts = Counter(all_technologies)
    unique_tech_count = len(tech_counts)
    
    print(f"Total technology mentions: {len(all_technologies)}")
    print(f"Unique technologies: {unique_tech_count}")
    print()
    
    print("Top 10 technologies:")
    for tech, count in tech_counts.most_common(10):
        pct = count / len(scenarios) * 100
        status = "⚠️ Over-represented" if pct > 50 else "✅"
        print(f"  {tech:20s}: {count:2d} scenarios ({pct:5.1f}%) {status}")
    
    print()
    print("TARGET for 80 scenarios: 30+ unique tech stacks, no stack >10%")
    print("CURRENT status:", f"{unique_tech_count} unique technologies")
    print()
    
    # === DIMENSION 5: Naming Pattern Analysis ===
    print("DIMENSION 5: NAMING PATTERN ANALYSIS")
    print("-" * 80)
    
    all_subdomains = []
    for s in scenarios:
        if 'tool_results' in s and 'subfinder' in s['tool_results']:
            subdomains = s['tool_results']['subfinder'].get('subdomains', [])
            # Extract just subdomain prefix (before .domain.com)
            names = [sd.split('.')[0] for sd in subdomains if '.' in sd]
            all_subdomains.extend(names)
    
    name_counts = Counter(all_subdomains)
    unique_names = len(name_counts)
    
    print(f"Total subdomain instances: {len(all_subdomains)}")
    print(f"Unique subdomain names: {unique_names}")
    print()
    
    print("Top 15 most common names:")
    for name, count in name_counts.most_common(15):
        pct = count / len(scenarios) * 100
        status = "⚠️ Over-used" if pct > 70 else "✅"
        print(f"  {name:15s}: {count:3d} occurrences ({pct:5.1f}% of scenarios) {status}")
    
    print()
    print("TARGET for 80 scenarios: 50+ unique names, no name >30% presence")
    print("CURRENT status:", f"{unique_names} unique names")
    print()
    
    # === DIMENSION 6: Optimal Strategy Distribution ===
    print("DIMENSION 6: OPTIMAL STRATEGY DISTRIBUTION")
    print("-" * 80)
    
    strategies = []
    for s in scenarios:
        if 'optimal_action_sequence' in s:
            nmap_mode = s['optimal_action_sequence'].get('nmap_mode', 'unknown')
            strategies.append((s['id'], nmap_mode))
    
    strategy_counts = Counter([mode for _, mode in strategies])
    
    print("Optimal strategy distribution:")
    for strategy, count in sorted(strategy_counts.items()):
        pct = count / len(scenarios) * 100
        print(f"  {strategy:15s}: {count:2d} scenarios ({pct:5.1f}%)")
    
    print()
    print("TARGET for 80 scenarios: 31% skip, 37% quick, 25% service, 7% full")
    print("CURRENT balance:", "✅ Balanced" if len(strategy_counts) >= 3 else "⚠️ Imbalanced")
    print()
    
    # === CORRELATION ANALYSIS ===
    print("DIMENSION 7: ANTI-CORRELATION ANALYSIS")
    print("-" * 80)
    
    # Check if size correlates with type
    print("Checking: Does size correlate with scenario type?")
    
    size_type_matrix = defaultdict(lambda: defaultdict(int))
    for s in scenarios:
        count = s['metadata']['total_subdomains']
        stype = 'web' if 'web' in s['scenario_type'].lower() else 'infra' if 'infra' in s['scenario_type'].lower() else 'hybrid'
        
        size_cat = 'small' if count <= 7 else 'medium' if count <= 15 else 'large'
        size_type_matrix[size_cat][stype] += 1
    
    print()
    for size_cat in ['small', 'medium', 'large']:
        print(f"  {size_cat:10s}:", end='')
        for stype in ['web', 'infra', 'hybrid']:
            count = size_type_matrix[size_cat][stype]
            print(f"  {stype}: {count:2d}", end='')
        print()
    
    print()
    print("⚠️  CRITICAL: Check for obvious correlations!")
    print("   Example bad pattern: All small = web, all large = infra")
    print("   Good pattern: Mixed distribution across all cells")
    print()
    
    # === SUMMARY & RECOMMENDATIONS ===
    print("="*80)
    print("SUMMARY & RECOMMENDATIONS FOR 80-SCENARIO EXPANSION")
    print("="*80)
    print()
    
    recommendations = []
    
    # Port patterns
    if len(port_pattern_counts) < len(scenarios):
        recommendations.append(f"⚠️  Remove {len(scenarios) - len(port_pattern_counts)} duplicate port patterns")
    else:
        recommendations.append("✅ Port patterns are unique - maintain uniqueness in expansion")
    
    # Size distribution
    if len(small) < len(scenarios) * 0.25:
        recommendations.append(f"⚠️  Increase small scenarios: {len(small)} → 25 (in 80-set)")
    
    # Technology variety
    over_represented = [tech for tech, count in tech_counts.items() if count / len(scenarios) > 0.5]
    if over_represented:
        recommendations.append(f"⚠️  Reduce over-represented techs: {', '.join(over_represented)}")
    
    # Naming variety
    over_used_names = [name for name, count in name_counts.items() if count / len(scenarios) > 0.7]
    if over_used_names:
        recommendations.append(f"⚠️  Diversify naming: {', '.join(over_used_names[:5])} appear too often")
    
    # Strategy balance
    if len(strategy_counts) < 4:
        recommendations.append("⚠️  Add more optimal strategy variety (need skip/quick/service/full balance)")
    
    print("EXPANSION PRIORITIES:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
    
    print()
    print("="*80)
    print("TASK 1.1 COMPLETE!")
    print("="*80)
    print()
    print("Next: Task 1.2 - Design 80-scenario expansion strategy")
    print()
    
    # Save analysis to file
    analysis_report = {
        "total_scenarios": len(scenarios),
        "size_distribution": {
            "small": len(small),
            "medium": len(medium),
            "large": len(large)
        },
        "type_distribution": {
            "web_only": web_only,
            "infrastructure": infrastructure,
            "hybrid": hybrid,
            "edge": edge
        },
        "unique_port_patterns": len(port_pattern_counts),
        "duplicate_patterns": len(duplicates),
        "unique_technologies": unique_tech_count,
        "unique_subdomain_names": unique_names,
        "strategy_distribution": dict(strategy_counts),
        "recommendations": recommendations
    }
    
    with open('scenario_analysis_report.json', 'w') as f:
        json.dump(analysis_report, f, indent=2)
    
    print("Report saved to: scenario_analysis_report.json")
    print()

if __name__ == "__main__":
    scenarios_path = "../data/phase1b_train.json"
    analyze_scenarios(scenarios_path)
