#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Isnad Data Processing Pipeline
------------------------------
Command-line interface for the isnad2network package.

This module provides a command-line interface for processing isnad data
through a complete pipeline:
1. Replace names using mapping files
2. Create dictionary files for annotation
3. Generate network JSON data

Usage:
    isnad2network --input-names names.csv --nodelist nodelist.csv 
                  --trans-terms transmissionterms.csv 
                  --path-metadata pathmetadata.csv --output-dir output

Author: Your Name
License: MIT
"""

import os
import sys
import argparse
import time
import logging
from datetime import datetime
import pandas as pd

# Import our modules
from .match_replace_isnads import NetworkNameProcessor
from .dict_creator import CSVDictionaryProcessor
from .generate_json_network_isnad import NetworkNameProcessor as JsonGenerator

# Set up logging
def setup_logging(output_dir):
    """Set up logging for the pipeline."""
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file)
        ]
    )
    return logging.getLogger('isnad_pipeline')

def debug_environment():
    """Print debug information about the environment."""
    logger = logging.getLogger('isnad_pipeline')
    logger.info("=" * 60 + " ENVIRONMENT INFO " + "=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    logger.info(f"System path: {sys.path}")
    logger.info("=" * 140)

def run_pipeline(args):
    """
    Run the complete pipeline or specified steps.
    
    Args:
        args (Namespace): Command line arguments
        
    Returns:
        bool: Overall success status
    """
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Setup logging
    logger = setup_logging(args.output_dir)
    
    # Add debugging information
    debug_environment()
    
    start_time = time.time()
    step_times = {}
    success = True
    
    # Prepare file paths
    names_replaced_file = os.path.join(args.output_dir, "names_replaced.csv")
    unmatched_file = os.path.join(args.output_dir, "unmatched_names.txt")
    dictionaries_dir = os.path.join(args.output_dir, "dictionaries")
    os.makedirs(dictionaries_dir, exist_ok=True)
    network_output_dir = os.path.join(args.output_dir, "network")
    os.makedirs(network_output_dir, exist_ok=True)
    
    try:
        # Step 1: Replace names with mapped values
        if args.steps in [0, 1]:
            step_start = time.time()
            
            logger.info("=" * 60 + " STEP 1: NAME REPLACEMENT " + "=" * 60)
            logger.info(f"Running name replacement using {args.input_names_file} and {args.nodelist_file}...")
            
            try:
                # Initialize the processor
                processor = NetworkNameProcessor(
                    names_file=args.input_names_file,
                    nodelist_file=args.nodelist_file,
                    output_file=names_replaced_file
                )
                
                # Run the processing
                success_step1 = processor.process()
                
                if success_step1:
                    logger.info(f"✓ Names replacement completed successfully")
                    logger.info(f"✓ Output saved to {names_replaced_file}")
                    if os.path.exists(unmatched_file):
                        logger.info(f"✓ Unmatched names saved to {unmatched_file}")
                else:
                    logger.error("❌ Names replacement failed")
                    success = False
                
            except Exception as e:
                logger.error(f"❌ Error during name replacement: {str(e)}")
                logger.exception(e)
                success = False
            
            step_times["Step 1: Name Replacement"] = time.time() - step_start
        
        # Step 2: Create dictionaries for annotation
        if args.steps in [0, 2] and success:
            step_start = time.time()
            
            logger.info("=" * 60 + " STEP 2: DICTIONARY CREATION " + "=" * 60)
            
            # Determine which names file to use
            names_file = names_replaced_file if os.path.exists(names_replaced_file) else args.input_names_file
            logger.info(f"Creating dictionaries using {names_file}...")
            
            try:
                # Initialize the dictionary processor
                processor = CSVDictionaryProcessor()
                
                # Set the input file directly (no upload needed in CLI mode)
                processor.input_file = names_file
                processor.filename_base = os.path.join(dictionaries_dir, os.path.splitext(os.path.basename(names_file))[0])
                
                # Load the CSV
                if processor.load_csv(skip_display=True):
                    # Identify t-columns automatically
                    t_columns = [col for col in processor.data.columns if col.startswith('t')]
                    
                    if t_columns:
                        logger.info(f"Using t-columns for dictionary creation: {', '.join(t_columns)}")
                        
                        # Create unique values dictionary
                        unique_file = processor.create_unique_values_dict(t_columns)
                        if unique_file:
                            logger.info(f"✓ Unique values dictionary saved to {unique_file}")
                        
                        # Create annotation dictionary
                        annotate_file = processor.create_annotation_dict(t_columns)
                        if annotate_file:
                            logger.info(f"✓ Annotation dictionary saved to {annotate_file}")
                        
                        success_step2 = bool(unique_file and annotate_file)
                    else:
                        logger.error("❌ No t-columns found in the CSV file")
                        success_step2 = False
                else:
                    logger.error("❌ Failed to load CSV file")
                    success_step2 = False
                
                if not success_step2:
                    logger.error("❌ Dictionary creation failed")
                    success = False
                
            except Exception as e:
                logger.error(f"❌ Error during dictionary creation: {str(e)}")
                logger.exception(e)
                success = False
            
            step_times["Step 2: Dictionary Creation"] = time.time() - step_start
        
        # Step 3: Generate network JSON
        if args.steps in [0, 3] and success:
            step_start = time.time()
            
            logger.info("=" * 60 + " STEP 3: NETWORK JSON GENERATION " + "=" * 60)
            
            # Determine which names file to use (original or replaced)
            names_file = names_replaced_file if os.path.exists(names_replaced_file) else args.input_names_file
            logger.info(f"Generating network JSON using {names_file}...")
            
            try:
                # Generate the network data
                result = JsonGenerator.generate_network_data(
                    names_replaced_path=names_file,
                    transmission_terms_path=args.trans_terms_file,
                    path_metadata_path=args.path_metadata_file,
                    output_dir=network_output_dir
                )
                
                if result:
                    logger.info(f"✓ Network JSON generation completed successfully")
                    logger.info(f"✓ Output files created in {network_output_dir}")
                    logger.info(f"✓ Created {result['metadata']['node_count']} nodes and {result['metadata']['edge_count']} edges")
                    logger.info(f"✓ Processed {result['metadata']['path_count']} paths")
                else:
                    logger.error("❌ Network JSON generation failed")
                    success = False
                
            except Exception as e:
                logger.error(f"❌ Error during network JSON generation: {str(e)}")
                logger.exception(e)
                success = False
            
            step_times["Step 3: Network JSON Generation"] = time.time() - step_start
        
        # Pipeline summary
        total_time = time.time() - start_time
        logger.info("=" * 80)
        logger.info("PIPELINE EXECUTION SUMMARY")
        logger.info("=" * 80)
        
        for step, step_time in step_times.items():
            logger.info(f"{step}: {step_time:.2f} seconds")
        
        logger.info(f"Total execution time: {total_time:.2f} seconds")
        
        if success:
            logger.info("Pipeline completed successfully!")
        else:
            logger.info("Pipeline completed with errors. Check the log for details.")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Unhandled exception in pipeline: {str(e)}")
        logger.exception(e)
        return False

def main():
    """Main function to parse arguments and run the pipeline."""
    parser = argparse.ArgumentParser(
        description="Isnad2Network - Process and analyze isnad data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Input and output paths
    parser.add_argument("--input-names", "--input-names-file", dest="input_names_file", required=True, 
                        help="Path to input names CSV file")
    parser.add_argument("--nodelist", "--nodelist-file", dest="nodelist_file", required=True, 
                        help="Path to nodelist CSV file with mappings")
    parser.add_argument("--trans-terms", "--trans-terms-file", dest="trans_terms_file", required=True, 
                        help="Path to transmission terms CSV file")
    parser.add_argument("--path-metadata", "--path-metadata-file", dest="path_metadata_file", required=True, 
                        help="Path to path metadata CSV file")
    parser.add_argument("--output-dir", "-o", default="output",
                        help="Directory to save output files")
    
    # Pipeline control
    parser.add_argument("--steps", type=int, choices=[0, 1, 2, 3], default=0,
                        help="Steps to run: 0=all, 1=name replacement, 2=dictionaries, 3=network JSON")
    parser.add_argument("--skip-filtering", action="store_true",
                        help="Skip filtering of records with NA values in JSON generation")
    parser.add_argument("--version", action="store_true",
                        help="Show version information and exit")
    
    args = parser.parse_args()
    
    # Show version and exit if requested
    if args.version:
        try:
            from . import __version__
            print(f"isnad2network version {__version__}")
        except ImportError:
            print("isnad2network version unknown")
        return 0
    
    # Run the pipeline
    success = run_pipeline(args)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
