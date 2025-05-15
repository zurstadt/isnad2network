# Usage Guide

This guide provides detailed instructions for using the Isnad2Network toolkit.

## Installation

Install the package from GitHub:

```bash
git clone https://github.com/zurstadt/isnad2network.git
cd isnad2network
pip install -e .
```

Or directly from PyPI (if published):

```bash
pip install isnad2network
```

## Data Preparation

Your data should be organized in CSV files with the following structure:

1. **names.csv**: Contains transmitter names with columns:
   - `path_id`: Unique identifier for each path
   - `isnad_id`: Isnad identifier
   - `t0`, `t-1`, `t-2`, etc.: Transmitter names at different positions

2. **nodelist.csv**: Mapping file with columns:
   - `short_name`: Original name reference
   - `name_replace`: Standardized name

3. **transmissionterms.csv**: Contains transmission terms with columns:
   - `path_id`: Path identifier
   - `isnad_id`: Isnad identifier
   - `t0`, `t-1`, `t-2`, etc.: Transmission terms at different positions

4. **pathmetadata.csv** (optional): Additional metadata with columns:
   - `path_id`: Path identifier
   - `_mode`: Transmission mode
   - `Reader`: Reader name
   - `Transmitter`: Transmitter name
   - `Path`: Path information

## Command-Line Interface

The toolkit provides a command-line interface for running the entire pipeline or individual steps.

### Basic Usage

Run the complete pipeline:

```bash
isnad2network --input-names data/names.csv \
              --nodelist data/nodelist.csv \
              --trans-terms data/transmissionterms.csv \
              --path-metadata data/pathmetadata.csv \
              --output-dir output
```

### Command-Line Arguments

| Argument | Description |
|----------|-------------|
| `--input-names` | Path to the names CSV file (required) |
| `--nodelist` | Path to the nodelist CSV file with mappings (required) |
| `--trans-terms` | Path to the transmission terms CSV file (required) |
| `--path-metadata` | Path to the path metadata CSV file (required) |
| `--output-dir` | Directory to save output files (default: "output") |
| `--steps` | Steps to run: 0=all, 1=name replacement, 2=dictionaries, 3=network JSON |
| `--skip-filtering` | Skip filtering of records with NA values in JSON generation |
| `--version` | Show version information and exit |

### Examples

Run only the name replacement step:

```bash
isnad2network --input-names data/names.csv \
              --nodelist data/nodelist.csv \
              --trans-terms data/transmissionterms.csv \
              --path-metadata data/pathmetadata.csv \
              --output-dir output \
              --steps 1
```

Run only the dictionary creation step:

```bash
isnad2network --input-names data/names.csv \
              --nodelist data/nodelist.csv \
              --trans-terms data/transmissionterms.csv \
              --path-metadata data/pathmetadata.csv \
              --output-dir output \
              --steps 2
```

Run only the network generation step:

```bash
isnad2network --input-names data/names.csv \
              --nodelist data/nodelist.csv \
              --trans-terms data/transmissionterms.csv \
              --path-metadata data/pathmetadata.csv \
              --output-dir output \
              --steps 3
```

Skip filtering of invalid records:

```bash
isnad2network --input-names data/names.csv \
              --nodelist data/nodelist.csv \
              --trans-terms data/transmissionterms.csv \
              --path-metadata data/pathmetadata.csv \
              --output-dir output \
              --skip-filtering
```

## Running in Google Colab

1. Open the notebook `notebooks/isnad2network_colab.ipynb` in Google Colab
2. Run the cells and follow the prompts to upload your data files
3. The notebook will guide you through each processing step
4. Results will be available for download as a ZIP file

## Programmatic Usage

### 1. Name Replacement

Process and standardize names in the transmission chains:

```python
from isnad2network.match_replace_isnads import NetworkNameProcessor

# Initialize processor
processor = NetworkNameProcessor(
    names_file='path/to/names.csv',
    nodelist_file='path/to/nodelist.csv',
    output_file='names_replaced.csv'
)

# Process names
success = processor.process()
if success:
    print("Names replacement completed successfully")
```

### 2. Dictionary Creation

Generate dictionaries for analysis:

```python
from isnad2network.dict_creator import CSVDictionaryProcessor

# Create processor instance
processor = CSVDictionaryProcessor()
processor.input_file = 'names_replaced.csv'
processor.filename_base = 'output/dictionaries/isnad'

# Load data
processor.load_csv()

# Create dictionaries
t_columns = [col for col in processor.data.columns if col.startswith('t') and col not in ['path_id', 'isnad_id']]
processor.create_unique_values_dict(t_columns)
processor.create_annotation_dict(t_columns)
```

### 3. Network Generation

Convert processed data to network format:

```python
from isnad2network.generate_json_network_isnad import process_isnad_network

# Generate network
result = process_isnad_network(
    trans_file='path/to/transmissionterms.csv',
    names_file='names_replaced.csv',
    metadata_file='path/to/pathmetadata.csv',
    output_dir='output/network'
)

# Check results
if result['status'] == 'success':
    print(f"Network generated with {result['node_count']} nodes and {result['edge_count']} edges")
    print(f"Output files: {result['output_files']}")
```

### 4. Running the Complete Pipeline

Run the complete pipeline programmatically:

```python
from isnad2network import process_pipeline
import argparse

# Create arguments similar to command-line usage
args = argparse.Namespace(
    input_names_file='data/names.csv',
    nodelist_file='data/nodelist.csv',
    trans_terms_file='data/transmissionterms.csv',
    path_metadata_file='data/pathmetadata.csv',
    output_dir='output',
    steps=0,  # Run all steps
    skip_filtering=False
)

# Run the pipeline
success = process_pipeline(args)
if success:
    print("Pipeline completed successfully")
else:
    print("Pipeline completed with errors")
```

## Working with the Output

### 1. Replaced Names File

`names_replaced.csv` contains the standardized names for each transmission chain.

### 2. Dictionary Files

- `*_dict_unique.csv`: Contains unique values extracted from specified columns
- `*_dict_annotate.csv`: Contains unique strings, their counts, and annotation columns

### 3. Network Files

- `isnad_network_data.json`: Contains detailed information about the isnad network
- `network_graph_data.json`: Contains the network structure with nodes and edges

### 4. Optional Files

- `unmatched_names.txt`: Contains names that were not found in the mapping

### 5. Visualization

The network JSON files can be loaded into network visualization tools like:

- [Gephi](https://gephi.org/)
- [Cytoscape](https://cytoscape.org/)
- JavaScript libraries like [D3.js](https://d3js.org/) or [Sigma.js](http://sigmajs.org/)

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Ensure you have installed all required packages
2. **File format issues**: Check that your CSV files have the correct format and encoding (UTF-8 recommended)
3. **Path issues**: Use absolute paths if relative paths are causing problems
4. **Memory issues**: For large networks, use a machine with sufficient RAM

### Logging

The toolkit generates detailed logs in the `logs` directory, which can be useful for troubleshooting.

By default, the log file is named `pipeline_YYYYMMDD_HHMMSS.log` with a timestamp.

### Getting Help

If you encounter issues:

1. Check the log files for error messages
2. Review the documentation for correct usage
3. Open an issue on GitHub with a detailed description of the problem
