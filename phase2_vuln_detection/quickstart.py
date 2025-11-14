"""
Quick Start Script for Phase 2

Run this to test the basic setup.
"""

import sys
from pathlib import Path

print("=" * 60)
print("Phase 2: Vulnerability Detection Layer")
print("Quick Start Test")
print("=" * 60)

# Test 1: Nuclei Scanner
print("\n1. Testing Nuclei Scanner (mock mode)...")
try:
    from envs.nuclei_scanner import NucleiScanner
    
    scanner = NucleiScanner(mock_mode=True)
    results = scanner.scan(['http://example.com'], mode='quick')
    
    print(f"   ✅ Scanner initialized")
    print(f"   ✅ Mock scan completed")
    print(f"   ✅ Found {len(results['vulnerabilities'])} vulnerabilities (mock)")
    print(f"   ✅ Execution time: {results['execution_time']:.2f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Project Structure
print("\n2. Checking project structure...")
required_dirs = ['envs', 'data', 'baselines', 'tests', 'training', 'outputs']
for dir_name in required_dirs:
    dir_path = Path(__file__).parent / dir_name
    if dir_path.exists():
        print(f"   ✅ {dir_name}/ exists")
    else:
        print(f"   ❌ {dir_name}/ missing")

# Test 3: Dependencies
print("\n3. Checking dependencies...")
required_packages = [
    'stable_baselines3',
    'gymnasium',
    'numpy',
    'torch',
    'tensorboard'
]

for package in required_packages:
    try:
        __import__(package.replace('-', '_'))
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} not installed")

# Summary
print("\n" + "=" * 60)
print("✅ Phase 2 basic setup complete!")
print("\nNext steps:")
print("1. Generate scenarios: cd data && python generate_scenarios_phase2.py")
print("2. Run tests: pytest tests/ -v")
print("3. Train model: cd training && python train_phase2_local.py")
print("=" * 60)
