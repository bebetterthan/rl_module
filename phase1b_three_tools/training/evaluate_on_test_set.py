#!/usr/bin/env python3
"""
Evaluate V13 and V16 on NEW test set

Action 1.2: Compare generalization capability on unseen scenarios
"""
import sys
import json
import numpy as np
from pathlib import Path
from stable_baselines3 import PPO

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from envs.full_recon_env import FullReconEnv

def evaluate_model_on_test_set(
    model_path: str,
    model_name: str,
    test_scenarios_path: str,
    num_runs: int = 50
) -> dict:
    """
    Evaluate a trained model on test set
    
    Args:
        model_path: Path to saved model
        model_name: Name for display (V13, V16)
        test_scenarios_path: Path to test scenarios JSON
        num_runs: Number of evaluation runs
        
    Returns:
        dict: Evaluation statistics
    """
    print(f"\n{'='*80}")
    print(f"EVALUATING {model_name}")
    print(f"{'='*80}\n")
    
    # Load model
    print(f"Loading model from: {model_path}")
    model = PPO.load(model_path)
    
    # Create environment with test scenarios
    print(f"Loading test scenarios from: {test_scenarios_path}")
    env = FullReconEnv(scenarios_path=test_scenarios_path)
    
    print(f"Running {num_runs} evaluation episodes...")
    print()
    
    all_rewards = []
    all_lengths = []
    nmap_usage = []
    skip_usage = []
    
    for run in range(num_runs):
        obs, info = env.reset()
        done = False
        episode_reward = 0.0
        episode_length = 0
        used_nmap = False
        used_skip = False
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            episode_reward += reward
            episode_length += 1
            
            # Track action usage
            if action in [6, 7, 8]:  # Nmap actions
                used_nmap = True
            elif action == 9:  # Skip action
                used_skip = True
            
            done = terminated or truncated
        
        all_rewards.append(episode_reward)
        all_lengths.append(episode_length)
        nmap_usage.append(1.0 if used_nmap else 0.0)
        skip_usage.append(1.0 if used_skip else 0.0)
        
        if (run + 1) % 10 == 0:
            print(f"Progress: {run + 1}/{num_runs} episodes completed")
    
    # Calculate statistics
    rewards_array = np.array(all_rewards)
    mean_reward = np.mean(rewards_array)
    std_reward = np.std(rewards_array)
    median_reward = np.median(rewards_array)
    min_reward = np.min(rewards_array)
    max_reward = np.max(rewards_array)
    ci_lower = mean_reward - 1.96 * (std_reward / np.sqrt(num_runs))
    ci_upper = mean_reward + 1.96 * (std_reward / np.sqrt(num_runs))
    
    nmap_pct = np.mean(nmap_usage) * 100
    skip_pct = np.mean(skip_usage) * 100
    
    stats = {
        "model_name": model_name,
        "model_path": model_path,
        "num_runs": num_runs,
        "mean": float(mean_reward),
        "std": float(std_reward),
        "median": float(median_reward),
        "min": float(min_reward),
        "max": float(max_reward),
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "nmap_usage_pct": float(nmap_pct),
        "skip_usage_pct": float(skip_pct),
        "all_rewards": [float(r) for r in all_rewards]
    }
    
    print()
    print(f"{'='*80}")
    print(f"{model_name} TEST SET RESULTS:")
    print(f"{'='*80}")
    print(f"  Mean Reward: {mean_reward:.1f} ± {std_reward:.1f}")
    print(f"  Median: {median_reward:.1f}")
    print(f"  Range: [{min_reward:.1f}, {max_reward:.1f}]")
    print(f"  95% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
    print(f"  Nmap Usage: {nmap_pct:.1f}%")
    print(f"  Skip Usage: {skip_pct:.1f}%")
    print()
    
    return stats

def compare_models(v13_stats: dict, v16_stats: dict, baseline_stats: dict):
    """Compare V13 and V16 performance"""
    print("\n" + "="*80)
    print("📊 MODEL COMPARISON ON TEST SET")
    print("="*80)
    print()
    
    print("PERFORMANCE:")
    print(f"  V13: {v13_stats['mean']:.1f} ± {v13_stats['std']:.1f}")
    print(f"  V16: {v16_stats['mean']:.1f} ± {v16_stats['std']:.1f}")
    print(f"  Hardcoded Baseline: {baseline_stats['mean']:.1f} ± {baseline_stats['std']:.1f}")
    print()
    
    # Improvement calculations
    v13_vs_baseline = ((v13_stats['mean'] / baseline_stats['mean']) - 1) * 100
    v16_vs_baseline = ((v16_stats['mean'] / baseline_stats['mean']) - 1) * 100
    v13_vs_v16 = ((v13_stats['mean'] / v16_stats['mean']) - 1) * 100
    
    print("IMPROVEMENT vs BASELINE:")
    print(f"  V13: {v13_vs_baseline:+.1f}%")
    print(f"  V16: {v16_vs_baseline:+.1f}%")
    print()
    
    print("V13 vs V16:")
    print(f"  V13 advantage: {v13_vs_v16:+.1f}%")
    print()
    
    # Statistical significance
    print("STATISTICAL SIGNIFICANCE:")
    
    # Check if V13 is outside baseline CI
    v13_significant = (v13_stats['mean'] > baseline_stats['ci_95_upper']) or \
                     (v13_stats['mean'] < baseline_stats['ci_95_lower'])
    
    v16_significant = (v16_stats['mean'] > baseline_stats['ci_95_upper']) or \
                     (v16_stats['mean'] < baseline_stats['ci_95_lower'])
    
    print(f"  V13 vs Baseline: {'✅ SIGNIFICANT' if v13_significant else '⚠️ NOT significant'}")
    print(f"  V16 vs Baseline: {'✅ SIGNIFICANT' if v16_significant else '⚠️ NOT significant'}")
    print()
    
    # Behavioral analysis
    print("BEHAVIORAL PATTERNS:")
    print(f"  V13 Nmap Usage: {v13_stats['nmap_usage_pct']:.1f}%")
    print(f"  V16 Nmap Usage: {v16_stats['nmap_usage_pct']:.1f}%")
    print(f"  Baseline Nmap Usage: {baseline_stats['nmap_usage_pct']:.1f}%")
    print()
    
    # Decision
    print("="*80)
    print("🎯 FINAL DECISION:")
    print("="*80)
    print()
    
    if v13_stats['mean'] > v16_stats['mean']:
        winner = "V13"
        advantage = v13_vs_v16
    else:
        winner = "V16"
        advantage = -v13_vs_v16
    
    print(f"✅ SELECT {winner} as final Phase 1B model")
    print(f"   Advantage: +{abs(advantage):.1f}% over alternative")
    
    if v13_significant or v16_significant:
        print(f"   Statistical significance: ✅ YES (beats baseline)")
    else:
        print(f"   Statistical significance: ⚠️ NO (within baseline range)")
    
    print()
    
    return winner

if __name__ == "__main__":
    print("\n🎯 ACTION 1.2: TEST SET EVALUATION")
    print("="*80)
    print()
    
    # Paths
    test_scenarios = "../data/phase1b_evaluation_test.json"
    
    # Find best V13 and V16 models
    outputs_dir = Path("../outputs")
    
    # V13 model (look for phase1b_run with V13 in name)
    v13_models = list(outputs_dir.glob("**/best_model.zip"))
    # For now, use the most recent one - you may need to specify exact path
    
    if not v13_models:
        print("❌ Could not find V13 model!")
        print("Please specify the path to V13 best_model.zip")
        sys.exit(1)
    
    # Load fixed baseline for comparison
    with open('FIXED_BASELINE_HARDCODED.json', 'r') as f:
        baseline_stats = json.load(f)
    
    print("⚠️  Model selection:")
    print("    Please provide paths to V13 and V16 models")
    print("    Or update this script with correct paths")
    print()
    
    # TODO: Update these paths with actual V13 and V16 model locations
    # v13_path = "../outputs/phase1b_v13_XXXXX/best_model.zip"
    # v16_path = "../outputs/phase1b_v16_XXXXX/best_model.zip"
    
    # For now, list available models
    print("Available model directories:")
    for output_dir in sorted(outputs_dir.iterdir()):
        if output_dir.is_dir():
            best_model = output_dir / "best_model.zip"
            if best_model.exists():
                print(f"  - {output_dir.name}")
    
    print()
    print("Please update evaluate_on_test_set.py with correct model paths")
    print("Then run again to complete Action 1.2")
