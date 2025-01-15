# NFL Big Data Bowl 2025 Submission: Pass-Run Play Prediction
My submission for the [Kaggle NFL Big Data Bowl 2025](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025) can be found [here](https://www.kaggle.com/code/maxfish/submisson-csv/).    
Created and maintained by @TechMax14


## Introduction

In this project, we aim to predict whether a given play in an NFL game is a **pass** or **run** based on historical data and player behavior. The challenge lies in leveraging a variety of game features, such as offensive formation, down, and player position, to accurately classify plays as either pass or run.

Traditional analysis of NFL plays tends to focus on simple statistics, such as passing attempts or rushing yards. However, predicting the play type (run or pass) before the snap opens the door for more nuanced strategies that coaches and analysts can use to prepare for upcoming games.

Our model utilizes machine learning techniques to predict the likelihood of a pass or run based on the offensive formation, down, and other situational features.

## Project Overview

This repository contains code and documentation for building a machine learning model to predict the type of play (pass or run) in NFL games. The core of this project revolves around:

1. **Data Processing**: Aggregating and preprocessing play-by-play data for training.
2. **Feature Engineering**: Creating meaningful features like offensive formation, down, and defensive mismatches.
3. **Model Training**: Using classification models to predict whether a play is a pass or a run.
4. **Model Evaluation**: Evaluating the performance of the model using various metrics like accuracy and confusion matrices.
5. **Visualization**: Displaying the results through visualizations, such as the predicted play percentages across different formations and down situations.

## Data

The project relies on NFL tracking data and play-by-play data, which can be found on platforms like [Kaggle](https://www.kaggle.com/competitions/nfl-big-data-bowl-2025/data). We preprocess the data and extract features like the offensive formation, down, and the presence of key players (e.g., wide receivers, tight ends, and running backs).

The key data files used in this project are:
- `training_data.csv`: Contains historical play data for training.
- `testing_data.csv`: Contains unseen play data for evaluation.
- `player_tracking_data.csv`: Includes player positions, speeds, and movements during each play for weeks 1-9 of the 2022 NFL season.

## Running Instructions

## Running Instructions

Follow these steps to train, test, and analyze the model:

1. **Data Preprocessing**:
    - Add the raw data files to the `data/` directory.
    - Execute the `load_data.ipynb` notebook to clean and preprocess the data. This notebook will process the raw data and prepare it for model training.

    You can run the notebook interactively by opening it in Jupyter or execute it directly via the following command:
    
    ```bash
    jupyter notebook load_data.ipynb
    ```

2. **Train the Model**:
    - After preprocessing, execute the `train_model.ipynb` notebook to train the model. This notebook will split the data into training and testing sets, train the model, and evaluate it based on accuracy and other metrics.
    
    You can run the notebook interactively by opening it in Jupyter or execute it directly via the following command:
    
    ```bash
    jupyter notebook train_model.ipynb
    ```

3. **Run Inference**:
    - Once the model is trained, execute the `run_model.ipynb` notebook to test the model on the testing data. This notebook will run inference on the data, predict whether each play is a pass or a run, and evaluate the results.
    
    You can run the notebook interactively by opening it in Jupyter or execute it directly via the following command:
    
    ```bash
    jupyter notebook run_model.ipynb
    ```

4. **Model Insights and Analysis**:
    - After running inference, execute the `model_insights.ipynb` notebook to generate analysis and insights. This notebook will provide detailed visualizations and breakdowns of model performance, including predicted vs. actual play type percentages and formation-based analysis.
    
    You can run the notebook interactively by opening it in Jupyter or execute it directly via the following command:
    
    ```bash
    jupyter notebook model_insights.ipynb
    ```



## Visualizations

This project includes several visualizations to help understand the model's performance:

1. **Team Predictability by Down**: A heatmap displaying how predictable a team's play-calling is on different downs. Higher values indicate more predictable decisions.
   
   ![Team Predictability by Down](https://raw.githubusercontent.com/TechMax14/BIG-DATA-BOWL-25/main/visuals/Model%20Results/team_predictability_by_down.png)

   *Figure 1. Play Type Predictability by Down per Team.*

2. **Play Type Predictability by Offensive Formation**: A bar chart showing the predicted pass and run percentages for each offensive formation. Formations like the I-Formation and Pistol tend to be more associated with run plays, while formations like Shotgun and Empty Set are more associated with pass plays.

   ![Play Type Predictability by Offensive Formation](https://raw.githubusercontent.com/TechMax14/BIG-DATA-BOWL-25/main/visuals/Model%20Results/formation_playtype_predictability.png)

   *Figure 2. Play Type Predictability by Offensive Formation.*

## Model Evaluation

The model is evaluated using several metrics:

- **Accuracy**: Measures the percentage of correct predictions (**88.6%**).
- **Confusion Matrix**: Provides a detailed breakdown of true positives, true negatives, false positives, and false negatives.
- **ROC-AUC**: Measures the trade-off between true positive rate and false positive rate (**92.4%**).




