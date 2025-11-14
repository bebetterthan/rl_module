"""
Nuclei Scanner Integration Module

This module provides a wrapper around Nuclei vulnerability scanner for
seamless integration with the RL environment.

Key Features:
- Execute Nuclei scans with different templates
- Parse JSON output
- Handle errors and timeouts
- Mock mode for testing

Author: @bebetterthan
Date: November 15, 2025
"""

import subprocess
import json
import shutil
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class NucleiScanner:
    """
    Wrapper class for Nuclei vulnerability scanner.

    Supports three scanning modes:
    - Quick: Top 100 most common templates (~30-60s)
    - Standard: CVEs + common misconfigs (~60-120s)
    - Comprehensive: All templates (~120-300s)
    """

    def __init__(
        self,
        nuclei_path: Optional[str] = None,
        templates_path: Optional[str] = None,
        mock_mode: bool = False,
        rate_limit: int = 10,
        timeout: int = 300
    ):
        """
        Initialize Nuclei scanner.

        Args:
            nuclei_path: Path to nuclei binary (auto-detect if None)
            templates_path: Path to templates directory (auto-detect if None)
            mock_mode: If True, return mock results for testing
            rate_limit: Max requests per second
            timeout: Max scan duration in seconds
        """
        self.mock_mode = mock_mode
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.nuclei_path: str = ''  # Initialize with empty string

        if not mock_mode:
            # Detect Nuclei binary
            detected_path = nuclei_path or shutil.which('nuclei')
            if not detected_path:
                install_cmd = (
                    "go install -v "
                    "github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest"
                )
                error_msg = f"Nuclei not found! Install with: {install_cmd}"
                raise RuntimeError(error_msg)
            self.nuclei_path = detected_path

            # Verify Nuclei version
            self._verify_nuclei()

            # Detect templates path
            if templates_path:
                self.templates_path = Path(templates_path)
            else:
                # Default Nuclei templates location
                home = Path.home()
                self.templates_path = home / "nuclei-templates"

            if not self.templates_path.exists():
                logger.warning(f"Templates not found at {self.templates_path}")
                logger.warning("Run: nuclei -update-templates")

        logger.info(f"NucleiScanner initialized (mock={mock_mode})")

    def _verify_nuclei(self):
        """Verify Nuclei installation and version."""
        try:
            result = subprocess.run(
                [self.nuclei_path, '-version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            version = result.stdout.strip()
            logger.info(f"Nuclei version: {version}")
        except Exception as e:
            raise RuntimeError(f"Failed to verify Nuclei: {e}")

    def scan(
        self,
        targets: List[str],
        mode: str = 'standard',
        custom_templates: Optional[List[str]] = None
    ) -> Dict:
        """
        Execute vulnerability scan on targets.

        Args:
            targets: List of URLs/hosts to scan
            mode: Scan mode ('quick', 'standard', 'comprehensive')
            custom_templates: Optional list of specific templates to use

        Returns:
            Dict containing:
                - vulnerabilities: List of findings
                - execution_time: Scan duration in seconds
                - targets_scanned: Number of targets
                - templates_used: Number of templates
                - http_requests: Number of HTTP requests made
        """
        if self.mock_mode:
            return self._mock_scan(targets, mode)

        # Build Nuclei command
        cmd = self._build_command(targets, mode, custom_templates)

        # Execute scan
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Parse results
            return self._parse_output(result.stdout, result.stderr)

        except subprocess.TimeoutExpired:
            logger.error(f"Nuclei scan timed out after {self.timeout}s")
            return {
                'vulnerabilities': [],
                'execution_time': self.timeout,
                'targets_scanned': len(targets),
                'templates_used': 0,
                'http_requests': 0,
                'error': 'timeout'
            }
        except Exception as e:
            logger.error(f"Nuclei scan failed: {e}")
            return {
                'vulnerabilities': [],
                'execution_time': 0,
                'targets_scanned': 0,
                'templates_used': 0,
                'http_requests': 0,
                'error': str(e)
            }

    def _build_command(
        self,
        targets: List[str],
        mode: str,
        custom_templates: Optional[List[str]]
    ) -> List[str]:
        """Build Nuclei command with appropriate flags."""
        if not self.nuclei_path:
            raise RuntimeError("Nuclei path not initialized")
        cmd: List[str] = [self.nuclei_path]

        # Add targets
        if len(targets) == 1:
            cmd.extend(['-u', targets[0]])
        else:
            # Create temp file with targets
            target_file = '/tmp/nuclei_targets.txt'
            with open(target_file, 'w') as f:
                f.write('\n'.join(targets))
            cmd.extend(['-l', target_file])

        # Add templates based on mode
        if custom_templates:
            for template in custom_templates:
                cmd.extend(['-t', template])
        else:
            if mode == 'quick':
                # Top severity templates only
                cmd.extend(['-s', 'critical,high'])
                cmd.extend(['-tags', 'cve,exposure'])
            elif mode == 'standard':
                # Common vulnerabilities
                cmd.extend(['-tags', 'cve,exposure,misconfig'])
            elif mode == 'comprehensive':
                # All templates
                cmd.extend(['-t', str(self.templates_path)])

        # Output format
        cmd.extend(['-json'])

        # Rate limiting
        cmd.extend(['-rl', str(self.rate_limit)])

        # Silent mode (no banner)
        cmd.extend(['-silent'])

        # Disable update check
        cmd.extend(['-duc'])

        return cmd

    def _parse_output(self, stdout: str, stderr: str) -> Dict:
        """Parse Nuclei JSON output."""
        vulnerabilities = []

        # Parse JSON lines
        for line in stdout.strip().split('\n'):
            if not line:
                continue
            try:
                vuln = json.loads(line)
                info = vuln.get('info', {})
                vulnerabilities.append({
                    'template_id': vuln.get('template-id', ''),
                    'name': info.get('name', ''),
                    'severity': info.get('severity', 'unknown'),
                    'host': vuln.get('host', ''),
                    'matched_at': vuln.get('matched-at', ''),
                    'description': info.get('description', ''),
                    'tags': info.get('tags', []),
                    'reference': vuln.get('info', {}).get('reference', []),
                })
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON line: {line[:100]}")

        # Extract stats from stderr
        execution_time = 0
        templates_used = 0
        http_requests = 0

        # TODO: Parse stats from Nuclei stderr output
        # Example: "[INF] Executing 1234 templates..."

        return {
            'vulnerabilities': vulnerabilities,
            'execution_time': execution_time,
            'targets_scanned': len(vulnerabilities) if vulnerabilities else 0,
            'templates_used': templates_used,
            'http_requests': http_requests,
            'error': None
        }

    def _mock_scan(self, targets: List[str], mode: str) -> Dict:
        """Return mock scan results for testing."""
        import random
        import time

        # Simulate scan time
        time.sleep(0.1)

        # Generate mock vulnerabilities
        mock_vulns = []

        if random.random() < 0.6:  # 60% chance of finding something
            num_vulns = random.randint(1, 5)
            severities = ['critical', 'high', 'medium', 'low', 'info']

            for i in range(num_vulns):
                target = targets[0] if targets else 'http://example.com'
                matched = (f'{target}/vulnerable/path'
                           if targets else 'http://example.com/test')
                mock_vulns.append({
                    'template_id': f'CVE-2024-{random.randint(1000, 9999)}',
                    'name': f'Test Vulnerability {i + 1}',
                    'severity': random.choice(severities),
                    'host': target,
                    'matched_at': matched,
                    'description': 'Mock vulnerability for testing',
                    'tags': ['test', 'mock'],
                    'reference': []
                })

        # Determine templates_used based on scan mode
        if mode == 'quick':
            templates_used = 100
        elif mode == 'standard':
            templates_used = 500
        else:
            templates_used = 1000

        return {
            'vulnerabilities': mock_vulns,
            'execution_time': random.uniform(10, 60),
            'targets_scanned': len(targets),
            'templates_used': templates_used,
            'http_requests': random.randint(50, 200),
            'error': None
        }

    def get_template_count(self, category: Optional[str] = None) -> int:
        """
        Get count of available templates.

        Args:
            category: Optional template category (cve, exposure, etc.)

        Returns:
            Number of templates
        """
        if self.mock_mode:
            return 1000

        # TODO: Implement actual template counting
        return 0

    def update_templates(self) -> bool:
        """
        Update Nuclei templates to latest version.

        Returns:
            True if successful, False otherwise
        """
        if self.mock_mode:
            return True

        if not self.nuclei_path:
            logger.error("Nuclei path not initialized")
            return False

        try:
            subprocess.run(
                [self.nuclei_path, '-update-templates'],
                check=True,
                timeout=60,
                capture_output=True
            )
            logger.info("Nuclei templates updated successfully")
            return True
        except subprocess.TimeoutExpired:
            logger.error("Template update timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to update templates: {e}")
            return False


# Convenience function for quick scanning
def quick_scan(targets: List[str], mock: bool = False) -> Dict:
    """
    Quick scan with top templates.

    Args:
        targets: List of URLs/hosts
        mock: Use mock mode for testing

    Returns:
        Scan results dictionary
    """
    scanner = NucleiScanner(mock_mode=mock)
    return scanner.scan(targets, mode='quick')


if __name__ == '__main__':
    # Test with mock mode
    print("Testing NucleiScanner in mock mode...")
    scanner = NucleiScanner(mock_mode=True)

    results = scanner.scan(['http://example.com'], mode='quick')
    print("\nScan Results:")
    print(f"  Vulnerabilities found: {len(results['vulnerabilities'])}")
    print(f"  Execution time: {results['execution_time']:.2f}s")
    print(f"  Templates used: {results['templates_used']}")

    if results['vulnerabilities']:
        print("\nSample vulnerability:")
        vuln = results['vulnerabilities'][0]
        print(f"  Name: {vuln['name']}")
        print(f"  Severity: {vuln['severity']}")
        print(f"  Host: {vuln['host']}")
