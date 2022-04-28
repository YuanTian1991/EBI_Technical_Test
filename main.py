#!/usr/bin/env python3

# This script use Python 3.8.10.
# 1. Read all in the evidence files on FTP page.
# 2. Count target-disease socres.
# 3. Added disease ID and target (gene) ID.
# 4. Export table as JSON.

# ==========================================
print("Parsing eva page for eva list...")
# ==========================================

import requests
from bs4 import BeautifulSoup

url = 'http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/21.11/output/etl/json/evidence/sourceId%3Deva/'
eva_ftp_page = requests.get(url)
soup = BeautifulSoup(eva_ftp_page.text, features="html.parser")
a_tags = soup.select('a')

eva_list = []

for element in a_tags:
    eva_list.append(element['href'])

del eva_list[0]
eva_list = list(map(lambda x: url + x, eva_list))

# ==========================================
print("Parsing each eva JSON file in parallel...")
# ==========================================

import requests
import json
from functools import reduce

# json_path = "http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/21.11/output/etl/json/evidence/sourceId%3Deva/part-00000-4134a310-5042-4942-82ed-565f3d91eddd.c000.json"

from joblib import Parallel, delayed

def parse_json(json_path):
    # print(json_path)
    content = requests.get(json_path)
    parsed_json = json.loads("[" + content.text.replace("}\n{", "},\n{") +"]")
    subkey = list(map(lambda x: list(x[k] for k in ('targetId', 'diseaseId', 'score')), parsed_json))
    return subkey

eva_records = Parallel(n_jobs=min(80, len(eva_list)))(delayed(parse_json)(i) for i in eva_list)
eva_records = reduce(lambda x, y: x+y, eva_records)

# ==========================================
print("Pairing up DiseaseID with TargetID...")
# ==========================================

import pandas as pd
import statistics

df = pd.DataFrame (eva_records, columns = ['targetID', 'diseaseID', "score"])

score_list = list(df[(df.targetID  == "ENSG00000000419") & (df.diseaseID == "EFO_0003847")].score)

def score_statistic(score_list):
    tmp_median = statistics.median(score_list)
    tmp_sorted = sorted(score_list, reverse=True)
    if len(tmp_sorted) < 3:
        for i in range(3 - len(tmp_sorted)):
            tmp_sorted.append(None)
    return [tmp_median, tmp_sorted[0], tmp_sorted[1], tmp_sorted[2], len(score_list)]

score_value = df.groupby(['targetID', 'diseaseID'])['score'].apply(score_statistic).reset_index()
score_df = pd.DataFrame((list(score_value.score)))


