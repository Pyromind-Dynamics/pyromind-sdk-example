# LoadDataset Node

![alt text](/imgs/LoadDataset/loadDataset.png)  

## 2.1.1 Overview

Receives a dataset path, validates its accessibility, and passes the path through.

- **Path Resolution**: Accepts a user-specified dataset path as input
- **Existence Validation**: Checks whether the dataset directory exists via a bash command, ensuring the path is valid
- **Output Passthrough**: Passes the validated dataset path to downstream nodes for use in training pipelines

## 2.1.2 Input

| Parameter    | Data Type | Description                                                                                |
| ------------ | --------- | ------------------------------------------------------------------------------------------ |
| dataset_path | PATH      | Path to the dataset file or directory to load. Ensure the path points to an existing dataset directory. Default: `/workspace/datasets/openai/gsm8k` |

## 2.1.3 Output

| Parameter    | Data Type | Description                                                                                                      |
| ------------ | --------- | ---------------------------------------------------------------------------------------------------------------- |
| dataset_path | STRING    | Validated dataset path (same as input), passed to downstream nodes (e.g., RL training, Rollout, etc.). Returns `Dataset path not found` if the path does not exist. |
