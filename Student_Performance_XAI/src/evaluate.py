"""
=============================================================================
STEP 3: Model Evaluation Metrics & Cross-Validation
=============================================================================
File: src/evaluate.py
Purpose:
  - Comprehensive model evaluation
  - Cross-validation scores
  - ROC-AUC analysis
  - Error analysis
  - Generate evaluation report

Usage:
  from src.evaluate import evaluate_model, generate_evaluation_report
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import sys
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score,
    matthews_corrcoef, cohen_kappa_score
)


def load_data_and_artifacts():
    """
    Load processed data and model artifacts for evaluation.

    Returns:
    --------
    tuple: (X_processed, y, model, preprocessor, label_encoder, feature_names)
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))

    # Load processed data
    data_path = os.path.join(base_dir, 'dataset', 'processed',
                             'student_data_cleaned.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(
            f"Processed data not found at {data_path}.\n"
            "Run data_preprocessing.py first."
        )

    df = pd.read_csv(data_path)

    # Load artifacts
    models_dir = os.path.join(base_dir, 'models')
    model_path = os.path.join(models_dir, 'student_performance_model.pkl')
    preprocessor_path = os.path.join(models_dir, 'preprocessor.pkl')
    encoder_path = os.path.join(models_dir, 'label_encoder.pkl')

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}.\n"
            "Run train_model.py first."
        )

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)
    label_encoder = joblib.load(encoder_path)

    # Prepare features
    numerical_features = [
        'Attendance_Percentage', 'Study_Hours_Per_Day', 'Previous_Academic_Marks',
        'Internal_Assessment_Marks', 'Assignment_Score', 'Practical_Lab_Score',
        'Number_of_Backlogs', 'Previous_Semester_GPA', 'Sleep_Hours',
        'Class_Participation', 'Assignment_Submission_Rate',
        'Academic_Consistency', 'Overall_Academic_Score', 'Engagement_Score',
        'Study_Efficiency'
    ]
    categorical_features = ['Internet_Access', 'Extracurricular_Activities']

    feature_cols = numerical_features + categorical_features
    y = df['Performance_Label']

    # Get feature names after transformation
    num_features = numerical_features
    cat_encoder = preprocessor.named_transformers_['categorical']
    if hasattr(cat_encoder, 'named_steps'):
        cat_features = cat_encoder.named_steps['onehot'].get_feature_names_out(categorical_features)
    else:
        cat_features = categorical_features
    all_features = list(num_features) + list(cat_features)

    X_processed = preprocessor.transform(df[feature_cols])

    print(f"Data loaded: {X_processed.shape[0]} samples, {X_processed.shape[1]} features")
    print(f"Target classes: {label_encoder.classes_}")

    return X_processed, y, model, preprocessor, label_encoder, all_features


def evaluate_model(model, X_test, y_test, class_names):
    """
    Comprehensive model evaluation with multiple metrics.

    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    X_test : numpy array
        Test features
    y_test : numpy array
        True labels
    class_names : list
        Names of target classes

    Returns:
    --------
    dict: Dictionary of all evaluation metrics
    """
    # Predictions
    y_pred = model.predict(X_test)
    y_proba = None
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_test)

    # Basic metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    # Advanced metrics
    mcc = matthews_corrcoef(y_test, y_pred)
    kappa = cohen_kappa_score(y_test, y_pred)

    # Per-class metrics
    class_report = classification_report(y_test, y_pred, target_names=class_names)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    # ROC-AUC (one-vs-rest for multi-class)
    roc_auc = None
    if y_proba is not None and len(class_names) > 2:
        try:
            roc_auc = roc_auc_score(y_test, y_proba, multi_class='ovr')
        except Exception:
            roc_auc = None

    # Per-class precision, recall, f1
    per_class_precision = precision_score(y_test, y_pred, average=None)
    per_class_recall = recall_score(y_test, y_pred, average=None)
    per_class_f1 = f1_score(y_test, y_pred, average=None)

    results = {
        'accuracy': round(accuracy, 4),
        'precision_weighted': round(precision, 4),
        'recall_weighted': round(recall, 4),
        'f1_weighted': round(f1, 4),
        'matthews_corrcoef': round(mcc, 4),
        'cohen_kappa': round(kappa, 4),
        'roc_auc': round(roc_auc, 4) if roc_auc is not None else 'N/A',
        'classification_report': class_report,
        'confusion_matrix': cm,
        'per_class': {
            class_names[i]: {
                'precision': round(per_class_precision[i], 4),
                'recall': round(per_class_recall[i], 4),
                'f1_score': round(per_class_f1[i], 4)
            }
            for i in range(len(class_names))
        }
    }

    return results


def cross_validate(model, X, y, cv=5):
    """
    Perform stratified k-fold cross-validation.

    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    X : numpy array
        Feature matrix
    y : numpy array
        Target labels
    cv : int, default=5
        Number of cross-validation folds

    Returns:
    --------
    dict: Cross-validation results
    """
    skf = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)

    cv_accuracy = cross_val_score(model, X, y, cv=skf, scoring='accuracy')
    cv_f1 = cross_val_score(model, X, y, cv=skf, scoring='f1_weighted')
    cv_precision = cross_val_score(model, X, y, cv=skf, scoring='precision_weighted')
    cv_recall = cross_val_score(model, X, y, cv=skf, scoring='recall_weighted')

    results = {
        'cv_accuracy_mean': round(cv_accuracy.mean(), 4),
        'cv_accuracy_std': round(cv_accuracy.std(), 4),
        'cv_f1_mean': round(cv_f1.mean(), 4),
        'cv_f1_std': round(cv_f1.std(), 4),
        'cv_precision_mean': round(cv_precision.mean(), 4),
        'cv_precision_std': round(cv_precision.std(), 4),
        'cv_recall_mean': round(cv_recall.mean(), 4),
        'cv_recall_std': round(cv_recall.std(), 4),
        'cv_scores': {
            'accuracy': [round(s, 4) for s in cv_accuracy],
            'f1': [round(s, 4) for s in cv_f1],
            'precision': [round(s, 4) for s in cv_precision],
            'recall': [round(s, 4) for s in cv_recall]
        }
    }

    return results


def analyze_errors(model, X_test, y_test, label_encoder, feature_names=None):
    """
    Analyze prediction errors in detail.

    Parameters:
    -----------
    model : sklearn model
        Trained classifier
    X_test : numpy array
        Test features
    y_test : numpy array
        True labels
    label_encoder : sklearn LabelEncoder
        Fitted label encoder
    feature_names : list, optional
        Names of features

    Returns:
    --------
    dict: Error analysis results
    """
    y_pred = model.predict(X_test)
    misclassified = np.where(y_pred != y_test)[0]

    error_analysis = {
        'total_misclassified': len(misclassified),
        'misclassification_rate': round(len(misclassified) / len(y_test) * 100, 2),
        'misclassified_indices': misclassified.tolist()[:20]  # First 20 only
    }

    # Error distribution per class
    class_names = label_encoder.classes_
    error_dist = {}
    for true_class in range(len(class_names)):
        for pred_class in range(len(class_names)):
            if true_class != pred_class:
                key = f"{class_names[true_class]}->{class_names[pred_class]}"
                count = np.sum((y_test == true_class) & (y_pred == pred_class))
                if count > 0:
                    error_dist[key] = int(count)

    error_analysis['error_distribution'] = error_dist

    return error_analysis


def generate_evaluation_report():
    """
    Generate complete evaluation report for the model.

    Returns:
    --------
    dict: Complete evaluation report
    """
    print("=" * 60)
    print("MODEL EVALUATION REPORT")
    print("=" * 60)

    try:
        # Load data and artifacts
        X, y, model, preprocessor, label_encoder, feature_names = load_data_and_artifacts()

        class_names = label_encoder.classes_

        # Split data for evaluation
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTrain set: {X_train.shape[0]} samples")
        print(f"Test set:  {X_test.shape[0]} samples")

        # 1. Model evaluation on test set
        print("\n" + "-" * 40)
        print("1. MODEL EVALUATION ON TEST SET")
        print("-" * 40)
        eval_results = evaluate_model(model, X_test, y_test, class_names)

        print(f"Accuracy:  {eval_results['accuracy']}")
        print(f"Precision: {eval_results['precision_weighted']}")
        print(f"Recall:    {eval_results['recall_weighted']}")
        print(f"F1-Score:  {eval_results['f1_weighted']}")
        print(f"MCC:       {eval_results['matthews_corrcoef']}")
        print(f"Kappa:     {eval_results['cohen_kappa']}")
        print(f"ROC-AUC:   {eval_results['roc_auc']}")

        print("\nPer-Class Performance:")
        for cls in class_names:
            p = eval_results['per_class'][cls]
            print(f"  {cls:12s}: Precision={p['precision']}, Recall={p['recall']}, F1={p['f1_score']}")

        # 2. Cross-validation
        print("\n" + "-" * 40)
        print("2. CROSS-VALIDATION RESULTS")
        print("-" * 40)
        cv_results = cross_validate(model, X, y, cv=5)

        print(f"CV Accuracy:  {cv_results['cv_accuracy_mean']} +/- {cv_results['cv_accuracy_std']}")
        print(f"CV F1-Score:  {cv_results['cv_f1_mean']} +/- {cv_results['cv_f1_std']}")
        print(f"CV Precision: {cv_results['cv_precision_mean']} +/- {cv_results['cv_precision_std']}")
        print(f"CV Recall:    {cv_results['cv_recall_mean']} +/- {cv_results['cv_recall_std']}")

        # 3. Error analysis
        print("\n" + "-" * 40)
        print("3. ERROR ANALYSIS")
        print("-" * 40)
        error_analysis = analyze_errors(model, X_test, y_test, label_encoder, feature_names)

        print(f"Total misclassified: {error_analysis['total_misclassified']}")
        print(f"Misclassification rate: {error_analysis['misclassification_rate']}%")
        print("\nError Distribution:")
        for key, count in sorted(error_analysis.get('error_distribution', {}).items(),
                                 key=lambda x: x[1], reverse=True):
            print(f"  {key}: {count}")

        # Combine all results
        report = {
            'model_type': type(model).__name__,
            'evaluation': eval_results,
            'cross_validation': cv_results,
            'error_analysis': error_analysis
        }

        print("\n" + "=" * 60)
        print("EVALUATION COMPLETE")
        print("=" * 60)

        return report

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run evaluation report generation."""
    report = generate_evaluation_report()
    if report:
        print("\n✓ Evaluation report generated successfully!")
    else:
        print("\n✗ Evaluation failed.")


if __name__ == "__main__":
    main()

