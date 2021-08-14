"""
    SET - Subdomain Enumeration Tool
    File name: set.py
    Description:  

    Date: August, 2021
    Author: b4c
"""

import os
import csv
import requests
import argparse
from bs4 import BeautifulSoup
from Sublist3r import sublist3r
from colorama import init, Fore

class SET():
    def __init__(self):
        self.session = requests.Session()
        self.error = 1
        self.subdlist_1 = []
        self.subdlist_2 = []
    
    def standardize_domain_format(self, _domain):
        print("[+] Standardize domain format...")
        if ('http://' in _domain):
            _domain = _domain.replace('http://', '')
        elif ('https://' in _domain):
            _domain = _domain.replace('https://', '')
        if ('www.' in _domain):
            _domain = _domain.replace('www.', '')
        print("     -> ", _domain)
        return _domain

    def request_dns_dumpster(self, _domain):
        print("[+] Extracting information with DNSdumpster...")
        _dnsdumpster = 'https://dnsdumpster.com'
        _req = self.session.get(_dnsdumpster)
        if (_req.status_code == 200):
            # print(_req.text)
            soup = BeautifulSoup(_req.text, 'html.parser')
            # print(soup.prettify())

            # Get CSRF token
            _token = soup.find('input', {'name':'csrfmiddlewaretoken'})['value']
            # print("     '-> CSRF Token: ", _token)

            # Query for DNS information
            headers = {'Referer': _dnsdumpster} 
            data = {'csrfmiddlewaretoken': _token, 'targetip': _domain, 'user': 'free'}
            _req = self.session.post(_dnsdumpster, data=data, headers=headers)
            if (_req.status_code == 200):
                _err = _req.text.find("There was an error getting results. Check your query and try again.")
                if _err != -1:
                    print(Fore.RED + "     [-] Something error. Please check your input domain!")
                else:
                    soup = BeautifulSoup(_req.text, 'html.parser')
                    tables = soup.findAll("table")
                    rows = tables[3].findAll('tr')
                    print(Fore.GREEN + "     [->] DNSdumpster found ", len(rows), Fore.GREEN + " subdomain(s).")
                    for row in rows:
                        cols = row.find_all('td')
                        _data_col_1 = cols[0].text.split('\n')
                        self.subdlist_1.append(_data_col_1[0])
                    # print(_subdlist)
                    self.error = 0
                    return self.subdlist_1, self.error
            else:
                print(Fore.RED + "     [-] Something error. Please check in DNSdumpster Web Interface!")
        else:
            print(Fore.RED + "     [-] Something error. Please check your connection!")
        return self.subdlist_1, self.error
    
    def request_sublist3r(self, _domain):
        print("[+] Extracting information with Sublist3r...")
        try:
            _subdomains = sublist3r.main(_domain, 40, savefile=False, ports=None, silent=True, verbose= False, enable_bruteforce=False, engines=None)
            print(Fore.GREEN + "     [->] Sublist3r found ", len(_subdomains), Fore.GREEN + " subdomain(s).")
            self.subdlist_2 = _subdomains
            self.error = 0
        except:
            self.error = 1
        return self.subdlist_2, self.error

    def merge_results(self, _sub1, _sub2):
        print("[+] Merging the results...")
        final_res = list(set(_sub1) | set(_sub2))
        print(Fore.GREEN + "     [->] Found total", len(final_res), Fore.GREEN + " subdomains.")
        return final_res

    def save_results(self, _domain, _result):
        try:
            if os.path.isdir('results'):
                pass
            else:
                os.mkdir('results')
            _filename = "results/" + str(_domain) + ".csv"
            _file = open(_filename, 'w', encoding='UTF8', newline ='')
            _result = [[el] for el in _result]
            with _file:
                write = csv.writer(_file)
                write.writerows(_result)
            print("[+] Your results will be saved to a file name: ", _filename)
            return True
        except:
            return False

    def print_results(self, _result):
        x = input("[?] Do you want to print the results? (y/n): ")
        if (x == 'y' or x == 'Y'):
            [print(el) for el in _result]

if __name__ == '__main__':
    init(autoreset=True)

    print(Fore.MAGENTA  + "                                                    __                                                      _____         ")
    print(Fore.CYAN     + "      ()      |)   _|   _           _,  o          / ()                      _  ,_   _, _|_ o  _           () | _   _  |\ ")
    print(Fore.MAGENTA  + "      /\ |  | |/\_/ |  / \_/|/|/|  / |  | /|/|     >-   /|/|  |  |  /|/|/|  |/ /  | / |  |  | / \_/|/|        |/ \_/ \_|/ ")
    print(Fore.CYAN     + "     /(_) \/|_/\/ \/|_/\_/  | | |_/\/|_/|/ | |_/   \___/ | |_/ \/|_/ | | |_/|_/   |/\/|_/|_/|/\_/  | |_/    (/ \_/ \_/ |_/")
    print(Fore.MAGENTA  + "                                                                                                                          ")
    parser = argparse.ArgumentParser(description='SET - Subdomain Enumeration Tool.')
    parser.add_argument("-d", "--domain", required=True, help="a specific domain")
    parser.add_argument("-o", "--output", help="save results to csv file", action='store_true')
    args = parser.parse_args()
    if (args.domain):
        _subdenum = SET()
        _domain = _subdenum.standardize_domain_format(args.domain)
        dnsdumpster_res, error_res = _subdenum.request_dns_dumpster(_domain)
        #if not error_res:
        #    print(dnsdumpster_res)
        sublist3r_res, error_res = _subdenum.request_sublist3r(_domain)
        #if not error_res:
        #    print(sublist3r_res)
        final_res = _subdenum.merge_results(dnsdumpster_res, sublist3r_res)
        if (args.output):
            if (_subdenum.save_results(_domain, final_res)):
                print(Fore.GREEN + "     '-> Done!")
            else:
                print(Fore.RED + "     '-> ERROR. Cannot save into this file!")
        _subdenum.print_results(final_res)
    # _subdenum.export_csv()
