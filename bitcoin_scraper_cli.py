#!/usr/bin/env python3
"""
Script to extract Bitcoin addresses with command line parameters
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import sys
from typing import List, Dict

class BitcoinAddressScraperCLI:
    def __init__(self):
        self.base_url = "https://bitinfocharts.com/top-100-richest-bitcoin-addresses.html"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.addresses = []
        
    def get_page_content(self, url: str) -> str:
        """Retrieves the content of a page"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error retrieving page {url}: {e}")
            return ""

    def parse_address_table(self, html_content: str) -> List[str]:
        soup = BeautifulSoup(html_content, 'html.parser')
        addresses = []
        
        # Search for both tables: tblOne and tblOne2
        tables = []
        
        # First table (tblOne)
        table1 = soup.find('table', {'id': 'tblOne'})
        if table1:
            tables.append(table1)
        
        # Second table (tblOne2) 
        table2 = soup.find('table', {'id': 'tblOne2'})
        if table2:
            tables.append(table2)
        
        # Fallback: search by class if not found by ID
        if not tables:
            fallback_tables = soup.find_all('table', {'class': ['table-striped', 'abtb']})
            if fallback_tables:
                tables = fallback_tables
        
        if not tables:
            print("No addresses table found")
            return addresses
                
        # Process each table
        for table_idx, table in enumerate(tables):            
            all_rows = table.find_all('tr')
            
            # Skip header if present
            rows = all_rows
            if all_rows and all_rows[0].find('th'):
                rows = all_rows[1:]  # Skip header
            
            # Parsing rows
            for i, row in enumerate(rows):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    try:
                        address_cell = cells[1]
                        
                        # Search for Bitcoin address link
                        address_link = None
                        for link in address_cell.find_all('a'):
                            href = link.get('href', '')
                            if '/bitcoin/address/' in href:
                                address_link = link
                                break
                        
                        if address_link:
                            # Extract complete address from URL
                            href = address_link.get('href', '')
                            address = href.split('/bitcoin/address/')[-1]
                        else:
                            # Fallback: use cell text
                            address = address_cell.text.strip()
                            address = re.sub(r'wallet:.*$', '', address).strip()
                        
                        # Verify it's a valid Bitcoin address
                        if address and (address.startswith('1') or address.startswith('3') or address.startswith('bc1')):
                            addresses.append(address)
                            print(f"Address {len(addresses)} extracted from table {table_idx + 1}: {address}")
                        else:
                            print(f"DEBUG: Invalid address in table {table_idx + 1}, row {i+1}: '{address}'")
                            
                    except Exception as e:
                        print(f"ERROR in table {table_idx + 1}, row {i+1}: {e}")
                        print(f"Row content: {row.get_text()[:200]}...")
                        continue
        
        print(f"Total addresses extracted from page: {len(addresses)}")
        return addresses

    def get_next_page_url(self, current_page: int) -> str:
        """Finds the URL of the next page"""
        
        return f"https://bitinfocharts.com/top-100-richest-bitcoin-addresses-{current_page + 1}.html"
    
    def scrape_addresses(self, max_addresses: int = 20000, start_page: int = 1) -> List[str]:
        """Scrapes addresses starting from a specific page"""
        print(f"Starting scraping for {max_addresses} addresses, starting from page {start_page}...")
        
        # Build initial URL
        if start_page == 1:
            current_url = self.base_url
        else:
            current_url = f"https://bitinfocharts.com/top-100-richest-bitcoin-addresses-{start_page}.html"
        
        page_num = start_page
        total_addresses = 0
        
        while total_addresses < max_addresses:
            print(f"\nScraping page {page_num}: {current_url}")
            
            html_content = self.get_page_content(current_url)
            if not html_content:
                print(f"Unable to retrieve page {page_num}")
                break
            
            page_addresses = self.parse_address_table(html_content)
            
            if not page_addresses:
                print(f"No address found on page {page_num}")
                break
            
            for addr in page_addresses:
                if total_addresses < max_addresses:
                    self.addresses.append(addr)
                    total_addresses += 1
                else:
                    break
            
            print(f"Addresses extracted so far: {total_addresses}")
            
            next_url = self.get_next_page_url(page_num)
            
            current_url = next_url
            page_num += 1
            
            time.sleep(2)
        
        print(f"\nScraping completed. Total addresses extracted: {len(self.addresses)}")
        return self.addresses
    
    def save_to_file(self, filename: str = "addresses.txt", append: bool = False):
        """Saves the addresses to file, one per line"""
        try:
            mode = 'a' if append else 'w'  # 'a' for append, 'w' for overwrite
            action = "added to" if append else "overwritten"
            
            with open(filename, mode, encoding='utf-8') as f:
                
                for address in self.addresses:
                    f.write(f"{address}\n")
            
            print(f"Addresses {action} {filename}")
            print(f"File contains {len(self.addresses)} addresses, one per line")
            
        except Exception as e:
            print(f"Error saving file: {e}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Bitcoin Address Scraper - CLI Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                           # Scrapes 20000 addresses from first page
  %(prog)s -n 1000                   # Scrapes 1000 addresses from first page
  %(prog)s -p 5                      # Scrapes 20000 addresses starting from page 5
  %(prog)s -n 500 -p 10              # Scrapes 500 addresses starting from page 10
  %(prog)s -o custom_filename.txt    # Saves to a custom file
        """
    )
    
    parser.add_argument(
        '-n', '--num-addresses',
        type=int,
        default=20000,
        help='Maximum number of addresses to extract (default: 20000)'
    )
    
    parser.add_argument(
        '-p', '--start-page',
        type=int,
        default=1,
        help='Starting page (default: 1)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='addresses.txt',
        help='Output file name (default: addresses.txt)'
    )
    
    parser.add_argument(
        '--append',
        action='store_true',
        help='Appends results to existing output file instead of overwriting it'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Parameter validation
    if args.num_addresses <= 0:
        print("Error: Number of addresses must be positive")
        sys.exit(1)
    
    if args.start_page < 1:
        print("Error: Starting page must be >= 1")
        sys.exit(1)
    
    print("Bitcoin Address Scraper - CLI Version")
    print("=" * 50)
    print(f"Addresses to extract: {args.num_addresses}")
    print(f"Starting page: {args.start_page}")
    print(f"Output file: {args.output}")
    print()
    
    scraper = BitcoinAddressScraperCLI()
    
    try:
        addresses = scraper.scrape_addresses(
            max_addresses=args.num_addresses,
            start_page=args.start_page
        )
        
        if addresses:
            scraper.save_to_file(args.output, args.append)
            
            print(f"\nStatistics:")
            print(f"Total addresses extracted: {len(addresses)}")
            print(f"First address: {addresses[0]}")
            print(f"Last address: {addresses[-1]}")
        
        else:
            print("No address extracted")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
