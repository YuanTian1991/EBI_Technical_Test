# EBI Technical Test

## Compute Setting
All code is code/tested on a Ubuntu server, which has 128 cores and 250 RAM. No GPU is used.

## Usage

Clone code:
```bash
git clone https://github.com/YuanTian1991/EBI_Technical_Test.git
cd EBI_Technical_Test
```

Install Dependency:
```bash
pip3 install beautifulsoup4 joblib pandas
```

Run python script:
```bash
python3 main.py
```

## Highlight

Two functions can be used for OpenTarget platform ETL automation. 

`parse_ftp_json()` can be used to convinently parallelly preprocess most OpenTarget ftp JSON pages. Just need to assign an JSON folder url and columns(key) wants to extract, like:

```python
>> from parse_ftp_json import *
>>> test = parse_ftp_json("http://ftp.ebi.ac.uk/pub/databases/opentargets/platform/21.11/output/etl/json/evidence/sourceId%3Dintogen/", 80, ['targetId', 'cohortDescription'])
Parsing ftp page for JSON file list...
Parsing each JSON file in parallel...
```

`find_target_combination()` function can be used to fine combinations of targets that shared same diseases according to evidence scores medians. Though some improvement is needed still, it provided a systemically way to adress target combination seeking problem. **This function requires a target-disease association dataframe as input.**

```python
>> from find_target_combination import *
>> target_2_disease_2 = find_target_combination(result_df, median_score_cutoff=0, n_targets=2, n_diseases=2)
Filtering df with median_score_cutoff 0
Finding 2 target combinations with 2 shared diseases...
  There are 700828 combinations for now.
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
              targetID        diseaseID                                               name approvedSymbol  ...  top_1  top_2  top_3  count
0      ENSG00000000419      EFO_0003847                                 mental retardation           DPM1  ...   0.00    NaN    NaN      1
13541  ENSG00000145362  Orphanet_399805  Male infertility with azoospermia or oligozoos...           ANK2  ...   0.00    NaN    NaN      1
13571  ENSG00000145700       HP_0001657                              Prolonged QT interval        ANKRD31  ...   0.00    NaN    NaN      1
13607  ENSG00000145949       HP_0001657                              Prolonged QT interval          MYLK4  ...   0.00    NaN    NaN      1
13611  ENSG00000145982      EFO_0003847                                 mental retardation          FARS2  ...   0.00    NaN    NaN      1
...                ...              ...                                                ...            ...  ...    ...    ...    ...    ...
7880   ENSG00000117877      EFO_0004647            response to platinum based chemotherapy         POLR1G  ...   0.97    NaN    NaN      1
21095  ENSG00000186115      EFO_0005801                               cholesterol embolism         CYP4F2  ...   0.97    NaN    NaN      1
30     ENSG00000001626      EFO_0009166                   response to ivacaftor - efficacy           CFTR  ...   0.97   0.97   0.97     33
15294  ENSG00000157764   Orphanet_98733        Noonan syndrome and Noonan-related syndrome           BRAF  ...   0.97   0.97   0.97      6
9495   ENSG00000128595      EFO_0005801                               cholesterol embolism           CALU  ...   0.97    NaN    NaN      1

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

Actually this question can be solved in a more systemically way, for example:
* How to find 3 targets combinations that share 8 diseaseID?
* Same question above but only consider target-disease association median\_score >= 0.8?

So I code a function `find_target_combination` to solve this issue, which allows user to assign below three parameters:
* `df`: A `result_df` in this report.
* `median_score_cutoff`: A cutoff for median score calculated from eva file list.
* `n_targets`: number of targets combinations.
* `n_diseases`: number of shared diseases by all targets in each combinations.

For example, below code will fine all 5-targets combinations that all targets have at least 0.9 median score in 10 shared diseases:

```python
>> test = find_target_combination(result_df, median_score_cutoff=0.9, n_targets=5, n_diseases=10)
Finding 2 target combinations with 10 shared diseases...
  There are 96 combinations for now.
Finding 3 target combinations with 10 shared diseases...
  There are 594 combinations for now.
Finding 4 target combinations with 10 shared diseases...
  There are 2832 combinations for now.
Finding 5 target combinations with 10 shared diseases...
  There are 10200 combinations for now.
>>
>>> test
                                       merged_targets_id                                          diseaseID
0      ENSG00000198712-ENSG00000198763-ENSG0000019880...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
1      ENSG00000198712-ENSG00000198763-ENSG0000019880...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
2      ENSG00000198712-ENSG00000198763-ENSG0000019880...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
3      ENSG00000198712-ENSG00000198763-ENSG0000019880...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
4      ENSG00000198712-ENSG00000198763-ENSG0000019880...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
...                                                  ...                                                ...
10195  ENSG00000228253-ENSG00000212907-ENSG0000019893...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
10196  ENSG00000228253-ENSG00000212907-ENSG0000019893...  [Orphanet_551, Orphanet_96210, Orphanet_206966...
10197  ENSG00000228253-ENSG00000212907-ENSG0000019893...  [Orphanet_551, Orphanet_206966, Orphanet_225, ...
10198  ENSG00000228253-ENSG00000212907-ENSG0000019893...  [Orphanet_551, Orphanet_96210, Orphanet_206966...
10199  ENSG00000228253-ENSG00000212907-ENSG0000019893...  [Orphanet_551, Orphanet_96210, Orphanet_225, E...

[10200 rows x 2 columns]
```

Note that there are some limitations in this function, it may crach due to lack fo memory in certain parameter combinations, like `n_targets=5` while `n_diseases=2`. The combination is too much. For example below code is quite challenge to run, even one a server with 251G RAM:
```python
test = find_target_combination(result_df, median_score_cutoff=0, n_targets=3, n_diseases=2)
```

In this case, one potential solution in my mind now is to:
1. firstly split combinations first, calculate separately, then merge them. For example: if `n_targets=20`, we calculated `n_targets=10` first, then merge two `n_targets=10` dataframes **without any** target\_ID duplicated. If still `n_targets=10` is too big, we divide again to merge two `n_targets=5` .etc. 
2. In the mean time, still sometimes combinations may boosting too fast, maybe database like sqlite/hadoop can be used for batch work.
3. Biologically, use pre-researched gene lists as constrains, to reduce calculation. For example, only select hundreds of genes in one pathway, then validate their co-existing status with this function.

