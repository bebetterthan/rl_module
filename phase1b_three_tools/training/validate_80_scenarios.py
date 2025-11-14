#!/usr/bin/env python3
"""
Quick validation of generated 80-scenario JSON structure
Ensure compatibility with FullReconEnv
"""
import json
import sys

def validate_json_structure(filepath: str):
    print(f"\n🔍 Validating JSON structure: {filepath}")
    print("="*80)
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        print("✅ JSON syntax valid")
        
        # Check top-level structure
        assert 'scenarios' in data, "Missing 'scenarios' key"
        scenarios = data['scenarios']
        print(f"✅ Found {len(scenarios)} scenarios")
        
        # Validate first scenario structure (representative)
        s = scenarios[0]
        required_fields = ['id', 'domain', 'scenario_type', 'metadata', 
                          'tool_results', 'optimal_action_sequence', 'expected_rewards']
        
        for field in required_fields:
            assert field in s, f"Missing field: {field}"
        
        print("✅ All required fields present")
        
        # Check metadata
        meta = s['metadata']
        assert 'total_subdomains' in meta
        assert 'port_list' in meta
        assert 'optimal_strategy' in meta
        print("✅ Metadata structure correct")
        
        # Check tool_results
        tools = s['tool_results']
        assert 'subfinder' in tools
        assert 'httpx' in tools
        assert 'nmap' in tools
        print("✅ Tool results structure correct")
        
        # Check optimal_action_sequence
        actions = s['optimal_action_sequence']
        assert 'subfinder_mode' in actions
        assert 'httpx_mode' in actions
        assert 'nmap_mode' in actions
        print("✅ Action sequence structure correct")
        
        # Spot check: Port patterns unique?
        port_patterns = [tuple(sorted(s['metadata']['port_list'])) for s in scenarios]
        unique_ports = len(set(port_patterns))
        print(f"✅ Port uniqueness: {unique_ports}/{len(scenarios)} ({unique_ports/len(scenarios)*100:.1f}%)")
        
        # Spot check: Strategy distribution
        strategies = [s['metadata']['optimal_strategy'] for s in scenarios]
        from collections import Counter
        strategy_dist = Counter(strategies)
        print(f"\n📊 Strategy Distribution:")
        for strategy, count in sorted(strategy_dist.items()):
            print(f"   {strategy:10s}: {count:2d} scenarios ({count/len(scenarios)*100:5.1f}%)")
        
        print("\n" + "="*80)
        print("✅ VALIDATION PASSED - Ready for training!")
        print("="*80)
        return True
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return False

if __name__ == "__main__":
    filepath = "../data/phase1b_train_80.json"
    success = validate_json_structure(filepath)
    sys.exit(0 if success else 1)
