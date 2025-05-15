#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Isnad Network Generator

This script generates network graph data in JSON format for isnad (chain of narration) analysis.
It processes CSV input files containing transmission terms, names, and metadata,
and outputs JSON files for visualization and analysis.

This code is designed to integrate with the isnad2network_colab.py pipeline
and serves as an enhanced implementation of generate_json_network_isnad.py.

Key enhancements:
- Adds metadata fields (Reader, Transmitter, Path) to edges for better SQL querying
- Improved memory management for large networks
- Better error handling and recovery
- Enhanced file write operations for large files
"""

import pandas as pd
import numpy as np
import os
import json
import warnings
import gc
import traceback
from datetime import datetime
from collections import defaultdict

# Silence warnings
warnings.filterwarnings('ignore', category=UserWarning)

class TransmissionTerm:
    """Class to analyze and classify transmission terms"""
    
    def __init__(self, term_text):
        """Initialize with term text"""
        self.original_text = str(term_text).strip() if pd.notna(term_text) else ""
        self.terms = []
        self.primary_classification = "unknown"
        
        # Extract and classify terms
        if self.original_text:
            self._extract_terms()
            self._classify()
    
    def _extract_terms(self):
        """Extract individual terms from the text"""
        if not self.original_text:
            return
            
        # Simple term extraction by splitting
        raw_terms = self.original_text.replace('،', ',').split(',')
        self.terms = [t.strip() for t in raw_terms if t.strip()]
    
    def _classify(self):
        """Classify the term based on content"""
        if not self.terms:
            return
            
        # Basic classification logic
        riwayah_indicators = ['حدثنا', 'أخبرنا', 'سمعت', 'عن', 'روى']
        tilawah_indicators = ['قرأت', 'قرأ', 'تلا']
        
        # Check for mixed mode
        has_riwayah = any(ri in self.original_text for ri in riwayah_indicators)
        has_tilawah = any(ti in self.original_text for ti in tilawah_indicators)
        
        # Set primary classification
        if has_riwayah and has_tilawah:
            self.primary_classification = "mixed"
        elif has_riwayah:
            self.primary_classification = "riwayah"
        elif has_tilawah:
            self.primary_classification = "tilawah"
        else:
            self.primary_classification = "other"
    
    def to_dict(self):
        """Convert to dictionary representation"""
        return {
            "original_text": self.original_text,
            "terms": self.terms,
            "primary_classification": self.primary_classification
        }


class CellAnalyzer:
    """Class to analyze a single cell in the transmission data"""
    
    def __init__(self, cell_value, cell_id):
        """Initialize with cell value and ID"""
        self.cell_value = cell_value
        self.cell_id = cell_id
        self.is_empty = pd.isna(cell_value) or cell_value == ""
        self.terms = []
        self.analysis = None
        
        # Analyze if not empty
        if not self.is_empty:
            self._analyze()
    
    def _analyze(self):
        """Analyze the cell content"""
        # Create a transmission term object
        self.analysis = TransmissionTerm(self.cell_value)
        
    def is_mixed_mode(self):
        """Check if the cell contains mixed mode terms"""
        if self.is_empty or not self.analysis:
            return False
        return self.analysis.primary_classification == "mixed"
    
    def to_dict(self):
        """Convert to dictionary representation"""
        if self.is_empty:
            return None
        return self.analysis.to_dict()


class IsnadAnalyzer:
    """Class to analyze isnad data across multiple records"""
    
    def __init__(self, trans_df, names_df, metadata_df=None):
        """Initialize with dataframes"""
        self.trans_df = trans_df if trans_df is not None else pd.DataFrame()
        self.names_df = names_df if names_df is not None else pd.DataFrame()
        self.metadata_df = metadata_df
        
        # Track statistics
        self.mixed_mode_cells = []
        self.cells_with_value_count = 0
        self.cell_analyses = {}
        
        # Get transmission columns - handle empty dataframes
        self.trans_columns = []
        if not self.trans_df.empty:
            self.trans_columns = [col for col in self.trans_df.columns 
                                if col.startswith('t') and col != 'path_id' and col != 'isnad_id']
        
        # Track unique terms
        self.unique_terms = set()
    
    def analyze_all_cells(self):
        """Analyze all cells in the transmission dataframe"""
        if self.trans_df.empty:
            print("No transmission data to analyze")
            return
            
        print(f"Analyzing {len(self.trans_df)} records with {len(self.trans_columns)} transmission columns...")
        
        # Process in chunks for memory efficiency
        chunk_size = 100
        for start_idx in range(0, len(self.trans_df), chunk_size):
            end_idx = min(start_idx + chunk_size, len(self.trans_df))
            chunk = self.trans_df.iloc[start_idx:end_idx]
            
            # Process each row in the chunk
            for idx, row in chunk.iterrows():
                path_id = row.get('path_id', idx)
                
                # Process each transmission column
                for col in self.trans_columns:
                    if col in row:
                        cell_value = row[col]
                        if pd.notna(cell_value) and cell_value != "":
                            self.cells_with_value_count += 1
                            
                            # Create unique cell ID
                            cell_id = f"{path_id}_{col}"
                            
                            # Analyze cell
                            analyzer = CellAnalyzer(cell_value, cell_id)
                            
                            # Store analysis
                            if not analyzer.is_empty:
                                self.cell_analyses[cell_id] = analyzer
                                
                                # Track if mixed mode
                                if analyzer.is_mixed_mode():
                                    self.mixed_mode_cells.append({
                                        "path_id": path_id,
                                        "column": col,
                                        "value": cell_value
                                    })
                                
                                # Track unique terms
                                if analyzer.analysis and analyzer.analysis.original_text:
                                    self.unique_terms.add(analyzer.analysis.original_text)
            
            # Force garbage collection to manage memory
            gc.collect()
        
        print(f"Found {len(self.mixed_mode_cells)} mixed-mode cells")
        print(f"Found {self.cells_with_value_count} cells with values")
        print(f"Found {len(self.unique_terms)} unique transmission terms")


def generate_network_data(isnad_data, output_file=None):
    """
    Generate network graph data from the isnad analysis results.
    
    Args:
        isnad_data: Dictionary containing isnad analysis results
        output_file: Path to save the network data JSON (optional)
        
    Returns:
        Dictionary with network graph data
    """
    print("\nGenerating network graph data...")
    
    # Validate input
    if isnad_data is None:
        print("⚠️ Cannot generate network: isnad_data is None")
        # Create minimal network structure
        network = {
            "metadata": {
                "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "path_count": 0,
                "node_count": 0,
                "edge_count": 0,
                "source": "Isnad Network Generator (Error Recovery)"
            },
            "nodes": [],
            "edges": [],
            "paths": []
        }
        
        # Save minimal network data if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(network, f, ensure_ascii=False, indent=2)
                print(f"✅ Created minimal network graph output at {output_file}")
            except Exception as e:
                print(f"Error writing network data: {e}")
        
        return network
    
    # Initialize network structure
    network = {
        "metadata": {
            "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "path_count": len(isnad_data.get('paths', [])),
            "source": "Isnad Network Generator"
        },
        "nodes": [],
        "edges": [],
        "paths": []
    }
    
    # Get paths
    paths = isnad_data.get('paths', [])
    if not paths:
        print("⚠️ No paths found in isnad_data")
        network["metadata"]["node_count"] = 0
        network["metadata"]["edge_count"] = 0
        
        # Save minimal network data if requested
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(network, f, ensure_ascii=False, indent=2)
                print(f"✅ Created minimal network graph output at {output_file}")
            except Exception as e:
                print(f"Error writing network data: {e}")
        
        return network
    
    # Track unique nodes and edges
    unique_nodes = set()
    node_dict = {}  # name -> node_id
    unique_edges = set()  # (source, target, type) tuples
    
    # Process each path
    print(f"Processing {len(paths)} paths to build network...")
    
    for path_idx, path in enumerate(paths):
        # Safely get path_id and isnad_id
        path_id = path.get('path_id', f"unknown_{path_idx}")
        isnad_id = path.get('isnad_id', "")
        
        # Get names data and transmission terms
        names = path.get('names', {})
        term_analysis = path.get('term_analysis', {})
        
        # Get metadata if available
        metadata = path.get('metadata', {})
        
        # Extract specific metadata fields that we'll include on edges
        reader = metadata.get('Reader', '')
        transmitter = metadata.get('Transmitter', '')
        path_info = metadata.get('Path', '')
        mode = metadata.get('_mode', '')
        
        # Create a path entry with metadata
        path_entry = {
            "path_id": path_id,
            "isnad_id": isnad_id,
            "nodes": [],
            "edges": [],
            "metadata": metadata
        }
        
        # Process nodes and edges in the path
        t_columns = sorted([col for col in names.keys() 
                          if isinstance(col, str) and col.startswith('t') 
                          and col != 'path_id' and col != 'isnad_id'])
        
        for i in range(len(t_columns)):
            col = t_columns[i]
            if col in names and names[col]:
                # Process node
                name = names[col]
                if name not in node_dict:
                    node_id = f"n{len(node_dict) + 1}"
                    node_dict[name] = node_id
                    unique_nodes.add(name)
                    network["nodes"].append({
                        "id": node_id,
                        "name": name,
                        "type": "transmitter"
                    })
                
                # Add node to path
                path_entry["nodes"].append(node_dict[name])
                
                # Process edge if not the last node
                if i < len(t_columns) - 1 and t_columns[i+1] in names and names[t_columns[i+1]]:
                    next_name = names[t_columns[i+1]]
                    if next_name in node_dict:
                        source_id = node_dict[name]
                        target_id = node_dict[next_name]
                        
                        # Get transmission term if available
                        edge_type = "unknown"
                        if col in term_analysis and term_analysis[col] is not None:
                            classification = term_analysis[col].get('primary_classification')
                            if classification:
                                edge_type = classification
                        
                        edge_key = (source_id, target_id, edge_type)
                        if edge_key not in unique_edges:
                            edge_id = f"e{len(unique_edges) + 1}"
                            unique_edges.add(edge_key)
                            
                            # Create edge with details
                            edge_data = {
                                "id": edge_id,
                                "source": source_id,
                                "target": target_id,
                                "type": edge_type,
                                # Add metadata fields to edge for better querying
                                "Reader": reader,
                                "Transmitter": transmitter,
                                "Path": path_info,
                                "mode": mode,
                                "path_id": path_id,
                                "isnad_id": isnad_id
                            }
                            
                            # Add transmission term details if available
                            if col in term_analysis and term_analysis[col] is not None:
                                original_text = term_analysis[col].get('original_text', '')
                                if original_text:
                                    edge_data["label"] = original_text
                                
                                # Add detailed term classifications
                                terms = term_analysis[col].get('terms', [])
                                if terms:
                                    edge_data["terms"] = terms
                            
                            network["edges"].append(edge_data)
                            
                            # Add edge to path
                            path_entry["edges"].append(edge_id)
        
        # Add path to network if it has nodes
        if path_entry["nodes"]:
            network["paths"].append(path_entry)
    
    # Add summary statistics
    network["metadata"]["node_count"] = len(network["nodes"])
    network["metadata"]["edge_count"] = len(network["edges"])
    
    # Add metadata statistics if available
    if any('metadata' in path and path['metadata'] for path in paths):
        # Count paths with metadata
        paths_with_metadata = sum(1 for path in paths if 'metadata' in path and path['metadata'])
        network["metadata"]["paths_with_metadata"] = paths_with_metadata
    
    # Save to file if specified
    if output_file:
        try:
            print(f"Writing network data to {output_file}...")
            # Use chunked writing for better memory efficiency with large networks
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write opening and metadata
                f.write('{\n')
                f.write(f'  "metadata": {json.dumps(network["metadata"], ensure_ascii=False)},\n')

                # Write nodes array
                f.write('  "nodes": [\n')
                for i, node in enumerate(network["nodes"]):
                    if i < len(network["nodes"]) - 1:
                        f.write(f"    {json.dumps(node, ensure_ascii=False)},\n")
                    else:
                        f.write(f"    {json.dumps(node, ensure_ascii=False)}\n")
                f.write('  ],\n')

                # Write edges array
                f.write('  "edges": [\n')
                for i, edge in enumerate(network["edges"]):
                    if i < len(network["edges"]) - 1:
                        f.write(f"    {json.dumps(edge, ensure_ascii=False)},\n")
                    else:
                        f.write(f"    {json.dumps(edge, ensure_ascii=False)}\n")
                f.write('  ],\n')

                # Write paths array
                f.write('  "paths": [\n')
                for i, path in enumerate(network["paths"]):
                    if i < len(network["paths"]) - 1:
                        f.write(f"    {json.dumps(path, ensure_ascii=False)},\n")
                    else:
                        f.write(f"    {json.dumps(path, ensure_ascii=False)}\n")
                f.write('  ]\n')

                # Close JSON
                f.write('}')
                
            print(f"✅ Network graph data saved to {output_file}")
            print(f"  Contains {len(network['nodes'])} nodes and {len(network['edges'])} edges")
        except Exception as e:
            print(f"Error writing network data: {e}")
            # Try alternative simpler method
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(network, f, ensure_ascii=False)
                print(f"✅ Used simplified method to save network data")
            except Exception as e2:
                print(f"Failed to save network data: {e2}")
    
    return network


def process_isnad_network(trans_file, names_file, metadata_file=None, output_dir="output/network", skip_filtering=False):
    """
    Main function to process isnad network data.
    Designed to be compatible with the isnad2network_colab.py pipeline.
    
    Args:
        trans_file: Path to transmission terms CSV file
        names_file: Path to names CSV file (typically names_replaced.csv from the previous step)
        metadata_file: Path to metadata CSV file (optional)
        output_dir: Directory for output files
        skip_filtering: If True, skip filtering out invalid records
        
    Returns:
        Dictionary with processing results, compatible with the pipeline
    """
    print(f"\nProcessing isnad network data...")
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read input files
    try:
        print(f"Reading transmission terms from {trans_file}...")
        trans_df = pd.read_csv(trans_file)
        print(f"  Found {len(trans_df)} records with {len(trans_df.columns)} columns")
        
        print(f"Reading names from {names_file}...")
        names_df = pd.read_csv(names_file)
        print(f"  Found {len(names_df)} records with {len(names_df.columns)} columns")
        
        metadata_df = None
        if metadata_file:
            print(f"Reading metadata from {metadata_file}...")
            metadata_df = pd.read_csv(metadata_file)
            print(f"  Found {len(metadata_df)} records with {len(metadata_df.columns)} columns")
    except Exception as e:
        print(f"Error reading input files: {e}")
        return {
            "status": "error",
            "error": f"Failed to read input files: {str(e)}"
        }
    
    # Check dimensions between dataframes
    def check_dimensions(names_df, trans_df, metadata_df=None):
        """Check if the dimensions of the dataframes match as expected."""
        is_valid = True
        mismatch_details = {}
        
        # Check if path_id is in both dataframes
        if 'path_id' not in names_df.columns:
            is_valid = False
            mismatch_details["missing_path_id_in_names"] = True
        
        if 'path_id' not in trans_df.columns:
            is_valid = False
            mismatch_details["missing_path_id_in_trans"] = True
        
        # Check if row counts match
        if len(names_df) != len(trans_df):
            is_valid = False
            mismatch_details["row_count_mismatch"] = {
                "names_df": len(names_df),
                "trans_df": len(trans_df)
            }
        
        # Check if metadata_df has path_id
        if metadata_df is not None:
            if 'path_id' not in metadata_df.columns:
                is_valid = False
                mismatch_details["missing_path_id_in_metadata"] = True
        
        return is_valid, mismatch_details
    
    # Filter invalid records
    def filter_invalid_records(names_df, trans_df, metadata_df=None):
        """Filter out records with NA values in critical columns."""
        original_count = len(names_df)
        
        # Ensure path_id exists in both dataframes
        if 'path_id' not in names_df.columns or 'path_id' not in trans_df.columns:
            print("⚠️ Cannot filter records: missing path_id column in one or both dataframes")
            return names_df, trans_df, metadata_df, 0
        
        # Find valid path_ids (not NA in either dataframe)
        valid_name_ids = names_df[pd.notna(names_df['path_id'])]['path_id'].unique()
        valid_trans_ids = trans_df[pd.notna(trans_df['path_id'])]['path_id'].unique()
        
        # Find common valid path_ids
        valid_ids = set(valid_name_ids).intersection(set(valid_trans_ids))
        
        # Filter dataframes
        names_df = names_df[names_df['path_id'].isin(valid_ids)].reset_index(drop=True)
        trans_df = trans_df[trans_df['path_id'].isin(valid_ids)].reset_index(drop=True)
        
        # Filter metadata if provided
        if metadata_df is not None and 'path_id' in metadata_df.columns:
            metadata_df = metadata_df[metadata_df['path_id'].isin(valid_ids)].reset_index(drop=True)
        
        # Calculate filtered count
        filtered_count = original_count - len(names_df)
        
        return names_df, trans_df, metadata_df, filtered_count
    
    # Check dimensions
    is_valid, mismatch_details = check_dimensions(names_df, trans_df, metadata_df)
    
    if not is_valid and not skip_filtering:
        print(f"⚠️ Dimension mismatch detected: {mismatch_details}")
        print("Filtering invalid records...")
        names_df, trans_df, metadata_df, filtered_count = filter_invalid_records(names_df, trans_df, metadata_df)
        print(f"Filtered {filtered_count} records")
    
    # Initialize analyzer
    analyzer = IsnadAnalyzer(trans_df, names_df, metadata_df)
    
    # Analyze cells
    analyzer.analyze_all_cells()
    
    # Generate isnad data
    isnad_data = {
        "metadata": {
            "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "rows_analyzed": len(analyzer.trans_df),
            "transmission_columns": analyzer.trans_columns,
            "mixed_mode_cells": len(analyzer.mixed_mode_cells),
            "cells_with_value": analyzer.cells_with_value_count,
            "unique_terms": len(analyzer.unique_terms)
        },
        "term_statistics": {
            "by_classification": {}
        },
        "mixed_mode_cells": analyzer.mixed_mode_cells,
        "paths": []
    }
    
    # Get classification statistics
    classifications = defaultdict(int)
    for cell_id, cell_analyzer in analyzer.cell_analyses.items():
        if cell_analyzer.analysis:
            classification = cell_analyzer.analysis.primary_classification
            classifications[classification] += 1
    
    isnad_data["term_statistics"]["by_classification"] = dict(classifications)
    
    # Process paths
    print("Building path data...")
    
    # Process each row in names_df
    for idx, row in names_df.iterrows():
        # Safely get path_id, defaulting to index if not present
        path_id = row.get('path_id', idx) if 'path_id' in row else idx
        isnad_id = row.get('isnad_id', "") if 'isnad_id' in row else ""
        
        # Get metadata if available
        metadata = {}
        if metadata_df is not None and not metadata_df.empty and 'path_id' in metadata_df.columns:
            meta_row = metadata_df[metadata_df['path_id'] == path_id]
            if not meta_row.empty:
                for col in meta_row.columns:
                    if col != 'path_id':
                        value = meta_row.iloc[0][col]
                        if pd.notna(value):
                            metadata[col] = value
        
        # Create path entry
        path_entry = {
            "path_id": path_id,
            "isnad_id": isnad_id,
            "names": {},
            "term_analysis": {},
            "metadata": metadata
        }
        
        # Add name columns
        name_columns = [col for col in row.index 
                       if isinstance(col, str) and col.startswith('t') 
                       and col != 'path_id' and col != 'isnad_id']
        
        for col in name_columns:
            name = row[col]
            if pd.notna(name) and name != "":
                path_entry["names"][col] = name
        
        # Add transmission terms analysis
        if not analyzer.trans_df.empty and 'path_id' in analyzer.trans_df.columns:
            trans_row = analyzer.trans_df[analyzer.trans_df['path_id'] == path_id]
            if not trans_row.empty:
                for col in analyzer.trans_columns:
                    if col in trans_row.columns:
                        cell_id = f"{path_id}_{col}"
                        if cell_id in analyzer.cell_analyses:
                            cell_analyzer = analyzer.cell_analyses[cell_id]
                            path_entry["term_analysis"][col] = cell_analyzer.to_dict()
        
        # Add to paths
        isnad_data["paths"].append(path_entry)
    
    # Define output file paths to match pipeline expectations
    isnad_output_file = os.path.join(output_dir, "isnad_network_data.json")
    network_output_file = os.path.join(output_dir, "network_graph_data.json")
    
    # Save isnad data
    try:
        print(f"Writing isnad data to {isnad_output_file}...")
        with open(isnad_output_file, 'w', encoding='utf-8') as f:
            json.dump(isnad_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Isnad data saved to {isnad_output_file}")
    except Exception as e:
        print(f"Error writing isnad data: {e}")
        return {
            "status": "error",
            "error": f"Failed to write isnad data: {str(e)}"
        }
    
    # Generate network data
    network_data = generate_network_data(isnad_data, network_output_file)
    
    # Prepare and return pipeline-compatible result
    result = {
        "status": "success",
        "output_files": {
            "isnad_data": isnad_output_file,
            "network_graph": network_output_file
        },
        "records_processed": len(names_df),
        "unique_terms": len(analyzer.unique_terms),
        "node_count": network_data["metadata"]["node_count"],
        "edge_count": network_data["metadata"]["edge_count"]
    }
    
    return result


def create_sample_data(output_dir='sample_data'):
    """Create sample CSV files for testing"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create sample transmission terms
    trans_df = pd.DataFrame({
        'path_id': range(1, 11),
        'isnad_id': [f'jb_{i:03d}' for i in range(1, 11)],
        't1': ['حدثنا', 'أخبرنا', 'عن', 'قرأت', 'سمعت', 'روى', 'قرأ', 'حدثنا', 'أخبرنا', 'قرأت عن'],
        't2': ['حدثنا', 'أخبرنا', 'عن', 'قرأت', '', 'روى', 'قرأ', 'حدثنا', 'أخبرنا', ''],
        't3': ['', '', '', '', '', '', '', '', '', ''],
    })
    
    # Create sample names
    names_df = pd.DataFrame({
        'path_id': range(1, 11),
        'isnad_id': [f'jb_{i:03d}' for i in range(1, 11)],
        't1': ['نافع', 'ابن كثير', 'أبو عمرو', 'ابن عامر', 'عاصم', 'حمزة', 'الكسائي', 'أبو جعفر', 'يعقوب', 'خلف'],
        't2': ['قالون', 'البزي', 'الدوري', 'هشام', 'أبو بكر', 'خلف', 'الدوري', 'ابن وردان', 'رويس', 'إسحاق'],
        't3': ['ورش', 'قنبل', 'السوسي', 'ابن ذكوان', 'حفص', 'خلاد', 'أبو الحارث', 'ابن جماز', 'روح', 'إدريس'],
    })
    
    # Create sample metadata
    metadata_df = pd.DataFrame({
        'path_id': range(1, 11),
        '_mode': ['riwayah', 'tilawah', 'riwayah', 'tilawah', 'riwayah', 'tilawah', 'riwayah', 'tilawah', 'riwayah', 'mixed'],
        'Reader': ['Nāfiʿ', 'Ibn Kaṯīr', 'ʾAbū ʿAmr', 'Ibn ʿĀmir', 'ʿĀṣim', 'Ḥamzah', 'al-Kisāʾī', 'ʾAbū Ǧaʿfar', 'Yaʿqūb', 'Ḫalaf'],
        'Path': ['al-Dūrī', 'al-Bazzī', 'al-Sūsī', 'Hišām', 'Ḥafṣ', 'Ḫalaf', 'ʾAbū al-Ḥāriṯ', 'Ibn Wardān', 'Ruwais', 'ʾIsḥāq'],
    })
    
    # Save to CSV
    trans_df.to_csv(f"{output_dir}/transmission_terms.csv", index=False)
    names_df.to_csv(f"{output_dir}/names.csv", index=False)
    metadata_df.to_csv(f"{output_dir}/metadata.csv", index=False)
    
    print(f"✅ Sample data files created in {output_dir}")
    
    return trans_df, names_df, metadata_df


def main():
    """Main function"""
    print("""
    ===============================================================
    Isnad Network Generator
    ===============================================================
    
    This script analyzes isnad data from transmission terms and names files
    to generate network representations for further analysis.
    
    Key features:
    - Consistent indexing by path_id throughout all processing
    - Adds metadata to edges for enhanced querying capabilities
    - Improved memory management for large datasets
    - Robust error handling and recovery
    - Enhanced chain-length comparison algorithm
    - Full compatibility with Google Colab and the isnad2network_colab.py pipeline
    ===============================================================
    """)
    
    # Check if running in Google Colab
    try:
        import google.colab
        is_colab = True
        print("Running in Google Colab environment")
    except ImportError:
        is_colab = False
        print("Running in local environment")
    
    # Create sample data if needed
    create_sample = input("Create sample data for testing? (y/n): ").strip().lower() == 'y'
    
    if create_sample:
        sample_dir = 'sample_data'
        trans_df, names_df, metadata_df = create_sample_data(sample_dir)
        
        # Process sample data
        result = process_isnad_network(
            trans_file=f"{sample_dir}/transmission_terms.csv",
            names_file=f"{sample_dir}/names.csv",
            metadata_file=f"{sample_dir}/metadata.csv",
            output_dir=f"{sample_dir}/output/network"
        )
        
        # Display result
        if result["status"] == "success":
            print("\n✅ Sample data processed successfully!")
            print(f"Records processed: {result['records_processed']}")
            print(f"Unique terms: {result['unique_terms']}")
            print(f"Network: {result['node_count']} nodes, {result['edge_count']} edges")
            print("\nOutput files:")
            for name, path in result["output_files"].items():
                print(f"- {name}: {path}")
        else:
            print(f"\n❌ Error processing sample data: {result.get('error', 'Unknown error')}")
    else:
        # Get input from user
        if is_colab:
            # When running in Colab, use default paths expected by the pipeline
            trans_file = input("Enter path to transmission terms CSV file (default: transmissionterms.csv): ").strip() or 'transmissionterms.csv'
            names_file = input("Enter path to names CSV file (default: output/data/names_replaced.csv): ").strip() or 'output/data/names_replaced.csv'
            metadata_file = input("Enter path to metadata CSV file (default: pathmetadata.csv): ").strip() or 'pathmetadata.csv'
            output_dir = input("Enter output directory (default: output/network): ").strip() or 'output/network'
        else:
            trans_file = input("Enter path to transmission terms CSV file: ").strip()
            names_file = input("Enter path to names CSV file: ").strip()
            metadata_file = input("Enter path to metadata CSV file (leave empty if none): ").strip()
            output_dir = input("Enter output directory (default: output/network): ").strip() or 'output/network'
        
        if not metadata_file:
            metadata_file = None
        
        # Process data
        result = process_isnad_network(
            trans_file=trans_file,
            names_file=names_file,
            metadata_file=metadata_file,
            output_dir=output_dir
        )
        
        # Display result
        if result["status"] == "success":
            print("\n✅ Isnad data processed successfully!")
            print(f"Records processed: {result['records_processed']}")
            print(f"Unique terms: {result['unique_terms']}")
            print(f"Network: {result['node_count']} nodes, {result['edge_count']} edges")
            print("\nOutput files:")
            for name, path in result["output_files"].items():
                print(f"- {name}: {path}")
                
            # Offer to download files if in Colab
            if is_colab:
                try:
                    from google.colab import files
                    download = input("\nDownload output files? (y/n): ").strip().lower() == 'y'
                    if download:
                        for path in result["output_files"].values():
                            files.download(path)
                        print("✅ Files downloaded")
                except Exception as e:
                    print(f"⚠️ Error during download: {e}")
        else:
            print(f"\n❌ Error processing data: {result.get('error', 'Unknown error')}")


# Add a compatibility function to match the original script's expected interface
def compare_chain_lengths(names_df, trans_df, output_dir='.'):
    """
    Compare the chain lengths in the names and transmission dataframes.
    Creates a report of mismatches.
    
    Args:
        names_df: Names dataframe
        trans_df: Transmission terms dataframe
        output_dir: Directory to save the report
        
    Returns:
        DataFrame with mismatches
    """
    print("\nComparing chain lengths between names and transmission terms...")
    
    # Safety checks
    if names_df is None or trans_df is None:
        print("⚠️ Cannot compare chain lengths: one or both dataframes are None")
        return pd.DataFrame()
    
    # Ensure path_id exists in both dataframes
    if 'path_id' not in names_df.columns or 'path_id' not in trans_df.columns:
        print("⚠️ Cannot compare chain lengths: missing path_id column in one or both dataframes")
        return pd.DataFrame()
    
    # Create empty dataframe for mismatches
    mismatch_df = pd.DataFrame(columns=[
        'path_id', 'names_length', 'trans_length', 'difference'
    ])
    
    # Get t-columns (safely handle column types)
    name_t_cols = [col for col in names_df.columns 
                  if isinstance(col, str) and col.startswith('t') 
                  and col != 'path_id' and col != 'isnad_id']
    trans_t_cols = [col for col in trans_df.columns 
                   if isinstance(col, str) and col.startswith('t') 
                   and col != 'path_id' and col != 'isnad_id']
    
    # Sort columns to ensure proper comparison
    name_t_cols.sort()
    trans_t_cols.sort()
    
    # Process each unique path_id
    mismatches = []
    unique_path_ids = names_df['path_id'].unique()
    
    for path_id in unique_path_ids:
        # Get matching rows
        names_rows = names_df[names_df['path_id'] == path_id]
        trans_rows = trans_df[trans_df['path_id'] == path_id]
        
        if len(names_rows) == 0 or len(trans_rows) == 0:
            print(f"⚠️ Missing data for path_id {path_id}")
            continue
        
        # Use first row for this path_id
        names_row = names_rows.iloc[0]
        trans_row = trans_rows.iloc[0]
        
        # Count non-NA values in names
        names_count = sum(1 for col in name_t_cols 
                          if col in names_row and pd.notna(names_row[col]) and names_row[col] != "")
        
        # Count non-NA values in transmission terms
        trans_count = sum(1 for col in trans_t_cols 
                          if col in trans_row and pd.notna(trans_row[col]) and trans_row[col] != "")
        
        # Check if counts match
        if names_count != trans_count:
            mismatches.append({
                'path_id': path_id,
                'names_length': names_count,
                'trans_length': trans_count,
                'difference': names_count - trans_count
            })
    
    # Create dataframe from mismatches
    if mismatches:
        mismatch_df = pd.DataFrame(mismatches)
        
        # Save to file
        report_path = os.path.join(output_dir, "chain_length_mismatches.csv")
        mismatch_df.to_csv(report_path, index=False)
        print(f"⚠️ Found {len(mismatch_df)} chains with length mismatches between names and transmission terms")
        print(f"⚠️ Saved mismatch report to {report_path}")
    else:
        print("✅ No chain length mismatches found!")
    
    return mismatch_df

# Provide all the necessary functions to make the script compatible with the pipeline
__all__ = [
    'TransmissionTerm',
    'CellAnalyzer', 
    'IsnadAnalyzer',
    'compare_chain_lengths',
    'generate_network_data',
    'process_isnad_network'
]

if __name__ == "__main__":
    main()