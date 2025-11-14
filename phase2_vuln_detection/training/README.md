# 🎓 Phase 2 Training Guide

Complete guide for training Phase 2 vulnerability detection agent.

---

## 📋 Pre-Training Checklist

### 1. Environment Setup

```bash
# Verify Nuclei installation
nuclei -version

# Update templates
nuclei -update-templates

# Install Python dependencies
pip install -r requirements.txt

# Test Nuclei wrapper
python envs/nuclei_scanner.py
```

### 2. Generate Training Data

```bash
cd data
python generate_scenarios_phase2.py

# Verify scenarios
ls -lh phase2_train.json phase2_test.json
```

### 3. Run Baseline Tests

```bash
cd baselines
python test_all_baselines.py

# Expected output:
# Random: ~2800 ± 1800
# Always Scan: ~4200 ± 2400
# Smart Heuristic: ~4800 ± 2100
```

---

## 🚀 Training

### Start Training

```bash
cd training
python train_phase2_local.py
```

### Monitor Progress

```bash
# In separate terminal
tensorboard --logdir=../outputs --port=6006
# Open: http://localhost:6006
```

### Training Configuration

```yaml
# config_phase2.yaml
total_timesteps: 200000
learning_rate: 0.001
ent_coef: 0.05
n_steps: 512
batch_size: 128
n_epochs: 20
gamma: 0.99
```

---

## 📊 Monitoring

### Key Metrics to Watch

**1. Episode Reward (rollout/ep_rew_mean)**

- Target: Trending upward to >5500
- Phase 1B V13 baseline: 3630
- Phase 2 target: >5500 (50% increase)

**2. Nuclei Usage Rate**

- Target: 50-80%
- Too low (<40%): Not scanning enough
- Too high (>90%): Not learning to skip

**3. Vulnerability Detection**

- Critical vulns found per episode
- High-value target identification
- False positive rate

**4. Execution Time**

- Average: <600s per episode
- Efficiency trend should improve over time

---

## 🎯 Evaluation

### Run Evaluation

```bash
cd training
python evaluate_phase2.py --model ../outputs/phase2_run_LATEST/final_model.zip
```

### Expected Results (V14 Target)

```
Agent Performance:
  Mean Reward: 5500-7000
  Nuclei Usage: 50-80%
  Vulns Found: >80% of actual
  Execution Time: <600s

vs Baselines:
  vs Random: +100-150%
  vs Always Scan: +30-50%
  vs Heuristic: +15-30%
```

---

## 🔧 Troubleshooting

### Issue 1: Low Reward

**Symptoms**: Reward stuck around 3000-4000
**Causes**:

- Not using Nuclei enough
- Skipping high-value targets
- Reward function imbalance

**Solutions**:

- Increase vulnerability detection rewards
- Add more strategic bonuses
- Check Nuclei execution (mock mode?)

### Issue 2: High Nuclei Usage (>90%)

**Symptoms**: Agent scans everything
**Causes**:

- Skip action penalty too high
- Vulnerability rewards too attractive
- Not learning efficiency

**Solutions**:

- Increase skip bonus for web-only targets
- Add execution time penalties
- Reduce vulnerability rewards slightly

### Issue 3: Training Unstable

**Symptoms**: Reward variance high, no convergence
**Causes**:

- State space not normalized
- Learning rate too high
- Scenario diversity too high

**Solutions**:

- Check VecNormalize is applied
- Reduce learning rate to 0.0005
- Reduce scenario complexity

---

## 📈 Hyperparameter Tuning

### If Training Too Slow

```python
learning_rate: 0.002  # Up from 0.001
n_steps: 1024  # Up from 512
batch_size: 256  # Up from 128
```

### If Training Unstable

```python
learning_rate: 0.0005  # Down from 0.001
ent_coef: 0.03  # Down from 0.05
clip_range: 0.1  # Down from 0.2
```

### If Not Exploring Enough

```python
ent_coef: 0.08  # Up from 0.05
gamma: 0.98  # Down from 0.99
```

---

## 💾 Checkpointing

### Auto-Save Schedule

- Every 25k steps: Checkpoint saved
- Best model: Saved when eval improves
- Final model: Saved at 200k steps

### Resume Training

```bash
# Training auto-resumes from last checkpoint
python train_phase2_local.py
# Will detect latest checkpoint and continue
```

---

## 🎓 Training Tips

### Tip 1: Start Small

Begin with 50k steps to validate setup, then run full 200k.

### Tip 2: Watch First 10k Steps

If reward doesn't improve in first 10k, something is wrong.

### Tip 3: Compare to Baselines

Always evaluate against baseline agents to measure progress.

### Tip 4: Log Everything

Enable verbose logging to understand agent decisions.

### Tip 5: Test on Real Targets

Use legal targets (HackTheBox, TryHackMe) for final validation.

---

## 📝 Training Log Template

```
Training Run: phase2_run_YYYYMMDD_HHMMSS
Date: YYYY-MM-DD
Duration: X hours

Configuration:
- Total steps: 200000
- Learning rate: 0.001
- Entropy coef: 0.05
- Scenarios: 20 training, 5 test

Results:
- Final reward: XXXX
- Nuclei usage: XX%
- vs Baseline: +XX%
- Best checkpoint: XXXk steps

Notes:
- [Any observations or issues]
```

---

**Next**: See PHASE2_PLANNING.md for full implementation roadmap
