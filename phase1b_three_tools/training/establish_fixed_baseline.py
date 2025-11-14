"""
Establish Fixed Baseline - Run 100 Times for Stable Reference
Action 1.1 from PM Strategic Plan
"""

import sys
import json
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from baselines.hardcoded_agent import HardcodedAgent
from baselines.random_agent import RandomAgent
from envs.full_recon_env import FullReconEnv

def run_baseline_100_times(agent_name="hardcoded", scenarios_file="../data/phase1b_train.json"):
    """
    Run baseline agent 100 times to establish fixed reference
    
    Args:
        agent_name: "hardcoded" or "random"
        scenarios_file: Path to scenarios JSON
    
    Returns:
        dict: Statistics including mean, std, confidence intervals
    """
    print(f"=" * 80)
    print(f"ESTABLISHING FIXED BASELINE: {agent_name.upper()}")
    print(f"=" * 80)
    print()
    
    # Load scenarios
    import json
    with open(scenarios_file, 'r') as f:
        scenarios = json.load(f)
    
    print(f"Loaded {len(scenarios)} scenarios")
    print(f"Running {agent_name} agent 100 times...")
    print()
    
    # Initialize agent
    if agent_name == "hardcoded":
        agent = HardcodedAgent()
    else:
        agent = RandomAgent()
    
    # Run 100 episodes
    all_rewards = []
    all_lengths = []
    all_nmap_usage = []
    
    for run in range(100):
        # Create fresh environment
        env = FullReconEnv(scenarios_path=scenarios_file)
        
        # Set agent's environment reference (both agents need it)
        agent.env = env
        
        obs, info = env.reset()
        
        episode_reward = 0
        episode_length = 0
        done = False
        
        while not done:
            # Use predict() method for baseline agents
            action, _ = agent.predict(obs)
            obs, reward, terminated, truncated, info = env.step(action[0])
            episode_reward += reward
            episode_length += 1
            done = terminated or truncated
        
        all_rewards.append(episode_reward)
        all_lengths.append(episode_length)
        all_nmap_usage.append(1.0 if info.get('nmap_used', False) else 0.0)
        
        if (run + 1) % 10 == 0:
            print(f"Progress: {run + 1}/100 runs completed")
    
    print()
    print("=" * 80)
    print("FIXED BASELINE STATISTICS")
    print("=" * 80)
    
    # Calculate statistics
    rewards_array = np.array(all_rewards)
    mean_reward = np.mean(rewards_array)
    std_reward = np.std(rewards_array)
    min_reward = np.min(rewards_array)
    max_reward = np.max(rewards_array)
    median_reward = np.median(rewards_array)
    
    # 95% confidence interval
    ci_lower = mean_reward - 1.96 * (std_reward / np.sqrt(100))
    ci_upper = mean_reward + 1.96 * (std_reward / np.sqrt(100))
    
    # Nmap usage
    mean_nmap = np.mean(all_nmap_usage) * 100
    
    # Print statistics
    print(f"\n{agent_name.upper()} BASELINE (100 runs):")
    print(f"  Mean Reward: {mean_reward:.1f}")
    print(f"  Std Deviation: {std_reward:.1f}")
    print(f"  Min: {min_reward:.1f}")
    print(f"  Max: {max_reward:.1f}")
    print(f"  Median: {median_reward:.1f}")
    print(f"  95% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
    print(f"  Mean Length: {np.mean(all_lengths):.1f}")
    print(f"  Nmap Usage: {mean_nmap:.1f}%")
    print()
    
    # Create statistics dict
    stats = {
        "agent": agent_name,
        "runs": 100,
        "scenarios_file": scenarios_file,
        "mean": float(mean_reward),
        "std": float(std_reward),
        "min": float(min_reward),
        "max": float(max_reward),
        "median": float(median_reward),
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "mean_length": float(np.mean(all_lengths)),
        "nmap_usage_pct": float(mean_nmap),
        "all_rewards": [float(r) for r in all_rewards]
    }
    
    # Save to file
    output_file = f"FIXED_BASELINE_{agent_name.upper()}.json"
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"✅ Fixed baseline saved to: {output_file}")
    print(f"✅ USE THIS AS PERMANENT REFERENCE FOR ALL COMPARISONS!")
    print()
    
    return stats

if __name__ == "__main__":
    print("\n🎯 ACTION 1.1: ESTABLISH FIXED BASELINE")
    print("=" * 80)
    print()
    
    # Run hardcoded baseline
    hardcoded_stats = run_baseline_100_times("hardcoded")
    
    print()
    print("=" * 80)
    print()
    
    # Run random baseline
    random_stats = run_baseline_100_times("random")
    
    print()
    print("=" * 80)
    print("🎉 FIXED BASELINES ESTABLISHED!")
    print("=" * 80)
    print()
    print("These are your PERMANENT reference baselines.")
    print("NEVER recalculate! Use these for ALL future comparisons.")
    print()
    print(f"Hardcoded Baseline: {hardcoded_stats['mean']:.1f} ± {hardcoded_stats['std']:.1f}")
    print(f"Random Baseline: {random_stats['mean']:.1f} ± {random_stats['std']:.1f}")
    print()
    print("✅ Ready for V13 vs V16 comparison with fixed reference!")
