#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
isnad2network - A toolkit for processing and analyzing isnad chains
------------------------------------------------------------------

This package provides tools for:
1. Standardizing transmitter names
2. Creating dictionaries for annotation
3. Generating network representations of isnad chains
4. Analyzing transmission methods

For more information, see the README.md file or visit:
https://github.com/zurstadt/isnad2network
"""

__version__ = '0.2.0'

# Import main components with error handling
try:
    from .match_replace_isnads import NetworkNameProcessor
except ImportError:
    NetworkNameProcessor = None

try:
    from .dict_creator import CSVDictionaryProcessor
except ImportError:
    CSVDictionaryProcessor = None

try:
    from .generate_json_network_isnad import generate_network_data
except ImportError:
    generate_network_data = None

# Import run_pipeline correctly
try:
    # Directly import run_pipeline from the correct file
    from .isnad2network_cli import run_pipeline as process_pipeline
except ImportError:
    # Simple placeholder that doesn't use the exception variable
    def process_pipeline(*args, **kwargs):
        """Placeholder for pipeline processing function."""
        raise ImportError("Could not import run_pipeline")

__all__ = [
    'NetworkNameProcessor',
    'CSVDictionaryProcessor',
    'generate_network_data',
    'process_pipeline',
    'isnad2network_cli'،
]