#!/usr/bin/env python3
"""
DAY 3: Task 2.1 - Establish Fixed Baseline on 80 Scenarios
Run hardcoded agent 100 times to get stable baseline reference
"""
import json
import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from envs.full_recon_env import FullReconEnv
from baselines.hardcoded_agent import HardcodedAgent

def run_baseline_100_times(scenarios_file: str = "../data/phase1b_train_80_augmented.json"):
    """Run hardcoded baseline 100 times on 80 scenarios"""
    
    print("\n" + "="*80)
    print("DAY 3: BASELINE RECALIBRATION (80 Scenarios)")
    print("="*80)
    print(f"\nRunning hardcoded agent 100 episodes on {scenarios_file}")
    print("This establishes the FIXED BASELINE for all future comparisons")
    print()
    
    # Load environment
    env = FullReconEnv(scenarios_path=scenarios_file)
    agent = HardcodedAgent()
    agent.env = env  # Set environment reference
    
    # Storage
    all_rewards = []
    all_lengths = []
    nmap_usage = []
    
    # Run 100 episodes
    print("Running episodes: ", end='', flush=True)
    for episode in range(100):
        obs, info = env.reset()
        done = False
        episode_reward = 0
        episode_length = 0
        used_nmap = False
        
        while not done:
            action, _ = agent.predict(obs)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            
            # Track nmap usage (actions 6-8 are nmap modes)
            if 6 <= action <= 8:
                used_nmap = True
            
            done = terminated or truncated
        
        all_rewards.append(episode_reward)
        all_lengths.append(episode_length)
        nmap_usage.append(1 if used_nmap else 0)
        
        if (episode + 1) % 10 == 0:
            print(f"{episode + 1}...", end='', flush=True)
    
    print(" Done!\n")
    
    # Calculate statistics
    rewards_array = np.array(all_rewards)
    mean_reward = np.mean(rewards_array)
    std_reward = np.std(rewards_array)
    
    # 95% confidence interval
    n = len(rewards_array)
    ci_lower = mean_reward - 1.96 * (std_reward / np.sqrt(n))
    ci_upper = mean_reward + 1.96 * (std_reward / np.sqrt(n))
    
    # Results
    results = {
        "scenarios_file": scenarios_file,
        "total_scenarios": 80,
        "agent": "hardcoded_comprehensive",
        "runs": 100,
        "statistics": {
            "mean_reward": float(mean_reward),
            "std_reward": float(std_reward),
            "min_reward": float(np.min(rewards_array)),
            "max_reward": float(np.max(rewards_array)),
            "median_reward": float(np.median(rewards_array)),
            "ci_95_lower": float(ci_lower),
            "ci_95_upper": float(ci_upper)
        },
        "behavioral": {
            "mean_episode_length": float(np.mean(all_lengths)),
            "nmap_usage_pct": float(np.mean(nmap_usage) * 100)
        },
        "all_rewards": [float(r) for r in all_rewards]
    }
    
    # Display results
    print("="*80)
    print("FIXED BASELINE RESULTS (80 Scenarios)")
    print("="*80)
    print()
    print(f"Agent: Hardcoded Comprehensive (always use nmap)")
    print(f"Episodes: 100")
    print(f"Scenarios: 80 (phase1b_train_80.json)")
    print()
    print(f"Mean Reward:    {mean_reward:7.1f} ± {std_reward:6.1f}")
    print(f"Median Reward:  {np.median(rewards_array):7.1f}")
    print(f"Min/Max:        {np.min(rewards_array):7.1f} / {np.max(rewards_array):7.1f}")
    print(f"95% CI:         [{ci_lower:7.1f}, {ci_upper:7.1f}]")
    print()
    print(f"Mean Episode Length: {np.mean(all_lengths):5.1f} steps")
    print(f"Nmap Usage:          {np.mean(nmap_usage)*100:5.1f}%")
    print()
    
    # Compare to old baseline (20 scenarios)
    old_baseline_20 = 4045.3
    print("COMPARISON TO OLD BASELINE (20 scenarios):")
    print(f"  Old (20 scenarios): {old_baseline_20:7.1f}")
    print(f"  New (80 scenarios): {mean_reward:7.1f}")
    print(f"  Difference:         {mean_reward - old_baseline_20:7.1f} ({(mean_reward/old_baseline_20-1)*100:+.1f}%)")
    print()
    
    if abs(mean_reward - old_baseline_20) < 500:
        print("✅ New baseline similar to old (expected with more diversity)")
    else:
        print("⚠️  Significant difference - review scenario difficulty balance")
    
    print()
    print("="*80)
    print("This is now the OFFICIAL BASELINE for Phase 1B Recovery!")
    print("ALL future model evaluations will compare against this reference.")
    print("="*80)
    print()
    
    # Save results
    output_file = "FIXED_BASELINE_80scenarios.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Results saved to: {output_file}")
    print()
    print("Next: Configure training parameters for 80-scenario training")
    print()
    
    return results

if __name__ == "__main__":
    try:
        results = run_baseline_100_times()
        sys.exit(0)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
