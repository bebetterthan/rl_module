#!/usr/bin/env python3
"""
DAY 4: Training on 80 Augmented Scenarios
Quick 5-minute training run with optimized parameters
"""
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from envs.full_recon_env import FullReconEnv
import torch

def train_phase1b_recovery():
    """Train on 80 augmented scenarios"""
    
    print("\n" + "="*80)
    print("PHASE 1B RECOVERY: TRAINING ON 80 AUGMENTED SCENARIOS")
    print("="*80)
    print()
    
    # Configuration
    scenarios_file = "../data/phase1b_train_80_augmented.json"
    total_timesteps = 500_000  # 6,250 exposures per scenario
    
    print(f"Dataset: {scenarios_file}")
    print(f"Scenarios: 80 (20 original + 60 augmented)")
    print(f"Total timesteps: {total_timesteps:,}")
    print(f"Exposures per scenario: {total_timesteps // 80:,}")
    print(f"Expected training time: 5-6 minutes")
    print()
    
    # Create environment
    print("Creating environment...")
    
    def make_env():
        return FullReconEnv(scenarios_path=scenarios_file)
    
    env = DummyVecEnv([make_env])
    # Skip VecNormalize for now to avoid episode info issues
    # env = VecNormalize(env, norm_obs=True, norm_reward=False)
    
    print("Environment ready!")
    print()
    
    # Model configuration (based on V13 successful config)
    print("Model configuration:")
    model_config = {
        "policy": "MlpPolicy",
        "learning_rate": 3e-4,  # Conservative for larger dataset
        "n_steps": 512,
        "batch_size": 256,  # Larger batch for stability
        "n_epochs": 10,
        "gamma": 0.99,
        "gae_lambda": 0.95,
        "clip_range": 0.2,
        "ent_coef": 0.06,  # Slightly more exploration
        "vf_coef": 0.5,
        "max_grad_norm": 0.5,
        "tensorboard_log": "./tensorboard_logs/",
        "verbose": 1,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    }
    
    for key, value in model_config.items():
        if key != "policy":
            print(f"  {key:20s}: {value}")
    print()
    
    # Create model
    print("Creating PPO model...")
    model = PPO(env=env, **model_config)
    print("Model ready!")
    print()
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=50_000,
        save_path="./checkpoints_recovery/",
        name_prefix="phase1b_recovery"
    )
    
    # Train
    print("="*80)
    print("STARTING TRAINING")
    print("="*80)
    print()
    print("Monitor with: tensorboard --logdir=./tensorboard_logs/")
    print()
    
    model.learn(
        total_timesteps=total_timesteps,
        callback=[checkpoint_callback],
        progress_bar=True
    )
    
    print()
    print("="*80)
    print("TRAINING COMPLETE!")
    print("="*80)
    print()
    
    # Save final model
    model_path = "./outputs/phase1b_recovery_final"
    model.save(model_path)
    # env.save(f"{model_path}_vecnormalize.pkl")  # Skip for now
    
    print(f"Model saved to: {model_path}.zip")
    print(f"Normalization stats: {model_path}_vecnormalize.pkl")
    print()
    print("Next: Evaluate on test set (25 scenarios)")
    print()

if __name__ == "__main__":
    train_phase1b_recovery()
