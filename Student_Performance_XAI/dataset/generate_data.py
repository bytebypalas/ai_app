"""
=============================================================================
STEP 2: Generate Synthetic Student Academic Performance Dataset
=============================================================================
File: dataset/generate_data.py
Purpose: Creates a realistic synthetic dataset for student performance prediction.
Output: dataset/raw/student_data_raw.csv

Features Generated:
1. Attendance Percentage (0-100)
2. Study Hours Per Day (0-12)
3. Previous Academic Marks (0-100)
4. Internal Assessment Marks (0-100)
5. Assignment Score (0-100)
6. Practical/Lab Score (0-100)
7. Number of Backlogs (0-10)
8. Previous Semester GPA/CGPA (0-10)
9. Sleep Hours (4-10)
10. Internet Access (0 or 1)
11. Parental Education (0-4 categorical)
12. Extracurricular Activities (0 or 1)
13. Class Participation (0-100)
14. Assignment Submission Rate (0-100)

Target: Performance_Category (Poor, Average, Good, Excellent)

Generation Strategy:
- First assign each student a performance category
- Then generate features appropriate to that category
- This ensures realistic correlation between features and target
================================================================================
"""

import pandas as pd
import numpy as np
import os

# Set random seed for reproducibility
np.random.seed(42)

def generate_student_data(n_samples=1200):
    """
    Generate synthetic student academic performance dataset.
    
    Parameters:
    -----------
    n_samples : int, default=1200
        Number of student records to generate (should be multiple of 4)
    
    Returns:
    --------
    pd.DataFrame: Generated dataset
    """
    
    # Ensure equal number per category (roughly)
    n_per_category = n_samples // 4
    remainder = n_samples - (n_per_category * 4)
    
    # Create category labels with balanced distribution
    categories = (['Poor'] * n_per_category + 
                  ['Average'] * n_per_category + 
                  ['Good'] * n_per_category + 
                  ['Excellent'] * (n_per_category + remainder))
    
    np.random.shuffle(categories)
    n = len(categories)
    
    # Initialize arrays
    attendance = np.zeros(n)
    study_hours = np.zeros(n)
    prev_marks = np.zeros(n)
    internal_marks = np.zeros(n)
    assignment_score = np.zeros(n)
    lab_score = np.zeros(n)
    backlogs = np.zeros(n)
    gpa = np.zeros(n)
    sleep_hours = np.zeros(n)
    internet = np.zeros(n)
    parent_edu = np.zeros(n)
    extracurricular = np.zeros(n)
    participation = np.zeros(n)
    submission_rate = np.zeros(n)
    
    # Define feature parameters for each category
    # Format: (mean_low, mean_high, std) for most features
    category_params = {
        'Poor': {
            'attendance': (40, 55, 8),
            'study_hours': (1, 3, 1),
            'prev_marks': (35, 50, 8),
            'internal_marks': (30, 48, 8),
            'assignment': (30, 50, 8),
            'lab_score': (30, 48, 8),
            'backlogs': (3, 7, 2),
            'gpa': (4.0, 5.5, 0.8),
            'participation': (25, 45, 8),
            'submission_rate': (50, 65, 8)
        },
        'Average': {
            'attendance': (55, 72, 8),
            'study_hours': (3, 6, 1.5),
            'prev_marks': (50, 68, 8),
            'internal_marks': (48, 68, 8),
            'assignment': (50, 70, 8),
            'lab_score': (48, 68, 8),
            'backlogs': (1, 3, 1.5),
            'gpa': (5.5, 7.0, 0.8),
            'participation': (45, 65, 8),
            'submission_rate': (65, 80, 8)
        },
        'Good': {
            'attendance': (72, 88, 7),
            'study_hours': (6, 9, 1.5),
            'prev_marks': (68, 85, 7),
            'internal_marks': (68, 85, 7),
            'assignment': (70, 88, 7),
            'lab_score': (68, 85, 7),
            'backlogs': (0, 1.5, 1),
            'gpa': (7.0, 8.5, 0.7),
            'participation': (65, 85, 7),
            'submission_rate': (80, 92, 7)
        },
        'Excellent': {
            'attendance': (88, 100, 5),
            'study_hours': (8, 12, 1.5),
            'prev_marks': (85, 100, 5),
            'internal_marks': (85, 100, 5),
            'assignment': (88, 100, 5),
            'lab_score': (85, 100, 5),
            'backlogs': (0, 0.5, 0.5),
            'gpa': (8.5, 10.0, 0.5),
            'participation': (85, 100, 5),
            'submission_rate': (92, 100, 4)
        }
    }
    
    # Generate features for each student based on their category
    for i, cat in enumerate(categories):
        params = category_params[cat]
        
        # Core academic features (using normal distribution clipped to valid range)
        lo, hi, std = params['attendance']
        attendance[i] = np.clip(np.random.normal((lo+hi)/2, std), 30, 100)
        
        lo, hi, std = params['study_hours']
        study_hours[i] = np.clip(np.random.normal((lo+hi)/2, std), 0.5, 12)
        
        lo, hi, std = params['prev_marks']
        prev_marks[i] = np.clip(np.random.normal((lo+hi)/2, std), 20, 100)
        
        lo, hi, std = params['internal_marks']
        internal_marks[i] = np.clip(np.random.normal((lo+hi)/2, std), 15, 100)
        
        lo, hi, std = params['assignment']
        assignment_score[i] = np.clip(np.random.normal((lo+hi)/2, std), 20, 100)
        
        lo, hi, std = params['lab_score']
        lab_score[i] = np.clip(np.random.normal((lo+hi)/2, std), 15, 100)
        
        lo, hi, std = params['backlogs']
        backlogs[i] = np.clip(np.random.poisson((lo+hi)/2), 0, 10)
        
        lo, hi, std = params['gpa']
        gpa[i] = np.clip(np.random.normal((lo+hi)/2, std), 3.0, 10.0)
        
        lo, hi, std = params['participation']
        participation[i] = np.clip(np.random.normal((lo+hi)/2, std), 10, 100)
        
        lo, hi, std = params['submission_rate']
        submission_rate[i] = np.clip(np.random.normal((lo+hi)/2, std), 30, 100)
        
        # Behavioral features (same distribution for all categories)
        sleep_hours[i] = np.clip(np.random.normal(7, 1.5), 4, 10)
        internet[i] = np.random.choice([0, 1], p=[0.15, 0.85])
        parent_edu[i] = np.random.choice([0, 1, 2, 3, 4], p=[0.10, 0.20, 0.35, 0.25, 0.10])
        extracurricular[i] = np.random.choice([0, 1], p=[0.40, 0.60])
    
    # Create DataFrame
    df = pd.DataFrame({
        'Attendance_Percentage': attendance.round(2),
        'Study_Hours_Per_Day': study_hours.round(2),
        'Previous_Academic_Marks': prev_marks.round(2),
        'Internal_Assessment_Marks': internal_marks.round(2),
        'Assignment_Score': assignment_score.round(2),
        'Practical_Lab_Score': lab_score.round(2),
        'Number_of_Backlogs': backlogs.astype(int),
        'Previous_Semester_GPA': gpa.round(2),
        'Sleep_Hours': sleep_hours.round(1),
        'Internet_Access': internet.astype(int),
        'Parental_Education': parent_edu.astype(int),
        'Extracurricular_Activities': extracurricular.astype(int),
        'Class_Participation': participation.round(2),
        'Assignment_Submission_Rate': submission_rate.round(2),
        'Performance_Category': categories
    })
    
    return df


def main():
    """Main function to generate and save the dataset."""
    
    print("=" * 60)
    print("STEP 2: Generating Synthetic Student Performance Dataset")
    print("=" * 60)
    
    # Generate 1200 student records (300 per category)
    df = generate_student_data(n_samples=1200)
    
    # Define output path
    output_dir = os.path.join(os.path.dirname(__file__), 'raw')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'student_data_raw.csv')
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    
    # Display dataset information
    print(f"\n✅ Dataset saved to: {output_file}")
    print(f"\n📊 Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    print("\n" + "=" * 60)
    print("PERFORMANCE CATEGORY DISTRIBUTION")
    print("=" * 60)
    dist = df['Performance_Category'].value_counts()
    pct = df['Performance_Category'].value_counts(normalize=True).mul(100).round(2)
    for cat in ['Poor', 'Average', 'Good', 'Excellent']:
        if cat in dist:
            print(f"  {cat:12s}: {dist[cat]:4d} students ({pct[cat]:.1f}%)")
    
    print("\n" + "=" * 60)
    print("FEATURE STATISTICS BY CATEGORY")
    print("=" * 60)
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    print(df.groupby('Performance_Category')[numeric_cols].mean().round(2))
    
    print("\n" + "=" * 60)
    print("FIRST 5 SAMPLE RECORDS")
    print("=" * 60)
    print(df.head())
    
    print("\n" + "=" * 60)
    print("DATASET INFO")
    print("=" * 60)
    print(df.info())


if __name__ == "__main__":
    main()

