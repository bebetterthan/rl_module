# 🎯 Phase 2: Vulnerability Detection Layer

**Status**: 🚧 In Development
**Version**: v14
**Based on**: Phase 1B V13 (4321 reward, 65% nmap usage)

---

## 🎯 Objectives

Add intelligent vulnerability scanning capability using **Nuclei** to transform RL Module from reconnaissance tool into actionable vulnerability intelligence platform.

### Key Goals

1. ✅ Learn WHEN to scan for vulnerabilities (40-70% Nuclei usage)
2. ✅ Beat "always scan" baseline by >20%
3. ✅ Maintain execution efficiency (<10 min per scenario)
4. ✅ Generate structured vulnerability reports

---

## 🏗️ Architecture

### Extended Pipeline

```
INPUT (Domain/IP)
    ↓
Phase 0: Disclaimer & Validation
    ↓
Phase 1A: Subfinder → HTTPX (subdomain discovery + probing)
    ↓
Phase 1B: Nmap (conditional port scanning)
    ↓
Phase 2A: Nuclei Vulnerability Scanning (NEW! - conditional)
    ↓
Phase 2B: Result Aggregation & Reporting (NEW!)
    ↓
OUTPUT: Vulnerability Intelligence Report
```

### State Space: 70 dimensions

- **Group 1-4** (40 dims): Phase 1B state (unchanged)
- **Group 5** (15 dims): Vulnerability scanning context
- **Group 6** (10 dims): Nuclei execution state
- **Group 7** (5 dims): Phase 1 summary statistics

### Action Space: 13 actions

- **0-8**: Phase 1B actions (Subfinder, HTTPX, Nmap)
- **9**: Nuclei Quick Scan (top 100 templates)
- **10**: Nuclei Standard Scan (common vulns + CVEs)
- **11**: Nuclei Comprehensive (all templates)
- **12**: Skip Nuclei (smart decision to not scan)

---

## 📁 Project Structure

```
phase2_vuln_detection/
├── README.md                          # This file
├── envs/
│   ├── __init__.py
│   ├── vuln_detection_env.py         # Main RL environment (70-dim state, 13 actions)
│   ├── nuclei_scanner.py             # Nuclei wrapper and integration
│   └── test_vuln_env.py              # Environment unit tests
├── data/
│   ├── phase2_train.json             # Training scenarios (20)
│   ├── phase2_test.json              # Test scenarios (5)
│   └── generate_scenarios_phase2.py  # Scenario generator
├── baselines/
│   ├── __init__.py
│   ├── random_agent.py               # Random actions (25% Nuclei)
│   ├── always_scan_agent.py          # Always use Nuclei (100%)
│   ├── smart_heuristic_agent.py      # Rule-based scanning
│   └── test_all_baselines.py        # Baseline evaluation
├── tests/
│   ├── __init__.py
│   ├── test_nuclei_scanner.py        # Nuclei integration tests
│   ├── test_vuln_env.py              # Environment tests
│   └── test_phase2_integration.py    # Full pipeline tests
├── training/
│   ├── train_phase2_local.py         # Main training script
│   ├── evaluate_phase2.py            # Evaluation script
│   ├── config_phase2.yaml            # Training configuration
│   └── README.md                     # Training guide
└── outputs/
    └── phase2_run_YYYYMMDD_HHMMSS/   # Training runs
        ├── final_model.zip
        ├── best_model/
        ├── checkpoints/
        ├── tensorboard/
        ├── results.json
        └── vec_normalize_stats.pkl
```

---

## 🎨 Reward Function (V14)

### Component Breakdown

**1. Discovery Rewards** (V13 Base - Unchanged)

- Subdomains: 43 each
- Endpoints: 32 each
- Ports: 65 (infra), 22 (web)
- Services: 108 each
- Versions: 54 each

**2. Vulnerability Detection** (NEW!)

- Critical: +500
- High: +250
- Medium: +100
- Low: +30
- First CVE: +200 bonus

**3. Strategic Scanning** (NEW!)

- Correct Skip: +150
- Correct Scan: +200
- Template Match: +100
- High ROI Scan: +250

**4. Completion Bonuses** (Enhanced)

- > 90% + Vulns: +1000
- > 80% + Vulns: +700
- > 70%: +432 (V13)

**5. Phase 2 Workflow** (NEW!)

- 4-tool optimal: +3500
- 3-tool + skip: +2000

**Expected Ranges**:

- Web-only (no Nuclei): 2000-3500
- Infrastructure (with vulns): 5000-8000
- High-value target: 8000-12000

---

## 🚀 Quick Start

### Prerequisites

```bash
# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# Update Nuclei templates
nuclei -update-templates

# Verify installation
nuclei -version
```

### Installation

```bash
cd phase2_vuln_detection
pip install -r requirements.txt
```

### Training

```bash
# Generate scenarios
cd data
python generate_scenarios_phase2.py

# Run baselines
cd ../baselines
python test_all_baselines.py

# Start training
cd ../training
python train_phase2_local.py
```

### Monitoring

```bash
# TensorBoard (separate terminal)
tensorboard --logdir=outputs --port=6006
# Open: http://localhost:6006
```

---

## 📊 Success Metrics

### Performance Targets

- **Reward**: >5500 (30% above baseline ~4200)
- **Nuclei Usage**: 50-80% (intelligent selection)
- **Execution Time**: <600s per scenario
- **Vulnerability Detection**: >80% of actual vulns

### Baselines

- Random (25% Nuclei): ~2800 ± 1800
- Always Scan (100%): ~4200 ± 2400
- Smart Heuristic: ~4800 ± 2100
- **Target Agent**: >5500

---

## 🧪 Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Tests

```bash
# Nuclei integration
pytest tests/test_nuclei_scanner.py -v

# Environment
pytest tests/test_vuln_env.py -v

# Full integration
pytest tests/test_phase2_integration.py -v
```

---

## 📈 Development Roadmap

### Week 1: Foundation ✅

- [x] Project structure created
- [x] Documentation setup
- [ ] Nuclei integration module
- [ ] Mock testing framework

### Week 2: Core Development 🔄

- [ ] VulnDetectionEnv implementation
- [ ] Reward function V14
- [ ] Unit tests
- [ ] Environment validation

### Week 3: Training Prep 📋

- [ ] Scenario generation
- [ ] Baseline agents
- [ ] Training script
- [ ] TensorBoard setup

### Week 4: Training 🎓

- [ ] Initial training (200k steps)
- [ ] Hyperparameter tuning
- [ ] Model optimization
- [ ] Performance evaluation

### Week 5: Integration 🔗

- [ ] End-to-end testing
- [ ] Documentation
- [ ] Integration with main module
- [ ] Release v14

---

## 🔐 Security Considerations

### Legal Compliance

- Enhanced Phase 0 disclaimer for vulnerability scanning
- Explicit authorization warnings
- Activity logging with timestamps
- Scope verification mechanisms

### Safety Mechanisms

- Rate limiting (10 req/s default)
- Target blacklist
- Safe mode (non-intrusive templates only)
- Confirmation prompts for aggressive scans

---

## 📚 Resources

### Official Docs

- [Nuclei Documentation](https://nuclei.projectdiscovery.io/)
- [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- [CVSS v3.1 Specification](https://www.first.org/cvss/v3.1/specification-document)

### Community

- ProjectDiscovery Discord
- Nuclei GitHub Issues
- Reddit r/netsec

---

## 🤝 Contributing

Phase 2 is actively under development. Key areas for contribution:

1. Nuclei template optimization
2. Reward function tuning
3. Performance optimization
4. Documentation improvements

---

## 📝 Change Log

### v14-alpha (Current)

- Initial Phase 2 structure
- Nuclei integration planning
- Architecture design complete

### Future Versions

- v14-beta: Core environment + training
- v14-rc: Testing and optimization
- v14: Production release

---

**Maintained by**: @bebetterthan
**Last Updated**: November 15, 2025
**Status**: 🚧 In Active Development
