#!/usr/bin/env python3
"""
Script to process the .tsv file downloaded from http://addresses.loyce.club and extract only the Bitcoin addresses to a text file.
"""

import csv
import argparse
import sys

def process_loyce(input_file, output_file):
    """Process Loyce TSV file and extract addresses to output file."""
    try:
        with open(input_file, "r", newline="", encoding="utf-8") as tsvfile, \
             open(output_file, "w", encoding="utf-8") as txtfile:

            reader = csv.reader(tsvfile, delimiter="\t")
            header = next(reader)  # skip header if present

            for row in reader:
                address = row[0]
                txtfile.write(address + "\n")
        
        print(f"Successfully processed {input_file} and saved addresses to {output_file}")
        
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Process Loyce TSV file and extract Bitcoin addresses",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python process_loyce.py
  python process_loyce.py -i custom_input.tsv
  python process_loyce.py -i custom_input.tsv -o custom_output.txt
        """
    )
    
    parser.add_argument(
        "-i", "--input", 
        default="blockchair_bitcoin_addresses_and_balance_LATEST.tsv",
        help="Input TSV file (default: blockchair_bitcoin_addresses_and_balance_LATEST.tsv)"
    )
    
    parser.add_argument(
        "-o", "--output", 
        default="addresses.txt",
        help="Output text file (default: addresses.txt)"
    )
    
    args = parser.parse_args()
    
    process_loyce(args.input, args.output)

if __name__ == "__main__":
    main()
