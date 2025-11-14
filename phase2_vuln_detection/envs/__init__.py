"""
Phase 2 Vulnerability Detection Environments

This module provides RL environments for learning intelligent vulnerability scanning.
"""

from .nuclei_scanner import NucleiScanner
# from .vuln_detection_env import VulnDetectionEnv  # TODO: Implement

__all__ = ['NucleiScanner']  # 'VulnDetectionEnv' will be added later
