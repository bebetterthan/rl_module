"""
Test V3 Model - Aggressive Reward Engineering
"""

print("Loading libraries (please wait, this takes time)...")

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.full_recon_env import FullReconEnv

print("Libraries loaded!")
print()

print("="*70)
print("TESTING V3 MODEL (AGGRESSIVE REWARD) ON TEST SET")
print("="*70)
print()

model = PPO.load("./outputs/phase1b_recovery_v3_final.zip")
print("Model V3 loaded!")

def make_env():
    return FullReconEnv(scenarios_path="../data/phase1b_test.json")

env = DummyVecEnv([make_env])
print("Test environment created (5 scenarios)")
print()

rewards = []
nmaps = 0
actions_total = 0
action_dist = {i: 0 for i in range(9)}

print("Running 50 test episodes...")
for i in range(50):
    obs = env.reset()
    r = 0
    done = False
    while not done:
        a, _ = model.predict(obs, deterministic=True)
        obs, rew, done, _ = env.step(a)
        r += rew[0]
        actions_total += 1
        action_dist[a[0]] += 1
        if a[0] >= 6:  # nmap actions
            nmaps += 1
    rewards.append(r)
    if (i+1) % 10 == 0:
        print(f"  {i+1}/50 done...")

env.close()

print()
print("="*70)
print("RESULTS")
print("="*70)
print()

mean_r = np.mean(rewards)
std_r = np.std(rewards)
median_r = np.median(rewards)
min_r = np.min(rewards)
max_r = np.max(rewards)
nmap_pct = (nmaps / actions_total * 100)

print(f"Mean reward:    {mean_r:,.1f} +/- {std_r:,.1f}")
print(f"Median:         {median_r:,.1f}")
print(f"Range:          [{min_r:,.1f}, {max_r:,.1f}]")
print(f"Nmap usage:     {nmap_pct:.1f}%")
print()

# Action distribution
action_names = ["subfinder", "httpx_light", "httpx_full",
                "nmap_web_light", "nmap_web_full", "nmap_infra",
                "nmap_skip", "nmap_quick", "nmap_service"]
print("ACTION DISTRIBUTION:")
for i, name in enumerate(action_names):
    pct = (action_dist[i] / actions_total * 100) if actions_total > 0 else 0
    print(f"  {name:20s}: {action_dist[i]:3d} ({pct:5.1f}%)")
print()

# Compare to baseline and previous versions
baseline = 4129.6
v1_test = 1053.1
v1_nmap = 18.7
v2_test = 1078.5
v2_nmap = 20.6

print("COMPARISON:")
print(f"  Baseline:     {baseline:,.1f} (100% nmap)")
print(f"  V1 test:      {v1_test:,.1f} ({v1_nmap}% nmap)")
print(f"  V2 test:      {v2_test:,.1f} ({v2_nmap:.1f}% nmap)")
print(f"  V3 test:      {mean_r:,.1f} ({nmap_pct:.1f}% nmap)")
print()
print(f"  V3 vs baseline:  {mean_r - baseline:+,.1f} ({(mean_r-baseline)/baseline*100:+.1f}%)")
print(f"  V3 vs V2:        {mean_r - v2_test:+,.1f} ({(mean_r-v2_test)/v2_test*100:+.1f}%)")
print(f"  V3 vs V1:        {mean_r - v1_test:+,.1f} ({(mean_r-v1_test)/v1_test*100:+.1f}%)")
print()

# Verdict
target = baseline * 1.05
if mean_r >= target:
    print(f"SUCCESS! Beats baseline target ({target:,.1f})")
    print(f"  Gap: +{mean_r-target:,.1f}")
elif mean_r >= 3000:
    print(f"MAJOR PROGRESS! 3x better than V1!")
    print(f"  Still need: {target-mean_r:,.1f} to reach target")
elif mean_r >= 2000:
    print(f"SIGNIFICANT IMPROVEMENT! 2x better than V1!")
    print(f"  Progress: {((mean_r-v1_test)/(target-v1_test)*100):.1f}% of the way")
elif mean_r >= v2_test * 1.5:
    print(f"GOOD IMPROVEMENT! 1.5x better than V2")
    print(f"  Progress: {((mean_r-v1_test)/(target-v1_test)*100):.1f}% of the way")
elif mean_r > v2_test:
    print(f"IMPROVEMENT! Better than V2")
else:
    print("NO IMPROVEMENT vs V2")

print()

# Nmap usage analysis
if nmap_pct >= 80:
    print(f"Nmap usage: EXCELLENT ({nmap_pct:.1f}% - close to baseline 100%)")
elif nmap_pct >= 60:
    print(f"Nmap usage: GOOD ({nmap_pct:.1f}% - significant increase from V2 20%)")
elif nmap_pct >= 40:
    print(f"Nmap usage: IMPROVED ({nmap_pct:.1f}% - doubled from V2)")
elif nmap_pct > v2_nmap:
    print(f"Nmap usage: SLIGHT INCREASE ({nmap_pct:.1f}% from {v2_nmap:.1f}%)")
else:
    print(f"Nmap usage: NO CHANGE ({nmap_pct:.1f}%)")

print()
print("="*70)
