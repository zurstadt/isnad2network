# isnad2network

[![PyPI version](https://img.shields.io/pypi/v/isnad2network.svg)](https://pypi.org/project/isnad2network/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python toolkit for processing, analyzing, and visualizing isnad chains (chains of transmission in Islamic texts).

## Overview

`isnad2network` converts traditional isnad chains from textual formats into structured network data for analysis and visualization. The package helps scholars and researchers to:

1. **Standardize Names**: Map various spellings and forms of transmitter names to standardized versions
2. **Create Dictionaries**: Generate annotation dictionaries for isnad terms and components
3. **Generate Networks**: Convert processed data into network formats for visualization and analysis
4. **Analyze Transmission**: Classify transmission methods and relationships between narrators

## Installation

```bash
pip install isnad2network
```

Or install from source:

```bash
git clone https://github.com/zurstadt/isnad2network.git
cd isnad2network
pip install -e .
```

## Quick Start

```python
from isnad2network import process_pipeline

# Run the complete pipeline
process_pipeline(
    input_names="names.csv",
    nodelist="nodelist.csv",
    trans_terms="transmissionterms.csv",
    path_metadata="pathmetadata.csv",
    output_dir="output"
)
```

## Command Line Usage

```bash
# Run the full pipeline
isnad2network --input-names names.csv --nodelist nodelist.csv \
              --trans-terms transmissionterms.csv --path-metadata pathmetadata.csv \
              --output-dir output

# Run specific steps (1=name replacement, 2=dictionaries, 3=network JSON)
isnad2network --input-names names.csv --nodelist nodelist.csv \
              --trans-terms transmissionterms.csv --path-metadata pathmetadata.csv \
              --output-dir output --steps 1
```

## Input Data Format

The pipeline expects data in a specific CSV format:

1. **names.csv**: Contains isnad chains with transmitters in columns
   - Required format: Path ID in one column, transmitters in time-ordered columns
   - Time columns should be labeled as t0, t-1, t-2, etc. (t0 = latest transmitter)

2. **nodelist.csv**: Contains name mappings for standardization 
   - Required columns: `short_name` (original text) and `name_replace` (standardized name)

3. **transmissionterms.csv**: Contains transmission terms used between narrators
   - Should match the structure of the names file with terms instead of names

4. **pathmetadata.csv**: Contains metadata about each isnad chain
   - Required columns: `path_id` to link with other files

## Pipeline Steps

### 1. Name Replacement

Maps various forms of transmitter names to standardized versions using the nodelist file. Generates `names_replaced.csv` and tracks unmatched names.

```python
from isnad2network.match_replace_isnads import NetworkNameProcessor

processor = NetworkNameProcessor(
    names_file="names.csv",
    nodelist_file="nodelist.csv",
    output_file="names_replaced.csv"
)
processor.process()
```

### 2. Dictionary Creation

Creates reference dictionaries for annotation and analysis:

```python
from isnad2network.dict_creator import CSVDictionaryProcessor

processor = CSVDictionaryProcessor()
processor.input_file = "names_replaced.csv"
processor.load_csv()

# Get columns starting with 't'
t_columns = [col for col in processor.data.columns if col.startswith('t')]

# Create dictionaries
processor.create_unique_values_dict(t_columns)
processor.create_annotation_dict(t_columns)
```

### 3. Network Generation

Converts processed data into network JSON for visualization and analysis:

```python
from isnad2network.generate_json_network_isnad import generate_network_data

generate_network_data(
    names_replaced_path="names_replaced.csv",
    transmission_terms_path="transmissionterms.csv",
    path_metadata_path="pathmetadata.csv",
    output_dir="output/network"
)
```

## Output Files

The pipeline produces several outputs:

- **names_replaced.csv**: Isnad chains with standardized transmitter names
- **unmatched_names.txt**: List of names that couldn't be matched in the nodelist
- **dictionaries/**:
  - **_dict_unique.csv**: Unique transmitter names for reference
  - **_dict_annotate.csv**: Unique terms with counts and annotation columns
- **network/**:
  - **combined_network_data.json**: Full network data in JSON format
  - **nodelist.csv**: List of nodes with IDs for network visualization
  - **edgelist.csv**: List of edges with source, target, and type for visualization
- **logs/**: Detailed logs of the pipeline execution

## Transmission Classification

The package automatically classifies transmission terms into categories:

- **riwayah**: Terms associated with written transmission (ḥaddaṯa, ʾaḫbara, etc.)
- **tilawah**: Terms associated with oral transmission (samiʿa, qāla, etc.)
- **both**: Terms that indicate both written and oral transmission
- **NULL**: Terms that couldn't be classified

This classification is included in the network data and enables deeper analysis of transmission methods.

## Google Colab Integration

The package is designed to work seamlessly in Google Colab, allowing researchers to process data without local installation:

1. Upload your data files in Colab
2. Run the processing steps using the provided functions
3. Download the resulting files directly to your computer

## Integration with Visualization Tools

The output files are compatible with network visualization tools like:

- **Gephi**: Import nodelist.csv and edgelist.csv
- **Cytoscape**: Use combined_network_data.json
- **D3.js**: Use combined_network_data.json for web visualization

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## How to Push Changes to GitHub

To push your changes to GitHub:

1. Ensure you have Git installed and configured
2. Clone the repository if you haven't already:
   ```bash
   git clone https://github.com/zurstadt/isnad2network.git
   cd isnad2network
   ```
3. Create a new branch for your changes:
   ```bash
   git checkout -b update-pipeline
   ```
4. Add your modified files:
   ```bash
   git add __main__.py isnad2network_cli.py dict_creator.py README.md
   ```
5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "Refactor pipeline to improve integration between modules"
   ```
6. Push your changes to GitHub:
   ```bash
   git push origin update-pipeline
   ```
7. Create a Pull Request on GitHub to merge your changes into the main branch

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citing isnad2network

If you use isnad2network in your research, please cite it as:

```
Author. (Year). isnad2network: A Python toolkit for processing and analyzing isnad chains. 
GitHub repository: https://github.com/zurstadt/isnad2network
```

## Contact

For questions and support, please open an issue on the GitHub repository.
