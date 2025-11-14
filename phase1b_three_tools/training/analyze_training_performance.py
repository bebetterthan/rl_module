"""
Deep Analysis: Model Performance on Training Set vs Test Set
Check if model overfitted to training set or failed to learn entirely
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.full_recon_env import FullReconEnv


def evaluate_on_dataset(
    model_path: str,
    scenarios_file: str,
    dataset_name: str,
    n_episodes: int = 50
) -> Dict:
    """Evaluate model on specific dataset"""
    
    print(f"\n{'='*80}")
    print(f"EVALUATING ON {dataset_name.upper()}")
    print(f"{'='*80}\n")
    
    print(f"Dataset: {scenarios_file}")
    print(f"Episodes: {n_episodes}")
    
    # Load model
    print("\nLoading model...")
    model = PPO.load(model_path)
    
    # Create environment
    def make_env():
        return FullReconEnv(scenarios_path=scenarios_file)
    env = DummyVecEnv([make_env])
    
    # Run evaluation
    print(f"Running {n_episodes} episodes...")
    all_rewards = []
    all_lengths = []
    nmap_usage_count = 0
    total_actions = 0
    
    # Track actions per scenario type
    action_counts = {i: 0 for i in range(9)}
    scenario_rewards = {}  # Track rewards per scenario
    
    for episode in range(n_episodes):
        obs = env.reset()
        episode_reward = 0
        episode_length = 0
        done = False
        
        # Get current scenario ID from environment
        current_scenario_id = env.envs[0].current_scenario['id'] if hasattr(env.envs[0], 'current_scenario') else f"ep_{episode}"
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            
            episode_reward += reward[0]
            episode_length += 1
            total_actions += 1
            
            # Track actions
            action_counts[action[0]] += 1
            if action[0] in [6, 7, 8]:  # nmap actions
                nmap_usage_count += 1
        
        all_rewards.append(episode_reward)
        all_lengths.append(episode_length)
        
        # Store reward per scenario
        if current_scenario_id not in scenario_rewards:
            scenario_rewards[current_scenario_id] = []
        scenario_rewards[current_scenario_id].append(episode_reward)
        
        if (episode + 1) % 10 == 0:
            print(f"  {episode + 1}/{n_episodes} episodes...")
    
    env.close()
    
    # Calculate statistics
    rewards_array = np.array(all_rewards)
    mean_reward = np.mean(rewards_array)
    std_reward = np.std(rewards_array)
    median_reward = np.median(rewards_array)
    
    nmap_usage_pct = (nmap_usage_count / total_actions * 100) if total_actions > 0 else 0
    mean_length = np.mean(all_lengths)
    
    # Scenario-wise statistics
    scenario_stats = {}
    for scenario_id, rewards in scenario_rewards.items():
        scenario_stats[scenario_id] = {
            'mean': float(np.mean(rewards)),
            'std': float(np.std(rewards)),
            'count': len(rewards)
        }
    
    results = {
        'dataset_name': dataset_name,
        'scenarios_file': scenarios_file,
        'n_episodes': n_episodes,
        'statistics': {
            'mean_reward': float(mean_reward),
            'std_reward': float(std_reward),
            'median_reward': float(median_reward),
            'min_reward': float(np.min(rewards_array)),
            'max_reward': float(np.max(rewards_array))
        },
        'behavioral': {
            'mean_episode_length': float(mean_length),
            'nmap_usage_pct': float(nmap_usage_pct),
            'action_distribution': {k: int(v) for k, v in action_counts.items()}
        },
        'scenario_stats': scenario_stats,
        'all_rewards': [float(r) for r in all_rewards]
    }
    
    return results


def compare_datasets(training_results: Dict, test_results: Dict, baseline_stats: Dict):
    """Compare performance across datasets"""
    
    print(f"\n{'='*80}")
    print("COMPARATIVE ANALYSIS")
    print(f"{'='*80}\n")
    
    train_mean = training_results['statistics']['mean_reward']
    test_mean = test_results['statistics']['mean_reward']
    baseline_mean = baseline_stats['statistics']['mean_reward']
    
    print("MEAN REWARDS:")
    print(f"  Training Set:  {train_mean:,.1f}")
    print(f"  Test Set:      {test_mean:,.1f}")
    print(f"  Baseline:      {baseline_mean:,.1f}")
    
    print("\nPERFORMANCE GAPS:")
    train_vs_baseline = train_mean - baseline_mean
    test_vs_baseline = test_mean - baseline_mean
    train_vs_test = train_mean - test_mean
    
    print(f"  Training vs Baseline: {train_vs_baseline:+,.1f} ({train_vs_baseline/baseline_mean*100:+.1f}%)")
    print(f"  Test vs Baseline:     {test_vs_baseline:+,.1f} ({test_vs_baseline/baseline_mean*100:+.1f}%)")
    print(f"  Training vs Test:     {train_vs_test:+,.1f} (generalization gap)")
    
    print("\nBEHAVIORAL COMPARISON:")
    print(f"  Nmap Usage:")
    print(f"    Training: {training_results['behavioral']['nmap_usage_pct']:.1f}%")
    print(f"    Test:     {test_results['behavioral']['nmap_usage_pct']:.1f}%")
    print(f"    Baseline: 100.0%")
    
    print(f"\n  Episode Length:")
    print(f"    Training: {training_results['behavioral']['mean_episode_length']:.1f} steps")
    print(f"    Test:     {test_results['behavioral']['mean_episode_length']:.1f} steps")
    print(f"    Baseline: 3.0 steps")
    
    # Diagnosis
    print(f"\n{'='*80}")
    print("DIAGNOSIS")
    print(f"{'='*80}\n")
    
    if train_mean < baseline_mean and test_mean < baseline_mean:
        print("LEARNING FAILURE")
        print("  Model failed to learn on both training and test sets")
        print("  Possible causes:")
        print("    - Reward function not aligned with optimal behavior")
        print("    - Exploration too high (entropy coefficient)")
        print("    - Training timesteps insufficient")
        print("    - Learning rate too high/low")
        print("\n  Recommended actions:")
        print("    1. Lower entropy coefficient (0.06 → 0.01-0.02)")
        print("    2. Increase timesteps (500k → 1M-2M)")
        print("    3. Check reward components alignment")
        
    elif train_mean >= baseline_mean and test_mean < baseline_mean:
        print("OVERFITTING")
        print("  Model learned training set but failed to generalize")
        print(f"  Generalization gap: {train_vs_test:,.1f}")
        print("  Possible causes:")
        print("    - Training set too different from test set")
        print("    - Model memorized training scenarios")
        print("    - Insufficient regularization")
        print("\n  Recommended actions:")
        print("    1. Increase entropy coefficient for more exploration")
        print("    2. Add more diverse training scenarios")
        print("    3. Use curriculum learning")
        
    elif train_mean >= baseline_mean and test_mean >= baseline_mean:
        print("SUCCESS")
        print("  Model learned effectively and generalizes well")
        
    else:
        print("ANOMALY")
        print("  Test performance better than training (unusual)")
        print("  May indicate lucky sampling or measurement issue")
    
    # Action distribution analysis
    print(f"\n{'='*80}")
    print("ACTION DISTRIBUTION ANALYSIS")
    print(f"{'='*80}\n")
    
    action_names = [
        "subfinder", "httpx_light", "httpx_full",
        "nmap_web_light", "nmap_web_full", "nmap_infra",
        "nmap_skip", "nmap_quick", "nmap_service"
    ]
    
    print("TRAINING SET:")
    for action_id, count in training_results['behavioral']['action_distribution'].items():
        pct = count / sum(training_results['behavioral']['action_distribution'].values()) * 100
        print(f"  {action_names[action_id]:20s}: {count:4d} ({pct:5.1f}%)")
    
    print("\nTEST SET:")
    for action_id, count in test_results['behavioral']['action_distribution'].items():
        pct = count / sum(test_results['behavioral']['action_distribution'].values()) * 100
        print(f"  {action_names[action_id]:20s}: {count:4d} ({pct:5.1f}%)")


def main():
    """Main analysis workflow"""
    
    model_path = "./outputs/phase1b_recovery_final.zip"
    train_scenarios = "../data/phase1b_train_80_augmented.json"
    test_scenarios = "../data/phase1b_test.json"
    baseline_file = "FIXED_BASELINE_80scenarios.json"
    
    # Check files
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found: {model_path}")
        return
    
    # Load baseline
    print("Loading baseline statistics...")
    with open(baseline_file, 'r') as f:
        baseline_stats = json.load(f)
    print(f"Baseline: {baseline_stats['statistics']['mean_reward']:.1f}")
    
    # Evaluate on training set
    training_results = evaluate_on_dataset(
        model_path=model_path,
        scenarios_file=train_scenarios,
        dataset_name="Training Set (80 scenarios)",
        n_episodes=50  # Sample from 80 scenarios
    )
    
    # Evaluate on test set
    test_results = evaluate_on_dataset(
        model_path=model_path,
        scenarios_file=test_scenarios,
        dataset_name="Test Set (5 scenarios)",
        n_episodes=50  # 10 episodes per test scenario
    )
    
    # Compare datasets
    compare_datasets(training_results, test_results, baseline_stats)
    
    # Save results
    output_file = f"training_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analysis_results = {
        'training_results': training_results,
        'test_results': test_results,
        'baseline_stats': baseline_stats,
        'timestamp': datetime.now().isoformat()
    }
    
    with open(output_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Analysis saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
