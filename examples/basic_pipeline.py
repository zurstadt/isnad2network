#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basic example demonstrating the Isnad2Network pipeline.
This script shows how to use the toolkit components to process isnad data.
"""

import os
import logging
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('isnad_example')

def run_pipeline():
    """Run the complete isnad2network pipeline on sample data"""
    
    # Define input and output paths
    data_dir = "../data"
    output_dir = "example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Replace Names
    logger.info("Step 1: Name Replacement")
    
    from isnad2network.match_replace_isnads import process_network_names
    
    names_file = os.path.join(data_dir, "names.csv")
    nodelist_file = os.path.join(data_dir, "nodelist.csv")
    names_replaced_file = os.path.join(output_dir, "names_replaced.csv")
    
    result_df = process_network_names(
        names_file=names_file,
        nodelist_file=nodelist_file,
        output_file=names_replaced_file
    )
    
    if result_df is not None:
        logger.info(f"Name replacement successful: {len(result_df)} records processed")
    else:
        logger.error("Name replacement failed")
        return
    
    # Step 2: Create Dictionaries
    logger.info("Step 2: Dictionary Creation")
    
    try:
        from isnad2network.dict_creator import CSVDictionaryProcessor
    except ImportError:
        # Try alternative module name
        try:
            from isnad2network import dict_creator as module
            CSVDictionaryProcessor = module.CSVDictionaryProcessor
        except ImportError:
            logger.error("Could not import CSVDictionaryProcessor")
            return
    
    dict_output_dir = os.path.join(output_dir, "dictionaries")
    os.makedirs(dict_output_dir, exist_ok=True)
    
    processor = CSVDictionaryProcessor()
    processor.input_file = names_replaced_file
    
    # Set output path
    base_filename = os.path.splitext(os.path.basename(names_replaced_file))[0]
    processor.filename_base = os.path.join(dict_output_dir, base_filename)
    
    # Load CSV
    if processor.load_csv():
        # Find t-columns
        t_columns = [col for col in processor.data.columns 
                    if col.startswith('t') and col not in ['path_id', 'isnad_id']]
        
        if t_columns:
            # Create dictionaries
            unique_file = processor.create_unique_values_dict(t_columns)
            annotate_file = processor.create_annotation_dict(t_columns)
            
            if unique_file or annotate_file:
                logger.info("Dictionary creation successful")
            else:
                logger.error("Dictionary creation failed")
        else:
            logger.error("No t-columns found in the data")
    else:
        logger.error(f"Failed to load {names_replaced_file}")
    
    # Step 3: Generate Network
    logger.info("Step 3: Network JSON Generation")
    
    from isnad2network.generate_json_network_isnad import process_isnad_network
    
    trans_terms_file = os.path.join(data_dir, "transmissionterms.csv")
    metadata_file = os.path.join(data_dir, "pathmetadata.csv")
    network_output_dir = os.path.join(output_dir, "network")
    os.makedirs(network_output_dir, exist_ok=True)
    
    result = process_isnad_network(
        trans_file=trans_terms_file,
        names_file=names_replaced_file,
        metadata_file=metadata_file,
        output_dir=network_output_dir,
        skip_filtering=False
    )
    
    if result and result.get("status") == "success":
        logger.info(f"Network generation successful: {result.get('node_count')} nodes, {result.get('edge_count')} edges")
        logger.info(f"Output files created in {network_output_dir}")
    else:
        logger.error(f"Network generation failed: {result.get('error', 'Unknown error')}")
    
    # Pipeline summary
    logger.info("Pipeline execution completed")
    logger.info(f"All output files are in {output_dir}")

if __name__ == "__main__":
    logger.info("Starting Isnad2Network example pipeline")
    run_pipeline()
    logger.info("Example pipeline completed")
