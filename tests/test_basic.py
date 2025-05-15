#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic tests for the isnad2network package.
"""

import unittest
import argparse

class TestBasicImports(unittest.TestCase):
    """Test basic imports of the package."""

    def test_can_import_modules(self):
        """Test that all main modules can be imported."""
        try:
            # Import from the package, not directly
            from isnad2network import NetworkNameProcessor
            # Check that the imported class has what we expect
            self.assertTrue(hasattr(NetworkNameProcessor, 'process'))
        except ImportError:
            self.fail("Could not import NetworkNameProcessor from isnad2network")
    
    def test_cli_parser(self):
        """Test that the CLI argument parser can be created."""
        try:
            # Import the CLI module from the package
            from isnad2network import isnad2network_cli
            # Create a parser to test basic functionality
            parser = isnad2network_cli.argparse.ArgumentParser()
            self.assertIsInstance(parser, argparse.ArgumentParser)
        except ImportError:
            self.fail("Could not import isnad2network_cli from isnad2network")

if __name__ == "__main__":
    unittest.main()
