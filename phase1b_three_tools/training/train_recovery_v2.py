"""
PM Recovery: Iteration 2 - Optimized Training
Based on analysis findings:
- Lower entropy: 0.06 → 0.01 (force exploitation, increase nmap usage)
- More timesteps: 500k → 1M (better conditional learning)
- Lower learning rate: 3e-4 → 1e-4 (more careful updates)
"""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from envs.full_recon_env import FullReconEnv


def train_phase1b_recovery_v2():
    """
    Second iteration of PM recovery training with optimized hyperparameters
    """
    
    print("="*80)
    print("PHASE 1B RECOVERY: ITERATION 2 (OPTIMIZED)")
    print("="*80)
    print()
    
    # Configuration
    scenarios_file = "../data/phase1b_train_80_augmented.json"
    total_timesteps = 1_000_000  # Doubled from 500k
    
    print("CONFIGURATION:")
    print(f"  Dataset:        {scenarios_file}")
    print(f"  Scenarios:      80 (20 original + 60 augmented)")
    print(f"  Total steps:    {total_timesteps:,}")
    print(f"  Exposures/scen: {total_timesteps // 80:,}")
    print(f"  Expected time:  20-25 minutes")
    print()
    
    print("OPTIMIZATIONS (based on analysis):")
    print("  1. Entropy:     0.06 -> 0.01 (force exploitation)")
    print("  2. Timesteps:   500k -> 1M (2x learning)")
    print("  3. Learn rate:  3e-4 -> 1e-4 (careful updates)")
    print()
    
    print("EXPECTED IMPROVEMENTS:")
    print("  - Higher nmap usage (33% -> 80-100%)")
    print("  - Better training reward (3,784 -> 4,200+)")
    print("  - Better generalization (test reward 1,076 -> 3,500+)")
    print()
    
    # Create environment
    print("Creating environment...")
    def make_env():
        return FullReconEnv(scenarios_path=scenarios_file)
    
    env = DummyVecEnv([make_env])
    print("Environment ready!")
    print()
    
    # Model configuration (optimized based on analysis)
    model_config = {
        'learning_rate': 1e-4,      # More careful (was 3e-4)
        'n_steps': 512,              # Keep same
        'batch_size': 256,           # Keep same
        'n_epochs': 10,              # Keep same
        'gamma': 0.99,               # Keep same
        'gae_lambda': 0.95,          # Keep same
        'clip_range': 0.2,           # Keep same
        'ent_coef': 0.01,            # MUCH LOWER (was 0.06) - force exploitation!
        'vf_coef': 0.5,              # Keep same
        'max_grad_norm': 0.5,        # Keep same
        'tensorboard_log': './tensorboard_logs/',
        'verbose': 1,
        'device': 'cpu'
    }
    
    print("Model configuration:")
    for key, value in model_config.items():
        if key != 'tensorboard_log' and key != 'device':
            print(f"  {key:20s}: {value}")
    print(f"  tensorboard_log     : {model_config['tensorboard_log']}")
    print(f"  verbose             : {model_config['verbose']}")
    print(f"  device              : {model_config['device']}")
    print()
    
    # Create model
    print("Creating PPO model...")
    model = PPO(
        policy="MlpPolicy",
        env=env,
        **model_config
    )
    print("Model ready!")
    print()
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=50_000,
        save_path='./checkpoints_recovery_v2/',
        name_prefix='phase1b_recovery_v2'
    )
    
    print("="*80)
    print("STARTING TRAINING (ITERATION 2)")
    print("="*80)
    print()
    print(f"Training for {total_timesteps:,} timesteps...")
    print()
    print("Monitor with: tensorboard --logdir=./tensorboard_logs/")
    print()
    
    # Train
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
    model_path = "./outputs/phase1b_recovery_v2_final.zip"
    os.makedirs("./outputs", exist_ok=True)
    model.save(model_path)
    print(f"Model saved to: {model_path}")
    
    # Close environment
    env.close()
    
    print()
    print("Next: Evaluate on test set")
    print("  python evaluate_recovery.py --model phase1b_recovery_v2_final.zip")
    print()


if __name__ == "__main__":
    train_phase1b_recovery_v2()
