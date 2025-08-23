# Bitcoin Address Bruteforcer

I made this simple project a while ago to have a tangible proof of the security of the Bitcoin crypto algorithm. It features 2 different cli scripts to download a list of rich or dormant Bitcoin Addresses from [BitInfoCharts](https://bitinfocharts.com). The third script ```bruteforce.py``` is used to load the generated list and try a bruteforce, generating the given number of bitcoin addresses and checking each one against the downloaded list.

The code in ```Gen.py```, used to generate the addresses, was taken and slightly edited from [this public Repo](https://github.com/BRO200BS/Bitcoin-Address-Generator/tree/main)

## Usage

### Set Up

```bash
git clone 
cd bitcoinbruteforce
pip install -r requirements.txt
```
### Download the richest bitcoin addresses

If you want to use the default configuration:
```bash
python3 bitcoin_scraper_cli.py 
```

You also have access to a helper:
```bash
python3 bitcoin_scraper_cli.py -h
```

By default the script scrapes for 20000 addresses and saves them to ```addresses.txt```

### Download Dormant Addresses

If you want to use the default configuration:

```bash
python3 bitcoin_dormant_scraper_cli.py 
```

In this case the script also scrapes for informations like balance and inactive time. If you only want addresses (to work with the ```bruteforce.py``` script):

```bash
python3 bitcoin_dormant_scraper_cli.py --addresses-only
```

Which will create two .txt files, one with only the addresses and one with all the info.

### Bruteforce

And now for the fun part! 

```bash
python3 bruteforce.py -f your_address_file.txt
```

The script will print each tested address, and will terminate if a collision is found (never).


Have fun knowing that your money is cryptographically secure!