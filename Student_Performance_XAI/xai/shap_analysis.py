"""
=============================================================================
STEP 10: SHAP-based Explainable AI Analysis
=============================================================================
File: xai/shap_analysis.py
Purpose:
  - Load trained model and preprocessor
  - Compute SHAP values for global and local explanations
  - Generate SHAP summary plots
  - Provide functions for individual prediction explanations

Input:  models/student_performance_model.pkl
        models/preprocessor.pkl
        models/label_encoder.pkl
Output: shap analysis functions used by Streamlit app
=============================================================================
"""

import pandas as pd
import numpy as np
import shap
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


def load_artifacts(models_dir='../models'):
    """Load all trained artifacts."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    models_dir = os.path.join(base_dir, 'models')

    model = joblib.load(os.path.join(models_dir, 'student_performance_model.pkl'))
    preprocessor = joblib.load(os.path.join(models_dir, 'preprocessor.pkl'))
    label_encoder = joblib.load(os.path.join(models_dir, 'label_encoder.pkl'))

    return model, preprocessor, label_encoder


def prepare_input_features(student_input, preprocessor):
    """
    Convert student input dictionary to processed feature array.
    
    Parameters:
    -----------
    student_input : dict
        Dictionary containing student feature values
    preprocessor : sklearn ColumnTransformer
        Fitted preprocessing pipeline
    
    Returns:
    --------
    numpy array: Processed features ready for prediction
    """
    # Define feature columns in the exact order expected by preprocessor
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

    return X_processed, df


def get_shap_explainer(model, X_background):
    """
    Create SHAP explainer for the trained model.
    
    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    X_background : numpy array
        Background data for SHAP (typically training data subset)
    
    Returns:
    --------
    SHAP Explainer object
    """
    # For Tree-based models (Random Forest, Decision Tree), use TreeExplainer
    if hasattr(model, 'feature_importances_'):
        explainer = shap.TreeExplainer(model)
    else:
        # For other models, use KernelExplainer with a background subset
        explainer = shap.KernelExplainer(model.predict_proba, X_background)

    return explainer


def explain_prediction(model, preprocessor, label_encoder, student_input):
    """
    Explain a single student's prediction using SHAP.
    
    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    preprocessor : sklearn ColumnTransformer
        Fitted preprocessing pipeline
    label_encoder : sklearn LabelEncoder
        Fitted label encoder for target
    student_input : dict
        Dictionary containing student feature values
    
    Returns:
    --------
    dict: Contains prediction, probabilities, and SHAP explanation
    """
    # Prepare input
    X_processed, df_original = prepare_input_features(student_input, preprocessor)

    # Make prediction
    prediction_encoded = model.predict(X_processed)[0]
    prediction_class = label_encoder.inverse_transform([prediction_encoded])[0]

    # Get probabilities
    probabilities = model.predict_proba(X_processed)[0]
    confidence = float(np.max(probabilities))

    # Create probability dict
    prob_dict = {}
    for i, cls in enumerate(label_encoder.classes_):
        prob_dict[cls] = round(float(probabilities[i]) * 100, 2)

    # SHAP Explanation
    # For Random Forest, use TreeExplainer
    if hasattr(model, 'feature_importances_'):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_processed)

        # Get feature names after preprocessing
        numerical_features = [
            'Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks',
            'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score',
            'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours',
            'Class_Participation', 'Assignment_Submission_Rate',
            'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score',
            'Study_Efficiency'
        ]
        categorical_features = ['Internet_Access', 'Extracurricular_Activities']

        all_features = numerical_features + categorical_features
        # After one-hot encoding, we have different feature names
        # Use the original feature names for display
        display_features = numerical_features + ['Internet_Access_Yes', 'Extracurricular_Yes']

        # Get SHAP values for the predicted class
        pred_class_idx = list(label_encoder.classes_).index(prediction_class)
        
        # shap_values shape: (n_samples, n_features, n_classes)
        # For single sample: shap_values[0, :, pred_class_idx]
        if len(shap_values.shape) == 3:
            shap_values_for_sample = shap_values[0, :, pred_class_idx]
        elif isinstance(shap_values, list):
            shap_values_for_sample = shap_values[pred_class_idx][0]
        else:
            shap_values_for_sample = shap_values[0]

        # Handle one-hot encoded features - simplify for display
        # Map SHAP values back to original features
        feature_contributions = {}
        for i, feat in enumerate(display_features):
            if i < len(shap_values_for_sample):
                feature_contributions[feat] = round(float(shap_values_for_sample[i]), 4)

        # Sort by absolute contribution
        sorted_contributions = dict(
            sorted(feature_contributions.items(),
                   key=lambda x: abs(x[1]), reverse=True)
        )

        # Separate positive and negative contributors
        positive_factors = {}
        negative_factors = {}
        for feat, val in sorted_contributions.items():
            if val > 0:
                positive_factors[feat] = val
            else:
                negative_factors[feat] = val

        result = {
            'prediction': prediction_class,
            'confidence': confidence,
            'probabilities': prob_dict,
            'shap_values': shap_values_for_sample.tolist() if hasattr(shap_values_for_sample, 'tolist') else shap_values_for_sample,
            'feature_names': display_features,
            'positive_factors': positive_factors,
            'negative_factors': negative_factors,
            'all_contributions': sorted_contributions,
            'base_value': float(explainer.expected_value[pred_class_idx]) if hasattr(explainer.expected_value, '__len__') else float(explainer.expected_value)
        }

        return result
    else:
        # For non-tree models
        return {
            'prediction': prediction_class,
            'confidence': confidence,
            'probabilities': prob_dict,
            'note': 'SHAP explanation requires tree-based model'
        }


def get_global_feature_importance(model, preprocessor, X_train_sample):
    """
    Get global feature importance using SHAP.
    
    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    preprocessor : sklearn ColumnTransformer
        Fitted preprocessing pipeline
    X_train_sample : numpy array
        Sample of training data for SHAP computation
    
    Returns:
    --------
    dict: Global feature importance values
    """
    if hasattr(model, 'feature_importances_'):
        # Use model's built-in feature importance
        importances = model.feature_importances_
        numerical_features = [
            'Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks',
            'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score',
            'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours',
            'Class_Participation', 'Assignment_Submission_Rate',
            'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score',
            'Study_Efficiency'
        ]
        categorical_features = ['Internet_Access', 'Extracurricular_Activities']
        all_features = numerical_features + categorical_features

        # Use SHAP for more accurate global importance
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_train_sample[:100])

        # Average absolute SHAP values across all samples for global importance
        avg_shap = np.mean(np.abs(shap_values), axis=(0, 1))

        importance_dict = {}
        for i, feat in enumerate(all_features):
            if i < len(avg_shap):
                importance_dict[feat] = round(float(avg_shap[i]), 4)

        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    else:
        return {}


def create_human_readable_explanation(explanation_result):
    """
    Create a human-readable explanation from SHAP results.
    
    Parameters:
    -----------
    explanation_result : dict
        Result from explain_prediction function
    
    Returns:
    --------
    str: Human-readable explanation
    """
    prediction = explanation_result['prediction']
    confidence = explanation_result['confidence']
    positive = explanation_result.get('positive_factors', {})
    negative = explanation_result.get('negative_factors', {})

    lines = []
    lines.append(f"🎯 Prediction: **{prediction}**")
    lines.append(f"📊 Confidence: **{confidence*100:.1f}%**")
    lines.append("")

    if positive:
        lines.append("✅ **Positive Factors (helped improve prediction):**")
        for feat, val in list(positive.items())[:5]:
            # Clean up feature names for readability
            clean_name = feat.replace('_', ' ').title()
            lines.append(f"   • {clean_name}: +{abs(val):.4f}")

    if negative:
        lines.append("")
        lines.append("⚠️ **Negative Factors (pulled prediction down):**")
        for feat, val in list(negative.items())[:5]:
            clean_name = feat.replace('_', ' ').title()
            lines.append(f"   • {clean_name}: -{abs(val):.4f}")

    lines.append("")
    lines.append("---")
    lines.append("💡 *SHAP values show feature influence on the model's prediction.")
    lines.append("   Higher absolute values = stronger influence.")
    lines.append("   This shows model behavior, not real-world causation.*")

    return "\n".join(lines)

