#!/usr/bin/env python3
# This function is used to find target combinations with shared diseases, when take target-disease association score into consideration.
# Author: Tian

import pandas as pd

def find_target_combination(df, median_score_cutoff=0.8, n_targets=10, n_diseases = 10):

    print("Filtering df with median_score_cutoff", median_score_cutoff)
    filter_df = df[df.median_score >= median_score_cutoff][["targetID", "diseaseID"]]
    disease_count = filter_df.groupby(["targetID"])["diseaseID"].size().reset_index()
    disease_count = disease_count[disease_count["diseaseID"] >= n_diseases]
    filter_df = filter_df[filter_df['targetID'].isin(disease_count["targetID"])]
    merge_df = filter_df.copy()

    merge_df.columns = ["merged_targets_id", "diseaseID"]

    for i in range(n_targets - 1):
        print("Finding", i+2, "target combinations with", n_diseases, "shared diseases...")
        merge_df = merge_df.merge(filter_df, on='diseaseID')
        merge_df['duplicate_id'] = merge_df.apply(lambda x: str(x["targetID"]) in str(x["merged_targets_id"]), axis=1)
        merge_df = merge_df[merge_df["duplicate_id"] == False]
        merge_df["merged_targets_id"] = merge_df["merged_targets_id"].str.cat(merge_df["targetID"], sep='-')
        merge_df = merge_df[["merged_targets_id", "diseaseID"]]
        tmp_count = merge_df.groupby(["merged_targets_id"])["diseaseID"].size().reset_index()
        tmp_count = tmp_count[tmp_count["diseaseID"] >= n_diseases]
        merge_df = merge_df[merge_df['merged_targets_id'].isin(tmp_count["merged_targets_id"])]
        if len(merge_df) == 0:
            print("No avaliable targets combinations already.")
            break
        tmp = merge_df.groupby("merged_targets_id")["diseaseID"].apply(lambda x: list(x)).reset_index()
        print("  There are", len(tmp), "combinations for now.")
    tmp = merge_df.groupby("merged_targets_id")["diseaseID"].apply(lambda x: list(x)).reset_index()
    return tmp
