# Isnad2Network: Islamic Transmission Chain Analysis Toolkit

Isnad2Network is a toolkit designed for analyzing and visualizing isnad (chains of transmission) data from Islamic scholarly traditions. The toolkit provides tools for processing, analyzing, and generating network visualizations from transmission chain data.

## Overview

This toolkit allows researchers to convert raw isnad data into network representations for advanced analysis. An isnad is a chain of authorities who have transmitted a report (hadith) of a statement, action, or approbation of Muhammad, one of his Companions, or a later authority. The toolkit helps analyze these chains as network graphs.

The pipeline consists of several key components:

1. **Name Replacement**: Processes and standardizes names in the transmission chains
2. **Dictionary Creation**: Generates dictionaries of terms and names for analysis
3. **Network Generation**: Converts processed data into network graph representations
4. **Visualization**: Exports the data in JSON format for visualization in external tools

## Dataset Description

The repository includes a toy dataset for testing and demonstration purposes. The dataset contains transmission chains with the following files:

### `names.csv`
Contains the names of transmitters in the isnad chains, with each row representing a single path:
- `path_id`: Unique identifier for each transmission path
- `isnad_id`: Identifier for the isnad (chain)
- `t0`, `t-1`, `t-2`, etc.: Columns representing transmitters at different positions in the chain, with `t0` being the earliest/source transmitter

### `nodelist.csv`
Mapping file for standardizing names across the network:
- Contains mappings between short names and standardized replacement names for transmitters
- Used to harmonize different spellings or references to the same individual

### `pathmetadata.csv`
Additional metadata about each transmission path:
- `path_id`: Link to the paths in other files
- `isnad_id`: Identifier for the isnad
- `_mode`: Transmission mode (e.g., "riwayah", "tilawah", "mixed")
- `Reader`: The original reader/source
- `Transmitter`: The transmitter
- `Path`: Information about the path

### `transmissionterms.csv`
Contains the transmission terms used between individuals in the chain:
- `path_id`: Identifier for the path
- `isnad_id`: Identifier for the isnad
- `t0`, `t-1`, `t-2`, etc.: Transmission terms used at each step in the chain

## Component Scripts

### `match_replace_isnads.py`
Processes network pathways and replaces node names based on mappings from `nodelist.csv`.

Key features:
- Applies standardized naming conventions to nodes
- Implements specific capitalization rules for Arabic names
- Tracks unmatched names for further curation
- Produces `names_replaced.csv` for further processing

### `2dict.py`
Creates dictionary files for analysis:
- Extracts unique values from specified columns
- Generates annotation dictionaries for terms
- Creates files for machine learning training

### `generate_json_network_isnad.py`
Generates JSON files for network visualization and analysis:
- Processes transmission terms and names
- Classifies transmission terms (riwayah, tilawah, mixed)
- Builds a network graph with nodes (transmitters) and edges (relationships)
- Attaches metadata to edges for enhanced querying

### `isnad2network_colab.ipynb`
Notebook script for running the pipeline in Google Colab:
- Handles file uploads in Google Colab environment
- Coordinates data processing through the three main components
- Packages results for download
- Provides error handling and recovery

### `isnad2network_cli.py`
Command-line interface for running the pipeline locally:
- Processes files from local filesystem
- Provides step-by-step execution with detailed logging
- Offers flexible configuration through command-line arguments
- Supports running individual steps or the complete pipeline

## Using the Toolkit

### Requirements
- Python 3.6+
- pandas
- numpy
- Google Colab (for interactive use with `isnad2network_colab.ipynb`)

### Command-Line Usage

Run the complete pipeline:

```bash
python src/isnad2network_cli.py --input-names-file data/names.csv \
                               --nodelist-file data/nodelist.csv \
                               --trans-terms-file data/transmissionterms.csv \
                               --path-metadata-file data/pathmetadata.csv \
                               --output-dir output
```

Run specific steps:

```bash
# Only run the name replacement step
python src/isnad2network_cli.py --input-names-file data/names.csv \
                               --nodelist-file data/nodelist.csv \
                               --trans-terms-file data/transmissionterms.csv \
                               --output-dir output \
                               --steps 1

# Only run the network generation step
python src/isnad2network_cli.py --input-names-file data/names.csv \
                               --nodelist-file data/nodelist.csv \
                               --trans-terms-file data/transmissionterms.csv \
                               --path-metadata-file data/pathmetadata.csv \
                               --output-dir output \
                               --steps 3
```

Additional options:
- `--skip-filtering`: Skip filtering of invalid records during network generation
- `--compare-chains`: Compare chain lengths between names and transmission terms

### Google Colab Usage

1. Open the notebook `notebooks/isnad2network_colab.ipynb` in Google Colab
2. Run the cells and follow the prompts to upload your data files
3. The notebook will guide you through each processing step
4. Results will be available for download as a ZIP file

### Processing Steps in Python

1. **Name Replacement**:
   ```python
   from isnad2network.match_replace_isnads import process_network_names
   
   names_replaced_df = process_network_names(
       names_file='names.csv',
       nodelist_file='nodelist.csv',
       output_file='names_replaced.csv'
   )
   ```

2. **Dictionary Creation**:
   ```python
   from isnad2network.dict_creator import CSVDictionaryProcessor
   
   processor = CSVDictionaryProcessor()
   processor.input_file = 'names_replaced.csv'
   processor.load_csv()
   processor.create_unique_values_dict(['t0', 't-1', 't-2'])
   processor.create_annotation_dict(['t0', 't-1', 't-2'])
   ```

3. **Network Generation**:
   ```python
   from isnad2network.generate_json_network_isnad import process_isnad_network
   
   result = process_isnad_network(
       trans_file='transmissionterms.csv',
       names_file='names_replaced.csv',
       metadata_file='pathmetadata.csv',
       output_dir='output/network'
   )
   ```

## Network Analysis

The resulting JSON files can be used with network visualization tools to analyze:

- Centrality of transmitters
- Community detection in transmission networks
- Path analysis between specific transmitters
- Temporal patterns in transmission chains
- Classification of transmission methods

## Output Files

### Name Replacement
- `names_replaced.csv`: Standardized names for the network

### Dictionary Creation
- `*_dict_unique.csv`: Unique values extracted from specified columns
- `*_dict_annotate.csv`: Unique strings, their counts, and annotation columns

### Network Generation
- `isnad_network_data.json`: Detailed data about the network
- `network_graph_data.json`: Network graph for visualization
- `chain_length_mismatches.csv` (optional): Mismatches between names and transmission terms

## Citation and License

[Add your preferred citation format and license information here]

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.
