"""
Test Suite for Nuclei Scanner Integration

Tests the NucleiScanner wrapper class functionality.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from envs.nuclei_scanner import NucleiScanner, quick_scan


class TestNucleiScanner:
    """Test cases for NucleiScanner class."""
    
    def test_init_mock_mode(self):
        """Test scanner initialization in mock mode."""
        scanner = NucleiScanner(mock_mode=True)
        assert scanner.mock_mode == True
        assert scanner.rate_limit == 10
        assert scanner.timeout == 300
    
    def test_quick_scan_mock(self):
        """Test quick scan in mock mode."""
        scanner = NucleiScanner(mock_mode=True)
        results = scanner.scan(['http://example.com'], mode='quick')
        
        assert 'vulnerabilities' in results
        assert 'execution_time' in results
        assert 'targets_scanned' in results
        assert 'templates_used' in results
        assert results['targets_scanned'] == 1
    
    def test_standard_scan_mock(self):
        """Test standard scan in mock mode."""
        scanner = NucleiScanner(mock_mode=True)
        results = scanner.scan(['http://example.com'], mode='standard')
        
        assert results['error'] is None
        assert isinstance(results['vulnerabilities'], list)
    
    def test_comprehensive_scan_mock(self):
        """Test comprehensive scan in mock mode."""
        scanner = NucleiScanner(mock_mode=True)
        results = scanner.scan(['http://example.com'], mode='comprehensive')
        
        assert results is not None
        assert 'vulnerabilities' in results
    
    def test_multiple_targets_mock(self):
        """Test scanning multiple targets."""
        scanner = NucleiScanner(mock_mode=True)
        targets = ['http://example1.com', 'http://example2.com']
        results = scanner.scan(targets, mode='quick')
        
        assert results['targets_scanned'] == 2
    
    def test_vulnerability_structure(self):
        """Test vulnerability data structure."""
        scanner = NucleiScanner(mock_mode=True)
        results = scanner.scan(['http://example.com'], mode='quick')
        
        if results['vulnerabilities']:
            vuln = results['vulnerabilities'][0]
            assert 'template_id' in vuln
            assert 'name' in vuln
            assert 'severity' in vuln
            assert 'host' in vuln
            assert vuln['severity'] in ['critical', 'high', 'medium', 'low', 'info']
    
    def test_quick_scan_convenience_function(self):
        """Test convenience function."""
        results = quick_scan(['http://example.com'], mock=True)
        
        assert results is not None
        assert 'vulnerabilities' in results
    
    def test_custom_templates(self):
        """Test scanning with custom templates."""
        scanner = NucleiScanner(mock_mode=True)
        custom = ['cves/2024/', 'exposures/']
        results = scanner.scan(['http://example.com'], mode='quick', custom_templates=custom)
        
        assert results is not None
    
    def test_rate_limiting(self):
        """Test rate limiting parameter."""
        scanner = NucleiScanner(mock_mode=True, rate_limit=5)
        assert scanner.rate_limit == 5
    
    def test_timeout_parameter(self):
        """Test timeout parameter."""
        scanner = NucleiScanner(mock_mode=True, timeout=600)
        assert scanner.timeout == 600
    
    def test_empty_target_list(self):
        """Test with empty target list."""
        scanner = NucleiScanner(mock_mode=True)
        results = scanner.scan([], mode='quick')
        
        assert results['targets_scanned'] == 0
    
    def test_get_template_count(self):
        """Test template count method."""
        scanner = NucleiScanner(mock_mode=True)
        count = scanner.get_template_count()
        
        assert count > 0
    
    def test_update_templates(self):
        """Test template update method."""
        scanner = NucleiScanner(mock_mode=True)
        result = scanner.update_templates()
        
        assert result == True


if __name__ == '__main__':
    # Run tests
    pytest.main([__file__, '-v'])
