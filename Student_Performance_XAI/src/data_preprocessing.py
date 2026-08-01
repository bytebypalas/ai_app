"""
STEP 4 & 5: Data Preprocessing & Feature Engineering
File: src/data_preprocessing.py
Input:  dataset/raw/student_data_raw.csv
Output: dataset/processed/student_data_cleaned.csv
        models/preprocessor.pkl
        models/label_encoder.pkl
"""

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')


def load_data(filepath):
    df = pd.read_csv(filepath)
    print(f"Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def check_missing_values(df):
    missing = df.isnull().sum()
    if missing.sum() == 0:
        print("No missing values found.")
    else:
        print("Missing values detected:", missing[missing > 0])
    return missing


def check_duplicates(df):
    dup = df.duplicated().sum()
    if dup == 0:
        print("No duplicate records found.")
    else:
        print(f"Found {dup} duplicates. Removing...")
        df.drop_duplicates(inplace=True)
    return dup


def check_data_types(df):
    info = pd.DataFrame({
        'Column': df.columns,
        'Dtype': df.dtypes.values,
        'Non-Null': df.count().values,
        'Unique': [df[c].nunique() for c in df.columns]
    })
    print(info.to_string(index=False))
    return info


def handle_outliers(df, columns, threshold=1.5):
    print("Outlier Detection & Treatment:")
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lo = Q1 - threshold * IQR
        hi = Q3 + threshold * IQR
        n = ((df[col] < lo) | (df[col] > hi)).sum()
        if n > 0:
            df[col] = df[col].clip(lo, hi)
            print(f"  {col}: capped {n} outliers")
    return df


def feature_engineering(df):
    marks_cols = ['Previous_Academic_Marks', 'Internal_Assessment_Marks',
                  'Assignment_Score', 'Practical_Lab_Score']
    df['Academic_Consistency'] = df[marks_cols].std(axis=1).round(2)
    df['Overall_Academic_Score'] = (
        df['Previous_Academic_Marks'] * 0.25 +
        df['Internal_Assessment_Marks'] * 0.25 +
        df['Assignment_Score'] * 0.20 +
        df['Practical_Lab_Score'] * 0.20 +
        (df['Previous_Semester_GPA'] / 10 * 100) * 0.10
    ).round(2)
    df['Engagement_Score'] = (df['Class_Participation'] * 0.5 + df['Assignment_Submission_Rate'] * 0.5).round(2)
    df['Study_Efficiency'] = df.apply(
        lambda r: round(r['Study_Hours_Per_Day'] / (r['Number_of_Backlogs'] + 1), 2), axis=1
    )
    edu_map = {0: 'None', 1: 'High_School', 2: 'Graduate', 3: 'Post_Graduate', 4: 'Doctorate'}
    df['Parental_Education_Label'] = df['Parental_Education'].map(edu_map)
    print("Created features: Academic_Consistency, Overall_Academic_Score, Engagement_Score, Study_Efficiency")
    return df


def encode_target_variable(df):
    le = LabelEncoder()
    order = ['Poor', 'Average', 'Good', 'Excellent']
    le.fit(order)
    # Fix: manually set classes to ensure correct order
    le.classes_ = np.array(['Poor', 'Average', 'Good', 'Excellent'])
    df['Performance_Label'] = le.transform(df['Performance_Category'])
    mapping = dict(zip(le.classes_, le.transform(le.classes_)))
    print(f"Target encoding: {mapping}")
    return df, le


def create_preprocessing_pipeline(num_features, cat_features):
    num_pipeline = Pipeline([('scaler', StandardScaler())])
    cat_pipeline = Pipeline([('onehot', OneHotEncoder(drop='first', sparse_output=False))])
    preprocessor = ColumnTransformer([
        ('numerical', num_pipeline, num_features),
        ('categorical', cat_pipeline, cat_features)
    ])
    print(f"Numerical: {len(num_features)}, Categorical: {len(cat_features)}")
    return preprocessor


def generate_eda_visualizations(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    colors = ['#ff6b6b', '#ffd93d', '#6bcb77', '#4d96ff']
    order = ['Poor', 'Average', 'Good', 'Excellent']

    # 1. Performance Distribution
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = df['Performance_Category'].value_counts().sort_index()
    ax.bar(counts.index, counts.values, color=colors, edgecolor='black', linewidth=1.5)
    for i, v in enumerate(counts.values):
        ax.text(i, v + 5, str(v), ha='center', fontweight='bold')
    ax.set_title('Performance Category Distribution', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of Students')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/performance_distribution.png', dpi=100)
    plt.close()

    # 2. Correlation Heatmap
    numeric_df = df.select_dtypes(include=[np.number])
    fig, ax = plt.subplots(figsize=(14, 10))
    corr = numeric_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=0.5, ax=ax)
    ax.set_title('Feature Correlation Heatmap', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/correlation_heatmap.png', dpi=100)
    plt.close()

    # 3-6. Box plots
    plot_configs = [
        ('Attendance_Percentage', 'Attendance Percentage', 'attendance_vs_performance'),
        ('Study_Hours_Per_Day', 'Study Hours Per Day', 'study_hours_vs_performance'),
        ('Number_of_Backlogs', 'Number of Backlogs', 'backlogs_vs_performance'),
        ('Previous_Semester_GPA', 'Previous Semester GPA', 'gpa_vs_performance')
    ]
    for col, ylabel, fname in plot_configs:
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.boxplot(x='Performance_Category', y=col, data=df, order=order, palette=colors, ax=ax)
        ax.set_title(f'{ylabel} vs Performance Category', fontsize=16, fontweight='bold')
        ax.set_xlabel('Performance Category')
        ax.set_ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f'{output_dir}/{fname}.png', dpi=100)
        plt.close()

    print(f"All EDA plots saved to: {output_dir}/")


def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_file = os.path.join(base_dir, 'dataset', 'raw', 'student_data_raw.csv')
    processed_file = os.path.join(base_dir, 'dataset', 'processed', 'student_data_cleaned.csv')
    preprocessor_file = os.path.join(base_dir, 'models', 'preprocessor.pkl')
    label_encoder_file = os.path.join(base_dir, 'models', 'label_encoder.pkl')
    reports_dir = os.path.join(base_dir, 'reports')

    os.makedirs(os.path.join(base_dir, 'dataset', 'processed'), exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'models'), exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("=" * 60)
    print("DATA PREPROCESSING & FEATURE ENGINEERING")
    print("=" * 60)

    df = load_data(raw_file)
    check_missing_values(df)
    check_duplicates(df)
    check_data_types(df)

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    df = handle_outliers(df, num_cols)
    df = feature_engineering(df)
    df, label_encoder = encode_target_variable(df)
    generate_eda_visualizations(df, reports_dir)

    numerical_features = [
        'Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks',
        'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score',
        'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours',
        'Class_Participation', 'Assignment_Submission_Rate',
        'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score',
        'Study_Efficiency'
    ]
    categorical_features = ['Internet_Access', 'Extracurricular_Activities']

    preprocessor = create_preprocessing_pipeline(numerical_features, categorical_features)
    X = df[numerical_features + categorical_features]
    preprocessor.fit(X)

    joblib.dump(preprocessor, preprocessor_file)
    joblib.dump(label_encoder, label_encoder_file)
    df.to_csv(processed_file, index=False)

    print(f"\nPreprocessor saved: {preprocessor_file}")
    print(f"Label encoder saved: {label_encoder_file}")
    print(f"Processed data saved: {processed_file}")

    print("\n" + "=" * 60)
    print("TARGET DISTRIBUTION:")
    dist = df['Performance_Category'].value_counts()
    for cat in ['Poor', 'Average', 'Good', 'Excellent']:
        print(f"  {cat:12s}: {dist[cat]}")
    print("=" * 60)
    print("STEP 4 & 5 COMPLETED!")
    print("=" * 60)

    return df, preprocessor, label_encoder


if __name__ == "__main__":
    main()
