"""
=============================================================================
STEP 5: Global & Local Feature Importance Analysis
=============================================================================
File: xai/feature_importance.py
Purpose:
  - Compute and display global feature importance
  - Compute and display local (per-instance) feature importance
  - Generate importance visualizations
  - Compare feature importance across models

Usage:
  from xai.feature_importance import (
      get_feature_importance_df,
      get_top_features,
      compare_feature_importance
  )
=============================================================================
"""

import pandas as pd
import numpy as np
import os
import sys
import joblib
import warnings
warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import seaborn as sns


def load_model_for_importance(models_dir=None):
    """
    Load model and data for feature importance analysis.

    Parameters:
    -----------
    models_dir : str, optional
        Path to models directory

    Returns:
    --------
    tuple: (model, feature_names, X_sample)
    """
    if models_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        models_dir = os.path.join(base_dir, 'models')

    # Load model
    model_path = os.path.join(models_dir, 'student_performance_model.pkl')
    preprocessor_path = os.path.join(models_dir, 'preprocessor.pkl')

    model = joblib.load(model_path)
    preprocessor = joblib.load(preprocessor_path)

    # Load sample data for SHAP
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'dataset', 'processed', 'student_data_cleaned.csv')
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        raise FileNotFoundError(f"Processed data not found at {data_path}")

    # Feature definitions
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

    # Get feature names after preprocessing
    num_features = numerical_features
    cat_encoder = preprocessor.named_transformers_['categorical']
    cat_features = cat_encoder.named_steps['onehot'].get_feature_names_out(categorical_features)
    all_features = list(num_features) + list(cat_features)

    # Transform sample data
    X_sample = preprocessor.transform(df[feature_cols][:200])

    return model, all_features, X_sample


def get_model_feature_importance(model):
    """
    Extract feature importance from model (if available).

    Parameters:
    -----------
    model : sklearn model
        Trained model

    Returns:
    --------
    numpy array: Feature importance values, or None if not available
    """
    if hasattr(model, 'feature_importances_'):
        return model.feature_importances_
    elif hasattr(model, 'coef_'):
        coef = model.coef_
        if len(coef.shape) > 1:
            return np.mean(np.abs(coef), axis=0)
        return np.abs(coef)
    return None


def get_feature_importance_df(model, feature_names):
    """
    Get feature importance as a DataFrame.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    feature_names : list
        Names of features

    Returns:
    --------
    pd.DataFrame: Feature importance sorted by importance
    """
    importances = get_model_feature_importance(model)

    if importances is None:
        return pd.DataFrame({'Feature': feature_names, 'Importance': 0})

    # Ensure lengths match
    min_len = min(len(importances), len(feature_names))
    importances = importances[:min_len]
    features = feature_names[:min_len]

    df = pd.DataFrame({
        'Feature': features,
        'Importance': importances
    })
    df = df.sort_values('Importance', ascending=False).reset_index(drop=True)

    return df


def get_top_features(model, feature_names, n=10):
    """
    Get top N most important features.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    feature_names : list
        Names of features
    n : int, default=10
        Number of top features to return

    Returns:
    --------
    pd.DataFrame: Top N features
    """
    df = get_feature_importance_df(model, feature_names)
    return df.head(n)


def compute_shap_feature_importance(model, X_sample):
    """
    Compute SHAP-based feature importance.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    X_sample : numpy array
        Sample of data for SHAP computation

    Returns:
    --------
    numpy array: 1D array of mean absolute SHAP values per feature, or None
    """
    try:
        import shap
        if hasattr(model, 'feature_importances_'):
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_sample[:100])

            if isinstance(shap_values, list):
                # Multi-class: list of (n_samples, n_features) for each class
                class_avgs = []
                for sv in shap_values:
                    class_avgs.append(np.mean(np.abs(sv), axis=0))
                avg_shap = np.mean(class_avgs, axis=0)
            elif len(shap_values.shape) == 3:
                # (n_samples, n_features, n_classes)
                avg_shap = np.mean(np.mean(np.abs(shap_values), axis=0), axis=1)
            else:
                # (n_samples, n_features)
                avg_shap = np.mean(np.abs(shap_values), axis=0)

            # Ensure 1D array
            result = np.asarray(avg_shap).ravel()
            return result
        else:
            return None
    except Exception as e:
        print(f"  SHAP computation warning: {e}")
        return None


def compare_feature_importance(model, feature_names, X_sample=None):
    """
    Compare model-based vs SHAP-based feature importance.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    feature_names : list
        Names of features
    X_sample : numpy array, optional
        Sample data for SHAP

    Returns:
    --------
    pd.DataFrame: Comparison of importance methods
    """
    model_importance = get_feature_importance_df(model, feature_names)
    model_importance.columns = ['Feature', 'Model_Importance']

    if X_sample is not None:
        shap_importance = compute_shap_feature_importance(model, X_sample)
        if shap_importance is not None:
            min_len = min(len(shap_importance), len(feature_names))
            shap_df = pd.DataFrame({
                'Feature': feature_names[:min_len],
                'SHAP_Importance': shap_importance[:min_len]
            })
            comparison = model_importance.merge(shap_df, on='Feature', how='outer')
            return comparison

    return model_importance


def plot_feature_importance(feature_importance_df, title="Feature Importance",
                            top_n=15, figsize=(10, 7)):
    """
    Plot feature importance bar chart.

    Parameters:
    -----------
    feature_importance_df : pd.DataFrame
        DataFrame with 'Feature' and 'Importance' columns
    title : str, default="Feature Importance"
        Chart title
    top_n : int, default=15
        Number of top features to display
    figsize : tuple, default=(10, 7)
        Figure size

    Returns:
    --------
    matplotlib Figure: The generated plot
    """
    df = feature_importance_df.head(top_n).copy()

    fig, ax = plt.subplots(figsize=figsize)

    # Color gradient
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(df)))

    bars = ax.barh(df['Feature'][::-1], df['Importance'][::-1], color=colors[::-1])

    # Add value labels
    for bar, val in zip(bars, df['Importance'][::-1]):
        ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                f'{val:.4f}', va='center', fontsize=9)

    ax.set_xlabel('Importance Score', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    return fig


def save_feature_importance_plot(model, feature_names, output_dir, X_sample=None):
    """
    Save feature importance plot to file.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    feature_names : list
        Names of features
    output_dir : str
        Directory to save the plot
    X_sample : numpy array, optional
        Sample data for SHAP computation
    """
    os.makedirs(output_dir, exist_ok=True)

    importance_df = get_feature_importance_df(model, feature_names)
    fig = plot_feature_importance(importance_df)
    fig.savefig(os.path.join(output_dir, 'model_feature_importance.png'), dpi=100, bbox_inches='tight')
    plt.close(fig)
    print(f"Feature importance plot saved to {output_dir}/model_feature_importance.png")


def get_local_feature_importance(model, X_instance, feature_names):
    """
    Get local feature importance for a single instance.

    Parameters:
    -----------
    model : sklearn model
        Trained model
    X_instance : numpy array
        Single instance features (1, n_features)
    feature_names : list
        Names of features

    Returns:
    --------
    pd.DataFrame: Local feature importance
    """
    import shap

    if hasattr(model, 'feature_importances_'):
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_instance)

        if isinstance(shap_values, list):
            # For multi-class, get absolute values across all classes
            feature_effects = np.mean([np.abs(sv[0]) for sv in shap_values], axis=0)
        else:
            feature_effects = np.abs(shap_values[0])

        min_len = min(len(feature_effects), len(feature_names))
        df = pd.DataFrame({
            'Feature': feature_names[:min_len],
            'Impact': feature_effects[:min_len],
            'Direction': ['Positive' if sv > 0 else 'Negative' for sv in
                         (shap_values[0] if not isinstance(shap_values, list)
                          else shap_values[0][0])[:min_len]]
        })
        return df.sort_values('Impact', ascending=False).reset_index(drop=True)

    return None


def main():
    """Test feature importance module."""
    print("=" * 60)
    print("TESTING FEATURE IMPORTANCE MODULE")
    print("=" * 60)

    try:
        model, feature_names, X_sample = load_model_for_importance()

        print(f"\nModel type: {type(model).__name__}")
        print(f"Number of features: {len(feature_names)}")

        # Get feature importance
        print("\nTop 10 Features (Model-based):")
        importance_df = get_feature_importance_df(model, feature_names)
        print(importance_df.head(10).to_string(index=False))

        # SHAP-based importance
        print("\nComputing SHAP feature importance...")
        comparison = compare_feature_importance(model, feature_names, X_sample)
        if 'SHAP_Importance' in comparison.columns:
            print("Top 10 Features (SHAP-based):")
            shap_sorted = comparison.sort_values('SHAP_Importance', ascending=False)
            print(shap_sorted.head(10).to_string(index=False))

        # Save plot
        output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'reports')
        save_feature_importance_plot(model, feature_names, output_dir, X_sample)

        print("\n✓ Feature importance module working correctly!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
