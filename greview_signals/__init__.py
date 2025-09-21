"""
GReviewSignals - Google Business Profile Review Analysis Package

A Python package for analyzing Google Business Profile reviews from Google Takeout data.
Extracts person names mentioned in reviews using Named Entity Recognition (NER) and
provides comprehensive filtering and export capabilities.

Main Components:
    - GoogleBusinessProfileAnalyzer: Core analysis class
    - Command-line interface via main.py

Usage:
    # As a module
    from greview_signals.analyzer import GoogleBusinessProfileAnalyzer
    
    # Via command line
    python main.py --year 2025 --stars FOUR FIVE --export-names staff.csv

Author: GReviewSignals Project
Version: 1.0.0
"""

from .analyzer import GoogleBusinessProfileAnalyzer

__version__ = "1.0.0"
__author__ = "GReviewSignals Project"
__email__ = "your-email@example.com"

__all__ = ["GoogleBusinessProfileAnalyzer"]