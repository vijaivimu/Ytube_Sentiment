# Welcome to the SuperDataScience Community Project!
Welcome to the Sentiment Analysis using YouTube repository! 🎉

This project is a collaborative initiative brought to you by SuperDataScience, a thriving community dedicated to advancing the fields of data science, machine learning, and AI. We are excited to have you join us in this journey of learning, experimentation, and growth.

# Project Scope of Works:

## Project Overview

This project focuses on performing sentiment analysis using tweets collected from YouTube channels. The project targets beginner to intermediate-level data scientists and involves building a machine learning pipeline to extract, analyze, and predict the sentiment of comments on YouTube videos. An ETL (Extract, Transform, Load) pipeline will be orchestrated using Apache Airflow to ensure seamless data management, while a machine learning model will be developed and deployed using Streamlit for real-time sentiment analysis.

## Objectives

### 1. Data Collection and Storage:
- Use the YouTube API to collect comments of recent/relevant videos of a YouTube channel.
- Store the collected comments in a structured database for analysis.

### 2. ETL Pipeline Setup:
- Build an ETL pipeline using Apache Airflow to automate the process of fetching, cleaning, and storing tweet data.

### 3. Sentiment Analysis Model Development:
- Perform data preprocessing and exploratory data analysis (EDA).
- Use a machine learning model from Huggingface to classify the sentiment of comments as positive, negative, or neutral.

### 4. Model Deployment:
- Deploy the sentiment analysis model using Streamlit/Huggingface to provide an interactive web application for real-time analysis.

## Technical Requirements

### Tools and Libraries:
- **API Integration:** Google Developer Portal, YouTube API.
- **ETL Pipeline:** Apache Airflow, Pandas.
- **Database:** PostgreSQL, SQLite, MySQL, etc.
- **Model Development:** scikit-learn, TensorFlow/PyTorch, Huggingface Transformers.
- **Deployment:** Streamlit.

### Environment:
- Python 3.8+
- Libraries: pandas, google-api-python-client, scikit-learn, transformers, streamlit, airflow.

## Workflow

### Phase 1: Setup (1 Week)
- Follow Intro to Git & GitHub tutorial on SDS to get started with cloning the SDS GitHub repo to your laptop/desktops.
- Setup an account on Google Developer using the following video for guidance (https://www.youtube.com/watch?v=th5_9woFJmk).

### Phase 2: Data Collection (1 Week)
- Register and authenticate with YouTube API.
- Write Python scripts to fetch and store comments.

### Phase 3: ETL Pipeline Development (1 Week)
- Build Airflow DAGs for automated tweet extraction, cleaning, and storage.
- Test and optimize data loading into a database.

### Phase 4: Sentiment Analysis Model (1 Week)
- Conduct EDA and preprocess comments data.
- Evaluate a sentiment analysis model.

### Phase 5: Model Deployment (1 Week)
- Build a Streamlit app with input options for YouTube channel/video comments to retrieve.
- Deploy the app on Streamlit/Huggingface.

## Timeline

| Phase          | Task                                 | Duration |
|----------------|--------------------------------------|----------|
| Phase 1: Setup | Setup GitHub repo & API Credentials  | Week 1   |
| Phase 2: Data  | Data collection via YouTube API      | Week 2   |
| Phase 3: ETL   | Build and test Airflow pipeline      | Week 3   |
| Phase 4: Model | Train and evaluate sentiment model   | Week 4   |
| Phase 5: Deployment | Deploy Streamlit app             | Week 5   |


# Getting Started

Follow these steps to set up the project locally:

## 1. Fork the Repository
To work on your own copy of this project:
1. Navigate to the SDS GitHub repository for this project.  
2. Click the **Fork** button in the top-right corner of the repository page.  
3. This will create a copy of the repository under your GitHub account.

---

## 2. Clone the Repository
After forking the repository:
1. Open a terminal on your local machine.  
2. Clone your forked repository by running:
   ```bash
   git clone https://github.com/<your-username>/<repository-name>.git
   ```
3. Navigate to the project directory:
    ```bash
    cd <repository-name>
    ```

## 3. Create a virtual environment
Setup a virtual environment to isolate project dependancies
1. Run the following command in the terminal to create a virtual environment
    ```bash
    python3 -m venv .venv
    ```
2. Activate the virtual environment
  - On a mac/linux:
    ```bash
    source .venv/bin/activate
    ```
  - On a windows:
    ```
    .venv\Scripts\activate
    ```
3. Verify the virtual environment is active (the shell prompt should show (.venv))

## 4. Install dependancies
Install the required libraries for the project
1. Run the following command in the terminal to isntall dependancies from the requirements.txt file:
    ```bash
    pip install -r requirements.txt
    ```
Once the setup is complete, you can proceed with building your project
