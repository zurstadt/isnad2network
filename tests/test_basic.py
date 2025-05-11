"""
Basic tests for the isnad2network package.
"""

import os
import unittest
import sys

# Add the src directory to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestBasicImports(unittest.TestCase):
    """Test basic imports to ensure modules can be loaded."""

    def test_can_import_modules(self):
        """Test that all main modules can be imported."""
        try:
            import match_replace_isnads
            self.assertTrue(hasattr(match_replace_isnads, 'process_network_names'))
        except ImportError:
            self.fail("Could not import match_replace_isnads")

        try:
            module_name = "dict_creator" if "dict_creator" in sys.modules else "2dict"
            if module_name == "dict_creator":
                import dict_creator
                self.assertTrue(hasattr(dict_creator, 'CSVDictionaryProcessor'))
            else:
                import importlib
                dict_module = importlib.import_module("2dict")
                self.assertTrue(hasattr(dict_module, 'CSVDictionaryProcessor'))
        except ImportError:
            self.fail(f"Could not import {module_name}")

        try:
            import generate_json_network_isnad
            self.assertTrue(hasattr(generate_json_network_isnad, 'process_isnad_network'))
        except ImportError:
            self.fail("Could not import generate_json_network_isnad")

        try:
            import isnad2network_cli
            self.assertTrue(hasattr(isnad2network_cli, 'main'))
        except ImportError:
            self.fail("Could not import isnad2network_cli")

    def test_cli_parser(self):
        """Test that the CLI argument parser can be created."""
        import argparse
        import isnad2network_cli
        
        # Test if we can create a parser
        parser = argparse.ArgumentParser(description="Test parser")
        try:
            # Get parser setup function by introspection
            setup_parser = getattr(isnad2network_cli, 'main', None)
            self.assertIsNotNone(setup_parser)
        except AttributeError:
            self.fail("isnad2network_cli does not have a 'main' function")

if __name__ == '__main__':
    unittest.main()
