"""
PM Recovery: Iteration 3 - Aggressive Reward Engineering
Changes from V2:
- TRIPLED strategic bonuses for nmap usage (1500 -> 4500 for service)
- TRIPLED penalties for skipping nmap on infra (-400 -> -1200)
- DOUBLED 3-tool workflow bonus (2600 -> 5200)
- TRIPLED efficiency/consistency bonuses
- Added penalty for skipping nmap on hybrid scenarios (-800)
- Reduced web-only skip bonus (1000 -> 800) to balance

Config same as V2 (working well):
- Entropy: 0.01 (force exploitation)
- Timesteps: 1M (sufficient learning)
- Learning rate: 1e-4 (careful updates)
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from envs.full_recon_env import FullReconEnv


def train_phase1b_recovery_v3():
    """
    Third iteration: Aggressive reward engineering to force nmap usage
    """
    
    print("="*80)
    print("PHASE 1B RECOVERY: ITERATION 3 (AGGRESSIVE REWARD ENGINEERING)")
    print("="*80)
    print()
    
    # Configuration
    scenarios_file = "../data/phase1b_train_80_augmented.json"
    total_timesteps = 1_000_000
    
    print("CONFIGURATION:")
    print(f"  Dataset:        {scenarios_file}")
    print(f"  Scenarios:      80 (20 original + 60 augmented)")
    print(f"  Total steps:    {total_timesteps:,}")
    print(f"  Exposures/scen: {total_timesteps // 80:,}")
    print(f"  Expected time:  20-25 minutes")
    print()
    
    print("REWARD ENGINEERING (from V16 to V17):")
    print("  1. Nmap service bonus:     1500 -> 4500 (TRIPLED)")
    print("  2. Nmap full bonus:        1200 -> 3600 (TRIPLED)")
    print("  3. Skip nmap penalty:      -400 -> -1200 (TRIPLED)")
    print("  4. 3-tool workflow:        2600 -> 5200 (DOUBLED)")
    print("  5. Hybrid nmap:            1200 -> 3600 (TRIPLED)")
    print("  6. Efficiency bonus:       144 -> 432 (TRIPLED)")
    print("  7. New hybrid skip penalty: -800 (NEW)")
    print()
    
    print("EXPECTED IMPROVEMENTS:")
    print("  - Nmap usage: 20% -> 60-80% (much higher!)")
    print("  - Test reward: 1078 -> 2500-3500 (2-3x better)")
    print("  - Training reward: ~3800 -> ~4500 (closer to baseline)")
    print()
    
    # Create environment
    print("Creating environment with V17 reward function...")
    def make_env():
        return FullReconEnv(scenarios_path=scenarios_file)
    
    env = DummyVecEnv([make_env])
    print("Environment ready with AGGRESSIVE nmap incentives!")
    print()
    
    # Model configuration (same as V2 - proven to work)
    model_config = {
        'learning_rate': 1e-4,
        'n_steps': 512,
        'batch_size': 256,
        'n_epochs': 10,
        'gamma': 0.99,
        'gae_lambda': 0.95,
        'clip_range': 0.2,
        'ent_coef': 0.01,  # Keep low entropy (force exploitation)
        'vf_coef': 0.5,
        'max_grad_norm': 0.5,
        'tensorboard_log': './tensorboard_logs/',
        'verbose': 1,
        'device': 'cpu'
    }
    
    print("Model configuration (same as V2):")
    for key, value in model_config.items():
        if key not in ['tensorboard_log', 'device', 'verbose']:
            print(f"  {key:20s}: {value}")
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
        save_path='./checkpoints_recovery_v3/',
        name_prefix='phase1b_recovery_v3'
    )
    
    print("="*80)
    print("STARTING TRAINING (ITERATION 3)")
    print("="*80)
    print()
    print(f"Training for {total_timesteps:,} timesteps...")
    print()
    print("Monitor with: tensorboard --logdir=./tensorboard_logs/")
    print()
    print("KEY HYPOTHESIS:")
    print("  Tripled nmap rewards + penalties will force model")
    print("  to use nmap consistently on infrastructure targets")
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
    model_path = "./outputs/phase1b_recovery_v3_final.zip"
    os.makedirs("./outputs", exist_ok=True)
    model.save(model_path)
    print(f"Model saved to: {model_path}")
    
    # Close environment
    env.close()
    
    print()
    print("Next: python test_v3_simple.py")
    print()


if __name__ == "__main__":
    train_phase1b_recovery_v3()
