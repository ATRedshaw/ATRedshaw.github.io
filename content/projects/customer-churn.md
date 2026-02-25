# Customer Churn Predictor

## Overview

This project focuses on predicting customer churn in the telecommunications sector. By analyzing customer behavior and demographic data, the model identifies high-risk customers, allowing the company to take proactive retention measures.

## Key Features

- **Data Preprocessing**: Handling missing values, encoding categorical variables, and feature scaling.
- **Model Selection**: Compared Logistic Regression, Random Forest, and XGBoost. XGBoost yielded the best performance with an AUC-ROC of 0.85.
- **API Deployment**: The model is served via a FastAPI endpoint, containerized with Docker for easy deployment.

## Technical Stack

- **Language**: Python 3.9
- **Libraries**: Pandas, Scikit-learn, XGBoost, FastAPI
- **Tools**: Docker, Git

## Code Snippet

Here is how the data is preprocessed:

```python
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

numeric_features = ['tenure', 'monthly_charges', 'total_charges']
categorical_features = ['contract', 'payment_method', 'gender']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(drop='first'), categorical_features)
    ])
```

## Results

The final model achieved an accuracy of 82% and an AUC-ROC score of 0.85 on the test set. The most important features influencing churn were contract type, tenure, and monthly charges.

![Confusion Matrix](https://via.placeholder.com/600x400?text=Confusion+Matrix)

## Future Work

- Incorporate more granular usage data.
- Experiment with Deep Learning models for potentially better performance.
