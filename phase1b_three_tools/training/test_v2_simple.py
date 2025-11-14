"""
Simple model tester - just run the model and print results
Avoid complex imports that cause KeyboardInterrupt
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

# Test V2 model on test set
print("="*70)
print("TESTING V2 MODEL ON TEST SET (5 scenarios, 50 episodes)")
print("="*70)
print()

model = PPO.load("./outputs/phase1b_recovery_v2_final.zip")
print("Model V2 loaded!")

def make_env():
    return FullReconEnv(scenarios_path="../data/phase1b_test.json")

env = DummyVecEnv([make_env])
print("Test environment created (5 scenarios)")
print()

rewards = []
nmaps = 0
actions_total = 0

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
        if a[0] >= 6:  # nmap actions are 6, 7, 8
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

# Compare to baseline and V1
baseline = 4129.6
v1_test = 1053.1
v1_nmap = 18.7

print("COMPARISON:")
print(f"  Baseline:     {baseline:,.1f} (100% nmap)")
print(f"  V1 test:      {v1_test:,.1f} ({v1_nmap}% nmap)")
print(f"  V2 test:      {mean_r:,.1f} ({nmap_pct:.1f}% nmap)")
print()
print(f"  V2 vs baseline:  {mean_r - baseline:+,.1f} ({(mean_r-baseline)/baseline*100:+.1f}%)")
print(f"  V2 vs V1:        {mean_r - v1_test:+,.1f} ({(mean_r-v1_test)/v1_test*100:+.1f}%)")
print()

target = baseline * 1.05
if mean_r >= target:
    print(f"SUCCESS! Beats baseline target ({target:,.1f}) by {mean_r-target:+,.1f}")
elif mean_r >= v1_test * 2:
    print(f"MAJOR IMPROVEMENT! 2x better than V1")
elif mean_r >= v1_test * 1.5:
    print(f"SIGNIFICANT IMPROVEMENT! 1.5x better than V1")  
elif mean_r > v1_test:
    print(f"IMPROVEMENT! Better than V1 by {((mean_r-v1_test)/v1_test*100):.1f}%")
else:
    print("NO IMPROVEMENT vs V1")

print()
print("="*70)
