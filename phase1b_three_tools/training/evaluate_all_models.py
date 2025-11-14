#!/usr/bin/env python3
"""
Evaluate ALL trained models on test set to find best one

Action 1.2 Complete: Comprehensive model evaluation
"""
import sys
import json
import numpy as np
from pathlib import Path
from stable_baselines3 import PPO
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from envs.full_recon_env import FullReconEnv

def evaluate_single_model(model_path: Path, test_scenarios_path: str, num_runs: int = 30) -> dict:
    """Evaluate one model on test set"""
    try:
        # Load model
        model = PPO.load(str(model_path))
        
        # Create environment
        env = FullReconEnv(scenarios_path=test_scenarios_path)
        
        all_rewards = []
        nmap_usage = []
        
        for run in range(num_runs):
            obs, info = env.reset()
            done = False
            episode_reward = 0.0
            used_nmap = False
            
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                episode_reward += reward
                
                if action in [6, 7, 8]:
                    used_nmap = True
                
                done = terminated or truncated
            
            all_rewards.append(episode_reward)
            nmap_usage.append(1.0 if used_nmap else 0.0)
        
        rewards_array = np.array(all_rewards)
        
        return {
            "model_path": str(model_path),
            "model_dir": model_path.parent.name,
            "success": True,
            "mean": float(np.mean(rewards_array)),
            "std": float(np.std(rewards_array)),
            "median": float(np.median(rewards_array)),
            "min": float(np.min(rewards_array)),
            "max": float(np.max(rewards_array)),
            "nmap_usage_pct": float(np.mean(nmap_usage) * 100),
            "num_runs": num_runs
        }
    except Exception as e:
        return {
            "model_path": str(model_path),
            "model_dir": model_path.parent.name,
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("\n" + "="*80)
    print("ACTION 1.2: COMPREHENSIVE MODEL EVALUATION")
    print("="*80)
    print()
    
    # Setup
    outputs_dir = Path("../outputs")
    
    # Use existing test scenarios (already validated)
    test_scenarios = "../data/phase1b_test.json"  # Use existing 5 test scenarios
    
    # Find all models (search for best_model.zip in all subdirectories)
    model_paths = []
    for output_dir in outputs_dir.iterdir():
        if output_dir.is_dir():
            # Check for best_model/best_model.zip
            best_model_zip = output_dir / "best_model" / "best_model.zip"
            if best_model_zip.exists():
                model_paths.append(best_model_zip)
            else:
                # Check for best_model.zip directly
                best_model_zip = output_dir / "best_model.zip"
                if best_model_zip.exists():
                    model_paths.append(best_model_zip)
    
    if not model_paths:
        print("❌ No models found in outputs directory!")
        sys.exit(1)
    
    print(f"Found {len(model_paths)} trained models")
    print()
    
    # Load fixed baseline
    with open('FIXED_BASELINE_HARDCODED.json', 'r') as f:
        baseline_stats = json.load(f)
    
    print(f"Fixed Baseline: {baseline_stats['mean']:.1f} ± {baseline_stats['std']:.1f}")
    print(f"                95% CI: [{baseline_stats['ci_95_lower']:.1f}, {baseline_stats['ci_95_upper']:.1f}]")
    print()
    print("="*80)
    print()
    
    # Evaluate each model
    results = []
    for idx, model_path in enumerate(sorted(model_paths), 1):
        print(f"[{idx}/{len(model_paths)}] Evaluating {model_path.parent.name}...")
        
        result = evaluate_single_model(model_path, test_scenarios, num_runs=30)
        results.append(result)
        
        if result["success"]:
            improvement = ((result['mean'] / baseline_stats['mean']) - 1) * 100
            print(f"    Mean: {result['mean']:.1f} ± {result['std']:.1f}")
            print(f"    Improvement vs baseline: {improvement:+.1f}%")
            print(f"    Nmap usage: {result['nmap_usage_pct']:.1f}%")
        else:
            print(f"    ❌ FAILED: {result['error']}")
        print()
    
    # Filter successful results
    successful_results = [r for r in results if r["success"]]
    
    if not successful_results:
        print("❌ No models evaluated successfully!")
        sys.exit(1)
    
    # Sort by mean reward
    successful_results.sort(key=lambda x: x['mean'], reverse=True)
    
    # Display ranking
    print("="*80)
    print("MODEL RANKING (Test Set Performance)")
    print("="*80)
    print()
    
    for rank, result in enumerate(successful_results, 1):
        improvement = ((result['mean'] / baseline_stats['mean']) - 1) * 100
        
        # Check significance
        significant = result['mean'] > baseline_stats['ci_95_upper']
        
        print(f"{rank}. {result['model_dir']}")
        print(f"   Mean Reward: {result['mean']:.1f} ± {result['std']:.1f}")
        print(f"   Improvement: {improvement:+.1f}% vs baseline")
        print(f"   Nmap Usage: {result['nmap_usage_pct']:.1f}%")
        print(f"   Significant: {'YES' if significant else 'NO (within baseline CI)'}")
        print()
    
    # Select best model
    best_model = successful_results[0]
    
    print("="*80)
    print("BEST MODEL SELECTION")
    print("="*80)
    print()
    print(f"Model: {best_model['model_dir']}")
    print(f"Path: {best_model['model_path']}")
    print(f"Test Set Performance: {best_model['mean']:.1f} ± {best_model['std']:.1f}")
    print(f"Nmap Usage: {best_model['nmap_usage_pct']:.1f}%")
    
    improvement = ((best_model['mean'] / baseline_stats['mean']) - 1) * 100
    significant = best_model['mean'] > baseline_stats['ci_95_upper']
    
    print()
    print(f"Improvement vs Baseline: {improvement:+.1f}%")
    print(f"Statistical Significance: {'YES' if significant else 'NO'}")
    print()
    
    # Save results
    results_file = f"test_set_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    evaluation_report = {
        "evaluation_date": datetime.now().isoformat(),
        "test_scenarios": test_scenarios,
        "baseline_stats": baseline_stats,
        "models_evaluated": len(results),
        "successful_evaluations": len(successful_results),
        "results": successful_results,
        "best_model": best_model,
        "conclusion": {
            "model": best_model['model_dir'],
            "improvement_pct": improvement,
            "statistically_significant": significant,
            "nmap_usage": best_model['nmap_usage_pct']
        }
    }
    
    with open(results_file, 'w') as f:
        json.dump(evaluation_report, f, indent=2)
    
    print(f"Full results saved to: {results_file}")
    print()
    
    # Final verdict
    print("="*80)
    print("ACTION 1.2 COMPLETE!")
    print("="*80)
    print()
    
    if significant:
        print("Best model SIGNIFICANTLY beats baseline")
        print("Conditional learning is EFFECTIVE")
    else:
        print("Best model does NOT significantly beat baseline")
        print("RL learned conditional behavior but not better than heuristic")
    
    print()
    print("Next: Action 1.3 - Variance analysis per scenario type")
    print()
