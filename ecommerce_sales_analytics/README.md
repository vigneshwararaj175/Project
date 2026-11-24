
# 🛒 E-Commerce Sales Analytics & Predictive Modeling

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Manipulation-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-Machine_Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualization-11557c?style=for-the-badge)

An end-to-end data science project that performs comprehensive exploratory data analysis (EDA), feature engineering, predictive modeling, and customer segmentation on an e-commerce dataset of 5,000 transactions. 

This project transforms raw sales data into actionable business insights, predicts future revenue using machine learning, and identifies distinct customer segments for targeted marketing.

## ✨ Key Features

- **🧹 Data Cleaning & Preprocessing:** Handles missing values, removes duplicates, and utilizes the IQR (Interquartile Range) method to eliminate outliers in pricing, quantity, and revenue.
- **🛠️ Advanced Feature Engineering:** Extracts time-based features (month, quarter, day of week), calculates discount amounts, and aggregates customer-level metrics like purchase frequency and average order value (AOV).
- **📊 Exploratory Data Analysis (EDA):** Generates a 9-panel visualization dashboard including heatmaps, correlation matrices, boxplots, and trend lines to uncover patterns in revenue by region, category, and payment method.
- **🤖 Predictive Modeling (Regression):** Trains and evaluates 5 different machine learning models (Linear Regression, Ridge, Lasso, Random Forest, Gradient Boosting) to predict order revenue. Automatically performs hyperparameter tuning via `GridSearchCV` on the best-performing model.
- **🎯 Customer Segmentation (Clustering):** Utilizes K-Means clustering (with Elbow and Silhouette analysis) to segment customers based on tenure, total spending, and order frequency.
- **📈 Time-Series Analysis:** Resamples data to identify weekly and monthly revenue trends, calculates month-over-month growth, and visualizes seasonal shopping peaks.
- **📝 Automated Reporting:** Generates a text-based executive summary report (`ecommerce_analysis_report.txt`) with actionable recommendations based on the analysis.

---

## 🛠️ Tech Stack

- **Data Manipulation:** `pandas`, `numpy`
- **Data Visualization:** `matplotlib`, `seaborn`
- **Machine Learning:** `scikit-learn` (Regressors, KMeans, StandardScaler, GridSearchCV)
- **Environment:** Python 3.9+

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ecommerce_sales_analytics.git
cd ecommerce_sales_analytics
```

### 2. Install Dependencies
Ensure you have Python installed, then install the required libraries:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

### 3. Dataset Setup
Ensure the dataset file named `ecommerce_sales_analytics_5000.csv` is placed in the **root directory** of the project folder. 
*(If you do not have this file, you can generate a synthetic dataset or adjust the `pd.read_csv()` file path in the script).*

### 4. Run the Script
```bash
python ecommerce_analysis.py
```
*(Replace `ecommerce_analysis.py` with the actual name of your Python file).*

---

## 📂 Project Structure

```text
ecommerce_sales_analytics/
│
├── ecommerce_analysis.py           # Main Python script containing EDA, ML, and reporting
├── ecommerce_sales_analytics_5000.csv # Dataset (not included in repo if too large)
├── ecommerce_analysis_report.txt   # Auto-generated report output
└── README.md                       # Project documentation
```

---

## 📊 Output & Insights Generated

When you run the script, it will generate multiple visualizations in pop-up windows and output a comprehensive report to your console and a text file. Key insights include:

1. **Top Categories:** Identifies which product categories generate the most revenue.
2. **Regional Performance:** Highlights the strongest geographic markets.
3. **Optimal Pricing:** Analyzes the relationship between discounts and total revenue.
4. **Customer Segments:** Groups customers into tiers (e.g., "High-Value", "Frequent Buyers") allowing for targeted loyalty programs.
5. **Model Performance:** Identifies the most accurate ML model (typically Random Forest or Gradient Boosting) and its R² score for predicting revenue.

---
