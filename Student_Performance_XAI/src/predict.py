"""
=============================================================================
STEP 2: Single Student Prediction with Grade, Risk, Confidence
=============================================================================
File: src/predict.py
Purpose:
  - Load trained model and artifacts
  - Make predictions on single student input
  - Calculate grade, risk level, confidence score
  - Determine pass/fail status

Usage:
  from src.predict import predict_student, get_grade, get_risk_level
=============================================================================
"""

import pandas as pd
import numpy as np
import joblib
import os
import sys
import warnings
warnings.filterwarnings('ignore')


def load_model_artifacts(models_dir=None):
    """
    Load trained model, preprocessor, and label encoder.

    Parameters:
    -----------
    models_dir : str, optional
        Path to models directory. If None, uses default path.

    Returns:
    --------
    tuple: (model, preprocessor, label_encoder)
    """
    if models_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        models_dir = os.path.join(base_dir, 'models')

    model_path = os.path.join(models_dir, 'student_performance_model.pkl')
    preprocessor_path = os.path.join(models_dir, 'preprocessor.pkl')
    encoder_path = os.path.join(models_dir, 'label_encoder.pkl')

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Please run train_model.py first."
        )

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    label_encoder = joblib.load(encoder_path)

    return model, preprocessor, label_encoder


def get_grade(percentage):
    """
    Determine letter grade based on percentage.

    Parameters:
    -----------
    percentage : float
        Predicted percentage (0-100)

    Returns:
    --------
    str: Letter grade (A+, A, B+, B, C, F)
    """
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B+'
    elif percentage >= 60:
        return 'B'
    elif percentage >= 50:
        return 'C'
    else:
        return 'F'


def get_risk_level(percentage):
    """
    Determine risk level based on predicted percentage.

    Parameters:
    -----------
    percentage : float
        Predicted percentage (0-100)

    Returns:
    --------
    str: Risk level (Low Risk, Medium Risk, High Risk)
    """
    if percentage >= 80:
        return 'Low Risk'
    elif percentage >= 60:
        return 'Medium Risk'
    else:
        return 'High Risk'


def get_performance_level(category):
    """
    Map model category to performance level.

    Parameters:
    -----------
    category : str
        Model prediction category

    Returns:
    --------
    str: Performance level
    """
    mapping = {
        'Excellent': 'Excellent',
        'Good': 'Good',
        'Average': 'Above Average',
        'Poor': 'Poor'
    }
    return mapping.get(category, 'Average')


def estimate_confidence(probabilities, category):
    """
    Estimate confidence score based on prediction probabilities.

    Parameters:
    -----------
    probabilities : dict
        Probability distribution across categories
    category : str
        Predicted category

    Returns:
    --------
    float: Confidence percentage (0-100)
    """
    # Base confidence from highest probability
    max_prob = max(probabilities.values())

    # Adjust confidence based on probability spread
    sorted_probs = sorted(probabilities.values(), reverse=True)
    if len(sorted_probs) > 1:
        margin = sorted_probs[0] - sorted_probs[1]
        # Higher margin = higher confidence
        margin_bonus = min(margin * 50, 15)  # Max 15% bonus
    else:
        margin_bonus = 0

    confidence = max_prob * 100 + margin_bonus

    # Cap between 60 and 99
    return round(min(max(confidence, 60), 99), 2)


def predict_student(student_input, model=None, preprocessor=None,
                    label_encoder=None, feature_names=None):
    """
    Predict performance for a single student.

    Parameters:
    -----------
    student_input : dict
        Dictionary of student feature values
    model : object, optional
        Trained model. If None, loads from default path.
    preprocessor : object, optional
        Fitted preprocessor. If None, loads from default path.
    label_encoder : object, optional
        Fitted label encoder. If None, loads from default path.
    feature_names : list, optional
        List of feature names in order expected by preprocessor

    Returns:
    --------
    dict: Complete prediction result with grade, risk, confidence
    """
    # Load artifacts if not provided
    if model is None or preprocessor is None or label_encoder is None:
        model, preprocessor, label_encoder = load_model_artifacts()

    # Define feature columns expected by the model
    numerical_features = [
        'Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks',
        'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score',
        'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours',
        'Class_Participation', 'Assignment_Submission_Rate',
        'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score',
        'Study_Efficiency'
    ]
    categorical_features = ['Internet_Access', 'Extracurricular_Activities']

    # Create DataFrame from input
    df = pd.DataFrame([student_input])

    # Compute engineered features
    df['Academic_Consistency'] = df[[
        'Previous_Academic_Marks', 'Internal_Assessment_Marks',
        'Assignment_Score', 'Practical_Lab_Score'
    ]].std(axis=1).round(2)

    df['Overall_Academic_Score'] = (
        df['Previous_Academic_Marks'] * 0.25 +
        df['Internal_Assessment_Marks'] * 0.25 +
        df['Assignment_Score'] * 0.20 +
        df['Practical_Lab_Score'] * 0.20 +
        (df['Previous_Semester_GPA'] / 10 * 100) * 0.10
    ).round(2)

    df['Engagement_Score'] = (
        df['Class_Participation'] * 0.5 +
        df['Assignment_Submission_Rate'] * 0.5
    ).round(2)

    df['Study_Efficiency'] = df.apply(
        lambda r: round(r['Study_Hours_Per_Day'] / (r['Number_of_Backlogs'] + 1), 2),
        axis=1
    )

    # Select features in correct order
    feature_cols = numerical_features + categorical_features
    X = df[feature_cols]

    # Transform using preprocessor
    X_processed = preprocessor.transform(X)

    # Make prediction
    prediction_encoded = model.predict(X_processed)[0]
    prediction_category = label_encoder.inverse_transform([prediction_encoded])[0]

    # Get prediction probabilities
    probabilities = model.predict_proba(X_processed)[0]

    # Create probability dict
    prob_dict = {}
    for i, cls in enumerate(label_encoder.classes_):
        prob_dict[cls] = round(float(probabilities[i]) * 100, 2)

    # Map category to performance metrics
    category_score_map = {
        'Excellent': 92,
        'Good': 78,
        'Average': 65,
        'Poor': 45
    }

    # Estimate percentage based on category with some variation
    base_percentage = category_score_map.get(prediction_category, 65)
    # Add small variation based on input quality features
    quality_factor = (
        student_input.get('Attendance_Percentage', 75) / 100 +
        student_input.get('Study_Hours_Per_Day', 4) / 12 +
        student_input.get('Previous_Academic_Marks', 65) / 100
    ) / 3
    variation = (quality_factor - 0.65) * 15  # -10 to +10 variation
    predicted_percentage = round(min(max(base_percentage + variation, 0), 100), 2)

    # Calculate grade
    grade = get_grade(predicted_percentage)

    # Determine pass/fail
    passed = predicted_percentage >= 50

    # Get risk level
    risk_level = get_risk_level(predicted_percentage)

    # Get performance level
    performance_level = get_performance_level(prediction_category)

    # Estimate confidence
    confidence = estimate_confidence(prob_dict, prediction_category)

    # Prepare result
    result = {
        'predicted_percentage': predicted_percentage,
        'grade': grade,
        'performance_level': performance_level,
        'confidence': confidence,
        'risk_level': risk_level,
        'passed': passed,
        'status': 'Pass' if passed else 'Fail',
        'prediction_category': prediction_category,
        'probabilities': prob_dict
    }

    return result


def prepare_student_input(
    attendance=75, study_hours=4, prev_marks=65, internal_marks=60,
    assignment_score=70, lab_score=65, backlogs=2, gpa=6.5,
    sleep_hours=7, internet_access=1, participation=55,
    submission_rate=75, extracurricular=0
):
    """
    Prepare student input dictionary from individual parameters.

    Parameters:
    -----------
    Various student feature parameters with sensible defaults.

    Returns:
    --------
    dict: Student input dictionary
    """
    return {
        'Attendance_Percentage': attendance,
        'Study_Hours_Per_Day': study_hours,
        'Previous_Academic_Marks': prev_marks,
        'Internal_Assessment_Marks': internal_marks,
        'Assignment_Score': assignment_score,
        'Practical_Lab_Score': lab_score,
        'Number_of_Backlogs': backlogs,
        'Previous_Semester_GPA': gpa,
        'Sleep_Hours': sleep_hours,
        'Internet_Access': internet_access,
        'Parental_Education': 2,
        'Extracurricular_Activities': extracurricular,
        'Class_Participation': participation,
        'Assignment_Submission_Rate': submission_rate
    }


def main():
    """Test the prediction function."""
    print("=" * 60)
    print("TESTING PREDICTION MODULE")
    print("=" * 60)

    try:
        # Load model artifacts
        print("\nLoading model artifacts...")
        model, preprocessor, label_encoder = load_model_artifacts()
        print("✓ Model artifacts loaded successfully")

        # Test with default student
        print("\nMaking prediction for default student...")
        student = prepare_student_input(
            attendance=85, study_hours=6, prev_marks=78, internal_marks=75,
            assignment_score=80, lab_score=72, backlogs=1, gpa=7.5,
            sleep_hours=7.5, participation=70, submission_rate=85,
            extracurricular=1
        )

        result = predict_student(student, model, preprocessor, label_encoder)

        print("\n" + "=" * 60)
        print("PREDICTION RESULT")
        print("=" * 60)
        for key, value in result.items():
            if key == 'probabilities':
                print(f"\n{key.replace('_', ' ').title()}:")
                for cat, prob in value.items():
                    print(f"  {cat}: {prob}%")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")

        print("\n✓ Prediction module working correctly!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTip: Run the following commands first:")
        print("  1. cd Student_Performance_XAI")
        print("  2. python dataset/generate_data.py")
        print("  3. python src/data_preprocessing.py")
        print("  4. python src/train_model.py")


if __name__ == "__main__":
    main()

