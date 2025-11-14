import json
import numpy as np

print("=" * 60)
print("ANALISIS MODEL RL PHASE 1A & PHASE 1B")
print("=" * 60)

# Phase 1A Analysis
print("\n### PHASE 1A: 2-Tool Sequential (Subfinder + HTTPX) ###")
print("-" * 60)

phase1a_eval = np.load('phase1_single_tool/outputs/run_20251113_034834/eval_logs/evaluations.npz')
phase1a_timesteps = phase1a_eval['timesteps']
phase1a_rewards = phase1a_eval['results']
phase1a_mean_rewards = np.mean(phase1a_rewards, axis=1)

print(f"Training: 100k steps")
print(f"Path: phase1_single_tool/outputs/run_20251113_034834")
print(f"\nEvaluation Progress (every 10k steps):")
for i, (ts, reward) in enumerate(zip(phase1a_timesteps, phase1a_mean_rewards)):
    print(f"  {ts:6d} steps: {reward:7.2f} reward")

print(f"\nFinal Performance:")
print(f"  Best eval: {np.max(phase1a_mean_rewards):.2f}")
print(f"  Final eval: {phase1a_mean_rewards[-1]:.2f}")
print(f"  Average (last 3): {np.mean(phase1a_mean_rewards[-3:]):.2f}")

# Phase 1B Analysis
print("\n" + "=" * 60)
print("### PHASE 1B: 3-Tool Sequential (Subfinder + HTTPX + Nmap) ###")
print("-" * 60)

# Manually construct results since JSON is incomplete
phase1b_results = {
    'baselines': {
        'random': {'mean': 2698.40, 'std': 1915.05},
        'hardcoded': {'mean': 4445.30, 'std': 2581.06},
        'phase1a_wrapper': {'mean': 2796.25, 'std': 1736.69}
    },
    'agent': {
        'mean': 4025.40,
        'std': 1954.996,
        'min': 1944.0,
        'max': 7288.0,
        'mean_length': 3.0,
        'mean_subdomains': 10.9,
        'mean_endpoints': 7.95,
        'mean_ports': 3.15,
        'mean_services': 1.1,
        'nmap_usage_rate': 0.6
    }
}

phase1b_eval = np.load('phase1b_three_tools/outputs/phase1b_run_20251113_220412/eval_logs/evaluations.npz')
phase1b_timesteps = phase1b_eval['timesteps']
phase1b_rewards = phase1b_eval['results']
phase1b_mean_rewards = np.mean(phase1b_rewards, axis=1)

print(f"Training: 150k steps")
print(f"Path: phase1b_three_tools/outputs/phase1b_run_20251113_220412")

print(f"\nBaselines (20 test scenarios):")
print(f"  Random:         {phase1b_results['baselines']['random']['mean']:7.2f} ± {phase1b_results['baselines']['random']['std']:.2f}")
print(f"  Hardcoded:      {phase1b_results['baselines']['hardcoded']['mean']:7.2f} ± {phase1b_results['baselines']['hardcoded']['std']:.2f} ← Best")
print(f"  Phase1A Agent:  {phase1b_results['baselines']['phase1a_wrapper']['mean']:7.2f} ± {phase1b_results['baselines']['phase1a_wrapper']['std']:.2f}")

print(f"\nAgent Performance (20 test scenarios):")
agent = phase1b_results['agent']
print(f"  Mean Reward:    {agent['mean']:7.2f} ± {agent['std']:.2f}")
print(f"  Range:          {agent['min']:.0f} - {agent['max']:.0f}")
print(f"  Episode Length: {agent['mean_length']:.1f} actions")

hardcoded = phase1b_results['baselines']['hardcoded']['mean']
improvement = (agent['mean'] / hardcoded - 1) * 100
print(f"\nVs Best Baseline:")
print(f"  Improvement:    {improvement:+.1f}%")
print(f"  Status:         {'✅ SUCCESS' if improvement > 0 else '❌ NEEDS WORK'}")

print(f"\nStrategic Behavior:")
print(f"  Nmap Usage:     {agent['nmap_usage_rate']*100:.0f}%")
print(f"  Avg Subdomains: {agent['mean_subdomains']:.1f}")
print(f"  Avg Endpoints:  {agent['mean_endpoints']:.1f}")
print(f"  Avg Ports:      {agent['mean_ports']:.1f}")
print(f"  Avg Services:   {agent['mean_services']:.1f}")

print(f"\nEvaluation Progress (every 10k steps):")
for i, (ts, reward) in enumerate(zip(phase1b_timesteps, phase1b_mean_rewards)):
    print(f"  {ts:6d} steps: {reward:7.2f} reward")

print(f"\nFinal Performance:")
print(f"  Best eval:      {np.max(phase1b_mean_rewards):.2f}")
print(f"  Final eval:     {phase1b_mean_rewards[-1]:.2f}")
print(f"  Average (last 5): {np.mean(phase1b_mean_rewards[-5:]):.2f}")

# Comparison
print("\n" + "=" * 60)
print("### COMPARISON & INSIGHTS ###")
print("-" * 60)

print(f"\n1. Complexity Increase:")
print(f"   Phase 1A: 2 tools, 6 actions → {phase1a_mean_rewards[-1]:.2f} reward")
print(f"   Phase 1B: 3 tools, 9 actions → {agent['mean']:.2f} reward")
print(f"   Note: Different reward scales, not directly comparable")

print(f"\n2. Learning Progress:")
print(f"   Phase 1A: Peak at {np.argmax(phase1a_mean_rewards)*10000} steps ({np.max(phase1a_mean_rewards):.2f})")
print(f"   Phase 1B: Peak at {np.argmax(phase1b_mean_rewards)*10000} steps ({np.max(phase1b_mean_rewards):.2f})")

print(f"\n3. Stability:")
phase1a_std_late = np.std(phase1a_mean_rewards[-3:])
phase1b_std_late = np.std(phase1b_mean_rewards[-5:])
print(f"   Phase 1A: Last 3 evals std = {phase1a_std_late:.2f}")
print(f"   Phase 1B: Last 5 evals std = {phase1b_std_late:.2f}")

print(f"\n4. Strategic Intelligence:")
print(f"   Phase 1A: Fixed 2-step workflow")
print(f"   Phase 1B: Conditional nmap usage ({agent['nmap_usage_rate']*100:.0f}%)")
print(f"   Phase 1B: Shows contextual tool selection ability")

print(f"\n5. Success Assessment:")
print(f"   Phase 1A: ✅ Completed training, learned basic workflow")
print(f"   Phase 1B: {improvement:+.1f}% vs hardcoded baseline")
if improvement > 30:
    print(f"   Phase 1B: ✅ EXCELLENT - Beats target by large margin")
elif improvement > 0:
    print(f"   Phase 1B: ⚠️  MARGINAL - Beats baseline but below 30% target")
else:
    print(f"   Phase 1B: ❌ UNDERPERFORMING - Needs improvement")

print("\n" + "=" * 60)
print("MODEL LOCATIONS:")
print("-" * 60)
print(f"Phase 1A: phase1_single_tool/outputs/run_20251113_034834/final_model.zip")
print(f"Phase 1B: phase1b_three_tools/outputs/phase1b_run_20251113_220412/final_model.zip")
print("=" * 60)
