#!/usr/bin/env python3
"""
OPTION B: Synthetic Data Augmentation
Generate 60 variant scenarios from existing 20 by intelligent perturbations
MUCH FASTER than hand-crafting - JSON structure guaranteed compatible!
"""
import json
import random
import copy
from typing import List, Dict, Any
from pathlib import Path

random.seed(42)

class ScenarioAugmentor:
    """Create diverse variants from existing scenarios"""
    
    def __init__(self):
        self.port_pools = {
            'web': [80, 443, 8000, 8080, 8443, 3000, 4000, 5000, 9000],
            'ssh': [22, 2222],
            'db': [3306, 5432, 6379, 27017, 1433, 5984],
            'mail': [25, 143, 587, 993, 995],
            'misc': [21, 389, 636, 1194, 3389, 8888, 9090]
        }
        
        self.tech_stacks = {
            'web_modern': ['React', 'Vue.js', 'Next.js', 'Node.js', 'Nginx', 'Docker'],
            'web_classic': ['Apache', 'PHP', 'MySQL', 'WordPress', 'jQuery'],
            'backend': ['Express.js', 'FastAPI', 'Django', 'Spring Boot', 'Ruby on Rails'],
            'database': ['PostgreSQL', 'MongoDB', 'Redis', 'Cassandra', 'Elasticsearch'],
            'devops': ['Jenkins', 'GitLab', 'Kubernetes', 'Docker', 'Ansible'],
            'legacy': ['IIS', 'MSSQL', '.NET', 'Oracle', 'Java EE']
        }
        
        self.subdomain_names = [
            'www', 'api', 'admin', 'app', 'auth', 'cdn', 'dev', 'stage', 'prod',
            'test', 'beta', 'dashboard', 'portal', 'web', 'mobile', 'secure',
            'internal', 'external', 'vpn', 'mail', 'blog', 'forum', 'store',
            'shop', 'payment', 'checkout', 'media', 'assets', 'static', 'files',
            'db', 'cache', 'queue', 'worker', 'monitor', 'metrics', 'logs',
            'us-east', 'us-west', 'eu-central', 'asia', 'global', 'edge'
        ]
    
    def augment_scenario(self, base_scenario: Dict[str, Any], variant_id: int, 
                        augmentation_type: str) -> Dict[str, Any]:
        """Create variant of scenario with specific augmentation"""
        
        # Deep copy to avoid modifying original
        scenario = copy.deepcopy(base_scenario)
        
        # Update ID and name
        original_id = scenario['id']
        scenario['id'] = f"{original_id}_variant_{variant_id:02d}"
        scenario['name'] = f"{scenario['name']} - Variant {variant_id}"
        
        if augmentation_type == 'port_variation':
            # Change port configuration while keeping type
            scenario = self._augment_ports(scenario)
            
        elif augmentation_type == 'size_variation':
            # Add or remove subdomains
            scenario = self._augment_size(scenario)
            
        elif augmentation_type == 'tech_variation':
            # Change technology stack
            scenario = self._augment_technologies(scenario)
            
        elif augmentation_type == 'naming_variation':
            # Change subdomain names
            scenario = self._augment_naming(scenario)
            
        elif augmentation_type == 'combined':
            # Multiple augmentations
            scenario = self._augment_ports(scenario)
            scenario = self._augment_technologies(scenario)
        
        return scenario
    
    def _augment_ports(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Modify port configuration"""
        current_ports = scenario['metadata']['port_list']
        scenario_type = scenario['scenario_type']
        
        # Determine category
        if 'web' in scenario_type:
            # Add or swap web ports
            new_ports = random.sample(self.port_pools['web'], 
                                     random.randint(1, min(3, len(self.port_pools['web']))))
        elif 'infra' in scenario_type:
            # Mix of infrastructure ports
            new_ports = []
            new_ports.append(random.choice(self.port_pools['ssh']))
            new_ports.extend(random.sample(self.port_pools['db'], random.randint(1, 2)))
            if random.random() > 0.5:
                new_ports.append(random.choice(self.port_pools['misc']))
        else:
            # Hybrid - keep mix
            new_ports = random.sample(self.port_pools['web'], 1)
            new_ports.append(random.choice(self.port_pools['ssh']))
            new_ports.extend(random.sample(self.port_pools['db'], 1))
        
        # Update metadata
        scenario['metadata']['port_list'] = sorted(list(set(new_ports)))
        scenario['metadata']['open_ports'] = len(new_ports)
        
        # Update critical services count
        critical = sum(1 for p in new_ports if p in self.port_pools['ssh'] + self.port_pools['db'])
        scenario['metadata']['critical_services'] = critical
        
        return scenario
    
    def _augment_size(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Add or remove subdomains"""
        
        # Get current subdomains from subfinder results
        subdomains = scenario['tool_results']['subfinder']['subdomains']
        domain = scenario['target'] if 'target' in scenario else scenario['domain']
        
        # Decide to add or remove
        if random.random() > 0.5 and len(subdomains) < 25:
            # Add subdomains
            num_to_add = random.randint(1, min(5, 25 - len(subdomains)))
            for _ in range(num_to_add):
                new_name = random.choice(self.subdomain_names)
                new_subdomain = f"{new_name}.{domain}"
                if new_subdomain not in subdomains:
                    subdomains.append(new_subdomain)
        elif len(subdomains) > 3:
            # Remove subdomains
            num_to_remove = random.randint(1, min(3, len(subdomains) - 3))
            subdomains = random.sample(subdomains, len(subdomains) - num_to_remove)
        
        # Update all references
        scenario['tool_results']['subfinder']['subdomains'] = subdomains
        scenario['tool_results']['subfinder']['total_found'] = len(subdomains)
        scenario['metadata']['total_subdomains'] = len(subdomains)
        
        # Update live_endpoints proportionally
        live_ratio = scenario['metadata']['live_endpoints'] / scenario['metadata']['total_subdomains'] if scenario['metadata']['total_subdomains'] > 0 else 0.8
        scenario['metadata']['live_endpoints'] = max(1, int(len(subdomains) * live_ratio))
        
        # Update httpx results
        scenario['tool_results']['httpx']['total_checked'] = len(subdomains)
        scenario['tool_results']['httpx']['live_endpoints'] = scenario['metadata']['live_endpoints']
        
        return scenario
    
    def _augment_technologies(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Change technology stack"""
        
        scenario_type = scenario['scenario_type']
        
        # Select appropriate tech stack
        if 'web' in scenario_type:
            if random.random() > 0.5:
                new_techs = self.tech_stacks['web_modern']
            else:
                new_techs = self.tech_stacks['web_classic']
        elif 'infra' in scenario_type:
            new_techs = random.choice([
                self.tech_stacks['database'],
                self.tech_stacks['devops'],
                self.tech_stacks['backend']
            ])
        else:
            new_techs = random.sample(
                self.tech_stacks['web_modern'] + self.tech_stacks['backend'],
                random.randint(3, 6)
            )
        
        # Update metadata
        scenario['metadata']['technologies'] = list(set(new_techs))
        
        # Update httpx endpoints tech_stack
        if 'endpoints' in scenario['tool_results']['httpx']:
            for endpoint in scenario['tool_results']['httpx']['endpoints']:
                endpoint['tech_stack'] = random.sample(new_techs, 
                                                      min(3, len(new_techs)))
        
        return scenario
    
    def _augment_naming(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Change subdomain names while keeping structure"""
        
        domain = scenario['target'] if 'target' in scenario else scenario['domain']
        base_domain = domain.split('.', 1)[0]  # Get base name
        
        # Get current subdomains
        old_subdomains = scenario['tool_results']['subfinder']['subdomains']
        
        # Create new names
        new_subdomains = []
        for old_sub in old_subdomains:
            old_name = old_sub.split('.')[0]
            new_name = random.choice(self.subdomain_names)
            new_subdomain = old_sub.replace(old_name, new_name, 1)
            new_subdomains.append(new_subdomain)
        
        # Update all references
        scenario['tool_results']['subfinder']['subdomains'] = new_subdomains
        
        # Update httpx endpoints
        if 'endpoints' in scenario['tool_results']['httpx']:
            for i, endpoint in enumerate(scenario['tool_results']['httpx']['endpoints']):
                if i < len(new_subdomains):
                    # Update URL with new subdomain
                    old_url = endpoint['url']
                    protocol = old_url.split('://')[0]
                    port = old_url.split(':')[-1] if ':' in old_url.split('/')[-1] else '443'
                    endpoint['url'] = f"{protocol}://{new_subdomains[i]}:{port}"
                    endpoint['title'] = f"Page on {new_subdomains[i]}"
        
        return scenario

def generate_augmented_dataset(input_file: str, output_file: str, target_count: int = 80):
    """Generate augmented dataset from existing scenarios"""
    
    print("="*80)
    print("OPTION B: SYNTHETIC DATA AUGMENTATION")
    print("="*80)
    print(f"\nInput: {input_file}")
    print(f"Target: {target_count} scenarios")
    print()
    
    # Load existing scenarios
    with open(input_file, 'r') as f:
        data = json.load(f)
        base_scenarios = data['scenarios']
    
    print(f"Loaded {len(base_scenarios)} base scenarios")
    print()
    
    augmentor = ScenarioAugmentor()
    
    # Start with original scenarios
    all_scenarios = base_scenarios.copy()
    print(f"Starting with {len(all_scenarios)} original scenarios")
    
    # Calculate how many variants needed
    variants_needed = target_count - len(base_scenarios)
    variants_per_scenario = variants_needed // len(base_scenarios)
    extra_variants = variants_needed % len(base_scenarios)
    
    print(f"Generating {variants_needed} variants...")
    print(f"  {variants_per_scenario} variants per scenario")
    print(f"  {extra_variants} extra variants")
    print()
    
    # Augmentation types to cycle through
    aug_types = ['port_variation', 'size_variation', 'tech_variation', 
                 'naming_variation', 'combined']
    
    variant_count = 0
    for i, base_scenario in enumerate(base_scenarios):
        # Generate variants for this scenario
        num_variants = variants_per_scenario
        if i < extra_variants:
            num_variants += 1
        
        for v in range(num_variants):
            aug_type = aug_types[v % len(aug_types)]
            variant = augmentor.augment_scenario(base_scenario, v + 1, aug_type)
            all_scenarios.append(variant)
            variant_count += 1
            
            if variant_count % 10 == 0:
                print(f"  Generated {variant_count}/{variants_needed} variants...")
    
    print(f"\nTotal scenarios: {len(all_scenarios)}")
    
    # Validation
    print("\nValidating augmented dataset...")
    scenario_ids = [s['id'] for s in all_scenarios]
    assert len(scenario_ids) == len(set(scenario_ids)), "Duplicate IDs found!"
    print("  OK - All IDs unique")
    
    port_patterns = [tuple(sorted(s['metadata']['port_list'])) for s in all_scenarios]
    unique_ports = len(set(port_patterns))
    print(f"  OK - {unique_ports}/{len(all_scenarios)} unique port patterns ({unique_ports/len(all_scenarios)*100:.1f}%)")
    
    sizes = [s['metadata']['total_subdomains'] for s in all_scenarios]
    print(f"  OK - Size range: {min(sizes)}-{max(sizes)} subdomains")
    
    # Save augmented dataset
    output_data = {
        "version": "1.1",
        "method": "synthetic_augmentation",
        "base_scenarios": len(base_scenarios),
        "augmented_scenarios": len(all_scenarios),
        "total_scenarios": len(all_scenarios),
        "scenarios": all_scenarios
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nSaved to: {output_file}")
    print()
    print("="*80)
    print("AUGMENTATION COMPLETE!")
    print("="*80)
    print("\nDataset is READY for training!")
    print("Next: Run baseline establishment on augmented dataset")
    print()

if __name__ == "__main__":
    input_file = "../data/phase1b_train.json"
    output_file = "../data/phase1b_train_80_augmented.json"
    
    generate_augmented_dataset(input_file, output_file, target_count=80)
