#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Dictionary Processing Module
--------------------------------
This module processes CSV files to create two output files:
1. A CSV with unique values from specified columns
2. A CSV with unique strings (split by whitespace), their counts, and annotation columns

Usage:
    Can be used as a standalone script or imported as a module.

Author: Your Name
License: MIT
"""

import pandas as pd
import numpy as np
import os
import re
import time
import logging
from tqdm.auto import tqdm
import io

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('csv_processing.log')
    ]
)
logger = logging.getLogger('csv_processor')

class CSVDictionaryProcessor:
    """Class to process CSV files and create dictionary outputs."""

    def __init__(self):
        """Initialize the processor."""
        self.input_file = None
        self.data = None
        self.filename_base = None

    def upload_file(self):
        """
        Upload a CSV file in Google Colab.
        This is a stub method for compatibility with the Colab implementation.
        """
        logger.info("This method is intended for Colab usage only.")
        logger.info("When using as a module, set input_file directly.")
        return False

    def load_csv(self, encoding='utf-8', sep=',', skip_display=False):
        """
        Load the CSV file and display a preview.

        Args:
            encoding (str): Character encoding of the file
            sep (str): Delimiter in the CSV file
            skip_display (bool): Whether to skip displaying the preview

        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not self.input_file:
            logger.error("No input file specified. Please set input_file first.")
            return False

        try:
            logger.info(f"Loading file: {self.input_file}")
            start_time = time.time()

            # Try with specified encoding first
            try:
                self.data = pd.read_csv(self.input_file, encoding=encoding, sep=sep)
            except UnicodeDecodeError:
                # Try with utf-8-sig if utf-8 fails
                logger.warning(f"Failed to decode with {encoding}, trying with utf-8-sig")
                self.data = pd.read_csv(self.input_file, encoding='utf-8-sig', sep=sep)

            load_time = time.time() - start_time
            rows, cols = self.data.shape

            logger.info(f"File loaded successfully in {load_time:.2f} seconds.")
            logger.info(f"Dataset dimensions: {rows} rows × {cols} columns")

            # Display preview and column information if not skipped
            if not skip_display:
                print("\n--- Data Preview ---")
                print(self.data.head())

                print("\n--- Column Information ---")
                for i, col in enumerate(self.data.columns):
                    print(f"{i+1}. {col} - {self.data[col].dtype}")

            return True

        except Exception as e:
            logger.error(f"Error loading file: {str(e)}")
            return False

    def create_unique_values_dict(self, columns):
        """
        Create a CSV with unique values from specified columns in a single column.

        Args:
            columns (list): List of column names to extract unique values from

        Returns:
            str: Path to the created file
        """
        if self.data is None:
            logger.error("No data loaded. Please load a CSV file first.")
            return None

        # Validate columns
        invalid_cols = [col for col in columns if col not in self.data.columns]
        if invalid_cols:
            logger.error(f"Invalid column(s): {', '.join(invalid_cols)}")
            return None

        output_file = f"{self.filename_base}_dict_unique.csv"
        logger.info(f"Creating unique values dictionary from columns: {columns}")

        try:
            # Collect all values from all specified columns
            all_values = []

            for col in tqdm(columns, desc="Processing columns"):
                unique_vals = self.data[col].dropna().unique()
                all_values.extend(unique_vals)

            # Remove duplicates
            unique_values = list(set(all_values))

            # Create DataFrame with a single column for unique values
            result_df = pd.DataFrame({
                'unique_names': unique_values
            })

            # Sort values alphabetically
            result_df = result_df.sort_values('unique_names').reset_index(drop=True)

            # Save to CSV
            result_df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Unique values dictionary saved to '{output_file}'")

            # Try to download file in Google Colab
            try:
                from google.colab import files
                files.download(output_file)
                logger.info("Download initiated in Colab environment.")
            except (ImportError, NameError):
                logger.info("Not running in Colab, skipping download.")

            return output_file

        except Exception as e:
            logger.error(f"Error creating unique values dictionary: {str(e)}")
            return None


    def create_annotation_dict(self, columns):
        """
        Create a CSV with unique strings (split by whitespace), their counts, and annotation columns.

        Args:
            columns (list): List of column names to extract strings from

        Returns:
            str: Path to the created file
        """
        if self.data is None:
            logger.error("No data loaded. Please load a CSV file first.")
            return None

        # Validate columns
        invalid_cols = [col for col in columns if col not in self.data.columns]
        if invalid_cols:
            logger.error(f"Invalid column(s): {', '.join(invalid_cols)}")
            return None

        output_file = f"{self.filename_base}_dict_annotate.csv"
        logger.info(f"Creating annotation dictionary from columns: {columns}")

        try:
            # Extract all words from all specified columns
            all_words = []

            for column in columns:
                logger.info(f"Processing column: {column}")
                # Extract the column data
                column_data = self.data[column].dropna().astype(str)

                # Split by whitespace and create a flat list of all words
                for text in tqdm(column_data, desc=f"Extracting words from {column}"):
                    # Split by whitespace
                    words = re.findall(r'\S+', text)
                    all_words.extend(words)

            # Count occurrences of each word
            word_counts = {}
            for word in tqdm(all_words, desc="Counting words"):
                word_counts[word] = word_counts.get(word, 0) + 1

            # Create DataFrame with words, counts, and empty annotation columns
            result_df = pd.DataFrame({
                'unique_strings': list(word_counts.keys()),
                'count': list(word_counts.values()),
                'annotate_ar': '',
                'annotate_kunyah': '',
                'annotate_nasab': '',
                'annotate_nisbah': ''
            })

            # Sort by count (descending)
            result_df = result_df.sort_values('count', ascending=False).reset_index(drop=True)

            # Save to CSV
            result_df.to_csv(output_file, index=False, encoding='utf-8')
            logger.info(f"Annotation dictionary saved to '{output_file}'")

            # Try to download file in Google Colab
            try:
                from google.colab import files
                files.download(output_file)
                logger.info("Download initiated in Colab environment.")
            except (ImportError, NameError):
                logger.info("Not running in Colab, skipping download.")

            return output_file

        except Exception as e:
            logger.error(f"Error creating annotation dictionary: {str(e)}")
            return None


def main():
    """Main function to run the CSV processor from the command line."""
    print("=" * 50)
    print("CSV Dictionary Processor")
    print("=" * 50)

    processor = CSVDictionaryProcessor()

    # Check if we're in a Google Colab environment
    try:
        import google.colab
        in_colab = True
    except ImportError:
        in_colab = False

    # Step 1: Get input file
    if in_colab:
        if not processor.upload_file():
            return
    else:
        # Command-line mode
        import argparse
        parser = argparse.ArgumentParser(description="CSV Dictionary Processor")
        parser.add_argument('input_file', help="Path to input CSV file")
        parser.add_argument('--output-dir', default=".", help="Directory for output files")
        args = parser.parse_args()

        processor.input_file = args.input_file
        processor.filename_base = os.path.join(args.output_dir, os.path.splitext(os.path.basename(args.input_file))[0])

    if not processor.load_csv():
        return

    # Step 2: Get column selection (used for both outputs)
    print("\n" + "=" * 50)
    print("Column Selection")
    print("=" * 50)

    # Get t-prefixed columns as default option
    t_columns = [col for col in processor.data.columns if col.startswith('t')]

    if t_columns:
        t_columns_str = ', '.join(t_columns)
        print(f"\nDefault option: Columns starting with 't': {t_columns_str}")
        use_default = input("Use these columns? (y/n): ").strip().lower()

        if use_default == 'y':
            columns = t_columns
        else:
            # Get custom column selection from user
            while True:
                column_input = input("\nEnter column names to extract unique values from (comma-separated): ")
                columns = [col.strip() for col in column_input.split(',')]

                # Validate columns
                invalid_cols = [col for col in columns if col not in processor.data.columns]
                if invalid_cols:
                    print(f"Invalid column(s): {', '.join(invalid_cols)}")
                    print("Available columns:")
                    for i, col in enumerate(processor.data.columns):
                        print(f"{i+1}. {col}")
                else:
                    break
    else:
        print("\nNo columns starting with 't' found.")
        # Get custom column selection from user
        while True:
            column_input = input("\nEnter column names to extract unique values from (comma-separated): ")
            columns = [col.strip() for col in column_input.split(',')]

            # Validate columns
            invalid_cols = [col for col in columns if col not in processor.data.columns]
            if invalid_cols:
                print(f"Invalid column(s): {', '.join(invalid_cols)}")
                print("Available columns:")
                for i, col in enumerate(processor.data.columns):
                    print(f"{i+1}. {col}")
            else:
                break

    # Step 3: Process for unique values dictionary
    print("\n" + "=" * 50)
    print("Creating Unique Values Dictionary")
    print("=" * 50)

    # Create unique values dictionary from all selected columns
    unique_file = processor.create_unique_values_dict(columns)

    # Step 4: Process for annotation dictionary
    print("\n" + "=" * 50)
    print("Creating Annotation Dictionary")
    print("=" * 50)

    print(f"Using the same columns selected earlier: {', '.join(columns)}")

    # Create annotation dictionary for all selected columns
    annotate_file = processor.create_annotation_dict(columns)

    # Summary
    if unique_file and annotate_file:
        print("\n" + "=" * 50)
        print("Processing Complete")
        print("=" * 50)
        print(f"1. Unique values dictionary: {unique_file}")
        print(f"2. Annotation dictionary: {annotate_file}")
        
        if in_colab:
            print("\nFiles have been downloaded. Check your downloads folder.")
        else:
            print("\nFiles have been saved to the specified output directory.")

if __name__ == "__main__":
    main()
