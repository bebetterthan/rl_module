"""
Quick V1 vs V2 Comparison - Simplified
"""

import os
import sys
import json
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.full_recon_env import FullReconEnv

print("="*80)
print("QUICK V1 VS V2 COMPARISON")
print("="*80)

# Baseline
with open("FIXED_BASELINE_80scenarios.json", 'r') as f:
    baseline_mean = json.load(f)['statistics']['mean_reward']
print(f"\nBaseline: {baseline_mean:,.1f}")

# V2 Test Set (most important metric!)
print("\nEvaluating V2 on Test Set (most critical)...")
model_v2 = PPO.load("./outputs/phase1b_recovery_v2_final.zip")

def make_test_env():
    return FullReconEnv(scenarios_path="../data/phase1b_test.json")

env = DummyVecEnv([make_test_env])

rewards = []
nmap_count = 0
total_actions = 0

for ep in range(50):
    obs = env.reset()
    ep_reward = 0
    done = False
    
    while not done:
        action, _ = model_v2.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        ep_reward += reward[0]
        total_actions += 1
        if action[0] in [6, 7, 8]:
            nmap_count += 1
    
    rewards.append(ep_reward)
    if (ep + 1) % 10 == 0:
        print(f"  {ep+1}/50 episodes...")

env.close()

mean = np.mean(rewards)
std = np.std(rewards)
nmap_pct = (nmap_count / total_actions * 100) if total_actions > 0 else 0

print("\n" + "="*80)
print("V2 TEST SET RESULTS")
print("="*80)
print(f"\nMean Reward:     {mean:,.1f} +- {std:,.1f}")
print(f"Nmap Usage:      {nmap_pct:.1f}%")
print(f"vs Baseline:     {mean - baseline_mean:+,.1f} ({(mean-baseline_mean)/baseline_mean*100:+.1f}%)")

target = baseline_mean * 1.05
print(f"\nTarget (5%):     {target:,.1f}")
print(f"Meets Target:    {'YES' if mean >= target else 'NO'}")

# Previous V1 results (from earlier evaluation)
v1_test_mean = 1053.1
v1_nmap = 18.7

print("\n" + "="*80)
print("V1 VS V2 COMPARISON")
print("="*80)
print(f"\nV1 Test:         {v1_test_mean:,.1f} (nmap {v1_nmap:.1f}%)")
print(f"V2 Test:         {mean:,.1f} (nmap {nmap_pct:.1f}%)")
print(f"Improvement:     {mean - v1_test_mean:+,.1f} ({(mean-v1_test_mean)/v1_test_mean*100:+.1f}%)")

print("\n" + "="*80)
if mean >= target:
    print("SUCCESS! V2 beats baseline by >5%")
elif mean > v1_test_mean * 1.5:
    print("SIGNIFICANT IMPROVEMENT! V2 much better than V1")
elif mean > v1_test_mean:
    print("IMPROVEMENT! V2 better than V1")
else:
    print("NO IMPROVEMENT")
print("="*80)
