# An Audit of Misinformation Filter Bubbles on YouTube: Bubble Bursting and Recent Behavior Changes

This repository contains supplementary material for the paper published at ACM RecSys 2021 ([available here](https://dl.acm.org/doi/10.1145/3460231.3474241)) and an extended version of the same paper that was submitted to ACM TORS 2022 and is currently under review.

### Citing the Paper:
If you make use of any data or modules in this repository, please cite the following paper:
> Matus Tomlein, Branislav Pecher, Jakub Simko, Ivan Srba, Robert Moro, Elena Stefancova, Michal Kompan, Andrea Hrckova, Juraj Podrouzek, and Maria Bielikova. 2021. An Audit of Misinformation Filter Bubbles on YouTube: Bubble Bursting and Recent Behavior Changes. In <i>Fifteenth ACM Conference on Recommender Systems</i> (<i>RecSys '21</i>). Association for Computing Machinery, New York, NY, USA, 1–11. DOI: https://doi.org/10.1145/3460231.3474241


## Abstract

The negative effects of misinformation filter bubbles in adaptive systems have been known to researchers for some time. Several studies investigated, most prominently on YouTube, how fast a user can get into a misinformation filter bubble simply by selecting "wrong choices" from the items offered. Yet, no studies so far have investigated what it takes to "burst the bubble", i.e., revert the bubble enclosure. We present a study in which pre-programmed agents (acting as YouTube users) delve into misinformation filter bubbles by watching misinformation promoting content (for various topics). Then, by watching misinformation debunking content, the agents try to burst the bubbles and reach more balanced recommendation mixes. We recorded the search results and recommendations, which the agents encountered, and analyzed them for the presence of misinformation. Our key finding is that bursting of a filter bubble is possible, albeit it manifests differently from topic to topic. Moreover, we observe that filter bubbles do not truly appear in some situations. We also draw a direct comparison with a previous study. Sadly, we did not find much improvements in misinformation occurrences, despite recent pledges by YouTube.

## Structure of repository

This repository is structured in three folders:

1. Code – source code for sockpuppeting bots
2. Data – collected, processed and annotated datasets
3. Notebooks – notebooks for data analysis containing results discussed in the paper


## Source code for sockpuppeting bots

See the README file under the `Code` folder to learn more.

*Note:* In our experiments, the bot was running in Google Chrome browser version 88, with chromedriver version 88.0.4324.96. The python version used was 3.8.7 with the Dockerfile being based on Debian version 10.7.
As adblock, we used uBlockOrigin, which is provided in the code as `.crx` file.

## Datasets

We provide three CSV datasets with raw data (contained in `raw_data` directory):

1. `search_results.csv` containing annotated and processed top-20 results for queries executed after watching videos on YouTube.
2. `recommendations.csv` containing annotated and processed top-20 recommendations shown next to watched videos on YouTube.
3. `home_page_results.csv` containing collected and processed results from homepage visits executed after watching videos.

In addition, we provide two additional datasets with mapping of videos to their normalized labels (contained in `normalized_data` directory):

1. `encountered_videos.csv` containing normalized labels for the videos we encountered and then annotated during experiments. The file was obtained by running the `normalize-annotations.ipynb` notebook.
2. `seed_videos.csv` containing the videos we used as seed for running the experiments, along with their assigned labels and topics.

We also provide two additional datasets that contain aggregated data that includes automatically generated predictions using a machine learning model (contained in `predicted_data` directory):

1. `recommendations_with_predicted_grouped.csv` containing misinformation score and ratio of annotated to automatically predicted labels for top-10 recommendations grouped by misinformation topic and sequence index within the experiment.
2. `home_page_with_predicted_grouped.csv` containing misinformation score and ratio of annotated to automatically predicted labels for home page results grouped by misinformation topic and sequence index within the experiment.

### Search results

Each row represents one search result displayed on YouTube.

Please refer to the paper for discussion of annotation classes.

| Column                 | Example                    | Description                                   |
| ---------------------- | -------------------------- | --------------------------------------------- |
| youtube\_id            | nbmMwMQEK9Y                | YouTube ID of the video in the search result  |
| bot\_id                | 5                          | Identifier of the bot performing the search |
| topic                  | 911                        | Identifier of the conspiratory topic of videos the bot was watching and searching |
| experiment             | 911                        | Identifier of the overall executed experiment (in this case, same as topic) |
| query                  | 9/11 conspiracy            | Search query used for these search results |
| position               | 13                         | Position within the list of search results |
| sequence\_number       | 219                        | Ordering of this search action within all actions executed by the bot |
| seed\_sequence         | 48                         | Ordering of this search action within search actions executed by the bot (0 to 80) |
| sequence\_name         | 48                         | Label for ordering of this search action within search actions executed by the bot (0 to 80) |
| annotation             | 2                          | Number code of the annotation given to the video with respect to the topic |
| normalized\_annotation | -1                         | Number code of the annotation normalized to range -1 to 1 |
| annotation\_label      | (2) debunking unrelated    | Readable label of the annotation |
| started\_at            | 2021-03-17 18:18:09.815451 | Timestamp of the search action |

### Recommendations

Each row represents one recommended video displayed on YouTube in the top-20
recommendations beside watched videos.

Please refer to the paper for discussion of annotation classes.

| Column                 | Example                    | Description                                   |
| ---------------------- | -------------------------- | --------------------------------------------- |
| watched\_youtube\_id   | 7aNnDjQxBNQ                | YouTube ID of the watched video next to which the recommendations were displayed |
| youtube\_id            | nJZBqmGLHQ8                | YouTube ID of the recommended video |
| bot\_id                | 5                          | Identifier of the bot watching the video |
| topic                  | 911                        | Identifier of the conspiratory topic of videos the bot was watching and searching |
| experiment             | 911                        | Identifier of the overall executed experiment (in this case, same as topic) |
| position               | 9                          | Position of the recommended video within list of recommendations |
| sequence\_number       | 144                        | Ordering of this video watching action within all actions executed by the bot |
| seed\_sequence         | 32                         | Ordering of this video watching action within video watching actions executed by the bot (0 to 80) |
| sequence\_name         | 32                         | Label for ordering of this video watching action within video watching actions executed by the bot (0 to 80) |
| annotation             | 5                          | Number code of the annotation given to the recommended video with respect to the topic |
| normalized\_annotation | 0                          | Number code of the annotation normalized to range -1 to 1 |
| annotation\_label      | (5) not about misinfo      | Readable label of the annotation |
| normalized\_label      | other                      | Readable label of the annotation normalized to range -1 to 1 |
| started\_at            | 2021-03-25 10:00:33.745248 | Timestamp of the video watching action |

### Homepage results

Each row represents one homepage result displayed on YouTube.

Please refer to the paper for discussion of annotation classes.

*Note:* This dataset was not annotated. Some annotations are still present as a result of the videos also appearing in recommendations or search results.

| Column                 | Example                    | Description                                   |
| ---------------------- | -------------------------- | --------------------------------------------- |
| youtube\_id            | Ds390gg6Kqs                | YouTube ID of the video appearing on homepage  |
| bot\_id                | 4                          | Identifier of the bot performing the visit to homepage |
| topic                  | chemtrails                 | Identifier of the conspiratory topic of videos the bot was watching and searching |
| experiment             | chemtrails                 | Identifier of the overall executed experiment (in this case, same as topic) |
| position               | 15                         | Position within the list of homepage results, going from top left to bottom right |
| sequence\_number       | 1                          | Ordering of this homepage action within all actions executed by the bot |
| seed\_sequence         | 0                          | Ordering of this homepage action within search actions executed by the bot (0 to 80) |
| sequence\_name         | A: start                   | Label for ordering of this homepage action within homepage actions executed by the bot (0 to 80) - in this case, corresponds to 0 |
| annotation             | -2                         | Number code of the annotation given to the video with respect to the topic (in this case, the video was not annotated) |
| normalized\_annotation |                            | Number code of the annotation normalized to range -1 to 1. Left empty as the video was not annotated |
| annotation\_label      | not annotated              | Readable label of the annotation |
| normalized\_label      | not annotated              | Readable label of the annotation normalized to range -1 to 1 |
| started\_at            | 2021-03-10 10:39:54.398890 | Timestamp of the homepage action |

### Aggregated datasets

The aggregated datasets for top-10 recommendations and home page results also consider automatically predicted annotations. Due to ethical risks, we only publish aggregated statistics.

| Column         | Example    | Description                                   |
| -------------- | ---------- | --------------------------------------------- |
| topic          | chemtrails | Identifier of the conspiratory topic of videos the bot was watching and searching |
| seed\_sequence | 0          | Ordering of this action within all actions executed by the bot (0 to 80) |
| score | 0.11 | Average number code of the annotation normalized to range -1 to 1 for the considered videos |
| annotated      |            | Ratio of manually annotated videos out of all considered. Labels for the remaining videos were automatically predicted using machine learning. |

## Notebooks for data analysis

There are five Jupyter Notebooks contained in this folder:

1. `rq1-compare-results-with-hussein.ipynb` contains analyses related to the first research question discussed in the paper.
1. `rq2-statistical-tests.ipynb` contains analyses related to the second research question discussed in the paper.
1. `rq2-trends.ipynb` contains visualizations of changes in misinformation scores over the experiments discussed in the paper.
1. `normalize-annotations.ipynb` contains code for obtaining the normalized labels for the videos we annotated using the raw data.
1. `reimplemented-model-by-hou.ipynb` contains the reimplemented model by Hout et al discussed in the extended version of our paper.
