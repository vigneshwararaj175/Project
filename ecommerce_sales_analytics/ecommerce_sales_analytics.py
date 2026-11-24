import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.cluster import KMeans
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')


plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


df = pd.read_csv('ecommerce_sales_analytics_5000.csv')


print("="*50)
print("DATASET OVERVIEW")
print("="*50)
print(f"Dataset Shape: {df.shape}")
print(f"\nFirst 5 rows:")
print(df.head())
print(f"\nDataset Info:")
print(df.info())
print(f"\nMissing Values:")
print(df.isnull().sum())
print(f"\nBasic Statistics:")
print(df.describe())


print(f"Duplicate rows: {df.duplicated().sum()}")
df = df.drop_duplicates()


df['order_date'] = pd.to_datetime(df['order_date'])


df['year'] = df['order_date'].dt.year
df['month'] = df['order_date'].dt.month
df['day_of_week'] = df['order_date'].dt.dayofweek
df['day_name'] = df['order_date'].dt.day_name()
df['quarter'] = df['order_date'].dt.quarter
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)


for col in df.columns:
    if df[col].isnull().sum() > 0:
        if df[col].dtype == 'object':
            df[col].fillna(df[col].mode()[0], inplace=True)
        else:
            df[col].fillna(df[col].median(), inplace=True)


numerical_cols = ['quantity', 'unit_price', 'discount', 'delivery_days', 'customer_rating', 'revenue']
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for idx, col in enumerate(numerical_cols):
    row, col_idx = idx // 3, idx % 3
    axes[row, col_idx].boxplot(df[col])
    axes[row, col_idx].set_title(f'Boxplot of {col}')
plt.tight_layout()
plt.show()


def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

print(f"Original shape: {df.shape}")
for col in ['quantity', 'unit_price', 'revenue']:
    df = remove_outliers(df, col)
print(f"Shape after removing outliers: {df.shape}")



df['discount_amount'] = df['unit_price'] * df['quantity'] * (df['discount'] / 100)


df['final_price'] = df['unit_price'] * (1 - df['discount'] / 100)


df['revenue_per_unit'] = df['revenue'] / df['quantity']


category_avg_revenue = df.groupby('product_category')['revenue'].mean().to_dict()
df['category_avg_revenue'] = df['product_category'].map(category_avg_revenue)


region_avg_revenue = df.groupby('region')['revenue'].mean().to_dict()
df['region_avg_revenue'] = df['region'].map(region_avg_revenue)


customer_freq = df.groupby('customer_id').size().reset_index(name='purchase_frequency')
df = df.merge(customer_freq, on='customer_id', how='left')


customer_spending = df.groupby('customer_id')['revenue'].sum().reset_index(name='customer_total_spending')
df = df.merge(customer_spending, on='customer_id', how='left')


df['customer_avg_order_value'] = df['customer_total_spending'] / df['purchase_frequency']


df['delivery_efficiency'] = df['delivery_days'] / df['quantity']


df['high_value_order'] = (df['revenue'] > df['revenue'].median()).astype(int)


df['discount_level'] = pd.cut(df['discount'], 
                              bins=[-1, 0, 10, 20, 100], 
                              labels=['No Discount', 'Low', 'Medium', 'High'])

print("Feature engineering completed!")
print(f"New shape: {df.shape}")
print(f"New features added: {[col for col in df.columns if col not in ['order_id', 'order_date', 'customer_id', 'product_category', 'region', 'quantity', 'unit_price', 'discount', 'payment_method', 'delivery_days', 'customer_rating', 'revenue']]}")


fig = plt.figure(figsize=(20, 16))


plt.subplot(3, 3, 1)
sns.histplot(df['revenue'], kde=True, bins=30)
plt.title('Revenue Distribution')
plt.xlabel('Revenue')


plt.subplot(3, 3, 2)
category_revenue = df.groupby('product_category')['revenue'].sum().sort_values(ascending=False)
category_revenue.plot(kind='bar', color='skyblue')
plt.title('Revenue by Product Category')
plt.xlabel('Category')
plt.ylabel('Total Revenue')
plt.xticks(rotation=45, ha='right')


plt.subplot(3, 3, 3)
region_revenue = df.groupby('region')['revenue'].sum().sort_values(ascending=False)
region_revenue.plot(kind='pie', autopct='%1.1f%%')
plt.title('Revenue Distribution by Region')


plt.subplot(3, 3, 4)
monthly_sales = df.groupby(df['order_date'].dt.to_period('M'))['revenue'].sum()
monthly_sales.plot(kind='line', marker='o')
plt.title('Monthly Sales Trend')
plt.xlabel('Month')
plt.ylabel('Revenue')


plt.subplot(3, 3, 5)
payment_counts = df['payment_method'].value_counts()
payment_counts.plot(kind='bar', color='lightgreen')
plt.title('Orders by Payment Method')
plt.xlabel('Payment Method')
plt.ylabel('Number of Orders')
plt.xticks(rotation=45)


plt.subplot(3, 3, 6)
sns.histplot(df['customer_rating'], bins=10, kde=True, color='orange')
plt.title('Customer Rating Distribution')
plt.xlabel('Rating')


plt.subplot(3, 3, 7)
sns.scatterplot(data=df, x='discount', y='revenue', hue='product_category', alpha=0.6)
plt.title('Discount vs Revenue')
plt.xlabel('Discount (%)')
plt.ylabel('Revenue')


plt.subplot(3, 3, 8)
sns.boxplot(x='product_category', y='delivery_days', data=df)
plt.title('Delivery Days by Category')
plt.xticks(rotation=45)


plt.subplot(3, 3, 9)
numerical_df = df.select_dtypes(include=[np.number])
correlation = numerical_df.corr()
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0, fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix')

plt.tight_layout()
plt.show()


print("\n" + "="*50)
print("KEY INSIGHTS")
print("="*50)
print(f"Total Revenue: ${df['revenue'].sum():,.2f}")
print(f"Average Order Value: ${df['revenue'].mean():,.2f}")
print(f"Most Popular Category: {df['product_category'].mode()[0]}")
print(f"Most Profitable Category: {category_revenue.index[0]}")
print(f"Top Region: {region_revenue.index[0]}")
print(f"Average Customer Rating: {df['customer_rating'].mean():.2f}")
print(f"Average Delivery Days: {df['delivery_days'].mean():.2f}")


categorical_cols = ['product_category', 'region', 'payment_method', 'day_name', 'discount_level']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# Select features for modeling
target = 'revenue'
exclude_cols = ['order_id', 'order_date', 'customer_id', 'revenue', 
                'final_price', 'revenue_per_unit', 'discount_amount']  # Redundant or target-related

feature_cols = [col for col in df_encoded.columns if col not in exclude_cols and df_encoded[col].dtype in ['int64', 'float64', 'bool']]

X = df_encoded[feature_cols]
y = df_encoded[target]

print(f"Features shape: {X.shape}")
print(f"Target shape: {y.shape}")
print(f"\nTop 20 Features:")
print(X.columns[:20])
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=1.0),
    'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
}

results = {}
for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    

    results[name] = {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2,
        'model': model
    }
    
    print(f"\n{name}:")
    print(f"  MAE: ${mae:,.2f}")
    print(f"  RMSE: ${rmse:,.2f}")
    print(f"  R² Score: {r2:.4f}")


best_model_name = max(results, key=lambda x: results[x]['R2'])
best_model = results[best_model_name]['model']
print(f"\n🏆 Best Model: {best_model_name} with R² = {results[best_model_name]['R2']:.4f}")


if best_model_name == 'Random Forest':
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    grid_search = GridSearchCV(RandomForestRegressor(random_state=42), 
                               param_grid, 
                               cv=5, 
                               scoring='r2',
                               n_jobs=-1)
    
elif best_model_name == 'Gradient Boosting':
    param_grid = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 0.2],
        'max_depth': [3, 5, 7],
        'min_samples_split': [2, 5, 10]
    }
    
    grid_search = GridSearchCV(GradientBoostingRegressor(random_state=42), 
                               param_grid, 
                               cv=5, 
                               scoring='r2',
                               n_jobs=-1)


print("Performing hyperparameter tuning...")
grid_search.fit(X_train_scaled, y_train)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best cross-validation score: {grid_search.best_score_:.4f}")


best_model_tuned = grid_search.best_estimator_
y_pred_tuned = best_model_tuned.predict(X_test_scaled)
r2_tuned = r2_score(y_test, y_pred_tuned)
print(f"Tuned model R² Score: {r2_tuned:.4f}")


customer_data = df.groupby('customer_id').agg({
    'revenue': ['sum', 'mean', 'count'],
    'quantity': 'sum',
    'discount': 'mean',
    'delivery_days': 'mean',
    'customer_rating': 'mean'
}).reset_index()


customer_data.columns = ['customer_id', 'total_revenue', 'avg_order_value', 
                         'order_count', 'total_quantity', 'avg_discount', 
                         'avg_delivery_days', 'avg_rating']


first_purchase = df.groupby('customer_id')['order_date'].min().reset_index()
last_purchase = df.groupby('customer_id')['order_date'].max().reset_index()
customer_data = customer_data.merge(first_purchase, on='customer_id')
customer_data = customer_data.merge(last_purchase, on='customer_id', suffixes=('_first', '_last'))
customer_data['tenure_days'] = (customer_data['order_date_last'] - customer_data['order_date_first']).dt.days


cluster_features = ['total_revenue', 'order_count', 'total_quantity', 'avg_order_value', 'tenure_days']
X_cluster = customer_data[cluster_features]


scaler_cluster = StandardScaler()
X_cluster_scaled = scaler_cluster.fit_transform(X_cluster)


inertias = []
silhouette_scores = []
K_range = range(2, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X_cluster_scaled)
    inertias.append(kmeans.inertia_)
    
    from sklearn.metrics import silhouette_score
    silhouette_scores.append(silhouette_score(X_cluster_scaled, kmeans.labels_))


fig, axes = plt.subplots(1, 2, figsize=(15, 5))
axes[0].plot(K_range, inertias, 'bx-')
axes[0].set_xlabel('Number of Clusters (k)')
axes[0].set_ylabel('Inertia')
axes[0].set_title('Elbow Method')

axes[1].plot(K_range, silhouette_scores, 'rx-')
axes[1].set_xlabel('Number of Clusters (k)')
axes[1].set_ylabel('Silhouette Score')
axes[1].set_title('Silhouette Analysis')
plt.tight_layout()
plt.show()


optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2  # +2 because range starts at 2
print(f"Optimal number of clusters: {optimal_k}")

kmeans = KMeans(n_clusters=optimal_k, random_state=42)
customer_data['customer_segment'] = kmeans.fit_predict(X_cluster_scaled)


segment_analysis = customer_data.groupby('customer_segment').agg({
    'total_revenue': 'mean',
    'order_count': 'mean',
    'total_quantity': 'mean',
    'avg_order_value': 'mean',
    'tenure_days': 'mean',
    'customer_id': 'count'
}).round(2)

segment_analysis.columns = ['Avg Revenue', 'Avg Orders', 'Avg Quantity', 'Avg Order Value', 'Avg Tenure (days)', 'Customer Count']
print("\nCustomer Segment Analysis:")
print(segment_analysis)


plt.figure(figsize=(10, 8))
scatter = plt.scatter(customer_data['total_revenue'], 
                     customer_data['order_count'], 
                     c=customer_data['customer_segment'], 
                     cmap='viridis', 
                     alpha=0.6)
plt.colorbar(scatter, label='Segment')
plt.xlabel('Total Revenue')
plt.ylabel('Number of Orders')
plt.title('Customer Segments Visualization')
plt.show()


df.set_index('order_date', inplace=True)
monthly_revenue = df['revenue'].resample('ME').sum()
weekly_revenue = df['revenue'].resample('W').sum()


fig, axes = plt.subplots(2, 1, figsize=(15, 10))

axes[0].plot(monthly_revenue.index, monthly_revenue.values, marker='o', linewidth=2)
axes[0].set_title('Monthly Revenue Trend')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Total Revenue')

axes[1].plot(weekly_revenue.index, weekly_revenue.values, linewidth=1)
axes[1].set_title('Weekly Revenue Trend')
axes[1].set_xlabel('Date')
axes[1].set_ylabel('Total Revenue')

plt.tight_layout()
plt.show()


if len(monthly_revenue) > 1:
    growth_rate = ((monthly_revenue.iloc[-1] - monthly_revenue.iloc[0]) / monthly_revenue.iloc[0]) * 100
    print(f"Overall revenue growth: {growth_rate:.2f}%")
    

    mom_growth = monthly_revenue.pct_change() * 100
    print(f"Average month-over-month growth: {mom_growth.mean():.2f}%")


df['month'] = df.index.month
monthly_avg = df.groupby('month')['revenue'].mean()
plt.figure(figsize=(10, 6))
monthly_avg.plot(kind='bar', color='lightcoral')
plt.title('Average Revenue by Month (Seasonality)')
plt.xlabel('Month')
plt.ylabel('Average Revenue')
plt.show()


report = f"""
E-COMMERCE SALES ANALYTICS REPORT
=================================

EXECUTIVE SUMMARY
----------------
Total Revenue: ${df['revenue'].sum():,.2f}
Total Orders: {len(df):,}
Average Order Value: ${df['revenue'].mean():,.2f}
Average Customer Rating: {df['customer_rating'].mean():.2f}/5.0

TOP PERFORMING CATEGORIES
------------------------
{category_revenue.head(3).to_string()}

REGIONAL PERFORMANCE
-------------------
{region_revenue.to_string()}

CUSTOMER SEGMENTS
----------------
{segment_analysis.to_string()}

MODEL PERFORMANCE
----------------
Best Model: {best_model_name}
R² Score: {results[best_model_name]['R2']:.4f}
Mean Absolute Error: ${results[best_model_name]['MAE']:,.2f}

KEY INSIGHTS
------------
1. Peak shopping periods identified for targeted marketing
2. {optimal_k} distinct customer segments identified
3. Top categories account for {category_revenue.head(3).sum() / category_revenue.sum() * 100:.1f}% of revenue
4. Average delivery time: {df['delivery_days'].mean():.1f} days

RECOMMENDATIONS
---------------
1. Focus marketing on high-revenue categories and regions
2. Implement loyalty programs for high-value customer segments
3. Optimize delivery for categories with long delivery times
4. Use pricing strategies based on regional preferences
5. Target discounts to increase sales in underperforming categories
6. Monitor customer ratings and address low-rated products/services
"""

# Save report
with open('ecommerce_analysis_report.txt', 'w') as f:
    f.write(report)

print(report)
print("\n✅ Analysis complete! Report saved as 'ecommerce_analysis_report.txt'")

