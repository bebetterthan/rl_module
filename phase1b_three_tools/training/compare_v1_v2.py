"""
Evaluate Recovery V2 Model
Compare v1 vs v2 performance
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.full_recon_env import FullReconEnv


def quick_evaluate(model_path: str, scenarios_file: str, dataset_name: str, n_episodes: int = 50) -> Dict:
    """Quick evaluation"""
    print(f"\nEvaluating {dataset_name}...")
    print(f"  Model: {os.path.basename(model_path)}")
    
    model = PPO.load(model_path)
    
    def make_env():
        return FullReconEnv(scenarios_path=scenarios_file)
    env = DummyVecEnv([make_env])
    
    all_rewards = []
    nmap_usage = 0
    total_actions = 0
    
    for episode in range(n_episodes):
        obs = env.reset()
        episode_reward = 0
        done = False
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            
            episode_reward += reward[0]
            total_actions += 1
            if action[0] in [6, 7, 8]:
                nmap_usage += 1
        
        all_rewards.append(episode_reward)
    
    env.close()
    
    mean_reward = np.mean(all_rewards)
    std_reward = np.std(all_rewards)
    nmap_pct = (nmap_usage / total_actions * 100) if total_actions > 0 else 0
    
    print(f"  Mean Reward: {mean_reward:,.1f} +- {std_reward:,.1f}")
    print(f"  Nmap Usage:  {nmap_pct:.1f}%")
    
    return {
        'mean_reward': float(mean_reward),
        'std_reward': float(std_reward),
        'nmap_usage_pct': float(nmap_pct),
        'all_rewards': [float(r) for r in all_rewards]
    }


def main():
    print("="*80)
    print("RECOVERY MODEL COMPARISON: V1 vs V2")
    print("="*80)
    
    # Load baseline
    with open("FIXED_BASELINE_80scenarios.json", 'r') as f:
        baseline = json.load(f)
    baseline_mean = baseline['statistics']['mean_reward']
    
    print(f"\nBaseline: {baseline_mean:,.1f}")
    
    # Evaluate V1
    print("\n" + "="*80)
    print("V1 RESULTS (entropy 0.06, 500k steps, lr 3e-4)")
    print("="*80)
    
    v1_train = quick_evaluate(
        "./outputs/phase1b_recovery_final.zip",
        "../data/phase1b_train_80_augmented.json",
        "Training Set",
        n_episodes=50
    )
    
    v1_test = quick_evaluate(
        "./outputs/phase1b_recovery_final.zip",
        "../data/phase1b_test.json",
        "Test Set",
        n_episodes=50
    )
    
    # Evaluate V2
    print("\n" + "="*80)
    print("V2 RESULTS (entropy 0.01, 1M steps, lr 1e-4)")
    print("="*80)
    
    v2_train = quick_evaluate(
        "./outputs/phase1b_recovery_v2_final.zip",
        "../data/phase1b_train_80_augmented.json",
        "Training Set",
        n_episodes=50
    )
    
    v2_test = quick_evaluate(
        "./outputs/phase1b_recovery_v2_final.zip",
        "../data/phase1b_test.json",
        "Test Set",
        n_episodes=50
    )
    
    # Comparison
    print("\n" + "="*80)
    print("COMPARATIVE SUMMARY")
    print("="*80)
    
    print("\nTRAINING SET PERFORMANCE:")
    print(f"  Baseline:    {baseline_mean:,.1f}")
    print(f"  V1:          {v1_train['mean_reward']:,.1f} ({(v1_train['mean_reward']-baseline_mean)/baseline_mean*100:+.1f}%)")
    print(f"  V2:          {v2_train['mean_reward']:,.1f} ({(v2_train['mean_reward']-baseline_mean)/baseline_mean*100:+.1f}%)")
    print(f"  V2 vs V1:    {v2_train['mean_reward']-v1_train['mean_reward']:+,.1f}")
    
    print("\nTEST SET PERFORMANCE:")
    print(f"  Baseline:    {baseline_mean:,.1f}")
    print(f"  V1:          {v1_test['mean_reward']:,.1f} ({(v1_test['mean_reward']-baseline_mean)/baseline_mean*100:+.1f}%)")
    print(f"  V2:          {v2_test['mean_reward']:,.1f} ({(v2_test['mean_reward']-baseline_mean)/baseline_mean*100:+.1f}%)")
    print(f"  V2 vs V1:    {v2_test['mean_reward']-v1_test['mean_reward']:+,.1f}")
    
    print("\nNMAP USAGE:")
    print(f"  Baseline:    100.0%")
    print(f"  V1 Train:    {v1_train['nmap_usage_pct']:.1f}%")
    print(f"  V1 Test:     {v1_test['nmap_usage_pct']:.1f}%")
    print(f"  V2 Train:    {v2_train['nmap_usage_pct']:.1f}%")
    print(f"  V2 Test:     {v2_test['nmap_usage_pct']:.1f}%")
    
    print("\nGENERALIZATION GAP:")
    v1_gap = v1_train['mean_reward'] - v1_test['mean_reward']
    v2_gap = v2_train['mean_reward'] - v2_test['mean_reward']
    print(f"  V1:          {v1_gap:,.1f}")
    print(f"  V2:          {v2_gap:,.1f}")
    print(f"  Improvement: {v1_gap-v2_gap:+,.1f}")
    
    # Verdict
    print("\n" + "="*80)
    print("VERDICT")
    print("="*80)
    
    target = baseline_mean * 1.05
    
    if v2_test['mean_reward'] >= target:
        print("\nSUCCESS! V2 beats baseline by >5% on test set")
        print(f"  Target:  {target:,.1f}")
        print(f"  V2 Test: {v2_test['mean_reward']:,.1f}")
    elif v2_test['mean_reward'] > v1_test['mean_reward']:
        print("\nIMPROVEMENT! V2 better than V1 but still below target")
        improvement = ((v2_test['mean_reward'] - v1_test['mean_reward']) / v1_test['mean_reward'] * 100)
        print(f"  V2 vs V1: +{improvement:.1f}%")
        print(f"  Still need: {target - v2_test['mean_reward']:,.1f} points to reach target")
    else:
        print("\nNO IMPROVEMENT. V2 not better than V1")
        print("Consider different approach")
    
    # Save
    results = {
        'baseline': baseline_mean,
        'v1': {'train': v1_train, 'test': v1_test},
        'v2': {'train': v2_train, 'test': v2_test},
        'timestamp': datetime.now().isoformat()
    }
    
    output_file = f"v1_vs_v2_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
