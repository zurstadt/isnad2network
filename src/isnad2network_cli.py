#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Isnad Data Processing Pipeline
------------------------------
Command-line interface for the isnad network processing pipeline.

Usage:
    python final_pipeline.py --input-names-file data/names.csv --nodelist-file data/nodelist.csv 
                             --trans-terms-file data/transmissionterms.csv 
                             --path-metadata-file data/pathmetadata.csv --output-dir output
"""

import os
import sys
import argparse
import time
import logging
from datetime import datetime
import pandas as pd

# Import your modules
from match_replace_isnads import replace_names_with_mappings  # For step 1
from generate_json_network_isnad import process_isnad_network, compare_chain_lengths  # For step 3

# Set up logging
log_dir = "logs"
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
logger = logging.getLogger('isnad_pipeline')

def run_pipeline(args):
    """
    Run the complete pipeline or specified steps
    
    Args:
        args (Namespace): Command line arguments
        
    Returns:
        bool: Overall success status
    """
    # Add debugging information
    debug_environment()
    
    start_time = time.time()
    step_times = {}
    success = True
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Prepare file paths
    names_replaced_file = os.path.join(args.output_dir, "names_replaced.csv")
    network_output_dir = os.path.join(args.output_dir, "network")
    os.makedirs(network_output_dir, exist_ok=True)
    
    try:
        # Step 1: Replace names
        if args.steps in [0, 1]:
            # Implementation for step 1...
            pass
        
        # Step 2: Create dictionaries
        if args.steps in [0, 2]:
            # Implementation for step 2...
            pass
        
        # Step 3: Generate network JSON
        if args.steps in [0, 3]:
            step_start = time.time()
            
            logger.info("=" * 60 + " STEP 3: NETWORK JSON GENERATION " + "=" * 60)
            
            # Determine which names file to use (original or replaced)
            names_file = names_replaced_file if os.path.exists(names_replaced_file) else args.input_names_file
            logger.info(f"Running network JSON generation using {names_file}...")
            logger.info(f"Output directory: {network_output_dir}")
            
            # Add debugging to trace the calls
            logger.info("DEBUGGING: Checking module imports and attributes")
            try:
                # Check if generate_json_network_isnad module is properly imported
                import generate_json_network_isnad
                logger.info("✓ Successfully imported generate_json_network_isnad module")
                
                # Check if process_isnad_network function exists in the module
                if hasattr(generate_json_network_isnad, 'process_isnad_network'):
                    logger.info("✓ process_isnad_network function found in generate_json_network_isnad module")
                else:
                    logger.error("❌ process_isnad_network function NOT found in generate_json_network_isnad module")
                    logger.info(f"Available attributes in generate_json_network_isnad: {dir(generate_json_network_isnad)}")
                
                # Check for any json_generator module in sys.modules
                import sys
                if 'json_generator' in sys.modules:
                    logger.error("❌ json_generator module found in sys.modules")
                    logger.info(f"json_generator source: {sys.modules['json_generator'].__file__ if hasattr(sys.modules['json_generator'], '__file__') else 'unknown'}")
                else:
                    logger.info("✓ No json_generator module found in sys.modules")
                
                # Try the actual implementation with detailed error tracking
                try:
                    logger.info("Generating network JSON:")
                    logger.info(f"- Names file: {names_file}")
                    logger.info(f"- Transmission terms file: {args.trans_terms_file}")
                    logger.info(f"- Metadata file: {args.path_metadata_file}")
                    logger.info(f"- Output directory: {network_output_dir}")
                    
                    # Call the process_isnad_network function directly and trace execution
                    logger.info("DEBUGGING: About to call process_isnad_network")
                    result = generate_json_network_isnad.process_isnad_network(
                        trans_file=args.trans_terms_file,
                        names_file=names_file,
                        metadata_file=args.path_metadata_file,
                        output_dir=network_output_dir,
                        skip_filtering=args.skip_filtering
                    )
                    logger.info("DEBUGGING: Successfully called process_isnad_network")
                    
                    logger.info(f"✓ Network JSON generation completed successfully")
                    logger.info(f"✓ Output files created in {network_output_dir}")
                    logger.info(f"✓ Processed {result['records_processed']} records")
                    logger.info(f"✓ Created {result['node_count']} nodes and {result['edge_count']} edges")
                    
                except Exception as e:
                    logger.error(f"❌ Error during process_isnad_network call: {str(e)}")
                    logger.error("DEBUGGING: Detailed traceback:")
                    import traceback
                    logger.error(traceback.format_exc())
                    success = False
                    
            except ImportError as e:
                logger.error(f"❌ Failed to import generate_json_network_isnad module: {str(e)}")
                logger.error("DEBUGGING: Python path:")
                logger.error(sys.path)
                success = False
            except Exception as e:
                logger.error(f"❌ Unexpected error during debugging: {str(e)}")
                logger.error(traceback.format_exc())
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Isnad Data Processing Pipeline")
    
    # Input and output paths
    parser.add_argument("--input-names-file", required=True, 
                        help="Path to input names file")
    parser.add_argument("--nodelist-file", required=True, 
                        help="Path to nodelist file with mappings")
    parser.add_argument("--trans-terms-file", required=True, 
                        help="Path to transmission terms file")
    parser.add_argument("--path-metadata-file", required=True, 
                        help="Path to path metadata file")
    parser.add_argument("--output-dir", default="output",
                        help="Directory to save output files (default: output)")
    
    # Pipeline control
    parser.add_argument("--steps", type=int, choices=[0, 1, 2, 3], default=0,
                        help="Steps to run: 0=all, 1=name replacement, 2=dictionaries, 3=network JSON")
    parser.add_argument("--skip-filtering", action="store_true",
                        help="Skip filtering of records with NA values in JSON generation")
    
    args = parser.parse_args()
    
    # Run the pipeline
    success = run_pipeline(args)
    sys.exit(0 if success else 1)