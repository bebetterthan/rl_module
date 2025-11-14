# 🏆 Best Models Archive

This folder contains the best performing RL models from each phase.

## 📁 Structure

```
best_models/
├── phase1a_best/          # Phase 1A: 2-Tool Sequential (Subfinder + HTTPX)
├── phase1b_v13_best/      # Phase 1B: 3-Tool Sequential (V13 - BEST!)
└── README.md              # This file
```

## 🎯 Model Details

### Phase 1A: Two-Tool Sequential Workflow

**Path**: `phase1a_best/`
**Source**: `run_20251113_034834`
**Training**: 100k steps (~5-10 minutes)

**Performance**:

- Best evaluation: 570.01 reward
- Final evaluation: 224.83 reward
- Tools: Subfinder + HTTPX (6 action space)
- State space: 20 dimensions

**Description**:
Learned basic 2-tool sequential workflow for subdomain discovery and HTTP probing. Successfully demonstrated tool selection capability.

---

### Phase 1B V13: Three-Tool Conditional Intelligence (🥇 BEST!)

**Path**: `phase1b_v13_best/`
**Source**: `phase1b_run_20251113_182956`
**Training**: 150k steps (~6-10 hours)

**Performance**:

- **Agent Reward**: 4321 ⭐
- **Baseline (Hardcoded)**: 3636
- **Improvement**: +18.8% ✅
- **Nmap Usage**: 65% (optimal!)
- **Variance**: ±1700

**Metrics**:

- Mean subdomains: 10.9
- Mean endpoints: 8.0
- Mean ports: 3.15
- Mean services: 1.1
- Episode length: 3.0 actions

**Why V13 is Best**:

1. ✅ Highest evaluation reward (4321) among all versions (V1-V16)
2. ✅ Optimal nmap usage (65%) - perfect balance
3. ✅ Beats hardcoded baseline significantly (+18.8%)
4. ✅ Stable training with positive-only rewards
5. ✅ Demonstrated conditional learning (WHEN to use nmap)

**Description**:
This is the pinnacle of Phase 1B training. V13 achieved the perfect balance of:

- **Strategic Intelligence**: Learned WHEN to use nmap (65% usage on infrastructure targets)
- **Efficiency**: Avoided unnecessary nmap scans on web-only targets
- **Performance**: Beat all baselines and subsequent versions (V14-V16)

**Reward Function (V13)**:

- Discovery rewards: Subdomains (43), Endpoints (32), Ports (65), Services (108)
- Completion bonuses: Coverage-based (216-648)
- Strategic bonus: 3-tool workflow (+2000)
- Efficiency bonus: Time-based optimization
- All positive, no penalties!

**Files Included**:

- `final_model.zip` - Final trained PPO model (0.2 MB)
- `best_model/` - Best model during training
- `vec_normalize_stats.pkl` - VecNormalize statistics for stable inference
- `results.json` - Evaluation results on 20 test scenarios
- `tensorboard/` - Training metrics and logs
- `checkpoints/` - Model checkpoints every 25k steps
- `eval_logs/` - Evaluation data (evaluations.npz)

---

## 🚀 Usage

### Loading Phase 1A Model

```python
from stable_baselines3 import PPO

# Load model
model = PPO.load("best_models/phase1a_best/final_model.zip")

# Use for inference
obs = env.reset()
action, _states = model.predict(obs, deterministic=True)
```

### Loading Phase 1B V13 Model (Recommended!)

```python
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import VecNormalize, DummyVecEnv
import pickle

# Load VecNormalize stats
with open("best_models/phase1b_v13_best/vec_normalize_stats.pkl", "rb") as f:
    vec_normalize_stats = pickle.load(f)

# Setup environment with normalization
env = DummyVecEnv([lambda: YourEnv()])
env = VecNormalize(env, norm_obs=True, norm_reward=False, clip_obs=10.0)
env.obs_rms = vec_normalize_stats['obs_rms']
env.ret_rms = vec_normalize_stats['ret_rms']

# Load model
model = PPO.load("best_models/phase1b_v13_best/final_model.zip")

# Use for inference
obs = env.reset()
action, _states = model.predict(obs, deterministic=True)
```

---

## 📊 Comparison

| Metric             | Phase 1A             | Phase 1B V13               |
| ------------------ | -------------------- | -------------------------- |
| **Tools**          | 2 (Subfinder, HTTPX) | 3 (Subfinder, HTTPX, Nmap) |
| **Actions**        | 6                    | 9                          |
| **State Dims**     | 20                   | 40                         |
| **Training Steps** | 100k                 | 150k                       |
| **Best Reward**    | 570                  | 4321                       |
| **Complexity**     | Sequential workflow  | Conditional intelligence   |
| **Key Learning**   | Tool selection       | WHEN to use tools          |

---

## 🎓 Key Learnings

### Phase 1A Success Factors:

1. Positive-dominant reward function prevented reward hacking
2. VecNormalize critical for stable training
3. High exploration (ent_coef 0.05) enabled discovery
4. Action masking simplified learning

### Phase 1B V13 Success Factors:

1. **V13 reward structure** found optimal balance
2. **65% nmap usage** is the sweet spot (not too aggressive, not too conservative)
3. **Strategic bonus** (+2000 for 3-tool workflow) raised performance ceiling
4. **Balanced discovery rewards** maintained stability
5. **No penalties** encouraged exploration without fear

### Why Later Versions (V14-V16) Failed:

- V14: Too aggressive (70% nmap), over-optimization
- V15: Unstable reward structure caused regression
- V16: Better training metrics but worse evaluation

**Lesson**: More reward ≠ Better performance (non-convex optimization)

---

## 🔄 Phase 2 Integration Plan

V13 will serve as the **foundation** for Phase 2: Vulnerability Scanning Layer

**Transfer Learning Strategy**:

1. Use V13 model as starting point
2. Freeze Phase 1 layers (Subfinder, HTTPX, Nmap decisions)
3. Add Phase 2 layers (Nuclei vulnerability scanning)
4. Fine-tune on expanded state space

**Why V13 for Phase 2**:

- Proven stability and performance
- Optimal strategic behavior (conditional tool usage)
- Strong baseline for building advanced capabilities
- Comprehensive target enumeration → perfect input for vuln scanning

---

## 📝 Notes

- Models saved on: November 15, 2025
- Training completed: November 13, 2025
- All models trained on: 20 diverse scenarios (5 web-only, 8 infrastructure, 7 hybrid)
- Hardware: Laptop (GTX 1650 Ti, 16GB RAM)
- Framework: Stable-Baselines3 (PPO algorithm)

---

## 🏗️ Next Steps (Phase 2)

**Immediate Actions**:

1. ✅ Archive best models (DONE!)
2. 🔄 Study Nuclei integration requirements
3. 🔄 Design Phase 2 state space (40 → 60+ dimensions)
4. 🔄 Plan reward function for vulnerability detection
5. 🔄 Create Phase 2 environment (full_recon_vuln_env.py)

**Phase 2 Goals**:

- Integrate Nuclei vulnerability scanner
- Learn WHEN to scan for vulnerabilities (based on Phase 1 findings)
- Achieve >30% improvement over simple "always scan" baseline
- Maintain execution efficiency (<5 minutes per target)

---

**Maintained by**: @bebetterthan
**Last Updated**: November 15, 2025
