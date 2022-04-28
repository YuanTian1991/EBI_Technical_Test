# EBI_Technical_Test

## Usage

Install Dependency:
```bash
pip3 install beautifulsoup4 joblib pandas
```

Run python script:
```bash
python3 main.py
```

## Code Explaination

`main.py` contains all core code, which contains 4 steps:

### 1. Extract ftp JSON page

A function `parse_ftp_json()` is defined in script `parse_ftp_json.py`, which will **parallelly** parse all existing JSON files in a ftp webpage. In this case, we need to parse ftp pages for [eva](http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/21.11/output/etl/json/evidence/sourceId%3Deva/), [disease](http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/etl/json/diseases/) and [targets](http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/latest/output/etl/json/targets/), with only three lines as:

```python
eva_records = parse_ftp_json(eva_url, 80, ['targetId', 'diseaseId', 'score'])
diseases_records = parse_ftp_json(diseases_url, 80, ['id', 'name'])
targets_records = parse_ftp_json(targets_url, 80, ['id', 'approvedSymbol'])
```

In the function, there are three parameters:
* `ftp_url` is the URL for OpenTarget JSON ftp page, like the three link in above context. 
* `max_cores` is max cores can be used for parallel JSON file running. If JSON file number is less than this parameter, the number of JSON files will be used for parallel running.
* `col_list` is keys in JSON object that want to extracted.

The function will return a list, with element is a list contains assigned columns.

### 2. Do score statistic

After step 1, a simple groupBy function will be used on pandas-converted dataframe, which will return median score, top 3 scores, and count of scores

### 3. Merge disease/target dataframe

Then, we merge the result from step 2 with disease name from disease/target name. The final result is:

```python
>>> result_df
              targetID       diseaseID                                         name approvedSymbol  median_score  top_1  top_2  top_3  count
30     ENSG00000001626     EFO_0009166             response to ivacaftor - efficacy           CFTR          0.97   0.97   0.97   0.97     33
11899  ENSG00000138109     EFO_0005801                         cholesterol embolism         CYP2C9          0.97   0.97   0.97   0.97      9
7372   ENSG00000115486     EFO_0005801                         cholesterol embolism           GGCX          0.97   0.97    NaN    NaN      1
15294  ENSG00000157764  Orphanet_98733  Noonan syndrome and Noonan-related syndrome           BRAF          0.97   0.97   0.97   0.97      6
9495   ENSG00000128595     EFO_0005801                         cholesterol embolism           CALU          0.97   0.97    NaN    NaN      1
...                ...             ...                                          ...            ...           ...    ...    ...    ...    ...
11882  ENSG00000138081      HP_0001249                      Intellectual disability         FBXO11          0.00   0.72   0.00   0.00      7
23845  ENSG00000213918     EFO_0002690                 systemic lupus erythematosus         DNASE1          0.00   0.00    NaN    NaN      1
11883  ENSG00000138081   MONDO_0007254                                breast cancer         FBXO11          0.00   0.00    NaN    NaN      1
11913  ENSG00000138160      HP_0001657                        Prolonged QT interval          KIF11          0.00   0.00    NaN    NaN      1
0      ENSG00000000419     EFO_0003847                           mental retardation           DPM1          0.00   0.00    NaN    NaN      1

[25132 rows x 9 columns]
```
As above result shows, totally there are 25132 target-disease pairs. The dataframe can be exported as JSON file for frontend visualisation.

### 4. Find target-pair share disease

After step 3, we have target-disease data.frame `result_df`, by merge itself again by `diseaseID` first then groupBy two targetIDs, we can get target-target pairs that have at least one disease shared, which can be filtered to fine target-pairs with at least two shared diseases (`pair_target_df`). Note that the instruction did not indicate if "score" (or "median score") value should be considered when identify shared diseases, thus in below result even median\_score 0.00 will be considered a valid "association".

Below is an example, in the first row: target `ENSG00000000419` and `ENSG00000001497` share two diseases: `[HP_0001249, EFO_0003847]`, which can be confirmed by separately extract rows of these two targets from `result_df`.

```python
>>> pair_target_df
                target_1         target_2                                       disease_list  disease_count
1        ENSG00000000419  ENSG00000001497                          [HP_0001249, EFO_0003847]              2
2        ENSG00000000419  ENSG00000004487                          [HP_0001249, EFO_0003847]              2
3        ENSG00000000419  ENSG00000004848                          [HP_0001249, EFO_0003847]              2
4        ENSG00000000419  ENSG00000004961                          [HP_0001249, EFO_0003847]              2
5        ENSG00000000419  ENSG00000005007                          [HP_0001249, EFO_0003847]              2
...                  ...              ...                                                ...            ...
2829802  ENSG00000288705  ENSG00000242366  [Orphanet_79234, HP_0002904, EFO_0004829, Orph...              6
2829803  ENSG00000288705  ENSG00000242515  [Orphanet_79234, HP_0002904, EFO_0004829, Orph...              6
2829804  ENSG00000288705  ENSG00000244122  [Orphanet_79234, HP_0002904, EFO_0004829, Orph...              6
2829805  ENSG00000288705  ENSG00000244474  [Orphanet_79234, HP_0002904, EFO_0004829, Orph...              6
2829807  ENSG00000288705  ENSG00000288702  [Orphanet_79234, HP_0002904, EFO_0004829, Orph...              6

[700828 rows x 4 columns]
>>>
>>> result_df[result_df.targetID == 'ENSG00000000419']
          targetID     diseaseID                                  name approvedSymbol  median_score  top_1  top_2  top_3  count
2  ENSG00000000419  Orphanet_137  Congenital disorder of glycosylation           DPM1          0.32   0.95   0.92   0.92    105
1  ENSG00000000419    HP_0001249               Intellectual disability           DPM1          0.00   0.00    NaN    NaN      1
0  ENSG00000000419   EFO_0003847                    mental retardation           DPM1          0.00   0.00    NaN    NaN      1
>>>
>>> result_df[result_df.targetID == 'ENSG00000001497']
           targetID      diseaseID                         name approvedSymbol  median_score  top_1  top_2  top_3  count
19  ENSG00000001497     HP_0001263   Global developmental delay          LAS1L          0.70   0.70    NaN    NaN      1
15  ENSG00000001497    EFO_0000508             genetic disorder          LAS1L          0.52   0.72   0.32    NaN      2
17  ENSG00000001497    EFO_0010642  Neurodevelopmental disorder          LAS1L          0.32   0.32    NaN    NaN      1
20  ENSG00000001497  Orphanet_3459       Wilson-Turner syndrome          LAS1L          0.32   0.90   0.72   0.32     42
18  ENSG00000001497     HP_0001249      Intellectual disability          LAS1L          0.00   0.00   0.00    NaN      2
16  ENSG00000001497    EFO_0003847           mental retardation          LAS1L          0.00   0.00   0.00    NaN      2
>>>
```

As above result shows, there are 700828 target-taget pairs that share at least two disease, when score value is not taken into consideration.
