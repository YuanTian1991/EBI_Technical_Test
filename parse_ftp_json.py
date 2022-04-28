#!/usr/bin/env python3
# This function conviniently parse JSON ftp page.
# Author: Tian

import requests
import requests
import json
from functools import reduce
from bs4 import BeautifulSoup
from joblib import Parallel, delayed

def parse_json(json_path, col_list):
    # print(json_path)
    content = requests.get(json_path)
    parsed_json = json.loads("[" + content.text.replace("}\n{", "},\n{") +"]")
    subkey = list(map(lambda x: list(x[k] for k in col_list), parsed_json))
    return subkey

def parse_ftp_json(ftp_url, max_cores, col_list):
    # ==========================================
    print("Parsing ftp page for JSON file list...")
    # ==========================================
    url = ftp_url
    ftp_page = requests.get(url)
    soup = BeautifulSoup(ftp_page.text, features="html.parser")
    a_tags = soup.select('a')
    json_list = []

    for element in a_tags:
        json_list.append(element['href'])
    del json_list[0]
    json_list = list(map(lambda x: url + x, json_list))

    # ==========================================
    print("Parsing each JSON file in parallel...")
    # ==========================================

    json_records = Parallel(n_jobs=min(max_cores, len(json_list)))(delayed(parse_json)(i, col_list) for i in json_list)
    json_records = reduce(lambda x, y: x+y, json_records)

    return json_records
