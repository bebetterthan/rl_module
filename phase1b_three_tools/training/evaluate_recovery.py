"""
PM Recovery Evaluation Script
Evaluates the trained recovery model on test set (25 scenarios)
Compares against baseline (4129.6)
"""

import os
import sys
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
from scipy import stats

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from envs.full_recon_env import FullReconEnv


def load_baseline_stats(baseline_file: str = "FIXED_BASELINE_80scenarios.json") -> Dict:
    """Load baseline statistics from file"""
    with open(baseline_file, 'r') as f:
        return json.load(f)


def evaluate_model_on_test_set(
    model_path: str,
    test_scenarios_file: str,
    n_episodes: int = 50
) -> Dict:
    """
    Evaluate trained model on test set
    
    Args:
        model_path: Path to trained model
        test_scenarios_file: Path to test scenarios JSON
        n_episodes: Number of episodes to run
    
    Returns:
        Dictionary with evaluation results
    """
    print(f"\n{'='*80}")
    print("PM RECOVERY: TEST SET EVALUATION")
    print(f"{'='*80}\n")
    
    print(f"Model: {model_path}")
    print(f"Test scenarios: {test_scenarios_file}")
    print(f"Episodes: {n_episodes}")
    
    # Load model
    print("\nLoading model...")
    model = PPO.load(model_path)
    print("Model loaded!")
    
    # Create environment
    print("\nCreating environment...")
    def make_env():
        return FullReconEnv(scenarios_path=test_scenarios_file)
    
    env = DummyVecEnv([make_env])
    print("Environment ready!")
    
    # Run evaluation
    print(f"\nRunning {n_episodes} episodes...")
    all_rewards = []
    all_lengths = []
    nmap_usage_count = 0
    action_counts = {i: 0 for i in range(9)}  # Track all actions
    
    for episode in range(n_episodes):
        obs = env.reset()
        episode_reward = 0
        episode_length = 0
        done = False
        
        while not done:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            
            episode_reward += reward[0]
            episode_length += 1
            
            # Track action usage
            action_counts[action[0]] += 1
            
            # Track nmap usage (actions 6, 7, 8)
            if action[0] in [6, 7, 8]:
                nmap_usage_count += 1
        
        all_rewards.append(episode_reward)
        all_lengths.append(episode_length)
        
        if (episode + 1) % 10 == 0:
            print(f"  Completed {episode + 1}/{n_episodes} episodes...")
    
    env.close()
    
    # Calculate statistics
    rewards_array = np.array(all_rewards)
    mean_reward = np.mean(rewards_array)
    std_reward = np.std(rewards_array)
    median_reward = np.median(rewards_array)
    min_reward = np.min(rewards_array)
    max_reward = np.max(rewards_array)
    
    # 95% confidence interval
    ci_lower = mean_reward - 1.96 * (std_reward / np.sqrt(n_episodes))
    ci_upper = mean_reward + 1.96 * (std_reward / np.sqrt(n_episodes))
    
    # Behavioral stats
    mean_length = np.mean(all_lengths)
    total_actions = sum(action_counts.values())
    nmap_usage_pct = (nmap_usage_count / total_actions * 100) if total_actions > 0 else 0
    
    results = {
        'model_path': model_path,
        'test_scenarios_file': test_scenarios_file,
        'n_episodes': n_episodes,
        'timestamp': datetime.now().isoformat(),
        'statistics': {
            'mean_reward': float(mean_reward),
            'std_reward': float(std_reward),
            'median_reward': float(median_reward),
            'min_reward': float(min_reward),
            'max_reward': float(max_reward),
            'ci_95_lower': float(ci_lower),
            'ci_95_upper': float(ci_upper)
        },
        'behavioral': {
            'mean_episode_length': float(mean_length),
            'nmap_usage_pct': float(nmap_usage_pct),
            'action_distribution': {k: int(v) for k, v in action_counts.items()}
        },
        'all_rewards': [float(r) for r in all_rewards]
    }
    
    return results


def compare_to_baseline(model_results: Dict, baseline_stats: Dict) -> Dict:
    """
    Compare model performance to baseline
    
    Args:
        model_results: Model evaluation results
        baseline_stats: Baseline statistics
    
    Returns:
        Comparison statistics
    """
    model_mean = model_results['statistics']['mean_reward']
    model_std = model_results['statistics']['std_reward']
    model_n = model_results['n_episodes']
    
    baseline_mean = baseline_stats['statistics']['mean_reward']
    baseline_std = baseline_stats['statistics']['std_reward']
    baseline_n = baseline_stats['runs']
    
    # Calculate improvement
    absolute_diff = model_mean - baseline_mean
    relative_diff_pct = (absolute_diff / baseline_mean * 100)
    
    # T-test for significance
    # Using Welch's t-test (doesn't assume equal variances)
    model_rewards = np.array(model_results['all_rewards'])
    baseline_rewards = np.array(baseline_stats['all_rewards'])
    
    t_stat, p_value = stats.ttest_ind(model_rewards, baseline_rewards, equal_var=False)
    
    # Effect size (Cohen's d)
    pooled_std = np.sqrt((model_std**2 + baseline_std**2) / 2)
    cohens_d = absolute_diff / pooled_std if pooled_std > 0 else 0
    
    # Determine significance
    is_significant = p_value < 0.05
    
    # Determine success
    target_reward = baseline_mean * 1.05  # 5% improvement target
    meets_target = model_mean >= target_reward
    
    comparison = {
        'model_mean': float(model_mean),
        'baseline_mean': float(baseline_mean),
        'absolute_difference': float(absolute_diff),
        'relative_difference_pct': float(relative_diff_pct),
        'target_reward': float(target_reward),
        'meets_target': meets_target,
        'statistical_test': {
            't_statistic': float(t_stat),
            'p_value': float(p_value),
            'is_significant': is_significant,
            'alpha': 0.05
        },
        'effect_size': {
            'cohens_d': float(cohens_d),
            'interpretation': (
                'large' if abs(cohens_d) >= 0.8 else
                'medium' if abs(cohens_d) >= 0.5 else
                'small' if abs(cohens_d) >= 0.2 else
                'negligible'
            )
        }
    }
    
    return comparison


def print_evaluation_summary(model_results: Dict, comparison: Dict):
    """Print comprehensive evaluation summary"""
    
    print(f"\n{'='*80}")
    print("EVALUATION RESULTS")
    print(f"{'='*80}\n")
    
    # Model performance
    stats = model_results['statistics']
    print("MODEL PERFORMANCE (Test Set):")
    print(f"  Mean Reward:     {stats['mean_reward']:.1f} ± {stats['std_reward']:.1f}")
    print(f"  Median Reward:   {stats['median_reward']:.1f}")
    print(f"  Min/Max:         {stats['min_reward']:.1f} / {stats['max_reward']:.1f}")
    print(f"  95% CI:         [{stats['ci_95_lower']:.1f}, {stats['ci_95_upper']:.1f}]")
    
    # Behavioral
    behavioral = model_results['behavioral']
    print(f"\n  Mean Episode Length: {behavioral['mean_episode_length']:.1f} steps")
    print(f"  Nmap Usage:          {behavioral['nmap_usage_pct']:.1f}%")
    
    # Comparison to baseline
    print(f"\n{'='*80}")
    print("COMPARISON TO BASELINE")
    print(f"{'='*80}\n")
    
    print(f"Model Mean:      {comparison['model_mean']:.1f}")
    print(f"Baseline Mean:   {comparison['baseline_mean']:.1f}")
    print(f"Difference:      {comparison['absolute_difference']:+.1f} ({comparison['relative_difference_pct']:+.1f}%)")
    print(f"Target (5%):     {comparison['target_reward']:.1f}")
    print(f"Meets Target:    {'YES' if comparison['meets_target'] else 'NO'}")
    
    # Statistical significance
    print(f"\nSTATISTICAL SIGNIFICANCE:")
    stat = comparison['statistical_test']
    print(f"  t-statistic:  {stat['t_statistic']:.3f}")
    print(f"  p-value:      {stat['p_value']:.4f}")
    print(f"  Significant:  {'YES (p < 0.05)' if stat['is_significant'] else 'NO (p >= 0.05)'}")
    
    # Effect size
    print(f"\nEFFECT SIZE:")
    effect = comparison['effect_size']
    print(f"  Cohen's d:    {effect['cohens_d']:.3f}")
    print(f"  Magnitude:    {effect['interpretation'].upper()}")
    
    # Final verdict
    print(f"\n{'='*80}")
    print("FINAL VERDICT")
    print(f"{'='*80}\n")
    
    if comparison['meets_target'] and stat['is_significant']:
        print("SUCCESS! Model beats baseline by >5% with statistical significance.")
        print("Phase 1B recovery achieved!")
    elif comparison['meets_target']:
        print("PARTIAL SUCCESS. Model meets target but not statistically significant.")
        print("Consider more training or evaluation episodes.")
    elif comparison['relative_difference_pct'] > 0:
        print("MARGINAL IMPROVEMENT. Model better than baseline but <5%.")
        print("Consider hyperparameter tuning or more training.")
    else:
        print("UNSUCCESSFUL. Model does not beat baseline.")
        print("Data expansion alone insufficient. Consider:")
        print("  - Different hyperparameters")
        print("  - More training timesteps")
        print("  - Alternative approaches")
        print("\nNOTE: Negative results are still valuable research!")


def main():
    """Main evaluation workflow"""
    
    # Configuration
    model_path = "./outputs/phase1b_recovery_final.zip"
    test_scenarios_file = "../data/phase1b_test.json"
    baseline_file = "FIXED_BASELINE_80scenarios.json"
    n_episodes = 50  # 2 episodes per test scenario (25 scenarios)
    
    # Check files exist
    if not os.path.exists(model_path):
        print(f"ERROR: Model not found: {model_path}")
        return
    
    if not os.path.exists(test_scenarios_file):
        print(f"ERROR: Test scenarios not found: {test_scenarios_file}")
        return
    
    if not os.path.exists(baseline_file):
        print(f"ERROR: Baseline not found: {baseline_file}")
        return
    
    # Load baseline
    print("Loading baseline statistics...")
    baseline_stats = load_baseline_stats(baseline_file)
    print(f"Baseline: {baseline_stats['statistics']['mean_reward']:.1f} ± {baseline_stats['statistics']['std_reward']:.1f}")
    
    # Evaluate model
    model_results = evaluate_model_on_test_set(
        model_path=model_path,
        test_scenarios_file=test_scenarios_file,
        n_episodes=n_episodes
    )
    
    # Compare to baseline
    comparison = compare_to_baseline(model_results, baseline_stats)
    
    # Print summary
    print_evaluation_summary(model_results, comparison)
    
    # Save results
    output_file = f"test_set_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    full_results = {
        'model_results': model_results,
        'baseline_stats': baseline_stats,
        'comparison': comparison
    }
    
    with open(output_file, 'w') as f:
        json.dump(full_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
