#!/usr/bin/env python3

# This script use Python 3.8.10.
# Author: Tian
# 1. Read all in the evidence/diseases/tagets files on FTP page.
# 2. Count target-disease socres.
# 3. Added disease ID and target (gene) ID. Export target-disease DataFrame as JSON.
# 4. Count target-target pairs share a connection to at least two diseases.

from parse_ftp_json import *

# ==========================================
print("\n1. Reading JSON files from FTP...")
# ==========================================

eva_url = 'http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/21.11/output/etl/json/evidence/sourceId%3Deva/'
diseases_url = 'http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/etl/json/diseases/'
targets_url = "http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/etl/json/targets/"

eva_records = parse_ftp_json(eva_url, 80, ['targetId', 'diseaseId', 'score'])
diseases_records = parse_ftp_json(diseases_url, 80, ['id', 'name'])
targets_records = parse_ftp_json(targets_url, 80, ['id', 'approvedSymbol'])

# ==========================================
print("\n2. Pairing up DiseaseID with TargetID...")
# ==========================================

import pandas as pd
import statistics

df = pd.DataFrame (eva_records, columns = ['targetID', 'diseaseID', "score"])

def score_statistic(score_list):
    tmp_median = statistics.median(score_list)
    tmp_sorted = sorted(score_list, reverse=True)
    if len(tmp_sorted) < 3:
        for i in range(3 - len(tmp_sorted)):
            tmp_sorted.append(None)
    return [tmp_median, tmp_sorted[0], tmp_sorted[1], tmp_sorted[2], len(score_list)]

score_value = df.groupby(['targetID', 'diseaseID'])['score'].apply(score_statistic).reset_index()
score_df = pd.DataFrame((list(score_value.score)))
score_df.columns = ["median_score", "top_1" ,"top_2", "top_3", "count"]

print("Totally there are", len(score_value.index), "target-disease pairs.")

# ==========================================
print("\n3. Add Disease Name and Target Symbol...")
# ==========================================

pair_df = score_value
diseases_df = pd.DataFrame(diseases_records, columns = ['id', "name"])
targets_df = pd.DataFrame(targets_records, columns = ['id', "approvedSymbol"])

pair_df = pair_df.merge(diseases_df, how='left', left_on="diseaseID", right_on="id")
pair_df = pair_df.merge(targets_df, how='left', left_on="targetID", right_on="id")

result_df = pair_df.loc[:,["targetID", "diseaseID", "name", "approvedSymbol"]].join(score_df)
result_df = result_df.sort_values(by=['median_score'], ascending=False)
result_df.to_json("target_disease_pair.json", orient="records")


# ==========================================
print("\n4. Count target-target pairs...")
# ==========================================

merge_df = result_df.merge(result_df, on='diseaseID')
pair_target_df = merge_df.groupby(["targetID_x", "targetID_y"])["diseaseID"].apply(lambda x: (list(set(x), len(x)))).reset_index()
pair_target_df = pair_target_df.loc[:, ["targetID_x", "targetID_y"]].join(pd.DataFrame((list(pair_target_df.diseaseID))))
pair_target_df.columns = ["target_1", "target_2" ,"disease_list" , "disease_count"]

pair_target_df = pair_target_df[(pair_target_df.disease_count >= 2) & (pair_target_df.target_1 != pair_target_df.target_2)]

# pair_target_matrix = pd.crosstab(merge_df.targetID_x, merge_df.targetID_y, merge_df.diseaseID, aggfunc='count').fillna(0)
# np.fill_diagonal(pair_target_matrix, 0)

