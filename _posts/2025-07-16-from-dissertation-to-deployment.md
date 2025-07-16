---
title: "From Dissertation to Deployment: Building My xG Plotter"
date: 2025-07-16 21:00:00 BST
categories: [Sports Analytics, xG Plotter]
tags: [python, flask, web development, full-stack development, sports analytics, xg, xG (Expected Goals), machine learning, scikit-learn, data science, javascript, tailwind css, football, data visualisation, api]
math: true
---

[Visit my xG Plotter](https://atredshaw.github.io/Redshaw-xG/)

For what feels like forever now, I’ve been fascinated by the intersection of football and data. It all started with Fantasy Premier League (FPL) then continued as a part of my university dissertation, where I plunged headfirst into the world of probabilistic machine learning models. This included a particular focus on the now-famous Expected Goals (xG) metric, achieving a first class grade in the process - to this day it is still probably the most proud I am of any work I have completed. I spent months buried in research papers and datasets, exploring how we could quantify the beautiful game’s most decisive moments. Ever since then, a little idea has been bubbling away in the back of my mind: to build my own interactive xG plotter from the ground up. I'd initially planned this as a part of my project to show off the models interactively, but ultimately deemed this to be a creep in scope that was not applicable, nor worthwhile, for the purposes of my dissertation.

Well, I’m thrilled to say, it’s finally here! This project is the culmination of that long-held ambition, a journey of rebuilding my original models in a far more structured, robust way and bringing them to life through a full-stack, interactive web application. It’s been a labour of love, so I wanted to pull back the curtain and share a little about how it was all put together.

## Part 1: The Backend Engine - The Brains of the Operation

Everything starts with the data and the models. Without a solid foundation here, the fanciest frontend in the world would be nothing more than a pretty picture. The entire backend is a self-contained pipeline, designed to be run from a single script, `run_pipeline.sh`, which orchestrates the entire process from raw data to deployable models.

### Step 1: Gathering the Raw Ingredients

You can't build a model without data. A Python script using the brilliant `understat.com`, and the BeautifulSoup library, was created to scrape thousands upon thousands of shots from Europe's top leagues over several seasons. This gave me a rich, detailed dataset capturing everything from the on-pitch coordinates to the game situation (like Open Play or a Set Piece) and the body part used for the shot.

### Step 2: Data Cleansing and Feature Engineering

Raw data is messy. The next crucial step was a rigorous cleansing process to handle inconsistencies and prepare it for modelling. But the real magic is in **feature engineering**. While the `x` and `y` coordinates are a good start, their true power is unlocked when you derive more meaningful features from them. The two most important are:

*   **Distance to Goal:** A simple Euclidean distance calculation from the shot location to the centre of the goal.
*   **Angle to Goal:** Using a bit of trigonometry to calculate the angle the shooter has to the goal. A wider angle is almost always a better scoring opportunity.

Categorical data, like `situation` and `shot_type`, was converted into a numerical format using one-hot encoding, allowing the machine learning model to understand it. Interaction features were also created where it was appropriate for the strain of model, as is explained in the following step.

### Step 3: Building the Intelligence with `scikit-learn`

With a clean, feature-rich dataset, it was time to train the models. I opted for **Logistic Regression**, a robust and highly interpretable algorithm perfect for a binary classification task like predicting a goal (1) or no goal (0). I did do some comparative experimentation with random forest models, but as I found in my dissertation, they performed better in some of the more common aras of the pitch, but rather unexplainably poorer in other edge cases (e.g. suggesting shots from the corner flag had an approximately 25% chance of being converted). I have previously explored using some sort of hybrid approach to get the best of both worlds, but the boost in performance (namely in the brier score) is so negligible it makes it unworthwhile. This is also the case for the difference between the logistic regression and random forest models, hence the decision to stick with Logistic Regression for it's smoothness and interpretability.

Instead of a one-size-fits-all approach, I trained four distinct models to provide more specialised predictions. The backend intelligently selects the best one based on the user's input:

1.  **Basic Model:** The simplest, using only location-based features.
2.  **Situation Model:** Adds the context of the game situation.
3.  **Shot Type Model:** Factors in whether the shot was a header or taken with the left or right foot.
4.  **Advanced Model:** The most comprehensive, using all available features for the most nuanced predictions.

All models were trained and saved as `.joblib` files, ready to be loaded into the API.

### Step 4: Pre-calculating Heatmaps

To power the 'Heatmaps' page without making users wait, a final pipeline step pre-calculates the xG value for a fine grid of points across the entire pitch. This is done for every `situation` and `shot_type` combination, and the results are stored in a single, optimised `heatmaps.json` file. This means that when a user requests a heatmap, the frontend can simply fetch the pre-calculated data, making the experience incredibly fast.

### Step 5: Serving the Models with a Flask API

With the models trained and heatmaps generated, they needed to be exposed to the world. A lightweight backend server built with **Flask** handles this. It exposes two key endpoints:

*   `POST /redshaw-xg/api/predict`: This endpoint receives the details of a single shot from the frontend, selects the appropriate model, preprocesses the inputs, and returns a live xG prediction.
*   `GET /redshaw-xg/api/predict/grid`: This endpoint serves the pre-generated `heatmaps.json` data, allowing the frontend to visualise the model's predictions quickly and efficiently.

The entire backend was then deployed on Render, ensuring it's always available and ready to serve predictions.

## Part 2: The Frontend Experience - Where Data Meets Design

The frontend is where the models come to life. Built with clean HTML, styled with the fantastic **Tailwind CSS**, and powered by vanilla JavaScript, it’s designed to be intuitive, interactive, and informative.

### The Homepage: Your First Interaction

The landing page offers a gentle introduction to the world of xG and provides a simple, interactive pitch. Users can click anywhere on the pitch, select a game situation and shot type, and instantly get an xG prediction from the backend. It’s the perfect way to get a feel for how different factors influence the probability of scoring.

### The Heatmaps: A Visual Deep-Dive

The 'Heatmaps' page allows for a deeper exploration of the model's patterns. Users can select a situation and shot type to see a full-pitch heatmap, revealing xG hotspots. Want to see how much more likely a header is to go in from the six-yard box compared to the penalty spot? This is the place to find out. The colours instantly tell the story, from the cool blues of low-probability chances to the fiery reds of near-certain goals.

### The Plotter: Recreate the Match

This is the most ambitious part of the application. The 'Plotter' page allows you to recreate the shot map for an entire match. You can create a match, define the home and away teams (and their colours!), and then plot shots for each side. The application keeps a running tally of the cumulative xG for both teams, providing a data-driven narrative of the game. You can even save your created matches in your browser's local storage (using IndexedDB) and load them up later!

### The API Documentation

For fellow developers and data enthusiasts, I created a dedicated API documentation page. It details exactly how to interact with the prediction and heatmap endpoints, providing example requests and responses to make it as easy as possible for others to build on this work.

## From Academia to Application

This project has been an incredible learning experience, taking a concept from my dissertation and building it into a tangible, interactive tool, deployed into production, that anyone can use. It’s a testament to the power of modern development tools like Python, Flask, and scikit-learn, and a reminder that with a bit of persistence, you can turn an old academic idea into a real-world application, even if only for a bit of fun!

---

***This project is fully open-source. You can find the complete code for both the backend and frontend on my [GitHub](https://github.com/ATRedshaw/Redshaw-xG).***