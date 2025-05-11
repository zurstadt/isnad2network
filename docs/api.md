# API Reference

This document provides detailed information about the key functions and classes in the Isnad2Network toolkit.

## Command-Line Interface

### `isnad2network_cli.py`

```python
def main()
```

Entry point for the command-line interface.

```python
def run_pipeline(args)
```

Runs the complete pipeline or specified steps based on command-line arguments.

**Parameters:**
- `args` (Namespace): Command line arguments from argparse
  
**Returns:**
- `bool`: Overall success status

```python
def debug_environment()
```

Logs information about the execution environment for troubleshooting.

## Name Replacement Module

### `process_network_names()`

```python
def process_network_names(names_file='names.csv', nodelist_file='nodelist.csv', output_file='names_replaced.csv')
```

Processes network names using the `NetworkNameProcessor`.

**Parameters:**
- `names_file` (str): Path to the names CSV file
- `nodelist_file` (str): Path to the nodelist CSV file
- `output_file` (str): Path to the output CSV file

**Returns:**
- `DataFrame`: The processed DataFrame with replaced names

### `NetworkNameProcessor`

```python
class NetworkNameProcessor(names_file, nodelist_file, output_file=None)
```

Class for processing network names and replacing them based on a mapping.

**Methods:**
- `load_data()`: Load the necessary data files
- `identify_time_columns()`: Identify time step columns in the names dataframe
- `create_mapping()`: Create a mapping dictionary from short_name to name_replace
- `apply_capitalization_rules(text)`: Apply capitalization rules to a text string
- `name_replaces()`: Replace names in the pathways with their mapped values
- `save_results(names_replaced_df)`: Save the results to files
- `analyze_network()`: Analyze the network structure and provide insights
- `process()`: Run the complete processing pipeline

## Dictionary Creation Module

### `CSVDictionaryProcessor`

```python
class CSVDictionaryProcessor()
```

Class to process CSV files and create dictionary outputs.

**Methods:**
- `upload_file()`: Upload a CSV file in Google Colab
- `load_csv(encoding='utf-8', sep=',')`: Load the CSV file and display a preview
- `create_unique_values_dict(columns)`: Create a CSV with unique values from specified columns
- `create_annotation_dict(columns)`: Create a CSV with unique strings, their counts, and annotation columns

## Network Generation Module

### `process_isnad_network()`

```python
def process_isnad_network(trans_file, names_file, metadata_file=None, output_dir="output/network", skip_filtering=False)
```

Main function to process isnad network data.

**Parameters:**
- `trans_file` (str): Path to transmission terms CSV file
- `names_file` (str): Path to names CSV file
- `metadata_file` (str, optional): Path to metadata CSV file
- `output_dir` (str): Directory for output files
- `skip_filtering` (bool): If True, skip filtering out invalid records

**Returns:**
- `dict`: Dictionary with processing results, containing:
  - `status`: "success" or "error"
  - `output_files`: Paths to output files
  - `records_processed`: Number of records processed
  - `node_count`: Number of nodes in the network
  - `edge_count`: Number of edges in the network
  - `error`: Error message (if status is "error")

### `compare_chain_lengths()`

```python
def compare_chain_lengths(names_df, trans_df, output_dir='.')
```

Compare the chain lengths in the names and transmission dataframes.

**Parameters:**
- `names_df` (DataFrame): Names dataframe
- `trans_df` (DataFrame): Transmission terms dataframe
- `output_dir` (str): Directory to save the report

**Returns:**
- `DataFrame`: DataFrame with mismatches

### `generate_network_data()`

```python
def generate_network_data(isnad_data, output_file=None)
```

Generate network graph data from the isnad analysis results.

**Parameters:**
- `isnad_data` (dict): Dictionary containing isnad analysis results
- `output_file` (str, optional): Path to save the network data JSON

**Returns:**
- `dict`: Dictionary with network graph data

### `TransmissionTerm`

```python
class TransmissionTerm(term_text)
```

Class to analyze and classify transmission terms.

**Methods:**
- `_extract_terms()`: Extract individual terms from the text
- `_classify()`: Classify the term based on content
- `to_dict()`: Convert to dictionary representation

### `CellAnalyzer`

```python
class CellAnalyzer(cell_value, cell_id)
```

Class to analyze a single cell in the transmission data.

**Methods:**
- `_analyze()`: Analyze the cell content
- `is_mixed_mode()`: Check if the cell contains mixed mode terms
- `to_dict()`: Convert to dictionary representation

### `IsnadAnalyzer`

```python
class IsnadAnalyzer(trans_df, names_df, metadata_df=None)
```

Class to analyze isnad data across multiple records.

**Methods:**
- `analyze_all_cells()`: Analyze all cells in the transmission dataframe

## Output Data Structures

### Network JSON Format

The `network_graph_data.json` file has the following structure:

```json
{
  "metadata": {
    "generated": "YYYY-MM-DD HH:MM:SS",
    "path_count": 0,
    "node_count": 0,
    "edge_count": 0,
    "source": "Isnad Network Generator"
  },
  "nodes": [
    {
      "id": "n1",
      "name": "Transmitter Name",
      "type": "transmitter"
    }
  ],
  "edges": [
    {
      "id": "e1",
      "source": "n1",
      "target": "n2",
      "type": "riwayah",
      "label": "transmission term",
      "Reader": "reader name",
      "Transmitter": "transmitter name",
      "Path": "path info",
      "mode": "riwayah",
      "path_id": "path_id",
      "isnad_id": "isnad_id"
    }
  ],
  "paths": [
    {
      "path_id": "path_id",
      "isnad_id": "isnad_id",
      "nodes": ["n1", "n2", "n3"],
      "edges": ["e1", "e2"],
      "metadata": {
        "Reader": "reader name",
        "Transmitter": "transmitter name",
        "Path": "path info",
        "_mode": "riwayah"
      }
    }
  ]
}
```

### Isnad Data Format

The `isnad_network_data.json` file has the following structure:

```json
{
  "metadata": {
    "generated": "YYYY-MM-DD HH:MM:SS",
    "rows_analyzed": 0,
    "transmission_columns": ["t0", "t-1", "t-2"],
    "mixed_mode_cells": 0,
    "cells_with_value": 0,
    "unique_terms": 0
  },
  "term_statistics": {
    "by_classification": {
      "riwayah": 0,
      "tilawah": 0,
      "mixed": 0,
      "other": 0,
      "unknown": 0
    }
  },
  "mixed_mode_cells": [
    {
      "path_id": "path_id",
      "column": "t0",
      "value": "transmission term"
    }
  ],
  "paths": [
    {
      "path_id": "path_id",
      "isnad_id": "isnad_id",
      "names": {
        "t0": "name1",
        "t-1": "name2"
      },
      "term_analysis": {
        "t0": {
          "original_text": "term text",
          "terms": ["term1", "term2"],
          "primary_classification": "riwayah"
        }
      },
      "metadata": {
        "Reader": "reader name",
        "Transmitter": "transmitter name",
        "Path": "path info",
        "_mode": "riwayah"
      }
    }
  ]
}
```
