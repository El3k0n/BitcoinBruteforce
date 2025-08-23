#!/usr/bin/env python3
"""
CLI Script to extract dormant Bitcoin addresses from BitInfoCharts
Dedicated to: https://bitinfocharts.com/top-100-dormant_1y-bitcoin-addresses.html
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import argparse
import sys
from typing import List, Dict
from datetime import datetime
import os

class BitcoinDormantScraper:
    def __init__(self):
        self.base_url = "https://bitinfocharts.com/top-100-dormant_1y-bitcoin-addresses.html"
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
    
    def parse_dormant_table(self, html_content: str) -> List[Dict]:
        """Parses the table of dormant Bitcoin addresses"""
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
            print("No dormant addresses table found")
            return addresses
                
        # Process each table
        for table_idx, table in enumerate(tables):            
            all_rows = table.find_all('tr')

            # Skip header if present
            rows = all_rows
            if all_rows and all_rows[0].find('th'):
                rows = all_rows[1:]  # Skip header
            
            # Parsing rows
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 5:  # At least 5 columns for dormant addresses
                    try:
                        # Extract address from second column (index 1)
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
                        
                        # Extract balance (third column - index 2)
                        balance_cell = cells[2]
                        balance_text = balance_cell.text.strip()
                        
                        # Extract BTC value
                        btc_match = re.search(r'(\d+(?:,\d+)*\.?\d*)\s*BTC', balance_text)
                        btc_amount = None
                        if btc_match:
                            btc_amount = float(btc_match.group(1).replace(',', ''))
                        
                        # Extract USD value
                        usd_match = re.search(r'\$([\d,]+)', balance_text)
                        usd_amount = None
                        if usd_match:
                            usd_amount = int(usd_match.group(1).replace(',', ''))
                        
                        # Extract percentage (fourth column - index 3)
                        percent_cell = cells[3]
                        percent_text = percent_cell.text.strip()
                        percent_match = re.search(r'(\d+\.?\d*)%', percent_text)
                        percentage = None
                        if percent_match:
                            percentage = float(percent_match.group(1))
                        
                        # Extract dates (fifth and sixth column - index 4 and 5)
                        first_in_cell = cells[4]
                        last_in_cell = cells[5]
                        first_in_date = first_in_cell.text.strip()
                        last_in_date = last_in_cell.text.strip()
                        
                        # Extract incoming transactions count (seventh column - index 6)
                        ins_cell = cells[6]
                        ins_count = ins_cell.text.strip()
                        
                        if address and btc_amount and len(address) > 20:
                            addresses.append({
                                'address': address,
                                'balance_btc': btc_amount,
                                'balance_usd': usd_amount,
                                'percentage': percentage,
                                'first_in': first_in_date,
                                'last_in': last_in_date,
                                'ins_count': ins_count,
                            })
                            print(f"Dormant address extracted from table {table_idx + 1}: {address} - {btc_amount} BTC")
                            
                    except Exception as e:
                        print(f"ERROR in table {table_idx + 1}, row: {e}")
                        continue
        
        print(f"DEBUG: Total dormant addresses extracted from all tables: {len(addresses)}")
        return addresses
    
    def get_next_page_url(self, current_page: int) -> str:
        """Finds the URL of the next page"""

        return f"https://bitinfocharts.com/top-100-dormant_{current_page + 1}y-bitcoin-addresses.html"
    
    def scrape_dormant_addresses(self, max_addresses: int = 10000, start_page: int = 1) -> List[Dict]:
        """Scrapes dormant addresses starting from a specific page"""
        print(f"Starting scraping for {max_addresses} dormant addresses, starting from page {start_page}...")
        
        # Build initial URL
        if start_page == 1:
            current_url = self.base_url
        else:
            current_url = f"https://bitinfocharts.com/top-100-dormant_{start_page}y-bitcoin-addresses.html"
        
        page_num = start_page
        total_addresses = 0
        
        while total_addresses < max_addresses:
            print(f"\nScraping page {page_num}: {current_url}")
            
            html_content = self.get_page_content(current_url)
            if not html_content:
                print(f"Unable to retrieve page {page_num}")
                break
            
            page_addresses = self.parse_dormant_table(html_content)
            
            if not page_addresses:
                print(f"No dormant address found on page {page_num}")
                break
            
            for addr in page_addresses:
                if total_addresses < max_addresses:
                    self.addresses.append(addr)
                    total_addresses += 1
                else:
                    break
            
            print(f"Dormant addresses extracted so far: {total_addresses}")
            
            next_url = self.get_next_page_url(page_num)
            if next_url == current_url:
                print("No next page found")
                break
            
            current_url = next_url
            page_num += 1
            
            time.sleep(2)
        
        print(f"\nScraping completed. Total dormant addresses extracted: {len(self.addresses)}")
        return self.addresses
    
    def sort_addresses(self):
        """Sorts addresses by BTC balance in descending order"""
        self.addresses.sort(key=lambda x: x['balance_btc'], reverse=True)
    
    def save_to_file(self, filename: str = "bitcoin_dormant_addresses.txt", append: bool = False):
        """Saves dormant addresses to a text file with full details"""
        try:
            mode = 'a' if append else 'w'  # 'a' for append, 'w' for overwrite
            action = "added to" if append else "overwritten"
            
            with open(filename, mode, encoding='utf-8') as f:
                if append:
                    # If we're adding, insert a separator
                    f.write(f"\n\n--- NEW SCRAPING SESSION ---\n")
                    f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Addresses added: {len(self.addresses)}\n\n")
                else:
                    # If we're overwriting, write complete header
                    f.write("Dormant Bitcoin Addresses (1 year) - Sorted by balance\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(f"Extraction date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Source: {self.base_url}\n\n")
                
                for i, addr in enumerate(self.addresses, 1):
                    f.write(f"{i:4d}. Address: {addr['address']}\n")
                    f.write(f"     Balance: {addr['balance_btc']:,.2f} BTC")
                    if addr['balance_usd']:
                        f.write(f" (${addr['balance_usd']:,})")
                    f.write("\n")
                    if addr['percentage']:
                        f.write(f"     Percentage: {addr['percentage']:.4f}%\n")
                    f.write(f"     First transaction: {addr['first_in']}\n")
                    f.write(f"     Last transaction: {addr['last_in']}\n")
                    f.write(f"     Incoming transactions: {addr['ins_count']}\n")
                    f.write("\n")
            
            print(f"Dormant addresses with full details {action} {filename}")
            
        except Exception as e:
            print(f"Error saving file: {e}")
    
    def save_to_json(self, filename: str = "bitcoin_dormant_addresses.json", append: bool = False):
        """Saves dormant addresses in JSON format"""
        try:
            if append and os.path.exists(filename):
                # If we're adding and file exists, read existing data
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                    # Add new data
                    existing_data.extend(self.addresses)
                    data_to_save = existing_data
                    action = "updated"
                except (json.JSONDecodeError, FileNotFoundError):
                    # If file is not valid JSON, overwrite
                    data_to_save = self.addresses
                    action = "overwritten"
            else:
                # Overwrite or create new file
                data_to_save = self.addresses
                action = "overwritten"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            
            print(f"Dormant addresses {action} in JSON format: {filename}")
            
        except Exception as e:
            print(f"Error saving JSON file: {e}")
    
    def save_addresses_only(self, filename: str = "bitcoin_dormant_addresses_only.txt", append: bool = False):
        """Saves ONLY the addresses, one per line"""
        try:
            mode = 'a' if append else 'w'  # 'a' for append, 'w' for overwrite
            action = "added to" if append else "overwritten"
            
            with open(filename, mode, encoding='utf-8') as f:
                
                for addr in self.addresses:
                    f.write(f"{addr['address']}\n")
            
            print(f"Dormant addresses (addresses only) {action} {filename}")
            print(f"File contains {len(self.addresses)} addresses, one per line")
            
        except Exception as e:
            print(f"Error saving file: {e}")

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(
        description='Bitcoin Dormant Address Scraper - Extracts dormant Bitcoin addresses',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  %(prog)s                           # Scrapes 10000 dormant addresses from first page
  %(prog)s -n 1000                   # Scrapes 1000 dormant addresses from first page
  %(prog)s -p 5                      # Scrapes 10000 dormant addresses starting from page 5
  %(prog)s -n 500 -p 10              # Scrapes 500 dormant addresses starting from page 10
  %(prog)s -o custom_filename.txt    # Saves to a custom file
  %(prog)s --addresses-only          # Saves only addresses, one per line
  %(prog)s --json                    # Also saves in JSON format
        """
    )
    
    parser.add_argument(
        '-n', '--num-addresses',
        type=int,
        default=10000,
        help='Maximum number of dormant addresses to extract (default: 10000)'
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
        default='bitcoin_dormant_addresses.txt',
        help='Main output file name (default: bitcoin_dormant_addresses.txt)'
    )
    
    parser.add_argument(
        '--addresses-only',
        action='store_true',
        help='Also saves only addresses in a separate file'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Also saves in JSON format'
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
    
    print("Bitcoin Dormant Address Scraper")
    print("=" * 50)
    print(f"Source: {parser.description}")
    print(f"Dormant addresses to extract: {args.num_addresses}")
    print(f"Starting page: {args.start_page}")
    print(f"Output file: {args.output}")
    print()
    
    scraper = BitcoinDormantScraper()
    
    try:
        addresses = scraper.scrape_dormant_addresses(
            max_addresses=args.num_addresses,
            start_page=args.start_page
        )
        
        if addresses:
            # Sort by balance
            scraper.sort_addresses()
            
            # Save based on addresses-only flag
            if args.addresses_only:
                # Save only addresses if requested
                addresses_only_file = args.output.replace('.txt', '_only.txt')
                scraper.save_addresses_only(addresses_only_file, args.append)
            else:
                # Save full format with statistics when addresses-only is NOT used
                scraper.save_to_file(args.output, args.append)
            
            # Save in JSON if requested
            if args.json:
                json_file = args.output.replace('.txt', '.json')
                scraper.save_to_json(json_file, args.append)
            
            # Show statistics
            print(f"\nStatistics:")
            print(f"Total dormant addresses extracted: {len(addresses)}")
            print(f"Richest dormant address: {addresses[0]['address']}")
            print(f"Maximum balance: {addresses[0]['balance_btc']:,.2f} BTC")
            print(f"Minimum balance: {addresses[-1]['balance_btc']:,.2f} BTC")
            
            # Calculate dormant statistics
            total_btc = sum(addr['balance_btc'] for addr in addresses)
            total_usd = sum(addr['balance_usd'] for addr in addresses if addr['balance_usd'])
            print(f"Total dormant BTC: {total_btc:,.2f} BTC")
            if total_usd:
                print(f"Total dormant USD: ${total_usd:,}")
        
        else:
            print("No dormant address extracted")
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error during scraping: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import json
    main()
