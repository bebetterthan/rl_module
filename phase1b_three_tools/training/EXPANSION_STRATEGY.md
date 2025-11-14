# PHASE 1B: 80-SCENARIO EXPANSION STRATEGY

**Task 1.2: Comprehensive Design for Data Expansion**

Generated: 2025-11-14
Based on: Task 1.1 analysis of current 20 scenarios

---

## 📊 CURRENT STATE SUMMARY (20 Scenarios)

**Size Distribution**:

- Small (3-7): 1 scenario (5%) ⚠️ INSUFFICIENT
- Medium (8-15): 14 scenarios (70%) ✅ GOOD
- Large (16-25): 5 scenarios (25%) ✅ GOOD

**Type Distribution** (has overlaps in categorization):

- Web-only: ~5 pure web scenarios
- Infrastructure: ~7 pure infra scenarios
- Hybrid: ~7 hybrid scenarios
- Edge cases: 1 (cdn_ecommerce)

**Quality Metrics**:

- ✅ 20 unique port patterns (100%)
- ✅ 49 unique technologies
- ✅ 43 unique subdomain names
- ⚠️ Optimal strategy metadata missing/incomplete

---

## 🎯 TARGET DISTRIBUTION (80 Scenarios Total)

### BY SIZE (Subdomain Count)

```
Small (3-7 subdomains):   25 scenarios (31%)  ← Need +24!
Medium (8-15 subdomains): 35 scenarios (44%)  ← Need +21
Large (16-25 subdomains): 20 scenarios (25%)  ← Need +15
```

**Rationale**:

- Small scenarios CRITICAL (only 1 currently!)
- Medium most common in real-world
- Large for complexity testing

### BY TYPE (Service Mix)

```
Pure Web-Only:       30 scenarios (37%)  ← HTTP/HTTPS only
Pure Infrastructure: 25 scenarios (31%)  ← SSH/DB/services, minimal web
Hybrid (Mixed):      20 scenarios (25%)  ← Combination of both
Edge Cases:           5 scenarios (7%)   ← Unusual/adversarial
```

**Explicit Definitions**:

- **Web-Only**: Ports 80/443/8080/3000 only, no SSH/DB/infra services
- **Infrastructure**: SSH (22), databases (3306/5432/6379/27017), monitoring (9090/3000), NO web or minimal
- **Hybrid**: Mix of web AND infrastructure services
- **Edge**: Stealth, filtered, custom ports, minimal attack surface

### BY TECHNOLOGY STACK (80 Total)

```
Modern Cloud (Docker, K8s, microservices):     15 scenarios
LAMP Stack (Apache, MySQL, PHP):               12 scenarios
MEAN Stack (Node, MongoDB, Express):           10 scenarios
Legacy Enterprise (IIS, .NET, Oracle, SAP):    10 scenarios
E-Commerce (Magento, WooCommerce, Shopify):     8 scenarios
DevOps/Security (Jenkins, GitLab, Nexus):       8 scenarios
Database-Heavy (PostgreSQL, MongoDB, Redis):    7 scenarios
Content/CMS (WordPress, Drupal, Joomla):        5 scenarios
Mixed/Unusual:                                  5 scenarios
```

**Anti-Over-Representation Rule**: No technology appears in >12% of scenarios (max 10 times)

### BY PORT PATTERNS (CRITICAL!)

```
REQUIREMENT: 80 UNIQUE PORT COMBINATIONS (one per scenario!)

Categories (distribution guide, not rigid):
Web-Only Ports (80, 443, 8080, 3000, etc):       30 scenarios
Web + SSH (80, 443, 22):                         12 scenarios
Web + Database (80, 443, 3306/5432):             12 scenarios
Full Infrastructure (SSH + DB + monitoring):     10 scenarios
Custom High Ports (4000-9000):                    8 scenarios
Minimal Ports (1-2 services only):                5 scenarios
Stealth/Filtered:                                 3 scenarios
```

**Validation**: Run uniqueness check - must be 80 unique tuples!

### BY NAMING PATTERNS (Prevent Memorization!)

```
REQUIREMENT: No scenario shares >3 subdomain names with any other

Name Categories (use diverse pool):
Generic (www, api, mail, ftp):                  ~15 scenarios
Functional (auth, payment, admin, dashboard):   ~15 scenarios
Regional (us-east, eu-west, asia, etc):         ~10 scenarios
Environment (dev, staging, prod, test):         ~10 scenarios
Business Units (hr, finance, sales, support):   ~10 scenarios
Technical (db, cache, cdn, lb, proxy):          ~10 scenarios
Random/Creative (custom names):                 ~10 scenarios
```

**Name Pool Size**: Aim for 100+ unique subdomain names total

### BY OPTIMAL STRATEGY (Learning Targets)

```
Skip Nmap (web-only, high time bonus):          25 scenarios (31%)
Quick Nmap (hybrid, balance efficiency):        30 scenarios (37%)
Service Nmap (infra, detailed discovery):       20 scenarios (25%)
Full Nmap (security-critical, comprehensive):    5 scenarios (7%)
```

**Critical**: This distribution teaches ALL decision patterns!

---

## 🚫 ANTI-CORRELATION REQUIREMENTS

**CRITICAL**: Break obvious feature correlations that enable memorization!

### Rule 1: Size ≠ Type

```
❌ BAD: All small = web-only, all large = infrastructure
✅ GOOD:
   Small scenarios: 15 web-only, 7 infrastructure, 3 hybrid
   Medium scenarios: 10 web-only, 12 infrastructure, 10 hybrid, 3 edge
   Large scenarios: 5 web-only, 6 infrastructure, 7 hybrid, 2 edge
```

### Rule 2: Naming ≠ Type

```
❌ BAD: "api" subdomain always means infrastructure
✅ GOOD: "api" appears in web-only, hybrid, AND infrastructure scenarios
```

### Rule 3: Technology ≠ Strategy

```
❌ BAD: WordPress always means skip nmap
✅ GOOD: WordPress can have SSH/MySQL (quick nmap needed)
```

### Rule 4: Port Count ≠ Optimal Strategy

```
❌ BAD: 2 ports = skip nmap, 6 ports = service nmap
✅ GOOD: 2 ports could be SSH+MySQL (service nmap), 6 ports could be all HTTP variants (skip nmap)
```

**Validation Method**: Calculate correlation coefficient for each feature pair - must be <0.3!

---

## 🎲 DIVERSITY ENFORCEMENT RULES

### Uniqueness Constraints

1. **Port patterns**: 80 unique combinations (STRICT)
2. **Domain names**: 80 unique domains (easy)
3. **Technology combos**: 60+ unique stacks (aim for max variety)
4. **Subdomain name sets**: Max 3 shared names between any two scenarios

### Distribution Constraints

1. **Size distribution**: Must be 25/35/20 (±2 tolerance)
2. **Type distribution**: Must be 30/25/20/5 (±2 tolerance)
3. **Strategy distribution**: Must be 25/30/20/5 (±2 tolerance)

### Quality Constraints

1. **Realistic timing**: 10-180 seconds per tool
2. **Coherent services**: SSH (port 22) with proper SSH service
3. **Logical stacks**: nginx + React (common), IIS + .NET (common)
4. **Realistic versions**: Apache 2.4, MySQL 8.0, not nonsense versions

---

## 📝 GENERATION APPROACH

### Method: Systematic + Random Hybrid

**Phase 1: Systematic Core (60 scenarios)**
Generate in blocks to ensure coverage:

- Block 1: 15 small web-only (various tech stacks)
- Block 2: 7 small infrastructure (minimal services)
- Block 3: 3 small hybrid (rare but need examples)
- Block 4: 10 medium web-only (common pattern)
- Block 5: 12 medium infrastructure (servers, DBs)
- Block 6: 10 medium hybrid (mixed environments)
- Block 7: 3 medium edge cases
- Total: 60 scenarios

**Phase 2: Random Diversity Fill (20 scenarios)**
Generate randomly with constraints:

- Must satisfy distribution targets (reach 80 total)
- Must have unique port patterns
- Must break any emerging correlations
- Purpose: Prevent systematic bias in generation

### Validation After Generation

1. **Syntax check**: JSON valid, all fields present
2. **Uniqueness check**: Port patterns, domain names
3. **Distribution check**: Size/type/strategy match targets
4. **Diversity check**: Name overlap matrix, tech distribution
5. **Correlation check**: Size-type, naming-type, ports-strategy
6. **Realism check**: Timing, service coherence, versions

**Pass Criteria**: All checks GREEN ✅

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Prepare Generation Template

- Define JSON structure matching phase1b_train.json format
- Create helper functions for tool result generation
- Setup validation functions

### Step 2: Generate Scenarios in Batches

- Batch 1: Scenarios 1-20 (focus on small size)
- Batch 2: Scenarios 21-40 (focus on medium size)
- Batch 3: Scenarios 41-60 (focus on large size)
- Batch 4: Scenarios 61-80 (random diversity fill)

### Step 3: Validate Each Batch

- Run validation script after each batch
- Fix issues before proceeding to next batch
- Maintain quality throughout process

### Step 4: Merge and Final Validation

- Combine all 4 batches into phase1b_train_80.json
- Run comprehensive validation on full 80-scenario set
- Generate validation report

### Step 5: Test Set Alignment

- Ensure test set (25 scenarios) has similar distribution
- No overlap with training scenarios
- Representative sample, not adversarial

---

## 📊 EXPECTED OUTCOMES

### Training Data Quality

- **Volume**: 80 scenarios (4x current)
- **Diversity**: High entropy in all dimensions
- **Balance**: Matches real-world distribution
- **Quality**: Realistic, coherent, validated

### Generalization Improvement

- **Current**: 3928 reward on test (baseline level)
- **Expected**: 4200+ reward on test (>5% improvement)
- **Mechanism**: More diverse data → Better pattern learning → Less overfitting

### Training Efficiency

- **Exposures per scenario**: 6,250 (vs 15,000 before)
- **Training time**: 5-6 minutes (vs 3 minutes for 20 scenarios)
- **Reasonable**: 6,250 exposures sufficient with high diversity

---

## ✅ SUCCESS CRITERIA

### Data Quality Metrics

- ✅ 80 unique port patterns (100%)
- ✅ 60+ unique technology stacks (75%+)
- ✅ 100+ unique subdomain names
- ✅ <3 name overlap between any two scenarios
- ✅ All distributions within ±2 of targets
- ✅ All correlations <0.3

### RL Performance Metrics (After Training)

- ✅ Test set reward: >4200 (+5% vs baseline)
- ✅ Statistical significance: p < 0.05
- ✅ Effect size: d > 0.3
- ✅ Conditional learning: 20% nmap (web) vs 85% nmap (infra)
- ✅ Generalization gap: <10% drop from training to test

---

## 🚀 NEXT STEPS

1. ✅ **Task 1.1 Complete**: Analysis done
2. ✅ **Task 1.2 Complete**: Strategy documented (THIS FILE)
3. ⏭️ **Task 1.3 Next**: Generate 80 scenarios using this strategy
4. ⏭️ **Task 1.4 Next**: Validate generated scenarios
5. ⏭️ **Day 3**: Baseline recalibration + training config
6. ⏭️ **Day 4**: Training execution (5-6 minutes!)
7. ⏭️ **Day 5**: Evaluation + behavioral analysis
8. ⏭️ **Day 6**: Iteration if needed
9. ⏭️ **Day 7**: Documentation + closure

**Timeline**: 5-7 days to complete Phase 1B recovery

---

## 💡 KEY INSIGHTS

**Why This Will Work**:

1. **Data quantity**: 80 scenarios = 4-5x increase
2. **Data quality**: Enforced diversity, no memorization cues
3. **Data balance**: Matches learning theory (10-20 examples per pattern)
4. **Validation rigor**: Multiple checks ensure quality
5. **Realistic expectations**: 5-10% improvement achievable

**Risk Mitigation**:

1. **Fast iteration**: 5-6 min training enables quick experiments
2. **Systematic approach**: Not random generation, designed coverage
3. **Quality gates**: Validation at each step
4. **Statistical rigor**: Proper significance testing
5. **Fallback plan**: If fails, accept as research finding

**Success Probability**: 70% (realistic, data-driven estimate)

---

**Strategy Owner**: Senior PM
**Execution Owner**: Development Team  
**Status**: READY FOR EXECUTION ✅
