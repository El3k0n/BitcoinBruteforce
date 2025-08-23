import sys
import argparse

from Gen import generate_bitcoin_address

def read_file_to_set(filename: str) -> set:
    """
    Reads a text file line by line and returns a set with sanitized lines.
    
    Args:
        filename (str): Path of the file to read
        
    Returns:
        set: Set containing all file lines without newline characters
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there are file reading problems
    """
    lines_set = set()
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                # Sanitize the line by removing \n and extra spaces
                clean_line = line.strip()
                if clean_line:  # Add only non-empty lines
                    lines_set.add(clean_line)
                    
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{filename}' not found")
    except IOError as e:
        raise IOError(f"Error reading file '{filename}': {e}")
    
    return lines_set

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Bitcoin Address Bruteforce - CLI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                           # Bruteforce 20000 addresses from first page
  %(prog)s -n 1000                   # Bruteforce 1000 addresses from first page
  %(prog)s -f custom_filename.txt    # Saves to a custom file
        """
    )

    parser.add_argument(
        '-f', '--file',
        type=str,
        default='addresses.txt',
        help='File containing addresses to bruteforce'
    )

    parser.add_argument(
        '-n', '--num-addresses',
        type=int,
        default=20000,
        help='Maximum number of addresses to bruteforce (default: 20000)'
    )

    args = parser.parse_args()

     # Parameter validation
    if args.num_addresses <= 0:
        print("Error: Number of addresses must be positive")
        sys.exit(1)

    addresses = read_file_to_set(args.file)

    print(f"File '{args.file}' loaded with {len(addresses)} addresses")

    for i in range(args.num_addresses):
        print(f"Generating address {i+1} of {args.num_addresses}")
        bitcoin_address = generate_bitcoin_address()

        print(f"Address generated, private key: {bitcoin_address['private_key']}")
        k = ['p2pkh_address', 'compressed_p2pkh_address', 'p2sh_address', 'bech32_address']

        for key in k:
            print(f"Checking {key}: {bitcoin_address[key]}")
            if bitcoin_address[key] in addresses:
                print("=" * 50)
                print("=" * 50)
                print("=" * 50)
                print("=" * 50)
                print(f"Address {bitcoin_address[key]} found in {args.file}")
                print(f"Private key: {bitcoin_address['private_key']}")
                print("=" * 50)
                print("=" * 50)
                print("=" * 50)
                print("=" * 50)
                break



if __name__ == "__main__":
    main()