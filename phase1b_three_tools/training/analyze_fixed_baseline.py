#!/usr/bin/env python3
"""
Analyze V13 and V16 performance against FIXED baseline

Action 1.1 Follow-up: Compare trained models with permanent baseline reference
"""
import json

# Load fixed baselines
with open('FIXED_BASELINE_HARDCODED.json', 'r') as f:
    hardcoded = json.load(f)

with open('FIXED_BASELINE_RANDOM.json', 'r') as f:
    random_baseline = json.load(f)

# Best model results (from evaluation)
v13_reward = 4321
v16_reward = 4025

# Calculate improvements
print("\n" + "="*80)
print("📊 PERFORMANCE vs FIXED BASELINE (100-run reference)")
print("="*80)
print()

print("FIXED BASELINES (PERMANENT REFERENCE):")
print(f"  Hardcoded: {hardcoded['mean']:.1f} ± {hardcoded['std']:.1f}")
print(f"             95% CI: [{hardcoded['ci_95_lower']:.1f}, {hardcoded['ci_95_upper']:.1f}]")
print(f"  Random:    {random_baseline['mean']:.1f} ± {random_baseline['std']:.1f}")
print(f"             95% CI: [{random_baseline['ci_95_lower']:.1f}, {random_baseline['ci_95_upper']:.1f}]")
print()

print("TRAINED MODELS:")
print(f"  V13: {v13_reward}")
print(f"  V16: {v16_reward}")
print()

print("="*80)
print("IMPROVEMENT OVER HARDCODED BASELINE:")
print("="*80)

v13_vs_hardcoded = ((v13_reward / hardcoded['mean']) - 1) * 100
v16_vs_hardcoded = ((v16_reward / hardcoded['mean']) - 1) * 100

print(f"  V13: +{v13_vs_hardcoded:.1f}%")
print(f"  V16: {v16_vs_hardcoded:+.1f}%")
print()

print("="*80)
print("IMPROVEMENT OVER RANDOM BASELINE:")
print("="*80)

v13_vs_random = ((v13_reward / random_baseline['mean']) - 1) * 100
v16_vs_random = ((v16_reward / random_baseline['mean']) - 1) * 100

print(f"  V13: +{v13_vs_random:.1f}%")
print(f"  V16: +{v16_vs_random:.1f}%")
print()

print("="*80)
print("V13 vs V16 COMPARISON:")
print("="*80)

v13_vs_v16 = ((v13_reward / v16_reward) - 1) * 100
print(f"  V13 beats V16 by: +{v13_vs_v16:.1f}%")
print()

print("="*80)
print("STATISTICAL SIGNIFICANCE:")
print("="*80)

# Check if trained models are significantly better than baseline
v13_in_ci = hardcoded['ci_95_lower'] <= v13_reward <= hardcoded['ci_95_upper']
v16_in_ci = hardcoded['ci_95_lower'] <= v16_reward <= hardcoded['ci_95_upper']

print(f"\nV13 ({v13_reward}) vs Hardcoded CI [{hardcoded['ci_95_lower']:.1f}, {hardcoded['ci_95_upper']:.1f}]:")
if v13_reward > hardcoded['ci_95_upper']:
    print(f"  ✅ V13 SIGNIFICANTLY BETTER (above 95% CI)")
elif v13_in_ci:
    print(f"  ⚠️  V13 within baseline range (NOT significantly different)")
else:
    print(f"  ❌ V13 below baseline")

print(f"\nV16 ({v16_reward}) vs Hardcoded CI [{hardcoded['ci_95_lower']:.1f}, {hardcoded['ci_95_upper']:.1f}]:")
if v16_reward > hardcoded['ci_95_upper']:
    print(f"  ✅ V16 SIGNIFICANTLY BETTER (above 95% CI)")
elif v16_in_ci:
    print(f"  ⚠️  V16 within baseline range (NOT significantly different)")
else:
    print(f"  ❌ V16 below baseline")

print()

print("="*80)
print("🎯 CONCLUSION:")
print("="*80)
print()

if v13_reward > hardcoded['ci_95_upper'] and v16_reward > hardcoded['ci_95_upper']:
    print("✅ BOTH V13 and V16 beat hardcoded baseline with statistical significance!")
    print(f"✅ V13 is best model (+{v13_vs_hardcoded:.1f}% improvement)")
elif v13_reward > hardcoded['ci_95_upper']:
    print("✅ V13 beats hardcoded baseline with statistical significance!")
    print(f"⚠️  V16 does NOT significantly beat baseline (within CI)")
    print(f"👉 SELECT V13 as final model")
else:
    print("⚠️  Neither model significantly beats hardcoded baseline!")
    print("   This suggests RL training did NOT improve over simple heuristic")

print()
print("="*80)
print()
